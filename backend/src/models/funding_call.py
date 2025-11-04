"""Funding call and blueprint data models.

Represents structured requirements extracted from funding calls.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SectionBlueprint(BaseModel):
    """Blueprint for a single proposal section"""
    
    name: str = Field(
        ...,
        description="Section name (e.g., 'Project Summary')"
    )
    
    required: bool = Field(
        default=True,
        description="Whether this section is mandatory"
    )
    
    word_limit: Optional[int] = Field(
        default=None,
        description="Maximum word count (null if no limit)"
    )
    
    character_limit: Optional[int] = Field(
        default=None,
        description="Maximum character count (null if no limit)"
    )
    
    page_limit: Optional[int] = Field(
        default=None,
        description="Maximum page count (null if no limit)"
    )
    
    format: str = Field(
        default="Narrative text",
        description="Expected format/content description"
    )
    
    scoring_weight: Optional[int] = Field(
        default=None,
        description="Points or percentage weight in scoring"
    )
    
    def get_limit_display(self) -> str:
        """Get human-readable limit string.
        
        Returns:
            Limit description (e.g., "500 words", "2000 characters", "No limit")
        """
        if self.word_limit:
            return f"{self.word_limit} words"
        elif self.character_limit:
            return f"{self.character_limit} characters"
        elif self.page_limit:
            return f"{self.page_limit} pages"
        else:
            return "No limit"


class ScoringCriteria(BaseModel):
    """Scoring criteria for proposal evaluation"""
    
    total_points: int = Field(
        default=100,
        description="Total points available"
    )
    
    criteria: List[str] = Field(
        default_factory=list,
        description="List of scoring criteria with point values"
    )
    
    notes: Optional[str] = Field(
        default=None,
        description="Additional scoring notes"
    )


class FundingCall(BaseModel):
    """Structured representation of a funding call"""
    
    session_id: str = Field(
        ...,
        description="Session ID this funding call belongs to"
    )
    
    document_filename: str = Field(
        ...,
        description="Original filename of funding call PDF"
    )
    
    sections: List[SectionBlueprint] = Field(
        default_factory=list,
        description="Required proposal sections"
    )
    
    eligibility: List[str] = Field(
        default_factory=list,
        description="Eligibility requirements"
    )
    
    scoring: Optional[ScoringCriteria] = Field(
        default=None,
        description="Scoring criteria and point allocation"
    )
    
    deadline: Optional[str] = Field(
        default=None,
        description="Application deadline (extracted if found)"
    )
    
    program_name: Optional[str] = Field(
        default=None,
        description="Funding program name"
    )
    
    total_award_amount: Optional[str] = Field(
        default=None,
        description="Total funding available (e.g., '$50,000 - $250,000')"
    )
    
    extracted_at: Optional[str] = Field(
        default=None,
        description="Timestamp when requirements were extracted"
    )
    
    raw_text: Optional[str] = Field(
        default=None,
        description="Full text of funding call (for reference)"
    )
    
    def get_total_word_limit(self) -> int:
        """Calculate total word limit across all sections.
        
        Returns:
            Sum of word limits (0 if none specified)
        """
        return sum(s.word_limit or 0 for s in self.sections)
    
    def get_required_sections(self) -> List[SectionBlueprint]:
        """Get only required sections.
        
        Returns:
            List of required section blueprints
        """
        return [s for s in self.sections if s.required]
    
    def get_section_by_name(self, name: str) -> Optional[SectionBlueprint]:
        """Find section by name.
        
        Args:
            name: Section name to search for
            
        Returns:
            SectionBlueprint or None if not found
        """
        for section in self.sections:
            if section.name.lower() == name.lower():
                return section
        return None
    
    def to_checklist_format(self) -> List[Dict[str, Any]]:
        """Convert to checklist format for frontend.
        
        Returns:
            List of dicts with section info for UI display
        """
        checklist = []
        for i, section in enumerate(self.sections):
            checklist.append({
                'id': i,
                'name': section.name,
                'required': section.required,
                'limit': section.get_limit_display(),
                'format': section.format,
                'scoring_weight': section.scoring_weight,
                'status': 'not_started',  # Will be updated as sections are generated
                'completed': False
            })
        return checklist
