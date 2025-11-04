"""Retriever Agent.

Performs semantic search via ChromaDB to find relevant document chunks
for a given section requirement. Returns top-k results with citation metadata.
"""

import logging
from typing import List, Dict, Optional
from ..services.vector_store import get_vector_store
from ..models.citation import Citation

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant document chunks via semantic search"""
    
    def __init__(self, top_k: int = 5, min_relevance_score: float = 0.25):
        """Initialize retriever with configuration.
        
        Args:
            top_k: Maximum number of results to return
            min_relevance_score: Minimum relevance threshold (0-1)
                Note: Using 1/(1+distance) formula, so 0.25 is reasonable for L2 distance
        """
        self.vector_store = get_vector_store()
        self.top_k = top_k
        self.min_relevance_score = min_relevance_score
    
    def retrieve_for_section(
        self,
        session_id: str,
        section_name: str,
        section_requirements: Optional[str] = None,
        word_limit: Optional[int] = None
    ) -> List[Citation]:
        """Retrieve relevant chunks for a proposal section.
        
        Args:
            session_id: Session identifier
            section_name: Name of the section to generate
            section_requirements: Additional requirements/description
            word_limit: Target word limit for the section
            
        Returns:
            List of Citation objects with source metadata
        """
        # Build search query
        query_parts = [f"{section_name}"]
        
        if section_requirements:
            query_parts.append(section_requirements)
        
        if word_limit:
            query_parts.append(f"requirements for {word_limit} word section")
        
        query_text = " ".join(query_parts)
        
        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"🔍 SEARCHING FOR RELEVANT CONTENT")
        logger.info(f"{'='*80}")
        logger.info(f"Section: {section_name}")
        logger.info(f"Query: {query_text[:100]}...")
        logger.info(f"Looking for top {self.top_k} matches with relevance > {self.min_relevance_score}")
        
        # Query vector store
        try:
            results = self.vector_store.query(
                session_id=session_id,
                query_text=query_text,
                n_results=self.top_k
            )
            
            if not results or 'documents' not in results or not results['documents']:
                logger.warning(f"⚠️  No results found for section: {section_name}")
                logger.info(f"{'='*80}")
                return []
            
            # Extract citations from results
            citations = []
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            # Log search results with clear relevance analysis
            logger.info(f"")
            logger.info(f"📊 SEARCH RESULTS:")
            logger.info(f"{'-'*80}")
            
            for i, (doc_text, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                relevance_score = 1.0 / (1.0 + distance)  # Fixed calculation
                doc_title = metadata.get('document_title', 'Unknown')
                page_num = metadata.get('page_number', 'N/A')
                
                # Show relevance decision
                passes = "✅ USING" if relevance_score >= self.min_relevance_score else "❌ SKIP"
                logger.info(f"{passes} | Rank {i+1} | Relevance: {relevance_score:.3f} | {doc_title}, p.{page_num}")
                logger.info(f"         Preview: {doc_text[:120]}...")
                if relevance_score < self.min_relevance_score:
                    logger.info(f"         Reason: Score {relevance_score:.3f} < threshold {self.min_relevance_score}")
                logger.info(f"")
            
            logger.info(f"{'-'*80}")
            
            for i, (doc_text, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # Convert distance to relevance score
                # ChromaDB uses L2 (squared euclidean) distance by default, not cosine
                # For L2: smaller distance = more similar, distance can be > 1
                # Convert to similarity score: use 1 / (1 + distance)
                relevance_score = 1.0 / (1.0 + distance)
                
                # Filter by relevance threshold
                if relevance_score < self.min_relevance_score:
                    logger.debug(f"[RETRIEVER] Skipping low-relevance result {i+1}: score={relevance_score:.3f}")
                    continue
                
                citation = Citation(
                    document_id=metadata.get('document_id', 'unknown'),
                    document_title=metadata.get('document_title', 'Unknown Document'),
                    page_number=metadata.get('page_number', 1),
                    chunk_text=doc_text[:500],  # Truncate for storage
                    relevance_score=round(relevance_score, 3)
                )
                
                citations.append(citation)
                logger.debug(
                    f"[RETRIEVER] Citation {i+1}: {citation.document_title}, "
                    f"p.{citation.page_number}, score={citation.relevance_score}"
                )
            
            logger.info(f"")
            logger.info(f"✅ FINAL RESULT: Retrieved {len(citations)} relevant chunks")
            if len(citations) == 0:
                logger.warning(f"⚠️  WARNING: No content passed relevance threshold!")
                logger.warning(f"   AI will generate WITHOUT your documents.")
            else:
                logger.info(f"   These will be sent to AI for section generation.")
            logger.info(f"{'='*80}")
            logger.info(f"")
            
            return citations
            
        except Exception as e:
            logger.error(f"[RETRIEVER] Error during retrieval: {str(e)}", exc_info=True)
            return []
    
    def format_citations_for_prompt(self, citations: List[Citation]) -> str:
        """Format citations as context for generation prompt.
        
        Args:
            citations: List of Citation objects
            
        Returns:
            Formatted string with numbered citations
        """
        if not citations:
            return "No relevant context found in uploaded documents."
        
        context_parts = ["RELEVANT CONTEXT FROM UPLOADED DOCUMENTS:\n"]
        
        for i, citation in enumerate(citations, 1):
            context_parts.append(
                f"[{i}] Source: {citation.document_title}, Page {citation.page_number}\n"
                f"Content: {citation.chunk_text}\n"
            )
        
        return "\n".join(context_parts)
