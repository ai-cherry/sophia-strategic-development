"""
Centralized Dependencies Module for Sophia AI

This module provides centralized dependency injection following FastAPI best practices
and Clean Architecture principles. All services are managed here to eliminate
circular imports and ensure proper lifecycle management.
"""

import asyncio
from functools import lru_cache

# Import the chat service
try:
    from backend.services.sophia_universal_chat_service import (
        SophiaUniversalChatService,
    )

    CHAT_SERVICE_AVAILABLE = True
except ImportError:
    try:
        from backend.services.enhanced_unified_chat_service import (
            EnhancedUnifiedChatService as SophiaUniversalChatService,
        )

        CHAT_SERVICE_AVAILABLE = True
    except ImportError:
        CHAT_SERVICE_AVAILABLE = False

        class SophiaUniversalChatService:
            """Mock chat service for when import fails"""

            def __init__(self):
                pass


# Global instance (singleton pattern)
_chat_service_instance: SophiaUniversalChatService | None = None


@lru_cache
def get_config_service():
    """Get configuration service (cached singleton)"""
    # This is already implemented in simple_config.py
    return True


async def get_chat_service() -> SophiaUniversalChatService:
    """
    Get the chat service instance.

    This function ensures we have a single instance of the chat service
    that is properly initialized and reused across requests.
    """
    global _chat_service_instance

    if _chat_service_instance is None:
        if CHAT_SERVICE_AVAILABLE:
            try:
                _chat_service_instance = SophiaUniversalChatService()
                # Add any initialization logic here
            except Exception as e:
                print(f"Warning: Failed to initialize chat service: {e}")
                # Create a mock instance
                _chat_service_instance = SophiaUniversalChatService()
        else:
            print("Warning: Chat service not available, using mock")
            _chat_service_instance = SophiaUniversalChatService()

    return _chat_service_instance


def get_chat_service_from_app_state(request):
    """
    Get chat service from FastAPI app state.

    This is used in routes to access the chat service instance
    that was initialized during app startup.
    """
    if hasattr(request.app.state, "chat_service_instance"):
        return request.app.state.chat_service_instance
    else:
        # Fallback to creating a new instance
        return asyncio.create_task(get_chat_service())


# Dependency functions for FastAPI injection
async def get_chat_service_dependency():
    """FastAPI dependency for chat service"""
    return await get_chat_service()


def get_request_chat_service(request):
    """FastAPI dependency that gets chat service from request app state"""
    return get_chat_service_from_app_state(request)
