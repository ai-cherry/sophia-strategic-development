#!/usr/bin/env python3
"""
Deploy Snowflake foundation for Sophia AI.
Creates database, schemas, tables, and initial configuration.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.infra.cortex_gateway import get_gateway

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class SnowflakeDeployer:
    """Deploy Snowflake foundation"""

    def __init__(self):
        self.gateway = get_gateway()
        self.deployment_log = []

    async def initialize(self):
        """Initialize gateway"""
        await self.gateway.initialize()
        logger.info("✅ Gateway initialized")

    async def execute_sql_file(self, file_path: Path) -> bool:
        """Execute SQL file"""
        logger.info(f"📄 Executing SQL file: {file_path}")

        try:
            with open(file_path) as f:
                sql_content = f.read()

            # Split by semicolons but handle multi-line statements
            statements = []
            current_statement = []

            for line in sql_content.split("\n"):
                # Skip comments and empty lines
                if line.strip().startswith("--") or not line.strip():
                    continue

                current_statement.append(line)

                # Check if line ends with semicolon
                if line.strip().endswith(";"):
                    statements.append("\n".join(current_statement))
                    current_statement = []

            # Execute each statement
            success_count = 0
            error_count = 0

            for i, statement in enumerate(statements):
                if not statement.strip():
                    continue

                try:
                    # Log the type of statement
                    first_word = statement.strip().split()[0].upper()
                    logger.info(
                        f"  [{i+1}/{len(statements)}] Executing {first_word}..."
                    )

                    result = await self.gateway.execute_sql(statement)
                    success_count += 1

                    self.deployment_log.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "statement_type": first_word,
                            "status": "success",
                            "statement": statement[:100] + "..."
                            if len(statement) > 100
                            else statement,
                        }
                    )

                except Exception as e:
                    error_count += 1
                    logger.error(f"  ❌ Failed: {e}")

                    self.deployment_log.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "statement_type": first_word,
                            "status": "error",
                            "error": str(e),
                            "statement": statement[:100] + "..."
                            if len(statement) > 100
                            else statement,
                        }
                    )

            logger.info(
                f"✅ Completed: {success_count} successful, {error_count} errors"
            )
            return error_count == 0

        except Exception as e:
            logger.error(f"❌ Failed to read SQL file: {e}")
            return False

    async def verify_deployment(self) -> Dict[str, Any]:
        """Verify deployment was successful"""
        logger.info("🔍 Verifying deployment...")

        checks = {
            "database_exists": False,
            "schemas_created": [],
            "warehouses_created": [],
            "tables_created": 0,
            "resource_monitor": False,
        }

        try:
            # Check database
            db_check = await self.gateway.execute_sql(
                "SHOW DATABASES LIKE 'SOPHIA_AI_UNIFIED'"
            )
            checks["database_exists"] = len(db_check) > 0

            # Check schemas
            await self.gateway.execute_sql("USE DATABASE SOPHIA_AI_UNIFIED")
            schemas = await self.gateway.execute_sql("SHOW SCHEMAS")
            checks["schemas_created"] = [
                s["name"]
                for s in schemas
                if s["name"] not in ["INFORMATION_SCHEMA", "PUBLIC"]
            ]

            # Check warehouses
            warehouses = await self.gateway.execute_sql("SHOW WAREHOUSES")
            checks["warehouses_created"] = [w["name"] for w in warehouses]

            # Check tables
            for schema in [
                "PRODUCTION",
                "ANALYTICS",
                "MONITORING",
                "AI_MEMORY",
                "KNOWLEDGE",
                "CONFIG",
            ]:
                tables = await self.gateway.execute_sql(
                    f"SHOW TABLES IN SCHEMA {schema}"
                )
                checks["tables_created"] += len(tables)

            # Check resource monitor
            monitors = await self.gateway.execute_sql(
                "SHOW RESOURCE MONITORS LIKE 'SOPHIA_AI_DAILY_LIMIT'"
            )
            checks["resource_monitor"] = len(monitors) > 0

        except Exception as e:
            logger.error(f"Verification error: {e}")

        return checks

    async def generate_deployment_report(self):
        """Generate deployment report"""
        report = {
            "deployment_date": datetime.now().isoformat(),
            "deployment_log": self.deployment_log,
            "verification": await self.verify_deployment(),
        }

        # Save report
        report_path = (
            Path("reports")
            / f'snowflake_deployment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        report_path.parent.mkdir(exist_ok=True)

        import json

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Deployment report saved to: {report_path}")

        # Print summary
        logger.info("\n📊 Deployment Summary:")
        logger.info(f"Database exists: {report['verification']['database_exists']}")
        logger.info(
            f"Schemas created: {len(report['verification']['schemas_created'])}"
        )
        logger.info(
            f"Warehouses created: {len(report['verification']['warehouses_created'])}"
        )
        logger.info(f"Tables created: {report['verification']['tables_created']}")
        logger.info(f"Resource monitor: {report['verification']['resource_monitor']}")

    async def deploy(self):
        """Run full deployment"""
        logger.info("🚀 Starting Snowflake foundation deployment...")
        logger.info("=" * 60)

        try:
            # Initialize
            await self.initialize()

            # Execute initial setup
            setup_file = Path("infrastructure/snowflake_setup/initial_setup.sql")
            if setup_file.exists():
                success = await self.execute_sql_file(setup_file)

                if not success:
                    logger.error("❌ Deployment failed with errors")
                    return False
            else:
                logger.error(f"❌ Setup file not found: {setup_file}")
                return False

            # Generate report
            await self.generate_deployment_report()

            logger.info("=" * 60)
            logger.info("✅ Snowflake foundation deployment completed!")
            return True

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Snowflake foundation")
    parser.add_argument(
        "--verify-only", action="store_true", help="Only verify existing deployment"
    )
    parser.add_argument("--sql-file", help="Deploy specific SQL file")
    args = parser.parse_args()

    deployer = SnowflakeDeployer()

    if args.verify_only:
        # Just verify
        await deployer.initialize()
        await deployer.generate_deployment_report()
    elif args.sql_file:
        # Deploy specific file
        await deployer.initialize()
        success = await deployer.execute_sql_file(Path(args.sql_file))
        sys.exit(0 if success else 1)
    else:
        # Full deployment
        success = await deployer.deploy()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
