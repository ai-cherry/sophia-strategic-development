"""
Sophia AI - Centralized MCP-Native Agent Framework.

This framework is the single source of truth for all AI agent initialization,
management, and interaction via the Model Context Protocol (MCP).
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Coroutine, Dict, List, Optional

from backend.core.auto_esc_config import config
from backend.mcp.mcp_client import mcp_client, MCP_GATEWAY_ENDPOINTS
from backend.agents.tools.gong_tools import gong_tools
from backend.agents.tools.hubspot_tools import hubspot_tools
from backend.agents.tools.custom_chunking_tools import custom_chunking_tools
from backend.agents.tools.pulumi_tools import pulumi_tools
from backend.agents.tools.llm_tools import llm_tools
from backend.agents.tools.design_tools import design_tools

logger = logging.getLogger(__name__)

class MCPOrchestrator:
    """
    The central nervous system for Sophia's AI agents.

    It manages agent sessions and funnels all tool interactions through the single,
    universal mcp_client.
    """

    def __init__(self):
        """Initializes the orchestrator."""
        self.is_initialized = False
        self.start_time: Optional[datetime] = None
        self.sessions: Dict[str, List[Dict]] = {} # Simplified session state
        logger.info("MCPOrchestrator instance created.")

    async def initialize(self):
        """Initializes the framework."""
        if self.is_initialized:
            logger.warning("Framework already initialized.")
            return

        logger.info("Initializing MCP-Native Agent Framework...")
        self.start_time = datetime.now()
        await self.initialize_tools()
        self.is_initialized = True
        logger.info("✅ MCP-Native Agent Framework Initialized Successfully.")

    async def ask_agent(self, session_id: str, request: str) -> Dict:
        """
        Primary method for interacting with an agent.
        
        Simulates the agent receiving a request and using an MCP tool to respond.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({"role": "user", "content": request})
        
        logger.info("Agent decided to use the 'pulumi' MCP service.")
        
        mcp_response = await mcp_client.get_context(
            service_name="pulumi",
            request=f"Preview the changes for the production stack based on user request: '{request}'"
        )
        
        final_answer = {
            "response": "I have initiated a preview of the infrastructure changes via the Pulumi MCP server.",
            "details_from_pulumi_mcp": mcp_response
        }
        self.sessions[session_id].append({"role": "assistant", "content": final_answer})
        return final_answer

    async def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the agent framework."""
        return {
            "is_healthy": self.is_initialized,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "active_sessions": len(self.sessions),
            "mcp_gateway_endpoints": list(MCP_GATEWAY_ENDPOINTS.keys())
        }

    async def shutdown(self):
        """Gracefully shuts down the framework."""
        logger.info("Shutting down MCP-Native Agent Framework...")
        self.is_initialized = False

    async def initialize_tools(self):
        """Loads all defined tools and registers them for agent use."""
        logger.info("Initializing and registering Agno-native tools...")
        
        all_tools = [gong_tools, hubspot_tools, custom_chunking_tools, pulumi_tools, llm_tools, design_tools]
        
        for tool_collection in all_tools:
            for tool_name, tool_func in tool_collection.items():
                self.register_tool(tool_name, tool_func)
            
        logger.info("Tool registration complete.")

    def register_tool(self, name: str, function: Coroutine):
        """Registers a single tool function in the framework."""
        if "tool_registry" not in self.__dict__:
            self.tool_registry = {}
        if name in self.tool_registry:
            logger.warning(f"Tool '{name}' is already registered. Overwriting.")
        self.tool_registry[name] = function
        logger.debug(f"Registered tool: {name}")

# Singleton instance of the framework, now renamed to reflect its purpose
agent_framework = MCPOrchestrator()
