FROM python:3.12-slim AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Copy application code
COPY mcp-servers/sophia_ai_intelligence/sophia_ai_intelligence_mcp_server.py .
COPY backend/core/clean_esc_config.py /app/backend/core/
COPY backend/core/__init__.py /app/backend/core/

# Set Python path
ENV PYTHONPATH=/app

# Expose MCP server port
EXPOSE 8091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8091/health || exit 1

# Run the MCP server
CMD ["python", "sophia_ai_intelligence_mcp_server.py"] 