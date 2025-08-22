# PyMD Syntax Guide

PyMD is a Markdown-like language written in Python that allows you to mix Python code execution with Markdown content. This guide covers the complete syntax and special methods available in PyMD.

## Quick Start

### Execution with PyExecMd

After install the pyexecmd, you can simply use below command to open the editor website.

```bash
pyexecmd serve
```

### Execution with Vanilla Python

To use PyMD with regular Python execution, simply add `import pymd` at the top of your `.pymd` file:

````pymd
import pymd

# Your PyMD content follows...
````

This allows you to run PyMD files directly with Python: `python your_file.pymd`

## Core Syntax

### Markdown Content

In PyMD, markdown content is prefixed with `#` (Python comments). This allows the file to be valid Python while containing rich markdown:

````pymd
# # This is a Level 1 Header
# ## This is a Level 2 Header
# ### This is a Level 3 Header
# 
# This is regular paragraph text with **bold formatting**.
# 
# - Unordered list item 1
# - Unordered list item 2
# 
# 1. Ordered list item 1
# 2. Ordered list item 2
````

### Code Execution Blocks

#### Executable Code Blocks

Use triple backticks for code that should be executed and have its output rendered:

````pymd
# ```

import numpy as np
x = 10
y = 20
print(f"Sum: {x + y}")

# ```
````

#### Display-Only Code Blocks

Use quadruple backticks for code that should only be displayed (not executed):

````pymd
# ````
# This code is only for display

def example_function():
    return "This won't be executed"
# ````
````

### Tables

Create tables using standard Markdown table syntax:

```pymd
# | Name | Age | City |
# |------|-----|------|
# | John | 25  | NYC  |
# | Jane | 30  | LA   |
```

### Comments

Use `//` for comments that will be ignored during rendering:

````pymd
// This is a comment that won't appear in output
````

## Special PyMD Methods

PyMD provides several special methods accessible through the `pymd` object:

### Headers (`pymd.h1`, `pymd.h2`, `pymd.h3`)

Create headers programmatically from Python code:

````pymd
# ```
pymd.h1("Dynamic Header 1")
pymd.h2("Dynamic Header 2")  
pymd.h3("Dynamic Header 3")
# ```
````

### Text (`pymd.text`)

Create paragraph text with bold formatting support:

````pymd
# ```
pymd.text("This is regular text with **bold** formatting.")
# ```
````

### Images (`pymd.image`)

Render matplotlib plots and other images:

````pymd
# ```
import matplotlib.pyplot as plt
import numpy as np

# Create a plot

x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)

# Render the current figure

pymd.image(caption="Sine wave plot")

# Or use plt.show() which automatically captures the plot

plt.show()
# ```
````

**Key Features:**

- Automatically captures matplotlib plots when using `plt.show()`
- Saves images to `images/` directory with automatic naming
- Supports both file-based and base64 fallback display
- Includes caption support

### Videos (`pymd.video`)

Embed video files in your PyMD documents:

````pymd
# ```
# Render a video file

pymd.video(
    video_path="path/to/video.mp4",
    caption="Demo video",
    width="80%",
    height="auto",
    controls=True,
    autoplay=False,
    loop=False
)
# ```
````

**Parameters:**

- `video_path`: Path to the video file
- `caption`: Optional caption text
- `width`: Video width (default: "100%")
- `height`: Video height (default: "auto")
- `controls`: Show video controls (default: True)
- `autoplay`: Auto-play video (default: False)
- `loop`: Loop video playback (default: False)

### Tables (`pymd.table`)

Render pandas DataFrames and other tabular data:

````pymd
# ```
import pandas as pd

# Create a DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['NYC', 'LA', 'Chicago']
}
df = pd.DataFrame(data)

# Render as table
pymd.table(df)
# ```
````

**Supported Data Types:**

- Pandas DataFrames (rendered as HTML tables)
- Lists and tuples (converted to simple tables)
- Any other data (displayed as formatted text)

### Code Blocks (`pymd.code`)

Create syntax-highlighted code blocks:

````pymd
# ```
code_example = '''
def hello_world():
    print("Hello, World!")
'''

pymd.code(code_example, language='python')
# ```
````

## Advanced Features

### Variable Persistence

Variables defined in one code block are available in subsequent blocks:

````pymd
# ```
# First execution code block
name = "PyMD"
version = "1.0"
# ```
# ## This is the markdown block
# - You can add the content here start with # syntex
# ```

# Second execution block
# Variables from first block are available
print(f"Welcome to {name} version {version}")

# ```
````

### Input Handling

For interactive input in code blocks, use comments to provide mock values:

````pymd
# ```
name = input("Enter your name: ")  # input: John Doe
age = int(input("Enter your age: "))  # input: 25
print(f"Hello {name}, you are {age} years old")
# ```
````

### Markdown from Print Output

Print statements can output markdown that gets rendered:

````pymd
# ```
print("## Dynamic Header")
print("This text was printed from Python code")
print("")
print("- Dynamic list item 1")  
print("- Dynamic list item 2")
print("")
print("| Column 1 | Column 2 |")
print("|----------|----------|")
print("| Value 1  | Value 2  |")
# ```
````

## File Structure

When PyMD renders content with media, it creates the following structure:

```bash
your_project/
├── your_file.pymd
├── output.html
├── images/
│   ├── plot_1_abc123.png
│   └── plot_2_def456.png  
└── videos/
    ├── video_1_ghi789.mp4
    └── video_2_jkl012.mp4
```

## Execution

### Using PyMD CLI

```bash
# Render to HTML
python -m pymd.cli render example.pymd -o output.html

# Render to Markdown  
python -m pymd.cli render example.pymd -f markdown -o output.md

# Start editor server
python -m pymd.cli serve --file example.pymd --port 8080
```

### Direct Python Execution

Add `import pymd` at the top of your `.pymd` file:

````pymd
import pymd

# # Your PyMD Content
# This is a PyMD document that can be run directly with Python.
# ```

x = 42
print(f"The answer is {x}")

# ```
````

Then run: `python your_file.pymd`

## Best Practices

1. **Structure**: Use `# #` for main headers, `# ##` for subheaders
2. **Code Organization**: Keep related code in the same block for better variable scope management
3. **Images**: Use descriptive captions for better documentation
4. **Comments**: Use `//` for implementation notes that shouldn't appear in output
5. **Mixed Content**: Combine markdown documentation with executable examples for comprehensive documents

## Examples

### Complete Example

````pymd
import pymd

# # Data Analysis Report
# 
# This report demonstrates PyMD's capabilities for combining code and documentation.
#
# ## Data Generation

# ```  

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Generate sample data

np.random.seed(42)
data = np.random.normal(100, 15, 1000)
print(f"Generated {len(data)} data points")
print(f"Mean: {np.mean(data):.2f}")
print(f"Std: {np.std(data):.2f}")

# ```

# ## Visualization

# ```

# Create histogram

plt.figure(figsize=(10, 6))
plt.hist(data, bins=30, alpha=0.7, color='skyblue')
plt.title('Data Distribution')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.show()  # Automatically captured by PyMD

# ```

# ## Summary Table

# ```

# Create summary statistics

summary_data = {
    'Statistic': ['Count', 'Mean', 'Std Dev', 'Min', 'Max'],
    'Value': [len(data), np.mean(data), np.std(data), np.min(data), np.max(data)]
}
summary_df = pd.DataFrame(summary_data)
pymd.table(summary_df)

# ```
````

This creates a complete document with text, code, visualizations, and tables all in one executable file.
