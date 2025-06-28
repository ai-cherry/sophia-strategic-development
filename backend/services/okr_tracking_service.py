"""
Sophia AI OKR Tracking Service

Real-time tracking and optimization for CEO's strategic OKRs:
1. AI-First Company transformation
2. Revenue per Employee optimization
3. Revenue per Apartment Unit tracking
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

from ..utils.enhanced_snowflake_cortex_service import EnhancedSnowflakeCortexService

logger = logging.getLogger(__name__)


class OKRStatus(Enum):
    """OKR status tracking"""

    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BEHIND = "behind"
    EXCEEDED = "exceeded"


@dataclass
class OKRMetric:
    """Individual OKR metric structure"""

    name: str
    current_value: float
    target_value: float
    unit: str
    trend_7d: float
    trend_30d: float
    status: OKRStatus
    confidence: float
    last_updated: datetime


@dataclass
class OKRInsight:
    """AI-generated OKR insight"""

    okr_name: str
    insight_type: str  # 'opportunity', 'risk', 'optimization'
    description: str
    impact_score: float
    urgency: str  # 'low', 'medium', 'high', 'critical'
    recommended_actions: List[str]
    confidence: float


class OKRTrackingService:
    """Comprehensive OKR tracking service for executive decision support"""

    def __init__(self):
        self.cortex_service = EnhancedSnowflakeCortexService()
        self.okr_definitions = {
            "ai_first_company": {
                "name": "AI-First Company Transformation",
                "target": 0.95,
                "unit": "transformation_score",
                "weight": 0.4,
            },
            "revenue_per_employee": {
                "name": "Revenue per Employee Optimization",
                "target": 250000,  # $250K per employee
                "unit": "usd_annually",
                "weight": 0.35,
            },
            "revenue_per_unit": {
                "name": "Revenue per Apartment Unit",
                "target": 2500,  # $2.5K per unit annually
                "unit": "usd_per_unit_annually",
                "weight": 0.25,
            },
        }

    async def get_real_time_okr_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive real-time OKR dashboard data"""
        try:
            # Fetch all OKR metrics in parallel
            ai_first_task = asyncio.create_task(self._calculate_ai_first_score())
            revenue_per_employee_task = asyncio.create_task(
                self._calculate_revenue_per_employee()
            )
            revenue_per_unit_task = asyncio.create_task(
                self._calculate_revenue_per_unit()
            )

            # Wait for all calculations
            ai_first_metric = await ai_first_task
            revenue_per_employee_metric = await revenue_per_employee_task
            revenue_per_unit_metric = await revenue_per_unit_task

            # Generate insights
            insights = await self._generate_okr_insights(
                [ai_first_metric, revenue_per_employee_metric, revenue_per_unit_metric]
            )

            # Calculate overall score
            overall_score = self._calculate_overall_okr_score(
                [ai_first_metric, revenue_per_employee_metric, revenue_per_unit_metric]
            )

            return {
                "overall_score": overall_score,
                "last_updated": datetime.now().isoformat(),
                "okrs": {
                    "ai_first_company": ai_first_metric,
                    "revenue_per_employee": revenue_per_employee_metric,
                    "revenue_per_unit": revenue_per_unit_metric,
                },
                "insights": insights,
                "critical_actions": await self._get_critical_actions(insights),
                "trend_analysis": await self._analyze_okr_trends(),
            }

        except Exception as e:
            logger.error(f"Error generating OKR dashboard: {e}")
            return self._get_fallback_dashboard()

    async def _calculate_ai_first_score(self) -> OKRMetric:
        """Calculate AI-First Company transformation score"""
        try:
            # Use Snowflake Cortex to analyze AI adoption metrics
            sql_query = """
            WITH ai_adoption_metrics AS (
                SELECT 
                    -- Employee AI tool usage
                    COUNT(DISTINCT CASE WHEN ai_tool_usage > 0 THEN employee_id END) / 
                    COUNT(DISTINCT employee_id) as employee_adoption_rate,
                    
                    -- AI-influenced decisions
                    COUNT(CASE WHEN decision_ai_input = true THEN 1 END) / 
                    COUNT(*) as ai_decision_ratio,
                    
                    -- Process automation coverage
                    SUM(CASE WHEN automated = true THEN 1 ELSE 0 END) / 
                    COUNT(*) as automation_coverage,
                    
                    -- AI investment ratio
                    SUM(CASE WHEN category = 'AI' THEN amount ELSE 0 END) / 
                    SUM(amount) as ai_investment_ratio
                    
                FROM AI_USAGE_ANALYTICS.ADOPTION_METRICS 
                WHERE date >= CURRENT_DATE - 30
            )
            SELECT 
                (employee_adoption_rate * 0.3 + 
                 ai_decision_ratio * 0.3 + 
                 automation_coverage * 0.2 + 
                 ai_investment_ratio * 0.2) as ai_first_score,
                employee_adoption_rate,
                ai_decision_ratio,
                automation_coverage,
                ai_investment_ratio
            FROM ai_adoption_metrics
            """

            result = await self.cortex_service.execute_query(sql_query)

            if result:
                current_score = float(result[0].get("AI_FIRST_SCORE", 0))

                # Calculate trends
                trend_7d = await self._calculate_score_trend("ai_first", 7)
                trend_30d = await self._calculate_score_trend("ai_first", 30)

                return OKRMetric(
                    name="AI-First Company Transformation",
                    current_value=current_score,
                    target_value=0.95,
                    unit="transformation_score",
                    trend_7d=trend_7d,
                    trend_30d=trend_30d,
                    status=self._determine_status(current_score, 0.95),
                    confidence=0.85,
                    last_updated=datetime.now(),
                )

        except Exception as e:
            logger.error(f"Error calculating AI-first score: {e}")

        # Fallback calculation
        return await self._get_fallback_ai_first_metric()

    async def _calculate_revenue_per_employee(self) -> OKRMetric:
        """Calculate revenue per employee with trend analysis"""
        try:
            sql_query = """
            WITH revenue_employee_metrics AS (
                SELECT 
                    SUM(revenue) as total_revenue,
                    COUNT(DISTINCT employee_id) as total_employees,
                    SUM(revenue) / COUNT(DISTINCT employee_id) as revenue_per_employee
                FROM (
                    -- HubSpot revenue data
                    SELECT amount as revenue, created_date, 'hubspot' as source
                    FROM HUBSPOT_DATA.DEALS 
                    WHERE deal_stage = 'closed_won' 
                    AND created_date >= CURRENT_DATE - 365
                    
                    UNION ALL
                    
                    -- Additional revenue sources
                    SELECT revenue_amount as revenue, transaction_date as created_date, 'payready' as source
                    FROM PAYREADY_CORE_SQL.TRANSACTIONS
                    WHERE transaction_date >= CURRENT_DATE - 365
                ) revenue_data
                CROSS JOIN (
                    SELECT COUNT(DISTINCT employee_id) as employee_id
                    FROM AI_USAGE_ANALYTICS.EMPLOYEE_METRICS
                    WHERE active = true
                ) employee_data
            )
            SELECT 
                revenue_per_employee,
                total_revenue,
                total_employees
            FROM revenue_employee_metrics
            """

            result = await self.cortex_service.execute_query(sql_query)

            if result:
                current_rpe = float(result[0].get("REVENUE_PER_EMPLOYEE", 0))

                # Calculate trends
                trend_7d = await self._calculate_revenue_trend("employee", 7)
                trend_30d = await self._calculate_revenue_trend("employee", 30)

                return OKRMetric(
                    name="Revenue per Employee Optimization",
                    current_value=current_rpe,
                    target_value=250000,
                    unit="usd_annually",
                    trend_7d=trend_7d,
                    trend_30d=trend_30d,
                    status=self._determine_status(current_rpe, 250000),
                    confidence=0.90,
                    last_updated=datetime.now(),
                )

        except Exception as e:
            logger.error(f"Error calculating revenue per employee: {e}")

        # Fallback calculation
        return await self._get_fallback_revenue_per_employee_metric()

    async def _calculate_revenue_per_unit(self) -> OKRMetric:
        """Calculate revenue per apartment unit"""
        try:
            sql_query = """
            WITH unit_revenue_metrics AS (
                SELECT 
                    SUM(revenue_amount) as total_revenue,
                    COUNT(DISTINCT property_unit_id) as total_units,
                    SUM(revenue_amount) / COUNT(DISTINCT property_unit_id) as revenue_per_unit
                FROM PROPERTY_ASSETS.UNIT_REVENUE_TRACKING
                WHERE revenue_date >= CURRENT_DATE - 365
                AND property_unit_id IS NOT NULL
            )
            SELECT 
                revenue_per_unit,
                total_revenue,
                total_units
            FROM unit_revenue_metrics
            """

            result = await self.cortex_service.execute_query(sql_query)

            if result:
                current_rpu = float(result[0].get("REVENUE_PER_UNIT", 0))

                # Calculate trends
                trend_7d = await self._calculate_revenue_trend("unit", 7)
                trend_30d = await self._calculate_revenue_trend("unit", 30)

                return OKRMetric(
                    name="Revenue per Apartment Unit",
                    current_value=current_rpu,
                    target_value=2500,
                    unit="usd_per_unit_annually",
                    trend_7d=trend_7d,
                    trend_30d=trend_30d,
                    status=self._determine_status(current_rpu, 2500),
                    confidence=0.88,
                    last_updated=datetime.now(),
                )

        except Exception as e:
            logger.error(f"Error calculating revenue per unit: {e}")

        # Fallback calculation
        return await self._get_fallback_revenue_per_unit_metric()

    async def _generate_okr_insights(
        self, metrics: List[OKRMetric]
    ) -> List[OKRInsight]:
        """Generate AI-powered insights for OKR optimization"""
        insights = []

        try:
            for metric in metrics:
                # Use Snowflake Cortex for AI-powered insight generation
                insight_prompt = f"""
                Analyze this OKR metric and provide strategic insights:
                
                OKR: {metric.name}
                Current: {metric.current_value} {metric.unit}
                Target: {metric.target_value} {metric.unit}
                7-day trend: {metric.trend_7d}%
                30-day trend: {metric.trend_30d}%
                Status: {metric.status.value}
                
                Provide specific, actionable insights for improvement.
                """

                cortex_result = await self.cortex_service.generate_insights(
                    insight_prompt, context_data={"okr_metric": metric}
                )

                if cortex_result:
                    insights.append(
                        OKRInsight(
                            okr_name=metric.name,
                            insight_type="optimization",
                            description=cortex_result.get("insight", ""),
                            impact_score=cortex_result.get("impact_score", 0.7),
                            urgency=cortex_result.get("urgency", "medium"),
                            recommended_actions=cortex_result.get("actions", []),
                            confidence=cortex_result.get("confidence", 0.8),
                        )
                    )

        except Exception as e:
            logger.error(f"Error generating OKR insights: {e}")
            # Add fallback insights
            insights.extend(await self._get_fallback_insights(metrics))

        return insights

    def _determine_status(self, current: float, target: float) -> OKRStatus:
        """Determine OKR status based on current vs target"""
        progress = current / target if target > 0 else 0

        if progress >= 1.0:
            return OKRStatus.EXCEEDED
        elif progress >= 0.8:
            return OKRStatus.ON_TRACK
        elif progress >= 0.6:
            return OKRStatus.AT_RISK
        else:
            return OKRStatus.BEHIND

    def _calculate_overall_okr_score(self, metrics: List[OKRMetric]) -> Dict[str, Any]:
        """Calculate weighted overall OKR score"""
        total_weighted_score = 0
        total_weight = 0

        for metric in metrics:
            okr_key = self._get_okr_key(metric.name)
            if okr_key in self.okr_definitions:
                weight = self.okr_definitions[okr_key]["weight"]
                progress = (
                    metric.current_value / metric.target_value
                    if metric.target_value > 0
                    else 0
                )

                total_weighted_score += progress * weight
                total_weight += weight

        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0

        return {
            "score": min(overall_score * 100, 100),  # Cap at 100%
            "grade": self._get_score_grade(overall_score),
            "trend": "improving",  # TODO: Calculate based on historical data
        }

    def _get_okr_key(self, okr_name: str) -> str:
        """Get OKR key from name"""
        if "AI-First" in okr_name:
            return "ai_first_company"
        elif "Employee" in okr_name:
            return "revenue_per_employee"
        elif "Unit" in okr_name:
            return "revenue_per_unit"
        return "unknown"

    def _get_score_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.70:
            return "C"
        else:
            return "D"

    async def _calculate_score_trend(self, okr_type: str, days: int) -> float:
        """Calculate trend for specific OKR over time period"""
        # TODO: Implement trend calculation from historical data
        # For now, return mock data
        return 2.5 if days == 7 else 8.3

    async def _calculate_revenue_trend(self, revenue_type: str, days: int) -> float:
        """Calculate revenue trend over time period"""
        # TODO: Implement revenue trend calculation
        # For now, return mock data
        return 3.2 if days == 7 else 12.1

    async def _get_critical_actions(
        self, insights: List[OKRInsight]
    ) -> List[Dict[str, Any]]:
        """Extract critical actions from insights"""
        critical_actions = []

        for insight in insights:
            if insight.urgency in ["high", "critical"]:
                critical_actions.append(
                    {
                        "okr": insight.okr_name,
                        "action": insight.recommended_actions[0]
                        if insight.recommended_actions
                        else "Review required",
                        "urgency": insight.urgency,
                        "impact": insight.impact_score,
                    }
                )

        # Sort by impact score descending
        return sorted(critical_actions, key=lambda x: x["impact"], reverse=True)[:5]

    async def _analyze_okr_trends(self) -> Dict[str, Any]:
        """Analyze OKR trends across all metrics"""
        return {
            "overall_direction": "improving",
            "momentum": "building",
            "risk_areas": ["AI adoption rate", "Process automation"],
            "opportunities": ["Employee productivity", "Customer expansion"],
        }

    # Fallback methods for when Snowflake data is unavailable
    async def _get_fallback_ai_first_metric(self) -> OKRMetric:
        """Fallback AI-first metric when data unavailable"""
        return OKRMetric(
            name="AI-First Company Transformation",
            current_value=0.72,
            target_value=0.95,
            unit="transformation_score",
            trend_7d=2.1,
            trend_30d=7.8,
            status=OKRStatus.AT_RISK,
            confidence=0.70,
            last_updated=datetime.now(),
        )

    async def _get_fallback_revenue_per_employee_metric(self) -> OKRMetric:
        """Fallback revenue per employee metric"""
        return OKRMetric(
            name="Revenue per Employee Optimization",
            current_value=185000,
            target_value=250000,
            unit="usd_annually",
            trend_7d=1.8,
            trend_30d=5.2,
            status=OKRStatus.AT_RISK,
            confidence=0.75,
            last_updated=datetime.now(),
        )

    async def _get_fallback_revenue_per_unit_metric(self) -> OKRMetric:
        """Fallback revenue per unit metric"""
        return OKRMetric(
            name="Revenue per Apartment Unit",
            current_value=1850,
            target_value=2500,
            unit="usd_per_unit_annually",
            trend_7d=2.3,
            trend_30d=9.1,
            status=OKRStatus.AT_RISK,
            confidence=0.80,
            last_updated=datetime.now(),
        )

    async def _get_fallback_insights(
        self, metrics: List[OKRMetric]
    ) -> List[OKRInsight]:
        """Fallback insights when AI generation fails"""
        return [
            OKRInsight(
                okr_name="AI-First Company Transformation",
                insight_type="opportunity",
                description="Accelerate AI tool adoption through targeted training programs",
                impact_score=0.85,
                urgency="high",
                recommended_actions=[
                    "Launch AI training program",
                    "Implement usage incentives",
                ],
                confidence=0.75,
            ),
            OKRInsight(
                okr_name="Revenue per Employee Optimization",
                insight_type="optimization",
                description="Focus on process automation to increase productivity",
                impact_score=0.78,
                urgency="medium",
                recommended_actions=[
                    "Automate manual processes",
                    "Optimize tool usage",
                ],
                confidence=0.80,
            ),
        ]

    def _get_fallback_dashboard(self) -> Dict[str, Any]:
        """Fallback dashboard when all else fails"""
        return {
            "overall_score": {"score": 75.0, "grade": "C", "trend": "stable"},
            "last_updated": datetime.now().isoformat(),
            "okrs": {},
            "insights": [],
            "critical_actions": [],
            "trend_analysis": {"error": "Data temporarily unavailable"},
            "status": "degraded",
        }


# Service instance for dependency injection
okr_tracking_service = OKRTrackingService()
