"""
Sales Intelligence Agent - Utils Module
Contains utility functions and helper classes
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from .sales_intelligence_agent_models import (
    DealRiskLevel,
    SalesStage,
    DealRiskAssessment,
    SalesEmailRequest,
)

logger = logging.getLogger(__name__)


class SalesIntelligenceUtils:
    """Utility functions for sales intelligence operations"""

    @staticmethod
    def calculate_risk_score(
        risk_factors: list[str], sentiment: dict[str, float]
    ) -> float:
        """Calculate overall risk score based on factors and sentiment"""
        base_score = 0.0
        
        # Risk factor scoring
        risk_weights = {
            "no_recent_activity": 15,
            "overdue_follow_up": 20,
            "negative_sentiment": 25,
            "competitor_mention": 10,
            "budget_concerns": 20,
            "decision_delay": 15,
            "stakeholder_change": 10,
            "price_objection": 15,
            "technical_concerns": 10,
            "timeline_pressure": 5,
        }
        
        for factor in risk_factors:
            base_score += risk_weights.get(factor, 5)
        
        # Sentiment scoring
        if sentiment:
            avg_sentiment = sum(sentiment.values()) / len(sentiment)
            if avg_sentiment < 0.3:  # Very negative
                base_score += 25
            elif avg_sentiment < 0.5:  # Negative
                base_score += 15
            elif avg_sentiment < 0.7:  # Neutral
                base_score += 5
        
        return min(100.0, base_score)

    @staticmethod
    def determine_risk_level(risk_score: float) -> DealRiskLevel:
        """Determine risk level from numerical score"""
        if risk_score >= 75:
            return DealRiskLevel.CRITICAL
        elif risk_score >= 50:
            return DealRiskLevel.HIGH
        elif risk_score >= 25:
            return DealRiskLevel.MEDIUM
        else:
            return DealRiskLevel.LOW

    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency amount for display"""
        if amount >= 1_000_000:
            return f"${amount/1_000_000:.1f}M"
        elif amount >= 1_000:
            return f"${amount/1_000:.0f}K"
        else:
            return f"${amount:.0f}"

    @staticmethod
    def calculate_days_to_close(close_date: datetime) -> int:
        """Calculate days until close date"""
        return (close_date - datetime.now()).days

    @staticmethod
    def get_stage_probability(stage: SalesStage) -> float:
        """Get probability of closing based on stage"""
        stage_probabilities = {
            SalesStage.PROSPECTING: 0.1,
            SalesStage.QUALIFICATION: 0.2,
            SalesStage.DISCOVERY: 0.3,
            SalesStage.PROPOSAL: 0.5,
            SalesStage.NEGOTIATION: 0.7,
            SalesStage.CLOSING: 0.9,
            SalesStage.WON: 1.0,
            SalesStage.LOST: 0.0,
        }
        return stage_probabilities.get(stage, 0.3)
