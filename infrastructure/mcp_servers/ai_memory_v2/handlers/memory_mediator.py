"""
Memory Mediator for AI Memory V2 MCP Server
Provides unified interface for memory operations across Redis, Snowflake, and Vector DBs
"""

import hashlib
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any

import redis.asyncio as redis
from pydantic import BaseModel, Field

from ..config import settings

logger = logging.getLogger(__name__)


# Memory Types
class MemoryType(str, Enum):
    CHAT = "chat"
    EVENT = "event"
    INSIGHT = "insight"
    CONTEXT = "context"
    DECISION = "decision"


# Memory Schema Models
class BaseMemory(BaseModel):
    """Base memory schema"""

    id: str = Field(
        default_factory=lambda: hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()
    )
    type: MemoryType
    content: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ttl_seconds: int | None = None


class ChatMemory(BaseMemory):
    """Chat conversation memory"""

    type: MemoryType = MemoryType.CHAT
    user_id: str
    session_id: str
    message: str
    response: str
    sentiment: float | None = None
    topics: list[str] = Field(default_factory=list)


class EventMemory(BaseMemory):
    """System event memory"""

    type: MemoryType = MemoryType.EVENT
    source: str
    event_type: str
    severity: str = "info"


class InsightMemory(BaseMemory):
    """Business insight memory"""

    type: MemoryType = MemoryType.INSIGHT
    category: str
    confidence: float = Field(ge=0, le=1)
    recommendations: list[str] = Field(default_factory=list)


# Memory Mediator
class MemoryMediator:
    """
    Unified memory access layer that handles:
    - Redis for hot cache (L1)
    - Snowflake for analytics (L2)
    - Vector DB for semantic search (L3)
    """

    def __init__(self):
        self.redis_client: redis.Redis | None = None
        self.cache_ttl = {
            MemoryType.CHAT: 3600,  # 1 hour
            MemoryType.EVENT: 7200,  # 2 hours
            MemoryType.INSIGHT: 86400,  # 24 hours
            MemoryType.CONTEXT: 1800,  # 30 minutes
            MemoryType.DECISION: 86400,  # 24 hours
        }
        self._cache_stats = {"hits": 0, "misses": 0, "writes": 0}

    async def initialize(self):
        """Initialize connections"""
        try:
            # Redis connection
            self.redis_client = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Memory Mediator initialized with Redis")

            # TODO: Initialize Snowflake connection
            # TODO: Initialize Vector DB connection

        except Exception as e:
            logger.exception(f"Failed to initialize Memory Mediator: {e}")
            raise

    async def store(
        self, memory: BaseMemory, rbac_context: dict | None = None
    ) -> dict[str, Any]:
        """
        Store memory with multi-tier strategy
        """
        try:
            # Validate RBAC if provided
            if rbac_context and not self._check_write_permission(memory, rbac_context):
                raise PermissionError("Insufficient permissions to store memory")

            # Serialize memory
            memory_dict = memory.dict()
            memory_json = json.dumps(memory_dict, default=str)

            # L1: Store in Redis with TTL
            cache_key = f"memory:{memory.type}:{memory.id}"
            ttl = memory.ttl_seconds or self.cache_ttl.get(memory.type, 3600)

            await self.redis_client.setex(cache_key, ttl, memory_json)

            # Store in sorted set for time-based queries
            score = memory.created_at.timestamp()
            await self.redis_client.zadd(
                f"memory:timeline:{memory.type}", {memory.id: score}
            )

            # L2: Queue for Snowflake write (via Estuary)
            await self._queue_for_persistence(memory_dict)

            # L3: Queue for vector embedding (if applicable)
            if memory.type in [MemoryType.CHAT, MemoryType.INSIGHT]:
                await self._queue_for_embedding(memory_dict)

            self._cache_stats["writes"] += 1

            logger.info(f"Stored memory {memory.id} of type {memory.type}")
            return {"id": memory.id, "status": "stored", "cache_ttl": ttl}

        except Exception as e:
            logger.exception(f"Failed to store memory: {e}")
            raise

    async def retrieve(
        self, memory_id: str, memory_type: MemoryType | None = None
    ) -> BaseMemory | None:
        """
        Retrieve memory with cache hierarchy
        """
        try:
            # L1: Check Redis
            cache_key = (
                f"memory:{memory_type}:{memory_id}"
                if memory_type
                else f"memory:*:{memory_id}"
            )

            if "*" in cache_key:
                # Search across all types
                keys = await self.redis_client.keys(cache_key)
                if keys:
                    cache_key = keys[0]

            cached = await self.redis_client.get(cache_key)

            if cached:
                self._cache_stats["hits"] += 1
                memory_dict = json.loads(cached)
                return self._deserialize_memory(memory_dict)

            self._cache_stats["misses"] += 1

            # L2: Check Snowflake (TODO)
            # memory_dict = await self._fetch_from_snowflake(memory_id)

            # L3: Check Vector DB (TODO)
            # if not memory_dict:
            #     memory_dict = await self._fetch_from_vector_db(memory_id)

            return None

        except Exception as e:
            logger.exception(f"Failed to retrieve memory: {e}")
            return None

    async def search(
        self,
        query: str,
        memory_types: list[MemoryType] | None = None,
        time_range: tuple | None = None,
        limit: int = 10,
    ) -> list[BaseMemory]:
        """
        Search memories with multiple strategies
        """
        results = []

        try:
            # Time-based search from Redis
            if time_range:
                start_ts = (
                    time_range[0].timestamp()
                    if isinstance(time_range[0], datetime)
                    else time_range[0]
                )
                end_ts = (
                    time_range[1].timestamp()
                    if isinstance(time_range[1], datetime)
                    else time_range[1]
                )

                types_to_search = memory_types or list(MemoryType)

                for mem_type in types_to_search:
                    timeline_key = f"memory:timeline:{mem_type}"
                    memory_ids = await self.redis_client.zrangebyscore(
                        timeline_key, start_ts, end_ts, start=0, num=limit
                    )

                    for mem_id in memory_ids:
                        memory = await self.retrieve(mem_id, mem_type)
                        if memory:
                            results.append(memory)

            # TODO: Semantic search via Vector DB
            # TODO: Full-text search via Snowflake

            return results[:limit]

        except Exception as e:
            logger.exception(f"Search failed: {e}")
            return []

    async def update(
        self,
        memory_id: str,
        updates: dict[str, Any],
        rbac_context: dict | None = None,
    ) -> bool:
        """
        Update existing memory
        """
        try:
            # Retrieve current memory
            memory = await self.retrieve(memory_id)
            if not memory:
                return False

            # Check permissions
            if rbac_context and not self._check_write_permission(memory, rbac_context):
                raise PermissionError("Insufficient permissions to update memory")

            # Apply updates
            memory_dict = memory.dict()
            memory_dict.update(updates)
            memory_dict["updated_at"] = datetime.utcnow()

            # Create updated memory object
            updated_memory = self._deserialize_memory(memory_dict)

            # Store updated version
            await self.store(updated_memory, rbac_context)

            return True

        except Exception as e:
            logger.exception(f"Failed to update memory: {e}")
            return False

    async def delete(
        self,
        memory_id: str,
        memory_type: MemoryType | None = None,
        rbac_context: dict | None = None,
    ) -> bool:
        """
        Delete memory (soft delete in Snowflake)
        """
        try:
            # Check permissions
            memory = await self.retrieve(memory_id, memory_type)
            if (
                memory
                and rbac_context
                and not self._check_write_permission(memory, rbac_context)
            ):
                raise PermissionError("Insufficient permissions to delete memory")

            # Remove from Redis
            cache_key = (
                f"memory:{memory_type}:{memory_id}"
                if memory_type
                else f"memory:*:{memory_id}"
            )

            if "*" in cache_key:
                keys = await self.redis_client.keys(cache_key)
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                await self.redis_client.delete(cache_key)

            # Remove from timeline
            if memory_type:
                await self.redis_client.zrem(
                    f"memory:timeline:{memory_type}", memory_id
                )

            # TODO: Soft delete in Snowflake

            return True

        except Exception as e:
            logger.exception(f"Failed to delete memory: {e}")
            return False

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_ops = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = self._cache_stats["hits"] / total_ops if total_ops > 0 else 0

        return {
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"],
            "cache_writes": self._cache_stats["writes"],
            "hit_rate": round(hit_rate, 3),
            "total_operations": total_ops,
        }

    # Private methods
    def _deserialize_memory(self, memory_dict: dict[str, Any]) -> BaseMemory:
        """Deserialize memory based on type"""
        memory_type = memory_dict.get("type")

        if memory_type == MemoryType.CHAT:
            return ChatMemory(**memory_dict)
        elif memory_type == MemoryType.EVENT:
            return EventMemory(**memory_dict)
        elif memory_type == MemoryType.INSIGHT:
            return InsightMemory(**memory_dict)
        else:
            return BaseMemory(**memory_dict)

    def _check_write_permission(self, memory: BaseMemory, rbac_context: dict) -> bool:
        """Check RBAC permissions"""
        user_role = rbac_context.get("role", "user")
        user_id = rbac_context.get("user_id")

        # CEO can write anything
        if user_role == "ceo":
            return True

        # Managers can write insights and decisions
        if user_role == "manager" and memory.type in [
            MemoryType.INSIGHT,
            MemoryType.DECISION,
        ]:
            return True

        # Users can only write their own chat memories
        if user_role == "user" and memory.type == MemoryType.CHAT:
            if isinstance(memory, ChatMemory) and memory.user_id == user_id:
                return True

        return False

    async def _queue_for_persistence(self, memory_dict: dict[str, Any]):
        """Queue memory for Snowflake persistence via Estuary"""
        # This will be picked up by Estuary webhook
        webhook_event = {
            "id": memory_dict["id"],
            "type": "memory_created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": memory_dict,
        }

        # Store in Redis stream for Estuary pickup
        await self.redis_client.xadd(
            "estuary:memory:events", {"event": json.dumps(webhook_event)}, maxlen=10000
        )

    async def _queue_for_embedding(self, memory_dict: dict[str, Any]):
        """Queue memory for vector embedding"""
        # This will be processed by a background worker
        await self.redis_client.lpush(
            "memory:embedding:queue",
            json.dumps(
                {
                    "memory_id": memory_dict["id"],
                    "content": memory_dict.get("content", {}),
                    "type": memory_dict["type"],
                }
            ),
        )


# Singleton instance
memory_mediator = MemoryMediator()
