"""
Unified LLM Service for Sophia AI
Centralizes all LLM interactions with intelligent routing
"""

import json
import time
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum

try:
    from portkey_ai import AsyncPortkey
except ImportError:
    AsyncPortkey = None

import snowflake.connector
from openai import AsyncOpenAI
from snowflake.connector import DictCursor

from backend.core.config_manager import ConfigManager
from backend.monitoring.llm_metrics import (
    data_movement_avoided,
    llm_cache_hit_rate,
    llm_request_duration,
    llm_requests_total,
)
from backend.utils.custom_logger import logger


class ModelTier(Enum):
    """Model tier classification for routing"""

    SNOWFLAKE = "snowflake"  # Primary for data operations
    TIER_1 = "tier_1"  # GPT-4, Claude-3-Opus (via Portkey)
    TIER_2 = "tier_2"  # GPT-3.5, Claude-Haiku (via Portkey)
    TIER_3 = "tier_3"  # Llama, Mixtral (via OpenRouter)
    EMBEDDINGS = "embeddings"  # Snowflake Cortex


class TaskType(Enum):
    """Task types for intelligent routing"""

    DATA_ANALYSIS = "data_analysis"  # Use Snowflake
    SQL_GENERATION = "sql_generation"  # Use Snowflake
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
        self.config = ConfigManager()
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

        api_key = self.config.get_value("portkey_api_key")
        if not api_key:
            logger.warning("Portkey API key not found")
            return None

        return AsyncPortkey(
            api_key=api_key,
            # Virtual keys for different providers
            virtual_keys={
                "openai": self.config.get_value("portkey_virtual_key_openai", ""),
                "anthropic": self.config.get_value("portkey_virtual_key_anthropic", ""),
            },
            # Performance-optimized config
            config={
                "cache": {
                    "mode": "semantic",
                    "threshold": 0.95,
                    "ttl": 3600,
                    "max_size": 1000,  # Maximum cached items
                    "enabled": True,  # Explicitly enable caching
                },
                "retry": {
                    "attempts": 3,
                    "on_status_codes": [429, 500, 502, 503, 504],
                },
                "request_timeout": 30000,
            },
        )

    def _init_openrouter(self) -> AsyncOpenAI | None:
        """Initialize OpenRouter client"""
        api_key = self.config.get_value("openrouter_api_key")
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
                user=self.config.get_value("snowflake_user"),
                password=self.config.get_value("snowflake_password"),
                account=self.config.get_value("snowflake_account"),
                warehouse=self.config.get_value("snowflake_warehouse", "COMPUTE_WH"),
                database=self.config.get_value("snowflake_database", "SOPHIA_AI"),
                schema=self.config.get_value("snowflake_schema", "CORE"),
            )
            return conn
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake: {e}")
            return None

    def _init_model_routing(self) -> dict[TaskType, ModelTier]:
        """CEO-configurable task-to-tier mapping"""
        return {
            # Snowflake-first for data operations
            TaskType.DATA_ANALYSIS: ModelTier.SNOWFLAKE,
            TaskType.SQL_GENERATION: ModelTier.SNOWFLAKE,
            TaskType.EMBEDDINGS: ModelTier.EMBEDDINGS,
            # External LLMs for other tasks
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

        # Add metadata for tracking
        request_metadata = {
            "task_type": task_type.value,
            "tier": tier.value,
            "source": "sophia_ai",
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }

        try:
            if tier == ModelTier.SNOWFLAKE:
                # Use Snowflake Cortex for data operations
                async for chunk in self._snowflake_complete(
                    prompt, task_type, temperature, max_tokens
                ):
                    yield chunk

            elif tier == ModelTier.EMBEDDINGS:
                # Use Snowflake Cortex for embeddings
                result = await self._snowflake_embedding(prompt)
                yield json.dumps(result)

            elif tier in [ModelTier.TIER_1, ModelTier.TIER_2]:
                # Use Portkey for primary models
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
                # Use OpenRouter for experimental/cost-optimized models
                async for chunk in self._openrouter_complete(
                    prompt,
                    stream,
                    request_metadata,
                    model_override,
                    temperature,
                    max_tokens,
                ):
                    yield chunk

            # Track metrics
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

            # Use appropriate Cortex function based on task
            if task_type == TaskType.SQL_GENERATION:
                query = """
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'mistral-large',
                    CONCAT(
                        'You are a SQL expert. Generate SQL for Snowflake based on this request: ',
                        %s
                    ),
                    {'temperature': %s, 'max_tokens': %s}
                ) as response
                """
            else:
                query = """
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'mistral-large',
                    %s,
                    {'temperature': %s, 'max_tokens': %s}
                ) as response
                """

            cursor.execute(query, (prompt, temperature, max_tokens))
            result = cursor.fetchone()

            if result and "response" in result and result["response"]:
                # Track data locality benefit
                data_movement_avoided.labels(operation_type="completion").inc(
                    len(prompt) / 1024
                )  # Track in KB

                yield result["response"]
            else:
                yield "Error: No response from Snowflake Cortex"

        except Exception as e:
            logger.error(f"Snowflake Cortex error: {e}")
            yield f"Error: {str(e)}"
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

            query = """
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s) as embedding
            """

            cursor.execute(query, (text,))
            result = cursor.fetchone()

            if result and result[0]:
                # Track data locality benefit
                data_movement_avoided.labels(operation_type="embeddings").inc(
                    len(text) / 1024
                )  # Track in KB

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
            # Fallback to OpenRouter if Portkey not available
            logger.warning("Portkey not available, falling back to OpenRouter")
            async for chunk in self._openrouter_complete(
                prompt, stream, metadata, model_override, temperature, max_tokens
            ):
                yield chunk
            return

        # Select model based on tier
        if model_override:
            model = model_override
        elif tier == ModelTier.TIER_1:
            model = "gpt-4o"  # Or claude-3-opus-20240229
        else:
            model = "gpt-3.5-turbo"  # Or claude-3-haiku-20240307

        try:
            response = await self._portkey.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                metadata=metadata,
            )

            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

            # Check for cache hit
            if hasattr(response, "headers"):
                cache_hit = response.headers.get("x-portkey-cache-status") == "hit"
                if cache_hit:
                    llm_cache_hit_rate.labels(provider="portkey").inc()

        except Exception as e:
            logger.error(f"Portkey error: {e}")
            # Fallback to OpenRouter
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

        # Default to cost-effective model
        model = model_override or "mistralai/mixtral-8x7b-instruct"

        try:
            response = await self._openrouter.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )

            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            yield f"Error: All LLM providers failed - {str(e)}"

    async def get_available_models(self) -> dict[str, list[str]]:
        """Get list of available models by provider"""
        models = {
            "snowflake": ["mistral-large", "mistral-7b", "llama2-70b-chat"],
            "portkey": [],
            "openrouter": [],
        }

        # Get Portkey models if available
        if self._portkey:
            try:
                # This would call Portkey's model listing API
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

        # Get OpenRouter models if available
        if self._openrouter:
            try:
                # This would call OpenRouter's model listing API
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
    ) -> dict[str, float]:
        """Estimate cost for a completion"""
        # Rough token estimation (4 chars per token)
        prompt_tokens = len(prompt) / 4
        estimated_completion_tokens = 500  # Average

        tier = self.model_routing.get(task_type, ModelTier.TIER_2)

        # Cost per 1K tokens (approximate)
        cost_map = {
            ModelTier.SNOWFLAKE: 0.0001,  # Snowflake compute cost
            ModelTier.TIER_1: 0.03,  # GPT-4 level
            ModelTier.TIER_2: 0.002,  # GPT-3.5 level
            ModelTier.TIER_3: 0.0001,  # Open models
        }

        base_cost = cost_map.get(tier, 0.001)
        total_tokens = prompt_tokens + estimated_completion_tokens
        estimated_cost = (total_tokens / 1000) * base_cost

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


# Singleton instance
_unified_llm_service = None


async def get_unified_llm_service() -> UnifiedLLMService:
    """Get or create the unified LLM service singleton"""
    global _unified_llm_service
    if _unified_llm_service is None:
        _unified_llm_service = UnifiedLLMService()
        await _unified_llm_service.initialize()
    return _unified_llm_service
