from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


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
    timestamp: Optional[datetime] = None
    agents_available: Optional[list[str]] = None
    memory_context: Optional[dict[str, Any]] = None


@dataclass
class OrchestrationResult:
    """Result from orchestration execution"""

    success: bool
    final_response: Optional[str] = None
    agents_used: Optional[list[str]] = None
    execution_time: Optional[float] = None
    quality_score: Optional[float] = None
    coordination_efficiency: Optional[float] = None
    error: Optional[str] = None


@dataclass
class DevelopmentState:
    """State for development group workflow"""

    request: str
    repository_context: dict[str, Any]
    priority: str = "normal"
    current_codebase_state: Optional[dict[str, Any]] = None
    memory_usage_metrics: Optional[dict[str, Any]] = None
    infrastructure_state: Optional[dict[str, Any]] = None
    development_plan: Optional[dict[str, Any]] = None


@dataclass
class DevelopmentResult:
    """Result from development group execution"""

    success: bool
    changes_made: Optional[list[str]] = None
    code_quality_improvement: Optional[float] = None
    infrastructure_updates: Optional[list[str]] = None
    memory_optimization_applied: Optional[bool] = None
    tests_passed: Optional[bool] = None
    deployment_status: Optional[str] = None
    shared_outputs: Optional[dict[str, Any]] = None


@dataclass
class BusinessIntelligenceState:
    """State for business intelligence group workflow"""

    request: str
    business_context: dict[str, Any]
    urgency: str = "normal"
    available_data_sources: Optional[list[str]] = None
    current_metrics: Optional[dict[str, Any]] = None
    external_research_required: Optional[bool] = None


@dataclass
class BusinessIntelligenceResult:
    """Result from business intelligence group execution"""

    success: bool
    executive_insights: Optional[dict[str, Any]] = None
    customer_health_analysis: Optional[dict[str, Any]] = None
    market_opportunities: Optional[list[str]] = None
    competitive_threats: Optional[list[str]] = None
    financial_projections: Optional[dict[str, Any]] = None
    recommended_actions: Optional[list[str]] = None
    confidence_scores: Optional[dict[str, float]] = None
    shared_outputs: Optional[dict[str, Any]] = None


@dataclass
class TaskAnalysis:
    """Analysis of cross-group task requirements"""

    requires_development: bool
    requires_business_intelligence: bool
    development_requirements: Optional[str] = None
    bi_requirements: Optional[str] = None
    can_parallelize: bool = True
    dev_first: bool = False
    coordination_strategy: str = "parallel"


@dataclass
class CrossGroupResult:
    """Result from cross-group coordination"""

    success: bool
    development_result: Optional[DevelopmentResult] = None
    bi_result: Optional[BusinessIntelligenceResult] = None
    synthesis: Optional[dict[str, Any]] = None
    effectiveness_score: Optional[float] = None
