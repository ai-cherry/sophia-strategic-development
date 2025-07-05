#!/usr/bin/env python3
"""
Snowflake Cleanup and Standardization Script
Cleans up old configurations and establishes the correct setup for Sophia AI
"""

import logging
from datetime import datetime

import snowflake.connector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CORRECT PRODUCTION CONFIGURATION - SINGLE SOURCE OF TRUTH
SNOWFLAKE_CONFIG = {
    "account": "UHDECNO-CVB64222",  # Account locator (resolves to ZNB04675)
    "user": "SCOOBYJAVA15",
    "password": "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",  # PAT valid until June 2026
    "role": "ACCOUNTADMIN",
}

# STANDARDIZED CONFIGURATION
STANDARD_CONFIG = {
    "database": "SOPHIA_AI_PRODUCTION",
    "warehouse": "SOPHIA_AI_COMPUTE_WH",
    "schemas": [
        # Core schemas
        "SOPHIA_CORE",
        "SOPHIA_AI_MEMORY",
        "SOPHIA_BUSINESS_INTELLIGENCE",
        "SOPHIA_PROJECT_MANAGEMENT",
        "SOPHIA_KNOWLEDGE_BASE",
        # Integration schemas
        "GONG_INTEGRATION",
        "HUBSPOT_INTEGRATION",
        "SLACK_INTEGRATION",
        "LINEAR_INTEGRATION",
        "ASANA_INTEGRATION",
        # Data processing schemas
        "RAW_DATA",
        "STAGING",
        "ANALYTICS",
        "CORTEX_AI",
        "MONITORING",
    ],
}

# OLD/INCORRECT CONFIGURATIONS TO CLEAN UP
OLD_CONFIGS = {
    "databases": [
        "SOPHIA_AI",  # Old name
        "SOPHIA_AI_DB",  # Old name
        "SOPHIA_AI_ADVANCED",  # Old name
        "SOPHIA_AI_DEV",  # Dev environment
        "SOPHIA_AI_STAGING",  # Staging
    ],
    "warehouses": [
        "SOPHIA_AI_WH",  # Old name
        "AI_SOPHIA_AI_WH",  # Typo
        "SOPHIA_AI_WH_DEV",  # Dev
        "SOPHIA_AI_WH_STAGING",  # Staging
        "COMPUTE_WH",  # Default
        "WH_SOPHIA_ETL_TRANSFORM",  # Old ETL
    ],
    "schemas": [
        "PROCESSED_AI",  # Old schema
        "UNIVERSAL_CHAT",  # Old schema
        "SOPHIA_GONG_RAW",  # Old naming
        "SOPHIA_SLACK_RAW",  # Old naming
        "SOPHIA_SEMANTIC",  # Old naming
        "ESTUARY_FLOW",  # Old integration
        "VECTOR_SEARCH",  # Replaced by AI_MEMORY
    ],
}


class SnowflakeCleanup:
    def __init__(self):
        self.conn = None
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "databases_cleaned": [],
            "warehouses_cleaned": [],
            "schemas_cleaned": [],
            "objects_created": [],
            "errors": [],
        }

    def connect(self):
        """Connect to Snowflake"""
        try:
            logger.info("🔗 Connecting to Snowflake...")
            self.conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)

            cursor = self.conn.cursor()
            cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()")
            result = cursor.fetchone()

            logger.info("✅ Connected to Snowflake")
            logger.info(f"   Account: {result[0]}")
            logger.info(f"   User: {result[1]}")
            logger.info(f"   Role: {result[2]}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            self.cleanup_report["errors"].append(str(e))
            return False

    def analyze_current_state(self):
        """Analyze current Snowflake state"""
        logger.info("\n📊 Analyzing current Snowflake state...")

        cursor = self.conn.cursor()

        # List databases
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        logger.info(f"\n📁 Current databases ({len(databases)}):")
        for db in databases:
            db_name = db[1]
            logger.info(f"   - {db_name}")

        # List warehouses
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        logger.info(f"\n🏭 Current warehouses ({len(warehouses)}):")
        for wh in warehouses:
            wh_name = wh[0]
            wh_state = wh[3]
            logger.info(f"   - {wh_name} (State: {wh_state})")

    def cleanup_old_objects(self):
        """Clean up old/incorrect objects"""
        logger.info("\n🧹 Cleaning up old objects...")

        cursor = self.conn.cursor()

        # Clean up old databases (except current production)
        for db in OLD_CONFIGS["databases"]:
            try:
                # Check if database exists
                cursor.execute(f"SHOW DATABASES LIKE '{db}'")
                if cursor.fetchone():
                    logger.info(f"   Dropping old database: {db}")
                    cursor.execute(f"DROP DATABASE IF EXISTS {db} CASCADE")
                    self.cleanup_report["databases_cleaned"].append(db)
            except Exception as e:
                logger.warning(f"   Could not drop {db}: {e}")

        # Clean up old warehouses
        for wh in OLD_CONFIGS["warehouses"]:
            try:
                cursor.execute(f"SHOW WAREHOUSES LIKE '{wh}'")
                if cursor.fetchone():
                    logger.info(f"   Dropping old warehouse: {wh}")
                    cursor.execute(f"DROP WAREHOUSE IF EXISTS {wh}")
                    self.cleanup_report["warehouses_cleaned"].append(wh)
            except Exception as e:
                logger.warning(f"   Could not drop {wh}: {e}")

    def create_standard_objects(self):
        """Create standardized objects"""
        logger.info("\n🏗️  Creating standardized objects...")

        cursor = self.conn.cursor()

        # Create production database
        logger.info(f"📊 Creating database: {STANDARD_CONFIG['database']}")
        cursor.execute(
            f"""
            CREATE DATABASE IF NOT EXISTS {STANDARD_CONFIG['database']}
            COMMENT = 'Sophia AI Production Database - Single Source of Truth'
        """
        )
        self.cleanup_report["objects_created"].append(
            f"Database: {STANDARD_CONFIG['database']}"
        )

        # Create optimized warehouse
        logger.info(f"🏭 Creating warehouse: {STANDARD_CONFIG['warehouse']}")
        cursor.execute(
            f"""
            CREATE WAREHOUSE IF NOT EXISTS {STANDARD_CONFIG['warehouse']}
            WITH
                WAREHOUSE_SIZE = 'MEDIUM'
                WAREHOUSE_TYPE = 'STANDARD'
                AUTO_SUSPEND = 60
                AUTO_RESUME = TRUE
                MIN_CLUSTER_COUNT = 1
                MAX_CLUSTER_COUNT = 3
                SCALING_POLICY = 'STANDARD'
                COMMENT = 'Sophia AI Production Compute Warehouse'
        """
        )
        self.cleanup_report["objects_created"].append(
            f"Warehouse: {STANDARD_CONFIG['warehouse']}"
        )

        # Create analytics warehouse for heavy queries
        analytics_wh = "SOPHIA_AI_ANALYTICS_WH"
        logger.info(f"🏭 Creating analytics warehouse: {analytics_wh}")
        cursor.execute(
            f"""
            CREATE WAREHOUSE IF NOT EXISTS {analytics_wh}
            WITH
                WAREHOUSE_SIZE = 'LARGE'
                WAREHOUSE_TYPE = 'STANDARD'
                AUTO_SUSPEND = 300
                AUTO_RESUME = TRUE
                MIN_CLUSTER_COUNT = 1
                MAX_CLUSTER_COUNT = 5
                SCALING_POLICY = 'ECONOMY'
                COMMENT = 'Sophia AI Analytics Warehouse for Heavy Queries'
        """
        )
        self.cleanup_report["objects_created"].append(f"Warehouse: {analytics_wh}")

        # Use production database
        cursor.execute(f"USE DATABASE {STANDARD_CONFIG['database']}")

        # Create all schemas
        for schema in STANDARD_CONFIG["schemas"]:
            logger.info(f"📁 Creating schema: {schema}")
            cursor.execute(
                f"""
                CREATE SCHEMA IF NOT EXISTS {schema}
                COMMENT = 'Sophia AI {schema.replace("_", " ").title()} Schema'
            """
            )
            self.cleanup_report["objects_created"].append(f"Schema: {schema}")

    def setup_resource_monitors(self):
        """Setup resource monitors for cost control"""
        logger.info("\n💰 Setting up resource monitors...")

        cursor = self.conn.cursor()

        # Create monthly monitor
        cursor.execute(
            """
            CREATE RESOURCE MONITOR IF NOT EXISTS SOPHIA_AI_MONTHLY_MONITOR
            WITH
                CREDIT_QUOTA = 1000
                FREQUENCY = MONTHLY
                START_TIMESTAMP = IMMEDIATELY
                TRIGGERS
                    ON 75 PERCENT DO NOTIFY
                    ON 90 PERCENT DO NOTIFY
                    ON 100 PERCENT DO SUSPEND
        """
        )

        # Assign to warehouses
        cursor.execute(
            f"""
            ALTER WAREHOUSE {STANDARD_CONFIG['warehouse']}
            SET RESOURCE_MONITOR = SOPHIA_AI_MONTHLY_MONITOR
        """
        )

        logger.info("✅ Resource monitors configured")

    def create_standard_roles(self):
        """Create standard roles for access control"""
        logger.info("\n👥 Creating standard roles...")

        cursor = self.conn.cursor()

        roles = [
            ("SOPHIA_AI_ADMIN", "Full administrative access to Sophia AI"),
            ("SOPHIA_AI_DEVELOPER", "Developer access for Sophia AI"),
            ("SOPHIA_AI_ANALYST", "Read-only analyst access"),
            ("SOPHIA_AI_SERVICE", "Service account for applications"),
        ]

        for role_name, comment in roles:
            cursor.execute(
                f"""
                CREATE ROLE IF NOT EXISTS {role_name}
                COMMENT = '{comment}'
            """
            )
            logger.info(f"✅ Created role: {role_name}")

    def generate_report(self):
        """Generate cleanup report"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 SNOWFLAKE CLEANUP REPORT")
        logger.info("=" * 60)

        logger.info(
            f"\n✅ Databases cleaned: {len(self.cleanup_report['databases_cleaned'])}"
        )
        for db in self.cleanup_report["databases_cleaned"]:
            logger.info(f"   - {db}")

        logger.info(
            f"\n✅ Warehouses cleaned: {len(self.cleanup_report['warehouses_cleaned'])}"
        )
        for wh in self.cleanup_report["warehouses_cleaned"]:
            logger.info(f"   - {wh}")

        logger.info(
            f"\n✅ Objects created: {len(self.cleanup_report['objects_created'])}"
        )
        for obj in self.cleanup_report["objects_created"]:
            logger.info(f"   - {obj}")

        if self.cleanup_report["errors"]:
            logger.info(f"\n⚠️  Errors: {len(self.cleanup_report['errors'])}")
            for err in self.cleanup_report["errors"]:
                logger.info(f"   - {err}")

        logger.info("\n📝 STANDARDIZED CONFIGURATION:")
        logger.info("   Account: UHDECNO-CVB64222 (resolves to ZNB04675)")
        logger.info(f"   Database: {STANDARD_CONFIG['database']}")
        logger.info(f"   Warehouse: {STANDARD_CONFIG['warehouse']}")
        logger.info(f"   Schemas: {len(STANDARD_CONFIG['schemas'])}")

    def update_codebase_config(self):
        """Generate config file for codebase"""
        config_content = f'''"""
Snowflake Configuration - SINGLE SOURCE OF TRUTH
Generated by snowflake_cleanup_and_standardize.py
DO NOT MODIFY - This is the authoritative configuration
Generated: {datetime.now().isoformat()}
"""

SNOWFLAKE_CONFIG = {{
    "account": "UHDECNO-CVB64222",
    "user": "SCOOBYJAVA15",
    "database": "{STANDARD_CONFIG['database']}",
    "warehouse": "{STANDARD_CONFIG['warehouse']}",
    "role": "ACCOUNTADMIN",
    "schema": "SOPHIA_CORE",  # Default schema
}}

# Available schemas
SNOWFLAKE_SCHEMAS = {STANDARD_CONFIG['schemas']}

# Environment-specific overrides (if needed)
SNOWFLAKE_ENV_CONFIG = {{
    "production": {{
        "database": "{STANDARD_CONFIG['database']}",
        "warehouse": "{STANDARD_CONFIG['warehouse']}",
        "role": "SOPHIA_AI_ADMIN",
    }},
    "development": {{
        "database": "{STANDARD_CONFIG['database']}_DEV",
        "warehouse": "{STANDARD_CONFIG['warehouse']}_DEV",
        "role": "SOPHIA_AI_DEVELOPER",
    }}
}}
'''

        with open("backend/core/snowflake_production_config.py", "w") as f:
            f.write(config_content)

        logger.info("\n✅ Created backend/core/snowflake_production_config.py")

    def run(self):
        """Run the complete cleanup process"""
        logger.info("🚀 Starting Snowflake cleanup and standardization")
        logger.info("=" * 60)

        if not self.connect():
            return

        # Analyze current state
        self.analyze_current_state()

        # Ask for confirmation
        confirm = input(
            "\n⚠️  This will clean up old objects and standardize configuration. Continue? (yes/no): "
        )
        if confirm.lower() != "yes":
            logger.info("Cancelled.")
            return

        # Run cleanup
        self.cleanup_old_objects()

        # Create standard objects
        self.create_standard_objects()

        # Setup monitoring
        self.setup_resource_monitors()

        # Create roles
        self.create_standard_roles()

        # Update codebase config
        self.update_codebase_config()

        # Generate report
        self.generate_report()

        # Close connection
        self.conn.close()

        logger.info("\n✅ Snowflake cleanup and standardization complete!")


if __name__ == "__main__":
    cleanup = SnowflakeCleanup()
    cleanup.run()
