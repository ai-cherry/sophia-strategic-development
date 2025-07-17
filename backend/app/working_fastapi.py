"""
Sophia AI - Working FastAPI Application
Consolidated version that works with current dependencies and infrastructure
Combines functionality from api/main.py, simple_fastapi.py, and minimal_fastapi.py
"""

import os
import sys
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import routers
from .routers import agents

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Create FastAPI app with comprehensive configuration
app = FastAPI(
    title="Sophia AI - Unified Platform",
    description="Unified Sophia AI Platform API",
    version="3.0.0",
    debug=DEBUG,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(agents.router)

# Add WebSocket endpoint at app level for agents
@app.websocket("/ws/agents")
async def websocket_endpoint(websocket: WebSocket):
    """Forward WebSocket connections to agents router"""
    await agents.websocket_endpoint(websocket)

# Instance configuration (from api/main.py concept)
class InstanceConfig:
    def __init__(self):
        self.instance_id = os.getenv("INSTANCE_ID", "default")
        self.role = os.getenv("INSTANCE_ROLE", "primary")
        self.gpu_enabled = os.getenv("GPU_ENABLED", "false").lower() == "true"
        self.lambda_instance = os.getenv("LAMBDA_INSTANCE", "unknown")

config = InstanceConfig()

@app.get("/")
async def root():
    """Root endpoint with instance information"""
    return {
        "message": "Sophia AI - Unified Platform",
        "version": "3.0.0",
        "status": "operational",
        "instance": {
            "id": config.instance_id,
            "role": config.role,
            "gpu_enabled": config.gpu_enabled,
            "lambda_instance": config.lambda_instance
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Basic system checks
        health_status = {
            "status": "healthy",
            "version": "3.0.0",
            "environment": ENVIRONMENT,
            "instance": {
                "id": config.instance_id,
                "role": config.role,
                "lambda_instance": config.lambda_instance,
                "gpu_enabled": config.gpu_enabled
            },
            "checks": {
                "environment": "ok",
                "python_version": sys.version.split()[0],
                "api_keys": {
                    "openai": bool(os.getenv("OPENAI_API_KEY")),
                    "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                    "gong": bool(os.getenv("GONG_API_KEY")),
                    "pinecone": bool(os.getenv("PINECONE_API_KEY"))
                },
                "services": {
                    "database": "available" if os.getenv("DATABASE_URL") else "not_configured",
                    "redis": "available" if os.getenv("REDIS_URL") else "not_configured",
                    "qdrant": "available" if os.getenv("QDRANT_URL") else "not_configured"
                }
            },
            "uptime": "healthy",
            "timestamp": datetime.now().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/api/status")
async def api_status():
    """API status and configuration"""
    return {
        "api": "sophia-ai-unified",
        "version": "3.0.0",
        "status": "operational",
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "features": [
            "health_monitoring",
            "cors_enabled", 
            "gzip_compression",
            "instance_awareness",
            "api_key_management"
        ],
        "endpoints": {
            "core": ["/", "/health", "/api/status"],
            "api": ["/api/test", "/api/config"],
            "docs": ["/docs", "/redoc"] if DEBUG else []
        },
        "instance": {
            "id": config.instance_id,
            "role": config.role,
            "capabilities": {
                "gpu": config.gpu_enabled,
                "lambda_labs": config.lambda_instance != "unknown"
            }
        }
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for functionality verification"""
    return {
        "test": "successful",
        "message": "Sophia AI unified backend is operational",
        "system": {
            "python_version": sys.version,
            "platform": sys.platform,
            "environment": ENVIRONMENT
        },
        "configuration": {
            "debug": DEBUG,
            "port": PORT,
            "host": HOST,
            "instance_role": config.role
        },
        "connectivity": {
            "api_keys_configured": sum([
                bool(os.getenv("OPENAI_API_KEY")),
                bool(os.getenv("ANTHROPIC_API_KEY")),
                bool(os.getenv("GONG_API_KEY")),
                bool(os.getenv("PINECONE_API_KEY"))
            ]),
            "services_available": sum([
                bool(os.getenv("DATABASE_URL")),
                bool(os.getenv("REDIS_URL")),
                bool(os.getenv("QDRANT_URL"))
            ])
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config")
async def configuration_info():
    """Configuration information (non-sensitive)"""
    return {
        "environment": ENVIRONMENT,
        "debug_mode": DEBUG,
        "instance": {
            "id": config.instance_id,
            "role": config.role,
            "lambda_instance": config.lambda_instance,
            "gpu_enabled": config.gpu_enabled
        },
        "features": {
            "cors": True,
            "gzip": True,
            "docs": DEBUG,
            "monitoring": True
        },
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if DEBUG else "An error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup configuration"""
    logger.info("🚀 Starting Sophia AI Unified Platform...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Instance: {config.instance_id} ({config.role})")
    logger.info(f"Lambda Labs: {config.lambda_instance}")
    logger.info(f"GPU Enabled: {config.gpu_enabled}")
    logger.info(f"Debug Mode: {DEBUG}")
    logger.info("✅ Startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown cleanup"""
    logger.info("🛑 Shutting down Sophia AI Unified Platform...")
    logger.info("✅ Shutdown complete!")

if __name__ == "__main__":
    logger.info("🚀 Starting Sophia AI Unified Backend...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Starting server on {HOST}:{PORT}")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info",
        access_log=True
    )
