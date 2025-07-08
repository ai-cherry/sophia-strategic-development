"""
Snowflake V2 Main Handler - Core business logic for Snowflake operations
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import snowflake.connector
from snowflake.connector import DictCursor
from snowflake.connector.errors import Error as SnowflakeError

from ..config import Config
from ..models.data_models import (
    DataLoadRequest,
    EmbeddingRequest,
    OptimizationRequest,
    QueryRequest,
    QueryResponse,
    SchemaRequest,
    SearchRequest,
    TableRequest,
)
from ..utils.db import SnowflakeConnection

logger = logging.getLogger(__name__)


class SnowflakeHandler:
    """Main handler for Snowflake operations with AI enhancements"""

    def __init__(self, config: Config):
        self.config = config
        self.db = SnowflakeConnection(config)
        self._initialized = False

    async def initialize(self):
        """Initialize handler and establish connection"""
        try:
            await self.db.connect()
            self._initialized = True
            logger.info("Snowflake handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize handler: {e}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.db.disconnect()
            self._initialized = False
            logger.info("Snowflake handler cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def execute_query(self, request: dict) -> dict:
        """Execute a Snowflake query with enhanced features"""
        try:
            query_req = QueryRequest(**request)

            # Execute query
            result = await self.db.execute_query(
                query_req.query,
                fetch_results=query_req.fetch_results,
                parameters=query_req.parameters,
            )

            # Format response
            response = QueryResponse(
                success=True,
                data=result if query_req.fetch_results else [],
                row_count=len(result) if result else 0,
                execution_time=0.0,  # TODO: Track actual execution time
                query_id=None,  # TODO: Get query ID from Snowflake
            )

            return response.dict()

        except SnowflakeError as e:
            logger.error(f"Snowflake error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return {"success": False, "error": str(e)}

    async def create_schema(self, request: dict) -> dict:
        """Create a new schema"""
        try:
            schema_req = SchemaRequest(**request)

            # Build CREATE SCHEMA statement
            sql = f"CREATE SCHEMA IF NOT EXISTS {schema_req.database}.{schema_req.name}"
            if schema_req.comment:
                sql += f" COMMENT = '{schema_req.comment}'"

            await self.db.execute_query(sql, fetch_results=False)

            # Create AI-ready tables if requested
            if schema_req.create_ai_tables:
                await self._create_ai_tables(schema_req.database, schema_req.name)

            return {
                "success": True,
                "schema": f"{schema_req.database}.{schema_req.name}",
                "message": f"Schema {schema_req.name} created successfully",
            }

        except Exception as e:
            logger.error(f"Schema creation error: {e}")
            return {"success": False, "error": str(e)}

    async def create_table(self, request: dict) -> dict:
        """Create a new table with AI-ready columns"""
        try:
            table_req = TableRequest(**request)

            # Build CREATE TABLE statement
            columns = []
            for col in table_req.columns:
                col_def = f"{col['name']} {col['type']}"
                if col.get("not_null"):
                    col_def += " NOT NULL"
                if col.get("default"):
                    col_def += f" DEFAULT {col['default']}"
                columns.append(col_def)

            # Add AI columns if requested
            if table_req.add_ai_columns:
                columns.extend(
                    [
                        "ai_embeddings VECTOR(FLOAT, 768)",
                        "ai_summary TEXT",
                        "ai_sentiment FLOAT",
                        "ai_keywords VARIANT",
                        "ai_processed_at TIMESTAMP",
                    ]
                )

            sql = f"""
            CREATE TABLE IF NOT EXISTS {table_req.database}.{table_req.schema}.{table_req.name} (
                {', '.join(columns)}
            )
            """

            if table_req.cluster_by:
                sql += f" CLUSTER BY ({', '.join(table_req.cluster_by)})"

            await self.db.execute_query(sql, fetch_results=False)

            return {
                "success": True,
                "table": f"{table_req.database}.{table_req.schema}.{table_req.name}",
                "message": f"Table {table_req.name} created successfully",
            }

        except Exception as e:
            logger.error(f"Table creation error: {e}")
            return {"success": False, "error": str(e)}

    async def load_data(self, request: dict) -> dict:
        """Load data with automatic AI enrichment"""
        try:
            DataLoadRequest(**request)

            # TODO: Implement data loading logic
            # This would handle various data sources and formats

            return {
                "success": True,
                "message": "Data loading not yet implemented",
                "rows_loaded": 0,
            }

        except Exception as e:
            logger.error(f"Data loading error: {e}")
            return {"success": False, "error": str(e)}

    async def generate_embeddings(self, request: dict) -> dict:
        """Generate embeddings using Snowflake Cortex"""
        try:
            embed_req = EmbeddingRequest(**request)

            # Use Snowflake Cortex for embeddings
            sql = f"""
            UPDATE {embed_req.table}
            SET {embed_req.embedding_column} = SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                'snowflake-arctic-embed-m-v2.0',
                {embed_req.text_column}
            )
            WHERE {embed_req.embedding_column} IS NULL
            """

            if embed_req.where_clause:
                sql += f" AND {embed_req.where_clause}"

            await self.db.execute_query(sql, fetch_results=False)

            # Get count of updated rows
            count_sql = f"""
            SELECT COUNT(*) as updated_count
            FROM {embed_req.table}
            WHERE {embed_req.embedding_column} IS NOT NULL
            """

            result = await self.db.execute_query(count_sql)
            updated_count = result[0]["UPDATED_COUNT"] if result else 0

            return {
                "success": True,
                "message": "Embeddings generated successfully",
                "rows_updated": updated_count,
            }

        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return {"success": False, "error": str(e)}

    async def semantic_search(self, request: dict) -> dict:
        """Perform semantic search using embeddings"""
        try:
            search_req = SearchRequest(**request)

            # Generate embedding for search query
            embed_sql = f"""
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                'snowflake-arctic-embed-m-v2.0',
                '{search_req.query}'
            ) as query_embedding
            """

            embed_result = await self.db.execute_query(embed_sql)
            if not embed_result:
                return {"success": False, "error": "Failed to generate query embedding"}

            # Perform vector similarity search
            search_sql = f"""
            SELECT
                {', '.join(search_req.return_columns)},
                VECTOR_COSINE_SIMILARITY(
                    {search_req.embedding_column},
                    {embed_result[0]['QUERY_EMBEDDING']}
                ) as similarity_score
            FROM {search_req.table}
            WHERE similarity_score > {search_req.similarity_threshold}
            ORDER BY similarity_score DESC
            LIMIT {search_req.limit}
            """

            results = await self.db.execute_query(search_sql)

            return {
                "success": True,
                "results": results,
                "count": len(results) if results else 0,
            }

        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return {"success": False, "error": str(e)}

    async def get_system_status(self) -> dict:
        """Get comprehensive Snowflake system status"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "connection": "connected" if self.db.connection else "disconnected",
                "current_context": {},
                "statistics": {},
            }

            # Get current context
            context_queries = {
                "role": "SELECT CURRENT_ROLE() as value",
                "warehouse": "SELECT CURRENT_WAREHOUSE() as value",
                "database": "SELECT CURRENT_DATABASE() as value",
                "schema": "SELECT CURRENT_SCHEMA() as value",
            }

            for key, query in context_queries.items():
                result = await self.db.execute_query(query)
                if result:
                    status["current_context"][key] = result[0]["VALUE"]

            # Get database statistics
            stats_sql = """
            SELECT
                COUNT(DISTINCT table_catalog) as database_count,
                COUNT(DISTINCT table_schema) as schema_count,
                COUNT(DISTINCT table_name) as table_count
            FROM information_schema.tables
            WHERE table_catalog LIKE 'SOPHIA%'
            """

            stats_result = await self.db.execute_query(stats_sql)
            if stats_result:
                status["statistics"] = stats_result[0]

            return status

        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {"error": str(e)}

    async def optimize_performance(self, request: dict) -> dict:
        """Optimize Snowflake performance"""
        try:
            opt_req = OptimizationRequest(**request)
            optimizations = []

            # Apply clustering if requested
            if opt_req.apply_clustering:
                for table, columns in opt_req.clustering_keys.items():
                    sql = f"ALTER TABLE {table} CLUSTER BY ({', '.join(columns)})"
                    await self.db.execute_query(sql, fetch_results=False)
                    optimizations.append(f"Applied clustering to {table}")

            # Analyze table statistics
            if opt_req.analyze_tables:
                for table in opt_req.tables_to_analyze:
                    # Snowflake automatically maintains statistics
                    # But we can force a refresh
                    sql = f"ALTER TABLE {table} SET CHANGE_TRACKING = TRUE"
                    await self.db.execute_query(sql, fetch_results=False)
                    optimizations.append(f"Enabled change tracking for {table}")

            return {
                "success": True,
                "optimizations": optimizations,
                "message": f"Applied {len(optimizations)} optimizations",
            }

        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return {"success": False, "error": str(e)}

    async def sync_schemas(self, request: dict) -> dict:
        """Synchronize schemas with codebase definitions"""
        try:
            # TODO: Implement schema synchronization
            # This would read schema definitions from the codebase
            # and apply them to Snowflake

            return {
                "success": True,
                "message": "Schema synchronization not yet implemented",
            }

        except Exception as e:
            logger.error(f"Schema sync error: {e}")
            return {"success": False, "error": str(e)}

    async def manage_warehouse(self, request: dict) -> dict:
        """Manage Snowflake warehouses"""
        try:
            action = request.get("action")
            warehouse = request.get("warehouse", self.config.SNOWFLAKE_WAREHOUSE)

            if action == "resume":
                sql = f"ALTER WAREHOUSE {warehouse} RESUME"
            elif action == "suspend":
                sql = f"ALTER WAREHOUSE {warehouse} SUSPEND"
            elif action == "resize":
                size = request.get("size", "MEDIUM")
                sql = f"ALTER WAREHOUSE {warehouse} SET WAREHOUSE_SIZE = '{size}'"
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

            await self.db.execute_query(sql, fetch_results=False)

            return {
                "success": True,
                "warehouse": warehouse,
                "action": action,
                "message": f"Warehouse {warehouse} {action} completed",
            }

        except Exception as e:
            logger.error(f"Warehouse management error: {e}")
            return {"success": False, "error": str(e)}

    async def _create_ai_tables(self, database: str, schema: str):
        """Create standard AI-ready tables in a schema"""
        # AI Memory table
        memory_sql = f"""
        CREATE TABLE IF NOT EXISTS {database}.{schema}.ai_memory (
            memory_id VARCHAR(255) PRIMARY KEY,
            content TEXT NOT NULL,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
        """
        await self.db.execute_query(memory_sql, fetch_results=False)

        # AI Analytics table
        analytics_sql = f"""
        CREATE TABLE IF NOT EXISTS {database}.{schema}.ai_analytics (
            id VARCHAR(255) PRIMARY KEY,
            event_type VARCHAR(100),
            event_data VARIANT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
        """
        await self.db.execute_query(analytics_sql, fetch_results=False)
