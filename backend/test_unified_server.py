#!/usr/bin/env python3
"""
Test Unified Dashboard Server
========================

Simple test server for Unified dashboard API endpoints
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sophia AI - Unified Dashboard Test Server",
    description="A lightweight server to test the Unified Dashboard frontend and its core API endpoints.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}/unified"
PORT = 8000

# --- Mock Data and Endpoints ---
mock_endpoints = {
    "chat": f"{API_PREFIX}/chat",
    "search": f"{API_PREFIX}/search",
    "dashboard": f"{API_PREFIX}/dashboard/summary",
    "insights": f"{API_PREFIX}/insights",
    "health": f"{API_PREFIX}/health",
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Unified Dashboard Test Server",
        "status": "running",
        "endpoints": {
            "chat": "/api/v1/ceo/chat",
            "search": "/api/v1/ceo/search",
            "dashboard": "/api/v1/ceo/dashboard/summary",
            "insights": "/api/v1/ceo/insights",
            "health": "/api/v1/ceo/health",
            "docs": "/docs",
        },
    }


@app.get(f"{API_PREFIX}/health")
async def get_health():
    """Health check"""
    return {"status": "ok", "message": "Unified Dashboard server is running"}


@app.get(f"{API_PREFIX}/dashboard/summary")
async def get_dashboard_summary():
    """Returns a summary of KPIs for the Unified Dashboard."""
    return {
        "status": "ok",
        "kpi_summary": {
            "revenue_ytd": 12500000,
            "active_projects": 42,
            "system_health": 99.8,
        },
    }


@app.post(f"{API_PREFIX}/chat")
async def post_chat(message: dict):
    """Simulates a chat interaction, echoing the message."""
    user_message = message.get("content", "No message received.")
    return {
        "status": "ok",
        "response": {"role": "assistant", "content": f"You said: '{user_message}'"},
    }


@app.post(f"{API_PREFIX}/search")
async def post_search(query: dict):
    """Simulates a search query, returning mock results."""
    search_term = query.get("term", "No term provided.")
    return {
        "status": "ok",
        "results": [
            {
                "title": f"Result for '{search_term}' 1",
                "snippet": "This is the first result.",
            },
            {
                "title": f"Result for '{search_term}' 2",
                "snippet": "This is the second result.",
            },
        ],
    }


@app.get(f"{API_PREFIX}/insights")
async def get_insights():
    """Returns mock AI-powered insights."""
    return {
        "status": "ok",
        "insights": [
            "Insight 1: Project velocity has increased by 15% this quarter.",
            "Insight 2: Customer satisfaction is at an all-time high.",
        ],
    }


if __name__ == "__main__":
    print("🚀 Starting Unified Dashboard Test Server...")
    print(f"📍 Server will be available at: http://localhost:{PORT}")
    print(f"📚 API Documentation: http://localhost:{PORT}/docs")
    print(f"🔍 Health Check: http://localhost:{PORT}{API_PREFIX}/health")
    print(f"💬 Chat Endpoint: http://localhost:{PORT}{API_PREFIX}/chat")

    uvicorn.run(app, host="0.0.0.0", port=PORT)
