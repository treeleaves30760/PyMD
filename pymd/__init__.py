"""
PyExecMD: Python-Powered Markdown

A revolutionary markup language that combines the simplicity of Markdown 
with the full power of Python. Write documents with executable code, 
dynamic content, and beautiful visualizations that update in real-time!
"""

__version__ = "0.1.9"
__author__ = "PyExecMD Team"
__description__ = "Python-Powered Markdown with executable code and dynamic content"

from .renderer import PyMDRenderer, PyMD
from .server import PyMDServer

# Create a default global pymd object for direct Python execution
# This provides basic functionality when .pymd files are run directly


class DefaultPyMD(PyMD):
    """Default PyMD object for direct Python execution with print fallback"""

    def __init__(self):
        super().__init__(renderer=None)

    def code(self, content: str, language: str = 'python') -> str:
        """Print code block content for direct execution"""
        print(f"```{language}")
        print(content)
        print("```")
        return content


# Create global pymd instance for direct execution
_default_pymd = DefaultPyMD()

# Make all methods available at module level for direct access


def code(content: str, language: str = 'python') -> str:
    """Print code block content for direct execution"""
    return _default_pymd.code(content, language)


def h1(text: str) -> str:
    """Create a level 1 heading"""
    return _default_pymd.h1(text)


def h2(text: str) -> str:
    """Create a level 2 heading"""
    return _default_pymd.h2(text)


def h3(text: str) -> str:
    """Create a level 3 heading"""
    return _default_pymd.h3(text)


def text(content: str) -> str:
    """Create paragraph text with bold text support"""
    return _default_pymd.text(content)


def image(image_source=None, caption: str = '') -> str:
    """Render matplotlib plot, image file path, or other image objects"""
    return _default_pymd.image(image_source, caption)


def video(video_path: str, caption: str = '', width: str = '100%',
          height: str = 'auto', controls: bool = True, autoplay: bool = False,
          loop: bool = False) -> str:
    """Render video from file path or video data"""
    return _default_pymd.video(video_path, caption, width, height, controls, autoplay, loop)


def table(data) -> str:
    """Render pandas DataFrame or other tabular data"""
    return _default_pymd.table(data)


__all__ = ['PyMDRenderer', 'PyMD', 'PyMDServer', 'code',
           'h1', 'h2', 'h3', 'text', 'image', 'video', 'table']
