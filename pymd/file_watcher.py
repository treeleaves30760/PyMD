"""
File system monitoring utilities for PyMD server
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .renderer import PyMDRenderer


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


class FileWatcher:
    """File watcher utility for monitoring PyMD files"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.observer = None
    
    def start_watching(self, file_path):
        """Start watching the file for changes"""
        if file_path and os.path.exists(file_path):
            event_handler = PyMDFileHandler(self.socketio, file_path)
            self.observer = Observer()
            self.observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
            self.observer.start()
            print(f"Watching file: {file_path}")
        elif file_path:
            print(f"Warning: File {file_path} does not exist")
        else:
            print("No file specified - file watching disabled")
    
    def stop_watching(self):
        """Stop file watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()