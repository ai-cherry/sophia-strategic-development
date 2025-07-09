"""
Enhanced WebSocket Handler for Sophia AI v3.0

Multi-channel streaming for real-time agent coordination,
progress tracking, and system status updates.

Date: July 9, 2025
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.services.enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator
from backend.services.unified_chat_service import UnifiedChatService

import logging
logger = logging.getLogger(__name__)


class WebSocketChannel(BaseModel):
    """WebSocket channel configuration"""
    name: str
    description: str
    active: bool = True
    subscribers: Set[str] = set()


class EnhancedWebSocketMessage(BaseModel):
    """Enhanced WebSocket message structure"""
    type: str
    channel: str
    data: Dict[str, Any]
    timestamp: str
    message_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class WebSocketSession:
    """WebSocket session management"""
    
    def __init__(self, websocket: WebSocket, user_id: str, session_id: str):
        self.websocket = websocket
        self.user_id = user_id
        self.session_id = session_id
        self.subscribed_channels: Set[str] = set()
        self.active = True
        self.connected_at = datetime.now()
        self.last_activity = datetime.now()
        
    async def send_message(self, message: EnhancedWebSocketMessage):
        """Send message to WebSocket client"""
        if not self.active:
            return
        
        try:
            await self.websocket.send_text(message.json())
            self.last_activity = datetime.now()
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            self.active = False
    
    def subscribe_to_channel(self, channel: str):
        """Subscribe to a channel"""
        self.subscribed_channels.add(channel)
    
    def unsubscribe_from_channel(self, channel: str):
        """Unsubscribe from a channel"""
        self.subscribed_channels.discard(channel)
    
    def is_subscribed_to(self, channel: str) -> bool:
        """Check if subscribed to channel"""
        return channel in self.subscribed_channels


class EnhancedWebSocketHandler:
    """
    Enhanced WebSocket handler with multi-channel streaming
    """
    
    def __init__(self):
        # Channel configuration
        self.channels = {
            "chat": WebSocketChannel(
                name="chat",
                description="Main chat responses and interactions"
            ),
            "agents": WebSocketChannel(
                name="agents",
                description="Agent coordination and status updates"
            ),
            "progress": WebSocketChannel(
                name="progress",
                description="Real-time progress tracking"
            ),
            "automation": WebSocketChannel(
                name="automation",
                description="Browser automation status and updates"
            ),
            "system": WebSocketChannel(
                name="system",
                description="System status and date/time updates"
            ),
            "metrics": WebSocketChannel(
                name="metrics",
                description="Performance and cost metrics"
            )
        }
        
        # Active sessions
        self.active_sessions: Dict[str, WebSocketSession] = {}
        
        # Services
        self.enhanced_orchestrator = EnhancedMultiAgentOrchestrator()
        self.unified_chat_service = UnifiedChatService()
        
        # System state
        self.current_date = "July 9, 2025"
        self.system_status = {
            "date_validated": True,
            "orchestrator_active": True,
            "agents_available": ["database", "web_search", "project_intelligence", "synthesis"],
            "last_health_check": datetime.now().isoformat()
        }
        
    async def handle_connection(self, websocket: WebSocket, user_id: str, session_id: str):
        """Handle new WebSocket connection"""
        
        try:
            await websocket.accept()
            
            # Create session
            session = WebSocketSession(websocket, user_id, session_id)
            self.active_sessions[session_id] = session
            
            # Subscribe to default channels
            session.subscribe_to_channel("chat")
            session.subscribe_to_channel("system")
            
            # Send connection acknowledgment with current date
            await session.send_message(EnhancedWebSocketMessage(
                type="connection_established",
                channel="system",
                data={
                    "session_id": session_id,
                    "user_id": user_id,
                    "current_date": self.current_date,
                    "system_date_validated": True,
                    "available_channels": list(self.channels.keys()),
                    "system_status": self.system_status
                },
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
                user_id=user_id
            ))
            
            logger.info(f"WebSocket connection established: {session_id}")
            
            # Handle messages
            await self._handle_messages(session)
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            # Clean up session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    async def _handle_messages(self, session: WebSocketSession):
        """Handle incoming WebSocket messages"""
        
        try:
            while session.active:
                # Receive message
                message_data = await session.websocket.receive_text()
                message = json.loads(message_data)
                
                # Update last activity
                session.last_activity = datetime.now()
                
                # Route message based on type
                message_type = message.get("type", "unknown")
                
                if message_type == "chat_message":
                    await self._handle_chat_message(session, message)
                elif message_type == "channel_subscribe":
                    await self._handle_channel_subscribe(session, message)
                elif message_type == "channel_unsubscribe":
                    await self._handle_channel_unsubscribe(session, message)
                elif message_type == "system_status":
                    await self._handle_system_status_request(session, message)
                elif message_type == "agent_status":
                    await self._handle_agent_status_request(session, message)
                else:
                    await self._handle_unknown_message(session, message)
                    
        except WebSocketDisconnect:
            session.active = False
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            session.active = False
    
    async def _handle_chat_message(self, session: WebSocketSession, message: Dict[str, Any]):
        """Handle chat message with enhanced orchestration"""
        
        try:
            query = message.get("content", "")
            message_id = message.get("id", f"msg_{datetime.now().timestamp()}")
            
            # Send initial acknowledgment with correct date
            await session.send_message(EnhancedWebSocketMessage(
                type="chat_started",
                channel="chat",
                data={
                    "message_id": message_id,
                    "query": query,
                    "current_date": self.current_date,
                    "system_date_validated": True,
                    "orchestration_type": "enhanced_multi_agent"
                },
                timestamp=datetime.now().isoformat(),
                message_id=message_id,
                session_id=session.session_id,
                user_id=session.user_id
            ))
            
            # Process with enhanced orchestrator
            async for update in self.enhanced_orchestrator.stream_process(query, {
                "user_id": session.user_id,
                "session_id": session.session_id,
                "current_date": self.current_date
            }):
                await self._route_orchestration_update(session, update, message_id)
                
        except Exception as e:
            logger.error(f"Chat message handling error: {e}")
            
            # Send error response
            await session.send_message(EnhancedWebSocketMessage(
                type="chat_error",
                channel="chat",
                data={
                    "error": str(e),
                    "message_id": message.get("id"),
                    "current_date": self.current_date,
                    "fallback_available": True
                },
                timestamp=datetime.now().isoformat(),
                session_id=session.session_id,
                user_id=session.user_id
            ))
    
    async def _route_orchestration_update(self, session: WebSocketSession, update: Dict[str, Any], message_id: str):
        """Route orchestration updates to appropriate channels"""
        
        update_type = update.get("type", "unknown")
        
        # Route to specific channels based on update type
        if update_type == "date_validation":
            if session.is_subscribed_to("system"):
                await session.send_message(EnhancedWebSocketMessage(
                    type="system_update",
                    channel="system",
                    data={
                        "update_type": "date_validation",
                        "current_date": update.get("current_date", self.current_date),
                        "status": update.get("status", "unknown"),
                        "timestamp": update.get("timestamp")
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=message_id,
                    session_id=session.session_id,
                    user_id=session.user_id
                ))
        
        elif update_type == "query_analysis":
            if session.is_subscribed_to("agents"):
                await session.send_message(EnhancedWebSocketMessage(
                    type="query_analysis",
                    channel="agents",
                    data={
                        "analysis": update.get("analysis", {}),
                        "status": update.get("status", "unknown"),
                        "timestamp": update.get("timestamp")
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=message_id,
                    session_id=session.session_id,
                    user_id=session.user_id
                ))
        
        elif update_type == "agent_selection":
            if session.is_subscribed_to("agents"):
                await session.send_message(EnhancedWebSocketMessage(
                    type="agent_selection",
                    channel="agents",
                    data={
                        "selected_agents": update.get("selected_agents", []),
                        "execution_strategy": update.get("execution_strategy", "parallel"),
                        "status": update.get("status", "unknown"),
                        "timestamp": update.get("timestamp")
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=message_id,
                    session_id=session.session_id,
                    user_id=session.user_id
                ))
        
        elif update_type == "agent_progress":
            if session.is_subscribed_to("agents"):
                await session.send_message(EnhancedWebSocketMessage(
                    type="agent_progress",
                    channel="agents",
                    data={
                        "agent": update.get("agent", "unknown"),
                        "status": update.get("status", "unknown"),
                        "result": update.get("result", {}),
                        "timestamp": update.get("timestamp")
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=message_id,
                    session_id=session.session_id,
                    user_id=session.user_id
                ))
        
        elif update_type == "parallel_execution":
            if session.is_subscribed_to("progress"):
                await session.send_message(EnhancedWebSocketMessage(
                    type="execution_progress",
                    channel="progress",
                    data={
                        "execution_time": update.get("execution_time", 0),
                        "success_rate": update.get("success_rate", 0),
                        "results_count": update.get("results_count", 0),
                        "status": update.get("status", "unknown"),
                        "timestamp": update.get("timestamp")
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=message_id,
                    session_id=session.session_id,
                    user_id=session.user_id
                ))
        
        elif update_type == "automation_step":
            if session.is_subscribed_to("automation"):
                await session.send_message(EnhancedWebSocketMessage(
                    type="automation_update",
                    channel="automation",
                    data={
                        "step": update.get("step", {}),
                        "status": update.get("status", "unknown"),
                        "result": update.get("result", {}),
                        "error": update.get("error"),
                        "timestamp": update.get("timestamp")
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=message_id,
                    session_id=session.session_id,
                    user_id=session.user_id
                ))
        
        elif update_type == "response_synthesis":
            if session.is_subscribed_to("progress"):
                await session.send_message(EnhancedWebSocketMessage(
                    type="synthesis_progress",
                    channel="progress",
                    data={
                        "confidence": update.get("confidence", 0),
                        "status": update.get("status", "unknown"),
                        "timestamp": update.get("timestamp")
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=message_id,
                    session_id=session.session_id,
                    user_id=session.user_id
                ))
        
        elif update_type == "final_response":
            if session.is_subscribed_to("chat"):
                response_data = update.get("data", {})
                await session.send_message(EnhancedWebSocketMessage(
                    type="chat_response",
                    channel="chat",
                    data={
                        "response": response_data.get("response", ""),
                        "confidence": response_data.get("confidence", 0),
                        "processing_time": response_data.get("processing_time", 0),
                        "agents_used": response_data.get("agents_used", []),
                        "sources": response_data.get("sources", []),
                        "current_date": response_data.get("current_date", self.current_date),
                        "system_date_validated": response_data.get("system_date_validated", True),
                        "fallback_triggered": response_data.get("fallback_triggered", False),
                        "message_id": message_id
                    },
                    timestamp=datetime.now().isoformat(),
                    message_id=message_id,
                    session_id=session.session_id,
                    user_id=session.user_id
                ))
        
        # Send metrics update if subscribed
        if session.is_subscribed_to("metrics") and update_type == "final_response":
            response_data = update.get("data", {})
            await session.send_message(EnhancedWebSocketMessage(
                type="metrics_update",
                channel="metrics",
                data={
                    "processing_time": response_data.get("processing_time", 0),
                    "confidence": response_data.get("confidence", 0),
                    "agents_used": len(response_data.get("agents_used", [])),
                    "success": response_data.get("success", False),
                    "current_date": self.current_date,
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now().isoformat(),
                message_id=message_id,
                session_id=session.session_id,
                user_id=session.user_id
            ))
    
    async def _handle_channel_subscribe(self, session: WebSocketSession, message: Dict[str, Any]):
        """Handle channel subscription request"""
        
        channel = message.get("channel")
        if channel and channel in self.channels:
            session.subscribe_to_channel(channel)
            
            await session.send_message(EnhancedWebSocketMessage(
                type="channel_subscribed",
                channel="system",
                data={
                    "channel": channel,
                    "subscribed": True,
                    "current_subscriptions": list(session.subscribed_channels)
                },
                timestamp=datetime.now().isoformat(),
                session_id=session.session_id,
                user_id=session.user_id
            ))
    
    async def _handle_channel_unsubscribe(self, session: WebSocketSession, message: Dict[str, Any]):
        """Handle channel unsubscription request"""
        
        channel = message.get("channel")
        if channel:
            session.unsubscribe_from_channel(channel)
            
            await session.send_message(EnhancedWebSocketMessage(
                type="channel_unsubscribed",
                channel="system",
                data={
                    "channel": channel,
                    "subscribed": False,
                    "current_subscriptions": list(session.subscribed_channels)
                },
                timestamp=datetime.now().isoformat(),
                session_id=session.session_id,
                user_id=session.user_id
            ))
    
    async def _handle_system_status_request(self, session: WebSocketSession, message: Dict[str, Any]):
        """Handle system status request"""
        
        # Update system status
        self.system_status.update({
            "current_date": self.current_date,
            "date_validated": True,
            "active_sessions": len(self.active_sessions),
            "orchestrator_active": True,
            "last_health_check": datetime.now().isoformat()
        })
        
        await session.send_message(EnhancedWebSocketMessage(
            type="system_status",
            channel="system",
            data=self.system_status,
            timestamp=datetime.now().isoformat(),
            session_id=session.session_id,
            user_id=session.user_id
        ))
    
    async def _handle_agent_status_request(self, session: WebSocketSession, message: Dict[str, Any]):
        """Handle agent status request"""
        
        agent_status = {
            "available_agents": ["database", "web_search", "project_intelligence", "synthesis"],
            "browser_automation_status": "Phase 2 implementation pending",
            "orchestrator_type": "enhanced_multi_agent",
            "parallel_execution": True,
            "current_date": self.current_date,
            "last_updated": datetime.now().isoformat()
        }
        
        await session.send_message(EnhancedWebSocketMessage(
            type="agent_status",
            channel="agents",
            data=agent_status,
            timestamp=datetime.now().isoformat(),
            session_id=session.session_id,
            user_id=session.user_id
        ))
    
    async def _handle_unknown_message(self, session: WebSocketSession, message: Dict[str, Any]):
        """Handle unknown message type"""
        
        await session.send_message(EnhancedWebSocketMessage(
            type="unknown_message",
            channel="system",
            data={
                "error": "Unknown message type",
                "received_message": message,
                "current_date": self.current_date
            },
            timestamp=datetime.now().isoformat(),
            session_id=session.session_id,
            user_id=session.user_id
        ))
    
    async def broadcast_to_channel(self, channel: str, message: EnhancedWebSocketMessage):
        """Broadcast message to all subscribers of a channel"""
        
        if channel not in self.channels:
            return
        
        for session in self.active_sessions.values():
            if session.is_subscribed_to(channel) and session.active:
                try:
                    await session.send_message(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to session {session.session_id}: {e}")
                    session.active = False
    
    async def get_session_metrics(self) -> Dict[str, Any]:
        """Get WebSocket session metrics"""
        
        active_sessions = len(self.active_sessions)
        channel_subscriptions = {}
        
        for channel_name in self.channels.keys():
            channel_subscriptions[channel_name] = sum(
                1 for session in self.active_sessions.values() 
                if session.is_subscribed_to(channel_name)
            )
        
        return {
            "active_sessions": active_sessions,
            "channel_subscriptions": channel_subscriptions,
            "system_status": self.system_status,
            "current_date": self.current_date,
            "last_updated": datetime.now().isoformat()
        }
    
    async def cleanup_inactive_sessions(self):
        """Clean up inactive sessions"""
        
        inactive_sessions = []
        current_time = datetime.now()
        
        for session_id, session in self.active_sessions.items():
            # Mark as inactive if no activity for 30 minutes
            if (current_time - session.last_activity).total_seconds() > 1800:
                session.active = False
                inactive_sessions.append(session_id)
        
        # Remove inactive sessions
        for session_id in inactive_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up inactive session: {session_id}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        
        # Clean up inactive sessions
        await self.cleanup_inactive_sessions()
        
        # Update system status
        self.system_status.update({
            "current_date": self.current_date,
            "date_validated": True,
            "active_sessions": len(self.active_sessions),
            "orchestrator_active": True,
            "last_health_check": datetime.now().isoformat()
        })
        
        return {
            "healthy": True,
            "system_status": self.system_status,
            "session_metrics": await self.get_session_metrics()
        } 