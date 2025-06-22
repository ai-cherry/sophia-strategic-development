FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and Pulumi CLI
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://get.pulumi.com | sh \
    && mv /root/.pulumi/bin/pulumi /usr/local/bin/

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY . .

# Expose MCP server port
EXPOSE 9000

# Run the MCP server
CMD ["python", "-m", "sentry_mcp_server"]
