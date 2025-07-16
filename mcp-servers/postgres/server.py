#!/usr/bin/env python3
"""
Sophia AI PostgreSQL MCP Server
Provides database operations and queries
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import sys
from pathlib import Path
from typing import Any, Optional

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

import asyncpg
from base.unified_standardized_base import (
    ServerConfig,
    ToolDefinition,
    ToolParameter,
)
from base.unified_standardized_base import (
    UnifiedStandardizedMCPServer as StandardizedMCPServer,
)

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class PostgresMCPServer(StandardizedMCPServer):
    """PostgreSQL MCP Server for database operations"""

    def __init__(self):
        config = ServerConfig(
            name="postgres",
            version="1.0.0",
            port=9012,
            capabilities=["DATABASE", "SQL", "ANALYTICS"],
            tier="PRIMARY",
        )
        super().__init__(config)

        # PostgreSQL configuration
        self.db_config = {
            "host": get_config_value("postgres_host", "localhost"),
            "port": int(get_config_value("postgres_port", "5432")),
            "database": get_config_value("postgres_database", "sophia"),
            "user": get_config_value("postgres_user", "postgres"),
            "password": get_config_value("postgres_password"),
        }
        self.pool: Optional[asyncpg.Pool] = None

    async def setup(self):
        """Initialize PostgreSQL connection pool"""
        await super().setup()
        self.pool = await asyncpg.create_pool(**self.db_config)

    async def cleanup(self):
        """Close PostgreSQL connection pool"""
        if self.pool:
            await self.pool.close()
        await super().cleanup()

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define PostgreSQL tools"""
        return [
            ToolDefinition(
                name="execute_query",
                description="Execute a SQL query and return results",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="SQL query to execute",
                        required=True,
                    ),
                    ToolParameter(
                        name="params",
                        type="array",
                        description="Query parameters for parameterized queries",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="list_tables",
                description="List all tables in the database",
                parameters=[
                    ToolParameter(
                        name="schema",
                        type="string",
                        description="Schema name (default: public)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="describe_table",
                description="Get table schema information",
                parameters=[
                    ToolParameter(
                        name="table_name",
                        type="string",
                        description="Name of the table",
                        required=True,
                    ),
                    ToolParameter(
                        name="schema",
                        type="string",
                        description="Schema name (default: public)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="insert_data",
                description="Insert data into a table",
                parameters=[
                    ToolParameter(
                        name="table_name",
                        type="string",
                        description="Name of the table",
                        required=True,
                    ),
                    ToolParameter(
                        name="data",
                        type="object",
                        description="Data to insert (column: value pairs)",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="update_data",
                description="Update data in a table",
                parameters=[
                    ToolParameter(
                        name="table_name",
                        type="string",
                        description="Name of the table",
                        required=True,
                    ),
                    ToolParameter(
                        name="data",
                        type="object",
                        description="Data to update (column: value pairs)",
                        required=True,
                    ),
                    ToolParameter(
                        name="where",
                        type="object",
                        description="WHERE conditions (column: value pairs)",
                        required=True,
                    ),
                ],
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle PostgreSQL tool calls"""

        if not self.pool:
            raise RuntimeError("Database connection pool not initialized")

        if tool_name == "execute_query":
            return await self._execute_query(**arguments)
        elif tool_name == "list_tables":
            return await self._list_tables(**arguments)
        elif tool_name == "describe_table":
            return await self._describe_table(**arguments)
        elif tool_name == "insert_data":
            return await self._insert_data(**arguments)
        elif tool_name == "update_data":
            return await self._update_data(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _execute_query(
        self, query: str, params: Optional[list[Any]] = None
    ) -> dict[str, Any]:
        """Execute a SQL query"""

        async with self.pool.acquire() as conn:
            try:
                # Determine query type
                query_lower = query.strip().lower()

                if query_lower.startswith("select") or query_lower.startswith("with"):
                    # Fetch query
                    rows = await conn.fetch(query, *(params or []))

                    # Convert rows to list of dicts
                    results = [dict(row) for row in rows]

                    return {
                        "query": query,
                        "row_count": len(results),
                        "results": results,
                    }
                else:
                    # Execute query (INSERT, UPDATE, DELETE, etc.)
                    result = await conn.execute(query, *(params or []))

                    # Parse affected rows
                    affected = 0
                    if result:
                        parts = result.split()
                        if len(parts) >= 2 and parts[1].isdigit():
                            affected = int(parts[1])

                    return {
                        "query": query,
                        "affected_rows": affected,
                        "result": result,
                    }

            except Exception as e:
                logger.error(f"Query execution error: {e}")
                return {
                    "query": query,
                    "error": str(e),
                }

    async def _list_tables(self, schema: str = "public") -> dict[str, Any]:
        """List all tables in the database"""

        query = """
        SELECT
            schemaname,
            tablename,
            tableowner,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables
        WHERE schemaname = $1
        ORDER BY tablename
        """

        result = await self._execute_query(query, [schema])

        return {
            "schema": schema,
            "tables": result.get("results", []),
            "count": result.get("row_count", 0),
        }

    async def _describe_table(
        self, table_name: str, schema: str = "public"
    ) -> dict[str, Any]:
        """Get table schema information"""

        # Get column information
        column_query = """
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = $1 AND table_name = $2
        ORDER BY ordinal_position
        """

        columns_result = await self._execute_query(column_query, [schema, table_name])

        # Get primary key information
        pk_query = """
        SELECT a.attname as column_name
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = ($1||'.'||$2)::regclass AND i.indisprimary
        """

        pk_result = await self._execute_query(pk_query, [schema, table_name])
        pk_columns = [row["column_name"] for row in pk_result.get("results", [])]

        # Get indexes
        index_query = """
        SELECT
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = $1 AND tablename = $2
        """

        index_result = await self._execute_query(index_query, [schema, table_name])

        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM {schema}.{table_name}"
        count_result = await self._execute_query(count_query)
        row_count = count_result.get("results", [{}])[0].get("count", 0)

        return {
            "schema": schema,
            "table": table_name,
            "columns": columns_result.get("results", []),
            "primary_keys": pk_columns,
            "indexes": index_result.get("results", []),
            "row_count": row_count,
        }

    async def _insert_data(
        self, table_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert data into a table"""

        if not data:
            return {"error": "No data provided"}

        # Build INSERT query
        columns = list(data.keys())
        values = list(data.values())
        placeholders = [f"${i+1}" for i in range(len(values))]

        query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        RETURNING *
        """

        result = await self._execute_query(query, values)

        if "error" not in result:
            return {
                "table": table_name,
                "inserted": True,
                "data": result.get("results", [{}])[0] if result.get("results") else {},
            }
        else:
            return result

    async def _update_data(
        self, table_name: str, data: dict[str, Any], where: dict[str, Any]
    ) -> dict[str, Any]:
        """Update data in a table"""

        if not data or not where:
            return {"error": "Both data and where conditions are required"}

        # Build UPDATE query
        set_clauses = []
        values = []
        param_count = 0

        # Build SET clauses
        for col, val in data.items():
            param_count += 1
            set_clauses.append(f"{col} = ${param_count}")
            values.append(val)

        # Build WHERE clauses
        where_clauses = []
        for col, val in where.items():
            param_count += 1
            where_clauses.append(f"{col} = ${param_count}")
            values.append(val)

        query = f"""
        UPDATE {table_name}
        SET {', '.join(set_clauses)}
        WHERE {' AND '.join(where_clauses)}
        """

        result = await self._execute_query(query, values)

        if "error" not in result:
            return {
                "table": table_name,
                "updated": True,
                "affected_rows": result.get("affected_rows", 0),
            }
        else:
            return result

# Create and run server
if __name__ == "__main__":
    server = PostgresMCPServer()
    server.run()
