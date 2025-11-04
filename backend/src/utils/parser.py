"""Document parser for PDF and DOCX files.

Extracts text and metadata from documents using PyMuPDF and python-docx.
Preserves page numbers for citation tracking.
"""

import fitz  # PyMuPDF
from docx import Document
from pathlib import Path
from typing import List, Dict, Any, Tuple


class DocumentParser:
    """Parse PDF and DOCX files to extract text and metadata"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> List[Dict[str, Any]]:
        """Parse PDF file and extract text with page numbers.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of dicts with keys: page_number, text, metadata
            
        Example:
            [
                {'page_number': 1, 'text': '...', 'metadata': {'source': 'doc.pdf'}},
                {'page_number': 2, 'text': '...', 'metadata': {'source': 'doc.pdf'}},
            ]
        """
        doc = fitz.open(file_path)
        pages = []
        
        filename = Path(file_path).name
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            pages.append({
                'page_number': page_num + 1,  # 1-indexed
                'text': text,
                'metadata': {
                    'source': filename,
                    'total_pages': len(doc),
                    'file_type': 'pdf'
                }
            })
        
        doc.close()
        return pages
    
    @staticmethod
    def parse_docx(file_path: str) -> List[Dict[str, Any]]:
        """Parse DOCX file and extract text.
        
        Note: DOCX doesn't have explicit pages, so we treat each paragraph
        as a separate section with pseudo-page numbers based on text length.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            List of dicts with keys: page_number, text, metadata
        """
        doc = Document(file_path)
        pages = []
        
        filename = Path(file_path).name
        
        # Estimate pages based on character count (rough: 3000 chars = 1 page)
        CHARS_PER_PAGE = 3000
        current_page = 1
        current_chars = 0
        current_text = []
        
        for para in doc.paragraphs:
            para_text = para.text.strip()
            if not para_text:
                continue
            
            current_text.append(para_text)
            current_chars += len(para_text)
            
            # If we've accumulated enough text for a page, save it
            if current_chars >= CHARS_PER_PAGE:
                pages.append({
                    'page_number': current_page,
                    'text': '\n'.join(current_text),
                    'metadata': {
                        'source': filename,
                        'file_type': 'docx'
                    }
                })
                current_page += 1
                current_text = []
                current_chars = 0
        
        # Add remaining text as final page
        if current_text:
            pages.append({
                'page_number': current_page,
                'text': '\n'.join(current_text),
                'metadata': {
                    'source': filename,
                    'file_type': 'docx'
                }
            })
        
        return pages
    
    @staticmethod
    def parse_file(file_path: str) -> List[Dict[str, Any]]:
        """Auto-detect file type and parse accordingly.
        
        Args:
            file_path: Path to PDF or DOCX file
            
        Returns:
            List of dicts with page data
            
        Raises:
            ValueError: If file type is not supported
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return DocumentParser.parse_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            return DocumentParser.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}. Only PDF and DOCX supported.")


def extract_text_from_file(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Extract full text and page data from a file.
    
    Args:
        file_path: Path to document
        
    Returns:
        Tuple of (full_text, page_data_list)
    """
    pages = DocumentParser.parse_file(file_path)
    full_text = '\n\n'.join(page['text'] for page in pages)
    return full_text, pages
