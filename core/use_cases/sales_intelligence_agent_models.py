"""
Sales Intelligence Agent - Models Module
Contains all data models, enums, and type definitions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DealRiskLevel(str, Enum):
    """Deal risk assessment levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SalesStage(str, Enum):
    """Sales pipeline stages"""

    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    DISCOVERY = "discovery"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    WON = "won"
    LOST = "lost"


class EmailType(str, Enum):
    """Types of sales emails"""

    FOLLOW_UP = "follow_up"
    PROPOSAL = "proposal"
    OBJECTION_HANDLING = "objection_handling"
    CHECK_IN = "check_in"
    CLOSING = "closing"
    THANK_YOU = "thank_you"
    RE_ENGAGEMENT = "re_engagement"


@dataclass
class DealRiskAssessment:
    """Deal risk assessment result"""

    deal_id: str
    deal_name: str
    account_name: str
    deal_stage: SalesStage
    deal_value: float
    close_date: datetime

    # Risk factors
    risk_level: DealRiskLevel
    risk_score: float  # 0-100
    risk_factors: list[str]

    # AI insights
    ai_analysis: str
    recommendations: list[str]
    next_actions: list[str]

    # Supporting data
    recent_activities: list[dict[str, Any]]
    gong_insights: list[dict[str, Any]]
    stakeholder_sentiment: dict[str, float]

    # Metadata
    confidence_score: float
    analysis_timestamp: datetime = datetime.now()


@dataclass
class SalesEmailRequest:
    """Request for AI-generated sales email"""

    email_type: EmailType
    deal_id: str
    recipient_name: str
    recipient_role: str
    context: str
    key_points: list[str]
    call_to_action: str
    tone: str = "professional"
    include_attachments: bool = False
    urgency_level: str = "normal"


@dataclass
class CompetitorTalkingPoints:
    """Competitor talking points and differentiators"""

    competitor_name: str
    deal_context: str

    # Talking points
    key_differentiators: list[str]
    competitive_advantages: list[str]
    objection_responses: list[str]
    proof_points: list[str]

    # AI insights
    positioning_strategy: str
    recommended_approach: str

    confidence_score: float


@dataclass
class PipelineAnalysis:
    """Sales pipeline analysis result"""

    analysis_period: str
    total_pipeline_value: float
    weighted_pipeline_value: float

    # Stage analysis
    deals_by_stage: dict[str, int]
    value_by_stage: dict[str, float]
    conversion_rates: dict[str, float]

    # Forecasting
    forecast_confidence: float
    likely_close_value: float
    best_case_value: float
    worst_case_value: float

    # AI insights
    pipeline_health_score: float
    key_insights: list[str]
    recommendations: list[str]

    analysis_timestamp: datetime = datetime.now()


@dataclass
class SalesEmailResult:
    """Result of sales email generation"""

    email_content: str
    subject_lines: list[str]
    email_type: str
    recipient: dict[str, str]
    deal_id: str
    quality_score: float
    word_count: int
    metadata: dict[str, Any]
    generated_at: datetime = datetime.now()


@dataclass
class WorkflowTaskResult:
    """Result of workflow task execution"""

    task_id: str
    status: str
    result: dict[str, Any]
    confidence_score: float
    execution_time: float
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCapabilities:
    """Agent capabilities definition"""

    primary_capabilities: list[str]
    supported_tasks: list[str]
    data_sources: list[str]
    output_formats: list[str]
    integration_points: list[str]
    performance_metrics: dict[str, Any]
