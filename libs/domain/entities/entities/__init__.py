"""
Domain Entities

This module contains the core business entities of the Sophia AI system.
"""

from .call import Call
from .contact import Contact, ContactType, EngagementLevel
from .deal import Deal, DealStage
from .user import PermissionLevel, User, UserRole

__all__ = [
    "Call",
    "Contact",
    "ContactType",
    "Deal",
    "DealStage",
    "EngagementLevel",
    "PermissionLevel",
    "User",
    "UserRole",
]
