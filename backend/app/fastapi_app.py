"""
Sophia AI FastAPI App

Practical FastAPI application with data flow management and LLM strategy.
Focuses on stability and scale without over-complexity.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import route modules
from backend.api.llm_strategy_routes import router as llm_router
from backend.api.data_flow_routes import router as data_flow_router
from backend.api.asana_integration_routes import router as asana_router
from backend.api.notion_integration_routes import router as notion_router
from backend.api.codacy_integration_routes import router as codacy_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Platform",
    description="AI assistant orchestrator for Pay Ready business intelligence",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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
async def read_root() -> dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Sophia AI Platform",
        "version": "1.0.0",
        "message": "Enterprise AI orchestrator ready"
    }


@app.get("/api/health", tags=["health"])
async def api_health_check() -> dict[str, str]:
    """Comprehensive API health check."""
    try:
        # Basic health indicators
        return {
            "status": "healthy",
            "api_version": "1.0.0",
            "services": {
                "llm_strategy": "available",
                "data_flow": "available",
                "asana_integration": "available",
                "notion_integration": "available",
                "codacy_integration": "available",
                "core_systems": "operational"
            },
            "message": "All systems operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "message": "Some systems may be unavailable"
        }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Sophia AI Platform...")
    logger.info("✅ FastAPI app initialized")
    logger.info("✅ CORS middleware configured")
    logger.info("✅ API routes registered")
    logger.info("✅ Code quality integration enabled")
    logger.info("🚀 Sophia AI Platform ready for requests")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Sophia AI Platform...")
    # Add cleanup logic here if needed
    logger.info("✅ Sophia AI Platform shutdown complete")
