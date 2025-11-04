"""File validation utilities.

Validates file types using magic bytes and enforces size limits.
"""

from typing import Tuple, Optional


# Magic bytes for file type detection
MAGIC_BYTES = {
    'pdf': b'%PDF',
    'docx': b'PK\x03\x04',  # DOCX is a ZIP file
    'doc': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'  # Legacy DOC format
}

# File size limits (from config.yaml)
MAX_FUNDING_CALL_SIZE = 10 * 1024 * 1024  # 10MB
MAX_SUPPORTING_DOC_SIZE = 10 * 1024 * 1024  # 10MB per file
MAX_TOTAL_SUPPORTING_SIZE = 50 * 1024 * 1024  # 50MB total


def validate_file_type(file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """Validate file type using magic bytes.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_content:
        return False, "File is empty"
    
    # Check file extension
    filename_lower = filename.lower()
    if not (filename_lower.endswith('.pdf') or 
            filename_lower.endswith('.docx') or 
            filename_lower.endswith('.doc')):
        return False, f"Unsupported file type. Only PDF and DOCX allowed. Got: {filename}"
    
    # Check magic bytes
    if filename_lower.endswith('.pdf'):
        if not file_content.startswith(MAGIC_BYTES['pdf']):
            return False, "File claims to be PDF but magic bytes don't match"
    elif filename_lower.endswith('.docx'):
        if not file_content.startswith(MAGIC_BYTES['docx']):
            return False, "File claims to be DOCX but magic bytes don't match"
    elif filename_lower.endswith('.doc'):
        # Legacy DOC format (less common)
        if not file_content.startswith(MAGIC_BYTES['doc']):
            return False, "File claims to be DOC but magic bytes don't match"
    
    return True, None


def validate_file_size(
    file_size: int,
    is_funding_call: bool = False,
    current_total_size: int = 0
) -> Tuple[bool, Optional[str]]:
    """Validate file size against limits.
    
    Args:
        file_size: Size of file in bytes
        is_funding_call: Whether this is the funding call document
        current_total_size: Current total upload size for session
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if is_funding_call:
        if file_size > MAX_FUNDING_CALL_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_mb = MAX_FUNDING_CALL_SIZE / (1024 * 1024)
            return False, f"Funding call exceeds {max_mb}MB limit. File is {size_mb:.1f}MB"
    else:
        # Supporting document
        if file_size > MAX_SUPPORTING_DOC_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_mb = MAX_SUPPORTING_DOC_SIZE / (1024 * 1024)
            return False, f"Supporting document exceeds {max_mb}MB limit. File is {size_mb:.1f}MB"
        
        # Check total size quota
        new_total = current_total_size + file_size
        if new_total > MAX_TOTAL_SUPPORTING_SIZE:
            remaining_mb = (MAX_TOTAL_SUPPORTING_SIZE - current_total_size) / (1024 * 1024)
            file_mb = file_size / (1024 * 1024)
            return False, f"Upload would exceed 50MB quota. File is {file_mb:.1f}MB, remaining quota: {remaining_mb:.1f}MB"
    
    return True, None


def validate_funding_call_pdf(file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """Validate funding call file (must be PDF).
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Funding call must be PDF
    if not filename.lower().endswith('.pdf'):
        return False, "Funding call must be PDF format"
    
    # Check magic bytes
    if not file_content.startswith(MAGIC_BYTES['pdf']):
        return False, "File claims to be PDF but magic bytes don't match"
    
    # Check size
    file_size = len(file_content)
    is_valid, error = validate_file_size(file_size, is_funding_call=True)
    if not is_valid:
        return False, error
    
    return True, None


def get_file_type(filename: str) -> Optional[str]:
    """Get file type from filename.
    
    Args:
        filename: Original filename
        
    Returns:
        File type ('pdf', 'docx', 'doc') or None
    """
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        return 'pdf'
    elif filename_lower.endswith('.docx'):
        return 'docx'
    elif filename_lower.endswith('.doc'):
        return 'doc'
    return None


def format_file_size(size_bytes: int) -> str:
    """Format file size for display.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size (e.g., "5.2MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
