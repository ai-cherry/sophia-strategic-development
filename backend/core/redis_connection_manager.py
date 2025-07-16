"""
Redis Connection Manager for Sophia AI
Standardized Redis connections with pooling, async support, and authentication

Features:
- Connection pooling for performance
- Async and sync Redis clients
- Automatic environment detection (local vs Kubernetes)
- Authentication with GitHub secrets
- Health monitoring and reconnection
- Consistent configuration across all services

Date: July 15, 2025
"""

import logging
from typing import Optional, Dict, Any
import redis
import redis.asyncio as aioredis
from redis.connection import ConnectionPool
from backend.core.auto_esc_config import get_redis_config

logger = logging.getLogger(__name__)

class RedisConnectionManager:
    """Centralized Redis connection management for Sophia AI"""
    
    _instance: Optional['RedisConnectionManager'] = None
    _sync_pool: Optional[ConnectionPool] = None
    _async_pool: Optional[aioredis.ConnectionPool] = None
    _sync_client: Optional[redis.Redis] = None
    _async_client: Optional[aioredis.Redis] = None
    
    def __new__(cls) -> 'RedisConnectionManager':
        """Singleton pattern for consistent connections"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Redis connection manager"""
        if not hasattr(self, '_initialized'):
            self.config = get_redis_config()
            self._initialized = True
            logger.info("🔧 Redis Connection Manager initialized")
    
    def get_sync_client(self) -> redis.Redis:
        """
        Get synchronized Redis client with connection pooling
        
        Returns:
            Redis client for synchronous operations
        """
        if self._sync_client is None:
            if self._sync_pool is None:
                self._sync_pool = ConnectionPool(
                    host=self.config["host"],
                    port=self.config["port"],
                    password=self.config.get("password"),
                    db=self.config["db"],
                    decode_responses=self.config["decode_responses"],
                    encoding=self.config["encoding"],
                    socket_timeout=self.config["socket_timeout"],
                    socket_connect_timeout=self.config["socket_connect_timeout"],
                    socket_keepalive=self.config["socket_keepalive"],
                    max_connections=self.config["connection_pool_kwargs"]["max_connections"],
                    retry_on_timeout=self.config["retry_on_timeout"]
                )
            
            self._sync_client = redis.Redis(connection_pool=self._sync_pool)
            logger.info(f"✅ Sync Redis client connected to {self.config['host']}:{self.config['port']}")
        
        return self._sync_client
    
    async def get_async_client(self) -> aioredis.Redis:
        """
        Get asynchronous Redis client with connection pooling
        
        Returns:
            Async Redis client for asynchronous operations
        """
        if self._async_client is None:
            if self._async_pool is None:
                self._async_pool = aioredis.ConnectionPool(
                    host=self.config["host"],
                    port=self.config["port"],
                    password=self.config.get("password"),
                    db=self.config["db"],
                    decode_responses=self.config["decode_responses"],
                    encoding=self.config["encoding"],
                    socket_timeout=self.config["socket_timeout"],
                    socket_connect_timeout=self.config["socket_connect_timeout"],
                    socket_keepalive=self.config["socket_keepalive"],
                    max_connections=self.config["connection_pool_kwargs"]["max_connections"],
                    retry_on_timeout=self.config["retry_on_timeout"]
                )
            
            self._async_client = aioredis.Redis(connection_pool=self._async_pool)
            await self._async_client.ping()
            logger.info(f"✅ Async Redis client connected to {self.config['host']}:{self.config['port']}")
        
        return self._async_client
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform Redis health check
        
        Returns:
            Health status information
        """
        health = {
            "status": "healthy",
            "host": self.config["host"],
            "port": self.config["port"],
            "authenticated": bool(self.config.get("password")),
            "connection_pool_size": self.config["connection_pool_kwargs"]["max_connections"]
        }
        
        try:
            # Test sync client
            sync_client = self.get_sync_client()
            sync_result = sync_client.ping()
            health["sync_connection"] = "healthy" if sync_result else "failed"
            
            # Test async client
            async_client = await self.get_async_client()
            async_result = await async_client.ping()
            health["async_connection"] = "healthy" if async_result else "failed"
            
            # Connection pool info
            if self._sync_pool:
                health["sync_pool_created_connections"] = self._sync_pool.created_connections
                health["sync_pool_available_connections"] = len(self._sync_pool._available_connections)
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
            logger.error(f"❌ Redis health check failed: {e}")
        
        return health
    
    async def close_connections(self):
        """Close all Redis connections and cleanup resources"""
        try:
            if self._async_client:
                await self._async_client.close()
                self._async_client = None
                logger.info("✅ Async Redis client closed")
            
            if self._sync_client:
                self._sync_client.close()
                self._sync_client = None
                logger.info("✅ Sync Redis client closed")
            
            if self._async_pool:
                await self._async_pool.disconnect()
                self._async_pool = None
                logger.info("✅ Async Redis pool disconnected")
            
            if self._sync_pool:
                self._sync_pool.disconnect()
                self._sync_pool = None
                logger.info("✅ Sync Redis pool disconnected")
                
        except Exception as e:
            logger.error(f"❌ Error closing Redis connections: {e}")

# Global connection manager instance
redis_manager = RedisConnectionManager()

def get_redis_client() -> redis.Redis:
    """
    Get synchronous Redis client (for backward compatibility)
    
    Returns:
        Sync Redis client with connection pooling
    """
    return redis_manager.get_sync_client()

async def get_async_redis_client() -> aioredis.Redis:
    """
    Get asynchronous Redis client
    
    Returns:
        Async Redis client with connection pooling
    """
    return await redis_manager.get_async_client()

def create_redis_from_config() -> redis.Redis:
    """
    Create Redis client using current configuration
    
    Returns:
        Redis client configured for current environment
        
    Note:
        This is the main function MCP servers should use
    """
    config = get_redis_config()
    
    # Create client with all configuration options
    client = redis.Redis(
        host=config["host"],
        port=config["port"],
        password=config.get("password"),
        db=config["db"],
        decode_responses=config["decode_responses"],
        encoding=config["encoding"],
        socket_timeout=config["socket_timeout"],
        socket_connect_timeout=config["socket_connect_timeout"],
        socket_keepalive=config["socket_keepalive"],
        retry_on_timeout=config["retry_on_timeout"]
    )
    
    logger.info(f"✅ Redis client created: {config['host']}:{config['port']} (auth: {'yes' if config.get('password') else 'no'})")
    return client

async def create_async_redis_from_config() -> aioredis.Redis:
    """
    Create async Redis client using current configuration
    
    Returns:
        Async Redis client configured for current environment
    """
    config = get_redis_config()
    
    # Create async client with all configuration options
    client = aioredis.Redis(
        host=config["host"],
        port=config["port"],
        password=config.get("password"),
        db=config["db"],
        decode_responses=config["decode_responses"],
        encoding=config["encoding"],
        socket_timeout=config["socket_timeout"],
        socket_connect_timeout=config["socket_connect_timeout"],
        socket_keepalive=config["socket_keepalive"],
        retry_on_timeout=config["retry_on_timeout"]
    )
    
    # Test connection
    await client.ping()
    logger.info(f"✅ Async Redis client created: {config['host']}:{config['port']} (auth: {'yes' if config.get('password') else 'no'})")
    return client 