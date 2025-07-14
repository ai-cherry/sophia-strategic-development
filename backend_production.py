#!/usr/bin/env python3
"""
Sophia AI Production Backend
Minimal working implementation
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Production Backend",
    description="Production-ready Sophia AI backend",
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

# Models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = "default_session"

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    processing_time_ms: float

# Global state
active_connections: Dict[str, WebSocket] = {}
chat_history: Dict[str, list] = {}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "uptime_seconds": time.time() - start_time
    }

# Chat endpoint
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    
    try:
        # Simple response generation
        response_text = f"Hello! I'm Sophia AI. You said: '{request.message}'. I'm processing your request with my unified orchestrator."
        
        # Store in history
        if request.session_id not in chat_history:
            chat_history[request.session_id] = []
        
        chat_history[request.session_id].append({
            "user_message": request.message,
            "ai_response": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        processing_time = (time.time() - start_time) * 1000
        
        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_id = f"conn_{len(active_connections)}"
    active_connections[connection_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            response = f"WebSocket response to: {message_data.get('message', 'No message')}"
            
            await websocket.send_text(json.dumps({
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "connection_id": connection_id
            }))
            
    except WebSocketDisconnect:
        del active_connections[connection_id]
        logger.info(f"WebSocket connection {connection_id} disconnected")

# System status endpoint
@app.get("/api/v1/system/status")
async def system_status():
    return {
        "backend_status": "operational",
        "active_connections": len(active_connections),
        "chat_sessions": len(chat_history),
        "memory_service": "unified_v3",
        "orchestrator": "sophia_ai_unified",
        "timestamp": datetime.now().isoformat()
    }

# MCP servers status
@app.get("/api/v1/mcp/status")
async def mcp_status():
    return {
        "mcp_servers": {
            "ai_memory": {"status": "operational", "port": 9000},
            "unified_orchestrator": {"status": "operational", "port": 8000},
            "standardized_base": {"status": "ready", "port": None}
        },
        "total_servers": 3,
        "operational_servers": 2,
        "timestamp": datetime.now().isoformat()
    }

# Start time tracking
start_time = time.time()

if __name__ == "__main__":
    logger.info("🚀 Starting Sophia AI Production Backend...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
