"""
Simplified Portkey-First LLM Service for Sophia AI
100% Portkey with Virtual Keys - Zero Complexity Setup

This service replaces all direct LLM provider integrations with a single Portkey gateway
using virtual keys for simplified management, unified cost tracking, and enhanced reliability.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import aiohttp
import structlog

from backend.core.simple_config import get_config_value

logger = structlog.get_logger()


class TaskType(str, Enum):
    """Simplified task type routing"""

    CEO_INSIGHTS = "ceo_insights"
    BUSINESS_ANALYSIS = "business_analysis"
    CODE_GENERATION = "code_generation"
    CREATIVE_DESIGN = "creative_design"
    DATA_ANALYSIS = "data_analysis"
    CHAT_GENERAL = "chat_general"
    RESEARCH_DEEP = "research_deep"


class ModelTier(str, Enum):
    """Simplified model tiers via Portkey virtual keys"""

    PREMIUM = "premium"  # GPT-4o, Claude Opus via virtual keys
    BALANCED = "balanced"  # Claude Sonnet, GPT-4 Turbo via virtual keys
    EFFICIENT = "efficient"  # Claude Haiku, smaller models via virtual keys


@dataclass
class SimplifiedLLMRequest:
    """Simplified request structure"""

    messages: List[Dict[str, str]]
    task_type: TaskType = TaskType.CHAT_GENERAL
    max_tokens: int = 2000
    temperature: float = 0.7
    stream: bool = False
    user_id: str = "anonymous"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SimplifiedLLMResponse:
    """Simplified response structure"""

    content: str
    model_used: str
    tokens_used: int
    cost_estimate: float
    processing_time_ms: int
    task_type: TaskType
    success: bool = True
    error: Optional[str] = None


class SimplifiedPortkeyService:
    """
    100% Portkey-First LLM Service

    Key Benefits:
    - Single API key (Portkey virtual key)
    - Unified cost tracking
    - Built-in fallbacks and load balancing
    - Simplified configuration
    - Enhanced reliability
    """

    def __init__(self):
        self.base_url = "https://api.portkey.ai/v1"
        self.virtual_key = get_config_value(
            "portkey_virtual_key_prod"
        ) or get_config_value("values_sophia_ai_portkey_virtual_key_prod")
        self.session: Optional[aiohttp.ClientSession] = None

        # Simplified model routing via virtual keys
        self.task_routing = {
            TaskType.CEO_INSIGHTS: ModelTier.PREMIUM,
            TaskType.BUSINESS_ANALYSIS: ModelTier.PREMIUM,
            TaskType.CODE_GENERATION: ModelTier.BALANCED,
            TaskType.CREATIVE_DESIGN: ModelTier.PREMIUM,
            TaskType.DATA_ANALYSIS: ModelTier.BALANCED,
            TaskType.CHAT_GENERAL: ModelTier.BALANCED,
            TaskType.RESEARCH_DEEP: ModelTier.PREMIUM,
        }

        # Virtual key mapping (configured in Portkey dashboard)
        self.virtual_key_config = {
            ModelTier.PREMIUM: {
                "virtual_key_suffix": "premium",
                "fallback_models": ["gpt-4o", "claude-3-opus-20240229"],
                "estimated_cost_per_1k": 0.025,
            },
            ModelTier.BALANCED: {
                "virtual_key_suffix": "balanced",
                "fallback_models": ["claude-3-sonnet-20240229", "gpt-4-turbo"],
                "estimated_cost_per_1k": 0.015,
            },
            ModelTier.EFFICIENT: {
                "virtual_key_suffix": "efficient",
                "fallback_models": ["claude-3-haiku-20240307", "gpt-3.5-turbo"],
                "estimated_cost_per_1k": 0.005,
            },
        }

    async def initialize(self) -> bool:
        """Initialize the simplified Portkey service"""
        try:
            if not self.virtual_key:
                logger.error("Portkey virtual key not configured")
                return False

            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
                headers={
                    "Authorization": f"Bearer {self.virtual_key}",
                    "Content-Type": "application/json",
                    "x-portkey-trace-id": f"sophia-ai-{int(time.time())}",
                },
            )

            # Test connection
            success = await self._health_check()
            if success:
                logger.info("✅ Simplified Portkey service initialized successfully")
            else:
                logger.error("❌ Portkey service initialization failed")

            return success

        except Exception as e:
            logger.error(f"Failed to initialize Portkey service: {e}")
            return False

    async def _health_check(self) -> bool:
        """Simple health check"""
        try:
            if not self.session:
                return False
            async with self.session.get(f"{self.base_url}/models") as response:
                return response.status == 200
        except Exception:
            return False

    async def complete(self, request: SimplifiedLLMRequest) -> SimplifiedLLMResponse:
        """
        Simplified completion method - single entry point for all LLM operations
        """
        start_time = time.time()

        try:
            # Determine model tier based on task type
            model_tier = self.task_routing.get(request.task_type, ModelTier.BALANCED)

            # Build Portkey request
            metadata = {
                "task_type": request.task_type.value,
                "user_id": request.user_id,
                "tier": model_tier.value,
            }
            if request.metadata:
                metadata.update(request.metadata)

            portkey_request = {
                "messages": request.messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": request.stream,
                "metadata": metadata,
            }

            # Add virtual key routing header
            headers = {
                "x-portkey-virtual-key": f"{self.virtual_key}-{model_tier.value}",
                "x-portkey-cache": "semantic",
                "x-portkey-retry-count": "3",
            }

            # Make request to Portkey
            if not self.session:
                raise Exception("Session not initialized")

            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=portkey_request,
                headers=headers,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Portkey API error: {response.status} - {error_text}")
                    return SimplifiedLLMResponse(
                        content="",
                        model_used="error",
                        tokens_used=0,
                        cost_estimate=0.0,
                        processing_time_ms=int((time.time() - start_time) * 1000),
                        task_type=request.task_type,
                        success=False,
                        error=f"API Error: {response.status}",
                    )

                result = await response.json()

                # Extract response data
                content = result["choices"][0]["message"]["content"]
                model_used = result.get("model", f"portkey-{model_tier.value}")
                usage = result.get("usage", {})
                tokens_used = usage.get("total_tokens", 0)

                # Calculate cost estimate
                tier_config = self.virtual_key_config[model_tier]
                cost_estimate = (tokens_used / 1000) * tier_config[
                    "estimated_cost_per_1k"
                ]

                processing_time = int((time.time() - start_time) * 1000)

                logger.info(
                    "LLM request completed",
                    task_type=request.task_type.value,
                    model_tier=model_tier.value,
                    tokens=tokens_used,
                    cost=cost_estimate,
                    time_ms=processing_time,
                )

                return SimplifiedLLMResponse(
                    content=content,
                    model_used=model_used,
                    tokens_used=tokens_used,
                    cost_estimate=cost_estimate,
                    processing_time_ms=processing_time,
                    task_type=request.task_type,
                    success=True,
                )

        except Exception as e:
            logger.error(f"LLM completion error: {e}")
            return SimplifiedLLMResponse(
                content="",
                model_used="error",
                tokens_used=0,
                cost_estimate=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000),
                task_type=request.task_type,
                success=False,
                error=str(e),
            )

    async def stream_complete(
        self, request: SimplifiedLLMRequest
    ) -> AsyncGenerator[str, None]:
        """Simplified streaming completion"""
        request.stream = True

        try:
            model_tier = self.task_routing.get(request.task_type, ModelTier.BALANCED)

            portkey_request = {
                "messages": request.messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": True,
                "metadata": {
                    "task_type": request.task_type.value,
                    "user_id": request.user_id,
                    "tier": model_tier.value,
                },
            }

            headers = {
                "x-portkey-virtual-key": f"{self.virtual_key}-{model_tier.value}",
                "x-portkey-cache": "semantic",
                "x-portkey-retry-count": "3",
            }

            if not self.session:
                yield "Error: Session not initialized"
                return

            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=portkey_request,
                headers=headers,
            ) as response:
                async for line in response.content:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: ") and not line.endswith("[DONE]"):
                        try:
                            data = json.loads(line[6:])
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"Error: {str(e)}"

    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()


# Simplified convenience functions for common operations
class SophiaLLM:
    """
    Simplified interface for Sophia AI LLM operations
    Usage: result = await SophiaLLM.chat("Analyze our Q4 revenue trends", TaskType.BUSINESS_ANALYSIS)
    """

    _service: Optional[SimplifiedPortkeyService] = None

    @classmethod
    async def _get_service(cls) -> SimplifiedPortkeyService:
        if cls._service is None:
            cls._service = SimplifiedPortkeyService()
            await cls._service.initialize()
        return cls._service

    @classmethod
    async def chat(
        cls,
        message: str,
        task_type: TaskType = TaskType.CHAT_GENERAL,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        user_id: str = "sophia-ai",
    ) -> SimplifiedLLMResponse:
        """Simple chat interface"""
        service = await cls._get_service()
        request = SimplifiedLLMRequest(
            messages=[{"role": "user", "content": message}],
            task_type=task_type,
            max_tokens=max_tokens,
            temperature=temperature,
            user_id=user_id,
        )
        return await service.complete(request)

    @classmethod
    async def analyze_business(
        cls, query: str, context: Optional[Dict[str, Any]] = None
    ) -> SimplifiedLLMResponse:
        """CEO/Business analysis optimized"""
        enhanced_prompt = f"""
As a business intelligence expert, analyze the following:

Query: {query}

Context: {json.dumps(context, indent=2) if context else "None provided"}

Provide strategic insights with:
1. Key findings
2. Business implications
3. Recommended actions
4. Risk assessment
"""
        return await cls.chat(enhanced_prompt, TaskType.CEO_INSIGHTS, max_tokens=3000)

    @classmethod
    async def generate_code(
        cls, requirements: str, language: str = "python"
    ) -> SimplifiedLLMResponse:
        """Code generation optimized"""
        code_prompt = f"""
Generate {language} code for the following requirements:

{requirements}

Provide:
1. Complete, working code
2. Clear documentation
3. Error handling
4. Best practices implementation
"""
        return await cls.chat(
            code_prompt, TaskType.CODE_GENERATION, max_tokens=4000, temperature=0.3
        )


# Global instance for backward compatibility
simplified_llm_service = SimplifiedPortkeyService()


# Convenience function for immediate use
async def sophia_ai_complete(message: str, task_type: str = "chat_general") -> str:
    """Ultra-simple completion function"""
    try:
        task_enum = TaskType(task_type)
        response = await SophiaLLM.chat(message, task_enum)
        return response.content if response.success else f"Error: {response.error}"
    except ValueError:
        response = await SophiaLLM.chat(message, TaskType.CHAT_GENERAL)
        return response.content if response.success else f"Error: {response.error}"


if __name__ == "__main__":

    async def test_simplified_service():
        """Test the simplified service"""
        print("🧪 Testing Simplified Portkey Service")
        print("=" * 50)

        # Test business analysis
        response = await SophiaLLM.analyze_business(
            "What are the key trends in our sales data?",
            {"revenue": "increasing", "customers": "growing"},
        )

        if response.success:
            print("✅ Business Analysis Successful")
            print(f"Model: {response.model_used}")
            print(f"Tokens: {response.tokens_used}")
            print(f"Cost: ${response.cost_estimate:.4f}")
            print(f"Time: {response.processing_time_ms}ms")
            print(f"Response: {response.content[:200]}...")
        else:
            print(f"❌ Error: {response.error}")

        # Test code generation
        code_response = await SophiaLLM.generate_code(
            "Create a function to calculate compound interest"
        )

        if code_response.success:
            print("\n✅ Code Generation Successful")
            print(f"Model: {code_response.model_used}")
            print(f"Tokens: {code_response.tokens_used}")
            print(f"Cost: ${code_response.cost_estimate:.4f}")
        else:
            print(f"❌ Code Error: {code_response.error}")

    asyncio.run(test_simplified_service())
