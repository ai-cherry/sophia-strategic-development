from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ResearchReport:
    """Research report for orchestration patterns"""

    research_results: list[dict[str, Any]]
    key_patterns: dict[str, Any]
    implementation_recommendations: dict[str, Any]
    architecture_insights: dict[str, Any]


@dataclass
class OrchestrationArchitecture:
    """Orchestration architecture configuration"""

    coordination_strategy: dict[str, Any]
    memory_integration: dict[str, Any]
    communication_protocols: dict[str, Any]
    monitoring_framework: dict[str, Any]
    research_validation: bool = True


@dataclass
class OrchestrationState:
    """State for LangGraph orchestration workflow"""

    request: str
    context: dict[str, Any]
    priority: str = "normal"
    timestamp: datetime | None = None
    agents_available: list[str] | None = None
    memory_context: dict[str, Any] | None = None


@dataclass
class OrchestrationResult:
    """Result from orchestration execution"""

    success: bool
    final_response: str | None = None
    agents_used: list[str] | None = None
    execution_time: float | None = None
    quality_score: float | None = None
    coordination_efficiency: float | None = None
    error: str | None = None


@dataclass
class DevelopmentState:
    """State for development group workflow"""

    request: str
    repository_context: dict[str, Any]
    priority: str = "normal"
    current_codebase_state: dict[str, Any] | None = None
    memory_usage_metrics: dict[str, Any] | None = None
    infrastructure_state: dict[str, Any] | None = None
    development_plan: dict[str, Any] | None = None


@dataclass
class DevelopmentResult:
    """Result from development group execution"""

    success: bool
    changes_made: list[str] | None = None
    code_quality_improvement: float | None = None
    infrastructure_updates: list[str] | None = None
    memory_optimization_applied: bool | None = None
    tests_passed: bool | None = None
    deployment_status: str | None = None
    shared_outputs: dict[str, Any] | None = None


@dataclass
class BusinessIntelligenceState:
    """State for business intelligence group workflow"""

    request: str
    business_context: dict[str, Any]
    urgency: str = "normal"
    available_data_sources: list[str] | None = None
    current_metrics: dict[str, Any] | None = None
    external_research_required: bool | None = None


@dataclass
class BusinessIntelligenceResult:
    """Result from business intelligence group execution"""

    success: bool
    executive_insights: dict[str, Any] | None = None
    customer_health_analysis: dict[str, Any] | None = None
    market_opportunities: list[str] | None = None
    competitive_threats: list[str] | None = None
    financial_projections: dict[str, Any] | None = None
    recommended_actions: list[str] | None = None
    confidence_scores: dict[str, float] | None = None
    shared_outputs: dict[str, Any] | None = None


@dataclass
class TaskAnalysis:
    """Analysis of cross-group task requirements"""

    requires_development: bool
    requires_business_intelligence: bool
    development_requirements: str | None = None
    bi_requirements: str | None = None
    can_parallelize: bool = True
    dev_first: bool = False
    coordination_strategy: str = "parallel"


@dataclass
class CrossGroupResult:
    """Result from cross-group coordination"""

    success: bool
    development_result: DevelopmentResult | None = None
    bi_result: BusinessIntelligenceResult | None = None
    synthesis: dict[str, Any] | None = None
    effectiveness_score: float | None = None
