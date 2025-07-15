"""
MCP Orchestration Adapter for Sophia Unified Orchestrator

This adapter provides the missing methods and integration between
the MCPOrchestrationService and SophiaUnifiedOrchestrator.

Date: July 9, 2025
"""

import logging
from typing import Any, Optional

from infrastructure.services.mcp_orchestration_service import (
    BusinessTask,
    MCPOrchestrationService,
    TaskPriority,
)

logger = logging.getLogger(__name__)


class MCPOrchestrationAdapter:
    """Adapter to provide missing methods for MCP orchestration"""

    def __init__(self, mcp_service: MCPOrchestrationService):
        self.mcp_service = mcp_service
        self._capability_mapping = self._build_capability_mapping()

    def _build_capability_mapping(self) -> dict[str, list[str]]:
        """Build mapping of capabilities to server names"""
        mapping = {}

        for server_name, server in self.mcp_service.servers.items():
            for capability in server.capabilities:
                if capability not in mapping:
                    mapping[capability] = []
                mapping[capability].append(server_name)

        return mapping

    async def get_servers_by_capability(
        self, capabilities: list[str]
    ) -> list[dict[str, Any]]:
        """Get servers that have any of the requested capabilities"""
        matching_servers = set()

        # Find servers with matching capabilities
        for capability in capabilities:
            if capability in self._capability_mapping:
                matching_servers.update(self._capability_mapping[capability])

        # Build server info list
        server_list = []
        for server_name in matching_servers:
            if server_name in self.mcp_service.servers:
                server = self.mcp_service.servers[server_name]
                server_list.append(
                    {
                        "name": server_name,
                        "port": server.port,
                        "capabilities": server.capabilities,
                        "healthy": await self._check_server_health(server_name),
                    }
                )

        return server_list

    async def _check_server_health(self, server_name: str) -> bool:
        """Check if a server is healthy"""
        health_status = self.mcp_service.health_status.get(server_name)
        if health_status:
            return health_status.status.value in ["healthy", "degraded"]
        return False

    async def route_to_server(
        self,
        server_name: str,
        tool: str,
        params: dict[str, Any],
        user_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Route a request to a specific MCP server"""
        try:
            response = await self.mcp_service.route_to_mcp(
                server=server_name,
                tool=tool,
                params=params,
                user_id=user_id,
            )

            if response.success:
                return {
                    "success": True,
                    "source": server_name,
                    "data": response.data,
                    "response_time": response.response_time_ms,
                }
            else:
                return {
                    "success": False,
                    "source": server_name,
                    "error": response.error_message,
                }

        except Exception as e:
            logger.error(f"Failed to route to {server_name}: {e}")
            return {
                "success": False,
                "source": server_name,
                "error": str(e),
            }

    async def execute_business_task(
        self,
        task_type: str,
        description: str,
        capabilities: list[str],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a business task through MCP orchestration"""
        import hashlib
        from datetime import datetime

        # Generate a unique task ID
        task_id = hashlib.md5(
            f"{task_type}_{description}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:8]

        task = BusinessTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            required_capabilities=capabilities,
            priority=TaskPriority.HIGH,
            context_data=context,
            requires_synthesis=True,
        )

        result = await self.mcp_service.execute_business_task(task)

        return {
            "success": result.success,
            "results": result.results,
            "servers_used": result.servers_used,
            "execution_time": result.execution_time_ms,
            "error": result.error_message,
        }

    async def get_health_status(self) -> dict[str, Any]:
        """Get health status of all MCP servers"""
        return await self.mcp_service.get_mcp_health_status()
