#!/usr/bin/env python3
"""
CEO Dashboard API Routes for Sophia AI Platform
==============================================

Comprehensive API endpoints for CEO dashboard including:
1. Chat/Search Interface with natural language processing
2. Project Management Dashboard (Linear + Asana + Notion)
3. Sales Coach Agent (Slack + HubSpot + Gong.io)
4. Real-time business intelligence and executive insights
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.services.ceo_dashboard_service import get_ceo_dashboard_service, QueryType
from backend.services.mcp_orchestration_service import get_orchestration_service
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class CEOChatRequest(BaseModel):
    """CEO chat/search request"""
    query: str = Field(..., description="Natural language query from CEO")
    query_type: Optional[str] = Field(None, description="Optional query type classification")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    include_recommendations: bool = Field(True, description="Include AI recommendations")
    include_visualizations: bool = Field(True, description="Include data for visualizations")

class CEOChatResponse(BaseModel):
    """CEO chat/search response"""
    success: bool
    query: str
    query_type: str
    response: str
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    data: Dict[str, Any]
    visualizations: Optional[Dict[str, Any]] = None
    timestamp: str
    processing_time_ms: int

class ProjectManagementRequest(BaseModel):
    """Project management query request"""
    query: Optional[str] = Field(None, description="Specific project query")
    platforms: List[str] = Field(default=["Linear", "Asana", "Notion"], description="Platforms to query")
    include_health_metrics: bool = Field(True, description="Include project health analysis")
    include_risk_assessment: bool = Field(True, description="Include risk assessment")
    date_range_days: int = Field(30, description="Date range for analysis in days")

class SalesCoachingRequest(BaseModel):
    """Sales coaching query request"""
    query: Optional[str] = Field(None, description="Specific sales coaching query")
    rep_name: Optional[str] = Field(None, description="Focus on specific sales rep")
    deal_id: Optional[str] = Field(None, description="Focus on specific deal")
    include_call_analysis: bool = Field(True, description="Include Gong call analysis")
    include_hubspot_data: bool = Field(True, description="Include HubSpot CRM data")
    include_slack_activity: bool = Field(True, description="Include Slack sales activity")

class DashboardSummaryResponse(BaseModel):
    """Dashboard summary response"""
    executive_summary: Dict[str, Any]
    critical_alerts: List[Dict[str, Any]]
    key_metrics: Dict[str, Any]
    recent_insights: List[Dict[str, Any]]
    quick_actions: List[Dict[str, Any]]
    last_updated: str

# Create router
router = APIRouter(prefix="/api/v1/ceo", tags=["CEO Dashboard"])

# Dependency to get services
async def get_ceo_service():
    """Get CEO dashboard service"""
    service = get_ceo_dashboard_service()
    if not hasattr(service, '_initialized'):
        await service.initialize()
        service._initialized = True
    return service

@router.post("/chat", response_model=CEOChatResponse)
async def ceo_chat_interface(
    request: CEOChatRequest,
    service = Depends(get_ceo_service)
) -> CEOChatResponse:
    """
    CEO Chat/Search Interface
    
    Natural language interface for CEO to query business data across all platforms.
    Supports:
    - Business intelligence queries
    - Project management questions
    - Sales coaching inquiries
    - Financial analysis requests
    - Team performance questions
    - Strategic planning discussions
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"🎯 CEO Chat Query: '{request.query}'")
        
        # Parse query type if provided
        query_type = None
        if request.query_type:
            try:
                query_type = QueryType(request.query_type.lower())
            except ValueError:
                logger.warning(f"Invalid query type: {request.query_type}")
        
        # Process the query
        result = await service.process_ceo_query(
            query=request.query,
            query_type=query_type
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Query processing failed: {result.get('error', 'Unknown error')}"
            )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Extract response components
        response_text = result.get("ai_analysis", result.get("coaching_analysis", result.get("bi_analysis", result.get("response", ""))))
        
        # Format insights
        insights = []
        if "summary_metrics" in result:
            insights.append({
                "type": "metrics",
                "title": "Summary Metrics",
                "data": result["summary_metrics"]
            })
        
        if "sales_metrics" in result:
            insights.append({
                "type": "sales",
                "title": "Sales Metrics",
                "data": result["sales_metrics"]
            })
        
        # Extract recommendations
        recommendations = []
        if "coaching_recommendations" in result:
            recommendations.extend([rec.get("recommendation", "") for rec in result["coaching_recommendations"]])
        
        # Prepare visualization data
        visualizations = None
        if request.include_visualizations:
            visualizations = await _prepare_visualization_data(result, request.query_type or result.get("query_type"))
        
        response = CEOChatResponse(
            success=True,
            query=request.query,
            query_type=result.get("query_type", "general"),
            response=response_text,
            insights=insights,
            recommendations=recommendations,
            data=result,
            visualizations=visualizations,
            timestamp=datetime.now().isoformat(),
            processing_time_ms=int(processing_time)
        )
        
        logger.info(f"✅ CEO Chat completed in {processing_time:.1f}ms")
        return response
        
    except Exception as e:
        logger.error(f"CEO chat error: {e}")
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return CEOChatResponse(
            success=False,
            query=request.query,
            query_type="error",
            response=f"I apologize, but I encountered an error processing your request: {str(e)}",
            insights=[],
            recommendations=["Please try rephrasing your question", "Check system status", "Contact support if issue persists"],
            data={"error": str(e)},
            timestamp=datetime.now().isoformat(),
            processing_time_ms=int(processing_time)
        )

@router.get("/chat/stream")
async def ceo_chat_stream(
    query: str = Query(..., description="CEO query"),
    query_type: Optional[str] = Query(None, description="Query type"),
    service = Depends(get_ceo_service)
):
    """
    Streaming CEO Chat Interface
    
    Server-sent events stream for real-time CEO chat responses.
    """
    async def generate_stream():
        try:
            yield f"data: {json.dumps({'type': 'start', 'message': 'Processing your query...'})}\n\n"
            
            # Parse query type
            parsed_query_type = None
            if query_type:
                try:
                    parsed_query_type = QueryType(query_type.lower())
                except ValueError:
                    pass
            
            # Process query
            result = await service.process_ceo_query(query, parsed_query_type)
            
            if result.get("success", False):
                # Stream the response
                response_text = result.get("ai_analysis", result.get("response", ""))
                
                # Split response into chunks for streaming
                words = response_text.split()
                chunk_size = 10
                
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size])
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                    await asyncio.sleep(0.1)  # Small delay for streaming effect
                
                # Send final data
                yield f"data: {json.dumps({'type': 'data', 'result': result})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': result.get('error', 'Unknown error')})}\n\n"
            
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.post("/projects")
async def project_management_dashboard(
    request: ProjectManagementRequest,
    service = Depends(get_ceo_service)
) -> Dict[str, Any]:
    """
    Project Management Dashboard
    
    Comprehensive project management view across Linear, Asana, and Notion.
    Provides project health monitoring, risk assessment, and team analytics.
    """
    try:
        logger.info(f"📊 Project Management Query: {request.query or 'Dashboard Summary'}")
        
        # If specific query provided, use chat interface
        if request.query:
            result = await service.process_ceo_query(
                query=request.query,
                query_type=QueryType.PROJECT_MANAGEMENT
            )
        else:
            # Get comprehensive project dashboard
            linear_projects = await service._get_linear_projects()
            asana_projects = await service._get_asana_projects()
            notion_projects = await service._get_notion_projects()
            
            all_projects = linear_projects + asana_projects + notion_projects
            
            # Calculate summary metrics
            total_projects = len(all_projects)
            avg_health_score = sum(p.health_score for p in all_projects) / total_projects if total_projects > 0 else 0
            at_risk_projects = [p for p in all_projects if p.health_score < 70]
            completed_projects = [p for p in all_projects if p.completion_percentage >= 100]
            
            # Platform breakdown
            platform_breakdown = {
                "Linear": len(linear_projects),
                "Asana": len(asana_projects),
                "Notion": len(notion_projects)
            }
            
            result = {
                "success": True,
                "summary_metrics": {
                    "total_projects": total_projects,
                    "average_health_score": round(avg_health_score, 1),
                    "at_risk_projects": len(at_risk_projects),
                    "completed_projects": len(completed_projects),
                    "platform_breakdown": platform_breakdown
                },
                "projects": [p.__dict__ for p in all_projects],
                "at_risk_projects": [p.__dict__ for p in at_risk_projects],
                "health_distribution": _calculate_health_distribution(all_projects),
                "completion_trends": _calculate_completion_trends(all_projects),
                "team_workload": _calculate_team_workload(all_projects),
                "timestamp": datetime.now().isoformat()
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Project management dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sales-coaching")
async def sales_coaching_dashboard(
    request: SalesCoachingRequest,
    service = Depends(get_ceo_service)
) -> Dict[str, Any]:
    """
    Sales Coaching Dashboard
    
    AI-powered sales coaching insights using data from Slack, HubSpot, and Gong.io.
    Provides deal analysis, rep performance, and coaching recommendations.
    """
    try:
        logger.info(f"💼 Sales Coaching Query: {request.query or 'Dashboard Summary'}")
        
        # If specific query provided, use chat interface
        if request.query:
            result = await service.process_ceo_query(
                query=request.query,
                query_type=QueryType.SALES_COACHING
            )
        else:
            # Get comprehensive sales coaching dashboard
            hubspot_deals = await service._get_hubspot_deals()
            gong_insights = await service._get_gong_insights()
            slack_activity = await service._get_slack_sales_activity()
            coaching_recommendations = await service._generate_coaching_recommendations(hubspot_deals, gong_insights)
            
            # Calculate sales metrics
            total_pipeline_value = sum(deal.get("amount", 0) for deal in hubspot_deals)
            high_probability_deals = [deal for deal in hubspot_deals if deal.get("probability", 0) > 70]
            recent_calls = len([insight for insight in gong_insights if insight.get("date", "") >= (datetime.now() - timedelta(days=7)).isoformat()])
            
            # Rep performance analysis
            rep_performance = _analyze_rep_performance(hubspot_deals, gong_insights)
            
            result = {
                "success": True,
                "sales_metrics": {
                    "total_pipeline_value": total_pipeline_value,
                    "active_deals": len(hubspot_deals),
                    "high_probability_deals": len(high_probability_deals),
                    "recent_calls_analyzed": recent_calls,
                    "coaching_opportunities": len(coaching_recommendations)
                },
                "deals": hubspot_deals,
                "gong_insights": gong_insights,
                "coaching_recommendations": [rec.__dict__ for rec in coaching_recommendations],
                "rep_performance": rep_performance,
                "pipeline_health": _calculate_pipeline_health(hubspot_deals),
                "call_sentiment_trends": _analyze_call_sentiment(gong_insights),
                "timestamp": datetime.now().isoformat()
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Sales coaching dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    service = Depends(get_ceo_service)
) -> DashboardSummaryResponse:
    """
    CEO Dashboard Summary
    
    High-level executive dashboard with key metrics, alerts, and quick actions.
    """
    try:
        logger.info("📈 Getting CEO dashboard summary")
        
        # Get comprehensive dashboard data
        dashboard_data = await service.get_dashboard_summary()
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=500, detail=dashboard_data["error"])
        
        # Extract critical alerts
        critical_alerts = []
        for insight in dashboard_data.get("insights", []):
            if insight.get("priority") == "critical":
                critical_alerts.append({
                    "title": insight.get("title", ""),
                    "message": insight.get("summary", ""),
                    "category": insight.get("category", ""),
                    "timestamp": insight.get("created_at", "")
                })
        
        # Calculate key metrics
        key_metrics = {
            "projects": {
                "total": dashboard_data["executive_summary"]["projects_tracked"],
                "at_risk": dashboard_data["executive_summary"]["at_risk_projects"],
                "health_percentage": 85.0  # Calculate from actual data
            },
            "sales": {
                "opportunities": dashboard_data["executive_summary"]["sales_opportunities"],
                "pipeline_value": 0,  # Get from actual data
                "win_rate": 0.35  # Calculate from actual data
            },
            "team": {
                "productivity_score": 87.5,  # Get from actual data
                "satisfaction_score": 92.0,  # Get from actual data
                "utilization_rate": 78.5   # Get from actual data
            }
        }
        
        response = DashboardSummaryResponse(
            executive_summary=dashboard_data["executive_summary"],
            critical_alerts=critical_alerts,
            key_metrics=key_metrics,
            recent_insights=dashboard_data.get("insights", [])[:5],
            quick_actions=dashboard_data.get("quick_actions", []),
            last_updated=dashboard_data["executive_summary"]["last_updated"]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for CEO dashboard services"""
    try:
        # Check MCP services
        mcp_service = get_orchestration_service()
        mcp_health = await mcp_service.health_check()
        
        # Check Snowflake
        cortex_service = SnowflakeCortexService()
        snowflake_health = await cortex_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "mcp_orchestration": mcp_health,
                "snowflake_cortex": snowflake_health,
                "ceo_dashboard": "operational"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/insights/refresh")
async def refresh_insights(
    background_tasks: BackgroundTasks,
    service = Depends(get_ceo_service)
) -> Dict[str, Any]:
    """Refresh dashboard insights and cache"""
    try:
        # Add background task to refresh cache
        background_tasks.add_task(service._refresh_dashboard_cache)
        
        return {
            "success": True,
            "message": "Dashboard refresh initiated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Insights refresh error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for data analysis
async def _prepare_visualization_data(result: Dict[str, Any], query_type: str) -> Dict[str, Any]:
    """Prepare data for dashboard visualizations"""
    visualizations = {}
    
    try:
        if query_type == "project_management":
            if "projects" in result:
                projects = result["projects"]
                
                # Health score distribution
                health_scores = [p.get("health_score", 0) for p in projects]
                visualizations["health_distribution"] = {
                    "type": "histogram",
                    "data": health_scores,
                    "bins": [0, 50, 70, 85, 100],
                    "labels": ["Critical", "At Risk", "Moderate", "Healthy"]
                }
                
                # Platform breakdown
                platform_counts = {}
                for project in projects:
                    platform = project.get("platform", "Unknown")
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                visualizations["platform_breakdown"] = {
                    "type": "pie",
                    "data": platform_counts
                }
        
        elif query_type == "sales_coaching":
            if "deals" in result:
                deals = result["deals"]
                
                # Pipeline by stage
                stage_values = {}
                for deal in deals:
                    stage = deal.get("dealstage", "Unknown")
                    amount = deal.get("amount", 0)
                    stage_values[stage] = stage_values.get(stage, 0) + amount
                
                visualizations["pipeline_by_stage"] = {
                    "type": "bar",
                    "data": stage_values
                }
        
        return visualizations
        
    except Exception as e:
        logger.warning(f"Visualization preparation error: {e}")
        return {}

def _calculate_health_distribution(projects: List[Any]) -> Dict[str, int]:
    """Calculate project health distribution"""
    distribution = {"Critical": 0, "At Risk": 0, "Moderate": 0, "Healthy": 0}
    
    for project in projects:
        health_score = project.health_score
        if health_score < 50:
            distribution["Critical"] += 1
        elif health_score < 70:
            distribution["At Risk"] += 1
        elif health_score < 85:
            distribution["Moderate"] += 1
        else:
            distribution["Healthy"] += 1
    
    return distribution

def _calculate_completion_trends(projects: List[Any]) -> Dict[str, Any]:
    """Calculate project completion trends"""
    completion_percentages = [p.completion_percentage for p in projects]
    avg_completion = sum(completion_percentages) / len(completion_percentages) if completion_percentages else 0
    
    return {
        "average_completion": round(avg_completion, 1),
        "completed_projects": len([p for p in projects if p.completion_percentage >= 100]),
        "in_progress": len([p for p in projects if 0 < p.completion_percentage < 100]),
        "not_started": len([p for p in projects if p.completion_percentage == 0])
    }

def _calculate_team_workload(projects: List[Any]) -> Dict[str, Any]:
    """Calculate team workload distribution"""
    team_workload = {}
    
    for project in projects:
        for member in project.team_members:
            if member not in team_workload:
                team_workload[member] = {"projects": 0, "total_health": 0}
            team_workload[member]["projects"] += 1
            team_workload[member]["total_health"] += project.health_score
    
    # Calculate average health per team member
    for member in team_workload:
        workload = team_workload[member]
        workload["average_health"] = workload["total_health"] / workload["projects"]
    
    return team_workload

def _analyze_rep_performance(deals: List[Dict], insights: List[Dict]) -> Dict[str, Any]:
    """Analyze sales rep performance"""
    rep_performance = {}
    
    for deal in deals:
        rep = deal.get("owner_name", "Unknown")
        if rep not in rep_performance:
            rep_performance[rep] = {
                "deals": 0,
                "total_value": 0,
                "avg_probability": 0,
                "call_insights": 0
            }
        
        rep_performance[rep]["deals"] += 1
        rep_performance[rep]["total_value"] += deal.get("amount", 0)
        rep_performance[rep]["avg_probability"] += deal.get("probability", 0)
    
    # Calculate averages
    for rep in rep_performance:
        perf = rep_performance[rep]
        if perf["deals"] > 0:
            perf["avg_probability"] = perf["avg_probability"] / perf["deals"]
            perf["avg_deal_size"] = perf["total_value"] / perf["deals"]
    
    return rep_performance

def _calculate_pipeline_health(deals: List[Dict]) -> Dict[str, Any]:
    """Calculate overall pipeline health"""
    total_value = sum(deal.get("amount", 0) for deal in deals)
    weighted_probability = sum(deal.get("amount", 0) * deal.get("probability", 0) / 100 for deal in deals)
    expected_value = weighted_probability
    
    # Pipeline velocity (deals closed in last 30 days)
    recent_closes = len([deal for deal in deals if deal.get("dealstage", "").lower() in ["closed won", "closed"]])
    
    return {
        "total_pipeline_value": total_value,
        "expected_value": expected_value,
        "conversion_rate": expected_value / total_value if total_value > 0 else 0,
        "recent_closes": recent_closes,
        "average_deal_size": total_value / len(deals) if deals else 0
    }

def _analyze_call_sentiment(insights: List[Dict]) -> Dict[str, Any]:
    """Analyze call sentiment trends from Gong insights"""
    if not insights:
        return {"trend": "neutral", "average_sentiment": 0.0, "positive_calls": 0, "negative_calls": 0}
    
    sentiments = [insight.get("sentiment_score", 0) for insight in insights if "sentiment_score" in insight]
    
    if not sentiments:
        return {"trend": "no_data", "average_sentiment": 0.0, "positive_calls": 0, "negative_calls": 0}
    
    avg_sentiment = sum(sentiments) / len(sentiments)
    positive_calls = len([s for s in sentiments if s > 0.1])
    negative_calls = len([s for s in sentiments if s < -0.1])
    
    # Determine trend
    if avg_sentiment > 0.2:
        trend = "positive"
    elif avg_sentiment < -0.2:
        trend = "negative"
    else:
        trend = "neutral"
    
    return {
        "trend": trend,
        "average_sentiment": round(avg_sentiment, 2),
        "positive_calls": positive_calls,
        "negative_calls": negative_calls,
        "total_calls": len(sentiments)
    } 