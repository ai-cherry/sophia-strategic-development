"""Codebase Awareness Agent for Sophia AI.

Handles interaction with the Codebase Awareness MCP Server.
"""

import logging

from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult
from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class CodebaseAwarenessAgent(BaseAgent):
    """An agent that specializes in using the CodebaseAwarenessMCPServer.

    to answer questions about the project's architecture and code.
    """

    def __init__(self, config: AgentConfig, mcp_client: MCPClient):
        super().__init__(config)
        self.mcp_client = mcp_client

    async def execute_task(self, task: Task) -> TaskResult:
        """Executes a task by calling the appropriate tool on the Codebase Awareness MCP Server."""
        command = task.command
        params = task.parameters

        try:
            # We map the task command to the MCP tool name.
            # E.g., a natural language command "ingest the codebase" will be
            # translated to the 'ingest_codebase' tool.

            tool_name = self._map_command_to_tool(command)
            if not tool_name:
                return TaskResult(
                    status="error",
                    output=f"Unknown codebase awareness command: {command}",
                )

            logger.info(
                f"CodebaseAwarenessAgent executing tool '{tool_name}' with params: {params}"
            )

            result = await self.mcp_client.call_tool(
                server="codebase_awareness", tool=tool_name, **params
            )

            if result.get("error"):
                return TaskResult(status="error", output=result)

            return TaskResult(status="success", output=result)

        except Exception as e:
            logger.error(
                f"Error executing codebase awareness task '{command}': {e}",
                exc_info=True,
            )
            return TaskResult(status="error", output={"error": str(e)})

    def _map_command_to_tool(self, command: str) -> str:
        """Maps natural language commands to specific MCP tool names."""
        command_lower = command.lower()
        if "ingest" in command_lower:
            return "ingest_codebase"
        if "find" in command_lower and "code" in command_lower:
            return "find_relevant_code"
        if "summary" in command_lower or "summarize" in command_lower:
            return "get_file_summary"
        return ""  # Default case
