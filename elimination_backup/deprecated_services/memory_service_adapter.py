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
            # Store conversation using UnifiedMemoryService's method
            messages = []
            messages.append({"role": "user", "content": user_message})
            if ai_response:
                messages.append({"role": "assistant", "content": ai_response})

            metadata = {
                "session_id": session_id,
                "type": "conversation",
            }

            # Use the correct method from UnifiedMemoryService
            await self.memory_service.add_conversation_memory(
                user_id=user_id,
                messages=messages,
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

            return True

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

                # Update in memory service as well
                user_id = last_conv["user_id"]
                user_message = last_conv["user_message"]

                messages = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": ai_response},
                ]

                await self.memory_service.add_conversation_memory(
                    user_id=user_id,
                    messages=messages,
                    metadata={
                        "session_id": session_id,
                        "type": "conversation",
                        "updated": True,
                    },
                )

            return True

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
            # Use the get_conversation_context method from UnifiedMemoryService
            return await self.memory_service.get_conversation_context(
                user_id=user_id,
                limit=limit,
            )
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []

    async def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Async passthrough to UnifiedMemoryService.search_knowledge"""
        return await self.memory_service.search_knowledge(
            query=query,
            limit=limit,
            metadata_filter=metadata_filter,
            user_id=user_id,
        )

    def health_check(self) -> dict[str, Any]:
        """Check health of memory service"""
        return {
            "status": (
                "healthy" if not self.memory_service.degraded_mode else "degraded"
            ),
            "degraded_mode": self.memory_service.degraded_mode,
            "redis_available": self.memory_service.redis_client is not None,
            "mem0_available": self.memory_service.mem0_client is not None,
            "qdrant_available": self.memory_service.qdrant_service is not None,
        }

    # Passthrough all other methods
    def __getattr__(self, name):
        """Pass through any other method calls to the underlying memory service"""
        return getattr(self.memory_service, name)
