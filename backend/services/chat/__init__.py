"""
Modular Chat Services Package - Phase 2B Implementation
Decomposed chat service architecture with dependency injection
"""

from .base_chat_service import BaseChatService
from .context_manager import ContextManager
from .executive_chat_service import ExecutiveChatService

# Provider imports
from .providers.base_provider import BaseProvider
from .providers.openai_provider import OpenAIProvider
from .providers.portkey_provider import PortkeyProvider
from .session_manager import SessionManager
from .sophia_chat_service import SophiaChatService
from .unified_chat_service import UnifiedChatService
from .universal_chat_service import UniversalChatService

__all__ = [
    # Core Services
    "BaseChatService",
    "SophiaChatService",
    "ExecutiveChatService",
    "UniversalChatService",
    "UnifiedChatService",

    # Managers
    "SessionManager",
    "ContextManager",

    # Providers
    "BaseProvider",
    "OpenAIProvider",
    "PortkeyProvider"
]

