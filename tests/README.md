# PyMD Test Suite

This directory contains the comprehensive test suite for PyMD, organized into structured modules for better maintainability.

## Test Structure

### Core Test Modules

- **`test_basic_functionality.py`** - Tests basic PyMD features
  - Header rendering (`#`, `##`, `###`)
  - List rendering (ordered and unordered)
  - Plain text paragraphs
  - Comment filtering (`//` comments)

- **`test_code_execution.py`** - Tests Python code execution
  - Simple code execution in ``` blocks
  - Variable persistence across code blocks
  - Multi-line code structures (functions, loops, classes)
  - PyMD helper functions (`pymd.h1()`, `pymd.text()`, etc.)
  - Code display with `pymd.code()`

- **`test_new_syntax.py`** - Tests the new ``` syntax
  - Mixed markdown and code content
  - Code block boundary parsing
  - Empty code block handling
  - Nested strings in code blocks
  - Backward compatibility

- **`test_styling.py`** - Tests CSS styling and appearance
  - List styling (custom bullets, numbering, hover effects)
  - Code output styling
  - Header styling
  - Comprehensive styling integration

### Support Files

- **`conftest.py`** - Test configuration and utilities
  - `TestUtils` class with helper methods
  - Renderer creation
  - Output file management
  - Content extraction and assertions

- **`test_runner.py`** - Main test runner
  - Runs all test suites
  - Provides summary reports
  - Supports running individual test suites

### Output Directory

- **`outputs/`** - Contains HTML output files from tests
  - Each test generates an HTML file for visual inspection
  - Files are named `{test_name}_output.html`
  - Useful for debugging and visual verification

## Running Tests

### Run All Tests

```bash
python3 tests/test_runner.py
```

### Run Specific Test Suite

```bash
python3 tests/test_runner.py basic     # Basic functionality
python3 tests/test_runner.py code      # Code execution  
python3 tests/test_runner.py syntax    # New syntax
python3 tests/test_runner.py styling   # Styling
```

### Run Individual Test Files

```bash
python3 tests/test_basic_functionality.py
python3 tests/test_code_execution.py
python3 tests/test_new_syntax.py
python3 tests/test_styling.py
```

## Test Coverage

The test suite covers:

✅ **Core Features**

- Markdown syntax (headers, lists, text)
- Python code execution in ``` blocks
- Variable persistence across code blocks
- Comment filtering

✅ **Advanced Features**  

- Multi-line code structures
- PyMD helper functions
- Code display with syntax highlighting
- Mixed content parsing

✅ **Styling & UI**

- Custom list styling
- Code output formatting
- Header styling with borders
- Hover effects and responsive design

✅ **Error Handling**

- Empty code blocks
- Malformed syntax
- Code execution errors
- Boundary conditions

## Adding New Tests

1. **Choose the appropriate test module** based on functionality
2. **Add test methods** following the naming convention `test_feature_name`
3. **Use `TestUtils`** helper methods for common operations
4. **Save output files** for visual inspection using `test_utils.save_test_output()`
5. **Update the test runner** if adding new test modules

## Example Test Method

````python
def test_new_feature(self):
    """Test description"""
    content = """
# Test Content
```

print("Hello World")

```
"""
    html = self.renderer.parse_and_render(content)
    output_file = test_utils.save_test_output(html, "test_new_feature")
    
    test_utils.assert_contains(html, "Hello World")
    print(f"✅ Test passed - output saved to {output_file}")
````

## Current Test Status

All test suites are passing! 🎉

- **18 individual tests** across 4 test suites
- **100% pass rate** for current functionality
- **Comprehensive coverage** of new ``` syntax
- **Visual outputs** for manual verification
