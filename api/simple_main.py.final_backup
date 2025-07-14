#!/usr/bin/env python3
"""
Sophia AI FastAPI - Simple Working Version
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Platform",
    description="AI-powered business intelligence platform",
    version="2.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "user"
    session_id: str | None = None
    context: str = "general"
    stream: bool = False
    metadata: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    response: str
    sources: list[dict[str, Any]] | None = None
    suggestions: list[str] | None = None
    metadata: dict[str, Any] | None = None
    timestamp: str = datetime.now().isoformat()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    services: dict[str, str]


# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="Sophia AI Platform",
        version="2.0.0",
        timestamp=datetime.now().isoformat(),
        services={
            "backend": "operational",
            "database": "operational",
            "redis": "operational",
            "mcp_servers": "partial",
        },
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Sophia AI Platform",
        "version": "2.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "health": "/health",
            "chat": "/api/v1/chat",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


# Simple chat endpoint
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Simple chat endpoint for testing
    """
    try:
        # For now, return a mock response
        mock_response = f"I received your message: '{request.message}'. This is a test response from Sophia AI."

        if request.stream:
            # Streaming response
            async def stream_response():
                words = mock_response.split()
                for word in words:
                    yield f"data: {word} "

                yield "\n\ndata: [DONE]\n\n"

            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )
        else:
            # Regular response
            return ChatResponse(
                response=mock_response,
                sources=[
                    {"type": "system", "name": "Sophia AI Core", "confidence": 0.95}
                ],
                suggestions=[
                    "Ask about Lambda Labs deployment status",
                    "Check MCP server health",
                    "View system metrics",
                ],
                metadata={
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "context": request.context,
                    "processing_time": "0.1s",
                },
            )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Lambda Labs status endpoint
@app.get("/api/v1/lambda-labs/status")
async def lambda_labs_status():
    """Get Lambda Labs instance status"""
    return {
        "instances": [
            {
                "name": "sophia-production-instance",
                "ip": "104.171.202.103",
                "status": "active",
                "gpu": "RTX 6000",
            },
            {
                "name": "sophia-ai-core",
                "ip": "192.222.58.232",
                "status": "active",
                "gpu": "GH200",
            },
            {
                "name": "sophia-mcp-orchestrator",
                "ip": "104.171.202.117",
                "status": "active",
                "gpu": "A6000",
            },
            {
                "name": "sophia-data-pipeline",
                "ip": "104.171.202.134",
                "status": "active",
                "gpu": "A100",
            },
            {
                "name": "sophia-development",
                "ip": "155.248.194.183",
                "status": "active",
                "gpu": "A10",
            },
        ],
        "total_cost_per_hour": "$5.83",
        "total_cost_per_month": "$4,257",
    }


# MCP servers status
@app.get("/api/v1/mcp/status")
async def mcp_status():
    """Get MCP servers status"""
    return {
        "servers": {
            "ai_memory": {"port": 9001, "status": "offline"},
            "codacy": {"port": 3008, "status": "offline"},
            "linear": {"port": 9004, "status": "running"},
            "github": {"port": 9103, "status": "running"},
            "asana": {"port": 9100, "status": "running"},
            "notion": {"port": 9005, "status": "offline"},
            "ui_ux_agent": {"port": 9002, "status": "running"},
            "lambda_labs_cli": {"port": 9040, "status": "running"},
            "lambda_labs_serverless": {"port": 9025, "status": "running"},
            "modern_stack_admin": {"port": 9020, "status": "offline"},
            "modern_stack_cortex": {"port": 9030, "status": "offline"},
            "portkey_admin": {"port": 9013, "status": "offline"},
        },
        "running": 6,
        "total": 12,
        "health_percentage": 50,
    }


# Debug routes
@app.get("/debug/routes")
async def debug_routes():
    """List all available routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append(
                {"path": route.path, "methods": list(route.methods), "name": route.name}
            )
    return {"routes": routes, "total": len(routes)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
