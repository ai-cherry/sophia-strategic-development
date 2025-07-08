"""
Fallback Chain for LLM Router
Implements ordered provider fallback for resilience
"""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from backend.core.auto_esc_config import get_config_value
from shared.utils.custom_logger import logger

from .config_schema import LLMRouterConfig
from .enums import Provider, TaskComplexity, TaskType
from .metrics import llm_fallback_attempts, llm_fallback_level


@dataclass
class FallbackProvider:
    """Fallback provider configuration"""

    provider: Provider
    client: Any
    priority: int
    max_retries: int = 3
    timeout: float = 30.0


class FallbackChain:
    """
    Manages fallback chain for LLM providers
    Ensures resilience when primary providers fail
    """

    def __init__(self, config: LLMRouterConfig):
        self.config = config
        self.providers: list[FallbackProvider] = []
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize fallback providers in priority order"""
        # Primary: Portkey (OpenAI/Anthropic gateway)
        if get_config_value("portkey_api_key"):
            self.providers.append(
                FallbackProvider(
                    provider=Provider.PORTKEY,
                    client=None,  # Will be initialized on demand
                    priority=1,
                )
            )

        # Secondary: OpenRouter (200+ models)
        if get_config_value("openrouter_api_key"):
            self.providers.append(
                FallbackProvider(
                    provider=Provider.OPENROUTER,
                    client=None,  # Will be initialized on demand
                    priority=2,
                )
            )

        # Tertiary: Direct OpenAI
        if get_config_value("openai_api_key"):
            self.providers.append(
                FallbackProvider(
                    provider=Provider.OPENAI,
                    client=None,  # Will be initialized on demand
                    priority=3,
                )
            )

        # Quaternary: Direct Anthropic
        if get_config_value("anthropic_api_key"):
            self.providers.append(
                FallbackProvider(
                    provider=Provider.ANTHROPIC,
                    client=None,  # Will be initialized on demand
                    priority=4,
                )
            )

        # Sort by priority
        self.providers.sort(key=lambda x: x.priority)

        logger.info(f"Initialized fallback chain with {len(self.providers)} providers")

    async def complete(
        self, prompt: str, task: TaskType, complexity: TaskComplexity, **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Complete request using fallback chain
        Tries each provider in order until success
        """
        last_error = None

        for i, provider in enumerate(self.providers):
            try:
                # Update fallback level metric
                llm_fallback_level.labels(provider=provider.provider.value).set(i)

                logger.info(
                    f"Attempting fallback provider {i+1}/{len(self.providers)}: {provider.provider.value}"
                )

                # Initialize client if needed
                if not provider.client:
                    provider.client = await self._initialize_client(provider)

                # Attempt completion
                async for chunk in self._complete_with_provider(
                    provider, prompt, task, complexity, **kwargs
                ):
                    yield chunk

                # Success - reset fallback level
                llm_fallback_level.labels(provider=provider.provider.value).set(0)

                # Track successful fallback
                if i > 0:
                    llm_fallback_attempts.labels(
                        from_provider=self.providers[i - 1].provider.value,
                        to_provider=provider.provider.value,
                        reason="provider_failure",
                    ).inc()

                return

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Fallback provider {provider.provider.value} failed: {e}"
                )

                # Track failed attempt
                if i < len(self.providers) - 1:
                    llm_fallback_attempts.labels(
                        from_provider=provider.provider.value,
                        to_provider=self.providers[i + 1].provider.value,
                        reason=type(e).__name__,
                    ).inc()

        # All providers failed
        logger.error(f"All fallback providers failed. Last error: {last_error}")
        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    async def _initialize_client(self, provider: FallbackProvider) -> Any:
        """Initialize client for specific provider"""
        if provider.provider == Provider.PORTKEY:
            return await self._init_portkey_client()
        elif provider.provider == Provider.OPENROUTER:
            return self._init_openrouter_client()
        elif provider.provider == Provider.OPENAI:
            return self._init_openai_client()
        elif provider.provider == Provider.ANTHROPIC:
            return self._init_anthropic_client()
        else:
            raise ValueError(f"Unknown provider: {provider.provider}")

    async def _init_portkey_client(self):
        """Initialize Portkey client"""
        try:
            from portkey_ai import AsyncPortkey

            return AsyncPortkey(
                api_key=get_config_value("portkey_api_key"),
                config={
                    "retry": {
                        "attempts": 3,
                        "on_status_codes": [429, 500, 502, 503, 504],
                    },
                    "request_timeout": 30000,
                },
            )
        except ImportError:
            logger.error("Portkey package not installed")
            return None

    def _init_openrouter_client(self):
        """Initialize OpenRouter client"""
        from openai import AsyncOpenAI

        return AsyncOpenAI(
            api_key=get_config_value("openrouter_api_key"),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://sophia-intel.ai",
                "X-Title": "Sophia AI",
            },
        )

    def _init_openai_client(self):
        """Initialize OpenAI client"""
        from openai import AsyncOpenAI

        return AsyncOpenAI(api_key=get_config_value("openai_api_key"))

    def _init_anthropic_client(self):
        """Initialize Anthropic client"""
        try:
            from anthropic import AsyncAnthropic

            return AsyncAnthropic(api_key=get_config_value("anthropic_api_key"))
        except ImportError:
            logger.error("Anthropic package not installed")
            return None

    async def _complete_with_provider(
        self,
        provider: FallbackProvider,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Complete request with specific provider"""
        if not provider.client:
            raise ValueError(f"Client not initialized for {provider.provider.value}")

        # Map to appropriate completion method based on provider
        if provider.provider == Provider.PORTKEY:
            async for chunk in self._complete_portkey(
                provider.client, prompt, task, complexity, **kwargs
            ):
                yield chunk

        elif provider.provider == Provider.OPENROUTER:
            async for chunk in self._complete_openrouter(
                provider.client, prompt, task, complexity, **kwargs
            ):
                yield chunk

        elif provider.provider == Provider.OPENAI:
            async for chunk in self._complete_openai(
                provider.client, prompt, task, complexity, **kwargs
            ):
                yield chunk

        elif provider.provider == Provider.ANTHROPIC:
            async for chunk in self._complete_anthropic(
                provider.client, prompt, task, complexity, **kwargs
            ):
                yield chunk

    async def _complete_portkey(
        self, client, prompt: str, task: TaskType, complexity: TaskComplexity, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Complete using Portkey"""
        model = self._select_model_for_task(task, complexity, "portkey")

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=kwargs.get("stream", True),
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
        )

        if kwargs.get("stream", True):
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            if response.choices and response.choices[0].message.content:
                yield response.choices[0].message.content

    async def _complete_openrouter(
        self, client, prompt: str, task: TaskType, complexity: TaskComplexity, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Complete using OpenRouter"""
        model = self._select_model_for_task(task, complexity, "openrouter")

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=kwargs.get("stream", True),
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
        )

        if kwargs.get("stream", True):
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            if response.choices and response.choices[0].message.content:
                yield response.choices[0].message.content

    async def _complete_openai(
        self, client, prompt: str, task: TaskType, complexity: TaskComplexity, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Complete using direct OpenAI"""
        model = self._select_model_for_task(task, complexity, "openai")

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=kwargs.get("stream", True),
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
        )

        if kwargs.get("stream", True):
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            if response.choices and response.choices[0].message.content:
                yield response.choices[0].message.content

    async def _complete_anthropic(
        self, client, prompt: str, task: TaskType, complexity: TaskComplexity, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Complete using direct Anthropic"""
        model = self._select_model_for_task(task, complexity, "anthropic")

        response = await client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.7),
        )

        if hasattr(response, "content") and response.content:
            yield response.content[0].text

    def _select_model_for_task(
        self, task: TaskType, complexity: TaskComplexity, provider: str
    ) -> str:
        """Select appropriate model based on task and provider"""
        # Simplified model selection - in production use config
        model_map = {
            "portkey": {
                TaskComplexity.SIMPLE: "gpt-3.5-turbo",
                TaskComplexity.MODERATE: "gpt-4",
                TaskComplexity.COMPLEX: "gpt-4o",
                TaskComplexity.ARCHITECTURE: "claude-3-opus-20240229",
            },
            "openrouter": {
                TaskComplexity.SIMPLE: "openai/gpt-3.5-turbo",
                TaskComplexity.MODERATE: "mistralai/mixtral-8x7b-instruct",
                TaskComplexity.COMPLEX: "openai/gpt-4",
                TaskComplexity.ARCHITECTURE: "anthropic/claude-3-opus",
            },
            "openai": {
                TaskComplexity.SIMPLE: "gpt-3.5-turbo",
                TaskComplexity.MODERATE: "gpt-4",
                TaskComplexity.COMPLEX: "gpt-4o",
                TaskComplexity.ARCHITECTURE: "gpt-4o",
            },
            "anthropic": {
                TaskComplexity.SIMPLE: "claude-3-haiku-20240307",
                TaskComplexity.MODERATE: "claude-3-sonnet-20240229",
                TaskComplexity.COMPLEX: "claude-3-opus-20240229",
                TaskComplexity.ARCHITECTURE: "claude-3-opus-20240229",
            },
        }

        return model_map.get(provider, {}).get(complexity, "gpt-4")
