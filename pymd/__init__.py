"""
PyExecMD: Python-Powered Markdown

A revolutionary markup language that combines the simplicity of Markdown 
with the full power of Python. Write documents with executable code, 
dynamic content, and beautiful visualizations that update in real-time!
"""

__version__ = "0.1.0"
__author__ = "PyExecMD Team"
__description__ = "Python-Powered Markdown with executable code and dynamic content"

from .renderer import PyMDRenderer, PyMD
from .server import PyMDServer

__all__ = ['PyMDRenderer', 'PyMD', 'PyMDServer']
