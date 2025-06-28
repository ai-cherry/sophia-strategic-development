"""
Deal Domain Entity

This module defines the Deal entity which represents a sales deal/opportunity
in the Sophia AI system.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class DealStage(Enum):
    """Enumeration of deal stages in the sales pipeline."""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


@dataclass
class Deal:
    """
    Domain entity representing a sales deal/opportunity.
    
    This entity encapsulates the core business logic and rules
    related to sales deals.
    """
    id: str
    external_id: str  # HubSpot ID or other CRM ID
    name: str
    company_name: str
    amount: Decimal
    stage: DealStage
    close_date: datetime
    probability: float  # 0.0 to 1.0
    owner_id: str
    created_at: datetime
    updated_at: datetime
    contacts: Optional[List[str]] = None  # List of contact IDs
    products: Optional[List[str]] = None  # List of product IDs
    competitor_mentioned: bool = False
    budget_confirmed: bool = False
    decision_maker_involved: bool = False
    
    def __post_init__(self):
        """Initialize default values and validate data."""
        if self.contacts is None:
            self.contacts = []
        if self.products is None:
            self.products = []
        
        # Validate probability
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(f"Probability must be between 0 and 1, got {self.probability}")
    
    def is_qualified(self) -> bool:
        """
        Business rule: Deal is qualified if budget is confirmed and
        decision maker is involved.
        
        Returns:
            bool: True if deal is properly qualified
        """
        return self.budget_confirmed and self.decision_maker_involved
    
    def is_at_risk(self) -> bool:
        """
        Business rule: Deal is at risk if close date is within 30 days
        and probability is less than 50%, or if competitor is mentioned.
        
        Returns:
            bool: True if deal is at risk
        """
        days_to_close = (self.close_date - datetime.now()).days
        return (
            self.competitor_mentioned or
            (days_to_close <= 30 and self.probability < 0.5)
        )
    
    def is_stalled(self) -> bool:
        """
        Business rule: Deal is stalled if it hasn't been updated in 14 days
        and is not in a closed stage.
        
        Returns:
            bool: True if deal is stalled
        """
        if self.stage in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]:
            return False
        
        days_since_update = (datetime.now() - self.updated_at).days
        return days_since_update > 14
    
    def get_weighted_value(self) -> Decimal:
        """
        Calculate the weighted value of the deal based on probability.
        
        Returns:
            Decimal: Weighted deal value
        """
        return self.amount * Decimal(str(self.probability))
    
    def get_health_score(self) -> float:
        """
        Calculate deal health score based on multiple factors.
        
        Business rule: Health score considers qualification, risk factors,
        and deal progression.
        
        Returns:
            float: Health score between 0 and 1
        """
        score = 0.0
        
        # Qualification component (30%)
        if self.is_qualified():
            score += 0.3
        
        # Risk component (30%)
        if not self.is_at_risk():
            score += 0.3
        elif not self.competitor_mentioned:
            score += 0.15  # Partial credit if only time-based risk
        
        # Progression component (20%)
        if not self.is_stalled():
            score += 0.2
        
        # Probability component (20%)
        score += self.probability * 0.2
        
        return score
    
    def needs_attention(self) -> bool:
        """
        Business rule: Deal needs attention if it's at risk, stalled,
        or has low health score.
        
        Returns:
            bool: True if deal needs immediate attention
        """
        return (
            self.is_at_risk() or
            self.is_stalled() or
            self.get_health_score() < 0.5
        )
    
    def can_progress_to_next_stage(self) -> bool:
        """
        Business rule: Check if deal can progress to the next stage
        based on current stage requirements.
        
        Returns:
            bool: True if deal meets requirements for next stage
        """
        if self.stage == DealStage.PROSPECTING:
            # Can move to qualification if we have contacts
            return len(self.contacts) > 0 if self.contacts else False
        
        elif self.stage == DealStage.QUALIFICATION:
            # Can move to proposal if qualified
            return self.is_qualified()
        
        elif self.stage == DealStage.PROPOSAL:
            # Can move to negotiation if products are defined
            return len(self.products) > 0 if self.products else False
        
        elif self.stage == DealStage.NEGOTIATION:
            # Can close if probability is high
            return self.probability >= 0.7
        
        # Closed deals cannot progress
        return False 