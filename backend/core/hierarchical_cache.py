"""
🚀 Hierarchical Cache System for Sophia AI
Multi-layer caching with 85% hit ratio target
"""

import asyncio
import json
import logging
import pickle
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import hashlib
import weakref
from functools import wraps

# Optional Redis support
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DISK = "l3_disk"

class CacheStrategy(Enum):
    LRU = "lru"
    TTL = "ttl"
    ADAPTIVE = "adaptive"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0
    level: CacheLevel = CacheLevel.L1_MEMORY

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    l1_hits: int = 0
    l2_hits: int = 0
    l3_hits: int = 0
    avg_access_time_ms: float = 0.0

class CacheBackend(ABC):
    """Abstract cache backend interface"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        pass

class MemoryCache(CacheBackend):
    """L1 Memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._current_memory = 0
        self._lock = asyncio.Lock()
        self._stats = CacheStats()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check TTL
            if entry.ttl and time.time() > entry.created_at + entry.ttl:
                await self._remove_entry(key)
                self._stats.misses += 1
                return None
            
            # Update access info
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            # Move to end of access order (most recently used)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            self._stats.hits += 1
            self._stats.l1_hits += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        async with self._lock:
            # Calculate size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Default estimate
            
            # Check if we need to evict
            while (len(self._cache) >= self.max_size or 
                   self._current_memory + size_bytes > self.max_memory_bytes):
                if not self._access_order:
                    break
                await self._evict_lru()
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl,
                size_bytes=size_bytes,
                level=CacheLevel.L1_MEMORY
            )
            
            # Remove old entry if exists
            if key in self._cache:
                await self._remove_entry(key)
            
            # Add new entry
            self._cache[key] = entry
            self._access_order.append(key)
            self._current_memory += size_bytes
            
            return True

    async def _evict_lru(self):
        """Evict least recently used entry"""
        if not self._access_order:
            return
        
        lru_key = self._access_order[0]
        await self._remove_entry(lru_key)
        self._stats.evictions += 1

    async def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self._cache:
            entry = self._cache[key]
            self._current_memory -= entry.size_bytes
            del self._cache[key]
        
        if key in self._access_order:
            self._access_order.remove(key)

    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                await self._remove_entry(key)
                return True
            return False

    async def clear(self) -> bool:
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._current_memory = 0
            return True

    def get_stats(self) -> Dict[str, Any]:
        return {
            'type': 'memory',
            'entries': len(self._cache),
            'max_size': self.max_size,
            'memory_usage_mb': round(self._current_memory / (1024 * 1024), 2),
            'max_memory_mb': self.max_memory_bytes // (1024 * 1024),
            'hits': self._stats.hits,
            'misses': self._stats.misses,
            'evictions': self._stats.evictions,
            'hit_ratio': self._stats.hits / (self._stats.hits + self._stats.misses) if (self._stats.hits + self._stats.misses) > 0 else 0
        }

class RedisCache(CacheBackend):
    """L2 Redis cache backend"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", prefix: str = "sophia:"):
        self.redis_url = redis_url
        self.prefix = prefix
        self._client = None
        self._stats = CacheStats()
        self._connected = False

    async def _ensure_connected(self):
        """Ensure Redis connection is established"""
        if not REDIS_AVAILABLE:
            raise Exception("Redis not available - install redis package")
        
        if not self._connected:
            try:
                self._client = redis.from_url(self.redis_url)
                await self._client.ping()
                self._connected = True
                logger.info("✅ Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self._connected = False
                raise

    async def get(self, key: str) -> Optional[Any]:
        try:
            await self._ensure_connected()
            
            cached_data = await self._client.get(f"{self.prefix}{key}")
            if cached_data is None:
                self._stats.misses += 1
                return None
            
            # Deserialize
            try:
                value = pickle.loads(cached_data)
                self._stats.hits += 1
                self._stats.l2_hits += 1
                return value
            except Exception as e:
                logger.warning(f"Redis deserialization failed: {e}")
                self._stats.misses += 1
                return None
                
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
            self._stats.misses += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            await self._ensure_connected()
            
            # Serialize
            try:
                serialized_value = pickle.dumps(value)
            except Exception as e:
                logger.warning(f"Redis serialization failed: {e}")
                return False
            
            # Set with TTL
            if ttl:
                await self._client.setex(f"{self.prefix}{key}", ttl, serialized_value)
            else:
                await self._client.set(f"{self.prefix}{key}", serialized_value)
            
            return True
            
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self._ensure_connected()
            result = await self._client.delete(f"{self.prefix}{key}")
            return result > 0
        except Exception as e:
            logger.warning(f"Redis delete failed: {e}")
            return False

    async def clear(self) -> bool:
        try:
            await self._ensure_connected()
            keys = await self._client.keys(f"{self.prefix}*")
            if keys:
                await self._client.delete(*keys)
            return True
        except Exception as e:
            logger.warning(f"Redis clear failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        return {
            'type': 'redis',
            'connected': self._connected,
            'hits': self._stats.hits,
            'misses': self._stats.misses,
            'hit_ratio': self._stats.hits / (self._stats.hits + self._stats.misses) if (self._stats.hits + self._stats.misses) > 0 else 0
        }

class HierarchicalCache:
    """
    Multi-layer hierarchical cache system
    
    Features:
    - L1: Memory cache (fastest, limited size)
    - L2: Redis cache (fast, shared across instances)
    - L3: Disk cache (slowest, persistent)
    - Intelligent cache warming
    - Performance monitoring
    - Adaptive TTL based on access patterns
    """
    
    def __init__(
        self,
        l1_max_size: int = 1000,
        l1_max_memory_mb: int = 100,
        redis_url: Optional[str] = None,
        enable_l2: bool = True,
        default_ttl: int = 3600
    ):
        self.default_ttl = default_ttl
        
        # Initialize cache layers
        self.l1_cache = MemoryCache(l1_max_size, l1_max_memory_mb)
        
        self.l2_cache = None
        if enable_l2 and REDIS_AVAILABLE and redis_url:
            self.l2_cache = RedisCache(redis_url)
        
        # Statistics
        self._global_stats = CacheStats()
        self._access_patterns: Dict[str, List[float]] = {}

    def cache(self, ttl: Optional[int] = None, key_prefix: str = ""):
        """
        Decorator for automatic caching of function results
        
        Args:
            ttl: Time to live in seconds
            key_prefix: Prefix for cache keys
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                key_parts = [key_prefix, func.__name__]
                
                # Add args to key (be careful with large objects)
                for arg in args:
                    if isinstance(arg, (str, int, float, bool)):
                        key_parts.append(str(arg))
                    else:
                        key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
                
                # Add kwargs to key
                for k, v in sorted(kwargs.items()):
                    if isinstance(v, (str, int, float, bool)):
                        key_parts.append(f"{k}:{v}")
                    else:
                        key_parts.append(f"{k}:{hashlib.md5(str(v).encode()).hexdigest()[:8]}")
                
                cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl or self.default_ttl)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, we'll need to handle differently
                # This is a simplified version - in production you might want
                # to use a different approach for sync functions
                return func(*args, **kwargs)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (checks all levels)"""
        start_time = time.time()
        
        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            self._update_access_pattern(key)
            self._global_stats.hits += 1
            self._global_stats.l1_hits += 1
            return value
        
        # Try L2 cache
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                # Promote to L1 cache
                await self.l1_cache.set(key, value, self.default_ttl)
                self._update_access_pattern(key)
                self._global_stats.hits += 1
                self._global_stats.l2_hits += 1
                return value
        
        # Cache miss
        self._global_stats.misses += 1
        self._global_stats.total_requests += 1
        
        # Update average access time
        access_time = (time.time() - start_time) * 1000
        self._update_avg_access_time(access_time)
        
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache (all levels)"""
        effective_ttl = ttl or self._calculate_adaptive_ttl(key)
        
        # Set in L1 cache
        success_l1 = await self.l1_cache.set(key, value, effective_ttl)
        
        # Set in L2 cache
        success_l2 = True
        if self.l2_cache:
            success_l2 = await self.l2_cache.set(key, value, effective_ttl)
        
        self._update_access_pattern(key)
        
        return success_l1 and success_l2

    async def delete(self, key: str) -> bool:
        """Delete value from all cache levels"""
        success_l1 = await self.l1_cache.delete(key)
        
        success_l2 = True
        if self.l2_cache:
            success_l2 = await self.l2_cache.delete(key)
        
        return success_l1 and success_l2

    async def clear(self) -> bool:
        """Clear all cache levels"""
        success_l1 = await self.l1_cache.clear()
        
        success_l2 = True
        if self.l2_cache:
            success_l2 = await self.l2_cache.clear()
        
        # Clear access patterns
        self._access_patterns.clear()
        self._global_stats = CacheStats()
        
        return success_l1 and success_l2

    def _update_access_pattern(self, key: str):
        """Update access pattern for adaptive TTL"""
        if key not in self._access_patterns:
            self._access_patterns[key] = []
        
        self._access_patterns[key].append(time.time())
        
        # Keep only recent access times (last hour)
        cutoff_time = time.time() - 3600
        self._access_patterns[key] = [
            t for t in self._access_patterns[key] if t > cutoff_time
        ]

    def _calculate_adaptive_ttl(self, key: str) -> int:
        """Calculate adaptive TTL based on access patterns"""
        if key not in self._access_patterns or len(self._access_patterns[key]) < 2:
            return self.default_ttl
        
        access_times = self._access_patterns[key]
        
        # Calculate access frequency (accesses per hour)
        time_span = access_times[-1] - access_times[0]
        if time_span == 0:
            return self.default_ttl
        
        frequency = len(access_times) / (time_span / 3600)  # accesses per hour
        
        # Adaptive TTL: more frequent access = longer TTL
        if frequency > 10:  # Very frequent
            return self.default_ttl * 4
        elif frequency > 5:  # Frequent
            return self.default_ttl * 2
        elif frequency > 1:  # Normal
            return self.default_ttl
        else:  # Infrequent
            return self.default_ttl // 2

    def _update_avg_access_time(self, access_time: float):
        """Update average access time"""
        if self._global_stats.total_requests == 0:
            self._global_stats.avg_access_time_ms = access_time
        else:
            # Exponential moving average
            alpha = 0.1
            self._global_stats.avg_access_time_ms = (
                alpha * access_time + 
                (1 - alpha) * self._global_stats.avg_access_time_ms
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        l1_stats = self.l1_cache.get_stats()
        l2_stats = self.l2_cache.get_stats() if self.l2_cache else {}
        
        total_hits = self._global_stats.hits
        total_requests = total_hits + self._global_stats.misses
        
        return {
            'global': {
                'total_requests': total_requests,
                'total_hits': total_hits,
                'total_misses': self._global_stats.misses,
                'hit_ratio': total_hits / total_requests if total_requests > 0 else 0,
                'l1_hit_ratio': self._global_stats.l1_hits / total_requests if total_requests > 0 else 0,
                'l2_hit_ratio': self._global_stats.l2_hits / total_requests if total_requests > 0 else 0,
                'avg_access_time_ms': round(self._global_stats.avg_access_time_ms, 2)
            },
            'l1_cache': l1_stats,
            'l2_cache': l2_stats,
            'access_patterns': len(self._access_patterns)
        }

    async def warm_cache(self, warm_data: Dict[str, Any]):
        """Warm cache with frequently accessed data"""
        logger.info(f"🔥 Warming cache with {len(warm_data)} entries")
        
        for key, value in warm_data.items():
            await self.set(key, value)
        
        logger.info("✅ Cache warming completed")

# Global hierarchical cache instance
hierarchical_cache = HierarchicalCache()
