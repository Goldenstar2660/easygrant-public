"""Upload endpoints for funding call and supporting documents.

Handles file upload, validation, storage, and indexing.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import List
import os
import logging

logger = logging.getLogger(__name__)

from backend.src.services.session_manager import get_session_manager
from backend.src.utils.file_storage import get_file_storage
from backend.src.utils.file_validation import (
    validate_funding_call_pdf,
    validate_file_type,
    validate_file_size,
    get_file_type,
    format_file_size
)
from backend.src.services.indexing_service import get_indexing_service
from backend.src.api.middleware import get_session_from_request


router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/funding-call")
async def upload_funding_call(
    request: Request,
    file: UploadFile = File(...)
):
    """Upload funding call PDF.
    
    - **file**: PDF file (max 10MB)
    - **session_id**: Required in query params or X-Session-ID header
    
    Returns:
        Upload status and indexing results
    """
    # Get session from middleware
    session = get_session_from_request(request)
    session_manager = get_session_manager()
    
    logger.info(f"[FUNDING UPLOAD] Received request - Session ID: {session.session_id}, Filename: {file.filename}")
    logger.info(f"[FUNDING UPLOAD] Funding call already uploaded: {session.funding_call_uploaded}")
    
    # Check if funding call already uploaded
    if session.funding_call_uploaded:
        logger.warning(f"[FUNDING UPLOAD] Funding call already uploaded for session {session.session_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Funding call already uploaded for this session"
        )
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    logger.info(f"[FUNDING UPLOAD] File size: {file_size} bytes")
    
    # Validate funding call (must be PDF)
    is_valid, error_msg = validate_funding_call_pdf(file_content, file.filename)
    if not is_valid:
        logger.error(f"[FUNDING UPLOAD] Validation failed: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    logger.info(f"[FUNDING UPLOAD] Validation passed")
    
    # Save file
    file_storage = get_file_storage()
    file_id, file_path = file_storage.save_file(
        session_id=session.session_id,
        file_content=file_content,
        original_filename=file.filename
    )
    logger.info(f"[FUNDING UPLOAD] File saved - ID: {file_id}, Path: {file_path}")
    
    # Update session
    session.add_upload(file_size, is_funding_call=True, filename=file.filename)
    session_manager.update_session(session)
    logger.info(f"[FUNDING UPLOAD] Session updated - funding_call_uploaded: {session.funding_call_uploaded}")
    
    # Track uploaded file
    session_manager.add_uploaded_file(
        session_id=session.session_id,
        filename=file.filename,
        file_id=file_id,
        file_type='pdf',
        is_funding_call=True
    )
    logger.info(f"[FUNDING UPLOAD] File tracked in session manager")
    
    # Index document (blocking operation)
    indexing_service = get_indexing_service()
    logger.info(f"[FUNDING UPLOAD] Starting indexing...")
    index_result = indexing_service.index_document(
        session_id=session.session_id,
        file_path=file_path,
        document_id=file_id,
        document_title=file.filename
    )
    logger.info(f"[FUNDING UPLOAD] Indexing complete - Success: {index_result['success']}, Chunks: {index_result.get('chunk_count', 0)}")
    
    if not index_result['success']:
        # File was saved but indexing failed
        logger.error(f"[FUNDING UPLOAD] Indexing failed: {index_result.get('error')}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'uploaded': True,
                'indexed': False,
                'error': index_result.get('error', 'Indexing failed'),
                'file_id': file_id,
                'filename': file.filename,
                'size': format_file_size(file_size)
            }
        )
    
    response = {
        'uploaded': True,
        'indexed': True,
        'file_id': file_id,
        'filename': file.filename,
        'size': format_file_size(file_size),
        'chunk_count': index_result['chunk_count'],
        'quota': session.get_quota_status()
    }
    logger.info(f"[FUNDING UPLOAD] Success - returning response with quota: {response['quota']}")
    return response


@router.post("/supporting-docs")
async def upload_supporting_docs(
    request: Request,
    files: List[UploadFile] = File(...)
):
    """Upload supporting documents (PDF or DOCX).
    
    - **files**: List of files (max 5 files, 50MB total)
    - **session_id**: Required in query params or X-Session-ID header
    
    Returns:
        Upload status and indexing results for each file
    """
    # Get session from middleware
    session = get_session_from_request(request)
    session_manager = get_session_manager()
    
    logger.info(f"[SUPPORTING UPLOAD] Received request - Session ID: {session.session_id}, File count: {len(files)}")
    logger.info(f"[SUPPORTING UPLOAD] Filenames: {[f.filename for f in files]}")
    
    # Check file count limit
    current_supporting_count = session.uploaded_file_count
    if session.funding_call_uploaded:
        current_supporting_count -= 1  # Exclude funding call
    
    logger.info(f"[SUPPORTING UPLOAD] Current supporting docs: {current_supporting_count}")
    
    max_supporting_docs = 5
    if current_supporting_count + len(files) > max_supporting_docs:
        logger.warning(f"[SUPPORTING UPLOAD] File count limit exceeded: {current_supporting_count} + {len(files)} > {max_supporting_docs}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot upload {len(files)} files. Already have {current_supporting_count}, max is {max_supporting_docs}"
        )
    
    # Validate and process each file
    file_storage = get_file_storage()
    indexing_service = get_indexing_service()
    
    results = []
    documents_to_index = []
    
    for upload_file in files:
        try:
            # Read file content
            file_content = await upload_file.read()
            file_size = len(file_content)
            
            # Validate file type
            is_valid, error_msg = validate_file_type(file_content, upload_file.filename)
            if not is_valid:
                results.append({
                    'filename': upload_file.filename,
                    'uploaded': False,
                    'indexed': False,
                    'error': error_msg
                })
                continue
            
            # Validate file size against quota
            is_valid, error_msg = validate_file_size(
                file_size,
                is_funding_call=False,
                current_total_size=session.total_upload_size_bytes
            )
            if not is_valid:
                results.append({
                    'filename': upload_file.filename,
                    'uploaded': False,
                    'indexed': False,
                    'error': error_msg
                })
                continue
            
            # Save file
            file_id, file_path = file_storage.save_file(
                session_id=session.session_id,
                file_content=file_content,
                original_filename=upload_file.filename
            )
            
            # Update session
            session.add_upload(file_size, is_funding_call=False, filename=upload_file.filename)
            
            # Track uploaded file
            file_type = get_file_type(upload_file.filename)
            session_manager.add_uploaded_file(
                session_id=session.session_id,
                filename=upload_file.filename,
                file_id=file_id,
                file_type=file_type
            )
            
            # Add to indexing queue
            documents_to_index.append({
                'file_path': file_path,
                'document_id': file_id,
                'document_title': upload_file.filename
            })
            
            results.append({
                'filename': upload_file.filename,
                'uploaded': True,
                'file_id': file_id,
                'size': format_file_size(file_size)
            })
            
        except Exception as e:
            results.append({
                'filename': upload_file.filename,
                'uploaded': False,
                'indexed': False,
                'error': str(e)
            })
    
    # Update session
    session_manager.update_session(session)
    logger.info(f"[SUPPORTING UPLOAD] Session updated - total uploaded files: {session.uploaded_file_count}")
    
    # Index all uploaded documents (blocking)
    if documents_to_index:
        logger.info(f"[SUPPORTING UPLOAD] Starting indexing for {len(documents_to_index)} documents...")
        index_results = indexing_service.index_multiple_documents(
            session_id=session.session_id,
            documents=documents_to_index
        )
        logger.info(f"[SUPPORTING UPLOAD] Indexing complete - Success count: {index_results.get('success_count', 0)}")
        
        # Merge indexing results with upload results
        for i, doc in enumerate(documents_to_index):
            doc_result = index_results['results'][i]
            
            # Find matching result
            for result in results:
                if result.get('file_id') == doc['document_id']:
                    result['indexed'] = doc_result['success']
                    result['chunk_count'] = doc_result.get('chunk_count', 0)
                    if not doc_result['success']:
                        result['indexing_error'] = doc_result.get('error')
                    break
    
    response = {
        'uploaded_count': len([r for r in results if r.get('uploaded')]),
        'failed_count': len([r for r in results if not r.get('uploaded')]),
        'total_chunks': sum(r.get('chunk_count', 0) for r in results),
        'files': results,
        'quota': session.get_quota_status()
    }
    logger.info(f"[SUPPORTING UPLOAD] Success - Uploaded: {response['uploaded_count']}, Failed: {response['failed_count']}, Chunks: {response['total_chunks']}")
    return response


@router.get("/status")
async def get_upload_status(request: Request):
    """Get current upload status for session.
    
    Returns:
        Quota usage and uploaded files list
    """
    session = get_session_from_request(request)
    session_manager = get_session_manager()
    
    logger.info(f"[STATUS] Request for session: {session.session_id}")
    logger.info(f"[STATUS] Session details - funding_call_uploaded: {session.funding_call_uploaded}, file_count: {session.uploaded_file_count}, total_size: {session.total_upload_size_bytes}")
    
    uploaded_files = session_manager.get_uploaded_files(session.session_id)
    logger.info(f"[STATUS] Uploaded files count: {len(uploaded_files)}")
    
    # Get indexing stats
    indexing_service = get_indexing_service()
    index_stats = indexing_service.get_index_stats(session.session_id)
    logger.info(f"[STATUS] Index stats: {index_stats}")
    
    quota = session.get_quota_status()
    logger.info(f"[STATUS] Quota: {quota}")
    
    return {
        'quota': quota,
        'uploaded_files': uploaded_files,
        'index_stats': index_stats
    }
