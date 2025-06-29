"""
FastAPI Application Factory
Creates and configures the main FastAPI application instance for Sophia AI
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from backend.presentation.api.router import create_application_router
from backend.core.startup_config import apply_startup_configuration

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Sophia AI FastAPI application...")

    try:
        # Initialize any startup tasks here
        logger.info("✅ Application startup complete")
        yield
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🔄 Shutting down Sophia AI application...")
        logger.info("✅ Application shutdown complete")


def create_fastapi_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    # Apply startup configuration for Snowflake fix
    apply_startup_configuration()

    # Create FastAPI app with lifespan management
    app = FastAPI(
        title="Sophia AI Platform",
        description="AI-powered business intelligence and automation platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Include application router
    app.include_router(create_application_router())

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "sophia-ai", "version": "1.0.0"}

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to Sophia AI Platform",
            "docs": "/docs",
            "health": "/health",
        }

    logger.info("✅ FastAPI application created and configured")
    return app


# Create the application instance
app = create_fastapi_app()
