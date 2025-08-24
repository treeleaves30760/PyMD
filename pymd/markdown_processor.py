"""
Markdown processing and parsing utilities for PyMD renderer
"""

import re
import hashlib
from typing import List, Dict, Any


class MarkdownProcessor:
    """Handles markdown parsing, processing, and conversion"""
    
    def __init__(self, add_element_callback):
        self.add_element = add_element_callback
    
    def _process_bold_text(self, text: str) -> str:
        """Process **bold** syntax in text"""
        # Replace **text** with <strong>text</strong>
        return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    def _is_header_content(self, content: str) -> bool:
        """Determine if content should be treated as a header vs regular text"""
        # Simple heuristic: treat as header if it's a single word or short phrase without punctuation
        content = content.strip()
        
        # Not a header if it's a list item
        if content.startswith('-') or re.match(r'^\d+\.\s+', content):
            return False
        
        # Not a header if it contains sentence-ending punctuation
        if content.endswith('.') or content.endswith('!') or content.endswith('?'):
            return False
        
        # Not a header if it's too long (more than 8 words)
        words = content.split()
        if len(words) > 8:
            return False
            
        # Not a header if it starts with lowercase (likely a sentence)
        if content and content[0].islower():
            return False
            
        return True
    
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
            header_cells = [cell.strip()
                           for cell in header_line[1:-1].split('|')]

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
            processed_header = self._process_bold_text(header)
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
                    data_cells = [cell.strip()
                                 for cell in row_line[1:-1].split('|')]

                html += '    <tr>\n'
                for i, cell in enumerate(data_cells):
                    align = alignments[i] if i < len(alignments) else 'left'
                    style = f' style="text-align: {align}"' if align != 'left' else ''
                    processed_cell = self._process_bold_text(cell)
                    html += f'      <td{style}>{processed_cell}</td>\n'
                html += '    </tr>\n'
            html += '  </tbody>\n'

        html += '</table>'
        return html
    
    def process_print_output_as_markdown(self, output: str):
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
                    processed_header = self._process_bold_text(header_text)
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
                    processed_text = self._process_bold_text(table_line)
                    text_html = f'<p>{processed_text}</p>'
                    self.add_element('text', table_line, text_html)
                continue

            # Check if line is a list item
            if line.startswith('-') or re.match(r'^\d+\.\s+', line):
                if line.startswith('-'):
                    item_text = line[1:].strip()
                    processed_item = self._process_bold_text(item_text)
                    ul_html = f'<ul><li>{processed_item}</li></ul>'
                    self.add_element('ul', [item_text], ul_html)
                else:
                    match = re.match(r'^\d+\.\s+(.*)$', line)
                    if match:
                        item_text = match.group(1).strip()
                        processed_item = self._process_bold_text(item_text)
                        ol_html = f'<ol><li>{processed_item}</li></ol>'
                        self.add_element('ol', [item_text], ol_html)
                i += 1
                continue

            # Regular text - treat as paragraph
            processed_text = self._process_bold_text(line)
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

            # Skip // comments (both standalone and prefixed)
            if stripped_line.startswith('//') or stripped_line.startswith('# //'):
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