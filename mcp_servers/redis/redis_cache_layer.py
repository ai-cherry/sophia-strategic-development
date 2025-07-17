"""
Redis Cache Layer MCP Server Implementation
High-performance caching with separation between coding and business data
"""

import asyncio
import json
import time
import pickle
import hashlib
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import os
import sys

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.auto_esc_config import get_config_value

# Try to import redis
try:
    import redis
    from redis import asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not installed. Install with: pip install redis")


class CacheType(Enum):
    """Cache types with different TTL strategies"""
    CODING = 0  # DB 0: Short TTL, frequent updates
    BUSINESS = 1  # DB 1: Long TTL, stable data
    AGGREGATION = 2  # DB 2: Dashboard aggregations


@dataclass
class CacheStats:
    """Statistics for cache performance"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    evictions: int = 0
    memory_usage_mb: float = 0.0
    keys_count: int = 0


class RedisCacheMCPServer:
    """
    MCP Server for Redis caching operations
    Tier 3 in the hybrid memory architecture
    """
    
    def __init__(self):
        self.name = "redis_cache"
        self.version = "1.0.0"
        self.port = 9503  # Redis MCP server port
        
        # Redis clients for different cache types
        self.clients: Dict[CacheType, Optional[redis.Redis]] = {
            CacheType.CODING: None,
            CacheType.BUSINESS: None,
            CacheType.AGGREGATION: None
        }
        
        # Cache configurations
        self.cache_configs = {
            CacheType.CODING: {
                "db": 0,
                "ttl": 3600,  # 1 hour default
                "max_memory": "2gb",
                "eviction_policy": "allkeys-lru"
            },
            CacheType.BUSINESS: {
                "db": 1,
                "ttl": 86400,  # 24 hours default
                "max_memory": "10gb",
                "eviction_policy": "allkeys-lru"
            },
            CacheType.AGGREGATION: {
                "db": 2,
                "ttl": 300,  # 5 minutes for dashboard data
                "max_memory": "1gb",
                "eviction_policy": "volatile-lru"
            }
        }
        
        # Performance tracking
        self.stats: Dict[CacheType, CacheStats] = {
            ct: CacheStats() for ct in CacheType
        }
        
    async def initialize(self):
        """Initialize Redis connections"""
        try:
            if not REDIS_AVAILABLE:
                print("❌ Redis not available, running in mock mode")
                return
                
            # Get Redis configuration
            redis_host = get_config_value("redis_host", "localhost")
            redis_port = int(get_config_value("redis_port", "6379") or "6379")
            redis_password = get_config_value("redis_password")
            
            # Initialize clients for each cache type
            for cache_type, config in self.cache_configs.items():
                try:
                    self.clients[cache_type] = redis.Redis(
                        host=redis_host or "localhost",
                        port=redis_port,
                        password=redis_password,
                        db=config["db"],
                        decode_responses=False  # Handle binary data
                    )
                    
                    # Configure memory limits and eviction
                    client = self.clients[cache_type]
                    if client:
                        client.config_set('maxmemory', config["max_memory"])
                        client.config_set('maxmemory-policy', config["eviction_policy"])
                    
                    print(f"✅ Redis {cache_type.name} cache initialized (DB {config['db']})")
                    
                except Exception as e:
                    print(f"⚠️  Failed to initialize {cache_type.name} cache: {e}")
                    self.clients[cache_type] = None
            
            print(f"✅ Redis Cache MCP Server initialized on port {self.port}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Redis Cache Server: {e}")
            raise
    
    def _generate_key(self, cache_type: CacheType, key: str) -> str:
        """Generate namespaced cache key"""
        return f"{cache_type.name.lower()}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        return pickle.loads(data) if data else None
    
    async def get(self, 
                  cache_type: CacheType,
                  key: str) -> Optional[Any]:
        """Get value from cache"""
        client = self.clients.get(cache_type)
        
        if not client:
            # Mock mode
            return None
            
        try:
            cache_key = self._generate_key(cache_type, key)
            data = client.get(cache_key)
            
            if data:
                self.stats[cache_type].hits += 1
                return self._deserialize_value(data) if isinstance(data, bytes) else None
            else:
                self.stats[cache_type].misses += 1
                return None
                
        except Exception as e:
            print(f"❌ Error getting from cache: {e}")
            return None
    
    async def set(self,
                  cache_type: CacheType,
                  key: str,
                  value: Any,
                  ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        client = self.clients.get(cache_type)
        
        if not client:
            # Mock mode
            return True
            
        try:
            cache_key = self._generate_key(cache_type, key)
            serialized = self._serialize_value(value)
            
            # Use configured TTL if not specified
            if ttl is None:
                ttl = self.cache_configs[cache_type]["ttl"]
            
            client.setex(cache_key, int(ttl), serialized)
            self.stats[cache_type].sets += 1
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting cache: {e}")
            return False
    
    async def delete(self,
                    cache_type: CacheType,
                    key: str) -> bool:
        """Delete value from cache"""
        client = self.clients.get(cache_type)
        
        if not client:
            return True
            
        try:
            cache_key = self._generate_key(cache_type, key)
            result = client.delete(cache_key)
            return bool(result)
            
        except Exception as e:
            print(f"❌ Error deleting from cache: {e}")
            return False
    
    async def exists(self,
                    cache_type: CacheType,
                    key: str) -> bool:
        """Check if key exists in cache"""
        client = self.clients.get(cache_type)
        
        if not client:
            return False
            
        try:
            cache_key = self._generate_key(cache_type, key)
            return bool(client.exists(cache_key))
            
        except Exception as e:
            print(f"❌ Error checking existence: {e}")
            return False
    
    async def get_many(self,
                      cache_type: CacheType,
                      keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        client = self.clients.get(cache_type)
        
        if not client:
            return {}
            
        try:
            cache_keys = [self._generate_key(cache_type, k) for k in keys]
            values = client.mget(cache_keys)
            
            result = {}
            for i, key in enumerate(keys):
                if values and i < len(values) and values[i]:
                    result[key] = self._deserialize_value(values[i]) if isinstance(values[i], bytes) else None
                    self.stats[cache_type].hits += 1
                else:
                    self.stats[cache_type].misses += 1
                    
            return result
            
        except Exception as e:
            print(f"❌ Error getting many from cache: {e}")
            return {}
    
    async def set_many(self,
                      cache_type: CacheType,
                      items: Dict[str, Any],
                      ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache"""
        client = self.clients.get(cache_type)
        
        if not client:
            return True
            
        try:
            if ttl is None:
                ttl = self.cache_configs[cache_type]["ttl"]
            
            # Use pipeline for atomic operation
            pipe = client.pipeline()
            
            for key, value in items.items():
                cache_key = self._generate_key(cache_type, key)
                serialized = self._serialize_value(value)
                pipe.setex(cache_key, int(ttl), serialized)
            
            pipe.execute()
            self.stats[cache_type].sets += len(items)
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting many in cache: {e}")
            return False
    
    async def cache_aggregation(self,
                              aggregation_type: str,
                              project_id: str,
                              data: Dict[str, Any],
                              ttl: int = 300) -> bool:
        """Cache computed aggregations for dashboards"""
        key = f"agg:{aggregation_type}:{project_id}"
        return await self.set(CacheType.AGGREGATION, key, data, ttl)
    
    async def get_aggregation(self,
                            aggregation_type: str,
                            project_id: str) -> Optional[Dict[str, Any]]:
        """Get cached aggregation"""
        key = f"agg:{aggregation_type}:{project_id}"
        return await self.get(CacheType.AGGREGATION, key)
    
    async def invalidate_pattern(self,
                               cache_type: CacheType,
                               pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        client = self.clients.get(cache_type)
        
        if not client:
            return 0
            
        try:
            full_pattern = self._generate_key(cache_type, pattern)
            keys = list(client.scan_iter(match=full_pattern))
            
            if keys:
                deleted = client.delete(*keys)
                return int(deleted) if deleted else 0
            return 0
            
        except Exception as e:
            print(f"❌ Error invalidating pattern: {e}")
            return 0
    
    async def get_stats(self, cache_type: Optional[CacheType] = None) -> Dict[str, Any]:
        """Get cache statistics"""
        if cache_type:
            # Stats for specific cache type
            client = self.clients.get(cache_type)
            stats = self.stats[cache_type]
            
            if client:
                try:
                    info = client.info("memory")
                    db_info = client.info("keyspace")
                    
                    db_key = f"db{self.cache_configs[cache_type]['db']}"
                    db_stats = db_info.get(db_key, {})
                    
                    return {
                        "cache_type": cache_type.name,
                        "hits": stats.hits,
                        "misses": stats.misses,
                        "hit_rate": stats.hits / (stats.hits + stats.misses) if (stats.hits + stats.misses) > 0 else 0,
                        "sets": stats.sets,
                        "memory_usage_mb": float(info.get("used_memory", 0)) / (1024 * 1024) if isinstance(info, dict) else 0.0,
                        "keys_count": db_stats.get("keys", 0) if isinstance(db_stats, dict) else 0
                    }
                except:
                    pass
            
            # Return basic stats if Redis not available
            return {
                "cache_type": cache_type.name,
                "hits": stats.hits,
                "misses": stats.misses,
                "hit_rate": stats.hits / (stats.hits + stats.misses) if (stats.hits + stats.misses) > 0 else 0,
                "sets": stats.sets
            }
        else:
            # Stats for all cache types
            all_stats = {}
            for ct in CacheType:
                all_stats[ct.name] = await self.get_stats(ct)
            return all_stats
    
    async def flush_cache(self, cache_type: CacheType) -> bool:
        """Flush all data from a specific cache type"""
        client = self.clients.get(cache_type)
        
        if not client:
            return True
            
        try:
            client.flushdb()
            # Reset stats
            self.stats[cache_type] = CacheStats()
            return True
            
        except Exception as e:
            print(f"❌ Error flushing cache: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        try:
            health_status = {
                "status": "healthy" if REDIS_AVAILABLE else "mock_mode",
                "service": "redis_cache",
                "version": self.version,
                "port": self.port,
                "caches": {}
            }
            
            for cache_type, client in self.clients.items():
                if client:
                    try:
                        client.ping()
                        status = "connected"
                    except:
                        status = "disconnected"
                else:
                    status = "not_initialized"
                    
                health_status["caches"][cache_type.name] = status
            
            return health_status
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "redis_cache",
                "version": self.version,
                "error": str(e)
            }
    
    # MCP Protocol Methods
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        if name == "get":
            cache_type = CacheType[arguments.get("cache_type", "CODING").upper()]
            key = arguments.get("key", "")
            
            value = await self.get(cache_type, key)
            return {"value": value, "found": value is not None}
            
        elif name == "set":
            cache_type = CacheType[arguments.get("cache_type", "CODING").upper()]
            key = arguments.get("key", "")
            value = arguments.get("value")
            ttl = arguments.get("ttl")
            
            success = await self.set(cache_type, key, value, ttl)
            return {"success": success}
            
        elif name == "delete":
            cache_type = CacheType[arguments.get("cache_type", "CODING").upper()]
            key = arguments.get("key", "")
            
            success = await self.delete(cache_type, key)
            return {"success": success}
            
        elif name == "cache_aggregation":
            aggregation_type = arguments.get("aggregation_type", "")
            project_id = arguments.get("project_id", "")
            data = arguments.get("data", {})
            ttl = arguments.get("ttl", 300)
            
            success = await self.cache_aggregation(aggregation_type, project_id, data, ttl)
            return {"success": success}
            
        elif name == "get_aggregation":
            aggregation_type = arguments.get("aggregation_type", "")
            project_id = arguments.get("project_id", "")
            
            data = await self.get_aggregation(aggregation_type, project_id)
            return {"data": data, "found": data is not None}
            
        elif name == "get_stats":
            cache_type_str = arguments.get("cache_type")
            cache_type = CacheType[cache_type_str.upper()] if cache_type_str else None
            
            return await self.get_stats(cache_type)
            
        elif name == "flush_cache":
            cache_type = CacheType[arguments.get("cache_type", "CODING").upper()]
            
            success = await self.flush_cache(cache_type)
            return {"success": success}
            
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get MCP tool descriptions"""
        return [
            {
                "name": "get",
                "description": "Get value from cache",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cache_type": {
                            "type": "string",
                            "enum": ["coding", "business", "aggregation"],
                            "description": "Cache type"
                        },
                        "key": {"type": "string", "description": "Cache key"}
                    },
                    "required": ["cache_type", "key"]
                }
            },
            {
                "name": "set",
                "description": "Set value in cache",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cache_type": {
                            "type": "string",
                            "enum": ["coding", "business", "aggregation"],
                            "description": "Cache type"
                        },
                        "key": {"type": "string", "description": "Cache key"},
                        "value": {"description": "Value to cache"},
                        "ttl": {"type": "integer", "description": "TTL in seconds"}
                    },
                    "required": ["cache_type", "key", "value"]
                }
            },
            {
                "name": "cache_aggregation",
                "description": "Cache dashboard aggregation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "aggregation_type": {"type": "string"},
                        "project_id": {"type": "string"},
                        "data": {"type": "object"},
                        "ttl": {"type": "integer", "default": 300}
                    },
                    "required": ["aggregation_type", "project_id", "data"]
                }
            },
            {
                "name": "get_stats",
                "description": "Get cache statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cache_type": {
                            "type": "string",
                            "enum": ["coding", "business", "aggregation"],
                            "description": "Specific cache type (optional)"
                        }
                    }
                }
            }
        ]


# MCP Server entry point
async def main():
    """Main entry point for the MCP server"""
    server = RedisCacheMCPServer()
    await server.initialize()
    
    # In real implementation, would start MCP protocol server
    print(f"🚀 Redis Cache MCP Server running on port {server.port}")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(60)
            # Could add periodic stats logging here
    except KeyboardInterrupt:
        print("\n👋 Shutting down Redis Cache Server")


if __name__ == "__main__":
    asyncio.run(main())
