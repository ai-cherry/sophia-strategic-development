"""OpenRouter and Portkey AI Model Routing and Gateway for Sophia AI.

Provides intelligent model routing, load balancing, and cost optimization
"""import json

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for an AI model."""

    name: str
    provider: str
    cost_per_token: float
    max_tokens: int
    capabilities: List[str]
    priority: int = 1


@dataclass
class RoutingRule:
    """Rule for routing requests to specific models."""condition: str.

    target_model: str
    weight: float = 1.0


class OpenRouterClient:
    """OpenRouter client for accessing multiple AI models through a unified API."""def __init__(self):.

        """Initialize OpenRouter client."""self.api_key = os.getenv("OPENROUTER_API_KEY").

        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY must be set")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sophia-ai.com",
            "X-Title": "Sophia AI Platform",
        }

        # Available models configuration
        self.models = {
            "gpt-4-turbo": ModelConfig(
                name="openai/gpt-4-turbo",
                provider="openai",
                cost_per_token=0.00003,
                max_tokens=128000,
                capabilities=["chat", "analysis", "coding", "reasoning"],
                priority=1,
            ),
            "claude-3-sonnet": ModelConfig(
                name="anthropic/claude-3-sonnet",
                provider="anthropic",
                cost_per_token=0.000015,
                max_tokens=200000,
                capabilities=["chat", "analysis", "writing", "reasoning"],
                priority=2,
            ),
            "gemini-pro": ModelConfig(
                name="google/gemini-pro",
                provider="google",
                cost_per_token=0.0000005,
                max_tokens=32000,
                capabilities=["chat", "analysis", "multimodal"],
                priority=3,
            ),
            "llama-3-70b": ModelConfig(
                name="meta-llama/llama-3-70b-instruct",
                provider="meta",
                cost_per_token=0.0000009,
                max_tokens=8000,
                capabilities=["chat", "reasoning", "coding"],
                priority=4,
            ),
        }

        logger.info("OpenRouter client initialized successfully")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a chat completion using OpenRouter.

                        Args:
                            messages: List of message dictionaries
                            model: Model to use (auto-selected if None)
                            max_tokens: Maximum tokens to generate
                            temperature: Sampling temperature
                            **kwargs: Additional parameters

                        Returns:
                            Dict with completion response
        """try:.

            # Auto-select model if not specified
            if not model:
                model = self._select_optimal_model(
                    messages, kwargs.get("capabilities", [])
                )

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4000,
                **kwargs,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successful completion with model: {model}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"OpenRouter API error: {response.status} - {error_text}"
                        )
                        return {"error": f"API error: {response.status}"}

        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            return {"error": str(e)}

    def _select_optimal_model(
        self, messages: List[Dict[str, str]], capabilities: List[str]
    ) -> str:
        """Select the optimal model based on request characteristics.

                        Args:
                            messages: Input messages
                            capabilities: Required capabilities

                        Returns:
                            str: Selected model name
        """# Calculate input length.

        total_length = sum(len(msg.get("content", "")) for msg in messages)

        # Filter models by capabilities
        suitable_models = []
        for model_key, config in self.models.items():
            if not capabilities or any(
                cap in config.capabilities for cap in capabilities
            ):
                if total_length < config.max_tokens * 0.7:  # Leave room for response
                    suitable_models.append((model_key, config))

        if not suitable_models:
            # Fallback to highest capacity model
            return "openai/gpt-4-turbo"

        # Select based on cost-effectiveness and priority
        suitable_models.sort(key=lambda x: (x[1].priority, x[1].cost_per_token))
        selected = suitable_models[0][1].name

        logger.info(f"Auto-selected model: {selected}")
        return selected

    async def get_models(self) -> List[Dict[str, Any]]:
        """Get available models from OpenRouter."""try:.

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/models", headers=self.headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", [])
                    else:
                        logger.error(f"Error fetching models: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            return []


class PortkeyGateway:
    """Portkey AI Gateway for advanced routing, caching, and observability."""def __init__(self):.

        """Initialize Portkey gateway."""self.api_key = os.getenv("PORTKEY_API_KEY").

        self.config_id = os.getenv("PORTKEY_CONFIG")
        self.base_url = "https://api.portkey.ai/v1"

        if not self.api_key:
            raise ValueError("PORTKEY_API_KEY must be set")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.config_id:
            self.headers["x-portkey-config"] = self.config_id

        # Routing rules for Sophia AI
        self.routing_rules = [
            RoutingRule(
                condition="length > 10000",
                target_model="anthropic/claude-3-sonnet",
                weight=1.0,
            ),
            RoutingRule(
                condition="type == 'coding'",
                target_model="openai/gpt-4-turbo",
                weight=1.0,
            ),
            RoutingRule(
                condition="type == 'analysis'",
                target_model="anthropic/claude-3-sonnet",
                weight=0.8,
            ),
            RoutingRule(
                condition="cost_sensitive == true",
                target_model="meta-llama/llama-3-70b-instruct",
                weight=1.0,
            ),
        ]

        logger.info("Portkey gateway initialized successfully")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        routing_strategy: str = "smart",
        cache: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a chat completion through Portkey gateway.

                        Args:
                            messages: List of message dictionaries
                            model: Specific model to use
                            routing_strategy: Routing strategy ("smart", "cost", "performance")
                            cache: Whether to use caching
                            **kwargs: Additional parameters

                        Returns:
                            Dict with completion response
        """try:.

            # Apply routing strategy
            if not model:
                model = self._apply_routing_strategy(messages, routing_strategy, kwargs)

            payload = {"model": model, "messages": messages, **kwargs}

            # Add Portkey-specific headers
            headers = self.headers.copy()
            if cache:
                headers["x-portkey-cache"] = "semantic"
            headers["x-portkey-trace-id"] = f"sophia-{datetime.now().timestamp()}"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(
                            f"Successful Portkey completion with model: {model}"
                        )
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Portkey API error: {response.status} - {error_text}"
                        )
                        return {"error": f"API error: {response.status}"}

        except Exception as e:
            logger.error(f"Error in Portkey completion: {str(e)}")
            return {"error": str(e)}

    def _apply_routing_strategy(
        self, messages: List[Dict[str, str]], strategy: str, kwargs: Dict[str, Any]
    ) -> str:
        """Apply routing strategy to select optimal model.

                        Args:
                            messages: Input messages
                            strategy: Routing strategy
                            kwargs: Additional parameters

                        Returns:
                            str: Selected model name
        """total_length = sum(len(msg.get("content", "")) for msg in messages).

        if strategy == "cost":
            # Prioritize cost-effective models
            if total_length < 5000:
                return "meta-llama/llama-3-70b-instruct"
            else:
                return "anthropic/claude-3-sonnet"

        elif strategy == "performance":
            # Prioritize high-performance models
            return "openai/gpt-4-turbo"

        else:  # smart strategy
            # Apply routing rules
            for rule in self.routing_rules:
                if self._evaluate_condition(rule.condition, messages, kwargs):
                    logger.info(
                        f"Applied routing rule: {rule.condition} -> {rule.target_model}"
                    )
                    return rule.target_model

            # Default fallback
            return "anthropic/claude-3-sonnet"

    def _evaluate_condition(
        self, condition: str, messages: List[Dict[str, str]], kwargs: Dict[str, Any]
    ) -> bool:
        """Evaluate a routing condition.

                        Args:
                            condition: Condition string to evaluate
                            messages: Input messages
                            kwargs: Additional parameters

                        Returns:
                            bool: True if condition is met
        """try:.

            total_length = sum(len(msg.get("content", "")) for msg in messages)
            request_type = kwargs.get("type", "general")
            cost_sensitive = kwargs.get("cost_sensitive", False)

            # Simple condition evaluation
            if "length >" in condition:
                threshold = int(condition.split(">")[1].strip())
                return total_length > threshold
            elif "type ==" in condition:
                target_type = condition.split("==")[1].strip().strip("'\"")
                return request_type == target_type
            elif "cost_sensitive ==" in condition:
                return cost_sensitive

            return False

        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False


class SophiaAIModelRouter:
    """Unified model router for Sophia AI platform.

            Combines OpenRouter and Portkey for optimal AI model access
    """def __init__(self):."""Initialize Sophia AI model router"""

        self.openrouter = OpenRouterClient()
        self.portkey = PortkeyGateway()

        # Router configuration
        self.config = {
            "default_provider": "portkey",  # Use Portkey as default for advanced features
            "fallback_provider": "openrouter",  # Fallback to OpenRouter
            "enable_caching": True,
            "enable_monitoring": True,
            "cost_optimization": True,
        }

        logger.info("Sophia AI model router initialized successfully")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Route chat completion request to optimal provider.

                        Args:
                            messages: List of message dictionaries
                            model: Specific model to use
                            provider: Specific provider to use ("openrouter" or "portkey")
                            **kwargs: Additional parameters

                        Returns:
                            Dict with completion response
        """try:.

            # Determine provider
            if not provider:
                provider = self.config["default_provider"]

            # Route to appropriate provider
            if provider == "portkey":
                result = await self.portkey.chat_completion(
                    messages=messages,
                    model=model,
                    cache=self.config["enable_caching"],
                    **kwargs,
                )

                # Fallback to OpenRouter if Portkey fails
                if (
                    "error" in result
                    and self.config["fallback_provider"] == "openrouter"
                ):
                    logger.warning("Portkey failed, falling back to OpenRouter")
                    result = await self.openrouter.chat_completion(
                        messages=messages, model=model, **kwargs
                    )
            else:
                result = await self.openrouter.chat_completion(
                    messages=messages, model=model, **kwargs
                )

            # Log for monitoring if enabled
            if self.config["enable_monitoring"]:
                self._log_request(messages, result, provider, model)

            return result

        except Exception as e:
            logger.error(f"Error in model routing: {str(e)}")
            return {"error": str(e)}

    def _log_request(
        self,
        messages: List[Dict[str, str]],
        result: Dict[str, Any],
        provider: str,
        model: Optional[str],
    ):
        """Log request for monitoring and analytics."""try:.

            log_data = {
                "timestamp": datetime.now().isoformat(),
                "provider": provider,
                "model": model,
                "input_tokens": sum(len(msg.get("content", "")) for msg in messages)
                // 4,  # Rough estimate
                "success": "error" not in result,
                "response_time": result.get("response_time", 0),
            }

            logger.info(f"Model request logged: {json.dumps(log_data)}")

        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")


# Global router instance
sophia_router = None


def get_sophia_router() -> SophiaAIModelRouter:
    """Get or create global Sophia AI model router."""global sophia_router.

    if sophia_router is None:
        sophia_router = SophiaAIModelRouter()
    return sophia_router


# Convenience functions for common use cases
async def sophia_chat(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """Convenience function for chat completions."""router = get_sophia_router().

    return await router.chat(messages, **kwargs)


async def sophia_analyze(
    text: str, analysis_type: str = "general", **kwargs
) -> Dict[str, Any]:
    """Convenience function for text analysis."""messages = [.

        {
            "role": "system",
            "content": f"You are Sophia AI, an expert analyst. Perform {analysis_type} analysis.",
        },
        {"role": "user", "content": text},
    ]
    router = get_sophia_router()
    return await router.chat(messages, type="analysis", **kwargs)


async def sophia_code(
    prompt: str, language: str = "python", **kwargs
) -> Dict[str, Any]:
    """Convenience function for code generation."""
    messages = [
        {
            "role": "system",
            "content": f"You are Sophia AI, an expert {language} developer.",
        },
        {"role": "user", "content": prompt},
    ]
    router = get_sophia_router()
    return await router.chat(messages, type="coding", **kwargs)
