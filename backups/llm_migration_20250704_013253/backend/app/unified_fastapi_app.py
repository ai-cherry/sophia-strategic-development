#!/usr/bin/env python3
"""
Unified FastAPI Application
===========================

Single, consolidated FastAPI application for the entire Sophia AI platform.
Integrates all routes, services, and middleware for optimal performance.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel

# Import all route modules
from backend.api import (
    asana_integration_routes,
    codacy_integration_routes,
    linear_integration_routes,
    mcp_integration_routes,
    notion_integration_routes,
    slack_linear_knowledge_routes,
    unified_routes,
)
from backend.api import (
    ceo_dashboard_routes as monitoring_routes,
)
from backend.api import (
    foundational_knowledge_routes as knowledge_base_routes,
)
from backend.core.config_manager import get_config_value
from backend.core.config_validator import DeploymentValidator
from backend.services.chat.unified_chat_service import UnifiedChatService
from backend.services.enhanced_unified_chat_service import EnhancedUnifiedChatService
from backend.services.foundational_knowledge_service import FoundationalKnowledgeService
from backend.services.mcp_orchestration_service import MCPOrchestrationService
from backend.services.n8n_webhook_service import N8NWebhookService
from backend.services.smart_ai_service import SmartAIService

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "sophia_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "sophia_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
)

ACTIVE_REQUESTS = Gauge("sophia_http_active_requests", "Active HTTP requests")

ERROR_RATE = Gauge("sophia_http_error_rate", "HTTP error rate")


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    timestamp: str
    version: str
    environment: str
    services: dict[str, str]
    uptime_seconds: float
    metrics: dict[str, Any] | None = None


class UnifiedFastAPIApp:
    """Unified FastAPI application manager"""

    def __init__(self):
        self.app: FastAPI | None = None
        self.start_time = datetime.now(UTC)
        self.services = {}
        self.validator = DeploymentValidator()
        self.error_count = 0
        self.request_count = 0

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage application lifecycle"""
        logger.info("🚀 Starting Sophia AI Unified Platform...")

        try:
            # Validate configuration
            await self._validate_configuration()

            # Initialize services
            await self._initialize_services()

            # Start background tasks
            await self._start_background_tasks()

            logger.info("✅ Sophia AI Platform started successfully")

            yield

        finally:
            # Cleanup
            logger.info("🛑 Shutting down Sophia AI Platform...")
            await self._cleanup_services()
            logger.info("✅ Shutdown complete")

    async def _validate_configuration(self):
        """Validate deployment configuration"""
        logger.info("🔍 Validating configuration...")

        validation_report = await self.validator.validate_deployment()

        if not validation_report.is_valid:
            critical_errors = [
                error
                for error in validation_report.errors
                if error.severity == "critical"
            ]

            if critical_errors:
                logger.error(f"❌ Critical configuration errors: {critical_errors}")
                raise RuntimeError("Critical configuration errors prevent startup")
            else:
                logger.warning(
                    f"⚠️  Configuration warnings: {validation_report.errors}"
                )

    async def _initialize_services(self):
        """Initialize all platform services"""
        logger.info("🔧 Initializing services...")

        # MCP Orchestration - use lazy import to prevent constructor execution at module load
        try:
            from backend.services.enhanced_mcp_orchestration_service import (
                EnhancedMCPOrchestrationService,
            )

            self.services["mcp_orchestration"] = EnhancedMCPOrchestrationService()
            await self.services["mcp_orchestration"].initialize()
        except Exception as e:
            logger.error(f"Failed to initialize MCP orchestration: {e}")
            # Fallback to basic orchestration
            from backend.services.mcp_orchestration_service import (
                get_orchestration_service,
            )

            self.services["mcp_orchestration"] = get_orchestration_service()

        # Chat Service
        self.services["chat"] = EnhancedUnifiedChatService()

        # Knowledge Service
        self.services["knowledge"] = FoundationalKnowledgeService()

        # AI Service
        self.services["ai"] = SmartAIService()

        # Initialize additional services
        MCPOrchestrationService()
        N8NWebhookService()

        # Initialize new services
        UnifiedChatService()
        FoundationalKnowledgeService()

        logger.info("✅ All services initialized")

    async def _start_background_tasks(self):
        """Start background tasks"""
        # Start MCP servers
        asyncio.create_task(self.services["mcp_orchestration"].start_all_servers())

        # Health monitoring
        asyncio.create_task(self._monitor_health())

    async def _monitor_health(self):
        """Monitor application health"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Update error rate
                if self.request_count > 0:
                    error_rate = (self.error_count / self.request_count) * 100
                    ERROR_RATE.set(error_rate)

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

    async def _cleanup_services(self):
        """Cleanup services on shutdown"""
        for service_name, service in self.services.items():
            try:
                if hasattr(service, "shutdown"):
                    await service.shutdown()
                elif hasattr(service, "close"):
                    await service.close()
            except Exception as e:
                logger.error(f"Error shutting down {service_name}: {e}")

    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application"""
        self.app = FastAPI(
            title="Sophia AI Unified Platform",
            description="The single, unified FastAPI application for all backend services.",
            version="2.0.0",
        )

        # Configure middleware
        self._configure_middleware()

        # Configure routes
        self._configure_routes()

        # Configure error handlers
        self._configure_error_handlers()

        return self.app

    def _configure_middleware(self):
        """Configure all middleware"""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Restrict in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # GZip compression
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Trusted host
        allowed_hosts = get_config_value("allowed_hosts", ["*"])
        if allowed_hosts != ["*"]:
            self.app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

        # Request tracking
        @self.app.middleware("http")
        async def track_requests(request: Request, call_next):
            start_time = time.time()

            # Track active requests
            ACTIVE_REQUESTS.inc()
            self.request_count += 1

            try:
                response = await call_next(request)

                # Track metrics
                duration = time.time() - start_time

                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code,
                ).inc()

                REQUEST_DURATION.labels(
                    method=request.method, endpoint=request.url.path
                ).observe(duration)

                if response.status_code >= 400:
                    self.error_count += 1

                # Add custom headers
                response.headers["X-Process-Time"] = str(duration)
                response.headers["X-Server-Version"] = "3.0.0"

                return response

            except Exception:
                self.error_count += 1
                raise
            finally:
                ACTIVE_REQUESTS.dec()

        # Rate limiting
        @self.app.middleware("http")
        async def rate_limit(request: Request, call_next):
            # Simple rate limiting - enhance as needed
            # Could integrate with Redis for distributed rate limiting
            return await call_next(request)

    def _configure_routes(self):
        """Configure all API routes"""

        @self.app.get("/", tags=["Status"])
        async def root() -> dict[str, str]:
            """Root endpoint for basic service health checks."""
            return {"status": "ok", "message": "Welcome to Sophia AI Unified Platform"}

        @self.app.get("/api/health", tags=["Status"])
        async def health_check() -> dict[str, str]:
            """Provides a simple health check endpoint."""
            return {"status": "ok"}

        @self.app.get("/api/status", tags=["Status"])
        async def get_status() -> dict[str, Any]:
            """Provides a detailed status of the application."""
            # This can be expanded to include database status, MCP server health, etc.
            return {
                "status": "ok",
                "service_name": "Sophia AI Unified Platform",
                "version": self.app.version,
            }

        # Include all route modules
        routers = [
            (unified_routes.router, "/api/v1", ["Unified API"]),
            (mcp_integration_routes.router, "/api", ["MCP"]),
            (knowledge_base_routes.router, "/api/v3", ["Knowledge Base"]),
            (slack_linear_knowledge_routes.router, "/api/v3", ["Integrations"]),
            (asana_integration_routes.router, "/api/v3", ["Integrations"]),
            (linear_integration_routes.router, "/api/v3", ["Integrations"]),
            (notion_integration_routes.router, "/api/v3", ["Integrations"]),
            (codacy_integration_routes.router, "/api/v3", ["Quality"]),
            (monitoring_routes.router, "/api/v3", ["Monitoring"]),
        ]

        for router, prefix, tags in routers:
            try:
                self.app.include_router(router, prefix=prefix, tags=tags)
                logger.info(f"✅ Loaded router: {router}")
            except Exception as e:
                logger.error(f"Failed to load router {router}: {e}")

        @self.app.post("/api/mcp/{tool_name:path}", tags=["MCP"])
        async def handle_mcp_request(
            tool_name: str, request: dict[str, Any]
        ) -> dict[str, Any]:
            """Handles all MCP requests and routes them to the orchestration service."""
            response = await self.services["mcp_orchestration"].route_tool_request(
                tool_name, request
            )
            return response

        @self.app.get("/api/mcp/health", tags=["MCP"])
        async def mcp_health() -> dict[str, Any]:
            """Provides a health check for the MCP orchestration service."""
            # This can be expanded to check the health of all registered MCP servers
            return {"status": "ok", "service": "mcp_orchestration"}

        @self.app.post("/api/n8n/webhook/{workflow_type:path}", tags=["N8N"])
        async def handle_n8n_webhook(
            workflow_type: str, payload: dict[str, Any]
        ) -> dict[str, Any]:
            """Handles all N8N webhooks and routes them to the webhook service."""
            result = await self.services["n8n_webhook_service"].process_webhook(
                workflow_type, payload
            )
            return {"status": "ok", "result": result}

        @self.app.get("/api/n8n/health", tags=["N8N"])
        async def n8n_health() -> dict[str, Any]:
            """Provides a health check for the N8N webhook service."""
            return {"status": "ok", "service": "n8n_webhook_service"}

        # Models for request/response
        class ChatRequest(BaseModel):
            query: str
            user_id: str
            session_id: str
            context: dict[str, Any] | None = None

        class FileUpload(BaseModel):
            file_name: str
            file_content: bytes  # Using bytes for file content

        class SyncRequest(BaseModel):
            source: str

        @self.app.post("/api/v1/chat", tags=["Chat"])
        async def chat(request: ChatRequest) -> dict[str, Any]:
            """Handles chat requests and returns an AI-generated response."""
            response = await self.services["chat"].process_chat(
                query=request.query,
                user_id=request.user_id,
                session_id=request.session_id,
                context=request.context,
            )
            return response

        @self.app.post("/api/v1/knowledge/upload", tags=["Knowledge"])
        async def upload_knowledge(file: FileUpload) -> dict[str, Any]:
            """Uploads a knowledge document to the system."""
            result = await self.services["knowledge"].upload_document(
                file_name=file.file_name,
                file_content=file.file_content,
            )
            return {"status": "ok", "result": result}

        @self.app.post("/api/v1/knowledge/sync", tags=["Knowledge"])
        async def sync_knowledge(request: SyncRequest) -> dict[str, Any]:
            """Triggers a knowledge sync from a specified source."""
            result = await self.services["knowledge"].sync_source(source=request.source)
            return {"status": "ok", "result": result}

    def _configure_error_handlers(self):
        """Configure global error handlers"""

        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "path": request.url.path,
                },
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {exc}", exc_info=True)

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": (
                        str(exc)
                        if logger.level <= logging.DEBUG
                        else "An error occurred"
                    ),
                    "timestamp": datetime.now(UTC).isoformat(),
                    "path": request.url.path,
                },
            )


# Create application instance
app_manager = UnifiedFastAPIApp()
app = app_manager.create_app()


if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "unified_fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=get_config_value("debug", False),
        log_level="info",
        access_log=True,
        workers=get_config_value("workers", 4),
    )
