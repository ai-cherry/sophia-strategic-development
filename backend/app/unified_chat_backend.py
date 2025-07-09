#!/usr/bin/env python3
"""
🎯 SOPHIA AI - UNIFIED CHAT BACKEND
Central orchestrator for all MCP servers and provides real business intelligence for Pay Ready CEO

🚨 FILE TYPE: PERMANENT
🔐 SECRET MANAGEMENT: Pulumi ESC integrated
🏗️ ARCHITECTURE: Hub-and-spoke with MCP server orchestration

Business Context:
- Supports Pay Ready CEO (80 employees, $50M revenue)
- Real-time business intelligence across all systems
- Unified chat interface for executive decision support

Performance Requirements:
- Response Time: <200ms for simple queries, <2s for complex analysis
- Throughput: 1000+ concurrent requests
- Uptime: >99.9%
- Real-time data synchronization
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import services
from backend.services.unified_chat_service import UnifiedChatService

# Try to import temporal learning
try:
    from backend.services.temporal_qa_learning_service import (
        get_temporal_qa_learning_service,
    )

    TEMPORAL_LEARNING_AVAILABLE = True
except ImportError:
    TEMPORAL_LEARNING_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize services
chat_service = UnifiedChatService()
temporal_service = None

if TEMPORAL_LEARNING_AVAILABLE:
    try:
        temporal_service = get_temporal_qa_learning_service()
        logger.info("Temporal learning service initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize temporal learning service: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Sophia AI Unified Chat Backend with Temporal Learning...")
    await chat_service.initialize()
    logger.info("✅ Unified Chat Backend with Temporal Learning ready")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Unified Chat Backend with Temporal Learning...")
    await chat_service.cleanup()
    logger.info("Services shutdown complete")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Sophia AI - Unified Chat Backend with Temporal Learning",
    description="Central orchestrator for Pay Ready business intelligence with temporal learning",
    version="3.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    context: Optional[dict[str, Any]] = None
    user_id: str = "default_user"
    session_id: str = "default_session"


class ChatResponse(BaseModel):
    response: str
    metadata: dict[str, Any]
    temporal_learning_applied: bool = False
    temporal_interaction_id: Optional[str] = None


class TemporalCorrectionRequest(BaseModel):
    interaction_id: str
    correction: str
    context: Optional[dict[str, Any]] = None


class TemporalCorrectionResponse(BaseModel):
    success: bool
    interaction_id: str
    message: str


class TemporalValidationRequest(BaseModel):
    interaction_id: str
    is_correct: bool
    feedback: Optional[str] = None


# Main chat endpoint with temporal learning
@app.post("/api/v3/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Enhanced chat endpoint with temporal learning integration
    Processes natural language queries with learning capabilities
    """
    try:
        # Process the query with temporal learning integration
        # Convert context dict to string for the chat service
        context_str = "chat"  # Default context
        if request.context:
            context_str = request.context.get("context_type", "chat")

        result = await chat_service.process_query(
            query=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            context=context_str,
        )

        return ChatResponse(
            response=result["response"],
            metadata=result["metadata"],
            temporal_learning_applied=result["metadata"].get(
                "temporal_learning_applied", False
            ),
            temporal_interaction_id=result["metadata"].get("temporal_interaction_id"),
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Temporal learning endpoints
@app.post(
    "/api/v1/temporal-learning/chat/correct", response_model=TemporalCorrectionResponse
)
async def temporal_correction_endpoint(request: TemporalCorrectionRequest):
    """
    Process user correction for temporal learning
    """
    if not temporal_service:
        raise HTTPException(
            status_code=503, detail="Temporal learning service not available"
        )

    try:
        result = await chat_service.process_temporal_correction(
            interaction_id=request.interaction_id,
            correction=request.correction,
            user_id="default_user",
            session_id="default_session",
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return TemporalCorrectionResponse(
            success=True,
            interaction_id=request.interaction_id,
            message="Correction processed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporal correction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/temporal-learning/interactions/{interaction_id}/validate")
async def temporal_validation_endpoint(
    interaction_id: str, request: TemporalValidationRequest
):
    """
    Validate a temporal learning interaction
    """
    if not temporal_service:
        raise HTTPException(
            status_code=503, detail="Temporal learning service not available"
        )

    try:
        # Find and update the interaction
        interaction = next(
            (
                i
                for i in temporal_service.learning_interactions
                if i.id == interaction_id
            ),
            None,
        )

        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")

        # Update validation status
        interaction.validated = request.is_correct
        if request.feedback:
            interaction.context["validation_feedback"] = request.feedback

        return {
            "success": True,
            "interaction_id": interaction_id,
            "validated": request.is_correct,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporal validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/temporal-learning/dashboard/data")
async def temporal_dashboard_data():
    """
    Get temporal learning dashboard data
    """
    if not temporal_service:
        # Return mock data if service not available
        return {
            "total_interactions": 0,
            "learning_accuracy": 0.0,
            "knowledge_concepts": 0,
            "system_status": "unavailable",
            "recent_interactions": [],
            "learning_suggestions": ["Temporal learning service not available"],
        }

    try:
        insights = await chat_service.get_temporal_learning_insights("default_user")

        if "error" in insights:
            raise HTTPException(status_code=503, detail=insights["error"])

        return insights

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporal dashboard data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/temporal-learning/health")
async def temporal_health_check():
    """
    Health check for temporal learning service
    """
    if not temporal_service:
        return {
            "status": "unavailable",
            "service": "temporal_qa_learning",
            "error": "Service not initialized",
        }

    try:
        return {
            "status": "healthy",
            "service": "temporal_qa_learning",
            "system_date": datetime.now().isoformat(),
            "total_interactions": len(temporal_service.learning_interactions),
            "total_knowledge": len(temporal_service.temporal_knowledge),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# System status endpoint (enhanced with temporal learning)
@app.get("/api/v3/system/status")
async def system_status():
    """
    Get comprehensive system status including temporal learning
    """
    mcp_servers = {}

    # Check MCP server status
    for server_name, server_client in chat_service.servers.items():
        mcp_servers[server_name] = {
            "name": server_name,
            "url": server_client.url,
            "healthy": server_client.healthy,
            "response_time": server_client.response_time,
            "description": server_client.description,
        }

    # Check temporal learning status
    temporal_status = {
        "available": TEMPORAL_LEARNING_AVAILABLE,
        "service_healthy": temporal_service is not None,
        "interactions_count": len(temporal_service.learning_interactions)
        if temporal_service
        else 0,
        "knowledge_count": len(temporal_service.temporal_knowledge)
        if temporal_service
        else 0,
    }

    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "mcp_servers": mcp_servers,
        "temporal_learning": temporal_status,
        "services": {
            "chat_service": "healthy",
            "temporal_learning": "healthy" if temporal_service else "unavailable",
        },
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "unified_chat_backend_with_temporal_learning",
        "version": "3.0.0",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Unified Chat Backend with Temporal Learning",
        "version": "3.0.0",
        "description": "Business intelligence orchestrator with natural language Q&A learning",
        "features": [
            "Natural language business intelligence",
            "MCP server integration",
            "Temporal learning and adaptation",
            "Multi-source data synthesis",
            "Interactive learning corrections",
        ],
        "endpoints": {
            "chat": "/api/v3/chat",
            "system_status": "/api/v3/system/status",
            "temporal_learning": "/api/v1/temporal-learning/",
            "health": "/health",
        },
        "temporal_learning_available": TEMPORAL_LEARNING_AVAILABLE,
    }


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the server on port 8001 to avoid conflicts
    logger.info("Starting Unified Chat Backend with Temporal Learning on port 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
