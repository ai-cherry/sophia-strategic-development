"""
Snowflake Connection Pool Manager
Manages separate connection pools for direct and MCP execution modes.
"""

import asyncio
import time
import uuid
from dataclasses import dataclass
from typing import Any, Union

import structlog
from prometheus_client import Gauge

from backend.core.config import get_config_value
from backend.integrations.snowflake_mcp_client import Session, SnowflakeMCPClient

logger = structlog.get_logger(__name__)

# Prometheus metrics
snowflake_pool_size = Gauge("snowflake_pool_size", "Current pool size", ["mode"])

snowflake_pool_in_use = Gauge(
    "snowflake_pool_in_use", "Connections currently in use", ["mode"]
)

snowflake_pool_wait_time = Gauge(
    "snowflake_pool_wait_time_ms",
    "Average wait time for connection acquisition",
    ["mode"],
)


@dataclass
class PoolConfig:
    """Configuration for connection pools"""

    direct_pool_size: int = 10
    mcp_pool_size: int = 20
    acquire_timeout: float = 30.0
    idle_timeout: float = 300.0  # 5 minutes
    max_lifetime: float = 3600.0  # 1 hour


@dataclass
class PoolMetrics:
    """Metrics for pool performance"""

    total_acquisitions: int = 0
    total_releases: int = 0
    total_timeouts: int = 0
    total_wait_time: float = 0.0
    avg_wait_ms: float = 0.0
    current_size: int = 0
    in_use: int = 0


class PoolExhaustedError(Exception):
    """Raised when connection pool is exhausted"""

    pass


class ConnectionWrapper:
    """Wrapper for direct Snowflake connections"""

    def __init__(self, connection, pool_id: str):
        self.connection = connection
        self.pool_id = pool_id
        self.created_at = time.time()
        self.last_used_at = time.time()
        self.use_count = 0

    async def execute_async(self, sql: str, params: dict | None = None):
        """Execute SQL asynchronously"""
        self.last_used_at = time.time()
        self.use_count += 1

        # For now, use sync execution in thread pool
        # In production, use snowflake-connector-python[async]
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.connection.execute, sql, params)
            result = await asyncio.get_event_loop().run_in_executor(None, future.result)
            return result.fetchall()

    def is_expired(self, max_lifetime: float, idle_timeout: float) -> bool:
        """Check if connection should be recycled"""
        now = time.time()

        if now - self.created_at > max_lifetime:
            return True

        if now - self.last_used_at > idle_timeout:
            return True

        return False

    def close(self):
        """Close the underlying connection"""
        try:
            self.connection.close()
        except Exception as e:
            logger.warning("Error closing connection", error=str(e))


class SnowflakePoolManager:
    """
    Manages connection pools for both direct and MCP modes.
    Provides connection acquisition, release, and health monitoring.
    """

    def __init__(self, config: PoolConfig | None = None):
        self.config = config or PoolConfig()

        # Get configuration from environment
        self.config.direct_pool_size = int(
            get_config_value("SOPHIA_SF_POOL_DIRECT", str(self.config.direct_pool_size))
        )
        self.config.mcp_pool_size = int(
            get_config_value("SOPHIA_SF_POOL_MCP", str(self.config.mcp_pool_size))
        )

        # Connection pools
        self.direct_pool = asyncio.Queue(maxsize=self.config.direct_pool_size)
        self.mcp_pool = asyncio.Queue(maxsize=self.config.mcp_pool_size)

        # Track connections in use
        self.direct_in_use: dict[str, ConnectionWrapper] = {}
        self.mcp_in_use: dict[str, Session] = {}

        # Metrics
        self.direct_metrics = PoolMetrics()
        self.mcp_metrics = PoolMetrics()

        # MCP client for creating sessions
        self.mcp_client: SnowflakeMCPClient | None = None

        # Background tasks
        self._cleanup_task: asyncio.Task | None = None

        logger.info(
            "SnowflakePoolManager initialized",
            direct_pool_size=self.config.direct_pool_size,
            mcp_pool_size=self.config.mcp_pool_size,
        )

    async def initialize(self):
        """Initialize the pool manager and create initial connections"""
        # Create MCP client
        try:
            self.mcp_client = SnowflakeMCPClient()
            logger.info("MCP client initialized")
        except Exception as e:
            logger.warning("Failed to initialize MCP client", error=str(e))

        # Pre-create some connections
        await self._ensure_minimum_connections()

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        # Update metrics
        self._update_metrics()

    async def acquire(self, mode: str) -> Union[ConnectionWrapper, Session]:
        """
        Acquire a connection from the pool.

        Args:
            mode: Either "direct" or "mcp"

        Returns:
            Connection wrapper or MCP session

        Raises:
            PoolExhaustedError: If no connection available within timeout
        """
        start_time = time.time()
        pool = self.direct_pool if mode == "direct" else self.mcp_pool
        metrics = self.direct_metrics if mode == "direct" else self.mcp_metrics

        try:
            # Try to get from pool with timeout
            connection = await asyncio.wait_for(
                pool.get(), timeout=self.config.acquire_timeout
            )

            # Track acquisition
            conn_id = uuid.uuid4().hex
            wait_time = time.time() - start_time

            metrics.total_acquisitions += 1
            metrics.total_wait_time += wait_time
            metrics.avg_wait_ms = (
                metrics.total_wait_time / metrics.total_acquisitions
            ) * 1000

            if mode == "direct":
                self.direct_in_use[conn_id] = connection
            else:
                self.mcp_in_use[conn_id] = connection

            # Update metrics
            self._update_metrics()

            logger.debug(
                "Connection acquired",
                mode=mode,
                conn_id=conn_id,
                wait_ms=wait_time * 1000,
            )

            return connection

        except TimeoutError:
            metrics.total_timeouts += 1

            # Try to create a new connection if under limit
            if (
                mode == "direct"
                and len(self.direct_in_use) < self.config.direct_pool_size
            ):
                connection = await self._create_direct_connection()
                conn_id = uuid.uuid4().hex
                self.direct_in_use[conn_id] = connection
                return connection

            elif mode == "mcp" and len(self.mcp_in_use) < self.config.mcp_pool_size:
                session = await self._create_mcp_session()
                conn_id = uuid.uuid4().hex
                self.mcp_in_use[conn_id] = session
                return session

            raise PoolExhaustedError(
                f"No available connections in {mode} pool after {self.config.acquire_timeout}s"
            )

    async def release(self, mode: str, connection: Union[ConnectionWrapper, Session]):
        """Release a connection back to the pool"""
        pool = self.direct_pool if mode == "direct" else self.mcp_pool
        metrics = self.direct_metrics if mode == "direct" else self.mcp_metrics
        in_use = self.direct_in_use if mode == "direct" else self.mcp_in_use

        # Find and remove from in-use tracking
        conn_id = None
        for cid, conn in in_use.items():
            if conn is connection:
                conn_id = cid
                break

        if conn_id:
            del in_use[conn_id]
            metrics.total_releases += 1

            # Check if connection is still healthy
            if mode == "direct" and connection.is_expired(
                self.config.max_lifetime, self.config.idle_timeout
            ):
                logger.info("Closing expired direct connection", conn_id=conn_id)
                connection.close()
                # Create a new one
                try:
                    new_conn = await self._create_direct_connection()
                    await pool.put(new_conn)
                except Exception as e:
                    logger.error(
                        "Failed to create replacement connection", error=str(e)
                    )
            else:
                # Return to pool
                try:
                    pool.put_nowait(connection)
                except asyncio.QueueFull:
                    logger.warning("Pool full, closing connection", mode=mode)
                    if mode == "direct":
                        connection.close()

            # Update metrics
            self._update_metrics()

            logger.debug("Connection released", mode=mode, conn_id=conn_id)
        else:
            logger.warning("Attempted to release unknown connection", mode=mode)

    async def _create_direct_connection(self) -> ConnectionWrapper:
        """Create a new direct Snowflake connection"""
        import snowflake.connector

        # Get connection parameters from config
        conn_params = {
            "account": get_config_value("snowflake_account"),
            "user": get_config_value("snowflake_user"),
            "password": get_config_value("snowflake_password"),
            "warehouse": get_config_value("snowflake_warehouse"),
            "database": get_config_value("snowflake_database"),
            "schema": get_config_value("snowflake_schema", "PUBLIC"),
            "role": get_config_value("snowflake_role", "SOPHIA_AI_ROLE"),
        }

        # Remove None values
        conn_params = {k: v for k, v in conn_params.items() if v is not None}

        logger.info("Creating new direct Snowflake connection")

        connection = snowflake.connector.connect(**conn_params)
        return ConnectionWrapper(connection, f"direct-{uuid.uuid4().hex[:8]}")

    async def _create_mcp_session(self) -> Session:
        """Create a new MCP session"""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")

        logger.info("Creating new MCP session")
        return Session(self.mcp_client)

    async def _ensure_minimum_connections(self):
        """Ensure minimum number of connections in pools"""
        # Direct pool
        direct_current = self.direct_pool.qsize()
        direct_needed = max(0, min(2, self.config.direct_pool_size) - direct_current)

        for _ in range(direct_needed):
            try:
                conn = await self._create_direct_connection()
                await self.direct_pool.put(conn)
            except Exception as e:
                logger.error("Failed to create direct connection", error=str(e))
                break

        # MCP pool
        if self.mcp_client:
            mcp_current = self.mcp_pool.qsize()
            mcp_needed = max(0, min(5, self.config.mcp_pool_size) - mcp_current)

            for _ in range(mcp_needed):
                try:
                    session = await self._create_mcp_session()
                    await self.mcp_pool.put(session)
                except Exception as e:
                    logger.error("Failed to create MCP session", error=str(e))
                    break

    async def _cleanup_loop(self):
        """Background task to clean up expired connections"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Clean up expired direct connections
                expired_connections = []

                # Check connections in pool
                temp_connections = []
                while not self.direct_pool.empty():
                    try:
                        conn = self.direct_pool.get_nowait()
                        if conn.is_expired(
                            self.config.max_lifetime, self.config.idle_timeout
                        ):
                            expired_connections.append(conn)
                        else:
                            temp_connections.append(conn)
                    except asyncio.QueueEmpty:
                        break

                # Put back non-expired connections
                for conn in temp_connections:
                    await self.direct_pool.put(conn)

                # Close expired connections
                for conn in expired_connections:
                    logger.info("Closing expired connection", pool_id=conn.pool_id)
                    conn.close()

                # Ensure minimum connections
                await self._ensure_minimum_connections()

            except Exception as e:
                logger.error("Error in cleanup loop", error=str(e))

    def _update_metrics(self):
        """Update Prometheus metrics"""
        # Direct pool
        self.direct_metrics.current_size = self.direct_pool.qsize() + len(
            self.direct_in_use
        )
        self.direct_metrics.in_use = len(self.direct_in_use)

        snowflake_pool_size.labels(mode="direct").set(self.direct_metrics.current_size)
        snowflake_pool_in_use.labels(mode="direct").set(self.direct_metrics.in_use)
        snowflake_pool_wait_time.labels(mode="direct").set(
            self.direct_metrics.avg_wait_ms
        )

        # MCP pool
        self.mcp_metrics.current_size = self.mcp_pool.qsize() + len(self.mcp_in_use)
        self.mcp_metrics.in_use = len(self.mcp_in_use)

        snowflake_pool_size.labels(mode="mcp").set(self.mcp_metrics.current_size)
        snowflake_pool_in_use.labels(mode="mcp").set(self.mcp_metrics.in_use)
        snowflake_pool_wait_time.labels(mode="mcp").set(self.mcp_metrics.avg_wait_ms)

    async def get_health(self) -> dict[str, Any]:
        """Get pool health status"""
        return {
            "direct": {
                "size": self.direct_metrics.current_size,
                "in_use": self.direct_metrics.in_use,
                "available": self.direct_pool.qsize(),
                "avg_wait_ms": self.direct_metrics.avg_wait_ms,
                "timeouts": self.direct_metrics.total_timeouts,
            },
            "mcp": {
                "size": self.mcp_metrics.current_size,
                "in_use": self.mcp_metrics.in_use,
                "available": self.mcp_pool.qsize(),
                "avg_wait_ms": self.mcp_metrics.avg_wait_ms,
                "timeouts": self.mcp_metrics.total_timeouts,
                "client_healthy": self.mcp_client is not None,
            },
        }

    async def close(self):
        """Close all connections and cleanup"""
        logger.info("Closing SnowflakePoolManager")

        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Close all direct connections
        while not self.direct_pool.empty():
            try:
                conn = self.direct_pool.get_nowait()
                conn.close()
            except asyncio.QueueEmpty:
                break

        for conn in self.direct_in_use.values():
            conn.close()

        # Close MCP client
        if self.mcp_client:
            await self.mcp_client.close()

        logger.info("SnowflakePoolManager closed")
