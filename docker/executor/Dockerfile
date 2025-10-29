FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install essential packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Create non-root user for execution
RUN useradd -m -u 1000 -s /bin/bash executor && \
    mkdir -p /workspace && \
    chown -R executor:executor /workspace

# Copy execute.py script into the image
COPY execute.py /usr/local/bin/execute.py
RUN chmod +x /usr/local/bin/execute.py

# Set working directory
WORKDIR /workspace

# Switch to non-root user
USER executor

# The /workspace directory will be mounted as a volume
# containing the user's environment and packages
VOLUME ["/workspace"]

# Default command - will be overridden when running
CMD ["python", "-u", "-c", "print('PyMD Executor Ready')"]
