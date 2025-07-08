"""
API Endpoints for AI Memory V2 MCP Server
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from .memory_mediator import (
    ChatMemory,
    EventMemory,
    InsightMemory,
    MemoryType,
    memory_mediator,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/memory", tags=["memory"])

# Request/Response Models
class MemoryStoreRequest(BaseModel):
    """Request model for storing memory"""
    type: MemoryType
    content: dict[str, Any]
    metadata: dict[str, Any] | None = None
    ttl_seconds: int | None = None

class MemoryResponse(BaseModel):
    """Response model for memory operations"""
    id: str
    type: MemoryType
    content: dict[str, Any]
    metadata: dict[str, Any]
    created_at: str
    updated_at: str

class SearchRequest(BaseModel):
    """Request model for searching memories"""
    query: str = ""
    memory_types: list[MemoryType] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    limit: int = Field(default=10, le=100)

class StatsResponse(BaseModel):
    """Response model for memory statistics"""
    cache_hits: int
    cache_misses: int
    cache_writes: int
    hit_rate: float
    total_operations: int

# Helper function to extract RBAC context
def get_rbac_context(x_user_context: str | None = None) -> dict[str, Any] | None:
    """Extract RBAC context from header"""
    if not x_user_context:
        return None

    try:
        import json
        return json.loads(x_user_context)
    except:
        return {"role": "user", "user_id": "anonymous"}

# API Endpoints
@router.post("/store", response_model=dict[str, Any])
async def store_memory(
    request: MemoryStoreRequest,
    x_user_context: str | None = Header(None)
):
    """Store a new memory"""
    try:
        rbac_context = get_rbac_context(x_user_context)

        # Create appropriate memory type
        if request.type == MemoryType.CHAT:
            memory = ChatMemory(
                content=request.content,
                metadata=request.metadata or {},
                ttl_seconds=request.ttl_seconds,
                **request.content  # Unpack chat-specific fields
            )
        elif request.type == MemoryType.EVENT:
            memory = EventMemory(
                content=request.content,
                metadata=request.metadata or {},
                ttl_seconds=request.ttl_seconds,
                **request.content  # Unpack event-specific fields
            )
        elif request.type == MemoryType.INSIGHT:
            memory = InsightMemory(
                content=request.content,
                metadata=request.metadata or {},
                ttl_seconds=request.ttl_seconds,
                **request.content  # Unpack insight-specific fields
            )
        else:
            # Generic memory for other types
            from .memory_mediator import BaseMemory
            memory = BaseMemory(
                type=request.type,
                content=request.content,
                metadata=request.metadata or {},
                ttl_seconds=request.ttl_seconds
            )

        result = await memory_mediator.store(memory, rbac_context)
        return result

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to store memory")

@router.get("/retrieve", response_model=Optional[MemoryResponse])
async def retrieve_memory(
    memory_id: str,
    memory_type: MemoryType | None = None
):
    """Retrieve a specific memory by ID"""
    try:
        memory = await memory_mediator.retrieve(memory_id, memory_type)

        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")

        return MemoryResponse(
            id=memory.id,
            type=memory.type,
            content=memory.content,
            metadata=memory.metadata,
            created_at=memory.created_at.isoformat(),
            updated_at=memory.updated_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve memory")

@router.post("/search", response_model=list[MemoryResponse])
async def search_memories(request: SearchRequest):
    """Search for memories"""
    try:
        memories = await memory_mediator.search(
            query=request.query,
            memory_types=request.memory_types,
            time_range=(request.start_time, request.end_time) if request.start_time else None,
            limit=request.limit
        )

        return [
            MemoryResponse(
                id=memory.id,
                type=memory.type,
                content=memory.content,
                metadata=memory.metadata,
                created_at=memory.created_at.isoformat(),
                updated_at=memory.updated_at.isoformat()
            )
            for memory in memories
        ]

    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        raise HTTPException(status_code=500, detail="Failed to search memories")

@router.patch("/{memory_id}")
async def update_memory(
    memory_id: str,
    updates: dict[str, Any],
    x_user_context: str | None = Header(None)
):
    """Update an existing memory"""
    try:
        rbac_context = get_rbac_context(x_user_context)

        success = await memory_mediator.update(memory_id, updates, rbac_context)

        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")

        return {"status": "updated", "memory_id": memory_id}

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to update memory")

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    memory_type: MemoryType | None = None,
    x_user_context: str | None = Header(None)
):
    """Delete a memory"""
    try:
        rbac_context = get_rbac_context(x_user_context)

        success = await memory_mediator.delete(memory_id, memory_type, rbac_context)

        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")

        return {"status": "deleted", "memory_id": memory_id}

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete memory")

@router.get("/stats", response_model=StatsResponse)
async def get_memory_stats():
    """Get memory system statistics"""
    try:
        stats = await memory_mediator.get_stats()
        return StatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@router.get("/health")
async def health_check():
    """Check memory system health"""
    try:
        # Initialize if not already done
        if not memory_mediator.redis_client:
            await memory_mediator.initialize()

        # Check Redis
        await memory_mediator.redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"

    stats = await memory_mediator.get_stats()

    return {
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "components": {
            "redis": redis_status,
            "snowflake": "not_implemented",
            "vector_db": "not_implemented"
        },
        "cache_stats": stats
    }
