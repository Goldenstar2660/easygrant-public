"""Requirements Extractor Agent.

Parses funding call PDF into structured blueprint using hybrid regex + GPT-4o approach.
Extracts sections, word limits, eligibility criteria, and scoring weights.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from ..services.llm_client import LLMClient
from ..utils.parser import DocumentParser, extract_text_from_file
from ..utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class RequirementsExtractor:
    """Extract structured requirements from funding call PDFs"""
    
    def __init__(self):
        """Initialize requirements extractor with LLM client and config"""
        self.llm_client = LLMClient()
        self.config = ConfigLoader()
        self.parser = DocumentParser()
    
    def extract_requirements(
        self,
        file_path: str,
        session_id: str,
        max_retries: int = 2
    ) -> Dict:
        """Extract requirements from funding call PDF.
        
        Args:
            file_path: Path to funding call PDF
            session_id: Session identifier
            max_retries: Maximum retry attempts if extraction fails
            
        Returns:
            Dict with structure:
            {
                "sections": [
                    {
                        "name": str,
                        "required": bool,
                        "word_limit": int | None,
                        "char_limit": int | None,
                        "format": str,
                        "scoring_weight": float | None
                    }
                ],
                "eligibility": [str],
                "scoring_criteria": Dict,
                "deadline": str | None,
                "total_sections": int
            }
        """
        # Parse PDF to text
        full_text, page_data = extract_text_from_file(file_path)
        
        # Log document info
        logger.info(f"[REQUIREMENTS EXTRACTION] Starting extraction for session {session_id}")
        logger.info(f"[REQUIREMENTS EXTRACTION] Document length: {len(full_text)} characters")
        logger.info(f"[REQUIREMENTS EXTRACTION] Document pages: {len(page_data)}")
        logger.info(f"[REQUIREMENTS EXTRACTION] First 500 characters:\n{full_text[:500]}")
        
        # DETAILED LOGGING: Log full parsed text from PDF
        logger.info(f"[REQUIREMENTS EXTRACTION] ========== FULL PARSED PDF TEXT ==========")
        logger.info(f"[REQUIREMENTS EXTRACTION] File: {file_path}")
        logger.info(f"[REQUIREMENTS EXTRACTION] Full text ({len(full_text)} chars):\n{full_text}")
        logger.info(f"[REQUIREMENTS EXTRACTION] ========== END FULL PARSED TEXT ==========")
        
        # Log page-by-page breakdown
        logger.info(f"[REQUIREMENTS EXTRACTION] ========== PAGE-BY-PAGE BREAKDOWN ==========")
        for page in page_data:
            logger.info(f"[REQUIREMENTS EXTRACTION] --- Page {page['page_number']} ({len(page['text'])} chars) ---")
            logger.info(f"[REQUIREMENTS EXTRACTION] {page['text'][:300]}...")
        logger.info(f"[REQUIREMENTS EXTRACTION] ========== END PAGE BREAKDOWN ==========")
        
        # Try extraction with retries
        for attempt in range(max_retries):
            try:
                logger.info(f"[REQUIREMENTS EXTRACTION] Attempt {attempt + 1}/{max_retries}")
                
                # Step 1: Regex-based word limit detection
                logger.info(f"[REQUIREMENTS EXTRACTION] Step 1: Extracting word limits via regex...")
                word_limits = self._extract_word_limits(full_text)
                logger.info(f"[REQUIREMENTS EXTRACTION] Found {len(word_limits)} word/char limits")
                
                # Step 2: GPT-4o structured extraction
                logger.info(f"[REQUIREMENTS EXTRACTION] Step 2: Calling GPT-4o for structured extraction...")
                blueprint = self._extract_with_gpt4o(full_text, word_limits)
                
                # Step 3: Validate blueprint
                logger.info(f"[REQUIREMENTS EXTRACTION] Step 3: Validating extracted blueprint...")
                if self._validate_blueprint(blueprint):
                    logger.info(f"[REQUIREMENTS EXTRACTION] ✓ Blueprint validation successful!")
                    logger.info(f"[REQUIREMENTS EXTRACTION] Final result: {blueprint.get('total_sections')} sections extracted")
                    return blueprint
                else:
                    logger.warning(f"[REQUIREMENTS EXTRACTION] ✗ Blueprint validation failed on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        logger.info(f"[REQUIREMENTS EXTRACTION] Retrying...")
                        continue  # Retry
                    else:
                        logger.error(f"[REQUIREMENTS EXTRACTION] All attempts failed, using fallback")
                        # Return fallback structure
                        return self._create_fallback_blueprint(full_text, word_limits)
                        
            except Exception as e:
                logger.error(f"[REQUIREMENTS EXTRACTION] Exception on attempt {attempt + 1}: {str(e)}", exc_info=True)
                if attempt < max_retries - 1:
                    logger.info(f"[REQUIREMENTS EXTRACTION] Retrying after exception...")
                    continue  # Retry
                else:
                    logger.error(f"[REQUIREMENTS EXTRACTION] All retries exhausted, using fallback")
                    # Return fallback on final failure
                    return self._create_fallback_blueprint(full_text, {})
        
        # Should never reach here, but return fallback just in case
        logger.warning(f"[REQUIREMENTS EXTRACTION] Unexpected fallthrough, using fallback")
        return self._create_fallback_blueprint(full_text, {})
    
    def _extract_word_limits(self, text: str) -> Dict[str, int]:
        """Extract word/character limits using regex patterns.
        
        Args:
            text: Full text of funding call
            
        Returns:
            Dict mapping section hints to limits
        """
        limits = {}
        
        # Common patterns for word limits
        patterns = [
            # "up to 500 words"
            r'(?:up to|maximum of?|max|limit of?|not (?:to )?exceed(?:ing)?)\s*(\d+)\s*words?',
            # "500 words maximum"
            r'(\d+)\s*words?\s*(?:maximum|max|limit)',
            # "500-word limit"
            r'(\d+)[\s-]*word\s*limit',
            # "maximum 2000 characters"
            r'(?:up to|maximum of?|max|limit of?|not (?:to )?exceed(?:ing)?)\s*(\d+)\s*(?:characters?|chars?)',
            # "2000 characters maximum"
            r'(\d+)\s*(?:characters?|chars?)\s*(?:maximum|max|limit)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                limit_value = int(match.group(1))
                # Store with context (50 chars before the match)
                start = max(0, match.start() - 50)
                context = text[start:match.start()].lower()
                limits[context] = limit_value
        
        return limits
    
    def _extract_with_gpt4o(
        self,
        text: str,
        word_limits: Dict[str, int]
    ) -> Dict:
        """Extract structured requirements using GPT-4o with JSON schema.
        
        Args:
            text: Full text of funding call
            word_limits: Pre-extracted word limits from regex
            
        Returns:
            Structured blueprint dictionary
        """
        # Truncate text if too long (GPT-4o has 128k tokens, ~100k chars safely)
        # Keep more text to capture all sections from large documents
        max_chars = 80000
        if len(text) > max_chars:
            logger.warning(f"[REQUIREMENTS EXTRACTION] Document too long ({len(text)} chars), truncating to {max_chars}")
            text = text[:max_chars] + "\n\n[Document truncated for analysis...]"
        
        logger.info(f"[REQUIREMENTS EXTRACTION] Detected {len(word_limits)} word/char limits via regex")
        
        # JSON schema for structured output
        json_schema = {
            "name": "funding_call_requirements",
            "schema": {
                "type": "object",
                "properties": {
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "required": {"type": "boolean"},
                                "word_limit": {"type": ["integer", "null"]},
                                "char_limit": {"type": ["integer", "null"]},
                                "format": {"type": "string"},
                                "scoring_weight": {"type": ["number", "null"]}
                            },
                            "required": ["name", "required", "format"]
                        }
                    },
                    "eligibility": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "scoring_criteria": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "criteria": {"type": "string"},
                                "weight": {"type": ["number", "null"]}
                            },
                            "required": ["criteria"]
                        }
                    },
                    "deadline": {"type": ["string", "null"]},
                    "total_sections": {"type": "integer"}
                },
                "required": ["sections", "eligibility", "total_sections"]
            }
        }
        
        # Improved prompt for comprehensive extraction
        prompt = f"""You are an expert grant proposal assistant analyzing a funding call document. Your task is to extract the WRITTEN PROPOSAL SECTIONS that applicants must complete.

**CRITICAL INSTRUCTIONS:**
- Extract ONLY sections that require written narrative, descriptions, or text responses
- DO NOT extract supporting documents, attachments, or administrative forms (e.g., financial statements, resolutions, letters of incorporation, cost estimates)
- Look for sections in tables of contents, proposal format sections, and application instructions
- Focus on sections where applicants write about their project

**PROPOSAL SECTIONS TO EXTRACT (examples):**
  ✓ Executive Summary / Abstract / Overview
  ✓ Project Description / Narrative / Statement
  ✓ Project Goals / Objectives / Purpose
  ✓ Methods / Approach / Work Plan / Activities
  ✓ Timeline / Schedule / Milestones
  ✓ Budget Narrative / Budget Justification (written explanation)
  ✓ Organizational Background / Capacity / Experience
  ✓ Key Personnel / Staff Qualifications / Team
  ✓ Project Impact / Outcomes / Expected Results
  ✓ Evaluation Plan / Success Metrics
  ✓ Sustainability Plan / Long-term Vision
  ✓ Community Need / Problem Statement
  ✓ Partnerships / Collaboration

**DO NOT EXTRACT (these are attachments/forms, not written sections):**
  ✗ Financial statements (audited, unaudited)
  ✗ Resolutions (Band Council, Board, etc.)
  ✗ Registration documents (incorporation, letters patent)
  ✗ Tax documents (CRA numbers, charitable status)
  ✗ Technical documents (feasibility studies, designs, cost estimates)
  ✗ Application forms (cover page, signature page)
  ✗ Budget spreadsheets/tables (unless it's a budget narrative)

**EXTRACTION REQUIREMENTS:**

1. **Sections** - Extract ONLY written proposal sections:
   - name: Section title as it appears (e.g., "Project Description", "Community Need Statement")
   - required: true if mandatory, false if optional
   - word_limit: maximum words (extract from phrases like "up to X words", "maximum 500 words")
   - char_limit: maximum characters (extract from "up to X characters")
   - format: "narrative" (prose), "bullet-points", "table", or "form"
   - scoring_weight: percentage or points if evaluation criteria mention this section

2. **Eligibility** - List ALL eligibility requirements (who can apply):
   - Extract from sections titled: "Eligibility", "Who Can Apply", "Eligible Applicants"
   - Include organization type requirements, geographic restrictions, etc.

3. **Scoring Criteria** - Extract evaluation/scoring criteria as a list:
   - Look for sections like "Evaluation Criteria", "Review Criteria", "Scoring Rubric"
   - For each criterion, extract:
     * criteria: The criterion description/question
     * weight: Point value or percentage weight (null if not specified)
   - Example: [{{"criteria": "Project feasibility", "weight": 25}}, {{"criteria": "Budget justification", "weight": 15}}]

4. **Deadline** - Application submission deadline (date/time if mentioned)

5. **Total Sections** - Count of ALL sections you extracted

**Regex-detected limits for context:**
{json.dumps(word_limits, indent=2)}

**FUNDING CALL DOCUMENT:**
{text}

**OUTPUT:** Return ONLY a valid JSON object following the schema. Be thorough - extract ALL sections, not just the main ones."""

        logger.info(f"[REQUIREMENTS EXTRACTION] Sending {len(text)} characters to GPT-4o")
        logger.info(f"[REQUIREMENTS EXTRACTION] Prompt length: {len(prompt)} characters")
        
        # DETAILED LOGGING: Log complete prompt being sent to GPT-4o
        logger.info(f"[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o PROMPT ==========")
        logger.info(f"[REQUIREMENTS EXTRACTION] Model: {self.llm_client.requirements_model}")
        logger.info(f"[REQUIREMENTS EXTRACTION] Temperature: {self.llm_client.requirements_temp}")
        logger.info(f"[REQUIREMENTS EXTRACTION] Prompt:\n{prompt}")
        logger.info(f"[REQUIREMENTS EXTRACTION] ========== END GPT-4o PROMPT ==========")
        
        # Call GPT-4o with JSON mode
        response = self.llm_client.extract_requirements(prompt, json_schema)
        
        logger.info(f"[REQUIREMENTS EXTRACTION] GPT-4o returned {len(response.get('sections', []))} sections")
        logger.info(f"[REQUIREMENTS EXTRACTION] Sections extracted: {[s.get('name') for s in response.get('sections', [])]}")
        
        # DETAILED LOGGING: Log complete GPT-4o response
        logger.info(f"[REQUIREMENTS EXTRACTION] ========== COMPLETE GPT-4o RESPONSE ==========")
        logger.info(f"[REQUIREMENTS EXTRACTION] Response JSON:\n{json.dumps(response, indent=2)}")
        logger.info(f"[REQUIREMENTS EXTRACTION] ========== END GPT-4o RESPONSE ==========")
        
        return response
    
    def _validate_blueprint(self, blueprint: Dict) -> bool:
        """Validate extracted blueprint structure.
        
        Args:
            blueprint: Extracted requirements blueprint
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if "sections" not in blueprint:
            logger.warning("[REQUIREMENTS EXTRACTION] Validation failed: 'sections' key missing")
            return False
        
        if "total_sections" not in blueprint:
            logger.warning("[REQUIREMENTS EXTRACTION] Validation failed: 'total_sections' key missing")
            return False
        
        # Sections must be non-empty
        sections = blueprint.get("sections", [])
        if not sections or len(sections) == 0:
            logger.warning("[REQUIREMENTS EXTRACTION] Validation failed: sections list is empty")
            return False
        
        # Each section must have required fields
        for i, section in enumerate(sections):
            if "name" not in section:
                logger.warning(f"[REQUIREMENTS EXTRACTION] Validation failed: section {i} missing 'name'")
                return False
            if "required" not in section:
                logger.warning(f"[REQUIREMENTS EXTRACTION] Validation failed: section {i} ({section.get('name')}) missing 'required'")
                return False
            if "format" not in section:
                logger.warning(f"[REQUIREMENTS EXTRACTION] Validation failed: section {i} ({section.get('name')}) missing 'format'")
                return False
            
            # Validate limit formats (must be positive integers if present)
            word_limit = section.get("word_limit")
            if word_limit is not None and (not isinstance(word_limit, int) or word_limit <= 0):
                logger.warning(f"[REQUIREMENTS EXTRACTION] Validation failed: section {i} ({section.get('name')}) has invalid word_limit: {word_limit}")
                return False
            
            char_limit = section.get("char_limit")
            if char_limit is not None and (not isinstance(char_limit, int) or char_limit <= 0):
                logger.warning(f"[REQUIREMENTS EXTRACTION] Validation failed: section {i} ({section.get('name')}) has invalid char_limit: {char_limit}")
                return False
        
        # Eligibility should be a list (can be empty)
        if "eligibility" not in blueprint or not isinstance(blueprint["eligibility"], list):
            logger.warning("[REQUIREMENTS EXTRACTION] Validation failed: 'eligibility' missing or not a list")
            return False
        
        return True
    
    def _create_fallback_blueprint(
        self,
        text: str,
        word_limits: Dict[str, int]
    ) -> Dict:
        """Create fallback blueprint when GPT-4o extraction fails.
        
        Args:
            text: Full text of funding call
            word_limits: Pre-extracted word limits
            
        Returns:
            Basic blueprint structure
        """
        # Try to find common section headers
        section_patterns = [
            r'(?:^|\n)\s*(?:\d+\.?\s+)?([A-Z][A-Za-z\s]+(?:Summary|Description|Narrative|Statement|Plan|Budget|Timeline))\s*(?:\n|:)',
        ]
        
        sections = []
        for pattern in section_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                section_name = match.group(1).strip()
                sections.append({
                    "name": section_name,
                    "required": True,  # Assume required
                    "word_limit": None,
                    "char_limit": None,
                    "format": "narrative",
                    "scoring_weight": None
                })
        
        # If no sections found, create default structure
        if not sections:
            sections = [
                {
                    "name": "Project Description",
                    "required": True,
                    "word_limit": 1000,
                    "char_limit": None,
                    "format": "narrative",
                    "scoring_weight": None
                },
                {
                    "name": "Budget Narrative",
                    "required": True,
                    "word_limit": 500,
                    "char_limit": None,
                    "format": "narrative",
                    "scoring_weight": None
                }
            ]
        
        return {
            "sections": sections[:10],  # Limit to 10 sections
            "eligibility": ["Please review funding call for eligibility criteria"],
            "scoring_criteria": [],
            "deadline": None,
            "total_sections": len(sections[:10])
        }
    
    def get_blueprint_summary(self, blueprint: Dict) -> str:
        """Generate human-readable summary of blueprint.
        
        Args:
            blueprint: Requirements blueprint
            
        Returns:
            Summary string
        """
        sections = blueprint.get("sections", [])
        required_count = sum(1 for s in sections if s.get("required", False))
        optional_count = len(sections) - required_count
        
        summary_lines = [
            f"Total Sections: {len(sections)} ({required_count} required, {optional_count} optional)",
            "",
            "Required Sections:"
        ]
        
        for section in sections:
            if section.get("required", False):
                name = section.get("name", "Unnamed")
                word_limit = section.get("word_limit")
                char_limit = section.get("char_limit")
                
                limit_str = ""
                if word_limit:
                    limit_str = f" ({word_limit} words max)"
                elif char_limit:
                    limit_str = f" ({char_limit} characters max)"
                
                summary_lines.append(f"  - {name}{limit_str}")
        
        if optional_count > 0:
            summary_lines.extend(["", "Optional Sections:"])
            for section in sections:
                if not section.get("required", False):
                    name = section.get("name", "Unnamed")
                    summary_lines.append(f"  - {name}")
        
        eligibility = blueprint.get("eligibility", [])
        if eligibility:
            summary_lines.extend(["", f"Eligibility Criteria: {len(eligibility)} items"])
        
        return "\n".join(summary_lines)
