"""
Memory Service Adapter for Sophia Unified Orchestrator

This adapter adds the missing conversation methods to UnifiedMemoryService
for compatibility with SophiaUnifiedOrchestrator.

Date: July 9, 2025
"""

import logging
from typing import Any, Optional

from backend.services.unified_memory_service import UnifiedMemoryService

logger = logging.getLogger(__name__)


class MemoryServiceAdapter:
    """Adapter to add conversation methods to UnifiedMemoryService"""

    def __init__(self, memory_service: UnifiedMemoryService):
        self.memory_service = memory_service
        self._conversations = {}  # In-memory storage for conversations

    async def add_conversation(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        ai_response: Optional[str] = None,
    ) -> bool:
        """Add a conversation to memory"""
        try:
            # Store in Mem0 if available
            metadata = {
                "session_id": session_id,
                "type": "conversation",
                "user_message": user_message,
                "ai_response": ai_response,
            }

            # Use the remember_conversation method from UnifiedMemoryService
            success = self.memory_service.remember_conversation(
                user_id=user_id,
                content=f"User: {user_message}\nAI: {ai_response or 'Pending...'}",
                metadata=metadata,
            )

            # Also store in local memory for session tracking
            if session_id not in self._conversations:
                self._conversations[session_id] = []

            self._conversations[session_id].append(
                {
                    "user_id": user_id,
                    "user_message": user_message,
                    "ai_response": ai_response,
                    "timestamp": self.memory_service.current_date.isoformat(),
                }
            )

            return success

        except Exception as e:
            logger.error(f"Failed to add conversation: {e}")
            return False

    async def update_conversation(
        self,
        session_id: str,
        ai_response: str,
    ) -> bool:
        """Update the last conversation with AI response"""
        try:
            # Update local memory
            if session_id in self._conversations and self._conversations[session_id]:
                last_conv = self._conversations[session_id][-1]
                last_conv["ai_response"] = ai_response

                # Update in Mem0 as well
                user_id = last_conv["user_id"]
                user_message = last_conv["user_message"]

                return self.memory_service.remember_conversation(
                    user_id=user_id,
                    content=f"User: {user_message}\nAI: {ai_response}",
                    metadata={
                        "session_id": session_id,
                        "type": "conversation",
                        "updated": True,
                    },
                )

            return False

        except Exception as e:
            logger.error(f"Failed to update conversation: {e}")
            return False

    async def search_conversations(
        self,
        user_id: str,
        query: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search conversations for a user"""
        try:
            # Use the recall_conversations method from UnifiedMemoryService
            return self.memory_service.recall_conversations(
                user_id=user_id,
                query=query,
                limit=limit,
            )
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []

    def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[dict[str, Any]] = None,
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Direct passthrough to UnifiedMemoryService.search_knowledge"""
        return self.memory_service.search_knowledge(
            query=query,
            limit=limit,
            metadata_filter=metadata_filter,
            threshold=threshold,
        )

    def health_check(self) -> dict[str, Any]:
        """Direct passthrough to UnifiedMemoryService.health_check"""
        return self.memory_service.health_check()

    # Passthrough all other methods
    def __getattr__(self, name):
        """Pass through any other method calls to the underlying memory service"""
        return getattr(self.memory_service, name)
