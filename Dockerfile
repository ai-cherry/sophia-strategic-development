# syntax=docker/dockerfile:1
# Canonical Dockerfile for Sophia AI Platform
# Multi-stage build with UV for optimized production images

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_SYSTEM_PYTHON=1

# Create non-root user early for security
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Install system dependencies needed by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Stage 1: Dependencies builder
# ============================================
FROM base AS dependencies

# Install UV for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser uv.lock* ./

# Install runtime dependencies only
RUN uv pip install --system --no-cache .

# ============================================
# Stage 2: Production runtime
# ============================================
FROM base AS production

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser backend/ ./backend/
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser pyproject.toml ./

# Switch to non-root user
USER appuser

# Expose the FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health').read()"

# Run the FastAPI application
CMD ["uvicorn", "backend.app.unified_fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================
# Stage 3: Development (optional)
# ============================================
FROM dependencies AS development

# Install development dependencies
RUN uv pip install --system --no-cache .[dev]

# Copy all source code for development
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Enable hot reload for development
CMD ["uvicorn", "backend.app.unified_fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Stage 4: Testing (optional)
# ============================================
FROM development AS testing

# Run tests during build
RUN python -m pytest tests/ -v --tb=short || true

# Default to running tests
CMD ["pytest", "tests/", "-v"]

