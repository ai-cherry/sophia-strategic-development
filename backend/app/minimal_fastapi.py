"""
Sophia AI - Minimal FastAPI Application
Minimal version that can start without complex dependencies
Aligned with working_fastapi.py standard
"""

import os
import sys
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Create FastAPI app
app = FastAPI(
    title="Sophia AI - Minimal",
    description="Minimal Sophia AI API",
    version="1.0.0",
    debug=DEBUG,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sophia AI - Minimal Version", 
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "version": "1.0.0",
            "environment": ENVIRONMENT,
            "checks": {
                "environment": "ok",
                "python_version": sys.version.split()[0],
                "api_keys": {
                    "openai": bool(os.getenv("OPENAI_API_KEY")),
                    "anthropic": bool(os.getenv("ANTHROPIC_API_KEY"))
                },
                "services": {
                    "database": "not_configured",
                    "redis": "not_configured", 
                    "memory": "minimal"
                }
            },
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
    """API status endpoint"""
    return {
        "api": "sophia-ai-minimal",
        "version": "1.0.0",
        "status": "minimal",
        "environment": ENVIRONMENT,
        "features": ["health_check", "cors", "basic_routing"],
        "endpoints": ["/", "/health", "/api/status", "/api/test"]
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for functionality"""
    return {
        "test": "successful",
        "message": "Sophia AI minimal backend is working",
        "system": {
            "python_version": sys.version,
            "platform": sys.platform,
            "environment": ENVIRONMENT
        },
        "configuration": {
            "debug": DEBUG,
            "minimal_mode": True
        },
        "environment_vars": {
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
            "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
            "DEBUG": DEBUG
        },
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
    """Application startup"""
    logger.info("🚀 Starting Sophia AI Minimal Platform...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug Mode: {DEBUG}")
    logger.info("✅ Minimal startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("🛑 Shutting down Sophia AI Minimal Platform...")
    logger.info("✅ Shutdown complete!")

if __name__ == "__main__":
    logger.info("🚀 Starting Sophia AI Minimal Backend...")
    
    # Basic environment check
    port = int(os.getenv("PORT", "8002"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Starting server on {host}:{port}")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=DEBUG,
        log_level="info"
    ) 