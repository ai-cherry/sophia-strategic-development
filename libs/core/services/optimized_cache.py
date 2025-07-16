#!/usr/bin/env python3
"""
Optimized Multi-Layer Caching System for Sophia AI
High-performance caching with TTL, LRU eviction, and Redis integration
"""

import asyncio
import json
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

import contextlib

from backend.core.auto_esc_config import get_config_value as config

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache level enumeration"""

    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_PERSISTENT = "l3_persistent"

@dataclass
class CacheMetrics:
    """Cache performance metrics"""

    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    total_sets: int = 0
    total_gets: int = 0
    evictions: int = 0
    avg_get_time_ms: float = 0.0
    avg_set_time_ms: float = 0.0

    @property
    def hit_ratio(self) -> float:
        total_requests = self.total_gets
        if total_requests == 0:
            return 0.0
        total_hits = self.l1_hits + self.l2_hits
        return total_hits / total_requests

    @property
    def l1_hit_ratio(self) -> float:
        total_requests = self.total_gets
        if total_requests == 0:
            return 0.0
        return self.l1_hits / total_requests

@dataclass
class CacheEntry:
    """Cache entry with metadata"""

    value: Any
    created_at: float
    ttl: int | None = None
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size_bytes: int = 0

    @property
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)

    def touch(self) -> None:
        """Update access metadata"""
        self.access_count += 1
        self.last_accessed = time.time()

class LRUCache:
    """High-performance LRU cache with TTL support"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Get value from LRU cache"""
        async with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # Check expiration
            if entry.is_expired:
                del self._cache[key]
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()

            return entry.value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in LRU cache"""
        async with self._lock:
            # Calculate size
            try:
                size_bytes = len(json.dumps(value, default=str).encode("utf-8"))
            except Exception:
                size_bytes = 1024  # Default estimate

            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=ttl or self.default_ttl,
                size_bytes=size_bytes,
            )

            # Remove if exists
            if key in self._cache:
                del self._cache[key]

            # Add new entry
            self._cache[key] = entry

            # Evict if necessary
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all entries"""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        expired_keys = []
        async with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

        return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_size = sum(entry.size_bytes for entry in self._cache.values())
        return {
            "entries": len(self._cache),
            "max_size": self.max_size,
            "total_size_bytes": total_size,
            "avg_size_bytes": total_size / len(self._cache) if self._cache else 0,
        }

class OptimizedHierarchicalCache:
    """
    High-performance multi-layer cache system

    Features:
    - L1: In-memory LRU cache with TTL
    - L2: Redis distributed cache
    - Automatic cache warming and invalidation
    - Performance monitoring and metrics
    - Batch operations for efficiency
    """

    def __init__(
        self,
        l1_max_size: int = 1000,
        l1_default_ttl: int = 300,  # 5 minutes
        l2_default_ttl: int = 3600,  # 1 hour
        enable_redis: bool = True,
    ):
        # L1 Cache (Memory)
        self.l1_cache = LRUCache(max_size=l1_max_size, default_ttl=l1_default_ttl)

        # L2 Cache (Redis)
        self.redis_client: redis.Redis | None = None
        self.enable_redis = enable_redis and REDIS_AVAILABLE
        self.l2_default_ttl = l2_default_ttl

        # Metrics
        self.metrics = CacheMetrics()
        self._get_times: list[float] = []
        self._set_times: list[float] = []
        self._max_metrics_history = 1000

        # Background tasks
        self._cleanup_task: asyncio.Task | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize cache system"""
        if self._initialized:
            return

        try:
            # Initialize Redis if enabled
            if self.enable_redis:
                await self._initialize_redis()

            # Start background cleanup task
            self._cleanup_task = asyncio.create_task(self._background_cleanup())

            self._initialized = True
            logger.info("✅ Optimized cache system initialized")

        except Exception as e:
            logger.exception(f"❌ Failed to initialize cache system: {e}")
            raise

    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            redis_config = {
                "host": config.get("redis_host", "localhost"),
                "port": int(config.get("redis_port", 6379)),
                "db": int(config.get("redis_db", 0)),
                "decode_responses": True,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
                "retry_on_timeout": True,
                "health_check_interval": 30,
            }

            # Add password if configured
            redis_password = config.get("redis_password")
            if redis_password:
                redis_config["password"] = redis_password

            self.redis_client = redis.Redis(**redis_config)

            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis cache initialized successfully")

        except Exception as e:
            logger.warning(f"⚠️ Redis initialization failed, using L1 cache only: {e}")
            self.redis_client = None
            self.enable_redis = False

    async def get(self, key: str, namespace: str = "default") -> Any | None:
        """
        Get value from hierarchical cache

        Args:
            key: Cache key
            namespace: Cache namespace for organization

        Returns:
            Cached value or None if not found
        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()
        full_key = f"{namespace}:{key}"

        try:
            self.metrics.total_gets += 1

            # L1 Cache (Memory) - fastest
            l1_value = await self.l1_cache.get(full_key)
            if l1_value is not None:
                self.metrics.l1_hits += 1
                self._track_get_time(time.time() - start_time)
                return l1_value

            self.metrics.l1_misses += 1

            # L2 Cache (Redis) - if available
            if self.redis_client:
                try:
                    l2_value_str = await self.redis_client.get(full_key)
                    if l2_value_str:
                        # Deserialize value
                        l2_value = json.loads(l2_value_str)

                        # Populate L1 cache
                        await self.l1_cache.set(
                            full_key, l2_value, ttl=300
                        )  # 5 min L1 TTL

                        self.metrics.l2_hits += 1
                        self._track_get_time(time.time() - start_time)
                        return l2_value

                    self.metrics.l2_misses += 1

                except Exception as e:
                    logger.warning(f"Redis get error for key {full_key}: {e}")
                    self.metrics.l2_misses += 1

            # Cache miss
            self._track_get_time(time.time() - start_time)
            return None

        except Exception as e:
            logger.exception(f"Cache get error for key {full_key}: {e}")
            self._track_get_time(time.time() - start_time)
            return None

    async def set(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        ttl: int | None = None,
    ) -> None:
        """
        Set value in hierarchical cache

        Args:
            key: Cache key
            value: Value to cache
            namespace: Cache namespace
            ttl: Time to live in seconds
        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()
        full_key = f"{namespace}:{key}"

        try:
            self.metrics.total_sets += 1

            # Set in L1 cache
            l1_ttl = min(ttl or 300, 300)  # Max 5 minutes for L1
            await self.l1_cache.set(full_key, value, ttl=l1_ttl)

            # Set in L2 cache (Redis) if available
            if self.redis_client:
                try:
                    value_str = json.dumps(value, default=str)
                    l2_ttl = ttl or self.l2_default_ttl
                    await self.redis_client.setex(full_key, l2_ttl, value_str)

                except Exception as e:
                    logger.warning(f"Redis set error for key {full_key}: {e}")

            self._track_set_time(time.time() - start_time)

        except Exception as e:
            logger.exception(f"Cache set error for key {full_key}: {e}")
            self._track_set_time(time.time() - start_time)

    async def get_many(
        self, keys: list[str], namespace: str = "default"
    ) -> dict[str, Any]:
        """
        Get multiple values efficiently

        Args:
            keys: List of cache keys
            namespace: Cache namespace

        Returns:
            Dictionary of key-value pairs found in cache
        """
        results = {}
        missing_keys = []

        # Check L1 cache first
        for key in keys:
            value = await self.get(key, namespace)
            if value is not None:
                results[key] = value
            else:
                missing_keys.append(key)

        # Batch fetch from Redis for missing keys
        if missing_keys and self.redis_client:
            try:
                full_keys = [f"{namespace}:{key}" for key in missing_keys]
                redis_values = await self.redis_client.mget(full_keys)

                for key, redis_value in zip(missing_keys, redis_values, strict=False):
                    if redis_value:
                        try:
                            value = json.loads(redis_value)
                            results[key] = value

                            # Populate L1 cache
                            full_key = f"{namespace}:{key}"
                            await self.l1_cache.set(full_key, value, ttl=300)

                        except json.JSONDecodeError:
                            continue

            except Exception as e:
                logger.warning(f"Batch Redis get error: {e}")

        return results

    async def set_many(
        self,
        items: dict[str, Any],
        namespace: str = "default",
        ttl: int | None = None,
    ) -> None:
        """
        Set multiple values efficiently

        Args:
            items: Dictionary of key-value pairs to cache
            namespace: Cache namespace
            ttl: Time to live in seconds
        """
        # Set in L1 cache
        for key, value in items.items():
            await self.set(key, value, namespace, ttl)

    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete key from all cache levels"""
        full_key = f"{namespace}:{key}"

        # Delete from L1
        l1_deleted = await self.l1_cache.delete(full_key)

        # Delete from L2 (Redis)
        l2_deleted = False
        if self.redis_client:
            try:
                l2_deleted = bool(await self.redis_client.delete(full_key))
            except Exception as e:
                logger.warning(f"Redis delete error for key {full_key}: {e}")

        return l1_deleted or l2_deleted

    async def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace"""
        cleared_count = 0

        # Clear from Redis first (get pattern)
        if self.redis_client:
            try:
                pattern = f"{namespace}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    cleared_count += await self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis namespace clear error: {e}")

        # Clear from L1 cache
        # Note: This is inefficient for L1, but necessary for consistency
        await self.l1_cache.clear()  # Clear all L1 for simplicity

        return cleared_count

    async def get_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics"""
        l1_stats = self.l1_cache.get_stats()

        redis_stats = {}
        if self.redis_client:
            try:
                redis_info = await self.redis_client.info("memory")
                redis_stats = {
                    "used_memory": redis_info.get("used_memory", 0),
                    "used_memory_human": redis_info.get("used_memory_human", "0B"),
                    "connected_clients": redis_info.get("connected_clients", 0),
                }
            except Exception as e:
                redis_stats = {"error": str(e)}

        return {
            "metrics": {
                "hit_ratio": round(self.metrics.hit_ratio, 3),
                "l1_hit_ratio": round(self.metrics.l1_hit_ratio, 3),
                "l1_hits": self.metrics.l1_hits,
                "l1_misses": self.metrics.l1_misses,
                "l2_hits": self.metrics.l2_hits,
                "l2_misses": self.metrics.l2_misses,
                "total_gets": self.metrics.total_gets,
                "total_sets": self.metrics.total_sets,
                "avg_get_time_ms": round(self.metrics.avg_get_time_ms, 2),
                "avg_set_time_ms": round(self.metrics.avg_set_time_ms, 2),
            },
            "l1_cache": l1_stats,
            "l2_cache": redis_stats,
            "configuration": {
                "redis_enabled": self.enable_redis,
                "l1_max_size": self.l1_cache.max_size,
                "l2_default_ttl": self.l2_default_ttl,
            },
        }

    def _track_get_time(self, time_seconds: float) -> None:
        """Track get operation time"""
        time_ms = time_seconds * 1000
        self._get_times.append(time_ms)
        if len(self._get_times) > self._max_metrics_history:
            self._get_times.pop(0)

        self.metrics.avg_get_time_ms = sum(self._get_times) / len(self._get_times)

    def _track_set_time(self, time_seconds: float) -> None:
        """Track set operation time"""
        time_ms = time_seconds * 1000
        self._set_times.append(time_ms)
        if len(self._set_times) > self._max_metrics_history:
            self._set_times.pop(0)

        self.metrics.avg_set_time_ms = sum(self._set_times) / len(self._set_times)

    async def _background_cleanup(self) -> None:
        """Background task for cache maintenance"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                # Cleanup expired entries from L1
                expired_count = await self.l1_cache.cleanup_expired()
                if expired_count > 0:
                    logger.debug(f"Cleaned up {expired_count} expired L1 cache entries")

                # Redis handles its own TTL cleanup

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Background cleanup error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def close(self) -> None:
        """Close cache system and cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

        if self.redis_client:
            await self.redis_client.close()

        await self.l1_cache.clear()
        logger.info("🔒 Cache system closed")

# Global cache instance
optimized_cache = OptimizedHierarchicalCache()

# Convenience functions
async def get_cached(key: str, namespace: str = "default") -> Any | None:
    """Get value from global cache"""
    return await optimized_cache.get(key, namespace)

async def set_cached(
    key: str, value: Any, namespace: str = "default", ttl: int | None = None
) -> None:
    """Set value in global cache"""
    await optimized_cache.set(key, value, namespace, ttl)

async def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics"""
    return await optimized_cache.get_stats()
