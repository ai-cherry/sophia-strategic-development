"""
Project Intelligence Service for CEO Dashboard.

Integrates Linear and Asana project data to provide real-time
project health monitoring and insights for the unified dashboard.
"""

from datetime import datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

from backend.utils.snowflake_hubspot_connector import SnowflakeHubSpotConnector

logger = structlog.get_logger()


class ProjectStatus(BaseModel):
    """Project status information."""

    project_id: str
    name: str
    status: str  # on_track, at_risk, delayed
    completion_percentage: float = Field(ge=0, le=100)
    due_date: datetime | None = None
    team_members: int
    open_issues: int
    completed_issues: int


class ProjectHealth(BaseModel):
    """Project health metrics."""

    health_score: float = Field(ge=0, le=100)
    velocity_trend: str  # increasing, stable, decreasing
    risk_factors: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ProjectIntelligenceService:
    """
    Provides real-time project intelligence for CEO dashboard.

    Integrates data from Linear and Asana to provide unified
    project health monitoring and insights.
    """

    def __init__(self):
        self.logger = logger.bind(service="project_intelligence")
        self.snowflake = SnowflakeHubSpotConnector()

    async def get_project_summary(self) -> dict[str, Any]:
        """
        Get high-level project summary for CEO dashboard.

        Returns:
            Summary of all active projects with health metrics
        """
        try:
            # Query consolidated project data
            query = """
            WITH project_metrics AS (
                SELECT
                    project_id,
                    project_name,
                    source_system,
                    status,
                    completion_percentage,
                    due_date,
                    team_member_count,
                    open_issue_count,
                    completed_issue_count,
                    health_score,
                    velocity_trend,
                    last_updated
                FROM AI_MEMORY.PROJECT_INTELLIGENCE
                WHERE is_active = TRUE
                    AND last_updated > DATEADD(hour, -24, CURRENT_TIMESTAMP())
            ),
            risk_analysis AS (
                SELECT
                    project_id,
                    ARRAY_AGG(risk_factor) as risk_factors
                FROM AI_MEMORY.PROJECT_RISKS
                WHERE severity IN ('high', 'critical')
                    AND is_resolved = FALSE
                GROUP BY project_id
            )
            SELECT
                pm.*,
                ra.risk_factors
            FROM project_metrics pm
            LEFT JOIN risk_analysis ra ON pm.project_id = ra.project_id
            ORDER BY pm.health_score ASC, pm.due_date ASC
            """

            results = await self.snowflake.execute_query(query)

            # Process results
            summary = {
                "total_projects": len(results),
                "at_risk_projects": 0,
                "on_track_projects": 0,
                "delayed_projects": 0,
                "projects": [],
            }

            for row in results:
                project = ProjectStatus(
                    project_id=row["PROJECT_ID"],
                    name=row["PROJECT_NAME"],
                    status=self._determine_status(row),
                    completion_percentage=row["COMPLETION_PERCENTAGE"],
                    due_date=row["DUE_DATE"],
                    team_members=row["TEAM_MEMBER_COUNT"],
                    open_issues=row["OPEN_ISSUE_COUNT"],
                    completed_issues=row["COMPLETED_ISSUE_COUNT"],
                )

                health = ProjectHealth(
                    health_score=row["HEALTH_SCORE"],
                    velocity_trend=row["VELOCITY_TREND"],
                    risk_factors=row.get("RISK_FACTORS", []),
                    recommendations=self._generate_recommendations(row),
                )

                # Update counters
                if project.status == "at_risk":
                    summary["at_risk_projects"] += 1
                elif project.status == "on_track":
                    summary["on_track_projects"] += 1
                elif project.status == "delayed":
                    summary["delayed_projects"] += 1

                summary["projects"].append(
                    {"project": project.dict(), "health": health.dict()}
                )

            self.logger.info(
                "Project summary generated",
                total_projects=summary["total_projects"],
                at_risk=summary["at_risk_projects"],
            )

            return summary

        except Exception as e:
            self.logger.error("Failed to get project summary", error=str(e))
            raise

    async def get_team_performance(self) -> dict[str, Any]:
        """
        Get team performance metrics across all projects.

        Returns:
            Team velocity, productivity, and collaboration metrics
        """
        try:
            query = """
            SELECT
                team_name,
                AVG(velocity_points) as avg_velocity,
                AVG(completion_rate) as avg_completion_rate,
                COUNT(DISTINCT project_id) as active_projects,
                SUM(completed_tasks_week) as tasks_completed_this_week,
                AVG(collaboration_score) as collaboration_score
            FROM AI_MEMORY.TEAM_PERFORMANCE
            WHERE week_start_date >= DATEADD(week, -4, CURRENT_DATE())
            GROUP BY team_name
            ORDER BY avg_velocity DESC
            """

            results = await self.snowflake.execute_query(query)

            return {
                "teams": [
                    {
                        "name": row["TEAM_NAME"],
                        "velocity": row["AVG_VELOCITY"],
                        "completion_rate": row["AVG_COMPLETION_RATE"],
                        "active_projects": row["ACTIVE_PROJECTS"],
                        "weekly_tasks": row["TASKS_COMPLETED_THIS_WEEK"],
                        "collaboration_score": row["COLLABORATION_SCORE"],
                    }
                    for row in results
                ],
                "summary": {
                    "total_teams": len(results),
                    "avg_velocity": sum(r["AVG_VELOCITY"] for r in results)
                    / len(results)
                    if results
                    else 0,
                    "total_weekly_tasks": sum(
                        r["TASKS_COMPLETED_THIS_WEEK"] for r in results
                    ),
                },
            }

        except Exception as e:
            self.logger.error("Failed to get team performance", error=str(e))
            raise

    async def get_milestone_tracking(self) -> dict[str, Any]:
        """
        Track upcoming milestones and deliverables.

        Returns:
            Upcoming milestones with risk assessment
        """
        try:
            query = """
            SELECT
                milestone_id,
                project_name,
                milestone_name,
                due_date,
                completion_percentage,
                dependencies_count,
                blockers_count,
                risk_level
            FROM AI_MEMORY.PROJECT_MILESTONES
            WHERE due_date BETWEEN CURRENT_DATE() AND DATEADD(day, 30, CURRENT_DATE())
                AND completion_percentage < 100
            ORDER BY due_date ASC, risk_level DESC
            """

            results = await self.snowflake.execute_query(query)

            milestones = []
            for row in results:
                days_until_due = (row["DUE_DATE"] - datetime.now()).days

                milestones.append(
                    {
                        "id": row["MILESTONE_ID"],
                        "project": row["PROJECT_NAME"],
                        "name": row["MILESTONE_NAME"],
                        "due_date": row["DUE_DATE"].isoformat(),
                        "days_until_due": days_until_due,
                        "completion": row["COMPLETION_PERCENTAGE"],
                        "dependencies": row["DEPENDENCIES_COUNT"],
                        "blockers": row["BLOCKERS_COUNT"],
                        "risk_level": row["RISK_LEVEL"],
                        "is_critical": days_until_due <= 7
                        and row["COMPLETION_PERCENTAGE"] < 80,
                    }
                )

            return {
                "milestones": milestones,
                "critical_count": sum(1 for m in milestones if m["is_critical"]),
                "total_count": len(milestones),
            }

        except Exception as e:
            self.logger.error("Failed to get milestone tracking", error=str(e))
            raise

    def _determine_status(self, project_data: dict[str, Any]) -> str:
        """Determine project status based on metrics."""
        health_score = project_data["HEALTH_SCORE"]
        due_date = project_data["DUE_DATE"]
        completion = project_data["COMPLETION_PERCENTAGE"]

        if health_score >= 80:
            return "on_track"
        elif health_score >= 60:
            return "at_risk"
        else:
            return "delayed"

        # Check if behind schedule
        if due_date:
            days_until_due = (due_date - datetime.now()).days
            expected_completion = max(0, min(100, (30 - days_until_due) / 30 * 100))
            if completion < expected_completion - 20:
                return "delayed"

        return "at_risk"

    def _generate_recommendations(self, project_data: dict[str, Any]) -> list[str]:
        """Generate actionable recommendations based on project metrics."""
        recommendations = []

        if project_data["VELOCITY_TREND"] == "decreasing":
            recommendations.append(
                "Consider team capacity review - velocity is declining"
            )

        if project_data["OPEN_ISSUE_COUNT"] > project_data["COMPLETED_ISSUE_COUNT"] * 2:
            recommendations.append("High backlog ratio - prioritize issue resolution")

        if project_data.get("RISK_FACTORS"):
            recommendations.append(
                f"Address {len(project_data['RISK_FACTORS'])} identified risk factors"
            )

        health_score = project_data["HEALTH_SCORE"]
        if health_score < 60:
            recommendations.append(
                "Schedule executive review - project health critical"
            )
        elif health_score < 80:
            recommendations.append("Increase monitoring frequency - project at risk")

        return recommendations
