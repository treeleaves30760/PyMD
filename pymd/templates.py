"""
PyMD HTML Templates
Contains all HTML templates for the PyMD server
"""

# Display template for the main page
DISPLAY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ filename }}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
            color: #1a1a1a;
        }
        
        h1 {
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 10px;
        }
        
        h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 8px;
        }
        
        h3 {
            font-size: 1.25em;
        }
        
        p {
            margin-bottom: 16px;
            color: #1a1a1a;
        }
        
        pre {
            background-color: #e8e8e8;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 14px;
            line-height: 1.45;
        }
        
        code {
            background-color: #e8e8e8;
            border-radius: 3px;
            padding: 2px 4px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 85%;
        }
        
        .image-container {
            margin: 20px 0;
            text-align: center;
        }
        
        .image-caption {
            font-style: italic;
            color: #666;
            margin-top: 8px;
        }
        
        .pymd-table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        
        .pymd-table th,
        .pymd-table td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }
        
        .pymd-table th {
            background-color: #f6f8fa;
            font-weight: 600;
        }
        
        .pymd-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        .error {
            background-color: #ffeaea;
            border: 1px solid #ff6b6b;
            border-radius: 6px;
            padding: 16px;
            color: #d63031;
            margin: 16px 0;
        }
        
        .data-output {
            background-color: #f0f8ff;
            border: 1px solid #b0c4de;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
        }
        
        .code-output {
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
        }
        
        ul, ol {
            margin: 16px 0;
            padding-left: 0;
            list-style: none;
        }
        
        ul li, ol li {
            margin: 8px 0;
            padding: 4px 0 4px 28px;
            line-height: 1.6;
            position: relative;
            color: #1a1a1a;
        }
        
        ul li::before {
            content: "•";
            color: #666;
            font-size: 16px;
            font-weight: bold;
            position: absolute;
            left: 12px;
            top: 4px;
        }
        
        ol {
            counter-reset: list-counter;
        }
        
        ol li {
            counter-increment: list-counter;
        }
        
        ol li::before {
            content: counter(list-counter) ".";
            color: #666;
            font-weight: 600;
            position: absolute;
            left: 8px;
            top: 4px;
            font-size: 14px;
        }
        
        ul li:hover, ol li:hover {
            background-color: #f8f9fa;
            border-radius: 4px;
            transition: background-color 0.2s ease;
        }
        
        /* Nested lists */
        ul ul, ol ol, ul ol, ol ul {
            margin: 4px 0;
            padding-left: 20px;
        }
        
        ul ul li::before {
            content: "◦";
            font-size: 14px;
        }
        
        ul ul ul li::before {
            content: "▪";
            font-size: 12px;
        }
        
        .footer {
            border-top: 1px solid #eaecef;
            padding: 20px 0;
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        
        .footer a {
            color: #0366d6;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .pymd-content {
            animation: fadeIn 0.3s ease-in-out;
        }
    </style>
</head>
<body>    
    <div id="content">
        {{ content|safe }}
    </div>

    <div class="footer">
        Powered By PyExecMD © <a href="https://github.com/treeleaves30760/PyMD" target="_blank">Github</a>
    </div>

    <script>
        const socket = io();
        const content = document.getElementById('content');
        
        socket.on('content_update', function(data) {
            content.innerHTML = data.html;
            // Add a subtle flash effect
            content.style.opacity = '0.7';
            setTimeout(() => { content.style.opacity = '1'; }, 150);
        });
    </script>
</body>
</html>
'''

# Error template for displaying errors
ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyExecMD Error</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .error { background: #ffebee; border: 1px solid #f44336; padding: 20px; border-radius: 4px; }
    </style>
</head>
<body>
    {error_content}
    <div style="border-top: 1px solid #eaecef; padding: 20px 0; margin-top: 40px; text-align: center; color: #666; font-size: 14px;">
        Powered By PyExecMD © <a href="https://github.com/treeleaves30760/PyMD" target="_blank">Github</a>
    </div>
</body>
</html>
'''


def get_editor_template(mode, filename, escaped_content, initial_html):
    """Generate the editor template with specified mode"""
    template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyExecMD Editor - {filename} - {mode.title()} Mode</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            height: 100vh;
            overflow: hidden;
            background-color: #fafafa;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 60px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 1.2em;
            margin: 0;
        }}
        
        .header-controls {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .export-btn {{
            background: #6f42c1;
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }}
        
        .export-btn:hover {{
            background: #5a2d91;
        }}
        
        .export-btn:disabled {{
            background: #6c757d;
            cursor: not-allowed;
        }}
        
        .mode-selector {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 5px;
            color: white;
            padding: 5px 10px;
            cursor: pointer;
        }}
        
        .mode-selector:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .save-btn {{
            background: #28a745;
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }}
        
        .save-btn:hover {{
            background: #218838;
        }}
        
        .save-btn:disabled {{
            background: #6c757d;
            cursor: not-allowed;
        }}
        
        .live-indicator {{
            background: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .live-indicator.disconnected {{
            background: #dc3545;
        }}
        
        .container {{
            height: calc(100vh - 60px);
            display: flex;
        }}
        
        .editor-panel {{
            width: {"100%" if mode == "editing" else "50%" if mode == "both" else "0"};
            {"display: none;" if mode == "viewing" else ""}
            border-right: 1px solid #ddd;
            position: relative;
        }}
        
        .preview-panel {{
            width: {"100%" if mode == "viewing" else "50%" if mode == "both" else "0"};
            {"display: none;" if mode == "editing" else ""}
            overflow-y: auto;
            padding: 20px;
            background: white;
            position: relative;
        }}

        /* Loading overlay for preview */
        .loading-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.75);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
        }}

        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid #e0e0e0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        /* Toast Notification */
        .toast {{
            position: fixed;
            right: 20px;
            bottom: 20px;
            background: rgba(50, 50, 50, 0.95);
            color: #fff;
            padding: 10px 16px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transform: translateY(10px);
            transition: opacity 0.2s ease, transform 0.2s ease;
            z-index: 9999;
        }}
        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        #editor {{
            height: 100%;
        }}
        
        .status-bar {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: #f8f9fa;
            border-top: 1px solid #ddd;
            padding: 5px 10px;
            font-size: 12px;
            color: #666;
            display: flex;
            justify-content: space-between;
        }}
        
        /* Preview styles */
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
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .pymd-content {{
            animation: fadeIn 0.3s ease-in-out;
        }}
        
        /* Monaco Editor custom line backgrounds for code blocks - using semi-transparent */
        .execution-code-line {{
            background-color: rgba(128, 128, 128, 0.15) !important;
        }}
        
        .display-code-line {{
            background-color: rgba(250, 250, 250, 0.8) !important;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PyExecMD Editor - {filename}</h1>
        <div class="header-controls">
            <select class="mode-selector" id="modeSelector">
                <option value="editing" {"selected" if mode == "editing" else ""}>Editing Only</option>
                <option value="viewing" {"selected" if mode == "viewing" else ""}>Preview Only</option>
                <option value="both" {"selected" if mode == "both" else ""}>Split View</option>
            </select>
            <button class="save-btn" id="saveBtn">💾 Save</button>
            <button class="export-btn" id="exportHtmlBtn">📄 Export HTML</button>
            <button class="export-btn" id="exportMdBtn">📝 Export MD</button>
            <div class="live-indicator" id="liveIndicator">🟢 Live</div>
        </div>
    </div>
    
    <div class="container">
        <div class="editor-panel" id="editorPanel">
            <div id="editor"></div>
            <div class="status-bar">
                <span id="statusText">Ready</span>
                <span id="positionInfo">Ln 1, Col 1</span>
            </div>
        </div>
        <div class="preview-panel" id="previewPanel">
            <div id="preview">{initial_html}</div>
            <div class="loading-overlay" id="previewLoading" style="display: none;">
                <div class="spinner"></div>
            </div>
        </div>
    </div>

    <script>
        let editor;
        let socket;
        let currentMode = '{mode}';
        let isModified = false;
        let isRendering = false;
        
        // Initialize Monaco Editor
        require.config({{ paths: {{ 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }} }});
        require(['vs/editor/editor.main'], function() {{
            // Register custom PyMD language
            monaco.languages.register({{ id: 'pymd' }});
            
            // Define tokenization rules for PyMD with proper Python highlighting
            monaco.languages.setMonarchTokensProvider('pymd', {{
                defaultToken: 'text-outside',
                tokenizer: {{
                    root: [
                        // Code block markers (regular)
                        [/^```\s*$/, {{ token: 'code-fence', next: '@codeblock' }}],
                        // Display-only code block markers (four backticks)
                        [/^````\s*$/, {{ token: 'display-fence', next: '@displayblock' }}],
                        // Code block markers prefixed with # (hide the #)
                        [/^#\s*```\s*$/, {{ token: 'code-fence-markdown', next: '@codeblock' }}],
                        [/^#\s*````\s*$/, {{ token: 'display-fence-markdown', next: '@displayblock' }}],
                        // Comments outside code blocks  
                        [/\/\/.*$/, 'comment.outside'],
                        // New syntax: # prefixed markdown content (headers) - hide the #
                        [/^#\s*(#+.*)$/, 'header.markdown'],
                        // New syntax: # prefixed markdown content (lists) - hide the #
                        [/^#\s*([-\*\+]\s.*)$/, 'list.markdown'],
                        [/^#\s*(\d+\.\s.*)$/, 'list.markdown'],
                        // New syntax: # prefixed markdown content (text) - hide the #
                        [/^#\s*(.+)$/, 'text.markdown'],
                        // Legacy: Headers without # prefix
                        [/^#+.*$/, 'header.outside'],
                        // Legacy: Lists without # prefix
                        [/^\s*[-\*\+]\s/, 'list.outside'],
                        [/^\s*\d+\.\s/, 'list.outside'],
                        // Everything else outside code blocks is darker text
                        [/.*/, 'text-outside']
                    ],
                    codeblock: [
                        // Code block end
                        [/^```\s*$/, {{ token: 'code-fence', next: '@pop' }}],
                        // Python keywords
                        [/\b(def|class|if|elif|else|for|while|try|except|finally|with|as|import|from|return|yield|pass|break|continue|raise|assert|global|nonlocal|lambda|and|or|not|in|is|True|False|None)\b/, 'keyword'],
                        // Python built-ins
                        [/\b(print|len|str|int|float|bool|list|dict|set|tuple|range|enumerate|zip|open|round|abs|min|max|sum|sorted|reversed|any|all)\b/, 'predefined'],
                        // Strings  
                        [/"([^"\\\\]|\\\\.)*"/, 'string'],
                        [/'([^'\\\\]|\\\\.)*'/, 'string'],
                        [/""\"[\\s\\S]*?""\"/, 'string'],
                        [/'\'\'[\\s\\S]*?'\'\'/, 'string'],
                        // Numbers
                        [/\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?/, 'number'],
                        // Comments
                        [/#.*$/, 'comment'],
                        // Operators
                        [/[=+\-*/%<>!&|^~]/, 'operator'],
                        // Delimiters
                        [/[\\[\\](){{}}]/, 'delimiter'],
                        // Variables and identifiers
                        [/[a-zA-Z_][a-zA-Z0-9_]*/, 'identifier'],
                        // Everything else in code blocks
                        [/.*/, 'source']
                    ],
                    displayblock: [
                        // Display block end
                        [/^````\s*$/, {{ token: 'display-fence', next: '@pop' }}],
                        // Python keywords
                        [/\b(def|class|if|elif|else|for|while|try|except|finally|with|as|import|from|return|yield|pass|break|continue|raise|assert|global|nonlocal|lambda|and|or|not|in|is|True|False|None)\b/, 'keyword'],
                        // Python built-ins
                        [/\b(print|len|str|int|float|bool|list|dict|set|tuple|range|enumerate|zip|open|round|abs|min|max|sum|sorted|reversed|any|all)\b/, 'predefined'],
                        // Strings  
                        [/"([^"\\\\]|\\\\.)*"/, 'string'],
                        [/'([^'\\\\]|\\\\.)*'/, 'string'],
                        [/""\"[\\s\\S]*?""\"/, 'string'],
                        [/'\'\'[\\s\\S]*?'\'\'/, 'string'],
                        // Numbers
                        [/\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?/, 'number'],
                        // Comments using // syntax for display blocks
                        [/\/\/.*$/, 'comment'],
                        // Operators
                        [/[=+\-*/%<>!&|^~]/, 'operator'],
                        // Delimiters
                        [/[\\[\\](){{}}]/, 'delimiter'],
                        // Variables and identifiers
                        [/[a-zA-Z_][a-zA-Z0-9_]*/, 'identifier'],
                        // Everything else in display blocks
                        [/.*/, 'source']
                    ]
                }}
            }});
            
            // Define custom theme with hidden # prefixes
            monaco.editor.defineTheme('pymd-theme', {{
                base: 'vs',
                inherit: true,
                rules: [
                    // Outside code block styling (darker)
                    {{ token: 'text-outside', foreground: '1a1a1a' }},
                    {{ token: 'comment.outside', foreground: '1a1a1a', fontStyle: 'italic' }},
                    {{ token: 'header.outside', foreground: '1a1a1a', fontStyle: 'bold' }},
                    {{ token: 'list.outside', foreground: '1a1a1a' }},
                    // New markdown syntax with # prefix (styled as markdown)
                    {{ token: 'text.markdown', foreground: '2d3748' }},
                    {{ token: 'header.markdown', foreground: '2d3748', fontStyle: 'bold' }},
                    {{ token: 'list.markdown', foreground: '2d3748' }},
                    // Code fence styling (both regular and # prefixed)
                    {{ token: 'code-fence', foreground: '0066cc', fontStyle: 'bold' }},
                    {{ token: 'display-fence', foreground: '6600cc', fontStyle: 'bold' }},
                    {{ token: 'code-fence-markdown', foreground: '0066cc', fontStyle: 'bold' }},
                    {{ token: 'display-fence-markdown', foreground: '6600cc', fontStyle: 'bold' }},
                    // Python syntax highlighting inside code blocks
                    {{ token: 'keyword', foreground: '0000ff', fontStyle: 'bold' }},
                    {{ token: 'predefined', foreground: '795e26' }},
                    {{ token: 'string', foreground: 'a31515' }},
                    {{ token: 'number', foreground: '09885a' }},
                    {{ token: 'comment', foreground: '008000', fontStyle: 'italic' }},
                    {{ token: 'operator', foreground: '000000' }},
                    {{ token: 'delimiter', foreground: '000000' }},
                    {{ token: 'identifier', foreground: '001080' }},
                    {{ token: 'source', foreground: '000000' }}
                ],
                colors: {{
                    'editor.background': '#ffffff',
                    'editor.selectionBackground': '#63A1FF',
                    'editor.selectionForeground': '#ffffff',
                    'editor.inactiveSelectionBackground': '#E5EBF1'
                }}
            }});
            
            // Add line background color rules for different code block types
            monaco.editor.onDidCreateEditor(function(editor) {{
                // Store original decorations
                let codeBlockDecorations = [];
                
                function updateCodeBlockBackgrounds() {{
                    const model = editor.getModel();
                    if (!model) return;
                    
                    const newDecorations = [];
                    const lines = model.getLinesContent();
                    let inExecutionBlock = false;
                    let inDisplayBlock = false;
                    
                    for (let i = 0; i < lines.length; i++) {{
                        const line = lines[i].trim();
                        
                        // Check for execution block start/end (```)
                        if (line === '```') {{
                            inExecutionBlock = !inExecutionBlock;
                            newDecorations.push({{
                                range: new monaco.Range(i + 1, 1, i + 1, 1),
                                options: {{
                                    isWholeLine: true,
                                    className: 'execution-code-line'
                                }}
                            }});
                        }}
                        // Check for display block start/end (````)
                        else if (line === '````') {{
                            inDisplayBlock = !inDisplayBlock;
                            newDecorations.push({{
                                range: new monaco.Range(i + 1, 1, i + 1, 1),
                                options: {{
                                    isWholeLine: true,
                                    className: 'display-code-line'
                                }}
                            }});
                        }}
                        // Lines inside execution blocks get gray background
                        else if (inExecutionBlock) {{
                            newDecorations.push({{
                                range: new monaco.Range(i + 1, 1, i + 1, 1),
                                options: {{
                                    isWholeLine: true,
                                    className: 'execution-code-line'
                                }}
                            }});
                        }}
                        // Lines inside display blocks keep white background
                        else if (inDisplayBlock) {{
                            newDecorations.push({{
                                range: new monaco.Range(i + 1, 1, i + 1, 1),
                                options: {{
                                    isWholeLine: true,
                                    className: 'display-code-line'
                                }}
                            }});
                        }}
                    }}
                    
                    codeBlockDecorations = editor.deltaDecorations(codeBlockDecorations, newDecorations);
                }}
                
                // Update backgrounds on content change
                editor.onDidChangeModelContent(updateCodeBlockBackgrounds);
                
                // Initial update
                setTimeout(updateCodeBlockBackgrounds, 100);
            }});
            
            // Create custom content transformer to hide # prefixes
            function createDisplayContent(rawContent) {{
                const lines = rawContent.split('\\n');
                const displayLines = [];
                let inCodeBlock = false;
                
                for (let i = 0; i < lines.length; i++) {{
                    const line = lines[i];
                    
                    // Check for code block markers
                    if (line.match(/^#\s*```[`]*\s*$/)) {{
                        // This is a code block marker, remove the # prefix and toggle code block state
                        displayLines.push(line.replace(/^#\s*/, ''));
                        inCodeBlock = !inCodeBlock;
                    }} else if (inCodeBlock) {{
                        // Inside code block, keep the line as-is (including Python # comments)
                        displayLines.push(line);
                    }} else if (line.match(/^#\s*/)) {{
                        // Outside code block, this is markdown content, remove the leading # and optional space
                        displayLines.push(line.replace(/^#\s?/, ''));
                    }} else {{
                        // Outside code block, non-# prefixed line (legacy markdown or Python code)
                        displayLines.push(line);
                    }}
                }}
                
                return displayLines.join('\\n');
            }}
            
            function createRawContent(displayContent) {{
                const lines = displayContent.split('\\n');
                const rawLines = [];
                let inCodeBlock = false;
                
                for (let i = 0; i < lines.length; i++) {{
                    const line = lines[i];
                    
                    // Check for code block markers
                    if (line.match(/^```[`]*\s*$/)) {{
                        // This is a code block marker, add # prefix and toggle code block state
                        rawLines.push('# ' + line);
                        inCodeBlock = !inCodeBlock;
                    }} else if (inCodeBlock) {{
                        // Inside code block, keep the line as-is (including Python # comments)
                        rawLines.push(line);
                    }} else if (line.trim() === '') {{
                        // Empty line outside code block becomes just #
                        rawLines.push('#');
                    }} else if (line.match(/^\s*(import|from|def|class|if|for|while|try|except|with|return|print)/) ||
                               line.match(/^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=/) ||
                               line.match(/^\s*[\[\](){{}}"']/)) {{
                        // This looks like Python code outside code blocks, keep as-is
                        rawLines.push(line);
                    }} else {{
                        // This looks like markdown content (including headers, lists, text), add # prefix
                        rawLines.push('# ' + line);
                    }}
                }}
                
                // Join lines back into a string
                return rawLines.join('\\n');
            }}
            
            // Transform content for display (hide # prefixes)
            const rawContent = {escaped_content};
            console.log('Raw content:', rawContent);
            const displayContent = createDisplayContent(rawContent);
            console.log('Display content:', displayContent);
            
            const editorElement = document.getElementById('editor');
            console.log('Editor element:', editorElement);
            
            try {{
                editor = monaco.editor.create(editorElement, {{
                    value: displayContent,
                    language: 'pymd',
                    theme: 'pymd-theme',
                    automaticLayout: true,
                    wordWrap: 'on',
                    minimap: {{ enabled: false }},
                    fontSize: 14,
                    lineNumbers: 'on',
                    renderWhitespace: 'boundary'
                }});
                console.log('Editor created successfully:', editor);
            }} catch (error) {{
                console.error('Error creating Monaco editor:', error);
                // Fallback: create a simple textarea
                const fallbackTextarea = document.createElement('textarea');
                fallbackTextarea.value = displayContent;
                fallbackTextarea.style.width = '100%';
                fallbackTextarea.style.height = '100%';
                fallbackTextarea.style.border = 'none';
                fallbackTextarea.style.resize = 'none';
                fallbackTextarea.style.fontFamily = 'monospace';
                fallbackTextarea.style.fontSize = '14px';
                editorElement.appendChild(fallbackTextarea);
                
                // Create a mock editor object for compatibility
                editor = {{
                    getValue: () => fallbackTextarea.value,
                    setValue: (value) => {{ fallbackTextarea.value = value; }},
                    onDidChangeModelContent: (callback) => {{
                        fallbackTextarea.addEventListener('input', callback);
                    }},
                    getPosition: () => ({{ lineNumber: 1, column: 1 }}),
                    onDidChangeCursorPosition: (callback) => {{}}
                }};
            }}
            
            // Store original content transformation functions
            editor._createDisplayContent = createDisplayContent;
            editor._createRawContent = createRawContent;
            editor._originalContent = rawContent;
            
            // Track changes
            editor.onDidChangeModelContent(function() {{
                isModified = true;
                updateSaveButton();
                updateStatusText('Modified');
            }});
            
            // Track cursor position
            editor.onDidChangeCursorPosition(function(e) {{
                const position = e.position;
                document.getElementById('positionInfo').textContent = `Ln ${{position.lineNumber}}, Col ${{position.column}}`;
            }});
            
            // Keyboard shortcuts
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, function() {{
                writeAndRun();
            }});
        }});
        
        // Initialize SocketIO
        socket = io();
        const liveIndicator = document.getElementById('liveIndicator');
        
        socket.on('connect', function() {{
            liveIndicator.textContent = '🟢 Live';
            liveIndicator.className = 'live-indicator';
        }});
        
        socket.on('disconnect', function() {{
            liveIndicator.textContent = '🔴 Disconnected';
            liveIndicator.className = 'live-indicator disconnected';
        }});
        
        socket.on('content_update', function(data) {{
            if (currentMode === 'viewing' || currentMode === 'both') {{
                document.getElementById('preview').innerHTML = data.html;
            }}
            // Hide loading overlay if we were rendering
            const overlay = document.getElementById('previewLoading');
            overlay.style.display = 'none';
            if (isRendering) {{
                // Determine if this is an error update
                const temp = document.createElement('div');
                temp.innerHTML = data.html || '';
                const hasError = !!temp.querySelector('.error');
                isRendering = false;
                isModified = false;
                updateSaveButton();
                updateStatusText('Rendered');
                setTimeout(() => updateStatusText('Ready'), 1500);
                if (!hasError) {{
                    showToast('Re-rendered successfully');
                }}
            }}
        }});
        
        // Mode switching
        document.getElementById('modeSelector').addEventListener('change', function(e) {{
            const newMode = e.target.value;
            switchMode(newMode);
        }});
        
        function switchMode(newMode) {{
            currentMode = newMode;
            const editorPanel = document.getElementById('editorPanel');
            const previewPanel = document.getElementById('previewPanel');
            
            // Update panel visibility and sizes
            switch(newMode) {{
                case 'editing':
                    editorPanel.style.width = '100%';
                    editorPanel.style.display = 'block';
                    previewPanel.style.width = '0';
                    previewPanel.style.display = 'none';
                    break;
                case 'viewing':
                    editorPanel.style.width = '0';
                    editorPanel.style.display = 'none';
                    previewPanel.style.width = '100%';
                    previewPanel.style.display = 'block';
                    break;
                case 'both':
                    editorPanel.style.width = '50%';
                    editorPanel.style.display = 'block';
                    previewPanel.style.width = '50%';
                    previewPanel.style.display = 'block';
                    break;
            }}
            
            // Update editor layout after panel resize
            if (editor) {{
                setTimeout(() => {{
                    editor.layout();
                }}, 100);
            }}
            
            // Do not auto-render on mode change; manual Ctrl+S to run
        }}
        // Write current content to disk and trigger render via file watcher
        function writeAndRun() {{
            if (!editor) return;
            const overlay = document.getElementById('previewLoading');
            overlay.style.display = 'flex';
            isRendering = true;
            updateStatusText('Saving & Rendering...');
            
            // Convert display content back to raw content with # prefixes
            const displayContent = editor.getValue();
            const rawContent = editor._createRawContent(displayContent);
            
            fetch('/api/write', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ content: rawContent }})
            }})
            .then(res => res.json())
            .then(data => {{
                if (!data.success) {{
                    // Fallback: if write failed (e.g., no file path), try client-side render
                    updateStatusText('Write failed, rendering client-side...');
                    isRendering = false;
                    updatePreview();
                }}
            }})
            .catch(err => {{
                console.error('Write error:', err);
                updateStatusText('Write error: ' + err.message);
                isRendering = false;
                overlay.style.display = 'none';
            }});
        }}
        
        // Save functionality
        document.getElementById('saveBtn').addEventListener('click', saveFile);
        
        // Export functionality
        document.getElementById('exportHtmlBtn').addEventListener('click', exportHtml);
        document.getElementById('exportMdBtn').addEventListener('click', exportMarkdown);
        
        function saveFile() {{
            if (!editor) return;
            
            // Convert display content back to raw content with # prefixes
            const displayContent = editor.getValue();
            const content = editor._createRawContent(displayContent);
            const saveBtn = document.getElementById('saveBtn');
            
            let filename = null;
            
            // If this is a blank file (no original file), prompt for filename
            if ('{filename}' === 'Blank File') {{
                filename = prompt('Enter filename (without extension):', 'untitled');
                if (filename === null) {{
                    // User cancelled
                    return;
                }}
            }}
            
            saveBtn.disabled = true;
            updateStatusText('Preparing download...');
            
            const payload = {{ content: content }};
            if (filename) {{
                payload.filename = filename;
            }}
            
            fetch('/api/save', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify(payload)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success && data.download) {{
                    // Create download
                    const blob = new Blob([data.content], {{ type: 'text/plain' }});
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = data.filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    isModified = false;
                    updateSaveButton();
                    updateStatusText('Downloaded: ' + data.filename);
                    setTimeout(() => updateStatusText('Ready'), 3000);
                }} else {{
                    updateStatusText('Save failed: ' + (data.error || 'Unknown error'));
                }}
            }})
            .catch(error => {{
                updateStatusText('Save error: ' + error.message);
            }})
            .finally(() => {{
                saveBtn.disabled = false;
            }});
        }}
        
        function exportHtml() {{
            if (!editor) return;
            
            // Convert display content back to raw content with # prefixes
            const displayContent = editor.getValue();
            const content = editor._createRawContent(displayContent);
            const exportBtn = document.getElementById('exportHtmlBtn');
            
            exportBtn.disabled = true;
            updateStatusText('Exporting to HTML...');
            
            fetch('/api/render', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ content: content }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    // Create filename
                    let filename = '{filename}';
                    if (filename === 'Blank File') {{
                        filename = 'export';
                    }} else if (filename.endsWith('.pymd')) {{
                        filename = filename.slice(0, -5);
                    }}
                    filename += '.html';
                    
                    // Create download
                    const blob = new Blob([data.html], {{ type: 'text/html' }});
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    updateStatusText('Exported: ' + filename);
                    setTimeout(() => updateStatusText('Ready'), 3000);
                    showToast('HTML exported successfully');
                }} else {{
                    updateStatusText('Export failed: ' + (data.error || 'Unknown error'));
                }}
            }})
            .catch(error => {{
                updateStatusText('Export error: ' + error.message);
            }})
            .finally(() => {{
                exportBtn.disabled = false;
            }});
        }}
        
        function exportMarkdown() {{
            if (!editor) return;
            
            // Convert display content back to raw content with # prefixes
            const displayContent = editor.getValue();
            const content = editor._createRawContent(displayContent);
            const exportBtn = document.getElementById('exportMdBtn');
            
            exportBtn.disabled = true;
            updateStatusText('Exporting to Markdown...');
            
            fetch('/api/export/markdown', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ content: content }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    // Create filename
                    let filename = '{filename}';
                    if (filename === 'Blank File') {{
                        filename = 'export';
                    }} else if (filename.endsWith('.pymd')) {{
                        filename = filename.slice(0, -5);
                    }}
                    filename += '.md';
                    
                    // Create download
                    const blob = new Blob([data.markdown], {{ type: 'text/markdown' }});
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    updateStatusText('Exported: ' + filename);
                    setTimeout(() => updateStatusText('Ready'), 3000);
                    showToast('Markdown exported successfully');
                }} else {{
                    updateStatusText('Export failed: ' + (data.error || 'Unknown error'));
                }}
            }})
            .catch(error => {{
                updateStatusText('Export error: ' + error.message);
            }})
            .finally(() => {{
                exportBtn.disabled = false;
            }});
        }}
        
        function updateSaveButton() {{
            const saveBtn = document.getElementById('saveBtn');
            if (isModified) {{
                saveBtn.textContent = '💾 Save*';
                saveBtn.style.background = '#ffc107';
            }} else {{
                saveBtn.textContent = '💾 Save';
                saveBtn.style.background = '#28a745';
            }}
        }}
        
        function updateStatusText(text) {{
            document.getElementById('statusText').textContent = text;
        }}

        function showToast(message) {{
            let toast = document.getElementById('toast');
            if (!toast) {{
                toast = document.createElement('div');
                toast.id = 'toast';
                toast.className = 'toast';
                document.body.appendChild(toast);
            }}
            toast.textContent = message;
            toast.style.display = 'block';
            requestAnimationFrame(() => {{
                toast.classList.add('show');
            }});
            setTimeout(() => {{
                toast.classList.remove('show');
                setTimeout(() => {{ toast.style.display = 'none'; }}, 200);
            }}, 2000);
        }}
        
        // Debounced preview update
        let previewTimeout;
        function debouncePreview() {{
            clearTimeout(previewTimeout);
            previewTimeout = setTimeout(updatePreview, 1000);
        }}
        
        function updatePreview() {{
            if (!editor) return;
            
            // Convert display content back to raw content with # prefixes
            const displayContent = editor.getValue();
            const content = editor._createRawContent(displayContent);
            const overlay = document.getElementById('previewLoading');
            overlay.style.display = 'flex';
            updateStatusText('Rendering...');
            
            fetch('/api/render', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ content: content }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    // Extract just the body content
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = data.html;
                    const contentDiv = tempDiv.querySelector('.pymd-content');
                    if (contentDiv) {{
                        document.getElementById('preview').innerHTML = contentDiv.innerHTML;
                    }}
                    updateStatusText('Rendered');
                    setTimeout(() => updateStatusText('Ready'), 1500);
                    showToast('Rendered successfully');
                }} else {{
                    updateStatusText('Render failed: ' + (data.error || 'Unknown error'));
                }}
            }})
            .catch(error => {{
                console.error('Preview update error:', error);
                updateStatusText('Render error: ' + error.message);
            }})
            .finally(() => {{
                overlay.style.display = 'none';
            }});
        }}
        
        // Prevent accidental page leave
        window.addEventListener('beforeunload', function(e) {{
            if (isModified) {{
                e.preventDefault();
                e.returnValue = '';
            }}
        }});
    </script>
</body>
</html>
    '''

    return template
