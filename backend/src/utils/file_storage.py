"""File storage utility for uploaded documents.

Saves files to /data/uploads/{session_id}/ with UUID filenames.
Tracks file metadata in session manager.
"""

import os
import uuid
from pathlib import Path
from typing import Tuple, Optional


class FileStorage:
    """Handles file storage for uploaded documents"""
    
    def __init__(self, base_upload_dir: str = "./data/uploads"):
        """Initialize file storage.
        
        Args:
            base_upload_dir: Base directory for all uploads
        """
        self.base_dir = Path(base_upload_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_session_dir(self, session_id: str) -> Path:
        """Get upload directory for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to session's upload directory
        """
        session_dir = self.base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    def save_file(
        self,
        session_id: str,
        file_content: bytes,
        original_filename: str
    ) -> Tuple[str, str]:
        """Save uploaded file with UUID filename.
        
        Args:
            session_id: Session identifier
            file_content: Raw file bytes
            original_filename: Original filename (for extension)
            
        Returns:
            Tuple of (file_id, saved_path)
        """
        # Generate UUID filename
        file_id = str(uuid.uuid4())
        
        # Preserve original extension
        extension = Path(original_filename).suffix.lower()
        filename = f"{file_id}{extension}"
        
        # Get session directory
        session_dir = self.get_session_dir(session_id)
        file_path = session_dir / filename
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_id, str(file_path)
    
    def get_file_path(self, session_id: str, file_id: str, extension: str) -> Optional[str]:
        """Get path to a stored file.
        
        Args:
            session_id: Session identifier
            file_id: File UUID
            extension: File extension (e.g., '.pdf')
            
        Returns:
            Path to file or None if not found
        """
        filename = f"{file_id}{extension}"
        file_path = self.get_session_dir(session_id) / filename
        
        if file_path.exists():
            return str(file_path)
        return None
    
    def delete_session_files(self, session_id: str) -> bool:
        """Delete all files for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        session_dir = self.get_session_dir(session_id)
        
        if not session_dir.exists():
            return True
        
        # Delete all files in session directory
        for file_path in session_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
        
        # Remove directory
        session_dir.rmdir()
        return True
    
    def get_file_size(self, session_id: str, file_id: str, extension: str) -> Optional[int]:
        """Get size of stored file.
        
        Args:
            session_id: Session identifier
            file_id: File UUID
            extension: File extension
            
        Returns:
            File size in bytes or None if not found
        """
        file_path = self.get_file_path(session_id, file_id, extension)
        if file_path and os.path.exists(file_path):
            return os.path.getsize(file_path)
        return None
    
    def list_session_files(self, session_id: str) -> list:
        """List all files for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of dicts with file info
        """
        session_dir = self.get_session_dir(session_id)
        
        if not session_dir.exists():
            return []
        
        files = []
        for file_path in session_dir.iterdir():
            if file_path.is_file():
                files.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size
                })
        
        return files


# Global file storage instance
_file_storage = None

def get_file_storage() -> FileStorage:
    """Get singleton file storage instance"""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorage()
    return _file_storage
