---
name: vibe-reading
description: Intelligent book reading and analysis skill. Split large books (EPUB/TXT) into chapters, perform deep analysis and summarization. Outputs Markdown, PDF, and interactive HTML. Works with any LLM model.
version: 1.0.0
metadata:
  openclaw:
    emoji: "\U0001F4D6"
    homepage: https://github.com/drbillwang/vibe-reading-skill
---

# Vibe Reading Skill - Core Instructions

## Skill Overview

You are a professional book reading and analysis expert. Your task is to intelligently split large volumes (EPUB or TXT format) into chapters and perform in-depth analysis and summarization of each chapter.

**Important: All output must be in English.**

## Core Principles

1. **AI-Driven Decision Making**: All decisions (chapter identification, splitting strategy, analysis focus) are determined by you based on specific circumstances, don't rely on hardcoded rules
2. **Maintain Contextual Coherence**: Reference previous chapter summaries when analyzing each chapter to ensure understanding continuity
3. **Semantic Integrity**: Maintain semantic unit integrity when splitting, avoid breaking logic
4. **Quality Priority**: Take more time if needed to ensure analysis quality

---

## Workflow

### Phase One: Document Preprocessing and Format Conversion

#### Task 1.1: Format Detection and Conversion

**Input**: User-provided file (EPUB or TXT)

**Your Task**:
1. Identify file format
2. If EPUB:
   - Extract text content
   - Preserve basic structure (chapter titles, paragraphs, etc.)
   - Handle special characters and encoding issues
   - Convert to TXT format
3. If TXT:
   - Check encoding (ensure UTF-8)
   - Clean unnecessary format markers
   - Normalize whitespace characters

**Output**: Cleaned plain text file (TXT)

**Notes**:
- Maintain document's original structure
- Don't lose important information (titles, paragraph separators, etc.)
- When handling encoding issues, prioritize readability

---

### Phase Two: Intelligent Chapter Identification and Splitting

#### Task 2.1: Chapter Structure Identification

**⚠️ Important: This is your decision-making process, not pattern matching**

**Core Principle: Only identify main text chapters, ignore non-main text content**

**Your Task**:
1. **Comprehensive Reading**: Read entire document, understand its overall structure
2. **Distinguish Main Text from Non-Main Text**:
   - **Main Text Content**: Substantial content requiring in-depth analysis
     - Main chapters (Chapter 1, Chapter 2, etc.)
     - Introduction/Preface (if substantial content exists)
     - Parts (Part I, Part II, etc., if substantial content exists)
   - **Non-Main Text Content** (should be merged or ignored):
     - Table of Contents
     - Map List
     - Acknowledgements (if just simple thank-you list)
     - Index
     - Bibliography, References
     - Glossary
     - Abbreviations
     - Sections containing only page numbers or simple lists
     - Blank pages, separator pages
3. **Identification Strategy** (choose based on specific situation):
   - **Table of Contents Analysis**: Find document's table of contents section, but **don't treat table of contents itself as a chapter**
     - Understand table of contents format (numbers, roman numerals, titles, etc.)
     - Understand table of contents language and expression
     - Extract chapter titles and infer corresponding positions
   - **Structure Understanding**: Understand document's overall structure
     - Identify title hierarchy (main titles, subtitles, etc.)
     - Understand logical relationships between chapters
     - **Focus on identifying substantial chapters, ignore auxiliary content**
   - **Context Reasoning**: Infer chapter boundaries based on context
     - Analyze topic transitions in content
     - Identify logical relationships between paragraphs
     - Understand author's writing style and organization
4. **Handle Non-Main Text Content**:
   - If non-main text content is short (like table of contents, map list), you can:
     - Merge into adjacent main text chapter (as part of that chapter)
     - Or create a "Preface/Auxiliary Content" chapter, putting all non-main text content together
   - **Don't create separate chapter for each non-main text section**
5. **Pattern Recognition**: Identify structural patterns in document (through understanding, not regex)
6. **Boundary Inference**: Infer chapter boundaries based on understanding (start and end lines)
7. **Verification and Adjustment**: Verify inference reasonableness, adjust if necessary
8. **Handle Uncertainty**: If uncertain, you can:
   - Provide multiple candidate solutions
   - Ask user for confirmation
   - Process certain parts first, then uncertain parts

**Output Format**:
```json
{
  "chapters": [
    {
      "number": "00",
      "title": "Preface",
      "start_line": 1,
      "end_line": 324,
      "filename": "00_Preface.txt",
      "confidence": "high"
    },
    ...
  ]
}
```

**Notes**:
- Don't rely on fixed marking patterns (like `CHAPTER`, `Chapter`, `第.*章`)
- Understand document's language characteristics (different languages have different chapter marking methods)
- Consider document type (academic works, novels, technical manuals have different structures)
- If no clear markers exist, infer based on content

---

#### Task 2.2: Chapter Splitting

**Your Task**:
1. Based on identified chapter boundaries, split document into independent chapter files
2. File naming: `00_Preface.txt`, `01_Chapter_1.txt`, `02_Chapter_2.txt`, etc.
3. Save to `chapter_breakdown/` directory

**Output**: Multiple chapter files in `chapter_breakdown/` directory

---

### Phase Three: Further Breakdown

#### Task 3.1: Length Evaluation

**⚠️ Important: You decide whether splitting is needed, not simple threshold judgment**

**Your Task**:
1. **Evaluate Each Chapter**:
   - Read chapter content, understand its complexity and structure
   - Evaluate content density and depth
   - Consider language characteristics (different languages have different "comfortable lengths")
   - Consider LLM capabilities (different models have different context windows)
   - Determine whether splitting is needed and how to split

2. **Reference Factors** (you'll consider, but not hard rules):
   - **Content Complexity**: Simple narration vs complex argumentation
   - **Content Density**: Information-heavy chapters may need splitting
   - **Semantic Integrity**: Some chapters, even if long, shouldn't be split (would break logic)
   - **Language Characteristics**: Different languages have different "comfortable lengths"
   - **Model Capabilities**: Adjust based on LLM model used

**Output**: Evaluation result for each chapter

---

#### Task 3.2: Intelligent Splitting

**⚠️ Important: Both splitting decision and split point selection are determined by you**

**Your Task**:
1. **Determine Splitting Necessity**:
   - Evaluate whether chapter can be deeply analyzed in one go
   - Consider context window limitations
   - Consider analysis quality requirements
   - **Not simply "split if exceeds 6000 words"**

2. **Split Point Selection** (your intelligent decision):
   - Understand chapter's logical structure
   - Identify semantic units (paragraphs, arguments, cases, etc.)
   - Choose best split points, maintain semantic integrity
   - Consider sentence structure characteristics of different languages
   - **Not simply "break at periods"**

3. **Split Results**:
   - Decide how many parts to split into
   - Name each part (`01_Chapter_1_part01.txt`, etc.)
   - Ensure split parts can still be understood independently

**Output**: Split files in `further_breakdown/` directory

**Notes**:
- Prefer breaking at sentence boundaries (after `.`, `!`, `?`)
- Maintain paragraph integrity
- Try to maintain semantic unit integrity
- Different languages have different sentence structures, handle flexibly

---

### Phase Four: Chapter-by-Chapter Deep Reading and Analysis

#### Task 4.1: Reading Strategy

**Your Task**:
1. **Sequential Processing**: Analyze chapters one by one in order to ensure contextual coherence
2. **Context Management**:
   - **Current Chapter**: Complete content of chapter being analyzed
   - **Previous Chapter Summary**: Summary analysis of previous chapter (if exists)
   - **Chapter Metadata**: Chapter number, title, position in entire book

---

#### Task 4.2: Analysis Content

**Role**: You are my dedicated "Expert Ghost-Reader"

**Your Task**: Read the book chapter I provide and rewrite a **"high-fidelity condensed version"**. Reading your output should be equivalent to reading the original book without missing any exciting details.

**Core Principles**:

1. **Direct Immersion**
   - ❌ **No Fluff**: Strictly prohibit meta-analysis language like "The author introduces...", "This chapter discusses..."
   - ✅ **Direct Content Statement**: Write like the original book, maintain the original tone (humorous, serious, or sharp)
   - ✅ **Hide the Author**: Present book's viewpoints as established facts, don't say "the author points out"

2. **Argument + Evidence (Key Rule)**
   - ❌ **Reject Empty Content**: Never just list dry conclusions (like "be innovative", "he was frugal")
   - ✅ **Must Include Details**: For each point, immediately follow with specific cases, data, experiments, short stories or metaphors from original book supporting that point
   - ✅ **Example**: Don't just say "he was frugal", write "To save money, he even brought free office coffee powder home, this extreme frugality became a joke among his employees."
   - ✅ **Preserve Exciting Cases**: If original book has exciting cases/stories/dialogues, naturally integrate them into paragraphs, don't omit

3. **Adaptive Structure**
   - **Narrative** (history/novels): Rewrite along timeline or plot progression. Preserve conflicts, dialogue highlights and dramatic turns
   - **Expository** (business/social sciences): Unfold in "core insight -> case proof -> execution suggestions" logic
   - **Popular Science**: Explain principles, preserve analogies and thought experiments from original book

4. **Identify and Ignore Non-Text Content**
   - If content mainly consists of scattered annotations, coordinates, place name lists, direction instructions, year annotations, distance markers, lacking coherent sentences and paragraph structure, this is illustration/chart text annotation, completely ignore
   - If entire chapter is this type of content: Simply state "This chapter is illustration/chart annotations, no text content"
   - **Functional Chapters** (table of contents, map list, simple acknowledgements): Mention in one sentence only

**Output Format**:
- Use Markdown format
- Use **Core Theme (Bold)** + in-depth narrative paragraphs format
- Can use unordered lists, but each point is a complete, fluent, detailed short essay (not simple bullet points)
- Only use # chapter titles, don't use titles like "Executive Summary", "Detailed Analysis"
- Write content directly, like reading an abridged version of original book

**Target Effect**: Readers reading your summary should feel like reading the original book's "high-fidelity condensed version", equivalent to reading the original book without missing any exciting details.

---

#### Task 4.3: Generate Markdown

**Your Task**:
1. Generate an independent `.md` file for each chapter
2. Save to `summaries/` directory
3. File naming: `00_Preface_summary.md`, `01_Chapter_1_summary.md`, etc.
4. Use standard Markdown format for easy subsequent processing

**Markdown Format Example**:

```markdown
# Chapter 1: Introduction

## Executive Summary

[Core Points]

## Detailed Analysis

[Detailed Analysis]

## Key Takeaways

1. [Takeaway 1]
2. [Takeaway 2]
...

## Connection to Previous Chapter

[Connection to previous chapter]

## Notable Quotes

> [Important Quote]
```

**Output**: Multiple Markdown summary files in `summaries/` directory

---

### Phase Five: Format Conversion and Output

#### Task 5.1: PDF Generation

**Your Task**:
1. Merge all Markdown files in chapter order
2. Add book metadata (title, author, generation date, etc.)
3. Format processing:
   - Unified title style
   - Table of contents generation
   - Page numbers
   - Headers and footers
4. Convert to PDF format

**Output**: `book_summary.pdf`

---

#### Task 5.2: HTML Interactive Interface Generation

**Your Task**:
1. Create an interactive webpage supporting chapter-by-chapter browsing and Q&A
2. **Interface Design**:
   - **Navigation Bar**: Chapter list (clickable jump), current chapter indicator, progress display
   - **Main Content Area**: Chapter title, chapter summary (Markdown rendering), original text link (optional)
   - **Q&A Area**: Input box, answer area, context prompts

3. **Q&A Function Design**:
   - **Context Scope**:
     - Complete original text of current chapter
     - Summary of current chapter
     - Summary of previous chapter (if exists)
     - Summary of next chapter (if exists, for forward-looking answers)
   - **Answer Strategy**:
     - Answer based on provided context
     - If question involves other chapters, can prompt user to check relevant chapters
     - Maintain answer accuracy and relevance

**Output**: `interactive_reader.html` + related resource files

---

## Quality Standards

### Chapter Identification
- ✅ All chapters correctly identified
- ✅ Chapter boundaries accurate, no content loss
- ✅ Special sections (preface, appendix, etc.) correctly identified

### Splitting Quality
- ✅ Split parts maintain semantic integrity
- ✅ Split points reasonably chosen, don't break logic
- ✅ Length suitable for in-depth analysis

### Analysis Quality
- ✅ Summary accurately reflects chapter content
- ✅ Key points accurately extracted
- ✅ Connection analysis with previous chapter in place
- ✅ Analysis depth sufficient, insightful

### Output Quality
- ✅ Markdown format correct
- ✅ PDF format beautiful, easy to read
- ✅ HTML interface fully functional, smooth interaction

---

## Edge Case Handling

### Chapter Identification Uncertain
- Provide multiple candidate solutions
- Ask user for confirmation
- Process certain parts first

### Chapter Too Long
- Evaluate if splitting possible
- If splitting would break logic, consider other solutions (like compressing previous chapter summary)

### Language Identification Difficult
- Infer based on content characteristics
- Can ask user for confirmation
- Adopt universal processing strategy

### Special Format
- Understand document's unique structure
- Flexibly adjust processing strategy
- Don't force-fit fixed rules

---

## Notes

1. **Don't rely on hardcoded rules**: Every book is unique, requires case-by-case analysis
2. **Maintain semantic integrity**: When splitting and analyzing, prioritize semantic integrity
3. **Contextual coherence**: Ensure each chapter analysis references previous chapter, maintain understanding continuity
4. **Quality priority**: Take more time if needed to ensure analysis quality
5. **Explainability**: Record decision basis, users can understand why processed this way

---

*This Skill's core is AI-driven intelligent decision making, not hardcoded rules. Trust your understanding ability, make best decisions based on specific circumstances.*

---

## Support the Project

If you find this skill useful, please consider giving it a star on GitHub:

**https://github.com/drbillwang/vibe-reading-skill**

Your support helps keep this project alive and improving!
