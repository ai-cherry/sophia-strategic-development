"""
Sophia AI Performance Optimization Configuration
Optimized for Vercel serverless deployment with focus on performance, stability, and quality.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cached_property
from typing import Any

import aiohttp

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """Performance configuration settings."""

    # Cache settings
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000

    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 20

    # Connection pooling
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30

    # Async settings
    max_concurrent_requests: int = 50
    request_timeout: int = 300

    # Memory optimization
    max_memory_usage: int = 512  # MB
    gc_threshold: int = 100

    # Response optimization
    compression_enabled: bool = True
    compression_level: int = 6

    # Monitoring
    metrics_enabled: bool = True
    profiling_enabled: bool = False


class PerformanceOptimizer:
    """Performance optimization utilities for Sophia AI."""

    def __init__(self, config: PerformanceConfig | None = None):
        self.config = config or PerformanceConfig()
        self._cache = {}
        self._cache_timestamps = {}
        self._request_counts = {}
        self._session_pool = None

    @cached_property
    def environment_config(self) -> dict[str, Any]:
        """Get cached environment configuration."""
        return {
            "sophia_env": get_config_value("sophia_env", "production"),
            "debug": get_config_value("debug", "false").lower() == "true",
            "log_level": get_config_value("log_level", "INFO"),
            "platform": get_config_value("platform", "vercel"),
            "cache_ttl": int(os.getenv("CACHE_TTL", self.config.cache_ttl)),
            "max_concurrent": int(
                os.getenv(
                    "MAX_CONCURRENT_REQUESTS", self.config.max_concurrent_requests
                )
            ),
            "request_timeout": int(
                os.getenv("REQUEST_TIMEOUT", self.config.request_timeout)
            ),
        }

    def cache_get(self, key: str) -> Any | None:
        """Get value from cache with TTL check."""
        if key not in self._cache:
            return None

        timestamp = self._cache_timestamps.get(key)
        if timestamp and datetime.utcnow() - timestamp > timedelta(
            seconds=self.config.cache_ttl
        ):
            # Cache expired
            del self._cache[key]
            del self._cache_timestamps[key]
            return None

        return self._cache[key]

    def cache_set(self, key: str, value: Any) -> None:
        """Set value in cache with timestamp."""
        # Implement LRU eviction if cache is full
        if len(self._cache) >= self.config.cache_max_size:
            # Remove oldest entry
            oldest_key = min(
                self._cache_timestamps.keys(), key=lambda k: self._cache_timestamps[k]
            )
            del self._cache[oldest_key]
            del self._cache_timestamps[oldest_key]

        self._cache[key] = value
        self._cache_timestamps[key] = datetime.utcnow()

    def cache_clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._cache_timestamps.clear()

    def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits."""
        now = datetime.utcnow()
        minute_key = f"{identifier}:{now.strftime('%Y-%m-%d:%H:%M')}"

        if minute_key not in self._request_counts:
            self._request_counts[minute_key] = 0

        # Clean old entries
        cutoff = now - timedelta(minutes=2)
        old_keys = [
            k
            for k in self._request_counts
            if datetime.strptime(k.split(":")[1], "%Y-%m-%d:%H:%M") < cutoff
        ]
        for old_key in old_keys:
            del self._request_counts[old_key]

        # Check rate limit
        if self._request_counts[minute_key] >= self.config.rate_limit_per_minute:
            return False

        self._request_counts[minute_key] += 1
        return True

    async def get_session_pool(self) -> aiohttp.ClientSession:
        """Get or create HTTP session pool."""
        if self._session_pool is None or self._session_pool.closed:
            connector = aiohttp.TCPConnector(
                limit=self.config.max_concurrent_requests,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
            )

            timeout = aiohttp.ClientTimeout(
                total=self.config.request_timeout, connect=30, sock_read=60
            )

            self._session_pool = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": "Sophia-AI/2.1.0",
                    "Accept-Encoding": (
                        "gzip, deflate" if self.config.compression_enabled else None
                    ),
                },
            )

        return self._session_pool

    async def close_session_pool(self) -> None:
        """Close HTTP session pool."""
        if self._session_pool and not self._session_pool.closed:
            await self._session_pool.close()

    def optimize_response(self, data: Any) -> dict[str, Any]:
        """Optimize response data for better performance."""
        if isinstance(data, dict):
            # Remove None values to reduce payload size
            optimized = {k: v for k, v in data.items() if v is not None}

            # Add performance metadata
            optimized["_performance"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "cache_enabled": True,
                "compression": self.config.compression_enabled,
                "optimized": True,
            }

            return optimized

        return data

    def get_memory_usage(self) -> dict[str, Any]:
        """Get current memory usage statistics."""
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                "rss": memory_info.rss / 1024 / 1024,  # MB
                "vms": memory_info.vms / 1024 / 1024,  # MB
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available / 1024 / 1024,  # MB
                "threshold_exceeded": memory_info.rss / 1024 / 1024
                > self.config.max_memory_usage,
            }
        except ImportError:
            return {"error": "psutil not available"}

    def trigger_garbage_collection(self) -> dict[str, Any]:
        """Trigger garbage collection if needed."""
        import gc

        before_count = len(gc.get_objects())
        collected = gc.collect()
        after_count = len(gc.get_objects())

        return {
            "objects_before": before_count,
            "objects_after": after_count,
            "collected": collected,
            "freed_objects": before_count - after_count,
        }

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            "cache_stats": {
                "size": len(self._cache),
                "max_size": self.config.cache_max_size,
                "hit_ratio": self._calculate_cache_hit_ratio(),
            },
            "rate_limiting": {
                "active_windows": len(self._request_counts),
                "total_requests": sum(self._request_counts.values()),
            },
            "memory": self.get_memory_usage(),
            "config": {
                "cache_ttl": self.config.cache_ttl,
                "max_concurrent": self.config.max_concurrent_requests,
                "compression_enabled": self.config.compression_enabled,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio (simplified)."""
        # This is a simplified implementation
        # In production, you'd want to track hits/misses properly
        if len(self._cache) == 0:
            return 0.0
        return min(len(self._cache) / self.config.cache_max_size, 1.0)


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()


# Decorator for caching function results
def cached(ttl: int | None = None):
    """Decorator to cache function results."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = (
                f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            )

            # Try to get from cache
            cached_result = performance_optimizer.cache_get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            performance_optimizer.cache_set(cache_key, result)

            return result

        return wrapper

    return decorator


# Decorator for rate limiting
def rate_limited(identifier_func=None):
    """Decorator to apply rate limiting."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Determine identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = "default"

            # Check rate limit
            if not performance_optimizer.check_rate_limit(identifier):
                raise Exception(f"Rate limit exceeded for {identifier}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Async context manager for session management
class SessionManager:
    """Async context manager for HTTP session management."""

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = await performance_optimizer.get_session_pool()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't close the session here as it's pooled
        pass


# Performance monitoring utilities
class PerformanceMonitor:
    """Performance monitoring utilities."""

    @staticmethod
    def log_performance_metrics():
        """Log current performance metrics."""
        metrics = performance_optimizer.get_performance_metrics()
        logger.info(f"Performance metrics: {metrics}")

    @staticmethod
    def check_memory_threshold():
        """Check if memory usage exceeds threshold."""
        memory_stats = performance_optimizer.get_memory_usage()
        if memory_stats.get("threshold_exceeded", False):
            logger.warning(f"Memory threshold exceeded: {memory_stats}")
            # Trigger garbage collection
            gc_stats = performance_optimizer.trigger_garbage_collection()
            logger.info(f"Garbage collection triggered: {gc_stats}")

    @staticmethod
    def optimize_for_cold_start():
        """Optimize for serverless cold start."""
        # Pre-warm cache with common configurations
        performance_optimizer.get_environment_config()

        # Pre-initialize session pool
        asyncio.create_task(performance_optimizer.get_session_pool())

        logger.info("Cold start optimization completed")


# Export key components
__all__ = [
    "PerformanceConfig",
    "PerformanceMonitor",
    "PerformanceOptimizer",
    "SessionManager",
    "cached",
    "performance_optimizer",
    "rate_limited",
]
