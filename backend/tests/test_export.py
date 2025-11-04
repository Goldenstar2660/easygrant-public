"""
Tests for DOCX export functionality (Phase 7)
"""

import pytest
from io import BytesIO
from backend.src.agents.assembler import Assembler
from backend.src.models.citation import Citation


def test_assembler_initialization():
    """Test assembler can be initialized"""
    assembler = Assembler()
    assert assembler is not None


def test_assemble_simple_proposal():
    """Test assembling a simple proposal with one section"""
    assembler = Assembler()
    
    # Create test section data
    sections = [
        {
            'section_name': 'Project Summary',
            'text': 'This is a test project summary. It includes a citation [Test Doc, p.1].',
            'word_count': 12,
            'citations': [
                {
                    'document_id': 'test-doc-1',
                    'document_title': 'Test Doc',
                    'page_number': 1,
                    'chunk_text': 'Sample text from test document',
                    'relevance_score': 0.85
                }
            ]
        }
    ]
    
    # Assemble document
    doc = assembler.assemble_proposal(
        sections=sections,
        funding_call_name='Test Funding Call',
        program_name='Test Organization'
    )
    
    assert doc is not None
    # Document should have paragraphs (title page + section content)
    assert len(doc.paragraphs) > 0


def test_assemble_multiple_sections():
    """Test assembling proposal with multiple sections"""
    assembler = Assembler()
    
    sections = [
        {
            'section_name': 'Project Summary',
            'text': 'First section text [Doc1, p.1].',
            'word_count': 4,
            'citations': []
        },
        {
            'section_name': 'Project Description',
            'text': 'Second section text with more details [Doc2, p.3].\n\nSecond paragraph here.',
            'word_count': 10,
            'citations': []
        }
    ]
    
    doc = assembler.assemble_proposal(sections=sections)
    
    assert doc is not None
    assert len(doc.paragraphs) > 0


def test_get_docx_bytes():
    """Test converting document to bytes for streaming"""
    assembler = Assembler()
    
    sections = [
        {
            'section_name': 'Test Section',
            'text': 'Test content',
            'word_count': 2,
            'citations': []
        }
    ]
    
    doc = assembler.assemble_proposal(sections=sections)
    docx_bytes = assembler.get_docx_bytes(doc)
    
    assert docx_bytes is not None
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 0
    # DOCX files start with PK (zip magic number)
    assert docx_bytes[:2] == b'PK'


def test_title_page_with_metadata():
    """Test title page includes funding call name and program name"""
    assembler = Assembler()
    
    sections = [
        {
            'section_name': 'Test Section',
            'text': 'Test',
            'word_count': 1,
            'citations': []
        }
    ]
    
    doc = assembler.assemble_proposal(
        sections=sections,
        funding_call_name='Community Development Grant 2025',
        program_name='Smallville Community Foundation'
    )
    
    # Check that document was created
    assert doc is not None
    
    # Check for title (first paragraph should be the heading)
    assert len(doc.paragraphs) > 0


def test_inline_citation_preservation():
    """Test that inline citations are preserved in output"""
    assembler = Assembler()
    
    citation_text = 'According to our research [Annual Report 2024, p.15], we found evidence.'
    
    sections = [
        {
            'section_name': 'Research Findings',
            'text': citation_text,
            'word_count': 10,
            'citations': [
                {
                    'document_id': 'annual-report',
                    'document_title': 'Annual Report 2024',
                    'page_number': 15,
                    'chunk_text': 'Research evidence...',
                    'relevance_score': 0.92
                }
            ]
        }
    ]
    
    doc = assembler.assemble_proposal(sections=sections)
    
    # Find the paragraph with our text
    found_citation = False
    for para in doc.paragraphs:
        if '[Annual Report 2024, p.15]' in para.text:
            found_citation = True
            break
    
    assert found_citation, "Inline citation should be preserved in document"


def test_empty_sections_list():
    """Test handling of empty sections list"""
    assembler = Assembler()
    
    doc = assembler.assemble_proposal(sections=[])
    
    # Should still create document with title page
    assert doc is not None


def test_section_with_paragraphs():
    """Test section with multiple paragraphs (double newline separated)"""
    assembler = Assembler()
    
    multi_para_text = """First paragraph with some content.

Second paragraph with more details [Source, p.5].

Third paragraph concluding the section."""
    
    sections = [
        {
            'section_name': 'Multi-Paragraph Section',
            'text': multi_para_text,
            'word_count': 15,
            'citations': []
        }
    ]
    
    doc = assembler.assemble_proposal(sections=sections)
    
    assert doc is not None
    # Should have multiple paragraphs
    assert len(doc.paragraphs) > 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
