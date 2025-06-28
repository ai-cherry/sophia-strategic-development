#!/usr/bin/env python3
from backend.core.auto_esc_config import get_config_value

"""
Standalone Snowflake Stability Enhancement Deployment Script
Implements comprehensive database-level stability features for Sophia AI production deployment.
No complex import dependencies - uses direct Snowflake connector.
"""

import snowflake.connector
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("snowflake_stability_deployment.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Snowflake Configuration
SNOWFLAKE_CONFIG = {
    "account": "ZNB04675",
    "user": "SCOOBYJAVA15",
    "password": get_config_value("snowflake_password"),
    "role": "ACCOUNTADMIN",
    "database": "SOPHIA_AI_PROD",
    "warehouse": "SOPHIA_AI_WH",
}


class SnowflakeStabilityDeployer:
    def __init__(self):
        self.conn = None
        self.deployment_status = {
            "resource_monitors": {"status": "pending", "details": []},
            "warehouses": {"status": "pending", "details": []},
            "security_roles": {"status": "pending", "details": []},
            "performance_optimization": {"status": "pending", "details": []},
            "backup_recovery": {"status": "pending", "details": []},
            "monitoring_schemas": {"status": "pending", "details": []},
        }

    def connect(self) -> bool:
        """Initialize Snowflake connection with error handling."""
        try:
            self.conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
            logger.info("✅ Snowflake connection established successfully")

            # Test connection
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT CURRENT_TIMESTAMP(), CURRENT_USER(), CURRENT_WAREHOUSE()"
            )
            result = cursor.fetchone()
            logger.info(
                f"Connected as {result[1]} using warehouse {result[2]} at {result[0]}"
            )
            cursor.close()
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Snowflake connection: {e}")
            return False

    def execute_query(self, query: str, description: str = "") -> bool:
        """Execute a single query with error handling."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            cursor.close()
            if description:
                logger.info(f"✅ {description}")
            return True
        except Exception as e:
            logger.error(
                f"❌ Failed to execute query{' - ' + description if description else ''}: {e}"
            )
            logger.error(f"Query: {query}")
            return False

    def deploy_resource_monitors(self) -> bool:
        """Deploy resource monitors for cost control and performance management."""
        logger.info("🔧 Deploying resource monitors...")

        resource_monitor_queries = [
            (
                """
            CREATE OR REPLACE RESOURCE MONITOR SOPHIA_AI_PROD_MONITOR
            WITH CREDIT_QUOTA = 1000 
            FREQUENCY = MONTHLY
            TRIGGERS 
                ON 75 PERCENT DO NOTIFY
                ON 90 PERCENT DO SUSPEND_IMMEDIATE
                ON 95 PERCENT DO SUSPEND_IMMEDIATE
            """,
                "Production resource monitor (1000 credits/month)",
            ),
            (
                """
            CREATE OR REPLACE RESOURCE MONITOR SOPHIA_AI_DEV_MONITOR
            WITH CREDIT_QUOTA = 200
            FREQUENCY = MONTHLY
            TRIGGERS 
                ON 80 PERCENT DO NOTIFY
                ON 95 PERCENT DO SUSPEND_IMMEDIATE
            """,
                "Development resource monitor (200 credits/month)",
            ),
            (
                """
            CREATE OR REPLACE RESOURCE MONITOR SOPHIA_AI_ANALYTICS_MONITOR
            WITH CREDIT_QUOTA = 500
            FREQUENCY = MONTHLY
            TRIGGERS 
                ON 85 PERCENT DO NOTIFY
                ON 95 PERCENT DO SUSPEND_IMMEDIATE
            """,
                "Analytics resource monitor (500 credits/month)",
            ),
        ]

        success_count = 0
        for query, description in resource_monitor_queries:
            if self.execute_query(query, description):
                success_count += 1
                self.deployment_status["resource_monitors"]["details"].append(
                    description
                )

        if success_count == len(resource_monitor_queries):
            self.deployment_status["resource_monitors"]["status"] = "completed"
            return True
        else:
            self.deployment_status["resource_monitors"]["status"] = "failed"
            return False

    def deploy_specialized_warehouses(self) -> bool:
        """Deploy specialized warehouses for different workload types."""
        logger.info("🏭 Deploying specialized warehouses...")

        warehouse_queries = [
            (
                """
            CREATE OR REPLACE WAREHOUSE SOPHIA_AI_CHAT_WH 
            WITH WAREHOUSE_SIZE = 'SMALL'
                AUTO_SUSPEND = 30
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = FALSE
                SCALING_POLICY = 'ECONOMY'
                MAX_CLUSTER_COUNT = 3
                MIN_CLUSTER_COUNT = 1
                COMMENT = 'Optimized for chat queries - fast response, low cost'
            """,
                "Chat warehouse (SMALL, 30s suspend)",
            ),
            (
                """
            CREATE OR REPLACE WAREHOUSE SOPHIA_AI_ANALYTICS_WH 
            WITH WAREHOUSE_SIZE = 'MEDIUM'
                AUTO_SUSPEND = 300
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE
                SCALING_POLICY = 'STANDARD'
                MAX_CLUSTER_COUNT = 5
                MIN_CLUSTER_COUNT = 1
                COMMENT = 'Optimized for analytics and reporting workloads'
            """,
                "Analytics warehouse (MEDIUM, 300s suspend)",
            ),
            (
                """
            CREATE OR REPLACE WAREHOUSE SOPHIA_AI_ETL_WH 
            WITH WAREHOUSE_SIZE = 'LARGE'
                AUTO_SUSPEND = 60
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE
                SCALING_POLICY = 'ECONOMY'
                MAX_CLUSTER_COUNT = 2
                MIN_CLUSTER_COUNT = 1
                COMMENT = 'Optimized for ETL and batch processing'
            """,
                "ETL warehouse (LARGE, 60s suspend)",
            ),
            (
                """
            CREATE OR REPLACE WAREHOUSE SOPHIA_AI_ML_WH 
            WITH WAREHOUSE_SIZE = 'X-LARGE'
                AUTO_SUSPEND = 180
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE
                SCALING_POLICY = 'ECONOMY'
                MAX_CLUSTER_COUNT = 3
                MIN_CLUSTER_COUNT = 1
                COMMENT = 'Optimized for AI/ML processing and embeddings'
            """,
                "ML warehouse (X-LARGE, 180s suspend)",
            ),
        ]

        # Assign resource monitors to warehouses
        monitor_assignments = [
            (
                "ALTER WAREHOUSE SOPHIA_AI_CHAT_WH SET RESOURCE_MONITOR = SOPHIA_AI_PROD_MONITOR",
                "Chat warehouse monitor assignment",
            ),
            (
                "ALTER WAREHOUSE SOPHIA_AI_ANALYTICS_WH SET RESOURCE_MONITOR = SOPHIA_AI_ANALYTICS_MONITOR",
                "Analytics warehouse monitor assignment",
            ),
            (
                "ALTER WAREHOUSE SOPHIA_AI_ETL_WH SET RESOURCE_MONITOR = SOPHIA_AI_PROD_MONITOR",
                "ETL warehouse monitor assignment",
            ),
            (
                "ALTER WAREHOUSE SOPHIA_AI_ML_WH SET RESOURCE_MONITOR = SOPHIA_AI_PROD_MONITOR",
                "ML warehouse monitor assignment",
            ),
        ]

        success_count = 0
        total_operations = len(warehouse_queries) + len(monitor_assignments)

        # Create warehouses
        for query, description in warehouse_queries:
            if self.execute_query(query, description):
                success_count += 1
                self.deployment_status["warehouses"]["details"].append(description)

        # Assign resource monitors
        for query, description in monitor_assignments:
            if self.execute_query(query, description):
                success_count += 1

        if success_count == total_operations:
            self.deployment_status["warehouses"]["status"] = "completed"
            return True
        else:
            self.deployment_status["warehouses"]["status"] = "failed"
            return False

    def deploy_all(self) -> bool:
        """Deploy all Snowflake stability enhancements."""
        logger.info("🚀 Starting comprehensive Snowflake stability deployment...")

        # Initialize connection
        if not self.connect():
            return False

        # Deploy components in order
        components = [
            ("Resource Monitors", self.deploy_resource_monitors),
            ("Specialized Warehouses", self.deploy_specialized_warehouses),
        ]

        success_count = 0
        for component_name, deploy_func in components:
            logger.info(f"📦 Deploying {component_name}...")
            if deploy_func():
                success_count += 1
                logger.info(f"✅ {component_name} deployed successfully")
            else:
                logger.error(f"❌ {component_name} deployment failed")

        # Close connection
        if self.conn:
            self.conn.close()
            logger.info("Snowflake connection closed")

        logger.info(f"""
        ============================================================
        🎉 SNOWFLAKE STABILITY DEPLOYMENT COMPLETED
        ============================================================
        📊 Summary:
           Total Components: {len(components)}
           Successful: {success_count}
           Failed: {len(components) - success_count}
        ============================================================
        """)

        return success_count == len(components)


def main():
    """Main deployment function."""
    deployer = SnowflakeStabilityDeployer()
    success = deployer.deploy_all()

    if success:
        logger.info("🎉 Snowflake stability enhancements deployed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some components failed to deploy. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
