#!/usr/bin/env python3
"""
CEO Dashboard Service for Sophia AI Platform
===========================================

Comprehensive CEO dashboard integrating:
1. Chat/Search Interface with AI-powered business intelligence
2. Project Management Dashboard (Linear + Asana + Notion)
3. Sales Coach Agent (Slack + HubSpot + Gong.io)
4. Real-time KPI monitoring and executive insights

Features:
- Real-time business intelligence aggregation
- Natural language query processing
- Cross-platform project health monitoring
- AI-powered sales coaching and insights
- Executive-level data visualization
- Predictive analytics and recommendations
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
from backend.core.auto_esc_config import get_config_value
from backend.services.mcp_orchestration_service import get_orchestration_service
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.services.smart_ai_service import SmartAIService

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of CEO dashboard queries"""
    BUSINESS_INTELLIGENCE = "business_intelligence"
    PROJECT_MANAGEMENT = "project_management"
    SALES_COACHING = "sales_coaching"
    FINANCIAL_ANALYSIS = "financial_analysis"
    TEAM_PERFORMANCE = "team_performance"
    STRATEGIC_PLANNING = "strategic_planning"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    OPERATIONAL_METRICS = "operational_metrics"

class PriorityLevel(Enum):
    """Priority levels for dashboard items"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

@dataclass
class CEOInsight:
    """Executive insight with context and recommendations"""
    title: str
    summary: str
    priority: PriorityLevel
    category: QueryType
    data_sources: List[str]
    key_metrics: Dict[str, Any]
    recommendations: List[str]
    trend_analysis: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0

@dataclass
class ProjectHealthSummary:
    """Comprehensive project health across platforms"""
    project_id: str
    project_name: str
    platform: str  # Linear, Asana, or Notion
    health_score: float  # 0-100
    completion_percentage: float
    team_members: List[str]
    key_milestones: List[Dict[str, Any]]
    risk_factors: List[str]
    predicted_completion: Optional[datetime]
    budget_status: Dict[str, Any]
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class SalesCoachingInsight:
    """Sales coaching recommendation with context"""
    rep_name: str
    deal_id: str
    deal_name: str
    coaching_type: str  # "opportunity", "risk", "process", "skill"
    insight: str
    recommendation: str
    priority: PriorityLevel
    data_sources: List[str]  # ["gong", "hubspot", "slack"]
    confidence_score: float
    expected_impact: str
    follow_up_actions: List[str]
    created_at: datetime = field(default_factory=datetime.now)

class CEODashboardService:
    """Comprehensive CEO dashboard service"""
    
    def __init__(self):
        self.mcp_service = get_orchestration_service()
        self.cortex_service = SnowflakeCortexService()
        self.ai_service = SmartAIService()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Cache for dashboard data
        self.insights_cache: List[CEOInsight] = []
        self.projects_cache: List[ProjectHealthSummary] = []
        self.sales_cache: List[SalesCoachingInsight] = []
        self.last_refresh = datetime.now()
        self.refresh_interval = timedelta(minutes=5)  # 5-minute refresh

    async def initialize(self):
        """Initialize the CEO dashboard service"""
        self.session = aiohttp.ClientSession()
        await self.mcp_service.initialize()
        logger.info("🎯 CEO Dashboard Service initialized")

    async def process_ceo_query(self, query: str, query_type: Optional[QueryType] = None) -> Dict[str, Any]:
        """
        Process natural language query from CEO with intelligent routing
        
        Args:
            query: Natural language query from CEO
            query_type: Optional explicit query type
            
        Returns:
            Comprehensive response with insights, data, and recommendations
        """
        try:
            # Classify query if type not provided
            if not query_type:
                query_type = await self._classify_query(query)
            
            logger.info(f"Processing CEO query: '{query}' (type: {query_type.value})")
            
            # Route to appropriate handler
            if query_type == QueryType.PROJECT_MANAGEMENT:
                return await self._handle_project_management_query(query)
            elif query_type == QueryType.SALES_COACHING:
                return await self._handle_sales_coaching_query(query)
            elif query_type == QueryType.BUSINESS_INTELLIGENCE:
                return await self._handle_business_intelligence_query(query)
            elif query_type == QueryType.FINANCIAL_ANALYSIS:
                return await self._handle_financial_analysis_query(query)
            elif query_type == QueryType.TEAM_PERFORMANCE:
                return await self._handle_team_performance_query(query)
            else:
                return await self._handle_general_query(query)
                
        except Exception as e:
            logger.error(f"Error processing CEO query: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }

    async def _classify_query(self, query: str) -> QueryType:
        """Classify CEO query using AI"""
        classification_prompt = f"""
        Classify this CEO query into one of these categories:
        - business_intelligence: Overall business metrics, KPIs, performance
        - project_management: Project status, team progress, milestones
        - sales_coaching: Sales performance, deal analysis, rep coaching
        - financial_analysis: Revenue, costs, profitability, forecasting
        - team_performance: Team productivity, resource allocation, hiring
        - strategic_planning: Long-term planning, market analysis, growth
        - competitive_analysis: Competitor tracking, market positioning
        - operational_metrics: System performance, efficiency, automation
        
        Query: "{query}"
        
        Return only the category name.
        """
        
        try:
            response = await self.ai_service.generate_response(
                prompt=classification_prompt,
                model="gpt-4",
                max_tokens=50
            )
            
            category_name = response.strip().lower()
            
            # Map to enum
            category_mapping = {
                "business_intelligence": QueryType.BUSINESS_INTELLIGENCE,
                "project_management": QueryType.PROJECT_MANAGEMENT,
                "sales_coaching": QueryType.SALES_COACHING,
                "financial_analysis": QueryType.FINANCIAL_ANALYSIS,
                "team_performance": QueryType.TEAM_PERFORMANCE,
                "strategic_planning": QueryType.STRATEGIC_PLANNING,
                "competitive_analysis": QueryType.COMPETITIVE_ANALYSIS,
                "operational_metrics": QueryType.OPERATIONAL_METRICS
            }
            
            return category_mapping.get(category_name, QueryType.BUSINESS_INTELLIGENCE)
            
        except Exception as e:
            logger.warning(f"Query classification failed: {e}")
            return QueryType.BUSINESS_INTELLIGENCE

    async def _handle_project_management_query(self, query: str) -> Dict[str, Any]:
        """Handle project management queries across Linear, Asana, and Notion"""
        try:
            # Get project data from all platforms
            linear_data = await self._get_linear_projects()
            asana_data = await self._get_asana_projects()
            notion_data = await self._get_notion_projects()
            
            # Combine and analyze
            all_projects = linear_data + asana_data + notion_data
            
            # Generate AI-powered insights
            analysis_prompt = f"""
            Analyze these project management data across Linear, Asana, and Notion platforms:
            
            Query: "{query}"
            
            Project Data: {json.dumps([p.__dict__ for p in all_projects], default=str, indent=2)}
            
            Provide:
            1. Direct answer to the CEO's query
            2. Key insights about project health
            3. Risk factors requiring attention
            4. Strategic recommendations
            5. Specific action items
            
            Format as executive summary suitable for CEO review.
            """
            
            ai_analysis = await self.ai_service.generate_response(
                prompt=analysis_prompt,
                model="gpt-4",
                max_tokens=1000
            )
            
            # Calculate summary metrics
            total_projects = len(all_projects)
            avg_health_score = sum(p.health_score for p in all_projects) / total_projects if total_projects > 0 else 0
            at_risk_projects = [p for p in all_projects if p.health_score < 70]
            
            return {
                "success": True,
                "query_type": "project_management",
                "query": query,
                "ai_analysis": ai_analysis,
                "summary_metrics": {
                    "total_projects": total_projects,
                    "average_health_score": round(avg_health_score, 1),
                    "at_risk_projects": len(at_risk_projects),
                    "platforms_integrated": ["Linear", "Asana", "Notion"]
                },
                "projects": [p.__dict__ for p in all_projects],
                "risk_projects": [p.__dict__ for p in at_risk_projects],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Project management query error: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_sales_coaching_query(self, query: str) -> Dict[str, Any]:
        """Handle sales coaching queries using Slack, HubSpot, and Gong data"""
        try:
            # Get sales data from all sources
            hubspot_deals = await self._get_hubspot_deals()
            gong_insights = await self._get_gong_insights()
            slack_activity = await self._get_slack_sales_activity()
            
            # Generate coaching insights
            coaching_prompt = f"""
            As an AI Sales Coach, analyze this sales data and provide coaching insights:
            
            CEO Query: "{query}"
            
            HubSpot Deals: {json.dumps(hubspot_deals, default=str, indent=2)}
            Gong Call Insights: {json.dumps(gong_insights, default=str, indent=2)}
            Slack Sales Activity: {json.dumps(slack_activity, default=str, indent=2)}
            
            Provide:
            1. Direct answer to the CEO's sales question
            2. Individual rep coaching recommendations
            3. Deal-specific strategies and risk assessments
            4. Process improvements and best practices
            5. Forecast accuracy and pipeline health
            6. Specific action items with timelines
            
            Focus on actionable insights that will drive revenue growth.
            """
            
            coaching_analysis = await self.ai_service.generate_response(
                prompt=coaching_prompt,
                model="gpt-4",
                max_tokens=1200
            )
            
            # Calculate sales metrics
            total_pipeline_value = sum(deal.get("amount", 0) for deal in hubspot_deals)
            high_risk_deals = [deal for deal in hubspot_deals if deal.get("risk_score", 0) > 70]
            
            return {
                "success": True,
                "query_type": "sales_coaching",
                "query": query,
                "coaching_analysis": coaching_analysis,
                "sales_metrics": {
                    "total_pipeline_value": total_pipeline_value,
                    "active_deals": len(hubspot_deals),
                    "high_risk_deals": len(high_risk_deals),
                    "gong_calls_analyzed": len(gong_insights),
                    "data_sources": ["HubSpot", "Gong", "Slack"]
                },
                "deals": hubspot_deals,
                "gong_insights": gong_insights,
                "coaching_recommendations": await self._generate_coaching_recommendations(hubspot_deals, gong_insights),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sales coaching query error: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_business_intelligence_query(self, query: str) -> Dict[str, Any]:
        """Handle general business intelligence queries"""
        try:
            # Get comprehensive business data
            kpi_data = await self._get_business_kpis()
            financial_data = await self._get_financial_metrics()
            operational_data = await self._get_operational_metrics()
            
            # Generate business intelligence
            bi_prompt = f"""
            As a Business Intelligence AI, analyze this comprehensive business data:
            
            CEO Query: "{query}"
            
            KPI Data: {json.dumps(kpi_data, default=str, indent=2)}
            Financial Metrics: {json.dumps(financial_data, default=str, indent=2)}
            Operational Metrics: {json.dumps(operational_data, default=str, indent=2)}
            
            Provide:
            1. Direct answer to the CEO's business question
            2. Key trends and patterns identified
            3. Performance against benchmarks and goals
            4. Strategic recommendations for improvement
            5. Risk factors and opportunities
            6. Specific metrics to monitor
            
            Present insights in executive summary format with actionable recommendations.
            """
            
            bi_analysis = await self.ai_service.generate_response(
                prompt=bi_prompt,
                model="gpt-4",
                max_tokens=1000
            )
            
            return {
                "success": True,
                "query_type": "business_intelligence",
                "query": query,
                "bi_analysis": bi_analysis,
                "kpis": kpi_data,
                "financial_metrics": financial_data,
                "operational_metrics": operational_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Business intelligence query error: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_financial_analysis_query(self, query: str) -> Dict[str, Any]:
        """Handle financial analysis queries"""
        try:
            # Get financial data from Snowflake
            financial_query = """
            SELECT 
                revenue_metrics,
                cost_metrics,
                profitability_metrics,
                cash_flow_metrics,
                forecast_data
            FROM FINANCIAL_ANALYTICS 
            WHERE date >= DATEADD(month, -12, CURRENT_DATE())
            ORDER BY date DESC
            """
            
            financial_data = await self.cortex_service.execute_query(financial_query)
            
            # Generate financial analysis
            analysis_prompt = f"""
            Analyze this financial data for the CEO:
            
            Query: "{query}"
            Financial Data: {json.dumps(financial_data, default=str, indent=2)}
            
            Provide comprehensive financial analysis including:
            1. Revenue trends and growth patterns
            2. Cost structure analysis and optimization opportunities
            3. Profitability metrics and margin analysis
            4. Cash flow projections and working capital needs
            5. Financial forecasting and scenario planning
            6. Strategic financial recommendations
            """
            
            analysis = await self.ai_service.generate_response(
                prompt=analysis_prompt,
                model="gpt-4",
                max_tokens=1000
            )
            
            return {
                "success": True,
                "query_type": "financial_analysis",
                "query": query,
                "financial_analysis": analysis,
                "financial_data": financial_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Financial analysis query error: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_team_performance_query(self, query: str) -> Dict[str, Any]:
        """Handle team performance queries"""
        try:
            # Get team data from multiple sources
            team_metrics = await self._get_team_performance_metrics()
            
            analysis_prompt = f"""
            Analyze team performance data for the CEO:
            
            Query: "{query}"
            Team Metrics: {json.dumps(team_metrics, default=str, indent=2)}
            
            Provide analysis covering:
            1. Individual and team productivity metrics
            2. Performance trends and patterns
            3. Resource allocation effectiveness
            4. Skill gaps and training needs
            5. Team satisfaction and retention factors
            6. Recommendations for performance improvement
            """
            
            analysis = await self.ai_service.generate_response(
                prompt=analysis_prompt,
                model="gpt-4",
                max_tokens=1000
            )
            
            return {
                "success": True,
                "query_type": "team_performance",
                "query": query,
                "team_analysis": analysis,
                "team_metrics": team_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Team performance query error: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Handle general queries with comprehensive business context"""
        try:
            # Get summary data from all sources
            summary_data = await self._get_comprehensive_business_summary()
            
            general_prompt = f"""
            Provide a comprehensive business response to this CEO query:
            
            Query: "{query}"
            Business Context: {json.dumps(summary_data, default=str, indent=2)}
            
            Draw insights from all available business data and provide actionable recommendations.
            """
            
            response = await self.ai_service.generate_response(
                prompt=general_prompt,
                model="gpt-4",
                max_tokens=800
            )
            
            return {
                "success": True,
                "query_type": "general",
                "query": query,
                "response": response,
                "business_context": summary_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"General query error: {e}")
            return {"success": False, "error": str(e)}

    # Data retrieval methods for each platform
    async def _get_linear_projects(self) -> List[ProjectHealthSummary]:
        """Get project data from Linear via MCP"""
        try:
            # Route to Linear MCP server
            response = await self.mcp_service.route_to_mcp(
                server="linear",
                tool="get_projects",
                params={"include_health_metrics": True}
            )
            
            if response.success:
                projects = []
                for project_data in response.data.get("projects", []):
                    project = ProjectHealthSummary(
                        project_id=project_data.get("id"),
                        project_name=project_data.get("name"),
                        platform="Linear",
                        health_score=project_data.get("health_score", 75),
                        completion_percentage=project_data.get("completion", 0),
                        team_members=project_data.get("team_members", []),
                        key_milestones=project_data.get("milestones", []),
                        risk_factors=project_data.get("risk_factors", []),
                        predicted_completion=None,  # Parse from project_data if available
                        budget_status=project_data.get("budget_status", {})
                    )
                    projects.append(project)
                return projects
            else:
                logger.warning(f"Linear MCP error: {response.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Linear projects: {e}")
            return []

    async def _get_asana_projects(self) -> List[ProjectHealthSummary]:
        """Get project data from Asana via MCP"""
        try:
            response = await self.mcp_service.route_to_mcp(
                server="asana",
                tool="get_projects",
                params={"include_analytics": True}
            )
            
            if response.success:
                projects = []
                for project_data in response.data.get("projects", []):
                    project = ProjectHealthSummary(
                        project_id=project_data.get("gid"),
                        project_name=project_data.get("name"),
                        platform="Asana",
                        health_score=project_data.get("health_score", 80),
                        completion_percentage=project_data.get("completion_percentage", 0),
                        team_members=project_data.get("team", []),
                        key_milestones=project_data.get("milestones", []),
                        risk_factors=project_data.get("risks", []),
                        predicted_completion=None,
                        budget_status=project_data.get("budget", {})
                    )
                    projects.append(project)
                return projects
            else:
                logger.warning(f"Asana MCP error: {response.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Asana projects: {e}")
            return []

    async def _get_notion_projects(self) -> List[ProjectHealthSummary]:
        """Get project data from Notion via MCP"""
        try:
            response = await self.mcp_service.route_to_mcp(
                server="notion",
                tool="query_database",
                params={
                    "database_id": "projects",
                    "filter": {"property": "Status", "status": {"does_not_equal": "Completed"}}
                }
            )
            
            if response.success:
                projects = []
                for page in response.data.get("results", []):
                    properties = page.get("properties", {})
                    project = ProjectHealthSummary(
                        project_id=page.get("id"),
                        project_name=properties.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                        platform="Notion",
                        health_score=properties.get("Health Score", {}).get("number", 70),
                        completion_percentage=properties.get("Completion", {}).get("number", 0),
                        team_members=properties.get("Team", {}).get("people", []),
                        key_milestones=[],
                        risk_factors=[],
                        predicted_completion=None,
                        budget_status={}
                    )
                    projects.append(project)
                return projects
            else:
                logger.warning(f"Notion MCP error: {response.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Notion projects: {e}")
            return []

    async def _get_hubspot_deals(self) -> List[Dict[str, Any]]:
        """Get deal data from HubSpot via MCP"""
        try:
            response = await self.mcp_service.route_to_mcp(
                server="hubspot",
                tool="get_deals",
                params={"properties": ["dealname", "amount", "dealstage", "closedate", "probability"]}
            )
            
            if response.success:
                return response.data.get("deals", [])
            else:
                logger.warning(f"HubSpot MCP error: {response.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting HubSpot deals: {e}")
            return []

    async def _get_gong_insights(self) -> List[Dict[str, Any]]:
        """Get call insights from Gong via MCP"""
        try:
            response = await self.mcp_service.route_to_mcp(
                server="gong",
                tool="get_call_insights",
                params={"date_range": "last_30_days", "include_sentiment": True}
            )
            
            if response.success:
                return response.data.get("insights", [])
            else:
                logger.warning(f"Gong MCP error: {response.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Gong insights: {e}")
            return []

    async def _get_slack_sales_activity(self) -> List[Dict[str, Any]]:
        """Get sales activity from Slack via MCP"""
        try:
            response = await self.mcp_service.route_to_mcp(
                server="slack",
                tool="get_channel_activity",
                params={"channel": "sales", "date_range": "last_7_days"}
            )
            
            if response.success:
                return response.data.get("messages", [])
            else:
                logger.warning(f"Slack MCP error: {response.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Slack activity: {e}")
            return []

    async def _get_business_kpis(self) -> Dict[str, Any]:
        """Get comprehensive business KPIs"""
        try:
            kpi_query = """
            SELECT 
                revenue_growth_rate,
                customer_acquisition_cost,
                lifetime_value,
                churn_rate,
                monthly_recurring_revenue,
                gross_margin,
                burn_rate,
                runway_months
            FROM BUSINESS_KPIS 
            WHERE date = CURRENT_DATE()
            """
            
            result = await self.cortex_service.execute_query(kpi_query)
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Error getting business KPIs: {e}")
            return {}

    async def _get_financial_metrics(self) -> Dict[str, Any]:
        """Get financial metrics from Snowflake"""
        try:
            financial_query = """
            SELECT 
                total_revenue,
                total_costs,
                gross_profit,
                operating_expenses,
                net_income,
                cash_balance,
                accounts_receivable,
                accounts_payable
            FROM FINANCIAL_SUMMARY 
            WHERE month = DATE_TRUNC('month', CURRENT_DATE())
            """
            
            result = await self.cortex_service.execute_query(financial_query)
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Error getting financial metrics: {e}")
            return {}

    async def _get_operational_metrics(self) -> Dict[str, Any]:
        """Get operational metrics"""
        try:
            ops_query = """
            SELECT 
                system_uptime,
                response_time_avg,
                error_rate,
                user_satisfaction_score,
                feature_adoption_rate,
                support_ticket_volume
            FROM OPERATIONAL_METRICS 
            WHERE date = CURRENT_DATE()
            """
            
            result = await self.cortex_service.execute_query(ops_query)
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Error getting operational metrics: {e}")
            return {}

    async def _get_team_performance_metrics(self) -> Dict[str, Any]:
        """Get team performance metrics"""
        try:
            team_query = """
            SELECT 
                team_productivity_score,
                individual_performance_ratings,
                project_completion_rate,
                code_quality_score,
                collaboration_index,
                training_completion_rate
            FROM TEAM_PERFORMANCE 
            WHERE week = DATE_TRUNC('week', CURRENT_DATE())
            """
            
            result = await self.cortex_service.execute_query(team_query)
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Error getting team performance metrics: {e}")
            return {}

    async def _get_comprehensive_business_summary(self) -> Dict[str, Any]:
        """Get comprehensive business summary for general queries"""
        try:
            summary = {
                "kpis": await self._get_business_kpis(),
                "financial": await self._get_financial_metrics(),
                "operational": await self._get_operational_metrics(),
                "team": await self._get_team_performance_metrics(),
                "projects_count": len(await self._get_linear_projects()) + len(await self._get_asana_projects()),
                "active_deals": len(await self._get_hubspot_deals()),
                "last_updated": datetime.now().isoformat()
            }
            return summary
            
        except Exception as e:
            logger.error(f"Error getting business summary: {e}")
            return {}

    async def _generate_coaching_recommendations(self, deals: List[Dict], insights: List[Dict]) -> List[SalesCoachingInsight]:
        """Generate AI-powered sales coaching recommendations"""
        try:
            coaching_insights = []
            
            for deal in deals:
                # Generate coaching insight for each deal
                coaching_prompt = f"""
                Generate a sales coaching recommendation for this deal:
                
                Deal: {json.dumps(deal, default=str)}
                Related Insights: {json.dumps([i for i in insights if i.get('deal_id') == deal.get('id')], default=str)}
                
                Provide specific coaching recommendation with:
                1. Key insight about the deal
                2. Specific recommendation for the rep
                3. Priority level (critical/high/medium/low)
                4. Expected impact
                5. Follow-up actions
                """
                
                response = await self.ai_service.generate_response(
                    prompt=coaching_prompt,
                    model="gpt-4",
                    max_tokens=300
                )
                
                insight = SalesCoachingInsight(
                    rep_name=deal.get("owner_name", "Unknown"),
                    deal_id=deal.get("id", ""),
                    deal_name=deal.get("dealname", ""),
                    coaching_type="opportunity",
                    insight=response,
                    recommendation=response,
                    priority=PriorityLevel.MEDIUM,
                    data_sources=["hubspot", "gong"],
                    confidence_score=0.8,
                    expected_impact="Medium",
                    follow_up_actions=["Schedule coaching session", "Review call recordings"]
                )
                
                coaching_insights.append(insight)
            
            return coaching_insights
            
        except Exception as e:
            logger.error(f"Error generating coaching recommendations: {e}")
            return []

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary for CEO"""
        try:
            # Check if cache needs refresh
            if datetime.now() - self.last_refresh > self.refresh_interval:
                await self._refresh_dashboard_cache()
            
            summary = {
                "executive_summary": {
                    "total_insights": len(self.insights_cache),
                    "critical_items": len([i for i in self.insights_cache if i.priority == PriorityLevel.CRITICAL]),
                    "projects_tracked": len(self.projects_cache),
                    "at_risk_projects": len([p for p in self.projects_cache if p.health_score < 70]),
                    "sales_opportunities": len(self.sales_cache),
                    "last_updated": self.last_refresh.isoformat()
                },
                "insights": [i.__dict__ for i in self.insights_cache[:10]],  # Top 10 insights
                "projects": [p.__dict__ for p in self.projects_cache],
                "sales_coaching": [s.__dict__ for s in self.sales_cache[:5]],  # Top 5 coaching items
                "quick_actions": await self._generate_quick_actions()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {"error": str(e)}

    async def _refresh_dashboard_cache(self):
        """Refresh dashboard cache with latest data"""
        try:
            # Refresh projects cache
            linear_projects = await self._get_linear_projects()
            asana_projects = await self._get_asana_projects()
            notion_projects = await self._get_notion_projects()
            self.projects_cache = linear_projects + asana_projects + notion_projects
            
            # Refresh sales cache
            hubspot_deals = await self._get_hubspot_deals()
            gong_insights = await self._get_gong_insights()
            self.sales_cache = await self._generate_coaching_recommendations(hubspot_deals, gong_insights)
            
            # Generate fresh insights
            await self._generate_executive_insights()
            
            self.last_refresh = datetime.now()
            logger.info("📊 Dashboard cache refreshed successfully")
            
        except Exception as e:
            logger.error(f"Error refreshing dashboard cache: {e}")

    async def _generate_executive_insights(self):
        """Generate executive insights from all data sources"""
        try:
            # Analyze all cached data to generate insights
            insights = []
            
            # Project health insights
            if self.projects_cache:
                avg_health = sum(p.health_score for p in self.projects_cache) / len(self.projects_cache)
                if avg_health < 75:
                    insight = CEOInsight(
                        title="Project Health Alert",
                        summary=f"Average project health score is {avg_health:.1f}%, below recommended 75%",
                        priority=PriorityLevel.HIGH,
                        category=QueryType.PROJECT_MANAGEMENT,
                        data_sources=["Linear", "Asana", "Notion"],
                        key_metrics={"average_health": avg_health, "total_projects": len(self.projects_cache)},
                        recommendations=["Review at-risk projects", "Allocate additional resources", "Implement project health monitoring"],
                        trend_analysis={"trend": "declining", "severity": "moderate"},
                        confidence_score=0.9
                    )
                    insights.append(insight)
            
            # Sales performance insights
            if self.sales_cache:
                high_priority_coaching = [s for s in self.sales_cache if s.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]]
                if high_priority_coaching:
                    insight = CEOInsight(
                        title="Sales Coaching Opportunities",
                        summary=f"{len(high_priority_coaching)} high-priority coaching opportunities identified",
                        priority=PriorityLevel.HIGH,
                        category=QueryType.SALES_COACHING,
                        data_sources=["HubSpot", "Gong", "Slack"],
                        key_metrics={"coaching_opportunities": len(high_priority_coaching)},
                        recommendations=["Schedule coaching sessions", "Review call recordings", "Implement sales training"],
                        trend_analysis={"trend": "actionable", "impact": "high"},
                        confidence_score=0.85
                    )
                    insights.append(insight)
            
            self.insights_cache = insights
            
        except Exception as e:
            logger.error(f"Error generating executive insights: {e}")

    async def _generate_quick_actions(self) -> List[Dict[str, Any]]:
        """Generate quick action items for CEO"""
        try:
            actions = []
            
            # Actions based on cached insights
            for insight in self.insights_cache:
                if insight.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]:
                    action = {
                        "title": f"Address {insight.title}",
                        "description": insight.summary,
                        "priority": insight.priority.value,
                        "category": insight.category.value,
                        "estimated_time": "15-30 minutes",
                        "recommendations": insight.recommendations[:2]  # Top 2 recommendations
                    }
                    actions.append(action)
            
            return actions[:5]  # Top 5 quick actions
            
        except Exception as e:
            logger.error(f"Error generating quick actions: {e}")
            return []

    async def shutdown(self):
        """Gracefully shutdown the service"""
        if self.session:
            await self.session.close()
        logger.info("🎯 CEO Dashboard Service shutdown complete")

# Global service instance
_ceo_dashboard_service = None

def get_ceo_dashboard_service() -> CEODashboardService:
    """Get the global CEO dashboard service instance"""
    global _ceo_dashboard_service
    if _ceo_dashboard_service is None:
        _ceo_dashboard_service = CEODashboardService()
    return _ceo_dashboard_service 