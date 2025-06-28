"""
Simple Sophia AI FastAPI App for Testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
async def read_root():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Sophia AI Platform",
        "version": "1.0.0",
        "message": "Enterprise AI orchestrator ready",
        "environment": ENVIRONMENT
    }

@app.get("/api/health", tags=["health"])
async def api_health_check():
    """Simple API health check."""
    try:
        # Check if we can load basic configuration
        from backend.core.auto_esc_config import get_config_value
        
        # Test basic config loading
        try:
            openai_key = get_config_value("openai_api_key")
            has_openai = bool(openai_key and len(openai_key) > 10)
        except:
            has_openai = False
            
        try:
            gong_key = get_config_value("gong_access_key")
            has_gong = bool(gong_key and len(gong_key) > 10)
        except:
            has_gong = False

        # Determine overall status
        config_health = "healthy" if (has_openai or has_gong) else "degraded"
        
        return {
            "status": config_health,
            "api_version": "1.0.0",
            "environment": ENVIRONMENT,
            "deployment_status": "OPERATIONAL",
            "configuration_summary": {
                "openai_configured": has_openai,
                "gong_configured": has_gong,
                "environment": ENVIRONMENT,
                "pulumi_esc": "connected"
            },
            "message": f"Sophia AI Platform operational in {ENVIRONMENT} environment"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Health check system failure",
            "environment": ENVIRONMENT
        }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info(f"🚀 Starting Sophia AI Platform in {ENVIRONMENT} environment...")
    logger.info("✅ Simple FastAPI app initialized")
    logger.info(f"🚀 Sophia AI Platform ready for requests in {ENVIRONMENT} environment")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("✅ Sophia AI Platform shutdown complete")
