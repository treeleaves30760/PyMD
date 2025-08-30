"""
PyMD Renderer - A Markdown-like language written in Python
Renders PyMD syntax to HTML with live Python code execution
"""

import re
import os
import hashlib
from typing import Dict, Any, Optional

# Import modular components
from .image_handler import ImageHandler
from .video_handler import VideoHandler
from .code_executor import CodeExecutor
from .markdown_processor import MarkdownProcessor
from .html_generator import HtmlGenerator
from .pymd_elements import PyMD

# Try to import optional dependencies with graceful fallbacks
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


class PyMDRenderer:
    """
    Main renderer class for PyMD documents
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.elements = []
        self.output_dir = output_dir or os.getcwd()
        self.last_full_content_hash = None

        # Initialize modular components
        self.image_handler = ImageHandler(self.output_dir)
        self.video_handler = VideoHandler(self.output_dir)
        self.code_executor = CodeExecutor()
        self.markdown_processor = MarkdownProcessor(self.add_element)
        self.html_generator = HtmlGenerator()

        # Initialize PyMD interface
        self.pymd = PyMD(self)
        self._custom_plt = None  # Store custom plt object for reuse

    def add_element(self, element_type: str, content: Any, html: str):
        """Add a rendered element to the document"""
        self.elements.append({
            'type': element_type,
            'content': content,
            'html': html
        })

    @property
    def variables(self):
        """Access to code executor variables"""
        return self.code_executor.variables

    @property
    def captured_images(self):
        """Access to captured images"""
        return self.image_handler.captured_images

    @property
    def captured_videos(self):
        """Access to captured videos"""
        return self.video_handler.captured_videos

    def _create_custom_plt_show(self):
        """Create a custom plt.show() function that captures and renders plots"""
        def custom_show(*_args, **_kwargs):
            if not MATPLOTLIB_AVAILABLE:
                return

            # Get current figure
            fig = plt.gcf()

            # Check if figure has any content
            if len(fig.get_axes()) > 0:
                # Save figure to file and get info
                image_info = self.image_handler.save_figure_to_file(fig)

                # Create HTML for both file-based and base64 display
                html = f'''
                <div class="image-container">
                    <img src="{image_info['relative_path']}" 
                         alt="{image_info['caption']}" 
                         style="max-width: 100%; height: auto;"
                         onerror="this.onerror=null; this.src='data:image/png;base64,{image_info['base64']}';">
                    {f'<p class="image-caption">{image_info["caption"]}</p>' if image_info["caption"] else ''}
                </div>
                '''

                # Add to elements with the image info for matching in markdown generation
                self.add_element('image', image_info, html)

                # Clear the figure to prevent memory leaks
                plt.clf()

        return custom_show

    def clear_cache(self):
        """Clear all cached results"""
        self.code_executor.clear_cache()
        self.last_full_content_hash = None

    def execute_code(self, code: str, cache_key: str = None) -> Dict[str, Any]:
        """Execute Python code and capture output with caching"""
        # Prepare custom globals with PyMD components
        custom_globals = {
            'pymd': self.pymd,
            'plt': self._get_custom_plt(),
            'pd': pd,
        }

        return self.code_executor.execute_code(code, cache_key, custom_globals)

    def _get_custom_plt(self):
        """Get custom matplotlib object with custom show method"""
        if MATPLOTLIB_AVAILABLE and plt is not None:
            if self._custom_plt is None:
                # Create custom plt object only once
                self._custom_plt = type('CustomPlt', (), {})()
                # Copy all plt attributes
                for attr in dir(plt):
                    if not attr.startswith('_'):
                        setattr(self._custom_plt, attr, getattr(plt, attr))
                # Override show method
                self._custom_plt.show = self._create_custom_plt_show()
            return self._custom_plt
        return plt

    def render_image(self, image_source=None, caption: str = '') -> str:
        """Render matplotlib plot, image file path, or other image objects"""
        try:
            # Check if image_source is a file path
            if isinstance(image_source, str):
                # Handle file path case
                html, image_info = self.image_handler.render_image_from_file(
                    image_source, caption)
                self.add_element('image', image_info, html)
                return html
            else:
                # Handle matplotlib figure case
                if image_source is None:
                    # If no specific plot object, use current figure
                    fig = plt.gcf()
                else:
                    fig = image_source

                # Save figure to file and get info
                image_info = self.image_handler.save_figure_to_file(
                    fig, caption=caption)

                # Clear the current figure to prevent memory leaks
                plt.clf()

                html = f'''
                <div class="image-container">
                    <img src="{image_info['relative_path']}" 
                         alt="{caption}" 
                         style="max-width: 100%; height: auto;"
                         onerror="this.onerror=null; this.src='data:image/png;base64,{image_info['base64']}';">
                    {f'<p class="image-caption">{caption}</p>' if caption else ''}
                </div>
                '''

                self.add_element('image', image_info, html)
                return html

        except Exception as e:
            error_html = f'<p class="error">Error rendering image: {str(e)}</p>'
            self.add_element('image', f'Error: {str(e)}', error_html)
            return error_html

    def render_video(self, video_path: str, caption: str = '', width: str = '100%',
                     height: str = 'auto', controls: bool = True, autoplay: bool = False,
                     loop: bool = False) -> str:
        """Render video from file path"""
        try:
            html, video_info = self.video_handler.render_video(
                video_path, caption, width, height, controls, autoplay, loop
            )
            self.add_element('video', video_info, html)
            return html
        except Exception as e:
            error_html = f'<p class="error">Error rendering video: {str(e)}</p>'
            self.add_element('video', f'Error: {str(e)}', error_html)
            return error_html

    def render_table(self, data) -> str:
        """Render pandas DataFrame or other tabular data"""
        try:
            if isinstance(data, pd.DataFrame):
                # Convert DataFrame to HTML
                table_html = data.to_html(
                    classes='pymd-table', table_id='data-table')
                self.add_element('table', 'DataFrame', table_html)
                return table_html
            elif isinstance(data, (list, tuple)):
                # Simple list/tuple to table
                html = '<table class="pymd-table"><tbody>'
                for row in data:
                    if isinstance(row, (list, tuple)):
                        html += '<tr>' + \
                            ''.join(
                                f'<td>{cell}</td>' for cell in row) + '</tr>'
                    else:
                        html += f'<tr><td>{row}</td></tr>'
                html += '</tbody></table>'
                self.add_element('table', 'Table', html)
                return html
            else:
                # Convert to string representation
                html = f'<pre class="data-output">{str(data)}</pre>'
                self.add_element('table', 'Data', html)
                return html

        except Exception as e:
            error_html = f'<p class="error">Error rendering table: {str(e)}</p>'
            self.add_element('table', f'Error: {str(e)}', error_html)
            return error_html

    def _get_content_hash(self, content: str) -> str:
        """Generate hash for entire content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def parse_and_render(self, pymd_content: str) -> str:
        """Parse PyMD content with ``` blocks for code and # prefixed markdown content"""
        # Check if content has changed significantly
        content_hash = self._get_content_hash(pymd_content)

        # For incremental updates, we need to detect what changed
        if self.last_full_content_hash and self.last_full_content_hash == content_hash:
            # Content hasn't changed, return cached HTML
            return self.generate_html()

        # Content changed, need to re-parse
        self.last_full_content_hash = content_hash

        # Extract code blocks for change detection (could be used for future optimizations)
        # current_code_blocks = self._extract_code_blocks(pymd_content)

        # Clear elements for fresh render
        self.elements = []

        lines = pymd_content.split('\n')
        i = 0
        code_block_index = 0

        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()

            # Skip empty lines
            if not stripped_line:
                i += 1
                continue

            # Skip import pymd lines (should exist in file but not be rendered)
            if stripped_line == 'import pymd':
                i += 1
                continue

            # Handle code blocks with ``` (only non-prefixed)
            if stripped_line == '```':
                i += 1  # Skip the opening ```
                code_lines = []

                # Collect all lines until closing ```
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()

                    # Check for closing ``` (only non-prefixed)
                    if current_stripped == '```':
                        # Found closing ```, stop collecting
                        i += 1  # Skip the closing ```
                        break

                    # Code inside ``` blocks should be used as-is
                    code_lines.append(current_line)
                    i += 1

                # Execute the collected code block with caching
                if code_lines:
                    code_block = '\n'.join(code_lines)
                    try:
                        # Create cache key for this specific code block
                        variables_snapshot = self.code_executor._get_variable_snapshot()
                        cache_key = f"exec_{code_block_index}_{self.code_executor._get_code_hash(code_block, variables_snapshot)}"

                        result = self.execute_code(code_block, cache_key)
                        if result['success']:
                            if result['output'].strip():
                                # Process print output as markdown
                                self.markdown_processor.process_print_output_as_markdown(
                                    result['output'].strip())
                        else:
                            # Display execution error
                            error_html = f'<pre class="error">Code execution error: {result["error"]}</pre>'
                            self.add_element(
                                'error', result['error'], error_html)

                        code_block_index += 1
                    except Exception as e:
                        error_html = f'<pre class="error">Code execution error: {str(e)}</pre>'
                        self.add_element('error', str(e), error_html)
                        code_block_index += 1
                continue

            # Handle display-only code blocks with ```` (only non-prefixed)
            if stripped_line == '````':
                i += 1  # Skip the opening ````
                code_lines = []

                # Collect all lines until closing ````
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()

                    # Check for closing ```` (only non-prefixed)
                    if current_stripped == '````':
                        # Found closing ````, stop collecting
                        i += 1  # Skip the closing ````
                        break

                    # Code inside ```` blocks should be used as-is
                    code_lines.append(current_line)
                    i += 1

                # Display the code block without execution (cached by content)
                if code_lines:
                    code_block = '\n'.join(code_lines)
                    cache_key = f"display_{code_block_index}_{hashlib.md5(code_block.encode()).hexdigest()}"

                    # Check if we have cached HTML for this display block
                    if cache_key in self.code_executor.code_cache:
                        cached_html = self.code_executor.code_cache[cache_key]['html']
                        self.add_element(
                            'display_code', code_block, cached_html)
                    else:
                        # Process // comments in display blocks
                        processed_code = self.markdown_processor._process_display_comments(
                            code_block)
                        display_html = f'<pre class="display-code">{processed_code}</pre>'
                        self.add_element(
                            'display_code', code_block, display_html)
                        # Cache the display HTML
                        self.code_executor.code_cache[cache_key] = {'html': display_html}

                    code_block_index += 1
                continue

            # Skip // comments (both standalone and prefixed)
            if stripped_line.startswith('//') or stripped_line.startswith('# //'):
                i += 1
                continue

            # Handle markdown content prefixed with # (Python comments)
            # Check if line starts with # followed by space or more # (markdown content)
            if stripped_line.startswith('#'):
                # Extract the markdown content (remove leading #)
                markdown_content = stripped_line[1:].strip()

                # Check if this is a code block marker inside markdown
                if markdown_content == '```':
                    # Start of code block within markdown
                    i += 1  # Skip the # ``` line
                    code_lines = []

                    # Collect code until # ``` closing marker
                    while i < len(lines):
                        current_line = lines[i]
                        current_stripped = current_line.strip()

                        # Check for closing # ```
                        if current_stripped.startswith('#') and current_stripped[1:].strip() == '```':
                            # Found closing # ```, stop collecting
                            i += 1  # Skip the closing # ```
                            break

                        # Regular code line (not prefixed with #)
                        code_lines.append(current_line)
                        i += 1

                    # Execute the collected code block
                    if code_lines:
                        code_block = '\n'.join(code_lines)
                        try:
                            # Create cache key for this specific code block
                            variables_snapshot = self.code_executor._get_variable_snapshot()
                            cache_key = f"exec_{code_block_index}_{self.code_executor._get_code_hash(code_block, variables_snapshot)}"

                            result = self.execute_code(code_block, cache_key)
                            if result['success']:
                                if result['output'].strip():
                                    # Process print output as markdown
                                    self.markdown_processor.process_print_output_as_markdown(
                                        result['output'].strip())
                            else:
                                # Display execution error
                                error_html = f'<pre class="error">Code execution error: {result["error"]}</pre>'
                                self.add_element(
                                    'error', result['error'], error_html)

                            code_block_index += 1
                        except Exception as e:
                            error_html = f'<pre class="error">Code execution error: {str(e)}</pre>'
                            self.add_element('error', str(e), error_html)
                            code_block_index += 1
                    continue

                # Check if this is a display-only code block marker
                elif markdown_content == '````':
                    # Start of display-only code block within markdown
                    i += 1  # Skip the # ```` line
                    code_lines = []

                    # Collect code until # ```` closing marker
                    while i < len(lines):
                        current_line = lines[i]
                        current_stripped = current_line.strip()

                        # Check for closing # ````
                        if current_stripped.startswith('#') and current_stripped[1:].strip() == '````':
                            # Found closing # ````, stop collecting
                            i += 1  # Skip the closing # ````
                            break

                        # Regular code line (preserve # prefixes for display)
                        code_lines.append(current_line)
                        i += 1

                    # Display the code block without execution
                    if code_lines:
                        code_block = '\n'.join(code_lines)
                        cache_key = f"display_{code_block_index}_{hashlib.md5(code_block.encode()).hexdigest()}"

                        # Check if we have cached HTML for this display block
                        if cache_key in self.code_executor.code_cache:
                            cached_html = self.code_executor.code_cache[cache_key]['html']
                            self.add_element(
                                'display_code', code_block, cached_html)
                        else:
                            # Process // comments in display blocks
                            processed_code = self.markdown_processor._process_display_comments(
                                code_block)
                            display_html = f'<pre class="display-code">{processed_code}</pre>'
                            self.add_element(
                                'display_code', code_block, display_html)
                            # Cache the display HTML
                            self.code_executor.code_cache[cache_key] = {'html': display_html}

                        code_block_index += 1
                    continue

                # Check if this is a header (## or more #s) but not escaped (# #)
                elif markdown_content.startswith('#') and not stripped_line.startswith('# # '):
                    # This is a multi-level header (##, ###, etc.)
                    level = 1  # Start with level 1 for the first #
                    header_content = markdown_content[1:]  # Remove the first #
                    while header_content.startswith('#'):
                        level += 1
                        header_content = header_content[1:]

                    if level <= 6 and header_content.strip():
                        header_text = header_content.strip()
                        processed_header = self.markdown_processor._process_bold_text(
                            header_text)
                        header_html = f'<h{level}>{processed_header}</h{level}>'
                        self.add_element(f'h{level}', header_text, header_html)
                        i += 1
                        continue

                # Check if this is a single-level header (simple case) but not escaped (# #)
                elif markdown_content and not stripped_line.startswith('# # ') and self.markdown_processor._is_header_content(markdown_content):
                    header_text = markdown_content.strip()
                    processed_header = self.markdown_processor._process_bold_text(
                        header_text)
                    header_html = f'<h1>{processed_header}</h1>'
                    self.add_element('h1', header_text, header_html)
                    i += 1
                    continue

                # Check if this is a markdown table
                elif '|' in markdown_content and markdown_content.count('|') >= 2:
                    # Collect table lines (prefixed with #)
                    table_lines = [markdown_content]
                    original_i = i
                    i += 1

                    while i < len(lines):
                        current_line = lines[i]
                        current_stripped = current_line.strip()

                        if current_stripped.startswith('#'):
                            current_content = current_stripped[1:].strip()
                            if '|' in current_content and current_content.count('|') >= 2:
                                table_lines.append(current_content)
                                i += 1
                            elif not current_content:
                                # Empty line, skip
                                i += 1
                                continue
                            else:
                                # Not a table line, stop collecting
                                break
                        else:
                            break

                    # Process table if we have valid table data
                    if len(table_lines) >= 2:
                        table_html = self.markdown_processor._process_markdown_table(
                            table_lines)
                        if table_html:
                            self.add_element('table', table_lines, table_html)
                            continue

                    # If not valid table, restore position and continue to next check
                    i = original_i

                # Check if this is a list item
                elif markdown_content.startswith('-') or re.match(r'^\d+\.\s+', markdown_content):
                    if markdown_content.startswith('-'):
                        # Handle unordered lists
                        list_items = []
                        while i < len(lines):
                            current_line = lines[i]
                            current_stripped = current_line.strip()

                            if current_stripped.startswith('#'):
                                current_content = current_stripped[1:].strip()
                                if current_content.startswith('-'):
                                    item_text = current_content[1:].strip()
                                    list_items.append(item_text)
                                    i += 1
                                else:
                                    break
                            else:
                                break

                        if list_items:
                            processed_items = [self.markdown_processor._process_bold_text(
                                item) for item in list_items]
                            ul_html = '<ul>' + \
                                ''.join(
                                    f'<li>{item}</li>' for item in processed_items) + '</ul>'
                            self.add_element('ul', list_items, ul_html)
                        continue

                    else:
                        # Handle ordered lists
                        list_items = []
                        while i < len(lines):
                            current_line = lines[i]
                            current_stripped = current_line.strip()

                            if current_stripped.startswith('#'):
                                current_content = current_stripped[1:].strip()
                                match = re.match(
                                    r'^\d+\.\s+(.*)$', current_content)
                                if match:
                                    item_text = match.group(1).strip()
                                    list_items.append(item_text)
                                    i += 1
                                else:
                                    break
                            else:
                                break

                        if list_items:
                            processed_items = [self.markdown_processor._process_bold_text(
                                item) for item in list_items]
                            ol_html = '<ol>' + \
                                ''.join(
                                    f'<li>{item}</li>' for item in processed_items) + '</ol>'
                            self.add_element('ol', list_items, ol_html)
                        continue

                # Handle regular markdown text (prefixed with #)
                if markdown_content:
                    # Special handling for escaped # (when line starts with # # with space)
                    if stripped_line.startswith('# # '):
                        # Remove the leading # to get the actual text content
                        actual_content = markdown_content[1:].strip()
                        # Check if the content should still be a header
                        if self.markdown_processor._is_header_content(actual_content):
                            processed_header = self.markdown_processor._process_bold_text(
                                actual_content)
                            header_html = f'<h1>{processed_header}</h1>'
                            self.add_element('h1', actual_content, header_html)
                        else:
                            processed_text = self.markdown_processor._process_bold_text(
                                actual_content)
                            text_html = f'<p>{processed_text}</p>'
                            self.add_element('text', actual_content, text_html)
                    else:
                        processed_text = self.markdown_processor._process_bold_text(
                            markdown_content)
                        text_html = f'<p>{processed_text}</p>'
                        self.add_element('text', markdown_content, text_html)
                i += 1
                continue

            # Handle legacy markdown syntax (headers, lists, text without # prefix)
            # This maintains backward compatibility
            # Headers without # prefix (legacy)
            if stripped_line.startswith('##'):
                level = 0
                for char in stripped_line:
                    if char == '#':
                        level += 1
                    else:
                        break

                if level > 0 and level <= 6 and stripped_line[level:].strip():
                    header_text = stripped_line[level:].strip()
                    processed_header = self.markdown_processor._process_bold_text(
                        header_text)
                    header_html = f'<h{level}>{processed_header}</h{level}>'
                    self.add_element(f'h{level}', header_text, header_html)
                    i += 1
                    continue

            # Handle markdown tables (legacy - without # prefix)
            if '|' in stripped_line and stripped_line.count('|') >= 2:
                table_lines = [stripped_line]
                original_i = i
                i += 1

                # Collect potential table lines
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()

                    if '|' in current_stripped and current_stripped.count('|') >= 2:
                        table_lines.append(current_stripped)
                        i += 1
                    elif not current_stripped:
                        # Empty line, skip
                        i += 1
                        continue
                    else:
                        break

                # Process table if we have valid table data
                if len(table_lines) >= 2:
                    table_html = self.markdown_processor._process_markdown_table(
                        table_lines)
                    if table_html:
                        self.add_element('table', table_lines, table_html)
                        continue

                # If not valid table, restore position and continue
                i = original_i

            # Handle unordered lists (legacy - without # prefix)
            if stripped_line.startswith('-') or line.startswith('\t-'):
                list_items = []
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()

                    if current_stripped.startswith('-') or current_line.startswith('\t-'):
                        # Extract list item text
                        if current_stripped.startswith('-'):
                            item_text = current_stripped[1:].strip()
                        else:  # tab-
                            item_text = current_line.lstrip('\t-').strip()
                        list_items.append(item_text)
                        i += 1
                    else:
                        break

                if list_items:
                    processed_items = [self.markdown_processor._process_bold_text(
                        item) for item in list_items]
                    ul_html = '<ul>' + \
                        ''.join(
                            f'<li>{item}</li>' for item in processed_items) + '</ul>'
                    self.add_element('ul', list_items, ul_html)
                continue

            # Handle ordered lists (legacy - without # prefix)
            if re.match(r'^\d+\.\s+', stripped_line):
                list_items = []
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()

                    match = re.match(r'^\d+\.\s+(.*)$', current_stripped)
                    if match:
                        item_text = match.group(1).strip()
                        list_items.append(item_text)
                        i += 1
                    else:
                        break

                if list_items:
                    processed_items = [self.markdown_processor._process_bold_text(
                        item) for item in list_items]
                    ol_html = '<ol>' + \
                        ''.join(
                            f'<li>{item}</li>' for item in processed_items) + '</ol>'
                    self.add_element('ol', list_items, ol_html)
                continue

            # Handle plain text (legacy - without # prefix)
            if stripped_line and not stripped_line.startswith('#'):
                processed_text = self.markdown_processor._process_bold_text(
                    stripped_line)
                text_html = f'<p>{processed_text}</p>'
                self.add_element('text', stripped_line, text_html)
            i += 1

        return self.generate_html()

    def generate_html(self) -> str:
        """Generate complete HTML document"""
        return self.html_generator.generate_html(self.elements)

    def to_markdown(self, pymd_content: str) -> str:
        """Convert PyMD content to standard Markdown"""
        return self.markdown_processor.to_markdown(pymd_content)

    def generate_markdown(self) -> str:
        """Generate markdown from rendered elements (including captured images)"""
        return self.html_generator.generate_markdown(self.elements)

    def render_file(self, file_path: str, output_path: str = None) -> str:
        """Render a PyMD file to HTML"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        html = self.parse_and_render(content)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return f"Rendered to {output_path}"

        return html


# Example usage and testing
if __name__ == "__main__":
    renderer = PyMDRenderer()

    # Example PyMD content with new format (# prefixed markdown)
    sample_content = """
// This is a comment and will be ignored

# # Welcome to PyMD
# This is a demonstration of PyMD with the new format using # prefixed markdown.
#
# ## Basic Features
#
# - Markdown content prefixed with #
# - Python code execution inside ``` blocks
# - Variables persist across code blocks  
# - Clean separation of content and code
#
# 1. First feature: Headers and lists work normally
# 2. Second feature: Code blocks are clearly separated
# 3. Third feature: Mixed content is easy to read
#
# ## Python Code Execution

# ```
x = 5
y = 10
print(f"Sum: {x + y}")
# ```

# ## Data Processing

# ```
import random
data = [random.randint(1, 100) for _ in range(5)]
print(f"Generated data: {data}")
average = sum(data) / len(data)
print(f"Average: {average:.2f}")
# ```

# ## Using PyMD Functions

# ```
print("## Generated Header")
print(f"The average from above is: **{average:.2f}**")
# ```

# Regular text works perfectly with the new format!

# ```
print("Variables persist across blocks!")
print(f"**x = {x}, y = {y}**")
# ```

# ## Video Support Example

# ```
# Demonstrate video functionality (would work with real video file)
print("### Video Rendering")
print("PyMD now supports video rendering:")
print("```python")
print("pymd.video('sample.mp4', 'Demo video', width='80%')")
print("```")
# ```
"""

    html_output = renderer.parse_and_render(sample_content)
    print("PyMD Renderer created successfully!")
    print("Sample HTML length:", len(html_output))
