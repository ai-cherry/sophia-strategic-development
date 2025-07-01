#!/usr/bin/env python3
"""
Unified Connection Manager for Sophia AI
Enterprise-grade connection pooling with circuit breakers and health monitoring
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, AsyncContextManager

import asyncpg
import redis.asyncio as redis

# Define UTC for compatibility
UTC = UTC

# Try to import optional dependencies
try:
    import snowflake.connector

    from backend.core.auto_esc_config import get_config_value
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    def get_config_value(key):
        return os.getenv(key.upper())

logger = logging.getLogger(__name__)


class ConnectionType(str, Enum):
    """Supported connection types"""

    SNOWFLAKE = "snowflake"
    POSTGRES = "postgres"
    REDIS = "redis"


class HealthStatus(str, Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pools"""

    min_connections: int = 2
    max_connections: int = 10
    connection_timeout: int = 30
    idle_timeout: int = 300
    health_check_interval: int = 60
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


@dataclass
class HealthCheckResult:
    """Health check result"""

    service: str
    status: HealthStatus
    response_time_ms: float
    error_message: str | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)


class CircuitBreaker:
    """Circuit breaker for connection failure handling"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if (
                self.last_failure_time
                and (datetime.now(UTC) - self.last_failure_time).seconds
                > self.recovery_timeout
            ):
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(UTC)

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class ConnectionPool:
    """High-performance connection pool"""

    def __init__(self, connection_type: ConnectionType, config: ConnectionPoolConfig):
        self.connection_type = connection_type
        self.config = config
        self.pool = []
        self.active_connections = set()
        self.pool_lock = asyncio.Lock()
        self.circuit_breaker = CircuitBreaker(
            config.circuit_breaker_threshold, config.circuit_breaker_timeout
        )
        self.health_status = HealthStatus.HEALTHY
        self.last_health_check = None

    async def initialize(self):
        """Initialize connection pool"""
        logger.info(f"Initializing {self.connection_type} connection pool...")

        # Create minimum connections
        for _ in range(self.config.min_connections):
            connection = await self._create_connection()
            if connection:
                self.pool.append(connection)

        # Start health check loop
        asyncio.create_task(self._health_check_loop())

        logger.info(
            f"✅ {self.connection_type} pool initialized with {len(self.pool)} connections"
        )

    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool"""
        if not self.circuit_breaker.can_execute():
            raise ConnectionError(f"Circuit breaker open for {self.connection_type}")

        connection = await self._get_connection_from_pool()

        try:
            yield connection
            self.circuit_breaker.record_success()
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Connection error for {self.connection_type}: {e}")
            raise
        finally:
            await self._return_connection_to_pool(connection)

    async def _create_connection(self):
        """Create new connection based on type"""
        try:
            if self.connection_type == ConnectionType.SNOWFLAKE:
                return await self._create_snowflake_connection()
            elif self.connection_type == ConnectionType.POSTGRES:
                return await self._create_postgres_connection()
            elif self.connection_type == ConnectionType.REDIS:
                return await self._create_redis_connection()
        except Exception as e:
            logger.error(f"Failed to create {self.connection_type} connection: {e}")
            return None

    async def _create_snowflake_connection(self):
        """Create Snowflake connection"""
        if not SNOWFLAKE_AVAILABLE:
            raise ImportError("Snowflake connector not available")

        # Get configuration from environment or config
        config = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": get_config_value("snowflake_password"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
            "role": os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"),
            "timeout": self.config.connection_timeout,
        }

        def _sync_connect():
            return snowflake.connector.connect(**config)

        return await asyncio.to_thread(_sync_connect)

    async def _create_postgres_connection(self):
        """Create PostgreSQL connection"""
        return await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DATABASE"),
            timeout=self.config.connection_timeout,
        )

    async def _create_redis_connection(self):
        """Create Redis connection"""
        return redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0")),
            socket_timeout=self.config.connection_timeout,
            decode_responses=True,
        )

    async def _get_connection_from_pool(self):
        """Get connection from pool or create new one"""
        async with self.pool_lock:
            if self.pool:
                connection = self.pool.pop()
                self.active_connections.add(connection)
                return connection

            if len(self.active_connections) < self.config.max_connections:
                connection = await self._create_connection()
                if connection:
                    self.active_connections.add(connection)
                    return connection

            # Pool exhausted, wait and retry
            await asyncio.sleep(0.1)
            return await self._get_connection_from_pool()

    async def _return_connection_to_pool(self, connection):
        """Return connection to pool"""
        async with self.pool_lock:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

                if await self._is_connection_healthy(connection):
                    self.pool.append(connection)
                else:
                    await self._close_connection(connection)

    async def _is_connection_healthy(self, connection) -> bool:
        """Check if connection is healthy"""
        try:
            if self.connection_type == ConnectionType.SNOWFLAKE:

                def _sync_health_check():
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                    return True

                return await asyncio.to_thread(_sync_health_check)
            elif self.connection_type == ConnectionType.POSTGRES:
                await connection.execute("SELECT 1")
                return True
            elif self.connection_type == ConnectionType.REDIS:
                await connection.ping()
                return True
        except Exception:
            return False
        return True

    async def _close_connection(self, connection):
        """Close connection"""
        try:
            if self.connection_type == ConnectionType.SNOWFLAKE:

                def _sync_close():
                    connection.close()

                await asyncio.to_thread(_sync_close)
            elif self.connection_type == ConnectionType.POSTGRES:
                await connection.close()
            elif self.connection_type == ConnectionType.REDIS:
                await connection.close()
        except Exception as e:
            logger.error(f"Error closing {self.connection_type} connection: {e}")

    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
            except Exception as e:
                logger.error(f"Health check error for {self.connection_type}: {e}")

    async def _perform_health_check(self) -> HealthCheckResult:
        """Perform health check"""
        start_time = time.time()

        try:
            # Test a connection from the pool
            async with self.get_connection() as conn:
                await self._is_connection_healthy(conn)

            response_time = (time.time() - start_time) * 1000
            self.health_status = HealthStatus.HEALTHY
            self.last_health_check = datetime.now(UTC)

            return HealthCheckResult(
                service=self.connection_type.value,
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.health_status = HealthStatus.UNHEALTHY

            return HealthCheckResult(
                service=self.connection_type.value,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e),
            )


class UnifiedConnectionManager:
    """Enterprise-grade unified connection manager"""

    def __init__(self):
        self.pools: dict[ConnectionType, ConnectionPool] = {}
        self.initialized = False
        self.metrics = {
            "total_connections": 0,
            "successful_operations": 0,
            "failed_operations": 0,
        }

    async def initialize(self):
        """Initialize all connection pools"""
        if self.initialized:
            return

        logger.info("🚀 Initializing Unified Connection Manager...")

        # Initialize Snowflake pool
        if SNOWFLAKE_AVAILABLE:
            snowflake_config = ConnectionPoolConfig(
                min_connections=5,
                max_connections=25,
                connection_timeout=30,
                idle_timeout=600,
            )
            self.pools[ConnectionType.SNOWFLAKE] = ConnectionPool(
                ConnectionType.SNOWFLAKE, snowflake_config
            )
            await self.pools[ConnectionType.SNOWFLAKE].initialize()

        # Initialize Redis pool
        redis_config = ConnectionPoolConfig(
            min_connections=3,
            max_connections=15,
            connection_timeout=10,
            idle_timeout=300,
        )
        self.pools[ConnectionType.REDIS] = ConnectionPool(
            ConnectionType.REDIS, redis_config
        )
        await self.pools[ConnectionType.REDIS].initialize()

        # Initialize PostgreSQL pool
        postgres_config = ConnectionPoolConfig(
            min_connections=2,
            max_connections=10,
            connection_timeout=20,
            idle_timeout=400,
        )
        self.pools[ConnectionType.POSTGRES] = ConnectionPool(
            ConnectionType.POSTGRES, postgres_config
        )
        await self.pools[ConnectionType.POSTGRES].initialize()

        self.initialized = True
        logger.info("✅ Unified Connection Manager initialized successfully")

    async def get_connection(
        self, connection_type: ConnectionType
    ) -> AsyncContextManager:
        """Get connection for specified type"""
        if not self.initialized:
            await self.initialize()

        pool = self.pools.get(connection_type)
        if not pool:
            raise ValueError(f"No pool available for {connection_type}")

        return pool.get_connection()

    async def health_check_all(self) -> dict[str, HealthCheckResult]:
        """Perform health check on all pools"""
        results = {}

        for connection_type, pool in self.pools.items():
            try:
                result = await pool._perform_health_check()
                results[connection_type.value] = result
            except Exception as e:
                results[connection_type.value] = HealthCheckResult(
                    service=connection_type.value,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=0,
                    error_message=str(e),
                )

        return results

    async def get_metrics(self) -> dict[str, Any]:
        """Get connection manager metrics"""
        pool_metrics = {}

        for connection_type, pool in self.pools.items():
            pool_metrics[connection_type.value] = {
                "active_connections": len(pool.active_connections),
                "idle_connections": len(pool.pool),
                "health_status": pool.health_status.value,
                "circuit_breaker_state": pool.circuit_breaker.state,
                "last_health_check": (
                    pool.last_health_check.isoformat()
                    if pool.last_health_check
                    else None
                ),
            }

        return {
            "global_metrics": self.metrics,
            "pool_metrics": pool_metrics,
            "timestamp": datetime.now(UTC).isoformat(),
        }


# Global instance
unified_connection_manager = UnifiedConnectionManager()
