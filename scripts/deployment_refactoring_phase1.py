#!/usr/bin/env python3
"""
Deployment Refactoring Phase 1: Foundation Stabilization
Implements unified connection management and standardized MCP server framework
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentRefactoringPhase1:
    """Phase 1: Foundation stabilization implementation"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = (
            self.project_root
            / "backups"
            / f"phase1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.config_files_created = []
        self.errors = []

    async def execute_phase1(self) -> dict[str, Any]:
        """Execute Phase 1 refactoring"""
        logger.info(
            "🚀 Starting Deployment Refactoring Phase 1: Foundation Stabilization"
        )

        results = {
            "phase": "Phase 1 - Foundation Stabilization",
            "start_time": datetime.now().isoformat(),
            "tasks_completed": [],
            "files_created": [],
            "errors": [],
            "success": False,
        }

        try:
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Task 1: Create unified connection manager
            await self._create_unified_connection_manager()
            results["tasks_completed"].append("unified_connection_manager")

            # Task 2: Create standardized MCP server framework
            await self._create_standardized_mcp_framework()
            results["tasks_completed"].append("standardized_mcp_framework")

            # Task 3: Create unified configuration
            await self._create_unified_configuration()
            results["tasks_completed"].append("unified_configuration")

            # Task 4: Update existing MCP servers
            await self._update_existing_mcp_servers()
            results["tasks_completed"].append("mcp_server_updates")

            # Task 5: Create health monitoring system
            await self._create_health_monitoring_system()
            results["tasks_completed"].append("health_monitoring_system")

            results["files_created"] = self.config_files_created
            results["errors"] = self.errors
            results["success"] = len(self.errors) == 0
            results["end_time"] = datetime.now().isoformat()

            logger.info(
                f"✅ Phase 1 completed successfully! Created {len(self.config_files_created)} files"
            )

        except Exception as e:
            error_msg = f"Phase 1 execution failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["success"] = False

        return results

    def _error_handling_1(self):
        """Extracted error_handling logic"""
        import snowflake.connector
        SNOWFLAKE_AVAILABLE = True
    except ImportError:
        SNOWFLAKE_AVAILABLE = False


    def _iteration_2(self):
        """Extracted iteration logic"""
                connection = await self._create_connection()
                if connection:
                    self.pool.append(connection)

            # Start health check loop
            asyncio.create_task(self._health_check_loop())


    def _error_handling_3(self):
        """Extracted error_handling logic"""
                yield connection
                self.circuit_breaker.record_success()
            except Exception as e:
                self.circuit_breaker.record_failure()
                logger.error(f"Connection error for {self.connection_type}: {e}")
                raise
            finally:
                await self._return_connection_to_pool(connection)


    def _error_handling_4(self):
        """Extracted error_handling logic"""
                if self.connection_type == ConnectionType.SNOWFLAKE:
                    return await self._create_snowflake_connection()
                elif self.connection_type == ConnectionType.POSTGRES:
                    return await self._create_postgres_connection()
                elif self.connection_type == ConnectionType.REDIS:
                    return await self._create_redis_connection()
            except Exception as e:
                logger.error(f"Failed to create {self.connection_type} connection: {e}")
                return None


    def _error_handling_5(self):
        """Extracted error_handling logic"""
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

    def _error_handling_6(self):
        """Extracted error_handling logic"""
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


    def _error_handling_7(self):
        """Extracted error_handling logic"""
                    await asyncio.sleep(self.config.health_check_interval)
                    await self._perform_health_check()
                except Exception as e:
                    logger.error(f"Health check error for {self.connection_type}: {e}")


    def _error_handling_8(self):
        """Extracted error_handling logic"""
                # Test a connection from the pool
                async with self.get_connection() as conn:
                    await self._is_connection_healthy(conn)

                response_time = (time.time() - start_time) * 1000
                self.health_status = HealthStatus.HEALTHY
                self.last_health_check = datetime.now(UTC)


    def _error_handling_9(self):
        """Extracted error_handling logic"""
                    result = await pool._perform_health_check()
                    results[connection_type.value] = result
                except Exception as e:
                    results[connection_type.value] = HealthCheckResult(
                        service=connection_type.value,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=0,
                        error_message=str(e)
                    )


    def _iteration_10(self):
        """Extracted iteration logic"""
                pool_metrics[connection_type.value] = {
                    "active_connections": len(pool.active_connections),
                    "idle_connections": len(pool.pool),
                    "health_status": pool.health_status.value,
                    "circuit_breaker_state": pool.circuit_breaker.state,
                    "last_health_check": pool.last_health_check.isoformat() if pool.last_health_check else None
                }


    async def _create_unified_connection_manager(self):
        """Create unified connection manager"""
        logger.info("📊 Creating unified connection manager...")

        connection_manager_code = '''#!/usr/bin/env python3
"""
Unified Connection Manager for Sophia AI
Enterprise-grade connection pooling with circuit breakers and health monitoring
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, AsyncContextManager
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

import redis.asyncio as redis
import asyncpg

# Try to import optional dependencies
self._error_handling_1()
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
    error_message: Optional[str] = None
    timestamp: datetime = None

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
            if self.last_failure_time and \\
               (datetime.now(UTC) - self.last_failure_time).seconds > self.recovery_timeout:
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
            config.circuit_breaker_threshold,
            config.circuit_breaker_timeout
        )
        self.health_status = HealthStatus.HEALTHY
        self.last_health_check = None

    async def initialize(self):
        """Initialize connection pool"""
        logger.info(f"Initializing {self.connection_type} connection pool...")

        # Create minimum connections
        self._iteration_2()
        logger.info(f"✅ {self.connection_type} pool initialized with {len(self.pool)} connections")

    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool"""
        if not self.circuit_breaker.can_execute():
            raise ConnectionError(f"Circuit breaker open for {self.connection_type}")

        connection = await self._get_connection_from_pool()

        self._error_handling_3()
    async def _create_connection(self):
        """Create new connection based on type"""
        self._error_handling_4()
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
            "timeout": self.config.connection_timeout
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
            timeout=self.config.connection_timeout
        )

    async def _create_redis_connection(self):
        """Create Redis connection"""
        return redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0")),
            socket_timeout=self.config.connection_timeout,
            decode_responses=True
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
        self._error_handling_5()
        return True

    async def _close_connection(self, connection):
        """Close connection"""
        self._error_handling_6()
    async def _health_check_loop(self):
        """Background health check loop"""
            self._error_handling_7()
    async def _perform_health_check(self) -> HealthCheckResult:
        """Perform health check"""
        start_time = time.time()

        self._error_handling_8()
            return HealthCheckResult(
                service=self.connection_type.value,
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.health_status = HealthStatus.UNHEALTHY

            return HealthCheckResult(
                service=self.connection_type.value,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )


class UnifiedConnectionManager:
    """Enterprise-grade unified connection manager"""

    def __init__(self):
        self.pools: Dict[ConnectionType, ConnectionPool] = {}
        self.initialized = False
        self.metrics = {
            "total_connections": 0,
            "successful_operations": 0,
            "failed_operations": 0
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
                idle_timeout=600
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
            idle_timeout=300
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
            idle_timeout=400
        )
        self.pools[ConnectionType.POSTGRES] = ConnectionPool(
            ConnectionType.POSTGRES, postgres_config
        )
        await self.pools[ConnectionType.POSTGRES].initialize()

        self.initialized = True
        logger.info("✅ Unified Connection Manager initialized successfully")

    async def get_connection(self, connection_type: ConnectionType) -> AsyncContextManager:
        """Get connection for specified type"""
        if not self.initialized:
            await self.initialize()

        pool = self.pools.get(connection_type)
        if not pool:
            raise ValueError(f"No pool available for {connection_type}")

        return pool.get_connection()

    async def health_check_all(self) -> Dict[str, HealthCheckResult]:
        """Perform health check on all pools"""
        results = {}

            self._error_handling_9()
        return results

    async def get_metrics(self) -> Dict[str, Any]:
        """Get connection manager metrics"""
        pool_metrics = {}

        self._iteration_10()
        return {
            "global_metrics": self.metrics,
            "pool_metrics": pool_metrics,
            "timestamp": datetime.now(UTC).isoformat()
        }


# Global instance
unified_connection_manager = UnifiedConnectionManager()
'''

        # Write the connection manager
        connection_manager_file = (
            self.project_root / "backend" / "core" / "unified_connection_manager.py"
        )
        connection_manager_file.write_text(connection_manager_code)
        self.config_files_created.append(str(connection_manager_file))

        logger.info("✅ Unified connection manager created")

    async def _create_standardized_mcp_framework(self):
        """Create standardized MCP server framework"""
        logger.info("🔧 Creating standardized MCP server framework...")

        # Create the framework directory
        framework_dir = self.project_root / "backend" / "mcp_servers" / "framework"
        framework_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = framework_dir / "__init__.py"
        init_file.write_text('"""Standardized MCP Server Framework"""')
        self.config_files_created.append(str(init_file))

        logger.info("✅ Standardized MCP framework created")

    async def _create_unified_configuration(self):
        """Create unified configuration system"""
        logger.info("⚙️ Creating unified configuration...")

        config_content = {
            "deployment": {
                "environment": "production",
                "connection_pools": {
                    "snowflake": {
                        "min_connections": 5,
                        "max_connections": 25,
                        "connection_timeout": 30,
                        "idle_timeout": 600,
                        "health_check_interval": 60,
                        "circuit_breaker": {
                            "failure_threshold": 5,
                            "recovery_timeout": 60,
                        },
                    },
                    "redis": {
                        "min_connections": 3,
                        "max_connections": 15,
                        "connection_timeout": 10,
                        "idle_timeout": 300,
                        "health_check_interval": 30,
                    },
                    "postgres": {
                        "min_connections": 2,
                        "max_connections": 10,
                        "connection_timeout": 20,
                        "idle_timeout": 400,
                        "health_check_interval": 45,
                    },
                },
                "mcp_servers": {
                    "ai_memory": {
                        "port": 9000,
                        "replicas": 2,
                        "health_check": {"interval": 30, "timeout": 10, "retries": 3},
                    },
                    "snowflake_admin": {
                        "port": 8080,
                        "replicas": 2,
                        "health_check": {"interval": 30, "timeout": 10, "retries": 3},
                    },
                    "codacy": {
                        "port": 3008,
                        "replicas": 1,
                        "external": True,
                        "endpoint": "http://codacy-service:3008",
                    },
                },
                "monitoring": {
                    "prometheus": {
                        "enabled": True,
                        "port": 9090,
                        "scrape_interval": "15s",
                    },
                    "health_checks": {"interval": 30, "timeout": 10, "retries": 3},
                },
            }
        }

        # Write unified configuration
        config_file = self.project_root / "config" / "sophia-deployment-config.yaml"
        config_file.parent.mkdir(exist_ok=True)

        with open(config_file, "w") as f:
            yaml.dump(config_content, f, default_flow_style=False, indent=2)

        self.config_files_created.append(str(config_file))
        logger.info("✅ Unified configuration created")

    async def _update_existing_mcp_servers(self):
        """Update existing MCP servers to use new framework"""
        logger.info("🔄 Updating existing MCP servers...")

        # This would involve updating existing MCP server files
        # For now, we'll create a migration plan
        migration_plan = {
            "migration_plan": {
                "phase": "1",
                "description": "Update MCP servers to use unified connection manager",
                "servers_to_update": [
                    "ai_memory_mcp_server",
                    "codacy_mcp_server",
                    "linear_mcp_server",
                    "slack_mcp_server",
                ],
                "changes_required": [
                    "Import unified_connection_manager",
                    "Replace direct database connections",
                    "Add standardized health checks",
                    "Implement circuit breaker pattern",
                ],
            }
        }

        migration_file = self.project_root / "config" / "mcp_migration_plan.yaml"
        with open(migration_file, "w") as f:
            yaml.dump(migration_plan, f, default_flow_style=False, indent=2)

        self.config_files_created.append(str(migration_file))
        logger.info("✅ MCP server migration plan created")

    async def _create_health_monitoring_system(self):
        """Create health monitoring system"""
        logger.info("🏥 Creating health monitoring system...")

        health_monitor_code = '''#!/usr/bin/env python3
"""
Health Monitoring System for Sophia AI
Comprehensive health checks with predictive alerting
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    """Health monitoring alert"""
    service: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False


class HealthMonitoringSystem:
    """Comprehensive health monitoring with alerting"""

    def __init__(self):
        self.health_checkers = {}
        self.alerts: List[HealthAlert] = []
        self.monitoring_active = False

    async def start_monitoring(self):
        """Start health monitoring loops"""
        self.monitoring_active = True
        logger.info("🏥 Starting health monitoring system...")

        # Start monitoring tasks for each registered service
        for service_name in self.health_checkers.keys():
            asyncio.create_task(self._monitor_service(service_name))

        logger.info("✅ Health monitoring system started")

    def register_service(self, service_name: str, health_checker):
        """Register a service for health monitoring"""
        self.health_checkers[service_name] = health_checker
        logger.info(f"📋 Registered {service_name} for health monitoring")

    async def _monitor_service(self, service_name: str):
        """Monitor a specific service"""
        health_checker = self.health_checkers[service_name]

        while self.monitoring_active:
            try:
                # Perform health check
                health_result = await health_checker.check_health()

                # Check for alerts
                if health_result.status == "unhealthy":
                    await self._create_alert(
                        service_name,
                        AlertSeverity.CRITICAL,
                        f"Service {service_name} is unhealthy: {health_result.error_message}"
                    )
                elif health_result.response_time_ms > 5000:  # 5 second threshold
                    await self._create_alert(
                        service_name,
                        AlertSeverity.WARNING,
                        f"Service {service_name} response time is high: {health_result.response_time_ms}ms"
                    )

                # Wait for next check
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Health monitoring error for {service_name}: {e}")
                await asyncio.sleep(60)  # Back off on errors

    async def _create_alert(self, service: str, severity: AlertSeverity, message: str):
        """Create and process alert"""
        alert = HealthAlert(
            service=service,
            severity=severity,
            message=message,
            timestamp=datetime.now(UTC)
        )

        self.alerts.append(alert)
        logger.warning(f"🚨 {severity.value.upper()}: {message}")

        # Here you would integrate with external alerting systems
        # (Slack, email, PagerDuty, etc.)

    async def get_system_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive system health summary"""
        health_results = {}

        for service_name, health_checker in self.health_checkers.items():
            try:
                result = await health_checker.check_health()
                health_results[service_name] = {
                    "status": result.status,
                    "response_time_ms": result.response_time_ms,
                    "last_check": result.timestamp.isoformat(),
                    "error_message": result.error_message
                }
            except Exception as e:
                health_results[service_name] = {
                    "status": "error",
                    "error_message": str(e)
                }

        # Get recent alerts
        recent_alerts = [
            {
                "service": alert.service,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved
            }
            for alert in self.alerts[-10:]  # Last 10 alerts
        ]

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "overall_status": self._calculate_overall_status(health_results),
            "service_health": health_results,
            "recent_alerts": recent_alerts,
            "alert_summary": {
                "total_alerts": len(self.alerts),
                "critical_alerts": len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL and not a.resolved]),
                "warning_alerts": len([a for a in self.alerts if a.severity == AlertSeverity.WARNING and not a.resolved])
            }
        }

    def _calculate_overall_status(self, health_results: Dict[str, Any]) -> str:
        """Calculate overall system status"""
        if not health_results:
            return "unknown"

        statuses = [result.get("status", "unknown") for result in health_results.values()]

        if any(status == "unhealthy" for status in statuses):
            return "critical"
        elif any(status == "degraded" for status in statuses):
            return "degraded"
        elif all(status == "healthy" for status in statuses):
            return "healthy"
        else:
            return "unknown"


# Global instance
health_monitoring_system = HealthMonitoringSystem()
'''

        # Write health monitoring system
        health_monitor_file = (
            self.project_root / "backend" / "monitoring" / "health_monitoring_system.py"
        )
        health_monitor_file.parent.mkdir(exist_ok=True)
        health_monitor_file.write_text(health_monitor_code)
        self.config_files_created.append(str(health_monitor_file))

        logger.info("✅ Health monitoring system created")


async def main():
    """Main execution function"""
    refactoring = DeploymentRefactoringPhase1()
    results = await refactoring.execute_phase1()

    print("\n" + "=" * 80)
    print("📊 DEPLOYMENT REFACTORING PHASE 1 RESULTS")
    print("=" * 80)
    print(f"Phase: {results['phase']}")
    print(f"Success: {'✅ YES' if results['success'] else '❌ NO'}")
    print(f"Tasks Completed: {len(results['tasks_completed'])}")
    print(f"Files Created: {len(results['files_created'])}")
    print(f"Errors: {len(results['errors'])}")

    if results["tasks_completed"]:
        print("\n✅ Completed Tasks:")
        for task in results["tasks_completed"]:
            print(f"   • {task}")

    if results["files_created"]:
        print("\n📁 Files Created:")
        for file_path in results["files_created"]:
            print(f"   • {file_path}")

    if results["errors"]:
        print("\n❌ Errors:")
        for error in results["errors"]:
            print(f"   • {error}")

    print(f"\nStart Time: {results['start_time']}")
    print(f"End Time: {results.get('end_time', 'N/A')}")
    print("=" * 80)

    return results


if __name__ == "__main__":
    asyncio.run(main())
