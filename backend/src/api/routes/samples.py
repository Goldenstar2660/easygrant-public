"""Sample PDF endpoints for demo/hackathon purposes.

Serves example PDFs for easy testing by judges.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/samples", tags=["samples"])

# Sample PDF paths - use absolute paths relative to app root
# In development: ./samples/
# In Docker: /app/samples/
APP_ROOT = Path(__file__).parent.parent.parent.parent.parent  # backend/src/api/routes/samples.py -> project root
SAMPLE_FUNDING_CALL = APP_ROOT / "samples" / "Sample_Funding_Call.pdf"
SAMPLE_SUPPORTING_DOC = APP_ROOT / "samples" / "Sample_Supporting_Document.pdf"


@router.get("/funding-call")
async def get_sample_funding_call():
    """
    Get sample funding call PDF for demo purposes.
    
    Returns:
        FileResponse with sample funding call PDF
    """
    logger.info("[SAMPLES] Request for sample funding call PDF")
    
    if not SAMPLE_FUNDING_CALL.exists():
        logger.error(f"[SAMPLES] Sample funding call not found at {SAMPLE_FUNDING_CALL.absolute()}")
        raise HTTPException(
            status_code=404,
            detail="Sample funding call PDF not found"
        )
    
    logger.info(f"[SAMPLES] Serving sample funding call: {SAMPLE_FUNDING_CALL.name}")
    return FileResponse(
        path=str(SAMPLE_FUNDING_CALL.absolute()),
        media_type="application/pdf",
        filename="Sample_Funding_Call.pdf"
    )


@router.get("/supporting-document")
async def get_sample_supporting_document():
    """
    Get sample supporting document PDF for demo purposes.
    
    Returns:
        FileResponse with sample supporting document PDF
    """
    logger.info("[SAMPLES] Request for sample supporting document PDF")
    
    if not SAMPLE_SUPPORTING_DOC.exists():
        logger.error(f"[SAMPLES] Sample supporting doc not found at {SAMPLE_SUPPORTING_DOC.absolute()}")
        raise HTTPException(
            status_code=404,
            detail="Sample supporting document PDF not found"
        )
    
    logger.info(f"[SAMPLES] Serving sample supporting doc: {SAMPLE_SUPPORTING_DOC.name}")
    return FileResponse(
        path=str(SAMPLE_SUPPORTING_DOC.absolute()),
        media_type="application/pdf",
        filename="Sample_Supporting_Document.pdf"
    )
