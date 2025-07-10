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

from backend.core.unified_config import UnifiedConfig
from backend.services.logging_service import logger
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

    def __init__(self, require_snowflake: bool = False):
        """
        Initialize the Unified Memory Service with all tiers.

        Args:
            require_snowflake: If True, raise error if Snowflake unavailable.
                             If False (default), run in degraded mode without Snowflake.
        """
        # Initialize instance variables
        self.require_snowflake = require_snowflake
        self.degraded_mode = False
        self.snowflake_conn = None
        self.redis_client = None
        self.mem0_client = None
        self.cache_ttl = 3600  # 1 hour default TTL

        self.initialize_date_awareness()
        self.initialize_redis()  # L1
        self.initialize_mem0()  # L2

        # Initialize Snowflake but don't fail if unavailable
        try:
            self.initialize_snowflake()  # L3, L4, L5
        except Exception as e:
            if require_snowflake:
                raise
            else:
                logger.warning(f"Snowflake unavailable, running in degraded mode: {e}")
                self.snowflake_conn = None
                self.degraded_mode = True

        # Configuration
        self.vector_dimension = 768  # Standard for CORTEX.EMBED_TEXT_768
        self.default_limit = 10

        logger.info(f"UnifiedMemoryService initialized - Date: {self.current_date}")

    def initialize_date_awareness(self):
        """Initialize date awareness for the service"""
        from backend.core.date_time_manager import date_manager

        self.current_date = date_manager.now()
        logger.info(f"🗓️ UnifiedMemoryService aware of date: {self.current_date}")

    def initialize_redis(self) -> None:
        """Initialize L1 - Redis for ephemeral cache"""
        try:
            redis_config = UnifiedConfig.get_redis_config()

            self.redis_client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                password=redis_config.get("password"),
                db=redis_config.get("db", 0),
                decode_responses=True,
            )

            # Test connection
            self.redis_client.ping()
            logger.info({"event": "✅ L1 Redis initialized successfully"})

        except Exception as e:
            logger.warning({"event": f"⚠️ L1 Redis not available: {e}"})
            self.redis_client = None

    def initialize_mem0(self) -> None:
        """Initialize L2 - Mem0 for agent conversational memory"""
        if not MEM0_AVAILABLE:
            logger.warning(
                {"event": "⚠️ L2 Mem0 not available - install with: pip install mem0ai"}
            )
            return

        try:
            # Mem0 configuration
            config = {
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-ada-002",
                        "api_key": UnifiedConfig.get("openai_api_key"),
                    },
                },
                "vector_store": {
                    "provider": "qdrant",  # Internal to Mem0, not our concern
                    "config": {
                        "collection_name": "sophia_ai_memory",
                        "embedding_model_dims": self.vector_dimension,
                    },
                },
            }

            self.mem0_client = Memory(config)
            logger.info({"event": "✅ L2 Mem0 initialized successfully"})

        except Exception as e:
            logger.warning({"event": f"⚠️ L2 Mem0 initialization failed: {e}"})
            self.mem0_client = None

    def initialize_snowflake(self) -> None:
        """Initialize L3, L4, L5 - Snowflake connection"""
        try:
            # Get Snowflake configuration using UnifiedConfig
            snowflake_config = UnifiedConfig.get_snowflake_config()

            # PAT token takes precedence if available
            pat_token = UnifiedConfig.get("snowflake_pat")
            if pat_token:
                logger.info("Using Snowflake PAT token for authentication")
                snowflake_config["password"] = pat_token

            # Log connection attempt (without exposing password)
            logger.info(
                f"Connecting to Snowflake account: {snowflake_config.get('account', 'unknown')}"
            )
            logger.info(f"Using user: {snowflake_config.get('user', 'unknown')}")

            # Ensure required fields are present
            if not snowflake_config.get("user"):
                raise ValueError("Snowflake user is required but not configured")

            if not snowflake_config.get("password"):
                raise ValueError(
                    "Snowflake password/PAT is required but not configured"
                )

            # Connect to Snowflake
            self.snowflake_conn = snowflake.connector.connect(
                account=snowflake_config["account"],
                user=snowflake_config["user"],
                password=snowflake_config["password"],
                role=snowflake_config.get("role", "ACCOUNTADMIN"),
                warehouse=snowflake_config.get("warehouse", "SOPHIA_AI_COMPUTE_WH"),
                database=snowflake_config.get("database", "AI_MEMORY"),
                schema=snowflake_config.get("schema", "VECTORS"),
            )

            # Test connection
            cursor = self.snowflake_conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()
            cursor.close()

            logger.info(
                {
                    "event": "✅ L3/L4/L5 Snowflake initialized successfully",
                    "version": version[0] if version else "unknown",
                }
            )
            self.degraded_mode = False

        except Exception as e:
            logger.error(f"❌ Snowflake initialization failed: {e}")
            raise ConnectionError(f"Failed to connect to Snowflake: {e}")

    @log_execution_time
    async def add_knowledge(
        self,
        content: str,
        source: str,
        metadata: dict[str, Any] | None = None,
        user_id: str = "system",
    ) -> str:
        """
        Add knowledge to L3 Snowflake Cortex vectors.

        This is the PRIMARY method for storing vectorized knowledge.
        """
        if self.degraded_mode:
            logger.warning(
                "Running in degraded mode - knowledge not persisted to Snowflake"
            )
            # Could still cache in Redis temporarily
            return "degraded_mode_no_id"

        metadata = metadata or {}
        metadata["source"] = source
        metadata["user_id"] = user_id
        metadata["timestamp"] = self.current_date.isoformat()

        try:
            cursor = self.snowflake_conn.cursor(DictCursor)

            # Generate embedding using Snowflake Cortex
            embedding_sql = """
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s) as embedding
            """
            cursor.execute(embedding_sql, (content,))
            result = cursor.fetchone()

            if not result:
                raise DataValidationError("Failed to generate embedding")

            # Store in Snowflake with vector
            insert_sql = """
            INSERT INTO AI_MEMORY.VECTORS.KNOWLEDGE_BASE
            (content, embedding, source, metadata, created_at)
            VALUES (%s, %s::VECTOR(FLOAT, 768), %s, PARSE_JSON(%s), CURRENT_TIMESTAMP())
            """

            cursor.execute(
                insert_sql,
                (content, str(result["embedding"]), source, json.dumps(metadata)),
            )

            # Get the inserted ID
            cursor.execute("SELECT LAST_QUERY_ID()")
            query_id = cursor.fetchone()[0]

            cursor.close()
            self.snowflake_conn.commit()

            logger.info(f"✅ Knowledge added to Snowflake Cortex: {query_id}")

            # Also cache in Redis for fast access
            if self.redis_client:
                cache_key = f"knowledge:{query_id}"
                self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps({"content": content, "metadata": metadata}),
                )

            return query_id

        except Exception as e:
            logger.error(f"Failed to add knowledge: {e}")
            if self.snowflake_conn:
                self.snowflake_conn.rollback()
            raise

    @log_execution_time
    async def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        metadata_filter: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search knowledge using Snowflake Cortex vector similarity.

        This is the PRIMARY vector search method.
        """
        if self.degraded_mode:
            logger.warning("Running in degraded mode - returning empty results")
            return []

        try:
            cursor = self.snowflake_conn.cursor(DictCursor)

            # Build metadata filter if provided
            filter_conditions = []
            params = [query, limit]

            if metadata_filter:
                for key, value in metadata_filter.items():
                    filter_conditions.append(f"metadata:{key} = %s")
                    params.append(value)

            if user_id:
                filter_conditions.append("metadata:user_id = %s")
                params.append(user_id)

            where_clause = ""
            if filter_conditions:
                where_clause = "WHERE " + " AND ".join(filter_conditions)

            # Vector similarity search using Snowflake Cortex
            search_sql = f"""
            WITH query_embedding AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s) as embedding
            )
            SELECT
                kb.id,
                kb.content,
                kb.source,
                kb.metadata,
                kb.created_at,
                VECTOR_COSINE_SIMILARITY(kb.embedding, qe.embedding) as similarity
            FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE kb
            CROSS JOIN query_embedding qe
            {where_clause}
            ORDER BY similarity DESC
            LIMIT %s
            """

            cursor.execute(search_sql, params)
            results = cursor.fetchall()
            cursor.close()

            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append(
                    {
                        "id": row["ID"],
                        "content": row["CONTENT"],
                        "source": row["SOURCE"],
                        "metadata": (
                            json.loads(row["METADATA"]) if row["METADATA"] else {}
                        ),
                        "similarity": float(row["SIMILARITY"]),
                        "created_at": (
                            row["CREATED_AT"].isoformat() if row["CREATED_AT"] else None
                        ),
                    }
                )

            logger.info(
                f"Found {len(formatted_results)} results for query: {query[:50]}..."
            )
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}")
            raise

    async def add_conversation_memory(
        self,
        user_id: str,
        messages: list[dict[str, str]],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add conversation to L2 Mem0 for agent memory.

        This is for conversational context, not knowledge vectors.
        """
        if not self.mem0_client:
            logger.warning("Mem0 not available, conversation not stored")
            return

        try:
            # Store conversation in Mem0
            for message in messages:
                self.mem0_client.add(
                    message["content"],
                    user_id=user_id,
                    metadata={
                        "role": message["role"],
                        "timestamp": self.current_date.isoformat(),
                        **(metadata or {}),
                    },
                )

            logger.info(f"Stored {len(messages)} messages for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            # Don't raise - this is not critical

    async def get_conversation_context(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get conversation context from L2 Mem0.
        """
        if not self.mem0_client:
            return []

        try:
            memories = self.mem0_client.get_all(user_id=user_id, limit=limit)
            return [
                {
                    "content": mem["text"],
                    "metadata": mem.get("metadata", {}),
                    "created_at": mem.get("created_at"),
                }
                for mem in memories
            ]

        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return []

    async def execute_snowflake_query(
        self,
        query: str,
        params: tuple | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a query on L4 Snowflake tables.

        This is for structured data queries, not vector search.
        """
        if self.degraded_mode:
            logger.warning("Running in degraded mode - cannot execute queries")
            return []

        try:
            cursor = self.snowflake_conn.cursor(DictCursor)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()

            return results

        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    async def analyze_with_cortex_ai(
        self,
        text: str,
        operation: str = "SUMMARIZE",
        options: dict[str, Any] | None = None,
    ) -> str:
        """
        Use L5 Snowflake Cortex AI for intelligent operations.

        Operations: SUMMARIZE, SENTIMENT, TRANSLATE, COMPLETE
        """
        if self.degraded_mode:
            logger.warning("Running in degraded mode - cannot use Cortex AI")
            return f"[Degraded mode: {operation} unavailable]"

        try:
            cursor = self.snowflake_conn.cursor()

            # Build Cortex AI query based on operation
            if operation == "SUMMARIZE":
                sql = "SELECT SNOWFLAKE.CORTEX.SUMMARIZE(%s) as result"
                params = (text,)
            elif operation == "SENTIMENT":
                sql = "SELECT SNOWFLAKE.CORTEX.SENTIMENT(%s) as result"
                params = (text,)
            elif operation == "TRANSLATE":
                target_lang = options.get("target_language", "es")
                sql = f"SELECT SNOWFLAKE.CORTEX.TRANSLATE(%s, 'en', '{target_lang}') as result"
                params = (text,)
            elif operation == "COMPLETE":
                model = options.get("model", "mistral-7b")
                sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', %s) as result"
                params = (text,)
            else:
                raise ValueError(f"Unknown operation: {operation}")

            cursor.execute(sql, params)
            result = cursor.fetchone()
            cursor.close()

            return result[0] if result else ""

        except Exception as e:
            logger.error(f"Failed to analyze with Cortex AI: {e}")
            raise

    def close(self):
        """Clean up connections"""
        if self.snowflake_conn:
            self.snowflake_conn.close()
        if self.redis_client:
            self.redis_client.close()


# Singleton instance
_memory_service_instance = None


def get_unified_memory_service(require_snowflake: bool = False) -> UnifiedMemoryService:
    """
    Get the singleton UnifiedMemoryService instance.

    Args:
        require_snowflake: If True, raise error if Snowflake is unavailable

    Returns:
        The unified memory service instance
    """
    global _memory_service_instance

    if _memory_service_instance is None:
        _memory_service_instance = UnifiedMemoryService(
            require_snowflake=require_snowflake
        )

    return _memory_service_instance
