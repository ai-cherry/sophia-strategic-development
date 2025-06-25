"""
Slack & Linear Knowledge API Routes
Provides endpoints for Slack conversation and Linear issue knowledge management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.auth import get_current_user
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.mcp.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer
from backend.core.cache_manager import DashboardCacheManager
from backend.core.logger import logger

router = APIRouter(prefix="/api/v1/knowledge", tags=["slack-linear-knowledge"])

# Initialize services
cortex_service = SnowflakeCortexService()
ai_memory = EnhancedAiMemoryMCPServer()
cache_manager = DashboardCacheManager()


# =====================================================================
# SLACK KNOWLEDGE ENDPOINTS
# =====================================================================


@router.get("/slack/stats")
async def get_slack_stats(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get Slack knowledge statistics"""
    try:
        cache_key = f"slack_stats:{user_id}"

        async def fetch_stats():
            query = """
            SELECT 
                COUNT(DISTINCT CONVERSATION_ID) as total_conversations,
                COUNT(DISTINCT MESSAGE_ID) as total_messages,
                COUNT(DISTINCT CHANNEL_ID) as active_channels,
                COUNT(DISTINCT USER_ID) as active_users,
                AVG(BUSINESS_VALUE_SCORE) as avg_business_value,
                COUNT(CASE WHEN KNOWLEDGE_EXTRACTED = TRUE THEN 1 END) as conversations_with_insights,
                MAX(UPDATED_AT) as last_sync
            FROM SLACK_DATA.STG_SLACK_CONVERSATIONS
            WHERE CREATED_AT >= DATEADD('day', -30, CURRENT_DATE())
            """

            result = await cortex_service.execute_query(query)
            if result and len(result) > 0:
                row = result[0]
                return {
                    "total_conversations": row[0] or 0,
                    "total_messages": row[1] or 0,
                    "active_channels": row[2] or 0,
                    "active_users": row[3] or 0,
                    "avg_business_value": float(row[4]) if row[4] else 0.0,
                    "conversations_with_insights": row[5] or 0,
                    "last_sync": row[6].isoformat() if row[6] else None,
                }
            return {}

        stats = await cache_manager.get_or_set(cache_key, fetch_stats, ttl=300)
        return stats

    except Exception as e:
        logger.error(f"Error fetching Slack stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Slack statistics")


@router.get("/slack/conversations")
async def get_slack_conversations(
    channel_name: Optional[str] = Query(None, description="Filter by channel"),
    date_range_days: int = Query(30, description="Date range in days"),
    min_business_value: float = Query(0.5, description="Minimum business value score"),
    limit: int = Query(50, description="Maximum results to return"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get Slack conversations with filtering"""
    try:
        # Build WHERE conditions
        conditions = [
            f"CREATED_AT >= DATEADD('day', -{date_range_days}, CURRENT_DATE())",
            f"BUSINESS_VALUE_SCORE >= {min_business_value}",
        ]

        if channel_name:
            conditions.append(f"sc.CHANNEL_NAME = '{channel_name}'")

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT 
            conv.CONVERSATION_ID,
            conv.CONVERSATION_TITLE,
            conv.CONVERSATION_SUMMARY,
            sc.CHANNEL_NAME,
            conv.PARTICIPANT_COUNT,
            conv.MESSAGE_COUNT,
            conv.DURATION_MINUTES,
            conv.BUSINESS_VALUE_SCORE,
            conv.SENTIMENT_SCORE,
            conv.KEY_TOPICS,
            conv.DECISIONS_MADE,
            conv.ACTION_ITEMS,
            conv.KNOWLEDGE_EXTRACTED,
            conv.CREATED_AT
        FROM SLACK_DATA.STG_SLACK_CONVERSATIONS conv
        JOIN SLACK_DATA.STG_SLACK_CHANNELS sc ON conv.CHANNEL_ID = sc.CHANNEL_ID
        WHERE {where_clause}
        ORDER BY conv.BUSINESS_VALUE_SCORE DESC, conv.CREATED_AT DESC
        LIMIT {limit}
        """

        result = await cortex_service.execute_query(query)

        conversations = []
        if result:
            for row in result:
                conversations.append(
                    {
                        "id": row[0],
                        "title": row[1],
                        "summary": row[2],
                        "channel_name": row[3],
                        "participant_count": row[4],
                        "message_count": row[5],
                        "duration_minutes": row[6],
                        "business_value_score": float(row[7]) if row[7] else 0.0,
                        "sentiment_score": float(row[8]) if row[8] else 0.0,
                        "key_topics": row[9] if row[9] else [],
                        "decisions_made": row[10] if row[10] else [],
                        "action_items": row[11] if row[11] else [],
                        "knowledge_extracted": bool(row[12]),
                        "created_at": row[13].isoformat() if row[13] else None,
                    }
                )

        return {
            "conversations": conversations,
            "total_results": len(conversations),
            "filters": {
                "channel_name": channel_name,
                "date_range_days": date_range_days,
                "min_business_value": min_business_value,
            },
        }

    except Exception as e:
        logger.error(f"Error fetching Slack conversations: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch Slack conversations"
        )


@router.get("/slack/insights")
async def get_slack_insights(
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    confidence_threshold: float = Query(0.7, description="Minimum confidence score"),
    limit: int = Query(20, description="Maximum results to return"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get Slack knowledge insights"""
    try:
        conditions = [f"CONFIDENCE_SCORE >= {confidence_threshold}"]

        if insight_type:
            conditions.append(f"INSIGHT_TYPE = '{insight_type}'")

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT 
            INSIGHT_ID,
            INSIGHT_TYPE,
            INSIGHT_TITLE,
            INSIGHT_DESCRIPTION,
            CONFIDENCE_SCORE,
            BUSINESS_IMPACT,
            IS_ACTIONABLE,
            HUMAN_VALIDATED,
            CONVERSATION_ID,
            EXTRACTED_AT
        FROM SLACK_DATA.SLACK_KNOWLEDGE_INSIGHTS
        WHERE {where_clause}
        ORDER BY CONFIDENCE_SCORE DESC, EXTRACTED_AT DESC
        LIMIT {limit}
        """

        result = await cortex_service.execute_query(query)

        insights = []
        if result:
            for row in result:
                insights.append(
                    {
                        "id": row[0],
                        "type": row[1],
                        "title": row[2],
                        "description": row[3],
                        "confidence_score": float(row[4]) if row[4] else 0.0,
                        "business_impact": row[5],
                        "actionable": bool(row[6]),
                        "human_validated": bool(row[7]),
                        "conversation_id": row[8],
                        "extracted_at": row[9].isoformat() if row[9] else None,
                    }
                )

        return {
            "insights": insights,
            "total_results": len(insights),
            "filters": {
                "insight_type": insight_type,
                "confidence_threshold": confidence_threshold,
            },
        }

    except Exception as e:
        logger.error(f"Error fetching Slack insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Slack insights")


@router.get("/slack/search")
async def search_slack_knowledge(
    query: str = Query(..., description="Search query"),
    channel_name: Optional[str] = Query(None, description="Filter by channel"),
    date_range_days: int = Query(30, description="Date range in days"),
    limit: int = Query(10, description="Maximum results to return"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Search Slack knowledge using AI Memory"""
    try:
        # Use AI Memory for semantic search
        results = await ai_memory.recall_slack_insights(
            query=query,
            channel_name=channel_name,
            date_range_days=date_range_days,
            limit=limit,
        )

        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_type": "semantic",
        }

    except Exception as e:
        logger.error(f"Error searching Slack knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search Slack knowledge")


@router.post("/slack/sync")
async def sync_slack_data(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Trigger Slack data synchronization"""
    try:
        # Check admin permissions
        if not await _check_admin_permissions(user_id):
            raise HTTPException(status_code=403, detail="Admin permissions required")

        # Trigger transformation pipeline
        from backend.scripts.transform_slack_linear_data import (
            SlackLinearTransformationService,
        )

        transformation_service = SlackLinearTransformationService()
        await transformation_service.initialize()

        try:
            results = await transformation_service.run_full_slack_pipeline()

            # Invalidate cache
            await cache_manager.invalidate_pattern("slack_*")

            return {
                "status": "success",
                "message": "Slack data synchronization completed",
                "results": {
                    "messages": results.get("messages", {}).processed_records,
                    "conversations": results.get("conversations", {}).processed_records,
                    "cortex_processing": results.get("cortex", {}).processed_records,
                    "insights": results.get("insights", {}).processed_records,
                },
            }

        finally:
            await transformation_service.close()

    except Exception as e:
        logger.error(f"Slack sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to sync Slack data")


# =====================================================================
# LINEAR KNOWLEDGE ENDPOINTS
# =====================================================================


@router.get("/linear/stats")
async def get_linear_stats(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get Linear knowledge statistics"""
    try:
        cache_key = f"linear_stats:{user_id}"

        async def fetch_stats():
            # Main stats query
            stats_query = """
            SELECT 
                COUNT(*) as total_issues,
                COUNT(CASE WHEN STATUS NOT IN ('Done', 'Canceled') THEN 1 END) as active_issues,
                COUNT(CASE WHEN STATUS = 'Done' THEN 1 END) as completed_issues,
                AVG(CASE WHEN CYCLE_TIME_DAYS IS NOT NULL THEN CYCLE_TIME_DAYS END) as avg_cycle_time,
                MAX(UPDATED_AT) as last_sync
            FROM LINEAR_DATA.STG_LINEAR_ISSUES
            WHERE CREATED_AT >= DATEADD('day', -90, CURRENT_DATE())
            """

            # Project stats query
            project_query = """
            SELECT 
                PROJECT_NAME,
                COUNT(*) as issue_count,
                COUNT(CASE WHEN STATUS = 'Done' THEN 1 END)::FLOAT / COUNT(*) as completion_rate,
                AVG(CASE WHEN CYCLE_TIME_DAYS IS NOT NULL THEN CYCLE_TIME_DAYS END) as avg_cycle_time
            FROM LINEAR_DATA.STG_LINEAR_ISSUES
            WHERE CREATED_AT >= DATEADD('day', -90, CURRENT_DATE())
            GROUP BY PROJECT_NAME
            """

            # Priority distribution query
            priority_query = """
            SELECT 
                PRIORITY,
                COUNT(*) as count
            FROM LINEAR_DATA.STG_LINEAR_ISSUES
            WHERE CREATED_AT >= DATEADD('day', -30, CURRENT_DATE())
            GROUP BY PRIORITY
            """

            stats_result = await cortex_service.execute_query(stats_query)
            project_result = await cortex_service.execute_query(project_query)
            priority_result = await cortex_service.execute_query(priority_query)

            # Process results
            main_stats = {}
            if stats_result and len(stats_result) > 0:
                row = stats_result[0]
                main_stats = {
                    "total_issues": row[0] or 0,
                    "active_issues": row[1] or 0,
                    "completed_issues": row[2] or 0,
                    "avg_cycle_time": float(row[3]) if row[3] else 0.0,
                    "last_sync": row[4].isoformat() if row[4] else None,
                }

            # Process project stats
            projects = {}
            if project_result:
                for row in project_result:
                    projects[row[0]] = {
                        "issue_count": row[1],
                        "completion_rate": float(row[2]) if row[2] else 0.0,
                        "avg_cycle_time": float(row[3]) if row[3] else 0.0,
                    }

            # Process priority distribution
            priority_distribution = {}
            if priority_result:
                for row in priority_result:
                    priority_distribution[row[0].lower()] = row[1]

            # Calculate team velocity (issues per week)
            velocity_query = """
            SELECT COUNT(*) / 4.0 as issues_per_week
            FROM LINEAR_DATA.STG_LINEAR_ISSUES
            WHERE CREATED_AT >= DATEADD('week', -4, CURRENT_DATE())
            """

            velocity_result = await cortex_service.execute_query(velocity_query)
            issues_per_week = (
                float(velocity_result[0][0])
                if velocity_result and velocity_result[0][0]
                else 0.0
            )

            return {
                **main_stats,
                "projects": projects,
                "priority_distribution": priority_distribution,
                "team_velocity": {
                    "issues_per_week": issues_per_week,
                    "completion_trend": 0.0,  # TODO: Calculate trend
                },
            }

        stats = await cache_manager.get_or_set(cache_key, fetch_stats, ttl=300)
        return stats

    except Exception as e:
        logger.error(f"Error fetching Linear stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Linear statistics")


@router.get("/linear/issues")
async def get_linear_issues(
    project_name: Optional[str] = Query(None, description="Filter by project"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    limit: int = Query(50, description="Maximum results to return"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get Linear issues with filtering"""
    try:
        # Build WHERE conditions
        conditions = ["1=1"]  # Base condition

        if project_name:
            conditions.append(f"PROJECT_NAME = '{project_name}'")
        if priority:
            conditions.append(f"PRIORITY = '{priority}'")
        if status:
            conditions.append(f"STATUS = '{status}'")
        if assignee:
            conditions.append(f"ASSIGNEE_NAME = '{assignee}'")

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT 
            ISSUE_ID,
            ISSUE_TITLE,
            ISSUE_DESCRIPTION,
            STATUS,
            PRIORITY,
            PROJECT_NAME,
            ASSIGNEE_NAME,
            LABELS,
            CYCLE_TIME_DAYS,
            CREATED_AT,
            UPDATED_AT
        FROM LINEAR_DATA.STG_LINEAR_ISSUES
        WHERE {where_clause}
        ORDER BY 
            CASE PRIORITY 
                WHEN 'Urgent' THEN 1 
                WHEN 'High' THEN 2 
                WHEN 'Medium' THEN 3 
                WHEN 'Low' THEN 4 
                ELSE 5 
            END,
            UPDATED_AT DESC
        LIMIT {limit}
        """

        result = await cortex_service.execute_query(query)

        issues = []
        if result:
            for row in result:
                issues.append(
                    {
                        "id": row[0],
                        "title": row[1],
                        "description": row[2],
                        "status": row[3],
                        "priority": row[4],
                        "project_name": row[5],
                        "assignee": row[6],
                        "labels": row[7] if row[7] else [],
                        "cycle_time_days": float(row[8]) if row[8] else None,
                        "created_at": row[9].isoformat() if row[9] else None,
                        "updated_at": row[10].isoformat() if row[10] else None,
                    }
                )

        return {
            "issues": issues,
            "total_results": len(issues),
            "filters": {
                "project_name": project_name,
                "priority": priority,
                "status": status,
                "assignee": assignee,
            },
        }

    except Exception as e:
        logger.error(f"Error fetching Linear issues: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Linear issues")


@router.get("/linear/insights")
async def get_linear_insights(
    project_name: Optional[str] = Query(None, description="Filter by project"),
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    limit: int = Query(20, description="Maximum results to return"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get Linear development insights"""
    try:
        # Generate insights from Linear data
        insights = []

        # Velocity insights
        velocity_query = """
        SELECT 
            PROJECT_NAME,
            COUNT(*) as issues_completed,
            AVG(CYCLE_TIME_DAYS) as avg_cycle_time
        FROM LINEAR_DATA.STG_LINEAR_ISSUES
        WHERE STATUS = 'Done'
        AND UPDATED_AT >= DATEADD('week', -2, CURRENT_DATE())
        GROUP BY PROJECT_NAME
        """

        velocity_result = await cortex_service.execute_query(velocity_query)

        if velocity_result:
            for row in velocity_result:
                if not project_name or row[0] == project_name:
                    insights.append(
                        {
                            "id": f"velocity_{row[0]}",
                            "type": "velocity",
                            "title": f"Team Velocity - {row[0]}",
                            "description": f"Completed {row[1]} issues with average cycle time of {row[2]:.1f} days",
                            "confidence_score": 0.9,
                            "business_impact": "medium",
                            "project_name": row[0],
                            "created_at": datetime.now().isoformat(),
                            "actionable": True,
                        }
                    )

        # Bottleneck insights
        bottleneck_query = """
        SELECT 
            STATUS,
            COUNT(*) as issue_count,
            AVG(DATEDIFF('day', CREATED_AT, CURRENT_DATE())) as avg_age_days
        FROM LINEAR_DATA.STG_LINEAR_ISSUES
        WHERE STATUS NOT IN ('Done', 'Canceled')
        GROUP BY STATUS
        HAVING COUNT(*) > 5
        ORDER BY avg_age_days DESC
        """

        bottleneck_result = await cortex_service.execute_query(bottleneck_query)

        if bottleneck_result:
            for row in bottleneck_result:
                if row[2] > 14:  # Issues older than 2 weeks
                    insights.append(
                        {
                            "id": f"bottleneck_{row[0]}",
                            "type": "bottleneck",
                            "title": f"Potential Bottleneck in {row[0]}",
                            "description": f"{row[1]} issues in {row[0]} status with average age of {row[2]:.1f} days",
                            "confidence_score": 0.8,
                            "business_impact": "high",
                            "project_name": "Multiple",
                            "created_at": datetime.now().isoformat(),
                            "actionable": True,
                        }
                    )

        # Filter by insight type if specified
        if insight_type:
            insights = [i for i in insights if i["type"] == insight_type]

        return {
            "insights": insights[:limit],
            "total_results": len(insights),
            "filters": {"project_name": project_name, "insight_type": insight_type},
        }

    except Exception as e:
        logger.error(f"Error fetching Linear insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Linear insights")


@router.get("/linear/search")
async def search_linear_knowledge(
    query: str = Query(..., description="Search query"),
    project_name: Optional[str] = Query(None, description="Filter by project"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, description="Maximum results to return"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Search Linear knowledge using AI Memory"""
    try:
        # Use AI Memory for semantic search
        results = await ai_memory.recall_linear_issue_details(
            query=query,
            project_name=project_name,
            priority=priority,
            status=status,
            limit=limit,
        )

        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_type": "semantic",
        }

    except Exception as e:
        logger.error(f"Error searching Linear knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search Linear knowledge")


@router.post("/linear/sync")
async def sync_linear_data(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Trigger Linear data synchronization"""
    try:
        # Check admin permissions
        if not await _check_admin_permissions(user_id):
            raise HTTPException(status_code=403, detail="Admin permissions required")

        # Trigger transformation pipeline
        from backend.scripts.transform_slack_linear_data import (
            SlackLinearTransformationService,
        )

        transformation_service = SlackLinearTransformationService()
        await transformation_service.initialize()

        try:
            results = await transformation_service.run_full_linear_pipeline()

            # Invalidate cache
            await cache_manager.invalidate_pattern("linear_*")

            return {
                "status": "success",
                "message": "Linear data synchronization completed",
                "results": {
                    "issues": results.get("issues", {}).processed_records,
                    "cortex_processing": results.get("cortex", {}).processed_records,
                },
            }

        finally:
            await transformation_service.close()

    except Exception as e:
        logger.error(f"Linear sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to sync Linear data")


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================


async def _check_admin_permissions(user_id: str) -> bool:
    """Check if user has admin permissions"""
    # TODO: Implement proper role-based access control
    # For now, allow all authenticated users
    return True
