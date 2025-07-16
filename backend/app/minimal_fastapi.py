"""
Minimal Sophia AI FastAPI Application
Simple version that can start without complex dependencies
"""

import os
import sys
import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI - Minimal",
    description="Minimal Sophia AI API",
    version="2.1.0"
)

# Add CORS middleware
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
    return {"message": "Sophia AI - Minimal Version", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "version": "2.1.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "checks": {
                "database": "not_configured",
                "redis": "not_configured", 
                "api_keys": bool(os.getenv("OPENAI_API_KEY")),
                "memory": "available"
            },
            "timestamp": "2025-07-16",
            "deployment": "minimal"
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-07-16"
            }
        )

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "sophia-ai",
        "version": "2.1.0",
        "status": "minimal",
        "features": ["health_check", "cors", "basic_routing"],
        "endpoints": ["/", "/health", "/api/status"]
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for functionality"""
    return {
        "test": "successful",
        "message": "Sophia AI minimal backend is working",
        "python_version": sys.version,
        "environment_vars": {
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
            "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
            "DEBUG": os.getenv("DEBUG", "false")
        }
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Sophia AI Minimal Backend...")
    
    # Basic environment check
    env = os.getenv("ENVIRONMENT", "development")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Environment: {env}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Starting server on {host}:{port}")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 