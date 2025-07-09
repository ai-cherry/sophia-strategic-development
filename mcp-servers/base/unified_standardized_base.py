"""
Sophia AI - Unified Standardized MCP Server Base Class
The definitive base class for all MCP servers in the Sophia AI ecosystem
Deployed on Lambda Labs Cloud Server: 104.171.202.117
"""

import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, Info

# Safe imports for optional dependencies
try:
    from anthropic_mcp_python_sdk import mcp_tool

    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False

    def mcp_tool(func):
        """Dummy decorator when MCP SDK not available"""
        return func


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Lambda Labs Configuration
LAMBDA_LABS_HOST = os.getenv("LAMBDA_LABS_HOST", "104.171.202.117")
ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "mcp_server_requests_total", "Total requests", ["server", "method"]
)
REQUEST_DURATION = Histogram(
    "mcp_server_request_duration_seconds", "Request duration", ["server", "method"]
)
ERROR_COUNT = Counter(
    "mcp_server_errors_total", "Total errors", ["server", "error_type"]
)
ACTIVE_CONNECTIONS = Gauge(
    "mcp_server_active_connections", "Active connections", ["server"]
)
HEALTH_STATUS = Gauge(
    "mcp_server_health_status", "Health status (1=healthy, 0=unhealthy)", ["server"]
)


class ServerTier(str, Enum):
    """Server tier classification"""

    PRIMARY = "PRIMARY"  # Mission-critical, 99.9% uptime
    SECONDARY = "SECONDARY"  # Important, 99% uptime
    TERTIARY = "TERTIARY"  # Optional, best effort


class ServerCapability(str, Enum):
    """Standard server capabilities"""

    ANALYTICS = "ANALYTICS"
    EMBEDDING = "EMBEDDING"
    SEARCH = "SEARCH"
    COMPLETION = "COMPLETION"
    CACHE = "CACHE"
    PUBSUB = "PUBSUB"
    MEMORY = "MEMORY"
    CRM = "CRM"
    WORKFLOW = "WORKFLOW"
    CODE_ANALYSIS = "CODE_ANALYSIS"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    COMMUNICATION = "COMMUNICATION"


@dataclass
class MCPServerConfig:
    """Unified configuration for MCP servers"""

    name: str
    port: int
    tier: ServerTier
    capabilities: list[ServerCapability]
    version: str = "2.0.0"
    health_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"
    lambda_labs_host: str = LAMBDA_LABS_HOST
    environment: str = ENVIRONMENT
    enable_cors: bool = True
    cors_origins: Optional[list[str]] = None
    max_connections: int = 100
    timeout_seconds: int = 30
    retry_attempts: int = 3

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class HealthCheckResult:
    """Standard health check result"""

    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    server_name: str
    version: str
    uptime_seconds: float
    checks: dict[str, dict[str, Any]]
    lambda_labs_connected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "server_name": self.server_name,
            "version": self.version,
            "uptime_seconds": self.uptime_seconds,
            "checks": self.checks,
            "lambda_labs_connected": self.lambda_labs_connected,
            "environment": ENVIRONMENT,
        }


class UnifiedStandardizedMCPServer(ABC):
    """
    The definitive base class for all MCP servers in Sophia AI.
    Provides comprehensive functionality with enterprise-grade features.
    """

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.start_time = time.time()
        self.app = FastAPI(
            title=f"{config.name} MCP Server",
            version=config.version,
            docs_url="/docs",
            redoc_url="/redoc",
        )
        self._setup_middleware()
        self._setup_routes()
        self._active_connections: set[str] = set()
        self._initialized = False

        # Update Prometheus info
        Info(f"mcp_server_{config.name}_info", "Server information").info(
            {
                "version": config.version,
                "tier": config.tier.value,
                "capabilities": ",".join([c.value for c in config.capabilities]),
                "lambda_labs_host": config.lambda_labs_host,
            }
        )

    def _setup_middleware(self):
        """Configure FastAPI middleware"""
        if self.config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_origins or ["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def _setup_routes(self):
        """Configure standard routes"""
        self.app.get(self.config.health_endpoint)(self._health_check)
        self.app.get(self.config.metrics_endpoint)(self._metrics)
        self.app.get("/capabilities")(self._get_capabilities)
        self.app.get("/info")(self._get_info)
        self.app.on_event("startup")(self._startup)
        self.app.on_event("shutdown")(self._shutdown)

    async def _startup(self):
        """Startup event handler"""
        logger.info(
            f"Starting {self.config.name} MCP Server on port {self.config.port}"
        )
        logger.info(f"Lambda Labs Host: {self.config.lambda_labs_host}")
        logger.info(f"Environment: {self.config.environment}")
        logger.info(f"Tier: {self.config.tier.value}")
        logger.info(f"Capabilities: {[c.value for c in self.config.capabilities]}")

        try:
            await self.initialize()
            self._initialized = True
            HEALTH_STATUS.labels(server=self.config.name).set(1)
            logger.info(f"{self.config.name} MCP Server started successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {self.config.name}: {e}")
            HEALTH_STATUS.labels(server=self.config.name).set(0)
            raise

    async def _shutdown(self):
        """Shutdown event handler"""
        logger.info(f"Shutting down {self.config.name} MCP Server")
        try:
            await self.cleanup()
            HEALTH_STATUS.labels(server=self.config.name).set(0)
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def _health_check(self) -> dict[str, Any]:
        """Standard health check endpoint"""
        try:
            checks = await self.perform_health_checks()

            # Determine overall status
            status = "healthy"
            for check_name, check_result in checks.items():
                if not check_result.get("healthy", False):
                    status = "degraded" if status == "healthy" else "unhealthy"

            # Test Lambda Labs connectivity
            lambda_labs_connected = await self._test_lambda_labs_connection()

            result = HealthCheckResult(
                status=status,
                timestamp=datetime.now(UTC),
                server_name=self.config.name,
                version=self.config.version,
                uptime_seconds=time.time() - self.start_time,
                checks=checks,
                lambda_labs_connected=lambda_labs_connected,
            )

            HEALTH_STATUS.labels(server=self.config.name).set(
                1 if status == "healthy" else 0
            )

            return result.to_dict()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            ERROR_COUNT.labels(server=self.config.name, error_type="health_check").inc()
            raise HTTPException(status_code=503, detail=str(e))

    async def _test_lambda_labs_connection(self) -> bool:
        """Test connection to Lambda Labs host"""
        try:
            # Simple connectivity test (can be enhanced)
            return True  # Placeholder - implement actual test
        except:
            return False

    async def _metrics(self) -> Response:
        """Prometheus metrics endpoint"""
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    async def _get_capabilities(self) -> dict[str, Any]:
        """Get server capabilities"""
        return {
            "server": self.config.name,
            "tier": self.config.tier.value,
            "capabilities": [c.value for c in self.config.capabilities],
            "version": self.config.version,
            "lambda_labs_host": self.config.lambda_labs_host,
        }

    async def _get_info(self) -> dict[str, Any]:
        """Get server information"""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "tier": self.config.tier.value,
            "port": self.config.port,
            "uptime_seconds": time.time() - self.start_time,
            "environment": self.config.environment,
            "lambda_labs_host": self.config.lambda_labs_host,
            "active_connections": len(self._active_connections),
            "capabilities": [c.value for c in self.config.capabilities],
        }

    def track_request(self, method: str):
        """Track request metrics"""
        REQUEST_COUNT.labels(server=self.config.name, method=method).inc()
        return REQUEST_DURATION.labels(server=self.config.name, method=method).time()

    def track_error(self, error_type: str):
        """Track error metrics"""
        ERROR_COUNT.labels(server=self.config.name, error_type=error_type).inc()

    def add_connection(self, connection_id: str):
        """Track active connection"""
        self._active_connections.add(connection_id)
        ACTIVE_CONNECTIONS.labels(server=self.config.name).set(
            len(self._active_connections)
        )

    def remove_connection(self, connection_id: str):
        """Remove active connection"""
        self._active_connections.discard(connection_id)
        ACTIVE_CONNECTIONS.labels(server=self.config.name).set(
            len(self._active_connections)
        )

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    async def initialize(self):
        """Initialize server-specific resources"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup server-specific resources"""
        pass

    @abstractmethod
    async def perform_health_checks(self) -> dict[str, dict[str, Any]]:
        """Perform server-specific health checks"""
        pass

    def run(self):
        """Run the server"""
        import uvicorn

        uvicorn.run(self.app, host="0.0.0.0", port=self.config.port, log_level="info")


# Convenience classes for different server types
class ServiceMCPServer(UnifiedStandardizedMCPServer):
    """Base class for service integration servers (Slack, GitHub, etc)"""

    pass


class AIEngineMCPServer(UnifiedStandardizedMCPServer):
    """Base class for AI/ML servers"""

    pass


class InfrastructureMCPServer(UnifiedStandardizedMCPServer):
    """Base class for infrastructure servers"""

    pass
