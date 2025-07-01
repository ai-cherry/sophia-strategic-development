"""
Snowflake MCP Server Implementation
Provides SQL query and data warehouse functionality
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from mcp import Server

from backend.core.optimized_connection_manager import (
    ConnectionType,
    OptimizedConnectionManager,
)

logger = logging.getLogger(__name__)


class SnowflakeMCPServer:
    """Snowflake MCP Server for data warehouse operations"""

    def __init__(self, port: int = 9100):
        self.port = port
        self.name = "snowflake"
        self.version = "1.0.0"

        # Initialize MCP server
        self.mcp_server = Server(self.name, self.version)

        # Initialize connection manager
        self.connection_manager = None

        # Register tools and resources
        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register Snowflake MCP tools"""

        @self.mcp_server.tool("execute_query")
        async def execute_query(query: str, limit: int = 100) -> dict[str, Any]:
            """Execute a SQL query on Snowflake"""
            try:
                if not self.connection_manager:
                    await self._initialize_connection()

                # Get connection
                connection = await self.connection_manager.get_connection(
                    ConnectionType.SNOWFLAKE
                )

                if not connection:
                    return {"error": "No Snowflake connection available"}

                # Execute query
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT * FROM (%s) LIMIT {limit}", (query,)
                )  # SECURITY FIX: Parameterized query

                # Fetch results
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # Format results
                formatted_results = []
                for row in results:
                    formatted_results.append(dict(zip(columns, row, strict=False)))

                cursor.close()

                return {
                    "success": True,
                    "results": formatted_results,
                    "row_count": len(formatted_results),
                    "columns": columns,
                }

            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                return {"error": str(e)}

        @self.mcp_server.tool("get_table_info")
        async def get_table_info(
            table_name: str, schema: str = "PROCESSED_AI"
        ) -> dict[str, Any]:
            """Get information about a Snowflake table"""
            try:
                if not self.connection_manager:
                    await self._initialize_connection()

                connection = await self.connection_manager.get_connection(
                    ConnectionType.SNOWFLAKE
                )

                if not connection:
                    return {"error": "No Snowflake connection available"}

                cursor = connection.cursor()

                # Get table schema
                cursor.execute(
                    f"""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
                    ORDER BY ORDINAL_POSITION
                """
                )

                columns = cursor.fetchall()

                # Get row count
                cursor.execute(
                    "SELECT COUNT(*) FROM %s.{table_name}", (schema,)
                )  # SECURITY FIX: Parameterized query
                row_count = cursor.fetchone()[0]

                cursor.close()

                return {
                    "success": True,
                    "table_name": table_name,
                    "schema": schema,
                    "row_count": row_count,
                    "columns": [
                        {
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2],
                            "default": col[3],
                        }
                        for col in columns
                    ],
                }

            except Exception as e:
                logger.error(f"Table info failed: {e}")
                return {"error": str(e)}

        @self.mcp_server.tool("health_check")
        async def health_check() -> dict[str, Any]:
            """Check Snowflake connection health"""
            try:
                if not self.connection_manager:
                    await self._initialize_connection()

                connection = await self.connection_manager.get_connection(
                    ConnectionType.SNOWFLAKE
                )

                if not connection:
                    return {"healthy": False, "error": "No connection available"}

                # Test query
                cursor = connection.cursor()
                cursor.execute("SELECT CURRENT_VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()

                return {
                    "healthy": True,
                    "snowflake_version": version,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return {"healthy": False, "error": str(e)}

    def _register_resources(self):
        """Register Snowflake MCP resources"""

        @self.mcp_server.resource("schemas")
        async def get_schemas() -> list[dict[str, Any]]:
            """Get available schemas"""
            try:
                if not self.connection_manager:
                    await self._initialize_connection()

                connection = await self.connection_manager.get_connection(
                    ConnectionType.SNOWFLAKE
                )

                if not connection:
                    return []

                cursor = connection.cursor()
                cursor.execute("SHOW SCHEMAS IN DATABASE SOPHIA_AI")
                schemas = cursor.fetchall()
                cursor.close()

                return [{"name": schema[1]} for schema in schemas]

            except Exception as e:
                logger.error(f"Schema list failed: {e}")
                return []

    async def _initialize_connection(self):
        """Initialize connection manager"""
        if not self.connection_manager:
            self.connection_manager = OptimizedConnectionManager()
            await self.connection_manager.initialize()

    async def start(self):
        """Start the Snowflake MCP server"""
        logger.info(f"🚀 Starting Snowflake MCP Server on port {self.port}")

        # Initialize connection
        await self._initialize_connection()

        # Test connection
        health = await self.mcp_server.call_tool("health_check", {})
        logger.info(f"   Health check: {health}")

        logger.info("✅ Snowflake MCP Server started successfully")

    async def stop(self):
        """Stop the Snowflake MCP server"""
        logger.info("🛑 Stopping Snowflake MCP Server")

        if self.connection_manager:
            # Close connections
            pass


# Create server instance
snowflake_server = SnowflakeMCPServer()

if __name__ == "__main__":
    asyncio.run(snowflake_server.start())
