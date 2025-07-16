"""In-memory conversation history manager for Sophia AI."""

from __future__ import annotations

from collections import defaultdict

class ComprehensiveMemoryManager:
    """
    Manage conversation history per user."""

    def __init__(self) -> None:
        self._memory: defaultdict[str, list[str]] = defaultdict(list)

    async def append(self, user: str, message: str) -> None:
        """
        Append a message to a user's history."""

        self._memory[user].append(message)

    async def history(self, user: str) -> list[str]:
        """
        Return the conversation history for a user."""

        return list(self._memory[user])
