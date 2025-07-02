#!/usr/bin/env python3
"""
Test CEO Dashboard Server
========================

Simple test server for CEO dashboard API endpoints
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the CEO dashboard routes
from backend.api.ceo_dashboard_unified_routes import router as ceo_router

app = FastAPI(
    title="CEO Dashboard Test Server",
    description="Test server for CEO dashboard API endpoints",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the CEO dashboard routes
app.include_router(ceo_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CEO Dashboard Test Server",
        "status": "running",
        "endpoints": {
            "chat": "/api/v1/ceo/chat",
            "search": "/api/v1/ceo/search",
            "dashboard": "/api/v1/ceo/dashboard/summary",
            "insights": "/api/v1/ceo/insights",
            "health": "/api/v1/ceo/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "ceo_dashboard_test"}

if __name__ == "__main__":
    print("🚀 Starting CEO Dashboard Test Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    print("💬 Chat Endpoint: http://localhost:8001/api/v1/ceo/chat")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    ) 