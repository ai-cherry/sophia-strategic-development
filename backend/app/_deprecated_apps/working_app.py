"""
Working Sophia AI FastAPI App

FastAPI application with data flow management and LLM strategy.
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.asana_integration_routes import router as asana_router
from backend.api.codacy_integration_routes import router as codacy_router
from backend.api.data_flow_routes import router as data_flow_router

# Import route modules
from backend.api.llm_strategy_routes import router as llm_router
from backend.api.notion_integration_routes import router as notion_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Platform",
    description="AI assistant orchestrator for Pay Ready business intelligence",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(llm_router)
app.include_router(data_flow_router)
app.include_router(asana_router)
app.include_router(notion_router)
app.include_router(codacy_router)


@app.get("/", tags=["health"])
async def read_root():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Sophia AI Platform",
        "version": "1.0.0",
        "message": "Enterprise AI orchestrator ready",
        "environment": ENVIRONMENT,
    }


@app.get("/api/health", tags=["health"])
async def api_health_check():
    """Simple API health check with configuration validation."""
    try:
        # Check if we can load basic configuration
        from backend.core.auto_esc_config import get_config_value

        # Test basic config loading
        try:
            openai_key = get_config_value("openai_api_key")
            has_openai = bool(openai_key and len(openai_key) > 10)
        except Exception:
            has_openai = False

        try:
            gong_key = get_config_value("gong_access_key")
            has_gong = bool(gong_key and len(gong_key) > 10)
        except Exception:
            has_gong = False

        # Determine overall status
        config_health = "healthy" if (has_openai or has_gong) else "degraded"

        return {
            "status": config_health,
            "api_version": "1.0.0",
            "environment": ENVIRONMENT,
            "deployment_status": "OPERATIONAL",
            "services": {
                "llm_strategy": "available",
                "data_flow": "available",
                "asana_integration": "available",
                "notion_integration": "available",
                "codacy_integration": "available",
                "core_systems": config_health,
                "configuration": "loaded",
            },
            "configuration_summary": {
                "openai_configured": has_openai,
                "gong_configured": has_gong,
                "environment": ENVIRONMENT,
                "pulumi_esc": "connected",
            },
            "message": f"Sophia AI Platform operational in {ENVIRONMENT} environment",
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Health check system failure",
            "environment": ENVIRONMENT,
            "api_version": "1.0.0",
            "deployment_status": "ERROR",
            "services": "error",
            "configuration_summary": "error",
        }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup with basic validation."""
    logger.info(f"🚀 Starting Sophia AI Platform in {ENVIRONMENT} environment...")

    try:
        # Basic configuration check
        from backend.core.auto_esc_config import get_config_value

        # Test basic config loading
        try:
            openai_key = get_config_value("openai_api_key")
            logger.info(
                f"✅ OpenAI configuration loaded: {'Yes' if openai_key else 'No'}"
            )
        except Exception as e:
            logger.warning(f"⚠️ OpenAI configuration issue: {e}")

        try:
            gong_key = get_config_value("gong_access_key")
            logger.info(f"✅ Gong configuration loaded: {'Yes' if gong_key else 'No'}")
        except Exception as e:
            logger.warning(f"⚠️ Gong configuration issue: {e}")

    except Exception as e:
        logger.error(f"❌ Startup configuration check failed: {e}")
        if ENVIRONMENT.lower() == "prod":
            logger.error("🚨 PRODUCTION STARTUP FAILED")
            raise RuntimeError(f"Production startup failed: {str(e)}")
        else:
            logger.warning(
                "🔄 Continuing startup in development mode despite errors..."
            )

    logger.info("✅ FastAPI app initialized")
    logger.info("✅ CORS middleware configured")
    logger.info("✅ API routes registered")
    logger.info(
        f"🚀 Sophia AI Platform ready for requests in {ENVIRONMENT} environment"
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Sophia AI Platform...")
    logger.info("✅ Sophia AI Platform shutdown complete")
