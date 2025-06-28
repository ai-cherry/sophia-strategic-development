FROM python:3.12-slim AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Copy MCP server code
COPY snowflake_mcp_server.py .
COPY mcp_base.py .

# Set environment variables
ENV MCP_SERVER_NAME=snowflake-mcp
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "snowflake_mcp_server.py"]
