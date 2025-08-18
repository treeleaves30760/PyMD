#!/usr/bin/env python3
"""
PyExecMD Command Line Interface
Render PyExecMD files to HTML and start live preview servers
"""

import argparse
import os
import sys
from .renderer import PyMDRenderer
from .server import PyMDServer


def render_command(args):
    """Render a PyExecMD file to HTML"""
    renderer = PyMDRenderer()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist")
        return 1

    try:
        html = renderer.render_file(args.input, args.output)

        if args.output:
            print(f"✅ Successfully rendered '{args.input}' to '{args.output}'")
        else:
            print(html)

        return 0

    except Exception as e:
        print(f"❌ Error rendering file: {e}")
        return 1


def serve_command(args):
    """Start live preview server"""
    file_path = args.file if args.file else None

    if file_path and not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist")
        return 1

    try:
        server = PyMDServer(file_path, args.port, args.host)

        # Display startup information
        print(f"🐍 PyMD Server Started")
        if file_path:
            print(f"📁 File: {file_path}")
        else:
            print(f"📁 File: <blank file>")
        print(f"🌐 Live Preview: http://{args.host}:{args.port}")

        if hasattr(args, 'show') and args.show:
            print(f"🌐 Display: http://{args.host}:{args.port}/display")
        else:
            # Default behavior - show editor URL
            editor_mode = getattr(args, 'mode', 'both')
            print(
                f"✏️ Editor: http://{args.host}:{args.port}/editor/{editor_mode}")

        print("-" * 50)

        server.run(args.debug)
        return 0

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1


def create_command(args):
    """Create a new PyExecMD file with template content"""
    if os.path.exists(args.filename) and not args.force:
        print(
            f"Error: File '{args.filename}' already exists. Use --force to overwrite.")
        return 1

    template_content = '''```
# Welcome to PyExecMD!
pymd.h1("My First PyExecMD Document")

pymd.text("PyExecMD is a Python-based markup language that lets you create documents with executable code!")

pymd.h2("Basic Text")
pymd.text(
    "You can create paragraphs, headings, and formatted text using Python syntax.")

pymd.h2("Code and Data")
pymd.text("Let's create some data and visualize it:")

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x) + np.random.normal(0, 0.1, 100)

pymd.h3("Data Visualization")
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', alpha=0.7, label='Data')
plt.plot(x, np.sin(x), 'r--', label='Sin(x)')
plt.title("Sample Data Visualization")
plt.xlabel("X values")
plt.ylabel("Y values")
plt.legend()
plt.grid(True, alpha=0.3)

pymd.image(plt.gcf(), "A beautiful plot showing sine wave with noise")

pymd.h3("Data Tables")
pymd.text("You can also display tabular data:")

# Create a sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'Age': [25, 30, 35, 28],
    'Score': [95.5, 87.2, 92.8, 89.1],
    'City': ['New York', 'London', 'Tokyo', 'Paris']
})

pymd.table(df)

pymd.h2("Interactive Content")
pymd.text("Since PyExecMD executes Python code, you can create dynamic content:")

# Calculate some statistics
mean_score = df['Score'].mean()
max_score = df['Score'].max()

pymd.text(f"The average score is {mean_score:.1f}")
pymd.text(f"The highest score is {max_score:.1f}")

pymd.h2("Code Blocks")
pymd.text("You can also display code without executing it:")

sample_code = \'\'\'


def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)


print([fibonacci(i) for i in range(10)])
\'\'\'


pymd.code(sample_code, "python")

pymd.h2("Conclusion")
pymd.text("This is just the beginning! PyExecMD combines the simplicity of Markdown with the power of Python.")
pymd.text("Happy coding! 🐍✨")
```'''

    try:
        with open(args.filename, 'w', encoding='utf-8') as f:
            f.write(template_content)

        print(f"✅ Created new PyExecMD file: {args.filename}")
        print(f"💡 To preview: pyexecmd serve {args.filename}")
        print(f"💡 To render: pyexecmd render {args.filename} -o output.html")

        return 0

    except Exception as e:
        print(f"❌ Error creating file: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='PyExecMD - Python-based Markdown with executable code',
        prog='pyexecmd'
    )

    subparsers = parser.add_subparsers(
        dest='command', help='Available commands')

    # Render command
    render_parser = subparsers.add_parser(
        'render', help='Render PyExecMD file to HTML')
    render_parser.add_argument('input', help='Input PyExecMD file')
    render_parser.add_argument(
        '-o', '--output', help='Output HTML file (default: print to stdout)')
    render_parser.set_defaults(func=render_command)

    # Serve command
    serve_parser = subparsers.add_parser(
        'serve', help='Start live preview server')
    serve_parser.add_argument(
        '--file', '-f', help='PyExecMD file to serve (optional)')
    serve_parser.add_argument('-p', '--port', type=int,
                              default=8080, help='Port (default: 8080)')
    serve_parser.add_argument(
        '--host', default='localhost', help='Host (default: localhost)')
    serve_parser.add_argument(
        '--debug', action='store_true', help='Debug mode')
    serve_parser.add_argument(
        '--show', action='store_true', help='Open display website instead of editor')
    serve_parser.add_argument(
        '--mode', choices=['editing', 'viewing', 'both'],
        default='both', help='Editor mode (default: both)')
    serve_parser.set_defaults(func=serve_command)

    # Create command
    create_parser = subparsers.add_parser(
        'create', help='Create new PyExecMD file from template')
    create_parser.add_argument(
        'filename', help='Name of the new PyExecMD file')
    create_parser.add_argument(
        '-f', '--force', action='store_true', help='Overwrite existing file')
    create_parser.set_defaults(func=create_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
