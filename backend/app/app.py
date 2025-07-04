"""
Sophia AI Unified Application
============================

Single source of truth for all backend services.
This is the ONLY production application entry point.

Created: July 4, 2025
Usage:
    uvicorn backend.app.app:app --host 0.0.0.0 --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core imports
from backend.api import unified_routes

logger = logging.getLogger(__name__)

# Global service instances
services = {}


async def initialize_core_services():
    """Initialize core services with proper error handling"""
    try:
        # Initialize chat service
        from backend.services.unified_chat_service import UnifiedChatService

        services["chat"] = UnifiedChatService()
        logger.info("✅ Chat service initialized")

        # Initialize knowledge service if available
        try:
            from backend.services.foundational_knowledge_service import (
                FoundationalKnowledgeService,
            )

            services["knowledge"] = FoundationalKnowledgeService()
            logger.info("✅ Knowledge service initialized")
        except ImportError:
            logger.warning("⚠️ Knowledge service not available")

        # Initialize LLM service if available
        try:
            from backend.services.unified_llm_service import get_unified_llm_service

            services["llm"] = await get_unified_llm_service()
            logger.info("✅ LLM service initialized")
        except ImportError:
            logger.warning("⚠️ LLM service not available")

    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        raise


async def start_health_monitoring():
    """Start health monitoring if available"""
    try:
        from backend.monitoring.health_monitor import HealthMonitor

        services["health_monitor"] = HealthMonitor()
        await services["health_monitor"].start()
        logger.info("✅ Health monitoring started")
    except ImportError:
        logger.warning("⚠️ Health monitoring not available")
    except Exception as e:
        logger.error(f"❌ Error starting health monitoring: {e}")


async def cleanup_services():
    """Cleanup services on shutdown"""
    for service_name, service in services.items():
        try:
            if hasattr(service, "cleanup"):
                await service.cleanup()
            elif hasattr(service, "close"):
                await service.close()
            logger.info(f"✅ {service_name} cleaned up")
        except Exception as e:
            logger.error(f"❌ Error cleaning up {service_name}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting Sophia AI Platform...")

    # Initialize services
    await initialize_core_services()

    # Start health monitoring
    await start_health_monitoring()

    logger.info("✅ Sophia AI Platform started successfully")

    yield

    # Cleanup
    logger.info("🛑 Shutting down Sophia AI Platform...")
    await cleanup_services()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sophia AI Platform",
    description="Unified AI Orchestrator for Pay Ready - Single Source of Truth",
    version="3.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(unified_routes.router, prefix="/api/v1", tags=["API v1"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Sophia AI Platform",
        "version": "3.0.0",
        "status": "operational",
        "message": "Unified AI Orchestrator for Pay Ready",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "timestamp": datetime.now(UTC).isoformat(),
        "date": "2025-07-04",  # Today's date
    }


# Health endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "sophia-ai",
            "version": "3.0.0",
            "timestamp": datetime.now(UTC).isoformat(),
            "services": {
                name: "operational" if service else "not_initialized"
                for name, service in services.items()
            },
        },
    )


# API health endpoint
@app.get("/api/health")
async def api_health():
    """API health check endpoint"""
    return await health()


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info"
    )
