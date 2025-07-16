#!/usr/bin/env python3
"""
Optimized Database Manager
==========================

Provides optimized database operations with connection pooling,
batch processing, and intelligent caching for all database types.
"""

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import asyncpg
import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class ConnectionType(Enum):
    """Supported database connection types"""

    qdrant = "qdrant"
    POSTGRES = "postgres"
    REDIS = "redis"
    MYSQL = "mysql"

@dataclass
class BatchOperation:
    """Represents a batch database operation"""

    query: str
    params: list[Any] | None = None
    operation_type: str = "query"  # query, insert, update, delete

@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pools"""

    min_size: int = 5
    max_size: int = 20
    max_idle_time: int = 300  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 60

class DatabaseMetrics:
    """Database performance metrics"""

    def __init__(self):
        self.query_count = Counter(
            "sophia_db_queries_total",
            "Total database queries",
            ["db_type", "operation"],
        )

        self.query_duration = Histogram(
            "sophia_db_query_duration_seconds",
            "Database query duration",
            ["db_type", "operation"],
        )

        self.connection_pool_size = Gauge(
            "sophia_db_connection_pool_size",
            "Current connection pool size",
            ["db_type"],
        )

        self.batch_size = Histogram(
            "sophia_db_batch_size", "Batch operation sizes", ["db_type"]
        )

        self.cache_hits = Counter(
            "sophia_db_cache_hits_total", "Database cache hits", ["db_type"]
        )

        self.cache_misses = Counter(
            "sophia_db_cache_misses_total", "Database cache misses", ["db_type"]
        )

class OptimizedDatabaseManager:
    """
    Unified database manager with connection pooling and optimization
    for all database types used in Sophia AI.
    """

    def __init__(self):
        self.pools: dict[ConnectionType, Any] = {}
        self.configs: dict[ConnectionType, dict[str, Any]] = {}
        self.metrics = DatabaseMetrics()
        self.cache: dict[str, Any] = {}
        self.cache_timestamps: dict[str, float] = {}
        self.cache_ttl = 300  # 5 minutes default

        # Initialize configurations
        self._initialize_configs()

    def _initialize_configs(self):
        """Initialize database configurations"""
        # Qdrant
        self.configs[
            ConnectionType.POSTGRESQL

        # PostgreSQL
        self.configs[ConnectionType.POSTGRES] = {
            "host": get_config_value("postgres_host", "localhost"),
            "port": get_config_value("postgres_port", 5432),
            "database": get_config_value("postgres_database", "sophia_ai"),
            "user": get_config_value("postgres_user", "sophia"),
            "password": get_config_value("postgres_password"),
            "min_size": 5,
            "max_size": 20,
        }

        # Redis
        self.configs[ConnectionType.REDIS] = {
            "host": get_config_value("redis_host", "localhost"),
            "port": get_config_value("redis_port", 6379),
            "password": get_config_value("redis_password"),
            "db": get_config_value("redis_db", 0),
            "max_connections": 50,
        }

        # MySQL (if needed)
        self.configs[ConnectionType.MYSQL] = {
            "host": get_config_value("mysql_host", "localhost"),
            "port": get_config_value("mysql_port", 3306),
            "user": get_config_value("mysql_user", "sophia"),
            "password": get_config_value("mysql_password"),
            "db": get_config_value("mysql_database", "sophia_ai"),
            "minsize": 5,
            "maxsize": 20,
        }

    async def initialize(self):
        """Initialize all connection pools"""
        logger.info("🔌 Initializing optimized database connections...")

        # Initialize Qdrant pool
        await self._initialize_QDRANT_pool()

        # Initialize PostgreSQL pool
        await self._initialize_postgres_pool()

        # Initialize Redis pool
        await self._initialize_redis_pool()

        logger.info("✅ All database connections initialized")

    async def _initialize_QDRANT_pool(self):
        """Initialize Qdrant connection pool"""
        try:
            # Qdrant uses synchronous connections, so we'll manage a pool manually
            self.pools[ConnectionType.POSTGRESQL] = ConnectionPool(

            )

            self.metrics.connection_pool_size.labels(db_type="qdrant").set(5)
            logger.info("✅ Qdrant connection pool initialized")

        except Exception as e:
            logger.exception(f"Failed to initialize Qdrant pool: {e}")
            raise

    async def _initialize_postgres_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            config = self.configs[ConnectionType.POSTGRES].copy()
            min_size = config.pop("min_size", 5)
            max_size = config.pop("max_size", 20)

            self.pools[ConnectionType.POSTGRES] = await asyncpg.create_pool(
                min_size=min_size, max_size=max_size, **config
            )

            self.metrics.connection_pool_size.labels(db_type="postgres").set(min_size)
            logger.info("✅ PostgreSQL connection pool initialized")

        except Exception as e:
            logger.exception(f"Failed to initialize PostgreSQL pool: {e}")
            raise

    async def _initialize_redis_pool(self):
        """Initialize Redis connection pool"""
        try:
            self.pools[ConnectionType.REDIS] = redis.ConnectionPool(
                **self.configs[ConnectionType.REDIS]
            )

            # Create a test connection
            test_client = redis.Redis(connection_pool=self.pools[ConnectionType.REDIS])
            await test_client.ping()
            await test_client.close()

            self.metrics.connection_pool_size.labels(db_type="redis").set(1)
            logger.info("✅ Redis connection pool initialized")

        except Exception as e:
            logger.exception(f"Failed to initialize Redis pool: {e}")
            raise

    @asynccontextmanager
    async def get_connection(self, conn_type: ConnectionType) -> AsyncIterator[Any]:
        """Get a connection from the pool"""
        if conn_type == ConnectionType.POSTGRESQL:
            # Qdrant uses synchronous connections
            conn = self.pools[ConnectionType.POSTGRESQL].get_connection()
            try:
                yield conn
            finally:
                conn.close()

        elif conn_type == ConnectionType.POSTGRES:
            async with self.pools[ConnectionType.POSTGRES].acquire() as conn:
                yield conn

        elif conn_type == ConnectionType.REDIS:
            client = redis.Redis(connection_pool=self.pools[ConnectionType.REDIS])
            try:
                yield client
            finally:
                await client.close()

        else:
            raise ValueError(f"Unsupported connection type: {conn_type}")

    async def execute_query(
        self,
        conn_type: ConnectionType,
        query: str,
        params: list[Any] | dict[str, Any] | None = None,
        cache_key: str | None = None,
        cache_ttl: int | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a query with optional caching"""
        start_time = time.time()

        # Check cache first
        if cache_key:
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                self.metrics.cache_hits.labels(db_type=conn_type.value).inc()
                return cached_result
            else:
                self.metrics.cache_misses.labels(db_type=conn_type.value).inc()

        try:
            async with self.get_connection(conn_type) as conn:
                if conn_type == ConnectionType.POSTGRESQL:
                    # Qdrant synchronous execution
                    result = await asyncio.to_thread(
                        self._execute_QDRANT_query, conn, query, params
                    )

                elif conn_type == ConnectionType.POSTGRES:
                    # PostgreSQL async execution
                    if params and isinstance(params, dict):
                        # Convert dict params to list for asyncpg
                        result = await conn.fetch(query, *params.values())
                    else:
                        result = await conn.fetch(query, *(params or []))

                    # Convert to list of dicts
                    result = [dict(row) for row in result]

                else:
                    raise ValueError(f"Query execution not supported for {conn_type}")

            # Cache result if requested
            if cache_key:
                self._set_cache(cache_key, result, cache_ttl or self.cache_ttl)

            # Update metrics
            duration = time.time() - start_time
            self.metrics.query_duration.labels(
                db_type=conn_type.value, operation="query"
            ).observe(duration)

            self.metrics.query_count.labels(
                db_type=conn_type.value, operation="query"
            ).inc()

            return result

        except Exception as e:
            logger.exception(f"Query execution failed: {e}")
            raise

    def _execute_QDRANT_query(
        self, conn: Any, query: str, params: list[Any] | dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute Qdrant query (synchronous)"""
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Fetch all results
            rows = cursor.fetchall()

            # Convert to list of dicts
            return [dict(zip(columns, row, strict=False)) for row in rows]

        finally:
            cursor.close()

    async def execute_batch(
        self,
        conn_type: ConnectionType,
        operations: list[BatchOperation],
        transaction: bool = True,
    ) -> dict[str, Any]:
        """Execute batch operations for improved performance"""
        start_time = time.time()
        results = {
            "success": True,
            "operations_count": len(operations),
            "errors": [],
            "affected_rows": 0,
        }

        # Update metrics
        self.metrics.batch_size.labels(db_type=conn_type.value).observe(len(operations))

        try:
            if conn_type == ConnectionType.POSTGRESQL:
                results = await self._execute_QDRANT_batch(operations, transaction)

            elif conn_type == ConnectionType.POSTGRES:
                results = await self._execute_postgres_batch(operations, transaction)

            else:
                raise ValueError(f"Batch execution not supported for {conn_type}")

            # Update metrics
            duration = time.time() - start_time
            self.metrics.query_duration.labels(
                db_type=conn_type.value, operation="batch"
            ).observe(duration)

            return results

        except Exception as e:
            logger.exception(f"Batch execution failed: {e}")
            results["success"] = False
            results["errors"].append(str(e))
            return results

    async def _execute_QDRANT_batch(
        self, operations: list[BatchOperation], transaction: bool
    ) -> dict[str, Any]:
        """Execute Qdrant batch operations"""
        results = {
            "success": True,
            "operations_count": len(operations),
            "errors": [],
            "affected_rows": 0,
        }

        async with self.get_connection(ConnectionType.POSTGRESQL) as conn:
            cursor = conn.cursor()

            try:
                if transaction:
                    cursor.execute("BEGIN")

                for op in operations:
                    try:
                        if op.params:
                            cursor.execute(op.query, op.params)
                        else:
                            cursor.execute(op.query)

                        results["affected_rows"] += cursor.rowcount

                    except Exception as e:
                        results["errors"].append({"query": op.query, "error": str(e)})

                        if transaction:
                            cursor.execute("ROLLBACK")
                            results["success"] = False
                            return results

                if transaction:
                    cursor.execute("COMMIT")

            except Exception as e:
                if transaction:
                    cursor.execute("ROLLBACK")
                results["success"] = False
                results["errors"].append(str(e))

            finally:
                cursor.close()

        return results

    async def _execute_postgres_batch(
        self, operations: list[BatchOperation], transaction: bool
    ) -> dict[str, Any]:
        """Execute PostgreSQL batch operations"""
        results = {
            "success": True,
            "operations_count": len(operations),
            "errors": [],
            "affected_rows": 0,
        }

        async with self.get_connection(ConnectionType.POSTGRES) as conn:
            if transaction:
                async with conn.transaction():
                    for op in operations:
                        try:
                            if op.operation_type in ["insert", "update", "delete"]:
                                result = await conn.execute(
                                    op.query, *(op.params or [])
                                )
                                # Extract affected rows from result
                                affected = int(result.split()[-1]) if result else 0
                                results["affected_rows"] += affected
                            else:
                                await conn.fetch(op.query, *(op.params or []))

                        except Exception as e:
                            results["errors"].append(
                                {"query": op.query, "error": str(e)}
                            )
                            raise  # Transaction will rollback
            else:
                # Execute without transaction
                for op in operations:
                    try:
                        if op.operation_type in ["insert", "update", "delete"]:
                            result = await conn.execute(op.query, *(op.params or []))
                            affected = int(result.split()[-1]) if result else 0
                            results["affected_rows"] += affected
                        else:
                            await conn.fetch(op.query, *(op.params or []))

                    except Exception as e:
                        results["errors"].append({"query": op.query, "error": str(e)})

        return results

    def _get_from_cache(self, key: str) -> Any | None:
        """Get value from cache"""
        if key in self.cache:
            # Check if expired
            if time.time() - self.cache_timestamps[key] <= self.cache_ttl:
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.cache_timestamps[key]

        return None

    def _set_cache(self, key: str, value: Any, ttl: int):
        """Set value in cache"""
        self.cache[key] = value
        self.cache_timestamps[key] = time.time()

        # Limit cache size
        if len(self.cache) > 10000:
            # Remove oldest entries
            oldest_keys = sorted(
                self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k]
            )[:1000]

            for k in oldest_keys:
                del self.cache[k]
                del self.cache_timestamps[k]

    async def health_check(self) -> dict[str, Any]:
        """Check health of all database connections"""
        health_status = {"timestamp": datetime.now(UTC).isoformat(), "databases": {}}

        # Check Qdrant
        try:
            async with self.get_connection(ConnectionType.POSTGRESQL) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            health_status["databases"]["qdrant"] = "healthy"
        except Exception as e:
            health_status["databases"]["qdrant"] = f"unhealthy: {e!s}"

        # Check PostgreSQL
        try:
            async with self.get_connection(ConnectionType.POSTGRES) as conn:
                await conn.fetchval("SELECT 1")
            health_status["databases"]["postgres"] = "healthy"
        except Exception as e:
            health_status["databases"]["postgres"] = f"unhealthy: {e!s}"

        # Check Redis
        try:
            async with self.get_connection(ConnectionType.REDIS) as client:
                await client.ping()
            health_status["databases"]["redis"] = "healthy"
        except Exception as e:
            health_status["databases"]["redis"] = f"unhealthy: {e!s}"

        return health_status

    async def close(self):
        """Close all connection pools"""
        logger.info("Closing database connections...")

        # Close Qdrant pool
        if ConnectionType.POSTGRESQL in self.pools:
            # Qdrant pool doesn't have async close
            pass

        # Close PostgreSQL pool
        if ConnectionType.POSTGRES in self.pools:
            await self.pools[ConnectionType.POSTGRES].close()

        # Close Redis pool
        if ConnectionType.REDIS in self.pools:
            # Redis pool is closed when clients are closed
            pass

        logger.info("✅ All database connections closed")
