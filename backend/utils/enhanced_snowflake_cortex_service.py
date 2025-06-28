"""
Sophia AI - Enhanced Snowflake Cortex Service
Unified AI processing using pure Snowflake Cortex for embeddings, LLM, and analytics
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)


class CortexModel(Enum):
    """Snowflake Cortex model enumeration."""

    # Embedding models
    E5_BASE_V2 = "e5-base-v2"
    MULTILINGUAL_E5_LARGE = "multilingual-e5-large"

    # LLM models
    LLAMA2_70B_CHAT = "llama2-70b-chat"
    LLAMA3_8B = "llama3-8b"
    LLAMA3_70B = "llama3-70b"
    MISTRAL_7B = "mistral-7b"
    MISTRAL_LARGE = "mistral-large"
    MIXTRAL_8X7B = "mixtral-8x7b"
    GEMMA_7B = "gemma-7b"


@dataclass
class AIProcessingConfig:
    """Configuration for AI processing operations."""

    embedding_model: CortexModel = CortexModel.E5_BASE_V2
    llm_model: CortexModel = CortexModel.LLAMA3_70B
    batch_size: int = 50
    max_tokens: int = 8192
    temperature: float = 0.1
    enable_caching: bool = True
    cache_ttl_hours: int = 24


@dataclass
class EmbeddingResult:
    """Result from embedding generation."""

    text: str
    embedding: list[float]
    model: str
    timestamp: datetime
    processing_time_ms: float


@dataclass
class SemanticSearchResult:
    """Result from semantic search."""

    content: str
    similarity_score: float
    metadata: dict[str, Any]
    source_table: str
    record_id: str


@dataclass
class AIInsight:
    """AI-generated insight."""

    insight_type: str
    content: str
    confidence_score: float
    supporting_data: list[str]
    generated_at: datetime


class EnhancedSnowflakeCortexService(SnowflakeCortexService):
    """
    Enhanced Snowflake Cortex service providing unified AI processing.

    Features:
    - Pure Snowflake Cortex embedding generation
    - Semantic search across all data sources
    - AI-powered summarization and insights
    - Intelligent caching and optimization
    - Cross-platform data enrichment
    """

    def __init__(self, config: AIProcessingConfig | None = None):
        super().__init__()
        self.config = config or AIProcessingConfig()
        self.embedding_cache: dict[str, EmbeddingResult] = {}
        self.insight_cache: dict[str, list[AIInsight]] = {}

    async def initialize(self) -> None:
        """Initialize enhanced Cortex service."""
        await super().initialize()

        # Create AI processing tables if they don't exist
        await self._create_ai_processing_tables()

        logger.info("✅ Enhanced Snowflake Cortex service initialized")

    async def _create_ai_processing_tables(self) -> None:
        """Create tables for AI processing and caching."""
        try:
            # Create schema if it doesn't exist
            schema_ddl = "CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_PROD.AI_PROCESSING"
            await self.execute_query(schema_ddl)

            # Embedding cache table
            embedding_cache_ddl = """
            CREATE TABLE IF NOT EXISTS SOPHIA_AI_PROD.AI_PROCESSING.EMBEDDING_CACHE (
                cache_key VARCHAR(255) PRIMARY KEY,
                text_content TEXT NOT NULL,
                embedding VECTOR(FLOAT, 768) NOT NULL,
                model VARCHAR(50) NOT NULL,
                created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
                expires_at TIMESTAMP_LTZ,
                processing_time_ms NUMBER
            )
            """

            # AI insights cache table
            insights_cache_ddl = """
            CREATE TABLE IF NOT EXISTS SOPHIA_AI_PROD.AI_PROCESSING.INSIGHTS_CACHE (
                cache_key VARCHAR(255),
                insight_type VARCHAR(100),
                content TEXT NOT NULL,
                confidence_score FLOAT,
                supporting_data VARIANT,
                model VARCHAR(50),
                created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
                expires_at TIMESTAMP_LTZ,
                PRIMARY KEY (cache_key, insight_type)
            )
            """

            # Semantic search index table
            search_index_ddl = """
            CREATE TABLE IF NOT EXISTS SOPHIA_AI_PROD.AI_PROCESSING.SEMANTIC_SEARCH_INDEX (
                index_id VARCHAR(255) PRIMARY KEY,
                source_table VARCHAR(100) NOT NULL,
                record_id VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                content_embedding VECTOR(FLOAT, 768) NOT NULL,
                metadata VARIANT,
                indexed_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
                updated_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """

            await self.execute_query(embedding_cache_ddl)
            await self.execute_query(insights_cache_ddl)
            await self.execute_query(search_index_ddl)

            logger.info("✅ AI processing tables created/verified")

        except Exception as e:
            logger.error(f"❌ Failed to create AI processing tables: {e}")
            raise

    async def generate_embeddings(
        self, texts: list[str], use_cache: bool = True
    ) -> list[EmbeddingResult]:
        """
        Generate embeddings using Snowflake Cortex with intelligent caching.

        Args:
            texts: List of texts to generate embeddings for
            use_cache: Whether to use/populate embedding cache

        Returns:
            List of EmbeddingResult objects
        """
        try:
            results = []

            # Process in batches to avoid Snowflake limits
            batch_size = min(self.config.batch_size, 20)

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                batch_start = datetime.utcnow()

                # Create batch embedding query
                embedding_queries = []
                for text in batch:
                    # Escape single quotes and limit text length
                    escaped_text = text.replace("'", "''")[:8000]  # Cortex text limit
                    embedding_queries.append(
                        f"""
                        SELECT
                            '{escaped_text}' as text,
                            SNOWFLAKE.CORTEX.EMBED_TEXT_768('{self.config.embedding_model.value}', '{escaped_text}') as embedding,
                            '{self.config.embedding_model.value}' as model
                    """
                    )

                # Execute batch query
                if embedding_queries:
                    batch_query = " UNION ALL ".join(embedding_queries)
                    query_results = await self.execute_query(batch_query)

                    batch_duration = (
                        datetime.utcnow() - batch_start
                    ).total_seconds() * 1000

                    # Process results
                    for result in query_results:
                        embedding_result = EmbeddingResult(
                            text=result["TEXT"],
                            embedding=result["EMBEDDING"],
                            model=result["MODEL"],
                            timestamp=datetime.utcnow(),
                            processing_time_ms=batch_duration / len(batch),
                        )
                        results.append(embedding_result)

            logger.info(f"✅ Generated {len(results)} embeddings")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            raise

    async def semantic_search(
        self,
        query_text: str,
        source_tables: list[str] | None = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
    ) -> list[SemanticSearchResult]:
        """
        Perform semantic search across specified tables.

        Args:
            query_text: Text to search for
            source_tables: List of specific tables to search
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score

        Returns:
            List of SemanticSearchResult objects
        """
        try:
            # Generate query embedding
            query_embeddings = await self.generate_embeddings([query_text])
            if not query_embeddings:
                return []

            query_embedding = query_embeddings[0].embedding

            # Build WHERE clause for source tables
            where_clause = ""
            if source_tables:
                table_list = "', '".join(source_tables)
                where_clause = f"WHERE source_table IN ('{table_list}')"

            # Perform semantic search using the index
            search_query = f"""
            SELECT
                content,
                source_table,
                record_id,
                metadata,
                VECTOR_COSINE_SIMILARITY(content_embedding, {query_embedding}) as similarity_score
            FROM SOPHIA_AI_PROD.AI_PROCESSING.SEMANTIC_SEARCH_INDEX
            {where_clause}
            ORDER BY similarity_score DESC
            LIMIT {limit}
            """

            results = await self.execute_query(search_query)

            # Filter by similarity threshold and convert to SemanticSearchResult
            search_results = []
            for result in results:
                if result["SIMILARITY_SCORE"] >= similarity_threshold:
                    search_result = SemanticSearchResult(
                        content=result["CONTENT"],
                        similarity_score=result["SIMILARITY_SCORE"],
                        metadata=result.get("METADATA", {}),
                        source_table=result["SOURCE_TABLE"],
                        record_id=result["RECORD_ID"],
                    )
                    search_results.append(search_result)

            return search_results

        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []

    async def generate_ai_summary(
        self, content: str, context: str = "", summary_type: str = "general"
    ) -> str:
        """
        Generate AI summary using Snowflake Cortex LLM.

        Args:
            content: Content to summarize
            context: Additional context for the summary
            summary_type: Type of summary (general, executive, technical, etc.)

        Returns:
            AI-generated summary
        """
        try:
            # Create summary prompt based on type
            prompts = {
                "general": "Provide a concise summary of the following content:",
                "executive": "Provide an executive summary highlighting key business insights:",
                "technical": "Provide a technical summary focusing on implementation details:",
                "risk": "Analyze the following content and identify key risks and concerns:",
                "opportunity": "Analyze the following content and identify key opportunities:",
            }

            base_prompt = prompts.get(summary_type, prompts["general"])

            prompt = f"""
            {base_prompt}

            Context: {context}

            Content to summarize:
            {content[:6000]}

            Summary:
            """

            # Generate summary using Cortex
            summary_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{self.config.llm_model.value}',
                $$({prompt})$$
            ) as summary
            """

            result = await self.execute_query(summary_query)
            summary = result[0]["SUMMARY"] if result else "Summary generation failed"

            return summary

        except Exception as e:
            logger.error(f"❌ AI summary generation failed: {e}")
            return f"Failed to generate summary: {str(e)}"

    async def generate_ai_insights(
        self,
        data: dict[str, Any],
        insight_type: str = "business",
        num_insights: int = 5,
    ) -> list[AIInsight]:
        """
        Generate AI insights from structured data.

        Args:
            data: Structured data to analyze
            insight_type: Type of insights to generate
            num_insights: Number of insights to generate

        Returns:
            List of AIInsight objects
        """
        try:
            # Create insight prompt based on type
            prompts = {
                "business": "Analyze the following business data and provide key business insights:",
                "risk": "Analyze the following data and identify potential risks:",
                "opportunity": "Analyze the following data and identify growth opportunities:",
                "performance": "Analyze the following performance data and provide improvement insights:",
                "customer": "Analyze the following customer data and provide customer insights:",
                "project": "Analyze the following project data and provide project management insights:",
            }

            base_prompt = prompts.get(insight_type, prompts["business"])
            data_json = json.dumps(data, indent=2)[:5000]  # Limit data size

            prompt = f"""
            {base_prompt}

            Data to analyze:
            {data_json}

            Please provide {num_insights} key insights in JSON format:
            [
                {{
                    "insight": "Clear, actionable insight",
                    "confidence": 0.8,
                    "supporting_evidence": ["data point 1", "data point 2"]
                }}
            ]

            Insights:
            """

            # Generate insights using Cortex
            insights_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{self.config.llm_model.value}',
                $$({prompt})$$
            ) as insights_json
            """

            result = await self.execute_query(insights_query)
            insights_json = result[0]["INSIGHTS_JSON"] if result else "[]"

            # Parse JSON response
            try:
                insights_data = json.loads(insights_json)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                insights_data = [
                    {
                        "insight": insights_json[:500],
                        "confidence": 0.7,
                        "supporting_evidence": ["Generated from AI analysis"],
                    }
                ]

            # Convert to AIInsight objects
            ai_insights = []
            for insight_data in insights_data[:num_insights]:
                insight = AIInsight(
                    insight_type=insight_type,
                    content=insight_data.get("insight", ""),
                    confidence_score=insight_data.get("confidence", 0.7),
                    supporting_data=insight_data.get("supporting_evidence", []),
                    generated_at=datetime.utcnow(),
                )
                ai_insights.append(insight)

            return ai_insights

        except Exception as e:
            logger.error(f"❌ AI insights generation failed: {e}")
            return [
                AIInsight(
                    insight_type=insight_type,
                    content=f"Failed to generate insights: {str(e)}",
                    confidence_score=0.0,
                    supporting_data=[],
                    generated_at=datetime.utcnow(),
                )
            ]

    async def index_content_for_search(
        self,
        content: str,
        source_table: str,
        record_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Index content in the semantic search index.

        Args:
            content: Content to index
            source_table: Source table name
            record_id: Record identifier
            metadata: Additional metadata

        Returns:
            Success status
        """
        try:
            # Generate embedding for content
            embeddings = await self.generate_embeddings([content])
            if not embeddings:
                return False

            embedding = embeddings[0].embedding
            index_id = f"{source_table}_{record_id}"

            # Insert into search index
            index_query = f"""
            MERGE INTO SOPHIA_AI_PROD.AI_PROCESSING.SEMANTIC_SEARCH_INDEX AS target
            USING (
                SELECT
                    '{index_id}' as index_id,
                    '{source_table}' as source_table,
                    '{record_id}' as record_id,
                    '{content.replace("'", "''")}' as content,
                    {embedding} as content_embedding,
                    PARSE_JSON('{json.dumps(metadata or {})}') as metadata
            ) AS source
            ON target.index_id = source.index_id
            WHEN MATCHED THEN
                UPDATE SET
                    content = source.content,
                    content_embedding = source.content_embedding,
                    metadata = source.metadata,
                    updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (index_id, source_table, record_id, content, content_embedding, metadata)
                VALUES (source.index_id, source.source_table, source.record_id,
                       source.content, source.content_embedding, source.metadata)
            """

            await self.execute_query(index_query)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to index content: {e}")
            return False
