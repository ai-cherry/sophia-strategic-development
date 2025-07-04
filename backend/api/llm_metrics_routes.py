"""
LLM Metrics and Cost Alerts API Routes
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import logging

from backend.services.unified_llm_service import UnifiedLLMService
from backend.services.cost_engineering_service import CostEngineeringService
from backend.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/llm")

# Pydantic models
class CostAlert(BaseModel):
    """Cost alert model"""
    title: str
    message: str
    severity: str = Field(..., pattern="^(info|warning|critical)$")
    timestamp: str
    alert_type: str = Field(..., pattern="^(daily_budget|monthly_budget|spike|projection)$")
    
class BudgetStatus(BaseModel):
    """Budget status model"""
    daily_budget: float
    monthly_budget: float
    daily_cost: float
    monthly_cost: float
    projected_monthly: float
    is_over_budget: bool
    budget_utilization_daily: float
    budget_utilization_monthly: float

class ProviderMetrics(BaseModel):
    """Provider usage metrics"""
    provider: str
    model: str
    requests: int
    cost: float
    avg_latency: int
    primary_task_type: str
    
class LLMMetricsResponse(BaseModel):
    """Complete LLM metrics response"""
    daily_cost: float
    monthly_cost: float
    cost_change: float
    daily_requests: int
    request_change: float
    avg_response_time: int
    response_time_change: float
    cache_hit_rate: float
    cache_improvement: float
    alerts: List[CostAlert]
    budget_status: BudgetStatus
    providers: List[ProviderMetrics]
    task_costs: Dict[str, float]
    request_trend: Dict[str, Any]
    snowflake_savings: float
    data_movement_avoided: float
    snowflake_percentage: float

# Dependency injection
def get_llm_service() -> UnifiedLLMService:
    """Get LLM service instance"""
    return UnifiedLLMService()

def get_cost_service() -> CostEngineeringService:
    """Get cost engineering service instance"""
    return CostEngineeringService()

def get_config_manager() -> ConfigManager:
    """Get config manager instance"""
    return ConfigManager()

@router.get("/stats", response_model=LLMMetricsResponse)
async def get_llm_stats(
    llm_service: UnifiedLLMService = Depends(get_llm_service),
    cost_service: CostEngineeringService = Depends(get_cost_service),
    config: ConfigManager = Depends(get_config_manager)
) -> LLMMetricsResponse:
    """Get comprehensive LLM metrics and cost data"""
    try:
        # Initialize services if needed
        if not cost_service.initialized:
            await cost_service.initialize()
            
        # Get current metrics
        global_metrics = cost_service.global_metrics
        
        # Calculate daily and monthly costs
        today = datetime.now().date()
        month_start = datetime.now().replace(day=1).date()
        
        # Get cost report
        cost_report = await cost_service.get_cost_report()
        
        # Check budget status
        daily_budget = config.get_value("llm_daily_budget", 100.0)
        monthly_budget = config.get_value("llm_monthly_budget", 3000.0)
        
        daily_cost = await cost_service._calculate_daily_cost()
        monthly_cost = await cost_service._calculate_monthly_cost()
        
        # Calculate projected monthly cost based on current rate
        days_in_month = 30
        days_elapsed = (datetime.now().date() - month_start).days + 1
        projected_monthly = (monthly_cost / days_elapsed) * days_in_month if days_elapsed > 0 else 0
        
        # Generate alerts
        alerts = []
        
        # Daily budget alert
        if daily_cost > daily_budget * 0.8:
            severity = "critical" if daily_cost > daily_budget else "warning"
            alerts.append(CostAlert(
                title="Daily Budget Alert",
                message=f"Daily LLM cost (${daily_cost:.2f}) is {'exceeding' if daily_cost > daily_budget else 'approaching'} the budget limit of ${daily_budget}",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                alert_type="daily_budget"
            ))
            
        # Monthly budget projection alert
        if projected_monthly > monthly_budget * 0.8:
            severity = "critical" if projected_monthly > monthly_budget else "warning"
            alerts.append(CostAlert(
                title="Monthly Budget Projection Alert",
                message=f"Projected monthly cost (${projected_monthly:.2f}) will {'exceed' if projected_monthly > monthly_budget else 'approach'} the budget limit of ${monthly_budget}",
                severity=severity,
                timestamp=datetime.now().isoformat(),
                alert_type="projection"
            ))
            
        # Cost spike alert (>50% increase from yesterday)
        yesterday_cost = 50.0  # Mock data - would calculate from historical data
        if daily_cost > yesterday_cost * 1.5:
            alerts.append(CostAlert(
                title="Cost Spike Detected",
                message=f"Today's cost is {((daily_cost / yesterday_cost - 1) * 100):.0f}% higher than yesterday",
                severity="warning",
                timestamp=datetime.now().isoformat(),
                alert_type="spike"
            ))
        
        # Budget status
        budget_status = BudgetStatus(
            daily_budget=daily_budget,
            monthly_budget=monthly_budget,
            daily_cost=round(daily_cost, 2),
            monthly_cost=round(monthly_cost, 2),
            projected_monthly=round(projected_monthly, 2),
            is_over_budget=daily_cost > daily_budget or monthly_cost > monthly_budget,
            budget_utilization_daily=round((daily_cost / daily_budget) * 100, 1),
            budget_utilization_monthly=round((monthly_cost / monthly_budget) * 100, 1)
        )
        
        # Provider breakdown (mock data - would come from actual metrics)
        providers = [
            ProviderMetrics(
                provider="snowflake",
                model="cortex-llama3",
                requests=1250,
                cost=15.30,
                avg_latency=450,
                primary_task_type="data_analysis"
            ),
            ProviderMetrics(
                provider="portkey",
                model="gpt-4o",
                requests=320,
                cost=28.50,
                avg_latency=850,
                primary_task_type="complex_reasoning"
            ),
            ProviderMetrics(
                provider="openrouter",
                model="mixtral-8x7b",
                requests=890,
                cost=8.90,
                avg_latency=320,
                primary_task_type="general_query"
            )
        ]
        
        # Task costs breakdown
        task_costs = {
            "data_analysis": 18.50,
            "complex_reasoning": 28.50,
            "general_query": 12.30,
            "summarization": 8.40,
            "code_generation": 15.20
        }
        
        # Request trend (last 7 days)
        request_trend = {
            "labels": [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)],
            "values": [1200, 1350, 1100, 1450, 1600, 1550, 1800]  # Mock data
        }
        
        # Calculate metrics changes
        cost_change = 15.5  # Mock: 15.5% increase
        request_change = 12.0  # Mock: 12% increase
        response_time_change = -5.0  # Mock: 5% improvement
        cache_improvement = 3.5  # Mock: 3.5% improvement
        
        return LLMMetricsResponse(
            daily_cost=round(daily_cost, 2),
            monthly_cost=round(monthly_cost, 2),
            cost_change=cost_change,
            daily_requests=global_metrics.request_count,
            request_change=request_change,
            avg_response_time=int(global_metrics.avg_latency_ms),
            response_time_change=response_time_change,
            cache_hit_rate=round(cost_report["metrics"]["cache_hit_rate"] * 100, 1),
            cache_improvement=cache_improvement,
            alerts=alerts,
            budget_status=budget_status,
            providers=providers,
            task_costs=task_costs,
            request_trend=request_trend,
            snowflake_savings=125.50,  # Mock data
            data_movement_avoided=450.0,  # Mock data GB
            snowflake_percentage=35.0  # Mock data %
        )
        
    except Exception as e:
        logger.error(f"Error getting LLM stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/budget/set")
async def set_budget(
    daily_budget: Optional[float] = None,
    monthly_budget: Optional[float] = None,
    cost_service: CostEngineeringService = Depends(get_cost_service),
    config: ConfigManager = Depends(get_config_manager)
) -> Dict[str, Any]:
    """Set LLM cost budgets"""
    try:
        # Update budgets
        if daily_budget is not None:
            config.set_value("llm_daily_budget", daily_budget)
            await cost_service.set_cost_budget(daily_budget=daily_budget)
            
        if monthly_budget is not None:
            config.set_value("llm_monthly_budget", monthly_budget)
            await cost_service.set_cost_budget(monthly_budget=monthly_budget)
            
        return {
            "status": "success",
            "daily_budget": daily_budget or config.get_value("llm_daily_budget", 100.0),
            "monthly_budget": monthly_budget or config.get_value("llm_monthly_budget", 3000.0)
        }
        
    except Exception as e:
        logger.error(f"Error setting budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_cost_alerts(
    limit: int = 10,
    severity: Optional[str] = None,
    cost_service: CostEngineeringService = Depends(get_cost_service)
) -> List[CostAlert]:
    """Get recent cost alerts"""
    try:
        # This would fetch from a persistent store
        # For now, generate based on current status
        alerts = []
        
        daily_cost = await cost_service._calculate_daily_cost()
        monthly_cost = await cost_service._calculate_monthly_cost()
        
        # Add relevant alerts based on current metrics
        if daily_cost > 80:
            alerts.append(CostAlert(
                title="High Daily Spend",
                message=f"Daily LLM cost of ${daily_cost:.2f} is above normal",
                severity="warning",
                timestamp=datetime.now().isoformat(),
                alert_type="daily_budget"
            ))
            
        # Filter by severity if requested
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
            
        return alerts[:limit]
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
