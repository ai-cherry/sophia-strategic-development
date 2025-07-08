"""
Memory Client for MCP Servers
Provides easy interface to store and retrieve memories from AI Memory V2
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    CHAT = "chat"
    EVENT = "event"
    INSIGHT = "insight"
    CONTEXT = "context"
    DECISION = "decision"


class MemoryClient:
    """
    Async client for AI Memory V2 operations
    Used by all MCP servers to store and retrieve memories
    """

    def __init__(self, base_url: str = "http://146.235.200.1:9000"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession | None = None
        self._retry_count = 3
        self._timeout = aiohttp.ClientTimeout(total=30)

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def initialize(self):
        """Initialize the client session"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self._timeout)

    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def store_memory(
        self,
        memory_type: MemoryType,
        content: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        ttl_seconds: int | None = None,
        user_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Store a memory in the system

        Args:
            memory_type: Type of memory (chat, event, insight, etc.)
            content: The actual memory content
            metadata: Additional metadata
            ttl_seconds: Time to live in seconds
            user_context: User context for RBAC

        Returns:
            Dict with memory ID and status
        """
        if not self.session:
            await self.initialize()

        payload = {
            "type": memory_type,
            "content": content,
            "metadata": metadata or {},
            "ttl_seconds": ttl_seconds,
        }

        headers = {}
        if user_context:
            headers["X-User-Context"] = str(user_context)

        for attempt in range(self._retry_count):
            try:
                async with self.session.post(
                    f"{self.base_url}/api/v2/memory/store",
                    json=payload,
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 403:
                        raise PermissionError(
                            "Insufficient permissions to store memory"
                        )
                    else:
                        error = await response.text()
                        logger.error(f"Failed to store memory: {error}")

            except TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt == self._retry_count - 1:
                    raise
                await asyncio.sleep(2**attempt)
            except Exception as e:
                logger.error(f"Error storing memory: {e}")
                if attempt == self._retry_count - 1:
                    raise
                await asyncio.sleep(2**attempt)

        return {"status": "failed", "error": "Max retries exceeded"}

    async def retrieve_memory(
        self, memory_id: str, memory_type: MemoryType | None = None
    ) -> dict[str, Any] | None:
        """
        Retrieve a specific memory by ID

        Args:
            memory_id: The memory ID
            memory_type: Optional memory type for faster lookup

        Returns:
            Memory dict or None if not found
        """
        if not self.session:
            await self.initialize()

        params = {"memory_id": memory_id}
        if memory_type:
            params["memory_type"] = memory_type

        try:
            async with self.session.get(
                f"{self.base_url}/api/v2/memory/retrieve", params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error = await response.text()
                    logger.error(f"Failed to retrieve memory: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return None

    async def search_memories(
        self,
        query: str = "",
        memory_types: list[MemoryType] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search for memories

        Args:
            query: Search query (for future semantic search)
            memory_types: Filter by memory types
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum results

        Returns:
            List of matching memories
        """
        if not self.session:
            await self.initialize()

        params = {"query": query, "limit": limit}

        if memory_types:
            params["memory_types"] = ",".join(memory_types)

        if start_time:
            params["start_time"] = start_time.isoformat()

        if end_time:
            params["end_time"] = end_time.isoformat()

        try:
            async with self.session.get(
                f"{self.base_url}/api/v2/memory/search", params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Failed to search memories: {error}")
                    return []

        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []

    async def update_memory(
        self,
        memory_id: str,
        updates: dict[str, Any],
        user_context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update an existing memory

        Args:
            memory_id: The memory ID to update
            updates: Fields to update
            user_context: User context for RBAC

        Returns:
            True if successful
        """
        if not self.session:
            await self.initialize()

        headers = {}
        if user_context:
            headers["X-User-Context"] = str(user_context)

        try:
            async with self.session.patch(
                f"{self.base_url}/api/v2/memory/{memory_id}",
                json=updates,
                headers=headers,
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            return False

    async def delete_memory(
        self, memory_id: str, user_context: dict[str, Any] | None = None
    ) -> bool:
        """
        Delete a memory

        Args:
            memory_id: The memory ID to delete
            user_context: User context for RBAC

        Returns:
            True if successful
        """
        if not self.session:
            await self.initialize()

        headers = {}
        if user_context:
            headers["X-User-Context"] = str(user_context)

        try:
            async with self.session.delete(
                f"{self.base_url}/api/v2/memory/{memory_id}", headers=headers
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False

    async def get_stats(self) -> dict[str, Any]:
        """Get memory system statistics"""
        if not self.session:
            await self.initialize()

        try:
            async with self.session.get(
                f"{self.base_url}/api/v2/memory/stats"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Convenience functions for quick operations
async def store_event(
    source: str, event_type: str, content: dict[str, Any], severity: str = "info"
):
    """Quick function to store an event memory"""
    async with MemoryClient() as client:
        return await client.store_memory(
            MemoryType.EVENT,
            content={
                "source": source,
                "event_type": event_type,
                "severity": severity,
                **content,
            },
        )


async def store_insight(
    category: str,
    insight: str,
    confidence: float = 0.8,
    recommendations: list[str] = None,
):
    """Quick function to store a business insight"""
    async with MemoryClient() as client:
        return await client.store_memory(
            MemoryType.INSIGHT,
            content={
                "category": category,
                "insight": insight,
                "confidence": confidence,
                "recommendations": recommendations or [],
            },
        )


async def store_chat(
    user_id: str, session_id: str, message: str, response: str, topics: list[str] = None
):
    """Quick function to store a chat memory"""
    async with MemoryClient() as client:
        return await client.store_memory(
            MemoryType.CHAT,
            content={
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "response": response,
                "topics": topics or [],
            },
        )
