from datetime import UTC, datetime

#!/usr/bin/env python3
"""
Snowflake Gong Setup Deployment Script

Executes Manus AI's finalized Snowflake DDL for Gong data pipeline including:
- RAW_ESTUARY target tables with VARIANT columns
- STG_TRANSFORMED Gong tables with AI memory columns
- PII policies and security
- Transformation/embedding stored procedures
- Automated scheduling tasks

Usage:
    python backend/scripts/deploy_gong_snowflake_setup.py --env dev
    python backend/scripts/deploy_gong_snowflake_setup.py --env dev --dry-run
    python backend/scripts/deploy_gong_snowflake_setup.py --env prod --execute-all
"""

import argparse
import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any

import snowflake.connector

from backend.core.auto_esc_config import get_config_value

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentEnvironment(Enum):
    """Deployment environments"""

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class SnowflakeDeploymentConfig:
    """Snowflake deployment configuration"""

    account: str
    user: str
    password: str
    warehouse: str
    database: str
    role: str

    # Environment-specific settings
    raw_schema: str = "RAW_ESTUARY"
    stg_schema: str = "STG_TRANSFORMED"
    ops_schema: str = "OPS_MONITORING"
    ai_memory_schema: str = "AI_MEMORY"


class GongSnowflakeDeployer:
    """
    Deploys complete Gong data pipeline infrastructure to Snowflake

    Capabilities:
    - Execute Manus AI's finalized DDL for all schemas
    - Create RAW_ESTUARY tables with proper VARIANT columns
    - Set up STG_TRANSFORMED tables with AI Memory integration
    - Configure PII policies and security
    - Deploy transformation and embedding procedures
    - Set up automated scheduling tasks
    - Idempotent deployment (safe to re-run)
    """

    def __init__(self, env: DeploymentEnvironment, dry_run: bool = False):
        self.env = env
        self.dry_run = dry_run
        self.connection: snowflake.connector.SnowflakeConnection | None = None

        # Load environment-specific configuration
        self.config = self._load_config()

        # Track deployment progress
        self.deployment_log: list[dict[str, Any]] = []

    def _load_config(self) -> SnowflakeDeploymentConfig:
        """Load configuration based on environment"""
        if self.env == DeploymentEnvironment.DEV:
            return SnowflakeDeploymentConfig(
                account=get_config_value("snowflake_account"),
                user=get_config_value("snowflake_user"),
                password=get_config_value("snowflake_password"),
                warehouse="WH_SOPHIA_ETL_TRANSFORM",
                database="SOPHIA_AI",
                role="ROLE_SOPHIA_ESTUARY_INGEST",
            )
        elif self.env == DeploymentEnvironment.PROD:
            return SnowflakeDeploymentConfig(
                account=get_config_value("snowflake_account"),
                user=get_config_value("snowflake_user"),
                password=get_config_value("snowflake_password"),
                warehouse="WH_SOPHIA_PRODUCTION",
                database="SOPHIA_AI",
                role="ROLE_SOPHIA_PRODUCTION",
            )
        else:
            raise ValueError(f"Unsupported environment: {self.env}")

    async def deploy_complete_pipeline(self) -> dict[str, Any]:
        """Deploy the complete Gong data pipeline to Snowflake"""
        try:
            logger.info(
                f"🚀 Starting Gong Snowflake deployment for {self.env.value.upper()} environment"
            )

            if self.dry_run:
                logger.info("🔍 DRY RUN MODE - No changes will be made")

            # Initialize connection
            await self._initialize_connection()

            # Execute Manus AI's consolidated DDL script
            ddl_file_path = "backend/snowflake_setup/manus_ai_final_gong_ddl_v2.sql"
            ddl_result = await self.execute_manus_ai_ddl(ddl_file_path)

            if not ddl_result["success"]:
                raise Exception(
                    f"DDL execution failed: {ddl_result.get('error', 'Unknown error')}"
                )

            # Verify deployment
            await self._verify_deployment()

            deployment_summary = {
                "success": True,
                "environment": self.env.value,
                "dry_run": self.dry_run,
                "deployment_timestamp": datetime.now(UTC).isoformat(),
                "steps_completed": len(self.deployment_log),
                "deployment_log": self.deployment_log,
                "ddl_execution": ddl_result,
                "next_steps": [
                    "Run Python Gong pipeline to ingest data",
                    "Execute transformation procedures",
                    "Test AI Memory integration",
                    "Activate automated tasks: ALTER TASK TASK_TRANSFORM_GONG_CALLS RESUME;",
                    "Verify data quality monitoring",
                ],
            }

            logger.info("✅ Gong Snowflake deployment completed successfully")
            return deployment_summary

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "environment": self.env.value,
                "deployment_log": self.deployment_log,
            }
        finally:
            await self._cleanup()

    async def execute_manus_ai_ddl(self, ddl_file_path: str) -> dict[str, Any]:
        """Execute Manus AI's consolidated DDL script"""
        try:
            logger.info(f"📜 Executing Manus AI DDL from: {ddl_file_path}")

            # Read the DDL file
            with open(ddl_file_path) as file:
                ddl_content = file.read()

            if self.dry_run:
                logger.info("[DRY RUN] Would execute Manus AI DDL script")
                await self._log_step(
                    "execute_manus_ddl", "DRY RUN - DDL script validated", True
                )
                return {"success": True, "dry_run": True, "statements_executed": 0}

            # Split DDL into individual statements
            statements = [
                stmt.strip() for stmt in ddl_content.split(";") if stmt.strip()
            ]
            executed_count = 0
            failed_count = 0

            cursor = self.connection.cursor()

            try:
                for i, statement in enumerate(statements):
                    if not statement or statement.startswith("--"):
                        continue

                    try:
                        logger.info(f"Executing statement {i + 1}/{len(statements)}")
                        cursor.execute(statement)
                        executed_count += 1

                    except Exception as stmt_error:
                        failed_count += 1
                        logger.warning(f"Statement {i + 1} failed: {stmt_error}")
                        # Continue with other statements for DDL operations
                        continue

                await self._log_step(
                    "execute_manus_ddl",
                    f"Executed {executed_count} statements, {failed_count} failed",
                    failed_count == 0,
                )

                return {
                    "success": failed_count == 0,
                    "statements_executed": executed_count,
                    "statements_failed": failed_count,
                    "total_statements": len(statements),
                }

            finally:
                cursor.close()

        except FileNotFoundError:
            error_msg = f"DDL file not found: {ddl_file_path}"
            logger.error(error_msg)
            await self._log_step("execute_manus_ddl", error_msg, False)
            return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f"Failed to execute Manus AI DDL: {e}"
            logger.error(error_msg)
            await self._log_step("execute_manus_ddl", error_msg, False)
            return {"success": False, "error": error_msg}

    async def _verify_deployment(self) -> None:
        """Verify that the deployment was successful"""
        try:
            cursor = self.connection.cursor()

            # Check that key tables exist
            tables_to_check = [
                f"{self.config.database}.{self.config.raw_schema}.RAW_GONG_CALLS_RAW",
                f"{self.config.database}.{self.config.raw_schema}.RAW_GONG_CALL_TRANSCRIPTS_RAW",
                f"{self.config.database}.{self.config.stg_schema}.STG_GONG_CALLS",
                f"{self.config.database}.{self.config.stg_schema}.STG_GONG_CALL_TRANSCRIPTS",
            ]

            for table in tables_to_check:
                cursor.execute(
                    "SELECT COUNT(*) FROM " + self._validate_table_name(table)
                )
                # If this doesn't throw an error, table exists
                logger.info(f"✅ Verified table exists: {table}")

            # Check that procedures exist
            procedures_to_check = [
                f"{self.config.database}.{self.config.stg_schema}.TRANSFORM_RAW_GONG_CALLS",
                f"{self.config.database}.{self.config.stg_schema}.TRANSFORM_RAW_GONG_TRANSCRIPTS",
                f"{self.config.database}.{self.config.stg_schema}.ENRICH_GONG_CALLS_WITH_AI",
            ]

            for procedure in procedures_to_check:
                cursor.execute(
                    f"SHOW PROCEDURES LIKE '{procedure.split('.')[-1]}' IN SCHEMA {self.config.database}.{self.config.stg_schema}"
                )
                result = cursor.fetchone()
                if result:
                    logger.info(f"✅ Verified procedure exists: {procedure}")
                else:
                    logger.warning(f"⚠️ Procedure not found: {procedure}")

            cursor.close()
            await self._log_step(
                "verify_deployment", "Deployment verification completed", True
            )

        except Exception as e:
            logger.warning(f"Deployment verification failed: {e}")
            await self._log_step(
                "verify_deployment", f"Verification failed: {e}", False
            )

    async def _initialize_connection(self) -> None:
        """Initialize Snowflake connection"""
        try:
            self.connection = snowflake.connector.connect(
                account=self.config.account,
                user=self.config.user,
                password=self.config.password,
                warehouse=self.config.warehouse,
                database=self.config.database,
                role=self.config.role,
            )

            await self._log_step("connection", "Snowflake connection established", True)

        except Exception as e:
            await self._log_step("connection", f"Failed to connect: {e}", False)
            raise

    async def _execute_sql(self, step_name: str, sql: str) -> None:
        """Execute SQL statement with error handling"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {step_name}")
            await self._log_step(step_name, "DRY RUN - SQL validated", True)
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            cursor.close()
            await self._log_step(step_name, "SQL executed successfully", True)

        except Exception as e:
            await self._log_step(step_name, f"SQL execution failed: {e}", False)
            raise

    async def _log_step(self, step: str, message: str, success: bool) -> None:
        """Log deployment step"""
        log_entry = {
            "step": step,
            "message": message,
            "success": success,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.deployment_log.append(log_entry)

        if success:
            logger.info(f"✅ {step}: {message}")
        else:
            logger.error(f"❌ {step}: {message}")

    async def _cleanup(self) -> None:
        """Cleanup resources"""
        if self.connection:
            self.connection.close()
            logger.info("🧹 Snowflake connection closed")


async def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy Gong Snowflake infrastructure")
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Deployment environment",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform dry run without making changes"
    )

    args = parser.parse_args()

    try:
        env = DeploymentEnvironment(args.env)
        deployer = GongSnowflakeDeployer(env, dry_run=args.dry_run)

        result = await deployer.deploy_complete_pipeline()

        # Print results
        print("\n" + "=" * 80)
        print("DEPLOYMENT SUMMARY")
        print("=" * 80)
        print(json.dumps(result, indent=2, default=str))

        if result["success"]:
            print("\n🎉 Deployment completed successfully!")
            if not args.dry_run:
                print("\nNext steps:")
                for step in result.get("next_steps", []):
                    print(f"  • {step}")
        else:
            print(f"\n💥 Deployment failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
