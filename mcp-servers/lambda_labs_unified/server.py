"""Unified Lambda Labs MCP server with natural language control."""

import asyncio
from typing import Optional

from mcp import Server  # type: ignore[import-not-found]
from mcp.server import Server  # type: ignore[import-not-found]
from mcp.types import TextContent, ToolResponse  # type: ignore[import-not-found]

from infrastructure.monitoring.lambda_labs_cost_monitor import LambdaLabsCostMonitor
from infrastructure.services.lambda_labs_hybrid_router import LambdaLabsHybridRouter
from infrastructure.services.lambda_labs_serverless_service import MODELS


class LambdaLabsUnifiedMCPServer:
    """MCP server for Lambda Labs with natural language commands.

    This server provides natural language tools for:
    - Invoking serverless inference
    - Estimating costs
    - Monitoring usage and budgets
    - Optimizing workloads

    All tools are designed for seamless integration with
    Sophia AI's unified chat interface.
    """

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("lambda-labs-unified")
        self.router = LambdaLabsHybridRouter()
        self.cost_monitor = LambdaLabsCostMonitor()
        self._setup_tools()

    def _setup_tools(self):
        """Register MCP tools."""

        @self.server.tool()
        async def invoke_serverless(
            prompt: str,
            model: Optional[str] = None,
            cost_priority: str = "balanced",
            max_tokens: int = 1000,
        ) -> ToolResponse:
            """Invoke Lambda Labs serverless inference with intelligent model selection.

            Args:
                prompt: The prompt to send to the model
                model: Optional specific model to use
                cost_priority: One of 'low_cost', 'balanced', 'performance', 'latency_critical'
                max_tokens: Maximum tokens to generate

            Returns:
                Model response with cost and performance metrics
            """
            messages = [{"role": "user", "content": prompt}]

            result = await self.router.generate(
                messages=messages,
                model=model,
                cost_priority=cost_priority,
                max_tokens=max_tokens,
            )

            # Extract key information
            completion = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            usage = result.get("usage", {})

            # Calculate cost
            model_used = result.get("model", "llama3.1-70b-instruct-fp8")
            tokens = usage.get("total_tokens", 0)
            cost = (tokens / 1_000_000) * MODELS[model_used]["cost_per_million"]

            response_text = f"""
**Response**: {completion}

**Metrics**:
- Model: {model_used}
- Backend: {result.get('backend', 'unknown')}
- Tokens: {tokens}
- Cost: ${cost:.4f}
- Latency: {result.get('latency_ms', 'N/A')}ms
"""

            return ToolResponse(content=[TextContent(text=response_text)])

        @self.server.tool()
        async def estimate_cost(
            prompt: str,
            model: str = "llama3.1-70b-instruct-fp8",
        ) -> ToolResponse:
            """Estimate the cost for processing a prompt with a specific model.

            Args:
                prompt: The prompt to estimate cost for
                model: The model to use for estimation

            Returns:
                Cost estimation details
            """
            # Rough token estimation (4 chars per token)
            estimated_tokens = len(prompt) // 4 + 500  # Add some for response

            if model not in MODELS:
                return ToolResponse(
                    content=[
                        TextContent(
                            text=f"Unknown model: {model}. Available models: {', '.join(MODELS.keys())}"
                        )
                    ]
                )

            cost_per_million = MODELS[model]["cost_per_million"]
            estimated_cost = (estimated_tokens / 1_000_000) * cost_per_million

            response = f"""
**Cost Estimation**:
- Model: {model}
- Estimated tokens: {estimated_tokens}
- Cost per million tokens: ${cost_per_million}
- Estimated cost: ${estimated_cost:.4f}
- Context window: {MODELS[model]['context']} tokens
"""

            return ToolResponse(content=[TextContent(text=response)])

        @self.server.tool()
        async def get_usage_stats(
            days: int = 30,
        ) -> ToolResponse:
            """Get Lambda Labs usage statistics and budget status.

            Args:
                days: Number of days to look back (default: 30)

            Returns:
                Detailed usage statistics and budget information
            """
            # Get usage stats
            stats = self.router.serverless.get_usage_stats(days=days)

            # Get budget status
            budget_status = await self.cost_monitor.check_and_alert()

            # Format response
            response = f"""
**Lambda Labs Usage Report ({days} days)**

**Budget Status**:
- Daily: ${budget_status['daily']:.2f} / ${budget_status['daily_budget']:.2f} ({budget_status['daily_percentage']:.1f}%)
- Monthly: ${budget_status['monthly']:.2f} / ${budget_status['monthly_budget']:.2f} ({budget_status['monthly_percentage']:.1f}%)

**Model Usage**:
"""

            for model, model_stats in stats.get("model_stats", {}).items():
                response += f"""
- **{model}**:
  - Requests: {model_stats['requests']}
  - Tokens: {model_stats['tokens']:,}
  - Cost: ${model_stats['cost']:.2f}
  - Avg latency: {model_stats['avg_latency_ms']:.0f}ms
  - Unique users: {model_stats['unique_users']}
"""

            if budget_status.get("alerts"):
                response += "\n**⚠️ Alerts**:\n"
                for alert in budget_status["alerts"]:
                    response += f"- {alert}\n"

            return ToolResponse(content=[TextContent(text=response)])

        @self.server.tool()
        async def optimize_costs(
            workload_description: str,
        ) -> ToolResponse:
            """Get cost optimization recommendations for a specific workload.

            Args:
                workload_description: Description of the workload to optimize

            Returns:
                Optimization recommendations with cost comparisons
            """
            # Analyze workload
            recommendations = []

            # Check for keywords
            keywords_low = ["summary", "simple", "basic", "quick"]
            keywords_high = ["complex", "detailed", "comprehensive", "analysis"]

            is_low_complexity = any(
                kw in workload_description.lower() for kw in keywords_low
            )
            is_high_complexity = any(
                kw in workload_description.lower() for kw in keywords_high
            )

            if is_low_complexity:
                recommendations.append(
                    {
                        "model": "llama3.1-8b-instruct",
                        "reason": "Low complexity task - smallest model sufficient",
                        "cost": "$0.07/1M tokens",
                        "savings": "80% vs default model",
                    }
                )
            elif is_high_complexity:
                recommendations.append(
                    {
                        "model": "llama-4-maverick-17b-128e-instruct-fp8",
                        "reason": "High complexity task - advanced model recommended",
                        "cost": "$0.88/1M tokens",
                        "savings": "Better quality despite higher cost",
                    }
                )
            else:
                recommendations.append(
                    {
                        "model": "llama3.1-70b-instruct-fp8",
                        "reason": "Balanced complexity - default model optimal",
                        "cost": "$0.35/1M tokens",
                        "savings": "Good balance of cost and performance",
                    }
                )

            response = f"""
**Cost Optimization Analysis**

Workload: "{workload_description}"

**Recommendations**:
"""

            for rec in recommendations:
                response += f"""
- **Recommended Model**: {rec['model']}
  - Reason: {rec['reason']}
  - Cost: {rec['cost']}
  - {rec['savings']}
"""

            response += """
**Additional Tips**:
- Use batch processing for large document sets
- Cache frequently requested completions
- Monitor usage patterns to identify optimization opportunities
- Consider time-of-day scheduling for non-urgent tasks
"""

            return ToolResponse(content=[TextContent(text=response)])

    async def run(self):
        """Run the MCP server."""
        async with self.server:
            await self.server.serve()


if __name__ == "__main__":
    server = LambdaLabsUnifiedMCPServer()
    asyncio.run(server.run())
