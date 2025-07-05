# Standardized Dockerfile for MCP Servers
# This template can be used for all MCP servers with minimal modifications

FROM python:3.11-slim

# Build arguments
ARG MODULE_PATH
ARG PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r mcp && useradd -r -g mcp mcp

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=prod
ENV PULUMI_ORG=scoobyjava-org
ENV PORT=9030
ENV MODULE_PATH=mcp-servers.snowflake_cortex.production_snowflake_cortex_mcp_server

# Change ownership to non-root user
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9030/health || exit 1

# Expose port
EXPOSE 9030

# Run the MCP server
CMD ["sh", "-c", "python -m uvicorn mcp-servers.snowflake_cortex.production_snowflake_cortex_mcp_server:app --host 0.0.0.0 --port 9030"]
