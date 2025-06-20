# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package installer)
RUN pip install uv

# Copy pyproject.toml and any lock files first for better caching
COPY pyproject.toml ./
COPY uv.lock* ./

# Create virtual environment and install dependencies
RUN uv venv --python 3.11
RUN uv pip install -e .

# Copy the entire source code
COPY . .

# Install the package in development mode
RUN uv pip install -e .

# Create a non-root user for security
RUN useradd -m -u 1000 lightrag
RUN chown -R lightrag:lightrag /app
USER lightrag

# Expose the default port (though MCP typically uses stdio)
EXPOSE 8080

# Default command - will be overridden by smithery.yaml
CMD ["uv", "run", "src/lightrag_mcp/main.py"]
