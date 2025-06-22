"""Admin Agent for Sophia AI.

Handles interaction with the Admin MCP Server for system management tasks.
"""

import logging

from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult
from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class AdminAgent(BaseAgent):
    """An agent that specializes in using the AdminMCPServer to perform.

    system-level checks and administrative actions.
    """
    def __init__(self, config: AgentConfig, mcp_client: MCPClient):
        super().__init__(config)
        self.mcp_client = mcp_client

    async def execute_task(self, task: Task) -> TaskResult:
        """Executes a task by calling the appropriate tool on the Admin MCP Server."""
        command = task.command
        params = task.parameters

        try:
            tool_name = self._map_command_to_tool(command)
            if not tool_name:
                return TaskResult(
                    status="error", output=f"Unknown admin command: {command}"
                )

            logger.info(
                f"AdminAgent executing tool '{tool_name}' with params: {params}"
            )

            result = await self.mcp_client.call_tool(
                server="admin", tool=tool_name, **params
            )

            if result.get("error"):
                return TaskResult(status="error", output=result)

            return TaskResult(status="success", output=result)

        except Exception as e:
            logger.error(f"Error executing admin task '{command}': {e}", exc_info=True)
            return TaskResult(status="error", output={"error": str(e)})

    def _map_command_to_tool(self, command: str) -> str:
        """Maps natural language commands to specific MCP tool names."""
        command_lower = command.lower()
        if "secret" in command_lower and "sync" in command_lower:
            return "get_secret_sync_status"
        if "health" in command_lower:
            return "check_all_integrations_health"
        if "list" in command_lower and "github" in command_lower:
            return "list_github_secrets"
        if "list" in command_lower and "pulumi" in command_lower:
            return "list_pulumi_secrets"
        return ""
