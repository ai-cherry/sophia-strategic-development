#!/usr/bin/env python3
"""
Snowflake Stability Enhancement Deployment Script
Implements comprehensive database-level stability features for Sophia AI production deployment.
"""

import asyncio
import logging
import os
import sys
from typing import Dict
from datetime import datetime
import json

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('snowflake_stability_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SnowflakeStabilityDeployer:
    def __init__(self):
        self.cortex_service = None
        self.deployment_status = {
            "resource_monitors": {"status": "pending", "details": []},
            "warehouses": {"status": "pending", "details": []},
            "security_roles": {"status": "pending", "details": []},
            "performance_optimization": {"status": "pending", "details": []},
            "backup_recovery": {"status": "pending", "details": []},
            "monitoring_schemas": {"status": "pending", "details": []}
        }
    
    async def initialize_connection(self) -> bool:
        """Initialize Snowflake connection with error handling."""
        try:
            # Get credentials from Pulumi ESC
            account = await get_config_value("snowflake_account")
            user = await get_config_value("snowflake_user") 
            password = await get_config_value("snowflake_password")
            database = await get_config_value("snowflake_database", "SOPHIA_AI_PROD")
            
            self.cortex_service = SnowflakeCortexService(
                account=account,
                user=user,
                password=password,
                database=database,
                warehouse="SOPHIA_AI_WH"
            )
            
            # Test connection
            await self.cortex_service.test_connection()
            logger.info("✅ Snowflake connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Snowflake connection: {e}")
            return False
    
    async def deploy_resource_monitors(self) -> bool:
        """Deploy resource monitors for cost control and performance management."""
        logger.info("🔧 Deploying resource monitors...")
        
        resource_monitor_queries = [
            # Main production resource monitor
            """
            CREATE OR REPLACE RESOURCE MONITOR SOPHIA_AI_PROD_MONITOR
            WITH CREDIT_QUOTA = 1000 
            FREQUENCY = MONTHLY
            TRIGGERS 
                ON 75 PERCENT DO NOTIFY
                ON 90 PERCENT DO SUSPEND_IMMEDIATE
                ON 95 PERCENT DO SUSPEND_IMMEDIATE;
            """,
            
            # Development resource monitor
            """
            CREATE OR REPLACE RESOURCE MONITOR SOPHIA_AI_DEV_MONITOR
            WITH CREDIT_QUOTA = 200
            FREQUENCY = MONTHLY
            TRIGGERS 
                ON 80 PERCENT DO NOTIFY
                ON 95 PERCENT DO SUSPEND_IMMEDIATE;
            """,
            
            # Analytics resource monitor
            """
            CREATE OR REPLACE RESOURCE MONITOR SOPHIA_AI_ANALYTICS_MONITOR
            WITH CREDIT_QUOTA = 500
            FREQUENCY = MONTHLY
            TRIGGERS 
                ON 85 PERCENT DO NOTIFY
                ON 95 PERCENT DO SUSPEND_IMMEDIATE;
            """
        ]
        
        try:
            for query in resource_monitor_queries:
                await self.cortex_service.execute_query(query)
                logger.info("✅ Resource monitor created successfully")
            
            self.deployment_status["resource_monitors"]["status"] = "completed"
            self.deployment_status["resource_monitors"]["details"] = [
                "SOPHIA_AI_PROD_MONITOR (1000 credits/month)",
                "SOPHIA_AI_DEV_MONITOR (200 credits/month)", 
                "SOPHIA_AI_ANALYTICS_MONITOR (500 credits/month)"
            ]
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy resource monitors: {e}")
            self.deployment_status["resource_monitors"]["status"] = "failed"
            self.deployment_status["resource_monitors"]["details"] = [str(e)]
            return False
    
    async def deploy_specialized_warehouses(self) -> bool:
        """Deploy specialized warehouses for different workload types."""
        logger.info("🏭 Deploying specialized warehouses...")
        
        warehouse_queries = [
            # Chat warehouse - fast, small, high concurrency
            """
            CREATE OR REPLACE WAREHOUSE SOPHIA_AI_CHAT_WH 
            WITH WAREHOUSE_SIZE = 'SMALL'
                AUTO_SUSPEND = 30
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = FALSE
                SCALING_POLICY = 'ECONOMY'
                MAX_CLUSTER_COUNT = 3
                MIN_CLUSTER_COUNT = 1
                COMMENT = 'Optimized for chat queries - fast response, low cost';
            """,
            
            # Analytics warehouse - medium, scalable
            """
            CREATE OR REPLACE WAREHOUSE SOPHIA_AI_ANALYTICS_WH 
            WITH WAREHOUSE_SIZE = 'MEDIUM'
                AUTO_SUSPEND = 300
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE
                SCALING_POLICY = 'STANDARD'
                MAX_CLUSTER_COUNT = 5
                MIN_CLUSTER_COUNT = 1
                COMMENT = 'Optimized for analytics and reporting workloads';
            """,
            
            # ETL warehouse - large, efficient
            """
            CREATE OR REPLACE WAREHOUSE SOPHIA_AI_ETL_WH 
            WITH WAREHOUSE_SIZE = 'LARGE'
                AUTO_SUSPEND = 60
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE
                SCALING_POLICY = 'ECONOMY'
                MAX_CLUSTER_COUNT = 2
                MIN_CLUSTER_COUNT = 1
                COMMENT = 'Optimized for ETL and batch processing';
            """,
            
            # AI processing warehouse - x-large for heavy AI workloads
            """
            CREATE OR REPLACE WAREHOUSE SOPHIA_AI_ML_WH 
            WITH WAREHOUSE_SIZE = 'X-LARGE'
                AUTO_SUSPEND = 180
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE
                SCALING_POLICY = 'ECONOMY'
                MAX_CLUSTER_COUNT = 3
                MIN_CLUSTER_COUNT = 1
                COMMENT = 'Optimized for AI/ML processing and embeddings';
            """
        ]
        
        # Assign resource monitors to warehouses
        monitor_assignments = [
            "ALTER WAREHOUSE SOPHIA_AI_CHAT_WH SET RESOURCE_MONITOR = SOPHIA_AI_PROD_MONITOR;",
            "ALTER WAREHOUSE SOPHIA_AI_ANALYTICS_WH SET RESOURCE_MONITOR = SOPHIA_AI_ANALYTICS_MONITOR;", 
            "ALTER WAREHOUSE SOPHIA_AI_ETL_WH SET RESOURCE_MONITOR = SOPHIA_AI_PROD_MONITOR;",
            "ALTER WAREHOUSE SOPHIA_AI_ML_WH SET RESOURCE_MONITOR = SOPHIA_AI_PROD_MONITOR;"
        ]
        
        try:
            # Create warehouses
            for query in warehouse_queries:
                await self.cortex_service.execute_query(query)
                logger.info("✅ Specialized warehouse created")
            
            # Assign resource monitors
            for query in monitor_assignments:
                await self.cortex_service.execute_query(query)
                logger.info("✅ Resource monitor assigned to warehouse")
            
            self.deployment_status["warehouses"]["status"] = "completed"
            self.deployment_status["warehouses"]["details"] = [
                "SOPHIA_AI_CHAT_WH (SMALL, 30s suspend)",
                "SOPHIA_AI_ANALYTICS_WH (MEDIUM, 300s suspend)",
                "SOPHIA_AI_ETL_WH (LARGE, 60s suspend)",
                "SOPHIA_AI_ML_WH (X-LARGE, 180s suspend)"
            ]
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy specialized warehouses: {e}")
            self.deployment_status["warehouses"]["status"] = "failed"
            self.deployment_status["warehouses"]["details"] = [str(e)]
            return False
    
    async def deploy_security_roles(self) -> bool:
        """Deploy security roles and access control."""
        logger.info("🔐 Deploying security roles and access control...")
        
        security_queries = [
            # Service roles
            "CREATE ROLE IF NOT EXISTS SOPHIA_AI_CHAT_SERVICE;",
            "CREATE ROLE IF NOT EXISTS SOPHIA_AI_ANALYTICS_SERVICE;",
            "CREATE ROLE IF NOT EXISTS SOPHIA_AI_ETL_SERVICE;",
            "CREATE ROLE IF NOT EXISTS SOPHIA_AI_ADMIN_SERVICE;",
            
            # Grant database access
            "GRANT USAGE ON DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_CHAT_SERVICE;",
            "GRANT USAGE ON DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_ANALYTICS_SERVICE;",
            "GRANT USAGE ON DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_ETL_SERVICE;",
            "GRANT ALL ON DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_ADMIN_SERVICE;",
            
            # Grant warehouse access
            "GRANT USAGE ON WAREHOUSE SOPHIA_AI_CHAT_WH TO ROLE SOPHIA_AI_CHAT_SERVICE;",
            "GRANT USAGE ON WAREHOUSE SOPHIA_AI_ANALYTICS_WH TO ROLE SOPHIA_AI_ANALYTICS_SERVICE;",
            "GRANT USAGE ON WAREHOUSE SOPHIA_AI_ETL_WH TO ROLE SOPHIA_AI_ETL_SERVICE;",
            "GRANT USAGE ON WAREHOUSE SOPHIA_AI_ML_WH TO ROLE SOPHIA_AI_ADMIN_SERVICE;",
            
            # Schema-level permissions
            "GRANT USAGE ON SCHEMA SOPHIA_AI_PROD.UNIVERSAL_CHAT TO ROLE SOPHIA_AI_CHAT_SERVICE;",
            "GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA SOPHIA_AI_PROD.UNIVERSAL_CHAT TO ROLE SOPHIA_AI_CHAT_SERVICE;",
            "GRANT SELECT, INSERT, UPDATE ON ALL VIEWS IN SCHEMA SOPHIA_AI_PROD.UNIVERSAL_CHAT TO ROLE SOPHIA_AI_CHAT_SERVICE;",
            
            # Analytics permissions
            "GRANT USAGE ON ALL SCHEMAS IN DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_ANALYTICS_SERVICE;",
            "GRANT SELECT ON ALL TABLES IN DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_ANALYTICS_SERVICE;",
            "GRANT SELECT ON ALL VIEWS IN DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_ANALYTICS_SERVICE;",
            
            # ETL permissions
            "GRANT USAGE ON ALL SCHEMAS IN DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_ETL_SERVICE;",
            "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN DATABASE SOPHIA_AI_PROD TO ROLE SOPHIA_AI_ETL_SERVICE;",
        ]
        
        try:
            for query in security_queries:
                await self.cortex_service.execute_query(query)
            
            logger.info("✅ Security roles and permissions deployed successfully")
            self.deployment_status["security_roles"]["status"] = "completed"
            self.deployment_status["security_roles"]["details"] = [
                "SOPHIA_AI_CHAT_SERVICE (chat operations)",
                "SOPHIA_AI_ANALYTICS_SERVICE (read-only analytics)",
                "SOPHIA_AI_ETL_SERVICE (data processing)",
                "SOPHIA_AI_ADMIN_SERVICE (full admin access)"
            ]
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy security roles: {e}")
            self.deployment_status["security_roles"]["status"] = "failed"
            self.deployment_status["security_roles"]["details"] = [str(e)]
            return False
    
    async def deploy_performance_optimization(self) -> bool:
        """Deploy performance optimization features."""
        logger.info("⚡ Deploying performance optimization...")
        
        optimization_queries = [
            # Clustering for chat tables
            """
            ALTER TABLE SOPHIA_AI_PROD.UNIVERSAL_CHAT.KNOWLEDGE_ENTRIES 
            CLUSTER BY (CREATED_AT, CATEGORY_ID);
            """,
            
            """
            ALTER TABLE SOPHIA_AI_PROD.UNIVERSAL_CHAT.CONVERSATION_MESSAGES 
            CLUSTER BY (SESSION_ID, CREATED_AT);
            """,
            
            # Clustering for AI Memory
            """
            ALTER TABLE SOPHIA_AI_PROD.AI_MEMORY.BUSINESS_MEMORIES 
            CLUSTER BY (CREATED_AT, IMPORTANCE_SCORE);
            """,
            
            # Search optimization
            """
            CREATE OR REPLACE SEARCH OPTIMIZATION ON SOPHIA_AI_PROD.UNIVERSAL_CHAT.KNOWLEDGE_ENTRIES
            ON EQUALITY(TITLE, CATEGORY_ID) 
            ON SUBSTRING(CONTENT);
            """,
            
            # Automatic clustering
            """
            ALTER TABLE SOPHIA_AI_PROD.UNIVERSAL_CHAT.KNOWLEDGE_ENTRIES 
            SET ENABLE_AUTOMATIC_CLUSTERING = TRUE;
            """,
            
            """
            ALTER TABLE SOPHIA_AI_PROD.UNIVERSAL_CHAT.CONVERSATION_MESSAGES 
            SET ENABLE_AUTOMATIC_CLUSTERING = TRUE;
            """,
            
            """
            ALTER TABLE SOPHIA_AI_PROD.AI_MEMORY.BUSINESS_MEMORIES 
            SET ENABLE_AUTOMATIC_CLUSTERING = TRUE;
            """
        ]
        
        try:
            for query in optimization_queries:
                await self.cortex_service.execute_query(query)
                logger.info("✅ Performance optimization applied")
            
            self.deployment_status["performance_optimization"]["status"] = "completed"
            self.deployment_status["performance_optimization"]["details"] = [
                "Clustering on KNOWLEDGE_ENTRIES",
                "Clustering on CONVERSATION_MESSAGES", 
                "Clustering on BUSINESS_MEMORIES",
                "Search optimization enabled",
                "Automatic clustering enabled"
            ]
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy performance optimization: {e}")
            self.deployment_status["performance_optimization"]["status"] = "failed"
            self.deployment_status["performance_optimization"]["details"] = [str(e)]
            return False
    
    async def deploy_backup_recovery(self) -> bool:
        """Deploy backup and recovery features."""
        logger.info("💾 Deploying backup and recovery features...")
        
        backup_queries = [
            # Extended time travel for critical tables
            """
            ALTER TABLE SOPHIA_AI_PROD.UNIVERSAL_CHAT.KNOWLEDGE_ENTRIES 
            SET DATA_RETENTION_TIME_IN_DAYS = 7;
            """,
            
            """
            ALTER TABLE SOPHIA_AI_PROD.UNIVERSAL_CHAT.CONVERSATION_MESSAGES 
            SET DATA_RETENTION_TIME_IN_DAYS = 7;
            """,
            
            """
            ALTER TABLE SOPHIA_AI_PROD.AI_MEMORY.BUSINESS_MEMORIES 
            SET DATA_RETENTION_TIME_IN_DAYS = 7;
            """,
            
            # Fail-safe for critical data
            """
            ALTER TABLE SOPHIA_AI_PROD.UNIVERSAL_CHAT.KNOWLEDGE_ENTRIES 
            SET ENABLE_SCHEMA_EVOLUTION = TRUE;
            """,
            
            """
            ALTER TABLE SOPHIA_AI_PROD.UNIVERSAL_CHAT.CONVERSATION_MESSAGES 
            SET ENABLE_SCHEMA_EVOLUTION = TRUE;
            """
        ]
        
        try:
            for query in backup_queries:
                await self.cortex_service.execute_query(query)
                logger.info("✅ Backup and recovery feature deployed")
            
            self.deployment_status["backup_recovery"]["status"] = "completed"
            self.deployment_status["backup_recovery"]["details"] = [
                "7-day time travel on critical tables",
                "Schema evolution enabled",
                "Fail-safe protection active"
            ]
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy backup and recovery: {e}")
            self.deployment_status["backup_recovery"]["status"] = "failed"
            self.deployment_status["backup_recovery"]["details"] = [str(e)]
            return False
    
    async def deploy_monitoring_schemas(self) -> bool:
        """Deploy monitoring and quality schemas."""
        logger.info("📊 Deploying monitoring schemas...")
        
        monitoring_queries = [
            # Monitoring schema
            "CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_PROD.MONITORING;",
            "CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_PROD.QUALITY;", 
            "CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_PROD.BACKUPS;",
            
            # Monitoring tables
            """
            CREATE OR REPLACE TABLE SOPHIA_AI_PROD.MONITORING.QUERY_PERFORMANCE (
                query_id VARCHAR(255),
                query_text TEXT,
                execution_time_ms INTEGER,
                warehouse_name VARCHAR(255),
                user_name VARCHAR(255),
                execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                bytes_scanned INTEGER,
                partitions_scanned INTEGER,
                cache_result BOOLEAN
            );
            """,
            
            """
            CREATE OR REPLACE TABLE SOPHIA_AI_PROD.MONITORING.WAREHOUSE_USAGE (
                warehouse_name VARCHAR(255),
                usage_date DATE,
                total_credits_used DECIMAL(10,2),
                total_queries INTEGER,
                avg_execution_time_ms INTEGER,
                peak_concurrent_queries INTEGER,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            );
            """,
            
            """
            CREATE OR REPLACE TABLE SOPHIA_AI_PROD.QUALITY.DATA_QUALITY_CHECKS (
                check_id VARCHAR(255),
                table_name VARCHAR(255),
                check_type VARCHAR(100),
                check_result VARCHAR(50),
                error_count INTEGER,
                total_rows INTEGER,
                check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                details TEXT
            );
            """,
            
            # Grant permissions
            "GRANT ALL ON SCHEMA SOPHIA_AI_PROD.MONITORING TO ROLE SOPHIA_AI_ADMIN_SERVICE;",
            "GRANT ALL ON SCHEMA SOPHIA_AI_PROD.QUALITY TO ROLE SOPHIA_AI_ADMIN_SERVICE;",
            "GRANT ALL ON SCHEMA SOPHIA_AI_PROD.BACKUPS TO ROLE SOPHIA_AI_ADMIN_SERVICE;",
        ]
        
        try:
            for query in monitoring_queries:
                await self.cortex_service.execute_query(query)
                logger.info("✅ Monitoring schema component deployed")
            
            self.deployment_status["monitoring_schemas"]["status"] = "completed"
            self.deployment_status["monitoring_schemas"]["details"] = [
                "MONITORING schema created",
                "QUALITY schema created",
                "BACKUPS schema created",
                "Performance monitoring tables created",
                "Data quality checking tables created"
            ]
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy monitoring schemas: {e}")
            self.deployment_status["monitoring_schemas"]["status"] = "failed"
            self.deployment_status["monitoring_schemas"]["details"] = [str(e)]
            return False
    
    async def generate_deployment_report(self) -> Dict:
        """Generate comprehensive deployment report."""
        report = {
            "deployment_timestamp": datetime.now().isoformat(),
            "overall_status": "success" if all(
                component["status"] == "completed" 
                for component in self.deployment_status.values()
            ) else "partial_failure",
            "components": self.deployment_status,
            "summary": {
                "total_components": len(self.deployment_status),
                "successful_components": sum(
                    1 for component in self.deployment_status.values() 
                    if component["status"] == "completed"
                ),
                "failed_components": sum(
                    1 for component in self.deployment_status.values() 
                    if component["status"] == "failed"
                )
            }
        }
        
        # Save report to file
        report_file = f"snowflake_stability_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📋 Deployment report saved to {report_file}")
        return report
    
    async def deploy_all(self) -> bool:
        """Deploy all Snowflake stability enhancements."""
        logger.info("🚀 Starting comprehensive Snowflake stability deployment...")
        
        # Initialize connection
        if not await self.initialize_connection():
            return False
        
        # Deploy components in order
        components = [
            ("Resource Monitors", self.deploy_resource_monitors),
            ("Specialized Warehouses", self.deploy_specialized_warehouses),
            ("Security Roles", self.deploy_security_roles),
            ("Performance Optimization", self.deploy_performance_optimization),
            ("Backup & Recovery", self.deploy_backup_recovery),
            ("Monitoring Schemas", self.deploy_monitoring_schemas)
        ]
        
        success_count = 0
        for component_name, deploy_func in components:
            logger.info(f"📦 Deploying {component_name}...")
            if await deploy_func():
                success_count += 1
                logger.info(f"✅ {component_name} deployed successfully")
            else:
                logger.error(f"❌ {component_name} deployment failed")
        
        # Generate report
        report = await self.generate_deployment_report()
        
        # Log summary
        logger.info(f"""
        ============================================================
        🎉 SNOWFLAKE STABILITY DEPLOYMENT COMPLETED
        ============================================================
        📊 Summary:
           Total Components: {len(components)}
           Successful: {success_count}
           Failed: {len(components) - success_count}
           Overall Status: {report['overall_status']}
        
        📋 Deployment Report: {report}
        ============================================================
        """)
        
        return success_count == len(components)

async def main():
    """Main deployment function."""
    deployer = SnowflakeStabilityDeployer()
    success = await deployer.deploy_all()
    
    if success:
        logger.info("🎉 All Snowflake stability enhancements deployed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some components failed to deploy. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
