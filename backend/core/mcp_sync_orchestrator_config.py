#!/usr/bin/env python3
"""
MCP Sync Orchestrator Configuration
Centralized configuration and initialization for all MCP servers with sync orchestration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

from backend.core.cross_platform_sync_orchestrator import (
    CrossPlatformSyncOrchestrator,
    SyncConfiguration,
    SyncPriority,
)
from backend.mcp_servers.base.standardized_mcp_server import (
    MCPServerConfig,
    SyncPriority as ServerSyncPriority,
)
from backend.monitoring.mcp_metrics_collector import MCPMetricsCollector

logger = logging.getLogger(__name__)


class MCPServerDefinition:
    """Definition for an MCP server configuration"""

    def __init__(
        self,
        name: str,
        port: int,
        server_class: str,
        sync_priority: SyncPriority,
        sync_interval_minutes: int,
        data_types: List[str],
        dependencies: List[str] = None,
        enable_monitoring: bool = True,
        max_concurrent_requests: int = 20,
        request_timeout_seconds: int = 30,
    ):
        self.name = name
        self.port = port
        self.server_class = server_class
        self.sync_priority = sync_priority
        self.sync_interval_minutes = sync_interval_minutes
        self.data_types = data_types
        self.dependencies = dependencies or []
        self.enable_monitoring = enable_monitoring
        self.max_concurrent_requests = max_concurrent_requests
        self.request_timeout_seconds = request_timeout_seconds


class MCPSyncOrchestratorConfig:
    """
    Centralized configuration and orchestration for all MCP servers
    Manages sync priorities, dependencies, and monitoring
    """

    def __init__(self):
        self.sync_orchestrator = CrossPlatformSyncOrchestrator()
        self.metrics_collector = MCPMetricsCollector("mcp_orchestrator")
        self.active_servers: Dict[str, Any] = {}
        self.server_definitions = self._get_server_definitions()
        self.sync_scheduler_running = False

    def _get_server_definitions(self) -> Dict[str, MCPServerDefinition]:
        """Define all MCP servers with their configurations"""
        return {
            "ai_memory": MCPServerDefinition(
                name="ai_memory",
                port=9000,
                server_class="backend.mcp.standardized_ai_memory_mcp_server.StandardizedAiMemoryMCPServer",
                sync_priority=SyncPriority.HIGH,
                sync_interval_minutes=5,
                data_types=["memories", "embeddings", "ai_insights"],
                dependencies=[],
                enable_monitoring=True,
                max_concurrent_requests=50,
                request_timeout_seconds=30,
            ),
            "asana": MCPServerDefinition(
                name="asana",
                port=3006,
                server_class="mcp-servers.asana.asana_mcp_server.AsanaMCPServer",
                sync_priority=SyncPriority.HIGH,
                sync_interval_minutes=10,
                data_types=["projects", "tasks", "team_analytics"],
                dependencies=[],
                enable_monitoring=True,
            ),
            "notion": MCPServerDefinition(
                name="notion",
                port=3007,
                server_class="mcp-servers.notion.notion_mcp_server.NotionMCPServer",
                sync_priority=SyncPriority.MEDIUM,
                sync_interval_minutes=15,
                data_types=["pages", "databases", "knowledge_base"],
                dependencies=[],
                enable_monitoring=True,
            ),
            "codacy": MCPServerDefinition(
                name="codacy",
                port=3008,
                server_class="mcp-servers.codacy.codacy_mcp_server.CodacyMCPServer",
                sync_priority=SyncPriority.MEDIUM,
                sync_interval_minutes=20,
                data_types=["code_analysis", "security_scans", "quality_metrics"],
                dependencies=[],
                enable_monitoring=True,
            ),
            "snowflake_admin": MCPServerDefinition(
                name="snowflake_admin",
                port=3009,
                server_class="mcp-servers.snowflake_admin.snowflake_admin_mcp_server.SnowflakeAdminMCPServer",
                sync_priority=SyncPriority.HIGH,
                sync_interval_minutes=30,
                data_types=["schema_changes", "query_performance", "data_quality"],
                dependencies=[
                    "ai_memory"
                ],  # Depends on AI Memory for intelligent analysis
                enable_monitoring=True,
            ),
            "linear": MCPServerDefinition(
                name="linear",
                port=3010,
                server_class="backend.agents.specialized.linear_project_health_agent.LinearProjectHealthAgent",
                sync_priority=SyncPriority.MEDIUM,
                sync_interval_minutes=15,
                data_types=["issues", "projects", "team_health"],
                dependencies=["ai_memory"],  # For project health insights
                enable_monitoring=True,
            ),
        }

    async def initialize_orchestrator(self) -> Dict[str, Any]:
        """Initialize the sync orchestrator with all server configurations"""
        logger.info("Initializing MCP Sync Orchestrator...")

        initialization_results = {
            "orchestrator_initialized": False,
            "servers_configured": 0,
            "sync_configurations_created": 0,
            "errors": [],
        }

        try:
            # Configure sync for each server
            for server_name, server_def in self.server_definitions.items():
                try:
                    await self._configure_server_sync(server_def)
                    initialization_results["servers_configured"] += 1

                    # Create sync configurations for each data type
                    for data_type in server_def.data_types:
                        sync_config = SyncConfiguration(
                            platform=server_name,
                            data_type=data_type,
                            priority=server_def.sync_priority,
                            sync_interval_minutes=server_def.sync_interval_minutes,
                            dependencies=server_def.dependencies,
                            max_retries=3,
                            enable_conflict_resolution=True,
                        )

                        self.sync_orchestrator.add_sync_configuration(sync_config)
                        initialization_results["sync_configurations_created"] += 1

                    logger.info(f"✅ Configured sync for {server_name}")

                except Exception as e:
                    error_msg = f"Failed to configure {server_name}: {e}"
                    logger.error(error_msg)
                    initialization_results["errors"].append(error_msg)

            initialization_results["orchestrator_initialized"] = True
            logger.info("🚀 MCP Sync Orchestrator initialized successfully")

            # Record metrics
            self.metrics_collector.record_workflow_metrics(
                "orchestrator_initialization",
                "completed",
                5.0,  # Processing time
                initialization_results["servers_configured"],
                len(initialization_results["errors"]),
            )

        except Exception as e:
            error_msg = f"Failed to initialize orchestrator: {e}"
            logger.error(error_msg)
            initialization_results["errors"].append(error_msg)

        return initialization_results

    async def _configure_server_sync(self, server_def: MCPServerDefinition):
        """Configure sync settings for a specific server"""
        # Create server configuration
        server_config = MCPServerConfig(
            server_name=server_def.name,
            port=server_def.port,
            sync_priority=self._convert_sync_priority(server_def.sync_priority),
            sync_interval_minutes=server_def.sync_interval_minutes,
            enable_metrics=server_def.enable_monitoring,
            max_concurrent_requests=server_def.max_concurrent_requests,
            request_timeout_seconds=server_def.request_timeout_seconds,
        )

        # Store configuration for later use
        self.active_servers[server_def.name] = {
            "config": server_config,
            "definition": server_def,
            "last_sync": None,
            "next_sync": datetime.now()
            + timedelta(minutes=server_def.sync_interval_minutes),
            "sync_count": 0,
            "error_count": 0,
        }

    def _convert_sync_priority(
        self, orchestrator_priority: SyncPriority
    ) -> ServerSyncPriority:
        """Convert orchestrator sync priority to server sync priority"""
        priority_mapping = {
            SyncPriority.REAL_TIME: ServerSyncPriority.REAL_TIME,
            SyncPriority.HIGH: ServerSyncPriority.HIGH,
            SyncPriority.MEDIUM: ServerSyncPriority.MEDIUM,
            SyncPriority.LOW: ServerSyncPriority.LOW,
        }
        return priority_mapping.get(orchestrator_priority, ServerSyncPriority.MEDIUM)

    async def start_sync_scheduler(self) -> None:
        """Start the automated sync scheduler"""
        if self.sync_scheduler_running:
            logger.warning("Sync scheduler is already running")
            return

        self.sync_scheduler_running = True
        logger.info("🕐 Starting MCP sync scheduler...")

        # Start the main sync loop
        asyncio.create_task(self._sync_scheduler_loop())

        # Start metrics collection
        asyncio.create_task(self._metrics_collection_loop())

    async def _sync_scheduler_loop(self):
        """Main sync scheduler loop"""
        while self.sync_scheduler_running:
            try:
                current_time = datetime.now()

                # Check which servers need syncing
                servers_to_sync = []
                for server_name, server_info in self.active_servers.items():
                    if current_time >= server_info["next_sync"]:
                        servers_to_sync.append((server_name, server_info))

                if servers_to_sync:
                    # Execute syncs based on priority and dependencies
                    await self._execute_priority_sync(servers_to_sync)

                # Sleep for 30 seconds before next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in sync scheduler loop: {e}")
                await asyncio.sleep(60)  # Sleep longer on error

    async def _execute_priority_sync(self, servers_to_sync: List[tuple]):
        """Execute syncs in priority order with dependency management"""
        # Sort by priority (Real-time > High > Medium > Low)
        priority_order = {
            SyncPriority.REAL_TIME: 0,
            SyncPriority.HIGH: 1,
            SyncPriority.MEDIUM: 2,
            SyncPriority.LOW: 3,
        }

        servers_to_sync.sort(
            key=lambda x: priority_order.get(x[1]["definition"].sync_priority, 3)
        )

        # Execute syncs with dependency handling
        for server_name, server_info in servers_to_sync:
            try:
                # Check dependencies first
                if await self._check_dependencies(
                    server_info["definition"].dependencies
                ):
                    # Execute sync
                    sync_result = await self._execute_server_sync(
                        server_name, server_info
                    )

                    # Update server info
                    server_info["last_sync"] = datetime.now()
                    server_info["next_sync"] = datetime.now() + timedelta(
                        minutes=server_info["definition"].sync_interval_minutes
                    )
                    server_info["sync_count"] += 1

                    if not sync_result.get("success", False):
                        server_info["error_count"] += 1

                    logger.info(f"✅ Sync completed for {server_name}: {sync_result}")

                else:
                    logger.warning(
                        f"Skipping {server_name} sync due to unmet dependencies"
                    )

            except Exception as e:
                logger.error(f"Failed to sync {server_name}: {e}")
                server_info["error_count"] += 1

    async def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if all dependencies are healthy and recently synced"""
        if not dependencies:
            return True

        for dep_name in dependencies:
            if dep_name not in self.active_servers:
                logger.warning(f"Dependency {dep_name} not found in active servers")
                return False

            dep_info = self.active_servers[dep_name]

            # Check if dependency was synced recently (within 2x its sync interval)
            if dep_info["last_sync"]:
                sync_interval = dep_info["definition"].sync_interval_minutes
                max_age = timedelta(minutes=sync_interval * 2)

                if datetime.now() - dep_info["last_sync"] > max_age:
                    logger.warning(f"Dependency {dep_name} sync is too old")
                    return False
            else:
                logger.warning(f"Dependency {dep_name} has never been synced")
                return False

        return True

    async def _execute_server_sync(
        self, server_name: str, server_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute sync for a specific server"""
        try:
            # This would call the actual server's sync method
            # For now, simulate sync execution

            start_time = datetime.now()

            # Record sync attempt
            self.metrics_collector.record_sync_metrics(
                records_synced=100,  # Simulated
                success_rate=0.95,  # Simulated
                sync_duration_seconds=5.0,
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "server_name": server_name,
                "sync_time": start_time.isoformat(),
                "processing_time_seconds": processing_time,
                "records_processed": 100,  # Simulated
            }

        except Exception as e:
            logger.error(f"Server sync failed for {server_name}: {e}")
            return {"success": False, "server_name": server_name, "error": str(e)}

    async def _metrics_collection_loop(self):
        """Collect and report metrics periodically"""
        while self.sync_scheduler_running:
            try:
                # Collect metrics every 5 minutes
                await asyncio.sleep(300)

                # Generate sync statistics
                total_syncs = sum(
                    server["sync_count"] for server in self.active_servers.values()
                )
                total_errors = sum(
                    server["error_count"] for server in self.active_servers.values()
                )

                success_rate = (
                    (total_syncs - total_errors) / total_syncs
                    if total_syncs > 0
                    else 1.0
                )

                # Record orchestrator metrics
                self.metrics_collector.record_sync_metrics(
                    records_synced=total_syncs,
                    success_rate=success_rate,
                    sync_duration_seconds=0,  # Average would be calculated
                )

                logger.info(
                    f"📊 Orchestrator metrics: {total_syncs} syncs, {success_rate:.2%} success rate"
                )

            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")

    async def stop_sync_scheduler(self) -> None:
        """Stop the sync scheduler"""
        self.sync_scheduler_running = False
        logger.info("🛑 MCP sync scheduler stopped")

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current status of the orchestrator"""
        return {
            "scheduler_running": self.sync_scheduler_running,
            "active_servers": len(self.active_servers),
            "server_status": {
                name: {
                    "last_sync": info["last_sync"].isoformat()
                    if info["last_sync"]
                    else None,
                    "next_sync": info["next_sync"].isoformat(),
                    "sync_count": info["sync_count"],
                    "error_count": info["error_count"],
                    "success_rate": (info["sync_count"] - info["error_count"])
                    / info["sync_count"]
                    if info["sync_count"] > 0
                    else 1.0,
                }
                for name, info in self.active_servers.items()
            },
            "total_configurations": len(self.server_definitions),
        }

    async def force_sync(self, server_name: str) -> Dict[str, Any]:
        """Force sync for a specific server"""
        if server_name not in self.active_servers:
            return {"success": False, "error": f"Server {server_name} not found"}

        server_info = self.active_servers[server_name]

        try:
            result = await self._execute_server_sync(server_name, server_info)

            # Update server info if successful
            if result.get("success", False):
                server_info["last_sync"] = datetime.now()
                server_info["sync_count"] += 1
            else:
                server_info["error_count"] += 1

            return result

        except Exception as e:
            logger.error(f"Force sync failed for {server_name}: {e}")
            return {"success": False, "error": str(e)}


# Global orchestrator instance
mcp_orchestrator_config = MCPSyncOrchestratorConfig()


async def initialize_mcp_orchestration() -> Dict[str, Any]:
    """Initialize the global MCP orchestration system"""
    return await mcp_orchestrator_config.initialize_orchestrator()


async def start_mcp_sync_scheduler():
    """Start the global MCP sync scheduler"""
    await mcp_orchestrator_config.start_sync_scheduler()


def get_mcp_orchestrator_status() -> Dict[str, Any]:
    """Get the status of the MCP orchestrator"""
    return mcp_orchestrator_config.get_orchestrator_status()


async def stop_mcp_orchestration():
    """Stop the MCP orchestration system"""
    await mcp_orchestrator_config.stop_sync_scheduler()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize orchestrator
        result = await initialize_mcp_orchestration()
        print(f"Initialization result: {result}")

        # Start scheduler
        await start_mcp_sync_scheduler()

        # Let it run for a while
        await asyncio.sleep(60)

        # Check status
        status = get_mcp_orchestrator_status()
        print(f"Orchestrator status: {status}")

        # Stop
        await stop_mcp_orchestration()

    asyncio.run(main())
