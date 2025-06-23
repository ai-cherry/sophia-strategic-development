# Competitive Intelligence Monitor MCP Server for Pay Ready
FROM python:3.11-alpine

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    postgresql-dev \
    chromium \
    chromium-chromedriver

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for monitoring results
RUN mkdir -p /app/data /app/screenshots

# Expose MCP server port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000/health')"

# Run the MCP server
CMD ["python", "competitive_monitor_mcp_server.py"]
