"""
Modular Chat Services Package - Phase 2B Implementation
Decomposed chat service architecture with dependency injection
"""

from .base_chat_service import BaseChatService
from .sophia_chat_service import SophiaChatService
from .executive_chat_service import ExecutiveChatService
from .universal_chat_service import UniversalChatService
from .session_manager import SessionManager
from .context_manager import ContextManager
from .unified_chat_service import UnifiedChatService

# Provider imports
from .providers.base_provider import BaseProvider
from .providers.openai_provider import OpenAIProvider
from .providers.portkey_provider import PortkeyProvider

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

