import json
import logging
from typing import Any

import tiktoken

from backend.services.constitutional_ai import ConstitutionalAI
from infrastructure.services.enhanced_portkey_llm_gateway import (
    TaskComplexity,
    get_enhanced_portkey_gateway,
)

logger = logging.getLogger(__name__)

class AdvancedLLMService:
    """
    Advanced LLM service with unified gateway routing.

    CRITICAL: All LLM interactions route through the unified LLM gateway
    to ensure centralized control, caching, monitoring, and cost optimization.

    This service provides advanced prompt engineering and constitutional AI
    while maintaining compliance with the unified LLM strategy.
    """

    def __init__(self):
        self.llm_gateway = None  # Will be initialized lazily
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        self.constitutional_ai = ConstitutionalAI()
        self.token_limit = 8192  # Default for gpt-4, can be model-specific
        logger.info("AdvancedLLMService initialized with unified gateway routing.")

    async def _ensure_gateway_initialized(self):
        """Ensure the unified LLM gateway is initialized"""
        if self.llm_gateway is None:
            self.llm_gateway = await get_enhanced_portkey_gateway()

    def _determine_task_complexity(self, query: str, context: dict) -> str:
        """Determine task complexity for intelligent routing"""
        # Analyze query and context to determine complexity
        query_lower = query.lower()

        # High complexity indicators
        if any(
            indicator in query_lower
            for indicator in [
                "analyze",
                "synthesize",
                "strategic",
                "complex",
                "detailed analysis",
                "comprehensive",
                "executive",
                "board",
                "strategic planning",
            ]
        ):
            return "high"

        # Medium complexity indicators
        if any(
            indicator in query_lower
            for indicator in ["explain", "summarize", "compare", "evaluate", "assess"]
        ):
            return "medium"

        # Consider context factors
        if context.get("executive_level", False):
            return "high"

        if context.get("task_priority") == "high":
            return "high"

        # Default to medium for balanced performance/cost
        return "medium"

    def _determine_routing_preference(self, query: str, context: dict) -> str:
        """Determine routing preference for the gateway"""
        # Map complexity and context to routing preferences
        complexity = self._determine_task_complexity(query, context)

        if complexity == "high":
            return "quality"  # Route to best models via Portkey
        elif context.get("cost_sensitive", False):
            return "cost"  # Route to cost-effective models
        elif "code" in query.lower() or "technical" in query.lower():
            return "balanced"  # Good balance for technical tasks
        else:
            return "balanced"  # Default balanced routing

    async def synthesize_response(
        self,
        query: str,
        context: dict,
        results: list[dict],
        use_constitutional_ai: bool = True,
    ) -> str:
        """
        Generate response with unified gateway routing and advanced prompt engineering

        IMPORTANT: This method now routes ALL requests through the unified LLM gateway
        instead of direct client instantiation, ensuring compliance with the unified LLM strategy.
        """
        await self._ensure_gateway_initialized()

        # Prepare data and build advanced prompt
        processed_data = self._prepare_data_for_llm(results)
        prompt = self._build_advanced_prompt(query, context, processed_data)

        # Check token limits and compress if needed
        if self._exceeds_token_limit(prompt):
            logger.warning("Prompt exceeds token limit, compressing...")
            prompt = self._compress_prompt(prompt)

        # Determine routing strategy
        routing_preference = self._determine_routing_preference(query, context)
        task_complexity = self._determine_task_complexity(query, context)

        logger.info(
            f"Routing LLM request through unified gateway - complexity: {task_complexity}, preference: {routing_preference}"
        )

        try:
            # Route through unified LLM gateway
            messages = [{"role": "user", "content": prompt}]

            # Convert our parameters to gateway format
            gateway_task_type = (
                "business_intelligence" if context.get("executive_level") else "general"
            )

            # Map routing preference to cost preference
            cost_preference_map = {
                "quality": "premium_mode",
                "balanced": "balanced_mode",
                "cost": "budget_mode",
            }
            cost_preference = cost_preference_map.get(
                routing_preference, "balanced_mode"
            )

            # Map task complexity to gateway complexity
            complexity_map = {
                "high": TaskComplexity.COMPLEX,
                "medium": TaskComplexity.MODERATE,
                "low": TaskComplexity.SIMPLE,
            }
            gateway_complexity = complexity_map.get(
                task_complexity, TaskComplexity.MODERATE
            )

            # Collect response chunks
            response_chunks = []
            async for chunk in self.llm_gateway.complete(
                messages=messages,
                task_type=gateway_task_type,
                complexity=gateway_complexity,
                cost_preference=cost_preference,
                temperature=0.7,
                max_tokens=2048,
                stream=False,
            ):
                response_chunks.append(chunk)

            response = "".join(response_chunks)

            # Apply constitutional AI if requested
            if use_constitutional_ai:
                response = await self.constitutional_ai.review_and_revise(
                    response, query
                )

            return response

        except Exception as e:
            logger.exception(f"Unified gateway error: {e}")
            # Fallback through gateway's built-in fallback mechanisms
            raise ValueError(f"LLM request failed through unified gateway: {e!s}")

    def _prepare_data_for_llm(self, results: list[dict]) -> str:
        """Prepare data for LLM consumption"""
        if not results:
            return "No data available."
        return json.dumps(results, indent=2, default=str)

    def _build_advanced_prompt(self, query: str, context: dict, data: str) -> str:
        """Build advanced prompt with business intelligence focus"""
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

    def _exceeds_token_limit(self, text: str) -> bool:
        """Check if text exceeds token limit"""
        return len(self.tokenizer.encode(text)) > self.token_limit

    def _compress_prompt(self, prompt: str) -> str:
        """Compress prompt to fit token limits"""
        tokens = self.tokenizer.encode(prompt)
        if len(tokens) > self.token_limit:
            tokens = tokens[: self.token_limit]
        return self.tokenizer.decode(tokens)

    async def _validate_response_quality(self, response: str) -> bool:
        """Validate response quality against defined criteria"""
        # Basic quality checks
        if not response or len(response.strip()) < 10:
            return False

        # Check for error messages
        error_indicators = ["error:", "failed:", "unable to", "cannot process"]
        return not any(indicator in response.lower() for indicator in error_indicators)

    async def _quality_fallback(self) -> str:
        """Fallback mechanism if quality check fails"""
        return "I apologize, but I'm unable to provide a comprehensive response at this time. Please try rephrasing your question or contact support if the issue persists."

    def get_quality_config(self) -> dict[str, Any]:
        """Returns the quality configuration for the service."""
        return {
            "constitutional_ai_enabled": True,
            "quality_validation_enabled": True,
            "unified_gateway_routing": True,
            "token_limit": self.token_limit,
            "temperature": 0.7,
            "max_tokens": 2048,
        }

    def get_supported_providers(self) -> list[str]:
        """Returns supported providers (now unified through gateway)"""
        return ["unified_gateway"]  # All providers accessed through unified gateway

    def get_routing_info(self) -> dict[str, Any]:
        """Get information about current routing configuration"""
        return {
            "gateway_type": "unified_llm_gateway",
            "routing_strategy": "intelligent_complexity_based",
            "constitutional_ai": True,
            "centralized_caching": True,
            "cost_optimization": True,
            "fallback_mechanisms": True,
        }
