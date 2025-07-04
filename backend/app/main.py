"""
Sophia AI Main Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.unified_routes import router as unified_router
from backend.services.unified_chat_service import UnifiedChatService

logger = logging.getLogger(__name__)

# Global service instances
chat_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global chat_service

    logger.info("🚀 Starting Sophia AI Platform...")

    # Initialize services
    chat_service = UnifiedChatService()
    await chat_service.initialize()

    logger.info("✅ Sophia AI Platform started successfully")

    yield

    # Cleanup
    logger.info("🛑 Shutting down Sophia AI Platform...")
    if hasattr(chat_service, "cleanup"):
        await chat_service.cleanup()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sophia AI Platform",
    description="Unified AI Platform with single dashboard and chat interface",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(unified_router, tags=["API"])


# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "message": "Sophia AI Platform - Unified Architecture",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "chat": "operational"
            if chat_service and chat_service.initialized
            else "not_initialized"
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
