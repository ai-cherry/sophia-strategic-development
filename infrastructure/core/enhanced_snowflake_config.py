#!/usr/bin/env python3
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import snowflake.connector

from core.config_manager import get_config_value

"""
Enhanced Snowflake Configuration for Comprehensive Schema Integration
Supports all 6 schemas: UNIVERSAL_CHAT, AI_MEMORY, APOLLO_IO, PROJECT_MANAGEMENT, GONG_INTEGRATION, HUBSPOT_INTEGRATION
"""

logger = logging.getLogger(__name__)


class SchemaType(str, Enum):
    UNIVERSAL_CHAT = "UNIVERSAL_CHAT"
    AI_MEMORY = "AI_MEMORY"
    APOLLO_IO = "APOLLO_IO"
    PROJECT_MANAGEMENT = "PROJECT_MANAGEMENT"
    GONG_INTEGRATION = "GONG_INTEGRATION"
    HUBSPOT_INTEGRATION = "HUBSPOT_INTEGRATION"


@dataclass
class EnhancedSnowflakeConfig:
    """Enhanced Snowflake configuration supporting all schemas"""

    # Production credentials from schema breakdown
    account: str = "ZNB04675.us-east-1"
    user: str = "SCOOBYJAVA15"
    password: str = get_config_value("snowflake_password")
    role: str = "ACCOUNTADMIN"
    database: str = "SOPHIA_AI"
    warehouse: str = "SOPHIA_AI_WH"
    default_schema: str = "UNIVERSAL_CHAT"


class EnhancedSnowflakeManager:
    """Enhanced Snowflake manager with comprehensive schema support"""

    def __init__(self, config: EnhancedSnowflakeConfig | None = None):
        self.config = config or EnhancedSnowflakeConfig()
        self.connection = None

        # Schema-specific table mappings for enhanced operations
        self.schema_tables = {
            SchemaType.UNIVERSAL_CHAT: {
                "knowledge_categories": "KNOWLEDGE_CATEGORIES",
                "knowledge_sources": "KNOWLEDGE_SOURCES",
                "knowledge_base_entries": "KNOWLEDGE_BASE_ENTRIES",
                "knowledge_embeddings": "KNOWLEDGE_EMBEDDINGS",
                "knowledge_usage_analytics": "KNOWLEDGE_USAGE_ANALYTICS",
                "conversation_sessions": "CONVERSATION_SESSIONS",
                "conversation_messages": "CONVERSATION_MESSAGES",
                "conversation_context": "CONVERSATION_CONTEXT",
                "user_management": "USER_MANAGEMENT",
                "teaching_sessions": "TEACHING_SESSIONS",
                "knowledge_weights": "KNOWLEDGE_WEIGHTS",
                "internet_search_sessions": "INTERNET_SEARCH_SESSIONS",
                "dynamic_scraping_sessions": "DYNAMIC_SCRAPING_SESSIONS",
                "system_analytics": "SYSTEM_ANALYTICS",
            },
            SchemaType.AI_MEMORY: {
                "business_memory_categories": "BUSINESS_MEMORY_CATEGORIES",
                "memory_entries": "MEMORY_ENTRIES",
                "memory_embeddings": "MEMORY_EMBEDDINGS",
                "memory_relationships": "MEMORY_RELATIONSHIPS",
                "memory_access_patterns": "MEMORY_ACCESS_PATTERNS",
            },
            SchemaType.PROJECT_MANAGEMENT: {
                "projects": "PROJECTS",
                "issues": "ISSUES",
                "team_members": "TEAM_MEMBERS",
                "project_health_metrics": "PROJECT_HEALTH_METRICS",
            },
            SchemaType.APOLLO_IO: {
                "raw_contacts": "RAW_CONTACTS",
                "raw_companies": "RAW_COMPANIES",
                "contacts_enriched": "CONTACTS_ENRICHED",
                "companies_enriched": "COMPANIES_ENRICHED",
                "data_quality_metrics": "DATA_QUALITY_METRICS",
            },
            SchemaType.GONG_INTEGRATION: {
                "calls": "CALLS",
                "call_participants": "CALL_PARTICIPANTS",
                "call_analytics": "CALL_ANALYTICS",
            },
            SchemaType.HUBSPOT_INTEGRATION: {
                "contacts": "CONTACTS",
                "companies": "COMPANIES",
                "deals": "DEALS",
            },
        }

    async def connect(self):
        """Connect to Snowflake with comprehensive error handling"""
        try:
            self.connection = snowflake.connector.connect(
                account=self.config.account,
                user=self.config.user,
                password=self.config.password,
                role=self.config.role,
                database=self.config.database,
                warehouse=self.config.warehouse,
                schema=self.config.default_schema,
            )

            logger.info("✅ Connected to enhanced Snowflake deployment with 6 schemas")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {e}")
            raise

    def get_table_name(self, schema: SchemaType, table_key: str) -> str:
        """Get fully qualified table name"""
        table_name = self.schema_tables.get(schema, {}).get(table_key)
        if not table_name:
            raise ValueError(f"Table {table_key} not found in schema {schema}")

        return f"{self.config.database}.{schema.value}.{table_name}"

    async def execute_query(
        self,
        query: str,
        params: tuple | None = None,
        schema: SchemaType | None = None,
    ) -> list[dict[str, Any]]:
        """Execute query with schema context"""
        try:
            if not self.connection:
                raise ConnectionError(
                    "Not connected to Snowflake. Call connect() first."
                )

            cursor = self.connection.cursor(snowflake.connector.DictCursor)

            # Switch schema if specified
            if schema:
                cursor.execute(f"USE SCHEMA {schema.value}")

            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()

            return results  # type: ignore

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    # Enhanced Knowledge Base Operations supporting chunking
    async def insert_knowledge_entry_chunked(
        self,
        entry_id: str,
        title: str,
        content: str,
        category_id: str = "general",
        source_id: str = "src_manual",
        importance_score: float = 1.0,
        is_foundational: bool = False,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        file_path: str | None = None,
        file_size_bytes: int | None = None,
        chunk_index: int = 0,
        total_chunks: int = 1,
        created_by: str = "system",
    ) -> bool:
        """Enhanced knowledge entry insertion with chunking support"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.UNIVERSAL_CHAT, "knowledge_base_entries")}
        (ENTRY_ID, TITLE, CONTENT, CATEGORY_ID, SOURCE_ID, IMPORTANCE_SCORE,
         IS_FOUNDATIONAL, TAGS, METADATA, FILE_PATH, FILE_SIZE_BYTES,
         CHUNK_INDEX, TOTAL_CHUNKS, CREATED_BY, CREATED_AT, UPDATED_AT)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """

        import json

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

    # AI Memory Operations for enhanced context
    async def insert_memory_entry(
        self,
        memory_id: str,
        category_id: str,
        memory_type: str,
        title: str,
        content: str,
        importance_score: float = 1.0,
        confidence_level: float = 1.0,
        related_entities: list[str] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Insert AI memory entry for enhanced context management"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.AI_MEMORY, "memory_entries")}
        (MEMORY_ID, CATEGORY_ID, MEMORY_TYPE, TITLE, CONTENT, IMPORTANCE_SCORE,
         CONFIDENCE_LEVEL, SOURCE_SYSTEM, RELATED_ENTITIES, TAGS, METADATA,
         CREATED_AT, UPDATED_AT)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """

        import json

        params = (
            memory_id,
            category_id,
            memory_type,
            title,
            content,
            importance_score,
            confidence_level,
            "sophia_ai",
            json.dumps(related_entities or []),
            json.dumps(tags or []),
            json.dumps(metadata or {}),
        )

        await self.execute_query(query, params, SchemaType.AI_MEMORY)
        return True

    # Enhanced search with cross-schema capabilities
    async def hybrid_search_enhanced(
        self,
        query: str,
        schemas: list[SchemaType] | None = None,
        limit: int = 10,
        include_embeddings: bool = True,
    ) -> dict[str, list[dict[str, Any]]]:
        """Enhanced hybrid search across multiple schemas"""

        if not schemas:
            schemas = [SchemaType.UNIVERSAL_CHAT, SchemaType.AI_MEMORY]

        results = {}

        for schema in schemas:
            if schema == SchemaType.UNIVERSAL_CHAT:
                # Search knowledge base
                search_query = f"""
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
                    'knowledge' as SOURCE_TYPE
                FROM {self.get_table_name(schema, "knowledge_base_entries")} k
                JOIN {self.get_table_name(schema, "knowledge_categories")} c
                  ON k.CATEGORY_ID = c.CATEGORY_ID
                WHERE (UPPER(k.TITLE) LIKE UPPER(?) OR UPPER(k.CONTENT) LIKE UPPER(?))
                ORDER BY k.IMPORTANCE_SCORE DESC, k.CREATED_AT DESC
                LIMIT ?
                """

                search_term = f"%{query}%"
                params = (search_term, search_term, limit)

                results[schema.value] = await self.execute_query(
                    search_query, params, schema
                )

            elif schema == SchemaType.AI_MEMORY:
                # Search AI memory
                memory_query = f"""
                SELECT
                    m.MEMORY_ID,
                    m.TITLE,
                    m.CONTENT,
                    m.MEMORY_TYPE,
                    m.IMPORTANCE_SCORE,
                    m.CONFIDENCE_LEVEL,
                    'memory' as SOURCE_TYPE
                FROM {self.get_table_name(schema, "memory_entries")} m
                WHERE (UPPER(m.TITLE) LIKE UPPER(?) OR UPPER(m.CONTENT) LIKE UPPER(?))
                ORDER BY m.IMPORTANCE_SCORE DESC, m.CREATED_AT DESC
                LIMIT ?
                """

                search_term = f"%{query}%"
                params = (search_term, search_term, limit)

                results[schema.value] = await self.execute_query(
                    memory_query, params, schema
                )

        return results

    # Analytics operations
    async def log_system_metric(
        self,
        metric_type: str,
        metric_name: str,
        metric_value: float,
        dimensions: dict[str, Any] | None = None,
    ) -> bool:
        """Log system metrics for comprehensive monitoring"""

        from uuid import uuid4

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.UNIVERSAL_CHAT, "system_analytics")}
        (ANALYTICS_ID, METRIC_TYPE, METRIC_NAME, METRIC_VALUE, DIMENSIONS, TIMESTAMP)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP())
        """

        import json

        params = (
            str(uuid4()),
            metric_type,
            metric_name,
            metric_value,
            json.dumps(dimensions or {}),
        )

        await self.execute_query(query, params, SchemaType.UNIVERSAL_CHAT)
        return True

    # Enhanced conversation operations with metadata
    async def save_conversation_message_enhanced(
        self,
        message_id: str,
        session_id: str,
        user_id: str,
        message_type: str,
        message_content: str,
        knowledge_entries_used: list[str] | None = None,
        processing_time_ms: int | None = None,
        model_used: str | None = None,
        confidence_score: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Save conversation message with comprehensive metadata"""

        query = f"""
        INSERT INTO {self.get_table_name(SchemaType.UNIVERSAL_CHAT, "conversation_messages")}
        (MESSAGE_ID, SESSION_ID, USER_ID, MESSAGE_TYPE, MESSAGE_CONTENT,
         KNOWLEDGE_ENTRIES_USED, PROCESSING_TIME_MS, MODEL_USED, CONFIDENCE_SCORE,
         METADATA, CREATED_AT)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP())
        """

        import json

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
        return True

    async def get_comprehensive_analytics(self, hours_back: int = 24) -> dict[str, Any]:
        """Get comprehensive analytics across all schemas"""

        analytics = {}

        # System analytics from UNIVERSAL_CHAT
        system_query = f"""
        SELECT
            METRIC_TYPE,
            METRIC_NAME,
            COUNT(*) as COUNT,
            AVG(METRIC_VALUE) as AVG_VALUE,
            MAX(METRIC_VALUE) as MAX_VALUE,
            MIN(METRIC_VALUE) as MIN_VALUE
        FROM {self.get_table_name(SchemaType.UNIVERSAL_CHAT, "system_analytics")}
        WHERE TIMESTAMP >= DATEADD(hour, -?, CURRENT_TIMESTAMP())
        GROUP BY METRIC_TYPE, METRIC_NAME
        ORDER BY METRIC_TYPE, METRIC_NAME
        """

        try:
            system_results = await self.execute_query(
                system_query, (hours_back,), SchemaType.UNIVERSAL_CHAT
            )
            analytics["system_metrics"] = system_results
        except Exception as e:
            logger.warning(f"Could not fetch system analytics: {e}")
            analytics["system_metrics"] = []

        # Knowledge usage analytics
        usage_query = f"""
        SELECT
            COUNT(DISTINCT USER_ID) as UNIQUE_USERS,
            COUNT(DISTINCT ENTRY_ID) as ENTRIES_ACCESSED,
            COUNT(*) as TOTAL_ACCESSES,
            AVG(RELEVANCE_SCORE) as AVG_RELEVANCE
        FROM {self.get_table_name(SchemaType.UNIVERSAL_CHAT, "knowledge_usage_analytics")}
        WHERE ACCESSED_AT >= DATEADD(hour, -?, CURRENT_TIMESTAMP())
        """

        try:
            usage_results = await self.execute_query(
                usage_query, (hours_back,), SchemaType.UNIVERSAL_CHAT
            )
            analytics["knowledge_usage"] = usage_results[0] if usage_results else {}
        except Exception as e:
            logger.warning(f"Could not fetch knowledge usage analytics: {e}")
            analytics["knowledge_usage"] = {}

        return analytics

    async def get_schema_health(self) -> dict[str, Any]:
        """Get health status for all schemas"""

        health_status = {}

        for schema in SchemaType:
            try:
                # Test basic connectivity
                test_query = "SELECT CURRENT_SCHEMA() as schema_name"
                await self.execute_query(test_query, schema=schema)

                # Get table information
                table_info = {}
                for table_key in self.schema_tables.get(schema, {}):
                    try:
                        count_query = f"SELECT COUNT(*) as row_count FROM {self.schema_tables[schema][table_key]}"
                        result = await self.execute_query(count_query, schema=schema)
                        table_info[table_key] = result[0]["ROW_COUNT"] if result else 0
                    except Exception:
                        table_info[table_key] = "inaccessible"

                health_status[schema.value] = {
                    "status": "healthy",
                    "tables": table_info,
                }

            except Exception as e:
                health_status[schema.value] = {"status": "error", "error": str(e)}

        return health_status

    async def disconnect(self):
        """Clean disconnect from Snowflake"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from enhanced Snowflake deployment")


# Global instance for application use
enhanced_snowflake_manager = EnhancedSnowflakeManager()
