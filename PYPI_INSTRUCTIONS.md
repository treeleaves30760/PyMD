# PyMD PyPI Package Instructions

## Building and Publishing to PyPI

Follow these steps to build and publish your PyMD package to PyPI:

### Prerequisites

1. **Install build tools:**

   ```bash
   pip install build twine
   ```

2. **Create PyPI accounts:**
   - Register at [PyPI](https://pypi.org/account/register/)
   - Register at [TestPyPI](https://test.pypi.org/account/register/) (recommended for testing)

### Building the Package

1. **Navigate to your project directory:**

   ```bash
   cd /Users/hsupohsiang/Self/Github_Local/PyMD
   ```

2. **Clean previous builds (if any):**

   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

3. **Build the package:**

   ```bash
   python -m build
   ```

   This will create:
   - `dist/pymd-0.1.0.tar.gz` (source distribution)
   - `dist/pymd-0.1.0-py3-none-any.whl` (wheel distribution)

### Testing the Package

1. **Upload to TestPyPI first:**

   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. **Install from TestPyPI to test:**

   ```bash
   pip install --index-url https://test.pypi.org/simple/ pymd
   ```

3. **Test the installation:**

   ```bash
   pymd --help
   pymd create test.pymd
   pymd render test.pymd -o test.html
   ```

### Publishing to PyPI

1. **Upload to PyPI:**

   ```bash
   python -m twine upload dist/*
   ```

2. **Install from PyPI:**

   ```bash
   pip install pymd
   ```

### Authentication

For secure uploads, create API tokens:

1. **TestPyPI:** Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/token/)
2. **PyPI:** Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)

Create a `~/.pypirc` file:

```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
username = __token__
password = <your-pypi-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-token>
```

### Automated Publishing with GitHub Actions

You can also set up automated publishing using GitHub Actions. Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### Version Management

To release new versions:

1. **Update version in `pyproject.toml`:**

   ```toml
   version = "0.1.1"  # or whatever the new version is
   ```

2. **Update version in `pymd/__init__.py`:**

   ```python
   __version__ = "0.1.1"
   ```

3. **Create a git tag:**

   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

4. **Rebuild and republish:**

   ```bash
   rm -rf dist/ build/
   python -m build
   python -m twine upload dist/*
   ```

### Package Structure Summary

Your package now has the following structure:

```
PyMD/
├── pymd/                   # Main package directory
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   ├── renderer.py        # Core rendering engine
│   └── server.py          # Live preview server
├── tests/                 # Test files (optional)
├── examples/              # Example files (optional)
├── pyproject.toml         # Modern Python packaging configuration
├── MANIFEST.in            # Additional files to include
├── LICENSE                # MIT License
├── README.md              # Project documentation
└── requirements.txt       # Dependencies (for development)
```

### Usage After Installation

Once published and installed via `pip install pymd`, users can:

```bash
# Create a new PyMD document
pymd create my_document.pymd

# Start live preview server
pymd serve my_document.pymd --port 8000

# Render to HTML
pymd render my_document.pymd -o output.html
```

Or use it programmatically:

```python
from pymd import PyMDRenderer

renderer = PyMDRenderer()
html = renderer.render_file('document.pymd')
```

### Next Steps

1. Test your package thoroughly before publishing
2. Consider setting up continuous integration (CI) tests
3. Add more comprehensive documentation
4. Set up automatic documentation generation with Sphinx
5. Consider adding type hints and running mypy for better code quality
