from datetime import UTC, datetime

"""
Unified Chat Service - Phase 2B Implementation
Main orchestrator for all chat modes with dependency injection
"""

import logging
from typing import Any

from ...models.chat_models import (
    ChatMode,
    ChatRequest,
    ChatResponse,
    ChatSession,
)
from .base_chat_service import BaseChatService
from .context_manager import ContextManager
from .executive_chat_service import ExecutiveChatService
from .session_manager import SessionManager
from .sophia_chat_service import SophiaChatService
from .universal_chat_service import UnifiedChatService

logger = logging.getLogger(__name__)


class UnifiedChatService:
    """
    Unified chat service that orchestrates all chat modes
    Provides dependency injection and service coordination
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Initialize managers
        self.session_manager = SessionManager()
        self.context_manager = ContextManager()

        # Initialize chat services
        self._services: dict[ChatMode, BaseChatService] = {}
        self._initialize_services()

        self.logger.info("Unified chat service initialized with all modes")

    def _initialize_services(self):
        """Initialize all chat service implementations"""
        try:
            self._services[ChatMode.UNIVERSAL] = UnifiedChatService()
            self._services[ChatMode.SOPHIA] = SophiaChatService()
            self._services[ChatMode.EXECUTIVE] = ExecutiveChatService()

            self.logger.info(f"Initialized {len(self._services)} chat services")
        except Exception as e:
            self.logger.error(f"Failed to initialize chat services: {str(e)}")
            raise

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request using the appropriate service
        Main entry point for all chat processing
        """
        try:
            # Get or create session
            await self.session_manager.get_or_create_session(
                session_id=request.session_id, mode=request.mode
            )

            # Update context if provided
            if request.context:
                await self.context_manager.update_context(
                    session_id=request.session_id, context=request.context
                )

            # Get the appropriate service
            service = self._get_service(request.mode)

            # Process the chat
            response = await service.process_with_timing(request)

            # Update session with response
            await self.session_manager.update_session_activity(
                session_id=request.session_id,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                cost=response.usage.estimated_cost if response.usage else 0.0,
            )

            self.logger.info(
                f"Chat processed successfully: mode={request.mode.value}, session={request.session_id}"
            )
            return response

        except Exception as e:
            self.logger.error(f"Unified chat processing failed: {str(e)}")
            raise

    def _get_service(self, mode: ChatMode) -> BaseChatService:
        """Get the appropriate chat service for the given mode"""
        service = self._services.get(mode)
        if not service:
            raise ValueError(f"Unsupported chat mode: {mode.value}")
        return service

    async def get_session_info(self, session_id: str) -> ChatSession | None:
        """Get session information"""
        return await self.session_manager.get_session(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        return await self.session_manager.delete_session(session_id)

    async def list_sessions(self, limit: int = 10, offset: int = 0) -> list:
        """List chat sessions"""
        return await self.session_manager.list_sessions(limit=limit, offset=offset)

    def get_supported_modes(self) -> list:
        """Get list of supported chat modes"""
        return [mode.value for mode in self._services]

    def get_service_capabilities(self, mode: ChatMode) -> list:
        """Get capabilities for a specific chat mode"""
        service = self._services.get(mode)
        return service.get_capabilities() if service else []

    def get_health_status(self) -> dict[str, Any]:
        """Get health status of all services"""
        status = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "services": {},
            "total_services": len(self._services),
        }

        for mode, service in self._services.items():
            status["services"][mode.value] = {
                "status": "healthy",
                "capabilities": service.get_capabilities(),
                "supports_streaming": service.supports_streaming(),
            }

        return status

    async def get_analytics(self, session_id: str | None = None) -> dict[str, Any]:
        """Get chat analytics"""
        # Mock implementation - replace with actual analytics
        return {
            "total_sessions": 150,
            "total_messages": 1250,
            "mode_distribution": {"universal": 45, "sophia": 75, "executive": 30},
            "average_session_length": 8.5,
            "total_tokens": 125000,
            "total_cost": 15.75,
        }

    def register_service(self, mode: ChatMode, service: BaseChatService):
        """Register a new chat service (for extensibility)"""
        self._services[mode] = service
        self.logger.info(f"Registered new service for mode: {mode.value}")

    def unregister_service(self, mode: ChatMode):
        """Unregister a chat service"""
        if mode in self._services:
            del self._services[mode]
            self.logger.info(f"Unregistered service for mode: {mode.value}")

    async def shutdown(self):
        """Gracefully shutdown all services"""
        self.logger.info("Shutting down unified chat service...")

        # Close session manager
        await self.session_manager.close()

        # Close context manager
        await self.context_manager.close()

        self.logger.info("Unified chat service shutdown complete")
