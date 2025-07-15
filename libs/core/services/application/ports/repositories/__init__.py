"""
Repository Interfaces

This module contains abstract repository interfaces that define
data persistence contracts.
"""

from .call_repository import CallRepository
from .contact_repository import ContactRepository
from .deal_repository import DealRepository

__all__ = ["CallRepository", "ContactRepository", "DealRepository"]
