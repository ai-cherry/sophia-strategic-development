"""
Mem0 Integration Service for Sophia AI
Provides persistent cross-session memory with learning capabilities
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

import httpx

from core.config_manager import get_config_value

logger = logging.getLogger(__name__)


class Mem0IntegrationService:
    """
    Integration service for Mem0 persistent memory
    Enables cross-session learning and RLHF capabilities
    """

    def __init__(self):
        self.mem0_url = get_config_value(
            "mem0_url", "http://mem0-server.sophia-memory:8080"
        )
        self.api_key = get_config_value("mem0_api_key", "")
        self.client = httpx.AsyncClient(
            base_url=self.mem0_url,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            timeout=30.0,
        )
        self.initialized = False

    async def initialize(self):
        """Initialize connection to Mem0 server"""
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                self.initialized = True
                logger.info("✅ Mem0 integration initialized successfully")
            else:
                logger.error(f"❌ Mem0 health check failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Mem0: {e}")
            self.initialized = False

    async def store_conversation_memory(
        self,
        user_id: str,
        conversation: list[dict[str, str]],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Store conversation with learning metadata

        Args:
            user_id: Unique user identifier
            conversation: List of message dictionaries with 'role' and 'content'
            metadata: Additional metadata for the memory

        Returns:
            Memory ID for future reference
        """
        if not self.initialized:
            await self.initialize()

        memory_id = str(uuid4())

        try:
            payload = {
                "memory_id": memory_id,
                "user_id": user_id,
                "messages": conversation,
                "metadata": {
                    "source": "sophia_ai",
                    "timestamp": datetime.now().isoformat(),
                    "session_id": metadata.get("session_id") if metadata else None,
                    "category": metadata.get("category", "conversation")
                    if metadata
                    else "conversation",
                    **(metadata or {}),
                },
            }

            response = await self.client.post("/memories", json=payload)

            if response.status_code == 201:
                logger.info(f"✅ Stored conversation memory: {memory_id}")
                return memory_id
            else:
                logger.error(f"Failed to store memory: {response.text}")
                return ""

        except Exception as e:
            logger.error(f"Error storing conversation memory: {e}")
            return ""

    async def recall_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Recall relevant memories for a user based on query

        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum number of memories to return
            filters: Additional filters for memory search

        Returns:
            List of relevant memories
        """
        if not self.initialized:
            await self.initialize()

        try:
            params = {
                "user_id": user_id,
                "query": query,
                "limit": limit,
                **(filters or {}),
            }

            response = await self.client.get("/memories/search", params=params)

            if response.status_code == 200:
                memories = response.json().get("memories", [])
                logger.info(f"✅ Recalled {len(memories)} memories for user {user_id}")
                return memories
            else:
                logger.error(f"Failed to recall memories: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error recalling memories: {e}")
            return []

    async def update_memory_with_feedback(
        self,
        memory_id: str,
        feedback_type: str,
        feedback_score: float,
        feedback_text: str | None = None,
    ) -> bool:
        """
        Update memory with RLHF feedback

        Args:
            memory_id: Memory to update
            feedback_type: Type of feedback (positive, negative, correction)
            feedback_score: Numerical feedback score
            feedback_text: Optional textual feedback

        Returns:
            Success status
        """
        try:
            payload = {
                "feedback_type": feedback_type,
                "feedback_score": feedback_score,
                "feedback_text": feedback_text,
                "timestamp": datetime.now().isoformat(),
            }

            response = await self.client.patch(
                f"/memories/{memory_id}/feedback", json=payload
            )

            if response.status_code == 200:
                logger.info(f"✅ Updated memory {memory_id} with feedback")
                return True
            else:
                logger.error(f"Failed to update memory feedback: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error updating memory feedback: {e}")
            return False

    async def get_user_profile(self, user_id: str) -> dict[str, Any]:
        """
        Get aggregated user profile from memories

        Args:
            user_id: User identifier

        Returns:
            User profile with preferences and patterns
        """
        try:
            response = await self.client.get(f"/users/{user_id}/profile")

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user profile: {response.text}")
                return {}

        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {}

    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a specific memory

        Args:
            memory_id: Memory to delete

        Returns:
            Success status
        """
        try:
            response = await self.client.delete(f"/memories/{memory_id}")

            if response.status_code == 204:
                logger.info(f"✅ Deleted memory {memory_id}")
                return True
            else:
                logger.error(f"Failed to delete memory: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False

    async def get_learning_analytics(
        self,
        user_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get learning analytics for memories

        Args:
            user_id: Optional user filter
            start_date: Start date for analytics
            end_date: End date for analytics

        Returns:
            Learning analytics data
        """
        try:
            params = {}
            if user_id:
                params["user_id"] = user_id
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()

            response = await self.client.get("/analytics/learning", params=params)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get learning analytics: {response.text}")
                return {}

        except Exception as e:
            logger.error(f"Error getting learning analytics: {e}")
            return {}

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global instance
_mem0_service: Mem0IntegrationService | None = None


def get_mem0_service() -> Mem0IntegrationService:
    """Get or create the global Mem0 service instance"""
    global _mem0_service
    if _mem0_service is None:
        _mem0_service = Mem0IntegrationService()
    return _mem0_service
