"""Context Management Layer for Sophia AI.

Maintains and manages context across all agents and sessions
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SessionContext:
    """Context for a single user session"""
        session_id: str
    user_id: str
    user_role: str = "viewer"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)

    # Tool-specific contexts
    docker_context: Dict[str, Any] = field(default_factory=dict)
    pulumi_context: Dict[str, Any] = field(default_factory=dict)
    claude_context: Dict[str, Any] = field(default_factory=dict)

    # General context
    current_project: Optional[str] = None
    current_environment: str = "development"
    command_history: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "user_role": self.user_role,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "docker_context": self.docker_context,
            "pulumi_context": self.pulumi_context,
            "claude_context": self.claude_context,
            "current_project": self.current_project,
            "current_environment": self.current_environment,
            "command_history": self.command_history[-50:],  # Keep last 50 commands
        }


class ContextManager:
    """Centralized context management for all agents.

    - Maintains session contexts
    - Provides context persistence
    - Handles context expiration
    - Thread-safe operations
    """
    def __init__(self, ttl_minutes: int = 60):
        self.sessions: Dict[str, SessionContext] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self._lock = asyncio.Lock()
        self._cleanup_task = None

    async def initialize(self):
        """Initialize context manager and start cleanup task"""
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        logger.info("Context manager initialized")

    async def shutdown(self):
        """Shutdown context manager and cleanup"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Context manager shutdown")

    async def get_or_create_session(
        self, session_id: str, user_id: str, user_role: str = "viewer"
    ) -> SessionContext:
        """Get existing session or create new one"""
        async with self._lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.last_accessed = datetime.utcnow()
                return session

            # Create new session
            session = SessionContext(
                session_id=session_id, user_id=user_id, user_role=user_role
            )
            self.sessions[session_id] = session
            logger.info(f"Created new session: {session_id} for user: {user_id}")
            return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get session by ID"""
        async with self._lock:
            session = self.sessions.get(session_id)
            if session:
                session.last_accessed = datetime.utcnow()
            return session

    async def update_docker_context(
        self,
        session_id: str,
        container: Optional[str] = None,
        image: Optional[str] = None,
        **kwargs,
    ):
        """Update Docker-specific context"""
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return

        async with self._lock:
            if container is not None:
                session.docker_context["current_container"] = container
            if image is not None:
                session.docker_context["current_image"] = image

            # Update any additional context
            session.docker_context.update(kwargs)

        logger.debug(
            f"Updated Docker context for session {session_id}: {session.docker_context}"
        )

    async def update_pulumi_context(
        self,
        session_id: str,
        stack: Optional[str] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        **kwargs,
    ):
        """Update Pulumi-specific context"""
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return

        async with self._lock:
            if stack is not None:
                session.pulumi_context["current_stack"] = stack
            if organization is not None:
                session.pulumi_context["organization"] = organization
            if project is not None:
                session.pulumi_context["project"] = project

            # Update any additional context
            session.pulumi_context.update(kwargs)

        logger.debug(
            f"Updated Pulumi context for session {session_id}: {session.pulumi_context}"
        )

    async def update_claude_context(
        self,
        session_id: str,
        conversation_id: Optional[str] = None,
        last_model: Optional[str] = None,
        **kwargs,
    ):
        """Update Claude-specific context"""
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return

        async with self._lock:
            if conversation_id is not None:
                session.claude_context["conversation_id"] = conversation_id
            if last_model is not None:
                session.claude_context["last_model"] = last_model

            # Update any additional context
            session.claude_context.update(kwargs)

        logger.debug(
            f"Updated Claude context for session {session_id}: {session.claude_context}"
        )

    async def add_command_to_history(self, session_id: str, command: str):
        """Add command to session history"""
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return

        async with self._lock:
            session.command_history.append(command)
            # Keep only last 50 commands
            if len(session.command_history) > 50:
                session.command_history = session.command_history[-50:]

    async def get_full_context(self, session_id: str) -> Dict[str, Any]:
        """Get complete context for a session"""
        session = await self.get_session(session_id)
        if not session:
            return {}

        return {
            "user": {"id": session.user_id, "role": session.user_role},
            "session": {
                "id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat(),
            },
            "docker": session.docker_context,
            "pulumi": session.pulumi_context,
            "claude": session.claude_context,
            "project": session.current_project,
            "environment": session.current_environment,
            "recent_commands": session.command_history[-10:],  # Last 10 commands
        }

    async def clear_context(self, session_id: str, context_type: Optional[str] = None):
        """Clear specific context or all contexts for a session"""
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return

        async with self._lock:
            if context_type == "docker":
                session.docker_context.clear()
            elif context_type == "pulumi":
                session.pulumi_context.clear()
            elif context_type == "claude":
                session.claude_context.clear()
            elif context_type is None:
                # Clear all contexts
                session.docker_context.clear()
                session.pulumi_context.clear()
                session.claude_context.clear()
                session.command_history.clear()

        logger.info(f"Cleared {context_type or 'all'} context for session {session_id}")

    async def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session context for persistence"""
        session = await self.get_session(session_id)
        if not session:
            return None

        return session.to_dict()

    async def import_session(self, session_data: Dict[str, Any]) -> SessionContext:
        """Import session context from persistence"""
        session = SessionContext(
            session_id=session_data["session_id"],
            user_id=session_data["user_id"],
            user_role=session_data.get("user_role", "viewer"),
            created_at=datetime.fromisoformat(session_data["created_at"]),
            last_accessed=datetime.utcnow(),  # Update last accessed
            docker_context=session_data.get("docker_context", {}),
            pulumi_context=session_data.get("pulumi_context", {}),
            claude_context=session_data.get("claude_context", {}),
            current_project=session_data.get("current_project"),
            current_environment=session_data.get("current_environment", "development"),
            command_history=session_data.get("command_history", []),
        )

        async with self._lock:
            self.sessions[session.session_id] = session

        logger.info(f"Imported session: {session.session_id}")
        return session

    async def _cleanup_expired_sessions(self):
        """Background task to cleanup expired sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                current_time = datetime.utcnow()
                expired_sessions = []

                async with self._lock:
                    for session_id, session in self.sessions.items():
                        if current_time - session.last_accessed > self.ttl:
                            expired_sessions.append(session_id)

                    # Remove expired sessions
                    for session_id in expired_sessions:
                        del self.sessions[session_id]
                        logger.info(f"Removed expired session: {session_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)

    def get_sessions_by_user(self, user_id: str) -> List[SessionContext]:
        """Get all sessions for a specific user"""
        return [
            session for session in self.sessions.values() if session.user_id == user_id
        ]


# Global context manager instance
context_manager = ContextManager()
