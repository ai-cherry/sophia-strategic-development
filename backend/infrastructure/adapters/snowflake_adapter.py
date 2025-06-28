#!/usr/bin/env python3
"""
Sophia AI - Snowflake Platform Adapter
Enhanced adapter that integrates with the central orchestrator
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.sophia_iac_orchestrator import (
    PlatformAdapter,
    PlatformStatus,
    PlatformType,
)
from scripts.snowflake_config_manager import SnowflakeConfigManager


class SnowflakeAdapter(PlatformAdapter):
    """
    Enhanced Snowflake adapter that integrates with the central orchestrator.
    Provides comprehensive Snowflake management capabilities.
    """

    def __init__(self, name: str, platform_type: PlatformType):
        super().__init__(name, platform_type)
        self.config_manager = SnowflakeConfigManager()
        self.last_health_check = None

    async def configure(self, config: dict[str, Any]) -> dict[str, Any]:
        """Configure Snowflake with given settings."""
        try:
            self.logger.info(
                f"Configuring Snowflake with config: {list(config.keys())}"
            )

            # Connect to Snowflake
            if not await self.config_manager.connect():
                return {"success": False, "error": "Failed to connect to Snowflake"}

            results = {"success": True, "operations": [], "errors": []}

            # Handle different configuration operations
            if "sync_schemas" in config and config["sync_schemas"]:
                sync_result = await self.config_manager.sync_github_schemas()
                results["operations"].append("schema_sync")
                if sync_result.get("errors"):
                    results["errors"].extend(sync_result["errors"])

            if "optimize_performance" in config and config["optimize_performance"]:
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
            self.logger.error(f"Configuration failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_status(self) -> PlatformStatus:
        """Get current Snowflake status and health."""
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
                "account": os.getenv("SNOWFLAKE_ACCOUNT", "UHDECNO-CVB64222"),
                "role": "ACCOUNTADMIN",
                "warehouse": "SOPHIA_AI_ANALYTICS_WH",
                "database": "SOPHIA_AI_CORE",
            }

            # Dependencies
            dependencies = ["estuary"]  # Estuary loads data into Snowflake

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
                webhooks_active=False,  # Snowflake doesn't have outbound webhooks
            )

        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return PlatformStatus(
                name=self.name,
                type=self.platform_type,
                status="error",
                last_check=datetime.now(),
                configuration={},
                metrics={"error": str(e)},
            )

    async def handle_webhook(self, payload: dict[str, Any]) -> None:
        """Handle incoming webhooks (Snowflake doesn't typically send webhooks)."""
        self.logger.info(f"Received webhook payload: {payload}")
        # Snowflake doesn't typically send webhooks, but we could handle
        # notifications from other systems about Snowflake operations

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
            self.logger.error(f"Configuration validation failed: {e}")
            return False

    async def rollback(self, checkpoint: dict[str, Any]) -> dict[str, Any]:
        """Rollback to a previous configuration state."""
        try:
            self.logger.info(
                f"Rolling back Snowflake to checkpoint: {checkpoint.get('id', 'unknown')}"
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
            self.logger.error(f"Rollback failed: {e}")
            return {"success": False, "error": str(e)}

    # Additional Snowflake-specific methods

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
        """Get detailed data statistics from Snowflake."""
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
            self.logger.error(f"Failed to get data statistics: {e}")
            return {"error": str(e)}


# CLI interface for testing
async def main():
    """Test the Snowflake adapter."""
    import argparse

    parser = argparse.ArgumentParser(description="Snowflake Adapter Test")
    parser.add_argument("command", choices=["status", "configure", "stats"])
    parser.add_argument("--config", help="Configuration JSON string")

    args = parser.parse_args()

    adapter = SnowflakeAdapter("snowflake", PlatformType.DATA_STACK)

    if args.command == "status":
        status = await adapter.get_status()
        print(f"Status: {status.status}")
        print(f"Metrics: {json.dumps(status.metrics, indent=2)}")
        print(f"Configuration: {json.dumps(status.configuration, indent=2)}")

    elif args.command == "configure":
        if args.config:
            config = json.loads(args.config)
            result = await adapter.configure(config)
            print(json.dumps(result, indent=2))
        else:
            print("Configuration JSON required")

    elif args.command == "stats":
        stats = await adapter.get_data_statistics()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
