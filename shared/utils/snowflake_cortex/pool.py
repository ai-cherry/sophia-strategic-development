# DEPRECATED – Use CortexGateway (core.infra.cortex_gateway). This module will be removed.
raise ImportError(
    "'shared.utils.modern_stack_cortex.pool' is deprecated. Use CortexGateway instead."
)

"""Async connection pool for ModernStack."""

import asyncio
from collections import deque
from contextlib import asynccontextmanager
from typing import Any

# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3
# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3 import ModernStackConnection

from .errors import CortexConnectionError


class AsyncConnectionPool:
    """Async connection pool for ModernStack connections."""

    def __init__(self, maxsize: int = 8, minsize: int = 2, **modern_stack_kwargs: Any):
        """Initialize connection pool.

        Args:
            maxsize: Maximum number of connections
            minsize: Minimum number of connections to maintain
            **modern_stack_kwargs: Arguments for self.modern_stack_connection
        """
        self._maxsize = maxsize
        self._minsize = minsize
        self._kwargs = modern_stack_kwargs
        self._pool: deque[ModernStackConnection] = deque()
        self._lock = asyncio.Lock()
        self._created = 0
        self._closed = False

    async def _create_connection(self) -> ModernStackConnection:
        """Create a new ModernStack connection."""
        loop = asyncio.get_running_loop()
        try:
            conn = await loop.run_in_executor(
                None, lambda: self.modern_stack_connection(**self._kwargs)
            )
            self._created += 1
            return conn
        except Exception as e:
            raise CortexConnectionError(
                f"Failed to create ModernStack connection: {e}", details={"error": str(e)}
            )

    async def acquire(self) -> ModernStackConnection:
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

    async def release(self, conn: ModernStackConnection) -> None:
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
