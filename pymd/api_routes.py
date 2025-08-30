"""
API route handlers for PyMD server
"""

import os
import json
import time
from flask import request, jsonify
from .renderer import PyMDRenderer


class ApiRoutes:
    """Handles API endpoint routing and logic"""
    
    def __init__(self, app, file_path, renderer, socketio=None):
        self.app = app
        self.file_path = file_path
        self.renderer = renderer
        self.socketio = socketio
        self.setup_routes()
        
    def _create_progress_callback(self):
        """Create a progress callback that emits via WebSocket"""
        if self.socketio:
            def progress_callback(step: str, progress: float):
                self.socketio.emit('render_status', {
                    'step': step,
                    'progress': progress,
                    'timestamp': time.time()
                })
            return progress_callback
        return None
    
    def setup_routes(self):
        """Setup API Flask routes"""

        @self.app.route('/api/render', methods=['POST'])
        def api_render():
            """API endpoint for rendering PyExecMD content"""
            try:
                content = request.json.get('content', '')
                
                # Create a temporary renderer with WebSocket progress callback
                output_dir = self.renderer.output_dir
                temp_renderer = PyMDRenderer(output_dir=output_dir, progress_callback=self._create_progress_callback())
                
                html = temp_renderer.parse_and_render(content)
                return jsonify({'success': True, 'html': html})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/export/markdown', methods=['POST'])
        def api_export_markdown():
            """API endpoint for exporting PyExecMD content to Markdown"""
            try:
                content = request.json.get('content', '')
                
                # Create a temporary renderer with WebSocket progress callback
                output_dir = self.renderer.output_dir
                temp_renderer = PyMDRenderer(output_dir=output_dir, progress_callback=self._create_progress_callback())
                
                markdown = temp_renderer.to_markdown(content)
                return jsonify({'success': True, 'markdown': markdown})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

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
                    base_name = os.path.splitext(os.path.basename(self.file_path))[0]
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