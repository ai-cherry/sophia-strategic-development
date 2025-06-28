"""
Domain Entities

This module contains the core business entities of the Sophia AI system.
"""

from .call import Call
from .deal import Deal, DealStage
from .contact import Contact, ContactType, EngagementLevel
from .user import User, UserRole, PermissionLevel

__all__ = [
    'Call',
    'Deal', 'DealStage',
    'Contact', 'ContactType', 'EngagementLevel',
    'User', 'UserRole', 'PermissionLevel'
]
