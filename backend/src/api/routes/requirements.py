"""Requirements extraction API endpoints.

GET /api/requirements/{session_id} - Extract requirements from uploaded funding call
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from ...services.session_manager import get_session_manager
from ...utils.file_storage import get_file_storage
from ...agents.requirements_extractor import RequirementsExtractor

router = APIRouter(prefix="/api/requirements", tags=["requirements"])
logger = logging.getLogger(__name__)

# Initialize services
session_manager = get_session_manager()  # Use singleton
file_storage = get_file_storage()  # Use singleton
requirements_extractor = RequirementsExtractor()


# Response models
class SectionRequirement(BaseModel):
    """Individual section requirement"""
    name: str
    required: bool
    word_limit: Optional[int] = None
    char_limit: Optional[int] = None
    format: str
    scoring_weight: Optional[float] = None


class ScoringCriterion(BaseModel):
    """Individual scoring/evaluation criterion"""
    criteria: str
    weight: Optional[float] = None


class RequirementsBlueprint(BaseModel):
    """Complete requirements blueprint"""
    sections: List[SectionRequirement]
    eligibility: List[str]
    scoring_criteria: List[ScoringCriterion]
    deadline: Optional[str] = None
    total_sections: int


@router.get("/{session_id}", response_model=RequirementsBlueprint)
async def get_requirements(session_id: str):
    """Extract requirements from uploaded funding call PDF.
    
    Args:
        session_id: Session identifier
        
    Returns:
        RequirementsBlueprint with structured requirements
        
    Raises:
        404: Session not found or no funding call uploaded
        500: Extraction failed after retries
    """
    try:
        # 1. Verify session exists
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # 2. Check if funding call uploaded
        if not session.funding_call_uploaded:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No funding call uploaded for this session. Please upload a funding call PDF first."
            )
        
        # 3. Get funding call file ID from uploaded files
        uploaded_files = session_manager.get_uploaded_files(session_id)
        funding_call_file = next(
            (f for f in uploaded_files if f.get('file_type') == 'pdf' and f.get('is_funding_call')),
            None
        )
        
        if not funding_call_file:
            # Fallback: get first PDF file (for backward compatibility)
            funding_call_file = next(
                (f for f in uploaded_files if f.get('file_type') == 'pdf'),
                None
            )
        
        if not funding_call_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Funding call file not found in uploaded files"
            )
        
        funding_call_id = funding_call_file['file_id']
        file_path = file_storage.get_file_path(session_id, funding_call_id, '.pdf')
        
        if not file_path or not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Funding call file not found: {funding_call_id}"
            )
        
        # 4. Extract requirements using agent
        logger.info(f"Extracting requirements for session {session_id}")
        blueprint = requirements_extractor.extract_requirements(
            file_path=str(file_path),
            session_id=session_id,
            max_retries=2
        )
        
        # 5. Store blueprint in session storage (not in UserSession model)
        # Note: UserSession is a Pydantic model and doesn't support arbitrary fields
        # We'll store it in a separate storage dict in session_manager
        if not hasattr(session_manager, '_requirements_cache'):
            session_manager._requirements_cache = {}
        session_manager._requirements_cache[session_id] = blueprint
        
        # 6. Log summary
        summary = requirements_extractor.get_blueprint_summary(blueprint)
        logger.info(f"Requirements extracted:\n{summary}")
        
        return blueprint
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Requirements extraction failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Requirements extraction failed: {str(e)}"
        )


@router.get("/{session_id}/summary")
async def get_requirements_summary(session_id: str):
    """Get human-readable summary of requirements.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dict with summary text and counts
        
    Raises:
        404: Session not found or requirements not extracted
    """
    try:
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Check if blueprint exists in cache
        if not hasattr(session_manager, '_requirements_cache'):
            session_manager._requirements_cache = {}
        
        blueprint = session_manager._requirements_cache.get(session_id)
        if not blueprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirements not extracted yet. Call GET /api/requirements/{session_id} first."
            )
        
        # Generate summary
        summary = requirements_extractor.get_blueprint_summary(blueprint)
        
        sections = blueprint.get("sections", [])
        required_count = sum(1 for s in sections if s.get("required", False))
        
        return {
            "summary": summary,
            "total_sections": len(sections),
            "required_sections": required_count,
            "optional_sections": len(sections) - required_count,
            "eligibility_count": len(blueprint.get("eligibility", [])),
            "has_deadline": blueprint.get("deadline") is not None,
            "extracted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )
