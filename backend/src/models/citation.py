"""Citation data model.

Represents inline citations linking generated text to source documents.
"""

from pydantic import BaseModel, Field
from typing import Optional


class Citation(BaseModel):
    """Citation linking generated text to source document"""
    
    document_id: str = Field(
        ...,
        description="Unique identifier of source document"
    )
    
    document_title: str = Field(
        ...,
        description="Human-readable document name (usually filename)"
    )
    
    page_number: int = Field(
        ...,
        description="Page number in source document (1-indexed)"
    )
    
    chunk_text: str = Field(
        ...,
        description="Original text chunk that was cited"
    )
    
    chunk_id: Optional[str] = Field(
        default=None,
        description="ID of chunk in vector store"
    )
    
    relevance_score: Optional[float] = Field(
        default=None,
        description="Relevance score from vector search (0-1)"
    )
    
    def to_inline_format(self) -> str:
        """Convert to inline citation format.
        
        Returns:
            Citation string like "[Annual Report 2023, p.12]"
        """
        return f"[{self.document_title}, p.{self.page_number}]"
    
    def to_short_format(self) -> str:
        """Convert to short citation format (doc name only).
        
        Returns:
            Short citation like "[Annual Report 2023]"
        """
        return f"[{self.document_title}]"
    
    def get_snippet(self, max_chars: int = 150) -> str:
        """Get truncated snippet of cited text.
        
        Args:
            max_chars: Maximum characters to include
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if len(self.chunk_text) <= max_chars:
            return self.chunk_text
        return self.chunk_text[:max_chars] + "..."
