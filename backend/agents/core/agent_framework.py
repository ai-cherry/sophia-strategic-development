"""Sophia AI - Centralized MCP-Native Agent Framework.

This module manages initialization of tools and orchestrates agent sessions
through the Model Context Protocol (MCP).
"""

import logging
from datetime import datetime
from typing import Any, Coroutine, Dict, List, Optional

from backend.agents.tools.custom_chunking_tools import custom_chunking_tools
from backend.agents.tools.design_tools import design_tools
from backend.agents.tools.gong_tools import gong_tools
from backend.agents.tools.hubspot_tools import hubspot_tools
from backend.agents.tools.llm_tools import llm_tools
from backend.agents.tools.pulumi_tools import pulumi_tools
from backend.mcp.mcp_client import MCP_GATEWAY_ENDPOINTS, mcp_client

logger = logging.getLogger(__name__)


class MCPOrchestrator:
    """Central orchestrator for Sophia's agents."""

    def __init__(self) -> None:
        """Initialize the orchestrator with default state."""
        self.is_initialized = False
        self.start_time: Optional[datetime] = None
        self.sessions: Dict[str, List[Dict]] = {}
        logger.info("MCPOrchestrator instance created.")

    async def initialize(self) -> None:
        """Initialize the framework and load tools."""
        if self.is_initialized:
            logger.warning("Framework already initialized.")
            return

        logger.info("Initializing MCP-Native Agent Framework...")
        self.start_time = datetime.now()
        await self.initialize_tools()
        self.is_initialized = True
        logger.info("✅ MCP-Native Agent Framework Initialized Successfully.")

    async def ask_agent(self, session_id: str, request: str) -> Dict[str, Any]:
        """Simulate an agent using MCP to answer a request."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": "user", "content": request})

        logger.info("Agent decided to use the 'pulumi' MCP service.")

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
        """Return the current status of the agent framework."""
        return {
            "is_healthy": self.is_initialized,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "active_sessions": len(self.sessions),
            "mcp_gateway_endpoints": list(MCP_GATEWAY_ENDPOINTS.keys()),
        }

    async def shutdown(self) -> None:
        """Gracefully shut down the framework."""
        logger.info("Shutting down MCP-Native Agent Framework...")
        self.is_initialized = False

    async def initialize_tools(self) -> None:
        """Load all defined tools and register them for agent use."""
        logger.info("Initializing and registering Agno-native tools...")
        all_tools = [
            gong_tools,
            hubspot_tools,
            custom_chunking_tools,
            pulumi_tools,
            llm_tools,
            design_tools,
        ]

        for tool_collection in all_tools:
            for tool_name, tool_func in tool_collection.items():
                self.register_tool(tool_name, tool_func)

        logger.info("Tool registration complete.")

    def register_tool(self, name: str, function: Coroutine) -> None:
        """Register a single tool function in the framework."""
        if not hasattr(self, "tool_registry"):
            self.tool_registry = {}
        if name in self.tool_registry:
            logger.warning(f"Tool '{name}' is already registered. Overwriting.")
        self.tool_registry[name] = function
        logger.debug(f"Registered tool: {name}")


# Singleton instance of the framework
agent_framework = MCPOrchestrator()
