# PyMD: Python-Powered Markdown

[![PyPI Downloads](https://static.pepy.tech/badge/pyexecmd)](https://pepy.tech/projects/pyexecmd)

PyMD is a revolutionary markup language that creates **executable Python files** that also render beautifully as markdown documents. All markdown content is prefixed with `#` (making it Python comments), while code blocks contain regular executable Python code that prints markdown during rendering.

![Screen Shot](./assets/v0.1.6.png)

## ✨ Features

### 🐍 Core Functionality

- **Executable Python Files**: Run directly with `python filename.pymd`
- **Dual Code Blocks**: ``` for executable code, ```` for display-only
- **Variable Persistence**: Variables persist across code blocks

### 📝 Document Creation

- **Commented Markdown**: All markdown prefixed with `#` (Python comments)
- **Print-to-Markdown**: `print()` statements output markdown during rendering
- **Dynamic Content**: Execute Python code and display results inline

### 🎨 Rich Media Support

- **Automatic Plot Capture**: `plt.show()` saves and renders matplotlib plots
- **Video Rendering**: Built-in video support with custom controls
- **Table Detection**: Automatic markdown table formatting

### 🔴 Live Development

- **Real-time Preview**: Auto-refresh as you edit with web editor
- **One-click Export**: Export to HTML or Markdown with embedded media
- **Fast Rendering**: Efficient parsing with caching

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

<details>
<summary> For Conda Users (Recommended Development Setup) </summary>

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

</details>

### Web Editor Features

The web editor (available at `/editor`) includes:

- **📝 Split-view editing**: Side-by-side editor and live preview
- **🖱️ One-click export**: Export HTML and Markdown buttons in the interface
- **⚡ Live rendering**: Ctrl+S to execute code and update preview
- **💾 File management**: Save and download your documents
- **🎨 Syntax highlighting**: Python syntax highlighting with PyMD-specific features

## 📝 PyMD Syntax

Please refer to [Syntex Guide](./PyMD_Syntax_Guide.md) to learn how to write the PyMD

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

**Output Directory Structure:**

After rendering documents with images and videos, your output directory will look like:

```bash
my_project/
├── document.pymd           # Source PyMD file
├── document.html           # Rendered HTML output
├── images/                 # Auto-generated plot images
│   ├── plot_1_abc123.png
│   └── plot_2_def456.png
└── videos/                 # Embedded video files
    ├── video_1_ghi789.mp4
    └── video_2_jkl012.mp4
```

**Web Editor Features:**

1. **Live Editing**: Open `http://localhost:8080/editor` in your browser
2. **Syntax Highlighting**: `#` prefixed markdown and Python code blocks
3. **Live Preview**: See rendered output in real-time
4. **Export Options**: Click **📄 Export HTML** or **📝 Export MD**
5. **File Execution**: Use Ctrl+S to execute code and update preview

## 🎯 Use Cases

- **📊 Data Science Reports**: Python scripts that execute analysis AND generate beautiful reports with automatic plot capture
- **📚 Executable Documentation**: Documentation that actually runs and validates itself, with embedded visualizations and demo videos
- **🎓 Interactive Tutorials**: Learning materials that students can execute and modify, featuring live charts, tables, and instructional videos
- **📈 Living Dashboards**: Python scripts that generate dynamic visual reports with automatic image saving
- **🔬 Reproducible Research**: Research papers where the code actually runs and produces publication-ready figures
- **🧪 Literate Programming**: Self-documenting code through executable markdown comments with inline visualizations
- **📋 Technical Specifications**: Specs that include working code examples and automatically generated plots
- **🤖 AI/ML Workflows**: Machine learning pipelines with embedded documentation and automatic model visualization
- **📑 Business Reports**: Automated reports with data tables and charts that update when code runs
- **🎨 Presentation Materials**: Technical presentations that combine code, explanation, live visualizations, and demo videos

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License.

---
