#!/usr/bin/env python3
"""
Analyze and Update Snowflake Configuration
Reviews current setup and updates to match Sophia AI standards
"""

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

# STANDARDIZED CONFIGURATION
STANDARD_CONFIG = {
    "database": "SOPHIA_AI_PRODUCTION",
    "warehouse": "SOPHIA_AI_COMPUTE_WH",
    "analytics_warehouse": "SOPHIA_AI_ANALYTICS_WH",
    "cortex_warehouse": "SOPHIA_AI_CORTEX_WH",
    "schemas": [
        # Core Phoenix schemas
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


class SnowflakeAnalyzer:
    def __init__(self):
        self.conn = None
        self.analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "current_state": {},
            "required_updates": [],
            "cortex_status": {},
            "recommendations": [],
        }

    def connect(self):
        """Connect to Snowflake"""
        try:
            logger.info("🔗 Connecting to Snowflake...")
            self.conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)

            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_VERSION()"
            )
            result = cursor.fetchone()

            logger.info("✅ Connected to Snowflake")
            logger.info(f"   Account: {result[0]}")
            logger.info(f"   User: {result[1]}")
            logger.info(f"   Role: {result[2]}")
            logger.info(f"   Version: {result[3]}")

            self.analysis_report["current_state"]["account"] = result[0]
            self.analysis_report["current_state"]["user"] = result[1]
            self.analysis_report["current_state"]["role"] = result[2]
            self.analysis_report["current_state"]["version"] = result[3]

            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            return False

    def analyze_databases(self):
        """Analyze current databases"""
        logger.info("\n📊 Analyzing databases...")

        cursor = self.conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()

        db_names = [db[1] for db in databases]
        self.analysis_report["current_state"]["databases"] = db_names

        logger.info(f"Found {len(databases)} databases:")
        for db in db_names:
            logger.info(f"   - {db}")

        # Check if production database exists
        if STANDARD_CONFIG["database"] not in db_names:
            self.analysis_report["required_updates"].append(
                f"Create database: {STANDARD_CONFIG['database']}"
            )

    def analyze_warehouses(self):
        """Analyze current warehouses"""
        logger.info("\n🏭 Analyzing warehouses...")

        cursor = self.conn.cursor()
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()

        wh_info = [(wh[0], wh[3], wh[5]) for wh in warehouses]  # name, state, size
        self.analysis_report["current_state"]["warehouses"] = wh_info

        logger.info(f"Found {len(warehouses)} warehouses:")
        for name, state, size in wh_info:
            logger.info(f"   - {name} (State: {state}, Size: {size})")

        # Check for required warehouses
        wh_names = [wh[0] for wh in wh_info]
        for wh in [
            STANDARD_CONFIG["warehouse"],
            STANDARD_CONFIG["analytics_warehouse"],
            STANDARD_CONFIG["cortex_warehouse"],
        ]:
            if wh not in wh_names:
                self.analysis_report["required_updates"].append(
                    f"Create warehouse: {wh}"
                )

    def analyze_schemas(self):
        """Analyze schemas in production database"""
        logger.info("\n📁 Analyzing schemas...")

        cursor = self.conn.cursor()

        # Check if production database exists
        try:
            cursor.execute(f"USE DATABASE {STANDARD_CONFIG['database']}")
            cursor.execute("SHOW SCHEMAS")
            schemas = cursor.fetchall()

            schema_names = [s[1] for s in schemas]
            self.analysis_report["current_state"]["schemas"] = schema_names

            logger.info(
                f"Found {len(schemas)} schemas in {STANDARD_CONFIG['database']}:"
            )
            for schema in schema_names:
                logger.info(f"   - {schema}")

            # Check for required schemas
            for schema in STANDARD_CONFIG["schemas"]:
                if schema not in schema_names:
                    self.analysis_report["required_updates"].append(
                        f"Create schema: {schema}"
                    )

        except Exception as e:
            logger.warning(f"Could not analyze schemas: {e}")
            self.analysis_report["current_state"]["schemas"] = []

    def test_cortex_ai(self):
        """Test Cortex AI functionality"""
        logger.info("\n🧠 Testing Cortex AI...")

        cursor = self.conn.cursor()

        try:
            # Test basic Cortex function
            cursor.execute(
                """
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'mistral-7b',
                    'Hello, what is Snowflake Cortex?'
                ) as response
            """
            )
            result = cursor.fetchone()

            if result and result[0]:
                logger.info("✅ Cortex AI is working!")
                logger.info(f"   Response preview: {result[0][:100]}...")
                self.analysis_report["cortex_status"]["functional"] = True
                self.analysis_report["cortex_status"]["models_available"] = [
                    "mistral-7b"
                ]
            else:
                logger.warning("⚠️  Cortex AI returned empty response")
                self.analysis_report["cortex_status"]["functional"] = False

        except Exception as e:
            logger.error(f"❌ Cortex AI test failed: {e}")
            self.analysis_report["cortex_status"]["functional"] = False
            self.analysis_report["cortex_status"]["error"] = str(e)

        # Test embedding function
        try:
            cursor.execute(
                """
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                    'e5-base-v2',
                    'Test embedding generation'
                ) as embedding
            """
            )
            result = cursor.fetchone()

            if result and result[0]:
                logger.info("✅ Cortex embeddings working!")
                self.analysis_report["cortex_status"]["embeddings"] = True
            else:
                logger.warning("⚠️  Cortex embeddings not working")
                self.analysis_report["cortex_status"]["embeddings"] = False

        except Exception as e:
            logger.error(f"❌ Cortex embedding test failed: {e}")
            self.analysis_report["cortex_status"]["embeddings"] = False

    def check_resource_monitors(self):
        """Check resource monitors"""
        logger.info("\n💰 Checking resource monitors...")

        cursor = self.conn.cursor()

        try:
            cursor.execute("SHOW RESOURCE MONITORS")
            monitors = cursor.fetchall()

            monitor_names = [m[0] for m in monitors]
            self.analysis_report["current_state"]["resource_monitors"] = monitor_names

            logger.info(f"Found {len(monitors)} resource monitors:")
            for name in monitor_names:
                logger.info(f"   - {name}")

            if "SOPHIA_AI_MONTHLY_MONITOR" not in monitor_names:
                self.analysis_report["required_updates"].append(
                    "Create resource monitor: SOPHIA_AI_MONTHLY_MONITOR"
                )

        except Exception as e:
            logger.warning(f"Could not check resource monitors: {e}")

    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        logger.info("\n📋 Generating recommendations...")

        # Database recommendations
        if STANDARD_CONFIG["database"] not in self.analysis_report["current_state"].get(
            "databases", []
        ):
            self.analysis_report["recommendations"].append(
                "Create production database SOPHIA_AI_PRODUCTION as the single source of truth"
            )

        # Warehouse recommendations
        wh_names = [
            wh[0] for wh in self.analysis_report["current_state"].get("warehouses", [])
        ]
        if STANDARD_CONFIG["cortex_warehouse"] not in wh_names:
            self.analysis_report["recommendations"].append(
                "Create dedicated Cortex AI warehouse for optimal AI performance"
            )

        # Cortex recommendations
        if not self.analysis_report["cortex_status"].get("functional"):
            self.analysis_report["recommendations"].append(
                "Enable Cortex AI functions for native AI capabilities"
            )

        # Schema recommendations
        missing_schemas = len(self.analysis_report["required_updates"])
        if missing_schemas > 5:
            self.analysis_report["recommendations"].append(
                f"Create {missing_schemas} missing schemas to complete Phoenix architecture"
            )

    def create_update_script(self):
        """Create SQL script for required updates"""
        if not self.analysis_report["required_updates"]:
            return

        script_content = f"""-- Snowflake Update Script
-- Generated: {datetime.now().isoformat()}
-- Account: {self.analysis_report['current_state']['account']}

USE ROLE ACCOUNTADMIN;

"""

        # Add database creation if needed
        if any(
            "Create database" in u for u in self.analysis_report["required_updates"]
        ):
            script_content += f"""
-- Create production database
CREATE DATABASE IF NOT EXISTS {STANDARD_CONFIG['database']}
COMMENT = 'Sophia AI Production Database - Phoenix Architecture';

USE DATABASE {STANDARD_CONFIG['database']};

"""

        # Add warehouse creation
        if any(
            "SOPHIA_AI_COMPUTE_WH" in u
            for u in self.analysis_report["required_updates"]
        ):
            script_content += f"""
-- Create compute warehouse
CREATE WAREHOUSE IF NOT EXISTS {STANDARD_CONFIG['warehouse']}
WITH
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 3
    SCALING_POLICY = 'STANDARD'
    COMMENT = 'Sophia AI Production Compute Warehouse';

"""

        if any(
            "SOPHIA_AI_CORTEX_WH" in u for u in self.analysis_report["required_updates"]
        ):
            script_content += f"""
-- Create Cortex AI warehouse
CREATE WAREHOUSE IF NOT EXISTS {STANDARD_CONFIG['cortex_warehouse']}
WITH
    WAREHOUSE_SIZE = 'LARGE'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 5
    SCALING_POLICY = 'ECONOMY'
    COMMENT = 'Sophia AI Cortex AI Warehouse';

"""

        # Add schema creation
        for update in self.analysis_report["required_updates"]:
            if "Create schema:" in update:
                schema_name = update.split(": ")[1]
                script_content += f"""
-- Create {schema_name} schema
CREATE SCHEMA IF NOT EXISTS {schema_name}
COMMENT = 'Sophia AI {schema_name.replace("_", " ").title()} Schema';

"""

        # Add resource monitor
        if any(
            "resource monitor" in u for u in self.analysis_report["required_updates"]
        ):
            script_content += """
-- Create resource monitor
CREATE RESOURCE MONITOR IF NOT EXISTS SOPHIA_AI_MONTHLY_MONITOR
WITH
    CREDIT_QUOTA = 1000
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS
        ON 75 PERCENT DO NOTIFY
        ON 90 PERCENT DO NOTIFY
        ON 100 PERCENT DO SUSPEND;

-- Assign to warehouses
ALTER WAREHOUSE SOPHIA_AI_COMPUTE_WH SET RESOURCE_MONITOR = 'SOPHIA_AI_MONTHLY_MONITOR';
ALTER WAREHOUSE SOPHIA_AI_CORTEX_WH SET RESOURCE_MONITOR = 'SOPHIA_AI_MONTHLY_MONITOR';

"""

        # Save script
        with open("snowflake_update_script.sql", "w") as f:
            f.write(script_content)

        logger.info("\n✅ Created snowflake_update_script.sql")

    def generate_report(self):
        """Generate analysis report"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 SNOWFLAKE ANALYSIS REPORT")
        logger.info("=" * 60)

        logger.info("\n📊 Current State:")
        logger.info(f"   Account: {self.analysis_report['current_state']['account']}")
        logger.info(
            f"   Databases: {len(self.analysis_report['current_state'].get('databases', []))}"
        )
        logger.info(
            f"   Warehouses: {len(self.analysis_report['current_state'].get('warehouses', []))}"
        )
        logger.info(
            f"   Schemas: {len(self.analysis_report['current_state'].get('schemas', []))}"
        )

        logger.info("\n🧠 Cortex AI Status:")
        logger.info(
            f"   Functional: {self.analysis_report['cortex_status'].get('functional', False)}"
        )
        logger.info(
            f"   Embeddings: {self.analysis_report['cortex_status'].get('embeddings', False)}"
        )

        if self.analysis_report["required_updates"]:
            logger.info(
                f"\n🔧 Required Updates: {len(self.analysis_report['required_updates'])}"
            )
            for update in self.analysis_report["required_updates"][:5]:
                logger.info(f"   - {update}")
            if len(self.analysis_report["required_updates"]) > 5:
                logger.info(
                    f"   ... and {len(self.analysis_report['required_updates']) - 5} more"
                )

        if self.analysis_report["recommendations"]:
            logger.info("\n💡 Recommendations:")
            for rec in self.analysis_report["recommendations"]:
                logger.info(f"   - {rec}")

    def run(self):
        """Run the complete analysis"""
        logger.info("🚀 Starting Snowflake configuration analysis")
        logger.info("=" * 60)

        if not self.connect():
            return

        # Run analysis
        self.analyze_databases()
        self.analyze_warehouses()
        self.analyze_schemas()
        self.test_cortex_ai()
        self.check_resource_monitors()

        # Generate recommendations
        self.generate_recommendations()

        # Create update script if needed
        self.create_update_script()

        # Generate report
        self.generate_report()

        # Close connection
        self.conn.close()

        logger.info("\n✅ Analysis complete!")


if __name__ == "__main__":
    analyzer = SnowflakeAnalyzer()
    analyzer.run()
