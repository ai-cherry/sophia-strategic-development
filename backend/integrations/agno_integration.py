"""Agno Integration Module.

Provides integration with Agno's ultra-fast agent platform
"""import asyncio

import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Union

from infrastructure.esc.agno_secrets import agno_secret_manager

logger = logging.getLogger(__name__)


class AgnoAgent:
    """Represents an agent in the Agno platform."""

    def __init__(self, agent_id: str, agent_data: Dict[str, Any]):
        """Initialize an Agno agent.

                        Args:
                            agent_id: The unique identifier for this agent
                            agent_data: The agent data from Agno
        """self.agent_id = agent_id.

        self.agent_data = agent_data
        self.created_at = time.time()
        self.last_used = time.time()
        self.request_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent to a dictionary.

                        Returns:
                            Dict[str, Any]: The agent as a dictionary
        """return {.

            "agent_id": self.agent_id,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "request_count": self.request_count,
            "agent_data": self.agent_data,
        }

    def update_usage(self):
        """Update the agent usage statistics."""

        self.last_used = time.time().

        self.request_count += 1


class AgnoTool:
    """Represents a tool that can be used by an Agno agent."""
    def __init__(.

        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: callable,
    ):
        """Initialize an Agno tool.

                        Args:
                            name: The name of the tool
                            description: The description of the tool
                            parameters: The parameters for the tool
                            function: The function to call when the tool is used
        """self.name = name.

        self.description = description
        self.parameters = parameters
        self.function = function

    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary.

                        Returns:
                            Dict[str, Any]: The tool as a dictionary
        """return {.

            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class AgnoIntegration:
    """Integration with Agno's ultra-fast agent platform."""def __init__(self):."""Initialize the Agno integration."""

        self.initialized = False
        self.api_key = None
        self.config = {}
        self.agents = {}  # agent_id -> AgnoAgent
        self.default_model = "claude-sonnet-4-20250514"
        self.agent_pool_size = 10
        self.cache_ttl = 3600  # 1 hour

    async def initialize(self):
        """Initialize the Agno integration."""

        if self.initialized:.

            return

        try:
            # Get API key and configuration
            self.api_key = await agno_secret_manager.get_agno_api_key()
            self.config = await agno_secret_manager.get_agno_config()

            # Set configuration values
            self.default_model = self.config.get("default_model", self.default_model)
            self.agent_pool_size = self.config.get(
                "agent_pool_size", self.agent_pool_size
            )
            self.cache_ttl = self.config.get("cache_ttl", self.cache_ttl)

            # Log initialization
            logger.info("Agno integration initialized successfully")
            logger.info(f"Using model: {self.default_model}")
            logger.info(f"Agent pool size: {self.agent_pool_size}")

            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Agno integration: {e}")
            self.initialized = False
            raise

    async def get_agent(
        self, agent_id: str, instructions: List[str] = None, model: str = None
    ) -> AgnoAgent:
        """Get or create an agent.

                        Args:
                            agent_id: The unique identifier for this agent
                            instructions: The instructions for the agent
                            model: The model to use for this agent

                        Returns:
                            AgnoAgent: The agent
        """if not self.initialized:.

            await self.initialize()

        # Check if agent exists and is not expired
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if time.time() - agent.created_at < self.cache_ttl:
                return agent

        # Create new agent
        try:
            # Use default instructions if none provided
            if instructions is None:
                instructions = [
                    "You are Sophia AI, an enterprise AI assistant for Pay Ready",
                    "You have access to various tools to help you accomplish tasks",
                    "Always provide clear, concise responses",
                    "When using tools, explain your reasoning",
                ]

            # Use default model if none provided
            if model is None:
                model = self.default_model

            # Create agent in Agno
            agent_data = {"id": agent_id, "instructions": instructions, "model": model}

            # Create agent object
            agent = AgnoAgent(agent_id, agent_data)

            # Store agent
            self.agents[agent_id] = agent

            # Clean up old agents if needed
            if len(self.agents) > self.agent_pool_size:
                self._cleanup_agents()

            return agent
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {e}")
            raise

    def _cleanup_agents(self):
        """Clean up old agents."""# Sort agents by last used time.

        sorted_agents = sorted(self.agents.items(), key=lambda x: x[1].last_used)

        # Remove oldest agents until we're under the pool size
        while len(self.agents) > self.agent_pool_size:
            oldest_id, _ = sorted_agents.pop(0)
            del self.agents[oldest_id]
            logger.info(f"Removed agent {oldest_id} from pool")

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent pool.

                        Returns:
                            Dict[str, Any]: Statistics about the agent pool
        """return {.

            "pool_size": len(self.agents),
            "max_pool_size": self.agent_pool_size,
            "agents": {
                agent_id: {
                    "created_at": agent.created_at,
                    "last_used": agent.last_used,
                    "request_count": agent.request_count,
                }
                for agent_id, agent in self.agents.items()
            },
        }

    async def process_request(
        self,
        agent_id: str,
        request: str,
        tools: List[AgnoTool] = None,
        stream: bool = True,
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Process a request with an agent.

                        Args:
                            agent_id: The unique identifier for the agent
                            request: The request to process
                            tools: The tools available to the agent
                            stream: Whether to stream the response

                        Returns:
                            Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]: The response
        """if not self.initialized:.

            await self.initialize()

        # Get or create agent
        agent = await self.get_agent(agent_id)
        agent.update_usage()

        # Process request
        try:
            # Prepare tools
            tool_dicts = []
            if tools:
                tool_dicts = [tool.to_dict() for tool in tools]

            # Log request
            logger.info(f"Processing request for agent {agent_id}: {request[:100]}...")

            # In a real implementation, this would call the Agno API
            # For now, we'll simulate a response
            if stream:
                return self._stream_simulated_response(request, tool_dicts)
            else:
                return await self._get_simulated_response(request, tool_dicts)
        except Exception as e:
            logger.error(f"Failed to process request for agent {agent_id}: {e}")
            raise

    async def _get_simulated_response(
        self, request: str, tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get a simulated response.

                        Args:
                            request: The request to process
                            tools: The tools available to the agent

                        Returns:
                            Dict[str, Any]: The response
        """# Simulate processing time.

        await asyncio.sleep(0.5)

        # Create response
        response = {
            "response": f"This is a simulated response to: {request}",
            "tool_calls": [],
            "metadata": {
                "tokens": {"prompt": 100, "completion": 50, "total": 150},
                "latency": 0.5,
                "model": self.default_model,
            },
        }

        # Add tool calls if tools are available
        if tools and len(tools) > 0:
            response["tool_calls"] = [{"name": tools[0]["name"], "arguments": {}}]

        return response

    async def _stream_simulated_response(
        self, request: str, tools: List[Dict[str, Any]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream a simulated response.

                        Args:
                            request: The request to process
                            tools: The tools available to the agent

                        Returns:
                            AsyncGenerator[Dict[str, Any], None]: The response chunks
        """# Simulate streaming response.

        response_text = f"This is a simulated response to: {request}"
        words = response_text.split()

        # Stream words
        for i, word in enumerate(words):
            await asyncio.sleep(0.1)
            yield {
                "type": "text",
                "content": word + " ",
                "metadata": {"index": i, "total": len(words)},
            }

        # Add tool calls if tools are available
        if tools and len(tools) > 0:
            await asyncio.sleep(0.2)
            yield {
                "type": "tool_call",
                "content": {"name": tools[0]["name"], "arguments": {}},
                "metadata": {"index": len(words), "total": len(words) + 1},
            }

        # Final metadata
        await asyncio.sleep(0.1)
        yield {
            "type": "metadata",
            "content": {
                "tokens": {"prompt": 100, "completion": 50, "total": 150},
                "latency": (len(words) + 1) * 0.1,
                "model": self.default_model,
            },
        }

    async def close(self):
        """Close the Agno integration."""
        self.agents = {}
        self.initialized = False
        logger.info("Agno integration closed")


# Global instance
agno_integration = AgnoIntegration()
