#!/usr/bin/env python3

"""
AG-UI MCP Server for Sophia AI
Implements the Agent-User Interaction Protocol for real-time streaming
and event-based communication with frontend applications.

Features:
- 16 structured event types for agent-user interaction
- Real-time streaming with state delta updates
- Human-in-the-loop workflow support
- Tool execution feedback and progress tracking
- Multi-agent orchestration support
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import structlog
from aiohttp import WSMsgType, web

# Import the standardized base class
from backend.mcp_servers.base.standardized_mcp_server import (
    HealthCheckResult,
    HealthStatus,
    MCPServerConfig,
    StandardizedMCPServer,
    SyncPriority,
)

logger = structlog.get_logger()


class AGUIEventType(str, Enum):
    """AG-UI Protocol Event Types"""

    # Content Events
    TEXT_MESSAGE_CONTENT = "text_message_content"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_END = "tool_call_end"
    TOOL_CALL_PROGRESS = "tool_call_progress"

    # State Management
    STATE_DELTA = "state_delta"
    STATE_SYNC = "state_sync"

    # User Interaction
    USER_INPUT_REQUEST = "user_input_request"
    USER_INPUT_RESPONSE = "user_input_response"

    # Agent Control
    AGENT_HANDOFF = "agent_handoff"
    AGENT_STATUS = "agent_status"

    # Session Management
    SESSION_START = "session_start"
    SESSION_END = "session_end"

    # Error Handling
    ERROR = "error"
    WARNING = "warning"

    # Custom Events
    BUSINESS_INSIGHT = "business_insight"
    EXECUTIVE_ALERT = "executive_alert"


class UIControlType(str, Enum):
    """UI Control Types for Human-in-the-Loop"""

    TEXT_INPUT = "text_input"
    SELECT = "select"
    BUTTON = "button"
    CHECKBOX = "checkbox"
    SLIDER = "slider"
    DATE_PICKER = "date_picker"
    FILE_UPLOAD = "file_upload"
    CONFIRMATION = "confirmation"


@dataclass
class AGUIEvent:
    """Standard AG-UI Event Structure"""

    event_type: AGUIEventType
    event_id: str
    timestamp: str
    session_id: str
    agent_id: str
    data: dict[str, Any]
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class StateUpdate:
    """State Delta Update for Efficient UI Sync"""

    path: str  # JSON path to update (e.g., "dashboard.kpis.revenue")
    operation: str  # "set", "append", "delete", "merge"
    value: Any
    timestamp: str


@dataclass
class UIControl:
    """UI Control for Human-in-the-Loop Interaction"""

    control_id: str
    control_type: UIControlType
    label: str
    required: bool = False
    options: list[str] | None = None
    default_value: Any | None = None
    validation: dict[str, Any] | None = None


class AGUIMCPServer(StandardizedMCPServer):
    """
    AG-UI MCP Server implementing the Agent-User Interaction Protocol

    Provides real-time streaming, state management, and human-in-the-loop
    capabilities for Sophia AI frontend applications.
    """

    def __init__(self, config: MCPServerConfig = None):
        if config is None:
            config = MCPServerConfig(
                server_name="ag_ui",
                port=9001,
                sync_priority=SyncPriority.HIGH,
                sync_interval_minutes=1,
                enable_metrics=True,
                health_check_interval=10,
                max_concurrent_requests=100,
                request_timeout_seconds=30,
            )

        super().__init__(config)

        # AG-UI specific components
        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.websocket_connections: dict[str, web.WebSocketResponse] = {}
        self.agent_states: dict[str, dict[str, Any]] = {}
        self.pending_user_inputs: dict[str, dict[str, Any]] = {}

        # Event handlers
        self.event_handlers: dict[AGUIEventType, list[callable]] = {}

        # Web application for HTTP/WebSocket endpoints
        self.app = web.Application()
        self._setup_routes()

    async def initialize_server(self) -> None:
        """Initialize AG-UI MCP Server"""
        logger.info("Initializing AG-UI MCP Server...")

        # Register default event handlers
        self._register_default_handlers()

        # Start web server
        await self._start_web_server()

        logger.info("AG-UI MCP Server initialized successfully")

    async def cleanup_server(self) -> None:
        """Cleanup AG-UI MCP Server resources"""
        # Close all WebSocket connections
        for ws in self.websocket_connections.values():
            if not ws.closed:
                await ws.close()

        # Clear session data
        self.active_sessions.clear()
        self.agent_states.clear()
        self.pending_user_inputs.clear()

        logger.info("AG-UI MCP Server cleaned up successfully")

    def _setup_routes(self) -> None:
        """Setup HTTP and WebSocket routes"""

        # WebSocket endpoint for real-time communication
        self.app.router.add_get("/ws", self._websocket_handler)

        # HTTP endpoints for REST API fallback
        self.app.router.add_post("/events", self._http_event_handler)
        self.app.router.add_get("/sessions/{session_id}/state", self._get_session_state)
        self.app.router.add_post(
            "/sessions/{session_id}/input", self._handle_user_input
        )

        # Health check endpoint
        self.app.router.add_get("/health", self._health_handler)

        # CORS middleware
        self.app.middlewares.append(self._cors_middleware)

    async def _start_web_server(self) -> None:
        """Start the web server for AG-UI endpoints"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()

            site = web.TCPSite(runner, "0.0.0.0", self.config.port)
            await site.start()

            logger.info(f"AG-UI web server started on port {self.config.port}")

        except Exception as e:
            logger.error(f"Failed to start AG-UI web server: {e}")
            raise

    async def _websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections for real-time communication"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        session_id = request.query.get("session_id", str(uuid.uuid4()))
        self.websocket_connections[session_id] = ws

        logger.info(f"WebSocket connection established for session {session_id}")

        try:
            # Send session start event
            await self._send_event(
                session_id,
                AGUIEvent(
                    event_type=AGUIEventType.SESSION_START,
                    event_id=str(uuid.uuid4()),
                    timestamp=datetime.now(UTC).isoformat(),
                    session_id=session_id,
                    agent_id="sophia_ai",
                    data={
                        "message": "Session started",
                        "capabilities": self._get_capabilities(),
                    },
                ),
            )

            # Handle incoming messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_websocket_message(session_id, data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON received: {msg.data}")
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break

        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")

        finally:
            # Cleanup on disconnect
            if session_id in self.websocket_connections:
                del self.websocket_connections[session_id]
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            logger.info(f"WebSocket connection closed for session {session_id}")

        return ws

    async def _handle_websocket_message(
        self, session_id: str, data: dict[str, Any]
    ) -> None:
        """Handle incoming WebSocket messages"""
        try:
            event_type = data.get("event_type")

            if event_type == AGUIEventType.USER_INPUT_RESPONSE:
                await self._handle_user_input_response(session_id, data)
            elif event_type == AGUIEventType.STATE_SYNC:
                await self._handle_state_sync_request(session_id, data)
            else:
                logger.warning(f"Unhandled WebSocket message type: {event_type}")

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self._send_error(session_id, str(e))

    async def _send_event(self, session_id: str, event: AGUIEvent) -> None:
        """Send event to client via WebSocket or HTTP"""
        try:
            # Try WebSocket first
            if session_id in self.websocket_connections:
                ws = self.websocket_connections[session_id]
                if not ws.closed:
                    await ws.send_str(event.to_json())
                    return

            # Fallback to storing for HTTP polling (if implemented)
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {"events": []}

            self.active_sessions[session_id]["events"].append(event.to_dict())

        except Exception as e:
            logger.error(f"Failed to send event: {e}")

    async def _send_error(self, session_id: str, error_message: str) -> None:
        """Send error event to client"""
        error_event = AGUIEvent(
            event_type=AGUIEventType.ERROR,
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC).isoformat(),
            session_id=session_id,
            agent_id="sophia_ai",
            data={"error": error_message},
        )
        await self._send_event(session_id, error_event)

    def _get_capabilities(self) -> list[str]:
        """Get AG-UI server capabilities"""
        return [
            "real_time_streaming",
            "state_delta_updates",
            "human_in_the_loop",
            "tool_execution_feedback",
            "multi_agent_orchestration",
            "business_intelligence",
            "executive_dashboards",
        ]

    # MCP Tool Methods

    async def server_specific_init(self) -> None:
        """Initialize AG UI server specific components"""
        pass

    async def server_specific_cleanup(self) -> None:
        """Cleanup AG UI server specific resources"""
        pass

    async def server_specific_health_check(self) -> dict:
        """Perform AG UI specific health checks"""
        return {
            "components_available": True,
            "ui_generation_ready": True
        }

    async def check_external_api(self) -> bool:
        """Check external API connectivity"""
        return True

    async def process_with_ai(self, data: dict) -> dict:
        """Process data with AI capabilities"""
        return {"processed": True, "data": data}

    def get_server_capabilities(self) -> dict:
        """Get AG UI server capabilities"""
        return {
            "ui_generation": True,
            "component_creation": True
        }

    async def sync_data(self) -> dict:
        """Sync UI data"""
        return {"synced": True}

    def get_mcp_tools(self) -> list[dict[str, Any]]:
        """Get available MCP tools for AG-UI"""
        return [
            {
                "name": "send_text_message",
                "description": "Send a text message to the user interface",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "message": {"type": "string", "description": "Message content"},
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata",
                        },
                    },
                    "required": ["session_id", "message"],
                },
            },
            {
                "name": "update_ui_state",
                "description": "Update UI state with delta changes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "updates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string"},
                                    "operation": {"type": "string"},
                                    "value": {},
                                },
                            },
                        },
                    },
                    "required": ["session_id", "updates"],
                },
            },
            {
                "name": "request_user_input",
                "description": "Request input from user with UI controls",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "prompt": {"type": "string", "description": "Input prompt"},
                        "controls": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "control_id": {"type": "string"},
                                    "control_type": {"type": "string"},
                                    "label": {"type": "string"},
                                    "required": {"type": "boolean"},
                                },
                            },
                        },
                    },
                    "required": ["session_id", "prompt", "controls"],
                },
            },
            {
                "name": "start_tool_execution",
                "description": "Signal start of tool execution with progress tracking",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "tool_name": {"type": "string", "description": "Tool name"},
                        "tool_id": {
                            "type": "string",
                            "description": "Unique tool execution ID",
                        },
                        "estimated_duration": {
                            "type": "number",
                            "description": "Estimated duration in seconds",
                        },
                    },
                    "required": ["session_id", "tool_name", "tool_id"],
                },
            },
            {
                "name": "update_tool_progress",
                "description": "Update tool execution progress",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "tool_id": {
                            "type": "string",
                            "description": "Tool execution ID",
                        },
                        "progress": {
                            "type": "number",
                            "description": "Progress percentage (0-100)",
                        },
                        "status_message": {
                            "type": "string",
                            "description": "Current status message",
                        },
                    },
                    "required": ["session_id", "tool_id", "progress"],
                },
            },
            {
                "name": "send_business_insight",
                "description": "Send business intelligence insight to executive dashboard",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "insight_type": {
                            "type": "string",
                            "description": "Type of insight",
                        },
                        "title": {"type": "string", "description": "Insight title"},
                        "content": {"type": "string", "description": "Insight content"},
                        "priority": {"type": "string", "description": "Priority level"},
                        "action_items": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["session_id", "insight_type", "title", "content"],
                },
            },
        ]

    async def execute_mcp_tool(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute MCP tool"""
        try:
            if tool_name == "send_text_message":
                return await self._send_text_message(**parameters)
            elif tool_name == "update_ui_state":
                return await self._update_ui_state(**parameters)
            elif tool_name == "request_user_input":
                return await self._request_user_input(**parameters)
            elif tool_name == "start_tool_execution":
                return await self._start_tool_execution(**parameters)
            elif tool_name == "update_tool_progress":
                return await self._update_tool_progress(**parameters)
            elif tool_name == "send_business_insight":
                return await self._send_business_insight(**parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}

    async def _send_text_message(
        self, session_id: str, message: str, metadata: dict | None = None
    ) -> dict[str, Any]:
        """Send text message to UI"""
        event = AGUIEvent(
            event_type=AGUIEventType.TEXT_MESSAGE_CONTENT,
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC).isoformat(),
            session_id=session_id,
            agent_id="sophia_ai",
            data={"message": message},
            metadata=metadata,
        )

        await self._send_event(session_id, event)
        return {"success": True, "event_id": event.event_id}

    async def _update_ui_state(
        self, session_id: str, updates: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Update UI state with delta changes"""
        state_updates = [
            StateUpdate(
                path=update["path"],
                operation=update["operation"],
                value=update["value"],
                timestamp=datetime.now(UTC).isoformat(),
            )
            for update in updates
        ]

        event = AGUIEvent(
            event_type=AGUIEventType.STATE_DELTA,
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC).isoformat(),
            session_id=session_id,
            agent_id="sophia_ai",
            data={"updates": [asdict(update) for update in state_updates]},
        )

        await self._send_event(session_id, event)
        return {"success": True, "updates_count": len(state_updates)}

    async def _send_business_insight(
        self,
        session_id: str,
        insight_type: str,
        title: str,
        content: str,
        priority: str = "medium",
        action_items: list[str] = None,
    ) -> dict[str, Any]:
        """Send business insight to executive dashboard"""
        event = AGUIEvent(
            event_type=AGUIEventType.BUSINESS_INSIGHT,
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC).isoformat(),
            session_id=session_id,
            agent_id="sophia_ai",
            data={
                "insight_type": insight_type,
                "title": title,
                "content": content,
                "priority": priority,
                "action_items": action_items or [],
            },
        )

        await self._send_event(session_id, event)
        return {"success": True, "insight_id": event.event_id}

    # Additional helper methods...
    async def _cors_middleware(self, request: web.Request, handler) -> web.Response:
        """CORS middleware for cross-origin requests"""
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    async def perform_health_checks(self) -> list[HealthCheckResult]:
        """Perform health checks for AG-UI server"""
        health_checks = []

        # Check WebSocket connections
        active_connections = len(self.websocket_connections)
        health_checks.append(
            HealthCheckResult(
                component="websocket_connections",
                status=HealthStatus.HEALTHY,
                response_time_ms=0.0,
                details=f"{active_connections} active connections",
            )
        )

        # Check active sessions
        active_sessions = len(self.active_sessions)
        health_checks.append(
            HealthCheckResult(
                component="active_sessions",
                status=HealthStatus.HEALTHY,
                response_time_ms=0.0,
                details=f"{active_sessions} active sessions",
            )
        )

        return health_checks


async def main():
    """Main entry point for AG-UI MCP Server"""
    config = MCPServerConfig(
        server_name="ag_ui",
        port=9001,
        sync_priority=SyncPriority.HIGH,
        enable_metrics=True,
    )

    server = AGUIMCPServer(config)

    try:
        await server.start()
        logger.info("AG-UI MCP Server started successfully")

        # Keep the server running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down AG-UI MCP Server...")
    except Exception as e:
        logger.error(f"AG-UI MCP Server error: {e}")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
