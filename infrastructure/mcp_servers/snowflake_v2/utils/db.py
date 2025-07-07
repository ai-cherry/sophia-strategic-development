"""
Database connection utilities for Snowflake V2 MCP Server
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import snowflake.connector
from snowflake.connector import DictCursor
from snowflake.connector.errors import Error as SnowflakeError

from ..config import Config

logger = logging.getLogger(__name__)


class SnowflakeConnection:
    """Async wrapper for Snowflake database operations"""

    def __init__(self, config: Config):
        self.config = config
        self.connection: Optional[snowflake.connector.SnowflakeConnection] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Establish connection to Snowflake"""
        async with self._lock:
            try:
                if self.connection and not self.connection.is_closed():
                    return True

                # Run synchronous connection in thread pool
                loop = asyncio.get_event_loop()
                self.connection = await loop.run_in_executor(
                    None, self._create_connection
                )

                logger.info("Successfully connected to Snowflake")
                return True

            except SnowflakeError as e:
                logger.error(f"Snowflake connection error: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected connection error: {e}")
                return False

    def _create_connection(self) -> snowflake.connector.SnowflakeConnection:
        """Create synchronous Snowflake connection"""
        return snowflake.connector.connect(
            account=self.config.SNOWFLAKE_ACCOUNT,
            user=self.config.SNOWFLAKE_USER,
            password=self.config.SNOWFLAKE_PASSWORD,
            role=self.config.SNOWFLAKE_ROLE,
            warehouse=self.config.SNOWFLAKE_WAREHOUSE,
            database=self.config.SNOWFLAKE_DATABASE,
            schema=self.config.SNOWFLAKE_SCHEMA,
            session_parameters={
                "QUERY_TAG": "sophia_ai_mcp_v2",
                "USE_CACHED_RESULT": True,
            },
        )

    async def disconnect(self):
        """Close Snowflake connection"""
        async with self._lock:
            if self.connection:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.connection.close)
                    self.connection = None
                    logger.info("Disconnected from Snowflake")
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict[str, Any]] = None,
        fetch_results: bool = True,
    ) -> Optional[list[dict[str, Any]]]:
        """Execute a query asynchronously"""
        if not self.connection:
            await self.connect()

        if not self.connection:
            raise ConnectionError("Failed to establish Snowflake connection")

        try:
            loop = asyncio.get_event_loop()

            # Run query in thread pool
            result = await loop.run_in_executor(
                None, self._execute_sync, query, parameters, fetch_results
            )

            return result

        except SnowflakeError as e:
            logger.error(f"Query execution error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected query error: {e}")
            raise

    def _execute_sync(
        self, query: str, parameters: Optional[dict[str, Any]], fetch_results: bool
    ) -> Optional[list[dict[str, Any]]]:
        """Execute query synchronously"""
        cursor = self.connection.cursor(DictCursor)

        try:
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            if fetch_results:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                return None

        finally:
            cursor.close()

    async def execute_many(self, query: str, data: list[tuple]) -> int:
        """Execute query with multiple parameter sets"""
        if not self.connection:
            await self.connect()

        if not self.connection:
            raise ConnectionError("Failed to establish Snowflake connection")

        try:
            loop = asyncio.get_event_loop()

            # Run in thread pool
            rows_affected = await loop.run_in_executor(
                None, self._execute_many_sync, query, data
            )

            return rows_affected

        except Exception as e:
            logger.error(f"Batch execution error: {e}")
            raise

    def _execute_many_sync(self, query: str, data: list[tuple]) -> int:
        """Execute many synchronously"""
        cursor = self.connection.cursor()

        try:
            cursor.executemany(query, data)
            return cursor.rowcount
        finally:
            cursor.close()

    async def get_query_id(self) -> Optional[str]:
        """Get the last query ID"""
        if not self.connection:
            return None

        try:
            result = await self.execute_query("SELECT LAST_QUERY_ID() as query_id")
            if result:
                return result[0]["QUERY_ID"]
            return None
        except Exception as e:
            logger.error(f"Failed to get query ID: {e}")
            return None

    async def test_connection(self) -> bool:
        """Test if connection is active"""
        try:
            result = await self.execute_query("SELECT 1 as test")
            return result is not None
        except Exception:
            return False
