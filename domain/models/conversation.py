# File: backend/models/conversation.py

"""
Conversation models for Sophia AI platform.
This module provides conversation-related data models for cross-platform integration.
"""

# Import the IntegratedConversationRecord from enhanced data models
from backend.agents.enhanced.data_models import (
    GongCallData,
    IntegratedConversationRecord,
    SlackMessageData,
)

# Re-export for backward compatibility
__all__ = [
    "IntegratedConversationRecord",
    "GongCallData",
    "SlackMessageData",
]
