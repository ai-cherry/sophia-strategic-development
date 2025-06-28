"""
Minimal Sophia AI FastAPI App
"""

from fastapi import FastAPI
import logging
import os

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


@app.get("/")
async def read_root():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Sophia AI Platform",
        "version": "1.0.0",
        "message": "Enterprise AI orchestrator ready",
        "environment": ENVIRONMENT,
    }


@app.get("/api/health")
async def api_health_check():
    """Simple API health check without config loading."""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "environment": ENVIRONMENT,
        "deployment_status": "OPERATIONAL",
        "message": f"Sophia AI Platform operational in {ENVIRONMENT} environment",
    }


@app.get("/api/test-config")
async def test_config():
    """Test configuration loading."""
    try:
        from backend.core.auto_esc_config import get_config_value

        openai_key = get_config_value("openai_api_key")
        gong_key = get_config_value("gong_access_key")

        return {
            "status": "success",
            "openai_configured": bool(openai_key and len(openai_key) > 10),
            "gong_configured": bool(gong_key and len(gong_key) > 10),
            "environment": ENVIRONMENT,
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "environment": ENVIRONMENT}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"🚀 Starting Sophia AI Platform in {ENVIRONMENT} environment...")
    logger.info("✅ Minimal FastAPI app initialized")
    logger.info("🚀 Sophia AI Platform ready for requests")
