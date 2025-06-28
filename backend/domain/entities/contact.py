"""
Contact Domain Entity

This module defines the Contact entity which represents a business contact
in the Sophia AI system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ContactType(Enum):
    """Enumeration of contact types."""

    PROSPECT = "prospect"
    CUSTOMER = "customer"
    PARTNER = "partner"
    VENDOR = "vendor"
    OTHER = "other"


class EngagementLevel(Enum):
    """Enumeration of engagement levels."""

    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    CHAMPION = "champion"


@dataclass
class Contact:
    """
    Domain entity representing a business contact.

    This entity encapsulates the core business logic and rules
    related to contacts and their relationships.
    """

    id: str
    external_id: str  # HubSpot ID or other CRM ID
    email: str
    first_name: str
    last_name: str
    company: str
    title: str | None = None
    phone: str | None = None
    contact_type: ContactType = ContactType.PROSPECT
    engagement_level: EngagementLevel = EngagementLevel.COLD
    is_decision_maker: bool = False
    last_interaction_date: datetime | None = None
    interaction_count: int = 0
    deal_ids: list[str] | None = None
    tags: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """Initialize default values."""
        if self.deal_ids is None:
            self.deal_ids = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    @property
    def full_name(self) -> str:
        """Get the contact's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        """Get formatted display name with title and company."""
        parts = [self.full_name]
        if self.title:
            parts.append(self.title)
        if self.company:
            parts.append(f"at {self.company}")
        return " ".join(parts)

    def is_engaged(self) -> bool:
        """
        Business rule: Contact is engaged if they have warm or better
        engagement level.

        Returns:
            bool: True if contact is engaged
        """
        return self.engagement_level in [
            EngagementLevel.WARM,
            EngagementLevel.HOT,
            EngagementLevel.CHAMPION,
        ]

    def needs_nurturing(self) -> bool:
        """
        Business rule: Contact needs nurturing if they haven't been
        contacted in 30 days and are not hot/champion.

        Returns:
            bool: True if contact needs nurturing
        """
        if self.engagement_level in [EngagementLevel.HOT, EngagementLevel.CHAMPION]:
            return False

        if not self.last_interaction_date:
            return True

        days_since_interaction = (datetime.now() - self.last_interaction_date).days
        return days_since_interaction > 30

    def is_qualified_lead(self) -> bool:
        """
        Business rule: Contact is qualified if they are a decision maker
        with warm or better engagement.

        Returns:
            bool: True if contact is a qualified lead
        """
        return self.is_decision_maker and self.is_engaged()

    def calculate_priority_score(self) -> float:
        """
        Calculate priority score based on multiple factors.

        Business rule: Priority considers engagement level, decision maker
        status, interaction recency, and deal involvement.

        Returns:
            float: Priority score between 0 and 1
        """
        score = 0.0

        # Engagement level component (40%)
        engagement_scores = {
            EngagementLevel.COLD: 0.0,
            EngagementLevel.WARM: 0.5,
            EngagementLevel.HOT: 0.8,
            EngagementLevel.CHAMPION: 1.0,
        }
        score += engagement_scores.get(self.engagement_level, 0.0) * 0.4

        # Decision maker component (30%)
        if self.is_decision_maker:
            score += 0.3

        # Interaction recency component (20%)
        if self.last_interaction_date:
            days_since = (datetime.now() - self.last_interaction_date).days
            if days_since <= 7:
                score += 0.2
            elif days_since <= 30:
                score += 0.1
            elif days_since <= 60:
                score += 0.05

        # Deal involvement component (10%)
        if self.deal_ids:
            score += min(len(self.deal_ids) * 0.05, 0.1)

        return score

    def update_engagement_level(self, new_level: EngagementLevel) -> None:
        """
        Update engagement level with business rules.

        Args:
            new_level: The new engagement level
        """
        # Business rule: Can't downgrade from champion to cold directly
        if (
            self.engagement_level == EngagementLevel.CHAMPION
            and new_level == EngagementLevel.COLD
        ):
            self.engagement_level = EngagementLevel.WARM
        else:
            self.engagement_level = new_level

        self.updated_at = datetime.now()

    def record_interaction(self) -> None:
        """Record a new interaction with the contact."""
        self.last_interaction_date = datetime.now()
        self.interaction_count += 1
        self.updated_at = datetime.now()

        # Business rule: Auto-upgrade cold contacts after 3 interactions
        if (
            self.engagement_level == EngagementLevel.COLD
            and self.interaction_count >= 3
        ):
            self.engagement_level = EngagementLevel.WARM
