"""Snowflake pooled connection helper for Sophia AI."""

import logging
from contextlib import asynccontextmanager, suppress
from queue import Empty, Full, Queue
from typing import Any

import snowflake.connector
from snowflake.connector import SnowflakeConnection

logger = logging.getLogger(__name__)


class SnowflakeConnectionPool:
    """Thread-safe connection pool for Snowflake."""

    def __init__(self, size: int = 10, **connection_kwargs):
        self.size = size
        self.connection_kwargs = connection_kwargs
        self._pool: Queue[SnowflakeConnection] = Queue(maxsize=size)
        self._all_connections: list[SnowflakeConnection] = []
        self._initialized = False

    async def initialize(self):
        """Initialize the connection pool."""
        if self._initialized:
            return

        logger.info(
            f"Initializing Snowflake connection pool with {self.size} connections"
        )

        for i in range(self.size):
            try:
                conn = snowflake.connector.connect(**self.connection_kwargs)
                self._pool.put(conn)
                self._all_connections.append(conn)
            except Exception as e:
                logger.error(f"Failed to create connection {i+1}: {e}")
                # Clean up any created connections
                await self.close()
                raise

        self._initialized = True
        logger.info("Snowflake connection pool initialized successfully")

    async def get_connection(self, timeout: float = 30.0) -> SnowflakeConnection:
        """Get a connection from the pool."""
        if not self._initialized:
            raise RuntimeError("Connection pool not initialized")

        try:
            conn = self._pool.get(timeout=timeout)

            # Validate connection is still alive
            try:
                conn.cursor().execute("SELECT 1")
            except Exception:
                logger.warning("Dead connection detected, creating new one")
                conn = snowflake.connector.connect(**self.connection_kwargs)

            return conn

        except Empty:
            raise TimeoutError(f"No connection available after {timeout} seconds")

    async def release_connection(self, conn: SnowflakeConnection):
        """Release a connection back to the pool."""
        if not self._initialized:
            return

        try:
            self._pool.put_nowait(conn)
        except Full:
            # Pool is full, close the extra connection
            logger.warning("Connection pool full, closing extra connection")
            with suppress(Exception):
                conn.close()

    @asynccontextmanager
    async def connection(self):
        """Context manager for connection checkout/checkin."""
        conn = await self.get_connection()
        try:
            yield conn
        finally:
            await self.release_connection(conn)

    async def close(self):
        """Close all connections in the pool."""
        logger.info("Closing Snowflake connection pool")

        for conn in self._all_connections:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        self._all_connections.clear()
        self._initialized = False


# Global pool instance
_pool: SnowflakeConnectionPool | None = None


async def init_pool(connection_kwargs: dict[str, Any]) -> None:
    """Initialize the global connection pool."""
    global _pool
    if _pool is None:
        _pool = SnowflakeConnectionPool(**connection_kwargs)
        await _pool.initialize()


async def get_connection():
    """Get a connection from the global pool."""
    if _pool is None:
        raise RuntimeError("Connection pool not initialized")
    return await _pool.get_connection()


async def release_connection(conn):
    """Release a connection back to the global pool."""
    if _pool is not None:
        await _pool.release_connection(conn)
