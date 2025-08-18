# PyExecMD: Python-Powered Markdown

PyExecMD is a revolutionary markup language that combines the simplicity of Markdown with the full power of Python. Write documents with executable code, dynamic content, and beautiful visualizations that update in real-time!

## ✨ Features

- **🐍 Python-Based Syntax**: Write markup using familiar Python function calls
- **🔴 Live Preview**: Real-time rendering with auto-refresh as you edit
- **📊 Rich Visualizations**: Built-in support for matplotlib, pandas, and other data science libraries
- **🧮 Dynamic Content**: Execute Python code and display results inline
- **📱 Beautiful Output**: Clean, responsive HTML with modern styling
- **⚡ Fast Rendering**: Efficient parsing and rendering engine
- **🔄 Auto-Refresh**: Changes reflect immediately in the live preview

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

1. **Create a new PyExecMD document:**

   ```bash
   pyexecmd create my_document.pymd
   ```

2. **Start live preview:**

   ```bash
   pyexecmd serve my_document.pymd --port 8000
   ```

   Then open <http://localhost:8000> in your browser

   > **Note for macOS users:** Port 5000 is often used by AirPlay. Use `--port 8000` or another port to avoid conflicts.

3. **Render to HTML:**

   ```bash
   pyexecmd render my_document.pymd -o output.html
   ```

## 📝 PyExecMD Syntax

PyExecMD uses Python function calls to create content:

### Headings

```python
pymd.h1("Main Title")
pymd.h2("Section Title")
pymd.h3("Subsection Title")
```

### Text

```python
pymd.text("This is a paragraph of text.")
pymd.text("You can write **bold** and *italic* text too!")
```

### Code Blocks

```python
code_sample = '''
def hello_world():
    print("Hello, PyExecMD!")
'''
pymd.code(code_sample, "python")
```

### Images and Plots

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title("Sine Wave")

pymd.image(plt.gcf(), "Beautiful sine wave visualization")
```

### Tables

```python
import pandas as pd

df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Score': [95, 87, 92]
})

pymd.table(df)
```

## 📁 Project Structure

```
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

### PyExecMD Class Methods

- `pymd.h1(text)` - Create level 1 heading
- `pymd.h2(text)` - Create level 2 heading
- `pymd.h3(text)` - Create level 3 heading
- `pymd.text(content)` - Create paragraph text
- `pymd.code(content, language)` - Create code block
- `pymd.image(plot_obj, caption)` - Render matplotlib plots
- `pymd.table(data)` - Render pandas DataFrames or tables

### CLI Commands

```bash
# Create new PyExecMD file from template
pyexecmd create <filename> [--force]

# Start live preview server
pyexecmd serve <file> [--port PORT] [--host HOST] [--debug]

# Render PyExecMD to HTML
pyexecmd render <input> [-o OUTPUT]
```

## 🎯 Use Cases

- **📊 Data Science Reports**: Combine analysis, visualizations, and explanations
- **📚 Interactive Documentation**: Living documents that update with code changes
- **🎓 Educational Materials**: Tutorials with executable examples
- **📈 Dashboard Reports**: Dynamic reports with real-time data
- **🔬 Research Papers**: Academic papers with reproducible results

## 🌟 Examples

Check out `example.pymd` for a comprehensive demonstration of PyExecMD features, including:

- Beautiful data visualizations
- Dynamic calculations
- Interactive tables
- Real-time updates

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License.

---
