"""
Call Participant Value Object

This module defines the CallParticipant value object which represents
a participant in a sales call.
"""

from dataclasses import dataclass
from enum import Enum


class ParticipantRole(Enum):
    """Enumeration of participant roles in a call."""
    SALES_REP = "sales_rep"
    CUSTOMER = "customer"
    MANAGER = "manager"
    TECHNICAL_EXPERT = "technical_expert"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CallParticipant:
    """
    Value object representing a participant in a call.
    
    This is an immutable object that encapsulates participant
    information and their role in the call.
    """
    id: str
    name: str
    email: str
    role: ParticipantRole
    is_decision_maker: bool = False
    company: str = ""
    title: str = ""
    
    def is_internal(self) -> bool:
        """
        Check if participant is internal (from the sales organization).
        
        Returns:
            bool: True if participant is a sales rep or manager
        """
        return self.role in [ParticipantRole.SALES_REP, ParticipantRole.MANAGER]
    
    def is_customer(self) -> bool:
        """
        Check if participant is a customer.
        
        Returns:
            bool: True if participant is a customer
        """
        return self.role == ParticipantRole.CUSTOMER
    
    def get_display_name(self) -> str:
        """
        Get formatted display name with title if available.
        
        Returns:
            str: Formatted name with title
        """
        if self.title:
            return f"{self.name} ({self.title})"
        return self.name
    
    def get_identifier(self) -> str:
        """
        Get a unique identifier string for the participant.
        
        Returns:
            str: Unique identifier combining email and role
        """
        return f"{self.email}:{self.role.value}" 