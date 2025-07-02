"""
Sophia AI Unified Platform - Main Application
Single entry point for all API services
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

# Import configuration
from backend.app.core.config import settings
from backend.app.core.dependencies import get_mcp_service

# Import routers
from backend.api.v3_chat_routes import router as v3_chat_router
from backend.api.data_flow_routes import router as data_flow_router
from backend.api.llm_strategy_routes import router as llm_strategy_router
from backend.api.mcp_integration_routes import router as mcp_router
from backend.api.knowledge_base_routes import router as kb_router
from backend.api.linear_integration_routes import router as linear_router
from backend.api.asana_integration_routes import router as asana_router
from backend.api.notion_integration_routes import router as notion_router
from backend.api.codacy_integration_routes import router as codacy_router
from backend.api.snowflake_admin_routes import router as snowflake_admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create rate limiter
limiter = Limiter(key_func=get_remote_address)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Custom logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        
        # Log request
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {duration:.2f}ms"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-API-Version"] = settings.app_version
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Sophia AI Unified Platform...")
    
    # Initialize MCP orchestration service
    try:
        mcp_service = get_mcp_service()
        init_result = await mcp_service.initialize_mcp_servers()
        logger.info(f"MCP initialization result: {init_result}")
    except Exception as e:
        logger.error(f"Failed to initialize MCP servers: {e}")
        # Continue startup even if MCP initialization fails
    
    # Startup complete
    logger.info(f"✅ Sophia AI Platform v{settings.app_version} started successfully!")
    logger.info(f"📍 API documentation available at http://localhost:{settings.port}/docs")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Sophia AI Platform...")
    
    # Cleanup MCP services
    try:
        if mcp_service:
            await mcp_service.shutdown()
    except Exception as e:
        logger.error(f"Error during MCP shutdown: {e}")
    
    logger.info("👋 Sophia AI Platform shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Unified AI Platform for Business Intelligence and Automation",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with platform information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
            "api": {
                "v3": settings.api_v3_prefix,
                "mcp": settings.api_mcp_prefix,
                "admin": settings.api_admin_prefix
            }
        }
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {}
    }
    
    # Check MCP services
    try:
        mcp_service = get_mcp_service()
        mcp_health = await mcp_service.get_mcp_health_status()
        health_status["services"]["mcp"] = {
            "status": mcp_health["overall_health"],
            "healthy_servers": mcp_health["healthy_servers"],
            "total_servers": mcp_health["total_servers"]
        }
    except Exception as e:
        health_status["services"]["mcp"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Determine overall health
    if any(service.get("status") == "error" for service in health_status["services"].values()):
        health_status["status"] = "degraded"
    
    return health_status


# Mount routers with versioned prefixes
app.include_router(v3_chat_router, prefix=settings.api_v3_prefix, tags=["Chat"])
app.include_router(data_flow_router, prefix=settings.api_v3_prefix, tags=["Data Flow"])
app.include_router(llm_strategy_router, prefix=settings.api_v3_prefix, tags=["LLM Strategy"])
app.include_router(kb_router, prefix=settings.api_v3_prefix, tags=["Knowledge Base"])

# MCP routes
app.include_router(mcp_router, prefix=settings.api_mcp_prefix, tags=["MCP"])

# Integration routes
app.include_router(linear_router, prefix=f"{settings.api_v3_prefix}/linear", tags=["Linear"])
app.include_router(asana_router, prefix=f"{settings.api_v3_prefix}/asana", tags=["Asana"])
app.include_router(notion_router, prefix=f"{settings.api_v3_prefix}/notion", tags=["Notion"])
app.include_router(codacy_router, prefix=f"{settings.api_v3_prefix}/codacy", tags=["Codacy"])

# Admin routes
app.include_router(snowflake_admin_router, prefix=settings.api_admin_prefix, tags=["Admin"])

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.app.unified_main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    ) 