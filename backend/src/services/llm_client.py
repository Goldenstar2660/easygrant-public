"""OpenAI LLM client wrapper.

Provides unified interface for GPT-4o, GPT-4o-mini, and embeddings.
Configuration loaded from config.yaml.
"""

import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
from backend.src.utils.config_loader import config


class LLMClient:
    """Wrapper for OpenAI API calls"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Load model configs (flat structure in config.yaml)
        self.requirements_model = config.get('llm', 'requirements_model', default='gpt-4o')
        self.requirements_temp = config.get('llm', 'requirements_temperature', default=0.1)
        
        self.drafting_model = config.get('llm', 'drafting_model', default='gpt-4o-mini')
        self.drafting_temp = config.get('llm', 'drafting_temperature', default=0.7)
        
        self.quality_model = config.get('llm', 'quality_model', default='gpt-4o')
        self.quality_temp = config.get('llm', 'quality_temperature', default=0.0)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to drafting model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Optional format constraint (e.g., {"type": "json_object"})
            
        Returns:
            Response text
        """
        model = model or self.drafting_model
        temperature = temperature if temperature is not None else self.drafting_temp
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def extract_requirements(
        self,
        prompt: str,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Extract structured requirements from funding call.
        
        Uses gpt-4o with JSON mode for reliable structured output.
        
        Args:
            prompt: Prompt with funding call text and instructions
            json_schema: Optional JSON schema for response_format
            
        Returns:
            Parsed JSON dict with structured requirements
        """
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # Use JSON mode for structured output
        response_text = self.chat_completion(
            messages=messages,
            model=self.requirements_model,
            temperature=self.requirements_temp,
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        import json
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Return empty structure if parsing fails
            return {
                "sections": [],
                "eligibility": [],
                "scoring_criteria": {},
                "deadline": None,
                "total_sections": 0
            }
    
    def generate_section(
        self,
        section_name: str,
        section_requirements: str,
        word_limit: int,
        retrieved_context: List[str]
    ) -> str:
        """Generate proposal section using RAG context.
        
        Uses gpt-4o-mini for cost-effective drafting.
        
        Args:
            section_name: Name of section (e.g., "Project Summary")
            section_requirements: Requirements/format for this section
            word_limit: Maximum word count
            retrieved_context: List of relevant text chunks from vector DB
            
        Returns:
            Generated section text with inline citations
        """
        context_text = "\n\n---\n\n".join(
            f"[Source {i+1}] {chunk}" 
            for i, chunk in enumerate(retrieved_context)
        )
        
        system_prompt = f"""You are an expert grant proposal writer. Generate compelling proposal sections using provided context.

CRITICAL REQUIREMENTS:
1. Use ONLY information from the provided source documents
2. Add inline citations in format: [Document Name, p.N]
3. Stay within {word_limit} words
4. Match the required format: {section_requirements}
5. Be specific and concrete (no generic fluff)

Citation format example: "Our organization has served 5,000 families since 2020 [Annual Report 2023, p.12]."
"""
        
        user_prompt = f"""Generate the "{section_name}" section for a grant proposal.

SECTION REQUIREMENTS:
{section_requirements}

WORD LIMIT: {word_limit} words

RETRIEVED CONTEXT FROM ORGANIZATION'S DOCUMENTS:
{context_text}

Write a compelling, evidence-based section with inline citations."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.chat_completion(
            messages=messages,
            model=self.drafting_model,
            temperature=self.drafting_temp,
            max_tokens=word_limit * 2  # Rough estimate: 1 word ≈ 1.3 tokens
        )
    
    def generate_section_from_prompt(self, prompt: str) -> str:
        """Generate section from a complete prompt.
        
        Simpler interface for section_generator agent that builds its own prompts.
        
        Args:
            prompt: Complete generation prompt
            
        Returns:
            Generated text
        """
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(
            messages=messages,
            model=self.drafting_model,
            temperature=self.drafting_temp,
            max_tokens=600  # Reduced limit for more concise section generation (was 2000)
        )
    
    def quality_check(self, section_text: str, requirements: str) -> Dict[str, Any]:
        """Run quality checks on generated section.
        
        Uses gpt-4o with temperature 0 for consistent evaluation.
        
        Args:
            section_text: Generated section text
            requirements: Original section requirements
            
        Returns:
            Dict with pass/fail checks and issues
        """
        system_prompt = """You are a grant proposal quality checker. Evaluate if sections meet requirements.

Return JSON with this schema:
{
  "passes_requirements": true,
  "has_citations": true,
  "issues": ["Missing specific impact metrics", "..."],
  "suggestions": ["Add quantitative outcomes", "..."]
}"""
        
        user_prompt = f"""Check if this section meets requirements:

REQUIREMENTS:
{requirements}

SECTION TEXT:
{section_text}

Return quality check results as JSON."""
        
        response = self.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=self.quality_model,
            temperature=self.quality_temp,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response)


# Global LLM client instance
_llm_client = None

def get_llm_client() -> LLMClient:
    """Get singleton LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
