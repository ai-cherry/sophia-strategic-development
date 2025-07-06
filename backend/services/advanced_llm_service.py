import json
import logging
from typing import Literal, Any

import tiktoken
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from backend.core.auto_esc_config import get_config_value
from backend.services.constitutional_ai import ConstitutionalAI

logger = logging.getLogger(__name__)

Provider = Literal["portkey", "openrouter", "openai", "anthropic"]


class AdvancedLLMService:
    """
    Enhanced LLM service with an intelligent routing gateway for multiple providers.
    Routes requests to Portkey (primary), OpenRouter (cost/specialized),
    or directly to OpenAI/Anthropic based on defined strategies.
    """

    def __init__(self):
        self._initialize_clients()
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        self.constitutional_ai = ConstitutionalAI()
        self.token_limit = 8192  # Default for gpt-4, can be model-specific
        logger.info("AdvancedLLMService initialized with multi-provider support.")

    def _initialize_clients(self):
        """Initializes API clients based on configuration."""
        self.clients = {}
        if get_config_value("llm.portkey.enabled", True):
            # Portkey uses standard OpenAI client with a special base_url
            self.clients["portkey"] = AsyncOpenAI(
                api_key=get_config_value("portkey_api_key"),
                base_url="https://api.portkey.ai/v1",
            )
        if get_config_value("llm.openrouter.enabled", True):
            self.clients["openrouter"] = AsyncOpenAI(
                api_key=get_config_value("openrouter_api_key"),
                base_url="https://openrouter.ai/api/v1",
            )
        if get_config_value("llm.openai.enabled", True):
            self.clients["openai"] = AsyncOpenAI(
                api_key=get_config_value("openai_api_key")
            )
        if get_config_value("llm.anthropic.enabled", False):
            self.clients["anthropic"] = AsyncAnthropic(
                api_key=get_config_value("anthropic_api_key")
            )

    def _determine_routing_strategy(self, query: str, context: dict) -> Provider:
        """Determines which provider to use based on query and context."""
        # This is where sophisticated routing logic will go.
        # For now, it's a simple placeholder.
        # Example logic:
        # if context.get("task_priority") == "high": return "portkey"
        # if "generate code" in query: return "openai"
        # if "long context" in query: return "anthropic"
        # if context.get("cost_sensitive"): return "openrouter"

        # Default to Portkey if available, else OpenRouter, else OpenAI
        if "portkey" in self.clients:
            return "portkey"
        if "openrouter" in self.clients:
            return "openrouter"
        if "openai" in self.clients:
            return "openai"
        return "anthropic"  # Fallback

    async def synthesize_response(
        self,
        query: str,
        context: dict,
        results: list[dict],
        use_constitutional_ai: bool = True,
    ) -> str:
        """Generate response with intelligent routing and advanced prompt engineering"""
        provider = self._determine_routing_strategy(query, context)
        client = self.clients.get(provider)

        if not client:
            raise ValueError(f"Provider '{provider}' is not enabled or configured.")

        processed_data = self._prepare_data_for_llm(results)
        prompt = self._build_advanced_prompt(query, context, processed_data)

        if self._exceeds_token_limit(prompt, provider):
            logger.warning(f"Prompt exceeds token limit for {provider}, compressing...")
            prompt = self._compress_prompt(prompt, provider)

        logger.info(f"Routing LLM request to provider: {provider}")

        if provider in ["portkey", "openrouter", "openai"]:
            response = await self._generate_openai_compatible_response(
                client, prompt, provider
            )
        elif provider == "anthropic":
            response = await self._generate_anthropic_response(client, prompt)
        else:
            raise ValueError(f"Unknown provider routing: {provider}")

        if use_constitutional_ai:
            response = await self.constitutional_ai.review_and_revise(response, query)

        return response

    async def _generate_openai_compatible_response(
        self, client: AsyncOpenAI, prompt: str, provider: str
    ) -> str:
        """Generates a response using an OpenAI-compatible client (OpenAI, Portkey, OpenRouter)."""
        model = get_config_value(f"llm.{provider}.model", "gpt-4")
        try:
            completion = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"{provider} API error: {e}")
            raise

    async def _generate_anthropic_response(
        self, client: AsyncAnthropic, prompt: str
    ) -> str:
        """Generates a response using the Anthropic client."""
        model = get_config_value("llm.anthropic.model", "claude-3-sonnet-20240229")
        try:
            completion = await client.messages.create(
                model=model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            # Handle list of content blocks
            response_text = ""
            for block in completion.content:
                if hasattr(block, "text"):
                    response_text += block.text
            return response_text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _prepare_data_for_llm(self, results: list[dict]) -> str:
        if not results:
            return "No data available."
        return json.dumps(results, indent=2, default=str)

    def _build_advanced_prompt(self, query: str, context: dict, data: str) -> str:
        return f"""
You are Sophia AI, an executive assistant providing business intelligence.

Context: {json.dumps(context, indent=2, default=str)}

Available Data:
{data}

User Query: "{query}"

Based *only* on the provided context and data, provide a comprehensive, actionable response. Follow these steps:
1. **Main Finding:** Start with a one-sentence summary of the key takeaway.
2. **Key Data Points:** Present the most relevant data in a structured format (e.g., bullet points, table).
3. **Critical Insights:** Identify 1-2 non-obvious insights based on the data.
4. **Actionable Next Steps:** Suggest 1-2 concrete actions the user can take.
"""

    def _exceeds_token_limit(self, text: str, provider: str) -> bool:
        # In a real system, we'd have model-specific token limits
        return len(self.tokenizer.encode(text)) > self.token_limit

    def _compress_prompt(self, prompt: str, provider: str) -> str:
        tokens = self.tokenizer.encode(prompt)
        if len(tokens) > self.token_limit:
            tokens = tokens[: self.token_limit]
        return self.tokenizer.decode(tokens)

    async def _execute_with_quality_assurance(self, request_data: dict[str, Any]) -> str:
        """Execute request with quality assurance measures"""
        pass

    async def _get_model_for_task(
        self, query: str, context: str | None
    ) -> Literal["high_quality", "balanced", "cost_effective"]:
        """Select the best model for a given task"""
        pass

    def _get_provider_for_task(
        self, task: str, provider: str = "default"  # noqa: ARG002
    ) -> Literal["openai", "anthropic", "google"]:
        """Select the best provider for a given task"""
        pass

    def _get_model_for_provider(
        self, provider: str, model: str = "default" # noqa: ARG002
    ) -> str:
        """Select the best model for a given provider"""
        pass

    def _get_llm_config(self, model: str) -> dict:
        pass

    async def _validate_response_quality(self, response: str) -> bool:
        """Validate response quality against defined criteria"""
        pass

    async def _quality_fallback(self) -> str:
        """Fallback mechanism if quality check fails"""
        pass
    
    def get_quality_config(self) -> dict[str, Any]:
        """Returns the quality configuration for the service."""
        return self.quality_config
        
    def get_supported_providers(self) -> list[str]:
        """Returns a list of supported LLM providers."""
        return self.supported_providers
