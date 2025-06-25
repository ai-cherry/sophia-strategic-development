"""
Project Dashboard API Routes
Provides endpoints for project management, tasks, team performance, and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.auth import get_current_user
from backend.services.project_service import ProjectService
from backend.services.task_service import TaskService
from backend.services.team_service import TeamService
from backend.services.analytics_service import AnalyticsService
from backend.models.project import Project, Task, TeamMember, SprintVelocity
from backend.core.cache_manager import DashboardCacheManager
from backend.core.logger import logger

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

# Initialize services
project_service = ProjectService()
task_service = TaskService()
team_service = TeamService()
analytics_service = AnalyticsService()
cache_manager = DashboardCacheManager()


@router.get("/", response_model=List[Project])
async def get_projects(
    status: Optional[str] = Query(None, description="Filter by project status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[Project]:
    """
    Get all projects with optional filters

    Returns:
        List of projects with their current status and metrics
    """
    try:
        # Try to get from cache first
        cache_key = f"projects:{user_id}:{status}:{priority}"
        cached_data = await cache_manager.get_or_set(
            cache_key,
            lambda: project_service.get_projects(session, user_id, status, priority),
            ttl=300,  # 5 minutes cache
        )
        return cached_data
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch projects")


@router.get("/tasks", response_model=List[Task])
async def get_tasks(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    due_date_start: Optional[datetime] = Query(
        None, description="Filter by due date start"
    ),
    due_date_end: Optional[datetime] = Query(
        None, description="Filter by due date end"
    ),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[Task]:
    """
    Get tasks with multiple filter options

    Returns:
        List of tasks matching the specified criteria
    """
    try:
        filters = {
            "project_id": project_id,
            "assignee": assignee,
            "status": status,
            "priority": priority,
            "due_date_start": due_date_start,
            "due_date_end": due_date_end,
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        tasks = await task_service.get_tasks(session, user_id, **filters)
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")


@router.get("/team/performance", response_model=List[TeamMember])
async def get_team_performance(
    time_period: str = Query(
        "30d", description="Time period for metrics (7d, 30d, 90d)"
    ),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[TeamMember]:
    """
    Get team performance metrics

    Returns:
        List of team members with their performance metrics
    """
    try:
        # Parse time period
        days = {"7d": 7, "30d": 30, "90d": 90}.get(time_period, 30)
        start_date = datetime.now() - timedelta(days=days)

        # Get team performance data
        performance_data = await team_service.get_performance_metrics(
            session, user_id, start_date
        )

        return performance_data
    except Exception as e:
        logger.error(f"Error fetching team performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch team performance")


@router.get("/stats/sprint-velocity", response_model=List[SprintVelocity])
async def get_sprint_velocity(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    sprints: int = Query(6, description="Number of sprints to include"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[SprintVelocity]:
    """
    Get sprint velocity data for analytics

    Returns:
        Sprint velocity data for the specified number of sprints
    """
    try:
        velocity_data = await analytics_service.get_sprint_velocity(
            session, user_id, project_id, sprints
        )
        return velocity_data
    except Exception as e:
        logger.error(f"Error fetching sprint velocity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sprint velocity")


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_project_stats_overview(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get comprehensive project statistics overview

    Returns:
        Dictionary containing project, task, and team statistics
    """
    try:
        # Use cache for frequently accessed overview data
        cache_key = f"project_stats_overview:{user_id}"

        async def fetch_overview():
            return {
                "projects": await project_service.get_project_stats(session, user_id),
                "tasks": await task_service.get_task_stats(session, user_id),
                "team": await team_service.get_team_stats(session, user_id),
                "recent_activity": await analytics_service.get_recent_activity(
                    session, user_id
                ),
                "upcoming_deadlines": await task_service.get_upcoming_deadlines(
                    session, user_id
                ),
            }

        overview_data = await cache_manager.get_or_set(
            cache_key, fetch_overview, ttl=120  # 2 minutes cache for overview
        )

        return overview_data
    except Exception as e:
        logger.error(f"Error fetching project overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch project overview")


@router.post("/{project_id}/tasks")
async def create_task(
    project_id: str,
    task_data: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    """
    Create a new task for a project

    Returns:
        The created task
    """
    try:
        # Verify project access
        project = await project_service.get_project(session, project_id, user_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Create task
        task = await task_service.create_task(
            session, project_id=project_id, **task_data
        )

        # Invalidate relevant caches
        await cache_manager.invalidate_pattern(f"projects:{user_id}:*")
        await cache_manager.invalidate_pattern(f"project_stats_overview:{user_id}")

        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    task_update: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    """
    Update an existing task

    Returns:
        The updated task
    """
    try:
        # Update task
        task = await task_service.update_task(
            session, task_id=task_id, user_id=user_id, **task_update
        )

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Invalidate relevant caches
        await cache_manager.invalidate_pattern(f"projects:{user_id}:*")
        await cache_manager.invalidate_pattern(f"project_stats_overview:{user_id}")

        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update task")


@router.get("/department-okrs", response_model=Dict[str, Any])
async def get_department_okrs(
    department: Optional[str] = Query(None, description="Filter by department"),
    quarter: Optional[str] = Query(
        None, description="Filter by quarter (e.g., Q1-2025)"
    ),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get OKRs organized by department

    Returns:
        Department OKRs with progress tracking
    """
    try:
        okr_data = await analytics_service.get_department_okrs(
            session, user_id, department, quarter
        )
        return okr_data
    except Exception as e:
        logger.error(f"Error fetching department OKRs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch department OKRs")


@router.get("/cross-functional-insights", response_model=Dict[str, Any])
async def get_cross_functional_insights(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get insights on cross-functional collaboration

    Returns:
        Cross-functional collaboration metrics and insights
    """
    try:
        insights = await analytics_service.get_cross_functional_insights(
            session, user_id
        )
        return insights
    except Exception as e:
        logger.error(f"Error fetching cross-functional insights: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch cross-functional insights"
        )


@router.get("/resource-allocation", response_model=Dict[str, Any])
async def get_resource_allocation(
    view: str = Query("team", description="View type: team, project, or department"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get resource allocation data

    Returns:
        Resource allocation breakdown by specified view
    """
    try:
        allocation_data = await analytics_service.get_resource_allocation(
            session, user_id, view
        )
        return allocation_data
    except Exception as e:
        logger.error(f"Error fetching resource allocation: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch resource allocation"
        )
