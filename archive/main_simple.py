"""Simplified Sophia AI Backend - Main Entry Point
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Sophia AI Backend...")
    yield
    logger.info("Shutting down Sophia AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="Sophia AI Backend",
    description="AI-powered business intelligence platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers that exist
try:
    from backend.app.routes import executive_routes

    app.include_router(
        executive_routes.router, prefix="/executive", tags=["Executive Intelligence"]
    )
except ImportError as e:
    logger.warning(f"Could not import executive_routes: {e}")

try:
    from backend.app.routes import retool_api_routes

    app.include_router(retool_api_routes.router, prefix="/api", tags=["Retool API"])
except ImportError as e:
    logger.warning(f"Could not import retool_api_routes: {e}")

try:
    from backend.app.routes import system_intel_routes

    app.include_router(
        system_intel_routes.router, prefix="/api", tags=["System Intelligence"]
    )
except ImportError as e:
    logger.warning(f"Could not import system_intel_routes: {e}")

try:
    from backend.app.routers import agno_router

    app.include_router(agno_router.router, prefix="/agno", tags=["AGNO"])
except ImportError as e:
    logger.warning(f"Could not import agno_router: {e}")

try:
    from backend.app.routers import llamaindex_router

    app.include_router(
        llamaindex_router.router, prefix="/llamaindex", tags=["LlamaIndex"]
    )
except ImportError as e:
    logger.warning(f"Could not import llamaindex_router: {e}")


# Basic routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sophia AI Backend",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "sophia-backend",
    }


@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for Retool"""
    return {
        "success": True,
        "message": "API is working",
        "data": {
            "test": "Hello from Sophia AI",
            "timestamp": datetime.now().isoformat(),
        },
    }


# CEO Dashboard specific endpoints
@app.get("/api/executive/summary")
async def get_executive_summary():
    """Get executive summary for CEO dashboard"""
    return {
        "success": True,
        "data": {
            "revenue": {"current_month": 125000, "last_month": 115000, "growth": 8.7},
            "clients": {"total": 45, "new_this_month": 3, "at_risk": 2},
            "team_performance": {
                "calls_completed": 127,
                "demos_scheduled": 23,
                "close_rate": 0.34,
            },
            "key_metrics": [
                {"name": "MRR", "value": 125000, "change": 8.7},
                {"name": "Active Clients", "value": 45, "change": 7.1},
                {"name": "NPS Score", "value": 72, "change": 3.2},
            ],
        },
    }


@app.get("/api/executive/alerts")
async def get_executive_alerts():
    """Get alerts for executive dashboard"""
    return {
        "success": True,
        "alerts": [
            {
                "id": 1,
                "type": "opportunity",
                "priority": "high",
                "message": "Large enterprise deal worth $50k/month in final negotiation",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "id": 2,
                "type": "risk",
                "priority": "medium",
                "message": "Client ABC Corp showing decreased usage - intervention recommended",
                "timestamp": datetime.now().isoformat(),
            },
        ],
    }


if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))

    # Run the server
    uvicorn.run(
        "main_simple:app", host="0.0.0.0", port=port, reload=True, log_level="info"
    )
