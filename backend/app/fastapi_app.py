"""
FastAPI Application Factory
Creates and configures the main FastAPI application instance for Sophia AI
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from backend.core.startup_config import apply_startup_configuration
from backend.presentation.api.router import create_application_router
from pydantic_settings import BaseSettings
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Sophia AI FastAPI application...")

    try:
        # Initialize any startup tasks here
        logger.info("✅ Application startup complete")
        yield
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🔄 Shutting down Sophia AI application...")
        logger.info("✅ Application shutdown complete")


def create_fastapi_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    # Apply startup configuration for Snowflake fix
    apply_startup_configuration()

    # Create FastAPI app with lifespan management
    
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings with Pydantic v2"""
    app_name: str = "Sophia AI Platform"
    app_version: str = "3.0.0"
    environment: str = "production"
    debug: bool = False
    
    # Security
    secret_key: str = "change-me-in-production"
    allowed_origins: List[str] = ["*"]
    
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
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import uuid

# Enhanced middleware stack
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.debug else ["app.sophia-intel.ai"]
)

# Request tracking middleware

from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse

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


    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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
        f"Unhandled exception", 
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


    # Include application router
    app.include_router(create_application_router())

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "sophia-ai", "version": "1.0.0"}

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to Sophia AI Platform",
            "docs": "/docs",
            "health": "/health",
        }

    logger.info("✅ FastAPI application created and configured")
    return app


# Create the application instance
app = create_fastapi_app()
