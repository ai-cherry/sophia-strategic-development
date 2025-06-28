FROM python:3.12-slim AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://get.pulumi.com | sh && \
    ln -s /root/.pulumi/bin/pulumi /usr/local/bin/pulumi && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY mcp-servers/pulumi/main.py .

CMD ["python", "main.py"]
