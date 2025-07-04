# syntax=docker/dockerfile:1
FROM python:3.11-slim as base

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

FROM base as dependencies
# Copy pyproject.toml for dependency installation
COPY pyproject.toml* ./
# Install UV and dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --system .

FROM base as runtime
# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy the application code
COPY --chown=appuser:appuser backend/mcp_servers/mem0_openmemory/ /app/

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()"

CMD ["uvicorn", "enhanced_mem0_server:app", "--host", "0.0.0.0", "--port", "8080"]
