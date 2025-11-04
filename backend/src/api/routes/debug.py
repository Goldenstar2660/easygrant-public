"""Debug route for testing vector store retrieval.

This endpoint helps diagnose why supporting documents aren't being used.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from ...services.vector_store import get_vector_store
from ...services.session_manager import get_session_manager
from ...agents.retriever import Retriever

router = APIRouter(prefix="/api/debug", tags=["debug"])
logger = logging.getLogger(__name__)


class DebugQueryRequest(BaseModel):
    session_id: str
    query_text: str
    n_results: int = 10


@router.post("/test-retrieval")
async def test_retrieval(request: DebugQueryRequest):
    """Test vector store retrieval to diagnose issues.
    
    This endpoint helps you see:
    - How many documents are in the collection
    - What the search query returns
    - Relevance scores
    - Document content
    """
    logger.info(f"[DEBUG] ========== TEST RETRIEVAL ==========")
    logger.info(f"[DEBUG] Session ID: {request.session_id}")
    logger.info(f"[DEBUG] Query: {request.query_text}")
    
    # Check if session exists
    session_manager = get_session_manager()
    session = session_manager.get_session(request.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Check collection stats
    collection_exists = vector_store.collection_exists(request.session_id)
    collection_count = vector_store.get_collection_count(request.session_id)
    
    logger.info(f"[DEBUG] Collection exists: {collection_exists}")
    logger.info(f"[DEBUG] Collection count: {collection_count}")
    
    if not collection_exists or collection_count == 0:
        return {
            "session_id": request.session_id,
            "collection_exists": collection_exists,
            "collection_count": collection_count,
            "error": "No documents indexed for this session",
            "suggestion": "Upload supporting documents first"
        }
    
    # Query the collection
    results = vector_store.query(
        session_id=request.session_id,
        query_text=request.query_text,
        n_results=request.n_results
    )
    
    # Format results for debugging
    documents = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]
    
    formatted_results = []
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        relevance = 1.0 - min(dist, 1.0)
        formatted_results.append({
            "rank": i + 1,
            "document_title": meta.get('document_title', 'Unknown'),
            "page_number": meta.get('page_number', 'N/A'),
            "distance": round(dist, 4),
            "relevance_score": round(relevance, 4),
            "text_preview": doc[:200] + "..." if len(doc) > 200 else doc,
            "text_length": len(doc)
        })
    
    logger.info(f"[DEBUG] Found {len(formatted_results)} results")
    logger.info(f"[DEBUG] ========== END TEST RETRIEVAL ==========")
    
    return {
        "session_id": request.session_id,
        "query": request.query_text,
        "collection_exists": collection_exists,
        "collection_count": collection_count,
        "results_found": len(formatted_results),
        "results": formatted_results
    }


@router.get("/collection-stats/{session_id}")
async def get_collection_stats(session_id: str):
    """Get detailed stats about the vector store collection."""
    logger.info(f"[DEBUG] Getting collection stats for session: {session_id}")
    
    # Check if session exists
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Get stats
    collection_exists = vector_store.collection_exists(session_id)
    collection_count = vector_store.get_collection_count(session_id)
    
    # Get uploaded files
    uploaded_files = session_manager.get_uploaded_files(session_id)
    
    return {
        "session_id": session_id,
        "collection_exists": collection_exists,
        "collection_count": collection_count,
        "uploaded_files": uploaded_files,
        "funding_call_uploaded": session.funding_call_uploaded,
        "total_file_count": session.uploaded_file_count
    }
