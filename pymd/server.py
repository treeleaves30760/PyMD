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
from .templates import DISPLAY_TEMPLATE, ERROR_TEMPLATE, get_editor_template
import threading
import argparse
import json


class PyMDFileHandler(FileSystemEventHandler):
    """File system event handler for watching PyExecMD files"""

    def __init__(self, socketio, file_path):
        self.socketio = socketio
        self.file_path = file_path
        # Set output directory based on the file location
        output_dir = os.path.dirname(file_path) if file_path else os.getcwd()
        self.renderer = PyMDRenderer(output_dir=output_dir)
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

            # Extract the full pymd-content wrapper robustly
            start_marker = '<div class="pymd-content">'
            start_idx = html.find(start_marker)
            end_body_idx = html.rfind('</body>')

            if start_idx != -1 and end_body_idx != -1 and end_body_idx > start_idx:
                body_content = html[start_idx:end_body_idx]
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
        
        # Set output directory based on the file location
        if self.file_path:
            output_dir = os.path.dirname(self.file_path)
        else:
            output_dir = os.getcwd()
        self.renderer = PyMDRenderer(output_dir=output_dir)
        self.observer = None

        self.setup_routes()
        self.setup_socketio()

    def setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/api/render', methods=['POST'])
        def api_render():
            """API endpoint for rendering PyExecMD content"""
            try:
                content = request.json.get('content', '')
                html = self.renderer.parse_and_render(content)
                return jsonify({'success': True, 'html': html})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/export/markdown', methods=['POST'])
        def api_export_markdown():
            """API endpoint for exporting PyExecMD content to Markdown"""
            try:
                content = request.json.get('content', '')
                markdown = self.renderer.to_markdown(content)
                return jsonify({'success': True, 'markdown': markdown})
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
                        # Extract full pymd-content wrapper safely
                        start_marker = '<div class="pymd-content">'
                        start_idx = initial_html.find(start_marker)
                        end_body_idx = initial_html.rfind('</body>')
                        if start_idx != -1 and end_body_idx != -1 and end_body_idx > start_idx:
                            initial_html = initial_html[start_idx:end_body_idx]
                    except Exception as e:
                        initial_html = f'<div class="error">Error rendering: {str(e)}</div>'

                # Properly escape content for JavaScript using JSON
                escaped_content = json.dumps(content)
                return get_editor_template(mode, os.path.basename(self.file_path) if self.file_path else "Blank File", escaped_content, initial_html)

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

        @self.app.route('/api/write', methods=['POST'])
        def write_content():
            """API endpoint to write editor content to the backing .pymd file"""
            try:
                if not self.file_path:
                    return jsonify({'success': False, 'error': 'No file path specified on server'}), 400

                content = request.json.get('content', '')
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # File watcher will detect the write and emit an update
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

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

        @self.app.route('/editor/videos/<path:filename>')
        def serve_videos(filename):
            """Serve video files from the videos directory"""
            try:
                # Get the directory where the .pymd file is located
                if self.file_path:
                    base_dir = os.path.dirname(self.file_path)
                else:
                    base_dir = os.getcwd()
                videos_dir = os.path.join(base_dir, 'videos')
                
                # Debug logging
                print(f"Serving video: {filename} from {videos_dir}")
                
                # Check if file exists
                file_path = os.path.join(videos_dir, filename)
                if not os.path.exists(file_path):
                    print(f"Video file not found: {file_path}")
                    return f"Video file not found: {file_path}", 404
                
                return send_from_directory(videos_dir, filename)
            except Exception as e:
                print(f"Error serving video {filename}: {str(e)}")
                return f"Video not found: {str(e)}", 404

        @self.app.route('/editor/images/<path:filename>')
        def serve_images(filename):
            """Serve image files from the images directory"""
            try:
                # Get the directory where the .pymd file is located
                if self.file_path:
                    base_dir = os.path.dirname(self.file_path)
                else:
                    base_dir = os.getcwd()
                images_dir = os.path.join(base_dir, 'images')
                
                # Debug logging
                print(f"Serving image: {filename} from {images_dir}")
                
                # Check if file exists
                file_path = os.path.join(images_dir, filename)
                if not os.path.exists(file_path):
                    print(f"Image file not found: {file_path}")
                    return f"Image file not found: {file_path}", 404
                
                return send_from_directory(images_dir, filename)
            except Exception as e:
                print(f"Error serving image {filename}: {str(e)}")
                return f"Image not found: {str(e)}", 404

        @self.app.route('/videos/<path:filename>')
        def serve_videos_root(filename):
            """Serve video files from the videos directory (root path)"""
            try:
                # Get the directory where the .pymd file is located
                if self.file_path:
                    base_dir = os.path.dirname(self.file_path)
                else:
                    base_dir = os.getcwd()
                videos_dir = os.path.join(base_dir, 'videos')
                
                # Debug logging
                print(f"Serving video (root): {filename} from {videos_dir}")
                
                # Check if file exists
                file_path = os.path.join(videos_dir, filename)
                if not os.path.exists(file_path):
                    print(f"Video file not found (root): {file_path}")
                    return f"Video file not found: {file_path}", 404
                
                return send_from_directory(videos_dir, filename)
            except Exception as e:
                print(f"Error serving video (root) {filename}: {str(e)}")
                return f"Video not found: {str(e)}", 404

        @self.app.route('/images/<path:filename>')
        def serve_images_root(filename):
            """Serve image files from the images directory (root path)"""
            try:
                # Get the directory where the .pymd file is located
                if self.file_path:
                    base_dir = os.path.dirname(self.file_path)
                else:
                    base_dir = os.getcwd()
                images_dir = os.path.join(base_dir, 'images')
                
                # Debug logging
                print(f"Serving image (root): {filename} from {images_dir}")
                
                # Check if file exists
                file_path = os.path.join(images_dir, filename)
                if not os.path.exists(file_path):
                    print(f"Image file not found (root): {file_path}")
                    return f"Image file not found: {file_path}", 404
                
                return send_from_directory(images_dir, filename)
            except Exception as e:
                print(f"Error serving image (root) {filename}: {str(e)}")
                return f"Image not found: {str(e)}", 404

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

                # Use template from templates module

                # Extract content from full HTML
                start_marker = '<div class="pymd-content">'
                start_idx = html.find(start_marker)
                end_body_idx = html.rfind('</body>')
                if start_idx != -1 and end_body_idx != -1 and end_body_idx > start_idx:
                    content = html[start_idx:end_body_idx]
                else:
                    content = '<div class="pymd-content"><p>No content rendered</p></div>'

                return render_template_string(DISPLAY_TEMPLATE,
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

                # Use error template from templates module
                return ERROR_TEMPLATE.format(error_content=error_content)

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
                              port=self.port, debug=debug, allow_unsafe_werkzeug=True)
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
