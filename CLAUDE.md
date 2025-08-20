# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development

### Environment Setup

The PyMD conda environment is available at `/opt/miniconda3/envs/PyMD`. To properly activate conda and use the environment:

```bash
# Initialize conda and activate PyMD environment
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD

# Verify activation
python --version && which python
```

### Running PyMD Commands

After activating the conda environment, use standard Python commands:

```bash
# Activate environment first
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD

# Then run PyMD commands
python -m pymd.cli --help

# Render to HTML
python -m pymd.cli render example.pymd -o output.html

# Render to Markdown (new feature)
python -m pymd.cli render example.pymd -f markdown -o output.md

# Start development server
python -m pymd.cli serve --file example.pymd --port 8080

# Create new PyMD file
python -m pymd.cli create new_document.pymd
```

### One-liner Commands

For convenience, you can combine conda activation with commands:

```bash
# Render to HTML
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD && python -m pymd.cli render example.pymd -o output.html

# Render to Markdown
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD && python -m pymd.cli render example.pymd -f markdown -o output.md

# Start server
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD && python -m pymd.cli serve --file example.pymd --port 8080
```

### File Management

Please remove test files in the root directory when done. If test files are needed, add them to the test folder.
