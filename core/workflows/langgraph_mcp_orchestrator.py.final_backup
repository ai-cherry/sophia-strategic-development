"""
LangGraph MCP Orchestrator for Sophia AI
Provides intelligent routing and failover for MCP servers
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any

try:
    from langgraph.graph import END, Graph
except ImportError:
    # Fallback if LangGraph not installed
    Graph = None
    END = None

logger = logging.getLogger(__name__)


class ServerTier(Enum):
    """Server priority tiers"""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class LangGraphMCPOrchestrator:
    """Simplified but effective MCP server orchestration using LangGraph concepts"""

    def __init__(self):
        self.server_registry = self._build_server_registry()
        self.health_scores = {}
        self.last_health_check = {}

    def _build_server_registry(self) -> dict[str, dict]:
        """Registry of key MCP servers with capabilities and fallbacks"""
        return {
            # Core Intelligence
            "ai_memory": {
                "port": 9000,
                "capabilities": ["memory", "storage", "retrieval", "semantic_search"],
                "tier": ServerTier.PRIMARY,
                "contexts": ["all"],
                "fallback": "modern_stack_unified",
            },
            "modern_stack_unified": {
                "port": 8080,
                "capabilities": ["query", "analysis", "data", "business_intelligence"],
                "tier": ServerTier.PRIMARY,
                "contexts": ["business_intelligence", "ceo_deep_research"],
                "fallback": None,
            },
            "codacy": {
                "port": 3008,
                "capabilities": ["code_analysis", "security", "quality"],
                "tier": ServerTier.PRIMARY,
                "contexts": ["coding_agents", "infrastructure"],
                "fallback": "github",
            },
            "github": {
                "port": 9003,
                "capabilities": [
                    "code_analysis",
                    "project_management",
                    "version_control",
                ],
                "tier": ServerTier.SECONDARY,
                "contexts": ["coding_agents", "project_management"],
                "fallback": None,
            },
            "linear": {
                "port": 9004,
                "capabilities": [
                    "project_management",
                    "task_tracking",
                    "team_analytics",
                ],
                "tier": ServerTier.SECONDARY,
                "contexts": ["project_management", "team_performance"],
                "fallback": "github",
            },
        }

    async def route_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Main routing logic - simplified version of LangGraph workflow"""
        # Analyze request
        analysis = self._analyze_request(request)

        # Select primary server
        primary_server = await self._select_primary_server(analysis)

        # Check health
        health_status = await self._check_server_health(primary_server)

        # Execute or failover
        if health_status["healthy"]:
            result = await self._execute_request(primary_server, request)
            if result["success"]:
                return result

        # Handle failure with fallback
        fallback_server = self.server_registry[primary_server].get("fallback")
        if fallback_server:
            logger.warning(
                f"Primary server {primary_server} failed, trying fallback {fallback_server}"
            )
            result = await self._execute_request(fallback_server, request)
            result["fallback_used"] = True
            return result

        # No fallback available
        return {
            "success": False,
            "error": f"Server {primary_server} failed with no fallback available",
            "server": primary_server,
        }

    def _analyze_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Analyze incoming request for routing decisions"""
        message = request.get("message", "")
        context = request.get("context", "general")

        # Extract required capabilities from message
        capabilities = []
        message_lower = message.lower()

        if any(
            word in message_lower
            for word in ["remember", "recall", "memory", "previous"]
        ):
            capabilities.append("memory")
        if any(
            word in message_lower for word in ["code", "analyze", "security", "bug"]
        ):
            capabilities.append("code_analysis")
        if any(word in message_lower for word in ["project", "task", "team", "sprint"]):
            capabilities.append("project_management")
        if any(
            word in message_lower for word in ["data", "revenue", "sales", "customer"]
        ):
            capabilities.append("business_intelligence")

        return {
            "context": context,
            "required_capabilities": capabilities,
            "message_type": self._classify_message_type(message),
            "urgency": "high" if context == "ceo_deep_research" else "normal",
        }

    def _classify_message_type(self, message: str) -> str:
        """Classify the type of message"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["revenue", "sales", "deals"]):
            return "revenue_analysis"
        elif any(word in message_lower for word in ["code", "security", "bug"]):
            return "technical_analysis"
        elif any(word in message_lower for word in ["remember", "recall", "previous"]):
            return "memory_operation"
        else:
            return "general_query"

    async def _select_primary_server(self, analysis: dict[str, Any]) -> str:
        """Select the best server based on analysis"""
        context = analysis["context"]
        capabilities = analysis["required_capabilities"]

        # Score servers
        server_scores = {}

        for server_name, config in self.server_registry.items():
            score = 0

            # Context match (highest priority)
            if context in config["contexts"] or "all" in config["contexts"]:
                score += 50

            # Capability match
            matching_capabilities = set(capabilities) & set(config["capabilities"])
            score += len(matching_capabilities) * 20

            # Tier preference
            if config["tier"] == ServerTier.PRIMARY:
                score += 30
            elif config["tier"] == ServerTier.SECONDARY:
                score += 20

            # Health score bonus
            if server_name in self.health_scores:
                score += self.health_scores[server_name] * 10

            server_scores[server_name] = score

        # Select highest scoring server
        if server_scores:
            return max(server_scores, key=lambda x: server_scores[x])
        else:
            # Default fallback
            return "ai_memory"

    async def _check_server_health(self, server_name: str) -> dict[str, Any]:
        """Check if server is healthy (simplified)"""
        # Check if we have recent health data
        if server_name in self.last_health_check:
            last_check = self.last_health_check[server_name]
            if (datetime.now() - last_check).seconds < 30:
                # Use cached health status
                return {"healthy": self.health_scores.get(server_name, 0) > 0.5}

        # For now, assume servers are healthy
        # In production, this would make actual health checks
        self.health_scores[server_name] = 0.9
        self.last_health_check[server_name] = datetime.now()

        return {"healthy": True, "score": 0.9}

    async def _execute_request(
        self, server_name: str, request: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute request on selected server (simplified)"""
        server_config = self.server_registry.get(server_name, {})

        try:
            # In production, this would make actual MCP calls
            # For now, return mock success
            logger.info(
                f"Routing request to {server_name} on port {server_config.get('port')}"
            )

            # Simulate processing
            await asyncio.sleep(0.1)

            return {
                "success": True,
                "response": f"Processed by {server_name}",
                "server": server_name,
                "capabilities_used": server_config.get("capabilities", []),
            }

        except Exception as e:
            logger.exception(f"Error executing on {server_name}: {e}")
            return {"success": False, "error": str(e), "server": server_name}

    def get_server_info(self, server_name: str) -> dict[str, Any] | None:
        """Get information about a specific server"""
        return self.server_registry.get(server_name)

    def get_all_servers(self) -> dict[str, dict[str, Any]]:
        """Get all registered servers"""
        return self.server_registry

    def get_servers_by_capability(self, capability: str) -> list[str]:
        """Get servers that have a specific capability"""
        servers = []
        for server_name, config in self.server_registry.items():
            if capability in config.get("capabilities", []):
                servers.append(server_name)
        return servers


class SimpleOrchestrationGraph:
    """Simple orchestration workflow without LangGraph dependency"""

    def __init__(self, orchestrator: LangGraphMCPOrchestrator):
        self.orchestrator = orchestrator

    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process request through orchestration workflow"""
        start_time = datetime.now()

        try:
            # Route through orchestrator
            result = await self.orchestrator.route_request(request)

            # Add metadata
            result["orchestration_time"] = (datetime.now() - start_time).total_seconds()
            result["timestamp"] = datetime.now().isoformat()

            return result

        except Exception as e:
            logger.exception(f"Orchestration error: {e}")
            return {
                "success": False,
                "error": str(e),
                "orchestration_time": (datetime.now() - start_time).total_seconds(),
            }
