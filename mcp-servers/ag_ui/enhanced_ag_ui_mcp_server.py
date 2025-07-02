from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

import structlog
from aiohttp import WSMsgType, web

# Configure structured logging
logger = structlog.get_logger(__name__)


class AGUIEventType(Enum):
    """Enhanced AG-UI event types based on research findings"""

    # Core communication events
    TEXT_MESSAGE_CONTENT = "text_message_content"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_RESULT = "tool_call_result"
    TOOL_CALL_ERROR = "tool_call_error"

    # State management events
    STATE_DELTA = "state_delta"
    STATE_SYNC = "state_sync"
    STATE_RESET = "state_reset"

    # Real-time streaming events
    STREAM_START = "stream_start"
    STREAM_CHUNK = "stream_chunk"
    STREAM_END = "stream_end"
    STREAM_ERROR = "stream_error"

    # Human-in-the-loop events
    HUMAN_INPUT_REQUIRED = "human_input_required"
    HUMAN_FEEDBACK = "human_feedback"
    WORKFLOW_PAUSE = "workflow_pause"
    WORKFLOW_RESUME = "workflow_resume"

    # Business intelligence events
    BUSINESS_INSIGHT = "business_insight"
    EXECUTIVE_ALERT = "executive_alert"


@dataclass
class AGUIEvent:
    """Enhanced AG-UI event structure"""

    event_type: AGUIEventType
    event_id: str
    timestamp: float
    session_id: str
    user_id: str | None
    data: dict[str, Any]
    metadata: dict[str, Any]
    priority: str = "normal"  # low, normal, high, urgent

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for JSON serialization"""
        return {
            "eventType": self.event_type.value,
            "eventId": self.event_id,
            "timestamp": self.timestamp,
            "sessionId": self.session_id,
            "userId": self.user_id,
            "data": self.data,
            "metadata": self.metadata,
            "priority": self.priority,
        }


class EnhancedAGUIServer:
    """Enhanced AG-UI MCP Server with real-time capabilities"""

    def __init__(self, port: int = 9001):
        self.port = port
        self.app = web.Application()
        self.websocket_connections: dict[str, web.WebSocketResponse] = {}
        self.session_states: dict[str, dict[str, Any]] = {}
        self.event_history: dict[str, list[AGUIEvent]] = {}
        self.business_insights_queue: list[dict[str, Any]] = []

        # Setup routes
        self._setup_routes()

        logger.info("Enhanced AG-UI MCP Server initialized", port=port)

    def _setup_routes(self):
        """Setup HTTP and WebSocket routes"""
        # WebSocket endpoint for real-time communication
        self.app.router.add_get("/ws", self.websocket_handler)

        # HTTP endpoints for AG-UI protocol
        self.app.router.add_post("/api/v1/events", self.send_event)
        self.app.router.add_get("/api/v1/events/{session_id}", self.get_events)
        self.app.router.add_post("/api/v1/state/update", self.update_state)
        self.app.router.add_get("/api/v1/state/{session_id}", self.get_state)

        # Business intelligence endpoints
        self.app.router.add_post("/api/v1/business/insight", self.send_business_insight)
        self.app.router.add_get("/api/v1/business/insights", self.get_business_insights)
        self.app.router.add_post("/api/v1/executive/alert", self.send_executive_alert)

        # Health and status endpoints
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_get("/api/v1/status", self.get_server_status)

        # CORS middleware
        self.app.middlewares.append(self._cors_middleware)

    async def _cors_middleware(self, request, handler):
        """CORS middleware for cross-origin requests"""
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    async def websocket_handler(self, request):
        """Enhanced WebSocket handler with session management"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        session_id = str(uuid.uuid4())
        user_id = request.query.get("user_id")

        # Register connection
        self.websocket_connections[session_id] = ws
        self.session_states[session_id] = {
            "connected_at": time.time(),
            "user_id": user_id,
            "last_activity": time.time(),
            "state": {},
        }

        logger.info(
            "WebSocket connection established", session_id=session_id, user_id=user_id
        )

        # Send connection acknowledgment
        await self._send_to_websocket(
            session_id,
            AGUIEvent(
                event_type=AGUIEventType.STATE_SYNC,
                event_id=str(uuid.uuid4()),
                timestamp=time.time(),
                session_id=session_id,
                user_id=user_id,
                data={"status": "connected", "sessionId": session_id},
                metadata={"connection_type": "websocket"},
            ),
        )

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await self._handle_websocket_message(session_id, msg.data)
                elif msg.type == WSMsgType.ERROR:
                    logger.error("WebSocket error", error=ws.exception())
        except Exception as e:
            logger.error("WebSocket handler error", error=str(e))
        finally:
            # Cleanup connection
            if session_id in self.websocket_connections:
                del self.websocket_connections[session_id]
            if session_id in self.session_states:
                del self.session_states[session_id]

            logger.info("WebSocket connection closed", session_id=session_id)

        return ws

    async def _handle_websocket_message(self, session_id: str, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            event_type = AGUIEventType(data.get("eventType"))

            # Update last activity
            if session_id in self.session_states:
                self.session_states[session_id]["last_activity"] = time.time()

            # Process different event types
            if event_type == AGUIEventType.HUMAN_FEEDBACK:
                await self._process_human_feedback(session_id, data)
            elif event_type == AGUIEventType.STATE_DELTA:
                await self._process_state_delta(session_id, data)
            elif event_type == AGUIEventType.TEXT_MESSAGE_CONTENT:
                await self._process_text_message(session_id, data)

            logger.info(
                "WebSocket message processed",
                session_id=session_id,
                event_type=event_type.value,
            )

        except Exception as e:
            logger.error(
                "Error processing WebSocket message",
                session_id=session_id,
                error=str(e),
            )

            # Send error event
            await self._send_to_websocket(
                session_id,
                AGUIEvent(
                    event_type=AGUIEventType.STREAM_ERROR,
                    event_id=str(uuid.uuid4()),
                    timestamp=time.time(),
                    session_id=session_id,
                    user_id=self.session_states.get(session_id, {}).get("user_id"),
                    data={"error": str(e)},
                    metadata={"error_source": "websocket_message_processing"},
                ),
            )

    async def _send_to_websocket(self, session_id: str, event: AGUIEvent):
        """Send event to specific WebSocket connection"""
        if session_id in self.websocket_connections:
            ws = self.websocket_connections[session_id]
            try:
                await ws.send_text(json.dumps(event.to_dict()))

                # Store in event history
                if session_id not in self.event_history:
                    self.event_history[session_id] = []
                self.event_history[session_id].append(event)

                # Keep only last 100 events per session
                if len(self.event_history[session_id]) > 100:
                    self.event_history[session_id] = self.event_history[session_id][
                        -100:
                    ]

            except Exception as e:
                logger.error(
                    "Error sending WebSocket message",
                    session_id=session_id,
                    error=str(e),
                )

    async def _broadcast_to_all(self, event: AGUIEvent):
        """Broadcast event to all connected WebSocket clients"""
        for session_id in list(self.websocket_connections.keys()):
            event.session_id = session_id
            await self._send_to_websocket(session_id, event)

    async def _process_human_feedback(self, session_id: str, data: dict[str, Any]):
        """Process human feedback events"""
        feedback_type = data.get("feedbackType", "general")
        feedback_content = data.get("content", "")

        # Store feedback in session state
        if session_id in self.session_states:
            if "feedback" not in self.session_states[session_id]:
                self.session_states[session_id]["feedback"] = []

            self.session_states[session_id]["feedback"].append(
                {
                    "type": feedback_type,
                    "content": feedback_content,
                    "timestamp": time.time(),
                }
            )

        # Send acknowledgment
        await self._send_to_websocket(
            session_id,
            AGUIEvent(
                event_type=AGUIEventType.HUMAN_FEEDBACK,
                event_id=str(uuid.uuid4()),
                timestamp=time.time(),
                session_id=session_id,
                user_id=self.session_states.get(session_id, {}).get("user_id"),
                data={"status": "received", "feedbackType": feedback_type},
                metadata={"processing_status": "acknowledged"},
            ),
        )

    async def _process_state_delta(self, session_id: str, data: dict[str, Any]):
        """Process state delta updates"""
        if session_id in self.session_states:
            delta = data.get("delta", {})

            # Apply delta to session state
            current_state = self.session_states[session_id].get("state", {})
            for key, value in delta.items():
                current_state[key] = value

            self.session_states[session_id]["state"] = current_state

            # Broadcast state update
            await self._send_to_websocket(
                session_id,
                AGUIEvent(
                    event_type=AGUIEventType.STATE_DELTA,
                    event_id=str(uuid.uuid4()),
                    timestamp=time.time(),
                    session_id=session_id,
                    user_id=self.session_states.get(session_id, {}).get("user_id"),
                    data={"delta": delta, "fullState": current_state},
                    metadata={"state_version": str(time.time())},
                ),
            )

    async def _process_text_message(self, session_id: str, data: dict[str, Any]):
        """Process text message events"""
        message = data.get("message", "")
        context = data.get("context", {})

        # Echo back with processing status
        await self._send_to_websocket(
            session_id,
            AGUIEvent(
                event_type=AGUIEventType.TEXT_MESSAGE_CONTENT,
                event_id=str(uuid.uuid4()),
                timestamp=time.time(),
                session_id=session_id,
                user_id=self.session_states.get(session_id, {}).get("user_id"),
                data={
                    "message": f"Received: {message}",
                    "originalMessage": message,
                    "context": context,
                    "processing": "acknowledged",
                },
                metadata={"message_type": "echo_response"},
            ),
        )

    # HTTP Endpoints

    async def send_event(self, request):
        """HTTP endpoint to send AG-UI events"""
        try:
            data = await request.json()

            event = AGUIEvent(
                event_type=AGUIEventType(data["eventType"]),
                event_id=data.get("eventId", str(uuid.uuid4())),
                timestamp=data.get("timestamp", time.time()),
                session_id=data["sessionId"],
                user_id=data.get("userId"),
                data=data.get("data", {}),
                metadata=data.get("metadata", {}),
                priority=data.get("priority", "normal"),
            )

            # Send to WebSocket if connected
            await self._send_to_websocket(event.session_id, event)

            return web.json_response(
                {
                    "success": True,
                    "eventId": event.event_id,
                    "timestamp": event.timestamp,
                }
            )

        except Exception as e:
            logger.error("Error sending event", error=str(e))
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def get_events(self, request):
        """Get event history for a session"""
        session_id = request.match_info["session_id"]

        events = self.event_history.get(session_id, [])
        return web.json_response(
            {
                "sessionId": session_id,
                "events": [event.to_dict() for event in events],
                "totalEvents": len(events),
            }
        )

    async def update_state(self, request):
        """Update session state"""
        try:
            data = await request.json()
            session_id = data["sessionId"]
            state_update = data.get("state", {})

            if session_id in self.session_states:
                self.session_states[session_id]["state"].update(state_update)

                # Broadcast state update
                await self._send_to_websocket(
                    session_id,
                    AGUIEvent(
                        event_type=AGUIEventType.STATE_SYNC,
                        event_id=str(uuid.uuid4()),
                        timestamp=time.time(),
                        session_id=session_id,
                        user_id=self.session_states.get(session_id, {}).get("user_id"),
                        data={"state": self.session_states[session_id]["state"]},
                        metadata={"update_source": "http_api"},
                    ),
                )

            return web.json_response({"success": True})

        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def get_state(self, request):
        """Get current session state"""
        session_id = request.match_info["session_id"]

        state = self.session_states.get(session_id, {})
        return web.json_response(
            {
                "sessionId": session_id,
                "state": state.get("state", {}),
                "metadata": {
                    "connectedAt": state.get("connected_at"),
                    "lastActivity": state.get("last_activity"),
                    "userId": state.get("user_id"),
                },
            }
        )

    async def send_business_insight(self, request):
        """Send business insight to executive dashboard"""
        try:
            data = await request.json()

            insight = {
                "id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "type": data.get("type", "general"),
                "title": data.get("title", ""),
                "content": data.get("content", ""),
                "priority": data.get("priority", "normal"),
                "source": data.get("source", "unknown"),
                "metadata": data.get("metadata", {}),
            }

            self.business_insights_queue.append(insight)

            # Broadcast to all connected clients
            await self._broadcast_to_all(
                AGUIEvent(
                    event_type=AGUIEventType.BUSINESS_INSIGHT,
                    event_id=insight["id"],
                    timestamp=insight["timestamp"],
                    session_id="broadcast",
                    user_id=None,
                    data=insight,
                    metadata={"broadcast": True},
                    priority=insight["priority"],
                )
            )

            return web.json_response({"success": True, "insightId": insight["id"]})

        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def get_business_insights(self, request):
        """Get recent business insights"""
        limit = int(request.query.get("limit", 50))
        return web.json_response(
            {
                "insights": self.business_insights_queue[-limit:],
                "totalInsights": len(self.business_insights_queue),
            }
        )

    async def send_executive_alert(self, request):
        """Send high-priority executive alert"""
        try:
            data = await request.json()

            alert = {
                "id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "title": data.get("title", "Executive Alert"),
                "message": data.get("message", ""),
                "severity": data.get("severity", "high"),
                "actionRequired": data.get("actionRequired", False),
                "source": data.get("source", "system"),
                "metadata": data.get("metadata", {}),
            }

            # Broadcast urgent alert to all connected clients
            await self._broadcast_to_all(
                AGUIEvent(
                    event_type=AGUIEventType.EXECUTIVE_ALERT,
                    event_id=alert["id"],
                    timestamp=alert["timestamp"],
                    session_id="broadcast",
                    user_id=None,
                    data=alert,
                    metadata={"broadcast": True, "urgent": True},
                    priority="urgent",
                )
            )

            return web.json_response({"success": True, "alertId": alert["id"]})

        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response(
            {
                "status": "healthy",
                "timestamp": time.time(),
                "connections": len(self.websocket_connections),
                "sessions": len(self.session_states),
                "insights_queued": len(self.business_insights_queue),
            }
        )

    async def get_server_status(self, request):
        """Get detailed server status"""
        return web.json_response(
            {
                "server": "Enhanced AG-UI MCP Server",
                "version": "1.0.0",
                "uptime": time.time(),
                "port": self.port,
                "connections": {
                    "websocket": len(self.websocket_connections),
                    "total_sessions": len(self.session_states),
                },
                "metrics": {
                    "total_events": sum(
                        len(events) for events in self.event_history.values()
                    ),
                    "business_insights": len(self.business_insights_queue),
                    "active_sessions": len(
                        [
                            s
                            for s in self.session_states.values()
                            if time.time() - s.get("last_activity", 0) < 300
                        ]
                    ),
                },
            }
        )

    async def start_server(self):
        """Start the AG-UI MCP server"""
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()

        logger.info(
            "Enhanced AG-UI MCP Server started",
            port=self.port,
            websocket_endpoint=f"ws://localhost:{self.port}/ws",
            api_endpoint=f"http://localhost:{self.port}/api/v1",
        )

        return runner


async def main():
    """Main function to run the Enhanced AG-UI MCP Server"""
    server = EnhancedAGUIServer(port=9001)
    runner = await server.start_server()

    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Enhanced AG-UI MCP Server")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

    async def server_specific_init(self):
        """Server-specific initialization"""
        # TODO: Add server-specific initialization
        pass

    def _setup_server_routes(self):
        """Setup server-specific routes"""
        # Existing routes should be moved here
        pass

    async def check_server_health(self) -> bool:
        """Check server health"""
        # TODO: Implement health check
        return True

    async def server_specific_shutdown(self):
        """Server-specific shutdown"""
        # TODO: Add cleanup logic
        pass
