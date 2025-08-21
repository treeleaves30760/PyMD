# PyMD: Python-Powered Markdown

PyMD is a revolutionary markup language that creates **executable Python files** that also render beautifully as markdown documents. All markdown content is prefixed with `#` (making it Python comments), while code blocks contain regular executable Python code that prints markdown during rendering.

## ✨ Features

- **🐍 Executable Python Files**: Files can be run directly with `python filename.pymd`
- **📝 Commented Markdown**: All markdown content is prefixed with `#` (Python comments)
- **🖨️ Print-to-Markdown**: Python `print()` statements output markdown content during rendering
- **🎨 Dual Code Block Types**: 
  - **``` (3 backticks)**: Execute Python code and process print output as markdown
  - **```` (4 backticks)**: Display code with syntax highlighting only
- **🔗 Variable Persistence**: Variables persist across code blocks in the same document
- **🔴 Live Preview**: Real-time rendering with auto-refresh as you edit
- **📊 Rich Visualizations**: Built-in support for matplotlib, pandas, and other data science libraries
- **🧮 Dynamic Content**: Execute Python code and display results inline
- **📱 Beautiful Output**: Clean, responsive HTML with modern styling
- **⚡ Fast Rendering**: Efficient parsing and rendering engine with caching
- **🔄 Auto-Refresh**: Changes reflect immediately in the live preview
- **💬 Smart Comments**: Display blocks use `//` for cleaner code presentation
- **📄 Export Options**: Export to HTML or standard Markdown formats
- **🖱️ One-Click Export**: Export buttons in the web editor interface
- **↔️ Backward Compatible**: Supports both executable and legacy syntax

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

# Render to Markdown
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
   
   # Render to Markdown
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

PyMD files are **executable Python scripts** where:
- **Markdown content** is prefixed with `#` (Python comments)
- **Code blocks** contain regular Python code that prints markdown
- **Print output** becomes rendered markdown content during PyMD rendering
- **Files run as Python** and render as beautiful documents

### Basic Structure

```python
# # This is a markdown header
# 
# This is regular markdown text with **bold** formatting.
#
# - This is a list item
# - Another list item
#
# ```
# This is a comment in the code block
print("## This becomes a rendered H2 header")
print("Regular text from Python print statement")
print("- **Dynamic list item** with variables")
# ```
#
# More markdown content here...
```

### 📝 Markdown Content (Prefixed with `#`)

All markdown content is prefixed with `#` making it Python comments:

**Headers:**

```python
# # Main Title
# ## Section Title  
# ### Subsection Title
```

**Lists:**

```python
# - Unordered list item
# - Another unordered item
#
# 1. Ordered list item
# 2. Another ordered item
```

**Plain Text:**

```python
# This is a paragraph of regular text.
# You can write multiple paragraphs easily.
```

**Comments:**

```python
# // This is a comment and will be ignored during rendering
```

### 🐍 Code Blocks (Executable Python)

Code blocks markers are prefixed with `#`, but the code inside is regular Python:

**Executable Code Block:**

```python
# ```
# This is a comment inside the code block
x = 42
y = "Hello, PyMD!"
print(f"## {y} The answer is {x}")  # This becomes an H2 header
print(f"The calculation result: **{x * 2}**")  # Bold text
# ```
```

**Display-Only Code Block:**

```python
# ````
# def example_function():
#     // This code is displayed but not executed
#     return "example"
# ````
```

### 📊 Complete Example

**Data Analysis with Print-to-Markdown:**

```python
# # Data Analysis Report
#
# Let's analyze some sample data:
#
# ```
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
data = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Score': [95, 87, 92],
    'Department': ['Engineering', 'Sales', 'Marketing']
})

print("## Sample Employee Data")
print(f"**Total employees:** {len(data)}")
print(f"**Average score:** {data['Score'].mean():.1f}")
print()
print("### Individual Scores:")
for _, row in data.iterrows():
    print(f"- **{row['Name']}** ({row['Department']}): {row['Score']}")
# ```
#
# ## Analysis Results
#
# The data shows interesting patterns in employee performance.
```

### 💬 Interactive Input with Mock Values

```python
# ## User Profile Generator
#
# ```
# Get user input (with mock values for non-interactive execution)
name = input("Enter your name: ") # input: Alice
age = input("Enter your age: ") # input: 25

print(f"### Welcome, {name}!")
print(f"**Age:** {age} years old")
print(f"**Birth year:** {2025 - int(age)}")

# Input without mock value defaults to empty string
optional_input = input("Optional comment: ")
if optional_input:
    print(f"**Comment:** {optional_input}")
else:
    print("*No comment provided*")
# ```
```

### 🎨 Display-Only Code Blocks

Use four backticks for code that displays but doesn't execute:

```python
# ## Algorithm Reference
#
# Here's the algorithm we'll implement:
#
# ````
# def factorial(n):
#     // Base case
#     if n <= 1:
#         return 1
#     // Recursive case  
#     return n * factorial(n-1)
# 
# // Example usage (this won't execute)
# result = factorial(5)
# ````
#
# Now let's implement it:
#
# ```
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

result = factorial(5)
print(f"## Factorial Results")
print(f"Factorial of 5 is: **{result}**")
# ```
```

### 🔑 Key Concepts

- **🐍 Executable Python**: Files run directly with `python filename.pymd`
- **📝 Commented Markdown**: All markdown content prefixed with `#` (Python comments)
- **🖨️ Print-to-Markdown**: Use `print()` to output markdown that gets rendered
- **🔗 Variable Persistence**: Variables persist across all code in the file
- **📦 Two Code Block Types**: 
  - **``` (3 backticks)**: Execute Python and process print output as markdown
  - **```` (4 backticks)**: Display code with syntax highlighting (no execution)
- **💬 Interactive Input**: Use `input()` with mock values for non-interactive execution
- **🎨 Clean Rendering**: `#` prefixes hidden during HTML/Markdown export
- **📊 Rich Output**: Print statements can output headers, lists, tables, even HTML
- **💡 Smart Comments**: Use `//` in display blocks for cleaner presentation
- **↔️ Dual Purpose**: Same file serves as Python script AND beautiful document

## 🛠️ Syntax Reference

### 📝 Markdown Content (All prefixed with `#`)

**Headers:**
```python
# # Level 1 Header
# ## Level 2 Header  
# ### Level 3 Header
```

**Lists:**
```python
# - Unordered list item
# - Another item
# 
# 1. Ordered list item
# 2. Another ordered item
```

**Text and Formatting:**
```python
# Regular paragraph text.
# 
# Text with **bold** and *italic* formatting.
# 
# // This is a comment (ignored during rendering)
```

### 🐍 Code Blocks (Regular Python)

**Executable Code Block:**
```python
# ```
# Comments inside code blocks (optional)
variable = "Hello World"
print(f"## {variable}")  # Becomes H2 header in output
print(f"Current value: **{variable}**")  # Bold text in output
print("- First result")   # List item in output
print("- Second result")  # Another list item
# ```
```

**Display-Only Code Block:**
```python
# ````
# def example_function():
#     // This is displayed but not executed
#     // Use // for comments in display blocks
#     return "example"
# ````
```

### 🖨️ Print-to-Markdown

Use `print()` statements to output markdown content:

```python
# ```
data = [1, 2, 3, 4, 5]
print("## Analysis Results")  # H2 header
print(f"**Count:** {len(data)}")  # Bold text
print(f"**Sum:** {sum(data)}")    # Bold text
print("### Detailed Breakdown:")   # H3 header
for i, value in enumerate(data, 1):
    print(f"{i}. Item value: **{value}**")  # Ordered list
# ```
```

### 💡 Best Practices

- **File Structure**: Start with `# # Title` as the main header
- **Code Comments**: Use `# Comments` inside code blocks for Python comments
- **Markdown Output**: Use `print()` to generate headers, lists, and formatted text
- **Display Code**: Use `# ````...# ``````` for code examples that shouldn't execute
- **Variables**: Define variables in code blocks and reference them in print statements
- **Clean Syntax**: Keep markdown content in `#` prefixed sections, code in blocks

### CLI Commands

```bash
# Create new PyExecMD file from template
pyexecmd create <filename> [--force]

# Start live preview server with web editor
pyexecmd serve [--file FILE] [--port PORT] [--host HOST] [--debug] [--mode {editing,viewing,both}]

# Render PyExecMD to HTML (default)
pyexecmd render <input> [-o OUTPUT] [-f html]

# Render PyExecMD to Markdown
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

## 🌟 Examples

### Simple Example (`example-simple.pymd`)

```python
# # Simple PyMD Example
#
# This demonstrates basic syntax:
#
# ```
# This is a comment in Python
print("## Hello from PyMD!")
a = 20
b = 30
print(f"The answer is: **{a + b}**")
# ```
#
# - This is a markdown list item
# 1. This is an ordered list item
```

**Usage:**
- **Run as Python**: `python example-simple.pymd`
- **Render to HTML**: `python -m pymd.cli render example-simple.pymd -o output.html`

### Comprehensive Example (`example.pymd`)

Check out `example.pymd` for a full demonstration including:

- **Executable Python file** with `#` prefixed markdown content
- **Data analysis** with pandas and numpy
- **Print-to-markdown** for dynamic content generation
- **Variable persistence** across code blocks
- **Interactive input** with mock values
- **Mixed workflow** of documentation and executable code
- **Export functionality** (HTML and Markdown)

### Complex Example (`example-complex.pymd`)

Advanced features including:
- **Machine learning model loading**
- **Error handling and device management**
- **AI text generation integration**
- **Complex data processing workflows**

### 🚀 Quick Example Usage

**1. Run as executable Python:**
```bash
python example.pymd
```

**2. Render as beautiful HTML:**
```bash
python -m pymd.cli render example.pymd -o presentation.html
```

**3. Export to standard Markdown:**
```bash
python -m pymd.cli render example.pymd -f markdown -o documentation.md
```

**4. Live editor with preview:**
```bash
python -m pymd.cli serve --file example.pymd --port 8080
# Open http://localhost:8080/editor in your browser
```

**How Export Works:**
- **HTML Export**: Full rendering with executed code output and styled markdown
- **Markdown Export**: Removes `#` prefixes and converts to standard markdown
- **Source Files**: Remain executable Python scripts with commented markdown
- **Compatibility**: Exported markdown works with GitHub, GitLab, and other renderers

**Web Editor Features:**
1. **Live Editing**: Open `http://localhost:8080/editor` in your browser
2. **Syntax Highlighting**: `#` prefixed markdown and Python code blocks
3. **Live Preview**: See rendered output in real-time
4. **Export Options**: Click **📄 Export HTML** or **📝 Export MD**
5. **File Execution**: Use Ctrl+S to execute code and update preview

## 🎯 Use Cases

- **📊 Data Science Reports**: Python scripts that execute analysis AND generate beautiful reports
- **📚 Executable Documentation**: Documentation that actually runs and validates itself
- **🎓 Interactive Tutorials**: Learning materials that students can execute and modify
- **📈 Living Dashboards**: Python scripts that generate dynamic visual reports
- **🔬 Reproducible Research**: Research papers where the code actually runs
- **🧪 Literate Programming**: Self-documenting code through executable markdown comments
- **📋 Technical Specifications**: Specs that include working code examples
- **🤖 AI/ML Workflows**: Machine learning pipelines with embedded documentation

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

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License.

---