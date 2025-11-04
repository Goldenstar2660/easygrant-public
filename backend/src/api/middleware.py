"""API middleware for session validation and quota enforcement.

Validates session IDs and enforces 50MB upload quota.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable
from backend.src.services.session_manager import get_session_manager
import logging

logger = logging.getLogger(__name__)


async def session_validation_middleware(request: Request, call_next: Callable):
    """Middleware to validate session IDs in requests.
    
    Checks for session_id in:
    1. Query parameters (?session_id=...)
    2. Request headers (X-Session-ID)
    3. Request body (JSON with session_id field)
    
    Args:
        request: FastAPI request
        call_next: Next middleware/endpoint
        
    Returns:
        Response from next handler or error
    """
    logger.info(f"[MIDDLEWARE] Request: {request.method} {request.url.path}")
    
    # Skip middleware for health check and docs
    if request.url.path in ['/health', '/docs', '/openapi.json', '/redoc']:
        logger.info(f"[MIDDLEWARE] Skipping validation for: {request.url.path}")
        return await call_next(request)
    
    # Skip for session creation endpoint
    if request.url.path == '/api/session/create':
        logger.info(f"[MIDDLEWARE] Skipping validation for session creation")
        return await call_next(request)
    
    # Skip for demo endpoints (they create their own sessions)
    if request.url.path.startswith('/api/demo'):
        logger.info(f"[MIDDLEWARE] Skipping validation for demo endpoint")
        return await call_next(request)
    
    # Skip for sample PDF endpoints (no session needed for example files)
    if request.url.path.startswith('/api/samples'):
        logger.info(f"[MIDDLEWARE] Skipping validation for samples endpoint")
        return await call_next(request)
    
    session_manager = get_session_manager()
    session_id = None
    
    logger.info(f"[MIDDLEWARE] Processing request: {request.method} {request.url.path}")
    logger.info(f"[MIDDLEWARE] Query params: {dict(request.query_params)}")
    logger.info(f"[MIDDLEWARE] Headers: X-Session-ID={request.headers.get('X-Session-ID', 'NOT_FOUND')}")
    logger.info(f"[MIDDLEWARE] Path params: {dict(request.path_params)}")
    
    # Try to get session_id from query params
    if 'session_id' in request.query_params:
        session_id = request.query_params['session_id']
        logger.info(f"[MIDDLEWARE] ✓ Found session_id in query params: {session_id}")
    
    # Try to get from headers
    elif 'X-Session-ID' in request.headers:
        session_id = request.headers['X-Session-ID']
        logger.info(f"[MIDDLEWARE] ✓ Found session_id in headers: {session_id}")
    
    # Try to get from path parameters (for routes like /api/requirements/{session_id})
    elif 'session_id' in request.path_params:
        session_id = request.path_params['session_id']
        logger.info(f"[MIDDLEWARE] ✓ Found session_id in path params: {session_id}")
    
    # Try to get from request body for POST requests (BEFORE trying URL path extraction)
    elif request.method == 'POST':
        logger.info(f"[MIDDLEWARE] Attempting to read session_id from POST body...")
        try:
            import json
            body = await request.body()
            logger.info(f"[MIDDLEWARE] Body length: {len(body)} bytes")
            if body:
                body_data = json.loads(body.decode())
                logger.info(f"[MIDDLEWARE] Body JSON keys: {list(body_data.keys())}")
                if 'session_id' in body_data:
                    session_id = body_data['session_id']
                    logger.info(f"[MIDDLEWARE] ✓ Found session_id in request body: {session_id}")
                    # Need to preserve body for the endpoint to read
                    async def receive():
                        return {'type': 'http.request', 'body': body}
                    request._receive = receive
                else:
                    logger.warning(f"[MIDDLEWARE] ✗ 'session_id' key not in body. Body: {body_data}")
        except Exception as e:
            logger.error(f"[MIDDLEWARE] ✗ Could not parse request body: {e}", exc_info=True)
    
    # Try to extract from URL path manually (for routes where path_params not yet populated)
    # This is LAST because it's only for GET requests with session_id in path
    if not session_id and request.url.path.startswith(('/api/requirements/', '/api/sections/')):
        logger.info(f"[MIDDLEWARE] Attempting to extract session_id from URL path...")
        import re
        # Match patterns like /api/requirements/{uuid} or /api/sections/{uuid}/...
        path_match = re.search(r'/api/(?:requirements|sections)/([a-f0-9\-]{36})', request.url.path)
        if path_match:
            session_id = path_match.group(1)
            logger.info(f"[MIDDLEWARE] ✓ Extracted session_id from URL path: {session_id}")
        else:
            logger.warning(f"[MIDDLEWARE] ✗ No session_id found in URL path")
    
    # If no session_id found, return error
    if not session_id:
        logger.warning(f"[MIDDLEWARE] No session_id found in request")
        logger.warning(f"[MIDDLEWARE] URL path: {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "session_id required",
                "message": "Provide session_id in query params, X-Session-ID header, or request body"
            }
        )
    
    # Validate session exists
    if not session_manager.session_exists(session_id):
        logger.warning(f"[MIDDLEWARE] Session not found: {session_id}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "session_not_found",
                "message": f"Session {session_id} not found. Create a session first."
            }
        )
    
    logger.info(f"[MIDDLEWARE] Session validated: {session_id}")
    
    # Attach session to request state for use in endpoints
    request.state.session_id = session_id
    request.state.session = session_manager.get_session(session_id)
    
    # Continue to next handler
    response = await call_next(request)
    return response


def validate_upload_quota(session_id: str, file_size_bytes: int) -> tuple[bool, str]:
    """Validate file upload against quota.
    
    Args:
        session_id: Session identifier
        file_size_bytes: Size of file to upload
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        return False, "Session not found"
    
    can_upload, error_msg = session.can_upload_file(file_size_bytes)
    if not can_upload:
        return False, error_msg
    
    return True, ""


def get_session_from_request(request: Request):
    """Helper to get session from request state.
    
    Args:
        request: FastAPI request
        
    Returns:
        UserSession instance
        
    Raises:
        HTTPException if session not found in request state
    """
    if not hasattr(request.state, 'session'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session not found in request state. Middleware may not be configured."
        )
    
    return request.state.session
