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

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

import snowflake.connector
import pandas as pd
import numpy as np

from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)


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
        self.connection = None
        self.database = config.get("snowflake_database", "SOPHIA_AI")
        self.schema = config.get("snowflake_schema", "AI_PROCESSING")
        self.warehouse = config.get("snowflake_warehouse", "COMPUTE_WH")
        self.initialized = False
        
        # Vector storage tables
        self.vector_tables = {
            "hubspot_embeddings": "HUBSPOT_CONTACT_EMBEDDINGS",
            "gong_embeddings": "GONG_CALL_EMBEDDINGS", 
            "document_embeddings": "DOCUMENT_EMBEDDINGS",
            "memory_embeddings": "AI_MEMORY_EMBEDDINGS"
        }
    
    async def initialize(self) -> None:
        """Initialize Snowflake connection for Cortex AI processing"""
        if self.initialized:
            return
            
        try:
            self.connection = snowflake.connector.connect(
                user=config.get("snowflake_user"),
                password=config.get("snowflake_password"),
                account=config.get("snowflake_account"),
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
                role=config.get("snowflake_role", "ACCOUNTADMIN")
            )
            
            # Ensure vector tables exist
            await self._create_vector_tables()
            
            self.initialized = True
            logger.info("✅ Snowflake Cortex service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake Cortex service: {e}")
            raise
    
    async def summarize_text_in_snowflake(
        self,
        text_column: str,
        table_name: str,
        conditions: Optional[str] = None,
        max_length: int = 200
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
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            summaries = []
            for row in results:
                record = dict(zip(columns, row))
                summaries.append(record)
            
            logger.info(f"Generated {len(summaries)} text summaries using Cortex")
            return summaries
            
        except Exception as e:
            logger.error(f"Error generating summaries with Cortex: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    async def analyze_sentiment_in_snowflake(
        self,
        text_column: str,
        table_name: str,
        conditions: Optional[str] = None
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
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            sentiment_analysis = []
            for row in results:
                record = dict(zip(columns, row))
                sentiment_analysis.append(record)
            
            logger.info(f"Analyzed sentiment for {len(sentiment_analysis)} records using Cortex")
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment with Cortex: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    async def generate_embedding_in_snowflake(
        self,
        text_column: str,
        table_name: str,
        conditions: Optional[str] = None,
        model: str = "e5-base-v2",
        store_embeddings: bool = True
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
        model: str = "e5-base-v2"
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
                    source_id=row[4]
                )
                results.append(result)
            
            logger.info(f"Found {len(results)} similar results for query: {query_text[:50]}...")
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
        context: Optional[str] = None
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
        conditions: Optional[str] = None
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
    
    async def _store_embeddings(self, embeddings: List[Dict[str, Any]], source_table: str):
        """Store embeddings in dedicated vector table"""
        
        vector_table = self.vector_tables.get("document_embeddings", "DOCUMENT_EMBEDDINGS")
        
        # Prepare insert data
        insert_data = []
        for embedding in embeddings:
            insert_data.append((
                embedding['id'],
                embedding['text'],
                embedding['embedding_vector'],
                embedding['embedding_model'],
                None,  # metadata
                source_table,
                embedding['id'],
            ))
        
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


# Global service instance
cortex_service = SnowflakeCortexService()


async def get_cortex_service() -> SnowflakeCortexService:
    """Get the global Cortex service instance"""
    if not cortex_service.initialized:
        await cortex_service.initialize()
    return cortex_service


# Convenience functions for common AI operations
async def summarize_hubspot_contact_notes(contact_id: str, max_length: int = 150) -> Dict[str, Any]:
    """Summarize all notes for a HubSpot contact using Cortex"""
    service = await get_cortex_service()
    
    conditions = f"contact_id = '{contact_id}' AND note_text IS NOT NULL"
    summaries = await service.summarize_text_in_snowflake(
        text_column="note_text",
        table_name="HUBSPOT_CONTACT_NOTES",
        conditions=conditions,
        max_length=max_length
    )
    
    return {
        "contact_id": contact_id,
        "note_summaries": summaries,
        "total_notes": len(summaries),
        "ai_service": "snowflake_cortex"
    }


async def analyze_gong_call_sentiment(call_id: str) -> Dict[str, Any]:
    """Analyze sentiment of a Gong call transcript using Cortex"""
    service = await get_cortex_service()
    
    conditions = f"call_id = '{call_id}'"
    sentiment_results = await service.analyze_sentiment_in_snowflake(
        text_column="transcript_text",
        table_name="GONG_CALL_TRANSCRIPTS",
        conditions=conditions
    )
    
    return {
        "call_id": call_id,
        "sentiment_analysis": sentiment_results,
        "ai_service": "snowflake_cortex"
    }


async def find_similar_customer_interactions(query_text: str, top_k: int = 5) -> List[VectorSearchResult]:
    """Find similar customer interactions using vector search"""
    service = await get_cortex_service()
    
    return await service.vector_search_in_snowflake(
        query_text=query_text,
        vector_table="AI_MEMORY_EMBEDDINGS",
        top_k=top_k,
        similarity_threshold=0.6
    ) 