"""
PyMD Renderer - A Markdown-like language written in Python
Renders PyMD syntax to HTML with live Python code execution
"""

import re
import io
import base64
import sys
import traceback
import hashlib
import os
import uuid
from typing import Dict, Any, Optional
from contextlib import redirect_stdout, redirect_stderr

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

    def video(self, video_path: str, caption: str = '', width: str = '100%', height: str = 'auto', controls: bool = True, autoplay: bool = False, loop: bool = False) -> str:
        """Render video from file path or video data"""
        if self.renderer:
            return self.renderer.render_video(video_path, caption, width, height, controls, autoplay, loop)
        return f'<p>Video: {caption}</p>'

    def table(self, data) -> str:
        """Render pandas DataFrame or other tabular data"""
        if self.renderer:
            return self.renderer.render_table(data)
        return '<p>Table data</p>'


class PyMDRenderer:
    """
    Main renderer class for PyMD documents
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.elements = []
        self.variables = {}
        self.pymd = PyMD(self)
        # Cache for code execution results
        self.code_cache = {}
        self.variable_snapshots = {}
        self.last_full_content_hash = None
        self.max_cache_size = 100  # Maximum number of cached results
        
        # Image handling
        self.output_dir = output_dir or os.getcwd()
        self.images_dir = os.path.join(self.output_dir, 'images')
        self.image_counter = 0
        self.captured_images = []  # Store info about captured images
        self._custom_plt = None  # Store custom plt object for reuse
        
        # Video handling
        self.videos_dir = os.path.join(self.output_dir, 'videos')
        self.video_counter = 0
        self.captured_videos = []  # Store info about captured videos

    def add_element(self, element_type: str, content: Any, html: str):
        """Add a rendered element to the document"""
        self.elements.append({
            'type': element_type,
            'content': content,
            'html': html
        })

    def _ensure_images_dir(self):
        """Ensure the images directory exists"""
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir, exist_ok=True)
    
    def _ensure_videos_dir(self):
        """Ensure the videos directory exists"""
        if not os.path.exists(self.videos_dir):
            os.makedirs(self.videos_dir, exist_ok=True)

    def _save_figure_to_file(self, fig, filename: str = None, caption: str = '') -> Dict[str, str]:
        """Save matplotlib figure to file and return image info"""
        self._ensure_images_dir()
        
        if filename is None:
            self.image_counter += 1
            filename = f"plot_{self.image_counter}_{uuid.uuid4().hex[:8]}.png"
        
        file_path = os.path.join(self.images_dir, filename)
        relative_path = f"images/{filename}"
        
        # Save figure to file
        fig.savefig(file_path, format='png', bbox_inches='tight', dpi=150)
        
        # Also create base64 for fallback
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        image_info = {
            'filename': filename,
            'file_path': file_path,
            'relative_path': relative_path,
            'base64': img_base64,
            'caption': caption
        }
        
        self.captured_images.append(image_info)
        return image_info

    def _render_image_from_file(self, image_path: str, caption: str = '') -> str:
        """Render image from file path"""
        try:
            # Check if image file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Copy image to images directory and get info
            image_info = self._save_image_file_to_images_dir(image_path, caption=caption)
            
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

    def _save_image_file_to_images_dir(self, image_path: str, filename: str = None, caption: str = '') -> Dict[str, str]:
        """Copy image file to images directory and return image info"""
        import shutil
        
        self._ensure_images_dir()
        
        if filename is None:
            # Try to preserve the original filename from the image_path
            original_filename = os.path.basename(image_path)
            if original_filename and not original_filename.startswith('.'):
                # Use the original filename if it's valid
                filename = original_filename
                # Check if filename already exists and make it unique if necessary
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(self.images_dir, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
            else:
                # Fall back to generating a unique filename
                self.image_counter += 1
                _, ext = os.path.splitext(image_path)
                if not ext:
                    ext = '.png'  # default extension
                filename = f"image_{self.image_counter}_{uuid.uuid4().hex[:8]}{ext}"
        
        file_path = os.path.join(self.images_dir, filename)
        relative_path = f"images/{filename}"
        
        try:
            # Copy image file to images directory
            shutil.copy2(image_path, file_path)
        except Exception as e:
            raise Exception(f"Failed to copy image file: {str(e)}")
        
        # Also create base64 for fallback
        try:
            import base64
            with open(file_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
        except Exception:
            img_base64 = ''  # If base64 encoding fails, use empty string
        
        image_info = {
            'filename': filename,
            'file_path': file_path,
            'relative_path': relative_path,
            'original_path': image_path,
            'base64': img_base64,
            'caption': caption
        }
        
        self.captured_images.append(image_info)
        return image_info

    def _create_custom_plt_show(self):
        """Create a custom plt.show() function that captures and renders plots"""
        def custom_show(*args, **kwargs):
            if not MATPLOTLIB_AVAILABLE:
                return
            
            # Get current figure
            fig = plt.gcf()
            
            # Check if figure has any content
            if len(fig.get_axes()) > 0:
                # Save figure to file and get info
                image_info = self._save_figure_to_file(fig)
                
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

    def _parse_input_mocks(self, code: str) -> Dict[str, str]:
        """Parse input mock values from comments in the format: # input: value"""
        input_mocks = {}
        lines = code.split('\n')

        for line in lines:
            # Look for input() calls with mock values in comments
            if 'input(' in line and '# input:' in line:
                # Extract the mock value after "# input:"
                comment_part = line.split('# input:')[1].strip()
                # Find the input() call to get a unique identifier
                # For simplicity, we'll use line position, but this could be improved
                input_mocks[len(input_mocks)] = comment_part
            elif 'input(' in line and '# input:' not in line:
                input_mocks[len(input_mocks)] = ''

        return input_mocks

    def _create_mock_input(self, input_mocks: Dict[str, str]):
        """Create a mock input function that returns predefined values"""
        mock_values = list(input_mocks.values())
        call_count = [0]  # Use list to make it mutable in closure

        def mock_input(prompt=''):
            value = mock_values[call_count[0]]
            call_count[0] += 1
            # Don't print anything - just return the mock value silently
            return value

        return mock_input

    def _get_code_hash(self, code: str, variables_snapshot: Dict[str, Any]) -> str:
        """Generate a hash for code block and variable state"""
        # Create a combined hash of code content and relevant variables
        content = code + str(sorted(variables_snapshot.items()))
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _get_variable_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current variables for caching"""
        # Only include serializable variables for hashing
        snapshot = {}
        for key, value in self.variables.items():
            try:
                # Try to serialize the value to check if it's cacheable
                str(value)
                snapshot[key] = value
            except:
                # Skip non-serializable values
                pass
        return snapshot

    def clear_cache(self):
        """Clear all cached results"""
        self.code_cache.clear()
        self.last_full_content_hash = None

    def _manage_cache_size(self):
        """Remove oldest cache entries if cache is too large"""
        if len(self.code_cache) > self.max_cache_size:
            # Remove oldest half of cache entries
            items_to_remove = len(self.code_cache) - (self.max_cache_size // 2)
            keys_to_remove = list(self.code_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self.code_cache[key]

    def execute_code(self, code: str, cache_key: str = None) -> Dict[str, Any]:
        """Execute Python code and capture output with caching"""
        # Generate cache key if not provided
        if cache_key is None:
            variables_snapshot = self._get_variable_snapshot()
            cache_key = self._get_code_hash(code, variables_snapshot)
        
        # Check cache first
        if cache_key in self.code_cache:
            cached_result = self.code_cache[cache_key]
            # Restore variables from cache
            self.variables.update(cached_result['variables'])
            return cached_result.copy()
        
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        result = {
            'success': True,
            'output': '',
            'error': '',
            'variables': {},
            'cache_key': cache_key
        }

        try:
            # Ensure output directories exist before code execution
            # This allows users to save files directly to these directories
            self._ensure_images_dir()
            self._ensure_videos_dir()
            
            # Parse input mock values
            input_mocks = self._parse_input_mocks(code)

            # Create execution environment with pymd available
            exec_globals = {
                '__builtins__': __builtins__,
                'pymd': self.pymd,
                'plt': plt,
                'pd': pd,
                **self.variables
            }
            
            # Override plt.show with our custom function if matplotlib is available
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
                exec_globals['plt'] = self._custom_plt

            # Override input function if there are input() calls in the code
            if 'input(' in code:
                if input_mocks:
                    exec_globals['input'] = self._create_mock_input(
                        input_mocks)
                else:
                    # Check if there are any input() calls without mock values
                    lines = code.split('\n')
                    input_line_found = False
                    for line in lines:
                        if 'input(' in line and '# input:' not in line:
                            input_line_found = True
                            break

                    if input_line_found:
                        raise RuntimeError("input() function found without mock value. "
                                           "Please add '# input: <value>' comment after each input() call.")

            # Redirect output
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute the code
            exec(code, exec_globals)

            # Update variables but preserve the custom_plt reference for consistent image counter
            updated_vars = {k: v for k, v in exec_globals.items()
                          if not k.startswith('__') and k not in ['pymd', 'pd', 'input']}
            # Don't update 'plt' to preserve our custom wrapper
            if 'plt' in updated_vars:
                del updated_vars['plt']
            self.variables.update(updated_vars)

            result['output'] = stdout_capture.getvalue()
            result['variables'] = self.variables.copy()
            
            # Cache the successful result
            self.code_cache[cache_key] = result.copy()
            self._manage_cache_size()

        except Exception as e:
            result['success'] = False
            result['error'] = traceback.format_exc()
            result['output'] = stdout_capture.getvalue()
            result['variables'] = self.variables.copy()
            
            # Cache the error result too to avoid re-executing failing code
            self.code_cache[cache_key] = result.copy()
            self._manage_cache_size()

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return result

    def render_image(self, image_source=None, caption: str = '') -> str:
        """Render matplotlib plot, image file path, or other image objects"""
        try:
            # Check if image_source is a file path
            if isinstance(image_source, str):
                # Handle file path case
                return self._render_image_from_file(image_source, caption)
            else:
                # Handle matplotlib figure case
                if image_source is None:
                    # If no specific plot object, use current figure
                    fig = plt.gcf()
                else:
                    fig = image_source

                # Save figure to file and get info
                image_info = self._save_figure_to_file(fig, caption=caption)

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

    def _save_video_to_file(self, video_path: str, filename: str = None, caption: str = '') -> Dict[str, str]:
        """Copy video file to videos directory and return video info"""
        import shutil
        
        self._ensure_videos_dir()
        
        # Check if the video_path is already in the videos directory
        abs_video_path = os.path.abspath(video_path)
        abs_videos_dir = os.path.abspath(self.videos_dir)
        
        if abs_video_path.startswith(abs_videos_dir + os.sep):
            # Video is already in the videos directory, no need to copy
            filename = os.path.basename(video_path)
            file_path = abs_video_path
            relative_path = f"videos/{filename}"
            
            video_info = {
                'filename': filename,
                'file_path': file_path,
                'relative_path': relative_path,
                'original_path': video_path,
                'caption': caption
            }
            
            self.captured_videos.append(video_info)
            return video_info
        
        if filename is None:
            # Try to preserve the original filename from the video_path
            original_filename = os.path.basename(video_path)
            if original_filename and not original_filename.startswith('.'):
                # Use the original filename if it's valid
                filename = original_filename
                # Check if filename already exists and make it unique if necessary
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(self.videos_dir, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
            else:
                # Fall back to generating a unique filename
                self.video_counter += 1
                # Get original file extension
                _, ext = os.path.splitext(video_path)
                if not ext:
                    ext = '.mp4'  # default extension
                filename = f"video_{self.video_counter}_{uuid.uuid4().hex[:8]}{ext}"
        
        file_path = os.path.join(self.videos_dir, filename)
        relative_path = f"videos/{filename}"
        
        try:
            # Copy video file to videos directory
            shutil.copy2(video_path, file_path)
        except Exception as e:
            raise Exception(f"Failed to copy video file: {str(e)}")
        
        video_info = {
            'filename': filename,
            'file_path': file_path,
            'relative_path': relative_path,
            'original_path': video_path,
            'caption': caption
        }
        
        self.captured_videos.append(video_info)
        return video_info

    def render_video(self, video_path: str, caption: str = '', width: str = '100%', height: str = 'auto', controls: bool = True, autoplay: bool = False, loop: bool = False) -> str:
        """Render video from file path"""
        try:
            # Check if video file exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Save video to videos directory and get info
            video_info = self._save_video_to_file(video_path, caption=caption)
            
            # Build video attributes
            video_attrs = []
            if controls:
                video_attrs.append('controls')
            if autoplay:
                video_attrs.append('autoplay')
            if loop:
                video_attrs.append('loop')
            
            attrs_str = ' '.join(video_attrs)
            if attrs_str:
                attrs_str = ' ' + attrs_str
            
            # Determine the correct MIME type based on file extension
            _, ext = os.path.splitext(video_info['filename'])
            ext = ext.lower()
            
            if ext == '.gif':
                # For GIF files, use an img tag instead of video tag since browsers handle animated GIFs as images
                html = f'''
                <div class="video-container">
                    <img src="{video_info['relative_path']}" 
                         alt="{caption}" 
                         width="{width}" 
                         style="height: {height}; max-width: 100%; border-radius: 6px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
                    {f'<p class="video-caption">{caption}</p>' if caption else ''}
                </div>
                '''
            else:
                # For actual video files, determine the correct MIME type
                mime_type = 'video/mp4'  # default
                if ext == '.webm':
                    mime_type = 'video/webm'
                elif ext == '.ogg':
                    mime_type = 'video/ogg'
                elif ext == '.mov':
                    mime_type = 'video/quicktime'
                elif ext == '.avi':
                    mime_type = 'video/x-msvideo'
                
                html = f'''
                <div class="video-container">
                    <video width="{width}" height="{height}"{attrs_str}>
                        <source src="{video_info['relative_path']}" type="{mime_type}">
                        Your browser does not support the video tag.
                    </video>
                    {f'<p class="video-caption">{caption}</p>' if caption else ''}
                </div>
                '''
            
            self.add_element('video', video_info, html)
            return html

        except Exception as e:
            error_html = f'<p class="error">Error rendering video: {str(e)}</p>'
            self.add_element('video', f'Error: {str(e)}', error_html)
            return error_html

    def _process_bold_text_in_content(self, text: str) -> str:
        """Process **bold** syntax in content text"""
        # Replace **text** with <strong>text</strong>
        return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    def _process_markdown_table(self, table_lines: list) -> str:
        """Process markdown table syntax into HTML"""
        if len(table_lines) < 2:
            return None
        
        # Parse header row
        header_line = table_lines[0].strip()
        if not header_line.startswith('|') or not header_line.endswith('|'):
            # Try to handle tables without outer pipes
            header_cells = [cell.strip() for cell in header_line.split('|')]
        else:
            # Remove outer pipes and split
            header_cells = [cell.strip() for cell in header_line[1:-1].split('|')]
        
        # Check if second line is separator (like |---|---|)
        separator_line = table_lines[1].strip()
        is_separator = re.match(r'^\|?[\s\-\|:]+\|?$', separator_line)
        
        # Extract alignment info from separator if it exists
        alignments = []
        if is_separator:
            if not separator_line.startswith('|') or not separator_line.endswith('|'):
                sep_cells = separator_line.split('|')
            else:
                sep_cells = separator_line[1:-1].split('|')
            
            for cell in sep_cells:
                cell = cell.strip()
                if cell.startswith(':') and cell.endswith(':'):
                    alignments.append('center')
                elif cell.endswith(':'):
                    alignments.append('right')
                else:
                    alignments.append('left')
            
            # Data rows start from index 2
            data_start = 2
        else:
            # No separator, all data including second row
            alignments = ['left'] * len(header_cells)
            data_start = 1
        
        # Build HTML table
        html = '<table class="pymd-table">\n'
        
        # Header
        html += '  <thead>\n    <tr>\n'
        for i, header in enumerate(header_cells):
            align = alignments[i] if i < len(alignments) else 'left'
            style = f' style="text-align: {align}"' if align != 'left' else ''
            processed_header = self._process_bold_text_in_content(header)
            html += f'      <th{style}>{processed_header}</th>\n'
        html += '    </tr>\n  </thead>\n'
        
        # Body
        if data_start < len(table_lines):
            html += '  <tbody>\n'
            for row_line in table_lines[data_start:]:
                row_line = row_line.strip()
                if not row_line:
                    continue
                
                # Parse data row
                if not row_line.startswith('|') or not row_line.endswith('|'):
                    data_cells = [cell.strip() for cell in row_line.split('|')]
                else:
                    data_cells = [cell.strip() for cell in row_line[1:-1].split('|')]
                
                html += '    <tr>\n'
                for i, cell in enumerate(data_cells):
                    align = alignments[i] if i < len(alignments) else 'left'
                    style = f' style="text-align: {align}"' if align != 'left' else ''
                    processed_cell = self._process_bold_text_in_content(cell)
                    html += f'      <td{style}>{processed_cell}</td>\n'
                html += '    </tr>\n'
            html += '  </tbody>\n'
        
        html += '</table>'
        return html
    
    def _process_print_output_as_markdown(self, output: str):
        """Process print output lines as markdown content"""
        lines = output.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            # Check if line is a markdown header
            if line.startswith('#'):
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                if level > 0 and level <= 6 and line[level:].strip():
                    header_text = line[level:].strip()
                    processed_header = self._process_bold_text_in_content(header_text)
                    header_html = f'<h{level}>{processed_header}</h{level}>'
                    self.add_element(f'h{level}', header_text, header_html)
                    i += 1
                    continue
            
            # Check if line is a markdown table
            if '|' in line and line.count('|') >= 2:
                table_lines = [line]
                i += 1
                
                # Collect potential table lines
                while i < len(lines):
                    next_line = lines[i].strip()
                    if '|' in next_line and next_line.count('|') >= 2:
                        table_lines.append(next_line)
                        i += 1
                    elif not next_line:
                        i += 1
                        continue
                    else:
                        break
                
                # Process table if we have at least 2 rows (header + separator/data)
                if len(table_lines) >= 2:
                    table_html = self._process_markdown_table(table_lines)
                    if table_html:
                        self.add_element('table', table_lines, table_html)
                        continue
                
                # If not a valid table, fall back to regular text processing
                for table_line in table_lines:
                    processed_text = self._process_bold_text_in_content(table_line)
                    text_html = f'<p>{processed_text}</p>'
                    self.add_element('text', table_line, text_html)
                continue
            
            # Check if line is a list item
            if line.startswith('-') or re.match(r'^\d+\.\s+', line):
                if line.startswith('-'):
                    item_text = line[1:].strip()
                    processed_item = self._process_bold_text_in_content(item_text)
                    ul_html = f'<ul><li>{processed_item}</li></ul>'
                    self.add_element('ul', [item_text], ul_html)
                else:
                    match = re.match(r'^\d+\.\s+(.*)$', line)
                    if match:
                        item_text = match.group(1).strip()
                        processed_item = self._process_bold_text_in_content(item_text)
                        ol_html = f'<ol><li>{processed_item}</li></ol>'
                        self.add_element('ol', [item_text], ol_html)
                i += 1
                continue
            
            # Regular text - treat as paragraph
            processed_text = self._process_bold_text_in_content(line)
            text_html = f'<p>{processed_text}</p>'
            self.add_element('text', line, text_html)
            i += 1

    def _process_display_comments(self, code: str) -> str:
        """Process // comments in display-only code blocks"""
        lines = code.split('\n')
        processed_lines = []
        for line in lines:
            # Replace # comments with // comments for display
            if '#' in line and not line.strip().startswith('"') and not line.strip().startswith("'"):
                # Find the first # that's not inside quotes
                in_quotes = False
                quote_char = None
                for i, char in enumerate(line):
                    if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                        if not in_quotes:
                            in_quotes = True
                            quote_char = char
                        elif char == quote_char:
                            in_quotes = False
                            quote_char = None
                    elif char == '#' and not in_quotes:
                        # Replace # with // for display
                        line = line[:i] + '//' + line[i+1:]
                        break
            processed_lines.append(line)
        return '\n'.join(processed_lines)

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
    
    def _extract_code_blocks(self, content: str) -> Dict[int, str]:
        """Extract all code blocks with their positions for change detection"""
        code_blocks = {}
        lines = content.split('\n')
        i = 0
        block_index = 0
        
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            
            # Handle code blocks with ```
            if stripped_line == '```':
                i += 1  # Skip the opening ```
                code_lines = []
                start_line = i
                
                # Collect all lines until closing ```
                while i < len(lines):
                    current_line = lines[i]
                    if current_line.strip() == '```':
                        i += 1  # Skip the closing ```
                        break
                    code_lines.append(current_line)
                    i += 1
                
                if code_lines:
                    code_block = '\n'.join(code_lines)
                    code_blocks[block_index] = {
                        'code': code_block,
                        'start_line': start_line,
                        'type': 'executable'
                    }
                    block_index += 1
                continue
            
            # Handle display-only code blocks with ````
            elif stripped_line == '````':
                i += 1  # Skip the opening ````
                code_lines = []
                
                # Collect all lines until closing ````
                while i < len(lines):
                    current_line = lines[i]
                    if current_line.strip() == '````':
                        i += 1  # Skip the closing ````
                        break
                    code_lines.append(current_line)
                    i += 1
                
                if code_lines:
                    code_block = '\n'.join(code_lines)
                    code_blocks[block_index] = {
                        'code': code_block,
                        'type': 'display'
                    }
                    block_index += 1
                continue
            
            i += 1
        
        return code_blocks

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
                        variables_snapshot = self._get_variable_snapshot()
                        cache_key = f"exec_{code_block_index}_{self._get_code_hash(code_block, variables_snapshot)}"
                        
                        result = self.execute_code(code_block, cache_key)
                        if result['success']:
                            if result['output'].strip():
                                # Process print output as markdown
                                self._process_print_output_as_markdown(result['output'].strip())
                        else:
                            # Display execution error
                            error_html = f'<pre class="error">Code execution error: {result["error"]}</pre>'
                            self.add_element('error', result['error'], error_html)
                        
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
                    if cache_key in self.code_cache:
                        cached_html = self.code_cache[cache_key]['html']
                        self.add_element('display_code', code_block, cached_html)
                    else:
                        # Process // comments in display blocks
                        processed_code = self._process_display_comments(code_block)
                        display_html = f'<pre class="display-code">{processed_code}</pre>'
                        self.add_element('display_code', code_block, display_html)
                        # Cache the display HTML
                        self.code_cache[cache_key] = {'html': display_html}
                    
                    code_block_index += 1
                continue

            # Skip // comments (but not markdown lines)
            if stripped_line.startswith('//'):
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
                            variables_snapshot = self._get_variable_snapshot()
                            cache_key = f"exec_{code_block_index}_{self._get_code_hash(code_block, variables_snapshot)}"
                            
                            result = self.execute_code(code_block, cache_key)
                            if result['success']:
                                if result['output'].strip():
                                    # Process print output as markdown
                                    self._process_print_output_as_markdown(result['output'].strip())
                            else:
                                # Display execution error
                                error_html = f'<pre class="error">Code execution error: {result["error"]}</pre>'
                                self.add_element('error', result['error'], error_html)
                            
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
                        if cache_key in self.code_cache:
                            cached_html = self.code_cache[cache_key]['html']
                            self.add_element('display_code', code_block, cached_html)
                        else:
                            # Process // comments in display blocks
                            processed_code = self._process_display_comments(code_block)
                            display_html = f'<pre class="display-code">{processed_code}</pre>'
                            self.add_element('display_code', code_block, display_html)
                            # Cache the display HTML
                            self.code_cache[cache_key] = {'html': display_html}
                        
                        code_block_index += 1
                    continue
                
                # Determine if this is a header by counting # characters
                elif markdown_content.startswith('#'):
                    # This is a header (##, ###, etc.)
                    level = 1  # Start with level 1 for the first #
                    header_content = markdown_content[1:]  # Remove the first #
                    while header_content.startswith('#'):
                        level += 1
                        header_content = header_content[1:]
                    
                    if level <= 6 and header_content.strip():
                        header_text = header_content.strip()
                        processed_header = self._process_bold_text_in_content(header_text)
                        header_html = f'<h{level}>{processed_header}</h{level}>'
                        self.add_element(f'h{level}', header_text, header_html)
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
                        table_html = self._process_markdown_table(table_lines)
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
                            processed_items = [self._process_bold_text_in_content(item) for item in list_items]
                            ul_html = '<ul>' + ''.join(f'<li>{item}</li>' for item in processed_items) + '</ul>'
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
                                match = re.match(r'^\d+\.\s+(.*)$', current_content)
                                if match:
                                    item_text = match.group(1).strip()
                                    list_items.append(item_text)
                                    i += 1
                                else:
                                    break
                            else:
                                break
                        
                        if list_items:
                            processed_items = [self._process_bold_text_in_content(item) for item in list_items]
                            ol_html = '<ol>' + ''.join(f'<li>{item}</li>' for item in processed_items) + '</ol>'
                            self.add_element('ol', list_items, ol_html)
                        continue
                
                # Handle regular markdown text (prefixed with #)
                if markdown_content:
                    processed_text = self._process_bold_text_in_content(markdown_content)
                    text_html = f'<p>{processed_text}</p>'
                    self.add_element('text', markdown_content, text_html)
                i += 1
                continue

            # Handle legacy markdown syntax (headers, lists, text without # prefix)
            # This maintains backward compatibility
            if stripped_line.startswith('##'):  # Headers without # prefix (legacy)
                level = 0
                for char in stripped_line:
                    if char == '#':
                        level += 1
                    else:
                        break

                if level > 0 and level <= 6 and stripped_line[level:].strip():
                    header_text = stripped_line[level:].strip()
                    processed_header = self._process_bold_text_in_content(
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
                    table_html = self._process_markdown_table(table_lines)
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
                    processed_items = [self._process_bold_text_in_content(
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
                    processed_items = [self._process_bold_text_in_content(
                        item) for item in list_items]
                    ol_html = '<ol>' + \
                        ''.join(
                            f'<li>{item}</li>' for item in processed_items) + '</ol>'
                    self.add_element('ol', list_items, ol_html)
                continue

            # Handle plain text (legacy - without # prefix)
            if stripped_line and not stripped_line.startswith('#'):
                processed_text = self._process_bold_text_in_content(stripped_line)
                text_html = f'<p>{processed_text}</p>'
                self.add_element('text', stripped_line, text_html)
            i += 1

        return self.generate_html()

    def generate_html(self) -> str:
        """Generate complete HTML document"""
        content = '\n'.join(element['html'] for element in self.elements)

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

    def to_markdown(self, pymd_content: str) -> str:
        """Convert PyMD content to standard Markdown"""
        lines = pymd_content.split('\n')
        markdown_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()

            # Skip empty lines
            if not stripped_line:
                markdown_lines.append('')
                i += 1
                continue

            # Handle code blocks with ``` (executable code)
            if stripped_line == '```':
                markdown_lines.append('```python')
                i += 1  # Skip the opening ```
                
                # Collect all lines until closing ```
                while i < len(lines):
                    current_line = lines[i]
                    if current_line.strip() == '```':
                        markdown_lines.append('```')
                        i += 1  # Skip the closing ```
                        break
                    markdown_lines.append(current_line)
                    i += 1
                continue

            # Handle display-only code blocks with ````
            if stripped_line == '````':
                markdown_lines.append('```python')
                i += 1  # Skip the opening ````
                
                # Collect all lines until closing ````
                while i < len(lines):
                    current_line = lines[i]
                    if current_line.strip() == '````':
                        markdown_lines.append('```')
                        i += 1  # Skip the closing ````
                        break
                    markdown_lines.append(current_line)
                    i += 1
                continue

            # Skip // comments
            if stripped_line.startswith('//'):
                i += 1
                continue

            # Handle markdown content prefixed with # (remove the # prefix)
            if stripped_line.startswith('#'):
                markdown_content = stripped_line[1:].strip()
                if markdown_content:  # Only add non-empty content
                    markdown_lines.append(markdown_content)
                i += 1
                continue

            # Handle legacy content (without # prefix) for backward compatibility
            if stripped_line.startswith('##'):  # Legacy headers
                markdown_lines.append(stripped_line)
                i += 1
                continue

            # Handle legacy unordered lists (- or tab-)
            if stripped_line.startswith('-') or line.startswith('\t-'):
                markdown_lines.append(stripped_line)
                i += 1
                continue

            # Handle legacy ordered lists (1., 2., 3., etc.)
            if re.match(r'^\d+\.\s+', stripped_line):
                markdown_lines.append(stripped_line)
                i += 1
                continue

            # Handle legacy plain text (everything else without # prefix)
            if stripped_line and not stripped_line.startswith('#'):
                markdown_lines.append(stripped_line)
            i += 1

        return '\n'.join(markdown_lines)

    def generate_markdown(self) -> str:
        """Generate markdown from rendered elements (including captured images)"""
        markdown_parts = []
        
        for element in self.elements:
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

```
x = 5
y = 10
print(f"Sum: {x + y}")
```

# ## Data Processing

```
import random
data = [random.randint(1, 100) for _ in range(5)]
print(f"Generated data: {data}")
average = sum(data) / len(data)
print(f"Average: {average:.2f}")
```

# ## Using PyMD Functions

```
print("## Generated Header")
print(f"The average from above is: **{average:.2f}**")
```

# Regular text works perfectly with the new format!

```
print("Variables persist across blocks!")
print(f"**x = {x}, y = {y}**")
```

# ## Video Support Example

```
# Demonstrate video functionality (would work with real video file)
print("### Video Rendering")
print("PyMD now supports video rendering:")
print("```python")
print("pymd.video('sample.mp4', 'Demo video', width='80%')")
print("```")
```
"""

    html_output = renderer.parse_and_render(sample_content)
    print("PyMD Renderer created successfully!")
    print("Sample HTML length:", len(html_output))
