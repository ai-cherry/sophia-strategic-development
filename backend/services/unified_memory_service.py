"""
Unified Memory Service for Sophia AI
THE ONLY MEMORY SERVICE - ALL MEMORY OPERATIONS MUST GO THROUGH HERE
Date: July 9, 2025

This service implements the 6-tier memory architecture:
- L0: GPU Cache (Lambda Labs) - Not managed here
- L1: Redis (Ephemeral cache)
- L2: Mem0 (Agent conversational memory)
- L3: Snowflake Cortex (Vector knowledge base) - PRIMARY VECTOR STORE
- L4: Snowflake Tables (Structured data warehouse)
- L5: Snowflake Cortex AI (Intelligence layer)

CRITICAL: This replaces ALL usage of Pinecone, Weaviate, ChromaDB, Qdrant
"""

import json
from typing import Any

import redis
import snowflake.connector
from snowflake.connector import DictCursor

from backend.core.auto_esc_config import get_config_value
from backend.core.date_time_manager import date_manager
from shared.utils.errors import ConnectionError, DataValidationError
from shared.utils.monitoring import get_logger, log_execution_time

# Try to import Mem0, but make it optional for now
try:
    from mem0 import Memory

    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    Memory = None

logger = get_logger(__name__)


class UnifiedMemoryService:
    """
    The single, authoritative memory service for Sophia AI.

    This service manages all memory tiers except L0 (GPU cache).
    All vector operations go through Snowflake Cortex ONLY.
    """

    def __init__(self):
        """Initialize all memory tier connections"""
        self.initialize_date_awareness()
        self.initialize_redis()  # L1
        self.initialize_mem0()  # L2
        self.initialize_snowflake()  # L3, L4, L5

        # Configuration
        self.vector_dimension = 768  # Standard for CORTEX.EMBED_TEXT_768
        self.default_limit = 10
        self.cache_ttl = 3600  # 1 hour default TTL for Redis cache

        logger.info(f"UnifiedMemoryService initialized - Date: {self.current_date}")

    def initialize_date_awareness(self):
        """Initialize with proper date awareness"""
        self.current_date = date_manager.now()
        logger.info(f"🗓️ UnifiedMemoryService aware of date: {self.current_date}")

    def initialize_redis(self):
        """Initialize L1: Redis for ephemeral cache"""
        try:
            redis_host = get_config_value("redis_host", "localhost") or "localhost"
            redis_port = int(get_config_value("redis_port", "6379") or "6379")
            redis_password = get_config_value("redis_password")

            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Test connection
            self.redis_client.ping()
            logger.info("✅ L1 Redis initialized successfully")

        except Exception as e:
            logger.warning(f"❌ L1 Redis initialization failed: {e}")
            self.redis_client = None

    def initialize_mem0(self):
        """Initialize L2: Mem0 for agent memory"""
        if not MEM0_AVAILABLE or Memory is None:
            logger.warning("⚠️ L2 Mem0 not available - install with: pip install mem0ai")
            self.mem0_client = None
            return

        try:
            # Mem0 configuration
            config = {
                "vector_store": {
                    "provider": "qdrant",  # Mem0 uses its own vector store
                    "config": {
                        "host": get_config_value("mem0_qdrant_host", "localhost")
                        or "localhost",
                        "port": int(
                            get_config_value("mem0_qdrant_port", "6333") or "6333"
                        ),
                    },
                }
            }

            self.mem0_client = Memory(config=config)
            logger.info("✅ L2 Mem0 initialized successfully")

        except Exception as e:
            logger.warning(f"❌ L2 Mem0 initialization failed: {e}")
            self.mem0_client = None

    def initialize_snowflake(self):
        """Initialize L3/L4/L5: Snowflake for vectors, data, and AI"""
        try:
            self.snowflake_conn = snowflake.connector.connect(
                account=get_config_value("snowflake_account"),
                user=get_config_value("snowflake_user"),
                password=get_config_value("snowflake_password"),
                warehouse=get_config_value(
                    "snowflake_warehouse", "SOPHIA_AI_COMPUTE_WH"
                ),
                database="AI_MEMORY",
                schema="VECTORS",
                session_parameters={
                    "QUERY_TAG": "UnifiedMemoryService",
                    "TIMESTAMP_TYPE_MAPPING": "TIMESTAMP_NTZ",
                },
            )

            # Test connection and create schema if needed
            cursor = self.snowflake_conn.cursor()
            try:
                cursor.execute("SELECT CURRENT_VERSION()")
                result = cursor.fetchone()
                version = result[0] if result else "unknown"
                logger.info(f"✅ L3/L4/L5 Snowflake initialized (version: {version})")

                # Ensure our tables exist
                self._ensure_snowflake_schema()

            finally:
                cursor.close()

        except Exception as e:
            logger.exception(f"❌ Snowflake initialization failed: {e}")
            raise ConnectionError(f"Failed to connect to Snowflake: {e}")

    def _ensure_snowflake_schema(self):
        """Ensure required Snowflake tables exist"""
        cursor = self.snowflake_conn.cursor()
        try:
            # Create database and schema if they don't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS AI_MEMORY")
            cursor.execute("CREATE SCHEMA IF NOT EXISTS AI_MEMORY.VECTORS")
            cursor.execute("USE SCHEMA AI_MEMORY.VECTORS")

            # Create the main knowledge base table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS KNOWLEDGE_BASE (
                    id VARCHAR(36) DEFAULT UUID_STRING(),
                    content TEXT NOT NULL,
                    embedding VECTOR(FLOAT, 768),
                    metadata VARIANT,
                    source VARCHAR(500),
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PRIMARY KEY (id)
                )
            """
            )

            # Create conversational memory table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS CONVERSATIONAL_MEMORY (
                    id VARCHAR(36) DEFAULT UUID_STRING(),
                    user_id VARCHAR(100),
                    session_id VARCHAR(100),
                    content TEXT NOT NULL,
                    embedding VECTOR(FLOAT, 768),
                    metadata VARIANT,
                    memory_type VARCHAR(50),
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PRIMARY KEY (id)
                )
            """
            )

            self.snowflake_conn.commit()
            logger.info("✅ Snowflake schema verified/created")

        except Exception as e:
            logger.exception(f"Failed to create Snowflake schema: {e}")
            self.snowflake_conn.rollback()
        finally:
            cursor.close()

    # ==================== L1: Redis Cache Operations ====================

    def cache_get(self, key: str) -> Any | None:
        """Get value from L1 Redis cache"""
        if not self.redis_client:
            return None

        try:
            value = self.redis_client.get(f"sophia:cache:{key}")
            if value:
                return json.loads(str(value))
            return None
        except Exception as e:
            logger.warning(f"Redis cache get error: {e}")
            return None

    def cache_set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in L1 Redis cache"""
        if not self.redis_client:
            return False

        try:
            ttl = ttl or self.cache_ttl
            self.redis_client.setex(f"sophia:cache:{key}", ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning(f"Redis cache set error: {e}")
            return False

    def cache_delete(self, key: str) -> bool:
        """Delete value from L1 Redis cache"""
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(f"sophia:cache:{key}")
            return True
        except Exception as e:
            logger.warning(f"Redis cache delete error: {e}")
            return False

    # ==================== L2: Mem0 Agent Memory ====================

    def remember_conversation(
        self, user_id: str, content: str, metadata: dict | None = None
    ) -> bool:
        """Store conversational memory in L2 Mem0"""
        if not self.mem0_client:
            logger.warning("Mem0 not available - storing in Snowflake instead")
            return self._store_conversation_in_snowflake(user_id, content, metadata)

        try:
            # Add timestamp to metadata
            if metadata is None:
                metadata = {}
            metadata["timestamp"] = self.current_date.isoformat()
            metadata["date_context"] = "July 9, 2025"

            # Store in Mem0
            self.mem0_client.add(content, user_id=user_id, metadata=metadata)

            logger.info(f"✅ Stored conversation memory for user {user_id}")
            return True

        except Exception as e:
            logger.exception(f"Failed to store in Mem0: {e}")
            # Fallback to Snowflake
            return self._store_conversation_in_snowflake(user_id, content, metadata)

    def recall_conversations(
        self, user_id: str, query: str | None = None, limit: int = 10
    ) -> list[dict]:
        """Recall conversational memories from L2 Mem0"""
        if not self.mem0_client:
            logger.warning("Mem0 not available - searching in Snowflake instead")
            return self._search_conversations_in_snowflake(user_id, query, limit)

        try:
            if query:
                memories = self.mem0_client.search(query, user_id=user_id, limit=limit)
            else:
                memories = self.mem0_client.get_all(user_id=user_id, limit=limit)

            return [
                {
                    "content": mem.get("memory", mem.get("text", "")),
                    "metadata": mem.get("metadata", {}),
                    "created_at": mem.get("created_at"),
                }
                for mem in memories
            ]

        except Exception as e:
            logger.exception(f"Failed to recall from Mem0: {e}")
            return self._search_conversations_in_snowflake(user_id, query, limit)

    # ==================== L3: Snowflake Vector Search ====================

    @log_execution_time
    def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        metadata_filter: dict | None = None,
        threshold: float = 0.7,
    ) -> list[dict]:
        """
        Search the knowledge base using Snowflake Cortex vector search.
        This is the PRIMARY method for all semantic search operations.

        REPLACES: Pinecone search, Weaviate search, ChromaDB search
        """
        # Check cache first
        cache_key = f"search:{query}:{limit}:{json.dumps(metadata_filter or {})}"
        cached_result = self.cache_get(cache_key)
        if cached_result:
            logger.info("✅ Returning cached search results")
            return cached_result

        cursor = self.snowflake_conn.cursor(DictCursor)
        try:
            # Build the query with Cortex functions
            sql = """
                WITH query_embedding AS (
                    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', ?) as embedding
                )
                SELECT
                    k.id,
                    k.content,
                    k.metadata,
                    k.source,
                    k.created_at,
                    VECTOR_COSINE_SIMILARITY(k.embedding, q.embedding) as similarity
                FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE k, query_embedding q
                WHERE VECTOR_COSINE_SIMILARITY(k.embedding, q.embedding) > ?
            """

            # Add metadata filtering if provided
            if metadata_filter:
                for key, value in metadata_filter.items():
                    sql += f" AND k.metadata:'{key}' = '{value}'"

            sql += " ORDER BY similarity DESC LIMIT ?"

            # Execute search
            cursor.execute(sql, (query, threshold, limit))
            results = cursor.fetchall()

            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append(
                    {
                        "id": row["ID"],
                        "content": row["CONTENT"],
                        "metadata": (
                            json.loads(row["METADATA"]) if row["METADATA"] else {}
                        ),
                        "source": row["SOURCE"],
                        "similarity": float(row["SIMILARITY"]),
                        "created_at": (
                            row["CREATED_AT"].isoformat() if row["CREATED_AT"] else None
                        ),
                    }
                )

            # Cache the results
            self.cache_set(cache_key, formatted_results, ttl=600)  # 10 minute cache

            logger.info(
                f"✅ Found {len(formatted_results)} results for query: {query[:50]}..."
            )
            return formatted_results

        except Exception as e:
            logger.exception(f"Knowledge search failed: {e}")
            return []
        finally:
            cursor.close()

    def add_knowledge(
        self,
        content: str,
        source: str,
        metadata: dict | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> list[str]:
        """
        Add new knowledge to the vector database.
        Automatically chunks, embeds, and stores in Snowflake.

        REPLACES: Pinecone index, Weaviate collection add
        """
        if not content or not content.strip():
            raise DataValidationError("Content cannot be empty")

        # Chunk the content if it's too large
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)

        cursor = self.snowflake_conn.cursor()
        inserted_ids = []

        try:
            for chunk in chunks:
                # Prepare metadata
                chunk_metadata = metadata or {}
                chunk_metadata.update(
                    {
                        "chunk_size": len(chunk),
                        "source": source,
                        "indexed_date": self.current_date.isoformat(),
                        "actual_date": "July 9, 2025",
                    }
                )

                # Insert with embedding generation
                sql = """
                    INSERT INTO AI_MEMORY.VECTORS.KNOWLEDGE_BASE
                    (content, embedding, metadata, source)
                    SELECT
                        ?,
                        SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', ?),
                        PARSE_JSON(?),
                        ?
                """

                cursor.execute(
                    sql,
                    (chunk, chunk, json.dumps(chunk_metadata), source),  # Text to embed
                )

                # Get the inserted ID
                cursor.execute("SELECT LAST_QUERY_ID()")
                query_id = cursor.fetchone()[0]
                inserted_ids.append(query_id)

            self.snowflake_conn.commit()
            logger.info(f"✅ Added {len(chunks)} knowledge chunks from {source}")

            # Clear relevant caches
            self._clear_search_cache()

            return inserted_ids

        except Exception as e:
            self.snowflake_conn.rollback()
            logger.exception(f"Failed to add knowledge: {e}")
            raise
        finally:
            cursor.close()

    # ==================== L4: Snowflake Data Warehouse ====================

    def query_warehouse(self, sql: str, params: tuple | None = None) -> list[dict]:
        """
        Execute SQL query against the Snowflake data warehouse.
        For structured data queries (not vector search).
        """
        cursor = self.snowflake_conn.cursor(DictCursor)
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            results = cursor.fetchall()
            return [dict(row) for row in results]

        except Exception as e:
            logger.exception(f"Warehouse query failed: {e}")
            raise
        finally:
            cursor.close()

    # ==================== L5: Snowflake Cortex AI ====================

    def generate_sql_from_natural_language(
        self, query: str, schema_context: str
    ) -> str:
        """
        Use Snowflake Cortex to generate SQL from natural language.
        L5 Intelligence layer operation.
        """
        cursor = self.snowflake_conn.cursor()
        try:
            prompt = f"""
            Given the following database schema:
            {schema_context}

            Generate a SQL query for this request: {query}

            Return only the SQL query without explanation.
            """

            sql = """
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'mistral-large',
                    ?
                ) as generated_sql
            """

            cursor.execute(sql, (prompt,))
            result = cursor.fetchone()

            if result and result[0]:
                generated_sql = json.loads(result[0])
                return generated_sql.get("choices", [{}])[0].get("text", "").strip()

            return ""

        except Exception as e:
            logger.exception(f"SQL generation failed: {e}")
            return ""
        finally:
            cursor.close()

    def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """
        Analyze sentiment using Snowflake Cortex.
        L5 Intelligence layer operation.
        """
        cursor = self.snowflake_conn.cursor()
        try:
            sql = """
                SELECT
                    SNOWFLAKE.CORTEX.SENTIMENT(?) as sentiment_score,
                    SNOWFLAKE.CORTEX.CLASSIFY_TEXT(?, ['positive', 'negative', 'neutral']) as classification
            """

            cursor.execute(sql, (text, text))
            result = cursor.fetchone()

            if result:
                return {
                    "sentiment_score": float(result[0]) if result[0] else 0.0,
                    "classification": result[1] if result[1] else "neutral",
                }

            return {"sentiment_score": 0.0, "classification": "neutral"}

        except Exception as e:
            logger.exception(f"Sentiment analysis failed: {e}")
            return {"sentiment_score": 0.0, "classification": "neutral"}
        finally:
            cursor.close()

    # ==================== Helper Methods ====================

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(". ")
                if last_period > chunk_size * 0.8:  # Only if we're past 80% of chunk
                    end = start + last_period + 1
                    chunk = text[start:end]

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def _store_conversation_in_snowflake(
        self, user_id: str, content: str, metadata: dict | None = None
    ) -> bool:
        """Fallback to store conversation in Snowflake when Mem0 is not available"""
        cursor = self.snowflake_conn.cursor()
        try:
            metadata = metadata or {}
            metadata["stored_via"] = "snowflake_fallback"

            sql = """
                INSERT INTO AI_MEMORY.VECTORS.CONVERSATIONAL_MEMORY
                (user_id, content, embedding, metadata, memory_type)
                SELECT
                    ?,
                    ?,
                    SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', ?),
                    PARSE_JSON(?),
                    'conversation'
            """

            cursor.execute(sql, (user_id, content, content, json.dumps(metadata)))
            self.snowflake_conn.commit()
            return True

        except Exception as e:
            logger.exception(f"Failed to store conversation in Snowflake: {e}")
            self.snowflake_conn.rollback()
            return False
        finally:
            cursor.close()

    def _search_conversations_in_snowflake(
        self, user_id: str, query: str | None, limit: int
    ) -> list[dict]:
        """Fallback to search conversations in Snowflake when Mem0 is not available"""
        cursor = self.snowflake_conn.cursor(DictCursor)
        try:
            if query:
                # Semantic search
                sql = """
                    WITH query_embedding AS (
                        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', ?) as embedding
                    )
                    SELECT
                        c.content,
                        c.metadata,
                        c.created_at,
                        VECTOR_COSINE_SIMILARITY(c.embedding, q.embedding) as relevance
                    FROM AI_MEMORY.VECTORS.CONVERSATIONAL_MEMORY c, query_embedding q
                    WHERE c.user_id = ?
                    ORDER BY relevance DESC
                    LIMIT ?
                """
                cursor.execute(sql, (query, user_id, limit))
            else:
                # Just get recent conversations
                sql = """
                    SELECT content, metadata, created_at
                    FROM AI_MEMORY.VECTORS.CONVERSATIONAL_MEMORY
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                cursor.execute(sql, (user_id, limit))

            results = cursor.fetchall()
            return [
                {
                    "content": row["CONTENT"],
                    "metadata": json.loads(row["METADATA"]) if row["METADATA"] else {},
                    "created_at": (
                        row["CREATED_AT"].isoformat() if row["CREATED_AT"] else None
                    ),
                }
                for row in results
            ]

        except Exception as e:
            logger.exception(f"Failed to search conversations in Snowflake: {e}")
            return []
        finally:
            cursor.close()

    def _clear_search_cache(self):
        """Clear all search-related caches"""
        if self.redis_client:
            try:
                pattern = "sophia:cache:search:*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
                logger.info("✅ Cleared search cache")
            except Exception as e:
                logger.warning(f"Failed to clear cache: {e}")

    # ==================== Health Check ====================

    def health_check(self) -> dict[str, Any]:
        """Check health of all memory tiers"""
        health = {
            "status": "healthy",
            "date_awareness": self.current_date.isoformat(),
            "actual_date": "July 9, 2025",
            "tiers": {},
        }

        # L1: Redis
        try:
            if self.redis_client:
                self.redis_client.ping()
                health["tiers"]["L1_redis"] = "healthy"
            else:
                health["tiers"]["L1_redis"] = "not_configured"
        except:
            health["tiers"]["L1_redis"] = "unhealthy"
            health["status"] = "degraded"

        # L2: Mem0
        health["tiers"]["L2_mem0"] = "healthy" if self.mem0_client else "not_configured"

        # L3/L4/L5: Snowflake
        try:
            cursor = self.snowflake_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            health["tiers"]["L3_L4_L5_snowflake"] = "healthy"
        except:
            health["tiers"]["L3_L4_L5_snowflake"] = "unhealthy"
            health["status"] = "unhealthy"

        return health


# Singleton instance
_memory_service_instance = None


def get_unified_memory_service() -> UnifiedMemoryService:
    """Get singleton instance of UnifiedMemoryService"""
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = UnifiedMemoryService()
    return _memory_service_instance
