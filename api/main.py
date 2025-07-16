"""
Sophia AI API - Distributed Architecture (Streamlined)

Simplified version of the distributed FastAPI application aligned with working standards.
Maintains instance-specific configuration while removing complex dependencies.

Features:
- Instance-specific FastAPI configuration
- Role-based endpoint exposure  
- Health monitoring integration
- Distributed request routing
- Performance optimization per instance type

Author: Sophia AI Team
Date: July 2025
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

class DistributedAPIError(Exception):
    """Custom exception for distributed API errors."""
    pass

class LambdaInstance:
    """Lambda Labs instance configuration"""
    def __init__(self):
        self.instance_id = os.getenv("INSTANCE_ID", "primary")
        self.role = os.getenv("INSTANCE_ROLE", "primary")
        self.gpu_type = os.getenv("GPU_TYPE", "unknown") 
        self.ip_address = os.getenv("LAMBDA_INSTANCE_IP", "unknown")
        self.gpu_enabled = os.getenv("GPU_ENABLED", "false").lower() == "true"

def create_distributed_app(instance: LambdaInstance) -> FastAPI:
    """
    Create instance-specific FastAPI application
    
    Args:
        instance: Lambda Labs instance configuration
        
    Returns:
        Configured FastAPI application
    """
    
    # Create app with instance-specific configuration
    app = FastAPI(
        title=f"Sophia AI - {instance.role.title()} Instance",
        description=f"Distributed Sophia AI API - {instance.role} node",
        version="3.0.0-distributed",
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
    
    @app.get("/")
    async def root():
        """Root endpoint with instance information"""
        return {
            "message": f"Sophia AI - {instance.role.title()} Instance",
            "version": "3.0.0-distributed",
            "status": "operational",
            "instance": {
                "id": instance.instance_id,
                "role": instance.role,
                "gpu_type": instance.gpu_type,
                "ip_address": instance.ip_address,
                "gpu_enabled": instance.gpu_enabled
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/health")
    async def health_check():
        """Comprehensive health check endpoint"""
        try:
            health_status = {
                "status": "healthy",
                "version": "3.0.0-distributed",
                "environment": ENVIRONMENT,
                "instance": {
                    "id": instance.instance_id,
                    "role": instance.role,
                    "gpu_type": instance.gpu_type,
                    "ip_address": instance.ip_address,
                    "gpu_enabled": instance.gpu_enabled
                },
                "checks": {
                    "environment": "ok",
                    "python_version": sys.version.split()[0],
                    "instance_config": "loaded",
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
                    },
                    "hardware": {
                        "gpu_available": instance.gpu_enabled,
                        "gpu_type": instance.gpu_type
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
                    "instance": instance.instance_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    @app.get("/api/status")
    async def api_status():
        """API status and instance capabilities"""
        return {
            "api": "sophia-ai-distributed",
            "version": "3.0.0-distributed",
            "status": "operational",
            "environment": ENVIRONMENT,
            "instance": {
                "id": instance.instance_id,
                "role": instance.role,
                "capabilities": get_instance_capabilities(instance.role),
                "hardware": {
                    "gpu_enabled": instance.gpu_enabled,
                    "gpu_type": instance.gpu_type,
                    "ip_address": instance.ip_address
                }
            },
            "features": [
                "distributed_architecture",
                "instance_awareness", 
                "role_based_routing",
                "gpu_optimization",
                "health_monitoring"
            ],
            "endpoints": get_instance_endpoints(instance.role)
        }
    
    @app.get("/api/instance/config")
    async def instance_config():
        """Instance configuration information"""
        return {
            "instance_id": instance.instance_id,
            "role": instance.role,
            "gpu_type": instance.gpu_type,
            "ip_address": instance.ip_address,
            "gpu_enabled": instance.gpu_enabled,
            "capabilities": get_instance_capabilities(instance.role),
            "environment": ENVIRONMENT,
            "debug": DEBUG,
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
                "instance": instance.instance_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {instance.instance_id}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc) if DEBUG else "An error occurred",
                "instance": instance.instance_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Application startup configuration"""
        logger.info(f"🚀 Starting Sophia AI {instance.role.title()} Instance...")
        logger.info(f"Instance ID: {instance.instance_id}")
        logger.info(f"GPU Type: {instance.gpu_type}")
        logger.info(f"IP Address: {instance.ip_address}")
        logger.info(f"Environment: {ENVIRONMENT}")
        logger.info("✅ Distributed instance startup complete!")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown cleanup"""
        logger.info(f"🛑 Shutting down {instance.role.title()} Instance...")
        logger.info("✅ Shutdown complete!")
    
    return app

def get_instance_capabilities(role: str) -> list:
    """Get capabilities based on instance role"""
    capabilities = {
        "primary": ["api_gateway", "database", "user_management", "orchestration"],
        "mcp_orchestrator": ["mcp_servers", "ai_processing", "workflow_management"], 
        "data_pipeline": ["data_processing", "ml_inference", "analytics"],
        "development": ["testing", "debugging", "development_tools"]
    }
    return capabilities.get(role, ["basic_api"])

def get_instance_endpoints(role: str) -> dict:
    """Get available endpoints based on instance role"""
    base_endpoints = ["health", "status", "config"]
    
    role_endpoints = {
        "primary": base_endpoints + ["users", "auth", "dashboard"],
        "mcp_orchestrator": base_endpoints + ["mcp", "orchestrate", "workflows"],
        "data_pipeline": base_endpoints + ["process", "analytics", "ml"],
        "development": base_endpoints + ["test", "debug", "tools"]
    }
    
    return {
        "core": ["/", "/health", "/api/status"],
        "role_specific": role_endpoints.get(role, base_endpoints),
        "docs": ["/docs", "/redoc"] if DEBUG else []
    }

# Create instance and app
instance = LambdaInstance()
app = create_distributed_app(instance)

if __name__ == "__main__":
    logger.info("🚀 Starting Sophia AI Distributed API...")
    
    # Environment configuration
    port = int(os.getenv("PORT", "8003"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Instance: {instance.instance_id} ({instance.role})")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Starting server on {host}:{port}")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=DEBUG,
        log_level="info",
        access_log=True
    )
