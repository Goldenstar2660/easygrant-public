"""Section data models.

Represents proposal sections with requirements and generated content.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.src.models.citation import Citation


class LockedParagraph(BaseModel):
    """Represents a user-locked paragraph that should persist across regenerations"""
    
    index: int = Field(
        ...,
        description="Paragraph index in section (0-based)"
    )
    
    text: str = Field(
        ...,
        description="User-edited paragraph text"
    )
    
    locked_at: Optional[str] = Field(
        default=None,
        description="Timestamp when paragraph was locked"
    )


class SectionRequirement(BaseModel):
    """Requirements for a proposal section (from funding call)"""
    
    section_id: str = Field(
        ...,
        description="Unique section identifier"
    )
    
    name: str = Field(
        ...,
        description="Section name (e.g., 'Project Summary')"
    )
    
    required: bool = Field(
        default=True,
        description="Whether section is mandatory"
    )
    
    word_limit: Optional[int] = Field(
        default=None,
        description="Maximum word count"
    )
    
    format_requirements: str = Field(
        default="",
        description="Format and content requirements"
    )
    
    scoring_weight: Optional[int] = Field(
        default=None,
        description="Points or weight in scoring"
    )


class GeneratedSection(BaseModel):
    """Generated proposal section with AI content and citations"""
    
    section_id: str = Field(
        ...,
        description="Unique section identifier (matches SectionRequirement)"
    )
    
    session_id: str = Field(
        ...,
        description="Session this section belongs to"
    )
    
    name: str = Field(
        ...,
        description="Section name"
    )
    
    ai_generated_text: str = Field(
        default="",
        description="AI-generated section text with inline citations"
    )
    
    word_count: int = Field(
        default=0,
        description="Current word count"
    )
    
    citations: List[Citation] = Field(
        default_factory=list,
        description="Citations used in this section"
    )
    
    locked_paragraphs: List[LockedParagraph] = Field(
        default_factory=list,
        description="User-locked paragraphs (preserved during regeneration)"
    )
    
    generated_at: Optional[str] = Field(
        default=None,
        description="Timestamp of generation"
    )
    
    regeneration_count: int = Field(
        default=0,
        description="Number of times section has been regenerated"
    )
    
    quality_check: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Quality check results from LLM"
    )
    
    def count_words(self) -> int:
        """Count words in generated text.
        
        Returns:
            Word count
        """
        if not self.ai_generated_text:
            return 0
        # Simple word count (split on whitespace)
        return len(self.ai_generated_text.split())
    
    def exceeds_limit(self, word_limit: Optional[int]) -> bool:
        """Check if section exceeds word limit.
        
        Args:
            word_limit: Maximum allowed words
            
        Returns:
            True if exceeds limit
        """
        if word_limit is None:
            return False
        return self.word_count > word_limit
    
    def within_threshold(self, word_limit: Optional[int], threshold_percent: float = 10.0) -> bool:
        """Check if section is within threshold of limit.
        
        Args:
            word_limit: Maximum allowed words
            threshold_percent: Warning threshold (default 10%)
            
        Returns:
            True if within threshold of limit
        """
        if word_limit is None:
            return False
        threshold = word_limit * (1 - threshold_percent / 100)
        return self.word_count >= threshold
    
    def get_limit_status(self, word_limit: Optional[int]) -> str:
        """Get status color for UI.
        
        Args:
            word_limit: Maximum allowed words
            
        Returns:
            Status: 'ok', 'warning', 'exceeded'
        """
        if word_limit is None:
            return 'ok'
        
        if self.exceeds_limit(word_limit):
            return 'exceeded'
        elif self.within_threshold(word_limit):
            return 'warning'
        else:
            return 'ok'
    
    def split_into_paragraphs(self) -> List[str]:
        """Split generated text into paragraphs.
        
        Returns:
            List of paragraph texts (split on double newlines)
        """
        if not self.ai_generated_text:
            return []
        
        # Split on double newline (paragraph separator)
        paragraphs = self.ai_generated_text.split('\n\n')
        # Filter empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]
    
    def is_paragraph_locked(self, paragraph_index: int) -> bool:
        """Check if a paragraph is locked.
        
        Args:
            paragraph_index: 0-based paragraph index
            
        Returns:
            True if paragraph is locked
        """
        return any(lp.index == paragraph_index for lp in self.locked_paragraphs)
    
    def lock_paragraph(self, paragraph_index: int, text: str):
        """Lock a paragraph to preserve during regeneration.
        
        Args:
            paragraph_index: 0-based paragraph index
            text: Paragraph text to preserve
        """
        # Remove existing lock if present
        self.locked_paragraphs = [
            lp for lp in self.locked_paragraphs if lp.index != paragraph_index
        ]
        
        # Add new lock
        from datetime import datetime
        self.locked_paragraphs.append(LockedParagraph(
            index=paragraph_index,
            text=text,
            locked_at=datetime.utcnow().isoformat()
        ))
    
    def merge_with_locked_paragraphs(self, new_text: str) -> str:
        """Merge new AI text with locked paragraphs.
        
        Args:
            new_text: Newly generated text
            
        Returns:
            Merged text with locked paragraphs preserved
        """
        if not self.locked_paragraphs:
            return new_text
        
        # Split new text into paragraphs
        new_paragraphs = new_text.split('\n\n')
        new_paragraphs = [p.strip() for p in new_paragraphs if p.strip()]
        
        # Create dict of locked paragraphs by index
        locked_dict = {lp.index: lp.text for lp in self.locked_paragraphs}
        
        # Merge: use locked text where available, otherwise use new text
        merged_paragraphs = []
        for i in range(max(len(new_paragraphs), max(locked_dict.keys(), default=-1) + 1)):
            if i in locked_dict:
                merged_paragraphs.append(locked_dict[i])
            elif i < len(new_paragraphs):
                merged_paragraphs.append(new_paragraphs[i])
        
        return '\n\n'.join(merged_paragraphs)
