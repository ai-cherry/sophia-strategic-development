"""AG-UI Protocol Implementation for Real-time Agent-User Interaction
Provides real-time streaming, state synchronization, and multi-modal support
"""

import asyncio
import json
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class EventType(Enum):
    """AG-UI event types."""

    # Client to Agent events
    USER_MESSAGE = "user_message"
    USER_ACTION = "user_action"
    STATE_UPDATE = "state_update"
    CONTEXT_UPDATE = "context_update"

    # Agent to Client events
    AGENT_MESSAGE = "agent_message"
    AGENT_ACTION = "agent_action"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_PROGRESS = "workflow_progress"
    WORKFLOW_COMPLETE = "workflow_complete"
    STATE_SYNC = "state_sync"
    ERROR = "error"

    # System events
    CONNECTION_START = "connection_start"
    CONNECTION_END = "connection_end"
    HEARTBEAT = "heartbeat"


@dataclass
class AGUIEvent:
    """AG-UI protocol event."""

    type: EventType
    payload: Dict[str, Any]
    session_id: str
    timestamp: float
    event_id: str = None

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "type": self.type.value,
            "payload": self.payload,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "event_id": self.event_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AGUIEvent":
        """Create event from dictionary."""
        return cls(
            type=EventType(data["type"]),
            payload=data["payload"],
            session_id=data["session_id"],
            timestamp=data["timestamp"],
            event_id=data.get("event_id"),
        )


@dataclass
class SessionState:
    """Session state for AG-UI connections."""

    session_id: str
    user_id: Optional[str]
    context: Dict[str, Any]
    workflow_state: Dict[str, Any]
    last_activity: float
    created_at: float

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()


class WorkflowManager:
    """Manages multi-step workflows with real-time progress tracking."""

    def __init__(self):
        """Initialize workflow manager."""
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_callbacks: Dict[str, List[Callable]] = {}

    def start_workflow(
        self, session_id: str, workflow_type: str, parameters: Dict[str, Any]
    ) -> str:
        """Start a new workflow."""
        workflow_id = str(uuid.uuid4())

        self.active_workflows[workflow_id] = {
            "id": workflow_id,
            "session_id": session_id,
            "type": workflow_type,
            "parameters": parameters,
            "status": "running",
            "progress": 0.0,
            "steps": [],
            "current_step": None,
            "started_at": time.time(),
            "updated_at": time.time(),
        }

        logger.info(
            f"Started workflow {workflow_id} of type {workflow_type} for session {session_id}"
        )
        return workflow_id

    def update_workflow_progress(
        self, workflow_id: str, progress: float, step_info: Dict[str, Any] = None
    ):
        """Update workflow progress."""
        if workflow_id not in self.active_workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return

        workflow = self.active_workflows[workflow_id]
        workflow["progress"] = progress
        workflow["updated_at"] = time.time()

        if step_info:
            workflow["current_step"] = step_info
            workflow["steps"].append(
                {**step_info, "timestamp": time.time(), "progress": progress}
            )

        # Notify callbacks
        self._notify_workflow_callbacks(workflow_id, "progress", workflow)

    def complete_workflow(self, workflow_id: str, result: Dict[str, Any]):
        """Complete a workflow."""
        if workflow_id not in self.active_workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return

        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "completed"
        workflow["progress"] = 1.0
        workflow["result"] = result
        workflow["completed_at"] = time.time()

        # Notify callbacks
        self._notify_workflow_callbacks(workflow_id, "complete", workflow)

        logger.info(f"Completed workflow {workflow_id}")

    def fail_workflow(self, workflow_id: str, error: str):
        """Fail a workflow."""
        if workflow_id not in self.active_workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return

        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "failed"
        workflow["error"] = error
        workflow["failed_at"] = time.time()

        # Notify callbacks
        self._notify_workflow_callbacks(workflow_id, "error", workflow)

        logger.error(f"Failed workflow {workflow_id}: {error}")

    def register_callback(self, workflow_id: str, callback: Callable):
        """Register callback for workflow events."""
        if workflow_id not in self.workflow_callbacks:
            self.workflow_callbacks[workflow_id] = []
        self.workflow_callbacks[workflow_id].append(callback)

    def _notify_workflow_callbacks(
        self, workflow_id: str, event_type: str, workflow_data: Dict[str, Any]
    ):
        """Notify workflow callbacks."""
        if workflow_id in self.workflow_callbacks:
            for callback in self.workflow_callbacks[workflow_id]:
                try:
                    callback(event_type, workflow_data)
                except Exception as e:
                    logger.error(f"Workflow callback error: {e}")

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status."""
        return self.active_workflows.get(workflow_id)

    def cleanup_completed_workflows(self, max_age_hours: int = 24):
        """Clean up old completed workflows."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        to_remove = []
        for workflow_id, workflow in self.active_workflows.items():
            if workflow["status"] in ["completed", "failed"]:
                age = current_time - workflow.get(
                    "completed_at", workflow.get("failed_at", workflow["updated_at"])
                )
                if age > max_age_seconds:
                    to_remove.append(workflow_id)

        for workflow_id in to_remove:
            del self.active_workflows[workflow_id]
            if workflow_id in self.workflow_callbacks:
                del self.workflow_callbacks[workflow_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old workflows")


class AGUIProtocol:
    """AG-UI Protocol implementation for real-time agent-user interaction.
    """

    def __init__(self):
        """Initialize AG-UI protocol."""
        self.sessions: Dict[str, SessionState] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.workflow_manager = WorkflowManager()
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Performance metrics
        self.metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_events": 0,
            "events_per_second": 0.0,
            "avg_response_time_ms": 0.0,
        }

        # Initialize default event handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default event handlers."""
        self.register_event_handler(EventType.USER_MESSAGE, self._handle_user_message)
        self.register_event_handler(EventType.USER_ACTION, self._handle_user_action)
        self.register_event_handler(EventType.STATE_UPDATE, self._handle_state_update)
        self.register_event_handler(
            EventType.CONTEXT_UPDATE, self._handle_context_update
        )

    def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def create_session(
        self, user_id: Optional[str] = None, context: Dict[str, Any] = None
    ) -> str:
        """Create new AG-UI session."""
        session_id = str(uuid.uuid4())

        session_state = SessionState(
            session_id=session_id,
            user_id=user_id,
            context=context or {},
            workflow_state={},
            last_activity=time.time(),
            created_at=time.time(),
        )

        self.sessions[session_id] = session_state
        self.metrics["total_sessions"] += 1
        self.metrics["active_sessions"] += 1

        logger.info(f"Created AG-UI session {session_id} for user {user_id}")
        return session_id

    async def connect_websocket(self, websocket: WebSocket, session_id: str):
        """Connect WebSocket for real-time communication."""
        await websocket.accept()
        self.websocket_connections[session_id] = websocket

        # Send connection start event
        await self.emit_event(
            session_id,
            EventType.CONNECTION_START,
            {
                "session_id": session_id,
                "timestamp": time.time(),
                "protocol_version": "1.0",
            },
        )

        logger.info(f"WebSocket connected for session {session_id}")

        try:
            # Listen for incoming events
            while True:
                data = await websocket.receive_text()
                event_data = json.loads(data)
                event = AGUIEvent.from_dict(event_data)

                # Update session activity
                if session_id in self.sessions:
                    self.sessions[session_id].update_activity()

                # Process event
                await self.process_event(event)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error for session {session_id}: {e}")
        finally:
            # Clean up connection
            if session_id in self.websocket_connections:
                del self.websocket_connections[session_id]

            # Send connection end event
            await self.emit_event(
                session_id,
                EventType.CONNECTION_END,
                {"session_id": session_id, "timestamp": time.time()},
            )

    async def process_event(self, event: AGUIEvent):
        """Process incoming AG-UI event."""
        start_time = time.perf_counter()

        try:
            # Update metrics
            self.metrics["total_events"] += 1

            # Call event handlers
            if event.type in self.event_handlers:
                for handler in self.event_handlers[event.type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Event handler error for {event.type}: {e}")
                        await self.emit_event(
                            event.session_id,
                            EventType.ERROR,
                            {"error": str(e), "event_id": event.event_id},
                        )
            else:
                logger.warning(f"No handlers registered for event type {event.type}")

            # Update response time metrics
            response_time = (time.perf_counter() - start_time) * 1000
            self._update_response_time_metrics(response_time)

        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            await self.emit_event(
                event.session_id,
                EventType.ERROR,
                {"error": str(e), "event_id": event.event_id},
            )

    async def emit_event(
        self, session_id: str, event_type: EventType, payload: Dict[str, Any]
    ):
        """Emit event to client."""
        event = AGUIEvent(
            type=event_type,
            payload=payload,
            session_id=session_id,
            timestamp=time.time(),
        )

        # Send via WebSocket if connected
        if session_id in self.websocket_connections:
            try:
                websocket = self.websocket_connections[session_id]
                await websocket.send_text(json.dumps(event.to_dict()))
            except Exception as e:
                logger.error(f"Failed to send event via WebSocket: {e}")

        # Store in session state for HTTP polling fallback
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if "pending_events" not in session.context:
                session.context["pending_events"] = []
            session.context["pending_events"].append(event.to_dict())

            # Keep only last 100 events
            if len(session.context["pending_events"]) > 100:
                session.context["pending_events"] = session.context["pending_events"][
                    -100:
                ]

    async def stream_events(self, session_id: str) -> AsyncGenerator[str, None]:
        """Stream events via HTTP Server-Sent Events."""
        if session_id not in self.sessions:
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return

        session = self.sessions[session_id]
        last_event_time = time.time()

        # Send initial connection event
        yield f"data: {json.dumps({'type': 'stream_start', 'session_id': session_id, 'timestamp': time.time()})}\n\n"

        try:
            while True:
                # Check for pending events
                pending_events = session.context.get("pending_events", [])
                new_events = [
                    e for e in pending_events if e["timestamp"] > last_event_time
                ]

                for event in new_events:
                    yield f"data: {json.dumps(event)}\n\n"
                    last_event_time = event["timestamp"]

                # Send heartbeat every 30 seconds
                if time.time() - last_event_time > 30:
                    heartbeat = {
                        "type": "heartbeat",
                        "session_id": session_id,
                        "timestamp": time.time(),
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
                    last_event_time = time.time()

                await asyncio.sleep(1)  # Poll every second

        except Exception as e:
            logger.error(f"Event streaming error for session {session_id}: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    async def _handle_user_message(self, event: AGUIEvent):
        """Handle user message event."""
        message = event.payload.get("message", "")
        context = event.payload.get("context", {})

        # Import here to avoid circular imports

        # Process message through hybrid RAG router
        try:
            # Start workflow for message processing
            workflow_id = self.workflow_manager.start_workflow(
                event.session_id,
                "message_processing",
                {"message": message, "context": context},
            )

            # Emit workflow start event
            await self.emit_event(
                event.session_id,
                EventType.WORKFLOW_START,
                {
                    "workflow_id": workflow_id,
                    "type": "message_processing",
                    "message": message,
                },
            )

            # Register workflow callback
            self.workflow_manager.register_callback(
                workflow_id,
                lambda event_type, workflow_data: asyncio.create_task(
                    self._workflow_callback(event.session_id, event_type, workflow_data)
                ),
            )

            # Process message asynchronously
            asyncio.create_task(
                self._process_user_message_async(
                    event.session_id, workflow_id, message, context
                )
            )

        except Exception as e:
            logger.error(f"Error handling user message: {e}")
            await self.emit_event(
                event.session_id, EventType.ERROR, {"error": str(e), "message": message}
            )

    async def _process_user_message_async(
        self, session_id: str, workflow_id: str, message: str, context: Dict[str, Any]
    ):
        """Process user message asynchronously."""
        try:
            from backend.core.hybrid_rag_router import hybrid_rag_router

            # Update workflow progress
            self.workflow_manager.update_workflow_progress(
                workflow_id,
                0.1,
                {
                    "step": "routing_query",
                    "description": "Determining optimal processing strategy",
                },
            )

            # Process through hybrid RAG router
            result = await hybrid_rag_router.route_query(message, context, stream=False)

            # Update workflow progress
            self.workflow_manager.update_workflow_progress(
                workflow_id,
                0.8,
                {
                    "step": "processing_complete",
                    "description": "Query processing completed",
                },
            )

            # Emit agent response
            await self.emit_event(
                session_id,
                EventType.AGENT_MESSAGE,
                {
                    "message": result.get("data", {}).get(
                        "primary_result", "No response generated"
                    ),
                    "confidence": result.get("confidence", 0.0),
                    "routing_info": result.get("routing_metadata", {}),
                    "workflow_id": workflow_id,
                },
            )

            # Complete workflow
            self.workflow_manager.complete_workflow(workflow_id, result)

        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            self.workflow_manager.fail_workflow(workflow_id, str(e))

    async def _workflow_callback(
        self, session_id: str, event_type: str, workflow_data: Dict[str, Any]
    ):
        """Handle workflow callbacks."""
        if event_type == "progress":
            await self.emit_event(
                session_id,
                EventType.WORKFLOW_PROGRESS,
                {
                    "workflow_id": workflow_data["id"],
                    "progress": workflow_data["progress"],
                    "current_step": workflow_data.get("current_step"),
                    "status": workflow_data["status"],
                },
            )
        elif event_type == "complete":
            await self.emit_event(
                session_id,
                EventType.WORKFLOW_COMPLETE,
                {
                    "workflow_id": workflow_data["id"],
                    "result": workflow_data.get("result"),
                    "execution_time": workflow_data.get("completed_at", 0)
                    - workflow_data["started_at"],
                },
            )
        elif event_type == "error":
            await self.emit_event(
                session_id,
                EventType.ERROR,
                {
                    "workflow_id": workflow_data["id"],
                    "error": workflow_data.get("error"),
                    "workflow_type": workflow_data["type"],
                },
            )

    async def _handle_user_action(self, event: AGUIEvent):
        """Handle user action event."""
        action = event.payload.get("action", "")
        parameters = event.payload.get("parameters", {})

        # Emit acknowledgment
        await self.emit_event(
            event.session_id,
            EventType.AGENT_ACTION,
            {
                "action": f"acknowledged_{action}",
                "parameters": parameters,
                "timestamp": time.time(),
            },
        )

    async def _handle_state_update(self, event: AGUIEvent):
        """Handle state update event."""
        if event.session_id in self.sessions:
            session = self.sessions[event.session_id]
            state_updates = event.payload.get("state", {})
            session.workflow_state.update(state_updates)

            # Emit state sync confirmation
            await self.emit_event(
                event.session_id,
                EventType.STATE_SYNC,
                {"updated_state": state_updates, "full_state": session.workflow_state},
            )

    async def _handle_context_update(self, event: AGUIEvent):
        """Handle context update event."""
        if event.session_id in self.sessions:
            session = self.sessions[event.session_id]
            context_updates = event.payload.get("context", {})
            session.context.update(context_updates)

            # Emit context sync confirmation
            await self.emit_event(
                event.session_id,
                EventType.STATE_SYNC,
                {"updated_context": context_updates},
            )

    def _update_response_time_metrics(self, response_time_ms: float):
        """Update response time metrics."""
        total_events = self.metrics["total_events"]
        current_avg = self.metrics["avg_response_time_ms"]
        self.metrics["avg_response_time_ms"] = (
            current_avg * (total_events - 1) + response_time_ms
        ) / total_events

    async def cleanup_inactive_sessions(self, max_inactive_hours: int = 24):
        """Clean up inactive sessions."""
        current_time = time.time()
        max_inactive_seconds = max_inactive_hours * 3600

        inactive_sessions = []
        for session_id, session in self.sessions.items():
            if current_time - session.last_activity > max_inactive_seconds:
                inactive_sessions.append(session_id)

        for session_id in inactive_sessions:
            del self.sessions[session_id]
            if session_id in self.websocket_connections:
                del self.websocket_connections[session_id]
            self.metrics["active_sessions"] -= 1

        if inactive_sessions:
            logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")

        # Also cleanup old workflows
        self.workflow_manager.cleanup_completed_workflows()

    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get comprehensive protocol statistics."""
        return {
            "sessions": {
                "total": self.metrics["total_sessions"],
                "active": self.metrics["active_sessions"],
                "websocket_connections": len(self.websocket_connections),
            },
            "events": {
                "total": self.metrics["total_events"],
                "avg_response_time_ms": self.metrics["avg_response_time_ms"],
            },
            "workflows": {
                "active": len(self.workflow_manager.active_workflows),
                "total_callbacks": sum(
                    len(callbacks)
                    for callbacks in self.workflow_manager.workflow_callbacks.values()
                ),
            },
            "event_handlers": {
                event_type.value: len(handlers)
                for event_type, handlers in self.event_handlers.items()
            },
        }


# Global instance
agui_protocol = AGUIProtocol()
