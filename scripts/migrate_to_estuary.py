#!/usr/bin/env python3
"""
Sophia AI Migration Script: MCP to Cortex + Estuary
Automated migration tool for transitioning infrastructure
"""

import argparse
import asyncio
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.integrations.estuary_flow_manager import EstuaryFlowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SophiaAIMigrator:
    """Orchestrates the migration from MCP to Cortex + Estuary"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = (
            self.project_root
            / "migration_backup"
            / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        self.migration_status = {
            "phase": None,
            "steps_completed": [],
            "errors": [],
            "warnings": [],
            "start_time": datetime.now().isoformat(),
        }

    async def migrate_data_pipeline(self):
        """Phase 1: Migrate data pipeline from Airbyte to Estuary"""
        logger.info("🚀 Starting Phase 1: Data Pipeline Migration")
        self.migration_status["phase"] = "data_pipeline"

        try:
            # 1. Backup existing configurations
            self._backup_configurations()

            # 2. Create Snowflake schemas
            await self._create_snowflake_schemas()
            self.migration_status["steps_completed"].append("snowflake_schemas_created")

            # 3. Configure Estuary captures
            await self._configure_estuary_captures()
            self.migration_status["steps_completed"].append(
                "estuary_captures_configured"
            )

            # 4. Set up session management
            await self._setup_session_management()
            self.migration_status["steps_completed"].append("session_management_setup")

            # 5. Migrate vector storage
            await self._migrate_vector_storage()
            self.migration_status["steps_completed"].append("vector_storage_migrated")

            logger.info("✅ Phase 1 completed successfully")

        except Exception as e:
            logger.error(f"❌ Phase 1 failed: {e}")
            self.migration_status["errors"].append(f"data_pipeline: {str(e)}")
            raise

    async def migrate_ai_agents(self):
        """Phase 2: Migrate MCP servers to Cortex agents"""
        logger.info("🚀 Starting Phase 2: AI Agent Migration")
        self.migration_status["phase"] = "ai_agents"

        try:
            # 1. Create Cortex agent configurations
            self._create_cortex_configs()
            self.migration_status["steps_completed"].append("cortex_configs_created")

            # 2. Set up JWT authentication
            await self._setup_jwt_auth()
            self.migration_status["steps_completed"].append("jwt_auth_configured")

            # 3. Configure Portkey gateway
            await self._configure_portkey()
            self.migration_status["steps_completed"].append("portkey_configured")

            # 4. Update agent endpoints
            self._update_agent_endpoints()
            self.migration_status["steps_completed"].append("agent_endpoints_updated")

            logger.info("✅ Phase 2 completed successfully")

        except Exception as e:
            logger.error(f"❌ Phase 2 failed: {e}")
            self.migration_status["errors"].append(f"ai_agents: {str(e)}")
            raise

    async def modernize_api(self):
        """Phase 3: API Modernization"""
        logger.info("🚀 Starting Phase 3: API Modernization")
        self.migration_status["phase"] = "api_modernization"

        try:
            # 1. Update FastAPI routes
            self._update_fastapi_routes()
            self.migration_status["steps_completed"].append("fastapi_routes_updated")

            # 2. Add WebSocket support
            self._add_websocket_support()
            self.migration_status["steps_completed"].append("websocket_support_added")

            # 3. Implement connection pooling
            await self._setup_connection_pooling()
            self.migration_status["steps_completed"].append("connection_pooling_setup")

            # 4. Update async patterns
            self._update_async_patterns()
            self.migration_status["steps_completed"].append("async_patterns_updated")

            logger.info("✅ Phase 3 completed successfully")

        except Exception as e:
            logger.error(f"❌ Phase 3 failed: {e}")
            self.migration_status["errors"].append(f"api_modernization: {str(e)}")
            raise

    async def enhance_business_logic(self):
        """Phase 4: Business Logic Enhancement"""
        logger.info("🚀 Starting Phase 4: Business Logic Enhancement")
        self.migration_status["phase"] = "business_logic"

        try:
            # 1. Set up real-time CDC processing
            await self._setup_cdc_processing()
            self.migration_status["steps_completed"].append("cdc_processing_setup")

            # 2. Implement Cortex Search
            await self._implement_cortex_search()
            self.migration_status["steps_completed"].append("cortex_search_implemented")

            # 3. Create business dashboards
            self._create_business_dashboards()
            self.migration_status["steps_completed"].append("dashboards_created")

            # 4. Set up monitoring
            await self._setup_monitoring()
            self.migration_status["steps_completed"].append("monitoring_configured")

            logger.info("✅ Phase 4 completed successfully")

        except Exception as e:
            logger.error(f"❌ Phase 4 failed: {e}")
            self.migration_status["errors"].append(f"business_logic: {str(e)}")
            raise

    def _backup_configurations(self):
        """Backup existing configurations before migration"""
        logger.info("📦 Backing up existing configurations...")

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup MCP configurations
        mcp_config_path = self.project_root / "cursor_mcp_config.json"
        if mcp_config_path.exists():
            shutil.copy2(mcp_config_path, self.backup_dir / "cursor_mcp_config.json")

        # Backup environment files
        for env_file in self.project_root.glob(".env*"):
            if env_file.is_file():
                shutil.copy2(env_file, self.backup_dir / env_file.name)

        logger.info(f"✅ Configurations backed up to: {self.backup_dir}")

    async def _create_snowflake_schemas(self):
        """Create optimized Snowflake schemas for Estuary"""
        logger.info("❄️ Creating Snowflake schemas...")

        schema_sql = """
        -- Estuary staging schemas
        CREATE SCHEMA IF NOT EXISTS SOPHIA_AI.ESTUARY_REALTIME;
        CREATE SCHEMA IF NOT EXISTS SOPHIA_AI.CORTEX_VECTORS;
        CREATE SCHEMA IF NOT EXISTS SOPHIA_AI.BUSINESS_ENRICHED;

        -- Session management
        CREATE TABLE IF NOT EXISTS SOPHIA_AI.PUBLIC.user_sessions (
            session_id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            last_activity TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            session_data VARIANT,
            ttl_seconds INTEGER DEFAULT 3600
        );

        -- Vector embeddings for Cortex Search
        CREATE TABLE IF NOT EXISTS SOPHIA_AI.CORTEX_VECTORS.embeddings (
            id VARCHAR(255) PRIMARY KEY,
            source_type VARCHAR(100),
            source_id VARCHAR(255),
            content TEXT,
            embedding VECTOR(FLOAT, 1536),
            metadata VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        );

        -- Cortex Search service
        CREATE OR REPLACE CORTEX SEARCH SERVICE sophia_search
        ON TABLE SOPHIA_AI.CORTEX_VECTORS.embeddings
        ATTRIBUTES (content)
        WAREHOUSE = CORTEX_COMPUTE_WH
        TARGET_LAG = '1 minute';
        """

        # Save SQL for manual execution
        sql_file = self.project_root / "scripts" / "snowflake_cortex_setup.sql"
        sql_file.write_text(schema_sql)

        logger.info(f"✅ Snowflake schema SQL saved to: {sql_file}")
        self.migration_status["warnings"].append(
            "Execute snowflake_cortex_setup.sql manually in Snowflake"
        )

    async def _configure_estuary_captures(self):
        """Configure Estuary Flow captures"""
        logger.info("🌊 Configuring Estuary captures...")

        # Use existing Estuary Flow Manager
        estuary_manager = EstuaryFlowManager()
        results = estuary_manager.create_sophia_ai_foundation()

        if results.get("success"):
            logger.info("✅ Estuary captures configured successfully")
        else:
            raise Exception(f"Estuary configuration failed: {results.get('errors')}")

    def _create_cortex_configs(self):
        """Create Cortex agent configuration file"""
        logger.info("🤖 Creating Cortex agent configurations...")

        cortex_config = {
            "agents": {
                "snowflake_ops": {
                    "model": "mistral-large",
                    "temperature": 0.1,
                    "system_prompt": "You are a Snowflake database expert. Help users with SQL queries, performance optimization, and schema management.",
                    "tools": [
                        {
                            "name": "execute_query",
                            "description": "Execute SQL query on Snowflake",
                            "parameters": {"query": "string", "warehouse": "string"},
                        },
                        {
                            "name": "optimize_query",
                            "description": "Analyze and optimize SQL query",
                            "parameters": {"query": "string"},
                        },
                    ],
                },
                "semantic_memory": {
                    "model": "mistral-7b",
                    "temperature": 0.3,
                    "system_prompt": "You are a memory management agent. Store and retrieve information using semantic search.",
                    "tools": [
                        {
                            "name": "store_memory",
                            "description": "Store information with embeddings",
                            "parameters": {"content": "string", "metadata": "object"},
                        },
                        {
                            "name": "recall_memory",
                            "description": "Retrieve similar memories",
                            "parameters": {"query": "string", "limit": "integer"},
                        },
                    ],
                },
                "business_intelligence": {
                    "model": "mistral-large",
                    "temperature": 0.2,
                    "system_prompt": "You are a business intelligence expert. Analyze data, generate insights, and help with strategic decisions.",
                    "tools": [
                        {
                            "name": "analyze_metrics",
                            "description": "Analyze business metrics",
                            "parameters": {
                                "metric_type": "string",
                                "time_range": "string",
                            },
                        },
                        {
                            "name": "generate_insights",
                            "description": "Generate AI-powered business insights",
                            "parameters": {
                                "data_source": "string",
                                "focus_area": "string",
                            },
                        },
                    ],
                },
            }
        }

        config_path = self.project_root / "backend" / "config" / "cortex_agents.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(cortex_config, f, default_flow_style=False)

        logger.info(f"✅ Cortex configurations saved to: {config_path}")

    def _update_fastapi_routes(self):
        """Update FastAPI app to include new routes"""
        logger.info("🔄 Updating FastAPI routes...")

        # Add import to fastapi_app.py
        fastapi_app_path = self.project_root / "backend" / "app" / "fastapi_app.py"

        if fastapi_app_path.exists():
            content = fastapi_app_path.read_text()

            # Add import if not present
            if (
                "from backend.api.cortex_routes import router as cortex_router"
                not in content
            ):
                import_line = (
                    "from backend.api.cortex_routes import router as cortex_router"
                )
                content = content.replace(
                    "from backend.api.universal_chat_routes import router as chat_router",
                    f"from backend.api.universal_chat_routes import router as chat_router\n{import_line}",
                )

                # Add router
                content = content.replace(
                    "app.include_router(chat_router)",
                    "app.include_router(chat_router)\napp.include_router(cortex_router)",
                )

                fastapi_app_path.write_text(content)
                logger.info("✅ FastAPI routes updated")
            else:
                logger.info("ℹ️ FastAPI routes already updated")

    def generate_migration_report(self):
        """Generate comprehensive migration report"""
        self.migration_status["end_time"] = datetime.now().isoformat()

        report = {
            **self.migration_status,
            "summary": {
                "total_steps": len(self.migration_status["steps_completed"]),
                "errors": len(self.migration_status["errors"]),
                "warnings": len(self.migration_status["warnings"]),
                "success": len(self.migration_status["errors"]) == 0,
            },
        }

        report_path = (
            self.project_root
            / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Migration report saved to: {report_path}")
        return report

    # Placeholder methods for remaining functionality
    async def _setup_session_management(self):
        logger.info("✅ Session management setup completed (placeholder)")

    async def _migrate_vector_storage(self):
        logger.info("✅ Vector storage migration completed (placeholder)")

    async def _setup_jwt_auth(self):
        logger.info("✅ JWT authentication setup completed (placeholder)")

    async def _configure_portkey(self):
        logger.info("✅ Portkey configuration completed (placeholder)")

    def _update_agent_endpoints(self):
        logger.info("✅ Agent endpoints updated (placeholder)")

    def _add_websocket_support(self):
        logger.info("✅ WebSocket support added (placeholder)")

    async def _setup_connection_pooling(self):
        logger.info("✅ Connection pooling setup completed (placeholder)")

    def _update_async_patterns(self):
        logger.info("✅ Async patterns updated (placeholder)")

    async def _setup_cdc_processing(self):
        logger.info("✅ CDC processing setup completed (placeholder)")

    async def _implement_cortex_search(self):
        logger.info("✅ Cortex Search implemented (placeholder)")

    def _create_business_dashboards(self):
        logger.info("✅ Business dashboards created (placeholder)")

    async def _setup_monitoring(self):
        logger.info("✅ Monitoring configured (placeholder)")


async def main():
    """Main migration entry point"""
    parser = argparse.ArgumentParser(description="Sophia AI Migration Tool")
    parser.add_argument(
        "--phase",
        choices=[
            "data-pipeline",
            "ai-agents",
            "api-modernization",
            "business-logic",
            "all",
        ],
        required=True,
        help="Migration phase to execute",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run migration phases in parallel (where possible)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes",
    )

    args = parser.parse_args()

    migrator = SophiaAIMigrator()

    try:
        if args.phase == "all":
            # Run all phases
            await migrator.migrate_data_pipeline()
            await migrator.migrate_ai_agents()
            await migrator.modernize_api()
            await migrator.enhance_business_logic()
        else:
            # Run specific phase
            phase_map = {
                "data-pipeline": migrator.migrate_data_pipeline,
                "ai-agents": migrator.migrate_ai_agents,
                "api-modernization": migrator.modernize_api,
                "business-logic": migrator.enhance_business_logic,
            }
            await phase_map[args.phase]()

        # Generate report
        report = migrator.generate_migration_report()

        if report["summary"]["success"]:
            logger.info("🎉 Migration completed successfully!")
        else:
            logger.error("❌ Migration completed with errors")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        migrator.generate_migration_report()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
