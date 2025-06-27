#!/usr/bin/env python3
"""
Optimized Global Connection Manager for Sophia AI
High-performance connection pooling and resource management
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import snowflake.connector
import snowflake.connector.pooling
from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Connection pool status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class ConnectionMetrics:
    """Connection pool performance metrics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    avg_connection_time_ms: float = 0.0
    total_queries_executed: int = 0
    avg_query_time_ms: float = 0.0
    cache_hit_ratio: float = 0.0


class OptimizedConnectionManager:
    """
    High-performance connection manager with pooling, monitoring, and optimization
    
    Features:
    - Connection pooling with health monitoring
    - Query performance tracking
    - Automatic connection recycling
    - Circuit breaker pattern
    - Connection warming
    """
    
    _instance: Optional['OptimizedConnectionManager'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls) -> 'OptimizedConnectionManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self._pool: Optional[snowflake.connector.pooling.SnowflakeConnectionPool] = None
        self._metrics = ConnectionMetrics()
        self._status = ConnectionStatus.OFFLINE
        self._circuit_breaker_failures = 0
        self._circuit_breaker_threshold = 5
        self._last_health_check = 0
        self._health_check_interval = 60  # seconds
        
        # Performance tracking
        self._query_times = []
        self._connection_times = []
        self._max_metrics_history = 1000
        
    async def initialize(self) -> None:
        """Initialize connection pool with optimized settings"""
        async with self._lock:
            if self._pool is not None:
                return
                
            try:
                logger.info("🚀 Initializing optimized Snowflake connection pool...")
                
                # Optimized pool configuration
                pool_config = {
                    'pool_size': int(config.get('snowflake_pool_size', 10)),
                    'pool_timeout': int(config.get('snowflake_pool_timeout', 30)),
                    'pool_recycle': int(config.get('snowflake_pool_recycle', 3600)),  # 1 hour
                    'user': config.get('snowflake_user'),
                    'password': config.get('snowflake_password'),
                    'account': config.get('snowflake_account'),
                    'warehouse': config.get('snowflake_warehouse', 'COMPUTE_WH'),
                    'database': config.get('snowflake_database', 'SOPHIA_AI'),
                    'schema': config.get('snowflake_schema', 'PUBLIC'),
                    'role': config.get('snowflake_role', 'ACCOUNTADMIN'),
                    'client_session_keep_alive': True,
                    'client_session_keep_alive_heartbeat_frequency': 3600,
                    'network_timeout': 60,
                    'login_timeout': 30,
                }
                
                self._pool = snowflake.connector.pooling.SnowflakeConnectionPool(**pool_config)
                
                # Warm up the pool
                await self._warm_up_pool()
                
                self._status = ConnectionStatus.HEALTHY
                self._circuit_breaker_failures = 0
                
                logger.info("✅ Connection pool initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize connection pool: {e}")
                self._status = ConnectionStatus.CRITICAL
                raise
    
    async def _warm_up_pool(self) -> None:
        """Warm up connection pool by creating initial connections"""
        try:
            logger.info("🔥 Warming up connection pool...")
            
            # Create and test initial connections
            warm_up_tasks = []
            for i in range(min(3, int(config.get('snowflake_pool_size', 10)))):
                warm_up_tasks.append(self._test_connection())
            
            await asyncio.gather(*warm_up_tasks, return_exceptions=True)
            logger.info("✅ Connection pool warmed up successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Connection pool warm-up partially failed: {e}")
    
    async def _test_connection(self) -> bool:
        """Test a single connection from the pool"""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            return False
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a connection from the pool with performance monitoring
        
        Usage:
            async with connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
                results = cursor.fetchall()
        """
        if self._pool is None:
            await self.initialize()
        
        # Circuit breaker check
        if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
            if time.time() - self._last_health_check < self._health_check_interval:
                raise Exception("Circuit breaker open - too many connection failures")
            else:
                # Reset circuit breaker after interval
                self._circuit_breaker_failures = 0
        
        connection = None
        start_time = time.time()
        
        try:
            # Get connection from pool
            connection = self._pool.get_connection(timeout=30)
            connection_time_ms = (time.time() - start_time) * 1000
            
            # Track connection performance
            self._track_connection_time(connection_time_ms)
            self._metrics.active_connections += 1
            
            yield connection
            
            # Reset circuit breaker on success
            self._circuit_breaker_failures = 0
            
        except Exception as e:
            # Track failures for circuit breaker
            self._circuit_breaker_failures += 1
            self._metrics.failed_connections += 1
            
            logger.error(f"Connection error: {e}")
            raise
            
        finally:
            if connection:
                try:
                    connection.close()  # Return to pool
                    self._metrics.active_connections -= 1
                except Exception as e:
                    logger.warning(f"Error returning connection to pool: {e}")
    
    async def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        """
        Execute query with performance monitoring and error handling
        
        Args:
            query: SQL query to execute
            params: Query parameters for prepared statements
            
        Returns:
            Query results
        """
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Determine if we need to fetch results
                if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                    results = cursor.fetchall()
                else:
                    results = cursor.rowcount
                
                # Track query performance
                query_time_ms = (time.time() - start_time) * 1000
                self._track_query_time(query_time_ms)
                self._metrics.total_queries_executed += 1
                
                return results
                
        except Exception as e:
            query_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Query execution failed ({query_time_ms:.1f}ms): {e}")
            raise
    
    async def execute_batch_queries(self, queries: list) -> list:
        """
        Execute multiple queries in a single connection for better performance
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            List of query results
        """
        results = []
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for query, params in queries:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                        results.append(cursor.fetchall())
                    else:
                        results.append(cursor.rowcount)
                
                # Track batch performance
                batch_time_ms = (time.time() - start_time) * 1000
                self._metrics.total_queries_executed += len(queries)
                
                logger.info(f"✅ Executed {len(queries)} queries in batch ({batch_time_ms:.1f}ms)")
                
                return results
                
        except Exception as e:
            batch_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Batch query execution failed ({batch_time_ms:.1f}ms): {e}")
            raise
    
    def _track_connection_time(self, time_ms: float) -> None:
        """Track connection establishment time for metrics"""
        self._connection_times.append(time_ms)
        if len(self._connection_times) > self._max_metrics_history:
            self._connection_times.pop(0)
        
        # Update average
        self._metrics.avg_connection_time_ms = sum(self._connection_times) / len(self._connection_times)
    
    def _track_query_time(self, time_ms: float) -> None:
        """Track query execution time for metrics"""
        self._query_times.append(time_ms)
        if len(self._query_times) > self._max_metrics_history:
            self._query_times.pop(0)
        
        # Update average
        self._metrics.avg_query_time_ms = sum(self._query_times) / len(self._query_times)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status and metrics"""
        try:
            # Test connection if needed
            if time.time() - self._last_health_check > self._health_check_interval:
                connection_test = await self._test_connection()
                self._last_health_check = time.time()
                
                if not connection_test:
                    self._status = ConnectionStatus.DEGRADED
                elif self._status == ConnectionStatus.DEGRADED:
                    self._status = ConnectionStatus.HEALTHY
            
            # Get pool statistics
            pool_stats = {}
            if self._pool:
                try:
                    pool_stats = {
                        'pool_size': self._pool.pool_size,
                        'pool_timeout': self._pool.pool_timeout,
                    }
                except:
                    pass
            
            return {
                'status': self._status.value,
                'metrics': {
                    'total_connections': self._metrics.total_connections,
                    'active_connections': self._metrics.active_connections,
                    'failed_connections': self._metrics.failed_connections,
                    'avg_connection_time_ms': round(self._metrics.avg_connection_time_ms, 2),
                    'avg_query_time_ms': round(self._metrics.avg_query_time_ms, 2),
                    'total_queries_executed': self._metrics.total_queries_executed,
                },
                'pool_config': pool_stats,
                'circuit_breaker': {
                    'failures': self._circuit_breaker_failures,
                    'threshold': self._circuit_breaker_threshold,
                    'status': 'open' if self._circuit_breaker_failures >= self._circuit_breaker_threshold else 'closed'
                },
                'performance': {
                    'recent_connection_times': self._connection_times[-10:] if self._connection_times else [],
                    'recent_query_times': self._query_times[-10:] if self._query_times else [],
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': ConnectionStatus.CRITICAL.value,
                'error': str(e)
            }
    
    async def close(self) -> None:
        """Close connection pool and cleanup resources"""
        if self._pool:
            try:
                # Note: Snowflake connector doesn't have explicit pool close
                # Connections will be closed when pool is garbage collected
                logger.info("🔒 Connection pool closed")
                self._pool = None
                self._status = ConnectionStatus.OFFLINE
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")


# Global instance
connection_manager = OptimizedConnectionManager()


# Convenience functions for backward compatibility
async def get_connection():
    """Get connection from global connection manager"""
    return connection_manager.get_connection()


async def execute_query(query: str, params: Optional[tuple] = None):
    """Execute query using global connection manager"""
    return await connection_manager.execute_query(query, params)


async def execute_batch_queries(queries: list):
    """Execute batch queries using global connection manager"""
    return await connection_manager.execute_batch_queries(queries)


async def get_health_status():
    """Get health status from global connection manager"""
    return await connection_manager.get_health_status()

