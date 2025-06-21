"""Sophia AI - Centralized MCP-Native Agent Framework
This framework is the single source of truth for all AI agent initialization,
management, and interaction via the Model Context Protocol (MCP).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.mcp.mcp_client import mcp_client

logger = logging.getLogger(__name__)


class MCPOrchestrator:
    """The central nervous system for Sophia's AI agents. It manages agent
    sessions and funnels all tool interactions through the single, universal
    mcp_client.
    """

    def __init__(self):
        self.is_initialized = False
        self.start_time: Optional[datetime] = None
        self.sessions: Dict[str, List[Dict]] = {}  # Simplified session state
        logger.info("MCPOrchestrator instance created.")

    async def initialize(self):
        """Initializes the framework."""
        if self.is_initialized:
            logger.warning("Framework already initialized.")
            return

        logger.info("Initializing MCP-Native Agent Framework...")
        self.start_time = datetime.now()
        self.is_initialized = True
        logger.info("✅ MCP-Native Agent Framework Initialized Successfully.")

    async def ask_agent(self, session_id: str, request: str) -> Dict:
        """The primary method for interacting with an agent. It simulates the
        agent receiving a request and using an MCP tool to respond.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append({"role": "user", "content": request})

        # This is where the agent's LLM would reason about which tool to use.
        # For this example, we simulate the agent deciding to call the 'pulumi' MCP service.
        logger.info("Agent decided to use the 'pulumi' MCP service.")

        # The agent uses the single, universal mcp_client.
        mcp_response = await mcp_client.get_context(
            service_name="pulumi",
            request=f"Preview the changes for the production stack based on user request: '{request}'",
        )

        final_answer = {
            "response": "I have initiated a preview of the infrastructure changes via the Pulumi MCP server.",
            "details_from_pulumi_mcp": mcp_response,
        }
        self.sessions[session_id].append({"role": "assistant", "content": final_answer})
        return final_answer

    async def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the agent framework."""
        return {
            "is_healthy": self.is_initialized,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "active_sessions": len(self.sessions),
            "mcp_gateway_endpoints": list(mcp_client.MCP_GATEWAY_ENDPOINTS.keys()),
        }

    async def shutdown(self):
        """Gracefully shuts down the framework."""
        logger.info("Shutting down MCP-Native Agent Framework...")
        self.is_initialized = False


# Singleton instance of the framework, now renamed to reflect its purpose
agent_framework = MCPOrchestrator()
