#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Generation Module
Generate professionally formatted PDF files from summaries directory

Features:
- Auto cover generation: Extract book title and author from filename, or use 00_Cover.md file
- Professional typesetting: Use Playwright and Chromium to generate high-quality PDF
- Table of contents support: Automatically generate table of contents page
- Chinese font support: Perfect support for Chinese typesetting
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Tuple
from markdown import markdown

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from .templates import get_pdf_css


def clean_text(text: str) -> str:
    """Remove unwanted text, especially Expert Ghost-Reader related text in the first line"""
    lines = text.split('\n')
    
    # Check and remove Expert Ghost-Reader related text in the first line
    if lines:
        first_line = lines[0].strip()
        # Match various variants
        patterns = [
            r'Okay, Expert Ghost-Reader is ready. This is a ["""]high-fidelity condensed version["""] rewrite of this chapter.',
            r'Okay, Expert Ghost-Reader is ready.*?rewrite.',
            r'Expert Ghost-Reader.*?rewrite.',
            r'Okay,.*?Expert Ghost-Reader.*?ready.*?rewrite.',
            r'Expert Ghost-Reader.*?ready.*?rewrite.',
        ]
        
        for pattern in patterns:
            if re.match(pattern, first_line):
                lines = lines[1:]  # Remove first line
                break
    
    # Recombine text
    text = '\n'.join(lines)
    
    # Remove possible residual multiple empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def standardize_title(title: str) -> str:
    """Standardize title, remove 'Chapter X' or 'Chapter X:' format"""
    title = re.sub(r'^第[一二三四五六七八九十百千万\d]+章[：:\s]*', '', title)
    title = re.sub(r'^第\d+章[：:\s]*', '', title)
    title = re.sub(r'^Chapter\s+\d+[:\s]*', '', title, flags=re.IGNORECASE)
    return title.strip()


def extract_title_from_content(content: str) -> Optional[str]:
    """Extract title from content"""
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()
            return standardize_title(title)
    return None


def extract_book_info_from_filename(filename: str) -> Tuple[str, Optional[str]]:
    """Extract book title and author information from filename
    
    Args:
        filename: Filename (can include path)
    
    Returns:
        (book_title, book_author): Book title and author (author may be None)
    """
    # Remove extension
    name = Path(filename).stem
    
    # Try to extract author (usually after -- or -)
    book_title = name
    book_author = None
    
    # Try to match format: "Book Title -- Author" or "Book Title - Author"
    if ' -- ' in name:
        parts = name.split(' -- ', 1)
        book_title = parts[0].strip()
        if len(parts) > 1:
            author_part = parts[1].strip()
            # Remove possible additional information (like publisher, ISBN, etc.)
            # Usually author name is before the first comma or semicolon
            if ',' in author_part:
                book_author = author_part.split(',')[0].strip()
            elif ';' in author_part:
                book_author = author_part.split(';')[0].strip()
            else:
                book_author = author_part
    elif ' - ' in name and name.count(' - ') == 1:
        parts = name.split(' - ', 1)
        book_title = parts[0].strip()
        if len(parts) > 1:
            author_part = parts[1].strip()
            if ',' in author_part:
                book_author = author_part.split(',')[0].strip()
            elif ';' in author_part:
                book_author = author_part.split(';')[0].strip()
            else:
                book_author = author_part
    
    # Clean book title (remove possible additional information)
    # If book title is too long, truncate to first 50 characters
    if len(book_title) > 50:
        book_title = book_title[:50] + '...'
    
    return book_title, book_author


def get_sorted_summary_files(directory: Path, include_all_md: bool = False) -> List[Tuple[str, Path]]:
    """Get sorted summary file list
    
    Args:
        directory: Directory path
        include_all_md: If True, process all .md files; if False, only process *_summary.md files
    
    Returns:
        File list, each element is a (filename, filepath) tuple
    """
    files = []
    for file in sorted(os.listdir(directory)):
        if file.startswith('.'):
            continue
        if file == '00_Cover.md' or file == '00_Cover':
            continue  # Skip cover file
        if include_all_md:
            if not file.endswith('.md'):
                continue
        else:
            if not file.endswith('_summary.md'):
                continue
        file_path = directory / file
        if file_path.is_file():
            files.append((file, file_path))
    
    return sorted(files)


def markdown_to_html(markdown_text: str, is_cover: bool = False) -> str:
    """Convert Markdown to HTML"""
    # Clean text
    markdown_text = clean_text(markdown_text)
    
    # Standardize title
    title = extract_title_from_content(markdown_text)
    if title and not is_cover:
        # Remove original title line
        lines = markdown_text.split('\n')
        new_lines = []
        title_found = False
        for line in lines:
            if not title_found and line.strip().startswith('# '):
                title_found = True
                continue
            new_lines.append(line)
        markdown_text = '\n'.join(new_lines)
        # Add standardized title
        markdown_text = f"# {title}\n\n{markdown_text}"
    
    # Convert to HTML
    html = markdown(markdown_text, extensions=['extra', 'codehilite', 'tables'])
    return html


def get_html_template() -> str:
    """Return HTML template"""
    pdf_css = get_pdf_css()
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Summary</title>
    <style>
        {pdf_css}
    </style>
</head>
<body>
    {{content}}
</body>
</html>"""


def generate_pdf_from_summaries(
    summaries_dir: Path,
    output_path: Path,
    book_title: Optional[str] = None,
    book_subtitle: Optional[str] = None,
    book_author: Optional[str] = None,
    skip_files: Optional[List[str]] = None,
    auto_extract_title: bool = True,
    include_all_md: bool = False
) -> bool:
    """
    Generate PDF from summaries directory
    
    Args:
        summaries_dir: Summaries directory path
        output_path: Output PDF file path
        book_title: Book title (optional, if None and auto_extract_title=True, will try to extract from filename)
        book_subtitle: Book subtitle (optional)
        book_author: Author (optional, if None and auto_extract_title=True, will try to extract from filename)
        skip_files: List of filename keywords to skip (e.g., ['Front_Matter', 'Authors_Note'])
        auto_extract_title: Whether to automatically extract book title and author from filename (default True)
        include_all_md: Whether to process all .md files (default False, only process *_summary.md)
    
    Returns:
        bool: Whether generation was successful
    """
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError(
            "playwright is not installed. Please run:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        )
    
    if skip_files is None:
        skip_files = ['Front_Matter', 'Authors_Note']
    
    # If book title not provided and auto-extract enabled, try to extract from book file in parent directory
    if (not book_title or not book_author) and auto_extract_title:
        script_dir = summaries_dir.parent
        for f in script_dir.glob("*.txt"):
            extracted_title, extracted_author = extract_book_info_from_filename(f.name)
            if not book_title:
                book_title = extracted_title
            if not book_author:
                book_author = extracted_author
            break
        if not book_title:
            for f in script_dir.glob("*.epub"):
                extracted_title, extracted_author = extract_book_info_from_filename(f.name)
                if not book_title:
                    book_title = extracted_title
                if not book_author:
                    book_author = extracted_author
                break
    
    # If still not found, use default value
    if not book_title:
        book_title = "Book Summary"
    
    # Get all summary files
    files = get_sorted_summary_files(summaries_dir, include_all_md=include_all_md)
    
    if not files:
        if include_all_md:
            raise ValueError(f"No .md files found in {summaries_dir}")
        else:
            raise ValueError(f"No *_summary.md files found in {summaries_dir}")
    
    print(f"Found {len(files)} files")
    
    # Check if 00_Cover file exists
    cover_file_found = False
    cover_html = None
    cover_file_md = summaries_dir / "00_Cover.md"
    cover_file_no_ext = summaries_dir / "00_Cover"
    
    if cover_file_md.exists():
        try:
            with open(cover_file_md, 'r', encoding='utf-8') as f:
                cover_content = f.read()
            lines = [line.strip() for line in cover_content.split('\n') if line.strip()]
            if lines:
                cover_html = '<div class="cover">'
                is_first = True
                for line in lines:
                    if is_first:
                        cover_html += f'<div class="cover-title">{line}</div>'
                        is_first = False
                    else:
                        cover_html += f'<div class="cover-subtitle">{line}</div>'
                cover_html += '</div>'
                cover_file_found = True
                print("  ✓ Using 00_Cover.md file as cover")
        except Exception as e:
            print(f"  ⚠️  Failed to read cover file: {e}")
    elif cover_file_no_ext.exists():
        try:
            with open(cover_file_no_ext, 'r', encoding='utf-8') as f:
                cover_content = f.read()
            lines = [line.strip() for line in cover_content.split('\n') if line.strip()]
            if lines:
                cover_html = '<div class="cover">'
                is_first = True
                for line in lines:
                    if is_first:
                        cover_html += f'<div class="cover-title">{line}</div>'
                        is_first = False
                    else:
                        cover_html += f'<div class="cover-subtitle">{line}</div>'
                cover_html += '</div>'
                cover_file_found = True
                print("  ✓ Using 00_Cover file as cover")
        except Exception as e:
            print(f"  ⚠️  Failed to read cover file: {e}")
    
    # Collect table of contents items (skip functional chapters)
    toc_items = []
    print("\nFirst pass: Collecting titles...")
    for filename, filepath in files:
        # Skip specified files
        should_skip = any(keyword in filename for keyword in skip_files)
        if should_skip:
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            title = extract_title_from_content(content)
            if title:
                toc_items.append(title)
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
    
    # Build HTML content
    print("\nSecond pass: Generating HTML content...")
    html_parts = []
    
    # Cover (if 00_Cover file not found, auto-generate)
    if not cover_file_found:
        cover_html = '<div class="cover">'
        cover_html += f'<div class="cover-title">{book_title}</div>'
        if book_subtitle:
            cover_html += f'<div class="cover-subtitle">{book_subtitle}</div>'
        if book_author:
            cover_html += f'<div class="cover-author">by {book_author}</div>'
        cover_html += '<div class="cover-subtitle" style="margin-top: 60pt;"></div>'
        cover_html += '<div class="cover-subtitle">Summarized by Vibe Reading</div>'
        cover_html += '</div>'
        print(f"  ✓ Auto-generated cover: {book_title}")
        if book_author:
            print(f"    Author: {book_author}")
    
    html_parts.append(cover_html)
    
    # Table of contents
    if toc_items:
        toc_html = '<div class="toc">'
        toc_html += '<div class="toc-title">Table of Contents</div>'
        for title in toc_items:
            toc_html += f'<div class="toc-item">{title}</div>'
        toc_html += '</div>'
        html_parts.append(toc_html)
    
    # Main content
    chapter_count = 0
    for idx, (filename, filepath) in enumerate(files):
        # Skip front matter (already shown in cover)
        should_skip = any(keyword in filename for keyword in skip_files)
        if should_skip:
            continue
        
        print(f"Processing file {idx+1}/{len(files)}: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert to HTML
            html_content = markdown_to_html(content)
            
            # Add chapter separator (starting from first non-functional chapter)
            if chapter_count > 0:
                html_parts.append(f'<div class="chapter">{html_content}</div>')
            else:
                html_parts.append(f'<div>{html_content}</div>')
            
            chapter_count += 1
                
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            continue
    
    # Merge all HTML
    template = get_html_template()
    # Replace placeholder, avoid CSS brace conflicts
    full_html = template.replace('{{content}}', ''.join(html_parts))
    
    # Generate PDF using Playwright
    print("\nGenerating PDF...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(full_html, wait_until='networkidle')
            
            page.pdf(
                path=str(output_path),
                format='A4',
                margin={
                    'top': '2.5cm',
                    'right': '2cm',
                    'bottom': '2.5cm',
                    'left': '2.5cm'
                },
                print_background=True,
                display_header_footer=True,
                header_template='<div></div>',  # Empty header, no page number
                footer_template='<div style="font-size:9pt;color:#666;text-align:center;width:100%;">— <span class="pageNumber"></span> —</div>'
            )
            
            browser.close()
        
        print(f"\nPDF generated: {output_path}")
        print(f"Total {len(toc_items)} chapters")
        return True
    except Exception as e:
        error_msg = str(e)
        # Check if it's a browser not installed error
        if "Executable doesn't exist" in error_msg or "chromium" in error_msg.lower():
            raise RuntimeError(
                "Chromium browser is not installed. Please run:\n"
                "  playwright install chromium"
            )
        else:
            raise


def generate_pdf_from_combined_content(
    content: str,
    output_path: Path,
    book_title: str,
    book_author: str,
    model_name: str,
    gen_date: str,
    toc_items: Optional[List[str]] = None,
    summaries_dir: Optional[Path] = None
) -> bool:
    """
    Generate PDF from combined content string (for existing flow in main.py)
    
    Args:
        content: Combined Markdown content
        output_path: Output PDF file path
        book_title: Book title
        book_author: Author
        model_name: Model name
        gen_date: Generation date
        toc_items: Table of contents item list (optional)
        summaries_dir: Summaries directory path (optional, for finding 00_Cover file)
    
    Returns:
        bool: Whether generation was successful
    """
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError(
            "playwright is not installed. Please run:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        )
    
    from .templates import get_pdf_css
    
    # Check if 00_Cover file exists
    cover_html = None
    if summaries_dir:
        cover_file_md = summaries_dir / "00_Cover.md"
        cover_file_no_ext = summaries_dir / "00_Cover"
        
        if cover_file_md.exists():
            try:
                with open(cover_file_md, 'r', encoding='utf-8') as f:
                    cover_content = f.read()
                lines = [line.strip() for line in cover_content.split('\n') if line.strip()]
                if lines:
                    cover_html = '<div class="cover">'
                    is_first = True
                    for line in lines:
                        if is_first:
                            cover_html += f'<div class="cover-title">{line}</div>'
                            is_first = False
                        else:
                            cover_html += f'<div class="cover-subtitle">{line}</div>'
                    cover_html += '</div>'
                    print("  ✓ Using 00_Cover.md file as cover")
            except Exception as e:
                print(f"  ⚠️  Failed to read cover file: {e}")
        elif cover_file_no_ext.exists():
            try:
                with open(cover_file_no_ext, 'r', encoding='utf-8') as f:
                    cover_content = f.read()
                lines = [line.strip() for line in cover_content.split('\n') if line.strip()]
                if lines:
                    cover_html = '<div class="cover">'
                    is_first = True
                    for line in lines:
                        if is_first:
                            cover_html += f'<div class="cover-title">{line}</div>'
                            is_first = False
                        else:
                            cover_html += f'<div class="cover-subtitle">{line}</div>'
                    cover_html += '</div>'
                    print("  ✓ Using 00_Cover file as cover")
            except Exception as e:
                print(f"  ⚠️  Failed to read cover file: {e}")
    
    # If no cover file found, use default cover
    if not cover_html:
        cover_html = f'''<div class="cover">
    <div class="cover-title">{book_title}</div>
    <div class="cover-subtitle">by {book_author}</div>
    <div class="cover-subtitle" style="margin-top: 60pt;"></div>
    <div class="cover-subtitle">Summarized by Vibe_reading ({model_name})</div>
    <div class="cover-subtitle">{gen_date}</div>
</div>'''
    
    # Generate table of contents
    toc_html = ''
    if toc_items:
        toc_html = '<div class="toc">'
        toc_html += '<div class="toc-title">Table of Contents</div>'
        for title in toc_items:
            toc_html += f'<div class="toc-item">{title}</div>'
        toc_html += '</div>'
    
    # Clean content
    content = clean_text(content)
    
    # Convert Markdown to HTML
    html_body = markdown(content, extensions=['extra', 'codehilite', 'tables'])
    
    # Handle chapter separation: add chapter class to each h1 (except the first)
    h1_pattern = r'<h1>(.*?)</h1>'
    h1_matches = list(re.finditer(h1_pattern, html_body))
    
    if len(h1_matches) > 1:
        # Add chapter class starting from second h1
        offset = 0
        for i, match in enumerate(h1_matches[1:], start=1):  # Skip first
            start_pos = match.start() + offset
            # Add <div class="chapter"> before h1
            html_body = html_body[:start_pos] + '<div class="chapter">' + html_body[start_pos:]
            offset += len('<div class="chapter">')
            # Add </div> after corresponding </h1>
            end_pos = match.end() + offset
            html_body = html_body[:end_pos] + '</div>' + html_body[end_pos:]
            offset += len('</div>')
    
    # Generate complete HTML
    pdf_css = get_pdf_css()
    html_with_styles = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title}</title>
    <style>
        {pdf_css}
    </style>
</head>
<body>
    {cover_html}
    {toc_html}
    {html_body}
</body>
</html>"""
    
    # Generate PDF using Playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_with_styles, wait_until='networkidle')
            
            page.pdf(
                path=str(output_path),
                format='A4',
                margin={
                    'top': '2.5cm',
                    'right': '2cm',
                    'bottom': '2.5cm',
                    'left': '2.5cm'
                },
                print_background=True,
                display_header_footer=True,
                header_template='<div></div>',  # Empty header
                footer_template='<div style="font-size:9pt;color:#666;text-align:center;width:100%;">— <span class="pageNumber"></span> —</div>'
            )
            
            browser.close()
        
        return True
    except Exception as e:
        error_msg = str(e)
        # Check if it's a browser not installed error
        if "Executable doesn't exist" in error_msg or "chromium" in error_msg.lower():
            raise RuntimeError(
                "Chromium browser is not installed. Please run:\n"
                "  playwright install chromium"
            )
        else:
            raise
