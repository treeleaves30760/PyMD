"""
Static file serving routes for PyMD server
"""

import os
import json
from flask import render_template_string, send_from_directory
from .templates import DISPLAY_TEMPLATE, ERROR_TEMPLATE, get_editor_template


class StaticRoutes:
    """Handles static file serving and page rendering"""
    
    def __init__(self, app, file_path, renderer):
        self.app = app
        self.file_path = file_path
        self.renderer = renderer
        self.setup_routes()
    
    def setup_routes(self):
        """Setup static file serving routes"""

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

        @self.app.route('/editor/videos/<path:filename>')
        def serve_videos_editor(filename):
            """Serve video files from the videos directory (editor path)"""
            return self._serve_media_file(filename, 'videos')

        @self.app.route('/editor/images/<path:filename>')
        def serve_images_editor(filename):
            """Serve image files from the images directory (editor path)"""
            return self._serve_media_file(filename, 'images')

        @self.app.route('/videos/<path:filename>')
        def serve_videos_root(filename):
            """Serve video files from the videos directory (root path)"""
            return self._serve_media_file(filename, 'videos')

        @self.app.route('/images/<path:filename>')
        def serve_images_root(filename):
            """Serve image files from the images directory (root path)"""
            return self._serve_media_file(filename, 'images')

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

                # Extract content from full HTML
                start_marker = '<div class="pymd-content">'
                start_idx = html.find(start_marker)
                end_body_idx = html.rfind('</body>')
                if start_idx != -1 and end_body_idx != -1 and end_body_idx > start_idx:
                    content = html[start_idx:end_body_idx]
                else:
                    content = '<div class="pymd-content"><p>No content rendered</p></div>'

                return render_template_string(DISPLAY_TEMPLATE,
                                              filename=os.path.basename(self.file_path) if self.file_path else "Blank File",
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
    
    def _serve_media_file(self, filename, media_type):
        """Generic helper to serve media files (images/videos)"""
        try:
            # Get the directory where the .pymd file is located
            if self.file_path:
                base_dir = os.path.dirname(self.file_path)
            else:
                base_dir = os.getcwd()
            media_dir = os.path.join(base_dir, media_type)
            
            # Debug logging
            print(f"Serving {media_type[:-1]}: {filename} from {media_dir}")
            
            # Check if file exists
            file_path = os.path.join(media_dir, filename)
            if not os.path.exists(file_path):
                print(f"{media_type.capitalize()[:-1]} file not found: {file_path}")
                return f"{media_type.capitalize()[:-1]} file not found: {file_path}", 404
            
            return send_from_directory(media_dir, filename)
        except Exception as e:
            print(f"Error serving {media_type[:-1]} {filename}: {str(e)}")
            return f"{media_type.capitalize()[:-1]} not found: {str(e)}", 404