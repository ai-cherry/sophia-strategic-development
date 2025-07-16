#!/usr/bin/env python3
"""
Sophia AI OpenRouter Search MCP Server
Provides AI model discovery and selection
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import sys
from pathlib import Path
from typing import Any, Optional

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

import httpx
from base.unified_standardized_base import (
    ServerConfig,
    ToolDefinition,
    ToolParameter,
)
from base.unified_standardized_base import (
    UnifiedStandardizedMCPServer as StandardizedMCPServer,
)

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class OpenRouterSearchMCPServer(StandardizedMCPServer):
    """OpenRouter Search MCP Server for AI model discovery"""

    def __init__(self):
        config = ServerConfig(
            name="openrouter_search",
            version="1.0.0",
            port=9015,
            capabilities=["MODEL_SEARCH", "MODEL_COMPARISON", "COST_ANALYSIS"],
            tier="SECONDARY",
        )
        super().__init__(config)

        # OpenRouter configuration
        self.api_key = get_config_value("openrouter_api_key")
        self.api_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sophia-ai.com",
            "X-Title": "Sophia AI",
        }

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define OpenRouter Search tools"""
        return [
            ToolDefinition(
                name="search_models",
                description="Search for AI models by capabilities or requirements",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="Search query (e.g., 'code generation', 'vision')",
                        required=True,
                    ),
                    ToolParameter(
                        name="max_cost",
                        type="number",
                        description="Maximum cost per 1k tokens",
                        required=False,
                    ),
                    ToolParameter(
                        name="min_context",
                        type="number",
                        description="Minimum context length required",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_model_info",
                description="Get detailed information about a specific model",
                parameters=[
                    ToolParameter(
                        name="model_id",
                        type="string",
                        description="Model ID (e.g., 'openai/gpt-4')",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="compare_models",
                description="Compare multiple models side by side",
                parameters=[
                    ToolParameter(
                        name="model_ids",
                        type="array",
                        description="List of model IDs to compare",
                        required=True,
                    ),
                    ToolParameter(
                        name="criteria",
                        type="array",
                        description="Comparison criteria (cost, speed, quality)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="list_providers",
                description="List all available model providers",
                parameters=[],
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle OpenRouter Search tool calls"""

        if tool_name == "search_models":
            return await self._search_models(**arguments)
        elif tool_name == "get_model_info":
            return await self._get_model_info(**arguments)
        elif tool_name == "compare_models":
            return await self._compare_models(**arguments)
        elif tool_name == "list_providers":
            return await self._list_providers()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _make_request(
        self, method: str, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a request to OpenRouter API"""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.api_url}{endpoint}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def _search_models(
        self,
        query: str,
        max_cost: Optional[float] = None,
        min_context: Optional[int] = None,
    ) -> dict[str, Any]:
        """Search for AI models"""

        # Mock model data for demo
        # In production, this would query the actual OpenRouter API
        all_models = [
            {
                "id": "openai/gpt-4",
                "name": "GPT-4",
                "provider": "openai",
                "context_length": 8192,
                "cost_per_1k_prompt": 0.03,
                "cost_per_1k_completion": 0.06,
                "capabilities": ["chat", "code", "reasoning"],
                "quality_score": 0.95,
                "speed_score": 0.7,
            },
            {
                "id": "anthropic/claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "anthropic",
                "context_length": 200000,
                "cost_per_1k_prompt": 0.015,
                "cost_per_1k_completion": 0.075,
                "capabilities": ["chat", "code", "vision", "reasoning"],
                "quality_score": 0.96,
                "speed_score": 0.6,
            },
            {
                "id": "anthropic/claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "provider": "anthropic",
                "context_length": 200000,
                "cost_per_1k_prompt": 0.003,
                "cost_per_1k_completion": 0.015,
                "capabilities": ["chat", "code", "vision"],
                "quality_score": 0.92,
                "speed_score": 0.8,
            },
            {
                "id": "meta-llama/llama-3-70b",
                "name": "Llama 3 70B",
                "provider": "meta",
                "context_length": 8192,
                "cost_per_1k_prompt": 0.0008,
                "cost_per_1k_completion": 0.0008,
                "capabilities": ["chat", "code"],
                "quality_score": 0.88,
                "speed_score": 0.9,
            },
            {
                "id": "google/gemini-pro",
                "name": "Gemini Pro",
                "provider": "google",
                "context_length": 32000,
                "cost_per_1k_prompt": 0.00025,
                "cost_per_1k_completion": 0.0005,
                "capabilities": ["chat", "code", "vision"],
                "quality_score": 0.90,
                "speed_score": 0.85,
            },
        ]

        # Filter models based on search criteria
        query_lower = query.lower()
        filtered_models = []

        for model in all_models:
            # Check if query matches capabilities or name
            if query_lower in model["name"].lower() or any(
                query_lower in cap for cap in model["capabilities"]
            ):
                # Apply cost filter
                if max_cost and model["cost_per_1k_prompt"] > max_cost:
                    continue

                # Apply context filter
                if min_context and model["context_length"] < min_context:
                    continue

                filtered_models.append(model)

        # Sort by quality score
        filtered_models.sort(key=lambda x: x["quality_score"], reverse=True)

        return {
            "query": query,
            "filters": {
                "max_cost": max_cost,
                "min_context": min_context,
            },
            "results": filtered_models,
            "count": len(filtered_models),
        }

    async def _get_model_info(self, model_id: str) -> dict[str, Any]:
        """Get detailed model information"""

        # Mock detailed model info
        model_details = {
            "openai/gpt-4": {
                "id": "openai/gpt-4",
                "name": "GPT-4",
                "provider": "openai",
                "description": "OpenAI's most capable model for complex tasks",
                "context_length": 8192,
                "max_tokens": 4096,
                "cost_per_1k_prompt": 0.03,
                "cost_per_1k_completion": 0.06,
                "capabilities": ["chat", "code", "reasoning", "function_calling"],
                "supported_languages": 95,
                "training_cutoff": "2023-04",
                "average_latency": 1.2,
                "quality_score": 0.95,
                "speed_score": 0.7,
                "best_use_cases": [
                    "Complex reasoning",
                    "Code generation",
                    "Creative writing",
                    "Technical analysis",
                ],
            },
            "anthropic/claude-3-opus": {
                "id": "anthropic/claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "anthropic",
                "description": "Anthropic's most powerful model with 200k context",
                "context_length": 200000,
                "max_tokens": 4096,
                "cost_per_1k_prompt": 0.015,
                "cost_per_1k_completion": 0.075,
                "capabilities": ["chat", "code", "vision", "reasoning", "analysis"],
                "supported_languages": 100,
                "training_cutoff": "2024-04",
                "average_latency": 1.5,
                "quality_score": 0.96,
                "speed_score": 0.6,
                "best_use_cases": [
                    "Long document analysis",
                    "Multi-modal tasks",
                    "Research assistance",
                    "Complex coding tasks",
                ],
            },
        }

        model_info = model_details.get(model_id)

        if not model_info:
            return {"error": f"Model '{model_id}' not found"}

        return model_info

    async def _compare_models(
        self, model_ids: list[str], criteria: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Compare multiple models"""

        if not criteria:
            criteria = ["cost", "quality", "speed", "context", "capabilities"]

        # Get info for each model
        models = []
        for model_id in model_ids:
            model_info = await self._get_model_info(model_id)
            if "error" not in model_info:
                models.append(model_info)

        if not models:
            return {"error": "No valid models found for comparison"}

        # Build comparison
        comparison = {
            "models": model_ids,
            "criteria": criteria,
            "comparison": {},
        }

        # Compare by each criterion
        if "cost" in criteria:
            comparison["comparison"]["cost"] = {
                model["id"]: {
                    "prompt_cost": model["cost_per_1k_prompt"],
                    "completion_cost": model["cost_per_1k_completion"],
                    "total_per_1k": model["cost_per_1k_prompt"]
                    + model["cost_per_1k_completion"],
                }
                for model in models
            }

        if "quality" in criteria:
            comparison["comparison"]["quality"] = {
                model["id"]: model["quality_score"] for model in models
            }

        if "speed" in criteria:
            comparison["comparison"]["speed"] = {
                model["id"]: {
                    "score": model["speed_score"],
                    "latency": model.get("average_latency", "N/A"),
                }
                for model in models
            }

        if "context" in criteria:
            comparison["comparison"]["context_length"] = {
                model["id"]: model["context_length"] for model in models
            }

        if "capabilities" in criteria:
            comparison["comparison"]["capabilities"] = {
                model["id"]: model["capabilities"] for model in models
            }

        # Add recommendations
        comparison["recommendations"] = self._generate_recommendations(models)

        return comparison

    def _generate_recommendations(self, models: list[dict[str, Any]]) -> dict[str, str]:
        """Generate model recommendations based on use cases"""

        recommendations = {}

        # Find best for different use cases
        # Best for quality
        best_quality = max(models, key=lambda x: x["quality_score"])
        recommendations["best_quality"] = best_quality["id"]

        # Best value (quality/cost ratio)
        best_value = max(
            models,
            key=lambda x: x["quality_score"]
            / (x["cost_per_1k_prompt"] + x["cost_per_1k_completion"]),
        )
        recommendations["best_value"] = best_value["id"]

        # Fastest
        fastest = max(models, key=lambda x: x["speed_score"])
        recommendations["fastest"] = fastest["id"]

        # Best for long context
        best_context = max(models, key=lambda x: x["context_length"])
        recommendations["best_long_context"] = best_context["id"]

        return recommendations

    async def _list_providers(self) -> dict[str, Any]:
        """List all available model providers"""

        providers = [
            {
                "id": "openai",
                "name": "OpenAI",
                "models_count": 8,
                "popular_models": ["gpt-4", "gpt-3.5-turbo"],
                "strengths": ["General purpose", "Function calling", "Code generation"],
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "models_count": 6,
                "popular_models": ["claude-3-opus", "claude-3-sonnet"],
                "strengths": ["Long context", "Safety", "Reasoning"],
            },
            {
                "id": "google",
                "name": "Google",
                "models_count": 4,
                "popular_models": ["gemini-pro", "gemini-pro-vision"],
                "strengths": ["Multi-modal", "Speed", "Cost efficiency"],
            },
            {
                "id": "meta",
                "name": "Meta",
                "models_count": 6,
                "popular_models": ["llama-3-70b", "llama-3-8b"],
                "strengths": ["Open source", "Cost efficiency", "Fine-tuning"],
            },
            {
                "id": "mistral",
                "name": "Mistral",
                "models_count": 4,
                "popular_models": ["mixtral-8x7b", "mistral-7b"],
                "strengths": ["European", "Efficiency", "Multi-lingual"],
            },
        ]

        return {
            "providers": providers,
            "count": len(providers),
            "total_models": sum(p["models_count"] for p in providers),
        }

# Create and run server
if __name__ == "__main__":
    server = OpenRouterSearchMCPServer()
    server.run()
