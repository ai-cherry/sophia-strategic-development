FROM python:3.12-slim AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy requirements and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV ENVIRONMENT=prod
ENV PULUMI_ORG=scoobyjava-org
ENV MCP_SERVER_PORT=${MCP_SERVER_PORT:-9000}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${MCP_SERVER_PORT}/health || exit 1

# Expose port
EXPOSE ${MCP_SERVER_PORT}

# Run the server
CMD ["python", "-m", "server"]
