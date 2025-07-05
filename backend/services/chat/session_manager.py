from datetime import UTC, datetime

"""
Session Manager - Phase 2B Implementation
Manages chat session state and persistence
"""

import asyncio
import contextlib
import logging
from datetime import timedelta

from ...models.chat_models import ChatConfiguration, ChatContext, ChatMode, ChatSession

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages chat session lifecycle and state
    Handles session creation, updates, and cleanup
    """

    def __init__(self, session_timeout_minutes: int = 60):
        self.session_timeout_minutes = session_timeout_minutes
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # In-memory session storage (replace with Redis/database in production)
        self._sessions: dict[str, ChatSession] = {}
        self._cleanup_task = None

        # Start cleanup task
        self._start_cleanup_task()

        self.logger.info(
            f"Session manager initialized with {session_timeout_minutes}min timeout"
        )

    def _start_cleanup_task(self):
        """Start background task to clean up expired sessions"""

        async def cleanup_expired_sessions():
            while True:
                try:
                    await self._cleanup_expired_sessions()
                    await asyncio.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    self.logger.error(f"Session cleanup error: {str(e)}")
                    await asyncio.sleep(60)  # Retry after 1 minute on error

        self._cleanup_task = asyncio.create_task(cleanup_expired_sessions())

    async def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        cutoff_time = datetime.now(UTC) - timedelta(
            minutes=self.session_timeout_minutes
        )
        expired_sessions = [
            session_id
            for session_id, session in self._sessions.items()
            if session.last_activity < cutoff_time
        ]

        for session_id in expired_sessions:
            del self._sessions[session_id]
            self.logger.debug(f"Cleaned up expired session: {session_id}")

        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    async def get_or_create_session(
        self,
        session_id: str,
        mode: ChatMode,
        context: ChatContext | None = None,
        configuration: ChatConfiguration | None = None,
    ) -> ChatSession:
        """Get existing session or create a new one"""

        # Check if session exists and is valid
        if session_id in self._sessions:
            session = self._sessions[session_id]

            # Update last activity
            session.last_activity = datetime.now(UTC)

            # Update mode if different (allows mode switching within session)
            if session.mode != mode:
                self.logger.info(
                    f"Session {session_id} mode changed: {session.mode.value} -> {mode.value}"
                )
                session.mode = mode

            return session

        # Create new session
        session = ChatSession(
            session_id=session_id,
            mode=mode,
            created_at=datetime.now(UTC),
            last_activity=datetime.now(UTC),
            context=context,
            configuration=configuration,
        )

        self._sessions[session_id] = session
        self.logger.info(f"Created new session: {session_id} (mode: {mode.value})")

        return session

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Get session by ID"""
        session = self._sessions.get(session_id)

        if session:
            # Check if session is expired
            cutoff_time = datetime.now(UTC) - timedelta(
                minutes=self.session_timeout_minutes
            )
            if session.last_activity < cutoff_time:
                await self.delete_session(session_id)
                return None

            # Update last activity
            session.last_activity = datetime.now(UTC)

        return session

    async def update_session_activity(
        self, session_id: str, tokens_used: int = 0, cost: float = 0.0
    ) -> bool:
        """Update session activity and usage metrics"""
        session = self._sessions.get(session_id)

        if not session:
            self.logger.warning(
                f"Attempted to update non-existent session: {session_id}"
            )
            return False

        # Update activity and metrics
        session.last_activity = datetime.now(UTC)
        session.message_count += 1
        session.total_tokens += tokens_used
        session.total_cost += cost

        self.logger.debug(
            f"Updated session {session_id}: +{tokens_used} tokens, +${cost:.4f}"
        )
        return True

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            self.logger.info(f"Deleted session: {session_id}")
            return True

        return False

    async def list_sessions(
        self,
        limit: int = 10,
        offset: int = 0,
        mode_filter: ChatMode | None = None,
        active_only: bool = True,
    ) -> list[ChatSession]:
        """List sessions with optional filtering"""
        sessions = list(self._sessions.values())

        # Filter by mode if specified
        if mode_filter:
            sessions = [s for s in sessions if s.mode == mode_filter]

        # Filter active sessions only
        if active_only:
            cutoff_time = datetime.now(UTC) - timedelta(
                minutes=self.session_timeout_minutes
            )
            sessions = [s for s in sessions if s.last_activity >= cutoff_time]

        # Sort by last activity (most recent first)
        sessions.sort(key=lambda s: s.last_activity, reverse=True)

        # Apply pagination
        return sessions[offset : offset + limit]

    async def get_session_count(self, mode_filter: ChatMode | None = None) -> int:
        """Get total number of sessions"""
        sessions = self._sessions.values()

        if mode_filter:
            sessions = [s for s in sessions if s.mode == mode_filter]

        return len(list(sessions))

    async def get_session_metrics(self) -> dict[str, any]:
        """Get session metrics and statistics"""
        sessions = list(self._sessions.values())

        if not sessions:
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "mode_distribution": {},
                "total_messages": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
            }

        # Calculate metrics
        cutoff_time = datetime.now(UTC) - timedelta(
            minutes=self.session_timeout_minutes
        )
        active_sessions = [s for s in sessions if s.last_activity >= cutoff_time]

        mode_distribution = {}
        for session in sessions:
            mode = session.mode.value
            mode_distribution[mode] = mode_distribution.get(mode, 0) + 1

        total_messages = sum(s.message_count for s in sessions)
        total_tokens = sum(s.total_tokens for s in sessions)
        total_cost = sum(s.total_cost for s in sessions)

        return {
            "total_sessions": len(sessions),
            "active_sessions": len(active_sessions),
            "mode_distribution": mode_distribution,
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "average_messages_per_session": (
                round(total_messages / len(sessions), 2) if sessions else 0
            ),
            "average_cost_per_session": (
                round(total_cost / len(sessions), 4) if sessions else 0
            ),
        }

    async def cleanup_all_sessions(self):
        """Remove all sessions (for testing/maintenance)"""
        session_count = len(self._sessions)
        self._sessions.clear()
        self.logger.info(f"Cleaned up all {session_count} sessions")

    async def close(self):
        """Close session manager and cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

        self.logger.info("Session manager closed")

    def __len__(self) -> int:
        """Get number of active sessions"""
        return len(self._sessions)

    def __contains__(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self._sessions
