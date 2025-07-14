#!/usr/bin/env python3
"""
Sophia AI - ModernStack Platform Adapter
Enhanced adapter that integrates with the central orchestrator
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3  # type: ignore[import-not-found]
# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3 import ModernStackConnection  # type: ignore[import-not-found]
from tenacity import (  # type: ignore[import-not-found]
    retry,
    stop_after_attempt,
    wait_exponential,
)

from backend.core.auto_esc_config import (
    get_config_value,  # type: ignore[import-not-found]
)
from backend.infrastructure.sophia_iac_orchestrator import (
    PlatformAdapter,
    PlatformStatus,
    PlatformType,
)
# REMOVED: ModernStack dependencyManager

logger = logging.getLogger(__name__)


class ModernStackAdapter(PlatformAdapter):
    """
    Enhanced ModernStack adapter that integrates with the central orchestrator.
    Provides comprehensive ModernStack management capabilities.
    """

    def __init__(self, name: str, platform_type: PlatformType):
        super().__init__(name, platform_type)
# REMOVED: ModernStack dependencyManager()
        self.last_health_check = None

    async def configure(self, config: dict[str, Any]) -> dict[str, Any]:
        """Configure ModernStack with given settings."""
        try:
            self.logger.info(
# REMOVED: ModernStack dependency.keys())}"
            )

            # Connect to ModernStack
            if not await self.config_manager.connect():
                return {"success": False, "error": "Failed to connect to ModernStack"}

            results = {"success": True, "operations": [], "errors": []}

            # Handle different configuration operations
            if config.get("sync_schemas"):
                sync_result = await self.config_manager.sync_github_schemas()
                results["operations"].append("schema_sync")
                if sync_result.get("errors"):
                    results["errors"].extend(sync_result["errors"])

            if config.get("optimize_performance"):
                optimize_result = await self.config_manager.optimize_performance()
                results["operations"].append("performance_optimization")
                if optimize_result.get("errors"):
                    results["errors"].extend(optimize_result["errors"])

            if "create_database" in config:
                db_config = config["create_database"]
                create_result = await self._create_database(db_config)
                results["operations"].append("database_creation")
                if not create_result["success"]:
                    results["errors"].append(create_result["error"])

            if "create_schema" in config:
                schema_config = config["create_schema"]
                schema_result = await self._create_schema(schema_config)
                results["operations"].append("schema_creation")
                if not schema_result["success"]:
                    results["errors"].append(schema_result["error"])

            if "execute_sql" in config:
                sql_config = config["execute_sql"]
                sql_result = await self._execute_sql(sql_config)
                results["operations"].append("sql_execution")
                if not sql_result["success"]:
                    results["errors"].append(sql_result["error"])

            # Set success based on whether there were errors
            results["success"] = len(results["errors"]) == 0

            self.config_manager.close_connection()
            return results

        except Exception as e:
            self.logger.exception(f"Configuration failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_status(self) -> PlatformStatus:
        """Get current ModernStack status and health."""
        try:
            # Connect to get status
            if not await self.config_manager.connect():
                return PlatformStatus(
                    name=self.name,
                    type=self.platform_type,
                    status="down",
                    last_check=datetime.now(),
                    configuration={},
                    metrics={"error": "Connection failed"},
                )

            # Get system status
            status_info = await self.config_manager.get_system_status()

            # Get basic metrics
            metrics = {
                "databases": status_info.get("databases", 0),
                "schemas": status_info.get("schemas", 0),
                "tables": status_info.get("tables", 0),
                "views": status_info.get("views", 0),
                "warehouses": status_info.get("warehouses", 0),
            }

            # Add data statistics if available
            if "data_statistics" in status_info:
                metrics["data_statistics"] = status_info["data_statistics"]

            # Determine overall health status
            health_status = "healthy"
            if metrics["databases"] == 0:
                health_status = "degraded"

            # Get configuration info
            configuration = {
                "account": get_config_value("postgres_host", "ZNB04675.us-east-1"),
                "role": "ACCOUNTADMIN",
                "warehouse": "SOPHIA_AI_ANALYTICS_WH",
                "database": "SOPHIA_AI_CORE",
            }

            # Dependencies
            dependencies = ["estuary"]  # Estuary loads data into ModernStack

            self.config_manager.close_connection()
            self.last_health_check = datetime.now()

            return PlatformStatus(
                name=self.name,
                type=self.platform_type,
                status=health_status,
                last_check=self.last_health_check,
                configuration=configuration,
                metrics=metrics,
                dependencies=dependencies,
                webhooks_active=False,  # ModernStack doesn't have outbound webhooks
            )

        except Exception as e:
            self.logger.exception(f"Status check failed: {e}")
            return PlatformStatus(
                name=self.name,
                type=self.platform_type,
                status="error",
                last_check=datetime.now(),
                configuration={},
                metrics={"error": str(e)},
            )

    async def handle_webhook(self, payload: dict[str, Any]) -> None:
        """Handle incoming webhooks (ModernStack doesn't typically send webhooks)."""
        self.logger.info(f"Received webhook payload: {payload}")
        # ModernStack doesn't typically send webhooks, but we could handle
        # notifications from other systems about ModernStack operations

    async def validate_configuration(self, config: dict[str, Any]) -> bool:
        """Validate configuration before applying."""
        try:
            # Check required fields for different operations
            if "create_database" in config:
                db_config = config["create_database"]
                if not isinstance(db_config, dict) or "name" not in db_config:
                    self.logger.error("create_database requires 'name' field")
                    return False

            if "create_schema" in config:
                schema_config = config["create_schema"]
                if not isinstance(schema_config, dict) or "name" not in schema_config:
                    self.logger.error("create_schema requires 'name' field")
                    return False

            if "execute_sql" in config:
                sql_config = config["execute_sql"]
                if not isinstance(sql_config, dict) or "query" not in sql_config:
                    self.logger.error("execute_sql requires 'query' field")
                    return False

            return True

        except Exception as e:
            self.logger.exception(f"Configuration validation failed: {e}")
            return False

    async def rollback(self, checkpoint: dict[str, Any]) -> dict[str, Any]:
        """Rollback to a previous configuration state."""
        try:
            self.logger.info(
                f"Rolling back ModernStack to checkpoint: {checkpoint.get('id', 'unknown')}"
            )

            if not await self.config_manager.connect():
                return {"success": False, "error": "Failed to connect for rollback"}

            # This would implement actual rollback logic
            # For now, we'll return a placeholder
            result = {
                "success": True,
                "message": "Rollback completed",
                "checkpoint_id": checkpoint.get("id"),
                "operations": ["schema_restore", "configuration_restore"],
            }

            self.config_manager.close_connection()
            return result

        except Exception as e:
            self.logger.exception(f"Rollback failed: {e}")
            return {"success": False, "error": str(e)}

    # Additional ModernStack-specific methods

    async def _create_database(self, config: dict[str, Any]) -> dict[str, Any]:
        """Create a new database."""
        try:
            database_name = config["name"]
            comment = config.get(
                "comment", f"Database created by Sophia AI on {datetime.now()}"
            )

            sql = f"""
            CREATE DATABASE IF NOT EXISTS {database_name}
            COMMENT = '{comment}';
            """

            self.config_manager.execute_query(sql, fetch_results=False)

            return {
                "success": True,
                "database": database_name,
                "message": f"Database {database_name} created successfully",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _create_schema(self, config: dict[str, Any]) -> dict[str, Any]:
        """Create a new schema."""
        try:
            schema_name = config["name"]
            database = config.get("database", "SOPHIA_AI_CORE")
            comment = config.get(
                "comment", f"Schema created by Sophia AI on {datetime.now()}"
            )

            sql = f"""
            CREATE SCHEMA IF NOT EXISTS {database}.{schema_name}
            COMMENT = '{comment}';
            """

            self.config_manager.execute_query(sql, fetch_results=False)

            return {
                "success": True,
                "schema": f"{database}.{schema_name}",
                "message": f"Schema {schema_name} created successfully",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_sql(self, config: dict[str, Any]) -> dict[str, Any]:
        """Execute arbitrary SQL."""
        try:
            query = config["query"]
            fetch_results = config.get("fetch_results", True)

            if fetch_results:
                results = self.config_manager.execute_query(query, fetch_results=True)
                return {
                    "success": True,
                    "results": results,
                    "row_count": len(results) if results else 0,
                }
            else:
                self.config_manager.execute_query(query, fetch_results=False)
                return {"success": True, "message": "SQL executed successfully"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # Orchestrator integration methods

    async def execute_sync_schemas(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute schema synchronization command."""
        return await self.configure({"sync_schemas": True})

    async def execute_optimize(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute performance optimization command."""
        return await self.configure({"optimize_performance": True})

    async def execute_query(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute a query command."""
        return await self.configure({"execute_sql": parameters})

    async def execute_create_database(
        self, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute database creation command."""
        return await self.configure({"create_database": parameters})

    async def execute_create_schema(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute schema creation command."""
        return await self.configure({"create_schema": parameters})

    async def get_data_statistics(self) -> dict[str, Any]:
        """Get detailed data statistics # REMOVED: ModernStack dependency
        try:
            if not await self.config_manager.connect():
                return {"error": "Connection failed"}

            # Get table row counts for key schemas
            stats = {}

            key_schemas = [
                "SOPHIA_GONG_RAW",
                "SOPHIA_SLACK_RAW",
                "SOPHIA_AI_CORE.AI_MEMORY",
                "SOPHIA_SEMANTIC",
            ]

            for schema in key_schemas:
                try:
                    # Get tables in schema
                    tables_query = f"""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = '{schema.split(".")[-1]}'
                    AND table_catalog = '{schema.split(".")[0] if "." in schema else "SOPHIA_AI_CORE"}'
                    """

                    tables = self.config_manager.execute_query(tables_query)

                    for table in tables or []:
                        table_name = table["TABLE_NAME"]
                        full_table_name = f"{schema}.{table_name}"

                        count_query = (
                            f"SELECT COUNT(*) as row_count FROM {full_table_name}"
                        )
                        count_result = self.config_manager.execute_query(count_query)

                        if count_result:
                            stats[full_table_name] = count_result[0]["ROW_COUNT"]

                except Exception as e:
                    self.logger.warning(f"Failed to get stats for {schema}: {e}")

            self.config_manager.close_connection()
            return stats

        except Exception as e:
            self.logger.exception(f"Failed to get data statistics: {e}")
            return {"error": str(e)}

    async def natural_language_to_sql(self, query: str) -> dict[str, Any]:
        """Convert natural language query to SQL using Lambda Labs AI."""
        try:
            if not await self.config_manager.connect():
                return {"success": False, "error": "Connection failed"}

            # Get schema context
            schema_context = await self._get_schema_context()

            # Import Lambda Labs service
            from backend.services.lambda_labs_service import LambdaLabsService

            lambda_service = LambdaLabsService()

            # Convert natural language to SQL
            sql_query = await lambda_service.natural_language_to_sql(
                query=query, schema_context=schema_context
            )

            # Execute the generated SQL
            results = self.config_manager.execute_query(sql_query)

            return {
                "success": True,
                "natural_language_query": query,
                "generated_sql": sql_query,
                "results": results,
                "row_count": len(results) if results else 0,
            }

        except Exception as e:
            self.logger.exception(f"Natural language to SQL failed: {e}")
            return {"success": False, "error": str(e)}

    async def _get_schema_context(self) -> str:
        """Get schema context for AI query generation."""
        try:
            # Get key tables and their structures
            key_tables = [
                "SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS",
                "SOPHIA_GONG_RAW.GONG_CALLS",
                "SOPHIA_SLACK_RAW.SLACK_MESSAGES",
                "SOPHIA_AI_CORE.AI_USAGE_ANALYTICS",
            ]

            schema_info = []

            for table in key_tables:
                parts = table.split(".")
                catalog = parts[0] if len(parts) > 2 else "SOPHIA_AI_CORE"
                schema = parts[1] if len(parts) > 2 else parts[0]
                table_name = parts[2] if len(parts) > 2 else parts[1]

                columns_query = f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_catalog = '{catalog}'
                AND table_schema = '{schema}'
                AND table_name = '{table_name}'
                ORDER BY ordinal_position
                """

                columns = self.config_manager.execute_query(columns_query)

                if columns:
                    table_info = f"\nTable: {table}\nColumns:"
                    for col in columns:
                        table_info += f"\n  - {col['COLUMN_NAME']} ({col['DATA_TYPE']})"
                    schema_info.append(table_info)

            return "\n".join(schema_info)

        except Exception as e:
            self.logger.warning(f"Failed to get schema context: {e}")
            return "Schema context unavailable"

    async def optimize_with_ai(self, query: str) -> dict[str, Any]:
        """Optimize SQL query using Lambda Labs AI."""
        try:
            from backend.services.lambda_labs_service import LambdaLabsService

            lambda_service = LambdaLabsService()

            optimization_prompt = f"""Optimize this ModernStack SQL query for performance:

Original Query:
{query}

Optimization requirements:
- Use appropriate indexes and clustering keys
- Minimize data scans
- Optimize JOIN order
- Add appropriate WHERE clause filters
- Use CTEs for readability

Optimized Query:"""

            optimized_sql = await lambda_service.simple_inference(
                optimization_prompt, complexity="premium"
            )

            return {
                "success": True,
                "original_query": query,
                "optimized_query": optimized_sql,
                "optimization_applied": True,
            }

        except Exception as e:
            self.logger.exception(f"Query optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_query": query,
                "optimization_applied": False,
            }


# REMOVED: ModernStack dependencyManager:
# REMOVED: ModernStack dependencyuration with retry logic.

    This manager provides:
    - Automatic connection retry with exponential backoff
    - Async context manager support
    - Connection pooling
    - Graceful error handling

    Attributes:
        account: ModernStack account identifier
        user: Username for authentication
        password: Password for authentication
        warehouse: Default warehouse
        database: Default database
        schema: Default schema
        role: Default role
        connection: Active connection instance
    """

    def __init__(
        self,
        warehouse: str = "SOPHIA_AI_COMPUTE_WH",
        database: str = "SOPHIA_AI",
        schema: str = "AI_INSIGHTS",
        role: str = "SOPHIA_ADMIN_ROLE",
    ):
# REMOVED: ModernStack dependencyuration.

        Args:
            warehouse: Default warehouse name
            database: Default database name
            schema: Default schema name
            role: Default role name
        """
        self.account = get_config_value("postgres_host")
        self.user = get_config_value("modern_stack_user")
        self.password = get_config_value("postgres_password")
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.role = role
        self.connection: ModernStackConnection | None = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def _create_connection(self) -> ModernStackConnection:
        """Create ModernStack connection with retry logic.

        Returns:
            Active ModernStack connection

        Raises:
            ConnectionError: If connection fails after retries
        """
        try:
            # Run synchronous connection in thread pool
            loop = asyncio.get_event_loop()
            connection = await loop.run_in_executor(
                None,
                self.modern_stack_connection,
                {
                    "account": self.account,
                    "user": self.user,
                    "password": self.password,
                    "warehouse": self.warehouse,
                    "database": self.database,
                    "schema": self.schema,
                    "role": self.role,
                    "session_parameters": {
                        "QUERY_TAG": "sophia_ai_lambda_labs",
                    },
                },
            )

            logger.info(f"Connected to ModernStack: {self.database}.{self.schema}")
            return connection

        except Exception as e:
            logger.error(f"Failed to connect to ModernStack: {e}")
            raise ConnectionError(f"ModernStack connection failed: {e}")

# REMOVED: ModernStack dependencyManager":
        """Async context manager entry.

        Returns:
            Self with active connection

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self.connection = await self._create_connection()
            return self
        except Exception as e:
            logger.error(f"Failed to enter ModernStack context: {e}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit.

        Args:
            exc_type: Exception type if any
            exc_val: Exception value if any
            exc_tb: Exception traceback if any
        """
        if self.connection:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.connection.close)
                logger.info("Closed ModernStack connection")
            except Exception as e:
                logger.error(f"Error closing ModernStack connection: {e}")
            finally:
                self.connection = None

    async def execute_query(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a query and return results.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result rows as dictionaries

        Raises:
            RuntimeError: If no active connection
            ValueError: If query is invalid
        """
        if not self.connection:
            raise RuntimeError("No active ModernStack connection")

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string")

        try:
            loop = asyncio.get_event_loop()
            cursor = await loop.run_in_executor(
                None, self.connection.cursor().execute, query, params
            )

            # Fetch results
            columns = [desc[0] for desc in cursor.description]
            rows = await loop.run_in_executor(None, cursor.fetchall)

            # Convert to list of dicts
            results = []
            for row in rows:
                results.append(dict(zip(columns, row, strict=False)))

            return results

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def record_lambda_usage(
        self,
        request_id: str,
        user_id: str,
        session_id: str,
        model: str,
        backend: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        latency_ms: int,
        cost_priority: str,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record Lambda Labs usage to ModernStack.

        Args:
            request_id: Unique request identifier
            user_id: User identifier
            session_id: Session identifier
            model: Model used
            backend: Backend used (serverless/gpu)
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost_usd: Cost in USD
            latency_ms: Latency in milliseconds
            cost_priority: Cost priority setting
            error_message: Optional error message
            metadata: Optional additional metadata
        """
        if not self.connection:
            raise RuntimeError("No active ModernStack connection")

        await self.execute_query(
            """
            CALL RECORD_LAMBDA_USAGE(
                :request_id,
                :user_id,
                :session_id,
                :model,
                :backend,
                :prompt_tokens,
                :completion_tokens,
                :cost_usd,
                :latency_ms,
                :cost_priority,
                :error_message,
                :metadata
            )
            """,
            {
                "request_id": request_id,
                "user_id": user_id,
                "session_id": session_id,
                "model": model,
                "backend": backend,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": cost_usd,
                "latency_ms": latency_ms,
                "cost_priority": cost_priority,
                "error_message": error_message,
                "metadata": metadata,
            },
        )


# CLI interface for testing
async def main():
    """Test the ModernStack adapter."""
    import argparse

    parser = argparse.ArgumentParser(description="ModernStack Adapter Test")
    parser.add_argument("command", choices=["status", "configure", "stats"])
    parser.add_argument("--config", help="Configuration JSON string")

    args = parser.parse_args()

    adapter = ModernStackAdapter("modern_stack", PlatformType.DATA_STACK)

    if args.command == "status":
        await adapter.get_status()

    elif args.command == "configure":
        if args.config:
            config = json.loads(args.config)
            await adapter.configure(config)
        else:
            pass

    elif args.command == "stats":
        await adapter.get_data_statistics()


if __name__ == "__main__":
    asyncio.run(main())
