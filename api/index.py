"""
Sophia AI Unified Dashboard - Vercel Serverless Backend
Clean implementation without any manus contamination
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from datetime import datetime
import logging

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Unified Dashboard API",
    description="Clean backend API for Unified dashboard",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    search_context: Optional[str] = "business_intelligence"
    user_id: Optional[str] = "ceo"

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    features: Dict[str, bool]
    version: str

# Health endpoint
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0"}

# Unified Dashboard Summary
@app.get("/api/v1/unified/dashboard/summary")
async def get_dashboard_summary():
    # This would fetch real data from the Business Intelligence service
    return {"message": "This is a mock summary for the Unified Dashboard."}

# Unified Chat endpoint
@app.post("/api/v1/unified/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message", "No message provided")
    # This would interact with the Unified Chat Service
    return {"response": f"Sophia AI: I received your message - '{user_message}'"}

# Unified Search endpoint
@app.post("/api/v1/unified/search")
async def search_endpoint(request: Request):
    data = await request.json()
    query = data.get("query", "No query provided")
    # This would use the semantic search on the vector store
    return {"results": f"Showing mock search results for: '{query}'"}

# Unified Insights endpoint
@app.get("/api/v1/unified/insights")
async def get_ai_insights():
    # This would generate real insights from the AI Memory
    return {"insights": ["Mock Insight 1: Project velocity is trending up.", "Mock Insight 2: High customer engagement in recent calls."]}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Sophia AI Unified Dashboard API - Clean Vercel Deployment",
        "status": "operational",
        "endpoints": [
            "/health",
            "/api/v1/unified/dashboard/summary",
            "/api/v1/unified/chat",
            "/api/v1/unified/search", 
            "/api/v1/unified/insights"
        ],
        "timestamp": datetime.now().isoformat()
    }

# Export for Vercel
async def handler(scope, receive, send):
    return await app(scope, receive, send)

# --- Endpoint Registration ---
# This list is used for health checks and service discovery.
# It should be the single source of truth for all available API endpoints.
REGISTERED_ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/unified/dashboard/summary",
    "/api/v1/unified/chat",
    "/api/v1/unified/search",
    "/api/v1/unified/insights"
]

@app.get("/api/v1/endpoints")
async def get_endpoints():
    return {"endpoints": REGISTERED_ENDPOINTS}
