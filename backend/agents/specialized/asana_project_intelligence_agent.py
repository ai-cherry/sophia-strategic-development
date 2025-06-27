from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from backend.agents.core.langgraph_agent_base import LangGraphAgentBase, AgentCapability
from backend.services.smart_ai_service import LLMRequest, TaskType, smart_ai_service
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.services.comprehensive_memory_service import ComprehensiveMemoryService
from backend.services.smart_ai_service import SmartAIService

logger = logging.getLogger(__name__)

class ProjectHealthStatus(Enum):
    """Project health status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MemoryCategory:
    """Memory categories for AI storage"""
    ASANA_PROJECT_ANALYSIS = "asana_project_analysis"
    ASANA_TEAM_INSIGHTS = "asana_team_insights"
    ASANA_RISK_ASSESSMENT = "asana_risk_assessment"

@dataclass
class AsanaProjectMetrics:
    """Comprehensive project metrics from Asana"""
    project_gid: str
    project_name: str
    completion_percentage: float
    task_count: int
    completed_task_count: int
    overdue_task_count: int
    team_name: Optional[str]
    owner_name: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    modified_at: datetime
    health_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    ai_insights: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TeamProductivityMetrics:
    """Team productivity analysis"""
    team_name: str
    total_projects: int
    active_projects: int
    completed_projects: int
    average_completion_rate: float
    overdue_tasks_ratio: float
    team_velocity: float
    member_count: int
    productivity_score: float = 0.0

@dataclass
class ProjectRiskAssessment:
    """Comprehensive project risk assessment"""
    project_gid: str
    project_name: str
    overall_risk: RiskLevel
    schedule_risk: RiskLevel
    resource_risk: RiskLevel
    scope_risk: RiskLevel
    quality_risk: RiskLevel
    risk_factors: List[str] = field(default_factory=list)
    mitigation_suggestions: List[str] = field(default_factory=list)
    predicted_completion_date: Optional[datetime] = None

class AsanaProjectIntelligenceAgent(LangGraphAgentBase):
    """Advanced Asana project intelligence and analytics agent"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cortex_service = None
        self.ai_memory_service = None
        self.smart_ai_service = None
        
    async def initialize(self) -> None:
        """Initialize the Asana intelligence agent"""
        try:
            await super().initialize()
            
            # Initialize services
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            
            self.ai_memory_service = EnhancedAiMemoryMCPServer()
            await self.ai_memory_service.initialize()
            
            self.smart_ai_service = SmartAIService()
            await self.smart_ai_service.initialize()
            
            logger.info("✅ Asana Project Intelligence Agent initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Asana intelligence agent: {e}")
            raise

    async def get_project_metrics(self, project_gid: Optional[str] = None) -> List[AsanaProjectMetrics]:
        """Get comprehensive project metrics from Asana data"""
        try:
            # Build query based on whether specific project is requested
            where_clause = f"WHERE PROJECT_GID = '{project_gid}'" if project_gid else "WHERE IS_ARCHIVED = FALSE"
            
            query = f"""
            WITH project_task_summary AS (
                SELECT 
                    p.PROJECT_GID,
                    COUNT(t.TASK_GID) as total_tasks,
                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,
                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,
                    AVG(CASE WHEN t.AI_URGENCY_SCORE IS NOT NULL THEN t.AI_URGENCY_SCORE ELSE 0.5 END) as avg_urgency
                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p
                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID
                GROUP BY p.PROJECT_GID
            )
            SELECT 
                p.PROJECT_GID,
                p.PROJECT_NAME,
                p.COMPLETION_PERCENTAGE,
                p.TEAM_NAME,
                p.OWNER_NAME,
                p.DUE_DATE,
                p.CREATED_AT,
                p.MODIFIED_AT,
                p.AI_HEALTH_SCORE,
                p.AI_RISK_ASSESSMENT,
                pts.total_tasks,
                pts.completed_tasks,
                pts.overdue_tasks,
                pts.avg_urgency,
                p.AI_MEMORY_METADATA
            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p
            LEFT JOIN project_task_summary pts ON p.PROJECT_GID = pts.PROJECT_GID
            {where_clause}
            ORDER BY p.MODIFIED_AT DESC
            """
            
            result = await self.cortex_service.execute_query(query)
            
            metrics = []
            for _, row in result.iterrows():
                # Calculate health score
                health_score = self._calculate_project_health_score(row)
                
                # Determine risk level
                risk_level = self._assess_project_risk_level(row)
                
                # Extract AI insights
                ai_metadata = json.loads(row.get('AI_MEMORY_METADATA', '{}')) if row.get('AI_MEMORY_METADATA') else {}
                
                metrics.append(AsanaProjectMetrics(
                    project_gid=row['PROJECT_GID'],
                    project_name=row['PROJECT_NAME'],
                    completion_percentage=row.get('COMPLETION_PERCENTAGE', 0.0),
                    task_count=row.get('TOTAL_TASKS', 0),
                    completed_task_count=row.get('COMPLETED_TASKS', 0),
                    overdue_task_count=row.get('OVERDUE_TASKS', 0),
                    team_name=row.get('TEAM_NAME'),
                    owner_name=row.get('OWNER_NAME'),
                    due_date=row.get('DUE_DATE'),
                    created_at=row['CREATED_AT'],
                    modified_at=row['MODIFIED_AT'],
                    health_score=health_score,
                    risk_level=risk_level,
                    ai_insights=ai_metadata
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get project metrics: {e}")
            return []

    def _calculate_project_health_score(self, project_data: Dict[str, Any]) -> float:
        """Calculate comprehensive project health score"""
        try:
            score = 0.0
            
            # Completion percentage (40% weight)
            completion = project_data.get('COMPLETION_PERCENTAGE', 0.0)
            score += (completion / 100.0) * 0.4
            
            # Task completion ratio (30% weight)
            total_tasks = project_data.get('TOTAL_TASKS', 0)
            completed_tasks = project_data.get('COMPLETED_TASKS', 0)
            if total_tasks > 0:
                task_completion_ratio = completed_tasks / total_tasks
                score += task_completion_ratio * 0.3
            
            # Overdue tasks penalty (20% weight)
            overdue_tasks = project_data.get('OVERDUE_TASKS', 0)
            if total_tasks > 0:
                overdue_ratio = overdue_tasks / total_tasks
                score += (1.0 - overdue_ratio) * 0.2
            else:
                score += 0.2  # No overdue tasks if no tasks
            
            # Timeline adherence (10% weight)
            due_date = project_data.get('DUE_DATE')
            if due_date:
                days_to_due = (due_date - datetime.now()).days
                if days_to_due > 0:
                    # Project is on time
                    score += 0.1
                elif days_to_due >= -7:
                    # Recently overdue, partial credit
                    score += 0.05
                # Significantly overdue gets no points
            else:
                score += 0.1  # No due date pressure
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating health score: {e}")
            return 0.5

    def _assess_project_risk_level(self, project_data: Dict[str, Any]) -> RiskLevel:
        """Assess project risk level based on multiple factors"""
        try:
            risk_score = 0.0
            
            # Overdue tasks
            total_tasks = project_data.get('TOTAL_TASKS', 0)
            overdue_tasks = project_data.get('OVERDUE_TASKS', 0)
            if total_tasks > 0:
                overdue_ratio = overdue_tasks / total_tasks
                risk_score += overdue_ratio * 0.4
            
            # Completion vs timeline
            completion = project_data.get('COMPLETION_PERCENTAGE', 0.0)
            due_date = project_data.get('DUE_DATE')
            if due_date:
                days_to_due = (due_date - datetime.now()).days
                if days_to_due > 0:
                    expected_completion = 100.0 - (days_to_due / 30.0) * 20.0  # Rough estimate
                    if completion < expected_completion:
                        risk_score += 0.3
                elif days_to_due <= 0:
                    risk_score += 0.5  # Already overdue
            
            # Average urgency
            avg_urgency = project_data.get('AVG_URGENCY', 0.5)
            risk_score += avg_urgency * 0.3
            
            # Determine risk level
            if risk_score >= 0.8:
                return RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                return RiskLevel.HIGH
            elif risk_score >= 0.4:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
                
        except Exception as e:
            logger.error(f"❌ Error assessing risk level: {e}")
            return RiskLevel.MEDIUM

    async def analyze_team_productivity(self, team_name: Optional[str] = None) -> List[TeamProductivityMetrics]:
        """Analyze team productivity across projects"""
        try:
            where_clause = f"WHERE p.TEAM_NAME = '{team_name}'" if team_name else ""
            
            query = f"""
            WITH team_metrics AS (
                SELECT 
                    p.TEAM_NAME,
                    COUNT(DISTINCT p.PROJECT_GID) as total_projects,
                    COUNT(DISTINCT CASE WHEN p.IS_ARCHIVED = FALSE THEN p.PROJECT_GID END) as active_projects,
                    COUNT(DISTINCT CASE WHEN p.COMPLETION_PERCENTAGE = 100 THEN p.PROJECT_GID END) as completed_projects,
                    AVG(p.COMPLETION_PERCENTAGE) as avg_completion_rate,
                    COUNT(DISTINCT u.USER_GID) as member_count
                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p
                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID
                LEFT JOIN STG_TRANSFORMED.STG_ASANA_USERS u ON p.TEAM_NAME = u.DEPARTMENT
                {where_clause}
                GROUP BY p.TEAM_NAME
            ),
            task_metrics AS (
                SELECT 
                    p.TEAM_NAME,
                    COUNT(t.TASK_GID) as total_tasks,
                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,
                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,
                    COUNT(CASE WHEN t.COMPLETED_AT >= CURRENT_DATE - 30 THEN 1 END) as tasks_completed_last_30d
                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p
                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID
                {where_clause}
                GROUP BY p.TEAM_NAME
            )
            SELECT 
                tm.TEAM_NAME,
                tm.total_projects,
                tm.active_projects,
                tm.completed_projects,
                tm.avg_completion_rate,
                tm.member_count,
                COALESCE(tkm.total_tasks, 0) as total_tasks,
                COALESCE(tkm.overdue_tasks, 0) as overdue_tasks,
                COALESCE(tkm.tasks_completed_last_30d, 0) as recent_completions
            FROM team_metrics tm
            LEFT JOIN task_metrics tkm ON tm.TEAM_NAME = tkm.TEAM_NAME
            WHERE tm.TEAM_NAME IS NOT NULL
            ORDER BY tm.avg_completion_rate DESC
            """
            
            result = await self.cortex_service.execute_query(query)
            
            team_metrics = []
            for _, row in result.iterrows():
                # Calculate productivity metrics
                total_tasks = row.get('TOTAL_TASKS', 0)
                overdue_tasks = row.get('OVERDUE_TASKS', 0)
                overdue_ratio = (overdue_tasks / total_tasks) if total_tasks > 0 else 0.0
                
                # Team velocity (tasks completed per member per month)
                member_count = row.get('MEMBER_COUNT', 1)
                recent_completions = row.get('RECENT_COMPLETIONS', 0)
                velocity = recent_completions / member_count if member_count > 0 else 0.0
                
                # Overall productivity score
                productivity_score = self._calculate_team_productivity_score(row, overdue_ratio, velocity)
                
                team_metrics.append(TeamProductivityMetrics(
                    team_name=row['TEAM_NAME'],
                    total_projects=row.get('TOTAL_PROJECTS', 0),
                    active_projects=row.get('ACTIVE_PROJECTS', 0),
                    completed_projects=row.get('COMPLETED_PROJECTS', 0),
                    average_completion_rate=row.get('AVG_COMPLETION_RATE', 0.0),
                    overdue_tasks_ratio=overdue_ratio,
                    team_velocity=velocity,
                    member_count=member_count,
                    productivity_score=productivity_score
                ))
            
            return team_metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze team productivity: {e}")
            return []

    def _calculate_team_productivity_score(self, team_data: Dict[str, Any], overdue_ratio: float, velocity: float) -> float:
        """Calculate team productivity score"""
        try:
            score = 0.0
            
            # Completion rate (40% weight)
            completion_rate = team_data.get('AVG_COMPLETION_RATE', 0.0)
            score += (completion_rate / 100.0) * 0.4
            
            # Overdue tasks penalty (30% weight)
            score += (1.0 - overdue_ratio) * 0.3
            
            # Team velocity (20% weight)
            # Normalize velocity (assume 5 tasks per person per month is excellent)
            normalized_velocity = min(1.0, velocity / 5.0)
            score += normalized_velocity * 0.2
            
            # Project completion ratio (10% weight)
            total_projects = team_data.get('TOTAL_PROJECTS', 0)
            completed_projects = team_data.get('COMPLETED_PROJECTS', 0)
            if total_projects > 0:
                completion_ratio = completed_projects / total_projects
                score += completion_ratio * 0.1
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating team productivity score: {e}")
            return 0.5

    async def perform_risk_assessment(self, project_gid: Optional[str] = None) -> List[ProjectRiskAssessment]:
        """Perform comprehensive risk assessment for projects"""
        try:
            projects = await self.get_project_metrics(project_gid)
            risk_assessments = []
            
            for project in projects:
                # Get detailed task data for risk analysis
                task_query = f"""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,
                    COUNT(CASE WHEN ASSIGNEE_GID IS NULL THEN 1 END) as unassigned_tasks,
                    COUNT(CASE WHEN DEPENDENCY_COUNT > 0 THEN 1 END) as dependent_tasks,
                    AVG(AI_URGENCY_SCORE) as avg_urgency,
                    COUNT(CASE WHEN ESTIMATED_HOURS IS NULL THEN 1 END) as unestimated_tasks
                FROM STG_TRANSFORMED.STG_ASANA_TASKS
                WHERE PROJECT_GID = '{project.project_gid}'
                """
                
                task_result = await self.cortex_service.execute_query(task_query)
                task_data = task_result.iloc[0] if not task_result.empty else {}
                
                # Assess different risk dimensions
                schedule_risk = self._assess_schedule_risk(project, task_data)
                resource_risk = self._assess_resource_risk(project, task_data)
                scope_risk = self._assess_scope_risk(project, task_data)
                quality_risk = self._assess_quality_risk(project, task_data)
                
                # Determine overall risk
                risk_scores = [schedule_risk, resource_risk, scope_risk, quality_risk]
                overall_risk_score = max(risk_scores)
                
                overall_risk = RiskLevel.LOW
                if overall_risk_score >= 0.8:
                    overall_risk = RiskLevel.CRITICAL
                elif overall_risk_score >= 0.6:
                    overall_risk = RiskLevel.HIGH
                elif overall_risk_score >= 0.4:
                    overall_risk = RiskLevel.MEDIUM
                
                # Generate risk factors and mitigation suggestions
                risk_factors, mitigation_suggestions = await self._generate_risk_insights(
                    project, task_data, schedule_risk, resource_risk, scope_risk, quality_risk
                )
                
                # Predict completion date
                predicted_completion = self._predict_completion_date(project, task_data)
                
                risk_assessments.append(ProjectRiskAssessment(
                    project_gid=project.project_gid,
                    project_name=project.project_name,
                    overall_risk=overall_risk,
                    schedule_risk=self._score_to_risk_level(schedule_risk),
                    resource_risk=self._score_to_risk_level(resource_risk),
                    scope_risk=self._score_to_risk_level(scope_risk),
                    quality_risk=self._score_to_risk_level(quality_risk),
                    risk_factors=risk_factors,
                    mitigation_suggestions=mitigation_suggestions,
                    predicted_completion_date=predicted_completion
                ))
            
            return risk_assessments
            
        except Exception as e:
            logger.error(f"❌ Failed to perform risk assessment: {e}")
            return []

    def _assess_schedule_risk(self, project: AsanaProjectMetrics, task_data: Dict[str, Any]) -> float:
        """Assess schedule-related risks"""
        risk_score = 0.0
        
        # Overdue tasks
        total_tasks = task_data.get('TOTAL_TASKS', 0)
        overdue_tasks = task_data.get('OVERDUE_TASKS', 0)
        if total_tasks > 0:
            risk_score += (overdue_tasks / total_tasks) * 0.5
        
        # Project timeline
        if project.due_date:
            days_to_due = (project.due_date - datetime.now()).days
            if days_to_due < 0:
                risk_score += 0.4  # Already overdue
            elif days_to_due < 7:
                risk_score += 0.3  # Due very soon
            elif days_to_due < 30:
                risk_score += 0.2  # Due soon
        
        # Completion vs time elapsed
        if project.due_date and project.created_at:
            total_duration = (project.due_date - project.created_at).days
            elapsed_duration = (datetime.now() - project.created_at).days
            if total_duration > 0:
                expected_completion = (elapsed_duration / total_duration) * 100
                if project.completion_percentage < expected_completion:
                    risk_score += 0.1
        
        return min(1.0, risk_score)

    def _assess_resource_risk(self, project: AsanaProjectMetrics, task_data: Dict[str, Any]) -> float:
        """Assess resource-related risks"""
        risk_score = 0.0
        
        # Unassigned tasks
        total_tasks = task_data.get('TOTAL_TASKS', 0)
        unassigned_tasks = task_data.get('UNASSIGNED_TASKS', 0)
        if total_tasks > 0:
            risk_score += (unassigned_tasks / total_tasks) * 0.6
        
        # High urgency tasks
        avg_urgency = task_data.get('AVG_URGENCY', 0.5)
        if avg_urgency > 0.7:
            risk_score += 0.4
        
        return min(1.0, risk_score)

    def _assess_scope_risk(self, project: AsanaProjectMetrics, task_data: Dict[str, Any]) -> float:
        """Assess scope-related risks"""
        risk_score = 0.0
        
        # Unestimated tasks
        total_tasks = task_data.get('TOTAL_TASKS', 0)
        unestimated_tasks = task_data.get('UNESTIMATED_TASKS', 0)
        if total_tasks > 0:
            risk_score += (unestimated_tasks / total_tasks) * 0.5
        
        # High number of dependent tasks
        dependent_tasks = task_data.get('DEPENDENT_TASKS', 0)
        if total_tasks > 0:
            dependency_ratio = dependent_tasks / total_tasks
            if dependency_ratio > 0.5:
                risk_score += 0.3
        
        return min(1.0, risk_score)

    def _assess_quality_risk(self, project: AsanaProjectMetrics, task_data: Dict[str, Any]) -> float:
        """Assess quality-related risks"""
        risk_score = 0.0
        
        # High urgency indicates potential quality pressure
        avg_urgency = task_data.get('AVG_URGENCY', 0.5)
        if avg_urgency > 0.8:
            risk_score += 0.4
        
        # Rapid completion might indicate quality shortcuts
        if project.completion_percentage > 80:
            days_since_start = (datetime.now() - project.created_at).days
            if days_since_start < 7:  # Very rapid completion
                risk_score += 0.2
        
        return min(1.0, risk_score)

    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    async def _generate_risk_insights(
        self, 
        project: AsanaProjectMetrics, 
        task_data: Dict[str, Any], 
        schedule_risk: float,
        resource_risk: float, 
        scope_risk: float, 
        quality_risk: float
    ) -> Tuple[List[str], List[str]]:
        """Generate AI-powered risk insights and mitigation suggestions"""
        try:
            # Prepare context for AI analysis
            context = f"""
            Project: {project.project_name}
            Completion: {project.completion_percentage}%
            Total Tasks: {task_data.get('TOTAL_TASKS', 0)}
            Overdue Tasks: {task_data.get('OVERDUE_TASKS', 0)}
            Unassigned Tasks: {task_data.get('UNASSIGNED_TASKS', 0)}
            Schedule Risk: {schedule_risk:.2f}
            Resource Risk: {resource_risk:.2f}
            Scope Risk: {scope_risk:.2f}
            Quality Risk: {quality_risk:.2f}
            """
            
            # Generate insights using Smart AI Service
            insights_prompt = f"""
            Analyze this project data and identify the top 3 risk factors and 3 mitigation strategies:
            
            {context}
            
            Provide:
            1. Risk factors (specific, actionable insights)
            2. Mitigation suggestions (concrete next steps)
            
            Format as JSON with 'risk_factors' and 'mitigation_suggestions' arrays.
            """
            
            ai_response = await self.smart_ai_service.generate_text(
                prompt=insights_prompt,
                model_tier="tier_2",
                max_tokens=500
            )
            
            # Parse AI response
            try:
                insights = json.loads(ai_response)
                risk_factors = insights.get('risk_factors', [])
                mitigation_suggestions = insights.get('mitigation_suggestions', [])
            except json.JSONDecodeError:
                # Fallback to rule-based insights
                risk_factors, mitigation_suggestions = self._generate_fallback_insights(
                    project, task_data, schedule_risk, resource_risk, scope_risk, quality_risk
                )
            
            return risk_factors, mitigation_suggestions
            
        except Exception as e:
            logger.error(f"❌ Error generating risk insights: {e}")
            return self._generate_fallback_insights(
                project, task_data, schedule_risk, resource_risk, scope_risk, quality_risk
            )

    def _generate_fallback_insights(
        self, 
        project: AsanaProjectMetrics, 
        task_data: Dict[str, Any],
        schedule_risk: float, 
        resource_risk: float, 
        scope_risk: float, 
        quality_risk: float
    ) -> Tuple[List[str], List[str]]:
        """Generate fallback insights using rule-based logic"""
        risk_factors = []
        mitigation_suggestions = []
        
        # Schedule risks
        if schedule_risk > 0.6:
            risk_factors.append("Project timeline is at risk due to overdue tasks")
            mitigation_suggestions.append("Prioritize overdue tasks and consider deadline extension")
        
        # Resource risks
        if resource_risk > 0.6:
            unassigned_ratio = task_data.get('UNASSIGNED_TASKS', 0) / max(task_data.get('TOTAL_TASKS', 1), 1)
            if unassigned_ratio > 0.3:
                risk_factors.append(f"{unassigned_ratio:.0%} of tasks are unassigned")
                mitigation_suggestions.append("Assign owners to unassigned tasks immediately")
        
        # Scope risks
        if scope_risk > 0.6:
            risk_factors.append("Project scope may be unclear due to unestimated tasks")
            mitigation_suggestions.append("Conduct estimation session for remaining tasks")
        
        return risk_factors, mitigation_suggestions

    def _predict_completion_date(self, project: AsanaProjectMetrics, task_data: Dict[str, Any]) -> Optional[datetime]:
        """Predict project completion date based on current progress"""
        try:
            if project.completion_percentage >= 100:
                return datetime.now()
            
            # Calculate velocity based on completed tasks
            days_since_start = (datetime.now() - project.created_at).days
            if days_since_start <= 0:
                return None
            
            completed_tasks = project.completed_task_count
            velocity = completed_tasks / days_since_start  # tasks per day
            
            if velocity <= 0:
                return None
            
            remaining_tasks = project.task_count - completed_tasks
            estimated_days_remaining = remaining_tasks / velocity
            
            # Add buffer for risk factors
            risk_buffer = 1.0
            total_tasks = task_data.get('TOTAL_TASKS', 0)
            if total_tasks > 0:
                overdue_ratio = task_data.get('OVERDUE_TASKS', 0) / total_tasks
                unassigned_ratio = task_data.get('UNASSIGNED_TASKS', 0) / total_tasks
                risk_buffer += (overdue_ratio + unassigned_ratio) * 0.5
            
            adjusted_days = estimated_days_remaining * risk_buffer
            predicted_date = datetime.now() + timedelta(days=adjusted_days)
            
            return predicted_date
            
        except Exception as e:
            logger.error(f"❌ Error predicting completion date: {e}")
            return None

    async def generate_project_intelligence_report(self, project_gid: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive project intelligence report"""
        try:
            logger.info(f"🧠 Generating project intelligence report for {project_gid or 'all projects'}")
            
            # Get project metrics
            projects = await self.get_project_metrics(project_gid)
            
            # Get team productivity
            teams = await self.analyze_team_productivity()
            
            # Get risk assessments
            risks = await self.perform_risk_assessment(project_gid)
            
            # Store insights in AI Memory
            await self._store_intelligence_insights(projects, teams, risks)
            
            # Generate summary insights
            summary = await self._generate_summary_insights(projects, teams, risks)
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "scope": "single_project" if project_gid else "all_projects",
                "project_metrics": [
                    {
                        "project_gid": p.project_gid,
                        "project_name": p.project_name,
                        "health_score": p.health_score,
                        "completion_percentage": p.completion_percentage,
                        "risk_level": p.risk_level.value,
                        "task_count": p.task_count,
                        "overdue_tasks": p.overdue_task_count,
                        "team_name": p.team_name,
                        "owner_name": p.owner_name
                    } for p in projects
                ],
                "team_productivity": [
                    {
                        "team_name": t.team_name,
                        "productivity_score": t.productivity_score,
                        "active_projects": t.active_projects,
                        "completion_rate": t.average_completion_rate,
                        "team_velocity": t.team_velocity,
                        "member_count": t.member_count
                    } for t in teams
                ],
                "risk_assessments": [
                    {
                        "project_gid": r.project_gid,
                        "project_name": r.project_name,
                        "overall_risk": r.overall_risk.value,
                        "risk_factors": r.risk_factors,
                        "mitigation_suggestions": r.mitigation_suggestions,
                        "predicted_completion": r.predicted_completion_date.isoformat() if r.predicted_completion_date else None
                    } for r in risks
                ],
                "summary": summary
            }
            
            logger.info(f"✅ Generated intelligence report for {len(projects)} projects")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate intelligence report: {e}")
            return {"error": str(e), "generated_at": datetime.now().isoformat()}

    async def _store_intelligence_insights(
        self, 
        projects: List[AsanaProjectMetrics], 
        teams: List[TeamProductivityMetrics], 
        risks: List[ProjectRiskAssessment]
    ) -> None:
        """Store intelligence insights in AI Memory for future reference"""
        try:
            # Store project insights
            for project in projects:
                insight_content = f"""
                Project Intelligence: {project.project_name}
                Health Score: {project.health_score:.2f}
                Completion: {project.completion_percentage}%
                Risk Level: {project.risk_level.value}
                Team: {project.team_name}
                Owner: {project.owner_name}
                Tasks: {project.completed_task_count}/{project.task_count} completed
                """
                
                await self.ai_memory_service.store_memory(
                    content=insight_content,
                    category="asana_project_intelligence",
                    tags=["project_analysis", "health_score", project.project_gid],
                    metadata={
                        "project_gid": project.project_gid,
                        "health_score": project.health_score,
                        "risk_level": project.risk_level.value,
                        "analysis_date": datetime.now().isoformat()
                    }
                )
            
            # Store team insights
            for team in teams:
                team_insight = f"""
                Team Productivity Analysis: {team.team_name}
                Productivity Score: {team.productivity_score:.2f}
                Active Projects: {team.active_projects}
                Completion Rate: {team.average_completion_rate:.1f}%
                Team Velocity: {team.team_velocity:.1f} tasks/member/month
                """
                
                await self.ai_memory_service.store_memory(
                    content=team_insight,
                    category="asana_team_productivity",
                    tags=["team_analysis", "productivity", team.team_name.lower().replace(" ", "_")],
                    metadata={
                        "team_name": team.team_name,
                        "productivity_score": team.productivity_score,
                        "analysis_date": datetime.now().isoformat()
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to store intelligence insights: {e}")

    async def _generate_summary_insights(
        self, 
        projects: List[AsanaProjectMetrics], 
        teams: List[TeamProductivityMetrics], 
        risks: List[ProjectRiskAssessment]
    ) -> Dict[str, Any]:
        """Generate high-level summary insights"""
        try:
            if not projects:
                return {"message": "No projects found for analysis"}
            
            # Calculate aggregate metrics
            avg_health_score = sum(p.health_score for p in projects) / len(projects)
            avg_completion = sum(p.completion_percentage for p in projects) / len(projects)
            total_overdue_tasks = sum(p.overdue_task_count for p in projects)
            
            # Risk distribution
            risk_distribution = {}
            for risk in risks:
                risk_level = risk.overall_risk.value
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # Top performing teams
            top_teams = sorted(teams, key=lambda t: t.productivity_score, reverse=True)[:3]
            
            # Projects needing attention
            at_risk_projects = [p for p in projects if p.health_score < 0.6 or p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
            
            summary = {
                "overall_health_score": round(avg_health_score, 2),
                "average_completion": round(avg_completion, 1),
                "total_projects": len(projects),
                "total_overdue_tasks": total_overdue_tasks,
                "risk_distribution": risk_distribution,
                "top_performing_teams": [
                    {"name": t.team_name, "score": round(t.productivity_score, 2)} 
                    for t in top_teams
                ],
                "projects_needing_attention": [
                    {
                        "name": p.project_name, 
                        "health_score": round(p.health_score, 2),
                        "risk_level": p.risk_level.value
                    } 
                    for p in at_risk_projects[:5]
                ],
                "key_insights": [
                    f"Portfolio health score: {avg_health_score:.1%}",
                    f"Average project completion: {avg_completion:.1f}%",
                    f"{len(at_risk_projects)} projects need immediate attention",
                    f"Top team: {top_teams[0].team_name}" if top_teams else "No team data available"
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate summary insights: {e}")
            return {"error": str(e)}

    async def close(self) -> None:
        """Clean up resources"""
        try:
            if self.cortex_service:
                await self.cortex_service.close()
            if self.ai_memory_service:
                await self.ai_memory_service.close()
            if self.smart_ai_service:
                await self.smart_ai_service.close()
            await super().close()
        except Exception as e:
            logger.error(f"❌ Error closing Asana intelligence agent: {e}")

# Example usage and testing
async def main():
    """Test the Asana Project Intelligence Agent"""
    config = {
        "agent_id": "asana_project_intelligence",
        "performance_target_ms": 200,
        "cache_ttl_seconds": 300
    }
    
    agent = AsanaProjectIntelligenceAgent(config)
    
    try:
        await agent.initialize()
        
        # Generate comprehensive intelligence report
        report = await agent.generate_project_intelligence_report()
        
        print("🧠 Asana Project Intelligence Report")
        print("=" * 50)
        print(f"Generated: {report['generated_at']}")
        print(f"Projects analyzed: {report['summary']['total_projects']}")
        print(f"Overall health score: {report['summary']['overall_health_score']}")
        print(f"Average completion: {report['summary']['average_completion']}%")
        
        if report['summary']['projects_needing_attention']:
            print("\n⚠️ Projects needing attention:")
            for project in report['summary']['projects_needing_attention']:
                print(f"  - {project['name']}: {project['health_score']} health, {project['risk_level']} risk")
        
        print("\n✅ Asana Project Intelligence Agent test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main()) 