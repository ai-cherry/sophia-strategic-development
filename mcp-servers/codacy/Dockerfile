FROM python:3.12-slim AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy only necessary files
COPY pyproject.toml uv.lock ./
COPY backend/ /app/backend
COPY mcp-servers/codacy/ /app/mcp-servers/codacy/

# Install dependencies
RUN uv sync --frozen --no-cache

# Set environment variables for production-first operation
ENV ENVIRONMENT="prod"
ENV PULUMI_ORG="scoobyjava-org"
ENV LOG_LEVEL="INFO"
ENV PYTHONPATH="/app"

# Expose the port the server will run on
EXPOSE 3008

CMD ["uvicorn", "mcp-servers.codacy.codacy_mcp_server:app", "--host", "0.0.0.0", "--port", "3008"] 