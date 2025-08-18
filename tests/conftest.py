"""
Test configuration and shared fixtures for PyMD tests
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add pymd to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pymd'))

from renderer import PyMDRenderer


class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def create_renderer():
        """Create a fresh PyMDRenderer instance"""
        return PyMDRenderer()
    
    @staticmethod
    def save_test_output(html, test_name):
        """Save test output to file for inspection"""
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{test_name}_output.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(output_file)
    
    @staticmethod
    def extract_content(html):
        """Extract content from HTML between pymd-content div"""
        start_marker = '<div class="pymd-content">'
        end_marker = '</div>'
        start_idx = html.find(start_marker)
        end_idx = html.find(end_marker, start_idx) + len(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            return html[start_idx:end_idx]
        return html
    
    @staticmethod
    def assert_contains(html, expected_content, message="Expected content not found"):
        """Assert that HTML contains expected content"""
        assert expected_content in html, f"{message}: '{expected_content}'"
    
    @staticmethod
    def assert_not_contains(html, unexpected_content, message="Unexpected content found"):
        """Assert that HTML does not contain unexpected content"""
        assert unexpected_content not in html, f"{message}: '{unexpected_content}'"


# Global test utilities instance
test_utils = TestUtils()