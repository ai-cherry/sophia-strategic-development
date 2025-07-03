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

# Copy only dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (if available), fallback to pip if not
RUN pip install --upgrade pip && \
    pip install uv || pip install -r requirements.txt

# Copy the application code
COPY . .

# Change to non-root user
USER appuser

# Expose the FastAPI port
EXPOSE 8080

# Healthcheck (optional, for Kubernetes)
HEALTHCHECK CMD curl --fail http://localhost:8080/health || exit 1

# Start the server with uvicorn
CMD ["uvicorn", "enhanced_mem0_server:app", "--host", "0.0.0.0", "--port", "8080"] 