"""
Redis Helper Module
Provides consistent Redis operations with metrics and vector caching

Date: July 10, 2025
"""

import json
import logging
from typing import Any, Optional
from datetime import datetime
import redis
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
cache_hits = Counter("redis_cache_hits_total", "Total cache hits")
cache_misses = Counter("redis_cache_misses_total", "Total cache misses")
cache_errors = Counter("redis_cache_errors_total", "Total cache errors", ["operation"])
cache_latency = Histogram(
    "redis_cache_latency_seconds", "Cache operation latency", ["operation"]
)

class RedisHelper:
    """Helper class for consistent Redis operations with metrics"""

    def __init__(self, client: redis.Redis, default_ttl: int = 3600):
        """
        Initialize Redis helper

        Args:
            client: Redis client instance
            default_ttl: Default TTL in seconds (1 hour)
        """
        self.client = client
        self.default_ttl = default_ttl

    @cache_latency.labels(operation="get").time()
    async def cache_get(self, key: str) -> Optional[Any]:
        """
        Get value from cache with metrics

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            value = self.client.get(key)
            if value:
                cache_hits.inc()
                return json.loads(value)
            else:
                cache_misses.inc()
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            cache_errors.labels(operation="get").inc()
            return None

    @cache_latency.labels(operation="set").time()
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if not specified)

        Returns:
            Success status
        """
        try:
            ttl = ttl or self.default_ttl
            self.client.setex(
                key,
                ttl,
                json.dumps(value, default=str),  # Handle datetime serialization
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            cache_errors.labels(operation="set").inc()
            return False

    @cache_latency.labels(operation="delete").time()
    async def cache_delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            Success status
        """
        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            cache_errors.labels(operation="delete").inc()
            return False

    async def cache_vector(self, key: str, vector: list[float], metadata: dict) -> bool:
        """
        Cache vector with metadata for fast retrieval

        Args:
            key: Vector cache key
            vector: Vector embeddings
            metadata: Associated metadata

        Returns:
            Success status
        """
        cache_data = {
            "vector": vector,
            "metadata": metadata,
            "cached_at": datetime.utcnow().isoformat(),
            "dimension": len(vector),
        }

        # Use longer TTL for vectors (2 hours)
        return await self.cache_set(f"vector:{key}", cache_data, ttl=7200)

    async def get_cached_vector(self, key: str) -> Optional[dict]:
        """
        Get cached vector with metadata

        Args:
            key: Vector cache key

        Returns:
            Dict with vector and metadata or None
        """
        return await self.cache_get(f"vector:{key}")

    async def cache_search_results(
        self, query_hash: str, results: list[dict], ttl: int = 1800
    ) -> bool:
        """
        Cache search results

        Args:
            query_hash: Hash of the search query
            results: Search results to cache
            ttl: Cache duration (default 30 minutes)

        Returns:
            Success status
        """
        cache_data = {
            "results": results,
            "cached_at": datetime.utcnow().isoformat(),
            "count": len(results),
        }
        return await self.cache_set(f"search:{query_hash}", cache_data, ttl=ttl)

    async def get_cached_search_results(self, query_hash: str) -> Optional[list[dict]]:
        """
        Get cached search results

        Args:
            query_hash: Hash of the search query

        Returns:
            Cached results or None
        """
        cached = await self.cache_get(f"search:{query_hash}")
        if cached:
            return cached.get("results", [])
        return None

    async def get_cache_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dict with cache statistics
        """
        try:
            info = self.client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0)
                    / max(
                        1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)
                    )
                    * 100,
                    2,
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
