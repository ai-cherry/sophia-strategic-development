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
from backend.services.foundational_knowledge_service import FoundationalKnowledgeService
from backend.services.unified_llm_service import get_unified_llm_service
from backend.services.unified_sophia_service import get_unified_sophia_service

logger = logging.getLogger(__name__)

# Global service instances
services = {}


async def initialize_core_services():
    """Initialize core services with proper error handling"""
    try:
        # Initialize the unified Sophia service
        services["sophia"] = get_unified_sophia_service()
        await services["sophia"].initialize()
        logger.info("✅ Unified Sophia Service initialized")

        # Initialize knowledge service if available
        try:
            services["knowledge"] = FoundationalKnowledgeService()
            logger.info("✅ Knowledge service initialized")
        except ImportError:
            logger.warning("⚠️ Knowledge service not available")

        # Initialize LLM service if available
        try:
            services["llm"] = await get_unified_llm_service()
            logger.info("✅ LLM service initialized")
        except ImportError:
            logger.warning("⚠️ LLM service not available")

    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        raise


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


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan manager"""
        logger.info("🚀 Starting up Sophia AI Platform...")
        await initialize_core_services()
        yield
        logger.info("🌙 Shutting down Sophia AI Platform...")
        await cleanup_services()

    app = FastAPI(
        title="Sophia AI Platform",
        description="Unified API for all Sophia AI services",
        version="3.0.0",
        lifespan=lifespan,
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(unified_routes.router)

    @app.get("/", tags=["Root"])
    async def read_root():
        """Root endpoint"""
        return {
            "service": "Sophia AI Platform",
            "version": "3.0.0",
            "status": "operational",
            "message": "Unified AI Orchestrator for Pay Ready",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "timestamp": datetime.now(UTC).isoformat(),
            "date": "2025-07-04",
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

    return app


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        create_app(),
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info",
    )
