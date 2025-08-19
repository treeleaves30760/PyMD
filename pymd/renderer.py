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

            # Update variables
            self.variables.update({k: v for k, v in exec_globals.items()
                                   if not k.startswith('__') and k not in ['pymd', 'plt', 'pd', 'input']})

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

    def _process_bold_text_in_content(self, text: str) -> str:
        """Process **bold** syntax in content text"""
        # Replace **text** with <strong>text</strong>
        return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

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

    def parse_and_render(self, pymd_content: str) -> str:
        """Parse PyMD content with ``` blocks for code and Markdown syntax for content"""
        self.elements = []

        lines = pymd_content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()

            # Skip empty lines
            if not stripped_line:
                i += 1
                continue

            # Handle code blocks with ```
            if stripped_line == '```':
                i += 1  # Skip the opening ```
                code_lines = []

                # Collect all lines until closing ```
                while i < len(lines):
                    current_line = lines[i]
                    if current_line.strip() == '```':
                        # Found closing ```, stop collecting
                        i += 1  # Skip the closing ```
                        break
                    code_lines.append(current_line)
                    i += 1

                # Execute the collected code block
                if code_lines:
                    code_block = '\n'.join(code_lines)
                    try:
                        result = self.execute_code(code_block)
                        if result['success'] and result['output'].strip():
                            output_html = f'<pre class="code-output">{result["output"].strip()}</pre>'
                            self.add_element(
                                'code_output', result['output'], output_html)
                    except Exception as e:
                        error_html = f'<pre class="error">Code execution error: {str(e)}</pre>'
                        self.add_element('error', str(e), error_html)
                continue

            # Handle display-only code blocks with ````
            if stripped_line == '````':
                i += 1  # Skip the opening ````
                code_lines = []

                # Collect all lines until closing ````
                while i < len(lines):
                    current_line = lines[i]
                    if current_line.strip() == '````':
                        # Found closing ````, stop collecting
                        i += 1  # Skip the closing ````
                        break
                    code_lines.append(current_line)
                    i += 1

                # Display the code block without execution
                if code_lines:
                    code_block = '\n'.join(code_lines)
                    # Process // comments in display blocks
                    processed_code = self._process_display_comments(code_block)
                    display_html = f'<pre class="display-code">{processed_code}</pre>'
                    self.add_element('display_code', code_block, display_html)
                continue

            # Skip // comments
            if stripped_line.startswith('//'):
                i += 1
                continue

            # Handle headers (#, ##, ###, etc.)
            if stripped_line.startswith('#'):
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

            # Handle unordered lists (- or tab-)
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

            # Handle ordered lists (1., 2., 3., etc.)
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

            # Handle plain text (everything else outside code blocks)
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

    # Example PyMD content with new ``` syntax
    sample_content = """
// This is a comment and will be ignored

# Welcome to PyMD
This is a demonstration of PyMD with new ``` syntax for code blocks.

## Basic Features

- Markdown content outside code blocks
- Python code execution inside ``` blocks
- Variables persist across code blocks
- Clean separation of content and code

1. First feature: Headers and lists work normally
2. Second feature: Code blocks are clearly separated
3. Third feature: Mixed content is easy to read

## Python Code Execution

```
x = 5
y = 10
print(f"Sum: {x + y}")
```

## Data Processing

```
import random
data = [random.randint(1, 100) for _ in range(5)]
print(f"Generated data: {data}")
average = sum(data) / len(data)
print(f"Average: {average:.2f}")
```

## Using PyMD Functions

```
pymd.h2("Generated Header")
pymd.text(f"The average from above is: {average:.2f}")
```

Regular text works perfectly between code blocks!

```
print("Variables persist across blocks!")
print(f"x = {x}, y = {y}")
```
"""

    html_output = renderer.parse_and_render(sample_content)
    print("PyMD Renderer created successfully!")
    print("Sample HTML length:", len(html_output))
