"""Text chunking utilities using tiktoken for token counting.

Implements RecursiveCharacterTextSplitter with configurable chunk size and overlap.
Based on config.yaml settings: 600 tokens, 90-token overlap.
"""

import tiktoken
from typing import List, Dict, Any


class RecursiveCharacterTextSplitter:
    """Split text into chunks with token-based sizing"""
    
    def __init__(
        self,
        chunk_size: int = 600,
        chunk_overlap: int = 90,
        encoding_name: str = "cl100k_base"  # GPT-4/GPT-3.5 encoding
    ):
        """Initialize the text splitter.
        
        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlap tokens between chunks
            encoding_name: tiktoken encoding to use
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
        
        # Separators in order of preference (recursive splitting)
        self.separators = ["\n\n", "\n", ". ", " ", ""]
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks of approximately chunk_size tokens.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # If text is small enough, return as single chunk
        if self.count_tokens(text) <= self.chunk_size:
            return [text]
        
        # Try each separator recursively
        for separator in self.separators:
            if separator in text:
                splits = text.split(separator)
                chunks = self._merge_splits(splits, separator)
                if chunks:
                    return chunks
        
        # If no separator worked, force split by tokens
        return self._split_by_tokens(text)
    
    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """Merge splits into chunks of appropriate size.
        
        Args:
            splits: List of text segments
            separator: Separator used for splitting
            
        Returns:
            List of merged chunks
        """
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for split in splits:
            if not split:
                continue
            
            split_tokens = self.count_tokens(split)
            
            # If single split is too large, recursively split it
            if split_tokens > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Recursively split the large segment
                sub_chunks = self.split_text(split)
                chunks.extend(sub_chunks)
                continue
            
            # Try adding to current chunk
            new_tokens = current_tokens + split_tokens
            if separator and current_chunk:
                new_tokens += self.count_tokens(separator)
            
            if new_tokens <= self.chunk_size:
                # Fits in current chunk
                current_chunk.append(split)
                current_tokens = new_tokens
            else:
                # Start new chunk
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                
                # Handle overlap
                overlap_text = self._get_overlap_text(current_chunk, separator)
                current_chunk = [overlap_text, split] if overlap_text else [split]
                current_tokens = self.count_tokens(separator.join(current_chunk))
        
        # Add final chunk
        if current_chunk:
            chunks.append(separator.join(current_chunk))
        
        return chunks
    
    def _get_overlap_text(self, chunks: List[str], separator: str) -> str:
        """Get overlap text from previous chunks.
        
        Args:
            chunks: Previous chunks
            separator: Separator used
            
        Returns:
            Overlap text (last N tokens from previous chunk)
        """
        if not chunks or self.chunk_overlap <= 0:
            return ""
        
        # Join last few chunks
        combined = separator.join(chunks)
        tokens = self.encoding.encode(combined)
        
        # Take last overlap_size tokens
        overlap_tokens = tokens[-self.chunk_overlap:]
        overlap_text = self.encoding.decode(overlap_tokens)
        
        return overlap_text
    
    def _split_by_tokens(self, text: str) -> List[str]:
        """Force split text by token count (last resort).
        
        Args:
            text: Text to split
            
        Returns:
            List of chunks split by token boundaries
        """
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move start forward with overlap
            start = end - self.chunk_overlap if end < len(tokens) else end
        
        return chunks


def create_text_splitter(chunk_size: int = 600, chunk_overlap: int = 90) -> RecursiveCharacterTextSplitter:
    """Factory function to create text splitter with default config.
    
    Args:
        chunk_size: Maximum tokens per chunk (default from config: 600)
        chunk_overlap: Overlap tokens (default from config: 90)
        
    Returns:
        Configured text splitter
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
