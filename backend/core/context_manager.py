"""Simplified context manager used for unit tests."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class SessionContext:
    """Minimal session context structure."""

    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """Thread-safe manager for :class:`SessionContext` objects."""

    def __init__(self, ttl_minutes: int = 60) -> None:
        self.sessions: Dict[str, SessionContext] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:  # pragma: no cover - trivial
        logger.info("Context manager initialized")

    async def shutdown(self) -> None:  # pragma: no cover - trivial
        logger.info("Context manager shutdown")

    async def get_or_create_session(self, session_id: str, user_id: str) -> SessionContext:
        async with self._lock:
            session = self.sessions.get(session_id)
            if session is None:
                session = SessionContext(session_id=session_id, user_id=user_id)
                self.sessions[session_id] = session
            session.last_accessed = datetime.utcnow()
            return session

    async def get_active_sessions_count(self) -> int:
        return len(self.sessions)


context_manager = ContextManager()
