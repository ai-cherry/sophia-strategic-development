"""
Enhanced Unified Chat API Routes - Phase 2

This module provides comprehensive API endpoints for:
- Natural language chat interface
- Workflow orchestration and management
- Human-in-the-loop interactions
- Agent creation and management
- Real-time status updates
- Approval and decision management

Key Features:
- RESTful API for chat interactions
- WebSocket support for real-time updates
- Workflow management endpoints
- Human approval checkpoint handling
- Agent creation through natural language
- Comprehensive error handling and validation
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.core.dependencies import get_audit_logger, get_current_user
from backend.security.audit_logger import AuditLogger
from backend.services.sophia_universal_chat_service import (
    universal_chat_service,
)
from backend.workflows.enhanced_langgraph_orchestration import enhanced_orchestrator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/chat", tags=["Enhanced Chat"])


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Chat message request"""

    message: str = Field(..., description="Chat message content")
    session_id: str = Field(..., description="Session identifier")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Optional metadata"
    )


class ChatResponse(BaseModel):
    """Chat message response"""

    message_id: str
    session_id: str
    message_type: str
    content: str
    metadata: dict[str, Any]
    timestamp: datetime
    workflow_id: str | None = None
    checkpoint_id: str | None = None
    intent: str | None = None
    confidence: float | None = None


class WorkflowCreateRequest(BaseModel):
    """Workflow creation request"""

    description: str = Field(
        ..., description="Natural language description of the workflow"
    )
    workflow_type: str | None = Field(default="custom", description="Type of workflow")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Optional metadata"
    )


class WorkflowResponse(BaseModel):
    """Workflow response"""

    workflow_id: str
    status: str
    current_node: str
    progress: dict[str, Any]
    pending_checkpoints: list[dict[str, Any]]
    execution_metrics: dict[str, Any]
    last_updated: datetime


class ApprovalRequest(BaseModel):
    """Approval request"""

    checkpoint_id: str = Field(..., description="Checkpoint identifier")
    approved: bool = Field(..., description="Approval decision")
    feedback: str | None = Field(default=None, description="Optional feedback")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Optional metadata"
    )


class ApprovalResponse(BaseModel):
    """Approval response"""

    checkpoint_id: str
    processed: bool
    workflow_continued: bool
    message: str


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    # Remove dead connections
                    self.active_connections[user_id].remove(connection)

    async def broadcast_to_user(self, message: dict[str, Any], user_id: str):
        if user_id in self.active_connections:
            message_str = json.dumps(message, default=str)
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message_str)
                except Exception:
                    # Remove dead connections
                    self.active_connections[user_id].remove(connection)


# Global connection manager
manager = ConnectionManager()


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    audit_logger: AuditLogger = Depends(get_audit_logger),
):
    """
    Send a chat message and get AI response

    This endpoint processes natural language messages and can:
    - Create and manage workflows
    - Handle approvals and decisions
    - Create AI agents
    - Provide status updates
    - Answer general questions
    """
    try:
        user_id = current_user.get("user_id", "anonymous")

        # Initialize chat service if needed
        if not universal_chat_service.initialized:
            await universal_chat_service.initialize()

        # Process the message
        response_message = await universal_chat_service.process_message(
            user_id=user_id,
            session_id=request.session_id,
            message_content=request.message,
            message_metadata=request.metadata,
        )

        # Convert to response model
        response = ChatResponse(
            message_id=response_message.message_id,
            session_id=response_message.session_id,
            message_type=response_message.message_type.value,
            content=response_message.content,
            metadata=response_message.metadata,
            timestamp=response_message.timestamp,
            workflow_id=response_message.workflow_id,
            checkpoint_id=response_message.checkpoint_id,
            intent=response_message.intent.value if response_message.intent else None,
            confidence=response_message.confidence,
        )

        # Send real-time update via WebSocket
        await manager.broadcast_to_user(
            {"type": "chat_response", "data": response.dict()}, user_id
        )

        # Log the interaction
        await audit_logger.log_chat_interaction(
            user_id=user_id,
            session_id=request.session_id,
            message_type="api_request",
            content=request.message,
            intent=response.intent,
            response_content=response.content,
        )

        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error processing message: {str(e)}"
        )


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """Get chat history for a session"""
    try:
        current_user.get("user_id", "anonymous")

        # Initialize chat service if needed
        if not universal_chat_service.initialized:
            await universal_chat_service.initialize()

        # Get session history
        history = await universal_chat_service.get_session_history(session_id, limit)

        # Convert to response format
        history_response = []
        for message in history:
            history_response.append(
                {
                    "message_id": message.message_id,
                    "session_id": message.session_id,
                    "user_id": message.user_id,
                    "message_type": message.message_type.value,
                    "content": message.content,
                    "metadata": message.metadata,
                    "timestamp": message.timestamp,
                    "workflow_id": message.workflow_id,
                    "checkpoint_id": message.checkpoint_id,
                    "intent": message.intent.value if message.intent else None,
                    "confidence": message.confidence,
                }
            )

        return {"session_id": session_id, "history": history_response}

    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting chat history: {str(e)}"
        )


@router.post("/workflow/create", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    audit_logger: AuditLogger = Depends(get_audit_logger),
):
    """Create a new workflow from natural language description"""
    try:
        user_id = current_user.get("user_id", "anonymous")
        session_id = f"api_session_{user_id}_{datetime.now().timestamp()}"

        # Initialize orchestrator if needed
        if not enhanced_orchestrator.initialized:
            await enhanced_orchestrator.initialize()

        # Create workflow
        workflow_id = await enhanced_orchestrator.create_workflow_from_natural_language(
            user_request=request.description, user_id=user_id, session_id=session_id
        )

        # Get workflow status
        status = await enhanced_orchestrator.get_workflow_status(workflow_id)

        # Convert to response model
        response = WorkflowResponse(
            workflow_id=workflow_id,
            status=status["status"],
            current_node=status["current_node"],
            progress=status["progress"],
            pending_checkpoints=status["pending_checkpoints"],
            execution_metrics=status["execution_metrics"],
            last_updated=status["last_updated"],
        )

        # Send real-time update via WebSocket
        await manager.broadcast_to_user(
            {"type": "workflow_created", "data": response.dict()}, user_id
        )

        # Log workflow creation
        await audit_logger.log_workflow_event(
            workflow_id=workflow_id,
            event_type="workflow_created_via_api",
            user_id=user_id,
            details={
                "description": request.description,
                "workflow_type": request.workflow_type,
            },
        )

        return response

    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error creating workflow: {str(e)}"
        )


@router.get("/workflow/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(
    workflow_id: str, current_user: dict[str, Any] = Depends(get_current_user)
):
    """Get status of a specific workflow"""
    try:
        # Initialize orchestrator if needed
        if not enhanced_orchestrator.initialized:
            await enhanced_orchestrator.initialize()

        # Get workflow status
        status = await enhanced_orchestrator.get_workflow_status(workflow_id)

        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])

        # Convert to response model
        response = WorkflowResponse(
            workflow_id=workflow_id,
            status=status["status"],
            current_node=status["current_node"],
            progress=status["progress"],
            pending_checkpoints=status["pending_checkpoints"],
            execution_metrics=status["execution_metrics"],
            last_updated=status["last_updated"],
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting workflow status: {str(e)}"
        )


@router.get("/workflows")
async def get_user_workflows(current_user: dict[str, Any] = Depends(get_current_user)):
    """Get all active workflows for the current user"""
    try:
        user_id = current_user.get("user_id", "anonymous")

        # Initialize chat service if needed
        if not universal_chat_service.initialized:
            await universal_chat_service.initialize()

        # Get active workflows
        workflows = await universal_chat_service.get_active_workflows(user_id)

        return {"user_id": user_id, "workflows": workflows}

    except Exception as e:
        logger.error(f"Error getting user workflows: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting workflows: {str(e)}"
        )


@router.post("/approval/{checkpoint_id}", response_model=ApprovalResponse)
async def handle_approval(
    checkpoint_id: str,
    request: ApprovalRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    audit_logger: AuditLogger = Depends(get_audit_logger),
):
    """Handle human approval for a checkpoint"""
    try:
        user_id = current_user.get("user_id", "anonymous")

        # Initialize orchestrator if needed
        if not enhanced_orchestrator.initialized:
            await enhanced_orchestrator.initialize()

        # Process approval
        workflow_continued = await enhanced_orchestrator.handle_human_response(
            checkpoint_id=checkpoint_id,
            response={
                "approved": request.approved,
                "feedback": request.feedback,
                "metadata": request.metadata,
            },
            user_id=user_id,
        )

        # Create response
        response = ApprovalResponse(
            checkpoint_id=checkpoint_id,
            processed=True,
            workflow_continued=workflow_continued,
            message=f"Checkpoint {'approved' if request.approved else 'rejected'} successfully",
        )

        # Send real-time update via WebSocket
        await manager.broadcast_to_user(
            {"type": "approval_processed", "data": response.dict()}, user_id
        )

        # Log approval
        await audit_logger.log_workflow_event(
            workflow_id="unknown",  # Would need to track this
            event_type="approval_processed_via_api",
            user_id=user_id,
            details={
                "checkpoint_id": checkpoint_id,
                "approved": request.approved,
                "feedback": request.feedback,
            },
        )

        return response

    except Exception as e:
        logger.error(f"Error handling approval: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error handling approval: {str(e)}"
        )


@router.get("/approvals")
async def get_pending_approvals(
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """Get pending approvals for the current user"""
    try:
        user_id = current_user.get("user_id", "anonymous")

        # Initialize chat service if needed
        if not universal_chat_service.initialized:
            await universal_chat_service.initialize()

        # Get pending approvals
        approvals = await universal_chat_service.get_pending_approvals_for_user(user_id)

        return {"user_id": user_id, "pending_approvals": approvals}

    except Exception as e:
        logger.error(f"Error getting pending approvals: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting approvals: {str(e)}"
        )


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                message_type = message_data.get("type")

                if message_type == "ping":
                    # Respond to ping with pong
                    await websocket.send_text(
                        json.dumps(
                            {"type": "pong", "timestamp": datetime.now().isoformat()}
                        )
                    )

                elif message_type == "chat_message":
                    # Process chat message via WebSocket
                    session_id = message_data.get("session_id", f"ws_session_{user_id}")
                    message_content = message_data.get("message", "")

                    if message_content:
                        # Initialize chat service if needed
                        if not universal_chat_service.initialized:
                            await universal_chat_service.initialize()

                        # Process the message
                        response_message = await universal_chat_service.process_message(
                            user_id=user_id,
                            session_id=session_id,
                            message_content=message_content,
                        )

                        # Send response back
                        response_data = {
                            "type": "chat_response",
                            "data": {
                                "message_id": response_message.message_id,
                                "session_id": response_message.session_id,
                                "message_type": response_message.message_type.value,
                                "content": response_message.content,
                                "metadata": response_message.metadata,
                                "timestamp": response_message.timestamp.isoformat(),
                                "workflow_id": response_message.workflow_id,
                                "checkpoint_id": response_message.checkpoint_id,
                                "intent": (
                                    response_message.intent.value
                                    if response_message.intent
                                    else None
                                ),
                                "confidence": response_message.confidence,
                            },
                        }

                        await websocket.send_text(
                            json.dumps(response_data, default=str)
                        )

                elif message_type == "status_request":
                    # Send current status
                    if not universal_chat_service.initialized:
                        await universal_chat_service.initialize()

                    workflows = await universal_chat_service.get_active_workflows(
                        user_id
                    )
                    approvals = (
                        await universal_chat_service.get_pending_approvals_for_user(
                            user_id
                        )
                    )

                    status_data = {
                        "type": "status_update",
                        "data": {
                            "workflows": workflows,
                            "pending_approvals": approvals,
                            "timestamp": datetime.now().isoformat(),
                        },
                    }

                    await websocket.send_text(json.dumps(status_data, default=str))

            except json.JSONDecodeError:
                # Invalid JSON, ignore
                pass
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                error_response = {
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


@router.post("/agent/create")
async def create_agent_via_api(
    request: WorkflowCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    audit_logger: AuditLogger = Depends(get_audit_logger),
):
    """Create a new AI agent through natural language description"""
    try:
        user_id = current_user.get("user_id", "anonymous")
        session_id = f"agent_creation_{user_id}_{datetime.now().timestamp()}"

        # Initialize chat service if needed
        if not universal_chat_service.initialized:
            await universal_chat_service.initialize()

        # Process as agent creation message
        response_message = await universal_chat_service.process_message(
            user_id=user_id,
            session_id=session_id,
            message_content=f"Create an AI agent: {request.description}",
            message_metadata={"api_request": True, "agent_creation": True},
        )

        # Send real-time update via WebSocket
        await manager.broadcast_to_user(
            {
                "type": "agent_creation_started",
                "data": {
                    "session_id": session_id,
                    "workflow_id": response_message.workflow_id,
                    "description": request.description,
                },
            },
            user_id,
        )

        # Log agent creation request
        await audit_logger.log_workflow_event(
            workflow_id=response_message.workflow_id or "unknown",
            event_type="agent_creation_requested_via_api",
            user_id=user_id,
            details={"description": request.description, "session_id": session_id},
        )

        return {
            "message": "Agent creation workflow started",
            "session_id": session_id,
            "workflow_id": response_message.workflow_id,
            "response": response_message.content,
        }

    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if services are initialized
        chat_initialized = universal_chat_service.initialized
        orchestrator_initialized = enhanced_orchestrator.initialized

        return {
            "status": "healthy",
            "services": {
                "chat_service": (
                    "initialized" if chat_initialized else "not_initialized"
                ),
                "orchestrator": (
                    "initialized" if orchestrator_initialized else "not_initialized"
                ),
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )


# Background task to send periodic updates
async def periodic_status_updates():
    """Send periodic status updates to connected clients"""
    while True:
        try:
            # Send updates every 30 seconds
            await asyncio.sleep(30)

            # Get all connected users
            for user_id in list(manager.active_connections.keys()):
                try:
                    if not universal_chat_service.initialized:
                        continue

                    # Get user's workflows and approvals
                    workflows = await universal_chat_service.get_active_workflows(
                        user_id
                    )
                    approvals = (
                        await universal_chat_service.get_pending_approvals_for_user(
                            user_id
                        )
                    )

                    # Only send if there are active items
                    if workflows or approvals:
                        status_update = {
                            "type": "periodic_status_update",
                            "data": {
                                "workflows": workflows,
                                "pending_approvals": approvals,
                                "timestamp": datetime.now().isoformat(),
                            },
                        }

                        await manager.broadcast_to_user(status_update, user_id)

                except Exception as e:
                    logger.error(
                        f"Error sending periodic update to user {user_id}: {e}"
                    )

        except Exception as e:
            logger.error(f"Error in periodic status updates: {e}")


# Start background task when module is imported
asyncio.create_task(periodic_status_updates())
