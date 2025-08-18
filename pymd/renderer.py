"""
PyMD Renderer - A Markdown-like language written in Python
Renders PyMD syntax to HTML with live Python code execution
"""

import re
import io
import base64
import sys
import traceback
from typing import Dict, Any, List, Optional
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
        """Create paragraph text"""
        html = f'<p>{content}</p>'
        if self.renderer:
            self.renderer.add_element('text', content, html)
        return html

    def code(self, content: str, language: str = 'python') -> str:
        """Create code block"""
        html = f'<pre><code class="language-{language}">{content}</code></pre>'
        if self.renderer:
            self.renderer.add_element('code', content, html)
        return html

    def image(self, plot_obj=None, caption: str = '') -> str:
        """Render matplotlib plot or other image objects"""
        if self.renderer:
            return self.renderer.render_image(plot_obj, caption)
        return f'<p>Image: {caption}</p>'

    def table(self, data) -> str:
        """Render pandas DataFrame or other tabular data"""
        if self.renderer:
            return self.renderer.render_table(data)
        return '<p>Table data</p>'


class PyMDRenderer:
    """
    Main renderer class for PyMD documents
    """

    def __init__(self):
        self.elements = []
        self.variables = {}
        self.pymd = PyMD(self)

    def add_element(self, element_type: str, content: Any, html: str):
        """Add a rendered element to the document"""
        self.elements.append({
            'type': element_type,
            'content': content,
            'html': html
        })

    def execute_code(self, code: str) -> Dict[str, Any]:
        """Execute Python code and capture output"""
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        result = {
            'success': True,
            'output': '',
            'error': '',
            'variables': {}
        }

        try:
            # Create execution environment with pymd available
            exec_globals = {
                '__builtins__': __builtins__,
                'pymd': self.pymd,
                'plt': plt,
                'pd': pd,
                **self.variables
            }

            # Redirect output
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute the code
            exec(code, exec_globals)

            # Update variables
            self.variables.update({k: v for k, v in exec_globals.items()
                                   if not k.startswith('__') and k not in ['pymd', 'plt', 'pd']})

            result['output'] = stdout_capture.getvalue()
            result['variables'] = self.variables

        except Exception as e:
            result['success'] = False
            result['error'] = traceback.format_exc()
            result['output'] = stdout_capture.getvalue()

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return result

    def render_image(self, plot_obj=None, caption: str = '') -> str:
        """Render matplotlib plot to base64 encoded image"""
        try:
            if plot_obj is None:
                # If no specific plot object, use current figure
                fig = plt.gcf()
            else:
                fig = plot_obj

            # Save plot to base64 string
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.getvalue()).decode()

            # Clear the current figure to prevent memory leaks
            plt.clf()

            html = f'''
            <div class="image-container">
                <img src="data:image/png;base64,{img_str}" alt="{caption}" style="max-width: 100%; height: auto;">
                {f'<p class="image-caption">{caption}</p>' if caption else ''}
            </div>
            '''

            self.add_element('image', caption, html)
            return html

        except Exception as e:
            error_html = f'<p class="error">Error rendering image: {str(e)}</p>'
            self.add_element('image', f'Error: {str(e)}', error_html)
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

    def parse_and_render(self, pymd_content: str) -> str:
        """Parse PyMD content and render to HTML"""
        self.elements = []

        # Process all content except comments (lines starting with #)
        lines = pymd_content.split('\n')
        code_lines = []

        for line in lines:
            stripped_line = line.strip()
            # Skip empty lines and comments (lines starting with #)
            if stripped_line and not stripped_line.startswith('#'):
                code_lines.append(line)

        # Execute all non-comment lines as a single code block
        if code_lines:
            code = '\n'.join(code_lines)
            if code.strip():
                result = self.execute_code(code)
                if not result['success']:
                    error_html = f'<pre class="error">Error: {result["error"]}</pre>'
                    self.add_element('error', result['error'], error_html)

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
            color: #333;
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
        }}
        
        pre {{
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 14px;
            line-height: 1.45;
        }}
        
        code {{
            background-color: #f6f8fa;
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

    # Example PyMD content
    sample_content = """
```
pymd.h1("Welcome to PyMD")
pymd.text("This is a demonstration of PyMD - a Python-based markup language.")

pymd.h2("Basic Usage")
pymd.text("You can create headings, text, and more using Python syntax.")

# Let's create some data
import numpy as np
data = np.random.randn(100)

pymd.h2("Data Visualization")
pymd.text("Here's a simple plot:")

plt.figure(figsize=(10, 6))
plt.plot(data)
plt.title("Random Data")
plt.xlabel("Index")
plt.ylabel("Value")
pymd.image(plt.gcf(), "A plot of random data")

pymd.h2("Tables")
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': ['a', 'b', 'c', 'd'],
    'C': [1.1, 2.2, 3.3, 4.4]
})
pymd.table(df)
```
"""

    html_output = renderer.parse_and_render(sample_content)
    print("PyMD Renderer created successfully!")
    print("Sample HTML length:", len(html_output))
