"""
HTML generation and template utilities for PyMD renderer
"""

import os
from pathlib import Path
from typing import List, Dict, Any


class HtmlGenerator:
    """Handles HTML generation and template rendering"""

    def __init__(self):
        # Get path to static CSS file
        self.static_dir = Path(__file__).parent / "static"
        self.css_file = self.static_dir / "css" / "pymd.css"

    def _load_css(self) -> str:
        """Load CSS from external file"""
        if self.css_file.exists():
            with open(self.css_file, 'r') as f:
                return f.read()
        return ""

    def _load_js(self) -> str:
        """Load JavaScript from external file"""
        js_file = self.static_dir / "js" / "dark-mode.js"
        if js_file.exists():
            with open(js_file, 'r') as f:
                return f.read()
        return ""

    def generate_html(self, elements: List[Dict[str, Any]]) -> str:
        """Generate complete HTML document"""
        content = '\n'.join(element['html'] for element in elements)
        css_content = self._load_css()
        js_content = self._load_js()

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyMD Document</title>

    <!-- MathJax for LaTeX support -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
    </script>

    <style>
{css_content}
    </style>
</head>
<body>
    <div class="pymd-content">
        {content}
    </div>

    <!-- Dark mode toggle script -->
    <script>
{js_content}
    </script>
</body>
</html>
        """

        return html_template
    
    def generate_markdown(self, elements: List[Dict[str, Any]]) -> str:
        """Generate markdown from rendered elements (including captured images)"""
        markdown_parts = []

        for element in elements:
            element_type = element['type']
            content = element['content']

            if element_type.startswith('h'):
                # Headers
                level = int(element_type[1])
                markdown_parts.append('#' * level + ' ' + content)
                markdown_parts.append('')
            elif element_type == 'text':
                # Regular text (process bold formatting)
                text = content.replace('<strong>', '**').replace('</strong>', '**')
                markdown_parts.append(text)
                markdown_parts.append('')
            elif element_type == 'image':
                # Images - content now contains the image_info dict
                if isinstance(content, dict) and 'relative_path' in content:
                    # Use the image info directly
                    markdown_parts.append(f"![{content['caption']}]({content['relative_path']})")
                else:
                    # Fallback for legacy images or text-based images
                    markdown_parts.append(f"![{content}]({content})")
                markdown_parts.append('')
            elif element_type == 'video':
                # Videos - content contains the video_info dict
                if isinstance(content, dict) and 'relative_path' in content:
                    # For markdown, we can use HTML video tags since most markdown processors support HTML
                    markdown_parts.append(f'<video controls width="100%">')
                    markdown_parts.append(f'  <source src="{content["relative_path"]}" type="video/mp4">')
                    markdown_parts.append(f'  Your browser does not support the video tag.')
                    markdown_parts.append(f'</video>')
                    if content['caption']:
                        markdown_parts.append(f"*{content['caption']}*")
                else:
                    # Fallback
                    markdown_parts.append(f"[Video: {content}]")
                markdown_parts.append('')
            elif element_type == 'ul':
                # Unordered lists
                for item in content:
                    item_text = item.replace('<strong>', '**').replace('</strong>', '**')
                    markdown_parts.append(f"- {item_text}")
                markdown_parts.append('')
            elif element_type == 'ol':
                # Ordered lists
                for i, item in enumerate(content, 1):
                    item_text = item.replace('<strong>', '**').replace('</strong>', '**')
                    markdown_parts.append(f"{i}. {item_text}")
                markdown_parts.append('')
            elif element_type == 'table':
                # Tables - convert from rendered table lines back to markdown
                if isinstance(content, list) and len(content) > 0:
                    # If content is the original table lines, use them
                    for line in content:
                        if line.strip():
                            markdown_parts.append(line)
                    markdown_parts.append('')
                else:
                    # Fallback for other table formats
                    markdown_parts.append("| Table Data |")
                    markdown_parts.append("| --- |")
                    markdown_parts.append('')
            elif element_type == 'error':
                # Error blocks
                markdown_parts.append("```")
                markdown_parts.append(f"Error: {content}")
                markdown_parts.append("```")
                markdown_parts.append('')
            elif element_type == 'display_code':
                # Display code blocks
                markdown_parts.append("```python")
                markdown_parts.append(content)
                markdown_parts.append("```")
                markdown_parts.append('')

        return '\n'.join(markdown_parts).strip()