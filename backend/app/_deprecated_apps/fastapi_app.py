"""
Sophia AI FastAPI Application

Modernized FastAPI application using lifespan events and proper dependency injection.
Eliminates circular imports and follows Clean Architecture principles.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core imports
from backend.core.simple_config import get_config_value
from backend.core.dependencies import get_chat_service

# Route imports - no circular dependencies
from backend.api import enhanced_ceo_chat_routes
from backend.api import simplified_llm_routes
from backend.api import unified_intelligence_routes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event handlers.
    """
    # Startup
    logger.info("🚀 Starting Sophia AI Unified Ecosystem...")
    
    try:
        # Initialize the simplified unified intelligence service
        from backend.services.simplified_unified_intelligence_service import get_simplified_unified_intelligence_service
        unified_service = await get_simplified_unified_intelligence_service()
        app.state.unified_intelligence = unified_service
        logger.info("✅ Simplified Unified Intelligence Service initialized")
        
        # Initialize the chat service and store in app state
        chat_service = await get_chat_service()
        app.state.chat_service_instance = chat_service
        logger.info("✅ Chat Service initialized")
        
        # Test configuration loading
        config_test = get_config_value("values_sophia_ai_openai_api_key", "")
        if config_test:
            logger.info("✅ Configuration loaded successfully")
        else:
            logger.warning("⚠️ No OpenAI API key found - running in limited mode")
        
        logger.info("✅ Sophia AI Unified Ecosystem startup complete")
        
        # Yield control to the application
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Still yield to prevent startup failure
        yield
    
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Sophia AI Unified Ecosystem...")
        
        # Cleanup services if they exist
        for service_name in ['unified_intelligence', 'chat_service_instance']:
            if hasattr(app.state, service_name):
                try:
                    delattr(app.state, service_name)
                    logger.info(f"✅ {service_name} cleaned up")
                except Exception as e:
                    logger.error(f"⚠️ Error during {service_name} cleanup: {e}")
        
        logger.info("✅ Sophia AI Unified Ecosystem shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Sophia AI Platform",
    description="AI-powered business intelligence and automation platform",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sophia AI Platform",
        "version": "2.0.0",
        "timestamp": asyncio.get_event_loop().time()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Sophia AI Platform",
        "version": "2.0.0",
        "docs_url": "/docs",
        "health_url": "/health"
    }

# Include routers
app.include_router(enhanced_ceo_chat_routes.router, prefix="/api/v1/ceo", tags=["CEO Dashboard"])
app.include_router(simplified_llm_routes.router, prefix="/api/v1/llm", tags=["LLM Strategy"])
app.include_router(unified_intelligence_routes.router, tags=["Unified Intelligence"])

def run_server():
    """Run the server with proper configuration"""
    uvicorn.run(
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()
