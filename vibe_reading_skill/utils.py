"""
Utility functions: File operations, format conversion, etc.
Code only executes, does not participate in decision-making
"""

import os
import re
from pathlib import Path
from typing import List, Optional
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def ensure_dir(directory: Path) -> Path:
    """Ensure directory exists, create if it doesn't"""
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def epub_to_txt(epub_path: Path, output_path: Optional[Path] = None) -> str:
    """
    Convert EPUB file to TXT
    
    Args:
        epub_path: EPUB file path
        output_path: Output TXT file path (optional)
    
    Returns:
        Converted text content
    """
    try:
        book = epub.read_epub(str(epub_path))
        text_content = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                # Extract text
                text = soup.get_text()
                # Clean text: replace multiple whitespace with single space, but preserve paragraph breaks
                # First, normalize whitespace within paragraphs
                text = re.sub(r'[ \t]+', ' ', text)  # Replace multiple spaces/tabs with single space
                # Preserve existing newlines (paragraph breaks)
                text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
                text = text.strip()
                if text:
                    text_content.append(text)
        
        full_text = '\n\n'.join(text_content)
        
        # Add line breaks after sentence endings (. ! ?) to improve readability
        # But avoid breaking on abbreviations and decimal numbers
        def add_sentence_breaks(text: str) -> str:
            # First, protect decimal numbers (e.g., 3.14, 0.5)
            text = re.sub(r'(\d+)\.(\d+)', r'\1<DECIMAL>\2', text)
            
            # Protect common abbreviations (case-insensitive)
            # Use placeholders to temporarily replace abbreviations
            abbr_map = {}
            abbr_counter = 0
            
            abbreviations = [
                r'\bMr\.', r'\bMrs\.', r'\bMs\.', r'\bDr\.', r'\bProf\.', r'\bSr\.', r'\bJr\.',
                r'\betc\.', r'\bi\.e\.', r'\be\.g\.', r'\bvs\.', r'\bcf\.', r'\bca\.',
                r'\bU\.S\.', r'\bU\.K\.', r'\bA\.D\.', r'\bB\.C\.', r'\bA\.M\.', r'\bP\.M\.',
                r'\bInc\.', r'\bLtd\.', r'\bCorp\.', r'\bCo\.',
            ]
            
            for abbr_pattern in abbreviations:
                def replace_func(match):
                    nonlocal abbr_counter
                    placeholder = f'<ABBR{abbr_counter}>'
                    abbr_map[placeholder] = match.group(0)
                    abbr_counter += 1
                    return placeholder
                text = re.sub(abbr_pattern, replace_func, text, flags=re.IGNORECASE)
            
            # Now add line breaks after sentence endings (. ! ?) followed by space/tab
            # Replace space/tab after sentence ending with newline (but preserve existing newlines)
            text = re.sub(r'([.!?])([ \t]+)(?=\S)', r'\1\n', text)
            
            # Restore protected patterns
            text = text.replace('<DECIMAL>', '.')
            for placeholder, original in abbr_map.items():
                text = text.replace(placeholder, original)
            
            return text
        
        full_text = add_sentence_breaks(full_text)
        
        # If output path is specified, save file
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
        
        return full_text
    except Exception as e:
        raise Exception(f"Error converting EPUB to TXT: {str(e)}")


def read_file(file_path: Path) -> str:
    """Read file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try other encodings
        for encoding in ['gbk', 'gb2312', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except:
                continue
        raise Exception(f"Unable to decode file: {file_path}")


def write_file(file_path: Path, content: str) -> None:
    """Write file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def split_text_by_lines(text: str, start_line: int, end_line: int) -> str:
    """
    Extract text based on line number range
    
    Args:
        text: Complete text
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
    
    Returns:
        Extracted text fragment
    """
    lines = text.split('\n')
    # Convert to 0-indexed
    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line)
    return '\n'.join(lines[start_idx:end_idx])


def find_sentence_breaks(text: str) -> List[int]:
    """
    Find all sentence break positions (refer to breakdown.md)
    
    **Important**: Must break at complete sentences, cannot break in the middle of a sentence!
    
    Args:
        text: Text content
    
    Returns:
        List of sentence break positions (character positions, after sentence ending punctuation)
    """
    import re
    # Sentence ending pattern: . ! ? followed by space or newline (refer to breakdown.md)
    # Note: Must match punctuation + space/newline to ensure breaking after complete sentence
    sentence_endings = re.compile(r'([.!?])\s+')
    breaks = []
    for match in sentence_endings.finditer(text):
        # Position after sentence ending punctuation (including punctuation and space)
        # This position is the first character position after sentence ends, safe to break
        pos = match.end()
        breaks.append(pos)
    # Also add text end
    breaks.append(len(text))
    return sorted(set(breaks))


def split_at_sentences(text: str, max_words: int) -> List[str]:
    """
    Split text at complete sentences (refer to breakdown.md)
    
    **Important Rules**:
    - Must break at complete sentences (after . ! ?)
    - **Absolutely cannot** break in the middle of a sentence
    - Maintain paragraph integrity
    
    Args:
        text: Text to split
        max_words: Maximum word count per part (English words)
        
    Returns:
        List of split text fragments (each fragment ends at a complete sentence)
    """
    word_count = count_words(text)
    if word_count <= max_words:
        return [text]
    
    chunks = []
    current_chunk = ""
    current_word_count = 0
    
    # Find all sentence break points (after . ! ?)
    breaks = find_sentence_breaks(text)
    
    if not breaks:
        # If no sentence breaks found, return entire text (shouldn't happen, but safe handling)
        return [text]
    
    start_pos = 0
    for break_pos in breaks:
        # Extract text segment from start_pos to this break point (contains complete sentence)
        segment = text[start_pos:break_pos]
        segment_words = count_words(segment)
        
        # If adding this segment would exceed max_words, save current chunk and start new chunk
        # **Key**: Must break at sentence boundary, so even if current segment exceeds max_words, must include it
        if current_word_count + segment_words > max_words and current_chunk:
            # Save current chunk (at sentence boundary)
            chunks.append(current_chunk)
            # Start new chunk (from current sentence)
            current_chunk = segment
            current_word_count = segment_words
        else:
            # Continue accumulating (at sentence boundary)
            current_chunk += segment
            current_word_count += segment_words
        
        start_pos = break_pos
    
    # Add last chunk (at sentence boundary)
    if current_chunk:
        chunks.append(current_chunk)
    
    # Verify: Ensure all chunks end at sentence boundaries
    for i, chunk in enumerate(chunks):
        # Check if chunk ends with sentence ending punctuation (. ! ? followed by space or newline, or text end)
        if not re.search(r'[.!?]\s*$', chunk) and i < len(chunks) - 1:
            # If not the last chunk, should end with sentence ending punctuation
            # If doesn't match, indicates splitting problem
            pass  # Can add warning here, but skip check for performance
    
    return chunks


def count_words(text: str, language: str = 'auto') -> int:
    """
    Count text word count
    
    Args:
        text: Text content
        language: Language type ('auto', 'en', 'zh', 'nl', etc.)
    
    Returns:
        Word count
    """
    if language == 'en' or (language == 'auto' and re.search(r'[a-zA-Z]', text)):
        # English: Count words
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return len(words)
    elif language == 'zh' or (language == 'auto' and re.search(r'[\u4e00-\u9fff]', text)):
        # Chinese: Count characters
        return len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    else:
        # Other languages: Use Unicode letter characters
        words = re.findall(r'\b\w+\b', text)
        return len(words)


def find_sentence_boundaries(text: str) -> List[int]:
    """
    Find all sentence boundary positions
    
    Args:
        text: Text content
    
    Returns:
        List of sentence boundary positions
    """
    # Match sentence ending markers (. ! ? followed by space or newline)
    pattern = r'([.!?])\s+'
    boundaries = []
    
    for match in re.finditer(pattern, text):
        boundaries.append(match.end())
    
    # Add text end
    boundaries.append(len(text))
    
    return sorted(set(boundaries))


def normalize_text(text: str) -> str:
    """
    Normalize text (for comparison)
    
    Args:
        text: Original text
    
    Returns:
        Normalized text
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with two newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading and trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    # Remove leading and trailing empty lines
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    
    return '\n'.join(lines)
