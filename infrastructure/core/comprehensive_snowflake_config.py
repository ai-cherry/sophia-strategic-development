#!/usr/bin/env python3
from core.config_manager import get_config_value

"""
Comprehensive Snowflake Configuration for Sophia AI
Maps to the complete schema breakdown with enhanced support for all features
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any
from uuid import uuid4

# Import snowflake connector to fix undefined name error
try:
    import snowflake.connector
except ImportError:
    snowflake = None

logger = logging.getLogger(__name__)


class SchemaType(str, Enum):
    UNIVERSAL_CHAT = "UNIVERSAL_CHAT"
    AI_MEMORY = "AI_MEMORY"
    APOLLO_IO = "APOLLO_IO"
    PROJECT_MANAGEMENT = "PROJECT_MANAGEMENT"
    GONG_INTEGRATION = "GONG_INTEGRATION"
    HUBSPOT_INTEGRATION = "HUBSPOT_INTEGRATION"


class TableType(str, Enum):
    # Unified Chat Tables
    KNOWLEDGE_CATEGORIES = "KNOWLEDGE_CATEGORIES"
    KNOWLEDGE_SOURCES = "KNOWLEDGE_SOURCES"
    KNOWLEDGE_BASE_ENTRIES = "KNOWLEDGE_BASE_ENTRIES"
    KNOWLEDGE_EMBEDDINGS = "KNOWLEDGE_EMBEDDINGS"
    KNOWLEDGE_USAGE_ANALYTICS = "KNOWLEDGE_USAGE_ANALYTICS"
    CONVERSATION_SESSIONS = "CONVERSATION_SESSIONS"
    CONVERSATION_MESSAGES = "CONVERSATION_MESSAGES"
    CONVERSATION_CONTEXT = "CONVERSATION_CONTEXT"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    TEACHING_SESSIONS = "TEACHING_SESSIONS"
    KNOWLEDGE_WEIGHTS = "KNOWLEDGE_WEIGHTS"
    INTERNET_SEARCH_SESSIONS = "INTERNET_SEARCH_SESSIONS"
    DYNAMIC_SCRAPING_SESSIONS = "DYNAMIC_SCRAPING_SESSIONS"
    SYSTEM_ANALYTICS = "SYSTEM_ANALYTICS"

    # AI Memory Tables
    BUSINESS_MEMORY_CATEGORIES = "BUSINESS_MEMORY_CATEGORIES"
    MEMORY_ENTRIES = "MEMORY_ENTRIES"
    MEMORY_EMBEDDINGS = "MEMORY_EMBEDDINGS"
    MEMORY_RELATIONSHIPS = "MEMORY_RELATIONSHIPS"
    MEMORY_ACCESS_PATTERNS = "MEMORY_ACCESS_PATTERNS"

    # Project Management Tables
    PROJECTS = "PROJECTS"
    ISSUES = "ISSUES"
    TEAM_MEMBERS = "TEAM_MEMBERS"
    PROJECT_HEALTH_METRICS = "PROJECT_HEALTH_METRICS"

    # Integration Tables
    APOLLO_RAW_CONTACTS = "RAW_CONTACTS"
    APOLLO_RAW_COMPANIES = "RAW_COMPANIES"
    APOLLO_CONTACTS_ENRICHED = "CONTACTS_ENRICHED"
    APOLLO_COMPANIES_ENRICHED = "COMPANIES_ENRICHED"
    GONG_CALLS = "CALLS"
    GONG_CALL_PARTICIPANTS = "CALL_PARTICIPANTS"
    GONG_CALL_ANALYTICS = "CALL_ANALYTICS"
    HUBSPOT_CONTACTS = "CONTACTS"
    HUBSPOT_COMPANIES = "COMPANIES"
    HUBSPOT_DEALS = "DEALS"


@dataclass
class SnowflakeConfig:
    """Comprehensive Snowflake configuration"""

    account: str = "ZNB04675.us-east-1"
    user: str = "SCOOBYJAVA15"
    password: str = get_config_value("snowflake_password")
    role: str = "ACCOUNTADMIN"
    database: str = "SOPHIA_AI"
    warehouse: str = "SOPHIA_AI_WH"
    default_schema: str = "UNIVERSAL_CHAT"


class ComprehensiveSnowflakeManager:
    """Enhanced Snowflake manager supporting all schemas and advanced features"""

    def __init__(self, config: SnowflakeConfig):
        self.config = config
        self.connection = None

        # Schema-to-table mappings
        self.schema_tables = {
            SchemaType.UNIVERSAL_CHAT: {
                TableType.KNOWLEDGE_CATEGORIES: "KNOWLEDGE_CATEGORIES",
                TableType.KNOWLEDGE_SOURCES: "KNOWLEDGE_SOURCES",
                TableType.KNOWLEDGE_BASE_ENTRIES: "KNOWLEDGE_BASE_ENTRIES",
                TableType.KNOWLEDGE_EMBEDDINGS: "KNOWLEDGE_EMBEDDINGS",
                TableType.KNOWLEDGE_USAGE_ANALYTICS: "KNOWLEDGE_USAGE_ANALYTICS",
                TableType.CONVERSATION_SESSIONS: "CONVERSATION_SESSIONS",
                TableType.CONVERSATION_MESSAGES: "CONVERSATION_MESSAGES",
                TableType.CONVERSATION_CONTEXT: "CONVERSATION_CONTEXT",
                TableType.USER_MANAGEMENT: "USER_MANAGEMENT",
                TableType.TEACHING_SESSIONS: "TEACHING_SESSIONS",
                TableType.KNOWLEDGE_WEIGHTS: "KNOWLEDGE_WEIGHTS",
                TableType.INTERNET_SEARCH_SESSIONS: "INTERNET_SEARCH_SESSIONS",
                TableType.DYNAMIC_SCRAPING_SESSIONS: "DYNAMIC_SCRAPING_SESSIONS",
                TableType.SYSTEM_ANALYTICS: "SYSTEM_ANALYTICS",
            },
            SchemaType.AI_MEMORY: {
                TableType.BUSINESS_MEMORY_CATEGORIES: "BUSINESS_MEMORY_CATEGORIES",
                TableType.MEMORY_ENTRIES: "MEMORY_ENTRIES",
                TableType.MEMORY_EMBEDDINGS: "MEMORY_EMBEDDINGS",
                TableType.MEMORY_RELATIONSHIPS: "MEMORY_RELATIONSHIPS",
                TableType.MEMORY_ACCESS_PATTERNS: "MEMORY_ACCESS_PATTERNS",
            },
            SchemaType.PROJECT_MANAGEMENT: {
                TableType.PROJECTS: "PROJECTS",
                TableType.ISSUES: "ISSUES",
                TableType.TEAM_MEMBERS: "TEAM_MEMBERS",
                TableType.PROJECT_HEALTH_METRICS: "PROJECT_HEALTH_METRICS",
            },
            SchemaType.APOLLO_IO: {
                TableType.APOLLO_RAW_CONTACTS: "RAW_CONTACTS",
                TableType.APOLLO_RAW_COMPANIES: "RAW_COMPANIES",
                TableType.APOLLO_CONTACTS_ENRICHED: "CONTACTS_ENRICHED",
                TableType.APOLLO_COMPANIES_ENRICHED: "COMPANIES_ENRICHED",
            },
            SchemaType.GONG_INTEGRATION: {
                TableType.GONG_CALLS: "CALLS",
                TableType.GONG_CALL_PARTICIPANTS: "CALL_PARTICIPANTS",
                TableType.GONG_CALL_ANALYTICS: "CALL_ANALYTICS",
            },
            SchemaType.HUBSPOT_INTEGRATION: {
                TableType.HUBSPOT_CONTACTS: "CONTACTS",
                TableType.HUBSPOT_COMPANIES: "COMPANIES",
                TableType.HUBSPOT_DEALS: "DEALS",
            },
        }

        # Enhanced table configurations for our services
        self.table_configs = {
            # Knowledge Base Tables (Enhanced for large file processing)
            TableType.KNOWLEDGE_BASE_ENTRIES: {
                "supports_chunking": True,
                "chunk_fields": ["CHUNK_INDEX", "TOTAL_CHUNKS"],
                "file_fields": ["FILE_PATH", "FILE_SIZE_BYTES"],
                "importance_fields": ["IMPORTANCE_SCORE", "IS_FOUNDATIONAL"],
                "metadata_fields": ["METADATA", "TAGS"],
            },
            # Embedding Tables (Enhanced for context windows)
            TableType.KNOWLEDGE_EMBEDDINGS: {
                "embedding_model_field": "EMBEDDING_MODEL",
                "vector_field": "EMBEDDING_VECTOR",
                "text_field": "CHUNK_TEXT",
                "supports_chunking": True,
            },
            # Memory Tables (Enhanced for cross-document context)
            TableType.MEMORY_ENTRIES: {
                "relationship_support": True,
                "importance_scoring": True,
                "expiration_support": True,
                "categorization": True,
            },
            # Analytics Tables (Enhanced for monitoring)
            TableType.SYSTEM_ANALYTICS: {
                "real_time_metrics": True,
                "aggregation_support": True,
                "dimension_support": True,
            },
        }

    async def connect(self):
        """Connect to Snowflake with comprehensive error handling"""
        try:
            self.connection = # TODO: Replace with repository injection
    # repository.get_connection(
                account=self.config.account,
                user=self.config.user,
                password=self.config.password,
                role=self.config.role,
                database=self.config.database,
                warehouse=self.config.warehouse,
                schema=self.config.default_schema,
            )

            logger.info("✅ Connected to comprehensive Snowflake deployment")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {e}")
            raise

    def get_table_name(self, schema: SchemaType, table: TableType) -> str:
        """Get fully qualified table name"""
        table_name = self.schema_tables.get(schema, {}).get(table)
        if not table_name:
            raise ValueError(f"Table {table} not found in schema {schema}")

        return f"{self.config.database}.{schema.value}.{table_name}"

    def get_table_config(self, table: TableType) -> dict[str, Any]:
        """Get configuration for specific table"""
        return self.table_configs.get(table, {})

    async def execute_query(
        self,
        query: str,
        params: tuple | None = None,
        schema: SchemaType | None = None,
    ) -> list[dict[str, Any]]:
        """Execute query with schema context"""
        try:
            cursor = self.connection.cursor(snowflake.connector.DictCursor)

            # Switch schema if specified
            if schema:
                # TODO: Replace with repository method
    # repository.execute_query("USE SCHEMA " + self._validate_schema(schema.value))

            # TODO: Replace with repository method
    # repository.execute_query(query, params or ())
            results = cursor.fetchall()
            cursor.close()

            return results

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    # Enhanced Knowledge Base Operations
    async def insert_knowledge_entry(
        self,
        entry_id: str,
        title: str,
        content: str,
        category_id: str,
        source_id: str = "src_manual",
        importance_score: float = 1.0,
        is_foundational: bool = False,
        tags: list[str] = None,
        metadata: dict[str, Any] = None,
        file_path: str = None,
        file_size_bytes: int = None,
        chunk_index: int = 0,
        total_chunks: int = 1,
        created_by: str = "system",
    ) -> bool:
        """Insert knowledge entry with enhanced support for chunking"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.UNIVERSAL_CHAT, TableType.KNOWLEDGE_BASE_ENTRIES)}
        (ENTRY_ID, TITLE, CONTENT, CATEGORY_ID, SOURCE_ID, IMPORTANCE_SCORE,
         IS_FOUNDATIONAL, TAGS, METADATA, FILE_PATH, FILE_SIZE_BYTES,
         CHUNK_INDEX, TOTAL_CHUNKS, CREATED_BY, CREATED_AT, UPDATED_AT)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """

        params = (
            entry_id,
            title,
            content,
            category_id,
            source_id,
            importance_score,
            is_foundational,
            json.dumps(tags or []),
            json.dumps(metadata or {}),
            file_path,
            file_size_bytes,
            chunk_index,
            total_chunks,
            created_by,
        )

        await self.execute_query(query, params, SchemaType.UNIVERSAL_CHAT)
        return True

    async def insert_knowledge_embedding(
        self,
        embedding_id: str,
        entry_id: str,
        embedding_vector: list[float],
        chunk_text: str,
        chunk_index: int = 0,
        embedding_model: str = "snowflake-arctic-embed-m",
    ) -> bool:
        """Insert knowledge embedding for semantic search"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.UNIVERSAL_CHAT, TableType.KNOWLEDGE_EMBEDDINGS)}
        (EMBEDDING_ID, ENTRY_ID, EMBEDDING_MODEL, EMBEDDING_VECTOR, CHUNK_TEXT, CHUNK_INDEX, CREATED_AT)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP())
        """

        params = (
            embedding_id,
            entry_id,
            embedding_model,
            json.dumps(embedding_vector),
            chunk_text,
            chunk_index,
        )

        await self.execute_query(query, params, SchemaType.UNIVERSAL_CHAT)
        return True

    # Enhanced Memory Operations
    async def insert_memory_entry(
        self,
        memory_id: str,
        category_id: str,
        memory_type: str,
        title: str,
        content: str,
        importance_score: float = 1.0,
        confidence_level: float = 1.0,
        source_system: str = "sophia_ai",
        source_id: str = None,
        related_entities: list[str] = None,
        tags: list[str] = None,
        metadata: dict[str, Any] = None,
        expires_at: str = None,
    ) -> bool:
        """Insert memory entry for enhanced context management"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.AI_MEMORY, TableType.MEMORY_ENTRIES)}
        (MEMORY_ID, CATEGORY_ID, MEMORY_TYPE, TITLE, CONTENT, IMPORTANCE_SCORE,
         CONFIDENCE_LEVEL, SOURCE_SYSTEM, SOURCE_ID, RELATED_ENTITIES, TAGS,
         METADATA, EXPIRES_AT, CREATED_AT, UPDATED_AT)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """

        params = (
            memory_id,
            category_id,
            memory_type,
            title,
            content,
            importance_score,
            confidence_level,
            source_system,
            source_id,
            json.dumps(related_entities or []),
            json.dumps(tags or []),
            json.dumps(metadata or {}),
            expires_at,
        )

        await self.execute_query(query, params, SchemaType.AI_MEMORY)
        return True

    # Enhanced Search Operations
    async def hybrid_search_knowledge(
        self,
        query: str,
        limit: int = 10,
        category_filter: str = None,
        importance_threshold: float = 0.5,
        include_embeddings: bool = True,
    ) -> list[dict[str, Any]]:
        """Perform hybrid search across knowledge base"""

        base_query = f"""
        SELECT
            k.ENTRY_ID,
            k.TITLE,
            k.CONTENT,
            k.CATEGORY_ID,
            c.CATEGORY_NAME,
            k.IMPORTANCE_SCORE,
            k.IS_FOUNDATIONAL,
            k.CHUNK_INDEX,
            k.TOTAL_CHUNKS,
            k.CREATED_AT
        FROM {self.get_table_name(SchemaType.UNIVERSAL_CHAT, TableType.KNOWLEDGE_BASE_ENTRIES)} k
        JOIN {self.get_table_name(SchemaType.UNIVERSAL_CHAT, TableType.KNOWLEDGE_CATEGORIES)} c
          ON k.CATEGORY_ID = c.CATEGORY_ID
        WHERE k.IMPORTANCE_SCORE >= ?
        """

        params = [importance_threshold]

        # Add text search
        base_query += (
            " AND (UPPER(k.TITLE) LIKE UPPER(?) OR UPPER(k.CONTENT) LIKE UPPER(?))"
        )
        search_term = f"%{query}%"
        params.extend([search_term, search_term])

        # Add category filter
        if category_filter:
            base_query += " AND k.CATEGORY_ID = ?"
            params.append(category_filter)

        base_query += " ORDER BY k.IMPORTANCE_SCORE DESC, k.CREATED_AT DESC LIMIT ?"
        params.append(limit)

        results = await self.execute_query(
            base_query, tuple(params), SchemaType.UNIVERSAL_CHAT
        )

        # Add embedding similarity if requested
        if include_embeddings and results:
            # This would typically involve vector similarity calculations
            # For now, we'll add a placeholder similarity score
            for result in results:
                result["similarity_score"] = 0.8  # Placeholder

        return results

    # Analytics Operations
    async def log_system_metric(
        self,
        metric_type: str,
        metric_name: str,
        metric_value: float,
        metric_unit: str = None,
        dimensions: dict[str, Any] = None,
        aggregation_period: str = "real_time",
    ) -> bool:
        """Log system metrics for monitoring"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.UNIVERSAL_CHAT, TableType.SYSTEM_ANALYTICS)}
        (ANALYTICS_ID, METRIC_TYPE, METRIC_NAME, METRIC_VALUE, METRIC_UNIT,
         DIMENSIONS, AGGREGATION_PERIOD, TIMESTAMP)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP())
        """

        params = (
            str(uuid4()),
            metric_type,
            metric_name,
            metric_value,
            metric_unit,
            json.dumps(dimensions or {}),
            aggregation_period,
        )

        await self.execute_query(query, params, SchemaType.UNIVERSAL_CHAT)
        return True

    # Enhanced Conversation Operations
    async def create_conversation_session(
        self,
        session_id: str,
        user_id: str,
        session_name: str = None,
        session_type: str = "chat",
        context_summary: str = None,
    ) -> bool:
        """Create enhanced conversation session"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.UNIVERSAL_CHAT, TableType.CONVERSATION_SESSIONS)}
        (SESSION_ID, USER_ID, SESSION_NAME, SESSION_TYPE, CONTEXT_SUMMARY,
         IS_ACTIVE, TOTAL_MESSAGES, STARTED_AT, LAST_ACTIVITY_AT)
        VALUES (?, ?, ?, ?, ?, TRUE, 0, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """

        params = (session_id, user_id, session_name, session_type, context_summary)

        await self.execute_query(query, params, SchemaType.UNIVERSAL_CHAT)
        return True

    async def save_conversation_message(
        self,
        message_id: str,
        session_id: str,
        user_id: str,
        message_type: str,
        message_content: str,
        knowledge_entries_used: list[str] = None,
        processing_time_ms: int = None,
        model_used: str = None,
        confidence_score: float = None,
        metadata: dict[str, Any] = None,
    ) -> bool:
        """Save conversation message with enhanced metadata"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.UNIVERSAL_CHAT, TableType.CONVERSATION_MESSAGES)}
        (MESSAGE_ID, SESSION_ID, USER_ID, MESSAGE_TYPE, MESSAGE_CONTENT,
         KNOWLEDGE_ENTRIES_USED, PROCESSING_TIME_MS, MODEL_USED, CONFIDENCE_SCORE,
         METADATA, CREATED_AT)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP())
        """

        params = (
            message_id,
            session_id,
            user_id,
            message_type,
            message_content,
            json.dumps(knowledge_entries_used or []),
            processing_time_ms,
            model_used,
            confidence_score,
            json.dumps(metadata or {}),
        )

        await self.execute_query(query, params, SchemaType.UNIVERSAL_CHAT)

        # Update session last activity
        update_query = f"""
        UPDATE {self.get_table_name(SchemaType.UNIVERSAL_CHAT, TableType.CONVERSATION_SESSIONS)}
        SET LAST_ACTIVITY_AT = CURRENT_TIMESTAMP(),
            TOTAL_MESSAGES = TOTAL_MESSAGES + 1
        WHERE SESSION_ID = ?
        """

        await self.execute_query(update_query, (session_id,), SchemaType.UNIVERSAL_CHAT)
        return True

    # Utility Methods
    async def get_schema_health(self) -> dict[str, Any]:
        """Get comprehensive schema health information"""

        health_info = {}

        for schema in SchemaType:
            try:
                # Get table counts
                query = f"""
                SELECT TABLE_NAME, ROW_COUNT
                FROM {self.config.database}.INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{schema.value}'
                AND TABLE_TYPE = 'BASE TABLE'
                """

                results = await self.execute_query(query)
                health_info[schema.value] = {
                    "status": "healthy",
                    "tables": {row["TABLE_NAME"]: row["ROW_COUNT"] for row in results},
                }

            except Exception as e:
                health_info[schema.value] = {"status": "error", "error": str(e)}

        return health_info

    async def optimize_performance(self) -> dict[str, Any]:
        """Run performance optimization queries"""

        optimizations = []

        # Analyze query performance
        perf_query = """
        SELECT QUERY_TEXT, EXECUTION_TIME, ROWS_PRODUCED
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE START_TIME >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
        AND DATABASE_NAME = ?
        ORDER BY EXECUTION_TIME DESC
        LIMIT 10
        """

        try:
            slow_queries = await self.execute_query(perf_query, (self.config.database,))
            optimizations.append(
                {
                    "type": "slow_queries",
                    "count": len(slow_queries),
                    "details": slow_queries[:5],  # Top 5 slowest
                }
            )
        except Exception as e:
            logger.warning(f"Could not analyze query performance: {e}")

        return {"optimizations": optimizations}

    async def disconnect(self):
        """Clean disconnect from Snowflake"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Snowflake")


# Global instance for easy access
snowflake_manager = ComprehensiveSnowflakeManager(SnowflakeConfig())
