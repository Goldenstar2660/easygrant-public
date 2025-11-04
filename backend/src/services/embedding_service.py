"""Embedding service using OpenAI text-embedding-3-small.

Generates embeddings for text chunks and queries.
Configuration loaded from config.yaml (1536 dimensions).
"""

import os
from openai import OpenAI
from typing import List, Optional
from backend.src.utils.config_loader import config


class EmbeddingService:
    """Generate embeddings using OpenAI embedding models"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize embedding service.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Load model config
        self.model = config.get('embeddings', 'model', default='text-embedding-3-small')
        self.dimensions = config.get('embeddings', 'dimensions', default=1536)
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536 dimensions for text-embedding-3-small)
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
            dimensions=self.dimensions
        )
        return response.data[0].embedding
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # OpenAI API accepts batches up to 2048 texts
        # For simplicity, we'll process all at once (MVP scope)
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            dimensions=self.dimensions
        )
        
        return [item.embedding for item in response.data]
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query.
        
        Same as embed_text but semantically clearer for search use cases.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        return self.embed_text(query)


# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
