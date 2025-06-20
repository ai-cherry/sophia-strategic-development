"""Project Management Admin Panel Routes
Provides unified API endpoints for cross-tool project intelligence and management
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...agents.core.base_agent import Task
from ...agents.specialized.project_intelligence_agent import ProjectIntelligenceAgent
from ..security import UserRole, get_current_user_role

router = APIRouter(prefix="/api/project-management", tags=["Project Management"])


# Pydantic models
class OKRUpdate(BaseModel):
    objective_id: str
    key_result_id: str
    current_value: float
    notes: Optional[str] = None


class ProjectAction(BaseModel):
    action_id: str
    status: str  # "completed", "in_progress", "dismissed"
    notes: Optional[str] = None


class CustomReport(BaseModel):
    name: str
    filters: Dict[str, Any]
    metrics: List[str]
    grouping: Optional[str] = None


# Initialize agent
project_agent = ProjectIntelligenceAgent(
    {
        "name": "project_intelligence",
        "description": "Unified project management intelligence",
    }
)


@router.get("/dashboard/summary")
async def get_dashboard_summary(current_user: Dict = Depends(get_current_user_role)):
    """Get comprehensive project portfolio summary"""
    try:
        # Execute portfolio analysis
        task = Task(task_type="analyze_project_portfolio", task_data={})

        result = await project_agent.execute_task(task)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Add user context
        result.data["user_role"] = current_user.get("role", "viewer")
        result.data["last_updated"] = datetime.now().isoformat()

        return result.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okr/alignment")
async def get_okr_alignment_report(
    quarter: Optional[str] = Query("Q1_2024", description="Quarter to analyze"),
    current_user: Dict = Depends(get_current_user_role),
):
    """Get detailed OKR alignment report"""
    try:
        task = Task(task_type="generate_okr_report", task_data={"quarter": quarter})

        result = await project_agent.execute_task(task)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return result.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/okr/update")
async def update_okr_progress(
    update: OKRUpdate, current_user: Dict = Depends(get_current_user_role)
):
    """Update OKR progress (requires admin role)"""
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # In production, this would update the database
        # For now, we'll return a success response
        return {
            "success": True,
            "objective_id": update.objective_id,
            "key_result_id": update.key_result_id,
            "new_value": update.current_value,
            "updated_by": current_user.get("email"),
            "updated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blockers")
async def get_cross_project_blockers(
    current_user: Dict = Depends(get_current_user_role),
):
    """Get analysis of cross-project blockers"""
    try:
        task = Task(task_type="identify_blockers", task_data={})

        result = await project_agent.execute_task(task)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return result.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_strategic_recommendations(
    focus_area: Optional[str] = Query(
        None, description="Focus area for recommendations"
    ),
    current_user: Dict = Depends(get_current_user_role),
):
    """Get AI-generated strategic recommendations"""
    try:
        task = Task(task_type="recommend_actions", task_data={"focus_area": focus_area})

        result = await project_agent.execute_task(task)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return result.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/action")
async def update_recommendation_status(
    action: ProjectAction, current_user: Dict = Depends(get_current_user_role)
):
    """Update status of a recommendation"""
    if current_user.get("role") not in [UserRole.ADMIN, UserRole.USER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        # In production, this would update the database
        return {
            "success": True,
            "action_id": action.action_id,
            "new_status": action.status,
            "updated_by": current_user.get("email"),
            "updated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}")
async def get_project_details(
    project_id: str, current_user: Dict = Depends(get_current_user_role)
):
    """Get detailed information about a specific project"""
    try:
        # Get portfolio data
        task = Task(task_type="analyze_project_portfolio", task_data={})

        result = await project_agent.execute_task(task)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Find the specific project
        projects = result.data.get("projects", [])
        project = None

        for p in projects:
            # Check across different sources
            if (
                p.get("raw_data", {}).get("linear", {}).get("id") == project_id
                or p.get("raw_data", {}).get("github", {}).get("id") == project_id
            ):
                project = p
                break

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Enhance with additional details
        project["detailed_timeline"] = _generate_project_timeline(project)
        project["team_members"] = _get_project_team(project)
        project["recent_updates"] = _get_recent_updates(project)

        return project

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/performance")
async def get_team_performance_metrics(
    team_name: Optional[str] = Query(None, description="Specific team to analyze"),
    current_user: Dict = Depends(get_current_user_role),
):
    """Get team performance metrics across projects"""
    try:
        # Get portfolio data
        task = Task(task_type="analyze_project_portfolio", task_data={})

        result = await project_agent.execute_task(task)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Analyze by team
        team_metrics = _calculate_team_metrics(result.data["projects"], team_name)

        return {
            "teams": team_metrics,
            "summary": _generate_team_summary(team_metrics),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/custom")
async def generate_custom_report(
    report_config: CustomReport, current_user: Dict = Depends(get_current_user_role)
):
    """Generate a custom project report"""
    try:
        # Get portfolio data
        task = Task(task_type="analyze_project_portfolio", task_data={})

        result = await project_agent.execute_task(task)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Apply filters and generate report
        filtered_projects = _apply_filters(
            result.data["projects"], report_config.filters
        )
        report_data = _generate_custom_metrics(filtered_projects, report_config.metrics)

        if report_config.grouping:
            report_data = _group_by_attribute(report_data, report_config.grouping)

        return {
            "report_name": report_config.name,
            "data": report_data,
            "project_count": len(filtered_projects),
            "generated_at": datetime.now().isoformat(),
            "generated_by": current_user.get("email"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/trends")
async def get_project_trends(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict = Depends(get_current_user_role),
):
    """Get trending insights across projects"""
    try:
        # This would analyze historical data in production
        # For now, return sample trends
        return {
            "velocity_trend": {
                "current": 15.2,
                "previous": 12.8,
                "change_percentage": 18.75,
                "trend": "increasing",
            },
            "blocker_trend": {
                "current": 8,
                "previous": 12,
                "change_percentage": -33.33,
                "trend": "decreasing",
            },
            "completion_trend": {
                "current": 68.5,
                "previous": 62.1,
                "change_percentage": 10.31,
                "trend": "increasing",
            },
            "team_sentiment_trend": {
                "current": 0.72,
                "previous": 0.68,
                "change_percentage": 5.88,
                "trend": "improving",
            },
            "period": f"Last {days} days",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/milestones")
async def get_milestone_calendar(
    start_date: Optional[datetime] = Query(None, description="Start date for calendar"),
    end_date: Optional[datetime] = Query(None, description="End date for calendar"),
    current_user: Dict = Depends(get_current_user_role),
):
    """Get project milestones for calendar view"""
    try:
        if not start_date:
            start_date = datetime.now()
        if not end_date:
            end_date = start_date + timedelta(days=90)

        # Get portfolio data
        task = Task(task_type="analyze_project_portfolio", task_data={})

        result = await project_agent.execute_task(task)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Extract milestones
        milestones = _extract_milestones(result.data["projects"], start_date, end_date)

        return {
            "milestones": milestones,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_milestones": len(milestones),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def _generate_project_timeline(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate timeline events for a project"""
    timeline = []

    # Add start date
    if "start_date" in project.get("raw_data", {}).get("linear", {}):
        timeline.append(
            {
                "date": project["raw_data"]["linear"]["start_date"],
                "event": "Project Started",
                "type": "milestone",
            }
        )

    # Add recent updates from issues
    for issue in project.get("raw_data", {}).get("linear", {}).get("issues", [])[:5]:
        if issue.get("updatedAt"):
            timeline.append(
                {
                    "date": issue["updatedAt"],
                    "event": f"Issue updated: {issue.get('title', 'Unknown')}",
                    "type": "update",
                }
            )

    # Sort by date
    timeline.sort(key=lambda x: x["date"], reverse=True)

    return timeline[:10]  # Return last 10 events


def _get_project_team(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract team members from project data"""
    team_members = {}

    # From Linear issues
    for issue in project.get("raw_data", {}).get("linear", {}).get("issues", []):
        assignee = issue.get("assignee")
        if assignee:
            email = assignee.get("email", "unknown")
            if email not in team_members:
                team_members[email] = {
                    "name": assignee.get("name", "Unknown"),
                    "email": email,
                    "avatar": assignee.get("avatarUrl"),
                    "issue_count": 0,
                }
            team_members[email]["issue_count"] += 1

    return list(team_members.values())


def _get_recent_updates(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get recent updates from Slack mentions"""
    updates = []

    slack_data = project.get("raw_data", {}).get("slack", {})
    mentions = slack_data.get("mentions", [])

    for mention in mentions[:5]:  # Last 5 mentions
        updates.append(
            {
                "timestamp": mention.get("ts"),
                "channel": mention.get("channel"),
                "user": mention.get("user"),
                "text": mention.get("text", "")[:200] + "...",
                "type": "slack_mention",
            }
        )

    return updates


def _calculate_team_metrics(
    projects: List[Dict[str, Any]], team_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Calculate metrics grouped by team"""
    team_metrics = {}

    for project in projects:
        team = project.get("raw_data", {}).get("linear", {}).get("team", "Unknown")

        if team_filter and team != team_filter:
            continue

        if team not in team_metrics:
            team_metrics[team] = {
                "project_count": 0,
                "total_velocity": 0,
                "blocked_items": 0,
                "completion_sum": 0,
                "sentiment_sum": 0,
                "on_track_count": 0,
                "at_risk_count": 0,
            }

        metrics = team_metrics[team]
        metrics["project_count"] += 1
        metrics["total_velocity"] += project["metrics"]["velocity"]
        metrics["blocked_items"] += project["metrics"]["blocked_items"]
        metrics["completion_sum"] += project["metrics"]["completion"]
        metrics["sentiment_sum"] += project["metrics"]["team_sentiment"]

        if project["status"] == "on_track":
            metrics["on_track_count"] += 1
        elif project["status"] == "at_risk":
            metrics["at_risk_count"] += 1

    # Calculate averages
    for team, metrics in team_metrics.items():
        count = metrics["project_count"]
        if count > 0:
            metrics["avg_velocity"] = metrics["total_velocity"] / count
            metrics["avg_completion"] = metrics["completion_sum"] / count
            metrics["avg_sentiment"] = metrics["sentiment_sum"] / count
            metrics["health_score"] = (metrics["on_track_count"] / count) * 100

    return team_metrics


def _generate_team_summary(team_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary of team performance"""
    if not team_metrics:
        return {"message": "No team data available"}

    # Find best and worst performing teams
    teams_by_health = sorted(
        team_metrics.items(), key=lambda x: x[1].get("health_score", 0), reverse=True
    )

    return {
        "total_teams": len(team_metrics),
        "best_performing_team": teams_by_health[0][0] if teams_by_health else None,
        "needs_attention_team": teams_by_health[-1][0] if teams_by_health else None,
        "avg_health_score": (
            sum(t[1].get("health_score", 0) for t in teams_by_health)
            / len(teams_by_health)
            if teams_by_health
            else 0
        ),
    }


def _apply_filters(
    projects: List[Dict[str, Any]], filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Apply filters to project list"""
    filtered = projects

    if "status" in filters:
        filtered = [p for p in filtered if p["status"] == filters["status"]]

    if "team" in filters:
        filtered = [
            p
            for p in filtered
            if p.get("raw_data", {}).get("linear", {}).get("team") == filters["team"]
        ]

    if "min_completion" in filters:
        filtered = [
            p
            for p in filtered
            if p["metrics"]["completion"] >= filters["min_completion"]
        ]

    if "has_blockers" in filters:
        filtered = [
            p
            for p in filtered
            if (p["metrics"]["blocked_items"] > 0) == filters["has_blockers"]
        ]

    return filtered


def _generate_custom_metrics(
    projects: List[Dict[str, Any]], metrics: List[str]
) -> List[Dict[str, Any]]:
    """Generate custom metrics for projects"""
    results = []

    for project in projects:
        project_metrics = {
            "project_name": project["name"],
            "project_id": project.get("raw_data", {})
            .get("linear", {})
            .get("id", "unknown"),
        }

        for metric in metrics:
            if metric in project["metrics"]:
                project_metrics[metric] = project["metrics"][metric]
            elif metric == "okr_count":
                project_metrics[metric] = len(project.get("okr_alignment", []))
            elif metric == "days_until_deadline":
                # Calculate from target date
                target_date = (
                    project.get("raw_data", {}).get("linear", {}).get("target_date")
                )
                if target_date:
                    try:
                        target = datetime.fromisoformat(
                            target_date.replace("Z", "+00:00")
                        )
                        project_metrics[metric] = (target - datetime.now()).days
                    except:
                        project_metrics[metric] = None
                else:
                    project_metrics[metric] = None

        results.append(project_metrics)

    return results


def _group_by_attribute(
    data: List[Dict[str, Any]], grouping: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Group data by specified attribute"""
    grouped = {}

    for item in data:
        key = item.get(grouping, "Unknown")
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)

    return grouped


def _extract_milestones(
    projects: List[Dict[str, Any]], start_date: datetime, end_date: datetime
) -> List[Dict[str, Any]]:
    """Extract project milestones within date range"""
    milestones = []

    for project in projects:
        # Check target date
        target_date_str = (
            project.get("raw_data", {}).get("linear", {}).get("target_date")
        )
        if target_date_str:
            try:
                target_date = datetime.fromisoformat(
                    target_date_str.replace("Z", "+00:00")
                )
                if start_date <= target_date <= end_date:
                    milestones.append(
                        {
                            "date": target_date.isoformat(),
                            "project": project["name"],
                            "type": "deadline",
                            "status": project["status"],
                            "completion": project["metrics"]["completion"],
                        }
                    )
            except:
                pass

        # Add other milestone types (launches, reviews, etc.)
        # This would be expanded in production

    # Sort by date
    milestones.sort(key=lambda x: x["date"])

    return milestones
