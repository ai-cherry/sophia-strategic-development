#!/usr/bin/env python3
"""
Sophia AI FastAPI - Minimal Deployment
Modern FastAPI with streaming chat support
"""

import asyncio
import logging
from typing import AsyncGenerator

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
    description="AI-powered business intelligence with streaming chat",
    version="2.0.0"
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
    stream: bool = False

class ChatResponse(BaseModel):
    content: str
    user_id: str

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Sophia AI Platform",
        "version": "2.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Sophia AI Platform",
        "version": "2.0.0",
        "docs_url": "/docs"
    }

# Mock AI response generator
async def generate_ai_response(message: str, user_id: str) -> AsyncGenerator[str, None]:
    response_parts = [
        f"Hello {user_id}! ",
        "I understand you said: ",
        f'"{message}". ',
        "This is a streaming response from Sophia AI. ",
        "I'm processing your request using advanced AI capabilities. ",
        "The system is working perfectly with FastAPI 2025 best practices. ",
        "Thank you for using Sophia AI!"
    ]
    
    for part in response_parts:
        await asyncio.sleep(0.2)  # Simulate processing
        yield part

# Streaming chat endpoint
@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        if request.stream:
            # Return streaming response
            async def stream_response():
                async for token in generate_ai_response(request.message, request.user_id):
                    yield f"data: {token}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Return complete response
            full_response = ""
            async for token in generate_ai_response(request.message, request.user_id):
                full_response += token
            
            return ChatResponse(
                content=full_response,
                user_id=request.user_id
            )
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

# Debug routes
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods)
            })
    return {"routes": routes}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

