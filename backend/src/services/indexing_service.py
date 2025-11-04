"""Document indexing service.

Handles the full pipeline: parse → chunk → embed → store in vector DB.
This is a blocking operation (not async) as per MVP scope.
"""

from typing import List, Dict, Any
from backend.src.utils.parser import DocumentParser
from backend.src.utils.chunking import create_text_splitter
from backend.src.services.vector_store import get_vector_store
from backend.src.utils.config_loader import config


class IndexingService:
    """Service for indexing documents into vector store"""
    
    def __init__(self):
        """Initialize indexing service"""
        self.vector_store = get_vector_store()
        
        # Load chunking config
        chunk_size = config.get('embeddings', 'chunk_size', default=600)
        chunk_overlap = config.get('embeddings', 'chunk_overlap', default=90)
        self.text_splitter = create_text_splitter(chunk_size, chunk_overlap)
    
    def index_document(
        self,
        session_id: str,
        file_path: str,
        document_id: str,
        document_title: str
    ) -> Dict[str, Any]:
        """Index a single document into vector store.
        
        This is a blocking operation that:
        1. Parses document (PDF or DOCX)
        2. Chunks text using token-based splitter
        3. Generates embeddings via OpenAI
        4. Stores in ChromaDB with metadata
        
        Args:
            session_id: Session identifier
            file_path: Path to uploaded file
            document_id: Unique document identifier (file UUID)
            document_title: Human-readable document name
            
        Returns:
            Dict with indexing results: {
                'success': bool,
                'chunk_count': int,
                'document_id': str,
                'error': str (if failed)
            }
        """
        try:
            # Step 1: Parse document
            pages = DocumentParser.parse_file(file_path)
            
            # SIMPLIFIED LOGGING: Only show key info during indexing
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[INDEXING] 📄 Processing: {document_title}")
            logger.info(f"[INDEXING] Session: {session_id}, Pages: {len(pages)}")
            
            if not pages:
                return {
                    'success': False,
                    'chunk_count': 0,
                    'document_id': document_id,
                    'error': 'No content extracted from document'
                }
            
            # Step 2: Chunk text with metadata
            texts = []
            metadatas = []
            chunk_index = 0
            
            for page in pages:
                page_text = page['text']
                page_number = page['page_number']
                
                # Split page into chunks
                page_chunks = self.text_splitter.split_text(page_text)
                
                for chunk_text in page_chunks:
                    if not chunk_text.strip():
                        continue
                    
                    texts.append(chunk_text)
                    metadatas.append({
                        'document_id': document_id,
                        'document_title': document_title,
                        'page_number': page_number,
                        'chunk_index': chunk_index,
                        'source_file': file_path
                    })
                    chunk_index += 1
            
            # SIMPLIFIED LOGGING: Only show chunk count
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[INDEXING] ✅ Created {len(texts)} chunks, embedding now...")
            
            if not texts:
                return {
                    'success': False,
                    'chunk_count': 0,
                    'document_id': document_id,
                    'error': 'No text chunks generated from document'
                }
            
            # Step 3 & 4: Embed and store (vector_store handles both)
            self.vector_store.add_documents(session_id, texts, metadatas)
            
            return {
                'success': True,
                'chunk_count': len(texts),
                'document_id': document_id,
                'document_title': document_title
            }
            
        except Exception as e:
            return {
                'success': False,
                'chunk_count': 0,
                'document_id': document_id,
                'error': str(e)
            }
    
    def index_multiple_documents(
        self,
        session_id: str,
        documents: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Index multiple documents.
        
        Args:
            session_id: Session identifier
            documents: List of dicts with keys: file_path, document_id, document_title
            
        Returns:
            Dict with overall results: {
                'total_documents': int,
                'successful': int,
                'failed': int,
                'total_chunks': int,
                'results': List[Dict]
            }
        """
        results = []
        successful = 0
        failed = 0
        total_chunks = 0
        
        for doc in documents:
            result = self.index_document(
                session_id=session_id,
                file_path=doc['file_path'],
                document_id=doc['document_id'],
                document_title=doc['document_title']
            )
            
            results.append(result)
            
            if result['success']:
                successful += 1
                total_chunks += result['chunk_count']
            else:
                failed += 1
        
        return {
            'total_documents': len(documents),
            'successful': successful,
            'failed': failed,
            'total_chunks': total_chunks,
            'results': results
        }
    
    def get_index_stats(self, session_id: str) -> Dict[str, Any]:
        """Get indexing statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with stats: {
                'total_chunks': int,
                'collection_exists': bool
            }
        """
        exists = self.vector_store.collection_exists(session_id)
        
        if exists:
            count = self.vector_store.get_collection_count(session_id)
        else:
            count = 0
        
        return {
            'total_chunks': count,
            'collection_exists': exists
        }


# Global indexing service instance
_indexing_service = None

def get_indexing_service() -> IndexingService:
    """Get singleton indexing service instance"""
    global _indexing_service
    if _indexing_service is None:
        _indexing_service = IndexingService()
    return _indexing_service
