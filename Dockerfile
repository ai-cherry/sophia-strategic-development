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

# Copy dependency files and create requirements.txt for Docker build
COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser uv.lock* ./

# Create a temporary requirements.txt with core dependencies for Docker build
RUN echo "fastapi>=0.115.0" > requirements.txt && \
    echo "uvicorn[standard]>=0.32.0" >> requirements.txt && \
    echo "starlette>=0.37.2" >> requirements.txt && \
    echo "pydantic>=2.5.0" >> requirements.txt && \
    echo "pydantic-settings>=2.6.1" >> requirements.txt && \
    echo "python-multipart>=0.0.18" >> requirements.txt && \
    echo "python-jose[cryptography]>=3.3.0" >> requirements.txt && \
    echo "pyjwt>=2.8.0" >> requirements.txt && \
    echo "passlib>=1.7.4" >> requirements.txt && \
    echo "bcrypt>=4.1.2" >> requirements.txt && \
    echo "jinja2>=3.1.0" >> requirements.txt && \
    echo "orjson>=3.9.0" >> requirements.txt && \
    echo "aiohttp>=3.9.1" >> requirements.txt && \
    echo "aiofiles>=24.1.0" >> requirements.txt && \
    echo "aiodns>=3.1.1" >> requirements.txt && \
    echo "httpx>=0.28.1" >> requirements.txt && \
    echo "anyio>=4.0.0" >> requirements.txt && \
    echo "uvloop>=0.21.0" >> requirements.txt && \
    echo "websockets>=14.1" >> requirements.txt && \
    echo "sse-starlette>=1.6.5" >> requirements.txt && \
    echo "httpx-sse>=0.4.0" >> requirements.txt && \
    echo "sqlalchemy>=2.0.23" >> requirements.txt && \
    echo "asyncpg>=0.29.0" >> requirements.txt && \
    echo "psycopg2-binary>=2.9.9" >> requirements.txt && \
    echo "aioredis>=2.0.1" >> requirements.txt && \
    echo "redis>=5.0.1" >> requirements.txt && \
    echo "snowflake-connector-python>=3.6.0" >> requirements.txt && \
    echo "snowflake-sqlalchemy>=1.7.5" >> requirements.txt && \
    echo "openai>=1.6.1" >> requirements.txt && \
    echo "anthropic>=0.25.0" >> requirements.txt && \
    echo "langchain>=0.1.0" >> requirements.txt && \
    echo "langchain-community>=0.0.10" >> requirements.txt && \
    echo "sentence-transformers>=2.2.2" >> requirements.txt && \
    echo "transformers>=4.36.2" >> requirements.txt && \
    echo "torch>=2.1.2" >> requirements.txt && \
    echo "numpy>=2.1.3" >> requirements.txt && \
    echo "pandas>=2.2.3" >> requirements.txt && \
    echo "scikit-learn>=1.3.2" >> requirements.txt && \
    echo "faiss-cpu>=1.7.4" >> requirements.txt && \
    echo "pinecone-client>=2.2.4" >> requirements.txt && \
    echo "weaviate-client>=3.25.3" >> requirements.txt && \
    echo "chromadb>=0.4.18" >> requirements.txt && \
    echo "mcp>=0.5.0" >> requirements.txt && \
    echo "fastmcp>=0.1.0" >> requirements.txt && \
    echo "hubspot-api-client>=9.0.0" >> requirements.txt && \
    echo "slack-sdk>=3.25.0" >> requirements.txt && \
    echo "notion-client>=2.2.1" >> requirements.txt && \
    echo "boto3>=1.34.0" >> requirements.txt && \
    echo "azure-storage-blob>=12.19.0" >> requirements.txt && \
    echo "google-cloud-storage>=2.10.0" >> requirements.txt && \
    echo "click>=8.1.7" >> requirements.txt && \
    echo "typer>=0.9.0" >> requirements.txt && \
    echo "rich>=13.9.4" >> requirements.txt && \
    echo "pyyaml>=6.0" >> requirements.txt && \
    echo "tomlkit>=0.12.0" >> requirements.txt && \
    echo "python-dotenv>=1.0.1" >> requirements.txt && \
    echo "python-dateutil>=2.8.2" >> requirements.txt && \
    echo "pytz>=2023.3" >> requirements.txt && \
    echo "structlog>=24.4.0" >> requirements.txt && \
    echo "sentry-sdk>=1.38.0" >> requirements.txt && \
    echo "cryptography>=45.0.5" >> requirements.txt && \
    echo "certifi>=2025.6.15" >> requirements.txt && \
    echo "celery>=5.3.4" >> requirements.txt && \
    echo "apscheduler>=3.10.4" >> requirements.txt && \
    echo "schedule>=1.2.0" >> requirements.txt && \
    echo "prometheus-client>=0.19.0" >> requirements.txt && \
    echo "psutil>=5.9.6" >> requirements.txt && \
    echo "memory-profiler>=0.61.0" >> requirements.txt && \
    echo "python-docx>=1.1.0" >> requirements.txt && \
    echo "python-pptx>=0.6.23" >> requirements.txt && \
    echo "beautifulsoup4>=4.12.0" >> requirements.txt && \
    echo "markdownify>=0.11.6" >> requirements.txt && \
    echo "readability>=0.3.1" >> requirements.txt && \
    echo "watchdog>=3.0.0" >> requirements.txt && \
    echo "joblib>=1.3.2" >> requirements.txt && \
    echo "tqdm>=4.66.1" >> requirements.txt && \
    echo "setuptools>=80.9.0" >> requirements.txt && \
    echo "wheel>=0.45.1" >> requirements.txt && \
    echo "pip>=25.1.1" >> requirements.txt

# Install dependencies from requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt

# ============================================
# Stage 2: Production runtime
# ============================================
FROM base AS production

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
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
