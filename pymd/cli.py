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
    """Render a PyExecMD file to HTML or Markdown"""
    # Set output directory for image saving
    output_dir = os.path.dirname(os.path.abspath(args.output)) if args.output else os.path.dirname(os.path.abspath(args.input))
    renderer = PyMDRenderer(output_dir=output_dir)

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist")
        return 1

    try:
        if args.format == 'markdown':
            # Execute the PyMD content to capture elements and images
            with open(args.input, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # First parse and render to capture all elements and images
            renderer.parse_and_render(content)
            
            # Then generate markdown from the rendered elements
            markdown = renderer.generate_markdown()
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                print(f"✅ Successfully rendered '{args.input}' to '{args.output}' (Markdown)")
                if renderer.captured_images:
                    print(f"📷 Captured {len(renderer.captured_images)} image(s) in '{renderer.images_dir}'")
            else:
                print(markdown)
        else:
            # Render to HTML (default)
            html = renderer.render_file(args.input, args.output)

            if args.output:
                print(f"✅ Successfully rendered '{args.input}' to '{args.output}' (HTML)")
                if renderer.captured_images:
                    print(f"📷 Captured {len(renderer.captured_images)} image(s) in '{renderer.images_dir}'")
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

    template_content = '''# # Welcome to PyMD!
#
# PyMD is a Python-based markup language that lets you create documents with executable code!
#
# ## Basic Features
#
# - **Markdown Syntax**: Use familiar markdown prefixed with `#`
# - **Python Execution**: Run Python code inside ``` blocks
# - **Variable Persistence**: Variables persist across code blocks
# - **Beautiful Output**: Clean, responsive HTML rendering
#
# ## Code and Data
#
# Let's create some data and visualize it:

```
# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x) + np.random.normal(0, 0.1, 100)

print("## Data Visualization")
print("Creating a beautiful sine wave with noise...")
```

```
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', alpha=0.7, label='Data')
plt.plot(x, np.sin(x), 'r--', label='Sin(x)')
plt.title("Sample Data Visualization")
plt.xlabel("X values")
plt.ylabel("Y values")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

# ## Data Tables
#
# You can also display tabular data:

```
# Create a sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'Age': [25, 30, 35, 28],
    'Score': [95.5, 87.2, 92.8, 89.1],
    'City': ['New York', 'London', 'Tokyo', 'Paris']
})

print("### Sample Data Table")
print(df.to_string())
```

# ## Interactive Content
#
# Since PyMD executes Python code, you can create dynamic content:

```
# Calculate some statistics
mean_score = df['Score'].mean()
max_score = df['Score'].max()

print(f"**Average score:** {mean_score:.1f}")
print(f"**Highest score:** {max_score:.1f}")
```

# ## Video Support (NEW!)
#
# PyMD now supports video rendering:

```
# Example video usage (would work with real video files)
print("### Video Rendering Example")
print("```python")
print("# Basic video with caption")
print("pymd.video('my_video.mp4', 'Demo video caption')")
print("")
print("# Customized video")
print("pymd.video('demo.mp4', 'Demo', width='80%', autoplay=True)")
print("```")
```

# ## Conclusion
#
# This is just the beginning! PyMD combines the simplicity of Markdown with the power of Python.
#
# **Happy coding!** 🐍✨
#
# Try modifying the code above and watch the results update in real-time!'''

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
        'render', help='Render PyExecMD file to HTML or Markdown')
    render_parser.add_argument('input', help='Input PyExecMD file')
    render_parser.add_argument(
        '-o', '--output', help='Output file (default: print to stdout)')
    render_parser.add_argument(
        '-f', '--format', choices=['html', 'markdown'], default='html',
        help='Output format (default: html)')
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
