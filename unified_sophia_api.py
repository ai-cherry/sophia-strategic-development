#!/usr/bin/env python3
"""
UNIFIED SOPHIA AI API - COMPREHENSIVE PLATFORM

This is the main FastAPI application that consolidates ALL Sophia AI functionality
into a single, unified, production-ready API server.
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("unified_sophia_api")

# Global services
chat_service = None
orchestration_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global chat_service, orchestration_service
    
    logger.info("🚀 Starting Unified Sophia AI Platform...")
    
    try:
        # Initialize core services
        from backend.services.enhanced_universal_chat_service import universal_chat_service
        
        # Initialize chat service
        logger.info("🧠 Initializing Unified Chat Service...")
        await universal_chat_service.initialize()
        chat_service = universal_chat_service
        logger.info("✅ Unified Chat Service ready")
        
        logger.info("🎉 Unified Sophia AI Platform is ready!")
        
        yield
        
    except Exception as e:
        logger.error(f"�� Failed to initialize services: {e}")
        raise
    
    finally:
        # Cleanup
        logger.info("🔄 Shutting down Unified Sophia AI Platform...")
        logger.info("👋 Unified Sophia AI Platform shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Sophia AI - Unified Platform",
    description="The comprehensive AI orchestrator for Pay Ready company",
    version="3.18.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
try:
    from backend.api.unified_chat_routes import router as chat_router
    app.include_router(chat_router, tags=["Unified Chat"])
    logger.info("✅ Unified Chat routes loaded")
except Exception as e:
    logger.warning(f"⚠️ Failed to load chat routes: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with platform overview"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sophia AI - Unified Platform</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; }}
            .container {{ max-width: 800px; margin: 0 auto; text-align: center; }}
            .status {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; 
                      margin: 20px 0; backdrop-filter: blur(10px); }}
            .links {{ display: flex; gap: 20px; justify-content: center; margin: 40px 0; }}
            .link {{ background: rgba(255,255,255,0.2); padding: 15px 30px; border-radius: 8px; 
                    text-decoration: none; color: white; transition: all 0.3s; }}
            .link:hover {{ background: rgba(255,255,255,0.3); transform: translateY(-2px); }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Sophia AI - Unified Platform</h1>
            <p>The comprehensive AI orchestrator for Pay Ready company</p>
            
            <div class="status">
                <h3>📊 Platform Status</h3>
                <p><strong>Status:</strong> ✅ Operational</p>
                <p><strong>Version:</strong> 3.18.0</p>
                <p><strong>Last Updated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
            </div>
            
            <div class="links">
                <a href="/docs" class="link">�� API Documentation</a>
                <a href="/health" class="link">🏥 Health Status</a>
                <a href="/api/chat/capabilities" class="link">⚡ Chat Capabilities</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    global chat_service
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.18.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {}
    }
    
    # Check chat service
    if chat_service:
        try:
            chat_health = chat_service.get_health_status()
            health_status["services"]["chat"] = chat_health
        except Exception as e:
            health_status["services"]["chat"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
    else:
        health_status["services"]["chat"] = {"status": "not_initialized"}
        health_status["status"] = "degraded"
    
    return health_status

def main():
    """Main entry point"""
    # Set environment variables
    os.environ.setdefault("ENVIRONMENT", "prod")
    os.environ.setdefault("SOPHIA_AI_TOKEN", "unified_platform_token")
    
    logger.info("🚀 Starting Unified Sophia AI Platform on http://0.0.0.0:8080")
    logger.info("📚 API Documentation available at http://0.0.0.0:8080/docs")
    logger.info("🏥 Health check available at http://0.0.0.0:8080/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
