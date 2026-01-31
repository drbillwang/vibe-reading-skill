#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vibe Reading Skill - Main Program
Intelligent Reading Analysis Agent Skill
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    from .gemini_client import GeminiClient
    from .utils import (
        ensure_dir, epub_to_txt, read_file, write_file,
        split_text_by_lines, count_words
    )
    from .prompts import (
        get_chapter_identification_prompt,
        get_chapter_boundary_prompt,
        get_fallback_chapter_identification_prompt,
        get_fix_chapter_format_prompt,
        get_fix_chapter_line_numbers_prompt,
        get_further_breakdown_prompt,
        get_context_strategy_prompt,
        get_chapter_analysis_prompt
    )
    from .templates import (
        get_pdf_css,
        get_html_css,
        get_pdf_html_template,
        get_html_interface_template,
        get_html_javascript_template
    )
except ImportError:
    # Support direct running of main.py or external calls
    import sys
    from pathlib import Path
    # Add package path to sys.path
    package_dir = Path(__file__).parent.parent
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    
    try:
        from vibe_reading_skill.gemini_client import GeminiClient
        from vibe_reading_skill.utils import (
            ensure_dir, epub_to_txt, read_file, write_file,
            split_text_by_lines, count_words
        )
        from vibe_reading_skill.prompts import (
            get_chapter_identification_prompt,
            get_chapter_boundary_prompt,
            get_fallback_chapter_identification_prompt,
            get_fix_chapter_format_prompt,
            get_fix_chapter_line_numbers_prompt,
            get_further_breakdown_prompt,
            get_context_strategy_prompt,
            get_chapter_analysis_prompt
        )
        from vibe_reading_skill.templates import (
            get_pdf_css,
            get_html_css,
            get_pdf_html_template,
            get_html_interface_template,
            get_html_javascript_template
        )
    except ImportError:
        # If still fails, try direct import (running inside package directory)
        from gemini_client import GeminiClient
        from utils import (
            ensure_dir, epub_to_txt, read_file, write_file,
            split_text_by_lines, count_words
        )
        from prompts import (
            get_chapter_identification_prompt,
            get_chapter_boundary_prompt,
            get_fallback_chapter_identification_prompt,
            get_fix_chapter_format_prompt,
            get_fix_chapter_line_numbers_prompt,
            get_further_breakdown_prompt,
            get_context_strategy_prompt,
            get_chapter_analysis_prompt
        )
        from templates import (
            get_pdf_css,
            get_html_css,
            get_pdf_html_template,
            get_html_interface_template,
            get_html_javascript_template
        )


class VibeReadingSkill:
    """
    Vibe Reading Skill Main Class
    
    Features:
    - Intelligent chapter identification: AI automatically identifies book structure, supports progressive preview strategy for large documents
    - Auto error fixing: When AI-generated code execution fails, AI will see the error and regenerate
    - Smart retry mechanism: Automatically retries when encountering API quota limits (up to 5 times)
    - Auto cover generation: Extract book title and author from filename, generate professional PDF cover
    """
    
    def __init__(self, api_key: Optional[str] = None, base_dir: Path = Path("."), model: Optional[str] = None):
        """
        Initialize
        
        Args:
            api_key: Gemini API Key
            base_dir: Project root directory (default current directory)
            model: Gemini model to use (optional)
        """
        self.client = GeminiClient(api_key=api_key, model=model)
        self.base_dir = Path(base_dir)
        
        # Create directory structure
        self.input_dir = ensure_dir(self.base_dir / "input")  # Input file directory
        self.chapters_dir = ensure_dir(self.base_dir / "chapters")  # Split original text txt
        self.summaries_dir = ensure_dir(self.base_dir / "summaries")  # Summary directory
        self.pdf_dir = ensure_dir(self.base_dir / "pdf")  # PDF directory
        self.html_dir = ensure_dir(self.base_dir / "html")  # HTML directory
        
        # Load SKILL.md as system instruction
        skill_path = Path(__file__).parent / "SKILL.md"
        if skill_path.exists():
            self.system_instruction = read_file(skill_path)
        else:
            self.system_instruction = None
    
    def preprocess_document(self, input_path: Path) -> str:
        """
        Phase One: Document preprocessing and format conversion
        
        Args:
            input_path: Input file path
        
        Returns:
            Cleaned text content
        """
        print("=" * 70)
        print("Phase One: Document Preprocessing and Format Conversion")
        print("=" * 70)
        
        if input_path.suffix.lower() == '.epub':
            print(f"EPUB format detected, converting...")
            # Save converted TXT to input directory
            txt_path = self.input_dir / f"{input_path.stem}.txt"
            text = epub_to_txt(input_path, txt_path)
            print(f"✓ EPUB converted to TXT: {txt_path}")
        else:
            print(f"Reading TXT file...")
            text = read_file(input_path)
            print(f"✓ File reading complete")
        
        return text
    
    def identify_chapters(self, document_text: str) -> List[Dict]:
        """
        Phase Two: Intelligent Chapter Identification (with progressive preview and auto error fixing)
        
        Strategy:
        1. Progressive preview: If document is too large, gradually reduce preview content (500→400→300→300→300 lines)
        2. AI generates code: Let AI analyze document format and generate scanning code
        3. Auto error fixing: If code execution fails, let AI see the error and regenerate (up to 3 times)
        4. Fallback: If all attempts fail, use direct AI query method
        
        Args:
            document_text: Document text
        
        Returns:
            Chapter information list
        """
        print("\n" + "=" * 70)
        print("Phase Two: Intelligent Chapter Identification and Splitting")
        print("=" * 70)
        
        lines = document_text.split('\n')
        total_lines = len(lines)
        
        # ========== Phase 1: AI Generate Scanning Code (Progressive Preview Strategy) ==========
        print("\nPhase 1: AI analyzes document format and generates scanning code...")
        
        # Define preview strategy sequence (gradually reduce preview amount)
        preview_strategies = [
            # Strategy 1: Initial attempt (maximum preview)
            {"start": 500, "end": 500, "mid1": 200, "mid2": 200, "desc": "Beginning 500/End 500/Middle 25% 400/Middle 50% 400"},
            # Strategy 2: First reduction
            {"start": 400, "end": 400, "mid1": 150, "mid2": 150, "desc": "Beginning 400/End 400/Middle 25% 300/Middle 50% 300"},
            # Strategy 3: Continue reduction
            {"start": 300, "end": 300, "mid1": 100, "mid2": 100, "desc": "Beginning 300/End 300/Middle 25% 200/Middle 50% 200"},
            # Strategy 4: Only keep beginning and end
            {"start": 300, "end": 300, "mid1": 0, "mid2": 0, "desc": "Beginning 300/End 300"},
            # Strategy 5: Minimum preview (last attempt)
            {"start": 300, "end": 0, "mid1": 0, "mid2": 0, "desc": "Only beginning 300 lines"},
        ]
        
        scan_code = None
        last_error = None
        
        response = None
        for i, strategy in enumerate(preview_strategies, 1):
            try:
                if i > 1:
                    print(f"  Trying strategy {i}: {strategy['desc']}...")
                else:
                    print(f"  Trying strategy {i}: {strategy['desc']}...")
                
                prompt = get_chapter_identification_prompt(
                    document_text,
                    start_lines=strategy['start'],
                    end_lines=strategy['end'],
                    mid1_range=strategy['mid1'],
                    mid2_range=strategy['mid2']
                )
                
                response = self.client.generate_content(
                    prompt,
                    system_instruction=self.system_instruction,
                    temperature=0.3
                )
                
                # If successful, break loop
                print(f"  ✓ Strategy {i} successful")
                break
                
            except Exception as e:
                error_msg = str(e)
                last_error = e
                
                # Check if it's a token limit exceeded error
                if "token count exceeds" in error_msg.lower() or "exceeds the maximum" in error_msg.lower():
                    if i < len(preview_strategies):
                        print(f"  ⚠️  Token limit exceeded, trying to reduce preview amount...")
                        continue
                    else:
                        # All strategies failed
                        raise Exception(
                            f"Document too large, even previewing only first 300 lines exceeds limit.\n"
                            f"Document total lines: {total_lines:,} lines\n"
                            f"Document total length: {len(document_text):,} characters\n"
                            f"Suggestion: Please consider using a smaller document, or contact developer to optimize strategy for handling large documents."
                        )
                else:
                    # Other errors, directly raise
                    raise
        
        # Check if response was successfully obtained
        if response is None:
            if last_error:
                raise last_error
            else:
                raise Exception("Unable to generate scanning code, all strategies failed")
        
        # Parse AI-returned scanning code
        scan_code = None
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response)
            
            scan_code = result.get('code', '')
            if not scan_code:
                print("  ⚠️  AI did not return scanning code, using fallback...")
                chapters = self._fallback_chapter_identification(document_text)
                return self._validate_and_fix_chapters(chapters, document_text)
        except Exception as e:
            print(f"  ⚠️  Failed to parse AI response: {str(e)}")
            chapters = self._fallback_chapter_identification(document_text)
            return self._validate_and_fix_chapters(chapters, document_text)
        
        # ========== Execute scanning code, find all chapter markers (with error retry loop) ==========
        print("  Executing scanning code, finding all chapter markers...")
        markers = []
        max_retries = 3  # Maximum 3 retries
        current_code = scan_code
        attempt = 0
        
        while attempt <= max_retries:
            try:
                local_vars = {'document_text': document_text}
                exec(current_code, {'__builtins__': __builtins__, 're': re, 'json': json}, local_vars)
                
                # If code defines a function, call it
                if 'scan_chapter_markers' in local_vars and callable(local_vars['scan_chapter_markers']):
                    markers = local_vars['scan_chapter_markers'](document_text)
                elif 'markers' in local_vars:
                    markers = local_vars['markers']
                
                # Check if markers found
                if markers and len(markers) > 0:
                    print(f"  ✓ Found {len(markers)} chapter markers")
                    break  # Success, break loop
                else:
                    # Code executed successfully but found no markers
                    if attempt < max_retries:
                        attempt += 1
                        print(f"  ⚠️  Scanning code found no markers, asking AI to regenerate code (attempt {attempt}/{max_retries})...")
                        # Let AI see the error and regenerate code
                        fix_prompt = f"""The Python scanning code you generated executed successfully but found no chapter markers.

Original code:
```python
{current_code}
```

Problem: Code execution returned empty list, found no chapter markers.

Please analyze the reason and regenerate code:
1. Check if regular expressions or matching rules are correct
2. Ensure code can iterate through all lines of the entire document
3. Adjust matching patterns to adapt to the document's actual format

Document statistics:
- Total length: {len(document_text):,} characters
- Total lines: {total_lines:,} lines

Document preview (first 1000 lines, for format analysis):
{'\n'.join(document_text.split('\n')[:1000])}

Please return fixed code (JSON format):
{{
    "code": "Fixed Python scanning code (string)",
    "format_analysis": "Chapter format characteristics you observed",
    "reasoning": "Why previous code found no markers and how to fix"
}}"""
                        
                        fix_response = self.client.generate_content(
                            fix_prompt,
                            system_instruction=self.system_instruction,
                            temperature=0.3
                        )
                        
                        try:
                            json_match = re.search(r'\{.*\}', fix_response, re.DOTALL)
                            if json_match:
                                fix_result = json.loads(json_match.group())
                            else:
                                fix_result = json.loads(fix_response)
                            
                            current_code = fix_result.get('code', current_code)
                            if not current_code:
                                print("  ⚠️  AI did not return new code, using fallback...")
                                chapters = self._fallback_chapter_identification(document_text)
                                return self._validate_and_fix_chapters(chapters, document_text)
                            continue  # Retry new code
                        except Exception as e2:
                            print(f"  ⚠️  Failed to parse AI fix response: {str(e2)}")
                            if attempt >= max_retries:
                                break
                            attempt += 1
                            continue
                    else:
                        print("  ⚠️  Retry count exhausted, using fallback...")
                        chapters = self._fallback_chapter_identification(document_text)
                        return self._validate_and_fix_chapters(chapters, document_text)
            
            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries:
                    attempt += 1
                    print(f"  ⚠️  Scanning code execution failed: {error_msg}")
                    print(f"  Asking AI to regenerate code based on error information (attempt {attempt}/{max_retries})...")
                    
                    # Let AI see the error and regenerate code
                    fix_prompt = f"""The Python scanning code you generated failed to execute, error message below:

Error: {error_msg}

Original code:
```python
{current_code}
```

Please analyze the error cause, then:
1. Fix problems in the code (such as syntax errors, escape character errors, variable name errors, etc.)
2. Regenerate correct code

Document statistics:
- Total length: {len(document_text):,} characters
- Total lines: {total_lines:,} lines

Document preview (first 1000 lines, for format analysis):
{'\n'.join(document_text.split('\n')[:1000])}

Please return fixed code (JSON format):
{{
    "code": "Fixed Python scanning code (string, note escape characters)",
    "error_analysis": "Error cause analysis",
    "fix_reasoning": "How to fix"
}}"""
                    
                    try:
                        fix_response = self.client.generate_content(
                            fix_prompt,
                            system_instruction=self.system_instruction,
                            temperature=0.3
                        )
                        
                        json_match = re.search(r'\{.*\}', fix_response, re.DOTALL)
                        if json_match:
                            fix_result = json.loads(json_match.group())
                        else:
                            fix_result = json.loads(fix_response)
                        
                        current_code = fix_result.get('code', current_code)
                        if not current_code:
                            print("  ⚠️  AI did not return new code, using fallback...")
                            chapters = self._fallback_chapter_identification(document_text)
                            return self._validate_and_fix_chapters(chapters, document_text)
                        continue  # Retry new code
                    except Exception as e2:
                        print(f"  ⚠️  AI fix also failed: {str(e2)}")
                        if attempt >= max_retries:
                            break
                        continue
                else:
                    print(f"  ⚠️  Retry count exhausted, using fallback...")
                    chapters = self._fallback_chapter_identification(document_text)
                    return self._validate_and_fix_chapters(chapters, document_text)
        
        # If loop ended without finding markers, use fallback
        if not markers or len(markers) == 0:
            print("  ⚠️  All retries failed, using fallback...")
            chapters = self._fallback_chapter_identification(document_text)
            return self._validate_and_fix_chapters(chapters, document_text)
        
        # ========== Phase 2: Based on scan results, let AI determine boundaries ==========
        print("\nPhase 2: AI determines chapter boundaries based on scan results...")
        boundary_prompt = get_chapter_boundary_prompt(markers, total_lines)
        
        boundary_response = self.client.generate_content(
            boundary_prompt,
            system_instruction=self.system_instruction,
            temperature=0.3
        )
        
        # Parse AI-returned chapter list
        chapters = []
        try:
            json_match = re.search(r'\{.*\}', boundary_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(boundary_response)
            
            chapters = result.get('chapters', [])
            if not chapters or len(chapters) == 0:
                print("  ⚠️  AI did not return chapter list, using fallback...")
                chapters = self._fallback_chapter_identification(document_text)
        except Exception as e:
            print(f"  ⚠️  Failed to parse chapter boundaries: {str(e)}")
            chapters = self._fallback_chapter_identification(document_text)
            
            # Validate chapter format: ensure it's a list of dictionaries
            if chapters:
                if not isinstance(chapters, list):
                    print("  ⚠️  AI returned non-list, attempting conversion...")
                    chapters = [chapters] if chapters else []
                
                # Check if each chapter is a dictionary (if not, fix in split_chapters)
                validated_chapters = []
                for i, ch in enumerate(chapters):
                    if isinstance(ch, dict):
                        validated_chapters.append(ch)
                    else:
                        print(f"  ⚠️  Chapter {i+1} format abnormal ({type(ch).__name__}), will fix during splitting")
                        validated_chapters.append(ch)  # Keep original format, fix in split_chapters
                
                chapters = validated_chapters
            else:
                # If AI-generated code returns empty list, trigger fallback
                print("  ⚠️  AI-generated code returned empty list, triggering fallback...")
                chapters = None  # Mark need for fallback
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ⚠️  AI-generated code execution failed: {error_msg}")
            print("  Asking AI to fix code based on error information...")
            
            # Let AI know error cause and fix
            fix_prompt = f"""The Python code you generated failed to execute, error message below:

Error: {error_msg}

Please analyze the error cause, then:
1. Fix problems in the code (such as escape character errors, syntax errors, etc.)
2. Regenerate correct code

Original prompt requirements:
- Generate a function `identify_chapters(document_text)` 
- Return chapter list, each chapter contains: number, title, start_line, end_line, filename
- Must hardcode accurate line numbers for all chapters

Document statistics:
- Total length: {len(document_text):,} characters
- Total lines: {len(document_text.split(chr(10))):,} lines

Please return fixed code (JSON format):
{{
    "code": "Fixed Python code (string, note escape characters)",
    "chapters": [
        {{
            "number": "00",
            "title": "Introduction",
            "start_line": 1,
            "end_line": 324,
            "filename": "00_Introduction.txt"
        }},
        ...
    ]
}}"""
            
            try:
                fix_response = self.client.generate_content(
                    fix_prompt,
                    system_instruction=self.system_instruction,
                    temperature=0.3
                )
                
                json_match = re.search(r'\{.*\}', fix_response, re.DOTALL)
                if json_match:
                    fix_result = json.loads(json_match.group())
                else:
                    fix_result = json.loads(fix_response)
                
                # Try using fixed code
                fixed_code = fix_result.get('code', '')
                fixed_chapters = fix_result.get('chapters', [])
                
                if fixed_chapters and isinstance(fixed_chapters, list) and len(fixed_chapters) > 0:
                    print(f"  ✓ AI directly returned {len(fixed_chapters)} chapters after fix")
                    chapters = fixed_chapters
                elif fixed_code:
                    print("  Executing fixed code...")
                    try:
                        local_vars = {'document_text': document_text}
                        exec(fixed_code, {'__builtins__': __builtins__, 're': re, 'json': json}, local_vars)
                        chapters = local_vars.get('chapters', [])
                        if 'identify_chapters' in local_vars and callable(local_vars['identify_chapters']):
                            chapters = local_vars['identify_chapters'](document_text)
                    except Exception as e3:
                        print(f"  ⚠️  Fixed code execution also failed: {str(e3)}")
                        chapters = []
                else:
                    chapters = []
            except Exception as e2:
                print(f"  ⚠️  AI fix also failed: {str(e2)}")
                chapters = []
            
            # If fix fails, use fallback
            if not chapters or len(chapters) == 0:
                print("  Falling back to direct AI query...")
                fallback_prompt = get_fallback_chapter_identification_prompt(document_text, 50000)
                
                fallback_response = self.client.generate_content(
                    fallback_prompt,
                    system_instruction=self.system_instruction,
                    temperature=0.3
                )
                
                try:
                    json_match = re.search(r'\{.*\}', fallback_response, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        result = json.loads(fallback_response)
                    chapters = result.get('chapters', [])
                except Exception as e3:
                    print(f"  ⚠️  Fallback also failed: {str(e3)}")
                    chapters = []
        
        # If chapter list is empty, use fallback
        if not chapters or len(chapters) == 0:
            print("  ⚠️  Chapter identification failed, using fallback...")
            chapters = self._fallback_chapter_identification(document_text)
        
        # Validate chapter identification reasonableness
        chapters = self._validate_and_fix_chapters(chapters, document_text)
        
        # Verify line number coverage, find gaps and mark as non-main text
        chapters = self._verify_line_coverage(chapters, document_text)
        
        # Fixed use 7000 words as maximum words per chapter (no longer let AI decide)
        self.suggested_max_words = 7000
        
        # Count main text chapters (exclude non-main text chapters)
        content_chapters = [ch for ch in chapters if not ch.get('is_non_content', False)]
        print(f"✓ Identified {len(content_chapters)} main text chapters")
        if len(chapters) > len(content_chapters):
            print(f"  Including {len(chapters) - len(content_chapters)} non-main text chapters (for word count verification)")
        print(f"  Maximum words per chapter: 7000 English words (fixed value, for further breakdown)")
        return chapters
    
    def _validate_and_fix_chapters(self, chapters: List[Dict], document_text: str) -> List[Dict]:
        """
        Validate chapter identification reasonableness, if issues found let AI fix
        
        Args:
            chapters: Chapter list
            document_text: Document text
            
        Returns:
            Fixed chapter list
        """
        if not chapters:
            return chapters
        
        lines = document_text.split('\n')
        total_lines = len(lines)
        
        # Check if there are issues
        issues = []
        
        # Check 1: Are there multiple chapters with end_line equal to document total lines
        chapters_with_full_end = [i for i, ch in enumerate(chapters) 
                                 if isinstance(ch, dict) and 
                                 (ch.get('end_line') or ch.get('end') or 0) == total_lines]
        if len(chapters_with_full_end) > 1:
            issues.append(f"Found {len(chapters_with_full_end)} chapters with end_line equal to document total lines, indicating identification error")
        
        # Check 2: Are there chapters with start_line >= end_line
        invalid_ranges = [i for i, ch in enumerate(chapters)
                         if isinstance(ch, dict) and
                         (ch.get('start_line') or 1) >= (ch.get('end_line') or total_lines)]
        if invalid_ranges:
            issues.append(f"Found {len(invalid_ranges)} chapters with invalid line number ranges")
        
        # Check 3: Are there chapters with start_line == 1 and end_line == total_lines (contains entire document)
        full_doc_chapters = [i for i, ch in enumerate(chapters)
                            if isinstance(ch, dict) and
                            (ch.get('start_line') or 1) == 1 and
                            (ch.get('end_line') or total_lines) == total_lines]
        if len(full_doc_chapters) > 0:
            issues.append(f"Found {len(full_doc_chapters)} chapters containing entire document, indicating identification error")
        
        if issues:
            print(f"  ⚠️  Detected chapter identification issues:")
            for issue in issues:
                print(f"    - {issue}")
            print(f"  Asking AI to re-identify chapters...")
            
            # Let AI re-identify (use fallback, but provide more document content)
            fixed_chapters = self._fallback_chapter_identification(document_text)
            
            # Verify fixed chapters again
            if fixed_chapters:
                return self._validate_and_fix_chapters(fixed_chapters, document_text)
            else:
                # If still fails, use emergency split
                print("  ⚠️  AI re-identification also failed, using emergency split...")
                return self._emergency_split(document_text)
        
        return chapters
    
    def _verify_line_coverage(self, chapters: List[Dict], document_text: str) -> List[Dict]:
        """
        Verify line number coverage, find gaps and mark as non-main text
        
        Args:
            chapters: Chapter list
            document_text: Document text
            
        Returns:
            Complete chapter list including non-main text chapters
        """
        if not chapters:
            return chapters
        
        lines = document_text.split('\n')
        total_lines = len(lines)
        
        # Collect all main text chapter line number ranges (exclude non-main text chapters)
        covered_ranges = []
        for chapter in chapters:
            if isinstance(chapter, dict) and not chapter.get('is_non_content', False):
                start = chapter.get('start_line') or chapter.get('start') or 1
                end = chapter.get('end_line') or chapter.get('end') or total_lines
                try:
                    start = int(start)
                    end = int(end)
                    covered_ranges.append((start, end))
                except (ValueError, TypeError):
                    continue
        
        if not covered_ranges:
            return chapters
        
        # Sort
        covered_ranges.sort(key=lambda x: x[0])
        
        # Find gaps (uncovered line ranges)
        gaps = []
        current_pos = 1
        
        for start, end in covered_ranges:
            if current_pos < start:
                # Found gap
                gaps.append((current_pos, start - 1))
            current_pos = max(current_pos, end + 1)
        
        # Check if there's a gap at the end
        if current_pos <= total_lines:
            gaps.append((current_pos, total_lines))
        
        # If there are gaps, mark as non-main text chapters
        if gaps:
            print(f"\n  Found {len(gaps)} non-main text areas (table of contents, map lists, etc.)")
            non_content_chapters = []
            for i, (gap_start, gap_end) in enumerate(gaps):
                # Read first few lines of gap content for generating title
                gap_preview = '\n'.join(lines[gap_start-1:min(gap_start+5, gap_end)])
                # Try to extract title
                title_match = re.search(r'^(Contents?|Table of Contents|List of Maps|Acknowledgements?|Preface|Title Page)', gap_preview, re.I)
                if title_match:
                    title = title_match.group(1)
                else:
                    title = f"Non-Content Section {i+1}"
                
                non_content_chapters.append({
                    "number": f"NC{i+1:02d}",
                    "title": title,
                    "start_line": gap_start,
                    "end_line": gap_end,
                    "filename": f"NC{i+1:02d}_{title.replace(' ', '_')[:30]}.txt",
                    "is_non_content": True  # Mark as non-main text
                })
            
            # Merge main text chapters and non-main text chapters
            all_chapters = chapters + non_content_chapters
            # Sort by start_line
            all_chapters.sort(key=lambda x: int(x.get('start_line', 0)))
            
            print(f"  ✓ Added {len(non_content_chapters)} non-main text chapters (for word count verification)")
            return all_chapters
        
        return chapters
    
    def _fallback_chapter_identification(self, document_text: str) -> List[Dict]:
        """
        Fallback: If AI-generated code fails, directly ask AI to identify chapters
        
        Args:
            document_text: Document text
            
        Returns:
            Chapter information list
        """
        print("  Using fallback: directly asking AI...")
        
        # Read more document content (first 100000 characters, or entire document if shorter)
        preview_length = min(100000, len(document_text))
        fallback_prompt = get_fallback_chapter_identification_prompt(document_text, preview_length)
        
        try:
            fallback_response = self.client.generate_content(
                fallback_prompt,
                system_instruction=self.system_instruction,
                temperature=0.3
            )
            
            json_match = re.search(r'\{.*\}', fallback_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(fallback_response)
            
            chapters = result.get('chapters', [])
            
            # If still empty, use final backup: split by fixed length
            if not chapters or len(chapters) == 0:
                print("  ⚠️  Fallback also failed, using final backup: split by fixed length...")
                chapters = self._emergency_split(document_text)
            
            return chapters
            
        except Exception as e:
            print(f"  ⚠️  Fallback execution failed: {str(e)}")
            print("  Using final backup: split by fixed length...")
            return self._emergency_split(document_text)
    
    def _emergency_split(self, document_text: str) -> List[Dict]:
        """
        Final backup: If all AI methods fail, split document by fixed length
        
        Args:
            document_text: Document text
            
        Returns:
            Chapter information list
        """
        lines = document_text.split('\n')
        total_lines = len(lines)
        
        # Split into 10 parts
        num_parts = 10
        lines_per_part = total_lines // num_parts
        
        chapters = []
        for i in range(num_parts):
            start_line = i * lines_per_part + 1
            if i == num_parts - 1:
                end_line = total_lines
            else:
                end_line = (i + 1) * lines_per_part
            
            # Try to extract title from content (take first few lines of this part)
            part_preview = '\n'.join(lines[start_line-1:min(start_line+10, end_line)])
            title_match = re.search(r'^(?:CHAPTER|Chapter|Part|第.*?章|第.*?部分)\s*[:\-]?\s*(.+?)$', part_preview, re.MULTILINE | re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()[:50]  # Limit title length
            else:
                title = f"Part {i+1}"
            
            chapters.append({
                "number": f"{i:02d}",
                "title": title,
                "start_line": start_line,
                "end_line": end_line,
                "filename": f"{i:02d}_{title.replace(' ', '_')[:30]}.txt"
            })
        
        print(f"  ✓ Using backup split into {len(chapters)} parts")
        return chapters
    
    def split_chapters(self, document_text: str, chapters: List[Dict]) -> None:
        """
        Execute chapter splitting
        
        Args:
            document_text: Document text
            chapters: Chapter information list (may be in various formats, need intelligent handling)
        """
        print("\nSplitting chapters...")
        lines = document_text.split('\n')
        
        # Intelligently handle chapter format: if format is wrong, let AI fix
        if not chapters:
            print("  ⚠️  No chapter data, skipping split")
            return
        
        # Check and fix chapter format
        fixed_chapters = []
        for i, chapter in enumerate(chapters):
            if isinstance(chapter, dict):
                # Already in dict format, use directly
                fixed_chapters.append(chapter)
            elif isinstance(chapter, str):
                # If string, try to parse or let AI fix
                print(f"  ⚠️  Chapter {i+1} format abnormal (string), attempting fix...")
                try:
                    # Try to parse as JSON
                    parsed = json.loads(chapter)
                    if isinstance(parsed, dict):
                        fixed_chapters.append(parsed)
                    else:
                        # Let AI fix format
                        fixed_chapters.append(self._fix_chapter_format(chapter, document_text, i))
                except:
                    # Let AI fix format
                    fixed_chapters.append(self._fix_chapter_format(chapter, document_text, i))
            else:
                # Other formats, let AI fix
                print(f"  ⚠️  Chapter {i+1} format abnormal, attempting fix...")
                fixed_chapters.append(self._fix_chapter_format(str(chapter), document_text, i))
        
        # Use fixed chapter list
        chapters = fixed_chapters
        
        for i, chapter in enumerate(chapters):
            # Safely get fields, support various possible key names
            start_line = chapter.get('start_line') or chapter.get('start') or chapter.get('startLine') or 1
            end_line = chapter.get('end_line') or chapter.get('end') or chapter.get('endLine') or len(lines)
            filename = chapter.get('filename') or chapter.get('name') or f"{chapter.get('number', '00')}_Chapter.txt"
            
            # Ensure integers
            try:
                start_line = int(start_line)
                end_line = int(end_line)
            except (ValueError, TypeError):
                print(f"  ⚠️  Chapter {i+1} line number format error, using default values")
                start_line = 1
                end_line = len(lines)
            
            # Ensure not None
            if start_line is None:
                start_line = 1
            if end_line is None:
                end_line = len(lines)
            
            # Verify line numbers are reasonable
            if start_line < 1:
                start_line = 1
            if end_line > len(lines):
                end_line = len(lines)
            if start_line >= end_line:
                print(f"  ⚠️  Chapter {i+1} ({filename}) line numbers invalid (start={start_line}, end={end_line}), asking AI to fix...")
                # Let AI re-identify this chapter's line numbers
                fixed = self._fix_chapter_line_numbers(chapter, document_text, i, len(lines))
                start_line = fixed.get('start_line') or 1
                end_line = fixed.get('end_line') or len(lines)
                filename = fixed.get('filename') or filename
                # Ensure integers
                try:
                    start_line = int(start_line)
                    end_line = int(end_line)
                except (ValueError, TypeError):
                    start_line = 1
                    end_line = len(lines)
            
            # Check if all chapters' end_line equal document total lines (indicates identification problem)
            if i > 0 and end_line == len(lines) and start_line == 1:
                print(f"  ⚠️  Chapter {i+1} ({filename}) may be incorrectly identified (contains entire document), asking AI to re-identify...")
                fixed = self._fix_chapter_line_numbers(chapter, document_text, i, len(lines))
                start_line = fixed.get('start_line') or 1
                end_line = fixed.get('end_line') or len(lines)
                filename = fixed.get('filename') or filename
                # Ensure integers
                try:
                    start_line = int(start_line)
                    end_line = int(end_line)
                except (ValueError, TypeError):
                    start_line = 1
                    end_line = len(lines)
            
            chapter_text = split_text_by_lines(document_text, start_line, end_line)
            output_path = self.chapters_dir / filename
            
            # Verify extracted content is reasonable (shouldn't be same as entire document)
            if len(chapter_text) == len(document_text) and i > 0:
                print(f"  ⚠️  Warning: Chapter {i+1} ({filename}) content same as entire document, may be identification error")
                # Try using previous chapter's end_line as start_line
                if i > 0 and isinstance(chapters[i-1], dict):
                    prev_end = chapters[i-1].get('end_line') or chapters[i-1].get('end') or chapters[i-1].get('endLine')
                    if prev_end:
                        try:
                            start_line = int(prev_end) + 1
                            # Let AI decide this chapter's end position
                            fixed = self._fix_chapter_line_numbers(chapter, document_text, i, len(lines), start_line)
                            end_line = fixed.get('end_line') or min(start_line + 1000, len(lines))
                            # Ensure integer
                            try:
                                end_line = int(end_line)
                            except (ValueError, TypeError):
                                end_line = min(start_line + 1000, len(lines))
                            chapter_text = split_text_by_lines(document_text, start_line, end_line)
                            print(f"  ✓ Fixed: {filename} (lines {start_line}-{end_line})")
                        except:
                            pass
            
            write_file(output_path, chapter_text)
            print(f"  ✓ {filename} (lines {start_line}-{end_line}, {len(chapter_text)} characters)")
        
        print(f"\n✓ All chapters saved to: {self.chapters_dir}")
    
    def _fix_chapter_line_numbers(self, chapter: Dict, document_text: str, index: int, total_lines: int, suggested_start: Optional[int] = None) -> Dict:
        """
        Let AI fix chapter line numbers
        
        Args:
            chapter: Chapter dictionary
            document_text: Document text
            index: Chapter index
            total_lines: Document total lines
            suggested_start: Suggested starting line number (optional)
            
        Returns:
            Fixed chapter dictionary
        """
        # Use prompt from prompts.py
        prompt = get_fix_chapter_line_numbers_prompt(chapter, document_text, index, total_lines, suggested_start)
        
        try:
            response = self.client.generate_content(
                prompt,
                system_instruction=self.system_instruction,
                temperature=0.3
            )
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                fixed = json.loads(json_match.group())
                # Get title, use default if not available
                default_title = chapter.get('title', f"Chapter {index+1}")
                # Ensure start_line and end_line are not None
                fixed_start = fixed.get('start_line') or suggested_start or max(1, (index * total_lines // 25))
                fixed_end = fixed.get('end_line') or min(total_lines, ((index + 1) * total_lines // 25))
                # Merge original information
                fixed.update({
                    "number": chapter.get('number', f"{index:02d}"),
                    "title": chapter.get('title', default_title),
                    "start_line": fixed_start,
                    "end_line": fixed_end
                })
                return fixed
            else:
                # If parsing fails, use default values
                default_title = chapter.get('title', f"Chapter {index+1}")
                safe_title = default_title.replace('/', '_').replace('\\', '_')[:50]  # Clean title for filename
                return {
                    "number": chapter.get('number', f"{index:02d}"),
                    "title": default_title,
                    "start_line": suggested_start or max(1, (index * total_lines // 25)),
                    "end_line": min(total_lines, ((index + 1) * total_lines // 25)),
                    "filename": chapter.get('filename', f"{index:02d}_{safe_title}.txt")
                }
        except Exception as e:
            print(f"    ⚠️  AI fix failed: {e}")
            # Use safe default values
            default_title = chapter.get('title', f"Chapter {index+1}")
            safe_title = default_title.replace('/', '_').replace('\\', '_')[:50]  # Clean title for filename
            return {
                "number": chapter.get('number', f"{index:02d}"),
                "title": default_title,
                "start_line": suggested_start or max(1, (index * total_lines // 25)),
                "end_line": min(total_lines, ((index + 1) * total_lines // 25)),
                "filename": chapter.get('filename', f"{index:02d}_{safe_title}.txt")
            }
    
    def _fix_chapter_format(self, raw_chapter: str, document_text: str, index: int) -> Dict:
        """
        Let AI fix chapter format
        
        Args:
            raw_chapter: Raw chapter data (may be string or other format)
            document_text: Document text
            index: Chapter index
            
        Returns:
            Fixed chapter dictionary
        """
        prompt = get_fix_chapter_format_prompt(raw_chapter, document_text)
        
        try:
            response = self.client.generate_content(
                prompt,
                system_instruction=self.system_instruction,
                temperature=0.3
            )
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                fixed = json.loads(json_match.group())
            else:
                fixed = json.loads(response)
            
            return fixed
        except:
            # If fix fails, return default format
            return {
                "number": f"{index:02d}",
                "title": f"Chapter {index+1}",
                "start_line": 1,
                "end_line": len(document_text.split('\n')),
                "filename": f"{index:02d}_Chapter_{index+1}.txt"
            }
    
    def further_breakdown(self, chapters: List[Dict], max_words_per_chapter: Optional[int] = None) -> None:
        """
        Phase Three: Further Breakdown (using breakdown.md method: break at complete sentences)
        
        Args:
            chapters: Chapter information list
            max_words_per_chapter: Maximum words per chapter (English words), fixed at 7000
        """
        print("\n" + "=" * 70)
        print("Phase Three: Further Breakdown")
        print("=" * 70)
        
        # Fixed use 7000 English words as limit
        max_words_per_chapter = 7000
        
        print(f"Maximum words per chapter limit: {max_words_per_chapter} English words (fixed value)")
        
        # Fix format errors in chapters
        fixed_chapters = []
        for i, chapter in enumerate(chapters):
            if not isinstance(chapter, dict):
                print(f"  ⚠️  Detected format error in chapter (index {i}), asking AI to fix...")
                # Try to read file to infer chapter information
                all_files = sorted(self.chapters_dir.glob("*.txt"))
                if i < len(all_files):
                    # Use filename to infer
                    filename = all_files[i].name
                    fixed = {
                        "number": f"{i:02d}",
                        "title": filename.replace('.txt', '').replace('_', ' '),
                        "start_line": 1,
                        "end_line": 1000,
                        "filename": filename
                    }
                else:
                    fixed = self._fix_chapter_format(str(chapter), "", i)
                fixed_chapters.append(fixed)
                chapter = fixed
            else:
                fixed_chapters.append(chapter)
        
        # Update chapters list
        if fixed_chapters != chapters:
            chapters[:] = fixed_chapters
        
        for chapter in chapters:
            # Skip non-main text chapters (no need for further breakdown)
            if chapter.get('is_non_content', False):
                continue
            
            filename = chapter.get('filename', '')
            chapter_path = self.chapters_dir / filename
            
            if not chapter_path.exists():
                continue
            
            chapter_content = read_file(chapter_path)
            
            # Use correct English word count (not tokens, not simple split)
            chapter_length = len(chapter_content)
            word_count = count_words(chapter_content)  # Use count_words function to count English words
            lines = chapter_content.split('\n')
            
            print(f"\nEvaluating chapter: {filename}")
            print(f"  Word count: {word_count} English words (not tokens)")
            
            # If chapter doesn't exceed limit, skip
            if word_count <= max_words_per_chapter:
                print(f"  → No need to split ({word_count} <= {max_words_per_chapter})")
                continue
            
            # Use breakdown.md method: break at complete sentences
            print(f"  → Need to split ({word_count} > {max_words_per_chapter}), using breakdown.md method...")
            
            try:
                from .utils import split_at_sentences
                chunks = split_at_sentences(chapter_content, max_words_per_chapter)
                
                print(f"  → Split into {len(chunks)} parts (broken at complete sentences)")
                
                base_name = filename.rsplit('.', 1)[0]
                total_words = 0
                
                for i, chunk in enumerate(chunks, 1):
                    # If only one part, keep original filename; otherwise add _partXX
                    if len(chunks) == 1:
                        chunk_filename = filename
                    else:
                        chunk_filename = f"{base_name}_part{i:02d}.txt"
                    
                    chunk_path = self.chapters_dir / chunk_filename
                    write_file(chunk_path, chunk)
                    
                    chunk_word_count = count_words(chunk)
                    total_words += chunk_word_count
                    print(f"    ✓ {chunk_filename}: {chunk_word_count} English words")
                
                # Verify word count (allow 5% error)
                if abs(total_words - word_count) > word_count * 0.05:
                    print(f"  ⚠️  Warning: Total words after split ({total_words}) differs significantly from original ({word_count})")
                else:
                    print(f"  ✅ Word count verification passed: {total_words} ≈ {word_count}")
                
                # Delete original chapter file (because already split into multiple parts)
                if chapter_path.exists() and len(chunks) > 1:
                    chapter_path.unlink()
                    print(f"  ✓ Deleted original file: {filename}")
                
            except Exception as e:
                print(f"  ❌ Split failed: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
    
    def verify_chapters_completeness(self, original_text: str, chapters: List[Dict]) -> List[Dict]:
        """
        Verify chapter split completeness: Check if split chapters' word count matches original text
        
        Args:
            original_text: Original document text
            chapters: Chapter information list
        """
        print("\n" + "=" * 70)
        print("Verifying Chapter Split Completeness")
        print("=" * 70)
        
        original_word_count = count_words(original_text)
        original_char_count = len(original_text)
        
        combined_word_count = 0
        combined_char_count = 0
        
        print(f"Original text statistics:")
        print(f"  - Character count: {original_char_count:,}")
        print(f"  - Word count: {original_word_count:,}")
        
        print(f"\nSplit chapter statistics:")
        # Fix format errors in chapters
        fixed_chapters = []
        for i, chapter in enumerate(chapters):
            if not isinstance(chapter, dict):
                print(f"  ⚠️  Detected format error in chapter (index {i}), asking AI to fix...")
                fixed = self._fix_chapter_format(str(chapter), original_text, i)
                fixed_chapters.append(fixed)
                chapter = fixed
            else:
                fixed_chapters.append(chapter)
            
            filename = chapter.get('filename', '')
            chapter_path = self.chapters_dir / filename
            
            if chapter_path.exists():
                chapter_content = read_file(chapter_path)
                chapter_words = count_words(chapter_content)
                chapter_chars = len(chapter_content)
                
                combined_word_count += chapter_words
                combined_char_count += chapter_chars
                
                print(f"  - {filename}: {chapter_chars:,} characters, {chapter_words:,} words")
        
        # Update chapters list (if any chapters were fixed)
        if fixed_chapters != chapters:
            chapters[:] = fixed_chapters
        
        print(f"\nCombined statistics:")
        print(f"  - Character count: {combined_char_count:,}")
        print(f"  - Word count: {combined_word_count:,}")
        
        # Calculate differences
        char_diff = abs(original_char_count - combined_char_count)
        word_diff = abs(original_word_count - combined_word_count)
        char_diff_pct = (char_diff / original_char_count * 100) if original_char_count > 0 else 0
        word_diff_pct = (word_diff / original_word_count * 100) if original_word_count > 0 else 0
        
        print(f"\nDifferences:")
        print(f"  - Character difference: {char_diff:,} ({char_diff_pct:.2f}%)")
        print(f"  - Word difference: {word_diff:,} ({word_diff_pct:.2f}%)")
        
        if char_diff_pct < 1 and word_diff_pct < 1:
            print(f"\n✅ Verification passed: Split content basically matches original (difference < 1%)")
        elif char_diff_pct < 5 and word_diff_pct < 5:
            print(f"\n⚠️  Warning: Split content has slight difference from original (difference < 5%), may be due to format processing")
        else:
            print(f"\n❌ Error: Split content differs significantly from original (difference {char_diff_pct:.2f}% >= 5%)")
            print(f"  Asking AI to re-identify chapters...")
            
            # Let AI re-identify chapters
            retry_prompt = f"""Previous chapter identification had serious errors, split content differs from original by {char_diff_pct:.2f}%, indicating chapter boundary identification is inaccurate.

Original text statistics:
- Character count: {original_char_count:,}
- Word count: {original_word_count:,}

Split statistics:
- Character count: {combined_char_count:,}
- Word count: {combined_word_count:,}

**Problem**: Chapter boundary identification is inaccurate, causing significant content loss.

Please carefully re-analyze the document, **accurately identify all chapters' start and end line numbers**, ensuring:
1. All chapters' line numbers cover the entire document (from line 1 to last line)
2. Adjacent chapters' line numbers are continuous (previous chapter's end_line + 1 = next chapter's start_line)
3. All chapters' end_line should sum to document total lines (or close)

Document total lines: {len(original_text.split(chr(10))):,} lines

Please return chapter information in JSON format (must be accurate):"""
            
            try:
                retry_response = self.client.generate_content(
                    retry_prompt,
                    system_instruction=self.system_instruction,
                    temperature=0.3
                )
                
                json_match = re.search(r'\{.*\}', retry_response, re.DOTALL)
                if json_match:
                    retry_result = json.loads(json_match.group())
                else:
                    retry_result = json.loads(retry_response)
                
                retry_chapters = retry_result.get('chapters', [])
                if retry_chapters and len(retry_chapters) > 0:
                    print(f"  ✓ AI re-identified {len(retry_chapters)} chapters")
                    # Update chapters list
                    chapters[:] = retry_chapters
                    # Re-split chapters
                    print("  Re-splitting chapters...")
                    self.split_chapters(original_text, chapters)
                    # Verify again (recursive call, but limit depth)
                    print("  Verifying again...")
                    return self.verify_chapters_completeness(original_text, chapters)
                else:
                    print(f"  ⚠️  AI re-identification returned empty list")
                    return chapters
            except Exception as e:
                print(f"  ⚠️  AI re-identification failed: {str(e)}")
                return chapters
        
        return chapters
    
    def verify_further_breakdown_completeness(self, chapters: List[Dict]) -> None:
        """
        Verify further breakdown completeness: Check if each chapter's split parts match original chapter
        
        Args:
            chapters: Chapter information list
        """
        print("\n" + "=" * 70)
        print("Verifying Further Breakdown Completeness")
        print("=" * 70)
        
        all_chapter_files = sorted(self.chapters_dir.glob("*.txt"))
        
        # Fix format errors in chapters
        fixed_chapters = []
        for i, chapter in enumerate(chapters):
            if not isinstance(chapter, dict):
                print(f"  ⚠️  Detected format error in chapter (index {i}), asking AI to fix...")
                # Try to extract information from string or use default values
                if isinstance(chapter, str):
                    # Try to read corresponding file to infer
                    # If string looks like filename, try using it
                    if chapter.endswith('.txt'):
                        fixed = {
                            "number": f"{i:02d}",
                            "title": chapter.replace('.txt', '').replace('_', ' '),
                            "start_line": 1,
                            "end_line": 1000,
                            "filename": chapter
                        }
                    else:
                        fixed = self._fix_chapter_format(chapter, "", i)
                else:
                    fixed = {
                        "number": f"{i:02d}",
                        "title": f"Chapter {i+1}",
                        "start_line": 1,
                        "end_line": 1000,
                        "filename": f"{i:02d}_Chapter_{i+1}.txt"
                    }
                fixed_chapters.append(fixed)
                chapter = fixed
            else:
                fixed_chapters.append(chapter)
        
        # Update chapters list (if any chapters were fixed)
        if fixed_chapters != chapters:
            chapters[:] = fixed_chapters
        
        # Find which are original chapters and which are split parts
        original_chapters = {ch.get('filename', '') for ch in chapters if isinstance(ch, dict)}
        split_parts = {}  # {original_filename: [part_files]}
        
        for file in all_chapter_files:
            filename = file.name
            # Check if it's a split part (contains _part)
            if '_part' in filename:
                # Extract original chapter name
                base_name = filename.rsplit('_part', 1)[0] + '.txt'
                if base_name not in split_parts:
                    split_parts[base_name] = []
                split_parts[base_name].append(file)
        
        if not split_parts:
            print("  No split chapters to verify")
            return
        
        # Verify each split chapter
        for original_filename, part_files in split_parts.items():
            original_path = self.chapters_dir / original_filename
            if not original_path.exists():
                continue
            
            original_content = read_file(original_path)
            original_words = count_words(original_content)
            original_chars = len(original_content)
            
            combined_words = 0
            combined_chars = 0
            
            print(f"\nVerifying chapter: {original_filename}")
            print(f"  Original: {original_chars:,} characters, {original_words:,} words")
            
            for part_file in sorted(part_files):
                part_content = read_file(part_file)
                part_words = count_words(part_content)
                part_chars = len(part_content)
                
                combined_words += part_words
                combined_chars += part_chars
                
                print(f"  - {part_file.name}: {part_chars:,} characters, {part_words:,} words")
            
            print(f"  Combined: {combined_chars:,} characters, {combined_words:,} words")
            
            char_diff = abs(original_chars - combined_chars)
            word_diff = abs(original_words - combined_words)
            char_diff_pct = (char_diff / original_chars * 100) if original_chars > 0 else 0
            word_diff_pct = (word_diff / original_words * 100) if original_words > 0 else 0
            
            if char_diff_pct < 1 and word_diff_pct < 1:
                print(f"  ✅ Verification passed (difference < 1%)")
            elif char_diff_pct < 5 and word_diff_pct < 5:
                print(f"  ⚠️  Slight difference (difference < 5%)")
            else:
                print(f"  ❌ Significant difference (difference >= 5%)")
    
    def analyze_chapters(self, chapters: List[Dict]) -> None:
        """
        Phase Four: Chapter-by-chapter deep reading and analysis
        
        Args:
            chapters: Chapter information list
        """
        print("\n" + "=" * 70)
        print("Phase Four: Chapter-by-Chapter Deep Reading and Analysis")
        print("=" * 70)
        
        # Fix format errors in chapters
        fixed_chapters = []
        for i, chapter in enumerate(chapters):
            if not isinstance(chapter, dict):
                print(f"  ⚠️  Detected format error in chapter (index {i}), asking AI to fix...")
                # Try to infer from filename
                all_files = sorted(self.chapters_dir.glob("*.txt"))
                # Filter out part files
                all_files = [f for f in all_files if '_part' not in f.name]
                if i < len(all_files):
                    filename = all_files[i].name
                    fixed = {
                        "number": f"{i:02d}",
                        "title": filename.replace('.txt', '').replace('_', ' '),
                        "start_line": 1,
                        "end_line": 1000,
                        "filename": filename
                    }
                else:
                    fixed = self._fix_chapter_format(str(chapter), "", i)
                fixed_chapters.append(fixed)
                chapter = fixed
            else:
                fixed_chapters.append(chapter)
        
        # Update chapters list
        if fixed_chapters != chapters:
            chapters[:] = fixed_chapters
        
        previous_summary = None
        
        for i, chapter in enumerate(chapters):
            filename = chapter.get('filename', '')
            chapter_path = self.chapters_dir / filename
            
            # If original file doesn't exist, check if there are part files
            if not chapter_path.exists():
                # Find corresponding part files
                base_name = filename.rsplit('.', 1)[0]  # Remove .txt extension
                part_files = sorted(self.chapters_dir.glob(f"{base_name}_part*.txt"))
                
                if part_files:
                    # Generate summary for each part separately
                    print(f"\nAnalyzing chapter {i+1}/{len(chapters)}: {filename} (consists of {len(part_files)} parts, will generate summary for each part separately)")
                    
                    # Generate independent summary for each part
                    for part_idx, part_file in enumerate(part_files, 1):
                        try:
                            part_content = read_file(part_file)
                        except Exception as e:
                            print(f"    ⚠️  Failed to read part file: {part_file.name}, error: {str(e)}")
                            continue
                        
                        # Try to extract title from part content (first few lines)
                        part_lines = part_content.split('\n')[:20]
                        part_title = None
                        for line in part_lines:
                            # Find possible title (uppercase, single line, not too long)
                            stripped = line.strip()
                            if stripped and len(stripped) < 100 and not stripped.startswith(('Chapter', 'CHAPTER', 'Part')):
                                # Check if looks like title (first letter uppercase, no period)
                                if stripped[0].isupper() and '.' not in stripped and len(stripped.split()) < 15:
                                    part_title = stripped
                                    break
                        
                        if not part_title:
                            part_title = f"{chapter.get('title', base_name)} - Part {part_idx}"
                        
                        part_metadata = {
                            "number": f"{chapter.get('number', '')}_part{part_idx:02d}",
                            "title": part_title,
                            "filename": part_file.name
                        }
                        
                        print(f"  Analyzing part {part_idx}/{len(part_files)}: {part_file.name}")
                        
                        # Let AI decide how much context and content needed
                        part_length = len(part_content)
                        prev_summary_length = len(previous_summary) if previous_summary else 0
                        
                        context_strategy_prompt = get_context_strategy_prompt(part_length, prev_summary_length)
                        
                        print(f"    AI is deciding analysis strategy...")
                        context_strategy_response = self.client.generate_content(
                            context_strategy_prompt,
                            system_instruction=self.system_instruction,
                            temperature=0.3
                        )
                        
                        # Parse strategy
                        try:
                            strategy_match = re.search(r'\{.*\}', context_strategy_response, re.DOTALL)
                            if strategy_match:
                                context_strategy = json.loads(strategy_match.group())
                            else:
                                context_strategy = json.loads(context_strategy_response)
                            
                            # Decide how much previous chapter summary to use
                            prev_to_use = context_strategy.get('previous_summary_to_use', 'all')
                            if prev_to_use == 'all' or not previous_summary:
                                context = previous_summary if previous_summary else ""
                            else:
                                prev_len = int(prev_to_use) if isinstance(prev_to_use, (int, str)) and str(prev_to_use).isdigit() else len(previous_summary)
                                context = previous_summary[:prev_len] if previous_summary else ""
                            
                            # Decide how much chapter content to read
                            content_to_read = context_strategy.get('chapter_content_to_read', 'all')
                            if content_to_read == 'all':
                                analysis_content = part_content
                            else:
                                content_len = int(content_to_read) if isinstance(content_to_read, (int, str)) and str(content_to_read).isdigit() else len(part_content)
                                analysis_content = part_content[:content_len]
                        except:
                            # If AI decision fails, use all content
                            context = previous_summary if previous_summary else ""
                            analysis_content = part_content
                        
                        # Build analysis prompt
                        context_str = f"Previous chapter summary (for contextual coherence):\n{context}\n\n" if context else ""
                        prompt = get_chapter_analysis_prompt(context_str, part_metadata, analysis_content)
                        
                        print(f"    AI is analyzing...")
                        try:
                            part_summary = self.client.generate_content(
                                prompt,
                                system_instruction=self.system_instruction,
                                temperature=0.7
                            )
                            
                            # Save part summary
                            part_base_name = part_file.stem  # e.g., "02_Main_Body_part01"
                            part_summary_filename = f"{part_base_name}_summary.md"
                            part_summary_path = self.summaries_dir / part_summary_filename
                            
                            write_file(part_summary_path, part_summary)
                            print(f"    ✓ Summary saved: {part_summary_filename}")
                            
                            # Update previous chapter summary (for next part)
                            previous_summary = part_summary
                        except Exception as e:
                            print(f"    ⚠️  Failed to process part {part_idx}: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            # Continue processing next part
                            continue
                    
                    # Skip original chapter processing (because already generated summary for each part)
                    continue
                else:
                    print(f"\n⚠️  Skipping: {filename} (file doesn't exist, and no part files found)")
                    continue
            else:
                print(f"\nAnalyzing chapter {i+1}/{len(chapters)}: {filename}")
                chapter_content = read_file(chapter_path)
            
            chapter_metadata = {
                "number": chapter.get('number', ''),
                "title": chapter.get('title', ''),
                "filename": filename
            }
            
            # Let AI decide how much context and content needed
            chapter_length = len(chapter_content)
            prev_summary_length = len(previous_summary) if previous_summary else 0
            
            context_strategy_prompt = get_context_strategy_prompt(chapter_length, prev_summary_length)
            
            print(f"  AI is deciding analysis strategy...")
            context_strategy_response = self.client.generate_content(
                context_strategy_prompt,
                system_instruction=self.system_instruction,
                temperature=0.3
            )
            
            # Parse strategy
            try:
                strategy_match = re.search(r'\{.*\}', context_strategy_response, re.DOTALL)
                if strategy_match:
                    context_strategy = json.loads(strategy_match.group())
                else:
                    context_strategy = json.loads(context_strategy_response)
                
                # Decide how much previous chapter summary to use
                prev_to_use = context_strategy.get('previous_summary_to_use', 'all')
                if prev_to_use == 'all' or not previous_summary:
                    context = previous_summary if previous_summary else ""
                else:
                    prev_len = int(prev_to_use) if isinstance(prev_to_use, (int, str)) and str(prev_to_use).isdigit() else len(previous_summary)
                    context = previous_summary[:prev_len] if previous_summary else ""
                
                # Decide how much chapter content to read
                content_to_read = context_strategy.get('chapter_content_to_read', 'all')
                if content_to_read == 'all':
                    analysis_content = chapter_content
                else:
                    content_len = int(content_to_read) if isinstance(content_to_read, (int, str)) and str(content_to_read).isdigit() else len(chapter_content)
                    analysis_content = chapter_content[:content_len]
            except:
                # If AI decision fails, use all content
                context = previous_summary if previous_summary else ""
                analysis_content = chapter_content
            
            # Build analysis prompt
            context_str = f"Previous chapter summary (for contextual coherence):\n{context}\n\n" if context else ""
            prompt = get_chapter_analysis_prompt(context_str, chapter_metadata, analysis_content)
            
            print("  AI is analyzing...")
            summary = self.client.generate_content(
                prompt,
                system_instruction=self.system_instruction,
                temperature=0.7
            )
            
            # Save summary
            base_name = filename.rsplit('.', 1)[0]
            summary_filename = f"{base_name}_summary.md"
            summary_path = self.summaries_dir / summary_filename
            
            write_file(summary_path, summary)
            print(f"  ✓ Summary saved: {summary_filename}")
            
            # Update previous chapter summary (for next chapter)
            # AI has already decided how much context to use in analyze_chapters, save full summary here
            previous_summary = summary
    
    def generate_outputs(self) -> None:
        """
        Phase Five: Generate PDF and HTML outputs
        """
        print("\n" + "=" * 70)
        print("Phase Five: Format Conversion and Output")
        print("=" * 70)
        
        # Check if cover file exists (support .md and no extension)
        cover_info = None
        cover_file_md = self.summaries_dir / "00_Cover.md"
        cover_file_no_ext = self.summaries_dir / "00_Cover"
        
        if cover_file_md.exists():
            try:
                cover_content = read_file(cover_file_md)
                cover_info = self._parse_cover_file(cover_content)
                print(f"  ✓ Found cover file: {cover_file_md}")
            except Exception as e:
                print(f"  ⚠️  Failed to read cover file: {e}")
        elif cover_file_no_ext.exists():
            try:
                cover_content = read_file(cover_file_no_ext)
                cover_info = self._parse_cover_file(cover_content)
                print(f"  ✓ Found cover file: {cover_file_no_ext}")
            except Exception as e:
                print(f"  ⚠️  Failed to read cover file: {e}")
        
        # Collect all summary files (exclude cover file)
        summary_files = sorted([f for f in self.summaries_dir.glob("*.md") if f.name != "00_Cover.md"])
        
        if not summary_files:
            print("⚠️  No summary files found")
            return
        
        # Merge all Markdown files
        print("\nMerging Markdown files...")
        combined_content = ""
        
        for i, summary_file in enumerate(summary_files):
            content = read_file(summary_file)
            
            # Extract chapter title (first line's # title)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                chapter_title = title_match.group(1).strip()
            else:
                # If no title found, use filename
                chapter_title = summary_file.stem.replace('_summary', '').replace('_', ' ')
            
            # If not first chapter, add divider
            if i > 0:
                combined_content += "\n\n<div class='chapter-divider'></div>\n\n"
            
            # Ensure chapter title exists
            # If original content has no title, add one; if has title, use original content directly
            if not title_match:
                combined_content += f"# {chapter_title}\n\n"
                combined_content += content
            else:
                # If already has title, add content directly (title already in content)
                combined_content += content
            
            # Add empty lines between chapters
            combined_content += "\n\n"
        
        # Generate PDF (using new pdf_generator module)
        try:
            from .pdf_generator import generate_pdf_from_combined_content
            from datetime import datetime
            
            print("Generating PDF...")
            
            # Get book information
            # Priority: use information from cover file
            if cover_info:
                book_title = cover_info.get('title', 'Book Summary')
                book_author = cover_info.get('author', 'Unknown Author')
                gen_date = cover_info.get('date', datetime.now().strftime("%Y/%m/%d"))
                model_name = cover_info.get('model', self.client.model_name)
            else:
                # Infer from first summary file, or use generic title
                book_title = "Book Summary"
                book_author = "Unknown Author"
                
                # Try to extract author and title information from input filename (using pdf_generator function)
                try:
                    from .pdf_generator import extract_book_info_from_filename
                    if hasattr(self, 'input_file_path') and self.input_file_path:
                        extracted_title, extracted_author = extract_book_info_from_filename(self.input_file_path.name)
                        if extracted_title and extracted_title != "Book Summary":
                            book_title = extracted_title
                        if extracted_author:
                            book_author = extracted_author
                    elif hasattr(self, 'input_path'):
                        input_file = Path(self.input_path)
                        if input_file.exists():
                            extracted_title, extracted_author = extract_book_info_from_filename(input_file.name)
                            if extracted_title and extracted_title != "Book Summary":
                                book_title = extracted_title
                            if extracted_author:
                                book_author = extracted_author
                except Exception as e:
                    # If extraction fails, use old method as fallback
                    if hasattr(self, 'input_file_path') and self.input_file_path:
                        input_filename = self.input_file_path.stem
                        if ' - ' in input_filename:
                            parts = input_filename.split(' - ', 1)
                            if len(parts) == 2:
                                book_author = parts[0].strip()
                                potential_title = parts[1].strip()
                                if len(potential_title) < 100:  # Reasonable title length
                                    book_title = potential_title
                
                if summary_files:
                    first_summary = read_file(summary_files[0])
                    # Try to extract title
                    title_match = re.search(r'^#\s+(.+)$', first_summary, re.MULTILINE)
                    if title_match:
                        # If first chapter title looks like book title, use it; otherwise use generic title
                        potential_title = title_match.group(1).strip()
                        # If title too long (might be chapter name not book title), use generic title
                        if len(potential_title) < 50 and book_title == "Book Summary":
                            book_title = potential_title
                
                # Generation date
                gen_date = datetime.now().strftime("%Y/%m/%d")
                
                # Get model name
                model_name = self.client.model_name
            
            # Collect table of contents items
            toc_items = []
            for summary_file in summary_files:
                content = read_file(summary_file)
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                    # Standardize title (remove "Chapter X" format)
                    title = re.sub(r'^第[一二三四五六七八九十百千万\d]+章[：:\s]*', '', title)
                    title = re.sub(r'^第\d+章[：:\s]*', '', title)
                    title = re.sub(r'^Chapter\s+\d+[:\s]*', '', title, flags=re.IGNORECASE)
                    toc_items.append(title.strip())
            
            # Use new PDF generation module
            pdf_path = self.pdf_dir / "book_summary.pdf"
            generate_pdf_from_combined_content(
                combined_content, 
                pdf_path,
                book_title, 
                book_author,
                model_name,
                gen_date,
                toc_items,
                summaries_dir=self.summaries_dir  # Pass summaries_dir to support 00_Cover file
            )
            
            print(f"  ✓ PDF generated: {pdf_path}")
        except ImportError as e:
            print("  ⚠️  playwright not installed, skipping PDF generation")
            print("  Tip: To enable PDF generation, complete these two steps:")
            print("    1. pip install playwright")
            print("    2. playwright install chromium  ← This step is important!")
            print("  For details, see the 'Installing PDF Generation Dependencies' section in README.md")
        except RuntimeError as e:
            print(f"  ⚠️  PDF generation failed: {str(e)}")
            print("  For details, see the 'Installing PDF Generation Dependencies' section in README.md")
        except Exception as e:
            error_msg = str(e)
            print(f"  ⚠️  PDF generation failed: {error_msg}")
            import traceback
            traceback.print_exc()
        
        # Generate HTML interactive interface
        print("Generating HTML interactive interface...")
        self._generate_html_interface(summary_files)
        print(f"  ✓ HTML generated: {self.html_dir / 'interactive_reader.html'}")
    
    def _generate_pdf_html(self, content: str, book_title: str, book_author: str, model_name: str, gen_date: str, toc_items: list = None) -> str:
        """Generate PDF HTML with cover and styling (for Playwright)"""
        import markdown
        
        # Clean text (remove unwanted text)
        def clean_text(text):
            """Remove unwanted text, especially first line Expert Ghost-Reader related text"""
            lines = text.split('\n')
            
            # Check and remove first line Expert Ghost-Reader related text
            if lines:
                first_line = lines[0].strip()
                patterns = [
                    r'好的，Expert Ghost-Reader 已就位。这是对该章节的["""]高保真浓缩版["""]重写。',
                    r'好的，Expert Ghost-Reader 已就位。.*?重写。',
                    r'Expert Ghost-Reader.*?重写。',
                    r'好的，.*?Expert Ghost-Reader.*?已就位.*?重写。',
                    r'Expert Ghost-Reader.*?已就位.*?重写。',
                    r'Okay, Expert Ghost-Reader is in position.*?rewrite\.',
                ]
                
                for pattern in patterns:
                    if re.match(pattern, first_line):
                        lines = lines[1:]  # Remove first line
                        break
            
            # Recombine text
            text = '\n'.join(lines)
            
            # Remove possible remaining multiple empty lines
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text.strip()
        
        # Standardize title
        def standardize_title(title):
            """Standardize title, remove 'Chapter X' or 'Chapter X:' format"""
            title = re.sub(r'^第[一二三四五六七八九十百千万\d]+章[：:\s]*', '', title)
            title = re.sub(r'^第\d+章[：:\s]*', '', title)
            title = re.sub(r'^Chapter\s+\d+[:\s]*', '', title, flags=re.IGNORECASE)
            return title.strip()
        
        # Clean content
        content = clean_text(content)
        
        # Convert Markdown to HTML
        html_body = markdown.markdown(content, extensions=['extra', 'codehilite', 'tables'])
        
        # Process chapter separation: add chapter class to each h1 (except first)
        # Find all h1 tags first
        h1_pattern = r'<h1>(.*?)</h1>'
        h1_matches = list(re.finditer(h1_pattern, html_body))
        
        if len(h1_matches) > 1:
            # Start from second h1 to add chapter class
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
        
        # Use template to generate HTML
        return get_pdf_html_template(html_body, book_title, book_author, model_name, gen_date, toc_items)
    
    def _parse_cover_file(self, cover_content: str) -> dict:
        """Parse cover file content
        
        Format example:
        CAESAR - life of a colossus
        
        by Adrian Goldsworthy
        
        YALE UNIVERSITY PRESS
        
        Summarized by Vibe_reading (Gemini 2.5 pro)
        2026/01/26
        """
        lines = [line.strip() for line in cover_content.split('\n') if line.strip()]
        
        cover_info = {}
        
        if not lines:
            return cover_info
        
        # First line is usually book title (may contain " - " separator, like "CAESAR - life of a colossus")
        title_line = lines[0]
        # If contains " - ", usually "TITLE - subtitle" format, use whole as book title
        # Or might be "AUTHOR - TITLE", but usually first line is book title
        cover_info['title'] = title_line
        
        # Find "by" author line
        for line in lines:
            if line.lower().startswith('by '):
                cover_info['author'] = line[3:].strip()
                break
        
        # Find "Summarized by" line
        for line in lines:
            if 'summarized by' in line.lower():
                # Extract model name (might be in parentheses)
                model_match = re.search(r'\(([^)]+)\)', line)
                if model_match:
                    cover_info['model'] = model_match.group(1).strip()
                break
        
        # Find date (format: YYYY/MM/DD or YYYY-MM-DD)
        for line in lines:
            date_match = re.search(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})', line)
            if date_match:
                date_str = date_match.group(1)
                # Unified format as YYYY/MM/DD
                date_str = date_str.replace('-', '/')
                cover_info['date'] = date_str
                break
        
        return cover_info
    
    def _get_pdf_css(self) -> str:
        """Return PDF professional layout CSS"""
        return get_pdf_css()
    
    def _get_html_css(self) -> str:
        """Return professional HTML CSS styles"""
        return get_html_css()
    
    def _get_html_javascript(self, summary_files: List[Path]) -> str:
        """Return HTML JavaScript code"""
        import re
        
        # Read summary files, extract titles and content
        summaries_data = {}
        chapter_titles = {}
        chapter_originals = {}  # Store chapter original text
        
        for f in summary_files:
            key = str(f.stem)
            content = read_file(f)
            summaries_data[key] = content
            
            # Extract title (first line's # title)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                chapter_titles[key] = title_match.group(1).strip()
            else:
                # If no title found, use filename
                chapter_titles[key] = key.replace('_summary', '').replace('_', ' ')
            
            # Read corresponding chapter original text
            # Summary filename format: XX_Chapter_summary.md
            # Original text filename format: XX_Chapter.txt or XX_Chapter_part01.txt etc.
            original_key = key.replace('_summary', '')
            
            # Try to find original text file (might be single file or multiple part files)
            original_files = sorted(self.chapters_dir.glob(f"{original_key}.txt"))
            if not original_files:
                # If not found, try to find part files
                original_files = sorted(self.chapters_dir.glob(f"{original_key}_part*.txt"))
            
            if original_files:
                # Merge all part files' content
                original_content = ""
                for orig_file in original_files:
                    original_content += read_file(orig_file) + "\n\n"
                chapter_originals[key] = original_content.strip()
            else:
                # If can't find original text, use empty string
                chapter_originals[key] = ""
        
        # Get API key and model name
        api_key = self.client.api_key
        model_name = self.client.model_name
        
        return get_html_javascript_template(
            summaries_data, chapter_originals, chapter_titles, api_key, model_name
        )
    
    def _generate_html_interface(self, summary_files: List[Path]) -> None:
        """Generate HTML interactive interface (professional graphic design)"""
        html_css = self._get_html_css()
        html_javascript = self._get_html_javascript(summary_files)
        html_content = get_html_interface_template(html_css, html_javascript, len(summary_files))
        write_file(self.html_dir / "interactive_reader.html", html_content)
    
    def process(self, input_path: Path) -> None:
        """
        Process complete workflow
        
        Includes the following phases:
        1. Document preprocessing: EPUB → TXT conversion (if needed)
        2. Intelligent chapter identification: AI automatically identifies chapter structure (with progressive preview and error fixing)
        3. Chapter splitting: AI evaluates chapter length, split if necessary
        4. Chapter-by-chapter analysis: AI deep reads each chapter, generates summary (with intelligent retry mechanism)
        5. Format output: Generate Markdown, PDF (automatically generate cover), HTML
        
        Args:
            input_path: Input file path
        """
        # Save input file path for later metadata extraction
        self.input_file_path = Path(input_path)
        print("=" * 70)
        print("Vibe Reading Skill - Start Processing")
        print("=" * 70)
        
        # Phase One: Preprocessing
        document_text = self.preprocess_document(input_path)
        
        # Phase Two: Chapter identification
        chapters = self.identify_chapters(document_text)
        if not chapters or len(chapters) == 0:
            print("⚠️  Failed to identify chapters, but will continue trying to process...")
            # No longer return directly, but continue trying to process
            # If really can't identify, will handle in subsequent steps
        
        # Split chapters
        self.split_chapters(document_text, chapters)
        
        # Verify chapter split completeness (if gap too large, will re-identify and update chapters)
        chapters = self.verify_chapters_completeness(document_text, chapters)
        
        # Phase Three: Further breakdown
        # Fixed use 7000 English words
        self.further_breakdown(chapters, max_words_per_chapter=7000)
        
        # Verify further breakdown completeness
        self.verify_further_breakdown_completeness(chapters)
        
        # Phase Four: Analysis
        self.analyze_chapters(chapters)
        
        # Phase Five: Generate outputs
        self.generate_outputs()
        
        print("\n" + "=" * 70)
        print("Processing complete!")
        print(f"Input directory: {self.input_dir}")
        print(f"Chapter files: {self.chapters_dir}")
        print(f"Summary files: {self.summaries_dir}")
        print(f"PDF files: {self.pdf_dir}")
        print(f"HTML files: {self.html_dir}")
        print("=" * 70)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Vibe Reading Skill - Intelligent Reading Analysis")
    parser.add_argument("--input", "-i", type=Path, help="Input file path (EPUB or TXT), if not provided will read from input/ directory")
    parser.add_argument("--base-dir", "-d", type=Path, default=Path("."), help="Project root directory (default: current directory)")
    parser.add_argument("--api-key", type=str, help="Gemini API Key (optional, can also be set via .env file)")
    
    args = parser.parse_args()
    
    skill = VibeReadingSkill(api_key=args.api_key, base_dir=args.base_dir)
    
    # Determine input file
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file does not exist: {input_path}")
            return
    else:
        # Find file from input directory
        input_files = list(skill.input_dir.glob("*.epub")) + list(skill.input_dir.glob("*.txt"))
        if not input_files:
            print(f"Error: No EPUB or TXT files found in {skill.input_dir} directory")
            print(f"Please place file in {skill.input_dir} directory, or use --input parameter to specify file path")
            return
        input_path = input_files[0]
        print(f"Found file from input directory: {input_path}")
    
    skill.process(input_path)


if __name__ == "__main__":
    import re
    import json
    main()
