# PyMD: Python-Powered Markdown

PyMD is a revolutionary markup language that combines familiar markdown syntax with the full power of Python execution. Write beautiful documents using standard markdown headers, lists, and text, while executing Python code in clearly separated code blocks!

## ✨ Features

- **📝 Markdown Syntax**: Use familiar markdown headers (#), lists (-), and plain text
- **🐍 Dual Code Block Types**: 
  - **``` (3 backticks)**: Execute Python code and show output
  - **```` (4 backticks)**: Display code with syntax highlighting only
- **🔗 Variable Persistence**: Variables persist across code blocks in the same document
- **🔴 Live Preview**: Real-time rendering with auto-refresh as you edit
- **📊 Rich Visualizations**: Built-in support for matplotlib, pandas, and other data science libraries
- **🧮 Dynamic Content**: Execute Python code and display results inline
- **📱 Beautiful Output**: Clean, responsive HTML with modern styling
- **⚡ Fast Rendering**: Efficient parsing and rendering engine
- **🔄 Auto-Refresh**: Changes reflect immediately in the live preview
- **💬 Smart Comments**: Display blocks use `//` for cleaner code presentation
- **📄 Export Options**: Export to HTML or standard Markdown formats
- **🖱️ One-Click Export**: Export buttons in the web editor interface

## 🚀 Quick Start

### Installation

**Option 1: Install from PyPI (Recommended)**

```bash
pip install pyexecmd
```

<details>

<summary> Option 2: Install from source </summary>

1. **Clone the repository:**

   ```bash
   git clone https://www.github.com/treeleaves30760/PyMD
   cd PyMD
   ```

2. **Install in development mode:**

   ```bash
   pip install -e .
   ```

</details>

## Usage

### For Conda Users (Recommended Development Setup)

If you're using conda for development, first activate the environment:

```bash
# Initialize conda and activate environment
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD

# Verify activation
python --version && which python
```

Then use standard Python commands:

```bash
# Create a new PyMD document
python -m pymd.cli create my_document.pymd

# Start live preview with web editor
python -m pymd.cli serve --file my_document.pymd --port 8080

# Render to HTML
python -m pymd.cli render my_document.pymd -o output.html

# Render to Markdown (NEW!)
python -m pymd.cli render my_document.pymd -f markdown -o output.md
```

### For PyPI Installation

1. **Create a new PyMD document:**

   ```bash
   pyexecmd create my_document.pymd
   ```

2. **Start live preview with web editor:**

   ```bash
   pyexecmd serve --file my_document.pymd --port 8080
   ```

   Then open <http://localhost:8080/editor> in your browser for the full editor experience, or <http://localhost:8080> for display-only view.

   > **Note for macOS users:** Port 5000 is often used by AirPlay. Use `--port 8000` or another port to avoid conflicts.

3. **Export Options:**

   ```bash
   # Render to HTML
   pyexecmd render my_document.pymd -o output.html
   
   # Render to Markdown (NEW!)
   pyexecmd render my_document.pymd -f markdown -o output.md
   ```

### Web Editor Features

The web editor (available at `/editor`) includes:

- **📝 Split-view editing**: Side-by-side editor and live preview
- **🖱️ One-click export**: Export HTML and Markdown buttons in the interface
- **⚡ Live rendering**: Ctrl+S to execute code and update preview
- **💾 File management**: Save and download your documents
- **🎨 Syntax highlighting**: Python syntax highlighting with PyMD-specific features

## 📝 PyMD Syntax

PyMD combines familiar markdown syntax with Python code execution:

### Markdown Content (Outside Code Blocks)

**Headers:**

```markdown
# Main Title
## Section Title
### Subsection Title
```

**Lists:**

```markdown
- Unordered list item
- Another unordered item

1. Ordered list item
2. Another ordered item
```

**Plain Text:**

```markdown
This is a paragraph of regular text.
You can write multiple paragraphs easily.
```

**Comments:**

```markdown
// This is a comment and will be ignored
```

### Python Code Blocks

**Simple Code Execution:**

````markdown
```
x = 42
y = "Hello, PyMD!"
print(f"{y} The answer is {x}")
```
````

**Data Analysis:**

````markdown
```
import pandas as pd
import numpy as np

# Create sample data

data = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Score': [95, 87, 92]
})

print("Sample Data:")
pymd.table(data)
```
````

**Visualizations:**

````markdown
```
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 5))
plt.plot(x, y, 'b-', linewidth=2)
plt.title("Sine Wave Visualization")
plt.grid(True)

pymd.image(plt.gcf(), "Beautiful sine wave")
```
````

**Interactive Input with Mock Values:**

````markdown
```
# Get user input (with mock values for non-interactive execution)
name = input("Enter your name: ") # input: Alice
age = input("Enter your age: ") # input: 25

# Use the input values
pymd.h2(f"Welcome, {name}!")
pymd.text(f"You are {age} years old.")

# Input without mock value defaults to empty string
optional_input = input("Optional comment: ")
if optional_input:
    print(f"Comment: {optional_input}")
else:
    print("No comment provided")
```
````

**Code Display (Method 1 - Using pymd.code()):**

````markdown
```
sample_code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
'''

pymd.code(sample_code, "python")
print(f"Factorial of 5 is: {factorial(5)}")
```
````

**Code Display (Method 2 - Using four backticks):**

`````markdown
````
def factorial(n):
    // Base case
    if n <= 1:
        return 1
    // Recursive case
    return n * factorial(n-1)

// Example usage (not executed)
result = factorial(5)
````
`````

### Key Features

- **Variable Persistence**: Variables defined in one code block are available in subsequent blocks
- **Mixed Content**: Alternate between markdown content and Python code seamlessly  
- **Two Code Block Types**: 
  - **Three backticks (```)**: Execute Python code and show output
  - **Four backticks (````)**: Display code with syntax highlighting (no execution)
- **Interactive Input Support**: Use `input()` with mock values for non-interactive execution
- **Clean Separation**: Clear visual distinction between documentation and executable code
- **Rich Output**: Code execution results are displayed with beautiful formatting
- **Smart Comment Styling**: Display blocks use `//` comments for cleaner presentation

### Input Mock System

PyMD supports interactive input through a mock system that allows documents to be rendered without user interaction:

- **With Mock Value**: `input("Prompt: ") # input: mock_value` - Returns "mock_value"
- **Without Mock Value**: `input("Prompt: ")` - Returns empty string ("")
- **Multiple Inputs**: Each `input()` call uses mock values in sequence
- **Silent Execution**: Mock inputs don't produce console output, only the actual code results are shown

## 📁 Project Structure

```file
PyMD/
├── pymd/                   # Main package directory
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   ├── renderer.py        # Core rendering engine
│   └── server.py          # Live preview server
├── example.pymd           # Example PyMD document
├── pyproject.toml         # Package configuration
├── MANIFEST.in            # Additional files to include
├── LICENSE                # MIT License
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🛠️ API Reference

### Markdown Syntax (Outside Code Blocks)

- `# Header` - Create level 1 heading
- `## Header` - Create level 2 heading  
- `### Header` - Create level 3 heading
- `- Item` - Unordered list item
- `1. Item` - Ordered list item
- `Plain text` - Regular paragraph text
- `// Comment` - Comments (ignored during rendering)

### PyMD Functions (Inside Code Blocks)

- `pymd.h1(text)` - Create level 1 heading programmatically
- `pymd.h2(text)` - Create level 2 heading programmatically
- `pymd.h3(text)` - Create level 3 heading programmatically
- `pymd.text(content)` - Create paragraph text programmatically
- `pymd.code(content, language)` - Display code block with syntax highlighting
- `pymd.image(plot_obj, caption)` - Render matplotlib plots
- `pymd.table(data)` - Render pandas DataFrames or tables

### CLI Commands

```bash
# Create new PyExecMD file from template
pyexecmd create <filename> [--force]

# Start live preview server with web editor
pyexecmd serve [--file FILE] [--port PORT] [--host HOST] [--debug] [--mode {editing,viewing,both}]

# Render PyExecMD to HTML (default)
pyexecmd render <input> [-o OUTPUT] [-f html]

# Render PyExecMD to Markdown (NEW!)
pyexecmd render <input> [-o OUTPUT] -f markdown

# Render options
pyexecmd render <input> --format {html,markdown} --output <filename>
```

#### Command Examples

```bash
# Conda development setup
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD

# Create and serve
python -m pymd.cli create tutorial.pymd
python -m pymd.cli serve --file tutorial.pymd --port 8080

# Export to different formats
python -m pymd.cli render tutorial.pymd -o tutorial.html          # HTML export
python -m pymd.cli render tutorial.pymd -f markdown -o tutorial.md # Markdown export
python -m pymd.cli render tutorial.pymd -f markdown               # Print to stdout

# PyPI installation
pyexecmd create tutorial.pymd
pyexecmd serve --file tutorial.pymd --port 8080
pyexecmd render tutorial.pymd -f markdown -o tutorial.md
```

## 🎯 Use Cases

- **📊 Data Science Reports**: Combine analysis, visualizations, and explanations
- **📚 Interactive Documentation**: Living documents that update with code changes
- **🎓 Educational Materials**: Tutorials with executable examples
- **📈 Dashboard Reports**: Dynamic reports with real-time data
- **🔬 Research Papers**: Academic papers with reproducible results

## 🌟 Examples

Check out `example.pymd` for a comprehensive demonstration of PyMD features, including:

- Markdown-style headers, lists, and text
- Python code execution with output
- Beautiful data visualizations with matplotlib
- Dynamic calculations and variable persistence
- Interactive tables with pandas
- Mixed content workflow
- Real-time preview updates
- Export functionality (HTML and Markdown)

### Export Examples

**Export to HTML for presentations and sharing:**
```bash
python -m pymd.cli render example.pymd -o presentation.html
```

**Export to Markdown for documentation and version control:**
```bash
python -m pymd.cli render example.pymd -f markdown -o documentation.md
```

**Web Editor Export:**
1. Open `http://localhost:8080/editor` in your browser
2. Edit your PyMD content
3. Click **📄 Export HTML** for a complete HTML file
4. Click **📝 Export MD** for a clean Markdown file

The exported Markdown maintains the structure while converting PyMD-specific syntax to standard Markdown format, making it compatible with GitHub, GitLab, and other Markdown renderers.

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License.

---
