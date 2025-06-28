"""
Snowflake Cortex AI Service

Utility module for leveraging Snowflake Cortex AI capabilities directly within Snowflake.
This module provides a Python interface to Snowflake's native AI functions including
text summarization, sentiment analysis, embeddings, and vector search.

Key Features:
- Native Snowflake AI processing with SNOWFLAKE.CORTEX functions
- Vector embeddings and semantic search within Snowflake
- Text analysis and summarization for business intelligence
- Integration with HubSpot and Gong data for contextual AI
- Reduced dependency on external AI services for specific use cases
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

import pandas as pd
import snowflake.connector

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


# Custom Exception Classes
class CortexEmbeddingError(Exception):
    """Raised when Snowflake Cortex embedding generation fails"""

    pass


class InsufficientPermissionsError(Exception):
    """Raised when user lacks required Snowflake permissions"""

    pass


class BusinessTableNotFoundError(Exception):
    """Raised when business table doesn't exist or is not accessible"""

    pass


class InvalidInputError(Exception):
    """Raised when input parameters are invalid"""

    pass


class CortexModel(Enum):
    """Available Snowflake Cortex models"""

    # Text generation models
    LLAMA2_70B = "llama2-70b-chat"
    MISTRAL_7B = "mistral-7b"
    MISTRAL_LARGE = "mistral-large"
    MIXTRAL_8X7B = "mixtral-8x7b"

    # Embedding models
    E5_BASE_V2 = "e5-base-v2"
    MULTILINGUAL_E5_LARGE = "multilingual-e5-large"

    # Analysis models
    SENTIMENT_ANALYSIS = "sentiment"
    SUMMARIZATION = "summarize"


@dataclass
class CortexQuery:
    """Configuration for Cortex AI queries"""

    model: CortexModel
    input_text: str
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[str] = None
    max_tokens: Optional[int] = None


@dataclass
class VectorSearchResult:
    """Result from vector similarity search"""

    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    source_table: str
    source_id: str


class SnowflakeCortexService:
    """
    Service for accessing Snowflake Cortex AI capabilities

    This class provides methods to use Snowflake's native AI functions
    for text processing, embeddings, and vector search directly within
    the data warehouse.
    """

    def __init__(self):
        # Remove individual connection - use optimized connection manager
        from backend.core.optimized_connection_manager import connection_manager
        self.connection_manager = connection_manager
        
        self.database = get_config_value("snowflake_database", "SOPHIA_AI")
        self.schema = get_config_value("snowflake_schema", "AI_PROCESSING")
        self.warehouse = get_config_value("snowflake_warehouse", "COMPUTE_WH")
        self.initialized = False

        # Vector storage tables
        self.vector_tables = {
            "hubspot_embeddings": "HUBSPOT_CONTACT_EMBEDDINGS",
            "gong_embeddings": "GONG_CALL_EMBEDDINGS",
            "document_embeddings": "DOCUMENT_EMBEDDINGS",
            "memory_embeddings": "AI_MEMORY_EMBEDDINGS",
        }

    async def __aenter__(self):
        """Async context manager entry - initialize connection"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources"""
        # No need to close individual connection - managed by connection manager
        pass

    async def initialize(self) -> None:
        """Initialize Snowflake connection for Cortex AI processing"""
        if self.initialized:
            return

        try:
            # Use connection manager instead of individual connection
            await self.connection_manager.initialize()
            
            # Set database and schema context
            await self.connection_manager.execute_query(f"USE DATABASE {self.database}")
            await self.connection_manager.execute_query(f"USE SCHEMA {self.schema}")
            await self.connection_manager.execute_query(f"USE WAREHOUSE {self.warehouse}")

            # Ensure vector tables exist
            await self._create_vector_tables()

            self.initialized = True
            logger.info("✅ Snowflake Cortex service initialized successfully with optimized connection manager")

        except Exception as e:
            logger.error(f"Failed to initialize Snowflake Cortex service: {e}")
            raise

    async def summarize_text_in_snowflake(
        self,
        text_column: str,
        table_name: str,
        conditions: Optional[str] = None,
        max_length: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Summarize text data using Snowflake Cortex SUMMARIZE function

        Args:
            text_column: Column containing text to summarize
            table_name: Source table name
            conditions: Optional WHERE conditions
            max_length: Maximum summary length

        Returns:
            List of records with original text and AI-generated summaries
        """
        if not self.initialized:
            await self.initialize()

        # Build query using Snowflake Cortex SUMMARIZE function
        query = f"""
        SELECT 
            id,
            {text_column} as original_text,
            SNOWFLAKE.CORTEX.SUMMARIZE(
                {text_column},
                {max_length}
            ) as ai_summary,
            CURRENT_TIMESTAMP() as processed_at
        FROM {table_name}
        """

        if conditions:
            query += f" WHERE {conditions}"

        query += " ORDER BY id"

        try:
            # Use connection manager instead of direct cursor
            results = await self.connection_manager.execute_query(query)
            
            summaries = []
            for row in results:
                # Convert row to dictionary format
                record = {
                    'id': row[0],
                    'original_text': row[1], 
                    'ai_summary': row[2],
                    'processed_at': row[3]
                }
                summaries.append(record)

            logger.info(f"Generated {len(summaries)} text summaries using Cortex")
            return summaries

        except Exception as e:
            logger.error(f"Error generating summaries with Cortex: {e}")
            raise

    async def analyze_sentiment_in_snowflake(
        self, text_column: str, table_name: str, conditions: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze sentiment using Snowflake Cortex SENTIMENT function

        Args:
            text_column: Column containing text to analyze
            table_name: Source table name
            conditions: Optional WHERE conditions

        Returns:
            List of records with sentiment scores and classifications
        """
        if not self.initialized:
            await self.initialize()

        query = f"""
        SELECT 
            id,
            {text_column} as text,
            SNOWFLAKE.CORTEX.SENTIMENT({text_column}) as sentiment_score,
            CASE 
                WHEN SNOWFLAKE.CORTEX.SENTIMENT({text_column}) > 0.1 THEN 'POSITIVE'
                WHEN SNOWFLAKE.CORTEX.SENTIMENT({text_column}) < -0.1 THEN 'NEGATIVE'
                ELSE 'NEUTRAL'
            END as sentiment_label,
            CURRENT_TIMESTAMP() as analyzed_at
        FROM {table_name}
        """

        if conditions:
            query += f" WHERE {conditions}"

        try:
            # Use connection manager instead of direct cursor
            results = await self.connection_manager.execute_query(query)
            
            sentiment_analysis = []
            for row in results:
                # Convert row to dictionary format
                record = {
                    'id': row[0],
                    'text': row[1],
                    'sentiment_score': row[2],
                    'sentiment_label': row[3],
                    'analyzed_at': row[4]
                }
                sentiment_analysis.append(record)

            logger.info(
                f"Analyzed sentiment for {len(sentiment_analysis)} records using Cortex"
            )
            return sentiment_analysis

        except Exception as e:
            logger.error(f"Error analyzing sentiment with Cortex: {e}")
            raise

    async def generate_embedding_in_snowflake(
        self,
        text_column: str,
        table_name: str,
        conditions: Optional[str] = None,
        model: str = "e5-base-v2",
        store_embeddings: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings using Snowflake Cortex EMBED_TEXT function

        Args:
            text_column: Column containing text to embed
            table_name: Source table name
            conditions: Optional WHERE conditions
            model: Embedding model to use
            store_embeddings: Whether to store embeddings in vector table

        Returns:
            List of records with generated embeddings
        """
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
            cursor = self.connection.cursor()
            cursor.execute(query)

            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            embeddings = []
            for row in results:
                record = dict(zip(columns, row))
                embeddings.append(record)

            # Optionally store embeddings in dedicated vector table
            if store_embeddings and embeddings:
                await self._store_embeddings(embeddings, table_name)

            logger.info(f"Generated {len(embeddings)} embeddings using Cortex {model}")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings with Cortex: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    async def vector_search_in_snowflake(
        self,
        query_text: str,
        vector_table: str,
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        model: str = "e5-base-v2",
    ) -> List[VectorSearchResult]:
        """
        Perform vector similarity search using Snowflake native functions

        Args:
            query_text: Text to search for
            vector_table: Table containing stored embeddings
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            model: Embedding model for query encoding

        Returns:
            List of similar content with scores and metadata
        """
        if not self.initialized:
            await self.initialize()

        # Generate embedding for query text
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
            cursor = self.connection.cursor()
            cursor.execute(query)

            results = []
            for row in cursor.fetchall():
                result = VectorSearchResult(
                    content=row[1],
                    similarity_score=row[5],
                    metadata=row[2] if row[2] else {},
                    source_table=row[3],
                    source_id=row[4],
                )
                results.append(result)

            logger.info(
                f"Found {len(results)} similar results for query: {query_text[:50]}..."
            )
            return results

        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    async def complete_text_with_cortex(
        self,
        prompt: str,
        model: CortexModel = CortexModel.MISTRAL_7B,
        max_tokens: int = 500,
        temperature: float = 0.7,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate text completion using Snowflake Cortex LLM functions

        Args:
            prompt: Input prompt for text generation
            model: Cortex model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            context: Optional context for the prompt

        Returns:
            Generated text completion
        """
        if not self.initialized:
            await self.initialize()

        # Combine context and prompt if provided
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
            cursor = self.connection.cursor()
            cursor.execute(query)

            result = cursor.fetchone()
            completion = result[0] if result else ""

            logger.info(f"Generated text completion using {model.value}")
            return completion

        except Exception as e:
            logger.error(f"Error generating text completion: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    async def extract_entities_from_text(
        self,
        text_column: str,
        table_name: str,
        entity_types: List[str],
        conditions: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract named entities from text using Cortex capabilities

        Args:
            text_column: Column containing text to analyze
            table_name: Source table name
            entity_types: Types of entities to extract (PERSON, ORG, MONEY, etc.)
            conditions: Optional WHERE conditions

        Returns:
            List of records with extracted entities
        """
        if not self.initialized:
            await self.initialize()

        # Use Cortex completion to extract entities
        entity_prompt = f"Extract the following entity types from the text: {', '.join(entity_types)}. Return as JSON."

        query = f"""
        SELECT 
            id,
            {text_column} as text,
            SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-7b',
                CONCAT('{entity_prompt}\\n\\nText: ', {text_column}),
                {{'max_tokens': 200}}
            ) as extracted_entities,
            CURRENT_TIMESTAMP() as extracted_at
        FROM {table_name}
        """

        if conditions:
            query += f" WHERE {conditions}"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)

            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            entities = []
            for row in results:
                record = dict(zip(columns, row))
                entities.append(record)

            logger.info(f"Extracted entities from {len(entities)} records")
            return entities

        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    async def _create_vector_tables(self):
        """Create vector storage tables if they don't exist"""

        for table_key, table_name in self.vector_tables.items():
            create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id STRING,
                original_text STRING,
                embedding_vector VECTOR(FLOAT, 768),  -- Adjust dimensions based on model
                embedding_model STRING,
                metadata VARIANT,
                source_table STRING,
                source_id STRING,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            )
            """

            try:
                cursor = self.connection.cursor()
                cursor.execute(create_query)
                logger.debug(f"Ensured vector table {table_name} exists")
            except Exception as e:
                logger.warning(f"Could not create vector table {table_name}: {e}")
            finally:
                if cursor:
                    cursor.close()

    async def _store_embeddings(
        self, embeddings: List[Dict[str, Any]], source_table: str
    ):
        """Store embeddings in dedicated vector table"""

        vector_table = self.vector_tables.get(
            "document_embeddings", "DOCUMENT_EMBEDDINGS"
        )

        # Prepare insert data
        insert_data = []
        for embedding in embeddings:
            insert_data.append(
                (
                    embedding["id"],
                    embedding["text"],
                    embedding["embedding_vector"],
                    embedding["embedding_model"],
                    None,  # metadata
                    source_table,
                    embedding["id"],
                )
            )

        insert_query = f"""
        INSERT INTO {vector_table} 
        (id, original_text, embedding_vector, embedding_model, metadata, source_table, source_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        try:
            cursor = self.connection.cursor()
            cursor.executemany(insert_query, insert_data)
            logger.info(f"Stored {len(insert_data)} embeddings in {vector_table}")
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    async def close(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            self.initialized = False
            logger.info("Snowflake Cortex service connection closed")

    async def store_embedding_in_business_table(
        self,
        table_name: str,
        record_id: str,
        text_content: str,
        embedding_column: str = "ai_memory_embedding",
        metadata: Optional[Dict[str, Any]] = None,
        model: str = "e5-base-v2",
    ) -> bool:
        """
        Store embedding directly in business table using SNOWFLAKE.CORTEX.EMBED_TEXT_768

        Args:
            table_name: Business table name (e.g., ENRICHED_GONG_CALLS, ENRICHED_HUBSPOT_DEALS)
            record_id: Primary key value for the record
            text_content: Text content to embed
            embedding_column: Column name for storing embedding (should be VECTOR(FLOAT, 768))
            metadata: Optional metadata to store
            model: Embedding model to use (should produce 768-dimensional vectors)

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If record doesn't exist or invalid parameters
            CortexEmbeddingError: If embedding generation fails
            InsufficientPermissionsError: If lacking required permissions
        """
        if not self.initialized:
            await self.initialize()

        # Input validation
        ALLOWED_TABLES = {"ENRICHED_HUBSPOT_DEALS", "ENRICHED_GONG_CALLS"}
        ALLOWED_EMBEDDING_COLUMNS = {"ai_memory_embedding"}
        ALLOWED_MODELS = {"e5-base-v2", "multilingual-e5-large"}

        if table_name not in ALLOWED_TABLES:
            raise ValueError(
                f"Table {table_name} not allowed. Allowed: {ALLOWED_TABLES}"
            )

        if embedding_column not in ALLOWED_EMBEDDING_COLUMNS:
            raise ValueError(f"Embedding column {embedding_column} not allowed")

        if model not in ALLOWED_MODELS:
            raise ValueError(f"Model {model} not allowed. Allowed: {ALLOWED_MODELS}")

        if not text_content or not text_content.strip():
            raise ValueError("Text content cannot be empty")

        if len(text_content) > 8000:  # Snowflake Cortex limit
            logger.warning(
                f"Text content truncated from {len(text_content)} to 8000 characters"
            )
            text_content = text_content[:8000]

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Step 1: Verify record exists
            check_query = f"SELECT 1 FROM {table_name} WHERE id = %s"
            cursor.execute(check_query, (record_id,))
            record_exists = cursor.fetchone() is not None

            if not record_exists:
                raise ValueError(f"Record {record_id} not found in {table_name}")

            # Step 2: Generate embedding with error handling
            try:
                embed_query = (
                    "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(%s, %s) as embedding"
                )
                cursor.execute(embed_query, (model, text_content))
                embedding_result = cursor.fetchone()

                if not embedding_result or not embedding_result[0]:
                    raise CortexEmbeddingError(
                        f"Failed to generate embedding with model {model}"
                    )

                generated_embedding = embedding_result[0]

            except Exception as cortex_error:
                if "insufficient credits" in str(cortex_error).lower():
                    raise CortexEmbeddingError(
                        "Insufficient Snowflake credits for embedding generation"
                    )
                elif "model not available" in str(cortex_error).lower():
                    raise CortexEmbeddingError(
                        f"Model {model} not available in Snowflake Cortex"
                    )
                elif "text too long" in str(cortex_error).lower():
                    raise CortexEmbeddingError("Text content exceeds model limits")
                else:
                    raise CortexEmbeddingError(
                        f"Cortex embedding error: {cortex_error}"
                    )

            # Step 3: Serialize metadata properly
            metadata_json = None
            if metadata:
                try:
                    metadata_json = json.dumps(
                        metadata, default=str, ensure_ascii=False
                    )
                except (TypeError, ValueError) as e:
                    logger.warning(f"Failed to serialize metadata: {e}")
                    metadata_json = json.dumps(
                        {"error": "failed_to_serialize", "original_error": str(e)}
                    )

            # Step 4: Update record with embedding and metadata
            update_query = f"""
            UPDATE {table_name}
            SET 
                {embedding_column} = %s,
                ai_memory_metadata = %s,
                ai_memory_updated_at = CURRENT_TIMESTAMP()
            WHERE id = %s
            """

            cursor.execute(
                update_query, (generated_embedding, metadata_json, record_id)
            )
            rows_affected = cursor.rowcount

            if rows_affected > 0:
                logger.info(
                    f"Successfully stored embedding for {record_id} in {table_name}"
                )
                return True
            else:
                logger.error(
                    f"No rows updated for {record_id} in {table_name} - this should not happen"
                )
                return False

        except ValueError:
            # Re-raise validation errors
            raise
        except CortexEmbeddingError:
            # Re-raise Cortex-specific errors
            raise
        except Exception as e:
            if (
                "permission denied" in str(e).lower()
                or "access denied" in str(e).lower()
            ):
                raise InsufficientPermissionsError(
                    f"Insufficient permissions to update {table_name}: {e}"
                )
            else:
                logger.error(
                    f"Unexpected error storing embedding in business table: {e}"
                )
                return False
        finally:
            if cursor:
                cursor.close()

    async def vector_search_business_table(
        self,
        query_text: str,
        table_name: str,
        embedding_column: str = "ai_memory_embedding",
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        metadata_filters: Optional[Dict[str, Any]] = None,
        model: str = "e5-base-v2",
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search directly on business tables with metadata filtering

        Args:
            query_text: Text to search for
            table_name: Business table name (e.g., ENRICHED_GONG_CALLS, ENRICHED_HUBSPOT_DEALS)
            embedding_column: Column containing embeddings
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            metadata_filters: Optional filters (e.g., {'deal_id': '123', 'sentiment_category': 'positive'})
            model: Embedding model for query encoding

        Returns:
            List of similar records with business context

        Raises:
            InvalidInputError: If input parameters are invalid
            BusinessTableNotFoundError: If table doesn't exist
            CortexEmbeddingError: If query embedding generation fails
        """
        if not self.initialized:
            await self.initialize()

        # Input validation
        ALLOWED_TABLES = {"ENRICHED_HUBSPOT_DEALS", "ENRICHED_GONG_CALLS"}
        ALLOWED_EMBEDDING_COLUMNS = {"ai_memory_embedding"}
        ALLOWED_FILTER_COLUMNS = {
            "deal_stage",
            "sentiment_category",
            "primary_user_name",
            "hubspot_deal_id",
            "call_type",
            "id",
            "contact_id",
        }
        ALLOWED_MODELS = {"e5-base-v2", "multilingual-e5-large"}

        # Validate table name
        if table_name not in ALLOWED_TABLES:
            raise InvalidInputError(
                f"Table {table_name} not allowed. Allowed: {ALLOWED_TABLES}"
            )

        # Validate embedding column
        if embedding_column not in ALLOWED_EMBEDDING_COLUMNS:
            raise InvalidInputError(f"Embedding column {embedding_column} not allowed")

        # Validate model
        if model not in ALLOWED_MODELS:
            raise InvalidInputError(
                f"Model {model} not allowed. Allowed: {ALLOWED_MODELS}"
            )

        # Validate query text
        if not query_text or not query_text.strip():
            raise InvalidInputError("Query text cannot be empty")

        if len(query_text) > 8000:  # Snowflake Cortex limit
            logger.warning(
                f"Query text truncated from {len(query_text)} to 8000 characters"
            )
            query_text = query_text[:8000]

        # Validate parameters
        if top_k <= 0 or top_k > 100:
            raise InvalidInputError("top_k must be between 1 and 100")

        if not 0.0 <= similarity_threshold <= 1.0:
            raise InvalidInputError("similarity_threshold must be between 0.0 and 1.0")

        # Validate metadata filters
        if metadata_filters:
            for key in metadata_filters.keys():
                if key not in ALLOWED_FILTER_COLUMNS:
                    raise InvalidInputError(
                        f"Filter column {key} not allowed. Allowed: {ALLOWED_FILTER_COLUMNS}"
                    )

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Step 1: Verify table exists and has required columns
            table_check_query = """
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = %s 
              AND TABLE_SCHEMA = %s 
              AND TABLE_CATALOG = %s
            """
            cursor.execute(table_check_query, (table_name, self.schema, self.database))
            table_exists = cursor.fetchone()[0] > 0

            if not table_exists:
                raise BusinessTableNotFoundError(
                    f"Table {table_name} not found in {self.database}.{self.schema}"
                )

            # Step 2: Generate query embedding with error handling
            try:
                embed_query = (
                    "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(%s, %s) as query_vector"
                )
                cursor.execute(embed_query, (model, query_text))
                embedding_result = cursor.fetchone()

                if not embedding_result or not embedding_result[0]:
                    raise CortexEmbeddingError(
                        f"Failed to generate query embedding with model {model}"
                    )

                query_embedding = embedding_result[0]

            except Exception as cortex_error:
                if "insufficient credits" in str(cortex_error).lower():
                    raise CortexEmbeddingError(
                        "Insufficient Snowflake credits for query embedding"
                    )
                elif "model not available" in str(cortex_error).lower():
                    raise CortexEmbeddingError(
                        f"Model {model} not available in Snowflake Cortex"
                    )
                else:
                    raise CortexEmbeddingError(f"Query embedding error: {cortex_error}")

            # Step 3: Build WHERE clause with parameterized queries
            where_conditions = [f"{embedding_column} IS NOT NULL"]
            query_params = [query_embedding, similarity_threshold, top_k]

            if metadata_filters:
                for key, value in metadata_filters.items():
                    where_conditions.append(f"{key} = %s")
                    query_params.insert(-2, value)  # Insert before threshold and limit

            where_clause = " AND ".join(where_conditions)

            # Step 4: Build the vector search query with proper parameterization
            search_query = f"""
            SELECT 
                *,
                VECTOR_COSINE_SIMILARITY(%s, {embedding_column}) as similarity_score
            FROM {table_name}
            WHERE {where_clause}
              AND VECTOR_COSINE_SIMILARITY(%s, {embedding_column}) >= %s
            ORDER BY similarity_score DESC
            LIMIT %s
            """

            # Parameters: [query_embedding, query_embedding, ...metadata_values..., similarity_threshold, top_k]
            final_params = (
                [query_embedding, query_embedding]
                + query_params[:-2]
                + query_params[-2:]
            )

            cursor.execute(search_query, final_params)

            # Get column names and results
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            # Convert to list of dictionaries
            search_results = []
            for row in results:
                record = dict(zip(columns, row))
                search_results.append(record)

            logger.info(
                f"Found {len(search_results)} similar records in {table_name} for query: {query_text[:50]}..."
            )
            return search_results

        except InvalidInputError:
            # Re-raise validation errors
            raise
        except BusinessTableNotFoundError:
            # Re-raise table errors
            raise
        except CortexEmbeddingError:
            # Re-raise Cortex errors
            raise
        except Exception as e:
            if "permission denied" in str(e).lower():
                raise InsufficientPermissionsError(
                    f"Insufficient permissions to query {table_name}: {e}"
                )
            else:
                logger.error(f"Unexpected error in vector search: {e}")
                raise
        finally:
            if cursor:
                cursor.close()

    async def ensure_embedding_columns_exist(self, table_name: str) -> bool:
        """
        Ensure AI Memory embedding columns exist in business table

        Args:
            table_name: Business table name

        Returns:
            True if columns exist or were created successfully

        Raises:
            InvalidInputError: If table name is not allowed
            InsufficientPermissionsError: If lacking ALTER TABLE permissions
        """
        if not self.initialized:
            await self.initialize()

        # Input validation - only allow specific business tables
        ALLOWED_TABLES = {"ENRICHED_HUBSPOT_DEALS", "ENRICHED_GONG_CALLS"}

        if table_name not in ALLOWED_TABLES:
            raise InvalidInputError(
                f"Table {table_name} not allowed. Allowed: {ALLOWED_TABLES}"
            )

        cursor = None
        try:
            cursor = self.connection.cursor()

            # Use IF NOT EXISTS for safe concurrent execution
            alter_statements = [
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS ai_memory_embedding VECTOR(FLOAT, 768)",
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS ai_memory_metadata VARCHAR(16777216)",
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS ai_memory_updated_at TIMESTAMP_NTZ",
            ]

            # Execute within transaction for atomicity
            cursor.execute("BEGIN TRANSACTION")

            try:
                for statement in alter_statements:
                    cursor.execute(statement)
                    logger.info(f"Executed: {statement}")

                cursor.execute("COMMIT")
                logger.info(
                    f"✅ Successfully ensured AI Memory columns exist in {table_name}"
                )
                return True

            except Exception as alter_error:
                cursor.execute("ROLLBACK")

                if "permission denied" in str(alter_error).lower():
                    raise InsufficientPermissionsError(
                        f"Insufficient permissions to alter {table_name}: {alter_error}"
                    )
                else:
                    logger.error(f"Error adding columns to {table_name}: {alter_error}")
                    raise

        except InvalidInputError:
            # Re-raise validation errors
            raise
        except InsufficientPermissionsError:
            # Re-raise permission errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error ensuring embedding columns exist: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    async def search_hubspot_deals_with_ai_memory(
        self,
        query_text: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        deal_stage: Optional[str] = None,
        min_deal_value: Optional[float] = None,
        max_deal_value: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search HubSpot deals using AI Memory embeddings with business filters

        Args:
            query_text: Search query
            top_k: Number of results
            similarity_threshold: Minimum similarity
            deal_stage: Optional deal stage filter
            min_deal_value: Minimum deal value filter
            max_deal_value: Maximum deal value filter

        Returns:
            List of matching deals with similarity scores
        """
        # Build metadata filters
        metadata_filters = {}

        if deal_stage:
            metadata_filters["deal_stage"] = deal_stage

        # Add value range filtering in the search query
        additional_conditions = []
        if min_deal_value is not None:
            additional_conditions.append(f"amount >= {min_deal_value}")
        if max_deal_value is not None:
            additional_conditions.append(f"amount <= {max_deal_value}")

        # Use the enhanced vector search
        results = await self.vector_search_business_table(
            query_text=query_text,
            table_name="ENRICHED_HUBSPOT_DEALS",
            embedding_column="ai_memory_embedding",
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metadata_filters=metadata_filters,
        )

        # Apply additional value filters if needed
        if additional_conditions:
            filtered_results = []
            for result in results:
                amount = result.get("AMOUNT", 0) or 0
                if min_deal_value is not None and amount < min_deal_value:
                    continue
                if max_deal_value is not None and amount > max_deal_value:
                    continue
                filtered_results.append(result)
            results = filtered_results

        return results

    async def search_gong_calls_with_ai_memory(
        self,
        query_text: str,
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        call_direction: Optional[str] = None,
        date_range_days: Optional[int] = None,
        sentiment_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhanced semantic search across STG_GONG_CALLS with AI Memory integration
        
        Args:
            query_text: Natural language search query
            top_k: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            call_direction: Filter by call direction ('Inbound', 'Outbound')
            date_range_days: Filter calls from last N days
            sentiment_filter: Filter by sentiment ('positive', 'negative', 'neutral')
            
        Returns:
            List of matching Gong calls with similarity scores and AI Memory metadata
        """
        try:
            # Generate embedding for the search query
            query_embedding_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', '{query_text}') as query_embedding"
            embedding_result = await self.execute_query(query_embedding_sql)
            
            if embedding_result.empty:
                return []
            
            # Build the search query with filters
            filters = ["AI_MEMORY_EMBEDDING IS NOT NULL"]
            
            if call_direction:
                filters.append(f"CALL_DIRECTION = '{call_direction}'")
            
            if date_range_days:
                filters.append(f"CALL_DATETIME_UTC >= DATEADD(day, -{date_range_days}, CURRENT_TIMESTAMP())")
            
            if sentiment_filter:
                if sentiment_filter.lower() == 'positive':
                    filters.append("SENTIMENT_SCORE > 0.3")
                elif sentiment_filter.lower() == 'negative':
                    filters.append("SENTIMENT_SCORE < -0.3")
                elif sentiment_filter.lower() == 'neutral':
                    filters.append("SENTIMENT_SCORE BETWEEN -0.3 AND 0.3")
            
            filter_clause = " AND ".join(filters)
            
            # Enhanced semantic search query
            search_sql = f"""
            WITH query_embedding AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', '{query_text}') as embedding
            ),
            similarity_search AS (
                SELECT 
                    gc.*,
                    VECTOR_COSINE_SIMILARITY(gc.AI_MEMORY_EMBEDDING, qe.embedding) as SIMILARITY_SCORE,
                    -- Enhanced metadata extraction
                    gc.AI_MEMORY_METADATA:call_id::STRING as MEMORY_CALL_ID,
                    gc.AI_MEMORY_METADATA:account_name::STRING as MEMORY_ACCOUNT_NAME,
                    gc.AI_MEMORY_METADATA:deal_stage::STRING as MEMORY_DEAL_STAGE,
                    gc.AI_MEMORY_METADATA:sentiment_score::FLOAT as MEMORY_SENTIMENT_SCORE,
                    gc.AI_MEMORY_METADATA:talk_ratio::FLOAT as MEMORY_TALK_RATIO,
                    gc.AI_MEMORY_METADATA:primary_user::STRING as MEMORY_PRIMARY_USER,
                    gc.AI_MEMORY_METADATA:embedding_generated_at::TIMESTAMP_NTZ as MEMORY_EMBEDDING_TIMESTAMP
                FROM STG_TRANSFORMED.STG_GONG_CALLS gc
                CROSS JOIN query_embedding qe
                WHERE {filter_clause}
                AND VECTOR_COSINE_SIMILARITY(gc.AI_MEMORY_EMBEDDING, qe.embedding) >= {similarity_threshold}
            )
            SELECT 
                CALL_ID,
                CALL_TITLE,
                CALL_DATETIME_UTC,
                CALL_DURATION_SECONDS,
                CALL_DIRECTION,
                PRIMARY_USER_NAME,
                PRIMARY_USER_EMAIL,
                ACCOUNT_NAME,
                CONTACT_NAME,
                DEAL_STAGE,
                DEAL_VALUE,
                SENTIMENT_SCORE,
                CALL_SUMMARY,
                KEY_TOPICS,
                RISK_INDICATORS,
                NEXT_STEPS,
                TALK_RATIO,
                SIMILARITY_SCORE,
                -- AI Memory metadata
                MEMORY_CALL_ID,
                MEMORY_ACCOUNT_NAME,
                MEMORY_DEAL_STAGE,
                MEMORY_SENTIMENT_SCORE,
                MEMORY_TALK_RATIO,
                MEMORY_PRIMARY_USER,
                MEMORY_EMBEDDING_TIMESTAMP,
                AI_MEMORY_UPDATED_AT
            FROM similarity_search
            ORDER BY SIMILARITY_SCORE DESC
            LIMIT {top_k}
            """
            
            results = await self.execute_query(search_sql)
            
            if results.empty:
                return []
            
            # Convert to list of dictionaries with enhanced formatting
            search_results = []
            for _, row in results.iterrows():
                result = {
                    "call_id": row["CALL_ID"],
                    "call_title": row["CALL_TITLE"],
                    "call_datetime": row["CALL_DATETIME_UTC"].isoformat() if pd.notna(row["CALL_DATETIME_UTC"]) else None,
                    "call_duration_seconds": int(row["CALL_DURATION_SECONDS"]) if pd.notna(row["CALL_DURATION_SECONDS"]) else 0,
                    "call_direction": row["CALL_DIRECTION"],
                    "primary_user": {
                        "name": row["PRIMARY_USER_NAME"],
                        "email": row["PRIMARY_USER_EMAIL"]
                    },
                    "account_info": {
                        "account_name": row["ACCOUNT_NAME"],
                        "contact_name": row["CONTACT_NAME"],
                        "deal_stage": row["DEAL_STAGE"],
                        "deal_value": float(row["DEAL_VALUE"]) if pd.notna(row["DEAL_VALUE"]) else None
                    },
                    "ai_insights": {
                        "sentiment_score": float(row["SENTIMENT_SCORE"]) if pd.notna(row["SENTIMENT_SCORE"]) else None,
                        "call_summary": row["CALL_SUMMARY"],
                        "key_topics": row["KEY_TOPICS"],
                        "risk_indicators": row["RISK_INDICATORS"],
                        "next_steps": row["NEXT_STEPS"],
                        "talk_ratio": float(row["TALK_RATIO"]) if pd.notna(row["TALK_RATIO"]) else None
                    },
                    "search_metadata": {
                        "similarity_score": float(row["SIMILARITY_SCORE"]),
                        "ai_memory_updated_at": row["AI_MEMORY_UPDATED_AT"].isoformat() if pd.notna(row["AI_MEMORY_UPDATED_AT"]) else None,
                        "embedding_timestamp": row["MEMORY_EMBEDDING_TIMESTAMP"].isoformat() if pd.notna(row["MEMORY_EMBEDDING_TIMESTAMP"]) else None
                    }
                }
                search_results.append(result)
            
            logger.info(f"Found {len(search_results)} Gong calls matching query: '{query_text}'")
            return search_results
            
        except Exception as e:
            logger.error(f"Error in Gong calls semantic search: {e}")
            return []

    async def search_gong_transcripts_with_ai_memory(
        self,
        query_text: str,
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        speaker_type: Optional[str] = None,
        call_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhanced semantic search across STG_GONG_CALL_TRANSCRIPTS with AI Memory integration
        
        Args:
            query_text: Natural language search query
            top_k: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            speaker_type: Filter by speaker type ('Internal', 'External')
            call_id: Filter by specific call ID
            
        Returns:
            List of matching transcript segments with similarity scores
        """
        try:
            # Build filters
            filters = ["AI_MEMORY_EMBEDDING IS NOT NULL"]
            
            if speaker_type:
                filters.append(f"SPEAKER_TYPE = '{speaker_type}'")
            
            if call_id:
                filters.append(f"CALL_ID = '{call_id}'")
            
            filter_clause = " AND ".join(filters)
            
            # Enhanced transcript search query
            search_sql = f"""
            WITH query_embedding AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', '{query_text}') as embedding
            ),
            similarity_search AS (
                SELECT 
                    gt.*,
                    VECTOR_COSINE_SIMILARITY(gt.AI_MEMORY_EMBEDDING, qe.embedding) as SIMILARITY_SCORE,
                    -- Join with call data for context
                    gc.CALL_TITLE,
                    gc.ACCOUNT_NAME,
                    gc.DEAL_STAGE,
                    gc.CALL_DATETIME_UTC
                FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS gt
                CROSS JOIN query_embedding qe
                LEFT JOIN STG_TRANSFORMED.STG_GONG_CALLS gc ON gt.CALL_ID = gc.CALL_ID
                WHERE {filter_clause}
                AND VECTOR_COSINE_SIMILARITY(gt.AI_MEMORY_EMBEDDING, qe.embedding) >= {similarity_threshold}
            )
            SELECT 
                TRANSCRIPT_ID,
                CALL_ID,
                SPEAKER_NAME,
                SPEAKER_EMAIL,
                SPEAKER_TYPE,
                TRANSCRIPT_TEXT,
                START_TIME_SECONDS,
                END_TIME_SECONDS,
                SEGMENT_DURATION_SECONDS,
                SEGMENT_SENTIMENT,
                SEGMENT_SUMMARY,
                EXTRACTED_ENTITIES,
                KEY_PHRASES,
                SIMILARITY_SCORE,
                -- Call context
                CALL_TITLE,
                ACCOUNT_NAME,
                DEAL_STAGE,
                CALL_DATETIME_UTC,
                AI_MEMORY_UPDATED_AT
            FROM similarity_search
            ORDER BY SIMILARITY_SCORE DESC
            LIMIT {top_k}
            """
            
            results = await self.execute_query(search_sql)
            
            if results.empty:
                return []
            
            # Convert to enhanced result format
            search_results = []
            for _, row in results.iterrows():
                result = {
                    "transcript_id": row["TRANSCRIPT_ID"],
                    "call_id": row["CALL_ID"],
                    "speaker": {
                        "name": row["SPEAKER_NAME"],
                        "email": row["SPEAKER_EMAIL"],
                        "type": row["SPEAKER_TYPE"]
                    },
                    "content": {
                        "transcript_text": row["TRANSCRIPT_TEXT"],
                        "segment_summary": row["SEGMENT_SUMMARY"],
                        "extracted_entities": row["EXTRACTED_ENTITIES"],
                        "key_phrases": row["KEY_PHRASES"]
                    },
                    "timing": {
                        "start_time_seconds": int(row["START_TIME_SECONDS"]) if pd.notna(row["START_TIME_SECONDS"]) else 0,
                        "end_time_seconds": int(row["END_TIME_SECONDS"]) if pd.notna(row["END_TIME_SECONDS"]) else 0,
                        "segment_duration_seconds": int(row["SEGMENT_DURATION_SECONDS"]) if pd.notna(row["SEGMENT_DURATION_SECONDS"]) else 0
                    },
                    "ai_insights": {
                        "segment_sentiment": float(row["SEGMENT_SENTIMENT"]) if pd.notna(row["SEGMENT_SENTIMENT"]) else None,
                        "similarity_score": float(row["SIMILARITY_SCORE"])
                    },
                    "call_context": {
                        "call_title": row["CALL_TITLE"],
                        "account_name": row["ACCOUNT_NAME"],
                        "deal_stage": row["DEAL_STAGE"],
                        "call_datetime": row["CALL_DATETIME_UTC"].isoformat() if pd.notna(row["CALL_DATETIME_UTC"]) else None
                    },
                    "ai_memory_updated_at": row["AI_MEMORY_UPDATED_AT"].isoformat() if pd.notna(row["AI_MEMORY_UPDATED_AT"]) else None
                }
                search_results.append(result)
            
            logger.info(f"Found {len(search_results)} transcript segments matching query: '{query_text}'")
            return search_results
            
        except Exception as e:
            logger.error(f"Error in Gong transcripts semantic search: {e}")
            return []

    async def get_gong_call_analytics(
        self,
        date_range_days: int = 30,
        include_ai_insights: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive Gong call analytics with AI insights
        
        Args:
            date_range_days: Number of days to analyze
            include_ai_insights: Whether to include AI-generated insights
            
        Returns:
            Comprehensive analytics dictionary
        """
        try:
            # Base analytics query
            analytics_sql = f"""
            SELECT 
                COUNT(*) as total_calls,
                COUNT(DISTINCT PRIMARY_USER_EMAIL) as unique_users,
                COUNT(DISTINCT ACCOUNT_NAME) as unique_accounts,
                AVG(CALL_DURATION_SECONDS) as avg_duration_seconds,
                AVG(TALK_RATIO) as avg_talk_ratio,
                AVG(SENTIMENT_SCORE) as avg_sentiment_score,
                
                -- Call direction breakdown
                COUNT(CASE WHEN CALL_DIRECTION = 'Inbound' THEN 1 END) as inbound_calls,
                COUNT(CASE WHEN CALL_DIRECTION = 'Outbound' THEN 1 END) as outbound_calls,
                
                -- Sentiment distribution
                COUNT(CASE WHEN SENTIMENT_SCORE > 0.3 THEN 1 END) as positive_sentiment_calls,
                COUNT(CASE WHEN SENTIMENT_SCORE < -0.3 THEN 1 END) as negative_sentiment_calls,
                COUNT(CASE WHEN SENTIMENT_SCORE BETWEEN -0.3 AND 0.3 THEN 1 END) as neutral_sentiment_calls,
                
                -- Deal stage distribution
                COUNT(CASE WHEN DEAL_STAGE IS NOT NULL THEN 1 END) as calls_with_deals,
                SUM(CASE WHEN DEAL_VALUE IS NOT NULL THEN DEAL_VALUE ELSE 0 END) as total_deal_value,
                
                -- AI Memory integration stats
                COUNT(CASE WHEN AI_MEMORY_EMBEDDING IS NOT NULL THEN 1 END) as calls_with_embeddings,
                COUNT(CASE WHEN CALL_SUMMARY IS NOT NULL THEN 1 END) as calls_with_summaries,
                COUNT(CASE WHEN KEY_TOPICS IS NOT NULL THEN 1 END) as calls_with_topics
                
            FROM STG_TRANSFORMED.STG_GONG_CALLS
            WHERE CALL_DATETIME_UTC >= DATEADD(day, -{date_range_days}, CURRENT_TIMESTAMP())
            """
            
            analytics_result = await self.execute_query(analytics_sql)
            
            if analytics_result.empty:
                return {"error": "No analytics data available"}
            
            analytics_row = analytics_result.iloc[0]
            
            # Build comprehensive analytics response
            analytics = {
                "summary": {
                    "date_range_days": date_range_days,
                    "total_calls": int(analytics_row["TOTAL_CALLS"]),
                    "unique_users": int(analytics_row["UNIQUE_USERS"]),
                    "unique_accounts": int(analytics_row["UNIQUE_ACCOUNTS"]),
                    "avg_duration_minutes": round(analytics_row["AVG_DURATION_SECONDS"] / 60, 1) if pd.notna(analytics_row["AVG_DURATION_SECONDS"]) else 0,
                    "avg_talk_ratio": round(analytics_row["AVG_TALK_RATIO"], 2) if pd.notna(analytics_row["AVG_TALK_RATIO"]) else 0,
                    "avg_sentiment_score": round(analytics_row["AVG_SENTIMENT_SCORE"], 2) if pd.notna(analytics_row["AVG_SENTIMENT_SCORE"]) else 0
                },
                "call_direction": {
                    "inbound": int(analytics_row["INBOUND_CALLS"]),
                    "outbound": int(analytics_row["OUTBOUND_CALLS"])
                },
                "sentiment_distribution": {
                    "positive": int(analytics_row["POSITIVE_SENTIMENT_CALLS"]),
                    "negative": int(analytics_row["NEGATIVE_SENTIMENT_CALLS"]),
                    "neutral": int(analytics_row["NEUTRAL_SENTIMENT_CALLS"])
                },
                "deal_metrics": {
                    "calls_with_deals": int(analytics_row["CALLS_WITH_DEALS"]),
                    "total_deal_value": float(analytics_row["TOTAL_DEAL_VALUE"]) if pd.notna(analytics_row["TOTAL_DEAL_VALUE"]) else 0
                },
                "ai_memory_coverage": {
                    "calls_with_embeddings": int(analytics_row["CALLS_WITH_EMBEDDINGS"]),
                    "calls_with_summaries": int(analytics_row["CALLS_WITH_SUMMARIES"]),
                    "calls_with_topics": int(analytics_row["CALLS_WITH_TOPICS"]),
                    "embedding_coverage_percent": round(
                        (analytics_row["CALLS_WITH_EMBEDDINGS"] / analytics_row["TOTAL_CALLS"] * 100) if analytics_row["TOTAL_CALLS"] > 0 else 0, 1
                    )
                }
            }
            
            # Add AI insights if requested
            if include_ai_insights:
                insights_sql = f"""
                SELECT 
                    -- Top topics analysis
                    FLATTEN(KEY_TOPICS) as topic_data,
                    COUNT(*) as topic_frequency
                FROM STG_TRANSFORMED.STG_GONG_CALLS
                WHERE CALL_DATETIME_UTC >= DATEADD(day, -{date_range_days}, CURRENT_TIMESTAMP())
                AND KEY_TOPICS IS NOT NULL
                GROUP BY topic_data.value
                ORDER BY topic_frequency DESC
                LIMIT 10
                """
                
                try:
                    topics_result = await self.execute_query(insights_sql)
                    
                    if not topics_result.empty:
                        analytics["ai_insights"] = {
                            "top_topics": [
                                {
                                    "topic": row["TOPIC_DATA"],
                                    "frequency": int(row["TOPIC_FREQUENCY"])
                                }
                                for _, row in topics_result.iterrows()
                            ]
                        }
                except Exception as e:
                    logger.warning(f"Could not generate AI insights: {e}")
                    analytics["ai_insights"] = {"error": "AI insights unavailable"}
            
            analytics["generated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Generated Gong call analytics for {date_range_days} days: {analytics['summary']['total_calls']} calls analyzed")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating Gong call analytics: {e}")
            return {"error": str(e)}

    async def log_etl_job_status(self, job_log: Dict[str, Any]) -> bool:
        """
        Log ETL job status to OPS_MONITORING.ETL_JOB_LOGS table
        
        Args:
            job_log: Dictionary containing job status information
            
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            # Insert job log into monitoring table
            insert_sql = f"""
            INSERT INTO OPS_MONITORING.ETL_JOB_LOGS (
                JOB_ID,
                JOB_TYPE,
                STATUS,
                RECORDS_PROCESSED,
                SUCCESS_RATE,
                HEALTH_STATUS,
                CONNECTION_ID,
                SOURCE_TYPE,
                DESTINATION_TYPE,
                ERROR_MESSAGE,
                METADATA
            ) VALUES (
                '{job_log.get("job_id", "")}',
                '{job_log.get("job_type", "")}',
                '{job_log.get("status", "")}',
                {job_log.get("records_processed", 0)},
                {job_log.get("success_rate", 0.0)},
                '{job_log.get("health_status", "")}',
                '{job_log.get("connection_id", "")}',
                '{job_log.get("source_type", "")}',
                '{job_log.get("destination_type", "")}',
                '{job_log.get("error_message", "")}',
                PARSE_JSON('{json.dumps(job_log.get("metadata", {}))}')
            )
            """
            
            await self.execute_query(insert_sql)
            logger.info(f"ETL job status logged: {job_log.get('job_id', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log ETL job status: {e}")
            return False


# Global service instance
cortex_service = SnowflakeCortexService()


async def get_cortex_service() -> SnowflakeCortexService:
    """Get the global Cortex service instance"""
    if not cortex_service.initialized:
        await cortex_service.initialize()
    return cortex_service


# Convenience functions for common AI operations
async def summarize_hubspot_contact_notes(
    contact_id: str, max_length: int = 150
) -> Dict[str, Any]:
    """Summarize all notes for a HubSpot contact using Cortex"""
    service = await get_cortex_service()

    conditions = f"contact_id = '{contact_id}' AND note_text IS NOT NULL"
    summaries = await service.summarize_text_in_snowflake(
        text_column="note_text",
        table_name="HUBSPOT_CONTACT_NOTES",
        conditions=conditions,
        max_length=max_length,
    )

    return {
        "contact_id": contact_id,
        "note_summaries": summaries,
        "total_notes": len(summaries),
        "ai_service": "snowflake_cortex",
    }


async def analyze_gong_call_sentiment(call_id: str) -> Dict[str, Any]:
    """
    Analyze sentiment for a specific Gong call using Snowflake Cortex

    Args:
        call_id: Gong call ID

    Returns:
        Comprehensive sentiment analysis with call context
    """
    service = await get_cortex_service()

    query = f"""
    SELECT 
        gc.CALL_ID,
        gc.CALL_TITLE,
        gc.CALL_DATETIME_UTC,
        gc.PRIMARY_USER_NAME,
        gc.HUBSPOT_DEAL_ID,
        
        -- Overall call sentiment from Cortex
        SNOWFLAKE.CORTEX.SENTIMENT(
            COALESCE(gc.CALL_TITLE, '') || ' ' || 
            COALESCE(gc.CALL_SUMMARY, '') || ' ' ||
            COALESCE(gc.ACCOUNT_NAME, '')
        ) as call_sentiment_score,
        
        -- Transcript sentiment analysis
        AVG(t.SEGMENT_SENTIMENT) as avg_transcript_sentiment,
        COUNT(t.TRANSCRIPT_ID) as transcript_segments,
        
        -- Risk indicators from negative segments
        STRING_AGG(
            CASE WHEN t.SEGMENT_SENTIMENT < 0.2 
            THEN t.TRANSCRIPT_TEXT 
            ELSE NULL END, 
            ' | '
        ) as negative_segments,
        
        -- Positive highlights
        STRING_AGG(
            CASE WHEN t.SEGMENT_SENTIMENT > 0.7 
            THEN t.TRANSCRIPT_TEXT 
            ELSE NULL END, 
            ' | '
        ) as positive_segments
        
    FROM SOPHIA_AI.GONG_DATA.STG_GONG_CALLS gc
    LEFT JOIN SOPHIA_AI.GONG_DATA.STG_GONG_CALL_TRANSCRIPTS t 
        ON gc.CALL_ID = t.CALL_ID
    WHERE gc.CALL_ID = '{call_id}'
    GROUP BY 
        gc.CALL_ID, gc.CALL_TITLE, gc.CALL_DATETIME_UTC, 
        gc.PRIMARY_USER_NAME, gc.HUBSPOT_DEAL_ID,
        gc.CALL_SUMMARY, gc.ACCOUNT_NAME
    """

    try:
        cursor = service.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            return {
                "call_id": result[0],
                "call_title": result[1],
                "call_datetime": result[2],
                "sales_rep": result[3],
                "hubspot_deal_id": result[4],
                "call_sentiment_score": result[5],
                "avg_transcript_sentiment": result[6],
                "transcript_segments": result[7],
                "negative_segments": result[8],
                "positive_segments": result[9],
                "sentiment_category": _classify_sentiment_score(result[5]),
                "coaching_priority": _calculate_coaching_priority(result[5], result[6]),
                "ai_service": "snowflake_cortex",
            }
        else:
            return {
                "error": f"Call {call_id} not found",
                "ai_service": "snowflake_cortex",
            }

    except Exception as e:
        logger.error(f"Error analyzing Gong call sentiment: {e}")
        raise
    finally:
        if cursor:
            cursor.close()


async def summarize_gong_call_with_context(
    call_id: str, max_length: int = 300
) -> Dict[str, Any]:
    """
    Generate comprehensive call summary using Snowflake Cortex with HubSpot context

    Args:
        call_id: Gong call ID
        max_length: Maximum summary length

    Returns:
        AI-generated call summary with business context
    """
    service = await get_cortex_service()

    query = f"""
    WITH call_context AS (
        SELECT 
            gc.CALL_ID,
            gc.CALL_TITLE,
            gc.PRIMARY_USER_NAME,
            gc.CALL_DURATION_SECONDS,
            gc.SENTIMENT_SCORE,
            gc.TALK_RATIO,
            
            -- HubSpot context (if available)
            hd.DEAL_NAME,
            hd.DEAL_STAGE,
            hd.DEAL_AMOUNT,
            hc.COMPANY_NAME,
            
            -- Concatenated transcript for summarization
            STRING_AGG(t.TRANSCRIPT_TEXT, ' ') as full_transcript
            
        FROM SOPHIA_AI.GONG_DATA.STG_GONG_CALLS gc
        LEFT JOIN SOPHIA_AI.GONG_DATA.STG_GONG_CALL_TRANSCRIPTS t 
            ON gc.CALL_ID = t.CALL_ID
        LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.DEALS hd 
            ON gc.HUBSPOT_DEAL_ID = hd.DEAL_ID
        LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.CONTACTS hc 
            ON gc.HUBSPOT_CONTACT_ID = hc.CONTACT_ID
        WHERE gc.CALL_ID = '{call_id}'
        GROUP BY 
            gc.CALL_ID, gc.CALL_TITLE, gc.PRIMARY_USER_NAME,
            gc.CALL_DURATION_SECONDS, gc.SENTIMENT_SCORE, gc.TALK_RATIO,
            hd.DEAL_NAME, hd.DEAL_STAGE, hd.DEAL_AMOUNT, hc.COMPANY_NAME
    )
    SELECT 
        CALL_ID,
        CALL_TITLE,
        PRIMARY_USER_NAME,
        DEAL_NAME,
        DEAL_STAGE,
        DEAL_AMOUNT,
        COMPANY_NAME,
        
        -- Generate comprehensive summary with Cortex
        SNOWFLAKE.CORTEX.SUMMARIZE(
            'Sales Call: ' || CALL_TITLE || 
            CASE WHEN DEAL_NAME IS NOT NULL THEN '. Deal: ' || DEAL_NAME ELSE '' END ||
            CASE WHEN DEAL_STAGE IS NOT NULL THEN '. Stage: ' || DEAL_STAGE ELSE '' END ||
            CASE WHEN COMPANY_NAME IS NOT NULL THEN '. Company: ' || COMPANY_NAME ELSE '' END ||
            CASE WHEN full_transcript IS NOT NULL THEN '. Conversation: ' || LEFT(full_transcript, 8000) ELSE '' END,
            {max_length}
        ) as ai_summary,
        
        SENTIMENT_SCORE,
        TALK_RATIO,
        CALL_DURATION_SECONDS
        
    FROM call_context
    """

    try:
        cursor = service.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            return {
                "call_id": result[0],
                "call_title": result[1],
                "sales_rep": result[2],
                "deal_name": result[3],
                "deal_stage": result[4],
                "deal_amount": result[5],
                "company_name": result[6],
                "ai_summary": result[7],
                "sentiment_score": result[8],
                "talk_ratio": result[9],
                "duration_seconds": result[10],
                "summary_length": len(result[7]) if result[7] else 0,
                "ai_service": "snowflake_cortex",
            }
        else:
            return {
                "error": f"Call {call_id} not found",
                "ai_service": "snowflake_cortex",
            }

    except Exception as e:
        logger.error(f"Error summarizing Gong call: {e}")
        raise
    finally:
        if cursor:
            cursor.close()


async def find_similar_gong_calls(
    query_text: str,
    top_k: int = 5,
    similarity_threshold: float = 0.7,
    date_range_days: int = 90,
) -> List[Dict[str, Any]]:
    """
    Find similar Gong calls using vector similarity search with Snowflake Cortex

    Args:
        query_text: Text to search for (topic, concern, etc.)
        top_k: Number of similar calls to return
        similarity_threshold: Minimum similarity score
        date_range_days: Days back to search

    Returns:
        List of similar calls with similarity scores and context
    """
    service = await get_cortex_service()

    query = f"""
    WITH query_embedding AS (
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', '{query_text}') AS query_vector
    ),
    similar_transcripts AS (
        SELECT 
            t.CALL_ID,
            t.TRANSCRIPT_TEXT,
            t.SPEAKER_NAME,
            t.SEGMENT_SENTIMENT,
            VECTOR_COSINE_SIMILARITY(q.query_vector, t.TRANSCRIPT_EMBEDDING) AS similarity_score
        FROM SOPHIA_AI.GONG_DATA.STG_GONG_CALL_TRANSCRIPTS t
        CROSS JOIN query_embedding q
        JOIN SOPHIA_AI.GONG_DATA.STG_GONG_CALLS gc ON t.CALL_ID = gc.CALL_ID
        WHERE VECTOR_COSINE_SIMILARITY(q.query_vector, t.TRANSCRIPT_EMBEDDING) >= {similarity_threshold}
        AND gc.CALL_DATETIME_UTC >= DATEADD('day', -{date_range_days}, CURRENT_DATE())
        ORDER BY similarity_score DESC
        LIMIT {top_k * 3}  -- Get more results for better call-level aggregation
    )
    SELECT 
        gc.CALL_ID,
        gc.CALL_TITLE,
        gc.PRIMARY_USER_NAME,
        gc.CALL_DATETIME_UTC,
        gc.SENTIMENT_SCORE,
        hd.DEAL_NAME,
        hd.DEAL_STAGE,
        hd.DEAL_AMOUNT,
        hc.COMPANY_NAME,
        
        -- Aggregate similarity and context
        MAX(st.similarity_score) as max_similarity,
        AVG(st.similarity_score) as avg_similarity,
        COUNT(st.CALL_ID) as matching_segments,
        
        -- Best matching transcript segments
        STRING_AGG(
            CASE WHEN st.similarity_score >= {similarity_threshold + 0.1}
            THEN st.TRANSCRIPT_TEXT 
            ELSE NULL END, 
            ' | '
        ) as relevant_segments
        
    FROM similar_transcripts st
    JOIN SOPHIA_AI.GONG_DATA.STG_GONG_CALLS gc ON st.CALL_ID = gc.CALL_ID
    LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.DEALS hd ON gc.HUBSPOT_DEAL_ID = hd.DEAL_ID
    LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.CONTACTS hc ON gc.HUBSPOT_CONTACT_ID = hc.CONTACT_ID
    
    GROUP BY 
        gc.CALL_ID, gc.CALL_TITLE, gc.PRIMARY_USER_NAME, gc.CALL_DATETIME_UTC,
        gc.SENTIMENT_SCORE, hd.DEAL_NAME, hd.DEAL_STAGE, hd.DEAL_AMOUNT, hc.COMPANY_NAME
        
    ORDER BY max_similarity DESC
    LIMIT {top_k}
    """

    try:
        cursor = service.connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        similar_calls = []
        for row in results:
            similar_calls.append(
                {
                    "call_id": row[0],
                    "call_title": row[1],
                    "sales_rep": row[2],
                    "call_datetime": row[3],
                    "sentiment_score": row[4],
                    "deal_name": row[5],
                    "deal_stage": row[6],
                    "deal_amount": row[7],
                    "company_name": row[8],
                    "max_similarity": row[9],
                    "avg_similarity": row[10],
                    "matching_segments": row[11],
                    "relevant_segments": row[12],
                    "ai_service": "snowflake_cortex",
                }
            )

        logger.info(
            f"Found {len(similar_calls)} similar calls for query: {query_text[:50]}..."
        )
        return similar_calls

    except Exception as e:
        logger.error(f"Error finding similar Gong calls: {e}")
        raise
    finally:
        if cursor:
            cursor.close()


async def get_gong_coaching_insights(
    sales_rep: str, date_range_days: int = 30, min_calls: int = 3
) -> Dict[str, Any]:
    """
    Generate coaching insights for a sales rep using Snowflake Cortex analysis

    Args:
        sales_rep: Sales representative name
        date_range_days: Days back to analyze
        min_calls: Minimum calls required for analysis

    Returns:
        Comprehensive coaching insights with AI recommendations
    """
    service = await get_cortex_service()

    query = f"""
    WITH rep_calls AS (
        SELECT 
            gc.CALL_ID,
            gc.CALL_TITLE,
            gc.CALL_DATETIME_UTC,
            gc.SENTIMENT_SCORE,
            gc.TALK_RATIO,
            gc.CALL_DURATION_SECONDS,
            hd.DEAL_STAGE,
            hd.DEAL_AMOUNT,
            
            -- Aggregate transcript sentiment
            AVG(t.SEGMENT_SENTIMENT) as avg_transcript_sentiment,
            
            -- Identify coaching opportunities from transcript
            STRING_AGG(
                CASE WHEN t.SEGMENT_SENTIMENT < 0.3 AND t.SPEAKER_TYPE = 'Internal'
                THEN t.TRANSCRIPT_TEXT 
                ELSE NULL END, 
                ' | '
            ) as improvement_areas
            
        FROM SOPHIA_AI.GONG_DATA.STG_GONG_CALLS gc
        LEFT JOIN SOPHIA_AI.GONG_DATA.STG_GONG_CALL_TRANSCRIPTS t ON gc.CALL_ID = t.CALL_ID
        LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.DEALS hd ON gc.HUBSPOT_DEAL_ID = hd.DEAL_ID
        
        WHERE gc.PRIMARY_USER_NAME = '{sales_rep}'
        AND gc.CALL_DATETIME_UTC >= DATEADD('day', -{date_range_days}, CURRENT_DATE())
        
        GROUP BY 
            gc.CALL_ID, gc.CALL_TITLE, gc.CALL_DATETIME_UTC,
            gc.SENTIMENT_SCORE, gc.TALK_RATIO, gc.CALL_DURATION_SECONDS,
            hd.DEAL_STAGE, hd.DEAL_AMOUNT
    ),
    coaching_analysis AS (
        SELECT 
            COUNT(*) as total_calls,
            AVG(SENTIMENT_SCORE) as avg_sentiment,
            AVG(TALK_RATIO) as avg_talk_ratio,
            AVG(CALL_DURATION_SECONDS) as avg_duration,
            AVG(avg_transcript_sentiment) as avg_transcript_sentiment,
            
            -- Performance categories
            COUNT(CASE WHEN SENTIMENT_SCORE > 0.6 THEN 1 END) as positive_calls,
            COUNT(CASE WHEN SENTIMENT_SCORE < 0.3 THEN 1 END) as negative_calls,
            COUNT(CASE WHEN TALK_RATIO > 0.7 THEN 1 END) as high_talk_ratio_calls,
            COUNT(CASE WHEN TALK_RATIO < 0.4 THEN 1 END) as low_talk_ratio_calls,
            
            -- Deal outcomes
            COUNT(CASE WHEN DEAL_STAGE IN ('Closed Won', 'Closed - Won') THEN 1 END) as deals_won,
            SUM(CASE WHEN DEAL_STAGE IN ('Closed Won', 'Closed - Won') THEN DEAL_AMOUNT ELSE 0 END) as revenue_won,
            
            -- Improvement areas
            STRING_AGG(improvement_areas, ' ### ') as all_improvement_areas
            
        FROM rep_calls
    )
    SELECT 
        '{sales_rep}' as sales_rep,
        total_calls,
        avg_sentiment,
        avg_talk_ratio,
        avg_duration,
        positive_calls,
        negative_calls,
        high_talk_ratio_calls,
        low_talk_ratio_calls,
        deals_won,
        revenue_won,
        
        -- Generate AI coaching recommendations using Cortex
        SNOWFLAKE.CORTEX.COMPLETE(
            'mistral-7b',
            'Based on this sales performance data, provide 3 specific coaching recommendations: ' ||
            'Average sentiment: ' || ROUND(avg_sentiment, 2) || 
            ', Talk ratio: ' || ROUND(avg_talk_ratio, 2) ||
            ', Positive calls: ' || positive_calls || '/' || total_calls ||
            ', Negative calls: ' || negative_calls || '/' || total_calls ||
            CASE WHEN all_improvement_areas IS NOT NULL 
            THEN '. Common issues: ' || LEFT(all_improvement_areas, 1000)
            ELSE '' END,
            {{'max_tokens': 300}}
        ) as ai_coaching_recommendations
        
    FROM coaching_analysis
    WHERE total_calls >= {min_calls}
    """

    try:
        cursor = service.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            return {
                "sales_rep": result[0],
                "analysis_period_days": date_range_days,
                "total_calls": result[1],
                "avg_sentiment": result[2],
                "avg_talk_ratio": result[3],
                "avg_duration_seconds": result[4],
                "positive_calls": result[5],
                "negative_calls": result[6],
                "high_talk_ratio_calls": result[7],
                "low_talk_ratio_calls": result[8],
                "deals_won": result[9],
                "revenue_won": result[10],
                "ai_coaching_recommendations": result[11],
                "performance_score": _calculate_performance_score(
                    result[2], result[3], result[5], result[1]
                ),
                "coaching_priority": _determine_coaching_priority(
                    result[2], result[6], result[7]
                ),
                "ai_service": "snowflake_cortex",
            }
        else:
            return {
                "error": f"Insufficient data for {sales_rep} (minimum {min_calls} calls required)",
                "ai_service": "snowflake_cortex",
            }

    except Exception as e:
        logger.error(f"Error generating coaching insights: {e}")
        raise
    finally:
        if cursor:
            cursor.close()


# Helper functions for Gong analysis
def _classify_sentiment_score(score: float) -> str:
    """Classify sentiment score into categories"""
    if score is None:
        return "Unknown"
    elif score > 0.7:
        return "Very Positive"
    elif score > 0.3:
        return "Positive"
    elif score > -0.3:
        return "Neutral"
    elif score > -0.7:
        return "Negative"
    else:
        return "Very Negative"


def _calculate_coaching_priority(
    call_sentiment: float, transcript_sentiment: float
) -> str:
    """Calculate coaching priority based on sentiment scores"""
    if call_sentiment is None or transcript_sentiment is None:
        return "Low"

    avg_sentiment = (call_sentiment + transcript_sentiment) / 2

    if avg_sentiment < 0.2:
        return "High"
    elif avg_sentiment < 0.4:
        return "Medium"
    else:
        return "Low"


def _calculate_performance_score(
    avg_sentiment: float, avg_talk_ratio: float, positive_calls: int, total_calls: int
) -> float:
    """Calculate overall performance score (0-100)"""
    if not all([avg_sentiment, avg_talk_ratio, total_calls]):
        return 0.0

    # Sentiment component (40% weight)
    sentiment_score = max(0, min(100, (avg_sentiment + 1) * 50))

    # Talk ratio component (30% weight) - optimal range 0.4-0.6
    talk_ratio_score = max(0, min(100, 100 - abs(avg_talk_ratio - 0.5) * 200))

    # Positive call ratio component (30% weight)
    positive_ratio = positive_calls / total_calls
    positive_score = positive_ratio * 100

    return round(
        sentiment_score * 0.4 + talk_ratio_score * 0.3 + positive_score * 0.3, 1
    )


def _determine_coaching_priority(
    avg_sentiment: float, negative_calls: int, high_talk_ratio_calls: int
) -> str:
    """Determine coaching priority level"""
    if avg_sentiment < 0.3 or negative_calls > 2 or high_talk_ratio_calls > 3:
        return "High"
    elif avg_sentiment < 0.5 or negative_calls > 0 or high_talk_ratio_calls > 1:
        return "Medium"
    else:
        return "Low"
