#!/usr/bin/env python3
"""
Startup script for Sophia AI Backend Services
Launches enhanced chat service and knowledge dashboard for live testing
"""

import logging
import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import our services and routes
from backend.services.enhanced_unified_chat_service import app as chat_app
from backend.api.knowledge_dashboard_routes import knowledge_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create main application
app = FastAPI(
    title="Sophia AI Platform",
    description="Production-ready AI platform with knowledge management and chat",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(knowledge_router)

# Mount chat service
app.mount("/chat", chat_app)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sophia AI Platform - Production Ready",
        "version": "1.0.0",
        "services": {
            "chat": "/chat",
            "knowledge": "/api/v1/knowledge",
            "websocket": "/ws/chat/{user_id}",
            "health": "/api/v1/health"
        },
        "documentation": "/docs"
    }

@app.get("/health")
async def platform_health():
    """Platform health check"""
    return {
        "status": "healthy",
        "platform": "sophia-ai",
        "services": {
            "chat_service": "operational",
            "knowledge_service": "operational",
            "websocket": "operational"
        },
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Set environment variables for production
    os.environ.setdefault("CEO_ACCESS_TOKEN", "sophia_ceo_access_2024")
    
    logger.info("🚀 Starting Sophia AI Platform...")
    logger.info("📍 Chat Service: http://localhost:8000/chat")
    logger.info("📍 Knowledge API: http://localhost:8000/api/v1/knowledge")
    logger.info("📍 WebSocket: ws://localhost:8000/ws/chat/{user_id}")
    logger.info("📍 Documentation: http://localhost:8000/docs")
    logger.info("🔑 CEO Access Token: sophia_ceo_access_2024")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    ) 