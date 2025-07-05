# Sophia AI - Master Multi-Stage Dockerfile
# Production-ready container build for all services

# ================================
# BUILDER STAGE
# ================================
FROM python:3.11-slim-buster as builder

# Build arguments
ARG UV_VERSION=0.4.15
ARG BUILD_ENV=production

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv==${UV_VERSION}

# Set working directory
WORKDIR /app

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen --no-dev

# ================================
# RUNNER STAGE (Base Production)
# ================================
FROM python:3.11-slim-buster as runner

# Security: Create non-root user
RUN groupadd -r sophia && useradd -r -g sophia sophia

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Set ownership
RUN chown -R sophia:sophia /app

# Switch to non-root user
USER sophia

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# ================================
# MCP SERVER STAGE
# ================================
FROM runner as mcp-server

# MCP-specific environment
ENV MCP_SERVER=true
ENV PORT=9000

# Expose MCP port
EXPOSE ${PORT}

# Default command for MCP servers
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]

# ================================
# BACKEND API STAGE
# ================================
FROM runner as backend-api

# Backend-specific environment
ENV BACKEND_API=true
ENV PORT=8000

# Expose API port
EXPOSE ${PORT}

# Backend API command
CMD ["python", "-m", "uvicorn", "backend.app.fastapi_app:app", "--host", "0.0.0.0", "--port", "${PORT}"]

# ================================
# FRONTEND STAGE
# ================================
FROM node:18-alpine as frontend

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend code
COPY frontend/ .

# Build frontend
RUN npm run build

# Serve frontend
EXPOSE 3000
CMD ["npm", "start"]

# ================================
# PRODUCTION STAGE (Default)
# ================================
FROM runner as production

# Default production command
CMD ["python", "-m", "uvicorn", "backend.app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
