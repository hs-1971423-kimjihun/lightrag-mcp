# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY . .

# Install the package
RUN pip install -e .

# Create a non-root user
RUN useradd -m -u 1000 lightrag && \
    chown -R lightrag:lightrag /app

USER lightrag

# Default command
CMD ["python", "-m", "lightrag_mcp.main"]
