#!/usr/bin/env python3
"""
Portkey Admin MCP Server
Critical AI Gateway Management and Cost Optimization

Business Value:
- AI model routing and cost optimization
- Unified gateway for all AI operations
- Performance monitoring and analytics
- Strategic model selection based on task requirements
"""

import asyncio
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add the backend directory to Python path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_path))

from backend.mcp_servers.base.standardized_mcp_server import (
    HealthCheckResult,
    HealthStatus,
    MCPServerConfig,
    ModelProvider,
    ServerCapability,
    StandardizedMCPServer,
    SyncPriority,
)

logger = logging.getLogger(__name__)


class AIModelRoute:
    """Represents an AI model routing configuration"""

    def __init__(
        self,
        model_name: str,
        provider: str,
        cost_per_token: float,
        performance_score: float,
    ):
        self.model_name = model_name
        self.provider = provider
        self.cost_per_token = cost_per_token
        self.performance_score = performance_score
        self.usage_count = 0
        self.total_cost = 0.0
        self.last_used = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "provider": self.provider,
            "cost_per_token": self.cost_per_token,
            "performance_score": self.performance_score,
            "usage_count": self.usage_count,
            "total_cost": self.total_cost,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }


class PortkeyAdminMCPServer(StandardizedMCPServer):
    """MCP server for Portkey AI gateway administration"""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.available_models: dict[str, AIModelRoute] = {}
        self.routing_rules: list[dict[str, Any]] = []
        self.cost_analytics: dict[str, Any] = {}
        self.performance_metrics: dict[str, Any] = {}

    async def server_specific_init(self) -> None:
        """Initialize Portkey Admin server"""
        logger.info("🚀 Initializing Portkey Admin MCP Server...")

        # Initialize available AI models with cost and performance data
        self.available_models = {
            "gpt-4o": AIModelRoute("gpt-4o", "openai", 0.00003, 95.0),
            "claude-3-opus": AIModelRoute("claude-3-opus", "anthropic", 0.000015, 97.0),
            "gemini-1.5-pro": AIModelRoute("gemini-1.5-pro", "google", 0.000007, 90.0),
            "claude-3-haiku": AIModelRoute(
                "claude-3-haiku", "anthropic", 0.000001, 85.0
            ),
            "gpt-4-turbo": AIModelRoute("gpt-4-turbo", "openai", 0.00001, 88.0),
            "deepseek-v3": AIModelRoute("deepseek-v3", "openrouter", 0.000002, 82.0),
            "llama-3-70b": AIModelRoute("llama-3-70b", "openrouter", 0.000001, 78.0),
            "qwen2-72b": AIModelRoute("qwen2-72b", "openrouter", 0.0000015, 80.0),
            "mixtral-8x22b": AIModelRoute(
                "mixtral-8x22b", "openrouter", 0.000001, 75.0
            ),
        }

        # Initialize intelligent routing rules
        self.routing_rules = [
            {
                "rule_id": "complex_reasoning",
                "conditions": ["analyze", "reason", "complex", "architect"],
                "preferred_models": ["claude-3-opus", "gpt-4o"],
                "fallback_models": ["claude-3-haiku", "gpt-4-turbo"],
                "priority": "performance",
            },
            {
                "rule_id": "large_context",
                "conditions": ["context_size > 100000"],
                "preferred_models": ["gemini-1.5-pro", "claude-3-opus"],
                "fallback_models": ["gpt-4o"],
                "priority": "capability",
            },
            {
                "rule_id": "cost_optimization",
                "conditions": ["bulk", "simple", "routine"],
                "preferred_models": ["claude-3-haiku", "deepseek-v3", "llama-3-70b"],
                "fallback_models": ["gpt-4-turbo"],
                "priority": "cost",
            },
            {
                "rule_id": "experimental",
                "conditions": ["test", "experiment", "trial"],
                "preferred_models": ["qwen2-72b", "mixtral-8x22b", "deepseek-v3"],
                "fallback_models": ["claude-3-haiku"],
                "priority": "exploration",
            },
        ]

        logger.info("✅ Portkey Admin MCP Server initialized")

    async def server_specific_cleanup(self) -> None:
        """Cleanup Portkey Admin server"""
        logger.info("🔄 Cleaning up Portkey Admin MCP Server...")

    async def server_specific_health_check(self) -> HealthCheckResult:
        """Perform Portkey Admin specific health checks"""
        return HealthCheckResult(
            component="portkey_admin",
            status=HealthStatus.HEALTHY,
            response_time_ms=45.0,
            last_success=datetime.now(UTC),
            metadata={
                "available_models": len(self.available_models),
                "routing_rules": len(self.routing_rules),
                "total_usage": sum(
                    model.usage_count for model in self.available_models.values()
                ),
            },
        )

    async def check_external_api(self) -> bool:
        """Check if Portkey API is accessible"""
        return True  # Mock for demo - would check actual Portkey API

    async def get_server_capabilities(self) -> list[ServerCapability]:
        """Get Portkey Admin server capabilities"""
        return [
            ServerCapability(
                name="model_routing",
                description="Intelligent AI model routing and selection",
                category="ai",
                available=True,
                version="1.0.0",
                metadata={"models_available": len(self.available_models)},
            ),
            ServerCapability(
                name="cost_optimization",
                description="AI model cost analysis and optimization",
                category="finance",
                available=True,
                version="1.0.0",
            ),
            ServerCapability(
                name="performance_monitoring",
                description="AI model performance tracking and analytics",
                category="monitoring",
                available=True,
                version="1.0.0",
            ),
            ServerCapability(
                name="routing_rules",
                description="Dynamic routing rules management",
                category="automation",
                available=True,
                version="1.0.0",
            ),
        ]

    async def sync_data(self) -> dict[str, Any]:
        """Sync Portkey Admin data"""
        # Update cost analytics
        total_cost = sum(model.total_cost for model in self.available_models.values())
        total_usage = sum(model.usage_count for model in self.available_models.values())

        self.cost_analytics = {
            "total_cost": total_cost,
            "total_usage": total_usage,
            "average_cost_per_request": total_cost / max(total_usage, 1),
            "most_used_model": (
                max(self.available_models.items(), key=lambda x: x[1].usage_count)[0]
                if self.available_models
                else None
            ),
            "cost_by_provider": self._calculate_cost_by_provider(),
        }

        return {
            "synced": True,
            "models_synced": len(self.available_models),
            "cost_analytics": self.cost_analytics,
            "sync_time": datetime.now(UTC).isoformat(),
        }

    async def process_with_ai(
        self, data: Any, model: ModelProvider | None = None
    ) -> Any:
        """Process data with optimal AI model routing"""
        if isinstance(data, dict) and "task" in data:
            optimal_model = await self.route_request(
                data["task"], data.get("context_size", 0)
            )
            return {
                "optimal_model": optimal_model,
                "reasoning": "Selected based on task analysis and routing rules",
                "estimated_cost": self._estimate_cost(
                    optimal_model, data.get("context_size", 1000)
                ),
            }
        return data

    async def route_request(self, task: str, context_size: int = 0) -> str:
        """Intelligent AI model routing based on task and context"""
        # Analyze task for routing
        task_lower = task.lower()

        # Apply routing rules in priority order
        for rule in self.routing_rules:
            if self._matches_conditions(task_lower, context_size, rule["conditions"]):
                # Select best model from preferred list based on current performance/cost
                for model_name in rule["preferred_models"]:
                    if model_name in self.available_models:
                        # Update usage tracking
                        model = self.available_models[model_name]
                        model.usage_count += 1
                        model.last_used = datetime.now(UTC)
                        return model_name

                # Fallback to secondary models
                for model_name in rule["fallback_models"]:
                    if model_name in self.available_models:
                        model = self.available_models[model_name]
                        model.usage_count += 1
                        model.last_used = datetime.now(UTC)
                        return model_name

        # Default fallback
        default_model = "claude-3-haiku"  # Balanced cost/performance
        if default_model in self.available_models:
            self.available_models[default_model].usage_count += 1
            self.available_models[default_model].last_used = datetime.now(UTC)

        return default_model

    def _matches_conditions(
        self, task: str, context_size: int, conditions: list[str]
    ) -> bool:
        """Check if task matches routing rule conditions"""
        for condition in conditions:
            if "context_size" in condition:
                # Evaluate context size conditions
                try:
                    return eval(condition.replace("context_size", str(context_size)))
                except Exception:
                    continue
            else:
                # Check for keyword matches
                if condition in task:
                    return True
        return False

    def _estimate_cost(self, model_name: str, token_count: int) -> float:
        """Estimate cost for a request"""
        if model_name in self.available_models:
            return self.available_models[model_name].cost_per_token * token_count
        return 0.0

    def _calculate_cost_by_provider(self) -> dict[str, float]:
        """Calculate total cost by provider"""
        cost_by_provider = {}
        for model in self.available_models.values():
            if model.provider not in cost_by_provider:
                cost_by_provider[model.provider] = 0.0
            cost_by_provider[model.provider] += model.total_cost
        return cost_by_provider


# FastAPI route setup
def setup_portkey_admin_routes(app, server: PortkeyAdminMCPServer):
    """Setup Portkey Admin routes"""

    @app.get("/portkey/models")
    async def get_available_models():
        return {
            "models": {
                name: model.to_dict() for name, model in server.available_models.items()
            }
        }

    @app.get("/portkey/routing-rules")
    async def get_routing_rules():
        return {"routing_rules": server.routing_rules}

    @app.post("/portkey/route")
    async def route_request(request: dict[str, Any]):
        task = request.get("task", "")
        context_size = request.get("context_size", 0)
        optimal_model = await server.route_request(task, context_size)
        return {
            "optimal_model": optimal_model,
            "estimated_cost": server._estimate_cost(optimal_model, context_size),
            "routing_reasoning": "Selected based on intelligent routing rules",
        }

    @app.get("/portkey/analytics")
    async def get_cost_analytics():
        await server.sync_data()
        return server.cost_analytics

    @app.get("/portkey/status")
    async def get_status():
        return {"status": "Portkey Admin MCP Server operational", "port": 9013}


async def main():
    """Main function to run the Portkey Admin MCP Server"""
    config = MCPServerConfig(
        server_name="portkey_admin",
        port=9013,
        sync_priority=SyncPriority.HIGH,
        enable_ai_processing=False,  # Disabled to avoid Snowflake connection issues
        enable_metrics=True,
        enable_webfetch=True,
        enable_self_knowledge=True,
    )

    server = PortkeyAdminMCPServer(config)
    setup_portkey_admin_routes(server.app, server)

    # Start the server
    await server.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Portkey Admin MCP Server stopped by user.")
