"""Session manager service.

In-memory session storage for MVP. Stores session data, funding calls,
and generated sections in dictionaries keyed by session_id.

Note: For production, this should be replaced with Redis or database storage.
"""

from typing import Dict, Optional, List
from backend.src.models.session import UserSession
from backend.src.models.funding_call import FundingCall
from backend.src.models.section import GeneratedSection
import uuid


class SessionManager:
    """In-memory session manager (MVP implementation)"""
    
    def __init__(self):
        """Initialize session storage"""
        # Session data
        self._sessions: Dict[str, UserSession] = {}
        
        # Funding calls by session_id
        self._funding_calls: Dict[str, FundingCall] = {}
        
        # Generated sections by session_id -> section_id
        self._sections: Dict[str, Dict[str, GeneratedSection]] = {}
        
        # File metadata by session_id
        self._uploaded_files: Dict[str, List[Dict[str, str]]] = {}
    
    def create_session(self) -> UserSession:
        """Create a new session.
        
        Returns:
            New UserSession instance
        """
        session = UserSession()
        self._sessions[session.session_id] = session
        self._sections[session.session_id] = {}
        self._uploaded_files[session.session_id] = []
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            UserSession or None if not found
        """
        return self._sessions.get(session_id)
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists
        """
        return session_id in self._sessions
    
    def update_session(self, session: UserSession):
        """Update session data.
        
        Args:
            session: Updated UserSession instance
        """
        self._sessions[session.session_id] = session
    
    def delete_session(self, session_id: str):
        """Delete all data for a session.
        
        Args:
            session_id: Session identifier
        """
        self._sessions.pop(session_id, None)
        self._funding_calls.pop(session_id, None)
        self._sections.pop(session_id, None)
        self._uploaded_files.pop(session_id, None)
    
    # Funding call methods
    
    def set_funding_call(self, funding_call: FundingCall):
        """Store funding call for a session.
        
        Args:
            funding_call: FundingCall instance
        """
        self._funding_calls[funding_call.session_id] = funding_call
    
    def get_funding_call(self, session_id: str) -> Optional[FundingCall]:
        """Get funding call for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            FundingCall or None if not found
        """
        return self._funding_calls.get(session_id)
    
    # Section methods
    
    def save_section(self, section: GeneratedSection):
        """Save generated section.
        
        Args:
            section: GeneratedSection instance
        """
        if section.session_id not in self._sections:
            self._sections[section.session_id] = {}
        
        self._sections[section.session_id][section.section_id] = section
    
    def get_section(self, session_id: str, section_id: str) -> Optional[GeneratedSection]:
        """Get generated section.
        
        Args:
            session_id: Session identifier
            section_id: Section identifier
            
        Returns:
            GeneratedSection or None if not found
        """
        session_sections = self._sections.get(session_id, {})
        return session_sections.get(section_id)
    
    def get_all_sections(self, session_id: str) -> List[GeneratedSection]:
        """Get all sections for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of GeneratedSection instances
        """
        return list(self._sections.get(session_id, {}).values())
    
    def delete_section(self, session_id: str, section_id: str):
        """Delete a section.
        
        Args:
            session_id: Session identifier
            section_id: Section identifier
        """
        if session_id in self._sections:
            self._sections[session_id].pop(section_id, None)
    
    # File tracking methods
    
    def add_uploaded_file(self, session_id: str, filename: str, file_id: str, file_type: str, is_funding_call: bool = False):
        """Track uploaded file.
        
        Args:
            session_id: Session identifier
            filename: Original filename
            file_id: Unique file identifier
            file_type: File type (pdf, docx)
            is_funding_call: Whether this is the funding call PDF
        """
        if session_id not in self._uploaded_files:
            self._uploaded_files[session_id] = []
        
        self._uploaded_files[session_id].append({
            'filename': filename,
            'file_id': file_id,
            'file_type': file_type,
            'is_funding_call': is_funding_call
        })
    
    def get_uploaded_files(self, session_id: str) -> List[Dict[str, str]]:
        """Get list of uploaded files for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of file metadata dicts
        """
        return self._uploaded_files.get(session_id, [])


# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get singleton session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
