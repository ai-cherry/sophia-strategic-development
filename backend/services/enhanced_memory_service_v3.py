"""
Phase 5: Enhanced Memory Service V3
3-tier cache architecture with improved performance

Date: July 12, 2025
"""

import asyncio
import json
import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import redis.asyncio as redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MemoryTier(BaseModel):
    """Configuration for a memory tier"""
    name: str
    ttl_seconds: int
    max_size: int
    eviction_policy: str = "lru"


class CacheMetrics(BaseModel):
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    latency_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class EnhancedMemoryServiceV3:
    """Enhanced memory service with 3-tier cache architecture"""
    
    def __init__(self):
        self.initialized = False
        
        # 3-tier cache configuration
        self.tiers = {
            "L1": MemoryTier(name="Hot Cache", ttl_seconds=300, max_size=1000),      # 5 min
            "L2": MemoryTier(name="Warm Cache", ttl_seconds=3600, max_size=10000),   # 1 hour
            "L3": MemoryTier(name="Cold Cache", ttl_seconds=86400, max_size=100000)  # 24 hours
        }
        
        # In-memory L1 cache (fastest)
        self.l1_cache: Dict[str, Tuple[Any, float]] = {}
        self.l1_metrics = CacheMetrics()
        
        # Redis L2 cache
        self.redis_client: Optional[redis.Redis] = None
        self.l2_metrics = CacheMetrics()
        
        # Qdrant vector database
        self.l3_metrics = CacheMetrics()
        
        # Global metrics
        self.total_queries = 0
        self.avg_latency_ms = 0.0
        
    async def initialize(self):
        """Initialize the memory service"""
        if self.initialized:
            return
            
        try:
            # Initialize Redis connection
            self.redis_client = await redis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Qdrant vector database
            # Mock for now
            
            self.initialized = True
            logger.info("Enhanced Memory Service V3 initialized with 3-tier cache")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory service: {e}")
            raise
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with 3-tier cache lookup"""
        start_time = time.time()
        self.total_queries += 1
        
        # L1 Cache (Hot)
        value = self._get_from_l1(key)
        if value is not None:
            self.l1_metrics.hits += 1
            latency = (time.time() - start_time) * 1000
            self._update_latency(latency)
            logger.debug(f"L1 hit for {key}: {latency:.1f}ms")
            return value
        
        self.l1_metrics.misses += 1
        
        # L2 Cache (Warm - Redis)
        value = await self._get_from_l2(key)
        if value is not None:
            self.l2_metrics.hits += 1
            # Promote to L1
            self._set_in_l1(key, value)
            latency = (time.time() - start_time) * 1000
            self._update_latency(latency)
            logger.debug(f"L2 hit for {key}: {latency:.1f}ms")
            return value
        
        self.l2_metrics.misses += 1
        
        # L3 Cache (Cold - Persistent)
        value = await self._get_from_l3(key)
        if value is not None:
            self.l3_metrics.hits += 1
            # Promote to L2 and L1
            await self._set_in_l2(key, value)
            self._set_in_l1(key, value)
            latency = (time.time() - start_time) * 1000
            self._update_latency(latency)
            logger.debug(f"L3 hit for {key}: {latency:.1f}ms")
            return value
        
        self.l3_metrics.misses += 1
        latency = (time.time() - start_time) * 1000
        self._update_latency(latency)
        
        return None
    
    async def set(self, key: str, value: Any, tier: str = "L1") -> bool:
        """Set value in specified tier(s)"""
        try:
            if tier in ["L1", "all"]:
                self._set_in_l1(key, value)
            
            if tier in ["L2", "all"]:
                await self._set_in_l2(key, value)
            
            if tier in ["L3", "all"]:
                await self._set_in_l3(key, value)
            
            return True
        except Exception as e:
            logger.error(f"Failed to set {key}: {e}")
            return False
    
    def _get_from_l1(self, key: str) -> Optional[Any]:
        """Get from L1 in-memory cache"""
        if key in self.l1_cache:
            value, timestamp = self.l1_cache[key]
            # Check TTL
            if time.time() - timestamp < self.tiers["L1"].ttl_seconds:
                return value
            else:
                # Expired
                del self.l1_cache[key]
        return None
    
    def _set_in_l1(self, key: str, value: Any):
        """Set in L1 cache with LRU eviction"""
        # Check size limit
        if len(self.l1_cache) >= self.tiers["L1"].max_size:
            # Evict oldest (simple LRU)
            oldest_key = min(self.l1_cache.keys(), 
                           key=lambda k: self.l1_cache[k][1])
            del self.l1_cache[oldest_key]
            self.l1_metrics.evictions += 1
        
        self.l1_cache[key] = (value, time.time())
    
    async def _get_from_l2(self, key: str) -> Optional[Any]:
        """Get from L2 Redis cache"""
        if not self.redis_client:
            return None
            
        try:
            value = await self.redis_client.get(f"l2:{key}")
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"L2 get error: {e}")
        
        return None
    
    async def _set_in_l2(self, key: str, value: Any):
        """Set in L2 Redis cache"""
        if not self.redis_client:
            return
            
        try:
            await self.redis_client.setex(
                f"l2:{key}",
                self.tiers["L2"].ttl_seconds,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"L2 set error: {e}")
    
    async def _get_from_l3(self, key: str) -> Optional[Any]:
        """Get from L3 persistent cache (mock)"""
        # Qdrant vector database
        await asyncio.sleep(0.01)  # Simulate latency
        return None
    
    async def _set_in_l3(self, key: str, value: Any):
        """Set in L3 persistent cache (mock)"""
        # Qdrant vector database
        await asyncio.sleep(0.01)  # Simulate latency
    
    def _update_latency(self, latency_ms: float):
        """Update average latency metric"""
        # Running average
        self.avg_latency_ms = (
            (self.avg_latency_ms * (self.total_queries - 1) + latency_ms) / 
            self.total_queries
        )
    
    async def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search knowledge base with caching"""
        # Create cache key
        cache_key = f"search:{query}:{limit}:{json.dumps(metadata_filter or {})}"
        
        # Try cache first
        cached_results = await self.get(cache_key)
        if cached_results:
            return cached_results
        
        # Perform actual search (mock)
        await asyncio.sleep(0.05)  # Simulate search
        results = [
            {
                "id": f"doc_{i}",
                "content": f"Result {i} for {query}",
                "score": 0.9 - i * 0.05,
                "metadata": metadata_filter or {}
            }
            for i in range(min(limit, 5))
        ]
        
        # Cache results
        await self.set(cache_key, results, tier="all")
        
        return results
    
    async def add_knowledge(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add knowledge to the system"""
        # Generate ID
        knowledge_id = f"knowledge_{int(time.time() * 1000)}"
        
        # Create knowledge object
        knowledge = {
            "id": knowledge_id,
            "content": content,
            "source": source,
            "metadata": metadata or {},
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        # Store in L3 (persistent)
        await self.set(knowledge_id, knowledge, tier="L3")
        
        # Invalidate relevant search caches
        # In production, this would be more sophisticated
        
        return knowledge_id
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        return {
            "total_queries": self.total_queries,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "tiers": {
                "L1": {
                    "name": self.tiers["L1"].name,
                    "size": len(self.l1_cache),
                    "max_size": self.tiers["L1"].max_size,
                    "hit_rate": round(self.l1_metrics.hit_rate, 3),
                    "hits": self.l1_metrics.hits,
                    "misses": self.l1_metrics.misses,
                    "evictions": self.l1_metrics.evictions
                },
                "L2": {
                    "name": self.tiers["L2"].name,
                    "hit_rate": round(self.l2_metrics.hit_rate, 3),
                    "hits": self.l2_metrics.hits,
                    "misses": self.l2_metrics.misses
                },
                "L3": {
                    "name": self.tiers["L3"].name,
                    "hit_rate": round(self.l3_metrics.hit_rate, 3),
                    "hits": self.l3_metrics.hits,
                    "misses": self.l3_metrics.misses
                }
            },
            "overall_hit_rate": round(self._calculate_overall_hit_rate(), 3)
        }
    
    def _calculate_overall_hit_rate(self) -> float:
        """Calculate overall hit rate across all tiers"""
        total_hits = (self.l1_metrics.hits + self.l2_metrics.hits + 
                     self.l3_metrics.hits)
        total_queries = self.total_queries
        return total_hits / total_queries if total_queries > 0 else 0.0
    
    async def warm_cache(self, popular_queries: List[str]):
        """Warm up cache with popular queries"""
        logger.info(f"Warming cache with {len(popular_queries)} queries")
        
        tasks = []
        for query in popular_queries:
            tasks.append(self.search_knowledge(query, limit=5))
        
        # Process in batches
        batch_size = 10
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            await asyncio.gather(*batch)
        
        logger.info("Cache warming complete")
    
    async def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache entries"""
        if pattern:
            # Invalidate matching pattern
            keys_to_remove = [k for k in self.l1_cache if pattern in k]
            for key in keys_to_remove:
                del self.l1_cache[key]
            
            # Also invalidate in Redis
            if self.redis_client:
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor, match=f"l2:*{pattern}*"
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
        else:
            # Clear all caches
            self.l1_cache.clear()
            if self.redis_client:
                await self.redis_client.flushdb()
        
        logger.info(f"Cache invalidated: pattern={pattern}")


# Singleton instance
_memory_service: Optional[EnhancedMemoryServiceV3] = None


async def get_memory_service() -> EnhancedMemoryServiceV3:
    """Get or create memory service instance"""
    global _memory_service
    
    if _memory_service is None:
        _memory_service = EnhancedMemoryServiceV3()
        await _memory_service.initialize()
    
    return _memory_service 