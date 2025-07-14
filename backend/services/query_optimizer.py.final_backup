"""
Query Optimizer for Sophia AI Memory Ecosystem.

Analyzes queries and creates optimal execution plans for
performance and cost efficiency.
"""

import hashlib
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from backend.services.unified_memory_service import get_unified_memory_service

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries based on analysis"""

    KEYWORD = "keyword"  # Exact match queries
    SEMANTIC = "semantic"  # Conceptual/meaning queries
    HYBRID = "hybrid"  # Mix of keyword and semantic
    NAVIGATIONAL = "navigational"  # Looking for specific document
    ANALYTICAL = "analytical"  # Complex data analysis


class ExecutionStrategy(Enum):
    """Execution strategies for queries"""

    CACHE_ONLY = "cache_only"
    VECTOR_ONLY = "vector_only"
    BM25_ONLY = "bm25_only"
    HYBRID_PARALLEL = "hybrid_parallel"
    HYBRID_SEQUENTIAL = "hybrid_sequential"
    TIERED = "tiered"  # Check hot → warm → cold


@dataclass
class QueryPlan:
    """Execution plan for a query"""

    query: str
    query_type: QueryType
    strategy: ExecutionStrategy
    estimated_cost: float
    estimated_latency: float  # milliseconds
    use_cache: bool
    cache_key: Optional[str]
    metadata_filters: dict[str, Any]
    tier_order: list[str]
    score_weights: dict[str, float]


class QueryOptimizer:
    """
    Analyzes queries and creates optimal execution plans.

    This optimizer considers:
    - Query characteristics (keywords vs semantic)
    - Data location (cache, hot, warm, cold)
    - Cost and performance trade-offs
    - User patterns and preferences
    """

    def __init__(self):
        """Initialize the query optimizer"""
        self.memory_service = get_unified_memory_service()

        # Query patterns for classification
        self.keyword_patterns = [
            r'"[^"]+"',  # Quoted phrases
            r"\b(AND|OR|NOT)\b",  # Boolean operators
            r"\*",  # Wildcards
            r"[A-Z0-9_]+",  # Technical terms (all caps)
            r"\w+\.\w+",  # File names or methods
        ]

        self.semantic_patterns = [
            r"\b(what|how|why|when|where|who)\b",  # Question words
            r"\b(explain|describe|compare|analyze)\b",  # Action verbs
            r"\b(similar|like|related)\b",  # Similarity terms
            r"\b(meaning|concept|idea)\b",  # Abstract terms
        ]

        # Cost weights (relative)
        self.cost_weights = {
            "cache_read": 0.1,
            "redis_read": 0.2,
            "modern_stack_vector": 1.0,
            "modern_stack_bm25": 0.8,
            "modern_stack_cold": 1.5,
        }

        # Latency estimates (ms)
        self.latency_estimates = {
            "cache_read": 1,
            "redis_read": 5,
            "modern_stack_vector": 150,
            "modern_stack_bm25": 120,
            "modern_stack_cold": 300,
        }

        logger.info("QueryOptimizer initialized")

    def analyze_query(self, query: str) -> QueryPlan:
        """
        Analyze a query and create an optimal execution plan.

        Args:
            query: The search query

        Returns:
            QueryPlan with execution strategy
        """
        # Classify query type
        query_type = self._classify_query(query)

        # Extract metadata filters if any
        metadata_filters = self._extract_filters(query)

        # Determine execution strategy
        strategy = self._determine_strategy(query_type, query)

        # Calculate score weights based on query type
        score_weights = self._calculate_weights(query_type)

        # Determine tier order
        tier_order = self._determine_tier_order(query_type)

        # Estimate cost and latency
        estimated_cost = self._estimate_cost(strategy, tier_order)
        estimated_latency = self._estimate_latency(strategy, tier_order)

        # Generate cache key if caching is beneficial
        use_cache = strategy != ExecutionStrategy.CACHE_ONLY
        cache_key = (
            self._generate_cache_key(query, metadata_filters) if use_cache else None
        )

        plan = QueryPlan(
            query=query,
            query_type=query_type,
            strategy=strategy,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            use_cache=use_cache,
            cache_key=cache_key,
            metadata_filters=metadata_filters,
            tier_order=tier_order,
            score_weights=score_weights,
        )

        logger.info(
            f"Query plan created - Type: {query_type.value}, "
            f"Strategy: {strategy.value}, "
            f"Est. latency: {estimated_latency}ms"
        )

        return plan

    def _classify_query(self, query: str) -> QueryType:
        """
        Classify the query type based on characteristics.

        Args:
            query: The search query

        Returns:
            QueryType classification
        """
        query_lower = query.lower()

        # Check for navigational queries (looking for specific item)
        if any(pattern in query_lower for pattern in ["find", "get", "show me the"]):
            if re.search(r"#\d+|id:\s*\w+", query):
                return QueryType.NAVIGATIONAL

        # Check for analytical queries
        if any(
            word in query_lower
            for word in ["analyze", "compare", "trend", "statistics"]
        ):
            return QueryType.ANALYTICAL

        # Count keyword vs semantic indicators
        keyword_score = sum(
            1
            for pattern in self.keyword_patterns
            if re.search(pattern, query, re.IGNORECASE)
        )

        semantic_score = sum(
            1
            for pattern in self.semantic_patterns
            if re.search(pattern, query, re.IGNORECASE)
        )

        # Classify based on scores
        if keyword_score > 2 and semantic_score == 0:
            return QueryType.KEYWORD
        elif semantic_score > 2 and keyword_score == 0:
            return QueryType.SEMANTIC
        elif keyword_score > 0 and semantic_score > 0:
            return QueryType.HYBRID
        else:
            # Default to semantic for natural language queries
            return QueryType.SEMANTIC

    def _extract_filters(self, query: str) -> dict[str, Any]:
        """
        Extract metadata filters from the query.

        Examples:
        - "source:github" → {"source": "github"}
        - "type:bug priority:high" → {"type": "bug", "priority": "high"}

        Args:
            query: The search query

        Returns:
            Dictionary of metadata filters
        """
        filters = {}

        # Pattern for key:value filters
        filter_pattern = r"(\w+):([^\s]+)"
        matches = re.findall(filter_pattern, query)

        for key, value in matches:
            # Handle special values
            if value.lower() == "true":
                filters[key] = True
            elif value.lower() == "false":
                filters[key] = False
            elif value.isdigit():
                filters[key] = int(value)
            else:
                filters[key] = value

        return filters

    def _determine_strategy(
        self, query_type: QueryType, query: str
    ) -> ExecutionStrategy:
        """
        Determine the optimal execution strategy.

        Args:
            query_type: Classified query type
            query: The original query

        Returns:
            ExecutionStrategy to use
        """
        # Short queries often benefit from cache
        if len(query) < 20:
            return ExecutionStrategy.TIERED

        # Strategy based on query type
        if query_type == QueryType.KEYWORD:
            return ExecutionStrategy.BM25_ONLY
        elif query_type == QueryType.SEMANTIC:
            return ExecutionStrategy.VECTOR_ONLY
        elif query_type == QueryType.HYBRID:
            # Use parallel for better performance
            return ExecutionStrategy.HYBRID_PARALLEL
        elif query_type == QueryType.NAVIGATIONAL:
            # Check cache first, then direct lookup
            return ExecutionStrategy.CACHE_ONLY
        elif query_type == QueryType.ANALYTICAL:
            # Complex queries need full search
            return ExecutionStrategy.HYBRID_SEQUENTIAL

        # Default to hybrid parallel
        return ExecutionStrategy.HYBRID_PARALLEL

    def _calculate_weights(self, query_type: QueryType) -> dict[str, float]:
        """
        Calculate score weights based on query type.

        Args:
            query_type: Classified query type

        Returns:
            Dictionary of score weights
        """
        if query_type == QueryType.KEYWORD:
            return {
                "bm25": 0.8,
                "vector": 0.2,
                "personalization": 0.0,
            }
        elif query_type == QueryType.SEMANTIC:
            return {
                "bm25": 0.1,
                "vector": 0.85,
                "personalization": 0.05,
            }
        elif query_type == QueryType.HYBRID:
            return {
                "bm25": 0.35,
                "vector": 0.60,
                "personalization": 0.05,
            }
        else:
            # Default balanced weights
            return {
                "bm25": 0.3,
                "vector": 0.65,
                "personalization": 0.05,
            }

    def _determine_tier_order(self, query_type: QueryType) -> list[str]:
        """
        Determine the order of tiers to check.

        Args:
            query_type: Classified query type

        Returns:
            List of tier names in order
        """
        if query_type == QueryType.NAVIGATIONAL:
            # Check hot first for recent items
            return ["hot", "warm", "cold"]
        elif query_type == QueryType.ANALYTICAL:
            # May need to check all data
            return ["warm", "hot", "cold"]
        else:
            # Default order
            return ["hot", "warm", "cold"]

    def _estimate_cost(
        self, strategy: ExecutionStrategy, tier_order: list[str]
    ) -> float:
        """
        Estimate the relative cost of executing the query.

        Args:
            strategy: Execution strategy
            tier_order: Order of tiers to check

        Returns:
            Estimated relative cost
        """
        cost = 0.0

        if strategy == ExecutionStrategy.CACHE_ONLY:
            cost = self.cost_weights["cache_read"]
        elif strategy == ExecutionStrategy.VECTOR_ONLY:
            cost = self.cost_weights["modern_stack_vector"]
        elif strategy == ExecutionStrategy.BM25_ONLY:
            cost = self.cost_weights["modern_stack_bm25"]
        elif strategy == ExecutionStrategy.HYBRID_PARALLEL:
            # Both searches run in parallel
            cost = max(
                self.cost_weights["modern_stack_vector"],
                self.cost_weights["modern_stack_bm25"],
            )
        elif strategy == ExecutionStrategy.HYBRID_SEQUENTIAL:
            # Both searches run sequentially
            cost = (
                self.cost_weights["modern_stack_vector"]
                + self.cost_weights["modern_stack_bm25"]
            )
        elif strategy == ExecutionStrategy.TIERED:
            # Assume we check 2 tiers on average
            cost = (
                self.cost_weights["redis_read"]
                + self.cost_weights["modern_stack_vector"] * 0.5
            )

        return round(cost, 2)

    def _estimate_latency(
        self, strategy: ExecutionStrategy, tier_order: list[str]
    ) -> float:
        """
        Estimate the latency of executing the query.

        Args:
            strategy: Execution strategy
            tier_order: Order of tiers to check

        Returns:
            Estimated latency in milliseconds
        """
        latency = 0.0

        if strategy == ExecutionStrategy.CACHE_ONLY:
            latency = self.latency_estimates["cache_read"]
        elif strategy == ExecutionStrategy.VECTOR_ONLY:
            latency = self.latency_estimates["modern_stack_vector"]
        elif strategy == ExecutionStrategy.BM25_ONLY:
            latency = self.latency_estimates["modern_stack_bm25"]
        elif strategy == ExecutionStrategy.HYBRID_PARALLEL:
            # Parallel execution takes the max
            latency = max(
                self.latency_estimates["modern_stack_vector"],
                self.latency_estimates["modern_stack_bm25"],
            )
        elif strategy == ExecutionStrategy.HYBRID_SEQUENTIAL:
            # Sequential adds up
            latency = (
                self.latency_estimates["modern_stack_vector"]
                + self.latency_estimates["modern_stack_bm25"]
            )
        elif strategy == ExecutionStrategy.TIERED:
            # Assume cache hit 60% of the time
            latency = (
                self.latency_estimates["redis_read"] * 0.6
                + self.latency_estimates["modern_stack_vector"] * 0.4
            )

        return round(latency, 1)

    def _generate_cache_key(self, query: str, metadata_filters: dict[str, Any]) -> str:
        """Generate a unique cache key for the query"""
        key_parts = [
            "query_opt",
            query,
            str(sorted(metadata_filters.items()) if metadata_filters else ""),
        ]

        key_string = ":".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    async def execute_optimized(
        self,
        query: str,
        user_id: str = "default",
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Execute a query with optimization.

        This is a convenience method that analyzes and executes
        in one step.

        Args:
            query: Search query
            user_id: User identifier
            limit: Maximum results

        Returns:
            Dictionary with results and execution metadata
        """
        # Analyze query
        plan = self.analyze_query(query)

        # Log execution plan
        logger.info(
            f"Executing optimized query - "
            f"Strategy: {plan.strategy.value}, "
            f"Est. cost: {plan.estimated_cost}, "
            f"Est. latency: {plan.estimated_latency}ms"
        )

        # Execute based on strategy
        from backend.services.hybrid_search_engine import get_hybrid_search_engine

        if plan.strategy in [
            ExecutionStrategy.HYBRID_PARALLEL,
            ExecutionStrategy.HYBRID_SEQUENTIAL,
        ]:
            # Use hybrid search engine
            engine = get_hybrid_search_engine()

            # Update weights based on plan
            engine.update_weights(
                bm25_weight=plan.score_weights["bm25"],
                vector_weight=plan.score_weights["vector"],
                personalization_weight=plan.score_weights.get("personalization", 0),
            )

            # Execute search
            results = await engine.search(
                query=plan.query,
                user_id=user_id,
                limit=limit,
                metadata_filter=plan.metadata_filters,
                use_cache=plan.use_cache,
            )

            # Convert to dict format
            search_results = [r.to_dict() for r in results]

        else:
            # Direct execution for simple strategies
            search_results = await self.memory_service.search_knowledge(
                query=plan.query,
                limit=limit,
                metadata_filter=plan.metadata_filters,
                user_id=user_id,
            )

        return {
            "results": search_results,
            "execution_plan": {
                "query_type": plan.query_type.value,
                "strategy": plan.strategy.value,
                "estimated_cost": plan.estimated_cost,
                "estimated_latency": plan.estimated_latency,
                "actual_latency": None,  # TODO: Measure actual
            },
            "metadata": {
                "total_results": len(search_results),
                "cache_hit": False,  # TODO: Track cache hits
                "tiers_searched": plan.tier_order,
            },
        }


# Singleton instance
_query_optimizer = None


def get_query_optimizer() -> QueryOptimizer:
    """Get the singleton QueryOptimizer instance"""
    global _query_optimizer

    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()

    return _query_optimizer
