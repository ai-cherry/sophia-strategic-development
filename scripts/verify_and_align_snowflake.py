#!/usr/bin/env python3
"""
Verify and Align Snowflake Configuration for Sophia AI
Checks existing setup and creates missing components
"""

import json
import logging
from datetime import datetime

import snowflake.connector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CORRECT PRODUCTION CONFIGURATION
SNOWFLAKE_CONFIG = {
    "account": "UHDECNO-CVB64222",
    "user": "SCOOBYJAVA15",
    "password": "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",
    "role": "ACCOUNTADMIN",
}


class SnowflakeVerifier:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.verification_results = {
            "database": {},
            "schemas": {},
            "warehouses": {},
            "tables": {},
            "functions": {},
            "recommendations": [],
        }

    def connect(self):
        """Connect to Snowflake"""
        try:
            self.conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
            self.cursor = self.conn.cursor()
            logger.info("✅ Connected to Snowflake")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    def verify_database(self):
        """Verify database exists"""
        logger.info("🔍 Verifying Database...")

        try:
            self.cursor.execute("SHOW DATABASES LIKE 'SOPHIA_AI_PRODUCTION'")
            result = self.cursor.fetchall()

            if result:
                self.verification_results["database"]["exists"] = True
                self.cursor.execute("USE DATABASE SOPHIA_AI_PRODUCTION")
                logger.info("✅ Database SOPHIA_AI_PRODUCTION exists")
            else:
                self.verification_results["database"]["exists"] = False
                logger.warning("⚠️ Database SOPHIA_AI_PRODUCTION does not exist")
                self.verification_results["recommendations"].append(
                    "CREATE DATABASE SOPHIA_AI_PRODUCTION"
                )

        except Exception as e:
            logger.error(f"❌ Database verification failed: {e}")

    def verify_schemas(self):
        """Verify required schemas"""
        logger.info("🔍 Verifying Schemas...")

        required_schemas = [
            "SOPHIA_CORE",
            "SOPHIA_AI_MEMORY",
            "SOPHIA_BUSINESS_INTELLIGENCE",
            "CORTEX_AI",
            "AI_MEMORY",
            "ANALYTICS",
            "CHAT",
            "MONITORING",
            "GONG_INTEGRATION",
            "HUBSPOT_INTEGRATION",
            "SLACK_INTEGRATION",
        ]

        try:
            self.cursor.execute("SHOW SCHEMAS IN DATABASE SOPHIA_AI_PRODUCTION")
            existing_schemas = [row[1] for row in self.cursor.fetchall()]

            for schema in required_schemas:
                if schema in existing_schemas:
                    self.verification_results["schemas"][schema] = "exists"
                    logger.info(f"✅ Schema {schema} exists")
                else:
                    self.verification_results["schemas"][schema] = "missing"
                    logger.warning(f"⚠️ Schema {schema} is missing")

        except Exception as e:
            logger.error(f"❌ Schema verification failed: {e}")

    def verify_warehouses(self):
        """Verify warehouses"""
        logger.info("🔍 Verifying Warehouses...")

        required_warehouses = [
            ("SOPHIA_AI_COMPUTE_WH", "MEDIUM"),
            ("SOPHIA_AI_ANALYTICS_WH", "LARGE"),
            ("SOPHIA_AI_CORTEX_WH", "MEDIUM"),
        ]

        try:
            self.cursor.execute("SHOW WAREHOUSES")
            existing_warehouses = {row[0]: row[1] for row in self.cursor.fetchall()}

            for wh_name, wh_size in required_warehouses:
                if wh_name in existing_warehouses:
                    self.verification_results["warehouses"][wh_name] = {
                        "exists": True,
                        "size": existing_warehouses[wh_name],
                    }
                    logger.info(
                        f"✅ Warehouse {wh_name} exists (size: {existing_warehouses[wh_name]})"
                    )
                else:
                    self.verification_results["warehouses"][wh_name] = {
                        "exists": False,
                        "recommended_size": wh_size,
                    }
                    logger.warning(f"⚠️ Warehouse {wh_name} is missing")

        except Exception as e:
            logger.error(f"❌ Warehouse verification failed: {e}")

    def verify_cortex_ai(self):
        """Verify Cortex AI capabilities"""
        logger.info("🔍 Verifying Cortex AI...")

        try:
            # Test embedding function
            self.cursor.execute(
                """
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'test') as embedding
            """
            )
            result = self.cursor.fetchone()

            if result and result[0]:
                self.verification_results["functions"]["cortex_embedding"] = "working"
                logger.info("✅ Cortex AI embedding function is working")
            else:
                self.verification_results["functions"][
                    "cortex_embedding"
                ] = "not_working"
                logger.warning("⚠️ Cortex AI embedding function is not working")

            # Test completion function
            self.cursor.execute(
                """
                SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', 'Hello') as response
            """
            )
            result = self.cursor.fetchone()

            if result and result[0]:
                self.verification_results["functions"]["cortex_complete"] = "working"
                logger.info("✅ Cortex AI completion function is working")
            else:
                self.verification_results["functions"][
                    "cortex_complete"
                ] = "not_working"
                logger.warning("⚠️ Cortex AI completion function is not working")

        except Exception as e:
            logger.error(f"❌ Cortex AI verification failed: {e}")
            self.verification_results["functions"]["cortex_ai"] = str(e)

    def check_memory_architecture(self):
        """Check if memory architecture tables exist"""
        logger.info("🔍 Checking Memory Architecture...")

        memory_tables = [
            "AI_MEMORY.MEMORY_RECORDS",
            "AI_MEMORY.MEMORY_EMBEDDINGS",
            "AI_MEMORY.CONVERSATION_HISTORY",
            "AI_MEMORY.MEMORY_CATEGORIES",
        ]

        try:
            for table in memory_tables:
                try:
                    self.cursor.execute(f"DESCRIBE TABLE SOPHIA_AI_PRODUCTION.{table}")
                    self.verification_results["tables"][table] = "exists"
                    logger.info(f"✅ Table {table} exists")
                except:
                    self.verification_results["tables"][table] = "missing"
                    logger.warning(f"⚠️ Table {table} is missing")

        except Exception as e:
            logger.error(f"❌ Memory architecture check failed: {e}")

    def generate_recommendations(self):
        """Generate recommendations based on verification"""
        logger.info("📋 Generating Recommendations...")

        # Database recommendations
        if not self.verification_results["database"].get("exists"):
            self.verification_results["recommendations"].append(
                "CREATE DATABASE SOPHIA_AI_PRODUCTION"
            )

        # Schema recommendations
        for schema, status in self.verification_results["schemas"].items():
            if status == "missing":
                self.verification_results["recommendations"].append(
                    f"CREATE SCHEMA SOPHIA_AI_PRODUCTION.{schema}"
                )

        # Warehouse recommendations
        for wh_name, info in self.verification_results["warehouses"].items():
            if not info.get("exists"):
                size = info.get("recommended_size", "MEDIUM")
                self.verification_results["recommendations"].append(
                    f"CREATE WAREHOUSE {wh_name} WITH WAREHOUSE_SIZE = '{size}'"
                )

        # Table recommendations
        for table, status in self.verification_results["tables"].items():
            if status == "missing":
                self.verification_results["recommendations"].append(
                    f"Create table {table} (see ai_memory_schema.sql)"
                )

    def create_alignment_script(self):
        """Create SQL script to align Snowflake with requirements"""
        logger.info("📝 Creating Alignment Script...")

        sql_commands = []

        # Add database creation if needed
        if not self.verification_results["database"].get("exists"):
            sql_commands.append("CREATE DATABASE IF NOT EXISTS SOPHIA_AI_PRODUCTION;")
            sql_commands.append("USE DATABASE SOPHIA_AI_PRODUCTION;")
        else:
            sql_commands.append("USE DATABASE SOPHIA_AI_PRODUCTION;")

        # Add schema creation
        for schema, status in self.verification_results["schemas"].items():
            if status == "missing":
                sql_commands.append(f"CREATE SCHEMA IF NOT EXISTS {schema};")

        # Add warehouse creation
        for wh_name, info in self.verification_results["warehouses"].items():
            if not info.get("exists"):
                size = info.get("recommended_size", "MEDIUM")
                sql_commands.append(
                    f"""
CREATE WAREHOUSE IF NOT EXISTS {wh_name}
WITH WAREHOUSE_SIZE = '{size}'
AUTO_SUSPEND = 60
AUTO_RESUME = TRUE
MIN_CLUSTER_COUNT = 1
MAX_CLUSTER_COUNT = 3;
"""
                )

        # Save script
        with open("snowflake_alignment_script.sql", "w") as f:
            f.write("-- Snowflake Alignment Script for Sophia AI\n")
            f.write("-- Generated: " + datetime.now().isoformat() + "\n\n")
            f.write("\n".join(sql_commands))

        logger.info("✅ Alignment script created: snowflake_alignment_script.sql")

    def generate_report(self):
        """Generate verification report"""
        logger.info("📄 Generating Verification Report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "account": SNOWFLAKE_CONFIG["account"],
            "verification_results": self.verification_results,
            "summary": {
                "database_exists": self.verification_results["database"].get(
                    "exists", False
                ),
                "schemas_missing": len(
                    [
                        s
                        for s, status in self.verification_results["schemas"].items()
                        if status == "missing"
                    ]
                ),
                "warehouses_missing": len(
                    [
                        w
                        for w, info in self.verification_results["warehouses"].items()
                        if not info.get("exists")
                    ]
                ),
                "tables_missing": len(
                    [
                        t
                        for t, status in self.verification_results["tables"].items()
                        if status == "missing"
                    ]
                ),
                "cortex_ai_working": self.verification_results["functions"].get(
                    "cortex_embedding"
                )
                == "working",
            },
        }

        # Save report
        with open("snowflake_verification_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info(
            "✅ Verification report generated: snowflake_verification_report.json"
        )

        # Print summary

    def run_verification(self):
        """Run complete verification"""
        if not self.connect():
            return

        logger.info("🚀 Starting Snowflake Verification for Sophia AI...")

        # Run all verifications
        self.verify_database()
        self.verify_schemas()
        self.verify_warehouses()
        self.verify_cortex_ai()
        self.check_memory_architecture()

        # Generate outputs
        self.generate_recommendations()
        self.create_alignment_script()
        self.generate_report()

        # Close connection
        self.cursor.close()
        self.conn.close()

        logger.info("✅ Verification complete!")


if __name__ == "__main__":
    verifier = SnowflakeVerifier()
    verifier.run_verification()
