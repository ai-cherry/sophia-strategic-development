"""
Unified AI MCP Server
Natural language infrastructure control with unified AI service integration
"""

import asyncio
import json
import logging
from typing import Any

from mcp import McpTool
from mcp_servers.base.unified_mcp_base import (
    AIEngineMCPServer,
    MCPServerConfig,
)

from infrastructure.services.unified_ai_orchestrator import (
    AIProvider,
    AIRequest,
    UnifiedAIOrchestrator,
)

logger = logging.getLogger(__name__)


class UnifiedAIMCPServer(AIEngineMCPServer):
    """
    MCP Server for unified AI operations
    Provides natural language control over Snowflake Cortex and Lambda Labs
    """

    def __init__(self):
        config = MCPServerConfig(name="unified-ai", port=9000, version="2.0.0")
        super().__init__(config)
        self.orchestrator = UnifiedAIOrchestrator()
        self.tools = self._register_tools()

    def _register_tools(self) -> list[McpTool]:
        """Register MCP tools"""
        return [
            McpTool(
                name="ai_complete",
                description="Complete text using unified AI with intelligent routing",
                parameters={
                    "prompt": {"type": "string", "required": True},
                    "provider": {
                        "type": "string",
                        "enum": ["auto", "snowflake", "lambda"],
                        "default": "auto",
                    },
                    "model": {"type": "string", "required": False},
                    "max_tokens": {"type": "integer", "default": 1000},
                    "temperature": {"type": "number", "default": 0.7},
                    "cost_priority": {
                        "type": "string",
                        "enum": ["cost", "performance", "balanced"],
                        "default": "balanced",
                    },
                    "use_case": {"type": "string", "default": "general"},
                },
                handler=self.ai_complete,
            ),
            McpTool(
                name="ai_optimize",
                description="Optimize AI infrastructure using natural language",
                parameters={"command": {"type": "string", "required": True}},
                handler=self.ai_optimize,
            ),
            McpTool(
                name="ai_health",
                description="Check health of unified AI services",
                parameters={},
                handler=self.ai_health,
            ),
            McpTool(
                name="ai_analytics",
                description="Get AI usage analytics and cost analysis",
                parameters={},
                handler=self.ai_analytics,
            ),
            McpTool(
                name="sql_generation",
                description="Generate SQL from natural language",
                parameters={
                    "query": {"type": "string", "required": True},
                    "schema_context": {"type": "string", "required": False},
                },
                handler=self.sql_generation,
            ),
            McpTool(
                name="embedding_generation",
                description="Generate embeddings using Snowflake Cortex",
                parameters={
                    "text": {"type": "string", "required": True},
                    "model": {"type": "string", "default": "e5-base-v2"},
                },
                handler=self.embedding_generation,
            ),
        ]

    async def ai_complete(
        self,
        prompt: str,
        provider: str = "auto",
        model: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        cost_priority: str = "balanced",
        use_case: str = "general",
        **kwargs,
    ) -> dict[str, Any]:
        """Complete text using unified AI service"""

        try:
            # Map provider string to enum
            provider_map = {
                "auto": AIProvider.AUTO,
                "snowflake": AIProvider.SNOWFLAKE_CORTEX,
                "lambda": AIProvider.LAMBDA_LABS,
            }
            provider_enum = provider_map.get(provider, AIProvider.AUTO)

            # Create unified request
            request = AIRequest(
                prompt=prompt,
                provider=provider_enum,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                cost_priority=cost_priority,
                use_case=use_case,
            )

            # Process through orchestrator
            response = await self.orchestrator.process_request(request)

            return {
                "success": response.success,
                "response": response.response,
                "provider": response.provider,
                "model": response.model,
                "duration": response.duration,
                "cost_estimate": response.cost_estimate,
                "usage": response.usage,
                "error": response.error,
            }

        except Exception as e:
            logger.error(f"AI completion error: {e!s}")
            return {"success": False, "error": str(e)}

    async def ai_optimize(self, command: str) -> dict[str, Any]:
        """Optimize AI infrastructure using natural language"""

        try:
            result = await self.orchestrator.natural_language_optimization(command)

            return {"success": True, "command": command, "optimization_result": result}

        except Exception as e:
            logger.error(f"AI optimization error: {e!s}")
            return {"success": False, "error": str(e)}

    async def ai_health(self) -> dict[str, Any]:
        """Check health of unified AI services"""

        try:
            health = await self.orchestrator.health_check()

            return {"success": True, "health": health}

        except Exception as e:
            logger.error(f"Health check error: {e!s}")
            return {"success": False, "error": str(e)}

    async def ai_analytics(self) -> dict[str, Any]:
        """Get AI usage analytics"""

        try:
            analytics = await self.orchestrator.get_usage_analytics()
            performance = self.orchestrator.get_performance_summary()

            return {"success": True, "analytics": analytics, "performance": performance}

        except Exception as e:
            logger.error(f"Analytics error: {e!s}")
            return {"success": False, "error": str(e)}

    async def sql_generation(
        self, query: str, schema_context: str | None = None
    ) -> dict[str, Any]:
        """Generate SQL from natural language"""

        try:
            # Create request specifically for SQL generation
            request = AIRequest(
                prompt=query,
                provider=AIProvider.SNOWFLAKE_CORTEX,  # Prefer Snowflake for SQL
                use_case="sql",
                context={"schema": schema_context} if schema_context else None,
            )

            response = await self.orchestrator.process_request(request)

            return {
                "success": response.success,
                "natural_language": query,
                "generated_sql": response.response,
                "provider": response.provider,
                "error": response.error,
            }

        except Exception as e:
            logger.error(f"SQL generation error: {e!s}")
            return {"success": False, "error": str(e)}

    async def embedding_generation(
        self, text: str, model: str = "e5-base-v2"
    ) -> dict[str, Any]:
        """Generate embeddings using Snowflake Cortex"""

        try:
            # Create request specifically for embeddings
            request = AIRequest(
                prompt=text,
                provider=AIProvider.SNOWFLAKE_CORTEX,  # Always use Snowflake for embeddings
                model=model,
                use_case="embedding",
            )

            response = await self.orchestrator.process_request(request)

            # Parse embedding from response
            try:
                embedding = json.loads(response.response)
            except:
                embedding = response.response

            return {
                "success": response.success,
                "text": text,
                "embedding": embedding,
                "model": model,
                "provider": response.provider,
                "error": response.error,
            }

        except Exception as e:
            logger.error(f"Embedding generation error: {e!s}")
            return {"success": False, "error": str(e)}

    async def initialize(self):
        """Initialize the MCP server"""
        logger.info("Initializing Unified AI MCP Server")

        # Check health on startup
        health = await self.ai_health()

        if health["success"]:
            logger.info(
                f"Unified AI MCP Server initialized - Status: {health['health']['orchestrator']}"
            )
        else:
            logger.error(f"Failed to initialize: {health['error']}")

    async def shutdown(self):
        """Shutdown the MCP server"""
        logger.info("Shutting down Unified AI MCP Server")

        # Get final analytics
        analytics = await self.ai_analytics()

        if analytics["success"]:
            logger.info(
                f"Final usage stats: {analytics['analytics']['total_requests']} requests processed"
            )


# MCP Server entry point
async def main():
    """Run the MCP server"""
    server = UnifiedAIMCPServer()
    await server.initialize()

    # Run server (implementation depends on MCP framework)
    # This is a placeholder - actual implementation would use MCP server framework
    logger.info("Unified AI MCP Server running on port 9050")

    try:
        # Keep server running
        while True:
            await asyncio.sleep(60)

            # Periodic health check
            health = await server.ai_health()
            logger.info(
                f"Health check: {health['health']['orchestrator'] if health['success'] else 'failed'}"
            )

    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await server.shutdown()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    asyncio.run(main())
