#!/usr/bin/env python3
"""
CEO Dashboard Routes
===================

Executive dashboard routes with migration control integration, universal chat interface,
and real-time monitoring capabilities for CEO oversight.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.services.migration_orchestrator_client import get_migration_orchestrator_client
from backend.services.enhanced_ceo_chat_service import (
    get_ceo_chat_service,
    CEOChatRequest,
    ChatContext,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class MigrationStatusWidget(BaseModel):
    """Migration status widget data for CEO dashboard"""
    status: str
    current_phase: str
    overall_progress: float
    records_processed: int
    total_records: int
    success_rate: float
    estimated_completion: Optional[str]
    health_indicators: Dict[str, str]
    last_updated: str


class CEODashboardData(BaseModel):
    """Complete CEO dashboard data"""
    migration_widget: MigrationStatusWidget
    executive_summary: Dict[str, Any]
    system_health: Dict[str, str]
    business_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    last_updated: str


class ChatMessage(BaseModel):
    """Chat message model for universal interface"""
    message: str
    context: str = "general"
    voice_command: bool = False


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    context: str
    timestamp: str
    actions_taken: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    metrics: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False


class MigrationCommand(BaseModel):
    """Migration command model"""
    action: str  # "start", "pause", "resume", "stop", "rollback"
    confirmation: bool = False


# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"CEO dashboard WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"CEO dashboard WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


@router.get("/ceo/dashboard", response_model=CEODashboardData)
async def get_ceo_dashboard():
    """Get complete CEO dashboard data"""
    try:
        migration_client = get_migration_orchestrator_client()
        
        # Get migration status
        migration_status = await migration_client.get_migration_status()
        
        # Create migration widget data
        migration_widget = MigrationStatusWidget(
            status=migration_status.get("status", "unknown"),
            current_phase=migration_status.get("metrics", {}).get("current_phase", "unknown"),
            overall_progress=migration_status.get("metrics", {}).get("overall_progress", 0.0),
            records_processed=migration_status.get("metrics", {}).get("records_processed", 0),
            total_records=migration_status.get("metrics", {}).get("total_records", 0),
            success_rate=migration_status.get("metrics", {}).get("success_rate", 0.0),
            estimated_completion=migration_status.get("metrics", {}).get("estimated_completion"),
            health_indicators=migration_status.get("health_indicators", {}),
            last_updated=migration_status.get("last_updated", datetime.now(UTC).isoformat()),
        )
        
        # Get executive summary
        executive_summary = await migration_client.get_executive_summary()
        
        # Get system health
        system_health = migration_status.get("health_indicators", {})
        
        # Get business metrics
        business_metrics = executive_summary.get("business_impact", {})
        
        # Get alerts
        alerts = await migration_client.get_migration_issues()
        
        # Get recent activities (placeholder)
        recent_activities = [
            {
                "action": "Migration Status Check",
                "timestamp": datetime.now(UTC).isoformat(),
                "user": "CEO Dashboard",
                "result": "Success",
            }
        ]
        
        dashboard_data = CEODashboardData(
            migration_widget=migration_widget,
            executive_summary=executive_summary,
            system_health=system_health,
            business_metrics=business_metrics,
            alerts=alerts,
            recent_activities=recent_activities,
            last_updated=datetime.now(UTC).isoformat(),
        )
        
        # Broadcast update to connected WebSockets
        await manager.broadcast({
            "type": "dashboard_update",
            "data": dashboard_data.dict(),
            "timestamp": datetime.now(UTC).isoformat(),
        })
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get CEO dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")


@router.post("/ceo/chat", response_model=ChatResponse)
async def ceo_chat(message: ChatMessage):
    """Process CEO chat message with migration control integration"""
    try:
        ceo_chat_service = get_ceo_chat_service()
        
        # Create chat request
        chat_request = CEOChatRequest(
            message=message.message,
            user_id="ceo",  # In production, get from authentication
            context=ChatContext(message.context),
            voice_command=message.voice_command,
        )
        
        # Process message
        response = await ceo_chat_service.process_ceo_message(chat_request)
        
        # Convert to API response model
        chat_response = ChatResponse(
            message=response.message,
            context=response.context.value,
            timestamp=response.timestamp.isoformat(),
            actions_taken=response.actions_taken,
            suggestions=response.suggestions,
            metrics=response.metrics,
            requires_confirmation=response.requires_confirmation,
        )
        
        # Broadcast chat update if migration-related
        if response.context == ChatContext.MIGRATION_CONTROL:
            await manager.broadcast({
                "type": "migration_chat_update",
                "message": response.message,
                "actions": response.actions_taken,
                "timestamp": datetime.now(UTC).isoformat(),
            })
        
        return chat_response
        
    except Exception as e:
        logger.error(f"CEO chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/ceo/migration/control")
async def migration_control(command: MigrationCommand):
    """Direct migration control commands with executive confirmation"""
    try:
        migration_client = get_migration_orchestrator_client()
        
        # Validate command
        valid_actions = ["start", "pause", "resume", "stop", "rollback"]
        if command.action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
        
        # Execute command based on action
        user_id = "ceo"  # In production, get from authentication
        
        if command.action == "start":
            result = await migration_client.start_migration(user_id)
        elif command.action == "pause":
            result = await migration_client.pause_migration(user_id)
        elif command.action == "resume":
            result = await migration_client.resume_migration(user_id)
        elif command.action == "stop":
            result = await migration_client.stop_migration(user_id)
        elif command.action == "rollback":
            if not command.confirmation:
                raise HTTPException(
                    status_code=400, 
                    detail="Rollback requires explicit confirmation. Set confirmation=true"
                )
            result = await migration_client.rollback_migration(user_id)
        
        # Broadcast control action to connected clients
        await manager.broadcast({
            "type": "migration_control_action",
            "action": command.action,
            "result": result,
            "timestamp": datetime.now(UTC).isoformat(),
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Migration control error: {e}")
        raise HTTPException(status_code=500, detail=f"Control error: {str(e)}")


@router.get("/ceo/migration/status")
async def get_migration_status():
    """Get current migration status"""
    try:
        migration_client = get_migration_orchestrator_client()
        status = await migration_client.get_migration_status()
        return status
        
    except Exception as e:
        logger.error(f"Migration status error: {e}")
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")


@router.get("/ceo/migration/issues")
async def get_migration_issues():
    """Get current migration issues and alerts"""
    try:
        migration_client = get_migration_orchestrator_client()
        issues = await migration_client.get_migration_issues()
        return {"issues": issues, "count": len(issues)}
        
    except Exception as e:
        logger.error(f"Migration issues error: {e}")
        raise HTTPException(status_code=500, detail=f"Issues error: {str(e)}")


@router.get("/ceo/migration/summary")
async def get_executive_summary():
    """Get executive migration summary"""
    try:
        migration_client = get_migration_orchestrator_client()
        summary = await migration_client.get_executive_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Executive summary error: {e}")
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")


@router.websocket("/ceo/dashboard/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time CEO dashboard updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial dashboard data
        migration_client = get_migration_orchestrator_client()
        initial_status = await migration_client.get_migration_status()
        
        await manager.send_personal_message({
            "type": "connection_established",
            "message": "CEO Dashboard WebSocket connected",
            "initial_data": initial_status,
            "timestamp": datetime.now(UTC).isoformat(),
        }, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_json()
                
                # Handle different message types
                if data.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now(UTC).isoformat(),
                    }, websocket)
                
                elif data.get("type") == "request_update":
                    # Send current dashboard data
                    current_status = await migration_client.get_migration_status()
                    await manager.send_personal_message({
                        "type": "dashboard_update",
                        "data": current_status,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }, websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.now(UTC).isoformat(),
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("CEO dashboard WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/ceo/chat/history")
async def get_chat_history(limit: int = 10):
    """Get CEO chat history"""
    try:
        ceo_chat_service = get_ceo_chat_service()
        history = await ceo_chat_service.get_conversation_history("ceo", limit)
        return {"history": history, "count": len(history)}
        
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        raise HTTPException(status_code=500, detail=f"History error: {str(e)}")


@router.get("/ceo/system/health")
async def get_system_health():
    """Get comprehensive system health for CEO oversight"""
    try:
        migration_client = get_migration_orchestrator_client()
        status = await migration_client.get_migration_status()
        
        health_data = {
            "overall_status": "healthy",
            "systems": status.get("health_indicators", {}),
            "migration_status": status.get("status"),
            "last_check": datetime.now(UTC).isoformat(),
        }
        
        # Determine overall status
        system_statuses = list(status.get("health_indicators", {}).values())
        if "offline" in system_statuses:
            health_data["overall_status"] = "critical"
        elif "degraded" in system_statuses:
            health_data["overall_status"] = "degraded"
        
        return health_data
        
    except Exception as e:
        logger.error(f"System health error: {e}")
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")


# Background task to send periodic updates
async def send_periodic_updates():
    """Send periodic updates to connected WebSocket clients"""
    import asyncio
    
    while True:
        try:
            await asyncio.sleep(30)  # Update every 30 seconds
            
            if manager.active_connections:
                migration_client = get_migration_orchestrator_client()
                status = await migration_client.get_migration_status()
                
                await manager.broadcast({
                    "type": "periodic_update",
                    "data": status,
                    "timestamp": datetime.now(UTC).isoformat(),
                })
                
        except Exception as e:
            logger.error(f"Periodic update error: {e}")
            await asyncio.sleep(60)  # Wait longer on error


# Start periodic updates (this would be called during app startup)
# asyncio.create_task(send_periodic_updates()) 