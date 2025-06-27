#!/usr/bin/env python3
"""
Asana Integration API Routes

Comprehensive API endpoints for Asana project management integration including:
- Project intelligence and analytics
- Task management and tracking
- Team productivity metrics
- AI-powered insights and recommendations
- Chat service integration
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import json

from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.agents.specialized.asana_project_intelligence_agent import AsanaProjectIntelligenceAgent
from backend.services.sophia_universal_chat_service import SophiaUniversalChatService
from backend.etl.airbyte.airbyte_configuration_manager import EnhancedAirbyteManager
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer
from backend.services.enhanced_unified_chat_service import EnhancedUnifiedChatService, QueryContext
from backend.core.auth import get_current_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/asana", tags=["asana"])

# Pydantic models for request/response
class AsanaQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query about Asana data")
    user_id: str = Field(..., description="User ID for context")
    user_role: str = Field(default="manager", description="User role for access control")
    dashboard_type: str = Field(default="project", description="Dashboard context")
    time_filter: Optional[str] = Field(None, description="Time filter (e.g., '30d', '7d')")

class ProjectFilterRequest(BaseModel):
    team_name: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    search_term: Optional[str] = None
    sort_by: str = Field(default="health_score", description="Sort field")
    limit: int = Field(default=50, description="Maximum results")

class TaskFilterRequest(BaseModel):
    project_gid: Optional[str] = None
    assignee_name: Optional[str] = None
    status: Optional[str] = None
    priority_level: Optional[str] = None
    overdue_only: bool = Field(default=False)
    limit: int = Field(default=100, description="Maximum results")

class AsanaInsightRequest(BaseModel):
    project_gid: Optional[str] = None
    insight_type: str = Field(..., description="Type of insight: project_health, risk_assessment, team_productivity")
    include_ai_recommendations: bool = Field(default=True)

class AsanaSyncRequest(BaseModel):
    force_sync: bool = Field(default=False, description="Force immediate sync")
    sync_type: str = Field(default="incremental", description="Sync type: full, incremental")

# Service instances (will be initialized on startup)
intelligence_agent: Optional[AsanaProjectIntelligenceAgent] = None
chat_service: Optional[SophiaUniversalChatService] = None
airbyte_manager: Optional[EnhancedAirbyteManager] = None
cortex_service: Optional[SnowflakeCortexService] = None
ai_memory_service: Optional[EnhancedAiMemoryMCPServer] = None

async def get_intelligence_agent() -> AsanaProjectIntelligenceAgent:
    """Get or initialize the intelligence agent"""
    global intelligence_agent
    if intelligence_agent is None:
        intelligence_agent = AsanaProjectIntelligenceAgent({
            "agent_id": "asana_api_intelligence",
            "performance_target_ms": 200
        })
        await intelligence_agent.initialize()
    return intelligence_agent

async def get_chat_service() -> SophiaUniversalChatService:
    """Get or initialize the chat service"""
    global chat_service
    if chat_service is None:
        chat_service = SophiaUniversalChatService()
        await chat_service.initialize()
    return chat_service

async def get_airbyte_manager() -> EnhancedAirbyteManager:
    """Get or initialize the Airbyte manager"""
    global airbyte_manager
    if airbyte_manager is None:
        airbyte_manager = EnhancedAirbyteManager("dev")  # TODO: Make environment configurable
        await airbyte_manager.initialize()
    return airbyte_manager

async def get_cortex_service() -> SnowflakeCortexService:
    """Get or initialize the Cortex service"""
    global cortex_service
    if cortex_service is None:
        cortex_service = SnowflakeCortexService()
        await cortex_service.initialize()
    return cortex_service

# PROJECT INTELLIGENCE ENDPOINTS

@router.get("/intelligence-report")
async def get_project_intelligence_report(
    project_gid: Optional[str] = Query(None, description="Specific project GID"),
    agent: AsanaProjectIntelligenceAgent = Depends(get_intelligence_agent)
):
    """
    Generate comprehensive project intelligence report
    
    Returns:
    - Project metrics and health scores
    - Team productivity analysis
    - Risk assessments
    - AI-powered insights and recommendations
    """
    try:
        logger.info(f"Generating intelligence report for project: {project_gid or 'all'}")
        
        report = await agent.generate_project_intelligence_report(project_gid)
        
        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])
        
        return JSONResponse(content=report)
        
    except Exception as e:
        logger.error(f"Failed to generate intelligence report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects")
async def get_projects(
    team_name: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search_term: Optional[str] = Query(None),
    sort_by: str = Query("health_score"),
    limit: int = Query(50),
    agent: AsanaProjectIntelligenceAgent = Depends(get_intelligence_agent)
):
    """
    Get filtered and sorted project list with metrics
    """
    try:
        # Get all project metrics
        projects = await agent.get_project_metrics()
        
        # Apply filters
        if team_name:
            projects = [p for p in projects if p.team_name == team_name]
        
        if risk_level:
            projects = [p for p in projects if p.risk_level.value == risk_level]
        
        if search_term:
            search_lower = search_term.lower()
            projects = [
                p for p in projects 
                if search_lower in p.project_name.lower() 
                or (p.team_name and search_lower in p.team_name.lower())
                or (p.owner_name and search_lower in p.owner_name.lower())
            ]
        
        # Sort projects
        if sort_by == "health_score":
            projects.sort(key=lambda p: p.health_score, reverse=True)
        elif sort_by == "completion":
            projects.sort(key=lambda p: p.completion_percentage, reverse=True)
        elif sort_by == "risk":
            risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            projects.sort(key=lambda p: risk_order.get(p.risk_level.value, 0), reverse=True)
        elif sort_by == "due_date":
            projects.sort(key=lambda p: p.due_date or datetime.max)
        
        # Limit results
        projects = projects[:limit]
        
        # Convert to dict format
        project_data = []
        for project in projects:
            project_data.append({
                "project_gid": project.project_gid,
                "project_name": project.project_name,
                "health_score": project.health_score,
                "completion_percentage": project.completion_percentage,
                "risk_level": project.risk_level.value,
                "task_count": project.task_count,
                "completed_task_count": project.completed_task_count,
                "overdue_task_count": project.overdue_task_count,
                "team_name": project.team_name,
                "owner_name": project.owner_name,
                "due_date": project.due_date.isoformat() if project.due_date else None,
                "created_at": project.created_at.isoformat(),
                "modified_at": project.modified_at.isoformat(),
                "ai_insights": project.ai_insights
            })
        
        return JSONResponse(content={
            "projects": project_data,
            "total_count": len(project_data),
            "filters_applied": {
                "team_name": team_name,
                "risk_level": risk_level,
                "status": status,
                "search_term": search_term,
                "sort_by": sort_by
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_gid}")
async def get_project_details(
    project_gid: str = Path(..., description="Project GID"),
    agent: AsanaProjectIntelligenceAgent = Depends(get_intelligence_agent)
):
    """
    Get detailed information for a specific project
    """
    try:
        projects = await agent.get_project_metrics(project_gid)
        
        if not projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects[0]
        
        # Get risk assessment for this project
        risk_assessments = await agent.perform_risk_assessment(project_gid)
        risk_assessment = risk_assessments[0] if risk_assessments else None
        
        project_detail = {
            "project_gid": project.project_gid,
            "project_name": project.project_name,
            "health_score": project.health_score,
            "completion_percentage": project.completion_percentage,
            "risk_level": project.risk_level.value,
            "task_count": project.task_count,
            "completed_task_count": project.completed_task_count,
            "overdue_task_count": project.overdue_task_count,
            "team_name": project.team_name,
            "owner_name": project.owner_name,
            "due_date": project.due_date.isoformat() if project.due_date else None,
            "created_at": project.created_at.isoformat(),
            "modified_at": project.modified_at.isoformat(),
            "ai_insights": project.ai_insights
        }
        
        if risk_assessment:
            project_detail["risk_assessment"] = {
                "overall_risk": risk_assessment.overall_risk.value,
                "schedule_risk": risk_assessment.schedule_risk.value,
                "resource_risk": risk_assessment.resource_risk.value,
                "scope_risk": risk_assessment.scope_risk.value,
                "quality_risk": risk_assessment.quality_risk.value,
                "risk_factors": risk_assessment.risk_factors,
                "mitigation_suggestions": risk_assessment.mitigation_suggestions,
                "predicted_completion_date": risk_assessment.predicted_completion_date.isoformat() if risk_assessment.predicted_completion_date else None
            }
        
        return JSONResponse(content=project_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/productivity")
async def get_team_productivity(
    team_name: Optional[str] = Query(None),
    agent: AsanaProjectIntelligenceAgent = Depends(get_intelligence_agent)
):
    """
    Get team productivity metrics and analytics
    """
    try:
        teams = await agent.analyze_team_productivity(team_name)
        
        team_data = []
        for team in teams:
            team_data.append({
                "team_name": team.team_name,
                "productivity_score": team.productivity_score,
                "total_projects": team.total_projects,
                "active_projects": team.active_projects,
                "completed_projects": team.completed_projects,
                "average_completion_rate": team.average_completion_rate,
                "overdue_tasks_ratio": team.overdue_tasks_ratio,
                "team_velocity": team.team_velocity,
                "member_count": team.member_count
            })
        
        return JSONResponse(content={
            "teams": team_data,
            "total_teams": len(team_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get team productivity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-assessment")
async def get_risk_assessment(
    project_gid: Optional[str] = Query(None),
    agent: AsanaProjectIntelligenceAgent = Depends(get_intelligence_agent)
):
    """
    Get comprehensive risk assessment for projects
    """
    try:
        risk_assessments = await agent.perform_risk_assessment(project_gid)
        
        assessment_data = []
        for assessment in risk_assessments:
            assessment_data.append({
                "project_gid": assessment.project_gid,
                "project_name": assessment.project_name,
                "overall_risk": assessment.overall_risk.value,
                "schedule_risk": assessment.schedule_risk.value,
                "resource_risk": assessment.resource_risk.value,
                "scope_risk": assessment.scope_risk.value,
                "quality_risk": assessment.quality_risk.value,
                "risk_factors": assessment.risk_factors,
                "mitigation_suggestions": assessment.mitigation_suggestions,
                "predicted_completion_date": assessment.predicted_completion_date.isoformat() if assessment.predicted_completion_date else None
            })
        
        return JSONResponse(content={
            "risk_assessments": assessment_data,
            "total_assessments": len(assessment_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get risk assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# TASK MANAGEMENT ENDPOINTS

@router.get("/tasks")
async def get_tasks(
    project_gid: Optional[str] = Query(None),
    assignee_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority_level: Optional[str] = Query(None),
    overdue_only: bool = Query(False),
    limit: int = Query(100),
    cortex: SnowflakeCortexService = Depends(get_cortex_service)
):
    """
    Get filtered task list with details
    """
    try:
        # Build query conditions
        conditions = ["1=1"]  # Base condition
        
        if project_gid:
            conditions.append(f"PROJECT_GID = '{project_gid}'")
        
        if assignee_name:
            conditions.append(f"ASSIGNEE_NAME = '{assignee_name}'")
        
        if status:
            conditions.append(f"TASK_STATUS = '{status}'")
        
        if priority_level:
            conditions.append(f"PRIORITY_LEVEL = '{priority_level}'")
        
        if overdue_only:
            conditions.append("TASK_STATUS = 'OVERDUE'")
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        SELECT 
            TASK_GID,
            TASK_NAME,
            TASK_DESCRIPTION,
            TASK_STATUS,
            IS_COMPLETED,
            ASSIGNEE_NAME,
            PROJECT_GID,
            PROJECT_NAME,
            DUE_DATE,
            PRIORITY_LEVEL,
            AI_URGENCY_SCORE,
            AI_TASK_SENTIMENT,
            CREATED_AT,
            MODIFIED_AT
        FROM STG_TRANSFORMED.STG_ASANA_TASKS
        WHERE {where_clause}
        ORDER BY AI_URGENCY_SCORE DESC, DUE_DATE ASC
        LIMIT {limit}
        """
        
        result = await cortex.execute_query(query)
        
        tasks = []
        for _, row in result.iterrows():
            tasks.append({
                "task_gid": row["TASK_GID"],
                "task_name": row["TASK_NAME"],
                "task_description": row.get("TASK_DESCRIPTION"),
                "task_status": row["TASK_STATUS"],
                "is_completed": row["IS_COMPLETED"],
                "assignee_name": row.get("ASSIGNEE_NAME"),
                "project_gid": row["PROJECT_GID"],
                "project_name": row.get("PROJECT_NAME"),
                "due_date": row.get("DUE_DATE").isoformat() if row.get("DUE_DATE") else None,
                "priority_level": row.get("PRIORITY_LEVEL"),
                "ai_urgency_score": row.get("AI_URGENCY_SCORE"),
                "ai_task_sentiment": row.get("AI_TASK_SENTIMENT"),
                "created_at": row["CREATED_AT"].isoformat() if row.get("CREATED_AT") else None,
                "modified_at": row["MODIFIED_AT"].isoformat() if row.get("MODIFIED_AT") else None
            })
        
        return JSONResponse(content={
            "tasks": tasks,
            "total_count": len(tasks),
            "filters_applied": {
                "project_gid": project_gid,
                "assignee_name": assignee_name,
                "status": status,
                "priority_level": priority_level,
                "overdue_only": overdue_only
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/overdue")
async def get_overdue_tasks(
    team_name: Optional[str] = Query(None),
    limit: int = Query(50),
    cortex: SnowflakeCortexService = Depends(get_cortex_service)
):
    """
    Get all overdue tasks with priority scoring
    """
    try:
        team_filter = f"AND p.TEAM_NAME = '{team_name}'" if team_name else ""
        
        query = f"""
        SELECT 
            t.TASK_GID,
            t.TASK_NAME,
            t.ASSIGNEE_NAME,
            t.PROJECT_NAME,
            t.DUE_DATE,
            t.PRIORITY_LEVEL,
            t.AI_URGENCY_SCORE,
            p.TEAM_NAME,
            DATEDIFF('day', t.DUE_DATE, CURRENT_DATE) as DAYS_OVERDUE
        FROM STG_TRANSFORMED.STG_ASANA_TASKS t
        LEFT JOIN STG_TRANSFORMED.STG_ASANA_PROJECTS p ON t.PROJECT_GID = p.PROJECT_GID
        WHERE t.TASK_STATUS = 'OVERDUE'
        {team_filter}
        ORDER BY t.AI_URGENCY_SCORE DESC, DAYS_OVERDUE DESC
        LIMIT {limit}
        """
        
        result = await cortex.execute_query(query)
        
        overdue_tasks = []
        for _, row in result.iterrows():
            overdue_tasks.append({
                "task_gid": row["TASK_GID"],
                "task_name": row["TASK_NAME"],
                "assignee_name": row.get("ASSIGNEE_NAME"),
                "project_name": row["PROJECT_NAME"],
                "due_date": row["DUE_DATE"].isoformat() if row.get("DUE_DATE") else None,
                "priority_level": row.get("PRIORITY_LEVEL"),
                "ai_urgency_score": row.get("AI_URGENCY_SCORE"),
                "team_name": row.get("TEAM_NAME"),
                "days_overdue": row.get("DAYS_OVERDUE")
            })
        
        return JSONResponse(content={
            "overdue_tasks": overdue_tasks,
            "total_count": len(overdue_tasks),
            "team_filter": team_name
        })
        
    except Exception as e:
        logger.error(f"Failed to get overdue tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# CHAT INTEGRATION ENDPOINTS

@router.post("/chat/query")
async def process_asana_chat_query(
    request: AsanaQueryRequest,
    chat_service: SophiaUniversalChatService = Depends(get_chat_service)
):
    """
    Process natural language queries about Asana data through the chat service
    """
    try:
        # Create query context
        context = QueryContext(
            user_id=request.user_id,
            user_role=request.user_role,
            dashboard_type=request.dashboard_type,
            security_level="EXECUTIVE",  # Asana data requires executive access
            time_filter=request.time_filter
        )
        
        # Process the query
        result = await chat_service.process_unified_query(request.query, context)
        
        return JSONResponse(content={
            "response": result.content,
            "intent": result.intent.value,
            "data_sources": result.data_sources,
            "confidence_score": result.confidence_score,
            "execution_time_ms": result.execution_time_ms,
            "records_analyzed": result.records_analyzed,
            "security_level": result.security_level,
            "suggested_actions": result.suggested_actions
        })
        
    except Exception as e:
        logger.error(f"Failed to process chat query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat_analyze", response_model=Dict[str, Any])
async def analyze_asana_chat_query(
    request: AsanaQueryRequest,
    current_user: dict = Depends(get_current_user),
    airbyte_manager: EnhancedAirbyteManager = Depends(get_airbyte_manager)
):
    """Analyze a natural language query related to Asana projects."""
    try:
        # Create query context
        context = QueryContext(
            query=request.query,
            context={
                "user_id": request.user_id,
                "user_role": request.user_role,
                "asana_project_ids": request.project_ids,
            }
        )
        
        # In a real implementation, you would use a more sophisticated
        # chat service that can route the query and context.
        # For now, we'll simulate a response.
        
        return {
            "success": True,
            "query": request.query,
            "response": f"Analysis for '{request.query}' would be performed here.",
            "context_received": context,
        }
    except Exception as e:
        logger.error(f"Failed to analyze chat query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# DATA PIPELINE ENDPOINTS

@router.post("/sync")
async def trigger_asana_sync(
    request: AsanaSyncRequest,
    background_tasks: BackgroundTasks,
    airbyte: EnhancedAirbyteManager = Depends(get_airbyte_manager)
):
    """
    Trigger Asana data synchronization
    """
    try:
        if request.force_sync or request.sync_type == "full":
            # Trigger full pipeline setup
            background_tasks.add_task(
                _run_full_sync_pipeline,
                airbyte
            )
            
            return JSONResponse(content={
                "message": "Full Asana sync initiated",
                "sync_type": "full",
                "status": "initiated"
            })
        else:
            # Trigger incremental sync
            # This would typically trigger an existing connection
            health_status = await airbyte.perform_health_check()
            
            return JSONResponse(content={
                "message": "Incremental sync status checked",
                "sync_type": "incremental",
                "health_status": health_status
            })
        
    except Exception as e:
        logger.error(f"Failed to trigger sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync/status")
async def get_sync_status(
    airbyte: EnhancedAirbyteManager = Depends(get_airbyte_manager)
):
    """
    Get current synchronization status
    """
    try:
        health_status = await airbyte.perform_health_check()
        data_quality = await airbyte.validate_asana_data_quality()
        
        return JSONResponse(content={
            "health_status": health_status,
            "data_quality": {
                "quality_score": data_quality.quality_score,
                "total_records": data_quality.total_records,
                "valid_records": data_quality.valid_records,
                "validation_timestamp": data_quality.validation_timestamp.isoformat() if data_quality.validation_timestamp else None,
                "issues": data_quality.issues
            },
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ANALYTICS AND INSIGHTS ENDPOINTS

@router.get("/analytics/summary")
async def get_analytics_summary(
    time_period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    cortex: SnowflakeCortexService = Depends(get_cortex_service)
):
    """
    Get high-level analytics summary
    """
    try:
        # Calculate time filter
        days = int(time_period.replace('d', ''))
        
        query = f"""
        WITH project_summary AS (
            SELECT 
                COUNT(*) as total_projects,
                COUNT(CASE WHEN IS_ARCHIVED = FALSE THEN 1 END) as active_projects,
                AVG(COMPLETION_PERCENTAGE) as avg_completion,
                AVG(AI_HEALTH_SCORE) as avg_health_score,
                COUNT(CASE WHEN AI_RISK_ASSESSMENT = 'HIGH' OR AI_RISK_ASSESSMENT = 'CRITICAL' THEN 1 END) as high_risk_projects
            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS
            WHERE MODIFIED_AT >= CURRENT_DATE - {days}
        ),
        task_summary AS (
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,
                COUNT(CASE WHEN TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,
                AVG(AI_URGENCY_SCORE) as avg_urgency_score
            FROM STG_TRANSFORMED.STG_ASANA_TASKS
            WHERE MODIFIED_AT >= CURRENT_DATE - {days}
        ),
        team_summary AS (
            SELECT 
                COUNT(DISTINCT TEAM_NAME) as active_teams,
                AVG(COMPLETION_PERCENTAGE) as team_avg_completion
            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS
            WHERE IS_ARCHIVED = FALSE
            AND TEAM_NAME IS NOT NULL
        )
        SELECT 
            (SELECT OBJECT_CONSTRUCT(*) FROM project_summary) as projects,
            (SELECT OBJECT_CONSTRUCT(*) FROM task_summary) as tasks,
            (SELECT OBJECT_CONSTRUCT(*) FROM team_summary) as teams
        """
        
        result = await cortex.execute_query(query)
        
        if result.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified time period")
        
        row = result.iloc[0]
        projects = json.loads(row["PROJECTS"])
        tasks = json.loads(row["TASKS"])
        teams = json.loads(row["TEAMS"])
        
        return JSONResponse(content={
            "time_period": time_period,
            "summary": {
                "projects": projects,
                "tasks": tasks,
                "teams": teams
            },
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint for Asana integration
    """
    try:
        # Check if services are initialized
        services_status = {
            "intelligence_agent": intelligence_agent is not None,
            "chat_service": chat_service is not None,
            "airbyte_manager": airbyte_manager is not None,
            "cortex_service": cortex_service is not None
        }
        
        all_services_healthy = all(services_status.values())
        
        return JSONResponse(content={
            "status": "healthy" if all_services_healthy else "degraded",
            "services": services_status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def _run_full_sync_pipeline(airbyte_manager: EnhancedAirbyteManager):
    """Background task to run full sync pipeline"""
    try:
        logger.info("Starting full Asana sync pipeline")
        results = await airbyte_manager.setup_complete_asana_pipeline()
        
        success_count = sum(1 for result in results.values() if result.status.value == "success")
        total_count = len(results)
        
        logger.info(f"Full sync pipeline completed: {success_count}/{total_count} successful")
        
    except Exception as e:
        logger.error(f"Full sync pipeline failed: {e}")

# Cleanup function for application shutdown
async def cleanup_asana_services():
    """Cleanup function to be called on application shutdown"""
    global intelligence_agent, chat_service, airbyte_manager, cortex_service, ai_memory_service
    
    try:
        if intelligence_agent:
            await intelligence_agent.close()
        if chat_service:
            await chat_service.close()
        if airbyte_manager:
            await airbyte_manager.cleanup()
        if cortex_service:
            await cortex_service.close()
        if ai_memory_service:
            await ai_memory_service.close()
            
        logger.info("✅ Asana services cleaned up successfully")
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up Asana services: {e}")

# Export router and cleanup function
__all__ = ["router", "cleanup_asana_services"]
