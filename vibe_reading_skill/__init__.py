"""
Vibe Reading Skill - Intelligent Reading Analysis Agent Skill

An AI-driven book reading analysis tool that can intelligently identify chapters, deeply analyze content,
and generate multiple format outputs (Markdown, PDF, HTML).
"""

from pathlib import Path
from typing import Dict, Optional, Any

from .main import VibeReadingSkill
from .pdf_generator import (
    generate_pdf_from_summaries,
    generate_pdf_from_combined_content
)


def process_book(
    input_path: str,
    output_dir: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **options: Any
) -> Dict[str, Any]:
    """
    Skill main entry function - Process book and generate analysis report
    
    This is the standard interface for the skill, which can be called by IDE or skill marketplace.
    
    Features:
    - Intelligent chapter identification: AI automatically identifies book structure, supports progressive preview for large documents
    - Auto cover generation: Extract book title and author from filename, generate professional PDF cover
    - Smart retry mechanism: Automatically retry when encountering API quota limits (up to 5 times, wait 90/120/150/180/210 seconds)
    - Auto error fixing: When AI-generated code execution fails, AI will see the error and regenerate
    
    Args:
        input_path: Input file path (EPUB or TXT format)
        output_dir: Output directory (optional, default uses project directory structure)
        api_key: Gemini API Key (optional, can also be set via environment variable)
        model: Gemini model to use (optional, default gemini-2.5-pro)
        **options: Other options
            - generate_pdf: Whether to generate PDF (default True, requires playwright and chromium installation)
            - generate_html: Whether to generate HTML (default True)
            - base_dir: Project root directory (default current directory)
    
    Returns:
        Dict containing processing results:
        {
            "status": "success" | "error",
            "message": "Processing complete" | error message,
            "output_paths": {
                "chapters": "chapters/",
                "summaries": "summaries/",
                "pdf": "pdf/book_summary.pdf",  # If generated successfully
                "html": "html/interactive_reader.html"
            },
            "metadata": {
                "book_title": "...",
                "chapter_count": 10,
                "processing_time": 123.45
            }
        }
    
    Example:
        >>> result = process_book("book.epub")
        >>> print(result["status"])
        'success'
        >>> if result["status"] == "success":
        ...     print(f"PDF: {result['output_paths']['pdf']}")
        ...     print(f"Chapter count: {result['metadata']['chapter_count']}")
    
    Note:
        - If encountering API quota limits (429 error), system will automatically retry
        - PDF generation requires playwright and chromium installation (see README.md for details)
        - Cover will be automatically extracted from filename, or use summaries/00_Cover.md file
    """
    import time
    from pathlib import Path
    
    start_time = time.time()
    
    try:
        # Parse parameters
        input_file = Path(input_path)
        if not input_file.exists():
            return {
                "status": "error",
                "message": f"Input file does not exist: {input_path}",
                "output_paths": {},
                "metadata": {}
            }
        
        # Determine output directory
        if output_dir:
            base_dir = Path(output_dir)
        else:
            base_dir = options.get("base_dir", Path("."))
        
        # Create skill instance
        skill = VibeReadingSkill(
            api_key=api_key,
            base_dir=base_dir,
            model=model
        )
        
        # Process book
        skill.process(input_file)
        
        # Collect output paths
        processing_time = time.time() - start_time
        
        # Try to get book title
        book_title = "Book Summary"
        summary_files = list(skill.summaries_dir.glob("*.md"))
        if summary_files:
            try:
                from .utils import read_file
            except ImportError:
                from utils import read_file
            first_summary = read_file(summary_files[0])
            import re
            title_match = re.search(r'^#\s+(.+)$', first_summary, re.MULTILINE)
            if title_match:
                book_title = title_match.group(1)
        
        return {
            "status": "success",
            "message": "Book processing complete",
            "output_paths": {
                "chapters": str(skill.chapters_dir),
                "summaries": str(skill.summaries_dir),
                "pdf": str(skill.pdf_dir / "book_summary.pdf") if (skill.pdf_dir / "book_summary.pdf").exists() else None,
                "html": str(skill.html_dir / "interactive_reader.html") if (skill.html_dir / "interactive_reader.html").exists() else None
            },
            "metadata": {
                "book_title": book_title,
                "chapter_count": len(list(skill.chapters_dir.glob("*.txt"))),
                "processing_time": round(processing_time, 2)
            }
        }
    
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"Processing failed: {str(e)}",
            "error_details": traceback.format_exc(),
            "output_paths": {},
            "metadata": {}
        }


# Export main classes and functions
__all__ = [
    "VibeReadingSkill",
    "process_book",
    "generate_pdf_from_summaries",
    "generate_pdf_from_combined_content",
]

__version__ = "0.1.0"
