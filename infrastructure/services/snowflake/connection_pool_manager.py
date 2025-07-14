"""
ModernStack Connection Pool Manager
Implements connection pooling for improved performance and resource management
Replaces individual connections with managed pool
"""

import asyncio
import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any

# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3
# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3 import DictCursor

# REMOVED: ModernStack dependency

logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """Configuration for connection pool"""

    min_size: int = 5
    max_size: int = 20
    max_idle_time: int = 300  # 5 minutes
    connection_timeout: int = 30
    retry_attempts: int = 3
    health_check_interval: int = 60  # 1 minute


@dataclass
class PooledConnection:
    """Wrapper for pooled ModernStack connection"""

    connection: modern_stack.connector.ModernStackConnection
    created_at: float
    last_used: float
    in_use: bool = False

    @property
    def is_expired(self) -> bool:
        """Check if connection has exceeded max idle time"""
        return time.time() - self.last_used > 300  # 5 minutes

    @property
    def age(self) -> float:
        """Get connection age in seconds"""
        return time.time() - self.created_at


class ModernStackConnectionPool:
    """
    Thread-safe connection pool for ModernStack
    Manages connection lifecycle, health checks, and automatic cleanup
    """

    def __init__(self, config: PoolConfig | None = None):
        self.config = config or PoolConfig()
# REMOVED: ModernStack dependency.get_connection_params()

        # Pool management
        self._pool: Queue[PooledConnection] = Queue(maxsize=self.config.max_size)
        self._active_connections: dict[int, PooledConnection] = {}
        self._pool_lock = threading.RLock()
        self._shutdown = False
        self._shutdown_event = threading.Event()  # Add shutdown event

        # Statistics
        self._stats = {
            "total_created": 0,
            "total_destroyed": 0,
            "current_active": 0,
            "current_idle": 0,
            "pool_hits": 0,
            "pool_misses": 0,
        }

        # Initialize pool
        self._initialize_pool()

        # Start background tasks
        self._health_check_thread = threading.Thread(
            target=self._health_check_worker, daemon=True
        )
        self._health_check_thread.start()

        logger.info(
# REMOVED: ModernStack dependency.max_size} connections"
        )

    def _initialize_pool(self):
        """Initialize pool with minimum connections"""
        for _ in range(self.config.min_size):
            try:
                conn = self._create_connection()
                self._pool.put(conn, block=False)
                self._stats["total_created"] += 1
                self._stats["current_idle"] += 1
            except Exception as e:
                logger.exception(f"Failed to initialize pool connection: {e}")

    def _create_connection(self) -> PooledConnection:
        """Create a new pooled connection"""
        try:
            raw_conn = self.modern_stack_connection(**self.connection_params)

            # Test connection
            cursor = raw_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()

            pooled_conn = PooledConnection(
                connection=raw_conn, created_at=time.time(), last_used=time.time()
            )

            logger.debug("Created new ModernStack connection")
            return pooled_conn

        except Exception as e:
            logger.exception(f"Failed to create ModernStack connection: {e}")
            raise

    def _destroy_connection(self, pooled_conn: PooledConnection):
        """Safely destroy a connection"""
        try:
            if pooled_conn.connection and not pooled_conn.connection.is_closed():
                pooled_conn.connection.close()
            self._stats["total_destroyed"] += 1
            logger.debug("Destroyed ModernStack connection")
        except Exception as e:
            logger.warning(f"Error destroying connection: {e}")

    def _health_check_worker(self):
        """Background worker for connection health checks and cleanup"""
        while not self._shutdown:
            try:
                self._cleanup_expired_connections()
                self._ensure_minimum_connections()

                # Use event.wait() instead of time.sleep() for interruptible waiting
                if self._shutdown_event.wait(timeout=self.config.health_check_interval):
                    # Shutdown event was set, exit immediately
                    break

            except Exception as e:
                logger.exception(f"Health check worker error: {e}")
                # Brief pause on error, also interruptible
                if self._shutdown_event.wait(timeout=5):
                    break

    def _cleanup_expired_connections(self):
        """Remove expired connections from pool"""
        with self._pool_lock:
            expired_connections = []

            # Check idle connections in pool
            temp_queue = Queue()
            while not self._pool.empty():
                try:
                    pooled_conn = self._pool.get_nowait()
                    if pooled_conn.is_expired:
                        expired_connections.append(pooled_conn)
                        self._stats["current_idle"] -= 1
                    else:
                        temp_queue.put(pooled_conn)
                except Empty:
                    break

            # Put non-expired connections back
            while not temp_queue.empty():
                self._pool.put(temp_queue.get())

            # Destroy expired connections
            for conn in expired_connections:
                self._destroy_connection(conn)
                logger.debug("Cleaned up expired connection")

    def _ensure_minimum_connections(self):
        """Ensure pool has minimum number of connections"""
        with self._pool_lock:
            current_total = self._pool.qsize() + len(self._active_connections)
            needed = self.config.min_size - current_total

            for _ in range(needed):
                try:
                    conn = self._create_connection()
                    self._pool.put(conn, block=False)
                    self._stats["total_created"] += 1
                    self._stats["current_idle"] += 1
                except Exception as e:
                    logger.exception(f"Failed to create minimum connection: {e}")
                    break

    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool

        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
        """
        pooled_conn = None
        try:
            # Try to get connection from pool
            with self._pool_lock:
                try:
                    pooled_conn = self._pool.get_nowait()
                    self._stats["pool_hits"] += 1
                    self._stats["current_idle"] -= 1
                except Empty:
                    # Pool is empty, create new connection if under max
                    if len(self._active_connections) < self.config.max_size:
                        pooled_conn = self._create_connection()
                        self._stats["pool_misses"] += 1
                        self._stats["total_created"] += 1
                    else:
                        raise RuntimeError("Connection pool exhausted")

                # Mark as active
                pooled_conn.in_use = True
                pooled_conn.last_used = time.time()
                self._active_connections[id(pooled_conn)] = pooled_conn
                self._stats["current_active"] += 1

            # Test connection before use
            if pooled_conn.connection.is_closed():
                # Connection is closed, create new one
                self._destroy_connection(pooled_conn)
                pooled_conn = self._create_connection()
                pooled_conn.in_use = True
                pooled_conn.last_used = time.time()
                self._active_connections[id(pooled_conn)] = pooled_conn

            yield pooled_conn.connection

        except Exception as e:
            logger.exception(f"Error using pooled connection: {e}")
            if pooled_conn:
                # Destroy problematic connection
                self._destroy_connection(pooled_conn)
                with self._pool_lock:
                    self._active_connections.pop(id(pooled_conn), None)
                    self._stats["current_active"] -= 1
            raise
        finally:
            # Return connection to pool
            if pooled_conn and id(pooled_conn) in self._active_connections:
                with self._pool_lock:
                    pooled_conn.in_use = False
                    pooled_conn.last_used = time.time()
                    self._active_connections.pop(id(pooled_conn))
                    self._stats["current_active"] -= 1

                    # Return to pool if not expired and pool not full
                    if not pooled_conn.is_expired and not self._pool.full():
                        self._pool.put(pooled_conn)
                        self._stats["current_idle"] += 1
                    else:
                        self._destroy_connection(pooled_conn)

    def execute_query(self, query: str, *args, **kwargs) -> Any:
        """
        Execute a query using a pooled connection

        Args:
            query: SQL query to execute
            *args: Query parameters
            **kwargs: Additional options (fetch_mode, cursor_class)

        Returns:
            Query result
        """
        fetch_mode = kwargs.get("fetch_mode", "one")  # 'one', 'all', 'many'
        cursor_class = kwargs.get("cursor_class", DictCursor)

        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_class)
            try:
                cursor.execute(query, *args)

                if fetch_mode == "one":
                    result = cursor.fetchone()
                elif fetch_mode == "all":
                    result = cursor.fetchall()
                elif fetch_mode == "many":
                    size = kwargs.get("size", 100)
                    result = cursor.fetchmany(size)
                else:
                    result = cursor.rowcount

                return result
            finally:
                cursor.close()

    async def execute_query_async(self, query: str, *args, **kwargs) -> Any:
        """
        Execute a query asynchronously using thread pool

        Args:
            query: SQL query to execute
            *args: Query parameters
            **kwargs: Additional options

        Returns:
            Query result
        """
        return await asyncio.to_thread(self.execute_query, query, *args, **kwargs)

    def get_stats(self) -> dict[str, Any]:
        """Get connection pool statistics"""
        with self._pool_lock:
            return {
                **self._stats,
                "current_idle": self._pool.qsize(),
                "current_active": len(self._active_connections),
                "pool_size": self._pool.qsize() + len(self._active_connections),
                "max_size": self.config.max_size,
                "min_size": self.config.min_size,
            }

    def health_check(self) -> dict[str, Any]:
        """Perform health check on the connection pool"""
        try:
            # Test a connection from the pool
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT CURRENT_VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()

            stats = self.get_stats()

            return {
                "status": "healthy",
                "modern_stack_version": version,
                "pool_stats": stats,
                "timestamp": time.time(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "pool_stats": self.get_stats(),
                "timestamp": time.time(),
            }

    def shutdown(self):
        """Shutdown the connection pool"""
        logger.info("Shutting down ModernStack connection pool...")
        self._shutdown = True
        self._shutdown_event.set()  # Signal shutdown to health check worker

        # Wait for health check thread to finish (with timeout)
        if self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5)

        # Close all active connections
        with self._pool_lock:
            for pooled_conn in self._active_connections.values():
                self._destroy_connection(pooled_conn)

            # Close all idle connections
            while not self._pool.empty():
                try:
                    pooled_conn = self._pool.get_nowait()
                    self._destroy_connection(pooled_conn)
                except Empty:
                    break

        logger.info("Connection pool shutdown complete")


# Global connection pool instance
_global_pool: ModernStackConnectionPool | None = None
_pool_lock = threading.Lock()


def get_connection_pool() -> ModernStackConnectionPool:
    """Get the global connection pool instance"""
    global _global_pool

    if _global_pool is None:
        with _pool_lock:
            if _global_pool is None:
                _global_pool = ModernStackConnectionPool()

    return _global_pool


def shutdown_connection_pool():
    """Shutdown the global connection pool"""
    global _global_pool

    if _global_pool:
        _global_pool.shutdown()
        _global_pool = None


# Convenience functions
def execute_modern_stack_query(query: str, *args, **kwargs) -> Any:
    """Execute a ModernStack query using the global connection pool"""
    pool = get_connection_pool()
    return pool.execute_query(query, *args, **kwargs)


async def execute_modern_stack_query_async(query: str, *args, **kwargs) -> Any:
    """Execute a ModernStack query asynchronously using the global connection pool"""
    pool = get_connection_pool()
    return await pool.execute_query_async(query, *args, **kwargs)


def get_modern_stack_connection():
    """Get a ModernStack connection from the global pool"""
    pool = get_connection_pool()
    return pool.get_connection()


def get_pool_stats() -> dict[str, Any]:
    """Get statistics for the global connection pool"""
    pool = get_connection_pool()
    return pool.get_stats()


def pool_health_check() -> dict[str, Any]:
    """Perform health check on the global connection pool"""
    pool = get_connection_pool()
    return pool.health_check()
