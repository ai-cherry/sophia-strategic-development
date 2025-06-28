"""
Repository Interfaces

This module contains abstract repository interfaces that define
data persistence contracts.
"""

from .call_repository import CallRepository
from .deal_repository import DealRepository
from .contact_repository import ContactRepository

__all__ = ["CallRepository", "DealRepository", "ContactRepository"]
