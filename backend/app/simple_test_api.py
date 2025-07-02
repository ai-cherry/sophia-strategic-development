#!/usr/bin/env python3
"""
Simple Test API
===============

A minimal FastAPI application to test the setup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Test API",
    description="Simple test API for Sophia AI",
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
        "message": "Sophia AI Test API is running!",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sophia-ai-test",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
async def test_endpoint():
    """Test API endpoint"""
    return {
        "message": "Test endpoint working!",
        "data": {
            "test": True,
            "value": 42
        }
    }

if __name__ == "__main__":
    # Run the app
    print("🚀 Starting Sophia AI Test API on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001) 