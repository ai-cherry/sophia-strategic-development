"""Agno-MCP Bridge for Sophia AI Platform.

Seamless integration between Agno framework's high-performance agents
and Sophia's existing MCP (Model Context Protocol) tool ecosystem.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Union

from agno.agent import Agent
from agno.knowledge.vector import PineconeKnowledge, VectorKnowledge, WeaviateKnowledge
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.storage.memory.postgres import PgMemoryDb

from backend.agents.core.agent_framework import agent_framework
from backend.core.auto_esc_config import config
from backend.mcp.mcp_client import mcp_client
from backend.mcp.unified_mcp_servers import MCP_SERVERS

logger = logging.getLogger(__name__)


class AgnoMCPBridge:
    """Bridge between Agno agents and MCP tool ecosystem.

    This bridge enables Agno agents to seamlessly use existing MCP services
    while maintaining their performance characteristics (~3μs instantiation).
    """

    def __init__(self):
        self.mcp_client = mcp_client
        self.agent_framework = agent_framework
        self.mcp_tools_cache: Dict[str, Callable] = {}
        self.performance_metrics: Dict[str, Any] = {}

    async def initialize(self):
        """Initialize the bridge and cache MCP tool wrappers."""
        logger.info("Initializing Agno-MCP Bridge...")

        # Pre-create tool wrappers for all MCP services
        for server_name, server_config in MCP_SERVERS.items():
            for service in server_config.get("services", []):
                tool_wrapper = await self._create_mcp_tool_wrapper(service)
                self.mcp_tools_cache[service] = tool_wrapper

        logger.info(f"Cached {len(self.mcp_tools_cache)} MCP tool wrappers")

    async def create_agno_agent_with_mcp_tools(
        self,
        agent_name: str,
        agent_config: Dict[str, Any],
        mcp_services: List[str]
    ) -> Agent:
        """Create high-performance Agno agent with MCP tool access.

        Args:
            agent_name: Name of the agent
            agent_config: Agent configuration including model, memory, etc.
            mcp_services: List of MCP services to integrate

        Returns:
            Configured Agno agent with MCP tool access
        """
        logger.info(f"Creating Agno agent '{agent_name}' with MCP services: {mcp_services}")

        # Get MCP tools for this agent
        mcp_tools = []
        for service in mcp_services:
            if service in self.mcp_tools_cache:
                mcp_tools.append(self.mcp_tools_cache[service])
            else:
                # Create tool wrapper on-demand if not cached
                tool_wrapper = await self._create_mcp_tool_wrapper(service)
                self.mcp_tools_cache[service] = tool_wrapper
                mcp_tools.append(tool_wrapper)

        # Configure model based on agent config
        model = self._create_model(agent_config.get("model", {}))

        # Configure memory if specified
        memory = None
        if agent_config.get("use_memory", False):
            memory = PgMemoryDb(
                table_name=f"{agent_name}_memory",
                db_url=config.get("POSTGRES_URL")
            )

        # Configure knowledge base if specified
        knowledge = None
        if agent_config.get("use_knowledge", False):
            knowledge = self._create_knowledge_base(agent_config)

        # Create Agno agent with optimal configuration
        agent = Agent(
            name=agent_name,
            model=model,
            tools=mcp_tools,
            memory=memory,
            knowledge=knowledge,
            instructions=self._generate_instructions(agent_name, agent_config, mcp_services),
            session_state=agent_config.get("session_state", {}),
            show_tool_calls=agent_config.get("show_tool_calls", True),
            markdown=agent_config.get("markdown", True),
            add_state_in_messages=agent_config.get("add_state_in_messages", True)
        )

        # Track agent creation metrics
        self.performance_metrics[agent_name] = {
            "created_at": asyncio.get_event_loop().time(),
            "mcp_services": mcp_services,
            "memory_enabled": memory is not None,
            "knowledge_enabled": knowledge is not None
        }

        logger.info(f"Created Agno agent '{agent_name}' successfully")
        return agent

    async def _create_mcp_tool_wrapper(self, service_name: str) -> Callable:
        """Create optimized tool wrapper for MCP service.

        Args:
            service_name: Name of the MCP service

        Returns:
            Async callable tool function
        """
        async def mcp_tool(request: str, **kwargs) -> str:
            """Optimized MCP tool wrapper with error handling and caching"""
            try:
                # Use existing MCP client for service communication
                response = await self.mcp_client.get_context(
                    service_name=service_name,
                    request=request,
                    **kwargs
                )

                # Track tool usage metrics
                if service_name not in self.performance_metrics:
                    self.performance_metrics[service_name] = {"calls": 0, "errors": 0}
                self.performance_metrics[service_name]["calls"] += 1

                return response

            except Exception as e:
                logger.error(f"MCP tool error for {service_name}: {e}")

                # Track error metrics
                if service_name not in self.performance_metrics:
                    self.performance_metrics[service_name] = {"calls": 0, "errors": 0}
                self.performance_metrics[service_name]["errors"] += 1

                # Return graceful error response
                return f"Error accessing {service_name}: {str(e)}"

        # Set function metadata for Agno
        mcp_tool.__name__ = f"mcp_{service_name}"
        mcp_tool.__doc__ = f"Access {service_name} service via MCP"

        return mcp_tool

    def _create_model(self, model_config: Dict[str, Any]) -> Union[Claude, OpenAIChat]:
        """Create optimized model instance based on configuration."""
        model_type = model_config.get("type", "claude")

        if model_type == "claude":
            return Claude(
                id=model_config.get("id", "claude-sonnet-4-20250514"),
                api_key=config.get("ANTHROPIC_API_KEY")
            )
        elif model_type == "openai":
            return OpenAIChat(
                id=model_config.get("id", "gpt-4o"),
                api_key=config.get("OPENAI_API_KEY")
            )
        else:
            logger.warning(f"Unknown model type: {model_type}, defaulting to Claude")
            return Claude(id="claude-sonnet-4-20250514")

    def _create_knowledge_base(self, agent_config: Dict[str, Any]) -> Optional[VectorKnowledge]:
        """Create knowledge base based on configuration."""
        kb_config = agent_config.get("knowledge", {})
        kb_type = kb_config.get("type", "weaviate")

        if kb_type == "weaviate":
            return WeaviateKnowledge(
                schema=kb_config.get("schema", {}),
                num_documents=kb_config.get("num_documents", 10)
            )
        elif kb_type == "pinecone":
            return PineconeKnowledge(
                index_name=kb_config.get("index_name", "sophia-knowledge"),
                num_documents=kb_config.get("num_documents", 10)
            )

        return None

    def _generate_instructions(
        self,
        agent_name: str,
        agent_config: Dict[str, Any],
        mcp_services: List[str]
    ) -> str:
        """Generate optimized instructions for the agent."""
        base_instructions = agent_config.get("instructions", "")

        agno_instructions = f"""
You are {agent_name}, enhanced with Agno framework for maximum performance.

Core Capabilities:
- Instantiation time: ~3μs (ultra-fast response)
- Memory usage: ~6.5KiB (highly efficient)
- Access to MCP services: {', '.join(mcp_services)}

Performance Guidelines:
- Prioritize speed and efficiency in all responses
- Use MCP tools when external data is needed
- Maintain context across conversations
- Provide actionable business intelligence insights

{base_instructions}
        """.strip()

        return agno_instructions

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        return {
            "cached_tools": len(self.mcp_tools_cache),
            "agent_metrics": self.performance_metrics,
            "bridge_status": "active"
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the bridge."""
        try:
            # Test MCP client connectivity
            mcp_health = await self.mcp_client.health_check() if hasattr(self.mcp_client, 'health_check') else True

            return {
                "status": "healthy",
                "mcp_client_status": "connected" if mcp_health else "disconnected",
                "cached_tools": len(self.mcp_tools_cache),
                "performance_tracking": bool(self.performance_metrics)
            }
        except Exception as e:
            logger.error(f"Bridge health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global bridge instance
agno_mcp_bridge = AgnoMCPBridge()


async def initialize_bridge():
    """Initialize the global Agno-MCP bridge."""
    await agno_mcp_bridge.initialize()
    logger.info("Agno-MCP Bridge initialized successfully")


# Convenience functions
async def create_hybrid_agent(
    agent_name: str,
    agent_config: Dict[str, Any],
    mcp_services: List[str]
) -> Agent:
    """Create hybrid Agno agent with MCP integration."""
    return await agno_mcp_bridge.create_agno_agent_with_mcp_tools(
        agent_name, agent_config, mcp_services
    )


async def get_bridge_metrics() -> Dict[str, Any]:
    """Get bridge performance metrics."""
    return await agno_mcp_bridge.get_performance_metrics()
