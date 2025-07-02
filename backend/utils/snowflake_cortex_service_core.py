"""
Snowflake Cortex Service - Core Module
Contains the main service class with connection management and basic operations
"""

from __future__ import annotations

import logging
from typing import Any

from backend.core.auto_esc_config import get_config_value
from backend.core.optimized_connection_manager import ConnectionType

logger = logging.getLogger(__name__)


class SnowflakeCortexService:
    """
    Core service for accessing Snowflake Cortex AI capabilities

    This class provides the foundation for Snowflake's native AI functions
    for text processing, embeddings, and vector search directly within
    the data warehouse.
    """

    def __init__(self):
        # Remove individual connection - use optimized connection manager
        from backend.core.optimized_connection_manager import connection_manager

        self.connection_manager = connection_manager

        self.database = get_config_value("snowflake_database", "SOPHIA_AI")
        self.schema = get_config_value("snowflake_schema", "AI_PROCESSING")
        self.warehouse = get_config_value("snowflake_warehouse", "SOPHIA_AI_WH")
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
            await self.connection_manager.execute_query(
                f"USE WAREHOUSE {self.warehouse}"
            )

            # Ensure vector tables exist
            await self._create_vector_tables()

            self.initialized = True
            logger.info(
                "✅ Snowflake Cortex service initialized successfully with optimized connection manager"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Snowflake Cortex service: {e}")
            raise

    async def _create_vector_tables(self):
        """Create vector storage tables if they don't exist"""
        for table_type, table_name in self.vector_tables.items():
            create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id VARCHAR(255) PRIMARY KEY,
                original_text TEXT,
                embedding_vector VECTOR(FLOAT, 768),
                metadata VARIANT,
                source_table VARCHAR(255),
                source_id VARCHAR(255),
                embedding_model VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            )
            """
            try:
                await self.connection_manager.execute_query(create_query)
                logger.info(f"✅ Vector table {table_name} ready")
            except Exception as e:
                logger.error(f"Error creating vector table {table_name}: {e}")

    async def close(self):
        """Close Snowflake connection"""
        # Connection is managed by connection manager
        self.initialized = False
        logger.info("Snowflake Cortex service closed")

    async def get_connection(self):
        """Get the current connection (for backward compatibility)"""
        if not self.initialized:
            await self.initialize()
        return self.connection_manager

    async def execute_query(self, query: str, params: tuple | None = None):
        """Execute a query using the connection manager"""
        if not self.initialized:
            await self.initialize()
        return await self.connection_manager.execute_query(query, params) 