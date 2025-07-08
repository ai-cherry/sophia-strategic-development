"""Async connection pool for Snowflake."""

import asyncio
from collections import deque
from contextlib import asynccontextmanager
from typing import Any

import snowflake.connector
from snowflake.connector import SnowflakeConnection

from .errors import CortexConnectionError


class AsyncConnectionPool:
    """Async connection pool for Snowflake connections."""

    def __init__(self, maxsize: int = 8, minsize: int = 2, **snowflake_kwargs: Any):
        """Initialize connection pool.

        Args:
            maxsize: Maximum number of connections
            minsize: Minimum number of connections to maintain
            **snowflake_kwargs: Arguments for snowflake.connector.connect
        """
        self._maxsize = maxsize
        self._minsize = minsize
        self._kwargs = snowflake_kwargs
        self._pool: deque[SnowflakeConnection] = deque()
        self._lock = asyncio.Lock()
        self._created = 0
        self._closed = False

    async def _create_connection(self) -> SnowflakeConnection:
        """Create a new Snowflake connection."""
        loop = asyncio.get_running_loop()
        try:
            conn = await loop.run_in_executor(
                None, lambda: snowflake.connector.connect(**self._kwargs)
            )
            self._created += 1
            return conn
        except Exception as e:
            raise CortexConnectionError(
                f"Failed to create Snowflake connection: {e}", details={"error": str(e)}
            )

    async def acquire(self) -> SnowflakeConnection:
        """Acquire a connection from the pool."""
        if self._closed:
            raise CortexConnectionError("Connection pool is closed")

        async with self._lock:
            # Try to get from pool
            while self._pool:
                conn = self._pool.popleft()
                # Check if connection is still valid
                try:
                    if conn.is_closed():
                        self._created -= 1
                        continue
                    return conn
                except Exception:
                    self._created -= 1
                    continue

            # Create new connection if under limit
            if self._created < self._maxsize:
                return await self._create_connection()

            # Wait for a connection to be released
            # This is a simplified version - in production you'd want a proper queue
            raise CortexConnectionError(
                "Connection pool exhausted",
                details={"maxsize": self._maxsize, "created": self._created},
            )

    async def release(self, conn: SnowflakeConnection) -> None:
        """Release a connection back to the pool."""
        if self._closed:
            conn.close()
            return

        async with self._lock:
            try:
                if not conn.is_closed() and len(self._pool) < self._maxsize:
                    self._pool.append(conn)
                else:
                    conn.close()
                    self._created -= 1
            except Exception:
                self._created -= 1

    @asynccontextmanager
    async def connection(self):
        """Context manager for acquiring and releasing connections."""
        conn = await self.acquire()
        try:
            yield conn
        finally:
            await self.release(conn)

    async def close(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            self._closed = True
            while self._pool:
                conn = self._pool.popleft()
                try:
                    conn.close()
                except Exception:
                    pass
            self._created = 0

    async def initialize(self) -> None:
        """Initialize the pool with minimum connections."""
        async with self._lock:
            while self._created < self._minsize:
                try:
                    conn = await self._create_connection()
                    self._pool.append(conn)
                except Exception:
                    break

    @property
    def size(self) -> int:
        """Current number of connections in pool."""
        return len(self._pool)

    @property
    def created(self) -> int:
        """Total number of connections created."""
        return self._created
