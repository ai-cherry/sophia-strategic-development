"""Ai_Memory_V2 MCP Server implementation."""
import asyncio
from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from infrastructure.mcp_servers.ai_memory_v2.config import settings
from infrastructure.mcp_servers.ai_memory_v2.handlers.main_handler import (
    AiMemoryV2Handler,
)
from infrastructure.mcp_servers.ai_memory_v2.models.data_models import (
    BulkMemoryRequest,
    MemoryEntry,
    MemoryStats,
    MemoryUpdateRequest,
    SearchRequest,
    SearchResult,
)
from infrastructure.mcp_servers.ai_memory_v2.utils.logging_config import setup_logging

# Setup logging
setup_logging(settings.LOG_LEVEL)

# Create FastAPI app
app = FastAPI(
    title="AI Memory V2 MCP Server",
    description="Production-ready semantic memory storage and retrieval system",
    version="2.0.0"
)

# Create handler instance
handler = AiMemoryV2Handler()

# Dependency to get handler
async def get_handler():
    return handler

@app.on_event("startup")
async def startup_event():
    """Initialize handler on startup."""
    await handler.initialize()

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "ai_memory_v2",
        "version": "2.0.0",
        "embedding_enabled": settings.OPENAI_API_KEY != ""
    }

@app.get("/capabilities")
async def capabilities():
    """Get server capabilities."""
    return {
        "capabilities": [
            {
                "name": "semantic_search",
                "description": "Search memories using semantic similarity",
                "enabled": settings.OPENAI_API_KEY != ""
            },
            {
                "name": "auto_categorization",
                "description": "Automatically categorize memories",
                "enabled": settings.ENABLE_AUTO_CATEGORIZATION
            },
            {
                "name": "duplicate_detection",
                "description": "Detect duplicate memories",
                "enabled": settings.ENABLE_DUPLICATE_DETECTION
            }
        ],
        "settings": {
            "embedding_model": settings.EMBEDDING_MODEL,
            "embedding_dimension": settings.EMBEDDING_DIMENSION,
            "max_memory_size": settings.MAX_MEMORY_SIZE,
            "default_search_limit": settings.DEFAULT_SEARCH_LIMIT,
            "similarity_threshold": settings.SIMILARITY_THRESHOLD
        }
    }

# Memory endpoints

@app.post("/api/memory", response_model=MemoryEntry)
async def store_memory(
    content: str,
    category: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
    user_id: str | None = None,
    source: str | None = None,
    handler: AiMemoryV2Handler = Depends(get_handler)
):
    """Store a new memory."""
    try:
        memory = await handler.store_memory(
            content=content,
            category=category,
            metadata=metadata,
            tags=tags,
            user_id=user_id,
            source=source
        )
        return memory
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/bulk", response_model=list[MemoryEntry])
async def bulk_store_memories(
    request: BulkMemoryRequest,
    handler: AiMemoryV2Handler = Depends(get_handler)
):
    """Store multiple memories in bulk."""
    try:
        memories = await handler.bulk_store_memories(request)
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=list[SearchResult])
async def search_memories(
    request: SearchRequest,
    handler: AiMemoryV2Handler = Depends(get_handler)
):
    """Search memories using semantic similarity."""
    try:
        results = await handler.search_memories(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/{memory_id}", response_model=MemoryEntry)
async def get_memory(
    memory_id: int,
    handler: AiMemoryV2Handler = Depends(get_handler)
):
    """Get a specific memory by ID."""
    try:
        memory = await handler._get_memory_by_id(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
        return memory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/memory/{memory_id}", response_model=MemoryEntry)
async def update_memory(
    memory_id: int,
    request: MemoryUpdateRequest,
    handler: AiMemoryV2Handler = Depends(get_handler)
):
    """Update an existing memory."""
    try:
        memory = await handler.update_memory(memory_id, request)
        return memory
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory/{memory_id}")
async def delete_memory(
    memory_id: int,
    handler: AiMemoryV2Handler = Depends(get_handler)
):
    """Delete a memory."""
    try:
        success = await handler.delete_memory(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
        return {"message": f"Memory {memory_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", response_model=MemoryStats)
async def get_stats(handler: AiMemoryV2Handler = Depends(get_handler)):
    """Get memory system statistics."""
    try:
        stats = await handler.get_memory_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Prometheus metrics endpoint
if settings.ENABLE_METRICS:
    import time

    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )

    # Define metrics
    memory_operations = Counter('ai_memory_operations_total', 'Total memory operations', ['operation'])
    search_latency = Histogram('ai_memory_search_duration_seconds', 'Search operation latency')

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        return JSONResponse(
            content=generate_latest().decode('utf-8'),
            media_type=CONTENT_TYPE_LATEST
        )

async def main():
    """Main entry point."""
    config = uvicorn.Config(
        app,
        host="127.0.0.1"  # Changed from 0.0.0.0 for security. Use environment variable for production,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
