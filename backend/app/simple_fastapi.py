"""
Simple FastAPI Application for Sophia AI Demo
============================================
Minimal working FastAPI app without complex dependencies
"""

import logging
import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Sophia AI - Simple Demo",
    description="Minimal working Sophia AI backend for demo purposes",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sophia AI - Simple Demo Backend",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": {"status": "healthy"},
            "core": {"status": "healthy"},
        },
    }


@app.post("/chat")
async def simple_chat(request: dict):
    """
    Simple chat endpoint for demo
    
    Accepts: {"message": "your question here"}
    Returns: {"response": "AI response", "metadata": {...}}
    """
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Simple echo response for demo
        response = f"Echo: {message} (This is a demo response from Sophia AI)"

        return {
            "response": response,
            "metadata": {
                "provider": "demo",
                "model_used": "echo-model",
                "response_time": 0.1,
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard")
async def dashboard():
    """Simple dashboard data"""
    return {
        "title": "Sophia AI Dashboard",
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "total_requests": 42,
            "success_rate": 0.98,
            "average_response_time": 0.15,
            "uptime": "99.9%",
        },
        "status": "All systems operational",
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 