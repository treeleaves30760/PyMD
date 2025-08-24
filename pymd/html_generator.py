"""
HTML generation and template utilities for PyMD renderer
"""

from typing import List, Dict, Any


class HtmlGenerator:
    """Handles HTML generation and template rendering"""
    
    def __init__(self):
        pass
    
    def generate_html(self, elements: List[Dict[str, Any]]) -> str:
        """Generate complete HTML document"""
        content = '\n'.join(element['html'] for element in elements)

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyMD Document</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
            color: #1a1a1a;
        }}
        
        h1 {{
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 10px;
        }}
        
        h2 {{
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 8px;
        }}
        
        h3 {{
            font-size: 1.25em;
        }}
        
        p {{
            margin-bottom: 16px;
            color: #1a1a1a;
        }}
        
        strong {{
            font-weight: 600;
            color: #333;
        }}
        
        pre {{
            background-color: #e8e8e8;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 14px;
            line-height: 1.45;
        }}
        
        code {{
            background-color: #e8e8e8;
            border-radius: 3px;
            padding: 2px 4px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 85%;
        }}
        
        .image-container {{
            margin: 20px 0;
            text-align: center;
        }}
        
        .image-caption {{
            font-style: italic;
            color: #666;
            margin-top: 8px;
        }}
        
        .video-container {{
            margin: 20px 0;
            text-align: center;
        }}
        
        .video-container video {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .video-caption {{
            font-style: italic;
            color: #666;
            margin-top: 8px;
        }}
        
        .pymd-table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        
        .pymd-table th,
        .pymd-table td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        
        .pymd-table th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        
        .pymd-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        .error {{
            background-color: #ffeaea;
            border: 1px solid #ff6b6b;
            border-radius: 6px;
            padding: 16px;
            color: #d63031;
            margin: 16px 0;
        }}
        
        .data-output {{
            background-color: #f0f8ff;
            border: 1px solid #b0c4de;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
        }}
        
        .code-output {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 14px;
            line-height: 1.45;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .display-code {{
            background-color: #e8e8e8;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 14px;
            line-height: 1.45;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #333;
        }}
        
        ul, ol {{
            margin: 16px 0;
            padding-left: 0;
            list-style: none;
        }}
        
        ul li, ol li {{
            margin: 8px 0;
            padding: 4px 0 4px 28px;
            line-height: 1.6;
            position: relative;
            color: #1a1a1a;
        }}
        
        ul li::before {{
            content: "•";
            color: #666;
            font-size: 16px;
            font-weight: bold;
            position: absolute;
            left: 12px;
            top: 4px;
        }}
        
        ol {{
            counter-reset: list-counter;
        }}
        
        ol li {{
            counter-increment: list-counter;
        }}
        
        ol li::before {{
            content: counter(list-counter) ".";
            color: #666;
            font-weight: 600;
            position: absolute;
            left: 8px;
            top: 4px;
            font-size: 14px;
        }}
        
        ul li:hover, ol li:hover {{
            background-color: #f8f9fa;
            border-radius: 4px;
            transition: background-color 0.2s ease;
        }}
        
        /* Nested lists */
        ul ul, ol ol, ul ol, ol ul {{
            margin: 4px 0;
            padding-left: 20px;
        }}
        
        ul ul li::before {{
            content: "◦";
            font-size: 14px;
        }}
        
        ul ul ul li::before {{
            content: "▪";
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="pymd-content">
        {content}
    </div>
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