"""
Video handling utilities for PyMD renderer
"""

import os
import uuid
import shutil
from typing import Dict


class VideoHandler:
    """Handles video processing, saving, and management for PyMD documents"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.videos_dir = os.path.join(output_dir, 'videos')
        self.video_counter = 0
        self.captured_videos = []  # Store info about captured videos
    
    def _ensure_videos_dir(self):
        """Ensure the videos directory exists"""
        if not os.path.exists(self.videos_dir):
            os.makedirs(self.videos_dir, exist_ok=True)
    
    def save_video_to_file(self, video_path: str, filename: str = None, caption: str = '') -> Dict[str, str]:
        """Copy video file to videos directory and return video info"""
        self._ensure_videos_dir()

        # Check if the video_path is already in the videos directory
        abs_video_path = os.path.abspath(video_path)
        abs_videos_dir = os.path.abspath(self.videos_dir)

        if abs_video_path.startswith(abs_videos_dir + os.sep):
            # Video is already in the videos directory, no need to copy
            filename = os.path.basename(video_path)
            file_path = abs_video_path
            relative_path = f"videos/{filename}"

            video_info = {
                'filename': filename,
                'file_path': file_path,
                'relative_path': relative_path,
                'original_path': video_path,
                'caption': caption
            }

            self.captured_videos.append(video_info)
            return video_info

        if filename is None:
            # Try to preserve the original filename from the video_path
            original_filename = os.path.basename(video_path)
            if original_filename and not original_filename.startswith('.'):
                # Use the original filename if it's valid
                filename = original_filename
                # Check if filename already exists and make it unique if necessary
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(self.videos_dir, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
            else:
                # Fall back to generating a unique filename
                self.video_counter += 1
                # Get original file extension
                _, ext = os.path.splitext(video_path)
                if not ext:
                    ext = '.mp4'  # default extension
                filename = f"video_{self.video_counter}_{uuid.uuid4().hex[:8]}{ext}"

        file_path = os.path.join(self.videos_dir, filename)
        relative_path = f"videos/{filename}"

        try:
            # Copy video file to videos directory
            shutil.copy2(video_path, file_path)
        except Exception as e:
            raise Exception(f"Failed to copy video file: {str(e)}")

        video_info = {
            'filename': filename,
            'file_path': file_path,
            'relative_path': relative_path,
            'original_path': video_path,
            'caption': caption
        }

        self.captured_videos.append(video_info)
        return video_info
    
    def render_video(self, video_path: str, caption: str = '', width: str = '100%', 
                    height: str = 'auto', controls: bool = True, autoplay: bool = False, 
                    loop: bool = False) -> str:
        """Render video from file path"""
        try:
            # Check if video file exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")

            # Save video to videos directory and get info
            video_info = self.save_video_to_file(video_path, caption=caption)

            # Build video attributes
            video_attrs = []
            if controls:
                video_attrs.append('controls')
            if autoplay:
                video_attrs.append('autoplay')
            if loop:
                video_attrs.append('loop')

            attrs_str = ' '.join(video_attrs)
            if attrs_str:
                attrs_str = ' ' + attrs_str

            # Determine the correct MIME type based on file extension
            _, ext = os.path.splitext(video_info['filename'])
            ext = ext.lower()

            if ext == '.gif':
                # For GIF files, use an img tag instead of video tag since browsers handle animated GIFs as images
                html = f'''
                <div class="video-container">
                    <img src="{video_info['relative_path']}" 
                         alt="{caption}" 
                         width="{width}" 
                         style="height: {height}; max-width: 100%; border-radius: 6px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
                    {f'<p class="video-caption">{caption}</p>' if caption else ''}
                </div>
                '''
            else:
                # For actual video files, determine the correct MIME type
                mime_type = 'video/mp4'  # default
                if ext == '.webm':
                    mime_type = 'video/webm'
                elif ext == '.ogg':
                    mime_type = 'video/ogg'
                elif ext == '.mov':
                    mime_type = 'video/quicktime'
                elif ext == '.avi':
                    mime_type = 'video/x-msvideo'

                html = f'''
                <div class="video-container">
                    <video width="{width}" height="{height}"{attrs_str}>
                        <source src="{video_info['relative_path']}" type="{mime_type}">
                        Your browser does not support the video tag.
                    </video>
                    {f'<p class="video-caption">{caption}</p>' if caption else ''}
                </div>
                '''

            return html, video_info

        except Exception as e:
            error_html = f'<p class="error">Error rendering video: {str(e)}</p>'
            return error_html, f'Error: {str(e)}'