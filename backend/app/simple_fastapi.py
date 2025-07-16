"""
Sophia AI - Simple FastAPI Application
Aligned version that works with current dependencies
Based on working_fastapi.py with simplified configuration
"""

import os
import sys
import logging
from typing import Dict, Any
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
    title="Sophia AI - Simple Platform",
    description="Simple Sophia AI Platform API",
    version="2.0.0",
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
        "message": "Sophia AI - Simple Platform",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "version": "2.0.0",
            "environment": ENVIRONMENT,
            "checks": {
                "environment": "ok",
                "python_version": sys.version.split()[0],
                "api_keys": {
                    "openai": bool(os.getenv("OPENAI_API_KEY")),
                    "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                    "gong": bool(os.getenv("GONG_API_KEY"))
                },
                "services": {
                    "database": "available" if os.getenv("DATABASE_URL") else "not_configured",
                    "redis": "available" if os.getenv("REDIS_URL") else "not_configured"
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
        "api": "sophia-ai-simple",
        "version": "2.0.0",
        "status": "operational",
        "environment": ENVIRONMENT,
        "features": ["health_check", "cors", "basic_api"],
        "endpoints": ["/", "/health", "/api/status", "/api/test"]
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "test": "successful",
        "message": "Sophia AI simple backend is working",
        "system": {
            "python_version": sys.version,
            "environment": ENVIRONMENT
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
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 Starting Sophia AI Simple Platform...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug Mode: {DEBUG}")
    logger.info("✅ Startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("🛑 Shutting down Sophia AI Simple Platform...")
    logger.info("✅ Shutdown complete!")

if __name__ == "__main__":
    logger.info("🚀 Starting Sophia AI Simple Backend...")
    
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=DEBUG,
        log_level="info"
    ) 