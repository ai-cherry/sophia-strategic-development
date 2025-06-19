"""
Snowflake Integration for Sophia AI
Provides a secure and efficient way to connect to and query the Snowflake data warehouse.
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
import snowflake.connector
from snowflake.connector.errors import ProgrammingError

from infrastructure.esc.snowflake_secrets import snowflake_secret_manager

logger = logging.getLogger(__name__)

class SnowflakeIntegration:
    """
    Handles the connection and querying logic for Snowflake.
    """

    def __init__(self):
        self.connection = None
        self.credentials = None

    async def initialize(self):
        """
        Initializes the connection to Snowflake using credentials from the secret manager.
        """
        if self.connection:
            return
            
        logger.info("Initializing Snowflake integration...")
        try:
            self.credentials = await snowflake_secret_manager.get_snowflake_credentials()
            
            # The Snowflake connector's connect method is synchronous,
            # so we run it in an executor to avoid blocking the asyncio event loop.
            loop = asyncio.get_running_loop()
            self.connection = await loop.run_in_executor(
                None,  # Uses the default ThreadPoolExecutor
                snowflake.connector.connect,
                user=self.credentials.user,
                password=self.credentials.password,
                account=self.credentials.account,
                warehouse=self.credentials.warehouse,
                database=self.credentials.database,
                schema=self.credentials.schema,
                role=self.credentials.role
            )
            logger.info("Successfully connected to Snowflake.")
        except ProgrammingError as e:
            logger.error(f"Snowflake authentication error: {e}")
            raise ConnectionError("Snowflake authentication failed. Please check your credentials.")
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake connection: {e}", exc_info=True)
            raise

    async def close(self):
        """Closes the Snowflake connection."""
        if self.connection and not self.connection.is_closed():
            logger.info("Closing Snowflake connection.")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.connection.close)

    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a SQL query against the Snowflake database.
        
        Args:
            query: The SQL query string to execute.
            
        Returns:
            A list of dictionaries, where each dictionary represents a row.
        """
        if not self.connection:
            await self.initialize()
        
        logger.info(f"Executing Snowflake query: {query[:100]}...")
        
        try:
            # Run the synchronous database call in a thread pool
            loop = asyncio.get_running_loop()
            cursor = await loop.run_in_executor(None, self.connection.cursor)
            
            await loop.run_in_executor(None, cursor.execute, query)
            
            # Fetch results
            column_names = [desc[0] for desc in cursor.description]
            rows = await loop.run_in_executor(None, cursor.fetchall)
            
            # Format results as a list of dictionaries
            results = [dict(zip(column_names, row)) for row in rows]
            
            logger.info(f"Query executed successfully, fetched {len(results)} rows.")
            return results
            
        except ProgrammingError as e:
            logger.error(f"Error executing Snowflake query: {e}")
            raise ValueError(f"Invalid SQL query: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                await loop.run_in_executor(None, cursor.close)

# Global instance for easy, shared access
snowflake_integration = SnowflakeIntegration() 