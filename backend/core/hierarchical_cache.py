"""Hierarchical 3-Tier Caching System.

Implements L1 (Memory), L2 (Redis), and L3 (Database) caching for optimal performance
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

import aioredis
from cachetools import TTLCache
from pydantic import BaseModel, Field

from backend.core.auto_esc_config import config
from backend.monitoring.observability import logger


class CacheTier(str, Enum):
    """Cache tier levels"""
        L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"


class CacheStrategy(str, Enum):
    """Cache strategies"""
        WRITE_THROUGH = "write_through"

    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"


class CacheMetrics(BaseModel):
    """Cache performance metrics"""
        hits: int = 0

    misses: int = 0
    evictions: int = 0
    writes: int = 0
    avg_latency_ms: float = 0.0
    memory_usage_mb: float = 0.0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class CacheEntry(BaseModel):
    """Cache entry with metadata"""
        key: str

    value: Any
    tier: CacheTier
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    tags: List[str] = []

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:

            return False
        expiry = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() > expiry


class HierarchicalCache:
    """3-tier hierarchical caching system"""
    def __init__(.

        self,
        l1_max_size: int = 1000,
        l1_ttl_seconds: int = 300,  # 5 minutes
        l2_ttl_seconds: int = 3600,  # 1 hour
        l3_ttl_seconds: int = 86400,  # 24 hours
        strategy: CacheStrategy = CacheStrategy.WRITE_THROUGH,
    ):
        # L1: In-memory cache
        self.l1_cache = TTLCache(maxsize=l1_max_size, ttl=l1_ttl_seconds)
        self.l1_ttl = l1_ttl_seconds

        # L2: Redis cache
        self.l2_client: Optional[aioredis.Redis] = None
        self.l2_ttl = l2_ttl_seconds

        # L3: Database cache (reference only, actual implementation in database layer)
        self.l3_ttl = l3_ttl_seconds

        # Configuration
        self.strategy = strategy
        self.metrics: Dict[CacheTier, CacheMetrics] = {
            tier: CacheMetrics() for tier in CacheTier
        }

        # Warm-up tracking
        self._warm_keys: Set[str] = set()
        self._access_patterns: Dict[str, List[float]] = {}

        self._initialized = False

    async def initialize(self):
        """Initialize cache components"""
        if self._initialized:

            return

        # Initialize Redis connection
        self.l2_client = await aioredis.create_redis_pool(
            config.redis_url or "redis://localhost:6379", encoding="utf-8"
        )

        # Start background tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._adaptive_optimization())

        self._initialized = True
        logger.info("Hierarchical cache initialized")

    async def get(
        self,
        key: str,
        fetch_fn: Optional[Callable] = None,
        ttl_override: Optional[Dict[CacheTier, int]] = None,
    ) -> Optional[Any]:
        """Get value from cache with hierarchical lookup"""
await self.initialize()

        start_time = time.time()

        # Track access pattern
        self._track_access(key)

        # L1 lookup
        value = await self._get_l1(key)
        if value is not None:
            self._record_hit(CacheTier.L1_MEMORY, time.time() - start_time)
            return value

        # L2 lookup
        value = await self._get_l2(key)
        if value is not None:
            self._record_hit(CacheTier.L2_REDIS, time.time() - start_time)
            # Promote to L1
            await self._set_l1(key, value, ttl_override)
            return value

        # L3 lookup
        value = await self._get_l3(key)
        if value is not None:
            self._record_hit(CacheTier.L3_DATABASE, time.time() - start_time)
            # Promote to L1 and L2
            await self._set_l1(key, value, ttl_override)
            await self._set_l2(key, value, ttl_override)
            return value

        # Cache miss - fetch if function provided
        if fetch_fn:
            value = await fetch_fn()
            if value is not None:
                await self.set(key, value, ttl_override)
            return value

        # Record miss
        self._record_miss(time.time() - start_time)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_override: Optional[Dict[CacheTier, int]] = None,
        tags: Optional[List[str]] = None,
    ):
        """Set value in cache based on strategy"""
await self.initialize()

        ttls = ttl_override or {}

        if self.strategy == CacheStrategy.WRITE_THROUGH:
            # Write to all tiers
            await asyncio.gather(
                self._set_l1(key, value, ttls.get(CacheTier.L1_MEMORY)),
                self._set_l2(key, value, ttls.get(CacheTier.L2_REDIS)),
                self._set_l3(key, value, ttls.get(CacheTier.L3_DATABASE), tags),
            )
        elif self.strategy == CacheStrategy.WRITE_BACK:
            # Write to L1 only, background sync to other tiers
            await self._set_l1(key, value, ttls.get(CacheTier.L1_MEMORY))
            asyncio.create_task(self._write_back(key, value, ttls, tags))
        elif self.strategy == CacheStrategy.WRITE_AROUND:
            # Write to L3 only
            await self._set_l3(key, value, ttls.get(CacheTier.L3_DATABASE), tags)

    async def invalidate(self, key: str):
        """Invalidate entry across all tiers"""
await self.initialize()

        await asyncio.gather(
            self._invalidate_l1(key), self._invalidate_l2(key), self._invalidate_l3(key)
        )

    async def invalidate_by_tag(self, tag: str):
        """Invalidate all entries with a specific tag"""
await self.initialize()

        # Get all keys with tag from L3
        keys = await self._get_keys_by_tag(tag)

        # Invalidate all keys
        tasks = []
        for key in keys:
            tasks.append(self.invalidate(key))

        await asyncio.gather(*tasks)

    async def warm_cache(self, keys: List[str], fetch_fn: Callable):
        """Pre-warm cache with specific keys"""

    await self.initialize()

        tasks = []
        for key in keys:
            self._warm_keys.add(key)
            tasks.append(self.get(key, fetch_fn))

        await asyncio.gather(*tasks)
        logger.info(f"Warmed cache with {len(keys)} keys")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        metrics = {}

        for tier, metric in self.metrics.items():
            metrics[tier.value] = {
                "hit_rate": metric.hit_rate,
                "hits": metric.hits,
                "misses": metric.misses,
                "evictions": metric.evictions,
                "writes": metric.writes,
                "avg_latency_ms": metric.avg_latency_ms,
                "memory_usage_mb": metric.memory_usage_mb,
            }

        # Add L1 specific metrics
        metrics["l1_memory"]["size"] = len(self.l1_cache)
        metrics["l1_memory"]["max_size"] = self.l1_cache.maxsize

        # Add warm key metrics
        metrics["warm_keys"] = {
            "count": len(self._warm_keys),
            "keys": list(self._warm_keys)[:10],  # Sample
        }

        return metrics

    # L1 Operations
    async def _get_l1(self, key: str) -> Optional[Any]:
        """Get from L1 memory cache"""
        try:
except Exception:
    pass
            value = self.l1_cache.get(key)
            if value is not None:
                return json.loads(value) if isinstance(value, str) else value
        except KeyError:
            pass
        return None

    async def _set_l1(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set in L1 memory cache"""
        try:
    except Exception:
        pass
            serialized = json.dumps(value) if not isinstance(value, str) else value
            self.l1_cache[key] = serialized
            self.metrics[CacheTier.L1_MEMORY].writes += 1
        except Exception as e:
            logger.error(f"L1 set error: {e}")

    async def _invalidate_l1(self, key: str):
        """Invalidate L1 entry"""
        try:
except Exception:
    pass
            del self.l1_cache[key]
            self.metrics[CacheTier.L1_MEMORY].evictions += 1
        except KeyError:
            pass

    # L2 Operations
    async def _get_l2(self, key: str) -> Optional[Any]:
        """Get from L2 Redis cache"""
        if not self.l2_client:

            return None

        try:
        except Exception:
            pass
            value = await self.l2_client.get(f"cache:{key}")
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"L2 get error: {e}")
        return None

    async def _set_l2(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set in L2 Redis cache"""
        if not self.l2_client:

            return

        try:
        except Exception:
            pass
            serialized = json.dumps(value)
            ttl = ttl or self.l2_ttl
            await self.l2_client.setex(f"cache:{key}", ttl, serialized)
            self.metrics[CacheTier.L2_REDIS].writes += 1
        except Exception as e:
            logger.error(f"L2 set error: {e}")

    async def _invalidate_l2(self, key: str):
        """Invalidate L2 entry"""
        if not self.l2_client:

            return

        try:
        except Exception:
            pass
            await self.l2_client.delete(f"cache:{key}")
            self.metrics[CacheTier.L2_REDIS].evictions += 1
        except Exception as e:
            logger.error(f"L2 invalidate error: {e}")

    # L3 Operations (placeholder - actual implementation in database layer)
    async def _get_l3(self, key: str) -> Optional[Any]:
        """Get from L3 database cache"""
        # This would be implemented by the database layer
# For now, return None
        return None

    async def _set_l3(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ):
        """Set in L3 database cache"""
        # This would be implemented by the database layer.
self.metrics[CacheTier.L3_DATABASE].writes += 1

    async def _invalidate_l3(self, key: str):
        """Invalidate L3 entry"""
        # This would be implemented by the database layer.
self.metrics[CacheTier.L3_DATABASE].evictions += 1

    async def _get_keys_by_tag(self, tag: str) -> List[str]:
        """Get all keys with a specific tag from L3"""
        # This would be implemented by the database layer
return []

    # Helper methods
    def _track_access(self, key: str):
        """Track access patterns for optimization"""
        now = time.time()

        if key not in self._access_patterns:
            self._access_patterns[key] = []
        self._access_patterns[key].append(now)

        # Keep only recent accesses (last hour)
        cutoff = now - 3600
        self._access_patterns[key] = [
            t for t in self._access_patterns[key] if t > cutoff
        ]

    def _record_hit(self, tier: CacheTier, latency: float):
        """Record cache hit metrics"""
        metrics = self.metrics[tier].

        metrics.hits += 1
        metrics.avg_latency_ms = (
            metrics.avg_latency_ms * (metrics.hits - 1) + latency * 1000
        ) / metrics.hits

    def _record_miss(self, latency: float):
        """Record cache miss metrics"""
for metrics in self.metrics.values():

            metrics.misses += 1

    async def _write_back(
        self,
        key: str,
        value: Any,
        ttls: Dict[CacheTier, int],
        tags: Optional[List[str]],
    ):
        """Background write to L2 and L3"""
await asyncio.sleep(0.1)  # Small delay to batch writes.

        await asyncio.gather(
            self._set_l2(key, value, ttls.get(CacheTier.L2_REDIS)),
            self._set_l3(key, value, ttls.get(CacheTier.L3_DATABASE), tags),
        )

    async def _monitor_performance(self):
        """Monitor cache performance and adjust parameters"""

    while True:

            await asyncio.sleep(60)  # Check every minute

            # Update memory usage
            import sys

            self.metrics[CacheTier.L1_MEMORY].memory_usage_mb = (
                sys.getsizeof(self.l1_cache) / 1024 / 1024
            )

            # Log metrics
            metrics = await self.get_metrics()
            logger.info(f"Cache metrics: {metrics}")

    async def _adaptive_optimization(self):
        """Adaptively optimize cache based on access patterns"""

    while True:

            await asyncio.sleep(300)  # Run every 5 minutes

            # Identify hot keys
            hot_keys = []
            for key, accesses in self._access_patterns.items():
                if len(accesses) > 10:  # More than 10 accesses in last hour
                    hot_keys.append((key, len(accesses)))

            # Sort by access count
            hot_keys.sort(key=lambda x: x[1], reverse=True)

            # Pre-warm top keys if not already warm
            for key, _ in hot_keys[:20]:
                if key not in self._warm_keys:
                    self._warm_keys.add(key)
                    # Ensure hot keys are in L1
                    value = await self._get_l2(key) or await self._get_l3(key)
                    if value:
                        await self._set_l1(key, value)

            logger.info(f"Identified {len(hot_keys)} hot keys for optimization")


# Global cache instance
hierarchical_cache = HierarchicalCache()


# Decorator for automatic caching
def cached(
    ttl: Optional[Dict[CacheTier, int]] = None,
    key_prefix: str = "",
    tags: Optional[List[str]] = None,
):
    """Decorator for automatic method caching"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            result = await hierarchical_cache.get(cache_key)
            if result is not None:
                return result

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None:
                await hierarchical_cache.set(cache_key, result, ttl, tags)

            return result

        return wrapper

    return decorator
