# backend/mcp/mcp_orchestrator.py
"""
The MCP Orchestrator for Sophia AI.

Inspired by composable agent frameworks like `lastmile-ai/mcp-agent`, this
orchestrator manages agent sessions and funnels all tool and service
interactions through the universal Model Context Protocol (MCP).
"""

import logging
from typing import Any, Dict, Optional
from backend.mcp.mcp_client import mcp_client

logger = logging.getLogger(__name__)

class MCPSession:
    """Represents a single, stateful interaction with an agent."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history = []
        logger.info(f"MCP Session '{self.session_id}' created.")

    async def ask(self, agent_persona: Dict, request: str) -> Dict:
        """
        The primary method for interacting with an agent. It simulates the
        agent receiving a request, using its tools (via MCP), and returning a response.
        """
        self.history.append({"role": "user", "content": request})
        
        # In a real scenario, the agent's LLM would decide which tool to call.
        # Here, we simulate the agent deciding it needs to talk to Pulumi.
        logger.info(f"Agent decided to use the 'pulumi' MCP service.")

        # The agent uses the single, universal mcp_client to talk to the tool.
        mcp_response = await mcp_client.get_context(
            service_name="pulumi",
            request="Preview the changes for the 'sophia-production' stack in the 'infra-main' project.",
            context={"user_request": request}
        )
        
        # The agent then uses the tool's response to formulate a final answer.
        final_answer = {
            "response": "I have contacted the Pulumi MCP server to preview the infrastructure changes.",
            "mcp_tool_response": mcp_response
        }
        self.history.append({"role": "assistant", "content": final_answer})
        return final_answer

class MCPOrchestrator:
    """
    Manages all MCP sessions and provides a clean interface for the application.
    """
    def __init__(self):
        self.sessions: Dict[str, MCPSession] = {}

    def create_session(self, session_id: str) -> MCPSession:
        """Creates a new, stateful session for an agent interaction."""
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        session = MCPSession(session_id)
        self.sessions[session_id] = session
        return session

# Singleton instance for the entire application
mcp_orchestrator = MCPOrchestrator()
