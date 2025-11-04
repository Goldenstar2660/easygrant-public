"""Paragraph locking utilities.

Provides utilities for splitting text into paragraphs and managing paragraph locks.
"""

from typing import List, Tuple
import re


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs using double newline separator.
    
    Args:
        text: Input text
        
    Returns:
        List of paragraph strings (stripped, non-empty)
    """
    if not text:
        return []
    
    # Split on double newline (paragraph separator)
    paragraphs = text.split('\n\n')
    
    # Filter empty paragraphs and strip whitespace
    return [p.strip() for p in paragraphs if p.strip()]


def find_paragraph_at_position(text: str, cursor_position: int) -> Tuple[int, str]:
    """Find which paragraph contains the cursor position.
    
    Args:
        text: Full text
        cursor_position: Character position in text (0-based)
        
    Returns:
        Tuple of (paragraph_index, paragraph_text)
        Returns (-1, "") if position is invalid
    """
    if not text or cursor_position < 0 or cursor_position > len(text):
        return (-1, "")
    
    paragraphs = split_into_paragraphs(text)
    
    # Find position boundaries for each paragraph
    current_pos = 0
    for idx, para in enumerate(paragraphs):
        # Account for paragraph separator (double newline)
        para_start = text.find(para, current_pos)
        para_end = para_start + len(para)
        
        if para_start <= cursor_position <= para_end:
            return (idx, para)
        
        current_pos = para_end
    
    return (-1, "")


def get_paragraph_boundaries(text: str, paragraph_index: int) -> Tuple[int, int]:
    """Get start and end character positions for a paragraph.
    
    Args:
        text: Full text
        paragraph_index: 0-based paragraph index
        
    Returns:
        Tuple of (start_pos, end_pos) character positions
        Returns (-1, -1) if index is invalid
    """
    paragraphs = split_into_paragraphs(text)
    
    if paragraph_index < 0 or paragraph_index >= len(paragraphs):
        return (-1, -1)
    
    target_para = paragraphs[paragraph_index]
    
    # Find this paragraph in the original text
    # Account for previous paragraphs
    search_start = 0
    for i in range(paragraph_index):
        found_pos = text.find(paragraphs[i], search_start)
        if found_pos == -1:
            return (-1, -1)
        search_start = found_pos + len(paragraphs[i])
    
    start_pos = text.find(target_para, search_start)
    if start_pos == -1:
        return (-1, -1)
    
    end_pos = start_pos + len(target_para)
    return (start_pos, end_pos)


def merge_paragraphs_with_locks(
    new_text: str,
    locked_paragraphs: List[Tuple[int, str]]
) -> str:
    """Merge new generated text with locked paragraphs.
    
    Args:
        new_text: Newly generated text
        locked_paragraphs: List of (index, text) tuples for locked paragraphs
        
    Returns:
        Merged text with locked paragraphs preserved in their original positions
    """
    if not locked_paragraphs:
        return new_text
    
    new_paragraphs = split_into_paragraphs(new_text)
    
    # Create dict of locked paragraphs by index
    locked_dict = {idx: text for idx, text in locked_paragraphs}
    
    # Determine max index needed
    max_idx = max(
        len(new_paragraphs) - 1,
        max(locked_dict.keys(), default=-1)
    )
    
    # Merge: use locked text where available, otherwise use new text
    merged_paragraphs = []
    for i in range(max_idx + 1):
        if i in locked_dict:
            # Use locked paragraph
            merged_paragraphs.append(locked_dict[i])
        elif i < len(new_paragraphs):
            # Use new AI-generated paragraph
            merged_paragraphs.append(new_paragraphs[i])
        # If index is beyond both, skip (shouldn't happen normally)
    
    return '\n\n'.join(merged_paragraphs)


def count_words(text: str) -> int:
    """Count words in text.
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    # Split on whitespace and filter empty strings
    words = text.strip().split()
    return len([w for w in words if w])
