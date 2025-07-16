"""
Qualify Deal Use Case

This module implements the business logic for qualifying deals
based on various criteria.
"""

from dataclasses import dataclass
from datetime import datetime

from core.application.ports.repositories.call_repository import CallRepository
from core.application.ports.repositories.contact_repository import ContactRepository
from core.application.ports.repositories.deal_repository import DealRepository
from domain.entities.contact import EngagementLevel
from domain.entities.deal import Deal, DealStage

@dataclass
class QualifyDealRequest:
    """Request object for qualifying a deal."""

    deal_id: str
    user_id: str  # User performing the qualification

@dataclass
class QualificationCriteria:
    """Criteria used for deal qualification."""

    has_budget: bool
    has_authority: bool
    has_need: bool
    has_timeline: bool
    decision_maker_engaged: bool
    multiple_stakeholders: bool
    positive_sentiment: bool
    recent_engagement: bool

@dataclass
class QualifyDealResponse:
    """Response object for deal qualification."""

    deal_id: str
    is_qualified: bool
    qualification_score: float
    criteria: QualificationCriteria
    recommended_next_steps: list[str]
    risk_factors: list[str]

class DealNotFoundError(Exception):
    """Raised when deal is not found."""

    pass

class QualifyDealUseCase:
    """
    Use case for qualifying deals based on BANT criteria and engagement metrics.

    This use case encapsulates the business logic for determining if a deal
    should move to the qualified stage based on various factors.
    """

    def __init__(
        self,
        deal_repository: DealRepository,
        contact_repository: ContactRepository,
        call_repository: CallRepository,
    ):
        """
        Initialize the use case with required repositories.

        Args:
            deal_repository: Repository for deal data access
            contact_repository: Repository for contact data access
            call_repository: Repository for call data access
        """
        self.deal_repository = deal_repository
        self.contact_repository = contact_repository
        self.call_repository = call_repository

    async def execute(self, request: QualifyDealRequest) -> QualifyDealResponse:
        """
        Execute the deal qualification process.

        Args:
            request: The qualification request

        Returns:
            QualifyDealResponse: The qualification result

        Raises:
            DealNotFoundError: If the deal doesn't exist
        """
        # Retrieve the deal
        deal = await self.deal_repository.get_by_id(request.deal_id)
        if not deal:
            raise DealNotFoundError(f"Deal {request.deal_id} not found")

        # Gather qualification criteria
        criteria = await self._gather_qualification_criteria(deal)

        # Calculate qualification score
        score = self._calculate_qualification_score(criteria)

        # Determine if qualified
        is_qualified = self._is_qualified(score, criteria)

        # Generate recommendations
        next_steps = self._generate_next_steps(deal, criteria, is_qualified)

        # Identify risk factors
        risk_factors = self._identify_risk_factors(deal, criteria)

        # Update deal stage if qualified
        if is_qualified and deal.stage == DealStage.PROSPECTING:
            deal.stage = DealStage.QUALIFICATION
            await self.deal_repository.save(deal)

        return QualifyDealResponse(
            deal_id=deal.id,
            is_qualified=is_qualified,
            qualification_score=score,
            criteria=criteria,
            recommended_next_steps=next_steps,
            risk_factors=risk_factors,
        )

    async def _gather_qualification_criteria(self, deal: Deal) -> QualificationCriteria:
        """
        Gather all qualification criteria for the deal.

        Args:
            deal: The deal to qualify

        Returns:
            QualificationCriteria: The gathered criteria
        """
        # Get associated contacts
        contacts = await self.contact_repository.get_by_deal(deal.id)

        # Get recent calls
        calls = await self.call_repository.get_by_deal(deal.id)
        # Consider calls from the last 30 days as recent
        recent_calls = [
            c for c in calls if (datetime.now() - c.scheduled_at).days <= 30
        ]

        # Check for decision maker engagement
        decision_makers = [c for c in contacts if c.is_decision_maker]
        decision_maker_engaged = any(
            c.engagement_level
            in [EngagementLevel.WARM, EngagementLevel.HOT, EngagementLevel.CHAMPION]
            for c in decision_makers
        )

        # Check for multiple stakeholders
        engaged_contacts = [c for c in contacts if c.is_engaged()]
        multiple_stakeholders = len(engaged_contacts) >= 3

        # Check sentiment from recent calls
        positive_sentiment = False
        if recent_calls:
            # Calculate average sentiment from calls that have sentiment
            calls_with_sentiment = [c for c in recent_calls if c.sentiment]
            if calls_with_sentiment:
                avg_sentiment = sum(
                    c.sentiment.score for c in calls_with_sentiment
                ) / len(calls_with_sentiment)
                positive_sentiment = avg_sentiment > 0.6

        # Check for recent engagement
        recent_engagement = len(recent_calls) > 0 or any(
            c.interaction_count > 0 for c in contacts
        )

        # BANT criteria (simplified - in real implementation, these would come from
        # structured data, call analysis, or explicit fields)
        has_budget = deal.amount is not None and deal.amount > 0
        has_authority = decision_maker_engaged
        has_need = deal.description is not None and len(deal.description) > 50
        has_timeline = deal.expected_close_date is not None

        return QualificationCriteria(
            has_budget=has_budget,
            has_authority=has_authority,
            has_need=has_need,
            has_timeline=has_timeline,
            decision_maker_engaged=decision_maker_engaged,
            multiple_stakeholders=multiple_stakeholders,
            positive_sentiment=positive_sentiment,
            recent_engagement=recent_engagement,
        )

    def _calculate_qualification_score(self, criteria: QualificationCriteria) -> float:
        """
        Calculate a qualification score based on criteria.

        Args:
            criteria: The qualification criteria

        Returns:
            float: Score between 0 and 1
        """
        score = 0.0

        # BANT criteria (60% weight)
        if criteria.has_budget:
            score += 0.15
        if criteria.has_authority:
            score += 0.15
        if criteria.has_need:
            score += 0.15
        if criteria.has_timeline:
            score += 0.15

        # Engagement criteria (40% weight)
        if criteria.decision_maker_engaged:
            score += 0.15
        if criteria.multiple_stakeholders:
            score += 0.10
        if criteria.positive_sentiment:
            score += 0.10
        if criteria.recent_engagement:
            score += 0.05

        return score

    def _is_qualified(self, score: float, criteria: QualificationCriteria) -> bool:
        """
        Determine if a deal is qualified based on score and criteria.

        Business rule: Deal is qualified if:
        - Score >= 0.7 OR
        - Has all BANT criteria OR
        - Has 3/4 BANT + decision maker engaged

        Args:
            score: The qualification score
            criteria: The qualification criteria

        Returns:
            bool: True if qualified
        """
        # High score qualifies
        if score >= 0.7:
            return True

        # All BANT qualifies
        bant_complete = all(
            [
                criteria.has_budget,
                criteria.has_authority,
                criteria.has_need,
                criteria.has_timeline,
            ]
        )
        if bant_complete:
            return True

        # 3/4 BANT + decision maker qualifies
        bant_count = sum(
            [
                criteria.has_budget,
                criteria.has_authority,
                criteria.has_need,
                criteria.has_timeline,
            ]
        )
        return bool(bant_count >= 3 and criteria.decision_maker_engaged)

    def _generate_next_steps(
        self, deal: Deal, criteria: QualificationCriteria, is_qualified: bool
    ) -> list[str]:
        """
        Generate recommended next steps based on qualification results.

        Args:
            deal: The deal
            criteria: The qualification criteria
            is_qualified: Whether the deal is qualified

        Returns:
            List[str]: Recommended next steps
        """
        next_steps = []

        if is_qualified:
            next_steps.append("Schedule a demo or proof of concept")
            next_steps.append("Prepare a formal proposal")
            if not criteria.multiple_stakeholders:
                next_steps.append("Identify and engage additional stakeholders")
        else:
            # Address missing criteria
            if not criteria.has_budget:
                next_steps.append("Discuss budget and confirm funding availability")
            if not criteria.has_authority:
                next_steps.append("Identify and engage decision makers")
            if not criteria.has_need:
                next_steps.append("Conduct deeper discovery to understand pain points")
            if not criteria.has_timeline:
                next_steps.append("Establish a clear timeline and urgency")
            if not criteria.decision_maker_engaged:
                next_steps.append("Schedule a meeting with key decision makers")
            if not criteria.recent_engagement:
                next_steps.append(
                    "Re-engage with the prospect through calls or meetings"
                )

        return next_steps

    def _identify_risk_factors(
        self, deal: Deal, criteria: QualificationCriteria
    ) -> list[str]:
        """
        Identify risk factors for the deal.

        Args:
            deal: The deal
            criteria: The qualification criteria

        Returns:
            List[str]: List of risk factors
        """
        risks = []

        # Check for missing BANT
        missing_bant = []
        if not criteria.has_budget:
            missing_bant.append("budget")
        if not criteria.has_authority:
            missing_bant.append("authority")
        if not criteria.has_need:
            missing_bant.append("need")
        if not criteria.has_timeline:
            missing_bant.append("timeline")

        if missing_bant:
            risks.append(f"Missing BANT criteria: {', '.join(missing_bant)}")

        # Check engagement risks
        if not criteria.decision_maker_engaged:
            risks.append("No decision maker engagement")

        if not criteria.multiple_stakeholders:
            risks.append("Limited stakeholder involvement")

        if not criteria.positive_sentiment:
            risks.append("Neutral or negative sentiment in recent interactions")

        if not criteria.recent_engagement:
            risks.append("No recent engagement activity")

        # Check deal-specific risks
        if deal.is_at_risk():
            risks.append("Deal flagged as at-risk based on activity patterns")

        if deal.days_in_stage and deal.days_in_stage > 30:
            risks.append(
                f"Stuck in {deal.stage.value} stage for {deal.days_in_stage} days"
            )

        return risks
