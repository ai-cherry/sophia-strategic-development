#!/usr/bin/env python3
"""
Unified MCP Server Base Class
Provides standardized foundation for all Sophia AI MCP servers.
"""

import logging
import os
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_client.core import CollectorRegistry

# Import custom logger when available, fallback to standard logging
try:
    from backend.utils.custom_logger import setup_logger
except ImportError:

    def setup_logger(name: str):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        return logger


logger = logging.getLogger(__name__)

# Lambda Labs Configuration
LAMBDA_LABS_HOST = os.getenv("LAMBDA_LABS_HOST", "104.171.202.64")


class ServerStatus(Enum):
    """Unified server status enumeration"""

    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class HealthCheckLevel(Enum):
    """Health check detail levels"""

    BASIC = "basic"
    DETAILED = "detailed"
    FULL = "full"


@dataclass
class HealthCheckResult:
    """Health check result with proper serialization."""

    status: str  # healthy, degraded, unhealthy
    timestamp: str
    server_name: str
    version: str
    port: int
    uptime_seconds: float
    errors: list[str]
    metrics: dict[str, Any]

    def dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class MCPServerConfig:
    """Configuration for MCP servers."""

    name: str
    port: int
    version: str = "1.0.0"
    environment: str = "prod"
    enable_metrics: bool = True
    enable_health_check: bool = True
    log_level: str = "INFO"
    cors_origins: list[str] | None = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

    # Lambda Labs Integration
    lambda_labs_host: str = LAMBDA_LABS_HOST
    enable_lambda_labs: bool = True

    # Features
    enable_cortex: bool = False
    enable_caching: bool = True

    # Performance
    timeout_seconds: int = 30
    max_retries: int = 3
    cache_ttl_seconds: int = 300

    # Security
    enable_auth: bool = False
    api_key: str | None = None


class UnifiedMCPMetrics:
    """Unified metrics collection"""

    def __init__(self, server_name: str):
        self.server_name = server_name

        # Counters
        self.requests_total = Counter(
            f"{server_name}_requests_total", f"Total requests to {server_name}"
        )
        self.errors_total = Counter(
            f"{server_name}_errors_total", f"Total errors in {server_name}"
        )

        # Gauges
        self.health_status = Gauge(
            f"{server_name}_health_status",
            f"Health status of {server_name} (1=healthy, 0=unhealthy)",
        )
        self.active_connections = Gauge(
            f"{server_name}_active_connections", f"Active connections to {server_name}"
        )

        # Histograms
        self.request_duration = Histogram(
            f"{server_name}_request_duration_seconds",
            f"Request duration for {server_name}",
        )


class StandardizedMCPServer(ABC):
    """Base class for all Sophia AI MCP servers."""

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.logger = setup_logger(f"mcp.{config.name}")
        self.start_time = datetime.utcnow()

        # Metrics
        self.registry = CollectorRegistry()
        self.request_count = Counter(
            "mcp_requests_total",
            "Total MCP requests",
            ["method", "status"],
            registry=self.registry,
        )
        self.request_duration = Histogram(
            "mcp_request_duration_seconds",
            "MCP request duration",
            ["method"],
            registry=self.registry,
        )
        self.active_connections = Gauge(
            "mcp_active_connections", "Active MCP connections", registry=self.registry
        )

        # Create app without lifespan for now
        self.app = FastAPI(title=f"{config.name} MCP Server", version=config.version)

        self._setup_middleware()
        self._setup_routes()
        self._setup_events()

    def _setup_events(self):
        """Setup startup and shutdown events."""

        @self.app.on_event("startup")
        async def startup_event():
            await self.initialize()
            self.logger.info(f"{self.config.name} started on port {self.config.port}")

        @self.app.on_event("shutdown")
        async def shutdown_event():
            await self.shutdown()
            self.logger.info(f"{self.config.name} shutdown complete")

    def _setup_middleware(self):
        """Setup FastAPI middleware."""
        # CORS - ensure cors_origins is not None
        cors_origins = (
            self.config.cors_origins if self.config.cors_origins is not None else ["*"]
        )
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Request timing
        @self.app.middleware("http")
        async def add_process_time_header(request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response

    def _setup_routes(self):
        """Setup standard routes."""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            result = await self.health_check()
            status_code = 200 if result.status == "healthy" else 503
            return JSONResponse(content=result.dict(), status_code=status_code)

        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint."""
            if not self.config.enable_metrics:
                raise HTTPException(status_code=404, detail="Metrics not enabled")
            return generate_latest(self.registry)

        @self.app.post("/tools/list")
        async def list_tools():
            """List available tools."""
            try:
                tools = await self.get_tools()
                return {"tools": [self._tool_to_dict(tool) for tool in tools]}
            except Exception as e:
                self.logger.error(f"Failed to list tools: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/tools/execute")
        async def execute_tool(name: str, arguments: dict[str, Any]):
            """Execute a specific tool."""
            start_time = time.time()
            try:
                self.request_count.labels(method=name, status="success").inc()
                result = await self.execute_tool(name, arguments)
                duration = time.time() - start_time
                self.request_duration.labels(method=name).observe(duration)
                return {"result": result}
            except Exception as e:
                self.request_count.labels(method=name, status="error").inc()
                self.logger.error(f"Tool execution failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def _tool_to_dict(self, tool: Any) -> dict[str, Any]:
        """Convert tool to dictionary."""
        # If tool is already a dictionary, return it
        if isinstance(tool, dict):
            return tool

        # Otherwise try to extract attributes
        return {
            "name": getattr(tool, "name", "unknown"),
            "description": getattr(tool, "description", ""),
            "parameters": getattr(tool, "inputSchema", {}),
        }

    @abstractmethod
    async def get_tools(self) -> list[Any]:
        """Get list of tools provided by this server."""
        pass

    @abstractmethod
    async def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a specific tool."""
        pass

    @abstractmethod
    async def server_specific_init(self) -> None:
        """Server-specific initialization."""
        pass

    @abstractmethod
    async def server_specific_cleanup(self) -> None:
        """Server-specific cleanup."""
        pass

    async def health_check(self) -> HealthCheckResult:
        """Perform health check."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        errors = []
        status = "healthy"

        # Check server-specific health
        try:
            server_healthy = await self.check_server_health()
            if not server_healthy:
                status = "degraded"
                errors.append("Server-specific health check failed")
        except Exception as e:
            status = "unhealthy"
            errors.append(f"Health check error: {str(e)}")

        metrics = {
            "uptime_seconds": uptime,
            "active_connections": self.active_connections._value.get(),
            "total_requests": sum(
                self.request_count.labels(method=m, status=s)._value.get()
                for m in ["list_tools", "execute_tool"]
                for s in ["success", "error"]
            ),
        }

        return HealthCheckResult(
            status=status,
            timestamp=datetime.utcnow().isoformat(),
            server_name=self.config.name,
            version=self.config.version,
            port=self.config.port,
            uptime_seconds=uptime,
            errors=errors,
            metrics=metrics,
        )

    async def check_server_health(self) -> bool:
        """Override to implement server-specific health checks."""
        return True

    async def initialize(self) -> None:
        """Initialize the server."""
        try:
            await self.server_specific_init()
            self.logger.info(f"Server initialized: {self.config.name}")
        except Exception as e:
            self.logger.error(f"Server initialization failed: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown the server."""
        try:
            await self.server_specific_cleanup()
            self.logger.info(f"Server shutdown complete: {self.config.name}")
        except Exception as e:
            self.logger.error(f"Server shutdown failed: {e}")
            raise

    def run(self) -> None:
        """Run the MCP server."""
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.config.port,
            log_level=self.config.log_level.lower(),
        )


# Helper decorators for tool implementation
def mcp_tool(name: str, description: str, parameters: dict[str, Any]):
    """Decorator to mark a method as an MCP tool."""

    def decorator(func: Callable) -> Callable:
        func._mcp_tool = True
        func._mcp_name = name
        func._mcp_description = description
        func._mcp_parameters = parameters
        return func

    return decorator


class SimpleMCPServer(StandardizedMCPServer):
    """Simplified MCP server that auto-discovers tools from decorated methods."""

    async def get_tools(self) -> list[dict[str, Any]]:
        """Auto-discover tools from decorated methods."""
        tools = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_mcp_tool") and attr._mcp_tool:
                tools.append(
                    {
                        "name": attr._mcp_name,
                        "description": attr._mcp_description,
                        "inputSchema": attr._mcp_parameters,
                    }
                )
        return tools

    async def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute tool by finding decorated method."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_mcp_tool") and attr._mcp_tool and attr._mcp_name == name:
                return await attr(**arguments)
        raise ValueError(f"Unknown tool: {name}")

    async def server_specific_init(self) -> None:
        """Default implementation - override if needed."""
        pass

    async def server_specific_cleanup(self) -> None:
        """Default implementation - override if needed."""
        pass
