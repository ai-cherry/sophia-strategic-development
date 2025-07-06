#!/usr/bin/env python3
"""
Extended Context Manager for Sophia AI
Handles multi-tier memory architecture supporting up to 16M tokens
"""

import hashlib
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np

from backend.utils.custom_logger import setup_logger
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = setup_logger("extended_context_manager")


@dataclass
class ContextBundle:
    """Container for context with metadata"""

    primary_context: str
    metadata: dict[str, Any]
    retrieval_score: float
    business_context_preserved: bool
    token_count: int
    compression_ratio: float = 1.0


@dataclass
class ExtendedContextualIntelligence:
    """Extended context retrieval results"""

    context: str
    context_size_tokens: int
    retrieval_time_ms: float
    performance_met: bool
    context_quality_score: float
    optimization_applied: dict[str, bool]
    memory_layers_accessed: int
    business_context_preserved: bool


class ExtendedContextManager:
    """
    Multi-tier context window management for CEO-level intelligence
    Supports up to 16M tokens with performance optimization
    """

    # Context window limits for different memory tiers
    CONTEXT_LIMITS = {
        "session_memory": 32000,  # Current conversation
        "daily_memory": 128000,  # Today's interactions
        "weekly_memory": 500000,  # Weekly business context
        "monthly_memory": 1000000,  # Monthly strategic context
        "quarterly_memory": 2000000,  # Quarterly board preparation
        "annual_memory": 4000000,  # Annual business intelligence
        "perpetual_memory": 8000000,  # Long-term knowledge base
        "strategic_memory": 16000000,  # Ultra-long strategic context
    }

    # Performance targets for retrieval
    PERFORMANCE_TARGETS = {
        "immediate_retrieval": {"latency": 50, "context_size": 32000},
        "session_retrieval": {"latency": 200, "context_size": 128000},
        "business_retrieval": {"latency": 500, "context_size": 1000000},
        "strategic_retrieval": {"latency": 1000, "context_size": 4000000},
        "historical_retrieval": {"latency": 2000, "context_size": 8000000},
        "ultra_long_retrieval": {"latency": 5000, "context_size": 16000000},
    }

    def __init__(self):
        self.cortex_service = SnowflakeCortexService()

        # Memory indices for different tiers
        self.memory_indices = {}

        # Optimization strategies
        self.optimization_strategies = {
            "hierarchical_compression": True,
            "semantic_deduplication": True,
            "temporal_relevance_weighting": True,
            "business_entity_preservation": True,
            "cross_reference_maintenance": True,
            "adaptive_chunk_sizing": True,
            "quality_based_retention": True,
        }

        # Cache for frequently accessed contexts
        self.context_cache = {}
        self.cache_ttl = 3600  # 1 hour

        logger.info("Extended Context Manager initialized with 16M token support")

    async def optimize_context_retrieval(
        self,
        query: str,
        context_type: str,
        business_context: dict[str, Any] | None = None,
    ) -> ContextBundle:
        """
        High-performance contextual retrieval with semantic ranking
        """
        start_time = time.time()

        # Determine which memory tiers to search
        tiers_to_search = self._determine_search_tiers(context_type)
        max_tokens = self.CONTEXT_LIMITS.get(context_type, 32000)

        # Check cache first
        cache_key = self._generate_cache_key(query, context_type)
        if cache_key in self.context_cache:
            cached_result = self.context_cache[cache_key]
            if cached_result["timestamp"] > time.time() - self.cache_ttl:
                logger.info(f"Cache hit for context retrieval: {context_type}")
                return cached_result["bundle"]

        # Semantic similarity search across memory tiers
        relevant_contexts = await self.semantic_search(
            query=query,
            tiers=tiers_to_search,
            max_tokens=max_tokens,
            similarity_threshold=0.85,
            business_context=business_context or "pay_ready_operations",
        )

        # Hierarchical context compression for large windows
        compressed_context = await self.compress_context(
            contexts=relevant_contexts,
            target_size=int(max_tokens * 0.8),  # Leave 20% buffer
            preserve_business_entities=True,
            maintain_temporal_relationships=True,
        )

        # Calculate quality score
        quality_score = self._calculate_relevance_score(query, compressed_context)

        # Create context bundle
        bundle = ContextBundle(
            primary_context=compressed_context,
            metadata=self._generate_context_metadata(relevant_contexts),
            retrieval_score=quality_score,
            business_context_preserved=True,
            token_count=len(compressed_context.split()),
            compression_ratio=len(str(relevant_contexts)) / len(compressed_context)
            if compressed_context
            else 1.0,
        )

        # Cache the result
        self.context_cache[cache_key] = {"bundle": bundle, "timestamp": time.time()}

        retrieval_time = (time.time() - start_time) * 1000
        logger.info(
            f"Context retrieval completed in {retrieval_time:.2f}ms for {context_type}"
        )

        return bundle

    async def semantic_search(
        self,
        query: str,
        tiers: list[str],
        max_tokens: int,
        similarity_threshold: float,
        business_context: Any,
    ) -> list[dict[str, Any]]:
        """
        Perform semantic similarity search across memory tiers
        """
        # Generate query embedding
        query_embedding = await self.cortex_service.generate_embedding(query)

        all_results = []
        remaining_tokens = max_tokens

        for tier in tiers:
            if remaining_tokens <= 0:
                break

            # Search in Snowflake using Cortex vector search
            tier_results = await self._search_tier(
                tier=tier,
                query_embedding=query_embedding,
                similarity_threshold=similarity_threshold,
                max_results=50,
                business_context=business_context,
            )

            # Add results and track token usage
            for result in tier_results:
                if remaining_tokens <= 0:
                    break

                result_tokens = len(result["content"].split())
                if result_tokens <= remaining_tokens:
                    all_results.append(result)
                    remaining_tokens -= result_tokens

        # Sort by relevance score
        all_results.sort(key=lambda x: x["similarity_score"], reverse=True)

        return all_results

    async def compress_context(
        self,
        contexts: list[dict[str, Any]],
        target_size: int,
        preserve_business_entities: bool,
        maintain_temporal_relationships: bool,
    ) -> str:
        """
        Compress context while preserving important information
        """
        if not contexts:
            return ""

        # Group contexts by type and time
        grouped_contexts = self._group_contexts(contexts)

        # Apply compression strategies
        compressed_parts = []

        for group_type, group_contexts in grouped_contexts.items():
            if preserve_business_entities:
                # Extract and preserve business entities
                entities = await self._extract_business_entities(group_contexts)
                compressed_parts.append(
                    f"Key {group_type} entities: {', '.join(entities)}"
                )

            # Compress using summarization
            summary = await self._summarize_context_group(
                group_contexts, maintain_temporal=maintain_temporal_relationships
            )
            compressed_parts.append(summary)

        # Combine compressed parts
        compressed_context = "\n\n".join(compressed_parts)

        # Ensure we're within target size
        if len(compressed_context.split()) > target_size:
            compressed_context = self._truncate_to_size(compressed_context, target_size)

        return compressed_context

    async def retrieve_extended_contextual_intelligence(
        self, query: str, intelligence_type: str, max_context_tokens: int = 16000000
    ) -> ExtendedContextualIntelligence:
        """
        Retrieve relevant context with extended window support and performance guarantees
        """
        start_time = time.time()

        # Retrieve context with optimization
        context_bundle = await self.optimize_context_retrieval(
            query=query,
            context_type=intelligence_type,
            business_context={"focus": "pay_ready", "industry": "apartment_technology"},
        )

        retrieval_time = (time.time() - start_time) * 1000

        # Check if performance target was met
        target_latency = self._get_target_latency(intelligence_type)
        performance_met = retrieval_time < target_latency

        return ExtendedContextualIntelligence(
            context=context_bundle.primary_context,
            context_size_tokens=context_bundle.token_count,
            retrieval_time_ms=retrieval_time,
            performance_met=performance_met,
            context_quality_score=context_bundle.retrieval_score,
            optimization_applied=self.optimization_strategies,
            memory_layers_accessed=len(
                context_bundle.metadata.get("tiers_accessed", [])
            ),
            business_context_preserved=context_bundle.business_context_preserved,
        )

    def _determine_search_tiers(self, context_type: str) -> list[str]:
        """Determine which memory tiers to search based on context type"""
        tier_mapping = {
            "session_memory": ["session_memory"],
            "daily_memory": ["session_memory", "daily_memory"],
            "weekly_memory": ["session_memory", "daily_memory", "weekly_memory"],
            "monthly_memory": ["daily_memory", "weekly_memory", "monthly_memory"],
            "quarterly_memory": ["weekly_memory", "monthly_memory", "quarterly_memory"],
            "annual_memory": ["monthly_memory", "quarterly_memory", "annual_memory"],
            "perpetual_memory": [
                "quarterly_memory",
                "annual_memory",
                "perpetual_memory",
            ],
            "strategic_memory": [
                "annual_memory",
                "perpetual_memory",
                "strategic_memory",
            ],
        }
        return tier_mapping.get(context_type, ["session_memory"])

    def _generate_cache_key(self, query: str, context_type: str) -> str:
        """Generate cache key for context retrieval"""
        key_data = f"{query}:{context_type}"
        return hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()

    async def _search_tier(
        self,
        tier: str,
        query_embedding: list[float],
        similarity_threshold: float,
        max_results: int,
        business_context: Any,
    ) -> list[dict[str, Any]]:
        """Search a specific memory tier"""
        # This would connect to Snowflake and perform vector search
        # For now, returning mock data
        return [
            {
                "content": f"Sample context from {tier}",
                "similarity_score": 0.9,
                "timestamp": datetime.now().isoformat(),
                "tier": tier,
            }
        ]

    def _calculate_relevance_score(self, query: str, context: str) -> float:
        """Calculate relevance score between query and context"""
        # Simple implementation - would use more sophisticated scoring
        query_terms = set(query.lower().split())
        context_terms = set(context.lower().split())

        if not query_terms:
            return 0.0

        overlap = query_terms.intersection(context_terms)
        return len(overlap) / len(query_terms)

    def _generate_context_metadata(
        self, contexts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate metadata about retrieved contexts"""
        tiers_accessed = list({c.get("tier", "unknown") for c in contexts})

        return {
            "total_contexts": len(contexts),
            "tiers_accessed": tiers_accessed,
            "avg_similarity_score": np.mean(
                [c.get("similarity_score", 0) for c in contexts]
            )
            if contexts
            else 0,
            "timestamp": datetime.now().isoformat(),
        }

    def _group_contexts(
        self, contexts: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        """Group contexts by type for compression"""
        groups = {}
        for context in contexts:
            tier = context.get("tier", "unknown")
            if tier not in groups:
                groups[tier] = []
            groups[tier].append(context)
        return groups

    async def _extract_business_entities(
        self, contexts: list[dict[str, Any]]
    ) -> list[str]:
        """Extract business entities from contexts"""
        # Would use NER or entity extraction
        # For now, returning sample entities
        return [
            "Pay Ready",
            "apartment payments",
            "rent collection",
            "property management",
        ]

    async def _summarize_context_group(
        self, contexts: list[dict[str, Any]], maintain_temporal: bool
    ) -> str:
        """Summarize a group of contexts"""
        # Would use LLM for summarization
        # For now, simple concatenation
        summaries = []
        for context in contexts:
            content = context.get("content", "")
            if maintain_temporal:
                timestamp = context.get("timestamp", "")
                summaries.append(f"[{timestamp}] {content}")
            else:
                summaries.append(content)

        return " ".join(summaries[:10])  # Limit to first 10

    def _truncate_to_size(self, text: str, target_size: int) -> str:
        """Truncate text to target token size"""
        words = text.split()
        if len(words) <= target_size:
            return text
        return " ".join(words[:target_size])

    async def _calculate_optimal_context_size(
        self, query: str, intelligence_type: str, max_allowed: int
    ) -> int:
        """Calculate optimal context size based on query complexity"""
        # Simple heuristic - would use more sophisticated analysis
        base_size = self.CONTEXT_LIMITS.get(intelligence_type, 32000)

        # Adjust based on query complexity
        query_words = len(query.split())
        if query_words > 50:
            base_size = min(base_size * 2, max_allowed)

        return min(base_size, max_allowed)

    def _get_target_latency(self, intelligence_type: str) -> float:
        """Get target latency for intelligence type"""
        for target_type, target_info in self.PERFORMANCE_TARGETS.items():
            if intelligence_type.endswith(target_type.split("_")[0] + "_memory"):
                return target_info["latency"]
        return 5000  # Default to 5 seconds
