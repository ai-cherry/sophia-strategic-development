"""Snowflake pooled connection helper for Sophia AI."""
import asyncio
from typing import Any, List
import snowflake.connector
import threading

_POOL: List[snowflake.connector.SnowflakeConnection] | None = None
_POOL_SIZE = 10
_LOCK = threading.Lock()

async def init_pool(connection_kwargs: dict[str, Any]) -> None:
    global _POOL
    if _POOL is None:
        _POOL = [snowflake.connector.connect(**connection_kwargs) for _ in range(_POOL_SIZE)]

async def get_connection():
    while _POOL is None:
        await asyncio.sleep(0.1)
    return _POOL.pop()

async def release_connection(conn):
    global _POOL
    if _POOL is None:
        return
    with _LOCK:
        _POOL.append(conn) 