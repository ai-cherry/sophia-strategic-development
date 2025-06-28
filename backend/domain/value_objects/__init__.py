"""
Domain Value Objects

This module contains immutable value objects used in the domain layer.
"""

from .sentiment import Sentiment
from .call_participant import CallParticipant, ParticipantRole
from .money import Money, Currency

__all__ = [
    'Sentiment',
    'CallParticipant', 'ParticipantRole',
    'Money', 'Currency'
]
