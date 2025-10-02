"""
PyExecMD Live Preview Server
Provides real-time rendering of PyExecMD files with auto-refresh
"""

import os
import threading
import argparse
import time
from flask import Flask
from flask_socketio import SocketIO
from .renderer import PyMDRenderer
from .file_watcher import FileWatcher
from .api_routes import ApiRoutes
from .static_routes import StaticRoutes




class PyMDServer:
    """Live preview server for PyExecMD files"""

    def __init__(self, file_path=None, port=8080, host='localhost'):
        self.file_path = os.path.abspath(file_path) if file_path else None
        self.port = port
        self.host = host
        self.app = Flask(__name__)
        # Use environment variable for secret key, fallback to os.urandom for development
        self.app.config['SECRET_KEY'] = os.environ.get('PYMD_SECRET_KEY', os.urandom(24).hex())
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Set output directory based on the file location
        if self.file_path:
            output_dir = os.path.dirname(self.file_path)
        else:
            output_dir = os.getcwd()
        # Create progress callback for WebSocket status updates
        def progress_callback(step: str, progress: float):
            self.socketio.emit('render_status', {
                'step': step,
                'progress': progress,
                'timestamp': time.time()
            })
        
        self.renderer = PyMDRenderer(output_dir=output_dir, progress_callback=progress_callback)
        self.file_watcher = FileWatcher(self.socketio)
        
        # Setup routes using modular components
        self.api_routes = ApiRoutes(self.app, self.file_path, self.renderer, self.socketio)
        self.static_routes = StaticRoutes(self.app, self.file_path, self.renderer)
        self.setup_socketio()


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
        self.file_watcher.start_watching(self.file_path)

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
            self.file_watcher.stop_watching()


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
