#!/usr/bin/env python3
"""
CEO Dashboard FastAPI Application
=================================

Simple FastAPI app focused on CEO dashboard functionality:
1. Chat/Search Interface with natural language processing
2. Project Management Dashboard (Linear + Asana + Notion)
3. Sales Coach Agent (Slack + HubSpot + Gong.io)
4. Real-time business intelligence and executive insights
"""

import logging
import time
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import CEO dashboard routes
from backend.api.ceo_dashboard_routes import router as ceo_router

logger = logging.getLogger(__name__)

def create_ceo_dashboard_app() -> FastAPI:
    """Create and configure the CEO Dashboard FastAPI application"""
    
    # Create FastAPI app
    app = FastAPI(
        title="Sophia AI CEO Dashboard",
        description="AI-powered CEO dashboard with chat, project management, and sales coaching",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request tracking middleware
    @app.middleware("http")
    async def add_request_tracking(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Enhanced error handling
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        logger.error(
            f"Unhandled exception: {exc}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error": str(exc),
            },
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    # Include CEO dashboard router
    app.include_router(ceo_router)

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "sophia-ai-ceo-dashboard", "version": "1.0.0"}

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to Sophia AI CEO Dashboard",
            "docs": "/docs",
            "health": "/health",
            "features": [
                "CEO Chat Interface",
                "Project Management Dashboard", 
                "Sales Coaching Analytics",
                "Business Intelligence"
            ]
        }

    logger.info("✅ CEO Dashboard FastAPI application created and configured")
    return app

# Create the application instance
app = create_ceo_dashboard_app()

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Sophia AI CEO Dashboard...")
    uvicorn.run(
        "backend.app.ceo_dashboard_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 