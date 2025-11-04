"""Sections API endpoints.

Generate, retrieve, and manage proposal sections with citations.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from ...services.session_manager import get_session_manager
from ...agents.retriever import Retriever
from ...agents.section_generator import SectionGenerator
from ...models.citation import Citation
from ...utils.paragraph_lock import split_into_paragraphs, merge_paragraphs_with_locks

router = APIRouter(prefix="/api/sections", tags=["sections"])
logger = logging.getLogger(__name__)

# Initialize services
session_manager = get_session_manager()
retriever = Retriever(top_k=5, min_relevance_score=0.25)  # Lowered threshold for L2 distance
section_generator = SectionGenerator()


# Request/Response models
class GenerateSectionRequest(BaseModel):
    """Request to generate a section"""
    session_id: str
    section_name: str
    section_requirements: Optional[str] = None
    word_limit: Optional[int] = None
    char_limit: Optional[int] = None
    format_type: str = "narrative"


class CitationResponse(BaseModel):
    """Citation metadata"""
    document_id: str
    document_title: str
    page_number: int
    chunk_text: str
    relevance_score: float


class GeneratedSectionResponse(BaseModel):
    """Generated section with metadata"""
    section_id: str
    section_name: str
    text: str  # Changed from generated_text to match frontend
    word_count: int
    citations: List[CitationResponse]
    warning: Optional[str] = None
    locked_paragraphs: List[int] = []
    generated_at: str


class UpdateSectionRequest(BaseModel):
    """Request to update section text and lock paragraphs"""
    text: str
    locked_paragraph_indices: List[int] = []


class RegenerateSectionRequest(BaseModel):
    """Request to regenerate section preserving locks"""
    section_requirements: Optional[str] = None
    word_limit: Optional[int] = None
    char_limit: Optional[int] = None
    format_type: str = "narrative"


# In-memory storage for generated sections (session_id -> {section_name -> data})
_generated_sections = {}


@router.post("/generate", response_model=GeneratedSectionResponse)
async def generate_section(request: GenerateSectionRequest):
    """Generate a proposal section using RAG.
    
    Args:
        request: Generation parameters
        
    Returns:
        GeneratedSectionResponse with text and citations
        
    Raises:
        404: Session not found or no funding call uploaded
        500: Generation failed
    """
    logger.info(f"[SECTIONS API] ========== POST /generate ENDPOINT REACHED ==========")
    logger.info(f"[SECTIONS API] Request object type: {type(request)}")
    logger.info(f"[SECTIONS API] Request session_id: {request.session_id}")
    logger.info(f"[SECTIONS API] Request section_name: {request.section_name}")
    
    print(f"\n{'='*60}")
    print(f"[SECTIONS API] 🚀 GENERATE SECTION REQUEST")
    print(f"[SECTIONS API] Session: {request.session_id}")
    print(f"[SECTIONS API] Section: {request.section_name}")
    print(f"[SECTIONS API] Word limit: {request.word_limit}")
    print(f"{'='*60}\n")
    
    try:
        logger.info(f"[SECTIONS API] Generate request for section: {request.section_name}")
        
        # 1. Validate session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if not session.funding_call_uploaded:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No funding call uploaded. Please upload a funding call first."
            )
        
        # 2. Retrieve relevant context
        print(f"\n[SECTIONS API] ========================================")
        print(f"[SECTIONS API] Retrieving context for section: {request.section_name}")
        logger.info(f"[SECTIONS API] Retrieving context for: {request.section_name}")
        
        citations = retriever.retrieve_for_section(
            session_id=request.session_id,
            section_name=request.section_name,
            section_requirements=request.section_requirements,
            word_limit=request.word_limit
        )
        
        print(f"[SECTIONS API] Retrieved {len(citations)} citations from retriever")
        logger.info(f"[SECTIONS API] Retrieved {len(citations)} citations")
        
        if len(citations) > 0:
            print(f"[SECTIONS API] Citation details:")
            for i, cit in enumerate(citations[:3], 1):  # Show first 3
                print(f"[SECTIONS API]   {i}. {cit.document_title}, p.{cit.page_number}")
        else:
            print(f"[SECTIONS API] ⚠️  WARNING: NO CITATIONS RETRIEVED!")
            print(f"[SECTIONS API] This means no relevant context was found in your documents")
        print(f"[SECTIONS API] ========================================\n")
        
        # 3. Generate section
        print(f"[SECTIONS API] Calling section_generator.generate_section()...")
        logger.info(f"[SECTIONS API] Generating section text...")
        
        result = section_generator.generate_section(
            section_name=request.section_name,
            section_requirements=request.section_requirements,
            word_limit=request.word_limit,
            char_limit=request.char_limit,
            format_type=request.format_type,
            citations=citations
        )
        
        print(f"[SECTIONS API] Generation complete!")
        print(f"[SECTIONS API] Result keys: {list(result.keys())}")
        print(f"[SECTIONS API] Word count: {result['word_count']}")
        print(f"[SECTIONS API] Citations used: {len(result['citations_used'])}")
        
        if len(result['citations_used']) == 0:
            print(f"[SECTIONS API] ⚠️  NO CITATIONS IN RESULT!")
            print(f"[SECTIONS API] Possible reasons:")
            print(f"[SECTIONS API]   1. No citations were passed to generator ({len(citations)} available)")
            print(f"[SECTIONS API]   2. AI didn't use the citations in the text")
            print(f"[SECTIONS API]   3. Citation extraction failed")
        
        # 4. Store generated section
        section_id = str(uuid.uuid4())
        if request.session_id not in _generated_sections:
            _generated_sections[request.session_id] = {}
        
        _generated_sections[request.session_id][request.section_name] = {
            "section_id": section_id,
            "section_name": request.section_name,
            "text": result["generated_text"],  # Changed from generated_text
            "word_count": result["word_count"],
            "citations": result["citations_used"],
            "warning": result.get("warning"),
            "locked_paragraphs": result.get("locked_paragraphs", []),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"[SECTIONS API] Section generated successfully: "
            f"{result['word_count']} words, {len(result['citations_used'])} citations"
        )
        
        print(f"\n{'='*60}")
        print(f"[SECTIONS API] ✅ GENERATION SUCCESSFUL!")
        print(f"[SECTIONS API] Word count: {result['word_count']}")
        print(f"[SECTIONS API] Citations: {len(result['citations_used'])}")
        print(f"[SECTIONS API] Section ID: {section_id}")
        print(f"{'='*60}\n")
        
        # 5. Return response
        return GeneratedSectionResponse(
            section_id=section_id,
            section_name=request.section_name,
            text=result["generated_text"],  # Changed from generated_text
            word_count=result["word_count"],
            citations=[
                CitationResponse(
                    document_id=c.document_id,
                    document_title=c.document_title,
                    page_number=c.page_number,
                    chunk_text=c.chunk_text,
                    relevance_score=c.relevance_score
                )
                for c in result["citations_used"]
            ],
            warning=result.get("warning"),
            locked_paragraphs=result.get("locked_paragraphs", []),
            generated_at=datetime.utcnow().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SECTIONS API] Section generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Section generation failed: {str(e)}"
        )


@router.get("/{session_id}/{section_name}", response_model=GeneratedSectionResponse)
async def get_section(session_id: str, section_name: str):
    """Retrieve a previously generated section.
    
    Args:
        session_id: Session identifier
        section_name: Name of the section
        
    Returns:
        GeneratedSectionResponse
        
    Raises:
        404: Session or section not found
    """
    try:
        # Check if section exists
        if session_id not in _generated_sections or \
           section_name not in _generated_sections[session_id]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section '{section_name}' not found for this session"
            )
        
        section_data = _generated_sections[session_id][section_name]
        
        return GeneratedSectionResponse(
            section_id=section_data["section_id"],
            section_name=section_data["section_name"],
            text=section_data["text"],  # Changed from generated_text
            word_count=section_data["word_count"],
            citations=[
                CitationResponse(
                    document_id=c.document_id,
                    document_title=c.document_title,
                    page_number=c.page_number,
                    chunk_text=c.chunk_text,
                    relevance_score=c.relevance_score
                )
                for c in section_data["citations"]
            ],
            warning=section_data.get("warning"),
            locked_paragraphs=section_data.get("locked_paragraphs", []),
            generated_at=section_data["generated_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SECTIONS API] Error retrieving section: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving section: {str(e)}"
        )


@router.patch("/{session_id}/{section_name}", response_model=GeneratedSectionResponse)
async def update_section(
    session_id: str,
    section_name: str,
    request: UpdateSectionRequest
):
    """Update section text and lock specific paragraphs.
    
    Args:
        session_id: Session identifier
        section_name: Name of the section
        request: Updated text and locked paragraph indices
        
    Returns:
        Updated GeneratedSectionResponse
        
    Raises:
        404: Session or section not found
    """
    try:
        logger.info(f"[SECTIONS API] PATCH /{session_id}/{section_name}")
        
        # Check if section exists
        if session_id not in _generated_sections or \
           section_name not in _generated_sections[session_id]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section '{section_name}' not found for this session"
            )
        
        section_data = _generated_sections[session_id][section_name]
        
        # Split text into paragraphs
        paragraphs = split_into_paragraphs(request.text)
        
        # Validate locked paragraph indices
        valid_indices = [
            idx for idx in request.locked_paragraph_indices
            if 0 <= idx < len(paragraphs)
        ]
        
        if len(valid_indices) != len(request.locked_paragraph_indices):
            logger.warning(
                f"[SECTIONS API] Some locked paragraph indices were invalid. "
                f"Requested: {request.locked_paragraph_indices}, "
                f"Valid: {valid_indices}"
            )
        
        # Create locked paragraphs list with text
        locked_paragraphs_data = [
            {"index": idx, "text": paragraphs[idx]}
            for idx in valid_indices
        ]
        
        # Update section data
        section_data["text"] = request.text
        section_data["locked_paragraphs"] = valid_indices
        section_data["locked_paragraphs_data"] = locked_paragraphs_data
        
        # Recalculate word count
        from ...utils.paragraph_lock import count_words
        section_data["word_count"] = count_words(request.text)
        
        logger.info(
            f"[SECTIONS API] Section updated: {len(valid_indices)} paragraphs locked"
        )
        
        return GeneratedSectionResponse(
            section_id=section_data["section_id"],
            section_name=section_data["section_name"],
            text=section_data["text"],
            word_count=section_data["word_count"],
            citations=[
                CitationResponse(
                    document_id=c.document_id,
                    document_title=c.document_title,
                    page_number=c.page_number,
                    chunk_text=c.chunk_text,
                    relevance_score=c.relevance_score
                )
                for c in section_data["citations"]
            ],
            warning=section_data.get("warning"),
            locked_paragraphs=valid_indices,
            generated_at=section_data["generated_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SECTIONS API] Error updating section: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating section: {str(e)}"
        )


@router.post("/{session_id}/{section_name}/regenerate", response_model=GeneratedSectionResponse)
async def regenerate_section(
    session_id: str,
    section_name: str,
    request: RegenerateSectionRequest
):
    """Regenerate section while preserving locked paragraphs.
    
    Args:
        session_id: Session identifier
        section_name: Name of the section
        request: Regeneration parameters
        
    Returns:
        Regenerated GeneratedSectionResponse with locked paragraphs preserved
        
    Raises:
        404: Session or section not found
        500: Regeneration failed
    """
    try:
        logger.info(f"[SECTIONS API] POST /{session_id}/{section_name}/regenerate")
        
        # 1. Validate session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # 2. Check if section exists
        if session_id not in _generated_sections or \
           section_name not in _generated_sections[session_id]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section '{section_name}' not found for this session"
            )
        
        section_data = _generated_sections[session_id][section_name]
        locked_indices = section_data.get("locked_paragraphs", [])
        locked_paragraphs_data = section_data.get("locked_paragraphs_data", [])
        
        logger.info(
            f"[SECTIONS API] Regenerating with {len(locked_indices)} locked paragraphs"
        )
        
        # 3. Retrieve relevant context (same as generate)
        citations = retriever.retrieve_for_section(
            session_id=session_id,
            section_name=section_name,
            section_requirements=request.section_requirements,
            word_limit=request.word_limit
        )
        
        logger.info(f"[SECTIONS API] Retrieved {len(citations)} citations")
        
        # 4. Generate new section
        result = section_generator.generate_section(
            section_name=section_name,
            section_requirements=request.section_requirements,
            word_limit=request.word_limit,
            char_limit=request.char_limit,
            format_type=request.format_type,
            citations=citations
        )
        
        new_text = result["generated_text"]
        
        # 5. Merge with locked paragraphs
        if locked_paragraphs_data:
            locked_tuples = [(lp["index"], lp["text"]) for lp in locked_paragraphs_data]
            merged_text = merge_paragraphs_with_locks(new_text, locked_tuples)
            logger.info(
                f"[SECTIONS API] Merged {len(locked_tuples)} locked paragraphs "
                f"into regenerated text"
            )
        else:
            merged_text = new_text
        
        # 6. Update section data
        from ...utils.paragraph_lock import count_words
        section_data["text"] = merged_text
        section_data["word_count"] = count_words(merged_text)
        section_data["citations"] = result["citations_used"]
        section_data["warning"] = result.get("warning")
        section_data["generated_at"] = datetime.utcnow().isoformat()
        # Keep locked paragraphs
        
        logger.info(
            f"[SECTIONS API] Section regenerated: "
            f"{section_data['word_count']} words, "
            f"{len(result['citations_used'])} citations, "
            f"{len(locked_indices)} paragraphs preserved"
        )
        
        # 7. Return response
        return GeneratedSectionResponse(
            section_id=section_data["section_id"],
            section_name=section_data["section_name"],
            text=merged_text,
            word_count=section_data["word_count"],
            citations=[
                CitationResponse(
                    document_id=c.document_id,
                    document_title=c.document_title,
                    page_number=c.page_number,
                    chunk_text=c.chunk_text,
                    relevance_score=c.relevance_score
                )
                for c in result["citations_used"]
            ],
            warning=section_data.get("warning"),
            locked_paragraphs=locked_indices,
            generated_at=section_data["generated_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"[SECTIONS API] Section regeneration failed: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Section regeneration failed: {str(e)}"
        )
