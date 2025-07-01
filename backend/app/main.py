import os
import sys

from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest
from pydantic_settings import BaseSettings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "patches"))
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "patches"))
"""
Sophia AI FastAPI Application

Modernized FastAPI application using lifespan events and proper dependency injection.
Eliminates circular imports and follows Clean Architecture principles.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.dependencies import get_chat_service

# Core imports
from backend.core.simple_config import get_config_value

# Route imports - no circular dependencies
from backend.presentation.api.router import create_application_router
from backend.security.audit_logger import AuditEventType, configure_from_env, info

# Security imports
from backend.security.audit_middleware import setup_audit_middleware
from backend.security.ephemeral_credentials import (
    EphemeralCredentialsService,
    setup_ephemeral_credentials_middleware,
)
from backend.security.rbac import initialize_rbac_service, setup_rbac

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event handlers.
    """
    # Startup
    logger.info("🚀 Starting Sophia AI Unified Ecosystem...")

    try:
        # Configure audit logger from environment
        configure_from_env()
        logger.info("✅ Audit Logger configured")

        # Log system startup
        info(
            AuditEventType.SYSTEM_START,
            "Sophia AI Unified Ecosystem starting",
            {"app_name": "sophia"}
        )

        # Initialize the RBAC system
        rbac_storage_path = os.path.join(os.getcwd(), "data", "rbac.json")
        initialize_rbac_service(
            storage_path=rbac_storage_path,
            load_system_roles=True,
            auto_save=True,
        )
        logger.info("✅ RBAC System initialized")

        # Initialize the ephemeral credentials system
        ephemeral_credentials_service = EphemeralCredentialsService(
            storage_path=os.path.join(os.getcwd(), "data", "ephemeral_credentials.json"),
            auto_save=True,
        )
        await ephemeral_credentials_service.initialize()
        app.state.ephemeral_credentials_service = ephemeral_credentials_service
        logger.info("✅ Ephemeral Credentials System initialized")

        # Initialize the cache system
        from backend.core.cache_manager import (
            get_cache_manager,
            initialize_cache_system,
        )

        await initialize_cache_system()
        cache_manager = await get_cache_manager()
        app.state.cache_manager = cache_manager
        logger.info("✅ Enhanced Cache System initialized")

        # Initialize the simplified unified intelligence service
        from backend.services.simplified_unified_intelligence_service import (
            get_simplified_unified_intelligence_service,
        )

        unified_service = await get_simplified_unified_intelligence_service()
        app.state.unified_intelligence = unified_service
        logger.info("✅ Simplified Unified Intelligence Service initialized")

        # Initialize the chat service and store in app state
        chat_service = await get_chat_service()
        app.state.chat_service_instance = chat_service
        logger.info("✅ Chat Service initialized")

        # Test configuration loading
        config_test = get_config_value("values_sophia_ai_openai_api_key", "")
        if config_test:
            logger.info("✅ Configuration loaded successfully")
        else:
            logger.warning("⚠️ No OpenAI API key found - running in limited mode")

        logger.info("✅ Sophia AI Unified Ecosystem startup complete")

        # Yield control to the application
        yield

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Still yield to prevent startup failure
        yield

    finally:
        # Shutdown
        logger.info("🛑 Shutting down Sophia AI Unified Ecosystem...")

        # Log system shutdown
        info(
            AuditEventType.SYSTEM_STOP,
            "Sophia AI Unified Ecosystem shutting down",
            {"app_name": "sophia"}
        )

        # Cleanup cache system if it exists
        if hasattr(app.state, "cache_manager"):
            try:
                # Clean up cache resources
                await app.state.cache_manager.clear()
                delattr(app.state, "cache_manager")
                logger.info("✅ Cache system cleaned up")
            except Exception as e:
                logger.error(f"⚠️ Error during cache system cleanup: {e}")

        # Cleanup ephemeral credentials system if it exists
        if hasattr(app.state, "ephemeral_credentials_service"):
            try:
                # Clean up ephemeral credentials resources
                await app.state.ephemeral_credentials_service.shutdown()
                delattr(app.state, "ephemeral_credentials_service")
                logger.info("✅ Ephemeral credentials system cleaned up")
            except Exception as e:
                logger.error(f"⚠️ Error during ephemeral credentials system cleanup: {e}")

        # Cleanup services if they exist
        for service_name in ["unified_intelligence", "chat_service_instance"]:
            if hasattr(app.state, service_name):
                try:
                    delattr(app.state, service_name)
                    logger.info(f"✅ {service_name} cleaned up")
                except Exception as e:
                    logger.error(f"⚠️ Error during {service_name} cleanup: {e}")

        logger.info("✅ Sophia AI Unified Ecosystem shutdown complete")


# Create FastAPI app with lifespan



class Settings(BaseSettings):
    """Application settings with Pydantic v2"""
    app_name: str = "Sophia AI Platform"
    app_version: str = "3.0.0"
    environment: str = "production"
    debug: bool = False

    # Security
    secret_key: str = "change-me-in-production"
    allowed_origins: list[str] = ["*"]

    # API Configuration
    api_prefix: str = "/api/v3"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    class Config:
        env_prefix = "SOPHIA_"
        case_sensitive = False
        env_file = ".env"

# Initialize settings
settings = Settings()

app = FastAPI(
    title="Sophia AI Platform",
    description="AI-powered business intelligence and automation platform",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time
import uuid

from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Enhanced middleware stack
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["app.sophia-intel.ai"]
)

from slowapi.errors import RateLimitExceeded

# Set up audit middleware
setup_audit_middleware(app)

# Log middleware setup
logger.info("✅ Audit middleware configured")

# Set up RBAC
setup_rbac(
    app=app,
    storage_path=os.path.join(os.getcwd(), "data", "rbac.json"),
    load_system_roles=True,
    auto_save=True,
    default_resource_type=None,  # No default resource type
    exclude_paths=["/docs", "/redoc", "/openapi.json", "/api/v3/auth"],
    use_middleware=False,  # Use dependencies instead of middleware for fine-grained control
)

# Log RBAC setup
logger.info("✅ RBAC middleware configured")

# Set up ephemeral credentials middleware
setup_ephemeral_credentials_middleware(
    app=app,
    exclude_paths=["/docs", "/redoc", "/openapi.json", "/api/v3/auth", "/api/v3/health"],
)

# Log ephemeral credentials middleware setup
logger.info("✅ Ephemeral credentials middleware configured")

# Log RBAC setup
logger.info("✅ RBAC system configured")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enhanced error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured logging"""
    correlation_id = request.headers.get("X-Correlation-ID", "unknown")

    logger.error(
        "Unhandled exception",
        extra={
            "correlation_id": correlation_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc)
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Request tracking middleware


# Metrics
REQUEST_COUNT = Counter('sophia_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('sophia_request_duration_seconds', 'Request duration')

@app.get("/metrics", response_class=PlainTextResponse, tags=["System"])
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Metrics middleware
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.observe(duration)

    return response

@app.middleware("http")
async def add_request_tracking(request: Request, call_next):
    start_time = time.time()

    # Add correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

    # Process request
    response = await call_next(request)

    # Add response headers
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Correlation-ID"] = correlation_id

    return response



# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error", "error": str(exc)}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sophia AI Platform",
        "version": "2.0.0",
        "timestamp": asyncio.get_event_loop().time(),
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Sophia AI Platform",
        "version": "2.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
    }


# Include master router
master_router = create_application_router()
app.include_router(master_router)


def run_server():
    """Run the server with proper configuration"""
    uvicorn.run(
        "backend.app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )


if __name__ == "__main__":
    run_server()
