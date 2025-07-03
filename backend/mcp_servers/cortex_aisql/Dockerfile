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

# Install Python dependencies
FROM base as dependencies
COPY pyproject.toml* requirements.txt* ./
RUN pip install --no-cache-dir uv && \
    if [ -f pyproject.toml ]; then \
        uv pip install --system --no-cache-dir -r pyproject.toml; \
    elif [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        # Install minimal dependencies if no requirements file
        pip install --no-cache-dir \
            fastapi==0.110.0 \
            uvicorn[standard]==0.27.0 \
            snowflake-connector-python==3.6.0 \
            httpx==0.26.0 \
            pydantic==2.5.3; \
    fi

# Final stage
FROM base as runtime
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy the necessary backend modules
COPY --chown=appuser:appuser backend/core/auto_esc_config.py /app/backend/core/
COPY --chown=appuser:appuser backend/core/__init__.py /app/backend/core/
COPY --chown=appuser:appuser backend/mcp_servers/cortex_aisql/cortex_mcp_server.py /app/backend/mcp_servers/cortex_aisql/
COPY --chown=appuser:appuser backend/__init__.py /app/backend/

# Create empty __init__.py files for proper module structure
RUN touch /app/backend/mcp_servers/__init__.py

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()"

# Start the server
CMD ["uvicorn", "backend.mcp_servers.cortex_aisql.cortex_mcp_server:app", "--host", "0.0.0.0", "--port", "8080"] 