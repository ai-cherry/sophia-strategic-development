#!/usr/bin/env python3
"""
Linear Project Health Monitoring Agent
AI-driven project health analysis and risk detection for Linear issues
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from backend.agents.core.base_agent import BaseAgent
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.mcp.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Project health status levels"""
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    CRITICAL = "critical"
    BLOCKED = "blocked"


class RiskType(Enum):
    """Types of project risks"""
    SCHEDULE_DELAY = "schedule_delay"
    SCOPE_CREEP = "scope_creep"
    RESOURCE_CONSTRAINT = "resource_constraint"
    TECHNICAL_DEBT = "technical_debt"
    DEPENDENCY_ISSUE = "dependency_issue"
    QUALITY_CONCERN = "quality_concern"


@dataclass
class LinearIssue:
    """Linear issue data structure"""
    issue_id: str
    title: str
    description: str
    status: str
    priority: str
    assignee: Optional[str]
    project_id: Optional[str]
    project_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    estimate: Optional[float]
    labels: List[str] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProjectRisk:
    """Project risk assessment"""
    risk_type: RiskType
    severity: str  # low, medium, high, critical
    description: str
    affected_issues: List[str]
    impact_assessment: str
    mitigation_strategies: List[str]
    confidence_score: float


@dataclass
class ProjectHealthMetrics:
    """Project health metrics"""
    total_issues: int
    completed_issues: int
    in_progress_issues: int
    blocked_issues: int
    overdue_issues: int
    completion_rate: float
    velocity_trend: str
    avg_cycle_time: float
    team_utilization: float
    quality_score: float


@dataclass
class ProjectHealthReport:
    """Comprehensive project health report"""
    project_id: str
    project_name: str
    health_status: HealthStatus
    health_score: float
    metrics: ProjectHealthMetrics
    risks: List[ProjectRisk]
    recommendations: List[str]
    key_insights: List[str]
    team_performance: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.now)


class LinearProjectHealthAgent(BaseAgent):
    """
    Linear Project Health Monitoring Agent
    
    Provides:
    - Real-time project health assessment
    - Risk detection and analysis
    - Team performance monitoring
    - Predictive project insights
    - Automated recommendations
    """
    
    def __init__(self):
        super().__init__()
        self.name = "linear_project_health"
        self.description = "AI-driven Linear project health monitoring and risk detection"
        
        # Service integrations
        self.cortex_service: Optional[SnowflakeCortexService] = None
        self.ai_memory: Optional[EnhancedAiMemoryMCPServer] = None
        
        # Health assessment thresholds
        self.health_thresholds = {
            "completion_rate_healthy": 0.8,
            "completion_rate_at_risk": 0.6,
            "overdue_threshold": 0.2,
            "velocity_decline_threshold": 0.3,
            "cycle_time_increase_threshold": 1.5
        }
        
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize Linear Project Health Agent"""
        if self.initialized:
            return
        
        try:
            self.cortex_service = SnowflakeCortexService()
            self.ai_memory = EnhancedAiMemoryMCPServer()
            
            await self.ai_memory.initialize()
            
            self.initialized = True
            logger.info("✅ Linear Project Health Agent initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Linear Project Health Agent: {e}")
            raise
    
    async def assess_project_health(
        self,
        project_id: str,
        project_name: str,
        issues: List[LinearIssue],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> ProjectHealthReport:
        """
        Assess comprehensive project health
        
        Args:
            project_id: Linear project ID
            project_name: Project name
            issues: List of project issues
            historical_data: Historical project data for trend analysis
            
        Returns:
            Comprehensive project health report
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Calculate basic metrics
            metrics = self._calculate_project_metrics(issues)
            
            # Assess risks
            risks = await self._assess_project_risks(issues, metrics, historical_data)
            
            # Calculate overall health score
            health_score, health_status = self._calculate_health_score(metrics, risks)
            
            # Generate insights and recommendations
            insights = await self._generate_project_insights(issues, metrics, risks)
            recommendations = await self._generate_recommendations(metrics, risks)
            
            # Analyze team performance
            team_performance = self._analyze_team_performance(issues)
            
            # Create health report
            report = ProjectHealthReport(
                project_id=project_id,
                project_name=project_name,
                health_status=health_status,
                health_score=health_score,
                metrics=metrics,
                risks=risks,
                recommendations=recommendations,
                key_insights=insights,
                team_performance=team_performance
            )
            
            # Store report in AI Memory
            await self._store_health_report_in_memory(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error assessing project health: {e}")
            raise
    
    async def monitor_project_trends(
        self,
        project_id: str,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Monitor project trends over time
        
        Args:
            project_id: Linear project ID
            time_period_days: Number of days to analyze
            
        Returns:
            Project trend analysis
        """
        try:
            # Get historical project data
            historical_reports = await self._get_historical_health_reports(
                project_id, time_period_days
            )
            
            if not historical_reports:
                return {
                    "project_id": project_id,
                    "period_days": time_period_days,
                    "message": "Insufficient historical data for trend analysis"
                }
            
            # Analyze trends
            trends = self._analyze_health_trends(historical_reports)
            
            # Generate trend insights
            trend_insights = await self._generate_trend_insights(trends)
            
            return {
                "project_id": project_id,
                "period_days": time_period_days,
                "trends": trends,
                "insights": trend_insights,
                "recommendations": self._generate_trend_recommendations(trends)
            }
            
        except Exception as e:
            logger.error(f"Error monitoring project trends: {e}")
            raise
    
    async def detect_project_anomalies(
        self,
        issues: List[LinearIssue],
        baseline_metrics: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in project behavior
        
        Args:
            issues: Current project issues
            baseline_metrics: Baseline metrics for comparison
            
        Returns:
            List of detected anomalies
        """
        try:
            anomalies = []
            current_metrics = self._calculate_project_metrics(issues)
            
            if not baseline_metrics:
                return anomalies
            
            # Check for velocity anomalies
            if current_metrics.completion_rate < baseline_metrics.get("completion_rate", 0) * 0.7:
                anomalies.append({
                    "type": "velocity_drop",
                    "severity": "high",
                    "description": f"Completion rate dropped to {current_metrics.completion_rate:.1%}",
                    "impact": "Project delivery at risk"
                })
            
            # Check for cycle time anomalies
            baseline_cycle_time = baseline_metrics.get("avg_cycle_time", 0)
            if baseline_cycle_time > 0 and current_metrics.avg_cycle_time > baseline_cycle_time * 1.5:
                anomalies.append({
                    "type": "cycle_time_increase",
                    "severity": "medium",
                    "description": f"Average cycle time increased to {current_metrics.avg_cycle_time:.1f} days",
                    "impact": "Slower delivery velocity"
                })
            
            # Check for overdue issue spike
            if current_metrics.overdue_issues > current_metrics.total_issues * 0.3:
                anomalies.append({
                    "type": "overdue_spike",
                    "severity": "critical",
                    "description": f"{current_metrics.overdue_issues} issues are overdue",
                    "impact": "Schedule adherence compromised"
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def _calculate_project_metrics(self, issues: List[LinearIssue]) -> ProjectHealthMetrics:
        """Calculate basic project metrics"""
        total_issues = len(issues)
        
        if total_issues == 0:
            return ProjectHealthMetrics(
                total_issues=0,
                completed_issues=0,
                in_progress_issues=0,
                blocked_issues=0,
                overdue_issues=0,
                completion_rate=0.0,
                velocity_trend="stable",
                avg_cycle_time=0.0,
                team_utilization=0.0,
                quality_score=0.0
            )
        
        # Count issues by status
        completed_issues = len([i for i in issues if i.status.lower() in ["done", "completed", "closed"]])
        in_progress_issues = len([i for i in issues if i.status.lower() in ["in progress", "in review"]])
        blocked_issues = len([i for i in issues if "blocked" in i.status.lower() or "blocked" in [l.lower() for l in i.labels]])
        
        # Count overdue issues
        now = datetime.now()
        overdue_issues = len([i for i in issues if i.due_date and i.due_date < now and i.status.lower() not in ["done", "completed", "closed"]])
        
        # Calculate completion rate
        completion_rate = completed_issues / total_issues if total_issues > 0 else 0
        
        # Calculate average cycle time (simplified)
        completed_with_times = [i for i in issues if i.status.lower() in ["done", "completed", "closed"] and i.created_at and i.updated_at]
        avg_cycle_time = 0.0
        if completed_with_times:
            cycle_times = [(i.updated_at - i.created_at).days for i in completed_with_times]
            avg_cycle_time = sum(cycle_times) / len(cycle_times)
        
        # Calculate team utilization (simplified)
        assignees = set(i.assignee for i in issues if i.assignee)
        team_utilization = min(in_progress_issues / len(assignees) if assignees else 0, 1.0)
        
        # Calculate quality score (based on issue descriptions and comments)
        quality_score = self._calculate_quality_score(issues)
        
        return ProjectHealthMetrics(
            total_issues=total_issues,
            completed_issues=completed_issues,
            in_progress_issues=in_progress_issues,
            blocked_issues=blocked_issues,
            overdue_issues=overdue_issues,
            completion_rate=completion_rate,
            velocity_trend="stable",  # Would be calculated from historical data
            avg_cycle_time=avg_cycle_time,
            team_utilization=team_utilization,
            quality_score=quality_score
        )
    
    async def _assess_project_risks(
        self,
        issues: List[LinearIssue],
        metrics: ProjectHealthMetrics,
        historical_data: Optional[Dict[str, Any]]
    ) -> List[ProjectRisk]:
        """Assess project risks"""
        risks = []
        
        # Schedule delay risk
        if metrics.overdue_issues > metrics.total_issues * 0.2:
            risks.append(ProjectRisk(
                risk_type=RiskType.SCHEDULE_DELAY,
                severity="high" if metrics.overdue_issues > metrics.total_issues * 0.3 else "medium",
                description=f"{metrics.overdue_issues} issues are overdue ({metrics.overdue_issues/metrics.total_issues:.1%} of total)",
                affected_issues=[i.issue_id for i in issues if i.due_date and i.due_date < datetime.now()],
                impact_assessment="Project delivery timeline at risk",
                mitigation_strategies=[
                    "Prioritize overdue issues",
                    "Reassess scope and deadlines",
                    "Add resources to critical path items"
                ],
                confidence_score=0.9
            ))
        
        # Resource constraint risk
        if metrics.team_utilization > 0.9:
            risks.append(ProjectRisk(
                risk_type=RiskType.RESOURCE_CONSTRAINT,
                severity="medium",
                description=f"Team utilization at {metrics.team_utilization:.1%}",
                affected_issues=[i.issue_id for i in issues if i.status.lower() in ["in progress", "todo"]],
                impact_assessment="Team burnout and quality degradation risk",
                mitigation_strategies=[
                    "Balance workload across team",
                    "Consider additional resources",
                    "Prioritize critical features"
                ],
                confidence_score=0.8
            ))
        
        # Quality concern risk
        if metrics.quality_score < 0.6:
            risks.append(ProjectRisk(
                risk_type=RiskType.QUALITY_CONCERN,
                severity="medium",
                description=f"Quality score below threshold ({metrics.quality_score:.1f})",
                affected_issues=[i.issue_id for i in issues if len(i.description) < 50],
                impact_assessment="Technical debt and maintenance burden increase",
                mitigation_strategies=[
                    "Improve issue documentation",
                    "Implement code review processes",
                    "Add quality gates"
                ],
                confidence_score=0.7
            ))
        
        # AI-enhanced risk assessment
        ai_risks = await self._ai_enhanced_risk_assessment(issues, metrics)
        risks.extend(ai_risks)
        
        return risks
    
    async def _ai_enhanced_risk_assessment(
        self,
        issues: List[LinearIssue],
        metrics: ProjectHealthMetrics
    ) -> List[ProjectRisk]:
        """Use AI to assess additional project risks"""
        try:
            # Prepare issue summaries for AI analysis
            issue_summaries = []
            for issue in issues[:10]:  # Analyze top 10 issues
                summary = f"Issue: {issue.title}, Status: {issue.status}, Priority: {issue.priority}"
                if issue.description:
                    summary += f", Description: {issue.description[:200]}"
                issue_summaries.append(summary)
            
            async with self.cortex_service as cortex:
                risk_prompt = f"""
                Analyze these Linear project issues for potential risks:
                
                Project Metrics:
                - Total Issues: {metrics.total_issues}
                - Completion Rate: {metrics.completion_rate:.1%}
                - Overdue Issues: {metrics.overdue_issues}
                - Blocked Issues: {metrics.blocked_issues}
                
                Recent Issues:
                {chr(10).join(issue_summaries)}
                
                Identify potential risks in these categories:
                1. Technical debt accumulation
                2. Scope creep indicators
                3. Communication gaps
                4. Dependency issues
                
                Return findings as JSON with risk_type, severity, and description.
                """
                
                risk_analysis = await cortex.complete_text_with_cortex(
                    prompt=risk_prompt,
                    max_tokens=500
                )
                
                # Parse AI risk assessment
                try:
                    ai_risks_data = json.loads(risk_analysis)
                    ai_risks = []
                    
                    for risk_data in ai_risks_data.get("risks", []):
                        risk_type_str = risk_data.get("risk_type", "technical_debt")
                        risk_type = getattr(RiskType, risk_type_str.upper(), RiskType.TECHNICAL_DEBT)
                        
                        ai_risks.append(ProjectRisk(
                            risk_type=risk_type,
                            severity=risk_data.get("severity", "medium"),
                            description=risk_data.get("description", "AI-identified risk"),
                            affected_issues=[],
                            impact_assessment=risk_data.get("impact", "Potential project impact"),
                            mitigation_strategies=risk_data.get("mitigation", ["Monitor closely"]),
                            confidence_score=0.6
                        ))
                    
                    return ai_risks
                    
                except json.JSONDecodeError:
                    logger.warning("Failed to parse AI risk assessment")
                    return []
                
        except Exception as e:
            logger.error(f"Error in AI risk assessment: {e}")
            return []
    
    def _calculate_health_score(
        self,
        metrics: ProjectHealthMetrics,
        risks: List[ProjectRisk]
    ) -> Tuple[float, HealthStatus]:
        """Calculate overall project health score and status"""
        score = 1.0
        
        # Factor in completion rate
        score *= metrics.completion_rate
        
        # Penalize for overdue issues
        if metrics.total_issues > 0:
            overdue_ratio = metrics.overdue_issues / metrics.total_issues
            score *= (1 - overdue_ratio * 0.5)
        
        # Penalize for blocked issues
        if metrics.total_issues > 0:
            blocked_ratio = metrics.blocked_issues / metrics.total_issues
            score *= (1 - blocked_ratio * 0.3)
        
        # Factor in quality score
        score *= (0.7 + 0.3 * metrics.quality_score)
        
        # Penalize for high-severity risks
        high_severity_risks = len([r for r in risks if r.severity in ["high", "critical"]])
        score *= (1 - high_severity_risks * 0.1)
        
        # Determine health status
        if score >= 0.8:
            status = HealthStatus.HEALTHY
        elif score >= 0.6:
            status = HealthStatus.AT_RISK
        elif score >= 0.4:
            status = HealthStatus.CRITICAL
        else:
            status = HealthStatus.BLOCKED
        
        return max(score, 0.0), status
    
    async def _generate_project_insights(
        self,
        issues: List[LinearIssue],
        metrics: ProjectHealthMetrics,
        risks: List[ProjectRisk]
    ) -> List[str]:
        """Generate AI-powered project insights"""
        insights = []
        
        # Basic insights from metrics
        if metrics.completion_rate > 0.8:
            insights.append(f"Strong project momentum with {metrics.completion_rate:.1%} completion rate")
        elif metrics.completion_rate < 0.5:
            insights.append(f"Project velocity concerns with only {metrics.completion_rate:.1%} completion rate")
        
        if metrics.blocked_issues > 0:
            insights.append(f"{metrics.blocked_issues} blocked issues may impact delivery timeline")
        
        # Risk-based insights
        high_priority_risks = [r for r in risks if r.severity in ["high", "critical"]]
        if high_priority_risks:
            insights.append(f"{len(high_priority_risks)} critical risks require immediate attention")
        
        # AI-generated insights
        try:
            async with self.cortex_service as cortex:
                insight_prompt = f"""
                Generate 2-3 key insights for this project:
                
                Metrics:
                - Completion Rate: {metrics.completion_rate:.1%}
                - Overdue Issues: {metrics.overdue_issues}
                - Team Utilization: {metrics.team_utilization:.1%}
                - Quality Score: {metrics.quality_score:.1f}
                
                Risks: {len(risks)} identified
                
                Provide actionable insights for project management.
                """
                
                ai_insights = await cortex.complete_text_with_cortex(
                    prompt=insight_prompt,
                    max_tokens=200
                )
                
                # Parse insights from AI response
                ai_insight_lines = [line.strip() for line in ai_insights.split('\n') if line.strip()]
                insights.extend(ai_insight_lines[:3])
                
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
        
        return insights[:5]  # Limit to top 5 insights
    
    async def _generate_recommendations(
        self,
        metrics: ProjectHealthMetrics,
        risks: List[ProjectRisk]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Completion rate recommendations
        if metrics.completion_rate < 0.6:
            recommendations.append("Focus on completing in-progress issues before starting new work")
        
        # Overdue issue recommendations
        if metrics.overdue_issues > 0:
            recommendations.append("Prioritize overdue issues and reassess their scope and deadlines")
        
        # Team utilization recommendations
        if metrics.team_utilization > 0.9:
            recommendations.append("Consider redistributing workload to prevent team burnout")
        elif metrics.team_utilization < 0.5:
            recommendations.append("Team has capacity for additional work or faster delivery")
        
        # Risk-based recommendations
        for risk in risks:
            if risk.severity in ["high", "critical"]:
                recommendations.extend(risk.mitigation_strategies[:2])
        
        return list(set(recommendations))[:5]  # Remove duplicates and limit
    
    def _analyze_team_performance(self, issues: List[LinearIssue]) -> Dict[str, Any]:
        """Analyze team performance metrics"""
        assignee_stats = {}
        
        for issue in issues:
            if not issue.assignee:
                continue
            
            if issue.assignee not in assignee_stats:
                assignee_stats[issue.assignee] = {
                    "total_issues": 0,
                    "completed_issues": 0,
                    "in_progress_issues": 0,
                    "overdue_issues": 0
                }
            
            stats = assignee_stats[issue.assignee]
            stats["total_issues"] += 1
            
            if issue.status.lower() in ["done", "completed", "closed"]:
                stats["completed_issues"] += 1
            elif issue.status.lower() in ["in progress", "in review"]:
                stats["in_progress_issues"] += 1
            
            if issue.due_date and issue.due_date < datetime.now() and issue.status.lower() not in ["done", "completed", "closed"]:
                stats["overdue_issues"] += 1
        
        # Calculate completion rates
        for assignee, stats in assignee_stats.items():
            if stats["total_issues"] > 0:
                stats["completion_rate"] = stats["completed_issues"] / stats["total_issues"]
            else:
                stats["completion_rate"] = 0.0
        
        return {
            "team_members": len(assignee_stats),
            "individual_performance": assignee_stats,
            "top_performers": sorted(
                assignee_stats.items(),
                key=lambda x: x[1]["completion_rate"],
                reverse=True
            )[:3]
        }
    
    def _calculate_quality_score(self, issues: List[LinearIssue]) -> float:
        """Calculate quality score based on issue documentation"""
        if not issues:
            return 0.0
        
        quality_factors = []
        
        for issue in issues:
            score = 0.0
            
            # Description quality
            if issue.description and len(issue.description) > 50:
                score += 0.4
            elif issue.description and len(issue.description) > 20:
                score += 0.2
            
            # Title quality
            if issue.title and len(issue.title) > 10:
                score += 0.2
            
            # Labels usage
            if issue.labels:
                score += 0.2
            
            # Priority assignment
            if issue.priority:
                score += 0.1
            
            # Estimate provided
            if issue.estimate:
                score += 0.1
            
            quality_factors.append(min(score, 1.0))
        
        return sum(quality_factors) / len(quality_factors)
    
    async def _get_historical_health_reports(
        self,
        project_id: str,
        days: int
    ) -> List[ProjectHealthReport]:
        """Get historical health reports (placeholder implementation)"""
        # In production, this would query stored health reports
        return []
    
    def _analyze_health_trends(self, reports: List[ProjectHealthReport]) -> Dict[str, Any]:
        """Analyze health trends from historical reports"""
        if len(reports) < 2:
            return {"message": "Insufficient data for trend analysis"}
        
        # Sort reports by date
        sorted_reports = sorted(reports, key=lambda r: r.generated_at)
        
        # Calculate trends
        health_scores = [r.health_score for r in sorted_reports]
        completion_rates = [r.metrics.completion_rate for r in sorted_reports]
        
        return {
            "health_score_trend": "improving" if health_scores[-1] > health_scores[0] else "declining",
            "completion_rate_trend": "improving" if completion_rates[-1] > completion_rates[0] else "declining",
            "average_health_score": sum(health_scores) / len(health_scores),
            "health_score_variance": max(health_scores) - min(health_scores)
        }
    
    async def _generate_trend_insights(self, trends: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis"""
        insights = []
        
        if trends.get("health_score_trend") == "improving":
            insights.append("Project health is trending positively")
        elif trends.get("health_score_trend") == "declining":
            insights.append("Project health shows concerning decline")
        
        if trends.get("completion_rate_trend") == "improving":
            insights.append("Team velocity is accelerating")
        
        return insights
    
    def _generate_trend_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on trends"""
        recommendations = []
        
        if trends.get("health_score_trend") == "declining":
            recommendations.append("Investigate root causes of health decline")
            recommendations.append("Implement corrective measures immediately")
        
        if trends.get("health_score_variance", 0) > 0.3:
            recommendations.append("Project health is volatile - establish more consistent processes")
        
        return recommendations
    
    async def _store_health_report_in_memory(self, report: ProjectHealthReport) -> None:
        """Store health report in AI Memory"""
        try:
            if not self.ai_memory:
                return
            
            memory_content = f"""
            Linear Project Health Report
            Project: {report.project_name} ({report.project_id})
            Health Status: {report.health_status.value}
            Health Score: {report.health_score:.2f}
            
            Metrics:
            - Total Issues: {report.metrics.total_issues}
            - Completion Rate: {report.metrics.completion_rate:.1%}
            - Overdue Issues: {report.metrics.overdue_issues}
            - Team Utilization: {report.metrics.team_utilization:.1%}
            
            Risks Identified: {len(report.risks)}
            Key Insights: {len(report.key_insights)}
            Recommendations: {len(report.recommendations)}
            """
            
            await self.ai_memory.store_memory(
                content=memory_content,
                category="linear_project_health",
                tags=["linear", "project", "health", "monitoring"],
                metadata={
                    "project_id": report.project_id,
                    "project_name": report.project_name,
                    "health_status": report.health_status.value,
                    "health_score": report.health_score,
                    "total_issues": report.metrics.total_issues,
                    "completion_rate": report.metrics.completion_rate
                },
                importance_score=min(1.0, report.health_score + 0.2)
            )
            
        except Exception as e:
            logger.error(f"Error storing health report in AI Memory: {e}")
