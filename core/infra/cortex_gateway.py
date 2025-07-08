"""
Unified CortexGateway - Single entry point for all Snowflake operations.
Provides credit governance, monitoring, and intelligent routing.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Optional

from prometheus_client import Counter, Gauge, Histogram
from snowflake.connector import DictCursor

from infrastructure.core.optimized_connection_manager import OptimizedConnectionManager

logger = logging.getLogger(__name__)

# Prometheus metrics
snowflake_query_duration = Histogram(
    "snowflake_query_duration_seconds",
    "Time spent on Snowflake queries",
    ["function", "warehouse"],
)
snowflake_query_count = Counter(
    "snowflake_queries_total",
    "Total number of Snowflake queries",
    ["function", "status"],
)
snowflake_credits_used = Counter(
    "snowflake_credits_total",
    "Total Snowflake credits consumed",
    ["warehouse", "function"],
)
snowflake_daily_credits = Gauge(
    "snowflake_daily_credits_remaining", "Remaining daily credit allowance"
)


def track_metrics(function_name: str):
    """Decorator to track Prometheus metrics"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            warehouse = kwargs.get("warehouse", "COMPUTE_WH")

            try:
                result = await func(*args, **kwargs)
                snowflake_query_count.labels(
                    function=function_name, status="success"
                ).inc()
                return result
            except Exception:
                snowflake_query_count.labels(
                    function=function_name, status="error"
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                snowflake_query_duration.labels(
                    function=function_name, warehouse=warehouse
                ).observe(duration)

        return wrapper

    return decorator


class CortexGateway:
    """
    Unified gateway for all Snowflake and Cortex AI operations.
    Ensures single connection pool, credit governance, and monitoring.
    """

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = False
            self._conn_manager = None
            self._daily_credit_limit = 100
            self._credits_used_today = 0
            self._last_credit_reset = datetime.now().date()

    async def initialize(self):
        """Initialize the gateway with connection manager"""
        async with self._lock:
            if self._initialized:
                return

            logger.info("Initializing CortexGateway...")

            # Initialize connection manager
            self._conn_manager = OptimizedConnectionManager()
            await self._conn_manager.initialize()

            # Create usage tracking table if not exists
            await self._create_usage_table()

            # Load today's credit usage
            await self._load_credit_usage()

            self._initialized = True
            logger.info("CortexGateway initialized successfully")

    async def _create_usage_table(self):
        """Create credit usage tracking table"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS SOPHIA_AI_UNIFIED.MONITORING.CORTEX_USAGE_LOG (
            timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            function_name VARCHAR,
            warehouse_name VARCHAR,
            credits_estimated FLOAT,
            query_text VARCHAR,
            user_name VARCHAR DEFAULT CURRENT_USER(),
            session_id VARCHAR
        );
        """

        try:
            async with self._conn_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                cursor.close()
        except Exception as e:
            logger.warning(f"Could not create usage table: {e}")

    async def _load_credit_usage(self):
        """Load today's credit usage from database"""
        query = """
        SELECT COALESCE(SUM(credits_estimated), 0) as total_credits
        FROM SOPHIA_AI_UNIFIED.MONITORING.CORTEX_USAGE_LOG
        WHERE DATE(timestamp) = CURRENT_DATE()
        """

        try:
            async with self._conn_manager.get_connection() as conn:
                cursor = conn.cursor(DictCursor)
                cursor.execute(query)
                result = cursor.fetchone()
                self._credits_used_today = result["TOTAL_CREDITS"] if result else 0
                cursor.close()

            # Update Prometheus metric
            snowflake_daily_credits.set(
                self._daily_credit_limit - self._credits_used_today
            )

        except Exception as e:
            logger.warning(f"Could not load credit usage: {e}")
            self._credits_used_today = 0

    async def _check_credit_limit(self, estimated_credits: float = 0.01):
        """Check if operation would exceed daily credit limit"""
        # Reset daily counter if new day
        if datetime.now().date() > self._last_credit_reset:
            self._credits_used_today = 0
            self._last_credit_reset = datetime.now().date()

        if self._credits_used_today + estimated_credits > self._daily_credit_limit:
            raise Exception(
                f"Daily credit limit ({self._daily_credit_limit}) would be exceeded. "
                f"Current usage: {self._credits_used_today:.2f}"
            )

    async def _log_usage(
        self, function_name: str, warehouse: str, credits: float, query: str = None
    ):
        """Log credit usage to database"""
        self._credits_used_today += credits

        # Update Prometheus metrics
        snowflake_credits_used.labels(warehouse=warehouse, function=function_name).inc(
            credits
        )
        snowflake_daily_credits.set(self._daily_credit_limit - self._credits_used_today)

        # Log to database
        insert_sql = """
        INSERT INTO SOPHIA_AI_UNIFIED.MONITORING.CORTEX_USAGE_LOG
        (function_name, warehouse_name, credits_estimated, query_text, session_id)
        VALUES (%s, %s, %s, %s, %s)
        """

        try:
            async with self._conn_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    insert_sql,
                    (
                        function_name,
                        warehouse,
                        credits,
                        query[:1000] if query else None,  # Truncate long queries
                        self._conn_manager._session_id,
                    ),
                )
                cursor.close()
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")

    @track_metrics("execute_sql")
    async def execute_sql(
        self, query: str, params: Optional[tuple] = None, warehouse: str = "COMPUTE_WH"
    ) -> list[dict[str, Any]]:
        """Execute SQL query with credit tracking"""
        if not self._initialized:
            await self.initialize()

        # Estimate credits (simplified - 0.01 per query)
        estimated_credits = 0.01
        await self._check_credit_limit(estimated_credits)

        try:
            async with self._conn_manager.get_connection(warehouse) as conn:
                cursor = conn.cursor(DictCursor)

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                results = cursor.fetchall()
                cursor.close()

                # Log usage
                await self._log_usage(
                    "execute_sql", warehouse, estimated_credits, query
                )

                return results

        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise

    @track_metrics("cortex_complete")
    async def complete(
        self,
        prompt: str,
        model: str = "mixtral-8x7b",
        warehouse: str = "CORTEX_COMPUTE_WH",
    ) -> str:
        """Execute Cortex COMPLETE function"""
        if not self._initialized:
            await self.initialize()

        # Estimate credits based on model and prompt length
        estimated_credits = len(prompt) / 1000 * 0.1  # Simplified estimation
        await self._check_credit_limit(estimated_credits)

        query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', %s) as response"

        try:
            async with self._conn_manager.get_connection(warehouse) as conn:
                cursor = conn.cursor(DictCursor)
                cursor.execute(query, (prompt,))
                result = cursor.fetchone()
                cursor.close()

                response = result["RESPONSE"] if result else ""

                # Log usage
                await self._log_usage(
                    "cortex_complete", warehouse, estimated_credits, query
                )

                return response

        except Exception as e:
            logger.error(f"Cortex COMPLETE failed: {e}")
            raise

    @track_metrics("cortex_embed")
    async def embed(
        self, text: str, model: str = "e5-base-v2", warehouse: str = "CORTEX_COMPUTE_WH"
    ) -> list[float]:
        """Generate embeddings using Cortex"""
        if not self._initialized:
            await self.initialize()

        # Estimate credits
        estimated_credits = 0.05
        await self._check_credit_limit(estimated_credits)

        query = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('{model}', %s) as embedding"

        try:
            async with self._conn_manager.get_connection(warehouse) as conn:
                cursor = conn.cursor(DictCursor)
                cursor.execute(query, (text,))
                result = cursor.fetchone()
                cursor.close()

                embedding = json.loads(result["EMBEDDING"]) if result else []

                # Log usage
                await self._log_usage(
                    "cortex_embed", warehouse, estimated_credits, query
                )

                return embedding

        except Exception as e:
            logger.error(f"Cortex embedding failed: {e}")
            raise

    @track_metrics("cortex_batch_embed")
    async def batch_embed(
        self,
        texts: list[str],
        model: str = "e5-base-v2",
        warehouse: str = "CORTEX_COMPUTE_WH",
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts"""
        if not self._initialized:
            await self.initialize()

        # Estimate credits
        estimated_credits = 0.05 * len(texts)
        await self._check_credit_limit(estimated_credits)

        embeddings = []

        # Process in batches to avoid query size limits
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            # Create UNION ALL query for batch
            union_parts = []
            for j, text in enumerate(batch):
                union_parts.append(
                    f"SELECT {j} as idx, "
                    f"SNOWFLAKE.CORTEX.EMBED_TEXT_768('{model}', %s) as embedding"
                )

            query = " UNION ALL ".join(union_parts) + " ORDER BY idx"

            try:
                async with self._conn_manager.get_connection(warehouse) as conn:
                    cursor = conn.cursor(DictCursor)
                    cursor.execute(query, batch)
                    results = cursor.fetchall()
                    cursor.close()

                    for result in results:
                        embeddings.append(json.loads(result["EMBEDDING"]))

            except Exception as e:
                logger.error(f"Batch embedding failed: {e}")
                raise

        # Log usage
        await self._log_usage("cortex_batch_embed", warehouse, estimated_credits)

        return embeddings

    @track_metrics("cortex_sentiment")
    async def sentiment(self, text: str, warehouse: str = "CORTEX_COMPUTE_WH") -> float:
        """Analyze sentiment using Cortex"""
        if not self._initialized:
            await self.initialize()

        # Estimate credits
        estimated_credits = 0.02
        await self._check_credit_limit(estimated_credits)

        query = "SELECT SNOWFLAKE.CORTEX.SENTIMENT(%s) as sentiment"

        try:
            async with self._conn_manager.get_connection(warehouse) as conn:
                cursor = conn.cursor(DictCursor)
                cursor.execute(query, (text,))
                result = cursor.fetchone()
                cursor.close()

                sentiment = result["SENTIMENT"] if result else 0.0

                # Log usage
                await self._log_usage(
                    "cortex_sentiment", warehouse, estimated_credits, query
                )

                return sentiment

        except Exception as e:
            logger.error(f"Cortex sentiment analysis failed: {e}")
            raise

    @track_metrics("cortex_search")
    async def search(
        self,
        service_name: str,
        query: str,
        limit: int = 10,
        warehouse: str = "CORTEX_COMPUTE_WH",
    ) -> list[dict[str, Any]]:
        """Search using Cortex search service"""
        if not self._initialized:
            await self.initialize()

        # Estimate credits
        estimated_credits = 0.1
        await self._check_credit_limit(estimated_credits)

        search_query = f"""
        SELECT * FROM TABLE(
            SNOWFLAKE.CORTEX.SEARCH_SERVICE(
                '{service_name}',
                '{query}',
                {limit}
            )
        )
        """

        try:
            results = await self.execute_sql(search_query, warehouse=warehouse)

            # Log usage (already logged by execute_sql, just update)
            await self._log_usage("cortex_search", warehouse, estimated_credits - 0.01)

            return results

        except Exception as e:
            logger.error(f"Cortex search failed: {e}")
            raise

    async def health_check(self) -> dict[str, Any]:
        """Check gateway health and credit usage"""
        if not self._initialized:
            await self.initialize()

        try:
            # Test connection
            result = await self.execute_sql("SELECT 1 as health_check")

            return {
                "status": "healthy",
                "credits_used_today": self._credits_used_today,
                "credits_remaining": self._daily_credit_limit
                - self._credits_used_today,
                "daily_limit": self._daily_credit_limit,
                "connection_pool_size": self._conn_manager._pool_size
                if self._conn_manager
                else 0,
                "initialized": self._initialized,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": self._initialized,
            }

    async def close(self):
        """Close the gateway and cleanup resources"""
        if self._conn_manager:
            await self._conn_manager.close()
        self._initialized = False


# Global singleton instance
_gateway_instance = None


def get_gateway() -> CortexGateway:
    """Get the global CortexGateway instance"""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = CortexGateway()
    return _gateway_instance
