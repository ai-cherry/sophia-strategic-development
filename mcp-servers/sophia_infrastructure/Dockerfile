FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Docker CLI
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    docker.io \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
COPY ../../backend/core/clean_esc_config.py /app/backend/core/
COPY ../../backend/core/__init__.py /app/backend/core/

# Set Python path
ENV PYTHONPATH=/app

# Expose MCP server port
EXPOSE 8093

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8093/health || exit 1

# Run the MCP server
CMD ["python", "sophia_infrastructure_mcp_server.py"] 