"""
Sophia AI Unified API - Simplified Working Version
Consolidates all API endpoints into a single application
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import available routers
try:
    from backend.api.data_flow_routes import router as data_flow_router

    has_data_flow = True
except ImportError:
    has_data_flow = False
    logger.warning("Could not import data_flow_routes")

try:
    from backend.api.llm_strategy_routes import router as llm_strategy_router

    has_llm_strategy = True
except ImportError:
    has_llm_strategy = False
    logger.warning("Could not import llm_strategy_routes")

try:
    from backend.api.mcp_integration_routes import router as mcp_router

    has_mcp = True
except ImportError:
    has_mcp = False
    logger.warning("Could not import mcp_integration_routes")

try:
    from backend.api.linear_integration_routes import router as linear_router

    has_linear = True
except ImportError:
    has_linear = False
    logger.warning("Could not import linear_integration_routes")

try:
    from backend.api.asana_integration_routes import router as asana_router

    has_asana = True
except ImportError:
    has_asana = False
    logger.warning("Could not import asana_integration_routes")

try:
    from backend.api.notion_integration_routes import router as notion_router

    has_notion = True
except ImportError:
    has_notion = False
    logger.warning("Could not import notion_integration_routes")

try:
    from backend.api.codacy_integration_routes import router as codacy_router

    has_codacy = True
except ImportError:
    has_codacy = False
    logger.warning("Could not import codacy_integration_routes")


# Application configuration
APP_NAME = "Sophia AI Unified Platform"
APP_VERSION = "3.0.0"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(f"🚀 Starting {APP_NAME} v{APP_VERSION}...")
    logger.info(f"📍 Environment: {ENVIRONMENT}")

    # Initialize services
    try:
        # Try to initialize MCP orchestration if available
        from backend.services.mcp_orchestration_service import MCPOrchestrationService

        app.state.mcp_service = MCPOrchestrationService()
        logger.info("✅ MCP Orchestration Service initialized")
    except Exception as e:
        logger.warning(f"Could not initialize MCP service: {e}")
        app.state.mcp_service = None

    logger.info(f"✅ {APP_NAME} started successfully!")
    logger.info("📍 API documentation: http://localhost:8000/docs")

    yield

    # Shutdown
    logger.info(f"🛑 Shutting down {APP_NAME}...")

    # Cleanup services
    if hasattr(app.state, "mcp_service") and app.state.mcp_service:
        try:
            await app.state.mcp_service.shutdown()
        except Exception as e:
            logger.error(f"Error during MCP shutdown: {e}")

    logger.info("👋 Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Unified AI Platform for Business Intelligence and Automation",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with platform information"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": {"v3": "/api/v3", "mcp": "/api/mcp", "admin": "/api/admin"},
        },
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "services": {},
    }

    # Check MCP services if available
    if hasattr(app.state, "mcp_service") and app.state.mcp_service:
        try:
            mcp_health = await app.state.mcp_service.get_mcp_health_status()
            health_status["services"]["mcp"] = {
                "status": mcp_health.get("overall_health", "unknown"),
                "healthy_servers": mcp_health.get("healthy_servers", 0),
                "total_servers": mcp_health.get("total_servers", 0),
            }
        except Exception as e:
            health_status["services"]["mcp"] = {"status": "error", "error": str(e)}

    # Check loaded routers
    health_status["services"]["routers"] = {
        "data_flow": "loaded" if has_data_flow else "not_available",
        "llm_strategy": "loaded" if has_llm_strategy else "not_available",
        "mcp": "loaded" if has_mcp else "not_available",
        "linear": "loaded" if has_linear else "not_available",
        "asana": "loaded" if has_asana else "not_available",
        "notion": "loaded" if has_notion else "not_available",
        "codacy": "loaded" if has_codacy else "not_available",
    }

    # Determine overall health
    if any(
        service.get("status") == "error"
        for service in health_status["services"].values()
    ):
        health_status["status"] = "degraded"

    return health_status


# Simple chat endpoint for testing
@app.post("/api/v3/chat", tags=["Chat"])
async def chat_endpoint(request: Request):
    """Simple chat endpoint for testing"""
    try:
        body = await request.json()
        message = body.get("message", "")

        # Try to use chat service if available
        try:
            from backend.core.config_manager import ConfigManager
            from backend.services.enhanced_unified_chat_service import (
                EnhancedUnifiedChatService,
            )

            config_manager = ConfigManager()
            chat_service = EnhancedUnifiedChatService(config_manager)
            await chat_service.initialize()

            response = await chat_service.process_message(
                message=message,
                user_id=body.get("user_id", "test_user"),
                session_id=body.get("session_id", "test_session"),
            )

            return {"response": response, "status": "success"}

        except Exception as e:
            logger.error(f"Chat service error: {e}")
            # Fallback response
            return {
                "response": f"Echo: {message}",
                "status": "fallback",
                "note": "Chat service not available, returning echo",
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount available routers
if has_data_flow:
    app.include_router(data_flow_router, prefix="/api/v3", tags=["Data Flow"])
    logger.info("✅ Mounted data_flow_router")

if has_llm_strategy:
    app.include_router(llm_strategy_router, prefix="/api/v3", tags=["LLM Strategy"])
    logger.info("✅ Mounted llm_strategy_router")

if has_mcp:
    app.include_router(mcp_router, prefix="/api/mcp", tags=["MCP"])
    logger.info("✅ Mounted mcp_router")

if has_linear:
    app.include_router(linear_router, prefix="/api/v3/linear", tags=["Linear"])
    logger.info("✅ Mounted linear_router")

if has_asana:
    app.include_router(asana_router, prefix="/api/v3/asana", tags=["Asana"])
    logger.info("✅ Mounted asana_router")

if has_notion:
    app.include_router(notion_router, prefix="/api/v3/notion", tags=["Notion"])
    logger.info("✅ Mounted notion_router")

if has_codacy:
    app.include_router(codacy_router, prefix="/api/v3/codacy", tags=["Codacy"])
    logger.info("✅ Mounted codacy_router")


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
        },
    )


# API info endpoint
@app.get("/api/info", tags=["Info"])
async def api_info():
    """Get API information and available endpoints"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append(
                {"path": route.path, "methods": list(route.methods), "name": route.name}
            )

    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x["path"]),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "backend.app.unified_api:app",
        host="0.0.0.0",
        port=port,
        reload=True if ENVIRONMENT == "development" else False,
        log_level="info",
    )
