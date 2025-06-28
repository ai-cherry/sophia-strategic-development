"""
Temporary compatibility layer for EnhancedUnifiedChatService
This fixes the import error that's preventing MCP servers from starting
"""

# Import the actual working service
from .sophia_universal_chat_service import SophiaUniversalChatService

# Create compatibility aliases
EnhancedUnifiedChatService = SophiaUniversalChatService

# For compatibility with existing imports
class QueryContext:
    def __init__(self, query: str, context: dict = None):
        self.query = query
        self.context = context or {}


# Dummy snowflake_service for development
snowflake_service = None
