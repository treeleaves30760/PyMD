"""
PyExecMD Live Preview Server
Provides real-time rendering of PyExecMD files with auto-refresh
"""

import os
import time
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .renderer import PyMDRenderer
import threading
import argparse


class PyMDFileHandler(FileSystemEventHandler):
    """File system event handler for watching PyExecMD files"""

    def __init__(self, socketio, file_path):
        self.socketio = socketio
        self.file_path = file_path
        self.renderer = PyMDRenderer()
        self.last_modified = 0

    def on_modified(self, event):
        if event.src_path == self.file_path and not event.is_directory:
            # Debounce rapid file changes
            current_time = time.time()
            if current_time - self.last_modified > 0.5:  # 500ms debounce
                self.last_modified = current_time
                self.render_and_emit()

    def render_and_emit(self):
        """Render the file and emit to all connected clients"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            html = self.renderer.parse_and_render(content)

            # Extract just the body content for live updates
            start_marker = '<div class="pymd-content">'
            end_marker = '</div>'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)

            if start_idx != -1 and end_idx != -1:
                body_content = html[start_idx:end_idx]
            else:
                body_content = html

            self.socketio.emit('content_update', {'html': body_content})

        except Exception as e:
            error_content = f'<div class="error">Error rendering file: {str(e)}</div>'
            self.socketio.emit('content_update', {'html': error_content})


class PyMDServer:
    """Live preview server for PyExecMD files"""

    def __init__(self, file_path=None, port=8080, host='localhost'):
        self.file_path = os.path.abspath(file_path) if file_path else None
        self.port = port
        self.host = host
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'pymd_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.renderer = PyMDRenderer()
        self.observer = None

        self.setup_routes()
        self.setup_socketio()

    def setup_routes(self):
        """Setup Flask routes"""

#         @self.app.route('/')
#         def index():
#             """Serve the main page with live preview"""
#             try:
#                 if self.file_path:
#                     print(f"Attempting to read file: {self.file_path}")
#                     print(f"File exists: {os.path.exists(self.file_path)}")
#                     print(
#                         f"File readable: {os.access(self.file_path, os.R_OK)}")

#                     with open(self.file_path, 'r', encoding='utf-8') as f:
#                         content = f.read()

#                     print(f"File content length: {len(content)}")
#                 else:
#                     content = ""  # Empty content for blank file
#                     print("Using blank file content")

#                 html = self.renderer.parse_and_render(content)
#                 print(f"Rendered HTML length: {len(html)}")

#                 # Create live preview template
#                 template = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>PyExecMD Live Preview - {{ filename }}</title>
#     <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
#     <style>
#         body {
#             font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
#             line-height: 1.6;
#             color: #333;
#             max-width: 1200px;
#             margin: 0 auto;
#             padding: 20px;
#             background-color: #fafafa;
#         }

#         .header {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#             text-align: center;
#         }

#         .live-indicator {
#             position: fixed;
#             top: 20px;
#             right: 20px;
#             background: #28a745;
#             color: white;
#             padding: 8px 16px;
#             border-radius: 20px;
#             font-size: 14px;
#             font-weight: bold;
#             z-index: 1000;
#             box-shadow: 0 2px 10px rgba(0,0,0,0.2);
#         }

#         .live-indicator.disconnected {
#             background: #dc3545;
#         }

#         h1, h2, h3, h4, h5, h6 {
#             margin-top: 24px;
#             margin-bottom: 16px;
#             font-weight: 600;
#             line-height: 1.25;
#         }

#         h1 {
#             font-size: 2em;
#             border-bottom: 1px solid #eaecef;
#             padding-bottom: 10px;
#         }

#         h2 {
#             font-size: 1.5em;
#             border-bottom: 1px solid #eaecef;
#             padding-bottom: 8px;
#         }

#         h3 {
#             font-size: 1.25em;
#         }

#         p {
#             margin-bottom: 16px;
#         }

#         pre {
#             background-color: #f6f8fa;
#             border-radius: 6px;
#             padding: 16px;
#             overflow: auto;
#             font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
#             font-size: 14px;
#             line-height: 1.45;
#         }

#         code {
#             background-color: #f6f8fa;
#             border-radius: 3px;
#             padding: 2px 4px;
#             font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
#             font-size: 85%;
#         }

#         .image-container {
#             margin: 20px 0;
#             text-align: center;
#         }

#         .image-caption {
#             font-style: italic;
#             color: #666;
#             margin-top: 8px;
#         }

#         .pymd-table {
#             border-collapse: collapse;
#             width: 100%;
#             margin: 20px 0;
#         }

#         .pymd-table th,
#         .pymd-table td {
#             border: 1px solid #ddd;
#             padding: 8px 12px;
#             text-align: left;
#         }

#         .pymd-table th {
#             background-color: #f6f8fa;
#             font-weight: 600;
#         }

#         .pymd-table tr:nth-child(even) {
#             background-color: #f9f9f9;
#         }

#         .error {
#             background-color: #ffeaea;
#             border: 1px solid #ff6b6b;
#             border-radius: 6px;
#             padding: 16px;
#             color: #d63031;
#             margin: 16px 0;
#         }

#         .data-output {
#             background-color: #f0f8ff;
#             border: 1px solid #b0c4de;
#             border-radius: 6px;
#             padding: 16px;
#             margin: 16px 0;
#         }

#         @keyframes fadeIn {
#             from { opacity: 0; transform: translateY(10px); }
#             to { opacity: 1; transform: translateY(0); }
#         }

#         .pymd-content {
#             animation: fadeIn 0.3s ease-in-out;
#         }
#     </style>
# </head>
# <body>
#     <div class="live-indicator" id="liveIndicator">🟢 Live</div>

#     <div id="content">
#         {{ content|safe }}
#     </div>

#     <script>
#         const socket = io();
#         const liveIndicator = document.getElementById('liveIndicator');
#         const content = document.getElementById('content');

#         socket.on('connect', function() {
#             liveIndicator.textContent = '🟢 Live';
#             liveIndicator.className = 'live-indicator';
#         });

#         socket.on('disconnect', function() {
#             liveIndicator.textContent = '🔴 Disconnected';
#             liveIndicator.className = 'live-indicator disconnected';
#         });

#         socket.on('content_update', function(data) {
#             content.innerHTML = data.html;
#             // Add a subtle flash effect
#             content.style.opacity = '0.7';
#             setTimeout(() => { content.style.opacity = '1'; }, 150);
#         });
#     </script>
# </body>
# </html>
#                 '''

#                 # Extract content from full HTML
#                 start_marker = '<div class="pymd-content">'
#                 end_marker = '</div>'
#                 start_idx = html.find(start_marker)
#                 end_idx = html.find(end_marker, start_idx) + len(end_marker)

#                 if start_idx != -1 and end_idx != -1:
#                     content = html[start_idx:end_idx]
#                 else:
#                     content = '<div class="pymd-content"><p>No content rendered</p></div>'

#                 return render_template_string(template,
#                                               filename=os.path.basename(
#                                                   self.file_path) if self.file_path else "Blank File",
#                                               content=content)

#             except Exception as e:
#                 print(f"Error in index route: {str(e)}")
#                 print(f"Error type: {type(e)}")
#                 import traceback
#                 print(f"Full traceback: {traceback.format_exc()}")

#                 error_content = f'''
#                 <div class="error">
#                     <h2>Error loading file</h2>
#                     <p><strong>Error:</strong> {str(e)}</p>
#                     <p><strong>File:</strong> {self.file_path}</p>
#                     <p><strong>Exists:</strong> {os.path.exists(self.file_path)}</p>
#                     <p><strong>Readable:</strong> {os.access(self.file_path, os.R_OK) if os.path.exists(self.file_path) else 'File does not exist'}</p>
#                 </div>
#                 '''

#                 # Create a minimal template for error display
#                 error_template = f'''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>PyExecMD Error</title>
#     <style>
#         body {{ font-family: Arial, sans-serif; margin: 40px; }}
#         .error {{ background: #ffebee; border: 1px solid #f44336; padding: 20px; border-radius: 4px; }}
#     </style>
# </head>
# <body>
#     {error_content}
# </body>
# </html>
#                 '''
#                 return error_template

        @self.app.route('/api/render', methods=['POST'])
        def api_render():
            """API endpoint for rendering PyExecMD content"""
            try:
                content = request.json.get('content', '')
                html = self.renderer.parse_and_render(content)
                return jsonify({'success': True, 'html': html})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/editor')
        @self.app.route('/editor/<mode>')
        def editor(mode='both'):
            """Serve the editor page with different viewing modes"""
            try:
                # Validate mode
                if mode not in ['editing', 'viewing', 'both']:
                    mode = 'both'

                if self.file_path:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = ""  # Empty content for blank file

                # Get initial rendered content for viewing mode
                initial_html = ''
                if mode in ['viewing', 'both']:
                    try:
                        initial_html = self.renderer.parse_and_render(content)
                        # Extract just the body content
                        start_marker = '<div class="pymd-content">'
                        end_marker = '</div>'
                        start_idx = initial_html.find(start_marker)
                        end_idx = initial_html.find(
                            end_marker, start_idx) + len(end_marker)
                        if start_idx != -1 and end_idx != -1:
                            initial_html = initial_html[start_idx:end_idx]
                    except Exception as e:
                        initial_html = f'<div class="error">Error rendering: {str(e)}</div>'

                return self.render_editor_template(mode, content, initial_html)

            except Exception as e:
                return f"Error loading editor: {str(e)}"

        @self.app.route('/api/content', methods=['GET'])
        def get_content():
            """API endpoint to get current file content"""
            try:
                if self.file_path:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = ""  # Empty content for blank file
                return jsonify({'success': True, 'content': content})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/save', methods=['POST'])
        def save_content():
            """API endpoint to save file content as download"""
            try:
                content = request.json.get('content', '')
                filename = request.json.get('filename', None)

                if self.file_path:
                    # If we have an existing file, create a new name with timestamp
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = os.path.splitext(
                        os.path.basename(self.file_path))[0]
                    download_filename = f"{base_name}_copy_{timestamp}.pymd"
                else:
                    # No original file, create new filename
                    if filename and filename.strip():
                        # Use provided filename
                        if not filename.endswith('.pymd'):
                            filename += '.pymd'
                        download_filename = filename
                    else:
                        # Auto-generate filename
                        import datetime
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        download_filename = f"untitled_{timestamp}.pymd"

                return jsonify({
                    'success': True,
                    'download': True,
                    'filename': download_filename,
                    'content': content
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/')
        def display():
            """Serve the display page with direct render"""
            try:
                if self.file_path:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = ""  # Empty content for blank file

                html = self.renderer.parse_and_render(content)

                # Create display template with direct render and footer
                template = '''
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
            color: #333;
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
        }
        
        pre {
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 14px;
            line-height: 1.45;
        }
        
        code {
            background-color: #f6f8fa;
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

                # Extract content from full HTML
                start_marker = '<div class="pymd-content">'
                end_marker = '</div>'
                start_idx = html.find(start_marker)
                end_idx = html.find(end_marker, start_idx) + len(end_marker)

                if start_idx != -1 and end_idx != -1:
                    content = html[start_idx:end_idx]
                else:
                    content = '<div class="pymd-content"><p>No content rendered</p></div>'

                return render_template_string(template,
                                              filename=os.path.basename(
                                                  self.file_path) if self.file_path else "Blank File",
                                              content=content)

            except Exception as e:
                error_content = f'''
                <div class="error">
                    <h2>Error loading file</h2>
                    <p><strong>Error:</strong> {str(e)}</p>
                    <p><strong>File:</strong> {self.file_path}</p>
                </div>
                '''

                # Create a minimal template for error display
                error_template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyExecMD Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .error {{ background: #ffebee; border: 1px solid #f44336; padding: 20px; border-radius: 4px; }}
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
                return error_template

    def render_editor_template(self, mode, content, initial_html):
        """Render the editor template with specified mode"""
        filename = os.path.basename(
            self.file_path) if self.file_path else "Blank File"

        # Properly escape content for JavaScript using JSON
        import json
        escaped_content = json.dumps(content)

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
            editor = monaco.editor.create(document.getElementById('editor'), {{
                value: {escaped_content},
                language: 'python',
                theme: 'vs',
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

    def setup_socketio(self):
        """Setup SocketIO events"""

        @self.socketio.on('connect')
        def handle_connect():
            print(f"Client connected")

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"Client disconnected")

    def start_file_watcher(self):
        """Start watching the file for changes"""
        if self.file_path and os.path.exists(self.file_path):
            event_handler = PyMDFileHandler(self.socketio, self.file_path)
            self.observer = Observer()
            self.observer.schedule(event_handler, os.path.dirname(
                self.file_path), recursive=False)
            self.observer.start()
            print(f"Watching file: {self.file_path}")
        elif self.file_path:
            print(f"Warning: File {self.file_path} does not exist")
        else:
            print("No file specified - file watching disabled")

    def run(self, debug=False):
        """Start the live preview server"""
        print(f"🐍 PyExecMD Live Preview Server")
        if self.file_path:
            print(f"📁 File: {self.file_path}")
            print(f"💡 Tip: Edit your .pymd file and see changes instantly!")
        else:
            print(f"📁 File: <blank file>")
            print(
                f"💡 Tip: Start with a blank file, edit in the editor and save as needed!")
        print(f"🌐 Server: http://{self.host}:{self.port}")
        print("-" * 50)

        # Start file watcher in a separate thread
        watcher_thread = threading.Thread(target=self.start_file_watcher)
        watcher_thread.daemon = True
        watcher_thread.start()

        try:
            self.socketio.run(self.app, host=self.host,
                              port=self.port, debug=debug)
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()


def main():
    """Command line interface for PyExecMD server"""
    parser = argparse.ArgumentParser(
        description='PyExecMD Live Preview Server')
    parser.add_argument('file', help='PyExecMD file to preview')
    parser.add_argument('--port', '-p', type=int, default=8080,
                        help='Port to run server on (default: 8080)')
    parser.add_argument('--host', default='localhost',
                        help='Host to bind to (default: localhost)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' does not exist")
        return 1

    server = PyMDServer(args.file, args.port, args.host)
    server.run(args.debug)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
