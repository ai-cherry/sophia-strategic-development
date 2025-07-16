"""
Query Optimizer Service - Optimizes database and vector queries for performance
"""

import asyncio
import logging
import time
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of queries based on analysis"""
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    NAVIGATIONAL = "navigational"
    ANALYTICAL = "analytical"

class ExecutionStrategy(Enum):
    """Execution strategies for queries"""
    CACHE_ONLY = "cache_only"
    VECTOR_ONLY = "vector_only"
    BM25_ONLY = "bm25_only"
    HYBRID_PARALLEL = "hybrid_parallel"
    HYBRID_SEQUENTIAL = "hybrid_sequential"
    TIERED = "tiered"

@dataclass
class QueryPlan:
    """Execution plan for a query"""
    query_type: QueryType
    strategy: ExecutionStrategy
    estimated_latency: float
    confidence: float
    cache_key: Optional[str] = None

class QueryOptimizer:
    """Query optimization service for Sophia AI"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the query optimizer"""
        self.config = config or {}
        self.initialized = False
        
        # Query patterns for analysis
        self.patterns = {
            "keyword_patterns": [
                r'"[^"]+"',  # Quoted phrases
                r"\b(AND|OR|NOT)\b",  # Boolean operators
                r"\*",  # Wildcards
                r"[A-Z0-9_]+",  # Constants/IDs
                r"\w+\.\w+"  # Dotted notation
            ],
            "semantic_patterns": [
                r"\b(what|how|why|when|where|who)\b",  # Question words
                r"\b(explain|describe|compare|analyze)\b",  # Analytical verbs
                r"\b(similar|like|related)\b",  # Similarity words
                r"\b(meaning|concept|idea)\b"  # Conceptual words
            ]
        }
        
        # Performance targets
        self.performance_targets = {
            "cache_read": 5,  # ms
            "redis_read": 10,  # ms
            "qdrant_vector": 50,  # ms
            "qdrant_bm25": 30,  # ms
            "qdrant_cold": 200  # ms
        }
        
        # Performance tracking
        self.metrics = {
            "queries_optimized": 0,
            "cache_hits": 0,
            "average_latency": 0.0,
            "optimization_score": 0.0
        }
        
        logger.info("✅ QueryOptimizer initialized")
    
    async def initialize(self):
        """Initialize the query optimizer"""
        try:
            self.initialized = True
            logger.info("✅ QueryOptimizer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize QueryOptimizer: {e}")
            raise
    
    async def create_query_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryPlan:
        """Create optimized execution plan for a query"""
        try:
            # Analyze query characteristics
            query_type = await self._analyze_query_type(query)
            
            # Select optimal execution strategy
            strategy = await self._select_execution_strategy(query_type, query, context)
            
            # Estimate performance
            estimated_latency = await self._estimate_latency(strategy, query)
            
            # Calculate confidence
            confidence = await self._calculate_confidence(query_type, strategy)
            
            query_plan = QueryPlan(
                query_type=query_type,
                strategy=strategy,
                estimated_latency=estimated_latency,
                confidence=confidence
            )
            
            self.metrics["queries_optimized"] += 1
            
            logger.info(
                f"Query plan created - Type: {query_type.value}, "
                f"Strategy: {strategy.value}, "
                f"Est. latency: {estimated_latency}ms"
            )
            
            return query_plan
            
        except Exception as e:
            logger.error(f"Failed to create query plan: {e}")
            raise
    
    async def _analyze_query_type(self, query: str) -> QueryType:
        """Analyze query to determine its type"""
        query_lower = query.lower()
        
        # Check for navigational queries
        if any(pattern in query_lower for pattern in ["find", "get", "show me the"]):
            if re.search(r"#\d+|id:\s*\w+", query):
                return QueryType.NAVIGATIONAL
        
        # Check for analytical queries
        for word in ["analyze", "compare", "trend", "statistics"]:
            if word in query_lower:
                return QueryType.ANALYTICAL
        
        # Check semantic patterns
        semantic_score = sum(
            1 for pattern_list in self.patterns["semantic_patterns"]
            for pattern in pattern_list
            if re.search(pattern, query_lower, re.IGNORECASE)
        )
        
        # Check keyword patterns
        keyword_score = sum(
            1 for pattern_list in self.patterns["keyword_patterns"]
            for pattern in pattern_list
            if re.search(pattern, query, re.IGNORECASE)
        )
        
        # Determine type based on scores
        if semantic_score > keyword_score:
            return QueryType.SEMANTIC
        elif keyword_score > 0:
            return QueryType.KEYWORD
        else:
            return QueryType.HYBRID
    
    async def _select_execution_strategy(
        self, 
        query_type: QueryType, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionStrategy:
        """Select optimal execution strategy"""
        
        # Consider cache first for frequent queries
        if context and context.get("cache_available", False):
            return ExecutionStrategy.CACHE_ONLY
        
        # Strategy selection based on query type
        if query_type == QueryType.KEYWORD:
            return ExecutionStrategy.BM25_ONLY
        elif query_type == QueryType.SEMANTIC:
            return ExecutionStrategy.VECTOR_ONLY
        elif query_type == QueryType.HYBRID:
            return ExecutionStrategy.HYBRID_PARALLEL
        elif query_type == QueryType.ANALYTICAL:
            return ExecutionStrategy.TIERED
        else:
            return ExecutionStrategy.HYBRID_SEQUENTIAL
    
    async def _estimate_latency(self, strategy: ExecutionStrategy, query: str) -> float:
        """Estimate query execution latency"""
        base_latency = self.performance_targets.get("qdrant_vector", 50)
        
        # Adjust based on strategy
        strategy_multipliers = {
            ExecutionStrategy.CACHE_ONLY: 0.1,
            ExecutionStrategy.VECTOR_ONLY: 1.0,
            ExecutionStrategy.BM25_ONLY: 0.6,
            ExecutionStrategy.HYBRID_PARALLEL: 1.2,
            ExecutionStrategy.HYBRID_SEQUENTIAL: 1.8,
            ExecutionStrategy.TIERED: 2.0
        }
        
        multiplier = strategy_multipliers.get(strategy, 1.0)
        
        # Adjust based on query complexity
        complexity_factor = min(len(query) / 100, 2.0)
        
        estimated_latency = base_latency * multiplier * complexity_factor
        
        return round(estimated_latency, 2)
    
    async def _calculate_confidence(self, query_type: QueryType, strategy: ExecutionStrategy) -> float:
        """Calculate confidence in the optimization plan"""
        base_confidence = 0.8
        
        # Adjust confidence based on query type clarity
        type_confidence = {
            QueryType.KEYWORD: 0.9,
            QueryType.SEMANTIC: 0.85,
            QueryType.HYBRID: 0.75,
            QueryType.NAVIGATIONAL: 0.95,
            QueryType.ANALYTICAL: 0.8
        }
        
        confidence = base_confidence * type_confidence.get(query_type, 0.7)
        
        return round(min(confidence, 1.0), 2)
    
    async def execute_optimized_query(
        self, 
        query_plan: QueryPlan, 
        query: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Execute query using the optimized plan"""
        start_time = time.time()
        
        try:
            # Simulate query execution based on strategy
            result = await self._execute_query_strategy(query_plan, query, **kwargs)
            
            # Measure actual latency
            actual_latency = (time.time() - start_time) * 1000
            
            # Update metrics
            self.metrics["average_latency"] = (
                (self.metrics["average_latency"] * (self.metrics["queries_optimized"] - 1) + actual_latency) 
                / self.metrics["queries_optimized"]
            )
            
            return {
                "results": result,
                "execution_plan": {
                    "query_type": query_plan.query_type.value,
                    "strategy": query_plan.strategy.value,
                    "estimated_latency": query_plan.estimated_latency,
                    "actual_latency": actual_latency,
                    "confidence": query_plan.confidence
                },
                "performance": {
                    "latency_ms": actual_latency,
                    "optimized": True,
                    "cache_hit": query_plan.strategy == ExecutionStrategy.CACHE_ONLY
                }
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def _execute_query_strategy(
        self, 
        query_plan: QueryPlan, 
        query: str, 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Execute query based on the selected strategy"""
        # Placeholder for actual query execution logic
        await asyncio.sleep(0.01)  # Simulate processing time
        
        return [{
            "id": "example_result",
            "content": f"Optimized result for: {query}",
            "score": 0.95,
            "metadata": {
                "strategy_used": query_plan.strategy.value,
                "optimized": True
            }
        }]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get optimizer metrics"""
        return self.metrics.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "status": "healthy" if self.initialized else "unhealthy",
            "service": "QueryOptimizer",
            "metrics": self.get_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }