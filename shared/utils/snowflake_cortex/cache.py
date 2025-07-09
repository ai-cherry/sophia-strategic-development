"""Cache module for Cortex results."""

import hashlib
import json
import os
from typing import Any, Optional

import redis.asyncio as aioredis


class CortexCache:
    """Redis-based cache for Cortex results."""

    def __init__(
        self, redis_url: Optional[str] = None, ttl: int = 3600, prefix: str = "cortex:"
    ):
        """Initialize cache.

        Args:
            redis_url: Redis connection URL
            ttl: Default TTL in seconds
            prefix: Key prefix for all cache entries
        """
        self._redis_url = redis_url or os.getenv(
            "REDIS_MCP_URL", "redis://redis-cache:9120"
        )
        self._ttl = ttl
        self._prefix = prefix
        self._redis: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        if not self._redis:
            self._redis = await aioredis.from_url(
                self._redis_url, decode_responses=False
            )

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _generate_key(
        self, task_type: str, prompt: str, model: Optional[str] = None, **kwargs: Any
    ) -> str:
        """Generate cache key from parameters."""
        # Create a normalized representation
        key_data = {
            "task": task_type,
            "prompt": prompt.strip().lower(),
            "model": model,
            **kwargs,
        }

        # Sort keys for consistency
        key_str = json.dumps(key_data, sort_keys=True)

        # Generate hash
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]

        return f"{self._prefix}{task_type}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis:
            await self.connect()

        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
        except Exception:
            # Cache errors should not break functionality
            pass

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        if not self._redis:
            await self.connect()

        try:
            serialized = json.dumps(value)
            await self._redis.set(key, serialized, ex=ttl or self._ttl)
        except Exception:
            # Cache errors should not break functionality
            pass

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if not self._redis:
            await self.connect()

        try:
            await self._redis.delete(key)
        except Exception:
            pass

    async def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern."""
        if not self._redis:
            await self.connect()

        try:
            async for key in self._redis.scan_iter(match=f"{self._prefix}{pattern}*"):
                await self._redis.delete(key)
        except Exception:
            pass
