"""Export API endpoints.

Generate and export proposal documents in various formats.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from ...services.session_manager import get_session_manager
from ...agents.assembler import Assembler

router = APIRouter(prefix="/api/export", tags=["export"])
logger = logging.getLogger(__name__)

# Initialize services
session_manager = get_session_manager()
assembler = Assembler()


class ExportRequest(BaseModel):
    """Request to export proposal as DOCX"""
    session_id: str
    section_names: Optional[List[str]] = None  # If None, export all sections
    program_name: Optional[str] = None


@router.post("/docx")
async def export_docx(request: ExportRequest):
    """Export proposal sections as DOCX document.
    
    Args:
        request: Export parameters including session_id and optional section_names
        
    Returns:
        StreamingResponse with DOCX file
        
    Raises:
        404: Session not found or no sections generated
        500: Export failed
    """
    logger.info(f"[EXPORT API] ========== POST /docx ==========")
    logger.info(f"[EXPORT API] Session ID: {request.session_id}")
    logger.info(f"[EXPORT API] Requested sections: {request.section_names}")
    logger.info(f"[EXPORT API] Program name: {request.program_name}")
    
    try:
        # 1. Validate session
        logger.debug("[EXPORT API] Validating session")
        session = session_manager.get_session(request.session_id)
        if not session:
            logger.warning(f"[EXPORT API] Session not found: {request.session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        logger.debug(f"[EXPORT API] Session validated: {request.session_id}")
        
        # 2. Get funding call info
        logger.debug("[EXPORT API] Retrieving funding call info")
        funding_call = session_manager.get_funding_call(request.session_id)
        funding_call_name = None
        if funding_call:
            funding_call_name = funding_call.program_name or funding_call.document_filename
            logger.info(f"[EXPORT API] Funding call name: {funding_call_name}")
        else:
            logger.warning("[EXPORT API] No funding call found for session")
        
        # 3. Get sections from the in-memory storage in sections.py
        # Import the storage from sections route
        logger.debug("[EXPORT API] Importing section storage")
        from .sections import _generated_sections
        
        session_sections = _generated_sections.get(request.session_id, {})
        logger.info(f"[EXPORT API] Found {len(session_sections)} total sections in storage")
        logger.info(f"[EXPORT API] Available sections: {list(session_sections.keys())}")
        
        if not session_sections:
            logger.warning("[EXPORT API] No sections have been generated yet")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sections have been generated yet. Please generate at least one section before exporting."
            )
        
        # 4. Filter sections if specific names requested
        if request.section_names:
            logger.debug(f"[EXPORT API] Filtering for specific sections: {request.section_names}")
            sections_to_export = {
                name: data for name, data in session_sections.items()
                if name in request.section_names
            }
            
            if not sections_to_export:
                logger.warning(
                    f"[EXPORT API] None of requested sections found. "
                    f"Requested: {request.section_names}, Available: {list(session_sections.keys())}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"None of the requested sections found: {request.section_names}"
                )
            logger.info(f"[EXPORT API] Filtered to {len(sections_to_export)} sections")
        else:
            logger.debug("[EXPORT API] Exporting all available sections")
            sections_to_export = session_sections
        
        logger.info(
            f"[EXPORT API] Sections to export: {list(sections_to_export.keys())}"
        )
        
        # 5. Prepare section data for assembler
        # Get funding call blueprint for section ordering if available
        logger.debug("[EXPORT API] Preparing section data for assembler")
        section_order = []
        if funding_call and funding_call.sections:
            section_order = [s.name for s in funding_call.sections]
            logger.debug(f"[EXPORT API] Blueprint section order: {section_order}")
        else:
            logger.debug("[EXPORT API] No blueprint available, using alphabetical order")
        
        # Sort sections according to blueprint order (or alphabetically if no blueprint)
        sections_list = []
        for section_name in section_order:
            if section_name in sections_to_export:
                sections_list.append(sections_to_export[section_name])
                logger.debug(f"[EXPORT API] Added section from blueprint: {section_name}")
        
        # Add any sections not in blueprint
        for section_name, section_data in sections_to_export.items():
            if section_name not in section_order:
                sections_list.append(section_data)
                logger.debug(f"[EXPORT API] Added section not in blueprint: {section_name}")
        
        # If no blueprint, just use all sections in any order
        if not sections_list:
            sections_list = list(sections_to_export.values())
            logger.debug(f"[EXPORT API] Using all sections without ordering: {len(sections_list)}")
        
        logger.info(f"[EXPORT API] Final section count: {len(sections_list)}")
        for i, section in enumerate(sections_list):
            logger.info(
                f"[EXPORT API] Section {i+1}: '{section.get('section_name')}' "
                f"({section.get('word_count', 0)} words)"
            )
        
        # 6. Assemble DOCX
        logger.info("[EXPORT API] Starting DOCX assembly...")
        try:
            doc = assembler.assemble_proposal(
                sections=sections_list,
                funding_call_name=funding_call_name,
                program_name=request.program_name
            )
            logger.info("[EXPORT API] DOCX assembly successful")
        except Exception as e:
            logger.error(f"[EXPORT API] DOCX assembly failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"DOCX assembly failed: {str(e)}"
            )
        
        # 7. Convert to bytes
        logger.debug("[EXPORT API] Converting document to bytes...")
        try:
            docx_bytes = assembler.get_docx_bytes(doc)
            logger.info(f"[EXPORT API] Document converted: {len(docx_bytes)} bytes")
        except Exception as e:
            logger.error(f"[EXPORT API] Bytes conversion failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document conversion failed: {str(e)}"
            )
        
        # 8. Create filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"Proposal_{timestamp}.docx"
        logger.info(f"[EXPORT API] Generated filename: {filename}")
        
        logger.info(
            f"[EXPORT API] ========== Export successful: {len(docx_bytes)} bytes ==========")
        
        # 9. Return as Response with proper headers
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[EXPORT API] DOCX export failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DOCX export failed: {str(e)}"
        )
