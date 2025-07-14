#!/usr/bin/env python3
"""
Sophia AI FastAPI - Minimal Deployment
Modern FastAPI with streaming chat support
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.ai_memory_health_routes import router as ai_memory_router
from api.deployment_status_routes import router as deployment_router
from api.lambda_labs_health_routes import router as lambda_labs_router
from api.unified_health_routes import router as unified_health_router
from backend.services.unified_chat_service import (
    AccessLevel,
    ChatContext,
    SophiaUnifiedOrchestrator,
)
from backend.services.unified_chat_service import (
    ChatRequest as InternalChatRequest,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Platform",
    description="AI-powered business intelligence with streaming chat",
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

# Include monitoring routers
app.include_router(ai_memory_router)
app.include_router(deployment_router)
app.include_router(unified_health_router)
app.include_router(lambda_labs_router)


# Pydantic models for API (align with internal models but use Pydantic)
class ChatRequest(BaseModel):
    message: str
    user_id: str = "user"
    session_id: str | None = None
    context: ChatContext = ChatContext.BLENDED_INTELLIGENCE
    access_level: AccessLevel = AccessLevel.EMPLOYEE
    metadata: dict[str, Any] | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    sources: list[Any] | None = None
    suggestions: list[Any] | None = None
    metadata: dict[str, Any] | None = None
    timestamp: str = datetime.now().isoformat()


# Initialize the unified chat service
chat_service = SophiaUnifiedOrchestrator()


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sophia AI Platform", "version": "2.0.0"}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Sophia AI Platform",
        "version": "2.0.0",
        "docs_url": "/docs",
    }


# Streaming chat endpoint
@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        internal_request = InternalChatRequest(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context,
            access_level=request.access_level,
            metadata=request.metadata,
        )

        if request.stream:
            # For streaming, we'll need to adapt the internal service's response
            # This mock currently doesn't support streaming from the internal service
            # A full implementation would require the internal service to yield tokens
            async def stream_response():
                # Placeholder for actual streaming from SophiaUnifiedOrchestrator
                # For now, it will return the full response as a single chunk
                full_response_obj = await chat_service.process_chat(internal_request)
                yield f"data: {full_response_obj.response}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )
        else:
            # Return complete response
            internal_response = await chat_service.process_chat(internal_request)
            return ChatResponse(
                response=internal_response.response,
                sources=internal_response.sources,
                suggestions=internal_response.suggestions,
                metadata=internal_response.metadata,
                timestamp=internal_response.timestamp,
            )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {e!s}")


# Debug routes
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({"path": route.path, "methods": list(route.methods)})
    return {"routes": routes}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",  # Changed from 0.0.0.0 for security. Use environment variable for production
        port=8000,
        log_level="info",
    )
