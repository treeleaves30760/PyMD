"""
Image handling utilities for PyMD renderer
"""

import io
import base64
import os
import uuid
import shutil
from typing import Dict, Optional


class ImageHandler:
    """Handles image processing, saving, and management for PyMD documents"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, 'images')
        self.image_counter = 0
        self.captured_images = []  # Store info about captured images
    
    def _ensure_images_dir(self):
        """Ensure the images directory exists"""
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir, exist_ok=True)
    
    def save_figure_to_file(self, fig, filename: str = None, caption: str = '') -> Dict[str, str]:
        """Save matplotlib figure to file and return image info"""
        self._ensure_images_dir()

        if filename is None:
            self.image_counter += 1
            filename = f"plot_{self.image_counter}_{uuid.uuid4().hex[:8]}.png"

        file_path = os.path.join(self.images_dir, filename)
        relative_path = f"images/{filename}"

        # Save figure to file
        fig.savefig(file_path, format='png', bbox_inches='tight', dpi=150)

        # Also create base64 for fallback
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

        image_info = {
            'filename': filename,
            'file_path': file_path,
            'relative_path': relative_path,
            'base64': img_base64,
            'caption': caption
        }

        self.captured_images.append(image_info)
        return image_info
    
    def save_image_file_to_images_dir(self, image_path: str, filename: str = None, caption: str = '') -> Dict[str, str]:
        """Copy image file to images directory and return image info"""
        self._ensure_images_dir()

        if filename is None:
            # Try to preserve the original filename from the image_path
            original_filename = os.path.basename(image_path)
            if original_filename and not original_filename.startswith('.'):
                # Use the original filename if it's valid
                filename = original_filename
                # Check if filename already exists and make it unique if necessary
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(self.images_dir, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
            else:
                # Fall back to generating a unique filename
                self.image_counter += 1
                _, ext = os.path.splitext(image_path)
                if not ext:
                    ext = '.png'  # default extension
                filename = f"image_{self.image_counter}_{uuid.uuid4().hex[:8]}{ext}"

        file_path = os.path.join(self.images_dir, filename)
        relative_path = f"images/{filename}"

        try:
            # Copy image file to images directory
            shutil.copy2(image_path, file_path)
        except Exception as e:
            raise Exception(f"Failed to copy image file: {str(e)}")

        # Also create base64 for fallback
        try:
            with open(file_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
        except Exception:
            img_base64 = ''  # If base64 encoding fails, use empty string

        image_info = {
            'filename': filename,
            'file_path': file_path,
            'relative_path': relative_path,
            'original_path': image_path,
            'base64': img_base64,
            'caption': caption
        }

        self.captured_images.append(image_info)
        return image_info
    
    def render_image_from_file(self, image_path: str, caption: str = '') -> str:
        """Render image from file path"""
        try:
            # Check if image file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Copy image to images directory and get info
            image_info = self.save_image_file_to_images_dir(image_path, caption=caption)

            html = f'''
            <div class="image-container">
                <img src="{image_info['relative_path']}" 
                     alt="{caption}" 
                     style="max-width: 100%; height: auto;"
                     onerror="this.onerror=null; this.src='data:image/png;base64,{image_info['base64']}';">
                {f'<p class="image-caption">{caption}</p>' if caption else ''}
            </div>
            '''
            return html, image_info

        except Exception as e:
            error_html = f'<p class="error">Error rendering image: {str(e)}</p>'
            return error_html, f'Error: {str(e)}'