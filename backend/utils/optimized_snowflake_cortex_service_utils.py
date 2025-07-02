#!/usr/bin/env python3
"""
Optimized Snowflake Cortex Service - Utility Functions
Extracted from optimized_snowflake_cortex_service.py for better organization
"""

import hashlib
import logging
from typing import Any

from .optimized_snowflake_cortex_service_models import (
    CortexOperation,
    CortexPerformanceMetrics,
    CortexResult,
    ProcessingMode,
)

logger = logging.getLogger(__name__)


class CortexUtils:
    """Utility functions for Cortex operations"""

    @staticmethod
    def generate_cache_key(
        text: str, model: str, operation: CortexOperation
    ) -> str:
        """Generate cache key for text, model, and operation"""
        key_string = f"{operation.value}:{model}:{text}"
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    @staticmethod
    def determine_optimal_processing_mode(
        texts: list[str], operation: CortexOperation
    ) -> ProcessingMode:
        """Determine optimal processing mode based on text count and operation"""
        text_count = len(texts)
        
        if text_count <= 5:
            return ProcessingMode.SEQUENTIAL
        elif text_count <= 50:
            return ProcessingMode.BATCH
        elif text_count <= 200:
            return ProcessingMode.CONCURRENT
        else:
            return ProcessingMode.BATCH  # Use chunked batch for very large datasets

    @staticmethod
    def update_metrics(
        metrics: CortexPerformanceMetrics,
        operation: CortexOperation,
        text_count: int,
        execution_time: float,
        results: list[CortexResult],
    ):
        """Update performance metrics"""
        metrics.total_operations += 1
        metrics.batch_operations += 1 if text_count > 1 else 0
        
        # Update average batch size
        if metrics.total_operations > 0:
            metrics.avg_batch_size = (
                (metrics.avg_batch_size * (metrics.total_operations - 1) + text_count)
                / metrics.total_operations
            )
        
        # Update execution time
        metrics.total_execution_time_ms += execution_time
        metrics.avg_execution_time_ms = (
            metrics.total_execution_time_ms / metrics.total_operations
        )
        
        # Update token and cost tracking
        for result in results:
            if result.success:
                metrics.total_tokens_processed += result.tokens_processed
                metrics.total_cost_estimate += result.cost_estimate

    @staticmethod
    def update_search_metrics(
        metrics: CortexPerformanceMetrics, execution_time: float, result_count: int
    ):
        """Update search-specific metrics"""
        metrics.total_operations += 1
        metrics.total_execution_time_ms += execution_time
        metrics.avg_execution_time_ms = (
            metrics.total_execution_time_ms / metrics.total_operations
        )

    @staticmethod
    def escape_sql_text(text: str) -> str:
        """Escape text for SQL queries"""
        return text.replace("'", "''").replace("\\", "\\\\")

    @staticmethod
    def validate_texts(texts: list[str]) -> list[str]:
        """Validate and clean input texts"""
        if not texts:
            return []
        
        # Filter out empty or None texts
        valid_texts = [text for text in texts if text and text.strip()]
        
        # Truncate very long texts (optional)
        max_length = 10000  # Adjust based on model limits
        truncated_texts = [
            text[:max_length] if len(text) > max_length else text
            for text in valid_texts
        ]
        
        return truncated_texts

    @staticmethod
    def create_batch_query_sentiment(texts: list[str]) -> str:
        """Create batch SQL query for sentiment analysis"""
        case_statements = []
        for i, text in enumerate(texts):
            escaped_text = CortexUtils.escape_sql_text(text)
            case_statements.append(
                f"WHEN {i} THEN SNOWFLAKE.CORTEX.SENTIMENT('{escaped_text}')"
            )

        return f"""
        SELECT
            idx,
            CASE idx
                {" ".join(case_statements)}
            END as sentiment_score
        FROM (
            SELECT ROW_NUMBER() OVER (ORDER BY 1) - 1 as idx
            FROM TABLE(GENERATOR(ROWCOUNT => {len(texts)}))
        )
        ORDER BY idx
        """

    @staticmethod
    def create_batch_query_embeddings(texts: list[str], model: str) -> str:
        """Create batch SQL query for embedding generation"""
        case_statements = []
        for i, text in enumerate(texts):
            escaped_text = CortexUtils.escape_sql_text(text)
            case_statements.append(
                f"WHEN {i} THEN SNOWFLAKE.CORTEX.EMBED_TEXT_768('{model}', '{escaped_text}')"
            )

        return f"""
        SELECT
            idx,
            CASE idx
                {" ".join(case_statements)}
            END as embedding_vector
        FROM (
            SELECT ROW_NUMBER() OVER (ORDER BY 1) - 1 as idx
            FROM TABLE(GENERATOR(ROWCOUNT => {len(texts)}))
        )
        ORDER BY idx
        """

    @staticmethod
    def create_vector_search_query(
        query_embedding: list[float],
        table_name: str,
        embedding_column: str,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        additional_filters: dict[str, Any] | None = None,
    ) -> str:
        """Create optimized vector search query"""
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Build additional filters
        filter_clauses = []
        if additional_filters:
            for column, value in additional_filters.items():
                if isinstance(value, str):
                    filter_clauses.append(f"{column} = '{value}'")
                elif isinstance(value, (int, float)):
                    filter_clauses.append(f"{column} = {value}")
                elif isinstance(value, list):
                    value_str = ",".join([f"'{v}'" if isinstance(v, str) else str(v) for v in value])
                    filter_clauses.append(f"{column} IN ({value_str})")

        where_clause = ""
        if filter_clauses:
            where_clause = f"WHERE {' AND '.join(filter_clauses)} AND"
        else:
            where_clause = "WHERE"

        return f"""
        SELECT *,
               VECTOR_COSINE_SIMILARITY({embedding_column}, {embedding_str}::VECTOR(FLOAT, 768)) as similarity_score
        FROM {table_name}
        {where_clause} VECTOR_COSINE_SIMILARITY({embedding_column}, {embedding_str}::VECTOR(FLOAT, 768)) >= {similarity_threshold}
        ORDER BY similarity_score DESC
        LIMIT {limit}
        """

    @staticmethod
    def format_performance_stats(metrics: CortexPerformanceMetrics, start_time: float) -> dict[str, Any]:
        """Format performance statistics for reporting"""
        import time
        
        uptime_seconds = time.time() - start_time
        
        return {
            "service_uptime_seconds": uptime_seconds,
            "total_operations": metrics.total_operations,
            "batch_operations": metrics.batch_operations,
            "batch_ratio": (
                metrics.batch_operations / metrics.total_operations
                if metrics.total_operations > 0
                else 0
            ),
            "average_batch_size": round(metrics.avg_batch_size, 2),
            "total_execution_time_ms": round(metrics.total_execution_time_ms, 2),
            "average_execution_time_ms": round(metrics.avg_execution_time_ms, 2),
            "operations_per_second": (
                metrics.total_operations / uptime_seconds if uptime_seconds > 0 else 0
            ),
            "total_tokens_processed": metrics.total_tokens_processed,
            "tokens_per_second": (
                metrics.total_tokens_processed / uptime_seconds
                if uptime_seconds > 0
                else 0
            ),
            "total_cost_estimate": round(metrics.total_cost_estimate, 4),
            "average_cost_per_operation": (
                metrics.total_cost_estimate / metrics.total_operations
                if metrics.total_operations > 0
                else 0
            ),
            "cache_hit_ratio": (
                metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses)
                if (metrics.cache_hits + metrics.cache_misses) > 0
                else 0
            ),
            "error_rate": (
                metrics.error_count / metrics.total_operations
                if metrics.total_operations > 0
                else 0
            ),
            "performance_grade": CortexUtils._calculate_performance_grade(metrics, uptime_seconds),
        }

    @staticmethod
    def _calculate_performance_grade(metrics: CortexPerformanceMetrics, uptime_seconds: float) -> str:
        """Calculate overall performance grade"""
        score = 0
        
        # Execution time score (0-30 points)
        if metrics.avg_execution_time_ms < 50:
            score += 30
        elif metrics.avg_execution_time_ms < 100:
            score += 25
        elif metrics.avg_execution_time_ms < 200:
            score += 20
        elif metrics.avg_execution_time_ms < 500:
            score += 15
        else:
            score += 10
        
        # Cache hit ratio score (0-25 points)
        cache_ratio = (
            metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses)
            if (metrics.cache_hits + metrics.cache_misses) > 0
            else 0
        )
        score += int(cache_ratio * 25)
        
        # Error rate score (0-25 points)
        error_rate = (
            metrics.error_count / metrics.total_operations
            if metrics.total_operations > 0
            else 0
        )
        if error_rate < 0.01:
            score += 25
        elif error_rate < 0.05:
            score += 20
        elif error_rate < 0.1:
            score += 15
        else:
            score += 10
        
        # Batch efficiency score (0-20 points)
        batch_ratio = (
            metrics.batch_operations / metrics.total_operations
            if metrics.total_operations > 0
            else 0
        )
        score += int(batch_ratio * 20)
        
        # Convert to letter grade
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        else:
            return "D" 