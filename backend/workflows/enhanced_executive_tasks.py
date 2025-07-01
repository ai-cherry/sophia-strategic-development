#!/usr/bin/env python3
"""
🎯 Enhanced Executive Tasks for Sophia AI
========================================

Extends the existing business task system with executive-level tasks
that leverage group-aware orchestration for CEO dashboard and
strategic decision support.

Business Value:
- Executive business intelligence queries
- Predictive business analysis
- Operational health assessment
- Cross-group data synthesis
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from enum import Enum

from backend.services.mcp_orchestration_service import BusinessTask, TaskPriority


class ExecutiveTaskType(Enum):
    """Types of executive-level tasks"""
    QUARTERLY_BUSINESS_REVIEW = "quarterly_business_review"
    DEAL_PIPELINE_ANALYSIS = "deal_pipeline_analysis"
    TEAM_PRODUCTIVITY_ASSESSMENT = "team_productivity_assessment"
    COST_OPTIMIZATION_REVIEW = "cost_optimization_review"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    CUSTOMER_HEALTH_ANALYSIS = "customer_health_analysis"
    REVENUE_FORECAST = "revenue_forecast"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"


@dataclass
class ExecutiveBusinessIntelligence(BusinessTask):
    """
    CEO dashboard queries requiring cross-group synthesis.
    Extends BusinessTask with executive-specific attributes.
    """
    
    executive_task_type: ExecutiveTaskType
    time_range: str = "last_quarter"  # last_week, last_month, last_quarter, last_year
    comparison_period: Optional[str] = None  # For YoY, QoQ comparisons
    focus_areas: List[str] = field(default_factory=list)
    include_predictions: bool = True
    confidence_threshold: float = 0.8
    
    def __post_init__(self):
        """Initialize executive task with appropriate settings"""
        # Set high priority for executive tasks
        self.priority = TaskPriority.CRITICAL
        
        # Always require synthesis for executive intelligence
        self.requires_synthesis = True
        
        # Set appropriate task type
        self.task_type = "executive_dashboard"
        
        # Add executive context
        if self.context_data is None:
            self.context_data = {}
        
        self.context_data.update({
            "executive_task_type": self.executive_task_type.value,
            "time_range": self.time_range,
            "comparison_period": self.comparison_period,
            "focus_areas": self.focus_areas,
            "include_predictions": self.include_predictions,
            "confidence_threshold": self.confidence_threshold,
            "requested_at": datetime.now(UTC).isoformat()
        })
        
        # Set required capabilities based on task type
        self._set_required_capabilities()
        
        # Call parent post_init
        super().__post_init__()
    
    def _set_required_capabilities(self):
        """Set required capabilities based on executive task type"""
        capability_map = {
            ExecutiveTaskType.QUARTERLY_BUSINESS_REVIEW: [
                "business_insights", "analytics", "reporting", "data_aggregation"
            ],
            ExecutiveTaskType.DEAL_PIPELINE_ANALYSIS: [
                "crm_integration", "analytics", "predictive_modeling", "risk_assessment"
            ],
            ExecutiveTaskType.TEAM_PRODUCTIVITY_ASSESSMENT: [
                "project_management", "communication_analysis", "performance_metrics"
            ],
            ExecutiveTaskType.COST_OPTIMIZATION_REVIEW: [
                "cost_analysis", "infrastructure_monitoring", "optimization"
            ],
            ExecutiveTaskType.COMPETITIVE_INTELLIGENCE: [
                "market_analysis", "web_scraping", "sentiment_analysis"
            ],
            ExecutiveTaskType.CUSTOMER_HEALTH_ANALYSIS: [
                "customer_analytics", "sentiment_tracking", "churn_prediction"
            ],
            ExecutiveTaskType.REVENUE_FORECAST: [
                "financial_modeling", "predictive_analytics", "trend_analysis"
            ],
            ExecutiveTaskType.OPERATIONAL_EFFICIENCY: [
                "process_analysis", "performance_monitoring", "optimization"
            ]
        }
        
        self.required_capabilities = capability_map.get(
            self.executive_task_type,
            ["business_insights", "analytics"]
        )


@dataclass
class PredictiveBusinessAnalysis(BusinessTask):
    """
    AI-powered predictions using data from multiple groups.
    Focuses on forward-looking insights for strategic planning.
    """
    
    prediction_type: str  # revenue, churn, deal_closure, market_trends
    prediction_horizon: str  # next_week, next_month, next_quarter
    confidence_intervals: bool = True
    scenario_analysis: bool = False
    risk_factors: List[str] = field(default_factory=list)
    historical_context: str = "last_6_months"
    
    def __post_init__(self):
        """Initialize predictive analysis task"""
        self.priority = TaskPriority.HIGH
        self.requires_synthesis = True
        self.task_type = "predictive_analysis"
        
        if self.context_data is None:
            self.context_data = {}
        
        self.context_data.update({
            "prediction_type": self.prediction_type,
            "prediction_horizon": self.prediction_horizon,
            "confidence_intervals": self.confidence_intervals,
            "scenario_analysis": self.scenario_analysis,
            "risk_factors": self.risk_factors,
            "historical_context": self.historical_context
        })
        
        # Set capabilities for predictive analysis
        self.required_capabilities = [
            "predictive_analytics",
            "machine_learning",
            "data_aggregation",
            "trend_analysis",
            "risk_assessment"
        ]
        
        super().__post_init__()


@dataclass
class OperationalHealthAssessment(BusinessTask):
    """
    System-wide health monitoring with business impact analysis.
    Provides comprehensive view of operational status.
    """
    
    assessment_scope: List[str] = field(default_factory=list)  # systems to assess
    include_dependencies: bool = True
    business_impact_analysis: bool = True
    performance_benchmarks: Dict[str, float] = field(default_factory=dict)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    remediation_suggestions: bool = True
    
    def __post_init__(self):
        """Initialize operational health assessment"""
        self.priority = TaskPriority.HIGH
        self.requires_synthesis = True
        self.task_type = "operational_health"
        
        if self.context_data is None:
            self.context_data = {}
        
        # Default scope if not specified
        if not self.assessment_scope:
            self.assessment_scope = [
                "all_systems",
                "critical_integrations",
                "data_pipelines",
                "ai_services"
            ]
        
        self.context_data.update({
            "assessment_scope": self.assessment_scope,
            "include_dependencies": self.include_dependencies,
            "business_impact_analysis": self.business_impact_analysis,
            "performance_benchmarks": self.performance_benchmarks,
            "alert_thresholds": self.alert_thresholds,
            "remediation_suggestions": self.remediation_suggestions
        })
        
        # Set capabilities for health assessment
        self.required_capabilities = [
            "health_monitoring",
            "performance_analysis",
            "dependency_mapping",
            "impact_assessment",
            "system_diagnostics"
        ]
        
        super().__post_init__()


class ExecutiveTaskFactory:
    """Factory for creating executive-level tasks"""
    
    @staticmethod
    def create_quarterly_review(
        focus_areas: Optional[List[str]] = None,
        comparison_quarter: Optional[str] = None
    ) -> ExecutiveBusinessIntelligence:
        """Create a quarterly business review task"""
        return ExecutiveBusinessIntelligence(
            task_id=f"qbr_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            task_type="executive_dashboard",
            executive_task_type=ExecutiveTaskType.QUARTERLY_BUSINESS_REVIEW,
            description="Comprehensive quarterly business review with cross-functional insights",
            time_range="last_quarter",
            comparison_period=comparison_quarter,
            focus_areas=focus_areas or ["revenue", "customer_health", "team_performance", "market_position"],
            required_capabilities=[]  # Will be set in post_init
        )
    
    @staticmethod
    def create_deal_risk_analysis(
        deal_ids: Optional[List[str]] = None,
        include_sentiment: bool = True
    ) -> ExecutiveBusinessIntelligence:
        """Create a deal risk analysis task"""
        context_data = {}
        if deal_ids:
            context_data["specific_deals"] = deal_ids
        context_data["include_sentiment"] = include_sentiment
        
        return ExecutiveBusinessIntelligence(
            task_id=f"deal_risk_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            task_type="executive_dashboard",
            executive_task_type=ExecutiveTaskType.DEAL_PIPELINE_ANALYSIS,
            description="Analyze deal pipeline with risk assessment and sentiment analysis",
            time_range="current",
            focus_areas=["deal_health", "risk_factors", "closure_probability"],
            context_data=context_data,
            required_capabilities=[]
        )
    
    @staticmethod
    def create_revenue_forecast(
        horizon: str = "next_quarter",
        include_scenarios: bool = True
    ) -> PredictiveBusinessAnalysis:
        """Create a revenue forecast task"""
        return PredictiveBusinessAnalysis(
            task_id=f"revenue_forecast_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            task_type="predictive_analysis",
            description="AI-powered revenue forecast with confidence intervals",
            prediction_type="revenue",
            prediction_horizon=horizon,
            scenario_analysis=include_scenarios,
            risk_factors=["market_conditions", "deal_pipeline", "customer_churn"],
            required_capabilities=[]
        )
    
    @staticmethod
    def create_system_health_check(
        critical_only: bool = False
    ) -> OperationalHealthAssessment:
        """Create a system health assessment task"""
        scope = ["critical_systems"] if critical_only else ["all_systems"]
        
        return OperationalHealthAssessment(
            task_id=f"health_check_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            task_type="operational_health",
            description="Comprehensive operational health assessment with business impact",
            assessment_scope=scope,
            performance_benchmarks={
                "response_time_ms": 200,
                "error_rate": 0.01,
                "availability": 0.999
            },
            alert_thresholds={
                "response_time_ms": 500,
                "error_rate": 0.05,
                "availability": 0.99
            },
            required_capabilities=[]
        )
    
    @staticmethod
    def create_competitive_analysis(
        competitors: Optional[List[str]] = None,
        focus_areas: Optional[List[str]] = None
    ) -> ExecutiveBusinessIntelligence:
        """Create a competitive intelligence task"""
        context_data = {}
        if competitors:
            context_data["target_competitors"] = competitors
        
        return ExecutiveBusinessIntelligence(
            task_id=f"competitive_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            task_type="executive_dashboard",
            executive_task_type=ExecutiveTaskType.COMPETITIVE_INTELLIGENCE,
            description="Analyze competitive landscape and market positioning",
            time_range="last_month",
            focus_areas=focus_areas or ["market_share", "product_features", "pricing", "customer_sentiment"],
            context_data=context_data,
            required_capabilities=[]
        )
    
    @staticmethod
    def create_team_performance_review(
        teams: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None
    ) -> ExecutiveBusinessIntelligence:
        """Create a team performance assessment task"""
        context_data = {}
        if teams:
            context_data["specific_teams"] = teams
        if metrics:
            context_data["focus_metrics"] = metrics
        
        return ExecutiveBusinessIntelligence(
            task_id=f"team_perf_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            task_type="executive_dashboard",
            executive_task_type=ExecutiveTaskType.TEAM_PRODUCTIVITY_ASSESSMENT,
            description="Assess team productivity and collaboration effectiveness",
            time_range="last_month",
            focus_areas=["velocity", "quality", "collaboration", "satisfaction"],
            context_data=context_data,
            required_capabilities=[]
        ) 