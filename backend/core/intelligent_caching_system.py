#!/usr/bin/env python3
"""
Intelligent Caching System for Sophia AI
Multi-layer caching with TTL, invalidation, and performance optimization
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache level enumeration"""

    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""

    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: int

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return (datetime.now() - self.created_at).seconds > self.ttl_seconds

    def is_stale(self, staleness_threshold: int = 3600) -> bool:
        """Check if cache entry is stale"""
        return (datetime.now() - self.last_accessed).seconds > staleness_threshold


class IntelligentCache:
    """Multi-layer intelligent caching system"""

    def __init__(self):
        self.memory_cache: dict[str, CacheEntry] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_usage_mb": 0,
        }
        self.max_memory_entries = 1000
        self.default_ttl = 300  # 5 minutes

    async def get(self, key: str) -> Any | None:
        """Get value from cache with intelligent retrieval"""

        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]

            if not entry.is_expired():
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self.cache_stats["hits"] += 1
                logger.debug(f"Cache hit for key: {key}")
                return entry.data
            else:
                # Remove expired entry
                del self.memory_cache[key]
                logger.debug(f"Removed expired cache entry: {key}")

        # Cache miss
        self.cache_stats["misses"] += 1
        logger.debug(f"Cache miss for key: {key}")
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache with intelligent storage"""
        ttl = ttl or self.default_ttl

        # Create cache entry
        entry = CacheEntry(
            data=value,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            ttl_seconds=ttl,
        )

        # Check if we need to evict entries
        if len(self.memory_cache) >= self.max_memory_entries:
            await self._evict_least_used()

        self.memory_cache[key] = entry
        logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")
        return True

    async def invalidate(self, key: str) -> bool:
        """Invalidate cache entry"""
        if key in self.memory_cache:
            del self.memory_cache[key]
            logger.debug(f"Invalidated cache key: {key}")
            return True
        return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        keys_to_remove = [key for key in self.memory_cache if pattern in key]

        for key in keys_to_remove:
            del self.memory_cache[key]

        logger.debug(
            f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}"
        )
        return len(keys_to_remove)

    async def _evict_least_used(self):
        """Evict least recently used cache entries"""
        if not self.memory_cache:
            return

        # Sort by last accessed time and access count
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: (x[1].last_accessed, x[1].access_count),
        )

        # Remove oldest 10% of entries
        entries_to_remove = max(1, len(sorted_entries) // 10)

        for i in range(entries_to_remove):
            key, _ = sorted_entries[i]
            del self.memory_cache[key]
            self.cache_stats["evictions"] += 1

        logger.debug(f"Evicted {entries_to_remove} cache entries")

    async def cleanup_expired(self):
        """Clean up expired cache entries"""
        expired_keys = [
            key for key, entry in self.memory_cache.items() if entry.is_expired()
        ]

        for key in expired_keys:
            del self.memory_cache[key]

        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / total_requests if total_requests > 0 else 0.0
        )

        return {
            "hit_rate": hit_rate,
            "total_entries": len(self.memory_cache),
            "stats": self.cache_stats,
            "memory_usage_estimate_mb": len(self.memory_cache)
            * 0.001,  # Rough estimate
            "timestamp": datetime.now().isoformat(),
        }


class CacheDecorator:
    """Decorator for automatic caching of function results"""

    def __init__(self, cache: IntelligentCache):
        self.cache = cache

    def cached(self, ttl: int = 300, key_prefix: str = "", invalidate_on: list = None):
        """Decorator for caching function results"""

        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = (
                    f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
                )

                # Try to get from cache
                cached_result = await self.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.cache.set(cache_key, result, ttl)

                return result

            return wrapper

        return decorator


# Global instances
intelligent_cache = IntelligentCache()
cache_decorator = CacheDecorator(intelligent_cache)


# Background cleanup task
async def cache_cleanup_task():
    """Background task for cache maintenance"""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            await intelligent_cache.cleanup_expired()
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")


# Start cleanup task
asyncio.create_task(cache_cleanup_task())
