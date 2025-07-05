FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install UV and dependencies
RUN pip install uv && \
    uv sync --frozen

# Copy application code
COPY mcp-servers/hubspot_unified/ ./mcp-servers/hubspot_unified/
COPY backend/ ./backend/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 9006

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9006/health || exit 1

# Run the server
CMD ["python", "mcp-servers/hubspot_unified/hubspot_mcp_server.py"]
