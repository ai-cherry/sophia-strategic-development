FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://get.pulumi.com | sh && \
    ln -s /root/.pulumi/bin/pulumi /usr/local/bin/pulumi && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY mcp-servers/pulumi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp-servers/pulumi/main.py .

CMD ["python", "main.py"]
