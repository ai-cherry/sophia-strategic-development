"""
AI Memory Performance Optimization Module
Advanced async patterns, caching, and performance monitoring
"""

from __future__ import annotations

import asyncio
import logging
import time
import weakref
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Dict, List, Optional, TypeVar, Union

from .exceptions import MemoryCapacityError, MemoryTimeoutError, handle_async_exception

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""

    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    memory_usage: Optional[int] = None
    context: dict[str, Any] = field(default_factory=dict)

    def complete(
        self, success: bool = True, error_message: Optional[str] = None
    ) -> None:
        """Mark operation as complete"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/monitoring"""
        return {
            "operation": self.operation_name,
            "duration": self.duration,
            "success": self.success,
            "error": self.error_message,
            "memory_usage": self.memory_usage,
            "context": self.context,
        }


class AsyncSemaphorePool:
    """Advanced semaphore pool for controlling concurrent operations"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_operations: dict[str, PerformanceMetrics] = {}
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def acquire(
        self, operation_name: str
    ) -> AsyncGenerator[PerformanceMetrics, None]:
        """Acquire semaphore with performance tracking"""
        async with self.semaphore:
            metrics = PerformanceMetrics(operation_name)

            async with self._lock:
                self.active_operations[operation_name] = metrics

            try:
                yield metrics
                metrics.complete(success=True)
            except Exception as e:
                metrics.complete(success=False, error_message=str(e))
                raise
            finally:
                async with self._lock:
                    self.active_operations.pop(operation_name, None)

    async def get_active_operations(self) -> list[dict[str, Any]]:
        """Get currently active operations"""
        async with self._lock:
            return [metrics.to_dict() for metrics in self.active_operations.values()]

    def get_available_slots(self) -> int:
        """Get number of available concurrent slots"""
        return self.semaphore._value


class MemoryCache:
    """Multi-tier memory cache with TTL and LRU eviction"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: dict[str, dict[str, Any]] = {}
        self._access_times: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # Check TTL
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                self._access_times.pop(key, None)
                return None

            # Update access time for LRU
            self._access_times[key] = time.time()
            return entry["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        async with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()

            expires_at = time.time() + (ttl or self.default_ttl)
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time(),
            }
            self._access_times[key] = time.time()

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_times.pop(key, None)
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            self._access_times.clear()

    async def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self._access_times:
            return

        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        del self._cache[lru_key]
        del self._access_times[lru_key]

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            now = time.time()
            expired_count = sum(
                1 for entry in self._cache.values() if now > entry["expires_at"]
            )

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "expired_entries": expired_count,
                "hit_ratio": getattr(self, "_hit_count", 0)
                / max(getattr(self, "_access_count", 1), 1),
            }


class VectorOperationOptimizer:
    """Optimized vector operations with memory management"""

    def __init__(self):
        self._vector_cache = MemoryCache(max_size=500, default_ttl=1800)
        self._computation_pool = AsyncSemaphorePool(max_concurrent=5)

    @handle_async_exception
    async def compute_similarity_batch(
        self,
        query_vector: list[float],
        candidate_vectors: list[list[float]],
        similarity_threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Compute similarity for multiple vectors efficiently"""

        async with self._computation_pool.acquire("similarity_batch") as metrics:
            try:
                import numpy as np

                # Convert to numpy arrays for efficient computation
                query_array = np.array(query_vector, dtype=np.float32)
                candidate_arrays = np.array(candidate_vectors, dtype=np.float32)

                # Normalize vectors
                query_norm = query_array / np.linalg.norm(query_array)
                candidate_norms = candidate_arrays / np.linalg.norm(
                    candidate_arrays, axis=1, keepdims=True
                )

                # Compute cosine similarities in batch
                similarities = np.dot(candidate_norms, query_norm)

                # Filter by threshold and create results
                results = []
                for i, similarity in enumerate(similarities):
                    if similarity >= similarity_threshold:
                        results.append(
                            {
                                "index": i,
                                "similarity": float(similarity),
                                "vector": candidate_vectors[i],
                            }
                        )

                # Sort by similarity descending
                results.sort(key=lambda x: x["similarity"], reverse=True)

                metrics.context["query_vector_size"] = len(query_vector)
                metrics.context["candidate_count"] = len(candidate_vectors)
                metrics.context["results_count"] = len(results)

                return results

            except Exception as e:
                logger.error(f"Vector similarity computation failed: {e}")
                raise
            finally:
                # Explicit cleanup for large arrays
                try:
                    del (
                        query_array,
                        candidate_arrays,
                        query_norm,
                        candidate_norms,
                        similarities,
                    )
                except:
                    pass

    @handle_async_exception
    async def generate_embedding_cached(
        self, content: str, model: str = "text-embedding-3-small"
    ) -> list[float]:
        """Generate embedding with caching"""

        # Create cache key
        cache_key = f"embedding:{model}:{hash(content)}"

        # Try cache first
        cached_embedding = await self._vector_cache.get(cache_key)
        if cached_embedding:
            return cached_embedding

        async with self._computation_pool.acquire("embedding_generation") as metrics:
            try:
                # This would integrate with actual embedding service
                # For now, simulate with random vector
                import random

                embedding = [random.random() for _ in range(1536)]

                # Cache the result
                await self._vector_cache.set(cache_key, embedding, ttl=3600)

                metrics.context["content_length"] = len(content)
                metrics.context["model"] = model
                metrics.context["cache_miss"] = True

                return embedding

            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                raise


class AsyncBatchProcessor:
    """Batch processor for efficient async operations"""

    def __init__(self, batch_size: int = 10, max_wait_time: float = 1.0):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self._pending_items: list[dict[str, Any]] = []
        self._batch_lock = asyncio.Lock()
        self._processing = False

    async def add_item(self, item: Any, callback: Callable[[Any], Any]) -> Any:
        """Add item to batch for processing"""

        future = asyncio.Future()
        batch_item = {
            "item": item,
            "callback": callback,
            "future": future,
            "added_at": time.time(),
        }

        async with self._batch_lock:
            self._pending_items.append(batch_item)

            # Trigger batch processing if needed
            if len(self._pending_items) >= self.batch_size or not self._processing:
                asyncio.create_task(self._process_batch())

        return await future

    async def _process_batch(self) -> None:
        """Process current batch of items"""

        if self._processing:
            return

        self._processing = True

        try:
            while True:
                async with self._batch_lock:
                    if not self._pending_items:
                        break

                    # Take items for this batch
                    current_batch = self._pending_items[: self.batch_size]
                    self._pending_items = self._pending_items[self.batch_size :]

                # Process batch items
                await self._execute_batch(current_batch)

                # Wait a bit before checking for more items
                await asyncio.sleep(0.1)

        finally:
            self._processing = False

    async def _execute_batch(self, batch_items: list[dict[str, Any]]) -> None:
        """Execute a batch of items"""

        tasks = []
        for batch_item in batch_items:
            task = asyncio.create_task(self._execute_item(batch_item))
            tasks.append(task)

        # Wait for all items in batch to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_item(self, batch_item: dict[str, Any]) -> None:
        """Execute a single batch item"""

        try:
            result = await batch_item["callback"](batch_item["item"])
            batch_item["future"].set_result(result)
        except Exception as e:
            batch_item["future"].set_exception(e)


def performance_monitor(operation_name: str):
    """Decorator for monitoring function performance"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics = PerformanceMetrics(operation_name)

            try:
                result = await func(*args, **kwargs)
                metrics.complete(success=True)

                # Log performance metrics
                logger.info(f"Performance: {metrics.to_dict()}")

                return result

            except Exception as e:
                metrics.complete(success=False, error_message=str(e))
                logger.error(f"Performance: {metrics.to_dict()}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics = PerformanceMetrics(operation_name)

            try:
                result = func(*args, **kwargs)
                metrics.complete(success=True)

                # Log performance metrics
                logger.info(f"Performance: {metrics.to_dict()}")

                return result

            except Exception as e:
                metrics.complete(success=False, error_message=str(e))
                logger.error(f"Performance: {metrics.to_dict()}")
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


async def with_timeout(coro, timeout_seconds: float, operation_name: str = "operation"):
    """Execute coroutine with timeout"""

    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise MemoryTimeoutError(
            message=f"Operation timed out after {timeout_seconds} seconds",
            operation=operation_name,
            timeout_seconds=timeout_seconds,
        )


class ResourceMonitor:
    """Monitor system resources and enforce limits"""

    def __init__(self, max_memory_mb: int = 1000, max_concurrent_ops: int = 50):
        self.max_memory_mb = max_memory_mb
        self.max_concurrent_ops = max_concurrent_ops
        self._active_operations = 0
        self._lock = asyncio.Lock()

    async def check_resources(self, operation_name: str) -> None:
        """Check if resources are available for operation"""

        async with self._lock:
            if self._active_operations >= self.max_concurrent_ops:
                raise MemoryCapacityError(
                    message="Maximum concurrent operations exceeded",
                    limit_type="concurrent_operations",
                    current_value=self._active_operations,
                    limit_value=self.max_concurrent_ops,
                )

            # Check memory usage (simplified)
            try:
                import psutil

                memory_usage = psutil.Process().memory_info().rss / 1024 / 1024

                if memory_usage > self.max_memory_mb:
                    raise MemoryCapacityError(
                        message="Memory usage limit exceeded",
                        limit_type="memory_usage_mb",
                        current_value=memory_usage,
                        limit_value=self.max_memory_mb,
                    )
            except ImportError:
                # psutil not available, skip memory check
                pass

    @asynccontextmanager
    async def track_operation(self, operation_name: str) -> AsyncGenerator[None, None]:
        """Track an operation's resource usage"""

        await self.check_resources(operation_name)

        async with self._lock:
            self._active_operations += 1

        try:
            yield
        finally:
            async with self._lock:
                self._active_operations -= 1


# Global instances
_semaphore_pool = AsyncSemaphorePool()
_memory_cache = MemoryCache()
_vector_optimizer = VectorOperationOptimizer()
_batch_processor = AsyncBatchProcessor()
_resource_monitor = ResourceMonitor()


def get_semaphore_pool() -> AsyncSemaphorePool:
    """Get global semaphore pool"""
    return _semaphore_pool


def get_memory_cache() -> MemoryCache:
    """Get global memory cache"""
    return _memory_cache


def get_vector_optimizer() -> VectorOperationOptimizer:
    """Get global vector optimizer"""
    return _vector_optimizer


def get_batch_processor() -> AsyncBatchProcessor:
    """Get global batch processor"""
    return _batch_processor


def get_resource_monitor() -> ResourceMonitor:
    """Get global resource monitor"""
    return _resource_monitor
