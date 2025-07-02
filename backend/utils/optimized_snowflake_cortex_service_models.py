#!/usr/bin/env python3
"""
Optimized Snowflake Cortex Service - Data Models
Extracted from optimized_snowflake_cortex_service.py for better organization
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CortexOperation(str, Enum):
    """Snowflake Cortex operation types"""

    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TEXT_SUMMARIZATION = "text_summarization"
    EMBEDDING_GENERATION = "embedding_generation"
    VECTOR_SEARCH = "vector_search"
    TRANSLATE = "translate"
    COMPLETE = "complete"


class ProcessingMode(str, Enum):
    """Processing mode for batch operations"""

    SEQUENTIAL = "sequential"
    BATCH = "batch"
    CONCURRENT = "concurrent"
    ADAPTIVE = "adaptive"


@dataclass
class CortexResult:
    """Cortex operation result"""

    operation: CortexOperation
    success: bool
    result: Any | None = None
    error: str | None = None
    execution_time_ms: float = 0.0
    tokens_processed: int = 0
    cost_estimate: float = 0.0


@dataclass
class BatchCortexRequest:
    """Batch Cortex operation request"""

    operation: CortexOperation
    texts: list[str]
    model: str | None = None
    parameters: dict[str, Any] | None = None
    request_id: str | None = None


@dataclass
class CortexPerformanceMetrics:
    """Performance metrics for Cortex operations"""

    total_operations: int = 0
    batch_operations: int = 0
    avg_batch_size: float = 0.0
    total_execution_time_ms: float = 0.0
    avg_execution_time_ms: float = 0.0
    total_tokens_processed: int = 0
    total_cost_estimate: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    error_count: int = 0


@dataclass
class CortexConfig:
    """Configuration for Cortex service"""

    max_batch_size: int = 50
    optimal_batch_size: int = 10
    batch_timeout_ms: int = 5000
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    
    # Model configuration
    default_models: dict[CortexOperation, str] = None
    
    # Cost tracking (estimated costs per operation)
    operation_costs: dict[CortexOperation, float] = None
    
    def __post_init__(self):
        if self.default_models is None:
            self.default_models = {
                CortexOperation.SENTIMENT_ANALYSIS: "snowflake-arctic-sentiment",
                CortexOperation.TEXT_SUMMARIZATION: "snowflake-arctic-summarize",
                CortexOperation.EMBEDDING_GENERATION: "e5-base-v2",
                CortexOperation.TRANSLATE: "snowflake-arctic-translate",
                CortexOperation.COMPLETE: "snowflake-arctic",
            }
        
        if self.operation_costs is None:
            self.operation_costs = {
                CortexOperation.SENTIMENT_ANALYSIS: 0.001,
                CortexOperation.TEXT_SUMMARIZATION: 0.005,
                CortexOperation.EMBEDDING_GENERATION: 0.002,
                CortexOperation.VECTOR_SEARCH: 0.001,
                CortexOperation.TRANSLATE: 0.003,
                CortexOperation.COMPLETE: 0.010,
            } 