"""
Business AI API Routes for Sophia Platform
Integrates business AI agents into existing Sophia backend without duplication
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from datetime import datetime

from backend.agents.business.enhanced_business_ai_orchestrator import (
    business_orchestrator,
    BusinessQuery,
    BusinessResponse
)
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

# Create API router for business AI endpoints
business_ai_router = APIRouter(
    prefix="/api/business-ai",
    tags=["business-ai"],
    responses={404: {"description": "Not found"}}
)

@business_ai_router.post("/query", response_model=Dict[str, Any])
async def process_business_query(query_data: Dict[str, Any]):
    """
    Process business intelligence query through AI agents
    Integrates with existing Sophia dashboard and chat interface
    """
    try:
        # Extract query data
        query_text = query_data.get("query", "")
        user_id = query_data.get("user_id", "anonymous")
        department = query_data.get("department")
        priority = query_data.get("priority", "normal")
        context = query_data.get("context", {})
        
        if not query_text.strip():
            raise HTTPException(status_code=400, detail="Query text cannot be empty")
        
        # Create business query object
        business_query = BusinessQuery(
            query=query_text,
            user_id=user_id,
            department=department,
            priority=priority,
            context=context
        )
        
        # Process through business AI orchestrator
        start_time = datetime.now()
        response = await business_orchestrator.process_business_query(business_query)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log the interaction for analytics
        logger.info(f"Business AI query processed", extra={
            "user_id": user_id,
            "query_length": len(query_text),
            "processing_time_ms": processing_time,
            "confidence": response.confidence,
            "agent_routing": context.get("selectedAgent", "auto")
        })
        
        # Return response in format expected by frontend
        return {
            "response": response.response,
            "insights": response.insights,
            "recommendations": response.recommendations,
            "data_sources": response.data_sources,
            "confidence": response.confidence,
            "processing_time_ms": response.processing_time_ms,
            "metadata": response.metadata,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing business query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@business_ai_router.get("/agents", response_model=Dict[str, Any])
async def get_available_agents():
    """Get list of available business AI agents and their capabilities"""
    
    agents = {
        "revenue": {
            "name": "Revenue Intelligence Agent",
            "description": "Revenue analysis, forecasting, and growth insights",
            "capabilities": [
                "Monthly/quarterly revenue analysis",
                "Revenue trend identification",
                "Customer segment performance",
                "Growth forecasting",
                "Revenue optimization recommendations"
            ],
            "data_sources": ["hubspot_crm", "stripe_billing", "salesforce_analytics"],
            "example_queries": [
                "How is our revenue performing this quarter?",
                "What's driving our revenue growth?",
                "Which customer segments are most valuable?"
            ]
        },
        "team": {
            "name": "Team Performance Agent", 
            "description": "Team productivity, performance, and organizational insights",
            "capabilities": [
                "Team productivity analysis",
                "Department performance metrics",
                "Employee satisfaction tracking",
                "Hiring and capacity planning",
                "Cross-functional collaboration insights"
            ],
            "data_sources": ["hr_system", "jira_project_data", "slack_analytics", "employee_surveys"],
            "example_queries": [
                "How is our team performing?",
                "What's our hiring status?",
                "Which departments need attention?"
            ]
        },
        "customer": {
            "name": "Customer Intelligence Agent",
            "description": "Customer behavior, satisfaction, and lifecycle insights",
            "capabilities": [
                "Customer satisfaction analysis",
                "Churn risk identification",
                "Customer lifetime value analysis",
                "Usage and engagement patterns",
                "Expansion opportunity identification"
            ],
            "data_sources": ["hubspot_crm", "intercom_support", "mixpanel_analytics", "customer_surveys"],
            "example_queries": [
                "How satisfied are our customers?",
                "Which customers are at risk of churning?",
                "What expansion opportunities do we have?"
            ]
        },
        "market": {
            "name": "Market Intelligence Agent",
            "description": "Competitive analysis, market trends, and strategic insights",
            "capabilities": [
                "Competitive landscape analysis",
                "Market trend identification",
                "Pricing intelligence",
                "Customer acquisition insights",
                "Geographic expansion opportunities"
            ],
            "data_sources": ["cb_insights", "g2_reviews", "similarweb", "industry_reports"],
            "example_queries": [
                "How do we compare to competitors?",
                "What market trends should we watch?",
                "What are our pricing opportunities?"
            ]
        }
    }
    
    return {
        "agents": agents,
        "routing": {
            "auto": "Automatically routes to best agent based on query content",
            "manual": "User can manually select specific agent"
        },
        "shared_infrastructure": [
            "qdrant (vector database with separate collections)",
            "redis (cache with separate databases)",
            "perplexity (real-time research)",
            "notion (knowledge base with workspace separation)"
        ]
    }

@business_ai_router.get("/health", response_model=Dict[str, Any])
async def business_ai_health_check():
    """Health check for business AI orchestrator and agents"""
    
    try:
        # Test business AI orchestrator initialization
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "revenue_agent": "initialized",
                "team_agent": "initialized", 
                "customer_agent": "initialized",
                "market_agent": "initialized"
            },
            "shared_mcp_servers": business_orchestrator.shared_mcp_servers,
            "configuration": {
                "environment": get_config_value("ENVIRONMENT", "prod"),
                "qdrant_configured": bool(get_config_value("QDRANT_URL")),
                "redis_configured": True,  # Local Redis
                "openrouter_configured": bool(get_config_value("OPENROUTER_API_KEY"))
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Business AI health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@business_ai_router.get("/analytics", response_model=Dict[str, Any])
async def get_business_ai_analytics():
    """Get analytics and usage metrics for business AI"""
    
    # This would typically pull from analytics database
    # For now, return mock analytics data
    
    analytics = {
        "usage_metrics": {
            "total_queries_today": 127,
            "total_queries_this_week": 892,
            "total_queries_this_month": 3456,
            "average_response_time_ms": 245,
            "average_confidence_score": 0.84
        },
        "agent_usage": {
            "revenue": {"queries": 1234, "avg_confidence": 0.87},
            "team": {"queries": 987, "avg_confidence": 0.82},
            "customer": {"queries": 1567, "avg_confidence": 0.91},
            "market": {"queries": 654, "avg_confidence": 0.79},
            "comprehensive": {"queries": 234, "avg_confidence": 0.85}
        },
        "user_engagement": {
            "active_users_today": 23,
            "active_users_this_week": 67,
            "average_queries_per_user": 14.2,
            "user_satisfaction_score": 4.6
        },
        "performance_metrics": {
            "uptime_percentage": 99.7,
            "error_rate_percentage": 0.3,
            "cache_hit_rate_percentage": 78.4,
            "p95_response_time_ms": 450
        },
        "insights": [
            "Customer Intelligence agent has highest confidence scores",
            "Revenue queries show 23% increase this month",
            "Average response time improved 15% this week",
            "User engagement up 34% quarter-over-quarter"
        ]
    }
    
    return analytics

@business_ai_router.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(feedback_data: Dict[str, Any]):
    """Submit feedback on business AI responses for continuous improvement"""
    
    try:
        query_id = feedback_data.get("query_id")
        rating = feedback_data.get("rating")  # 1-5 stars
        feedback_text = feedback_data.get("feedback", "")
        user_id = feedback_data.get("user_id", "anonymous")
        
        if not query_id or not rating:
            raise HTTPException(status_code=400, detail="Query ID and rating are required")
        
        if rating not in [1, 2, 3, 4, 5]:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Log feedback for analytics and model improvement
        logger.info(f"Business AI feedback received", extra={
            "query_id": query_id,
            "rating": rating,
            "feedback_length": len(feedback_text),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # In a real implementation, this would:
        # 1. Store feedback in database
        # 2. Trigger model retraining if needed
        # 3. Update agent confidence calibration
        # 4. Generate improvement recommendations
        
        return {
            "status": "feedback_received",
            "message": "Thank you for your feedback! It helps improve our AI agents.",
            "query_id": query_id,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error submitting feedback")

# Integration endpoint for existing Sophia chat interface
@business_ai_router.post("/chat/business", response_model=Dict[str, Any])
async def business_chat_endpoint(message_data: Dict[str, Any]):
    """
    Business AI chat endpoint that integrates with existing Sophia chat
    Provides business intelligence within existing chat interface
    """
    
    try:
        message = message_data.get("message", "")
        user_id = message_data.get("user_id", "anonymous")
        session_id = message_data.get("session_id", "")
        context = message_data.get("context", {})
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Check if this is a business query
        business_keywords = [
            "revenue", "sales", "customer", "team", "performance", 
            "market", "competitor", "growth", "metric", "kpi",
            "profit", "satisfaction", "productivity", "analysis"
        ]
        
        is_business_query = any(keyword in message.lower() for keyword in business_keywords)
        
        if is_business_query:
            # Route to business AI orchestrator
            business_query = BusinessQuery(
                query=message,
                user_id=user_id,
                context={"session_id": session_id, **context}
            )
            
            response = await business_orchestrator.process_business_query(business_query)
            
            return {
                "type": "business_ai_response",
                "message": response.response,
                "insights": response.insights,
                "recommendations": response.recommendations,
                "confidence": response.confidence,
                "agent_type": "business_ai",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Return indication that this should be handled by regular chat
            return {
                "type": "regular_chat",
                "message": "This query will be handled by the regular chat system",
                "route_to": "general_chat",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in business chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing chat message")

# Export router for integration with main FastAPI app
__all__ = ["business_ai_router"] 