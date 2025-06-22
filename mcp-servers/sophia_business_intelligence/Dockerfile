FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY mcp-servers/sophia_business_intelligence/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mcp-servers/sophia_business_intelligence/sophia_business_intelligence_mcp_server.py .

# Set Python path
ENV PYTHONPATH=/app

# Expose MCP server port
EXPOSE 8094

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8094/health || exit 1

# Run the MCP server
CMD ["python", "sophia_business_intelligence_mcp_server.py"] 