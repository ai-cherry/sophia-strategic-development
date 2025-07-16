"""
Sophia AI - Development FastAPI Application
Simplified version for development testing without database dependencies
"""

import json
import logging
import os
import sys
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Sophia AI Platform - Development",
    description="Executive AI Orchestrator for Pay Ready Business Intelligence - Development Mode",
    version="4.0.0-unified-dev",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add large file ingestion routes
try:
    from backend.api.large_file_routes import router as large_file_router
    app.include_router(large_file_router)
    logger.info("✅ Large File Ingestion routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Large File Ingestion routes not available: {e}")

# Add enhanced platform integration routes
try:
    from backend.api.enhanced_platform_routes import router as enhanced_platform_router
    app.include_router(enhanced_platform_router)
    logger.info("✅ Enhanced Platform Integration routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced Platform Integration routes not available: {e}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
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

# Basic routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with welcome message"""
    return """
    <html>
        <head>
            <title>Sophia AI Platform - Development</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                h1 { color: #2563eb; margin-bottom: 20px; }
                .status { background: #10b981; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }
                .dev-notice { background: #f59e0b; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }
                .links { margin-top: 30px; }
                .links a { display: inline-block; margin: 10px 15px 10px 0; padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Sophia AI Platform - Development Mode</h1>
                <div class="dev-notice">
                    🚧 Development Mode: Database dependencies bypassed for testing
                </div>
                <div class="status">
                    ✅ Backend operational on port 7000
                </div>
                <p>Unified executive AI orchestrator for Pay Ready business intelligence, now ready for frontend testing.</p>
                
                <div class="links">
                    <a href="/docs">🔍 API Documentation</a>
                    <a href="/health">❤️ Health Check</a>
                    <a href="/system/status">📊 System Status</a>
                </div>
                
                <h3>🔧 Development Features</h3>
                <ul>
                    <li>✅ Frontend-Backend Connection</li>
                    <li>✅ WebSocket Real-Time Communication</li>
                    <li>✅ MCP Proxy Routing (Mock)</li>
                    <li>✅ System Status Endpoints</li>
                    <li>⚠️ Database Dependencies: Bypassed</li>
                </ul>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "development",
        "database": "bypassed"
    }

@app.get("/system/status")
async def system_status():
    """System status endpoint expected by frontend dashboard"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "4.0.0-unified-dev",
            "environment": "development",
            "mode": "dev-testing",
            "services": {
                "mcp_proxy": "operational",
                "orchestrator": "initialized", 
                "memory": "mocked",
                "database": "bypassed"
            },
            "uptime": "operational",
            "backend_port": 7000,
            "mcp_services_range": "8000-8499",
            "frontend_connection": "ready"
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

@app.post("/chat")
async def mock_chat(request: Request):
    """Mock chat endpoint for frontend testing"""
    try:
        body = await request.json()
        message = body.get("message", "")
        
        # Mock response
        return {
            "response": f"🤖 Mock Response: Received your message '{message}'. This is a development response to test frontend connectivity.",
            "sources": ["development_mock"],
            "insights": ["Frontend-backend connection working", "WebSocket ready for real-time"],
            "recommendations": ["Test WebSocket connection", "Verify MCP proxy routes"],
            "metadata": {
                "mode": "development",
                "timestamp": datetime.utcnow().isoformat(),
                "backend_port": 7000
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
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
            "message": "Connected to Sophia AI Platform - Development Mode",
            "timestamp": datetime.utcnow().isoformat(),
            "backend_port": 7000,
            "mode": "development"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Mock real-time response
            response = {
                "type": "response",
                "original": message,
                "echo": f"🔄 Real-time Echo: {message.get('content', 'No content')}",
                "status": "Development mode - WebSocket working correctly",
                "timestamp": datetime.utcnow().isoformat(),
                "backend_port": 7000
            }
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

# Mock MCP proxy routes for testing
@app.get("/api/v4/mcp/health/all")
async def mock_mcp_health():
    """Mock MCP services health check"""
    return {
        "overall_status": "development",
        "health_rate": 100.0,
        "healthy_services": 5,
        "total_services": 5,
        "services": {
            "gong_mcp": {"status": "mocked"},
            "linear_mcp": {"status": "mocked"},
            "asana_mcp": {"status": "mocked"},
            "hubspot_mcp": {"status": "mocked"},
            "slack_mcp": {"status": "mocked"}
        },
        "note": "Development mode - MCP services mocked for frontend testing"
    }

@app.get("/api/v4/mcp/{service_name}/health")
async def mock_mcp_service_health(service_name: str):
    """Mock individual MCP service health"""
    return {
        "service": service_name,
        "status": "mocked",
        "mode": "development",
        "timestamp": datetime.utcnow().isoformat()
    }

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
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Sophia AI Platform (Development) on {host}:{port}")
    logger.info("🔧 Development Mode: Database dependencies bypassed")
    logger.info("📡 Backend on port 7000 - Frontend can connect and test")
    
    uvicorn.run(
        "backend.app.simple_dev_fastapi:app",
        host=host,
        port=port,
        reload=True,  # Enable reload in development
        log_level="info"
    ) 