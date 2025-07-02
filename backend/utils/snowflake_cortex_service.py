"""
Snowflake Cortex AI Service - Facade Module

This module provides backward compatibility by importing and exposing all functionality
from the decomposed modules. External code can continue to import from this module
without any changes.

Decomposed Architecture:
- snowflake_cortex_service_core.py: Core service class and connection management
- snowflake_cortex_service_models.py: Data models, enums, and exceptions
- snowflake_cortex_service_utils.py: Utility functions and helper classes
- snowflake_cortex_service_handlers.py: AI operation handlers and business methods
"""

from __future__ import annotations

import logging
from typing import Any

# Import all models and exceptions for backward compatibility
from .snowflake_cortex_service_models import (
    CortexEmbeddingError,
    InsufficientPermissionsError,
    BusinessTableNotFoundError,
    InvalidInputError,
    CortexModel,
    CortexQuery,
    VectorSearchResult,
    CortexOperation,
    ProcessingMode,
    CortexResult,
    CortexConfig,
    CortexPerformanceMetrics,
)

# Import utility classes
from .snowflake_cortex_service_utils import (
    CortexUtils,
    QueryBuilder,
    ResultFormatter,
    PerformanceMonitor,
    CacheManager,
)

# Import core service
from .snowflake_cortex_service_core import SnowflakeCortexService as CoreService

# Import handlers
from .snowflake_cortex_service_handlers import CortexHandlers, BusinessHandlers

logger = logging.getLogger(__name__)


class SnowflakeCortexService(CoreService):
    """
    Enhanced Snowflake Cortex Service with decomposed architecture
    
    This facade provides all original functionality while using the new
    decomposed architecture for better maintainability and performance.
    """

    def __init__(self):
        super().__init__()
        
        # Initialize handlers
        self.cortex_handlers = CortexHandlers(self)
        self.business_handlers = BusinessHandlers(self)
        
        # Initialize utils
        self.utils = CortexUtils()
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()

    # Delegate AI operations to handlers for better organization
    async def summarize_text_in_snowflake(
        self,
        text_column: str,
        table_name: str,
        conditions: str | None = None,
        max_length: int = 200,
    ) -> list[dict[str, Any]]:
        """Summarize text data using Snowflake Cortex SUMMARIZE function"""
        return await self.cortex_handlers.summarize_text_in_snowflake(
            text_column, table_name, conditions, max_length
        )

    async def analyze_sentiment_in_snowflake(
        self, text_column: str, table_name: str, conditions: str | None = None
    ) -> list[dict[str, Any]]:
        """Analyze sentiment using Snowflake Cortex SENTIMENT function"""
        return await self.cortex_handlers.analyze_sentiment_in_snowflake(
            text_column, table_name, conditions
        )

    async def generate_embedding_in_snowflake(
        self,
        text_column: str,
        table_name: str,
        conditions: str | None = None,
        model: str = "e5-base-v2",
        store_embeddings: bool = True,
    ) -> list[dict[str, Any]]:
        """Generate embeddings using Snowflake Cortex EMBED_TEXT function"""
        if not self.initialized:
            await self.initialize()

        query = f"""
        SELECT
            id,
            {text_column} as text,
            SNOWFLAKE.CORTEX.EMBED_TEXT('{model}', {text_column}) as embedding_vector,
            '{model}' as embedding_model,
            CURRENT_TIMESTAMP() as embedded_at
        FROM {table_name}
        """

        if conditions:
            query += f" WHERE {conditions}"

        try:
            results = await self.connection_manager.execute_query(query)

            embeddings = []
            for row in results:
                record = {
                    "id": row[0],
                    "text": row[1],
                    "embedding_vector": row[2],
                    "embedding_model": row[3],
                    "embedded_at": row[4],
                }
                embeddings.append(record)

            if store_embeddings and embeddings:
                await self._store_embeddings(embeddings, table_name)

            logger.info(f"Generated {len(embeddings)} embeddings using Cortex {model}")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings with Cortex: {e}")
            raise

    async def vector_search_in_snowflake(
        self,
        query_text: str,
        vector_table: str,
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        model: str = "e5-base-v2",
    ) -> list[VectorSearchResult]:
        """Perform vector similarity search using Snowflake native functions"""
        if not self.initialized:
            await self.initialize()

        query = f"""
        WITH query_embedding AS (
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('{model}', '{query_text}') as query_vector
        ),
        similarity_scores AS (
            SELECT
                v.id,
                v.original_text,
                v.metadata,
                v.source_table,
                v.source_id,
                VECTOR_COSINE_SIMILARITY(q.query_vector, v.embedding_vector) as similarity_score
            FROM {vector_table} v
            CROSS JOIN query_embedding q
            WHERE VECTOR_COSINE_SIMILARITY(q.query_vector, v.embedding_vector) >= {similarity_threshold}
        )
        SELECT
            id,
            original_text as content,
            metadata,
            source_table,
            source_id,
            similarity_score
        FROM similarity_scores
        ORDER BY similarity_score DESC
        LIMIT {top_k}
        """

        try:
            results = await self.connection_manager.execute_query(query)
            
            vector_results = []
            for row in results:
                result = VectorSearchResult(
                    content=row[1],
                    similarity_score=row[5],
                    metadata=row[2] if row[2] else {},
                    source_table=row[3],
                    source_id=row[4],
                )
                vector_results.append(result)

            logger.info(f"Found {len(vector_results)} similar results for query: {query_text[:50]}...")
            return vector_results

        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            raise

    async def complete_text_with_cortex(
        self,
        prompt: str,
        model: CortexModel = CortexModel.MISTRAL_7B,
        max_tokens: int = 500,
        temperature: float = 0.7,
        context: str | None = None,
    ) -> str:
        """Generate text completion using Snowflake Cortex LLM functions"""
        if not self.initialized:
            await self.initialize()

        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model.value}',
            '{full_prompt}',
            {{
                'max_tokens': {max_tokens},
                'temperature': {temperature}
            }}
        ) as completion
        """

        try:
            results = await self.connection_manager.execute_query(query)
            
            if results and len(results) > 0:
                completion = results[0][0] if results[0][0] else ""
            else:
                completion = ""

            logger.info(f"Generated text completion using {model.value}")
            return completion

        except Exception as e:
            logger.error(f"Error generating text completion: {e}")
            raise

    async def extract_entities_from_text(
        self,
        text_column: str,
        table_name: str,
        entity_types: list[str],
        conditions: str | None = None,
    ) -> list[dict[str, Any]]:
        """Extract entities from text using Snowflake Cortex"""
        if not self.initialized:
            await self.initialize()

        entity_types_str = ", ".join([f"'{et}'" for et in entity_types])
        
        query = f"""
        SELECT
            id,
            {text_column} as text,
            SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
                {text_column},
                'Extract the following entities: {entity_types_str}'
            ) as extracted_entities,
            CURRENT_TIMESTAMP() as extracted_at
        FROM {table_name}
        """

        if conditions:
            query += f" WHERE {conditions}"

        try:
            results = await self.connection_manager.execute_query(query)

            entities = []
            for row in results:
                record = {
                    "id": row[0],
                    "text": row[1],
                    "extracted_entities": row[2],
                    "extracted_at": row[3],
                }
                entities.append(record)

            logger.info(f"Extracted entities from {len(entities)} records")
            return entities

        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            raise

    # Delegate business operations to business handlers
    async def store_embedding_in_business_table(
        self,
        table_name: str,
        record_id: str,
        text_content: str,
        embedding_column: str = "ai_memory_embedding",
        metadata: dict[str, Any] | None = None,
        model: str = "e5-base-v2",
    ) -> bool:
        """Store embedding directly in business table"""
        return await self.business_handlers.store_embedding_in_business_table(
            table_name, record_id, text_content, embedding_column, metadata, model
        )

    async def ensure_embedding_columns_exist(self, table_name: str) -> bool:
        """Ensure AI Memory embedding columns exist in business table"""
        return await self.business_handlers.ensure_embedding_columns_exist(table_name)

    async def vector_search_business_table(
        self,
        query_text: str,
        table_name: str,
        embedding_column: str = "ai_memory_embedding",
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        metadata_filters: dict[str, Any] | None = None,
        model: str = "e5-base-v2",
    ) -> list[dict[str, Any]]:
        """Perform vector similarity search directly on business tables"""
        if not self.initialized:
            await self.initialize()

        # Input validation
        ALLOWED_TABLES = {"ENRICHED_HUBSPOT_DEALS", "ENRICHED_GONG_CALLS"}
        ALLOWED_EMBEDDING_COLUMNS = {"ai_memory_embedding"}
        ALLOWED_MODELS = {"e5-base-v2", "multilingual-e5-large"}

        if table_name not in ALLOWED_TABLES:
            raise InvalidInputError(f"Table {table_name} not allowed. Allowed: {ALLOWED_TABLES}")

        if embedding_column not in ALLOWED_EMBEDDING_COLUMNS:
            raise InvalidInputError(f"Embedding column {embedding_column} not allowed")

        if model not in ALLOWED_MODELS:
            raise InvalidInputError(f"Model {model} not allowed. Allowed: {ALLOWED_MODELS}")

        if not query_text or not query_text.strip():
            raise InvalidInputError("Query text cannot be empty")

        if len(query_text) > 8000:
            logger.warning(f"Query text truncated from {len(query_text)} to 8000 characters")
            query_text = query_text[:8000]

        # Simplified implementation for facade
        try:
            # Generate query embedding
            embed_query = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('{model}', '{query_text}') as query_vector"
            embed_results = await self.connection_manager.execute_query(embed_query)
            
            if not embed_results or not embed_results[0][0]:
                raise CortexEmbeddingError(f"Failed to generate query embedding with model {model}")

            query_embedding = embed_results[0][0]

            # Build search query
            where_conditions = [f"{embedding_column} IS NOT NULL"]
            
            if metadata_filters:
                ALLOWED_FILTER_COLUMNS = {"deal_stage", "sentiment_category", "primary_user_name"}
                for key, value in metadata_filters.items():
                    if key in ALLOWED_FILTER_COLUMNS:
                        where_conditions.append(f"{key} = '{value}'")

            where_clause = " AND ".join(where_conditions)

            search_query = f"""
            SELECT
                *,
                VECTOR_COSINE_SIMILARITY('{query_embedding}', {embedding_column}) as similarity_score
            FROM {table_name}
            WHERE {where_clause}
              AND VECTOR_COSINE_SIMILARITY('{query_embedding}', {embedding_column}) >= {similarity_threshold}
            ORDER BY similarity_score DESC
            LIMIT {top_k}
            """

            results = await self.connection_manager.execute_query(search_query)

            # Convert to list of dictionaries
            search_results = []
            if results:
                # Get column names (simplified)
                columns = [f"col_{i}" for i in range(len(results[0]))]
                for row in results:
                    record = dict(zip(columns, row, strict=False))
                    search_results.append(record)

            logger.info(f"Found {len(search_results)} similar records in {table_name}")
            return search_results

        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            raise

    async def _store_embeddings(self, embeddings: list[dict[str, Any]], source_table: str):
        """Store embeddings in dedicated vector table"""
        try:
            vector_table = "AI_MEMORY_EMBEDDINGS"
            
            for embedding in embeddings:
                insert_query = f"""
                INSERT INTO {vector_table} (
                    id, original_text, embedding_vector, metadata,
                    source_table, source_id, embedding_model
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                await self.connection_manager.execute_query(
                    insert_query,
                    (
                        embedding["id"],
                        embedding["text"],
                        embedding["embedding_vector"],
                        "{}",  # Empty metadata
                        source_table,
                        embedding["id"],
                        embedding["embedding_model"],
                    )
                )
            
            logger.info(f"Stored {len(embeddings)} embeddings in {vector_table}")
            
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")

    # Simplified business intelligence methods for backward compatibility
    async def search_hubspot_deals_with_ai_memory(
        self,
        query_text: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        deal_stage: str | None = None,
        min_deal_value: float | None = None,
        max_deal_value: float | None = None,
    ) -> list[dict[str, Any]]:
        """Search HubSpot deals using AI Memory embeddings"""
        metadata_filters = {}
        if deal_stage:
            metadata_filters["deal_stage"] = deal_stage
            
        return await self.vector_search_business_table(
            query_text=query_text,
            table_name="ENRICHED_HUBSPOT_DEALS",
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metadata_filters=metadata_filters,
        )

    async def search_gong_calls_with_ai_memory(
        self,
        query_text: str,
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        call_direction: str | None = None,
        date_range_days: int | None = None,
        sentiment_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search Gong calls using AI Memory embeddings"""
        metadata_filters = {}
        if sentiment_filter:
            metadata_filters["sentiment_category"] = sentiment_filter
            
        return await self.vector_search_business_table(
            query_text=query_text,
            table_name="ENRICHED_GONG_CALLS",
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metadata_filters=metadata_filters,
        )

    async def log_etl_job_status(self, job_log: dict[str, Any]) -> bool:
        """Log ETL job status to monitoring table"""
        if not self.initialized:
            await self.initialize()

        try:
            insert_query = """
            INSERT INTO ETL_JOB_LOGS (
                job_name, status, start_time, end_time, 
                records_processed, error_message, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            await self.connection_manager.execute_query(
                insert_query,
                (
                    job_log.get("job_name"),
                    job_log.get("status"),
                    job_log.get("start_time"),
                    job_log.get("end_time"),
                    job_log.get("records_processed", 0),
                    job_log.get("error_message"),
                    str(job_log.get("metadata", {})),
                )
            )
            
            logger.info(f"Logged ETL job status: {job_log.get('job_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging ETL job status: {e}")
            return False

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            "facade_stats": self.performance_monitor.get_performance_stats(),
            "cortex_handler_stats": self.cortex_handlers.get_performance_stats(),
            "cache_stats": self.cache_manager.get_stats(),
        }


# Factory function for backward compatibility
async def get_cortex_service() -> SnowflakeCortexService:
    """Factory function to get Cortex service instance"""
    service = SnowflakeCortexService()
    await service.initialize()
    return service


# Standalone functions for backward compatibility
async def summarize_hubspot_contact_notes(
    contact_id: str, max_length: int = 150
) -> dict[str, Any]:
    """Summarize HubSpot contact notes"""
    service = await get_cortex_service()
    
    try:
        results = await service.summarize_text_in_snowflake(
            text_column="notes",
            table_name="HUBSPOT_CONTACTS",
            conditions=f"contact_id = '{contact_id}'",
            max_length=max_length,
        )
        
        if results:
            return {
                "contact_id": contact_id,
                "summary": results[0]["ai_summary"],
                "original_notes_count": len(results),
                "processed_at": results[0]["processed_at"],
            }
        else:
            return {
                "contact_id": contact_id,
                "summary": "No notes found",
                "original_notes_count": 0,
                "processed_at": None,
            }
            
    except Exception as e:
        logger.error(f"Error summarizing contact notes: {e}")
        return {
            "contact_id": contact_id,
            "summary": f"Error: {str(e)}",
            "original_notes_count": 0,
            "processed_at": None,
        }


async def analyze_gong_call_sentiment(call_id: str) -> dict[str, Any]:
    """Analyze sentiment of a Gong call"""
    service = await get_cortex_service()
    
    try:
        results = await service.analyze_sentiment_in_snowflake(
            text_column="transcript",
            table_name="GONG_CALL_TRANSCRIPTS",
            conditions=f"call_id = '{call_id}'",
        )
        
        if results:
            avg_sentiment = sum(r["sentiment_score"] for r in results) / len(results)
            sentiment_distribution = {}
            for result in results:
                label = result["sentiment_label"]
                sentiment_distribution[label] = sentiment_distribution.get(label, 0) + 1
                
            return {
                "call_id": call_id,
                "average_sentiment": avg_sentiment,
                "sentiment_distribution": sentiment_distribution,
                "segments_analyzed": len(results),
                "overall_sentiment": "POSITIVE" if avg_sentiment > 0.1 else "NEGATIVE" if avg_sentiment < -0.1 else "NEUTRAL",
            }
        else:
            return {
                "call_id": call_id,
                "average_sentiment": 0.0,
                "sentiment_distribution": {},
                "segments_analyzed": 0,
                "overall_sentiment": "UNKNOWN",
            }
            
    except Exception as e:
        logger.error(f"Error analyzing call sentiment: {e}")
        return {
            "call_id": call_id,
            "error": str(e),
            "average_sentiment": 0.0,
            "sentiment_distribution": {},
            "segments_analyzed": 0,
            "overall_sentiment": "ERROR",
        }
