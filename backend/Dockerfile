# Multi-stage build for optimized production image
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements.docker.txt* /app/
COPY pyproject.toml uv.lock* /app/

# Install dependencies using pip (more stable for Docker)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 sophia

# Set working directory
WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code with proper ownership
COPY --chown=sophia:sophia backend/ ./backend/
COPY --chown=sophia:sophia config/ ./config/
COPY --chown=sophia:sophia scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/logs && chown sophia:sophia /app/logs

# Set Python path to include app root
ENV PYTHONPATH=/app:$PYTHONPATH
ENV ENVIRONMENT=prod
ENV PORT=8000

# Switch to non-root user
USER sophia

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.app.unified_chat_backend:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 