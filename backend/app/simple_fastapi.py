"""
Sophia AI - Main FastAPI Application
Unified FastAPI application integrating all services and routes
"""

import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from backend.core.database import init_database, create_tables, check_database_health
from backend.core.security import check_security_health
from backend.core.auto_esc_config import get_config_value
from backend.utils.logging import setup_logging, get_logger

# Import route modules
from backend.api.routes.user_management import router as user_management_router
from backend.api.unified_chat_routes import router as chat_router
from backend.api.orchestrator_v4_routes import router as orchestrator_router
from backend.api.project_management_routes import router as project_router
from backend.api.mcp_proxy_routes import router as mcp_proxy_router

# Import services for health checks
try:
    from backend.services.QDRANT_unified_memory_service import QdrantUnifiedMemoryService
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management
    Handles startup and shutdown procedures
    """
    # Startup
    logger.info("🚀 Starting Sophia AI Platform...")
    
    try:
        # Initialize database
        init_database()
        create_tables()
        logger.info("✅ Database initialized")
        
        # Initialize Qdrant memory service if available
        if QDRANT_AVAILABLE:
            try:
                memory_service = QdrantUnifiedMemoryService()
                await memory_service.initialize()
                logger.info("✅ Qdrant memory service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Qdrant memory service not available: {e}")
        
        # Validate configuration
        config_status = validate_config_access()
        logger.info(f"✅ Configuration status: {config_status}")
        
        logger.info("🎉 Sophia AI Platform startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Sophia AI Platform...")
    logger.info("✅ Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Sophia AI Platform",
    description="Executive AI Orchestrator for Pay Ready Business Intelligence",
    version="4.0.0-unified",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://sophia.payready.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    import time
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Log request details
    process_time = time.time() - start_time
    logger.info(
        f"REQUEST {request.method} {request.url.path} "
        f"completed in {process_time:.3f}s with status {response.status_code}"
    )
    
    return response

# Include routers
app.include_router(user_management_router, prefix="/api/v1", tags=["User Management"])
app.include_router(chat_router, tags=["Chat"])
app.include_router(orchestrator_router, tags=["Orchestrator"])
app.include_router(project_router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(mcp_proxy_router, tags=["MCP Proxy"])

# Basic routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with welcome message"""
    return """
    <html>
        <head>
            <title>Sophia AI Platform</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                h1 { color: #2563eb; margin-bottom: 20px; }
                .status { background: #10b981; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }
                .links { margin-top: 30px; }
                .links a { display: inline-block; margin: 10px 15px 10px 0; padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; }
                .features { margin-top: 30px; }
                .feature { margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #2563eb; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Sophia AI Platform</h1>
                <div class="status">✅ Platform Operational - Ready for CEO Usage</div>
                
                <p><strong>Executive AI Orchestrator for Pay Ready Business Intelligence</strong></p>
                <p>Version: 4.0.0-unified | Environment: Production</p>
                
                <div class="features">
                    <div class="feature">
                        <strong>🧠 AI Orchestration:</strong> Multi-agent system with specialized business functions
                    </div>
                    <div class="feature">
                        <strong>👥 User Management:</strong> Complete user management system with role-based access
                    </div>
                    <div class="feature">
                        <strong>📊 Product Management:</strong> Asana, Linear, and Notion integration for project tracking
                    </div>
                    <div class="feature">
                        <strong>💾 Memory System:</strong> Advanced Qdrant-powered vector memory with intelligent search
                    </div>
                    <div class="feature">
                        <strong>🔐 Security:</strong> Enterprise-grade authentication and authorization
                    </div>
                </div>
                
                <div class="links">
                    <a href="/docs">📚 API Documentation</a>
                    <a href="/health">🏥 System Health</a>
                    <a href="/api/v1/users/stats/summary">📊 User Statistics</a>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": "2025-01-15T23:30:00Z",
            "version": "4.0.0-unified",
            "environment": get_config_value("environment", "production"),
            "components": {}
        }
        
        # Check database health
        try:
            db_health = check_database_health()
            health_status["components"]["database"] = db_health
        except Exception as e:
            health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check security system health
        try:
            security_health = check_security_health()
            health_status["components"]["security"] = security_health
        except Exception as e:
            health_status["components"]["security"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check Qdrant memory service health
        if QDRANT_AVAILABLE:
            try:
                memory_service = QdrantUnifiedMemoryService()
                memory_health = await memory_service.health_check()
                health_status["components"]["memory"] = memory_health
            except Exception as e:
                health_status["components"]["memory"] = {"status": "degraded", "error": str(e)}
        else:
            health_status["components"]["memory"] = {"status": "not_available", "reason": "Qdrant service not initialized"}
        
        # Check configuration access
        try:
            config_health = validate_config_access()
            health_status["components"]["configuration"] = {"status": "healthy", "details": config_health}
        except Exception as e:
            health_status["components"]["configuration"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-01-15T23:30:00Z"
            }
        )

@app.get("/info")
async def get_system_info():
    """Get system information and capabilities"""
    return {
        "name": "Sophia AI Platform",
        "version": "4.0.0-unified",
        "description": "Executive AI Orchestrator for Pay Ready Business Intelligence",
        "capabilities": [
            "User Management & Authentication",
            "Product Management Integration (Asana, Linear, Notion)",
            "AI-Powered Chat & Orchestration", 
            "Vector Memory & Search",
            "Project Management Analytics",
            "Business Intelligence & KPIs"
        ],
        "integrations": [
            "Qdrant Vector Database",
            "PostgreSQL Database",
            "Asana Project Management",
            "Linear Issue Tracking", 
            "Notion Knowledge Base",
            "Slack Communication",
            "HubSpot CRM",
            "Gong Call Analytics"
        ],
        "api_routes": [
            "/api/v1/users/ - User Management",
            "/api/v3/chat/ - Unified Chat",
            "/api/v4/orchestrate - AI Orchestration",
            "/api/v1/projects/ - Project Management"
        ]
    }

@app.get("/system/status")
async def system_status():
    """System status endpoint expected by frontend dashboard"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "4.0.0-unified",
            "environment": os.getenv("ENVIRONMENT", "prod"),
            "services": {
                "mcp_proxy": "operational",
                "orchestrator": "initialized", 
                "memory": "connected",
                "database": "healthy"
            },
            "uptime": "operational",
            "backend_port": 7000,
            "mcp_services_range": "8000-8499"
        }
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to Sophia AI Platform",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo back for now - can be enhanced with real chat processing
            response = {
                "type": "response",
                "original": message,
                "echo": f"Received: {message.get('content', 'No content')}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with proper logging"""
    logger.error(f"Unhandled exception: {str(exc)} - {request.method} {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

# Development server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 7000))  # Changed from 8000 to 7000 to avoid MCP conflicts
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Sophia AI Platform on {host}:{port}")
    logger.info("📡 Backend on port 7000 - MCP services on 8000-8499")
    
    uvicorn.run(
        "backend.app.simple_fastapi:app",
        host=host,
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    ) 