"""
Data models for Gong V2 MCP server
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Request Models
class CallRequest(BaseModel):
    """Request for fetching calls"""

    from_date: datetime | None = Field(None, description="Start date for calls")
    to_date: datetime | None = Field(None, description="End date for calls")
    user_id: str | None = Field(None, description="Filter by specific user")
    limit: int = Field(10, description="Number of calls to return", ge=1, le=100)


class TranscriptRequest(BaseModel):
    """Request for call transcript"""

    call_id: str = Field(..., description="Gong call ID")
    include_sentiment: bool = Field(True, description="Include sentiment analysis")
    include_summary: bool = Field(True, description="Include call summary")


class InsightRequest(BaseModel):
    """Request for sales insights"""

    from_date: datetime = Field(..., description="Start date for analysis")
    to_date: datetime = Field(..., description="End date for analysis")
    team_id: str | None = Field(None, description="Filter by team")
    insight_type: str | None = Field("all", description="Type of insights to generate")


class TeamAnalyticsRequest(BaseModel):
    """Request for team analytics"""

    team_id: str = Field(..., description="Team ID")
    from_date: datetime = Field(..., description="Start date")
    to_date: datetime = Field(..., description="End date")
    metrics: list[str] = Field(["all"], description="Specific metrics to include")


class CoachingRequest(BaseModel):
    """Request for coaching opportunities"""

    user_id: str = Field(..., description="User ID to analyze")
    from_date: datetime | None = Field(None, description="Start date")
    to_date: datetime | None = Field(None, description="End date")
    focus_areas: list[str] = Field([], description="Specific areas to focus on")


class SearchRequest(BaseModel):
    """Request for searching conversations"""

    query: str = Field(..., description="Search query")
    from_date: datetime | None = Field(None, description="Start date")
    to_date: datetime | None = Field(None, description="End date")
    limit: int = Field(20, description="Number of results", ge=1, le=100)


# Response Models
class CallInfo(BaseModel):
    """Information about a call"""

    id: str
    title: str
    scheduled: datetime
    duration: int
    participants: list[dict[str, Any]]
    url: str
    score: float | None
    topics: list[str]
    action_items: list[dict[str, Any]]


class CallResponse(BaseModel):
    """Response for call requests"""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class TranscriptSegment(BaseModel):
    """A segment of call transcript"""

    speaker: str
    text: str
    start_time: float
    sentiment: str


class TranscriptResponse(BaseModel):
    """Response for transcript requests"""

    success: bool
    call_id: str
    segments: list[TranscriptSegment] = []
    summary: str | None = None
    key_moments: list[dict[str, Any]] = []
    error: str | None = None


class InsightMetrics(BaseModel):
    """Sales metrics"""

    total_calls: int
    avg_call_duration: float
    talk_ratio: float
    conversion_rate: float
    customer_sentiment: float


class InsightResponse(BaseModel):
    """Response for insight requests"""

    success: bool
    period: dict[str, str]
    metrics: InsightMetrics | None = None
    insights: list[str] = []
    recommendations: list[str] = []
    trends: dict[str, str] = {}
    error: str | None = None


class TeamMember(BaseModel):
    """Team member analytics"""

    user_id: str
    name: str
    total_calls: int
    avg_score: float
    talk_ratio: float
    conversion_rate: float
    improvement_areas: list[str]


class TeamAnalyticsResponse(BaseModel):
    """Response for team analytics"""

    success: bool
    team_id: str
    period: dict[str, str]
    members: list[TeamMember] = []
    team_metrics: dict[str, Any] = {}
    comparisons: dict[str, Any] = {}
    error: str | None = None


class CoachingOpportunity(BaseModel):
    """A coaching opportunity"""

    type: str
    call_id: str
    title: str
    score: float
    areas: list[str]
    suggestions: list[str]


class CoachingResponse(BaseModel):
    """Response for coaching requests"""

    success: bool
    user_id: str
    opportunities: list[CoachingOpportunity] = []
    patterns: list[dict[str, Any]] = []
    action_plan: list[dict[str, Any]] = []
    error: str | None = None


class SearchResult(BaseModel):
    """A search result"""

    call_id: str
    title: str
    date: datetime
    relevance_score: float
    matched_segments: list[dict[str, Any]]
    context: str


class SearchResponse(BaseModel):
    """Response for search requests"""

    success: bool
    query: str
    total_results: int
    results: list[SearchResult] = []
    error: str | None = None


# Health Check Models
class HealthStatus(BaseModel):
    """Health check status"""

    status: str = Field("healthy", description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field("2.0.0", description="Service version")
    dependencies: dict[str, str] = Field(default_factory=dict)


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Webhook Models
class GongWebhookEvent(BaseModel):
    """Gong webhook event"""

    event_type: str
    call_id: str
    timestamp: datetime
    data: dict[str, Any]


# Analytics Models
class CallAnalytics(BaseModel):
    """Detailed call analytics"""

    call_id: str
    topics_discussed: list[str]
    questions_asked: int
    objections_raised: int
    next_steps: list[str]
    competitor_mentions: list[str]
    pricing_discussed: bool
    decision_criteria: list[str]
    engagement_score: float


class DealIntelligence(BaseModel):
    """Deal intelligence from calls"""

    deal_id: str
    total_calls: int
    last_call_date: datetime
    stakeholders: list[dict[str, Any]]
    deal_stage: str
    risk_factors: list[str]
    opportunities: list[str]
    recommended_actions: list[str]


# Configuration Models
class GongConfig(BaseModel):
    """Gong configuration"""

    api_key: str = Field(..., description="Gong API key")
    api_secret: str = Field(..., description="Gong API secret")
    webhook_secret: str | None = Field(None, description="Webhook secret")
    base_url: str = Field("https://api.gong.io/v2", description="API base URL")
