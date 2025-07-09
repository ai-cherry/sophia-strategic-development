"""
Enhanced Snowflake Adapter with PAT Authentication and Intelligent Routing
Integrates with Lambda Labs infrastructure and MCP server ecosystem
Works behind the CortexGateway for unified access
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

import redis.asyncio as redis
from pydantic import BaseSettings, Field

# Import our existing connection manager
from infrastructure.core.optimized_connection_manager import OptimizedConnectionManager

logger = logging.getLogger(__name__)


class SnowflakeConfig(BaseSettings):
    """Snowflake configuration with PAT authentication"""

    account: str = Field(default="UHDECNO-CVB64222", env="SNOWFLAKE_ACCOUNT")
    user: str = Field(default="SCOOBYJAVA15", env="SNOWFLAKE_USER")
    password: str = Field(
        default="eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",
        env="SNOWFLAKE_PAT_TOKEN",
    )
    role: str = Field(default="ACCOUNTADMIN", env="SNOWFLAKE_ROLE")
    database: str = Field(default="SOPHIA_AI_UNIFIED", env="SNOWFLAKE_DATABASE")
    schema: str = Field(default="PRODUCTION", env="SNOWFLAKE_SCHEMA")
    warehouse: str = Field(default="AI_COMPUTE_WH", env="SNOWFLAKE_WAREHOUSE")

    # Redis configuration for caching
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Credit limits
    daily_credit_limit: int = Field(default=100, env="SNOWFLAKE_DAILY_CREDIT_LIMIT")
    query_timeout: int = Field(default=300, env="SNOWFLAKE_QUERY_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = False


class WarehouseOptimizer:
    """Intelligent warehouse selection and optimization"""

    def __init__(self, config: SnowflakeConfig):
        self.config = config
        self.warehouse_mapping = {
            "ai_workloads": "CORTEX_COMPUTE_WH",
            "analytics": "AI_COMPUTE_WH",
            "general": "COMPUTE_WH",
            "loading": "LOADING_WH",
        }

    def select_optimal_warehouse(
        self, query: str, workload_type: str = "general"
    ) -> str:
        """Select optimal warehouse based on query characteristics"""
        query_upper = query.upper()

        # AI/ML workloads
        if any(
            keyword in query_upper
            for keyword in [
                "CORTEX",
                "ML",
                "AI",
                "PREDICT",
                "CLASSIFY",
                "EMBED",
                "COMPLETE",
            ]
        ):
            return "CORTEX_COMPUTE_WH"

        # Analytics workloads
        elif any(
            keyword in query_upper
            for keyword in [
                "AGGREGATE",
                "GROUP BY",
                "WINDOW",
                "ANALYTICS",
                "SUM",
                "AVG",
            ]
        ):
            return "AI_COMPUTE_WH"

        # Loading workloads
        elif any(
            keyword in query_upper
            for keyword in ["COPY", "INSERT", "MERGE", "LOAD", "CREATE", "ALTER"]
        ):
            return "LOADING_WH"

        # Default based on workload type
        return self.warehouse_mapping.get(workload_type, "COMPUTE_WH")


class CreditTracker:
    """Track and enforce credit limits"""

    def __init__(self, daily_limit: int = 100):
        self.daily_limit = daily_limit
        self.usage_log = []
        self.current_date = datetime.now().date()

    def estimate_credits(self, query: str, warehouse: str) -> float:
        """Estimate credits for a query (simplified)"""
        # Base estimates by warehouse size
        warehouse_credits = {
            "CORTEX_COMPUTE_WH": 0.5,  # Larger for AI
            "AI_COMPUTE_WH": 0.3,
            "COMPUTE_WH": 0.1,
            "LOADING_WH": 0.2,
        }

        base_credits = warehouse_credits.get(warehouse, 0.1)

        # Adjust for query complexity
        if "CORTEX" in query.upper():
            base_credits *= 2  # AI operations cost more

        return base_credits

    def can_execute(self, estimated_credits: float) -> bool:
        """Check if we have credits available"""
        # Reset daily usage
        if datetime.now().date() > self.current_date:
            self.usage_log = []
            self.current_date = datetime.now().date()

        daily_usage = sum(log["credits"] for log in self.usage_log)
        return (daily_usage + estimated_credits) <= self.daily_limit

    def log_usage(
        self, query: str, warehouse: str, credits: float, execution_time: float
    ):
        """Log credit usage"""
        self.usage_log.append(
            {
                "timestamp": datetime.now(),
                "query": query[:100],  # First 100 chars
                "warehouse": warehouse,
                "credits": credits,
                "execution_time": execution_time,
            }
        )


class EnhancedSnowflakeAdapter:
    """
    Enhanced Snowflake adapter with intelligent routing and optimization.
    Designed to work behind CortexGateway for production use.
    """

    def __init__(self, config: SnowflakeConfig | None = None):
        self.config = config or SnowflakeConfig()
        self.warehouse_optimizer = WarehouseOptimizer(self.config)
        self.credit_tracker = CreditTracker(self.config.daily_credit_limit)
        self.connection_manager = OptimizedConnectionManager()
        self.redis_client = None
        self._initialized = False

    async def initialize(self):
        """Initialize adapter components"""
        if self._initialized:
            return

        # Initialize connection manager
        await self.connection_manager.initialize()

        # Initialize Redis for caching
        await self._initialize_redis()

        self._initialized = True
        logger.info("✅ EnhancedSnowflakeAdapter initialized")

    async def _initialize_redis(self):
        """Initialize Redis client for caching"""
        try:
            self.redis_client = redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            logger.info("✅ Redis connection established for caching")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed, caching disabled: {e}")
            self.redis_client = None

    async def execute_query(
        self,
        query: str,
        workload_type: str = "general",
        use_cache: bool = True,
        cache_ttl: int = 300,
        params: tuple | None = None,
    ) -> list[dict[str, Any]]:
        """Execute query with intelligent warehouse routing and caching"""

        await self.initialize()

        # Check cache first
        cache_key = None
        if use_cache and self.redis_client and not params:
            cache_key = f"snowflake:{hash(query)}:{workload_type}"
            try:
                cached_result = await self.redis_client.get(cache_key)
                if cached_result:
                    logger.info("📋 Cache hit for query")
                    return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

        # Select optimal warehouse
        warehouse = self.warehouse_optimizer.select_optimal_warehouse(
            query, workload_type
        )
        logger.info(f"🎯 Selected warehouse: {warehouse} for workload: {workload_type}")

        # Check credit limits
        estimated_credits = self.credit_tracker.estimate_credits(query, warehouse)
        if not self.credit_tracker.can_execute(estimated_credits):
            raise Exception(
                f"Daily credit limit exceeded. Estimated: {estimated_credits}, Remaining: {self.config.daily_credit_limit - sum(log['credits'] for log in self.credit_tracker.usage_log)}"
            )

        # Set warehouse in query
        warehouse_query = f"USE WAREHOUSE {warehouse};"

        start_time = datetime.now()

        try:
            # Execute using connection manager
            await self.connection_manager.execute_query(warehouse_query)
            result = await self.connection_manager.execute_query(query, params=params)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Log credit usage
            actual_credits = estimated_credits * (execution_time / 60)  # Rough estimate
            self.credit_tracker.log_usage(
                query, warehouse, actual_credits, execution_time
            )

            # Cache results if applicable
            if use_cache and self.redis_client and cache_key:
                try:
                    await self.redis_client.setex(
                        cache_key, cache_ttl, json.dumps(result, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Cache write error: {e}")

            logger.info(
                f"✅ Query executed in {execution_time:.2f}s using {actual_credits:.4f} credits"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise

    async def execute_cortex_function(
        self, function_name: str, parameters: dict[str, Any]
    ) -> Any:
        """Execute Snowflake Cortex AI functions"""

        cortex_functions = {
            "COMPLETE": "SELECT SNOWFLAKE.CORTEX.COMPLETE(?, ?) AS RESULT",
            "SENTIMENT": "SELECT SNOWFLAKE.CORTEX.SENTIMENT(?) AS RESULT",
            "TRANSLATE": "SELECT SNOWFLAKE.CORTEX.TRANSLATE(?, ?, ?) AS RESULT",
            "SUMMARIZE": "SELECT SNOWFLAKE.CORTEX.SUMMARIZE(?) AS RESULT",
            "EXTRACT_ANSWER": "SELECT SNOWFLAKE.CORTEX.EXTRACT_ANSWER(?, ?) AS RESULT",
            "EMBED_TEXT_768": "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(?, ?) AS RESULT",
        }

        if function_name not in cortex_functions:
            raise ValueError(f"Unsupported Cortex function: {function_name}")

        query = cortex_functions[function_name]

        # Build parameters tuple based on function
        if function_name == "COMPLETE":
            params = (parameters["model"], parameters["prompt"])
        elif function_name == "SENTIMENT":
            params = (parameters["text"],)
        elif function_name == "TRANSLATE":
            params = (
                parameters["text"],
                parameters["source_lang"],
                parameters["target_lang"],
            )
        elif function_name == "SUMMARIZE":
            params = (parameters["text"],)
        elif function_name == "EXTRACT_ANSWER":
            params = (parameters["text"], parameters["question"])
        elif function_name == "EMBED_TEXT_768":
            params = (parameters["model"], parameters["text"])
        else:
            raise ValueError(f"Unknown parameter mapping for {function_name}")

        # Force use of CORTEX_COMPUTE_WH for AI operations
        result = await self.execute_query(
            query,
            workload_type="ai_workloads",
            use_cache=function_name != "COMPLETE",  # Don't cache completions
            params=params,
        )

        return result[0]["RESULT"] if result else None

    async def batch_execute_cortex(
        self,
        function_name: str,
        batch_parameters: list[dict[str, Any]],
        batch_size: int = 100,
    ) -> list[Any]:
        """Execute Cortex functions in batches for efficiency"""
        results = []

        for i in range(0, len(batch_parameters), batch_size):
            batch = batch_parameters[i : i + batch_size]

            # Execute batch in parallel
            tasks = [
                self.execute_cortex_function(function_name, params) for params in batch
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle results and errors
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch item failed: {result}")
                    results.append(None)
                else:
                    results.append(result)

        return results

    async def optimize_warehouse_usage(self) -> dict[str, Any]:
        """Analyze and optimize warehouse usage patterns"""

        usage_query = """
        SELECT
            WAREHOUSE_NAME,
            AVG(AVG_RUNNING) as avg_utilization,
            SUM(CREDITS_USED) as total_credits,
            AVG(AVG_QUEUED_LOAD) as avg_queue_load,
            COUNT(DISTINCT DATE_TRUNC('hour', START_TIME)) as active_hours,
            CASE
                WHEN AVG(AVG_RUNNING) < 0.3 AND SUM(CREDITS_USED) > 100 THEN 'DOWNSIZE_CANDIDATE'
                WHEN AVG(AVG_QUEUED_LOAD) > 10 THEN 'UPSIZE_CANDIDATE'
                WHEN SUM(CREDITS_USED) = 0 THEN 'SUSPEND_CANDIDATE'
                ELSE 'OPTIMIZED'
            END as recommendation
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY
        WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
        GROUP BY WAREHOUSE_NAME
        ORDER BY total_credits DESC;
        """

        results = await self.execute_query(usage_query, "analytics", use_cache=False)

        optimization_actions = []
        total_savings = 0

        for warehouse in results:
            if warehouse["RECOMMENDATION"] == "DOWNSIZE_CANDIDATE":
                potential_savings = (
                    warehouse["TOTAL_CREDITS"] * 0.3
                )  # 30% savings estimate
                optimization_actions.append(
                    {
                        "warehouse": warehouse["WAREHOUSE_NAME"],
                        "action": "downsize",
                        "reason": f"Low utilization ({warehouse['AVG_UTILIZATION']:.2%}) with high costs",
                        "potential_savings": potential_savings,
                    }
                )
                total_savings += potential_savings

            elif warehouse["RECOMMENDATION"] == "SUSPEND_CANDIDATE":
                optimization_actions.append(
                    {
                        "warehouse": warehouse["WAREHOUSE_NAME"],
                        "action": "suspend",
                        "reason": "No usage detected in last 7 days",
                        "potential_savings": 0,
                    }
                )

        return {
            "analysis": results,
            "recommendations": optimization_actions,
            "total_potential_savings": total_savings,
            "estimated_monthly_savings": total_savings * 4.3,  # Weekly to monthly
            "timestamp": datetime.now().isoformat(),
        }

    async def get_credit_usage_summary(self) -> dict[str, Any]:
        """Get current credit usage summary"""
        daily_usage = sum(log["credits"] for log in self.credit_tracker.usage_log)

        return {
            "date": self.credit_tracker.current_date.isoformat(),
            "daily_limit": self.config.daily_credit_limit,
            "credits_used": daily_usage,
            "credits_remaining": self.config.daily_credit_limit - daily_usage,
            "usage_percentage": (daily_usage / self.config.daily_credit_limit) * 100,
            "queries_executed": len(self.credit_tracker.usage_log),
            "top_warehouses": self._get_top_warehouses(),
        }

    def _get_top_warehouses(self) -> list[dict[str, Any]]:
        """Get top warehouses by credit usage"""
        warehouse_usage = {}

        for log in self.credit_tracker.usage_log:
            warehouse = log["warehouse"]
            if warehouse not in warehouse_usage:
                warehouse_usage[warehouse] = {"credits": 0, "queries": 0}
            warehouse_usage[warehouse]["credits"] += log["credits"]
            warehouse_usage[warehouse]["queries"] += 1

        return [
            {
                "warehouse": wh,
                "credits": stats["credits"],
                "queries": stats["queries"],
                "avg_credits_per_query": (
                    stats["credits"] / stats["queries"] if stats["queries"] > 0 else 0
                ),
            }
            for wh, stats in sorted(
                warehouse_usage.items(), key=lambda x: x[1]["credits"], reverse=True
            )
        ]

    async def health_check(self) -> dict[str, Any]:
        """Comprehensive health check of Snowflake environment"""

        try:
            # Test basic connectivity
            test_query = """
            SELECT
                CURRENT_TIMESTAMP() as timestamp,
                CURRENT_USER() as user,
                CURRENT_ROLE() as role,
                CURRENT_WAREHOUSE() as warehouse,
                CURRENT_DATABASE() as database,
                CURRENT_SCHEMA() as schema
            """

            info = await self.execute_query(test_query, use_cache=False)

            # Get credit usage
            credit_summary = await self.get_credit_usage_summary()

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "connection_info": info[0] if info else {},
                "credit_usage": credit_summary,
                "redis_status": "connected" if self.redis_client else "disconnected",
                "warehouse_optimizer": "active",
                "initialized": self._initialized,
            }

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def close(self):
        """Clean up connections"""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("🔌 EnhancedSnowflakeAdapter connections closed")


# Singleton instance for use by CortexGateway
_adapter_instance: EnhancedSnowflakeAdapter | None = None


def get_adapter() -> EnhancedSnowflakeAdapter:
    """Get singleton adapter instance"""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = EnhancedSnowflakeAdapter()
    return _adapter_instance
