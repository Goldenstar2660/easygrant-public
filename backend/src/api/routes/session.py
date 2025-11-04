"""Session management endpoints.

Handles session creation and retrieval.
"""

from fastapi import APIRouter
from backend.src.services.session_manager import get_session_manager


router = APIRouter(prefix="/api/session", tags=["session"])


@router.post("/create")
async def create_session():
    """Create a new session.
    
    Returns:
        New session with session_id and quota info
    """
    session_manager = get_session_manager()
    session = session_manager.create_session()
    
    return {
        'session_id': session.session_id,
        'created_at': session.created_at.isoformat(),
        'quota': session.get_quota_status()
    }


@router.get("/{session_id}")
async def get_session_info(session_id: str):
    """Get session information.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session details and quota status
    """
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        return {'error': 'Session not found'}, 404
    
    return {
        'session_id': session.session_id,
        'created_at': session.created_at.isoformat(),
        'quota': session.get_quota_status(),
        'funding_call_uploaded': session.funding_call_uploaded,
        'requirements_extracted': session.requirements_extracted,
        'indexed_document_count': session.indexed_document_count
    }
