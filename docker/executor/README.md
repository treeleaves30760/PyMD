# PyMD Executor Docker Image

This directory contains the Docker image for executing user Python code in an isolated environment.

## Building the Image

```bash
cd /Users/hsupohsiang/Self/Github_Local/PyMD
docker build -t pymd-executor:latest -f docker/executor/Dockerfile docker/executor/
```

## Features

- **Python 3.11**: Latest stable Python version
- **Non-root user**: Runs as `executor` user (UID 1000)
- **Minimal dependencies**: Only essential packages installed
- **Volume support**: `/workspace` directory for user environments
- **Security hardening**: No network access, resource limits enforced

## Usage

The image is designed to be used with Docker volumes containing user-specific Python environments:

```bash
# Create a volume for a user environment
docker volume create pymd-env-user123-default

# Run code execution
docker run --rm \
  -v pymd-env-user123-default:/workspace/.venv \
  --memory="512m" \
  --cpus="0.5" \
  --network=none \
  pymd-executor:latest \
  python -c "import numpy; print(numpy.__version__)"
```

## execute.py Script

The `execute.py` script is used for executing arbitrary Python code:

```bash
echo "print('Hello from PyMD!')" | docker run --rm -i pymd-executor:latest python execute.py
```

It returns JSON output:
```json
{
  "success": true,
  "stdout": "Hello from PyMD!\n",
  "stderr": "",
  "error": null
}
```

## Security

- Container runs as non-root user
- No network access (--network=none)
- Resource limits enforced (CPU, memory)
- Read-only root filesystem (except /workspace)
- Minimal attack surface
