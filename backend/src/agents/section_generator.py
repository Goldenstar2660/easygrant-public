"""Section Generator Agent.

Generates proposal section drafts using RAG context with inline citations.
Uses GPT-4o-mini for cost-effective drafting.
"""

import logging
import re
from typing import List, Dict, Optional
from ..services.llm_client import LLMClient
from ..models.citation import Citation
from ..utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class SectionGenerator:
    """Generate proposal sections with RAG-based citations"""
    
    def __init__(self):
        """Initialize section generator with LLM client"""
        self.llm_client = LLMClient()
        self.config = ConfigLoader()
    
    def generate_section(
        self,
        section_name: str,
        section_requirements: Optional[str],
        word_limit: Optional[int],
        char_limit: Optional[int],
        format_type: str,
        citations: List[Citation]
    ) -> Dict:
        """Generate a proposal section with inline citations.
        
        Args:
            section_name: Name of the section
            section_requirements: Additional requirements
            word_limit: Maximum words allowed
            char_limit: Maximum characters allowed
            format_type: Format (narrative, bullet-points, table, form)
            citations: Retrieved source citations
            
        Returns:
            Dict with generated_text, word_count, citations_used, warning
        """
        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"📝 GENERATING SECTION: {section_name}")
        logger.info(f"{'='*80}")
        logger.info(f"Format: {format_type} | Word limit: {word_limit} | Citations available: {len(citations)}")
        
        print(f"\n[SECTION GENERATOR] ========================================")
        print(f"[SECTION GENERATOR] generate_section() called")
        print(f"[SECTION GENERATOR] Section: {section_name}")
        print(f"[SECTION GENERATOR] Citations received: {len(citations)}")
        print(f"[SECTION GENERATOR] ========================================\n")
        
        # DETAILED LOGGING: Log citation details
        if len(citations) > 0:
            logger.info(f"")
            logger.info(f"📚 CONTEXT BEING SENT TO AI:")
            logger.info(f"{'-'*80}")
            for i, citation in enumerate(citations, 1):
                logger.info(f"Source {i}: {citation.document_title}, p.{citation.page_number} (relevance: {citation.relevance_score:.3f})")
                logger.info(f"   Text: {citation.chunk_text[:150]}...")
                logger.info(f"")
            logger.info(f"{'-'*80}")
        else:
            logger.warning(f"")
            logger.warning(f"⚠️  NO CONTEXT AVAILABLE - AI will generate without your documents")
            logger.warning(f"{'-'*80}")
        
        # Build generation prompt
        prompt = self._build_generation_prompt(
            section_name=section_name,
            section_requirements=section_requirements,
            word_limit=word_limit,
            char_limit=char_limit,
            format_type=format_type,
            citations=citations
        )
        
        # Simplified logging - just confirm AI is being called
        logger.info(f"")
        logger.info(f"🤖 Calling AI (GPT-4o-mini) with {len(prompt)} chars of context...")
        
        # Generate text via GPT-4o-mini
        try:
            generated_text = self.llm_client.generate_section_from_prompt(prompt)
            
            print(f"[SECTION GENERATOR] AI generation complete")
            print(f"[SECTION GENERATOR] Generated text length: {len(generated_text)} chars")
            
            # Count words
            word_count = len(generated_text.split())
            print(f"[SECTION GENERATOR] Word count: {word_count}")
            
            # Extract used citations from text
            print(f"[SECTION GENERATOR] Extracting citations from generated text...")
            citations_used = self._extract_citations_from_text(generated_text, citations)
            print(f"[SECTION GENERATOR] Citations extracted: {len(citations_used)}")
            
            if len(citations_used) == 0 and len(citations) > 0:
                print(f"[SECTION GENERATOR] ⚠️  WARNING: Had {len(citations)} citations available but none found in text!")
                print(f"[SECTION GENERATOR] Generated text preview: {generated_text[:200]}...")
            elif len(citations_used) > 0:
                print(f"[SECTION GENERATOR] ✓ Successfully extracted citations:")
                for i, cit in enumerate(citations_used[:3], 1):
                    print(f"[SECTION GENERATOR]   {i}. {cit.document_title}, p.{cit.page_number}")
            
            # Check word limit
            warning = None
            if word_limit and word_count > word_limit:
                warning = f"Section exceeds word limit by {word_count - word_limit} words"
                logger.warning(f"[SECTION GENERATOR] {warning}")
            elif word_limit and word_count > word_limit * 0.9:
                warning = f"Section is close to word limit ({word_count}/{word_limit} words)"
                logger.info(f"[SECTION GENERATOR] {warning}")
            
            logger.info(
                f"[SECTION GENERATOR] Generated {word_count} words, "
                f"used {len(citations_used)} citations"
            )
            
            return {
                "generated_text": generated_text,
                "word_count": word_count,
                "citations_used": citations_used,
                "warning": warning,
                "locked_paragraphs": []  # Empty initially
            }
            
        except Exception as e:
            logger.error(f"[SECTION GENERATOR] Generation failed: {str(e)}", exc_info=True)
            raise
    
    def _build_generation_prompt(
        self,
        section_name: str,
        section_requirements: Optional[str],
        word_limit: Optional[int],
        char_limit: Optional[int],
        format_type: str,
        citations: List[Citation]
    ) -> str:
        """Build prompt for section generation.
        
        Args:
            section_name: Section title
            section_requirements: Additional requirements
            word_limit: Word limit
            char_limit: Character limit
            format_type: Expected format
            citations: Retrieved source citations
            
        Returns:
            Formatted prompt string
        """
        # Format citations as numbered context
        if citations:
            context_parts = ["RELEVANT CONTEXT FROM UPLOADED DOCUMENTS:\n"]
            for i, citation in enumerate(citations, 1):
                context_parts.append(
                    f"[Source {i}] {citation.document_title}, Page {citation.page_number}:\n"
                    f"{citation.chunk_text}\n"
                )
            context_str = "\n".join(context_parts)
        else:
            # NO SOURCES - Be very explicit
            context_str = """WARNING: No relevant context found in uploaded documents.

CRITICAL INSTRUCTIONS WHEN NO SOURCES ARE AVAILABLE:
- DO NOT generate generic content with placeholders like [City/Region], [Organization], etc.
- DO NOT invent fake statistics, citations, or data
- DO NOT search the internet or use external knowledge
- INSTEAD: Generate a brief statement explaining that this section requires specific information from the organization/community that should be provided by the applicant
- Keep response under 100 words
- Be honest that supporting documentation is needed"""
        
        # Build requirements section
        requirements_parts = []
        if section_requirements:
            requirements_parts.append(f"Additional Requirements: {section_requirements}")
        if word_limit:
            requirements_parts.append(f"Word Limit: Maximum {word_limit} words")
        if char_limit:
            requirements_parts.append(f"Character Limit: Maximum {char_limit} characters")
        requirements_parts.append(f"Format: {format_type}")
        
        requirements_str = "\n".join(requirements_parts) if requirements_parts else "No specific requirements"
        
        # Build complete prompt
        prompt = f"""You are an expert grant proposal writer with deep knowledge of effective grantsmanship. Your task is to generate a compelling, evidence-based {section_name} section that maximizes the proposal's competitiveness.

**SECTION REQUIREMENTS:**
{requirements_str}

**CONTEXT FROM SOURCE DOCUMENTS:**
{context_str}

**CORE WRITING PRINCIPLES:**

1. **Specificity Over Generality**
   - Use concrete details, specific numbers, and real examples from the source documents
   - Avoid vague language like "many," "various," or "numerous" - be precise
   - Replace generic statements with evidence-based claims

2. **Evidence-Based Claims**
   - Ground every significant claim in evidence from the source documents
   - Use inline citations with EXACT document titles from the sources above: [EXACT_DOCUMENT_TITLE, p.PAGE_NUMBER]
   - CRITICAL: Use the EXACT document title as shown in the "Source" entries above - do NOT invent descriptive names
   - Example: If source is "[Source 1] cti_application_2020.pdf, Page 4:", cite as [cti_application_2020.pdf, p.4]
   - Cite data, statistics, documented needs, and factual statements
   - For strategic/contextual statements, citations are optional if they reflect general knowledge

3. **Demonstrate Clear Need and Alignment**
   - Articulate the specific problem, gap, or opportunity being addressed
   - Show how the proposed approach directly responds to documented needs
   - Explicitly connect to the funder's priorities and objectives as stated in the funding call
   - Explain WHY this matters and WHO benefits

4. **Be Concrete and Action-Oriented**
   - Describe specific activities, deliverables, and outcomes
   - Use active voice and strong verbs
   - Avoid passive constructions and weak qualifiers ("may," "might," "could potentially")

5. **Avoid Common Grant Writing Pitfalls**
   - NO generic fluff or filler language
   - NO unexplained jargon or acronyms
   - NO unsubstantiated claims or exaggeration
   - NO repetitive or redundant content
   - NO unsupported assumptions about what the funder knows

**STRUCTURAL APPROACH:**
- Open with a clear, compelling statement that establishes context
- Build logically from problem/need → approach/solution → expected outcomes
- Use transitions to connect ideas smoothly
- Conclude with impact or significance where appropriate

**TONE AND STYLE:**
- Professional, confident, and authoritative
- Third person perspective (avoid "I" or "we" unless quoting sources)
- Clear and accessible - write for reviewers who may not be subject-matter experts
- Persuasive but grounded in evidence, not hyperbole

**LENGTH AND CONCISENESS:**
- Write concisely - aim for 1-2 focused paragraphs maximum
- Every sentence should add value - no filler or redundancy
- Make your point clearly and move on - avoid over-explanation
- If you can say it in fewer words, do so

**FORMATTING:**
- Respect the specified format type: {format_type}
- Stay within word/character limits
- Use paragraph breaks for readability

Now generate the {section_name} section following these principles. Prioritize quality, specificity, and evidence over length. Be concise and impactful."""

        return prompt
    
    def _extract_citations_from_text(
        self,
        text: str,
        available_citations: List[Citation]
    ) -> List[Citation]:
        """Extract which citations were actually used in generated text.
        
        Args:
            text: Generated text with inline citations
            available_citations: All available citations
            
        Returns:
            List of Citation objects that appear in text
        """
        print(f"\n[CITATION EXTRACTOR] ========================================")
        print(f"[CITATION EXTRACTOR] Extracting citations from text")
        print(f"[CITATION EXTRACTOR] Available citations: {len(available_citations)}")
        
        if len(available_citations) > 0:
            print(f"[CITATION EXTRACTOR] Available citation details:")
            for i, cit in enumerate(available_citations, 1):
                print(f"[CITATION EXTRACTOR]   {i}. '{cit.document_title}', p.{cit.page_number}")
        
        used_citations = []
        # Updated pattern to allow optional space after 'p.' to match both "p.1" and "p. 1"
        citation_pattern = r'\[([^\]]+),\s*p\.\s*(\d+)\]'
        
        matches = re.findall(citation_pattern, text)
        print(f"[CITATION EXTRACTOR] Found {len(matches)} citation patterns in text")
        
        if len(matches) > 0:
            print(f"[CITATION EXTRACTOR] Citation patterns found:")
            for doc_title, page_str in matches[:5]:  # Show first 5
                print(f"[CITATION EXTRACTOR]   - [{doc_title}, p.{page_str}]")
        else:
            print(f"[CITATION EXTRACTOR] ⚠️  NO citation patterns found in text!")
            print(f"[CITATION EXTRACTOR] Text preview: {text[:300]}...")
        
        for doc_title, page_str in matches:
            page_num = int(page_str)
            
            print(f"\n[CITATION EXTRACTOR] Trying to match: '{doc_title}', p.{page_num}")
            
            # Find matching citation - prefer exact page match, but accept any page from same doc
            matched = False
            exact_match = None
            fallback_match = None
            
            for citation in available_citations:
                title_matches = (citation.document_title.lower() == doc_title.lower())
                page_matches = (citation.page_number == page_num)
                
                if title_matches and page_matches:
                    # Perfect match: same document AND same page
                    exact_match = citation
                    print(f"[CITATION EXTRACTOR]   ✓ EXACT MATCH: '{citation.document_title}', p.{citation.page_number}")
                    break
                elif title_matches and not fallback_match:
                    # Fallback: same document but different page (AI cited wrong page)
                    fallback_match = citation
                    print(f"[CITATION EXTRACTOR]   ~ Fallback match: '{citation.document_title}', p.{citation.page_number} (AI cited p.{page_num})")
            
            # Use exact match if found, otherwise use fallback
            citation_to_use = exact_match or fallback_match
            
            if citation_to_use and citation_to_use not in used_citations:
                used_citations.append(citation_to_use)
                if exact_match:
                    print(f"[CITATION EXTRACTOR] ✓ MATCHED EXACT: {citation_to_use.document_title}, p.{citation_to_use.page_number}")
                else:
                    print(f"[CITATION EXTRACTOR] ✓ MATCHED FALLBACK: {citation_to_use.document_title}, p.{citation_to_use.page_number} (AI cited p.{page_num}, using closest available)")
                matched = True
            
            if not matched:
                print(f"[CITATION EXTRACTOR] ✗ NO MATCH found for '{doc_title}', p.{page_num}")
        
        print(f"[CITATION EXTRACTOR] Total unique citations extracted: {len(used_citations)}")
        print(f"[CITATION EXTRACTOR] ========================================\n")
        
        logger.info(f"[SECTION GENERATOR] Extracted {len(used_citations)} unique citations from text")
        return used_citations
    
    def count_words(self, text: str) -> int:
        """Count words in text.
        
        Args:
            text: Input text
            
        Returns:
            Word count
        """
        return len(text.split())
