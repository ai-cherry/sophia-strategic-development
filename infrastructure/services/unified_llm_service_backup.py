"""
Unified LLM Service for Sophia AI
Centralizes all LLM interactions with intelligent routing
"""

import json
import time
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from typing import Any

from infrastructure.services.llm_router import TaskType, llm_router

try:
    from portkey_ai import AsyncPortkey
except ImportError:
    AsyncPortkey = None
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None
import snowflake.connector
from snowflake.connector import DictCursor

from core.auto_esc_config import config
from infrastructure.monitoring.llm_metrics import (
    data_movement_avoided,
    llm_cache_hit_rate,
    llm_request_duration,
    llm_requests_total,
)
from shared.utils.custom_logger import logger


class ModelTier(Enum):
    """Model tier classification for routing"""

    SNOWFLAKE = "snowflake"
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    EMBEDDINGS = "embeddings"


class TaskType(Enum):
    """Task types for intelligent routing"""

    DATA_ANALYSIS = "data_analysis"
    SQL_GENERATION = "sql_generation"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    CHAT_CONVERSATION = "chat_conversation"
    DOCUMENT_SUMMARY = "document_summary"
    EMBEDDINGS = "embeddings"


class LLMProvider(Enum):
    """LLM provider enumeration"""

    SNOWFLAKE = "snowflake"
    PORTKEY = "portkey"
    OPENROUTER = "openrouter"
    DIRECT = "direct"


class UnifiedLLMService:
    """
    Unified service for all LLM interactions in Sophia AI
    Implements intelligent routing based on task type and data location
    """

    def __init__(self):
        self.config = config
        self.initialized = False
        self._portkey = None
        self._openrouter = None
        self._snowflake = None
        self.model_routing = self._init_model_routing()

    async def initialize(self):
        """Initialize LLM connections lazily"""
        if not self.initialized:
            self._portkey = await self._init_portkey()
            self._openrouter = self._init_openrouter()
            self._snowflake = await self._init_snowflake()
            self.initialized = True
            logger.info("✅ UnifiedLLMService initialized successfully")

    async def _init_portkey(self) -> AsyncPortkey | None:
        """Initialize Portkey client"""
        if AsyncPortkey is None:
            logger.warning("Portkey package not installed")
            return None
        api_key = self.config.get("portkey_api_key")
        if not api_key:
            logger.warning("Portkey API key not found")
            return None
        return AsyncPortkey(
            api_key=api_key,
            virtual_keys={
                "openai": self.config.get("portkey_virtual_key_openai", ""),
                "anthropic": self.config.get("portkey_virtual_key_anthropic", ""),
            },
            config={
                "cache": {
                    "mode": "semantic",
                    "threshold": 0.95,
                    "ttl": 3600,
                    "max_size": 1000,
                    "enabled": True,
                },
                "retry": {"attempts": 3, "on_status_codes": [429, 500, 502, 503, 504]},
                "request_timeout": 30000,
            },
        )

    def _init_openrouter(self) -> AsyncOpenAI | None:
        """Initialize OpenRouter client"""
        api_key = self.config.get("openrouter_api_key")
        if not api_key:
            logger.warning("OpenRouter API key not found")
            return None
        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://sophia-intel.ai",
                "X-Title": "Sophia AI",
            },
        )

    async def _init_snowflake(self):
        """Initialize Snowflake connection"""
        try:
            conn = snowflake.connector.connect(
                user=self.config.get("snowflake_user"),
                password=self.config.get("snowflake_password"),
                account=self.config.get("snowflake_account"),
                warehouse=self.config.get("snowflake_warehouse", "COMPUTE_WH"),
                database=self.config.get("snowflake_database", "SOPHIA_AI"),
                schema=self.config.get("snowflake_schema", "CORE"),
            )
            return conn
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake: {e}")
            return None

    def _init_model_routing(self) -> dict[TaskType, ModelTier]:
        """CEO-configurable task-to-tier mapping"""
        return {
            TaskType.DATA_ANALYSIS: ModelTier.SNOWFLAKE,
            TaskType.SQL_GENERATION: ModelTier.SNOWFLAKE,
            TaskType.EMBEDDINGS: ModelTier.EMBEDDINGS,
            TaskType.CODE_GENERATION: ModelTier.TIER_1,
            TaskType.CODE_ANALYSIS: ModelTier.TIER_1,
            TaskType.BUSINESS_INTELLIGENCE: ModelTier.TIER_1,
            TaskType.CHAT_CONVERSATION: ModelTier.TIER_2,
            TaskType.DOCUMENT_SUMMARY: ModelTier.TIER_2,
        }

    async def complete(
        self,
        prompt: str,
        task_type: TaskType,
        stream: bool = True,
        metadata: dict | None = None,
        model_override: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """
        Unified completion interface with intelligent routing

        Args:
            prompt: The prompt to complete
            task_type: Type of task for routing
            stream: Whether to stream the response
            metadata: Additional metadata for tracking
            model_override: Override the default model selection
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Yields:
            Response chunks if streaming, otherwise complete response
        """
        if not self.initialized:
            await self.initialize()
        start_time = time.time()
        tier = self.model_routing.get(task_type, ModelTier.TIER_2)
        request_metadata = {
            "task_type": task_type.value,
            "tier": tier.value,
            "source": "sophia_ai",
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }
        try:
            if tier == ModelTier.SNOWFLAKE:
                async for chunk in self._snowflake_complete(
                    prompt, task_type, temperature, max_tokens
                ):
                    yield chunk
            elif tier == ModelTier.EMBEDDINGS:
                result = await self._snowflake_embedding(prompt)
                yield json.dumps(result)
            elif tier in [ModelTier.TIER_1, ModelTier.TIER_2]:
                async for chunk in self._portkey_complete(
                    prompt,
                    tier,
                    stream,
                    request_metadata,
                    model_override,
                    temperature,
                    max_tokens,
                ):
                    yield chunk
            else:
                async for chunk in self._openrouter_complete(
                    prompt,
                    stream,
                    request_metadata,
                    model_override,
                    temperature,
                    max_tokens,
                ):
                    yield chunk
            duration = time.time() - start_time
            llm_request_duration.labels(
                provider=tier.value, model=model_override or "default"
            ).observe(duration)
            llm_requests_total.labels(
                provider=tier.value,
                model=model_override or "default",
                task_type=task_type.value,
                status="success",
            ).inc()
        except Exception as e:
            logger.error(f"LLM completion error: {e}")
            llm_requests_total.labels(
                provider=tier.value,
                model=model_override or "default",
                task_type=task_type.value,
                status="error",
            ).inc()
            raise

    async def _snowflake_complete(
        self, prompt: str, task_type: TaskType, temperature: float, max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Complete using Snowflake Cortex"""
        if not self._snowflake:
            raise ValueError("Snowflake not initialized")
        cursor = None
        try:
            cursor = self._snowflake.cursor(DictCursor)
            if task_type == TaskType.SQL_GENERATION:
                query = "\n                SELECT SNOWFLAKE.CORTEX.COMPLETE(\n                    'mistral-large',\n                    CONCAT(\n                        'You are a SQL expert. Generate SQL for Snowflake based on this request: ',\n                        %s\n                    ),\n                    {'temperature': %s, 'max_tokens': %s}\n                ) as response\n                "
            else:
                query = "\n                SELECT SNOWFLAKE.CORTEX.COMPLETE(\n                    'mistral-large',\n                    %s,\n                    {'temperature': %s, 'max_tokens': %s}\n                ) as response\n                "
            cursor.execute(query, (prompt, temperature, max_tokens))
            result = cursor.fetchone()
            if result and "response" in result and result["response"]:
                data_movement_avoided.labels(operation_type="completion").inc(
                    len(prompt) / 1024
                )
                yield result["response"]
            else:
                yield "Error: No response from Snowflake Cortex"
        except Exception as e:
            logger.error(f"Snowflake Cortex error: {e}")
            yield f"Error: {e!s}"
        finally:
            if cursor:
                cursor.close()

    async def _snowflake_embedding(self, text: str) -> list[float]:
        """Generate embeddings using Snowflake Cortex"""
        if not self._snowflake:
            raise ValueError("Snowflake not initialized")
        cursor = None
        try:
            cursor = self._snowflake.cursor()
            query = "\n            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s) as embedding\n            "
            cursor.execute(query, (text,))
            result = cursor.fetchone()
            if result and result[0]:
                data_movement_avoided.labels(operation_type="embeddings").inc(
                    len(text) / 1024
                )
                return json.loads(result[0])
            else:
                return []
        except Exception as e:
            logger.error(f"Snowflake embedding error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    async def _portkey_complete(
        self,
        prompt: str,
        tier: ModelTier,
        stream: bool,
        metadata: dict,
        model_override: str | None,
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Complete using Portkey gateway"""
        if not self._portkey:
            logger.warning("Portkey not available, falling back to OpenRouter")
            async for chunk in self._openrouter_complete(
                prompt, stream, metadata, model_override, temperature, max_tokens
            ):
                yield chunk
            return
        if model_override:
            model = model_override
        elif tier == ModelTier.TIER_1:
            model = "gpt-4o"
        else:
            model = "gpt-3.5-turbo"
        try:
            if stream:
                response_stream = await llm_router.complete(
                    prompt=prompt,
                    task=TaskType.CODE_GENERATION,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    metadata=metadata,
                )
                async for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                response = await llm_router.complete(
                    prompt=prompt,
                    task=TaskType.CODE_GENERATION,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                    metadata=metadata,
                )
                if response.choices and response.choices[0].message.content:
                    yield response.choices[0].message.content
                if hasattr(response, "headers"):
                    cache_hit = response.headers.get("x-portkey-cache-status") == "hit"
                    if cache_hit:
                        llm_cache_hit_rate.labels(provider="portkey").inc()
        except Exception as e:
            logger.error(f"Portkey error: {e}")
            logger.info("Falling back to OpenRouter")
            async for chunk in self._openrouter_complete(
                prompt, stream, metadata, model_override, temperature, max_tokens
            ):
                yield chunk

    async def _openrouter_complete(
        self,
        prompt: str,
        stream: bool,
        metadata: dict,
        model_override: str | None,
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Complete using OpenRouter for experimental models"""
        if not self._openrouter:
            yield "Error: No LLM providers available"
            return
        model = model_override or "mistralai/mixtral-8x7b-instruct"
        try:
            if stream:
                response_stream = await llm_router.complete(
                    prompt=prompt,
                    task=TaskType.CODE_GENERATION,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                async for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                response = await llm_router.complete(
                    prompt=prompt,
                    task=TaskType.CODE_GENERATION,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                )
                if response.choices and response.choices[0].message.content:
                    yield response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            yield f"Error: All LLM providers failed - {e!s}"

    async def get_available_models(self) -> dict[str, list[str]]:
        """Get list of available models by provider"""
        models = {
            "snowflake": ["mistral-large", "mistral-7b", "llama2-70b-chat"],
            "portkey": [],
            "openrouter": [],
        }
        if self._portkey:
            try:
                models["portkey"] = [
                    "gpt-4o",
                    "gpt-4-turbo",
                    "gpt-3.5-turbo",
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307",
                ]
            except:
                pass
        if self._openrouter:
            try:
                models["openrouter"] = [
                    "mistralai/mixtral-8x7b-instruct",
                    "meta-llama/llama-3-70b-instruct",
                    "deepseek/deepseek-coder-v2",
                ]
            except:
                pass
        return models

    async def estimate_cost(
        self, prompt: str, task_type: TaskType, model_override: str | None = None
    ) -> dict[str, Any]:
        """Estimate cost for a completion"""
        prompt_tokens = len(prompt) / 4
        estimated_completion_tokens = 500
        tier = self.model_routing.get(task_type, ModelTier.TIER_2)
        cost_map = {
            ModelTier.SNOWFLAKE: 0.0001,
            ModelTier.TIER_1: 0.03,
            ModelTier.TIER_2: 0.002,
            ModelTier.TIER_3: 0.0001,
        }
        base_cost = cost_map.get(tier, 0.001)
        total_tokens = prompt_tokens + estimated_completion_tokens
        estimated_cost = total_tokens / 1000 * base_cost
        return {
            "estimated_cost_usd": estimated_cost,
            "prompt_tokens": prompt_tokens,
            "estimated_completion_tokens": estimated_completion_tokens,
            "tier": tier.value,
        }

    async def close(self):
        """Clean up connections"""
        if self._snowflake:
            self._snowflake.close()
        self.initialized = False


_unified_llm_service = None


async def get_unified_llm_service() -> UnifiedLLMService:
    """Get or create the unified LLM service singleton"""
    global _unified_llm_service
    if _unified_llm_service is None:
        _unified_llm_service = UnifiedLLMService()
        await _unified_llm_service.initialize()
    return _unified_llm_service
