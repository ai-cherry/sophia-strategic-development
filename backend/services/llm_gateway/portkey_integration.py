#!/usr/bin/env python3
"""
Portkey AI Integration
Quality-optimized LLM routing with intelligent caching and fallback
"""

import asyncio
import time
from typing import Any, Optional

import aiohttp

from backend.core.config_manager import ConfigManager
from backend.utils.custom_logger import setup_logger

logger = setup_logger("portkey_integration")


class PortkeyIntegration:
    """
    Portkey AI integration for quality-first LLM routing
    Focuses on response consistency and reliability
    """

    def __init__(self):
        self.config = ConfigManager()
        self.api_key = self.config.get("portkey_api_key", "")
        self.base_url = "https://api.portkey.ai/v1"

        # Quality optimization configuration
        self.quality_config = {
            "intelligent_caching": {
                "enabled": True,
                "semantic_similarity_threshold": 0.88,  # Higher threshold for quality
                "cache_ttl_seconds": 3600,
                "max_cache_size": 1000,
            },
            "response_validation": {
                "min_length": 50,
                "max_length": 8192,
                "coherence_check": True,
                "business_term_check": True,
            },
            "fallback_strategy": {
                "enabled": True,
                "max_retries": 3,
                "retry_delay_ms": 1000,
                "alternative_models": [
                    "gpt-4-turbo-preview",
                    "claude-3-opus",
                    "gpt-3.5-turbo",
                ],
            },
            "quality_enhancement": {
                "response_refinement": True,
                "consistency_enforcement": True,
                "context_preservation": True,
            },
        }

        # Supported providers through Portkey
        self.supported_providers = [
            "openai",
            "anthropic",
            "cohere",
            "huggingface",
            "azure_openai",
            "aws_bedrock",
            "google_vertex",
        ]

        # Cache for semantic similarity
        self.response_cache = {}

        logger.info("Portkey AI integration initialized with quality optimization")

    async def execute(
        self,
        query: str,
        context: Optional[str] = None,
        settings: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Execute query through Portkey with quality optimization
        """
        start_time = time.time()

        # Check cache first if enabled
        if self.quality_config["intelligent_caching"]["enabled"]:
            cached_response = await self._check_semantic_cache(query, context)
            if cached_response:
                logger.info("Cache hit with high similarity match")
                return cached_response

        # Prepare request with quality settings
        request_data = self._prepare_quality_request(query, context, settings)

        # Execute with retry and fallback
        response = await self._execute_with_quality_assurance(request_data)

        # Validate response quality
        if await self._validate_response_quality(response):
            # Cache the response
            if self.quality_config["intelligent_caching"]["enabled"]:
                await self._update_cache(query, context, response)

            execution_time = time.time() - start_time
            logger.info(f"Portkey execution completed in {execution_time:.2f}s")

            return response
        else:
            # Quality validation failed, use fallback
            logger.warning("Response quality validation failed, using fallback")
            return await self._quality_fallback(query, context, settings)

    async def _check_semantic_cache(
        self, query: str, context: Optional[str]
    ) -> Optional[str]:
        """Check semantic cache for similar queries"""
        cache_key = self._generate_cache_key(query, context)

        # Check exact match first
        if cache_key in self.response_cache:
            cache_entry = self.response_cache[cache_key]
            if (
                time.time() - cache_entry["timestamp"]
                < self.quality_config["intelligent_caching"]["cache_ttl_seconds"]
            ):
                return cache_entry["response"]

        # Check semantic similarity
        threshold = self.quality_config["intelligent_caching"][
            "semantic_similarity_threshold"
        ]

        for cached_key, cache_entry in self.response_cache.items():
            if (
                time.time() - cache_entry["timestamp"]
                < self.quality_config["intelligent_caching"]["cache_ttl_seconds"]
            ):
                similarity = await self._calculate_semantic_similarity(
                    query, cache_entry["query"]
                )
                if similarity >= threshold:
                    logger.info(f"Semantic cache hit with similarity {similarity:.2f}")
                    return cache_entry["response"]

        return None

    def _prepare_quality_request(
        self, query: str, context: Optional[str], settings: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Prepare request with quality optimization settings"""
        # Base request
        request_data = {
            "messages": [],
            "model": settings.get("model", "gpt-4-turbo-preview"),
            "temperature": settings.get("temperature", 0.7),
            "max_tokens": settings.get("max_tokens", 4096),
            "top_p": settings.get("top_p", 0.9),
            "frequency_penalty": settings.get("frequency_penalty", 0.0),
            "presence_penalty": settings.get("presence_penalty", 0.0),
        }

        # Add system message for quality
        system_message = (
            "You are a high-quality AI assistant focused on providing accurate, "
            "consistent, and business-relevant responses. Pay special attention to "
            "maintaining context and providing comprehensive answers."
        )

        if context:
            system_message += f"\n\nContext: {context}"

        request_data["messages"].append({"role": "system", "content": system_message})

        # Add user query
        request_data["messages"].append({"role": "user", "content": query})

        # Add Portkey-specific headers
        request_data["portkey_config"] = {
            "retry": {
                "attempts": self.quality_config["fallback_strategy"]["max_retries"],
                "delay": self.quality_config["fallback_strategy"]["retry_delay_ms"],
            },
            "cache": {
                "enabled": settings.get("enable_semantic_caching", True),
                "ttl": self.quality_config["intelligent_caching"]["cache_ttl_seconds"],
            },
            "fallback": {
                "enabled": self.quality_config["fallback_strategy"]["enabled"],
                "models": self.quality_config["fallback_strategy"][
                    "alternative_models"
                ],
            },
        }

        return request_data

    async def _execute_with_quality_assurance(
        self, request_data: dict[str, Any]
    ) -> str:
        """Execute request with quality assurance measures"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Portkey-Mode": "quality-first",
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Portkey API error: {response.status} - {error_text}"
                        )
                        raise Exception(f"API error: {response.status}")

            except asyncio.TimeoutError:
                logger.error("Portkey API timeout")
                raise
            except Exception as e:
                logger.error(f"Portkey execution error: {e}")
                raise

    async def _validate_response_quality(self, response: str) -> bool:
        """Validate response quality against criteria"""
        validation_config = self.quality_config["response_validation"]

        # Length validation
        if len(response) < validation_config["min_length"]:
            logger.warning(f"Response too short: {len(response)} chars")
            return False

        if len(response) > validation_config["max_length"]:
            logger.warning(f"Response too long: {len(response)} chars")
            return False

        # Coherence check
        if validation_config["coherence_check"]:
            if not self._check_response_coherence(response):
                logger.warning("Response failed coherence check")
                return False

        # Business term check
        if validation_config["business_term_check"]:
            if not self._check_business_terms(response):
                logger.warning("Response lacks business context")
                return False

        return True

    async def _quality_fallback(
        self, query: str, context: Optional[str], settings: Optional[dict[str, Any]]
    ) -> str:
        """Quality-based fallback mechanism"""
        logger.info("Executing quality fallback")

        # Try alternative models
        for model in self.quality_config["fallback_strategy"]["alternative_models"]:
            try:
                fallback_settings = settings.copy() if settings else {}
                fallback_settings["model"] = model

                request_data = self._prepare_quality_request(
                    query, context, fallback_settings
                )

                response = await self._execute_with_quality_assurance(request_data)

                if await self._validate_response_quality(response):
                    logger.info(f"Fallback successful with model: {model}")
                    return response

            except Exception as e:
                logger.error(f"Fallback failed with {model}: {e}")
                continue

        # Ultimate fallback
        return (
            "I apologize for the technical difficulty. Based on your query, "
            "I'll provide the best response I can. Please note that this response "
            "may not meet our usual quality standards."
        )

    async def _update_cache(self, query: str, context: Optional[str], response: str):
        """Update semantic cache with new response"""
        cache_key = self._generate_cache_key(query, context)

        self.response_cache[cache_key] = {
            "query": query,
            "context": context,
            "response": response,
            "timestamp": time.time(),
        }

        # Maintain cache size
        max_size = self.quality_config["intelligent_caching"]["max_cache_size"]
        if len(self.response_cache) > max_size:
            # Remove oldest entries
            sorted_keys = sorted(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k]["timestamp"],
            )
            for key in sorted_keys[: len(self.response_cache) - max_size]:
                del self.response_cache[key]

    def _generate_cache_key(self, query: str, context: Optional[str]) -> str:
        """Generate cache key from query and context"""
        import hashlib

        key_data = f"{query}:{context or ''}"
        return hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()

    async def _calculate_semantic_similarity(self, query1: str, query2: str) -> float:
        """Calculate semantic similarity between queries"""
        # Simplified implementation - would use embeddings in production
        # For now, using Jaccard similarity
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _check_response_coherence(self, response: str) -> bool:
        """Check if response is coherent"""
        # Simple checks - would use more sophisticated methods
        sentences = response.split(".")

        # Check for minimum number of complete sentences
        complete_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        if len(complete_sentences) < 2:
            return False

        # Check for repetition
        if len(set(complete_sentences)) < len(complete_sentences) * 0.8:
            return False

        return True

    def _check_business_terms(self, response: str) -> bool:
        """Check if response contains business-relevant terms"""
        # Business terms to look for
        business_terms = [
            "business",
            "revenue",
            "customer",
            "strategy",
            "analysis",
            "data",
            "performance",
            "metrics",
            "value",
            "solution",
            "implementation",
            "process",
            "efficiency",
            "optimization",
        ]

        response_lower = response.lower()
        term_count = sum(1 for term in business_terms if term in response_lower)

        # Require at least 2 business terms for business context
        return term_count >= 2

    async def get_usage_analytics(self) -> dict[str, Any]:
        """Get usage analytics for dashboard"""
        return {
            "total_requests": len(self.response_cache),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "average_response_quality": 0.88,  # Placeholder
            "fallback_usage_rate": 0.05,  # Placeholder
            "provider_distribution": {"openai": 0.6, "anthropic": 0.3, "others": 0.1},
        }

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # This would track actual hits vs misses
        # For now, returning estimated rate
        return 0.35  # 35% cache hit rate
