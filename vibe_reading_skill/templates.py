#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vibe Reading Skill - Templates
Store all HTML/CSS/JavaScript templates
"""


def get_pdf_css() -> str:
    """Return PDF professional typesetting CSS (for Playwright)"""
    return """
@page {
    size: A4;
    margin: 2.5cm 2cm 2.5cm 2.5cm;
}

@page:first {
    margin: 0;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: "PingFang SC", "Hiragino Sans GB", "STSong", "SimSun", "Microsoft YaHei", "WenQuanYi Micro Hei", "Source Han Serif SC", serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a1a;
    text-align: justify;
}

/* Cover styles */
.cover {
    page-break-after: always;
    text-align: center;
    padding: 200pt 40pt 0 40pt;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.cover-title {
    font-family: "PingFang SC", "Hiragino Sans GB", "STHeiti", "Microsoft YaHei", "Source Han Sans SC", sans-serif;
    font-size: 36pt;
    font-weight: bold;
    color: #000000;
    margin-bottom: 40pt;
    line-height: 1.4;
}

.cover-subtitle {
    font-family: "PingFang SC", "Hiragino Sans GB", "STSong", "SimSun", serif;
    font-size: 18pt;
    color: #1a1a1a;
    margin-bottom: 25pt;
    line-height: 1.6;
}

/* Table of contents styles */
.toc {
    page-break-after: always;
    padding: 20pt 0;
}

.toc-title {
    font-family: "PingFang SC", "Hiragino Sans GB", "STHeiti", "Microsoft YaHei", sans-serif;
    font-size: 28pt;
    font-weight: bold;
    text-align: center;
    margin: 40pt 0 40pt 0;
    color: #000000;
}

.toc-item {
    font-family: "PingFang SC", "Hiragino Sans GB", "STSong", "SimSun", serif;
    font-size: 13pt;
    line-height: 2;
    margin-bottom: 6pt;
    padding-left: 0;
    text-indent: 0;
}

/* Chapter titles */
h1 {
    font-family: "PingFang SC", "Hiragino Sans GB", "STHeiti", "Microsoft YaHei", "Source Han Sans SC", sans-serif;
    font-size: 26pt;
    font-weight: bold;
    color: #000000;
    margin: 40pt 0 24pt 0;
    page-break-after: avoid;
    line-height: 1.3;
    text-indent: 0;
}

h2 {
    font-family: "PingFang SC", "Hiragino Sans GB", "STHeiti", "Microsoft YaHei", sans-serif;
    font-size: 18pt;
    font-weight: bold;
    color: #000000;
    margin: 24pt 0 16pt 0;
    page-break-after: avoid;
    line-height: 1.4;
    text-indent: 0;
}

h3 {
    font-family: "PingFang SC", "Hiragino Sans GB", "STHeiti", "Microsoft YaHei", sans-serif;
    font-size: 15pt;
    font-weight: bold;
    color: #000000;
    margin: 18pt 0 12pt 0;
    page-break-after: avoid;
    line-height: 1.4;
    text-indent: 0;
}

/* Paragraph styles */
p {
    font-family: "PingFang SC", "Hiragino Sans GB", "STSong", "SimSun", "Source Han Serif SC", serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a1a;
    text-align: justify;
    text-indent: 2em;  /* First line indent 2 characters */
    margin-bottom: 8pt;
    orphans: 2;
    widows: 2;
}

/* List styles */
ul, ol {
    margin: 10pt 0 10pt 30pt;
    padding-left: 0;
}

li {
    font-family: "PingFang SC", "Hiragino Sans GB", "STSong", "SimSun", serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a1a;
    margin-bottom: 6pt;
    text-indent: 0;
}

ul ul, ol ol, ul ol, ol ul {
    margin-left: 30pt;
    margin-top: 6pt;
}

/* Blockquote styles */
blockquote {
    font-family: "PingFang SC", "Hiragino Sans GB", "STSong", "SimSun", serif;
    font-size: 10pt;
    line-height: 1.7;
    color: #1a1a1a;
    background-color: #F5F5F5;
    border-left: 4pt solid #CCCCCC;
    margin: 12pt 0;
    padding: 14pt 24pt;
    font-style: italic;
    text-indent: 0;
    border-radius: 2pt;
}

/* Code styles */
code {
    font-family: "Courier New", "Monaco", "Consolas", "Source Code Pro", monospace;
    font-size: 10pt;
    background-color: #F8F8F8;
    padding: 2pt 5pt;
    border-radius: 3pt;
    border: 1pt solid #E0E0E0;
}

pre {
    font-family: "Courier New", "Monaco", "Consolas", "Source Code Pro", monospace;
    font-size: 9.5pt;
    background-color: #F8F8F8;
    border: 1pt solid #CCCCCC;
    border-radius: 4pt;
    padding: 14pt;
    margin: 12pt 0;
    overflow-x: auto;
    text-indent: 0;
    line-height: 1.5;
}

pre code {
    background: none;
    padding: 0;
    border: none;
}

/* Emphasis styles */
strong, b {
    font-weight: bold;
    color: #000000;
}

em, i {
    font-style: italic;
}

/* Chapter separator */
.chapter {
    page-break-before: always;
}

/* Avoid page break after title */
h1, h2, h3 {
    page-break-after: avoid;
}

/* Avoid page break in middle of paragraph */
p {
    page-break-inside: avoid;
}

/* List items avoid page break */
li {
    page-break-inside: avoid;
}
"""


def get_html_css() -> str:
    """Return professional HTML CSS styles"""
    return """
        /* CSS variable definitions */
        :root {
            --primary-color: #2563eb;
            --primary-hover: #1d4ed8;
            --secondary-color: #64748b;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-tertiary: #94a3b8;
            --border-color: #e2e8f0;
            --accent-color: #10b981;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --radius-sm: 4px;
            --radius-md: 8px;
            --radius-lg: 12px;
        }
        
        /* Reset styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Roboto, sans-serif;
            line-height: 1.7;
            color: var(--text-primary);
            background: var(--bg-secondary);
            font-size: 16px;
        }
        
        /* Container layout */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 24px;
        }
        
        /* Sidebar */
        .sidebar {
            background: var(--bg-primary);
            padding: 24px;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            height: fit-content;
            position: sticky;
            top: 24px;
        }
        
        .sidebar-header {
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .sidebar h2 {
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        
        .progress-indicator {
            font-size: 12px;
            color: var(--text-tertiary);
        }
        
        .chapter-list {
            list-style: none;
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }
        
        .chapter-list::-webkit-scrollbar {
            width: 6px;
        }
        
        .chapter-list::-webkit-scrollbar-track {
            background: var(--bg-tertiary);
            border-radius: 3px;
        }
        
        .chapter-list::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 3px;
        }
        
        .chapter-list li {
            margin-bottom: 4px;
        }
        
        .chapter-list a {
            color: var(--text-secondary);
            text-decoration: none;
            display: block;
            padding: 10px 12px;
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
            font-size: 14px;
            border-left: 3px solid transparent;
        }
        
        .chapter-list a:hover {
            background: var(--bg-tertiary);
            color: var(--primary-color);
            border-left-color: var(--primary-color);
        }
        
        .chapter-list a.active {
            background: var(--primary-color);
            color: white;
            font-weight: 500;
            border-left-color: var(--primary-hover);
        }
        
        /* Main content area */
        .main-content {
            background: var(--bg-primary);
            padding: 40px;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            min-height: 600px;
        }
        
        .article-content {
            max-width: 800px;
            margin: 0 auto;
        }
        
        /* Welcome screen */
        .welcome-screen {
            text-align: center;
            padding: 60px 20px;
        }
        
        .welcome-screen h1 {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 16px;
        }
        
        .welcome-screen > p {
            font-size: 18px;
            color: var(--text-secondary);
            margin-bottom: 40px;
        }
        
        .welcome-features {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 40px;
        }
        
        .feature-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        
        .feature-icon {
            font-size: 32px;
        }
        
        /* Markdown content styles */
        .article-content h1 {
            font-size: 28px;
            font-weight: 700;
            color: var(--text-primary);
            margin-top: 32px;
            margin-bottom: 16px;
            line-height: 1.3;
        }
        
        .article-content h2 {
            font-size: 22px;
            font-weight: 600;
            color: var(--text-primary);
            margin-top: 32px;
            margin-bottom: 12px;
            line-height: 1.4;
        }
        
        .article-content h3 {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-top: 24px;
            margin-bottom: 10px;
        }
        
        .article-content p {
            margin-top: 12px;
            margin-bottom: 12px;
            line-height: 1.8;
            color: var(--text-primary);
        }
        
        .article-content ul, .article-content ol {
            margin-top: 12px;
            margin-bottom: 12px;
            padding-left: 24px;
        }
        
        .article-content li {
            margin-top: 6px;
            margin-bottom: 6px;
            line-height: 1.7;
        }
        
        .article-content blockquote {
            margin: 20px 0;
            padding: 16px 20px;
            border-left: 4px solid var(--primary-color);
            background: var(--bg-tertiary);
            border-radius: var(--radius-sm);
            font-style: italic;
            color: var(--text-secondary);
        }
        
        .article-content code {
            background: var(--bg-tertiary);
            padding: 2px 6px;
            border-radius: var(--radius-sm);
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 14px;
            color: var(--primary-color);
        }
        
        .article-content pre {
            background: #1e293b;
            color: #e2e8f0;
            padding: 16px;
            border-radius: var(--radius-md);
            overflow-x: auto;
            margin: 16px 0;
        }
        
        .article-content pre code {
            background: transparent;
            padding: 0;
            color: inherit;
        }
        
        .article-content hr {
            border: none;
            border-top: 2px solid var(--border-color);
            margin: 32px 0;
        }
        
        .article-content strong {
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .article-content em {
            font-style: italic;
        }
        
        /* Q&A area */
        .qa-section {
            margin-top: 60px;
            padding-top: 40px;
            border-top: 2px solid var(--border-color);
        }
        
        .qa-header {
            margin-bottom: 24px;
        }
        
        .qa-header h3 {
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        
        .qa-hint {
            font-size: 14px;
            color: var(--text-tertiary);
        }
        
        .qa-input-group {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .question-input {
            flex: 1;
            padding: 14px 16px;
            border: 2px solid var(--border-color);
            border-radius: var(--radius-md);
            font-size: 15px;
            font-family: inherit;
            transition: all 0.2s ease;
            background: var(--bg-primary);
        }
        
        .question-input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        .submit-btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: var(--radius-md);
            cursor: pointer;
            font-size: 15px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }
        
        .submit-btn:hover {
            background: var(--primary-hover);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .submit-btn:active {
            transform: translateY(0);
        }
        
        .btn-icon {
            font-size: 18px;
        }
        
        .answer-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 16px;
            background: var(--bg-secondary);
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
            margin-top: 24px;
            min-height: 60px;
        }
        
        .answer {
            padding: 20px;
            background: var(--bg-tertiary);
            border-radius: var(--radius-md);
            border-left: 4px solid var(--primary-color);
            animation: fadeIn 0.3s ease;
            margin-bottom: 16px;
        }
        
        .answer:last-child {
            margin-bottom: 0;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .answer p {
            margin: 0;
            line-height: 1.7;
        }
        
        .answer.loading {
            text-align: center;
            color: var(--text-tertiary);
        }
        
        .answer.error {
            border-left-color: #d32f2f;
            background: #ffebee;
        }
        
        .answer.error p {
            color: #d32f2f;
        }
        
        /* Back to top button */
        .back-to-top {
            position: fixed;
            bottom: 32px;
            right: 32px;
            width: 48px;
            height: 48px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            font-size: 20px;
            box-shadow: var(--shadow-lg);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .back-to-top:hover {
            background: var(--primary-hover);
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }
        
        /* Responsive design */
        @media (max-width: 1024px) {
            .container {
                grid-template-columns: 220px 1fr;
                gap: 20px;
                padding: 20px;
            }
            
            .main-content {
                padding: 32px;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                gap: 16px;
                padding: 16px;
            }
            
            .sidebar {
                position: static;
                max-height: 300px;
                overflow-y: auto;
            }
            
            .main-content {
                padding: 24px;
            }
            
            .welcome-features {
                flex-direction: column;
                gap: 24px;
            }
            
            .qa-input-group {
                flex-direction: column;
            }
            
            .submit-btn {
                width: 100%;
                justify-content: center;
            }
            
            .back-to-top {
                bottom: 20px;
                right: 20px;
                width: 44px;
                height: 44px;
            }
        }
        """


def get_pdf_html_template(html_body: str, book_title: str, book_author: str, model_name: str, gen_date: str, toc_items: list = None) -> str:
    """Generate PDF HTML with cover and styles (for Playwright)"""
    # Get CSS
    pdf_css = get_pdf_css()
    
    # Generate cover (refer to 00_Cover file format)
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
    
    # Generate complete HTML
    return f"""<!DOCTYPE html>
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


def get_html_interface_template(html_css: str, html_javascript: str, summary_count: int) -> str:
    """Generate HTML interactive interface template"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibe Reading - Interactive Reader</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        {html_css}
    </style>
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>📚 Chapter List</h2>
                <div class="progress-indicator" id="progressIndicator">
                    <span>0 / {summary_count}</span>
                </div>
            </div>
            <nav>
                <ul class="chapter-list" id="chapterList">
                    <!-- Chapter list will be dynamically generated by JavaScript -->
                </ul>
            </nav>
        </aside>
        
        <main class="main-content">
            <article id="chapterContent" class="article-content">
                <div class="welcome-screen">
                    <h1>Welcome to Vibe Reading</h1>
                    <p>Please select a chapter from the left to start reading.</p>
                    <div class="welcome-features">
                        <div class="feature-item">
                            <span class="feature-icon">📖</span>
                            <span>Chapter-by-chapter deep analysis</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">💬</span>
                            <span>Intelligent Q&A discussion</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-icon">🔗</span>
                            <span>Contextual coherent understanding</span>
                        </div>
                    </div>
                </div>
            </article>
            
            <section class="qa-section">
                <div class="qa-header">
                    <h3>💬 Q&A Discussion</h3>
                    <p class="qa-hint">Enter questions about this chapter, AI will answer based on context</p>
                </div>
                <div class="qa-input-group">
                    <input 
                        type="text" 
                        class="question-input" 
                        id="questionInput" 
                        placeholder="e.g., What is the core viewpoint of this chapter?"
                        onkeypress="if(event.key==='Enter') askQuestion()"
                    >
                    <button class="submit-btn" onclick="askQuestion()">
                        <span class="btn-text">Ask</span>
                        <span class="btn-icon">→</span>
                    </button>
                </div>
                <div id="answer" class="answer-container"></div>
            </section>
        </main>
    </div>
    
    <button class="back-to-top" id="backToTop" onclick="scrollToTop()" style="display: none;">
        ↑
    </button>
    
    <script>
        {html_javascript}
    </script>
</body>
</html>"""


def get_html_javascript_template(summaries_data: dict, chapter_originals: dict, chapter_titles: dict, 
                                  api_key: str, model_name: str) -> str:
    """Generate HTML JavaScript code"""
    import json
    return f"""
        const summaries = {json.dumps(summaries_data, ensure_ascii=False)};
        const chapterOriginals = {json.dumps(chapter_originals, ensure_ascii=False)};
        const chapterTitles = {json.dumps(chapter_titles, ensure_ascii=False)};
        const geminiApiKey = {json.dumps(api_key, ensure_ascii=False)};
        const geminiModel = {json.dumps(model_name, ensure_ascii=False)};
        let currentChapterIndex = 0;
        let currentChapterKey = null;
        
        // Markdown rendering function (using marked.js library)
        // If marked.js is not available, use simple implementation
        function renderMarkdown(markdown) {{
            if (typeof marked !== 'undefined') {{
                return marked.parse(markdown);
            }}
            
            // Simple implementation as fallback
            let html = markdown;
            
            // Code blocks (process first to avoid being affected by other rules)
            html = html.replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>');
            html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            // Headings
            html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
            html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
            html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
            html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
            
            // Bold and italic
            html = html.replace(/\\*\\*([^\\*]+)\\*\\*/g, '<strong>$1</strong>');
            html = html.replace(/\\*([^\\*]+)\\*/g, '<em>$1</em>');
            
            // Blockquotes
            html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');
            
            // Links
            html = html.replace(/\\[([^\\]]+)\\]\\(([^\\)]+)\\)/g, '<a href="$2">$1</a>');
            
            // Paragraphs (convert double newlines to paragraphs)
            const lines = html.split('\\n');
            let result = [];
            let currentPara = [];
            
            for (let i = 0; i < lines.length; i++) {{
                const line = lines[i].trim();
                if (!line) {{
                    if (currentPara.length > 0) {{
                        result.push('<p>' + currentPara.join(' ') + '</p>');
                        currentPara = [];
                    }}
                }} else if (line.match(/^<[h|b|p|u|o|l|d|pre]/)) {{
                    if (currentPara.length > 0) {{
                        result.push('<p>' + currentPara.join(' ') + '</p>');
                        currentPara = [];
                    }}
                    result.push(line);
                }} else {{
                    currentPara.push(line);
                }}
            }}
            if (currentPara.length > 0) {{
                result.push('<p>' + currentPara.join(' ') + '</p>');
            }}
            
            return result.join('\\n');
        }}
        
        // Generate chapter list
        const chapterList = document.getElementById('chapterList');
        Object.keys(summaries).forEach((key, index) => {{
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#';
            a.textContent = chapterTitles[key] || `Chapter ${{index + 1}}`;
            a.onclick = (e) => {{
                e.preventDefault();
                loadChapter(key, index);
            }};
            li.appendChild(a);
            chapterList.appendChild(li);
        }});
        
        function loadChapter(key, index) {{
            // Render Markdown content
            const markdown = summaries[key];
            const html = renderMarkdown(markdown);
            const contentDiv = document.getElementById('chapterContent');
            contentDiv.innerHTML = html;
            
            // Update current chapter
            currentChapterIndex = index;
            currentChapterKey = key;
            
            // Update active state
            document.querySelectorAll('.chapter-list a').forEach((a, i) => {{
                if (i === index) {{
                    a.classList.add('active');
                }} else {{
                    a.classList.remove('active');
                }}
            }});
            
            // Update progress
            updateProgress(index + 1, Object.keys(summaries).length);
            
            // Clear Q&A area
            document.getElementById('answer').innerHTML = '';
            document.getElementById('questionInput').value = '';
            
            // Scroll to top
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        function updateProgress(current, total) {{
            const indicator = document.getElementById('progressIndicator');
            indicator.textContent = `${{current}} / ${{total}}`;
        }}
        
        async function askQuestion() {{
            const question = document.getElementById('questionInput').value.trim();
            if (!question) {{
                alert('Please enter a question');
                return;
            }}
            
            if (!currentChapterKey) {{
                alert('Please select a chapter first');
                return;
            }}
            
            const answerDiv = document.getElementById('answer');
            
            // Add loading indicator (append to existing content)
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'answer loading';
            loadingDiv.innerHTML = '<p>Thinking...</p>';
            answerDiv.appendChild(loadingDiv);
            
            // Scroll to bottom
            answerDiv.scrollTop = answerDiv.scrollHeight;
            
            try {{
                // Build context: only chapter summaries (no original text to reduce context window size)
                const chapterKeys = Object.keys(summaries);
                const currentIndex = chapterKeys.indexOf(currentChapterKey);
                
                // Limit context window size to avoid 429 errors
                const MAX_SUMMARY_LENGTH = 2000; // Limit each summary to 2000 characters
                
                let context = '';
                
                // Add current chapter summary (limited)
                let currentSummary = summaries[currentChapterKey] || '';
                if (currentSummary.length > MAX_SUMMARY_LENGTH) {{
                    currentSummary = currentSummary.substring(0, MAX_SUMMARY_LENGTH) + '... [truncated]';
                }}
                context += `Current chapter summary:\\n${{currentSummary}}\\n\\n`;
                
                // Add previous chapter summary (for contextual coherence, limited)
                if (currentIndex > 0) {{
                    const prevKey = chapterKeys[currentIndex - 1];
                    let prevSummary = summaries[prevKey] || '';
                    if (prevSummary.length > MAX_SUMMARY_LENGTH) {{
                        prevSummary = prevSummary.substring(0, MAX_SUMMARY_LENGTH) + '... [truncated]';
                    }}
                    context += `Previous chapter summary (for context):\\n${{prevSummary}}\\n\\n`;
                }}
                
                // Add next chapter summary (for contextual coherence, limited)
                if (currentIndex < chapterKeys.length - 1) {{
                    const nextKey = chapterKeys[currentIndex + 1];
                    let nextSummary = summaries[nextKey] || '';
                    if (nextSummary.length > MAX_SUMMARY_LENGTH) {{
                        nextSummary = nextSummary.substring(0, MAX_SUMMARY_LENGTH) + '... [truncated]';
                    }}
                    context += `Next chapter summary (for context):\\n${{nextSummary}}\\n\\n`;
                }}
                
                // Build prompt
                const prompt = `${{context}}User question: ${{question}}\\n\\nPlease answer the user's question based on the above chapter summaries. Answer should be accurate and detailed. Answer directly, don't repeat the question itself. Answer in English.`;
                
                // Call Gemini API
                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${{geminiModel}}:generateContent?key=${{geminiApiKey}}`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        contents: [{{
                            parts: [{{
                                text: prompt
                            }}]
                        }}]
                    }})
                }});
                
                if (!response.ok) {{
                    throw new Error(`API request failed: ${{response.status}} ${{response.statusText}}`);
                }}
                
                const data = await response.json();
                
                if (data.error) {{
                    throw new Error(data.error.message || 'API returned error');
                }}
                
                const answer = data.candidates[0].content.parts[0].text;
                
                // Remove loading indicator
                loadingDiv.remove();
                
                // Render answer (supports Markdown)
                const answerHtml = renderMarkdown(answer);
                
                // Append new Q&A (don't overwrite previous)
                const newQADiv = document.createElement('div');
                newQADiv.className = 'answer';
                newQADiv.innerHTML = `
                    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 12px;">
                        <p style="margin: 0; color: #64748b; font-size: 14px;"><strong>Question:</strong> ${{question}}</p>
                    </div>
                    <div style="margin-top: 12px;">
                        <p style="margin: 0 0 8px 0; color: #64748b; font-size: 14px;"><strong>Answer:</strong></p>
                        <div style="margin-top: 8px;">${{answerHtml}}</div>
                    </div>
                `;
                answerDiv.appendChild(newQADiv);
                
                // Scroll to bottom
                answerDiv.scrollTop = answerDiv.scrollHeight;
                
            }} catch (error) {{
                console.error('Q&A error:', error);
                
                // Remove loading indicator
                loadingDiv.remove();
                
                // Append error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'answer error';
                errorDiv.innerHTML = `
                    <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 12px;">
                        <p style="margin: 0; color: #64748b; font-size: 14px;"><strong>Question:</strong> ${{question}}</p>
                    </div>
                    <p style="margin-top: 12px; color: #d32f2f;"><strong>Error:</strong> ${{error.message}}</p>
                    <p style="margin-top: 8px; color: #666;">Please check if API Key is correctly configured, or check browser console for more information.</p>
                `;
                answerDiv.appendChild(errorDiv);
                
                // Scroll to bottom
                answerDiv.scrollTop = answerDiv.scrollHeight;
            }}
            
            // Clear input box (but keep Q&A history)
            document.getElementById('questionInput').value = '';
        }}
        
        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        // Show/hide back to top button
        window.addEventListener('scroll', () => {{
            const backToTop = document.getElementById('backToTop');
            if (window.scrollY > 300) {{
                backToTop.style.display = 'block';
            }} else {{
                backToTop.style.display = 'none';
            }}
        }});
        
        // Initialize: load first chapter
        if (Object.keys(summaries).length > 0) {{
            const firstKey = Object.keys(summaries)[0];
            loadChapter(firstKey, 0);
        }}
        """
