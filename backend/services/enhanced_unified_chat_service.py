#!/usr/bin/env python3
"""
Enhanced Unified Chat Service
Extended to support comprehensive business intelligence across all schemas including
PAYREADY_CORE_SQL, NETSUITE_DATA, PROPERTY_ASSETS, AI_WEB_RESEARCH, and CEO_INTELLIGENCE
"""

import asyncio
import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.mcp.ai_memory_mcp_server import EnhancedAiMemoryMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    """Enhanced query intent classification"""
    # Executive/CEO intents
    EXECUTIVE_SUMMARY = "executive_summary"
    STRATEGIC_ANALYSIS = "strategic_analysis"
    BOARD_INTELLIGENCE = "board_intelligence"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    
    # Financial intents
    FINANCIAL_ANALYSIS = "financial_analysis"
    PAYMENT_ANALYSIS = "payment_analysis"
    EXPENSE_ANALYSIS = "expense_analysis"
    REVENUE_METRICS = "revenue_metrics"
    
    # Operational intents
    CUSTOMER_ANALYSIS = "customer_analysis"
    PROPERTY_ANALYSIS = "property_analysis"
    FEATURE_ANALYSIS = "feature_analysis"
    BUSINESS_RULES = "business_rules"
    
    # Intelligence intents
    MARKET_INTELLIGENCE = "market_intelligence"
    INDUSTRY_TRENDS = "industry_trends"
    PARTNERSHIP_OPPORTUNITIES = "partnership_opportunities"
    
    # Communication intents
    CALL_INSIGHTS = "call_insights"
    SLACK_ANALYSIS = "slack_analysis"
    TEAM_PERFORMANCE = "team_performance"
    
    # General intents
    KNOWLEDGE_SEARCH = "knowledge_search"
    DATA_EXPLORATION = "data_exploration"
    GENERAL_QUERY = "general_query"

@dataclass
class QueryContext:
    """Enhanced query context with security and role information"""
    user_id: str
    user_role: str
    dashboard_type: str
    security_level: str = "STANDARD"  # STANDARD, EXECUTIVE, CEO_ONLY
    accessible_schemas: List[str] = None
    time_filter: Optional[str] = None
    preferred_format: str = "conversational"

@dataclass
class QueryResult:
    """Enhanced query result with metadata"""
    content: str
    intent: QueryIntent
    data_sources: List[str]
    confidence_score: float
    execution_time_ms: int
    records_analyzed: int
    security_level: str
    suggested_actions: List[Dict[str, Any]] = None

class EnhancedUnifiedChatService:
    """Enhanced unified chat service with comprehensive business intelligence"""
    
    def __init__(self):
        self.cortex_service = None
        self.ai_memory_service = None
        self.snowflake_conn = None
        
        # Schema access mapping based on security levels
        self.schema_access_map = {
            "STANDARD": [
                "FOUNDATIONAL_KNOWLEDGE",
                "HUBSPOT_DATA", 
                "GONG_DATA",
                "SLACK_DATA"
            ],
            "EXECUTIVE": [
                "FOUNDATIONAL_KNOWLEDGE",
                "HUBSPOT_DATA",
                "GONG_DATA", 
                "SLACK_DATA",
                "PAYREADY_CORE_SQL",
                "NETSUITE_DATA",
                "PROPERTY_ASSETS",
                "AI_WEB_RESEARCH"
            ],
            "CEO_ONLY": [
                "FOUNDATIONAL_KNOWLEDGE",
                "HUBSPOT_DATA",
                "GONG_DATA",
                "SLACK_DATA", 
                "PAYREADY_CORE_SQL",
                "NETSUITE_DATA",
                "PROPERTY_ASSETS",
                "AI_WEB_RESEARCH",
                "CEO_INTELLIGENCE"
            ]
        }
        
    async def initialize(self) -> None:
        """Initialize the enhanced chat service"""
        try:
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            
            self.ai_memory_service = EnhancedAiMemoryMCPServer()
            await self.ai_memory_service.initialize()
            
            # Get direct Snowflake connection
            import snowflake.connector
            self.snowflake_conn = snowflake.connector.connect(
                account=await get_config_value("snowflake_account"),
                user=await get_config_value("snowflake_user"),
                password=await get_config_value("snowflake_password"),
                database="SOPHIA_AI_DEV",
                warehouse="WH_SOPHIA_AI_PROCESSING",
                role="ACCOUNTADMIN"
            )
            
            logger.info("✅ Enhanced Unified Chat Service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced chat service: {e}")
            raise

    async def classify_query_intent(self, query: str, context: QueryContext) -> QueryIntent:
        """Enhanced intent classification with context awareness"""
        try:
            query_lower = query.lower()
            
            # CEO/Executive specific intents
            if context.security_level == "CEO_ONLY" or context.dashboard_type == "ceo":
                if any(word in query_lower for word in ["strategic", "board", "confidential", "executive"]):
                    return QueryIntent.STRATEGIC_ANALYSIS
                if any(word in query_lower for word in ["competitor", "competitive", "market share"]):
                    return QueryIntent.COMPETITIVE_INTELLIGENCE
                if any(word in query_lower for word in ["board", "directors", "governance"]):
                    return QueryIntent.BOARD_INTELLIGENCE
                if any(word in query_lower for word in ["summary", "overview", "executive brief"]):
                    return QueryIntent.EXECUTIVE_SUMMARY
            
            # Financial analysis intents
            if any(word in query_lower for word in ["payment", "transaction", "revenue", "financial"]):
                if any(word in query_lower for word in ["payment", "transaction"]):
                    return QueryIntent.PAYMENT_ANALYSIS
                if any(word in query_lower for word in ["expense", "cost", "spending"]):
                    return QueryIntent.EXPENSE_ANALYSIS
                if any(word in query_lower for word in ["revenue", "income", "earnings"]):
                    return QueryIntent.REVENUE_METRICS
                return QueryIntent.FINANCIAL_ANALYSIS
            
            # Property and asset intents
            if any(word in query_lower for word in ["property", "asset", "unit", "occupancy"]):
                return QueryIntent.PROPERTY_ANALYSIS
            
            # Customer and feature intents
            if any(word in query_lower for word in ["customer", "feature", "subscription"]):
                if any(word in query_lower for word in ["feature", "subscription", "tier"]):
                    return QueryIntent.FEATURE_ANALYSIS
                return QueryIntent.CUSTOMER_ANALYSIS
            
            # Market intelligence intents
            if any(word in query_lower for word in ["trend", "industry", "market", "research"]):
                if any(word in query_lower for word in ["trend", "industry"]):
                    return QueryIntent.INDUSTRY_TRENDS
                if any(word in query_lower for word in ["partner", "partnership", "collaboration"]):
                    return QueryIntent.PARTNERSHIP_OPPORTUNITIES
                return QueryIntent.MARKET_INTELLIGENCE
            
            # Communication intents
            if any(word in query_lower for word in ["call", "gong", "conversation"]):
                return QueryIntent.CALL_INSIGHTS
            if any(word in query_lower for word in ["slack", "message", "chat"]):
                return QueryIntent.SLACK_ANALYSIS
            if any(word in query_lower for word in ["team", "performance", "employee"]):
                return QueryIntent.TEAM_PERFORMANCE
            
            # Business rules and operations
            if any(word in query_lower for word in ["rule", "process", "workflow", "automation"]):
                return QueryIntent.BUSINESS_RULES
            
            # Knowledge search
            if any(word in query_lower for word in ["search", "find", "document", "knowledge"]):
                return QueryIntent.KNOWLEDGE_SEARCH
            
            # Data exploration
            if any(word in query_lower for word in ["show", "list", "display", "data"]):
                return QueryIntent.DATA_EXPLORATION
            
            return QueryIntent.GENERAL_QUERY
            
        except Exception as e:
            logger.error(f"❌ Failed to classify query intent: {e}")
            return QueryIntent.GENERAL_QUERY

    async def execute_payment_analysis_query(self, query: str, context: QueryContext) -> QueryResult:
        """Execute payment and transaction analysis queries"""
        try:
            cursor = self.snowflake_conn.cursor()
            
            # Determine time filter
            time_filter = self._get_time_filter_sql(context.time_filter or "30d")
            
            # Execute payment analysis query
            cursor.execute(f"""
                WITH payment_metrics AS (
                    SELECT 
                        COUNT(*) as total_transactions,
                        SUM(CASE WHEN STATUS = 'COMPLETED' THEN AMOUNT ELSE 0 END) as total_amount,
                        AVG(CASE WHEN STATUS = 'COMPLETED' THEN AMOUNT END) as avg_amount,
                        COUNT(CASE WHEN STATUS = 'COMPLETED' THEN 1 END) as successful_transactions,
                        COUNT(CASE WHEN STATUS = 'FAILED' THEN 1 END) as failed_transactions,
                        ROUND(COUNT(CASE WHEN STATUS = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate,
                        COUNT(DISTINCT CUSTOMER_ID) as unique_customers,
                        COUNT(DISTINCT PROPERTY_ID) as unique_properties
                    FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS
                    WHERE {time_filter}
                ),
                payment_trends AS (
                    SELECT 
                        DATE_TRUNC('day', PROCESSING_DATE) as payment_date,
                        COUNT(*) as daily_transactions,
                        SUM(CASE WHEN STATUS = 'COMPLETED' THEN AMOUNT ELSE 0 END) as daily_amount
                    FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS
                    WHERE {time_filter}
                    GROUP BY DATE_TRUNC('day', PROCESSING_DATE)
                    ORDER BY payment_date DESC
                    LIMIT 7
                ),
                top_failure_reasons AS (
                    SELECT 
                        FAILURE_REASON,
                        COUNT(*) as failure_count
                    FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS
                    WHERE STATUS = 'FAILED' AND {time_filter}
                    AND FAILURE_REASON IS NOT NULL
                    GROUP BY FAILURE_REASON
                    ORDER BY failure_count DESC
                    LIMIT 5
                )
                SELECT 
                    (SELECT OBJECT_CONSTRUCT(*) FROM payment_metrics) as metrics,
                    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*)) FROM payment_trends) as trends,
                    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*)) FROM top_failure_reasons) as failures
            """)
            
            result = cursor.fetchone()
            metrics = json.loads(result[0])
            trends = json.loads(result[1]) if result[1] else []
            failures = json.loads(result[2]) if result[2] else []
            
            # Generate natural language response
            response = self._format_payment_analysis_response(metrics, trends, failures, context)
            
            cursor.close()
            
            return QueryResult(
                content=response,
                intent=QueryIntent.PAYMENT_ANALYSIS,
                data_sources=["PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS"],
                confidence_score=0.95,
                execution_time_ms=100,  # Would be measured in real implementation
                records_analyzed=metrics.get('total_transactions', 0),
                security_level="EXECUTIVE"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to execute payment analysis query: {e}")
            return QueryResult(
                content=f"I encountered an error analyzing payment data: {str(e)}",
                intent=QueryIntent.PAYMENT_ANALYSIS,
                data_sources=[],
                confidence_score=0.0,
                execution_time_ms=0,
                records_analyzed=0,
                security_level="EXECUTIVE"
            )

    async def execute_financial_analysis_query(self, query: str, context: QueryContext) -> QueryResult:
        """Execute financial analysis queries across NetSuite and PayReady data"""
        try:
            cursor = self.snowflake_conn.cursor()
            
            time_filter = self._get_time_filter_sql(context.time_filter or "30d")
            
            # Execute comprehensive financial analysis
            cursor.execute(f"""
                WITH revenue_metrics AS (
                    SELECT 
                        SUM(CASE WHEN STATUS = 'COMPLETED' THEN AMOUNT ELSE 0 END) as total_revenue,
                        COUNT(CASE WHEN STATUS = 'COMPLETED' THEN 1 END) as revenue_transactions
                    FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS
                    WHERE {time_filter}
                ),
                expense_metrics AS (
                    SELECT 
                        SUM(AMOUNT) as total_expenses,
                        COUNT(*) as expense_count,
                        COUNT(DISTINCT EMPLOYEE_ID) as employees_with_expenses
                    FROM NETSUITE_DATA.EXPENSE_REPORTS
                    WHERE EXPENSE_DATE >= CURRENT_DATE - 30
                ),
                ledger_summary AS (
                    SELECT 
                        SUM(DEBIT_AMOUNT) as total_debits,
                        SUM(CREDIT_AMOUNT) as total_credits,
                        COUNT(*) as ledger_entries
                    FROM NETSUITE_DATA.GENERAL_LEDGER
                    WHERE TRANSACTION_DATE >= CURRENT_DATE - 30
                )
                SELECT 
                    (SELECT OBJECT_CONSTRUCT(*) FROM revenue_metrics) as revenue,
                    (SELECT OBJECT_CONSTRUCT(*) FROM expense_metrics) as expenses,
                    (SELECT OBJECT_CONSTRUCT(*) FROM ledger_summary) as ledger
            """)
            
            result = cursor.fetchone()
            revenue = json.loads(result[0]) if result[0] else {}
            expenses = json.loads(result[1]) if result[1] else {}
            ledger = json.loads(result[2]) if result[2] else {}
            
            # Generate natural language response
            response = self._format_financial_analysis_response(revenue, expenses, ledger, context)
            
            cursor.close()
            
            return QueryResult(
                content=response,
                intent=QueryIntent.FINANCIAL_ANALYSIS,
                data_sources=["PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS", "NETSUITE_DATA.EXPENSE_REPORTS", "NETSUITE_DATA.GENERAL_LEDGER"],
                confidence_score=0.92,
                execution_time_ms=150,
                records_analyzed=revenue.get('revenue_transactions', 0) + expenses.get('expense_count', 0),
                security_level="EXECUTIVE"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to execute financial analysis query: {e}")
            return QueryResult(
                content=f"I encountered an error analyzing financial data: {str(e)}",
                intent=QueryIntent.FINANCIAL_ANALYSIS,
                data_sources=[],
                confidence_score=0.0,
                execution_time_ms=0,
                records_analyzed=0,
                security_level="EXECUTIVE"
            )

    async def execute_strategic_analysis_query(self, query: str, context: QueryContext) -> QueryResult:
        """Execute strategic analysis queries for CEO intelligence (CONFIDENTIAL)"""
        try:
            # Verify CEO-level access
            if context.security_level != "CEO_ONLY":
                return QueryResult(
                    content="I'm sorry, but strategic analysis requires CEO-level access. Please contact your administrator.",
                    intent=QueryIntent.STRATEGIC_ANALYSIS,
                    data_sources=[],
                    confidence_score=1.0,
                    execution_time_ms=0,
                    records_analyzed=0,
                    security_level="CEO_ONLY"
                )
            
            cursor = self.snowflake_conn.cursor()
            
            # Execute strategic analysis query
            cursor.execute("""
                WITH strategic_overview AS (
                    SELECT 
                        COUNT(*) as total_strategic_plans,
                        COUNT(CASE WHEN STATUS = 'IN_EXECUTION' THEN 1 END) as active_plans,
                        COUNT(CASE WHEN STATUS = 'COMPLETED' THEN 1 END) as completed_plans
                    FROM CEO_INTELLIGENCE.STRATEGIC_PLANS
                    WHERE PLANNING_PERIOD_END >= CURRENT_DATE
                ),
                competitive_intelligence AS (
                    SELECT 
                        COUNT(*) as total_intelligence_reports,
                        COUNT(CASE WHEN THREAT_LEVEL = 'HIGH' THEN 1 END) as high_threat_reports,
                        COUNT(CASE WHEN OPPORTUNITY_LEVEL = 'HIGH' THEN 1 END) as high_opportunity_reports
                    FROM CEO_INTELLIGENCE.COMPETITIVE_INTELLIGENCE
                    WHERE COLLECTION_DATE >= CURRENT_DATE - 90
                ),
                ma_pipeline AS (
                    SELECT 
                        COUNT(*) as total_opportunities,
                        COUNT(CASE WHEN OPPORTUNITY_STATUS = 'DUE_DILIGENCE' THEN 1 END) as active_dd,
                        SUM(ESTIMATED_VALUATION) as total_pipeline_value
                    FROM CEO_INTELLIGENCE.MA_OPPORTUNITIES
                    WHERE OPPORTUNITY_STATUS IN ('INITIAL_CONTACT', 'DUE_DILIGENCE', 'NEGOTIATION')
                )
                SELECT 
                    (SELECT OBJECT_CONSTRUCT(*) FROM strategic_overview) as strategy,
                    (SELECT OBJECT_CONSTRUCT(*) FROM competitive_intelligence) as competitive,
                    (SELECT OBJECT_CONSTRUCT(*) FROM ma_pipeline) as ma_pipeline
            """)
            
            result = cursor.fetchone()
            strategy = json.loads(result[0]) if result[0] else {}
            competitive = json.loads(result[1]) if result[1] else {}
            ma_pipeline = json.loads(result[2]) if result[2] else {}
            
            # Generate natural language response
            response = self._format_strategic_analysis_response(strategy, competitive, ma_pipeline, context)
            
            cursor.close()
            
            return QueryResult(
                content=response,
                intent=QueryIntent.STRATEGIC_ANALYSIS,
                data_sources=["CEO_INTELLIGENCE.STRATEGIC_PLANS", "CEO_INTELLIGENCE.COMPETITIVE_INTELLIGENCE", "CEO_INTELLIGENCE.MA_OPPORTUNITIES"],
                confidence_score=0.98,
                execution_time_ms=200,
                records_analyzed=strategy.get('total_strategic_plans', 0) + competitive.get('total_intelligence_reports', 0),
                security_level="CEO_ONLY",
                suggested_actions=[
                    {"action": "review_strategic_plans", "description": "Review active strategic plans"},
                    {"action": "assess_competitive_threats", "description": "Assess high-threat competitive intelligence"},
                    {"action": "evaluate_ma_pipeline", "description": "Evaluate M&A pipeline opportunities"}
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to execute strategic analysis query: {e}")
            return QueryResult(
                content=f"I encountered an error accessing strategic intelligence: {str(e)}",
                intent=QueryIntent.STRATEGIC_ANALYSIS,
                data_sources=[],
                confidence_score=0.0,
                execution_time_ms=0,
                records_analyzed=0,
                security_level="CEO_ONLY"
            )

    async def execute_property_analysis_query(self, query: str, context: QueryContext) -> QueryResult:
        """Execute property and asset analysis queries"""
        try:
            cursor = self.snowflake_conn.cursor()
            
            # Execute property analysis query
            cursor.execute("""
                WITH property_overview AS (
                    SELECT 
                        COUNT(*) as total_properties,
                        SUM(TOTAL_UNITS) as total_units,
                        SUM(OCCUPIED_UNITS) as occupied_units,
                        ROUND(AVG(OCCUPANCY_RATE), 2) as avg_occupancy_rate,
                        SUM(MONTHLY_RENT_POTENTIAL) as total_rent_potential,
                        SUM(ACTUAL_MONTHLY_RENT) as actual_monthly_rent
                    FROM PROPERTY_ASSETS.PROPERTIES
                    WHERE PROPERTY_STATUS = 'ACTIVE'
                ),
                property_performance AS (
                    SELECT 
                        PROPERTY_TYPE,
                        COUNT(*) as property_count,
                        AVG(OCCUPANCY_RATE) as avg_occupancy,
                        AVG(MONTHLY_RENT_POTENTIAL) as avg_rent_potential
                    FROM PROPERTY_ASSETS.PROPERTIES
                    WHERE PROPERTY_STATUS = 'ACTIVE'
                    GROUP BY PROPERTY_TYPE
                    ORDER BY avg_occupancy DESC
                ),
                unit_analysis AS (
                    SELECT 
                        OCCUPANCY_STATUS,
                        COUNT(*) as unit_count,
                        AVG(MONTHLY_RENT) as avg_rent
                    FROM PROPERTY_ASSETS.PROPERTY_UNITS
                    GROUP BY OCCUPANCY_STATUS
                )
                SELECT 
                    (SELECT OBJECT_CONSTRUCT(*) FROM property_overview) as overview,
                    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*)) FROM property_performance) as performance,
                    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*)) FROM unit_analysis) as units
            """)
            
            result = cursor.fetchone()
            overview = json.loads(result[0]) if result[0] else {}
            performance = json.loads(result[1]) if result[1] else []
            units = json.loads(result[2]) if result[2] else []
            
            # Generate natural language response
            response = self._format_property_analysis_response(overview, performance, units, context)
            
            cursor.close()
            
            return QueryResult(
                content=response,
                intent=QueryIntent.PROPERTY_ANALYSIS,
                data_sources=["PROPERTY_ASSETS.PROPERTIES", "PROPERTY_ASSETS.PROPERTY_UNITS"],
                confidence_score=0.93,
                execution_time_ms=120,
                records_analyzed=overview.get('total_properties', 0),
                security_level="EXECUTIVE"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to execute property analysis query: {e}")
            return QueryResult(
                content=f"I encountered an error analyzing property data: {str(e)}",
                intent=QueryIntent.PROPERTY_ANALYSIS,
                data_sources=[],
                confidence_score=0.0,
                execution_time_ms=0,
                records_analyzed=0,
                security_level="EXECUTIVE"
            )

    async def execute_market_intelligence_query(self, query: str, context: QueryContext) -> QueryResult:
        """Execute market intelligence and industry trend queries"""
        try:
            cursor = self.snowflake_conn.cursor()
            
            # Execute market intelligence query
            cursor.execute("""
                WITH industry_trends AS (
                    SELECT 
                        COUNT(*) as total_trends,
                        COUNT(CASE WHEN RELEVANCE_SCORE > 0.8 THEN 1 END) as high_relevance_trends,
                        COUNT(CASE WHEN BUSINESS_IMPACT_SCORE > 0.7 THEN 1 END) as high_impact_trends,
                        AVG(RELEVANCE_SCORE) as avg_relevance_score
                    FROM AI_WEB_RESEARCH.INDUSTRY_TRENDS
                    WHERE PUBLICATION_DATE >= CURRENT_DATE - 30
                ),
                competitor_intel AS (
                    SELECT 
                        COUNT(*) as total_intelligence,
                        COUNT(CASE WHEN THREAT_LEVEL = 'HIGH' THEN 1 END) as high_threats,
                        COUNT(CASE WHEN OPPORTUNITY_LEVEL = 'HIGH' THEN 1 END) as high_opportunities
                    FROM AI_WEB_RESEARCH.COMPETITOR_INTELLIGENCE
                    WHERE COLLECTION_DATE >= CURRENT_DATE - 30
                ),
                partnership_opps AS (
                    SELECT 
                        COUNT(*) as total_opportunities,
                        COUNT(CASE WHEN STRATEGIC_FIT_SCORE > 0.8 THEN 1 END) as high_fit_opportunities,
                        AVG(POTENTIAL_VALUE) as avg_potential_value
                    FROM AI_WEB_RESEARCH.PARTNERSHIP_OPPORTUNITIES
                ),
                top_trends AS (
                    SELECT 
                        TREND_TITLE,
                        RELEVANCE_SCORE,
                        BUSINESS_IMPACT_SCORE
                    FROM AI_WEB_RESEARCH.INDUSTRY_TRENDS
                    WHERE PUBLICATION_DATE >= CURRENT_DATE - 30
                    ORDER BY RELEVANCE_SCORE DESC
                    LIMIT 5
                )
                SELECT 
                    (SELECT OBJECT_CONSTRUCT(*) FROM industry_trends) as trends,
                    (SELECT OBJECT_CONSTRUCT(*) FROM competitor_intel) as competitive,
                    (SELECT OBJECT_CONSTRUCT(*) FROM partnership_opps) as partnerships,
                    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*)) FROM top_trends) as top_trends
            """)
            
            result = cursor.fetchone()
            trends = json.loads(result[0]) if result[0] else {}
            competitive = json.loads(result[1]) if result[1] else {}
            partnerships = json.loads(result[2]) if result[2] else {}
            top_trends = json.loads(result[3]) if result[3] else []
            
            # Generate natural language response
            response = self._format_market_intelligence_response(trends, competitive, partnerships, top_trends, context)
            
            cursor.close()
            
            return QueryResult(
                content=response,
                intent=QueryIntent.MARKET_INTELLIGENCE,
                data_sources=["AI_WEB_RESEARCH.INDUSTRY_TRENDS", "AI_WEB_RESEARCH.COMPETITOR_INTELLIGENCE", "AI_WEB_RESEARCH.PARTNERSHIP_OPPORTUNITIES"],
                confidence_score=0.90,
                execution_time_ms=180,
                records_analyzed=trends.get('total_trends', 0) + competitive.get('total_intelligence', 0),
                security_level="EXECUTIVE"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to execute market intelligence query: {e}")
            return QueryResult(
                content=f"I encountered an error analyzing market intelligence: {str(e)}",
                intent=QueryIntent.MARKET_INTELLIGENCE,
                data_sources=[],
                confidence_score=0.0,
                execution_time_ms=0,
                records_analyzed=0,
                security_level="EXECUTIVE"
            )

    def _get_time_filter_sql(self, time_filter: str) -> str:
        """Generate SQL time filter based on time period"""
        time_mappings = {
            "7d": "PROCESSING_DATE >= CURRENT_DATE - 7",
            "30d": "PROCESSING_DATE >= CURRENT_DATE - 30", 
            "90d": "PROCESSING_DATE >= CURRENT_DATE - 90",
            "1y": "PROCESSING_DATE >= CURRENT_DATE - 365"
        }
        return time_mappings.get(time_filter, "PROCESSING_DATE >= CURRENT_DATE - 30")

    def _format_payment_analysis_response(self, metrics: Dict, trends: List, failures: List, context: QueryContext) -> str:
        """Format payment analysis response in natural language"""
        total_amount = metrics.get('total_amount', 0)
        success_rate = metrics.get('success_rate', 0)
        total_transactions = metrics.get('total_transactions', 0)
        
        response = f"""📊 **Payment Analysis Summary**

**Overall Performance:**
• Total transactions: {total_transactions:,}
• Total amount processed: ${total_amount:,.2f}
• Success rate: {success_rate}%
• Unique customers: {metrics.get('unique_customers', 0):,}
• Average transaction: ${metrics.get('avg_amount', 0):.2f}

**Recent Trends:**
"""
        
        for trend in trends[:3]:
            date = trend.get('payment_date', '')
            daily_amount = trend.get('daily_amount', 0)
            daily_transactions = trend.get('daily_transactions', 0)
            response += f"• {date}: {daily_transactions} transactions, ${daily_amount:,.2f}\n"
        
        if failures:
            response += "\n**Top Failure Reasons:**\n"
            for failure in failures[:3]:
                reason = failure.get('failure_reason', 'Unknown')
                count = failure.get('failure_count', 0)
                response += f"• {reason}: {count} failures\n"
        
        return response

    def _format_financial_analysis_response(self, revenue: Dict, expenses: Dict, ledger: Dict, context: QueryContext) -> str:
        """Format financial analysis response in natural language"""
        total_revenue = revenue.get('total_revenue', 0)
        total_expenses = expenses.get('total_expenses', 0)
        net_income = total_revenue - total_expenses
        
        response = f"""💰 **Financial Analysis Summary**

**Revenue & Income:**
• Total revenue: ${total_revenue:,.2f}
• Revenue transactions: {revenue.get('revenue_transactions', 0):,}

**Expenses:**
• Total expenses: ${total_expenses:,.2f}
• Expense reports: {expenses.get('expense_count', 0):,}
• Employees with expenses: {expenses.get('employees_with_expenses', 0)}

**Net Performance:**
• Net income: ${net_income:,.2f}
• Profit margin: {(net_income / total_revenue * 100) if total_revenue > 0 else 0:.1f}%

**Ledger Summary:**
• Total debits: ${ledger.get('total_debits', 0):,.2f}
• Total credits: ${ledger.get('total_credits', 0):,.2f}
• Ledger entries: {ledger.get('ledger_entries', 0):,}
"""
        
        return response

    def _format_strategic_analysis_response(self, strategy: Dict, competitive: Dict, ma_pipeline: Dict, context: QueryContext) -> str:
        """Format strategic analysis response for CEO (CONFIDENTIAL)"""
        response = f"""🎯 **CONFIDENTIAL - Strategic Intelligence Summary**

**Strategic Plans:**
• Total strategic plans: {strategy.get('total_strategic_plans', 0)}
• Active plans: {strategy.get('active_plans', 0)}
• Completed plans: {strategy.get('completed_plans', 0)}

**Competitive Intelligence:**
• Intelligence reports (90 days): {competitive.get('total_intelligence_reports', 0)}
• High-threat reports: {competitive.get('high_threat_reports', 0)}
• High-opportunity reports: {competitive.get('high_opportunity_reports', 0)}

**M&A Pipeline:**
• Active opportunities: {ma_pipeline.get('total_opportunities', 0)}
• Due diligence phase: {ma_pipeline.get('active_dd', 0)}
• Total pipeline value: ${ma_pipeline.get('total_pipeline_value', 0):,.0f}

**Strategic Recommendations:**
• Review high-threat competitive intelligence
• Evaluate M&A opportunities in due diligence
• Assess strategic plan execution progress
"""
        
        return response

    def _format_property_analysis_response(self, overview: Dict, performance: List, units: List, context: QueryContext) -> str:
        """Format property analysis response in natural language"""
        occupancy_rate = overview.get('avg_occupancy_rate', 0)
        total_properties = overview.get('total_properties', 0)
        
        response = f"""🏢 **Property Portfolio Analysis**

**Portfolio Overview:**
• Total properties: {total_properties}
• Total units: {overview.get('total_units', 0):,}
• Occupied units: {overview.get('occupied_units', 0):,}
• Average occupancy rate: {occupancy_rate}%
• Monthly rent potential: ${overview.get('total_rent_potential', 0):,.2f}
• Actual monthly rent: ${overview.get('actual_monthly_rent', 0):,.2f}

**Performance by Property Type:**
"""
        
        for perf in performance[:3]:
            prop_type = perf.get('property_type', 'Unknown')
            avg_occ = perf.get('avg_occupancy', 0)
            avg_rent = perf.get('avg_rent_potential', 0)
            response += f"• {prop_type}: {avg_occ:.1f}% occupancy, ${avg_rent:,.0f} avg rent\n"
        
        response += "\n**Unit Status Distribution:**\n"
        for unit in units:
            status = unit.get('occupancy_status', 'Unknown')
            count = unit.get('unit_count', 0)
            avg_rent = unit.get('avg_rent', 0)
            response += f"• {status}: {count} units, ${avg_rent:.0f} avg rent\n"
        
        return response

    def _format_market_intelligence_response(self, trends: Dict, competitive: Dict, partnerships: Dict, top_trends: List, context: QueryContext) -> str:
        """Format market intelligence response in natural language"""
        response = f"""📈 **Market Intelligence Summary**

**Industry Trends (Last 30 Days):**
• Total trends identified: {trends.get('total_trends', 0)}
• High-relevance trends: {trends.get('high_relevance_trends', 0)}
• High-impact trends: {trends.get('high_impact_trends', 0)}
• Average relevance score: {trends.get('avg_relevance_score', 0):.2f}

**Competitive Intelligence:**
• Intelligence reports: {competitive.get('total_intelligence', 0)}
• High-threat items: {competitive.get('high_threats', 0)}
• High-opportunity items: {competitive.get('high_opportunities', 0)}

**Partnership Opportunities:**
• Total opportunities: {partnerships.get('total_opportunities', 0)}
• High-fit opportunities: {partnerships.get('high_fit_opportunities', 0)}
• Average potential value: ${partnerships.get('avg_potential_value', 0):,.0f}

**Top Industry Trends:**
"""
        
        for trend in top_trends[:3]:
            title = trend.get('trend_title', 'Unknown')
            relevance = trend.get('relevance_score', 0)
            impact = trend.get('business_impact_score', 0)
            response += f"• {title} (Relevance: {relevance:.2f}, Impact: {impact:.2f})\n"
        
        return response

    async def process_unified_query(self, query: str, context: QueryContext) -> QueryResult:
        """Process unified query across all schemas based on intent and security level"""
        try:
            start_time = datetime.now()
            
            # Classify query intent
            intent = await self.classify_query_intent(query, context)
            
            # Verify schema access based on security level
            accessible_schemas = self.schema_access_map.get(context.security_level, [])
            
            # Route to appropriate query handler
            if intent == QueryIntent.PAYMENT_ANALYSIS:
                result = await self.execute_payment_analysis_query(query, context)
            elif intent == QueryIntent.FINANCIAL_ANALYSIS:
                result = await self.execute_financial_analysis_query(query, context)
            elif intent == QueryIntent.STRATEGIC_ANALYSIS:
                result = await self.execute_strategic_analysis_query(query, context)
            elif intent == QueryIntent.PROPERTY_ANALYSIS:
                result = await self.execute_property_analysis_query(query, context)
            elif intent == QueryIntent.MARKET_INTELLIGENCE:
                result = await self.execute_market_intelligence_query(query, context)
            else:
                # Default to general knowledge search
                result = await self._execute_general_query(query, context)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result.execution_time_ms = int(execution_time)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to process unified query: {e}")
            return QueryResult(
                content=f"I encountered an error processing your query: {str(e)}",
                intent=QueryIntent.GENERAL_QUERY,
                data_sources=[],
                confidence_score=0.0,
                execution_time_ms=0,
                records_analyzed=0,
                security_level=context.security_level
            )

    async def _execute_general_query(self, query: str, context: QueryContext) -> QueryResult:
        """Execute general queries using semantic search across accessible schemas"""
        try:
            # Use AI Memory service for semantic search
            search_results = await self.ai_memory_service.search_memories(
                query=query,
                category="ALL",
                max_results=10
            )
            
            if not search_results:
                return QueryResult(
                    content="I couldn't find any relevant information for your query. Please try rephrasing or be more specific.",
                    intent=QueryIntent.GENERAL_QUERY,
                    data_sources=[],
                    confidence_score=0.5,
                    execution_time_ms=50,
                    records_analyzed=0,
                    security_level=context.security_level
                )
            
            # Format search results into natural language response
            response = "Based on your query, here's what I found:\n\n"
            data_sources = set()
            
            for result in search_results[:5]:
                response += f"• {result.get('content', 'No content available')}\n"
                if result.get('source'):
                    data_sources.add(result['source'])
            
            return QueryResult(
                content=response,
                intent=QueryIntent.GENERAL_QUERY,
                data_sources=list(data_sources),
                confidence_score=0.8,
                execution_time_ms=100,
                records_analyzed=len(search_results),
                security_level=context.security_level
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to execute general query: {e}")
            return QueryResult(
                content=f"I encountered an error searching for information: {str(e)}",
                intent=QueryIntent.GENERAL_QUERY,
                data_sources=[],
                confidence_score=0.0,
                execution_time_ms=0,
                records_analyzed=0,
                security_level=context.security_level
            )

    async def close(self) -> None:
        """Clean up connections"""
        try:
            if self.snowflake_conn:
                self.snowflake_conn.close()
            if self.cortex_service:
                await self.cortex_service.close()
            if self.ai_memory_service:
                await self.ai_memory_service.close()
            logger.info("✅ Enhanced Unified Chat Service connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")

async def main():
    """Test the enhanced unified chat service"""
    service = EnhancedUnifiedChatService()
    
    try:
        await service.initialize()
        
        # Test queries for different security levels
        test_queries = [
            ("What's our payment volume this month?", "EXECUTIVE"),
            ("Show me property occupancy rates", "EXECUTIVE"),
            ("Analyze strategic plans and competitive threats", "CEO_ONLY"),
            ("What are the latest industry trends?", "EXECUTIVE")
        ]
        
        for query, security_level in test_queries:
            context = QueryContext(
                user_id="test_user",
                user_role="executive",
                dashboard_type="ceo",
                security_level=security_level
            )
            
            result = await service.process_unified_query(query, context)
            print(f"\n🔍 Query: {query}")
            print(f"🎯 Intent: {result.intent.value}")
            print(f"📊 Response: {result.content[:200]}...")
            print(f"⚡ Execution time: {result.execution_time_ms}ms")
            print(f"🔒 Security level: {result.security_level}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    finally:
        await service.close()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
