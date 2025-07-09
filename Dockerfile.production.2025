# syntax=docker/dockerfile:1.5
# Enable BuildKit features for 2025 best practices

# Build stage - optimized for caching
FROM python:3.12-slim AS builder

# Install build dependencies with cache mount
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y \
    gcc g++ git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install UV for blazing fast dependency management
RUN curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /build

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock* ./
COPY backend/ ./backend/

# Use BuildKit cache mount for UV cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Production stage - minimal runtime
FROM python:3.12-slim

# Install runtime dependencies and security updates
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash sophia

WORKDIR /app

# Copy from builder with proper ownership
COPY --from=builder --chown=sophia:sophia /build/.venv /app/.venv
COPY --from=builder --chown=sophia:sophia /build/backend /app/backend

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    ENVIRONMENT="prod" \
    PULUMI_ORG="scoobyjava-org" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp && \
    chown -R sophia:sophia /app

# Switch to non-root user
USER sophia

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Use exec form for proper signal handling
ENTRYPOINT ["uvicorn"]
CMD ["backend.app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop"] 