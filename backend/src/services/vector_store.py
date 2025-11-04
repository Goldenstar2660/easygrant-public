"""Vector store service using ChromaDB.

Manages session-based collections for document embeddings.
Implements persistent storage with metadata tracking.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from backend.src.utils.config_loader import config
from backend.src.services.embedding_service import get_embedding_service


class VectorStore:
    """ChromaDB vector store with session-based collections"""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize vector store.
        
        Args:
            persist_directory: Directory for persistent storage (defaults to config)
        """
        self.persist_dir = persist_directory or config.get(
            'vector_store', 'persist_directory', default='./vector'
        )
        
        # Create directory if it doesn't exist
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.embedding_service = get_embedding_service()
        self.collection_prefix = config.get(
            'vector_store', 'collection_prefix', default='session_'
        )
    
    def get_collection_name(self, session_id: str) -> str:
        """Get collection name for a session.
        
        Args:
            session_id: User session ID
            
        Returns:
            Collection name (e.g., "session_abc123")
        """
        return f"{self.collection_prefix}{session_id}"
    
    def create_or_get_collection(self, session_id: str):
        """Create or retrieve a collection for a session.
        
        Args:
            session_id: User session ID
            
        Returns:
            ChromaDB collection object
        """
        collection_name = self.get_collection_name(session_id)
        
        # ChromaDB get_or_create_collection handles existence check
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"session_id": session_id}
        )
        
        return collection
    
    def add_documents(
        self,
        session_id: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to the vector store.
        
        Args:
            session_id: User session ID
            texts: List of text chunks
            metadatas: List of metadata dicts (must match texts length)
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        if not texts:
            return
        
        if len(texts) != len(metadatas):
            raise ValueError("texts and metadatas must have same length")
        
        collection = self.create_or_get_collection(session_id)
        
        # Generate embeddings
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Auto-generate IDs if not provided
        if ids is None:
            ids = [f"{session_id}_chunk_{i}" for i in range(len(texts))]
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(
        self,
        session_id: str,
        query: str,
        top_k: Optional[int] = None,
        min_relevance: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents.
        
        Args:
            session_id: User session ID
            query: Search query text
            top_k: Number of results to return (defaults to config)
            min_relevance: Minimum relevance score (0-1, defaults to config)
            filter_metadata: Optional metadata filter
            
        Returns:
            List of results with keys: id, text, metadata, score
        """
        top_k = top_k or config.get('retrieval', 'top_k', default=5)
        min_relevance = min_relevance or config.get(
            'retrieval', 'min_relevance_score', default=0.3
        )
        
        collection = self.create_or_get_collection(session_id)
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)
        
        # Search collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                # ChromaDB returns distances (lower is better)
                # Convert to similarity score (1 - distance/2) for cosine distance
                distance = results['distances'][0][i] if results['distances'] else 0
                score = 1 - (distance / 2)  # Approximate conversion
                
                # Filter by minimum relevance
                if score >= min_relevance:
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'score': score
                    })
        
        return formatted_results
    
    def query(
        self,
        session_id: str,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Query vector store and return raw ChromaDB format.
        
        This method is used by the Retriever agent and returns results
        in the raw ChromaDB format (with documents, metadatas, distances arrays).
        
        Args:
            session_id: User session ID
            query_text: Search query text
            n_results: Number of results to return
            
        Returns:
            Dict with ChromaDB format: {
                'documents': [[...]],
                'metadatas': [[...]],
                'distances': [[...]]
            }
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[VECTOR STORE] ========== QUERY EXECUTION ==========")
        logger.info(f"[VECTOR STORE] Session ID: {session_id}")
        logger.info(f"[VECTOR STORE] Query: {query_text}")
        logger.info(f"[VECTOR STORE] Requested results: {n_results}")
        
        collection = self.create_or_get_collection(session_id)
        
        # Check if collection has documents
        count = collection.count()
        logger.info(f"[VECTOR STORE] Collection has {count} documents")
        
        if count == 0:
            logger.warning(f"[VECTOR STORE] No documents in collection for session {session_id}")
            logger.info(f"[VECTOR STORE] ========== END QUERY ==========")
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query_text)
        
        # Search collection (raw ChromaDB query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, count)  # Don't request more than available
        )
        
        logger.info(f"[VECTOR STORE] Query returned {len(results.get('documents', [[]])[0])} results")
        logger.info(f"[VECTOR STORE] ========== END QUERY ==========")
        
        return results
    
    def delete_collection(self, session_id: str) -> None:
        """Delete a session's collection.
        
        Args:
            session_id: User session ID
        """
        collection_name = self.get_collection_name(session_id)
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            # Collection might not exist, ignore
            pass
    
    def get_collection_count(self, session_id: str) -> int:
        """Get number of documents in a session's collection.
        
        Args:
            session_id: User session ID
            
        Returns:
            Number of documents
        """
        try:
            collection = self.create_or_get_collection(session_id)
            return collection.count()
        except Exception:
            return 0
    
    def collection_exists(self, session_id: str) -> bool:
        """Check if a session's collection exists.
        
        Args:
            session_id: User session ID
            
        Returns:
            True if collection exists
        """
        collection_name = self.get_collection_name(session_id)
        try:
            self.client.get_collection(name=collection_name)
            return True
        except Exception:
            return False


# Global vector store instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get singleton vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
