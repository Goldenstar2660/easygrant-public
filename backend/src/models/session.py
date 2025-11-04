"""Session data model.

Tracks user sessions with upload quota enforcement.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import uuid


class UserSession(BaseModel):
    """User session with upload tracking"""
    
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session creation timestamp"
    )
    
    total_upload_size_bytes: int = Field(
        default=0,
        description="Total size of uploaded files in bytes"
    )
    
    uploaded_file_count: int = Field(
        default=0,
        description="Number of files uploaded"
    )
    
    funding_call_uploaded: bool = Field(
        default=False,
        description="Whether funding call has been uploaded"
    )
    
    funding_call_filename: Optional[str] = Field(
        default=None,
        description="Filename of uploaded funding call"
    )
    
    requirements_extracted: bool = Field(
        default=False,
        description="Whether requirements have been extracted"
    )
    
    indexed_document_count: int = Field(
        default=0,
        description="Number of documents indexed in vector store"
    )
    
    @field_validator('total_upload_size_bytes')
    @classmethod
    def validate_upload_quota(cls, v):
        """Validate total upload size doesn't exceed 50MB"""
        MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB in bytes
        if v > MAX_TOTAL_SIZE:
            raise ValueError(
                f"Total upload size {v} bytes exceeds maximum {MAX_TOTAL_SIZE} bytes (50MB)"
            )
        return v
    
    @field_validator('uploaded_file_count')
    @classmethod
    def validate_file_count(cls, v):
        """Validate file count doesn't exceed 5 supporting docs + 1 funding call"""
        MAX_FILES = 6  # 1 funding call + 5 supporting docs
        if v > MAX_FILES:
            raise ValueError(
                f"File count {v} exceeds maximum {MAX_FILES} files"
            )
        return v
    
    def can_upload_file(self, file_size_bytes: int, max_supporting_docs: int = 5) -> tuple[bool, Optional[str]]:
        """Check if a file can be uploaded within quota.
        
        Args:
            file_size_bytes: Size of file to upload
            max_supporting_docs: Maximum number of supporting documents
            
        Returns:
            Tuple of (can_upload, error_message)
        """
        MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB
        
        # Check total size quota
        if self.total_upload_size_bytes + file_size_bytes > MAX_TOTAL_SIZE:
            remaining_mb = (MAX_TOTAL_SIZE - self.total_upload_size_bytes) / (1024 * 1024)
            return False, f"Upload would exceed 50MB quota. Remaining: {remaining_mb:.1f}MB"
        
        # Check file count (excluding funding call from supporting doc count)
        supporting_doc_count = self.uploaded_file_count
        if self.funding_call_uploaded:
            supporting_doc_count -= 1
        
        if supporting_doc_count >= max_supporting_docs and not self.funding_call_uploaded:
            return False, f"Maximum {max_supporting_docs} supporting documents already uploaded"
        
        return True, None
    
    def add_upload(self, file_size_bytes: int, is_funding_call: bool = False, filename: Optional[str] = None):
        """Record a successful file upload.
        
        Args:
            file_size_bytes: Size of uploaded file
            is_funding_call: Whether this is the funding call document
            filename: Name of uploaded file
        """
        self.total_upload_size_bytes += file_size_bytes
        self.uploaded_file_count += 1
        
        if is_funding_call:
            self.funding_call_uploaded = True
            self.funding_call_filename = filename
    
    def get_quota_status(self) -> dict:
        """Get current quota usage status.
        
        Returns:
            Dict with quota information
        """
        MAX_TOTAL_SIZE = 50 * 1024 * 1024
        MAX_FILES = 5  # Supporting docs only
        
        supporting_doc_count = self.uploaded_file_count
        if self.funding_call_uploaded:
            supporting_doc_count -= 1
        
        return {
            'total_size_mb': self.total_upload_size_bytes / (1024 * 1024),
            'max_size_mb': MAX_TOTAL_SIZE / (1024 * 1024),
            'size_remaining_mb': (MAX_TOTAL_SIZE - self.total_upload_size_bytes) / (1024 * 1024),
            'supporting_docs_count': supporting_doc_count,
            'max_supporting_docs': MAX_FILES,
            'funding_call_uploaded': self.funding_call_uploaded
        }
