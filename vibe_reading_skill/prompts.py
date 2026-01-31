#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vibe Reading Skill - AI Prompts
Store all AI prompt templates
"""

from typing import Optional, Dict, List, Tuple


def get_chapter_identification_prompt(
    document_text: str,
    start_lines: int = 500,
    end_lines: int = 500,
    mid1_range: int = 200,
    mid2_range: int = 200
) -> str:
    """
    Get chapter identification prompt - Phase 1: Let AI analyze document format and generate scanning code
    
    Args:
        document_text: Document text
        start_lines: Number of preview lines at the beginning
        end_lines: Number of preview lines at the end
        mid1_range: Range around 25% position (single-side line count)
        mid2_range: Range around 50% position (single-side line count)
    """
    lines = document_text.split('\n')
    total_lines = len(lines)
    
    # Get multiple key parts of the document for analysis
    preview_parts = []
    
    # Beginning part
    if start_lines > 0:
        preview_parts.append((f"Beginning part (first {start_lines} lines)", '\n'.join(lines[:start_lines])))
    
    # Middle part (25% position)
    if mid1_range > 0 and total_lines > 100:
        mid_start = max(0, total_lines // 4 - mid1_range)
        mid_end = min(total_lines, total_lines // 4 + mid1_range)
        if mid_end > mid_start:
            preview_parts.append((f"Middle part (lines {mid_start}-{mid_end}, around 25% position)", '\n'.join(lines[mid_start:mid_end])))
    
    # Middle part (50% position)
    if mid2_range > 0 and total_lines > 100:
        mid2_start = max(0, total_lines // 2 - mid2_range)
        mid2_end = min(total_lines, total_lines // 2 + mid2_range)
        if mid2_end > mid2_start:
            preview_parts.append((f"Middle part (lines {mid2_start}-{mid2_end}, around 50% position)", '\n'.join(lines[mid2_start:mid2_end])))
    
    # Ending part
    if end_lines > 0:
        preview_parts.append((f"Ending part (last {end_lines} lines)", '\n'.join(lines[-end_lines:])))
    
    preview_text = "\n\n".join([f"=== {name} ===\n{content}" for name, content in preview_parts])
    
    return f"""Please carefully analyze the chapter structure of this document, then generate Python code to **scan all chapter markers**.

Document Statistics:
- Total length: {len(document_text):,} characters
- Total word count: {len(document_text.split()):,} words
- Total lines: {total_lines:,} lines

Document Key Parts (for structure analysis):
{preview_text}

**Your Task (Phase 1: Generate Scanning Code)**:

1. **Analyze document chapter format**:
   - Observe the format of chapter markers in the document (e.g., "CHAPTER 1", "Chapter One", "Part I", "Chapter X", etc.)
   - Identify common patterns of chapter titles (whether on a separate line, whether numbered, whether format is consistent, etc.)
   - Note: Different books may have different formats, need to generate code based on actual document characteristics

2. **Generate scanning code**:
   - Generate a function `scan_chapter_markers(document_text)` 
   - The function should **iterate through all lines of the entire document**, finding all possible chapter markers
   - Return a list, each element is a `(line_number, line_content)` tuple
   - Line numbers start from 1
   - Code should use regular expressions or string matching to identify chapter markers

3. **Key Requirements**:
   - Code must **iterate through all lines of the entire document**, cannot just look at the first few lines
   - Scanning should find **all possible chapter markers** (including table of contents, title pages, etc., AI will judge which are real chapters later)
   - Code should adapt to the actual format of the document (based on the format characteristics you observe)

**Return Format**:
```json
{{
    "code": "Generated Python scanning code (string)",
    "format_analysis": "Chapter format characteristics you observed",
    "reasoning": "Why design the scanning code this way"
}}
```

**Example Code Structure**:
```python
def scan_chapter_markers(document_text):
    import re
    lines = document_text.split('\\n')
    markers = []
    for i, line in enumerate(lines, 1):
        # Design matching rules based on document format
        if re.match(r'^(?:CHAPTER|Chapter|Part|Chapter.*)', line.strip(), re.I):
            markers.append((i, line.strip()))
    return markers
```

**Important**: The generated code must be able to iterate through the entire document and find all chapter markers!"""


def get_chapter_boundary_prompt(markers: List[tuple], total_lines: int) -> str:
    """Get chapter boundary determination prompt - Phase 2: Let AI determine boundaries based on scan results"""
    markers_text = "\n".join([f"- Line {line_num}: {content[:100]}" for line_num, content in markers[:50]])  # Show max 50
    if len(markers) > 50:
        markers_text += f"\n... (Total {len(markers)} markers, only showing first 50)"
    
    return f"""I scanned the entire document and found the following chapter markers:

Document total lines: {total_lines:,} lines

Chapter marker list (line number + content):
{markers_text}

**Your Task (Phase 2: Determine Chapter Boundaries)**:

1. **Judge which are real main text chapters**:
   - Identify main text chapter markers (e.g., "CHAPTER 1", "Chapter 1", etc.)
   - **Ignore** non-main text content (table of contents, map lists, acknowledgments, title pages, etc.)
   - Only keep main text chapter markers

2. **Determine boundaries for each chapter**:
   - Each chapter's `start_line` = line number where the chapter marker is located
   - Each chapter's `end_line` = **the line before the next chapter starts**, or **the last line of this chapter's content**
   - **The last chapter's `end_line` must equal the document total line count {total_lines}**
   - Adjacent chapters' line numbers must be continuous: previous chapter's `end_line + 1` = next chapter's `start_line`

3. **Key Requirements**:
   - All chapters' `start_line` and `end_line` must cover the entire document (from line 1 to line {total_lines})
   - **Absolutely cannot** make all chapters' `end_line` equal the document total line count (unless it's the last chapter)
   - Only identify main text chapters, ignore table of contents, map lists, and other non-main text content
   - If some lines are not covered by any main text chapter, these lines will be marked as "non-main text" (for word count verification)

**Return Format**:
```json
{{
    "chapters": [
        {{
            "number": "00",
            "title": "Introduction",
            "start_line": 1,
            "end_line": 324,
            "filename": "00_Introduction.txt"
        }},
        {{
            "number": "01",
            "title": "Chapter 1",
            "start_line": 325,
            "end_line": 850,
            "filename": "01_Chapter_1.txt"
        }},
        ...
    ]
}}
```

**Important**:
- Ensure all chapters' line numbers continuously cover the entire document
- The last chapter's `end_line` must equal {total_lines}
- Adjacent chapters' line numbers must be continuous (previous end_line + 1 = next start_line)"""


def get_fallback_chapter_identification_prompt(document_text: str, preview_length: int) -> str:
    """Get fallback chapter identification prompt"""
    lines = document_text.split('\n')
    total_lines = len(lines)
    
    # Get multiple key parts of the document
    preview_parts = []
    preview_parts.append(("Beginning part", '\n'.join(lines[:min(500, total_lines)])))
    if total_lines > 1000:
        mid_start = max(0, total_lines // 2 - 300)
        mid_end = min(total_lines, total_lines // 2 + 300)
        preview_parts.append((f"Middle part (lines {mid_start}-{mid_end})", '\n'.join(lines[mid_start:mid_end])))
    preview_parts.append(("Ending part", '\n'.join(lines[-min(500, total_lines):])))
    
    preview_text = "\n\n".join([f"=== {name} ===\n{content}" for name, content in preview_parts])
    
    return f"""Please carefully analyze the chapter structure of the following document. This is a historical biography, please identify all chapters.

Document Statistics:
- Total length: {len(document_text):,} characters
- Total lines: {total_lines:,} lines

Document Key Parts (for structure analysis):
{preview_text}

**Important Requirements**:
1. **Must identify all chapters**, do not return an empty list
2. **Accurately identify chapter boundaries**:
   - Search for chapter markers (e.g., "CHAPTER", "Chapter", "Part", "Chapter X", etc.)
   - Each chapter's `start_line` is the line number where the chapter title is located
   - Each chapter's `end_line` is **the line before the next chapter starts**, or **the last line of this chapter's content**
   - **Absolutely cannot** make all chapters' `end_line` equal the document total line count!
   - Adjacent chapters' `start_line` should equal the previous chapter's `end_line + 1`

3. **If the document has no clear chapter markers**:
   - Infer chapter boundaries based on content theme changes
   - At least split the document into 5-10 parts, each part approximately 1000-2000 lines
   - Each part's `end_line` must be less than the document total line count (unless it's the last part)

4. **Only identify main text chapters**, ignore table of contents, map lists, and other non-main text content

Please return chapter information in JSON format:
{{
    "chapters": [
        {{
            "number": "00",
            "title": "Introduction",
            "start_line": 1,
            "end_line": 324,
            "filename": "00_Introduction.txt"
        }},
        {{
            "number": "01",
            "title": "Chapter 1",
            "start_line": 325,
            "end_line": 850,
            "filename": "01_Chapter_1.txt"
        }},
        ...
    ]
}}

**Key**: Ensure each chapter's `end_line` is less than the document total line count (unless it's the last chapter), and adjacent chapters' line numbers are continuous!"""


def get_fix_chapter_format_prompt(raw_chapter: str, document_text: str) -> str:
    """Get fix chapter format prompt"""
    return f"""Chapter data format is abnormal, please fix to correct JSON format.

Raw Data:
{raw_chapter}

Document Context (first 10000 characters):
{document_text[:10000]}

Please return a JSON object containing the following fields:
- number: Chapter number (string)
- title: Chapter title (string)
- start_line: Starting line number (integer)
- end_line: Ending line number (integer)
- filename: Filename (string, format: XX_Title.txt)

If unable to extract from raw data, please infer from document context.

Return Format:
{{
    "number": "00",
    "title": "Introduction",
    "start_line": 1,
    "end_line": 324,
    "filename": "00_Introduction.txt"
}}"""


def get_further_breakdown_prompt(chapter: dict, chapter_content: str, chapter_length: int, 
                                  word_count: int, lines_count: int, max_words_per_chapter: int) -> str:
    """Get further breakdown prompt"""
    import json
    return f"""Please split the following chapter into smaller parts.

Chapter Information:
{json.dumps(chapter, ensure_ascii=False, indent=2)}

Chapter Statistics:
- Total length: {chapter_length} characters
- Total word count: {word_count} English words (not tokens)
- Total lines: {lines_count} lines
- Maximum word limit: {max_words_per_chapter} English words

**Important Requirements**:
1. Chapter exceeds {max_words_per_chapter} English words, must split
2. Each part should not exceed {max_words_per_chapter} English words
3. Break at complete sentences (after . ! ?)
4. Maintain paragraph integrity
5. Return complete content for each part, not indices

Complete Chapter Content:
{chapter_content}

Please return in JSON format:
{{
    "parts": [
        {{
            "part_number": 1,
            "content": "Complete content of first part (not exceeding {max_words_per_chapter} English words)",
            "filename": "01_Chapter_1_part01.txt",
            "word_count": actual word count
        }},
        ...
    ]
}}

Ensure the combined word count of all parts equals the original chapter's word count."""


def get_context_strategy_prompt(chapter_length: int, prev_summary_length: int) -> str:
    """Get context strategy decision prompt"""
    return f"""Please decide the context and content needed when analyzing this chapter.

Chapter Statistics:
- Chapter length: {chapter_length} characters
- Previous chapter summary length: {prev_summary_length} characters

Please decide:
1. How much previous chapter summary is needed as context? (can be all, partial, or none)
2. How much chapter content needs to be read for analysis? (can be all, partial, or segmented)

Return JSON:
{{
    "previous_summary_to_use": "all" or specific character count,
    "chapter_content_to_read": "all" or specific character count,
    "analysis_strategy": "your analysis strategy"
}}"""


def get_fix_chapter_line_numbers_prompt(chapter: dict, document_text: str, index: int, total_lines: int,
                                        suggested_start: Optional[int] = None) -> str:
    """Get fix chapter line numbers prompt"""
    title = chapter.get('title', f'Chapter {index+1}')
    chapter_preview = document_text[:50000]  # First 50000 characters for analysis
    
    return f"""Please help me determine the line number range for this chapter.

Chapter Information:
- Title: {title}
- Chapter number: {chapter.get('number', str(index))}
- Document total lines: {total_lines}
{f"- Suggested starting line: {suggested_start}" if suggested_start else ""}

Document Content (first 50000 characters, for chapter location):
{chapter_preview}

Please analyze the document and find the accurate starting and ending line numbers for this chapter.

**Important Requirements**:
1. Starting line number should be the line where the chapter title is located or where chapter content begins
2. Ending line number should be the line before the next chapter starts, or the last line of this chapter's content
3. If this is the last chapter, ending line number should be the last line of the document
4. Line numbers start from 1

Please return in JSON format:
{{
    "start_line": starting line number (integer),
    "end_line": ending line number (integer),
    "filename": "{chapter.get('filename', f'{index:02d}_{title}.txt')}"
}}"""


def get_chapter_analysis_prompt(context_str: str, chapter_metadata: dict, analysis_content: str) -> str:
    """Get chapter analysis prompt"""
    import json
    return f"""{context_str}You are my exclusive "Expert Ghost-Reader" (expert-level substitute reader). Your goal is to read the book chapter I provide and rewrite a **"high-fidelity condensed version"**. Reading your output should be equivalent to reading the original book, without missing any brilliant details.

**Critical Requirements**:
- **All output must be in English** (translate if original is in another language)
- **Maximum 2000 English words** (strict limit)
- **No explanatory phrases** like "Expert Ghost-Reader is ready" or "This is a high-fidelity condensed version rewrite"
- **Start directly with `# Chapter Title`** (no prefix, no chapter numbers like "Chapter Twelve")

Chapter Information:
{json.dumps(chapter_metadata, ensure_ascii=False, indent=2)}

Chapter Content:
{analysis_content}

**Core Principles**:

1. **Direct Immersion**:
   - ❌ No fluff: Prohibit meta-analysis language like "the author introduces...", "this chapter discusses..."
   - ❌ Prohibit explanatory phrases like "Expert Ghost-Reader is ready" or "This is a high-fidelity condensed version rewrite"
   - ✅ Write like the original book, maintaining its tone (humorous, serious, or sharp)
   - ✅ Hide the author: Write viewpoints as established facts, don't say "the author points out"

2. **Argument + Evidence (Key Rule)**:
   - ❌ Reject emptiness: Never just list dry conclusions (like "maintain innovation", "he is frugal")
   - ✅ Must include details: Every viewpoint must immediately follow with specific cases, data, experiments, anecdotes, or metaphors from the original book
   - ✅ Example: Don't just say "he is frugal", write "To save money, he even took the office's free coffee powder home, and this extreme frugality became a joke among his employees."
   - ✅ Preserve brilliant cases: If the original book has brilliant cases/stories/dialogues, naturally integrate them into paragraphs

3. **Adaptive Structure**:
   - **Narrative type** (history/fiction): Rewrite following timeline or plot progression. Preserve conflicts, dialogue highlights, and dramatic turns
   - **Argumentative type** (business/social science): Expand following the logic of "core insight -> case proof -> execution suggestions"
   - **Popular science type**: Explain principles and preserve analogies and thought experiments from the original book

4. **Identify and Ignore Non-text Content**:
   - If content is mainly scattered annotations, coordinates, place name lists, direction indicators, year annotations, distance annotations, etc., lacking coherent sentence and paragraph structure, this is text annotations for illustrations/charts, completely ignore
   - If the entire chapter is this type of content: directly say "This chapter contains illustration/chart annotations, no text content"
   - Functional chapters (table of contents, map lists, simple acknowledgments): Just mention in one sentence

**Output Format (Strictly Follow)**:
- **Start directly with `# Chapter Title`, no prefix, explanatory text, or phrases**
- ❌ Prohibit outputting phrases like "Expert Ghost-Reader is ready"
- ❌ Prohibit outputting chapter numbers (like "Chapter Twelve", "Chapter 12", etc.), only output the chapter title itself
- ✅ Correct example: `# Politics and War`
- ❌ Wrong example: `# Chapter Twelve Politics and War` or `Okay, Expert Ghost-Reader is ready. This is a "high-fidelity condensed version" rewrite of this chapter.\n\n# Chapter Twelve Politics and War`
- Use Markdown format
- Use **Core Theme (Bold)** + deep narrative paragraphs format
- Can use unordered lists, but each point should be a complete, fluent, detailed short essay (not simple bullet points)
- Only use # chapter title, don't use "Executive Summary", "Detailed Analysis" and other titles
- Write content directly, like reading a condensed version of the original book
"""

