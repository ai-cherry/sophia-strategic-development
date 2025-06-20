"""Agno MCP Server
Provides MCP tools for interacting with Agno's ultra-fast agent platform
"""

import logging
from typing import Any, Dict, List

from backend.integrations.agno_integration import agno_integration
from backend.mcp.base_mcp_server import BaseMCPServer
from infrastructure.esc.agno_secrets import agno_secret_manager

logger = logging.getLogger(__name__)


class AgnoMCPServer(BaseMCPServer):
    """MCP server for Agno integration.
    Provides tools for interacting with Agno's ultra-fast agent platform.
    """

    def __init__(self):
        """Initialize the Agno MCP server."""
        super().__init__("agno")
        self.initialized = False

    async def initialize(self):
        """Initialize the Agno MCP server."""
        if self.initialized:
            return

        try:
            # Initialize Agno integration
            await agno_integration.initialize()

            # Register tools
            self.register_tool(
                "create_agent",
                self.create_agent,
                "Create a new agent in the Agno platform",
                {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The unique identifier for this agent",
                        },
                        "instructions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "The instructions for the agent",
                        },
                        "model": {
                            "type": "string",
                            "description": "The model to use for this agent",
                        },
                    },
                    "required": ["agent_id"],
                },
            )

            self.register_tool(
                "process_request",
                self.process_request,
                "Process a request with an agent",
                {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The unique identifier for the agent",
                        },
                        "request": {
                            "type": "string",
                            "description": "The request to process",
                        },
                        "stream": {
                            "type": "boolean",
                            "description": "Whether to stream the response",
                        },
                    },
                    "required": ["agent_id", "request"],
                },
            )

            self.register_tool(
                "get_pool_stats",
                self.get_pool_stats,
                "Get statistics about the agent pool",
                {"type": "object", "properties": {}},
            )

            self.register_tool(
                "register_tool",
                self.register_agno_tool,
                "Register a new tool for Agno agents",
                {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the tool",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the tool",
                        },
                        "parameters": {
                            "type": "object",
                            "description": "The parameters for the tool",
                        },
                    },
                    "required": ["name", "description", "parameters"],
                },
            )

            self.initialized = True
            logger.info("Agno MCP server initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agno MCP server: {e}")
            self.initialized = False
            raise

    async def create_agent(
        self, agent_id: str, instructions: List[str] = None, model: str = None
    ) -> Dict[str, Any]:
        """Create a new agent in the Agno platform.

        Args:
            agent_id: The unique identifier for this agent
            instructions: The instructions for the agent
            model: The model to use for this agent

        Returns:
            Dict[str, Any]: The created agent
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Create agent
            agent = await agno_integration.get_agent(
                agent_id=agent_id, instructions=instructions, model=model
            )

            # Return agent data
            return {
                "success": True,
                "agent_id": agent.agent_id,
                "created_at": agent.created_at,
                "model": agent.agent_data.get("model", "unknown"),
            }
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {e}")
            return {"success": False, "error": str(e)}

    async def process_request(
        self, agent_id: str, request: str, stream: bool = False
    ) -> Dict[str, Any]:
        """Process a request with an agent.

        Args:
            agent_id: The unique identifier for the agent
            request: The request to process
            stream: Whether to stream the response

        Returns:
            Dict[str, Any]: The response
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Process request
            if stream:
                # For streaming, we need to collect all chunks
                chunks = []
                async for chunk in agno_integration.process_request(
                    agent_id=agent_id, request=request, stream=True
                ):
                    chunks.append(chunk)

                # Return all chunks
                return {"success": True, "agent_id": agent_id, "chunks": chunks}
            else:
                # For non-streaming, we get a single response
                response = await agno_integration.process_request(
                    agent_id=agent_id, request=request, stream=False
                )

                # Return response
                return {"success": True, "agent_id": agent_id, "response": response}
        except Exception as e:
            logger.error(f"Failed to process request for agent {agent_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent pool.

        Returns:
            Dict[str, Any]: Statistics about the agent pool
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Get pool stats
            stats = agno_integration.get_pool_stats()

            # Return stats
            return {"success": True, "stats": stats}
        except Exception as e:
            logger.error(f"Failed to get pool stats: {e}")
            return {"success": False, "error": str(e)}

    async def register_agno_tool(
        self, name: str, description: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register a new tool for Agno agents.

        Args:
            name: The name of the tool
            description: The description of the tool
            parameters: The parameters for the tool

        Returns:
            Dict[str, Any]: The result of the registration
        """
        if not self.initialized:
            await self.initialize()

        try:
            # This is a placeholder for registering custom tools
            # In a real implementation, we would register the tool with Agno

            # Return success
            return {
                "success": True,
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        except Exception as e:
            logger.error(f"Failed to register tool {name}: {e}")
            return {"success": False, "error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check.

        Returns:
            Dict[str, Any]: The health check result
        """
        try:
            # Check if Agno integration is initialized
            if not agno_integration.initialized:
                await agno_integration.initialize()

            # Get API key (without logging it)
            api_key = await agno_secret_manager.get_agno_api_key()
            has_api_key = api_key is not None and len(api_key) > 0

            # Get pool stats
            stats = agno_integration.get_pool_stats()

            # Return health check result
            return {
                "status": "healthy",
                "initialized": self.initialized,
                "integration_initialized": agno_integration.initialized,
                "has_api_key": has_api_key,
                "agent_count": stats["pool_size"],
                "max_agent_count": stats["max_pool_size"],
                "default_model": agno_integration.default_model,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Create server instance
server = AgnoMCPServer()
