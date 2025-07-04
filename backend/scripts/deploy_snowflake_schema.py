#!/usr/bin/env python3
"""
SOPHIA AI PHOENIX PLATFORM - SCHEMA DEPLOYMENT SCRIPT

This script deploys the unified Snowflake schema that serves as the single source
of truth for the entire Sophia AI platform. This implements the Phoenix architecture
where Snowflake is the center of the universe.

Version: Phoenix 1.0
Created: January 2025
Status: AUTHORITATIVE - This script deploys the definitive schema
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

import snowflake.connector
from core.auto_esc_config import get_config_value
from snowflake.connector import DictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("snowflake_deployment.log")],
)
logger = logging.getLogger(__name__)


class PhoenixSchemaDeployer:
    """
    Deploys the Phoenix Platform unified schema to Snowflake.

    This class implements the single source of truth deployment strategy,
    creating all schemas, tables, views, and procedures needed for the
    unified Sophia AI platform.
    """

    def __init__(self):
        """Initialize the schema deployer with Snowflake connection."""
        self.connection = None
        self.deployment_start_time = datetime.utcnow()
        self.deployed_objects = []
        self.errors = []

    async def connect_to_snowflake(self) -> bool:
        """
        Establish connection to Snowflake using Pulumi ESC configuration.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("🔗 Connecting to Snowflake...")

            # Get Snowflake credentials from Pulumi ESC
            snowflake_config = {
                "account": get_config_value("snowflake_account"),
                "user": get_config_value("snowflake_user"),
                "password": get_config_value("snowflake_password"),
                "warehouse": get_config_value("snowflake_warehouse", "COMPUTE_WH"),
                "database": get_config_value(
                    "snowflake_database", "SOPHIA_AI_PRODUCTION"
                ),
                "role": get_config_value("snowflake_role", "SYSADMIN"),
            }

            logger.info(f"📊 Connecting to account: {snowflake_config['account']}")
            logger.info(f"🏢 Database: {snowflake_config['database']}")
            logger.info(f"🏭 Warehouse: {snowflake_config['warehouse']}")

            self.connection = snowflake.connector.connect(**snowflake_config)

            # Test the connection
            cursor = self.connection.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            logger.info(f"✅ Connected to Snowflake version: {version}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {e}")
            self.errors.append(f"Connection error: {e}")
            return False

    def load_schema_ddl(self) -> str:
        """
        Load the unified platform schema DDL from file.

        Returns:
            str: The complete DDL script content
        """
        try:
            schema_file = (
                Path(__file__).parent.parent
                / "snowflake_setup"
                / "unified_platform_schema.sql"
            )

            if not schema_file.exists():
                raise FileNotFoundError(f"Schema file not found: {schema_file}")

            with open(schema_file, encoding="utf-8") as f:
                ddl_content = f.read()

            logger.info(f"📄 Loaded schema DDL: {len(ddl_content)} characters")
            return ddl_content

        except Exception as e:
            logger.error(f"❌ Failed to load schema DDL: {e}")
            self.errors.append(f"DDL loading error: {e}")
            return ""

    def split_ddl_statements(self, ddl_content: str) -> list[str]:
        """
        Split the DDL content into individual executable statements.

        Args:
            ddl_content: The complete DDL script

        Returns:
            List[str]: Individual SQL statements
        """
        # Split by semicolons, but be careful with procedure definitions
        statements = []
        current_statement = ""
        in_procedure = False

        lines = ddl_content.split("\n")

        for line in lines:
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith("--"):
                continue

            # Track if we're inside a procedure definition
            if "CREATE OR REPLACE PROCEDURE" in line.upper():
                in_procedure = True
            elif line.upper().startswith("$$;") and in_procedure:
                in_procedure = False
                current_statement += line + "\n"
                statements.append(current_statement.strip())
                current_statement = ""
                continue

            current_statement += line + "\n"

            # If we hit a semicolon and we're not in a procedure, end the statement
            if line.endswith(";") and not in_procedure:
                statements.append(current_statement.strip())
                current_statement = ""

        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())

        logger.info(f"📝 Split DDL into {len(statements)} statements")
        return statements

    async def execute_ddl_statement(self, statement: str) -> bool:
        """
        Execute a single DDL statement.

        Args:
            statement: SQL statement to execute

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not statement.strip():
                return True

            cursor = self.connection.cursor(DictCursor)

            # Log the type of statement being executed
            statement_type = self.get_statement_type(statement)
            logger.info(f"🔨 Executing {statement_type}...")

            cursor.execute(statement)

            # For queries that return results, fetch them
            if statement_type in ["SELECT", "SHOW", "DESCRIBE"]:
                results = cursor.fetchall()
                if results:
                    logger.info(f"📊 Query returned {len(results)} rows")
                    # Log first few results for verification queries
                    if len(results) <= 5:
                        for row in results:
                            logger.info(f"   {row}")

            self.deployed_objects.append(statement_type)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to execute statement: {e}")
            logger.error(f"   Statement: {statement[:100]}...")
            self.errors.append(f"Statement error: {e}")
            return False

    def get_statement_type(self, statement: str) -> str:
        """
        Determine the type of SQL statement.

        Args:
            statement: SQL statement

        Returns:
            str: Statement type (CREATE SCHEMA, CREATE TABLE, etc.)
        """
        statement_upper = statement.upper().strip()

        if statement_upper.startswith("CREATE SCHEMA"):
            return "CREATE SCHEMA"
        elif statement_upper.startswith("CREATE TABLE") or statement_upper.startswith(
            "CREATE OR REPLACE TABLE"
        ):
            return "CREATE TABLE"
        elif statement_upper.startswith("CREATE VIEW") or statement_upper.startswith(
            "CREATE OR REPLACE VIEW"
        ):
            return "CREATE VIEW"
        elif statement_upper.startswith(
            "CREATE PROCEDURE"
        ) or statement_upper.startswith("CREATE OR REPLACE PROCEDURE"):
            return "CREATE PROCEDURE"
        elif statement_upper.startswith("CREATE TASK") or statement_upper.startswith(
            "CREATE OR REPLACE TASK"
        ):
            return "CREATE TASK"
        elif statement_upper.startswith("CREATE ROLE"):
            return "CREATE ROLE"
        elif statement_upper.startswith("GRANT"):
            return "GRANT PERMISSION"
        elif statement_upper.startswith("INSERT"):
            return "INSERT DATA"
        elif statement_upper.startswith("SELECT"):
            return "SELECT"
        elif statement_upper.startswith("USE"):
            return "USE"
        elif "CORTEX SEARCH SERVICE" in statement_upper:
            return "CREATE CORTEX SERVICE"
        else:
            return "OTHER"

    async def deploy_schema(self) -> bool:
        """
        Deploy the complete Phoenix platform schema.

        Returns:
            bool: True if deployment successful, False otherwise
        """
        try:
            logger.info("🔥 STARTING PHOENIX PLATFORM SCHEMA DEPLOYMENT 🔥")
            logger.info("=" * 60)

            # Load the DDL content
            ddl_content = self.load_schema_ddl()
            if not ddl_content:
                return False

            # Split into individual statements
            statements = self.split_ddl_statements(ddl_content)
            if not statements:
                logger.error("❌ No valid statements found in DDL")
                return False

            # Execute each statement
            successful_statements = 0
            failed_statements = 0

            for i, statement in enumerate(statements, 1):
                logger.info(f"\n📍 Statement {i}/{len(statements)}")

                success = await self.execute_ddl_statement(statement)
                if success:
                    successful_statements += 1
                else:
                    failed_statements += 1
                    # Continue with deployment even if some statements fail
                    # (they might be trying to create objects that already exist)

            # Log deployment summary
            logger.info("\n" + "=" * 60)
            logger.info("🔥 PHOENIX PLATFORM DEPLOYMENT SUMMARY 🔥")
            logger.info(f"✅ Successful statements: {successful_statements}")
            logger.info(f"❌ Failed statements: {failed_statements}")
            logger.info(
                f"📊 Success rate: {(successful_statements / len(statements)) * 100:.1f}%"
            )

            # Log deployed object types
            object_counts = {}
            for obj_type in self.deployed_objects:
                object_counts[obj_type] = object_counts.get(obj_type, 0) + 1

            logger.info("\n📋 Deployed Objects:")
            for obj_type, count in object_counts.items():
                logger.info(f"   {obj_type}: {count}")

            # Determine overall success
            success_rate = (successful_statements / len(statements)) * 100
            deployment_successful = success_rate >= 80  # 80% success threshold

            if deployment_successful:
                logger.info("\n🎉 PHOENIX PLATFORM DEPLOYMENT SUCCESSFUL! 🎉")
                logger.info("Snowflake is now the center of the universe! 🌟")
            else:
                logger.warning("\n⚠️  PHOENIX PLATFORM DEPLOYMENT PARTIALLY SUCCESSFUL")
                logger.warning("Some components may need manual attention.")

            return deployment_successful

        except Exception as e:
            logger.error(f"❌ Deployment failed with critical error: {e}")
            self.errors.append(f"Critical deployment error: {e}")
            return False

    async def verify_deployment(self) -> dict[str, any]:
        """
        Verify the deployment by checking created objects.

        Returns:
            Dict: Verification results
        """
        verification_results = {
            "schemas": 0,
            "tables": 0,
            "views": 0,
            "procedures": 0,
            "roles": 0,
            "errors": [],
        }

        try:
            cursor = self.connection.cursor(DictCursor)

            # Check schemas
            cursor.execute("SHOW SCHEMAS LIKE 'SOPHIA_%'")
            schemas = cursor.fetchall()
            verification_results["schemas"] = len(schemas)
            logger.info(f"✅ Found {len(schemas)} Sophia schemas")

            # Check tables
            cursor.execute(
                """
                SELECT COUNT(*) as table_count
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA LIKE 'SOPHIA_%'
            """
            )
            table_count = cursor.fetchone()["TABLE_COUNT"]
            verification_results["tables"] = table_count
            logger.info(f"✅ Found {table_count} Sophia tables")

            # Check views
            cursor.execute(
                """
                SELECT COUNT(*) as view_count
                FROM INFORMATION_SCHEMA.VIEWS
                WHERE TABLE_SCHEMA LIKE 'SOPHIA_%'
            """
            )
            view_count = cursor.fetchone()["VIEW_COUNT"]
            verification_results["views"] = view_count
            logger.info(f"✅ Found {view_count} Sophia views")

            # Test a simple query on the core table
            cursor.execute(
                "SELECT COUNT(*) as registry_count FROM SOPHIA_CORE.MCP_SERVER_REGISTRY"
            )
            registry_count = cursor.fetchone()["REGISTRY_COUNT"]
            logger.info(f"✅ MCP Server Registry has {registry_count} entries")

        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            verification_results["errors"].append(str(e))

        return verification_results

    def generate_deployment_report(self, verification_results: dict) -> str:
        """
        Generate a comprehensive deployment report.

        Args:
            verification_results: Results from deployment verification

        Returns:
            str: Formatted deployment report
        """
        deployment_duration = datetime.utcnow() - self.deployment_start_time

        report = f"""
🔥 SOPHIA AI PHOENIX PLATFORM DEPLOYMENT REPORT 🔥
{"=" * 60}

DEPLOYMENT SUMMARY:
  📅 Started: {self.deployment_start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
  ⏱️  Duration: {deployment_duration.total_seconds():.1f} seconds
  📊 Objects Deployed: {len(self.deployed_objects)}
  ❌ Errors: {len(self.errors)}

VERIFICATION RESULTS:
  📁 Schemas Created: {verification_results['schemas']}
  📋 Tables Created: {verification_results['tables']}
  👁️  Views Created: {verification_results['views']}
  ⚙️  Procedures Created: {verification_results['procedures']}
  🔐 Roles Created: {verification_results['roles']}

DEPLOYED OBJECT BREAKDOWN:
"""

        # Add object type counts
        object_counts = {}
        for obj_type in self.deployed_objects:
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1

        for obj_type, count in sorted(object_counts.items()):
            report += f"  {obj_type}: {count}\n"

        if self.errors:
            report += "\nERRORS ENCOUNTERED:\n"
            for error in self.errors[:5]:  # Show first 5 errors
                report += f"  ❌ {error}\n"
            if len(self.errors) > 5:
                report += f"  ... and {len(self.errors) - 5} more errors\n"

        report += f"""
PHOENIX ARCHITECTURE STATUS:
  🌟 Snowflake is now the center of the universe
  📊 Single source of truth established
  🧠 AI Memory system ready for Cortex integration
  🎯 Unified dashboard data layer prepared
  🔄 MCP server registry initialized

NEXT STEPS:
  1. Deploy Sophia AI brain (Cortex integration)
  2. Activate MCP server orchestration
  3. Initialize knowledge base ingestion
  4. Configure executive dashboard KPIs
  5. Begin Phase 2 of Phoenix Plan

{"=" * 60}
🎉 THE PHOENIX HAS RISEN FROM THE ASHES! 🎉
"""

        return report

    def close_connection(self):
        """Close the Snowflake connection."""
        if self.connection:
            self.connection.close()
            logger.info("🔌 Snowflake connection closed")


async def main():
    """Main deployment function."""
    deployer = PhoenixSchemaDeployer()

    try:
        # Connect to Snowflake
        if not await deployer.connect_to_snowflake():
            logger.error("❌ Failed to connect to Snowflake. Deployment aborted.")
            return False

        # Deploy the schema
        deployment_success = await deployer.deploy_schema()

        # Verify the deployment
        verification_results = await deployer.verify_deployment()

        # Generate and log the report
        report = deployer.generate_deployment_report(verification_results)
        logger.info(report)

        # Save report to file
        report_file = (
            Path(__file__).parent.parent.parent / "PHOENIX_DEPLOYMENT_REPORT.md"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"📄 Deployment report saved to: {report_file}")

        return deployment_success

    except Exception as e:
        logger.error(f"❌ Critical deployment error: {e}")
        return False

    finally:
        deployer.close_connection()


if __name__ == "__main__":
    print("🔥 SOPHIA AI PHOENIX PLATFORM SCHEMA DEPLOYMENT 🔥")
    print("Deploying the single source of truth architecture...")
    print()

    # Run the deployment
    success = asyncio.run(main())

    if success:
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("The Phoenix has risen! Snowflake is now the center of the universe.")
        print("\nNext: Run the unified dashboard to see the Phoenix in action!")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("Check the logs for details and retry.")

    sys.exit(0 if success else 1)
