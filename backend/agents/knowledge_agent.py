"""Knowledge Agent for Sophia AI.

Handles interacting with the Knowledge Base MCP Server.
"""

import logging

from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult
from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class KnowledgeAgent(BaseAgent):
    """An agent that specializes in interacting with the knowledge base.

    It uses the MCPClient to communicate with the KnowledgeMCPServer.
    """

    def __init__(self, config: AgentConfig, mcp_client: MCPClient):
        super().__init__(config)
        self.mcp_client = mcp_client

    async def execute_task(self, task: Task) -> TaskResult:
        """Executes a task by calling the appropriate tool on the Knowledge MCP Server.

        Args:
            task: The task to execute, containing the command and parameters.

        Returns:
            A TaskResult with the status and output of the operation.
        """
        command = task.command
        params = task.parameters

        try:
            # The 'command' for this agent is the tool name on the MCP server.
            # E.g., 'search', 'ingest_document'
            logger.info(f"KnowledgeAgent executing '{command}' with params: {params}")

            result = await self.mcp_client.call_tool(
                server="knowledge", tool=command, **params
            )

            if result.get("error"):
                return TaskResult(status="error", output=result)

            return TaskResult(status="success", output=result)

        except Exception as e:
            logger.error(
                f"Error executing knowledge task '{command}': {e}", exc_info=True
            )
            return TaskResult(status="error", output={"error": str(e)})
