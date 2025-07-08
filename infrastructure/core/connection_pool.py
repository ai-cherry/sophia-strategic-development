"""
Snowflake Connection Pool Implementation
Thread-safe connection pooling with monitoring and health checks

Features:
- Configurable pool size with min/max connections
- Connection validation and health checks
- Automatic retry and reconnection
- Performance metrics collection
- Connection lifecycle management
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import snowflake.connector
from snowflake.connector import SnowflakeConnection
from snowflake.connector.errors import DatabaseError, OperationalError

from core.config_manager import get_config_value as config as esc_config

logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """Configuration for connection pool"""

    min_size: int = 5
    max_size: int = 20
    acquire_timeout: float = 30.0
    idle_timeout: int = 3600  # 1 hour
    validation_interval: int = 300  # 5 minutes
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Snowflake connection parameters
    account: str = field(default_factory=lambda: esc_config.get("snowflake_account"))
    user: str = field(default_factory=lambda: esc_config.get("snowflake_user"))
    password: str = field(default_factory=lambda: esc_config.get("snowflake_password"))
    role: str = field(
        default_factory=lambda: esc_config.get(
            "snowflake_role", "ROLE_SOPHIA_AI_AGENT_SERVICE"
        
    
    warehouse: str = field(
        default_factory=lambda: esc_config.get(
            "snowflake_warehouse", "WH_SOPHIA_AGENT_QUERY"
        
    
    database: str = field(
        default_factory=lambda: esc_config.get("snowflake_database", "SOPHIA_AI")
    
    schema: str = field(
        default_factory=lambda: esc_config.get("snowflake_schema", "CORE")
    


@dataclass
class ConnectionInfo:
    """Information about a pooled connection"""

    connection: SnowflakeConnection
    created_at: datetime
    last_used: datetime
    use_count: int = 0
    in_use: bool = False
    connection_id: str = ""

    def __post_init__(self):
        if hasattr(self.connection, "session_id"):
            self.connection_id = str(self.connection.session_id)


@dataclass
class PoolMetrics:
    """Metrics for connection pool monitoring"""

    total_connections_created: int = 0
    total_connections_closed: int = 0
    total_acquisitions: int = 0
    total_releases: int = 0
    failed_acquisitions: int = 0
    validation_failures: int = 0
    average_acquisition_time: float = 0.0
    current_size: int = 0
    active_connections: int = 0
    idle_connections: int = 0

    def record_acquisition(self, duration: float):
        """Record connection acquisition metrics"""
        self.total_acquisitions += 1
        # Update rolling average
        self.average_acquisition_time = (
            self.average_acquisition_time * (self.total_acquisitions - 1) + duration
         / self.total_acquisitions


class ConnectionWrapper:
    """Wrapper for connection to ensure proper release back to pool"""

    def __init__(
        self, connection_info: ConnectionInfo, pool: "SnowflakeConnectionPool"
    :
        self.connection_info = connection_info
        self.pool = pool
        self.connection = connection_info.connection

    def __getattr__(self, name):
        """Proxy attribute access to underlying connection"""
        return getattr(self.connection, name)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Return connection to pool on exit"""
        await self.pool.release_connection(self.connection_info)


class SnowflakeConnectionPool:
    """Thread-safe connection pool with monitoring"""

    def __init__(self, config: PoolConfig | None = None):
        self.config = config or PoolConfig()
        self.pool: asyncio.Queue[ConnectionInfo] = asyncio.Queue()
        self.all_connections: dict[str, ConnectionInfo] = {}
        self.metrics = PoolMetrics()
        self._lock = asyncio.Lock()
        self._closed = False
        self._validation_task = None

    async def initialize(self):
        """Initialize connection pool"""
        logger.info(
            f"Initializing Snowflake connection pool with min_size={self.config.min_size}"
        

        # Create initial connections
        for _ in range(self.config.min_size):
            try:
                conn_info = await self._create_connection()
                await self.pool.put(conn_info)
            except Exception as e:
                logger.error(f"Failed to create initial connection: {e}")

        # Start validation task
        self._validation_task = asyncio.create_task(self._validation_loop())

        self.metrics.current_size = self.pool.qsize()
        self.metrics.idle_connections = self.pool.qsize()

        logger.info(
            f"Connection pool initialized with {self.metrics.current_size} connections"
        

    async def close(self):
        """Close all connections and shutdown pool"""
        self._closed = True

        # Cancel validation task
        if self._validation_task:
            self._validation_task.cancel()

        # Close all connections
        async with self._lock:
            for conn_info in self.all_connections.values():
                try:
                    conn_info.connection.close()
                    self.metrics.total_connections_closed += 1
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")

            self.all_connections.clear()

        logger.info("Connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool with timeout"""
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        start_time = time.time()
        connection_info = None

        try:
            # Try to get from pool with timeout
            try:
                connection_info = await asyncio.wait_for(
                    self.pool.get(), timeout=self.config.acquire_timeout
                
            except TimeoutError:
                # Pool exhausted, try to create new connection if under max_size
                if self.metrics.current_size < self.config.max_size:
                    connection_info = await self._create_connection()
                else:
                    self.metrics.failed_acquisitions += 1
                    raise PoolExhaustedError(
                        f"Connection pool exhausted (size={self.metrics.current_size}, "
                        f"max={self.config.max_size}"
                    

            # Validate connection
            if not await self._validate_connection(connection_info):
                # Connection invalid, create new one
                await self._close_connection(connection_info)
                connection_info = await self._create_connection()

            # Mark connection as in use
            connection_info.in_use = True
            connection_info.last_used = datetime.now()
            connection_info.use_count += 1

            # Update metrics
            acquisition_time = time.time() - start_time
            self.metrics.record_acquisition(acquisition_time)
            self.metrics.active_connections += 1
            self.metrics.idle_connections = max(0, self.metrics.idle_connections - 1)

            # Yield wrapped connection
            yield ConnectionWrapper(connection_info, self)

        except Exception:
            # Return connection to pool on error
            if connection_info and not self._closed:
                await self.release_connection(connection_info)
            raise
        finally:
            # Release connection when done (if not already released)
            if connection_info and not self._closed and connection_info.in_use:
                await self.release_connection(connection_info)

    async def release_connection(self, connection_info: ConnectionInfo):
        """Release connection back to pool"""
        if self._closed:
            # Pool is closed, just close the connection
            await self._close_connection(connection_info)
            return

        try:
            # Mark as not in use
            connection_info.in_use = False
            connection_info.last_used = datetime.now()

            # Update metrics
            self.metrics.total_releases += 1
            self.metrics.active_connections = max(
                0, self.metrics.active_connections - 1
            

            # Check if connection is still valid
            if await self._validate_connection(connection_info):
                # Return to pool
                await self.pool.put(connection_info)
                self.metrics.idle_connections += 1
            else:
                # Close invalid connection
                await self._close_connection(connection_info)

                # Create replacement if below min_size
                if self.metrics.current_size < self.config.min_size:
                    try:
                        new_conn = await self._create_connection()
                        await self.pool.put(new_conn)
                    except Exception as e:
                        logger.error(f"Failed to create replacement connection: {e}")

        except Exception as e:
            logger.error(f"Error releasing connection: {e}")
            await self._close_connection(connection_info)

    async def _create_connection(self) -> ConnectionInfo:
        """Create new Snowflake connection"""
        for attempt in range(self.config.retry_attempts):
            try:
                # Create connection with parameters
                connection = # TODO: Replace with repository injection
    # repository.get_connection(
                    account=self.config.account,
                    user=self.config.user,
                    password=self.config.password,
                    role=self.config.role,
                    warehouse=self.config.warehouse,
                    database=self.config.database,
                    schema=self.config.schema,
                    autocommit=True,
                    network_timeout=30,
                    ocsp_response_cache_filename="/tmp/snowflake_ocsp_cache",
                

                # Create connection info
                conn_info = ConnectionInfo(
                    connection=connection,
                    created_at=datetime.now(),
                    last_used=datetime.now(),
                

                # Track connection
                async with self._lock:
                    self.all_connections[conn_info.connection_id] = conn_info
                    self.metrics.total_connections_created += 1
                    self.metrics.current_size += 1

                logger.debug(f"Created new connection: {conn_info.connection_id}")
                return conn_info

            except (DatabaseError, OperationalError) as e:
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise ConnectionError(
                        f"Failed to create connection after {self.config.retry_attempts} attempts: {e}"
                    

        # Should never reach here, but satisfy type checker
        raise ConnectionError("Failed to create connection - unexpected error")

    async def _close_connection(self, connection_info: ConnectionInfo):
        """Close a connection and remove from tracking"""
        try:
            connection_info.connection.close()
            logger.debug(f"Closed connection: {connection_info.connection_id}")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

        # Remove from tracking
        async with self._lock:
            self.all_connections.pop(connection_info.connection_id, None)
            self.metrics.total_connections_closed += 1
            self.metrics.current_size = max(0, self.metrics.current_size - 1)

    async def _validate_connection(self, connection_info: ConnectionInfo) -> bool:
        """Validate connection is still alive"""
        try:
            # Check connection age
            age = datetime.now() - connection_info.created_at
            if age > timedelta(seconds=self.config.idle_timeout):
                logger.debug(
                    f"Connection {connection_info.connection_id} exceeded idle timeout"
                
                return False

            # Execute test query
            cursor = connection_info.connection.cursor()
            # TODO: Replace with repository method
    # repository.execute_query("SELECT 1")
            cursor.close()

            return True

        except Exception as e:
            logger.debug(f"Connection validation failed: {e}")
            self.metrics.validation_failures += 1
            return False

    async def _validation_loop(self):
        """Background task to validate idle connections"""
        while not self._closed:
            try:
                await asyncio.sleep(self.config.validation_interval)

                # Get all idle connections
                idle_connections = []
                for _ in range(self.pool.qsize()):
                    try:
                        conn_info = self.pool.get_nowait()
                        idle_connections.append(conn_info)
                    except asyncio.QueueEmpty:
                        break

                # Validate each connection
                valid_connections = []
                for conn_info in idle_connections:
                    if await self._validate_connection(conn_info):
                        valid_connections.append(conn_info)
                    else:
                        await self._close_connection(conn_info)

                # Return valid connections to pool
                for conn_info in valid_connections:
                    await self.pool.put(conn_info)

                # Ensure minimum pool size
                while self.metrics.current_size < self.config.min_size:
                    try:
                        new_conn = await self._create_connection()
                        await self.pool.put(new_conn)
                    except Exception as e:
                        logger.error(f"Failed to maintain minimum pool size: {e}")
                        break

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in validation loop: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get current pool metrics"""
        return {
            "current_size": self.metrics.current_size,
            "active_connections": self.metrics.active_connections,
            "idle_connections": self.metrics.idle_connections,
            "total_created": self.metrics.total_connections_created,
            "total_closed": self.metrics.total_connections_closed,
            "total_acquisitions": self.metrics.total_acquisitions,
            "failed_acquisitions": self.metrics.failed_acquisitions,
            "average_acquisition_time_ms": self.metrics.average_acquisition_time * 1000,
            "validation_failures": self.metrics.validation_failures,
            "pool_config": {
                "min_size": self.config.min_size,
                "max_size": self.config.max_size,
                "acquire_timeout": self.config.acquire_timeout,
                "idle_timeout": self.config.idle_timeout,
            },
        }


class PoolExhaustedError(Exception):
    """Raised when connection pool is exhausted"""

    pass


class ConnectionError(Exception):
    """Raised when connection creation fails"""

    pass


# Global connection pool instance
_connection_pool: SnowflakeConnectionPool | None = None


async def get_connection_pool() -> SnowflakeConnectionPool:
    """Get or create global connection pool"""
    global _connection_pool

    if _connection_pool is None:
        _connection_pool = SnowflakeConnectionPool()
        await _connection_pool.initialize()

    return _connection_pool


async def close_connection_pool():
    """Close global connection pool"""
    global _connection_pool

    if _connection_pool:
        await _connection_pool.close()
        _connection_pool = None
