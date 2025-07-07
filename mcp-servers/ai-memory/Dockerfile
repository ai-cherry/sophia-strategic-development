FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install fastapi uvicorn mcp

# Create a basic MCP server
RUN echo 'from fastapi import FastAPI' > app.py && \
    echo 'import mcp' >> app.py && \
    echo '' >> app.py && \
    echo 'app = FastAPI(title="AI Memory MCP Server - Stores and recalls architectural decisions")' >> app.py && \
    echo '' >> app.py && \
    echo '@app.get("/health")' >> app.py && \
    echo 'async def health():' >> app.py && \
    echo '    return {"status": "healthy", "service": "ai-memory"}' >> app.py && \
    echo '' >> app.py && \
    echo '@app.get("/")' >> app.py && \
    echo 'async def root():' >> app.py && \
    echo '    return {"message": "AI Memory MCP Server - Stores and recalls architectural decisions"}' >> app.py && \
    echo '' >> app.py && \
    echo '@app.get("/mcp/tools")' >> app.py && \
    echo 'async def list_tools():' >> app.py && \
    echo '    return {"tools": []}' >> app.py

EXPOSE 9001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9001"]
