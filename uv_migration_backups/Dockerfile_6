FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set Python path to include backend modules
ENV PYTHONPATH=/app:/app/backend

# Expose MCP server port
EXPOSE 8085

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from snowflake_admin_mcp_server import admin_agent; print('healthy')" || exit 1

# Run the MCP server
CMD ["python", "snowflake_admin_mcp_server.py"] 