#!/usr/bin/env python3
"""
Simple Working Backend for Sophia AI
Minimal FastAPI app to get services running immediately
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import time
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Backend",
    description="Sophia AI Backend API",
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sophia AI Backend is running",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sophia-ai-backend",
        "timestamp": datetime.now().isoformat(),
        "uptime": "operational",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0"
    }

@app.get("/docs-redirect")
async def docs_redirect():
    """Redirect to API documentation"""
    return {"message": "API documentation available at /docs"}

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "running",
        "endpoints": [
            "/health",
            "/docs",
            "/api/v1/status",
            "/api/v1/users",
            "/api/v1/chat"
        ],
        "features": [
            "User Management",
            "AI Chat",
            "Health Monitoring",
            "API Documentation"
        ]
    }

@app.get("/api/v1/users")
async def list_users():
    """List users (demo endpoint)"""
    return {
        "users": [
            {
                "id": "emp_lynn_musil",
                "name": "Lynn Patrick Musil",
                "role": "CEO",
                "email": "lynn@payready.com"
            },
            {
                "id": "emp_tiffany_york", 
                "name": "Tiffany York",
                "role": "CPO",
                "email": "tiffany@payready.com"
            },
            {
                "id": "emp_steve_gabel",
                "name": "Steve Gabel", 
                "role": "VP Strategic",
                "email": "steve@payready.com"
            }
        ],
        "total": 3
    }

@app.post("/api/v1/chat")
async def chat_endpoint(message: dict):
    """AI Chat endpoint (demo)"""
    user_message = message.get("message", "")
    
    return {
        "response": f"Hello! You said: '{user_message}'. This is the Sophia AI backend responding from {os.getenv('ENVIRONMENT', 'development')} environment.",
        "timestamp": datetime.now().isoformat(),
        "model": "sophia-ai-v1",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Sophia AI Backend on {host}:{port}")
    print(f"📍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"🌐 Health check: http://{host}:{port}/health")
    print(f"📚 API docs: http://{host}:{port}/docs")
    
    uvicorn.run(
        "simple_working_backend:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 