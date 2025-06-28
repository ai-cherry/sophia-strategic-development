"""
Call Domain Entity

This module defines the Call entity which represents a sales call in the
Sophia AI system. It encapsulates business rules related to calls.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from backend.domain.value_objects.sentiment import Sentiment
from backend.domain.value_objects.call_participant import CallParticipant


@dataclass
class Call:
    """
    Domain entity representing a sales call.
    
    This entity encapsulates the core business logic and rules
    related to sales calls.
    """
    id: str
    external_id: str  # Gong ID or other external system ID
    title: str
    scheduled_at: datetime
    duration_seconds: int
    participants: List[CallParticipant]
    transcript: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    talk_ratio: Optional[float] = None  # Ratio of customer vs sales rep talking
    next_steps: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.next_steps is None:
            self.next_steps = []
        if self.topics is None:
            self.topics = []
    
    def is_high_value(self) -> bool:
        """
        Business rule: Calls > 30 min with decision makers are high value.
        
        Returns:
            bool: True if the call is considered high value
        """
        has_decision_maker = any(p.is_decision_maker for p in self.participants)
        return self.duration_seconds > 1800 and has_decision_maker
    
    def requires_followup(self) -> bool:
        """
        Business rule: Negative sentiment calls need immediate followup.
        
        Returns:
            bool: True if the call requires immediate followup
        """
        return bool(self.sentiment and self.sentiment.is_negative())
    
    def has_clear_next_steps(self) -> bool:
        """
        Business rule: Successful calls have clear next steps defined.
        
        Returns:
            bool: True if next steps are clearly defined
        """
        return len(self.next_steps) > 0 if self.next_steps else False
    
    def get_engagement_score(self) -> float:
        """
        Calculate engagement score based on talk ratio and sentiment.
        
        Business rule: Good engagement has balanced talk ratio (40-60%)
        and positive sentiment.
        
        Returns:
            float: Engagement score between 0 and 1
        """
        score = 0.0
        
        # Talk ratio component (optimal is 40-60% customer talking)
        if self.talk_ratio:
            if 0.4 <= self.talk_ratio <= 0.6:
                talk_score = 1.0
            else:
                # Score decreases as we move away from optimal range
                deviation = min(abs(self.talk_ratio - 0.4), abs(self.talk_ratio - 0.6))
                talk_score = max(0, 1 - (deviation * 2))
            score += talk_score * 0.5
        
        # Sentiment component
        if self.sentiment:
            sentiment_score = (self.sentiment.score + 1) / 2  # Normalize -1 to 1 -> 0 to 1
            score += sentiment_score * 0.5
        
        return score
    
    def get_risk_indicators(self) -> List[str]:
        """
        Identify risk indicators based on call characteristics.
        
        Returns:
            List[str]: List of identified risk indicators
        """
        risks = []
        
        if self.sentiment and self.sentiment.is_negative():
            risks.append("negative_sentiment")
        
        if not self.has_clear_next_steps():
            risks.append("no_clear_next_steps")
        
        if self.talk_ratio and self.talk_ratio > 0.7:
            risks.append("high_talk_ratio")
        
        if self.duration_seconds < 600:  # Less than 10 minutes
            risks.append("short_duration")
        
        return risks 