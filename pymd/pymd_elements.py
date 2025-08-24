"""
PyMD element classes and utilities
"""

import re
from typing import Optional


class PyMD:
    """
    PyMD syntax handler for creating markdown-like content with Python
    """

    def __init__(self, renderer=None):
        self.renderer = renderer
        self.elements = []

    def h1(self, text: str) -> str:
        """Create a level 1 heading"""
        html = f'<h1>{text}</h1>'
        if self.renderer:
            self.renderer.add_element('h1', text, html)
        return html

    def h2(self, text: str) -> str:
        """Create a level 2 heading"""
        html = f'<h2>{text}</h2>'
        if self.renderer:
            self.renderer.add_element('h2', text, html)
        return html

    def h3(self, text: str) -> str:
        """Create a level 3 heading"""
        html = f'<h3>{text}</h3>'
        if self.renderer:
            self.renderer.add_element('h3', text, html)
        return html

    def text(self, content: str) -> str:
        """Create paragraph text with bold text support"""
        # Process bold text (**text**)
        processed_content = self._process_bold_text(content)
        html = f'<p>{processed_content}</p>'
        if self.renderer:
            self.renderer.add_element('text', content, html)
        return html

    def _process_bold_text(self, text: str) -> str:
        """Process **bold** syntax in text"""
        # Replace **text** with <strong>text</strong>
        return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

    def code(self, content: str, language: str = 'python') -> str:
        """Create code block"""
        html = f'<pre><code class="language-{language}">{content}</code></pre>'
        if self.renderer:
            self.renderer.add_element('code', content, html)
        return html

    def image(self, image_source=None, caption: str = '') -> str:
        """Render matplotlib plot, image file path, or other image objects"""
        if self.renderer:
            return self.renderer.render_image(image_source, caption)
        return f'<p>Image: {caption}</p>'

    def video(self, video_path: str, caption: str = '', width: str = '100%', 
              height: str = 'auto', controls: bool = True, autoplay: bool = False, 
              loop: bool = False) -> str:
        """Render video from file path or video data"""
        if self.renderer:
            return self.renderer.render_video(video_path, caption, width, height, 
                                            controls, autoplay, loop)
        return f'<p>Video: {caption}</p>'

    def table(self, data) -> str:
        """Render pandas DataFrame or other tabular data"""
        if self.renderer:
            return self.renderer.render_table(data)
        return '<p>Table data</p>'