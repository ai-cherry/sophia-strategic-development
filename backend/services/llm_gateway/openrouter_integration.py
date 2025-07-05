#!/usr/bin/env python3
"""
OpenRouter Integration
Access to 200+ models with quality-focused selection
"""

import time
from typing import Any

import aiohttp

from backend.core.config_manager import ConfigManager
from backend.utils.custom_logger import setup_logger

logger = setup_logger("openrouter_integration")


class OpenRouterIntegration:
    """
    OpenRouter integration for accessing 200+ models
    Focuses on specialized model selection for quality
    """

    def __init__(self):
        self.config = ConfigManager()
        self.api_key = self.config.get("openrouter_api_key", "")
        self.base_url = "https://openrouter.ai/api/v1"

        # Model catalog organized by capability
        self.model_catalog = {
            "general_purpose": [
                "openai/gpt-4-turbo-preview",
                "anthropic/claude-3-opus",
                "google/gemini-pro",
                "meta-llama/llama-3-70b-instruct",
            ],
            "code_generation": [
                "openai/gpt-4-turbo",
                "anthropic/claude-3-sonnet",
                "phind/phind-codellama-34b",
                "wizardlm/wizardcoder-33b",
            ],
            "reasoning": [
                "anthropic/claude-3-opus",
                "openai/gpt-4",
                "google/gemini-ultra",
                "mistralai/mixtral-8x22b",
            ],
            "creative_writing": [
                "anthropic/claude-3-creative",
                "openai/gpt-4-creative",
                "cohere/command-r-plus",
                "meta-llama/llama-3-creative",
            ],
            "apartment_industry": [
                "openai/gpt-4-turbo",  # Fine-tuned for business
                "anthropic/claude-3-opus",  # Strong context understanding
                "mistralai/mistral-large",  # European property focus
                "custom/pay-ready-assistant",  # Custom fine-tuned model
            ],
            "financial_analysis": [
                "openai/gpt-4-turbo",
                "anthropic/claude-3-opus",
                "bloomberg/bloomberggpt",
                "custom/fintech-analyst",
            ],
            "customer_service": [
                "anthropic/claude-3-haiku",  # Fast and accurate
                "openai/gpt-3.5-turbo",
                "cohere/command-light",
                "custom/pay-ready-support",
            ],
        }

        # Model performance characteristics
        self.model_characteristics = {
            "openai/gpt-4-turbo-preview": {
                "quality_score": 0.95,
                "speed": "medium",
                "cost_per_1k": 0.03,
                "context_window": 128000,
                "strengths": ["reasoning", "code", "analysis"],
            },
            "anthropic/claude-3-opus": {
                "quality_score": 0.96,
                "speed": "medium",
                "cost_per_1k": 0.015,
                "context_window": 200000,
                "strengths": ["writing", "analysis", "safety"],
            },
            "google/gemini-pro": {
                "quality_score": 0.93,
                "speed": "fast",
                "cost_per_1k": 0.001,
                "context_window": 32000,
                "strengths": ["multimodal", "reasoning", "speed"],
            },
            "meta-llama/llama-3-70b-instruct": {
                "quality_score": 0.91,
                "speed": "fast",
                "cost_per_1k": 0.0008,
                "context_window": 8192,
                "strengths": ["open-source", "customizable", "efficient"],
            },
        }

        logger.info("OpenRouter integration initialized with 200+ model access")

    async def execute(
        self,
        query: str,
        context: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> str:
        """
        Execute query through OpenRouter with quality-optimized model selection
        """
        start_time = time.time()

        # Select optimal model for the task
        selected_model = await self._select_quality_optimal_model(
            query, context, settings
        )

        logger.info(f"Selected model: {selected_model} for quality optimization")

        # Prepare request
        request_data = self._prepare_request(query, context, selected_model, settings)

        # Execute request
        response = await self._execute_request(request_data)

        execution_time = time.time() - start_time
        logger.info(
            f"OpenRouter execution completed in {execution_time:.2f}s with {selected_model}"
        )

        return response

    async def _select_quality_optimal_model(
        self, query: str, context: str | None, settings: dict[str, Any] | None
    ) -> str:
        """Select the best model for quality based on task type"""
        # Analyze query to determine task type
        task_type = self._analyze_task_type(query, context)

        # Check if specific model requested
        if settings and "model" in settings:
            return settings["model"]

        # Get candidate models for task type
        candidates = self.model_catalog.get(
            task_type, self.model_catalog["general_purpose"]
        )

        # Score models based on quality requirements
        best_model = candidates[0]  # Default to first
        best_score = 0

        for model in candidates:
            if model in self.model_characteristics:
                characteristics = self.model_characteristics[model]

                # Calculate quality score
                score = characteristics["quality_score"]

                # Boost score if model strengths match task
                task_keywords = self._get_task_keywords(query)
                matching_strengths = sum(
                    1
                    for strength in characteristics["strengths"]
                    if any(keyword in strength for keyword in task_keywords)
                )
                score += matching_strengths * 0.05

                # Consider context window if large context
                if context and len(context) > 50000:
                    if characteristics["context_window"] >= len(context):
                        score += 0.1

                if score > best_score:
                    best_score = score
                    best_model = model

        return best_model

    def _analyze_task_type(self, query: str, context: str | None) -> str:
        """Analyze query to determine task type"""
        query_lower = query.lower()

        # Check for apartment industry keywords
        apartment_keywords = [
            "apartment",
            "tenant",
            "lease",
            "rent",
            "property",
            "payment",
            "maintenance",
            "resident",
            "unit",
        ]
        if any(keyword in query_lower for keyword in apartment_keywords):
            return "apartment_industry"

        # Check for code generation
        code_keywords = ["code", "function", "implement", "debug", "program"]
        if any(keyword in query_lower for keyword in code_keywords):
            return "code_generation"

        # Check for reasoning tasks
        reasoning_keywords = ["analyze", "explain", "why", "reason", "logic"]
        if any(keyword in query_lower for keyword in reasoning_keywords):
            return "reasoning"

        # Check for creative writing
        creative_keywords = ["write", "create", "story", "creative", "compose"]
        if any(keyword in query_lower for keyword in creative_keywords):
            return "creative_writing"

        # Check for financial analysis
        financial_keywords = ["revenue", "financial", "profit", "cost", "roi"]
        if any(keyword in query_lower for keyword in financial_keywords):
            return "financial_analysis"

        # Check for customer service
        service_keywords = ["help", "support", "issue", "problem", "assist"]
        if any(keyword in query_lower for keyword in service_keywords):
            return "customer_service"

        return "general_purpose"

    def _get_task_keywords(self, query: str) -> list[str]:
        """Extract task-related keywords from query"""
        # Simple keyword extraction
        important_words = []

        query_words = query.lower().split()

        # Keywords that indicate specific capabilities
        capability_keywords = [
            "analyze",
            "code",
            "reason",
            "explain",
            "create",
            "write",
            "calculate",
            "optimize",
            "debug",
            "design",
        ]

        for word in query_words:
            if word in capability_keywords:
                important_words.append(word)

        return important_words

    def _prepare_request(
        self,
        query: str,
        context: str | None,
        model: str,
        settings: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Prepare request for OpenRouter API"""
        request_data = {
            "model": model,
            "messages": [],
            "temperature": settings.get("temperature", 0.7) if settings else 0.7,
            "max_tokens": settings.get("max_tokens", 4096) if settings else 4096,
            "top_p": settings.get("top_p", 0.9) if settings else 0.9,
            "frequency_penalty": settings.get("frequency_penalty", 0.0)
            if settings
            else 0.0,
            "presence_penalty": settings.get("presence_penalty", 0.0)
            if settings
            else 0.0,
            "stream": False,
        }

        # Add system message for quality
        system_message = (
            "You are a high-quality AI assistant with expertise in the apartment "
            "technology and payments industry. Provide accurate, detailed, and "
            "actionable responses that demonstrate deep understanding of the domain."
        )

        if context:
            system_message += f"\n\nContext: {context}"

        request_data["messages"].append({"role": "system", "content": system_message})

        # Add user query
        request_data["messages"].append({"role": "user", "content": query})

        # Add OpenRouter-specific parameters
        request_data["route"] = "quality"  # Prioritize quality routing
        request_data["models"] = [model]  # Specific model selection

        return request_data

    async def _execute_request(self, request_data: dict[str, Any]) -> str:
        """Execute request to OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://payready.com",  # Your app URL
            "X-Title": "Sophia AI - Pay Ready",
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"OpenRouter API error: {response.status} - {error_text}"
                        )
                        raise Exception(f"API error: {response.status}")

            except TimeoutError:
                logger.error("OpenRouter API timeout")
                raise
            except Exception as e:
                logger.error(f"OpenRouter execution error: {e}")
                raise

    async def get_available_models(self) -> dict[str, list[str]]:
        """Get list of available models from OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Organize models by provider
                        models_by_provider = {}
                        for model in data.get("data", []):
                            provider = model["id"].split("/")[0]
                            if provider not in models_by_provider:
                                models_by_provider[provider] = []
                            models_by_provider[provider].append(model["id"])
                        return models_by_provider
                    else:
                        logger.error(f"Failed to fetch models: {response.status}")
                        return self.model_catalog

            except Exception as e:
                logger.error(f"Error fetching models: {e}")
                return self.model_catalog

    async def benchmark_models(
        self, query: str, models: list[str]
    ) -> dict[str, dict[str, Any]]:
        """Benchmark multiple models for quality comparison"""
        results = {}

        for model in models:
            try:
                start_time = time.time()

                response = await self.execute(query=query, settings={"model": model})

                execution_time = time.time() - start_time

                results[model] = {
                    "response": response[:200] + "..."
                    if len(response) > 200
                    else response,
                    "execution_time": execution_time,
                    "response_length": len(response),
                    "quality_score": self._estimate_quality(response),
                }

            except Exception as e:
                results[model] = {
                    "error": str(e),
                    "execution_time": 0,
                    "response_length": 0,
                    "quality_score": 0,
                }

        return results

    def _estimate_quality(self, response: str) -> float:
        """Estimate response quality (simplified)"""
        score = 0.5  # Base score

        # Length bonus (up to 0.2)
        if len(response) > 100:
            score += min(0.2, len(response) / 1000)

        # Structure bonus (up to 0.2)
        if response.count("\n") > 2:
            score += 0.1
        if any(marker in response for marker in ["1.", "2.", "•", "-"]):
            score += 0.1

        # Completeness bonus (up to 0.1)
        if response.strip().endswith("."):
            score += 0.05
        if len(response.split(".")) > 3:
            score += 0.05

        return min(1.0, score)
