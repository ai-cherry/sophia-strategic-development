"""
Semantic Cache for LLM Router
Implements intelligent caching with semantic similarity matching
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Any

import redis.asyncio as redis

from backend.core.auto_esc_config import get_config_value
from backend.utils.logging import logger

from .config_schema import CacheConfig
from .enums import TaskComplexity, TaskType
from .metrics import llm_cache_hit_rate, llm_cache_operations

class SemanticCache:
    """
    Semantic cache implementation with Redis backend
    Uses embeddings for similarity matching
    """

    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client: redis.Redis | None = None
        self.enabled = config.enabled
        self.ttl = config.ttl
        self.similarity_threshold = config.semantic_similarity_threshold
        self.max_size = config.max_size

        # Cache statistics
        self._stats = {"hits": 0, "misses": 0, "errors": 0}

    async def initialize(self):
        """Initialize Redis connection"""
        if not self.enabled:
            logger.info("Semantic cache disabled")
            return

        try:
            redis_url = self.config.redis_url or get_config_value(
                "redis_url", "redis://localhost:6379"
            )
            self.redis_client = await redis.from_url(
                redis_url, encoding="utf-8", decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Semantic cache initialized")

        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            self.enabled = False

    def _generate_cache_key(
        self,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity,
        model_override: str | None = None,
    ) -> str:
        """Generate cache key for exact matching"""
        key_parts = [prompt, task.value, complexity.value, model_override or "default"]

        key_string = "|".join(key_parts)
        return f"llm:exact:{hashlib.sha256(key_string.encode()).hexdigest()}"

    def _generate_semantic_key(self, prompt: str) -> str:
        """Generate semantic cache key prefix"""
        # Simple hash-based bucketing for now
        # In production, use actual embeddings
        prompt_hash = hashlib.md5(prompt.lower().strip().encode()).hexdigest()
        bucket = prompt_hash[:4]  # Use first 4 chars as bucket
        return f"llm:semantic:{bucket}"

    async def get(
        self,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity,
        model_override: str | None = None,
    ) -> str | None:
        """
        Get cached response if available
        First tries exact match, then semantic similarity
        """
        if not self.enabled or not self.redis_client:
            return None

        try:
            # Try exact match first
            exact_key = self._generate_cache_key(
                prompt, task, complexity, model_override
            )
            exact_result = await self.redis_client.get(exact_key)

            if exact_result:
                self._stats["hits"] += 1
                llm_cache_operations.labels(operation="get", status="hit").inc()
                self._update_hit_rate()

                # Parse cached data
                cached_data = json.loads(exact_result)

                # Update access time
                cached_data["last_accessed"] = datetime.utcnow().isoformat()
                cached_data["access_count"] = cached_data.get("access_count", 0) + 1

                # Update cache with new access info
                await self.redis_client.setex(
                    exact_key, self.ttl, json.dumps(cached_data)
                )

                return cached_data["response"]

            # Try semantic match if enabled
            if self.config.semantic_similarity_threshold < 1.0:
                semantic_result = await self._semantic_search(prompt, task, complexity)
                if semantic_result:
                    self._stats["hits"] += 1
                    llm_cache_operations.labels(
                        operation="get", status="semantic_hit"
                    ).inc()
                    self._update_hit_rate()
                    return semantic_result

            # Cache miss
            self._stats["misses"] += 1
            llm_cache_operations.labels(operation="get", status="miss").inc()
            self._update_hit_rate()
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self._stats["errors"] += 1
            llm_cache_operations.labels(operation="get", status="error").inc()
            return None

    async def set(
        self,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity,
        model_override: str | None,
        response: str,
    ) -> bool:
        """Store response in cache"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            # Check cache size limit
            cache_size = await self.redis_client.dbsize()
            if cache_size >= self.max_size:
                # Evict oldest entries (simple LRU)
                await self._evict_oldest()

            # Prepare cache data
            cache_data = {
                "prompt": prompt,
                "task": task.value,
                "complexity": complexity.value,
                "model": model_override or "default",
                "response": response,
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat(),
                "access_count": 1,
                "prompt_length": len(prompt),
                "response_length": len(response),
            }

            # Store exact match
            exact_key = self._generate_cache_key(
                prompt, task, complexity, model_override
            )
            await self.redis_client.setex(exact_key, self.ttl, json.dumps(cache_data))

            # Store for semantic search
            semantic_key = self._generate_semantic_key(prompt)
            semantic_data = {
                "exact_key": exact_key,
                "prompt_summary": prompt[:200],  # Store first 200 chars for comparison
                "task": task.value,
                "complexity": complexity.value,
            }

            # Add to semantic bucket (using Redis sorted set with timestamp as score)
            await self.redis_client.zadd(
                semantic_key, {json.dumps(semantic_data): time.time()}
            )

            llm_cache_operations.labels(operation="set", status="success").inc()
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            llm_cache_operations.labels(operation="set", status="error").inc()
            return False

    async def _semantic_search(
        self, prompt: str, task: TaskType, complexity: TaskComplexity
    ) -> str | None:
        """
        Search for semantically similar cached responses
        Simplified implementation - in production use actual embeddings
        """
        try:
            semantic_key = self._generate_semantic_key(prompt)

            # Get all entries in the semantic bucket
            entries = await self.redis_client.zrange(semantic_key, 0, -1)

            for entry in entries:
                entry_data = json.loads(entry)

                # Simple similarity check (in production, use embeddings)
                if (
                    entry_data["task"] == task.value
                    and entry_data["complexity"] == complexity.value
                ):
                    # Get the actual cached response
                    exact_key = entry_data["exact_key"]
                    cached_result = await self.redis_client.get(exact_key)

                    if cached_result:
                        cached_data = json.loads(cached_result)

                        # Simple similarity based on prompt overlap
                        similarity = self._calculate_similarity(
                            prompt, cached_data["prompt"]
                        )

                        if similarity >= self.similarity_threshold:
                            return cached_data["response"]

            return None

        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return None

    def _calculate_similarity(self, prompt1: str, prompt2: str) -> float:
        """
        Calculate similarity between prompts
        Simplified implementation - in production use embeddings
        """
        # Normalize prompts
        p1 = set(prompt1.lower().split())
        p2 = set(prompt2.lower().split())

        # Jaccard similarity
        intersection = p1 & p2
        union = p1 | p2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    async def _evict_oldest(self):
        """Evict oldest cache entries when size limit reached"""
        try:
            # Get all keys with llm: prefix
            keys = await self.redis_client.keys("llm:exact:*")

            if len(keys) > self.max_size * 0.9:  # Start evicting at 90% capacity
                # Get TTL for each key and sort by remaining time
                key_ttls = []
                for key in keys:
                    ttl = await self.redis_client.ttl(key)
                    if ttl > 0:
                        key_ttls.append((key, ttl))

                # Sort by TTL (ascending) and delete 10% oldest
                key_ttls.sort(key=lambda x: x[1])
                to_delete = key_ttls[: int(len(key_ttls) * 0.1)]

                for key, _ in to_delete:
                    await self.redis_client.delete(key)

                logger.info(f"Evicted {len(to_delete)} cache entries")

        except Exception as e:
            logger.error(f"Cache eviction error: {e}")

    def _update_hit_rate(self):
        """Update cache hit rate metric"""
        total = self._stats["hits"] + self._stats["misses"]
        if total > 0:
            hit_rate = self._stats["hits"] / total
            llm_cache_hit_rate.labels(cache_type="semantic").set(hit_rate)

    async def clear(self):
        """Clear all cache entries"""
        if not self.redis_client:
            return

        try:
            keys = await self.redis_client.keys("llm:*")
            if keys:
                await self.redis_client.delete(*keys)

            self._stats = {"hits": 0, "misses": 0, "errors": 0}
            logger.info("Cache cleared")

        except Exception as e:
            logger.error(f"Cache clear error: {e}")

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        stats = self._stats.copy()

        if self.redis_client:
            try:
                stats["size"] = await self.redis_client.dbsize()
                stats["memory_usage"] = await self.redis_client.info("memory")
            except:
                pass

        return stats

    async def health_check(self) -> dict[str, Any]:
        """Check cache health"""
        if not self.enabled:
            return {"status": "disabled"}

        try:
            if self.redis_client:
                await self.redis_client.ping()
                stats = await self.get_stats()
                return {"status": "healthy", "enabled": True, "stats": stats}
            else:
                return {"status": "not_initialized"}

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
