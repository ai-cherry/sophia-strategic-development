"""Contextual memory utilities for Sophia AI."""

from __future__ import annotations

from .comprehensive_memory_manager import ComprehensiveMemoryManager


class ContextualMemoryIntelligence:
    """
Provide higher-level memory operations."""

    def __init__(self, memory_manager: ComprehensiveMemoryManager) -> None:
        self._memory = memory_manager

    async def last_message(self, user: str) -> str | None:
        """
Return the last message from the user's history."""

        history = await self._memory.history(user)
        return history[-1] if history else None
