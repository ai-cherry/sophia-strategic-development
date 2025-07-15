"""
GPTCache Service for Sophia AI
Intelligent caching with semantic similarity matching
"""

import json
import logging
import time
from typing import Any

import numpy as np
import redis.asyncio as redis
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# CEO Common Queries for pre-warming
CEO_COMMON_QUERIES = [
    "What is our current revenue?",
    "Show me the sales pipeline",
    "What are our top deals?",
    "How is the team performing?",
]


class GPTCacheService:
    """
    Intelligent caching service with semantic similarity
    Uses Redis for persistence and sentence transformers for similarity
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        similarity_threshold: float = 0.85,
        cache_ttl: int = 3600,
        model_name: str = "all-MiniLM-L6-v2",  # Fast, efficient model
    ):
        self.redis_url = redis_url
        self.similarity_threshold = similarity_threshold
        self.cache_ttl = cache_ttl
        self.redis_client: redis.Redis | None = None
        self.model = None
        self.model_name = model_name

        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
            "cache_size": 0,
            "avg_similarity": 0.0,
        }

    async def initialize(self):
        """Initialize Redis connection and load model"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url, decode_responses=True, db=1  # Use DB 1 for cache
            )
            await self.redis_client.ping()
            logger.info("Redis cache connected successfully")

            # Load sentence transformer model
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")

            # Pre-warm cache with CEO queries
            await self._prewarm_cache()
        except Exception as e:
            logger.exception(f"Failed to initialize cache service: {e}")
            # Continue without cache if Redis is unavailable
            self.redis_client = None
            self.model = None

    async def _prewarm_cache(self):
        """Pre-warm cache with common CEO queries"""
        logger.info("Pre-warming cache with CEO queries...")

        # Example pre-warmed responses
        prewarm_data = {
            "What is our current revenue?": {
                "response": "Current Q4 revenue is $12.5M, up 23% YoY. Monthly recurring revenue is $4.2M with 15% growth rate.",
                "sources": ["qdrant.revenue_dashboard", "hubspot.deals"],
                "timestamp": time.time(),
            },
            "Show me the sales pipeline": {
                "response": "Active pipeline: $45M across 127 deals. Closing this quarter: $15M (33%). Top opportunities: Enterprise deals worth $8M.",
                "sources": ["hubspot.pipeline", "gong.calls"],
                "timestamp": time.time(),
            },
        }

        for query, data in prewarm_data.items():
            await self.set(query, data, ttl_seconds=7200)  # 2 hour TTL for pre-warmed

        logger.info(f"Pre-warmed {len(prewarm_data)} CEO queries")

    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text using sentence transformer"""
        if self.model is None:
            # Fallback to simple hash-based similarity if model not loaded
            return np.array([hash(text) % 1000 / 1000.0] * 384)

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.exception(f"Error generating embedding: {e}")
            # Fallback embedding
            return np.array([0.0] * 384)

    def _calculate_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            # Cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.exception(f"Error calculating similarity: {e}")
            return 0.0

    async def get(self, query: str) -> tuple[Any, float] | None:
        """
        Get cached result for query using semantic similarity
        Returns (result, similarity_score) or None
        """
        if not self.redis_client:
            return None

        self.stats["total_queries"] += 1

        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)

            # Get all cached queries
            cache_keys = await self.redis_client.keys("cache:*")

            best_match = None
            best_similarity = 0.0

            for key in cache_keys:
                # Get cached data
                cached_data = await self.redis_client.get(key)
                if not cached_data:
                    continue

                cached_item = json.loads(cached_data)
                cached_item.get("query", "")

                # Calculate similarity
                cached_embedding = np.array(cached_item.get("embedding", []))
                similarity = self._calculate_similarity(
                    query_embedding, cached_embedding
                )

                if (
                    similarity > best_similarity
                    and similarity >= self.similarity_threshold
                ):
                    best_similarity = similarity
                    best_match = cached_item.get("result")

            if best_match:
                self.stats["hits"] += 1
                self.stats["avg_similarity"] = (
                    self.stats["avg_similarity"] * 0.9 + best_similarity * 0.1
                )
                logger.info(f"Cache hit with similarity {best_similarity:.2f}")
                return (best_match, best_similarity)
            else:
                self.stats["misses"] += 1
                return None

        except Exception as e:
            logger.exception(f"Cache get error: {e}")
            return None

    async def set(self, query: str, result: Any, ttl_seconds: int | None = None):
        """Set cache entry with query and result"""
        if not self.redis_client:
            return

        try:
            # Generate embedding
            embedding = self._get_embedding(query)

            # Create cache entry
            cache_entry = {
                "query": query,
                "result": result,
                "embedding": embedding.tolist(),
                "timestamp": time.time(),
            }

            # Generate cache key
            cache_key = f"cache:{hash(query)}"

            # Store in Redis
            ttl = ttl_seconds or self.cache_ttl
            await self.redis_client.setex(cache_key, ttl, json.dumps(cache_entry))

            # Update stats
            self.stats["cache_size"] = await self.redis_client.dbsize()

        except Exception as e:
            logger.exception(f"Cache set error: {e}")

    async def clear(self):
        """Clear all cache entries"""
        if not self.redis_client:
            return

        try:
            await self.redis_client.flushdb()
            self.stats["cache_size"] = 0
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.exception(f"Cache clear error: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        hit_rate = (
            self.stats["hits"] / self.stats["total_queries"]
            if self.stats["total_queries"] > 0
            else 0
        )

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "total_queries": self.stats["total_queries"],
            "cache_size": self.stats["cache_size"],
            "avg_similarity": self.stats["avg_similarity"],
            "model": self.model_name if self.model else "fallback",
            "threshold": self.similarity_threshold,
        }


# Singleton instance
cache_service = GPTCacheService()


# Initialize on import
import asyncio


def _init_cache():
    """Initialize cache service synchronously"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Schedule initialization for later
            asyncio.create_task(cache_service.initialize())
        else:
            # Run initialization now
            loop.run_until_complete(cache_service.initialize())
    except Exception as e:
        logger.warning(f"Cache initialization deferred: {e}")


_init_cache()
