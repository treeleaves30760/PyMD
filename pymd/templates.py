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
        </div>
    </div>

    <script>
        let editor;
        let socket;
        let currentMode = '{mode}';
        let isModified = false;
        
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
                        // Code block markers
                        [/^```\s*$/, {{ token: 'code-fence', next: '@codeblock' }}],
                        // Display-only code block markers (four backticks)
                        [/^````\s*$/, {{ token: 'display-fence', next: '@displayblock' }}],
                        // Comments outside code blocks  
                        [/\/\/.*$/, 'comment.outside'],
                        // Headers
                        [/^#+.*$/, 'header.outside'],
                        // Lists
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
            
            // Define custom theme
            monaco.editor.defineTheme('pymd-theme', {{
                base: 'vs',
                inherit: true,
                rules: [
                    // Outside code block styling (darker)
                    {{ token: 'text-outside', foreground: '1a1a1a' }},
                    {{ token: 'comment.outside', foreground: '1a1a1a', fontStyle: 'italic' }},
                    {{ token: 'header.outside', foreground: '1a1a1a', fontStyle: 'bold' }},
                    {{ token: 'list.outside', foreground: '1a1a1a' }},
                    // Code fence styling
                    {{ token: 'code-fence', foreground: '0066cc', fontStyle: 'bold' }},
                    {{ token: 'display-fence', foreground: '6600cc', fontStyle: 'bold' }},
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
                    'editor.background': '#ffffff'
                }}
            }});
            
            editor = monaco.editor.create(document.getElementById('editor'), {{
                value: {escaped_content},
                language: 'pymd',
                theme: 'pymd-theme',
                automaticLayout: true,
                wordWrap: 'on',
                minimap: {{ enabled: false }},
                fontSize: 14,
                lineNumbers: 'on',
                renderWhitespace: 'boundary'
            }});
            
            // Track changes
            editor.onDidChangeModelContent(function() {{
                isModified = true;
                updateSaveButton();
                updateStatusText('Modified');
                
                // Auto-preview in both mode
                if (currentMode === 'both' || currentMode === 'viewing') {{
                    debouncePreview();
                }}
            }});
            
            // Track cursor position
            editor.onDidChangeCursorPosition(function(e) {{
                const position = e.position;
                document.getElementById('positionInfo').textContent = `Ln ${{position.lineNumber}}, Col ${{position.column}}`;
            }});
            
            // Keyboard shortcuts
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, function() {{
                saveFile();
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
        }});
        
        // Mode switching
        document.getElementById('modeSelector').addEventListener('change', function(e) {{
            const newMode = e.target.value;
            window.location.href = `/editor/${{newMode}}`;
        }});
        
        // Save functionality
        document.getElementById('saveBtn').addEventListener('click', saveFile);
        
        function saveFile() {{
            if (!editor) return;
            
            const content = editor.getValue();
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
        
        // Debounced preview update
        let previewTimeout;
        function debouncePreview() {{
            clearTimeout(previewTimeout);
            previewTimeout = setTimeout(updatePreview, 1000);
        }}
        
        function updatePreview() {{
            if (!editor) return;
            
            const content = editor.getValue();
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
                }}
            }})
            .catch(error => {{
                console.error('Preview update error:', error);
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