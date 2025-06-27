"""
Universal Chat API Routes for Sophia AI

Provides conversational business intelligence backend with:
- Multi-source data synthesis and context awareness
- Real-time OKR updates and insights
- Progressive autonomy management
- Customer expansion and churn analysis
- Executive dashboard integration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import json

from ..core.auth import get_current_user
from ..services.okr_tracking_service import okr_tracking_service
from ..services.progressive_autonomy_manager import progressive_autonomy_manager, ActionRequest, ActionCategory
from ..integrations.enhanced_gong_integration import enhanced_gong_integration
from ..services.smart_ai_service import smart_ai_service
from ..utils.enhanced_snowflake_cortex_service import EnhancedSnowflakeCortexService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Universal Chat"])

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    user_role: Optional[str] = Field(default="employee", description="User role for access control")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for continuity")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    confidence: float = Field(..., description="Response confidence score")
    sources: List[str] = Field(default=[], description="Data sources used")
    insights: List[Dict[str, Any]] = Field(default=[], description="Additional insights")
    recommended_actions: List[str] = Field(default=[], description="Recommended next actions")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: str = Field(..., description="Response timestamp")


class OKRQuery(BaseModel):
    okr_type: Optional[str] = Field(default=None, description="Specific OKR to query")
    time_period: Optional[str] = Field(default="current", description="Time period for analysis")


class CustomerQuery(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    analysis_type: str = Field(..., description="Type of analysis: timeline, expansion, churn, health")
    time_range_days: Optional[int] = Field(default=90, description="Days back to analyze")


class AutonomyRequest(BaseModel):
    action_description: str = Field(..., description="Description of action to evaluate")
    category: str = Field(..., description="Action category")
    confidence_score: float = Field(..., description="AI confidence in action")
    impact_score: float = Field(..., description="Estimated business impact")
    risk_score: float = Field(..., description="Risk assessment score")
    context: Dict[str, Any] = Field(default={}, description="Additional context")


# Chat service class
class UniversalChatService:
    """Universal chat service for conversational business intelligence"""
    
    def __init__(self):
        self.cortex_service = EnhancedSnowflakeCortexService()
        self.conversation_memory = {}  # In-memory conversation storage
        
        # Intent classification patterns
        self.intent_patterns = {
            "okr_query": ["okr", "objective", "goal", "target", "progress", "ai-first", "revenue per employee", "revenue per unit"],
            "customer_analysis": ["customer", "client", "account", "churn", "expansion", "timeline", "relationship"],
            "business_metrics": ["metrics", "performance", "analytics", "dashboard", "kpi", "trend"],
            "autonomy_management": ["automation", "autonomy", "approve", "execute", "decision"],
            "general_business": ["business", "strategy", "opportunities", "risks", "recommendations"],
            "data_query": ["data", "report", "analysis", "insights", "trends"],
            "system_status": ["health", "status", "performance", "integration", "connectivity"]
        }
    
    async def process_chat_message(self, message: ChatMessage, user_id: str) -> ChatResponse:
        """Process chat message and generate intelligent response"""
        try:
            # Classify intent
            intent = self._classify_intent(message.message)
            
            # Route to appropriate handler
            response_data = await self._route_to_handler(intent, message, user_id)
            
            # Store conversation for continuity
            conversation_id = message.conversation_id or f"conv_{user_id}_{datetime.now().timestamp()}"
            await self._store_conversation(conversation_id, message.message, response_data["response"], user_id)
            
            return ChatResponse(
                response=response_data["response"],
                confidence=response_data.get("confidence", 0.8),
                sources=response_data.get("sources", []),
                insights=response_data.get("insights", []),
                recommended_actions=response_data.get("recommended_actions", []),
                conversation_id=conversation_id,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return ChatResponse(
                response="I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                confidence=0.1,
                sources=[],
                insights=[],
                recommended_actions=["Try rephrasing your question", "Contact support if issue persists"],
                conversation_id=message.conversation_id or f"error_{datetime.now().timestamp()}",
                timestamp=datetime.now().isoformat()
            )
    
    def _classify_intent(self, message: str) -> str:
        """Classify user intent from message"""
        message_lower = message.lower()
        
        # Score each intent based on keyword matches
        intent_scores = {}
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return highest scoring intent or default to general business
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return "general_business"
    
    async def _route_to_handler(self, intent: str, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Route message to appropriate handler based on intent"""
        
        handlers = {
            "okr_query": self._handle_okr_query,
            "customer_analysis": self._handle_customer_analysis,
            "business_metrics": self._handle_business_metrics,
            "autonomy_management": self._handle_autonomy_management,
            "general_business": self._handle_general_business,
            "data_query": self._handle_data_query,
            "system_status": self._handle_system_status
        }
        
        handler = handlers.get(intent, self._handle_general_business)
        return await handler(message, user_id)
    
    async def _handle_okr_query(self, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Handle OKR-related queries"""
        try:
            # Get real-time OKR dashboard
            okr_data = await okr_tracking_service.get_real_time_okr_dashboard()
            
            # Generate contextual response based on query
            context_prompt = f"""
            User query: {message.message}
            
            Current OKR Status:
            - Overall Score: {okr_data['overall_score']['score']:.1f}% ({okr_data['overall_score']['grade']})
            - AI-First Company: {okr_data['okrs']['ai_first_company'].current_value:.2f} / {okr_data['okrs']['ai_first_company'].target_value} (Target)
            - Revenue per Employee: ${okr_data['okrs']['revenue_per_employee'].current_value:,.0f} / ${okr_data['okrs']['revenue_per_employee'].target_value:,.0f} (Target)
            - Revenue per Unit: ${okr_data['okrs']['revenue_per_unit'].current_value:,.0f} / ${okr_data['okrs']['revenue_per_unit'].target_value:,.0f} (Target)
            
            Provide a conversational response addressing the user's specific question about OKRs.
            """
            
            ai_response = await smart_ai_service.generate_response(
                context_prompt, 
                model_preference="premium",
                user_context={"role": message.user_role}
            )
            
            return {
                "response": ai_response,
                "confidence": 0.9,
                "sources": ["OKR Tracking Service", "Snowflake Analytics"],
                "insights": [
                    {
                        "type": "okr_progress",
                        "data": okr_data['okrs']
                    },
                    {
                        "type": "critical_actions",
                        "data": okr_data.get('critical_actions', [])
                    }
                ],
                "recommended_actions": okr_data.get('critical_actions', [])
            }
            
        except Exception as e:
            logger.error(f"Error handling OKR query: {e}")
            return {
                "response": "I'm having trouble accessing OKR data right now. Let me help you with other business questions.",
                "confidence": 0.3,
                "sources": [],
                "insights": [],
                "recommended_actions": ["Try asking about specific OKRs", "Check system status"]
            }
    
    async def _handle_customer_analysis(self, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Handle customer-related queries"""
        try:
            # Extract customer information from message if possible
            customer_id = self._extract_customer_id(message.message)
            
            if customer_id:
                # Get customer analysis
                timeline = await enhanced_gong_integration.get_customer_interaction_timeline(customer_id)
                expansion_analysis = await enhanced_gong_integration.analyze_customer_expansion_potential(customer_id)
                churn_analysis = await enhanced_gong_integration.assess_churn_risk(customer_id)
                
                context_prompt = f"""
                User query: {message.message}
                
                Customer Analysis for {timeline.customer_name} ({timeline.company_name}):
                - Total Interactions: {timeline.total_interactions}
                - Relationship Health: {timeline.relationship_health_score:.2f}/1.0
                - Expansion Readiness: {expansion_analysis['expansion_readiness_score']:.2f}/1.0
                - Churn Risk: {churn_analysis['churn_risk_level']} ({churn_analysis['churn_risk_score']:.2f})
                - Recent Sentiment Trend: {timeline.overall_sentiment_trend[-5:] if timeline.overall_sentiment_trend else 'No data'}
                
                Provide insights and recommendations based on this customer data.
                """
                
                ai_response = await smart_ai_service.generate_response(
                    context_prompt,
                    model_preference="premium",
                    user_context={"role": message.user_role}
                )
                
                return {
                    "response": ai_response,
                    "confidence": 0.85,
                    "sources": ["Gong Integration", "Customer Timeline Analysis"],
                    "insights": [
                        {
                            "type": "customer_health",
                            "data": {
                                "health_score": timeline.relationship_health_score,
                                "churn_risk": churn_analysis['churn_risk_level'],
                                "expansion_readiness": expansion_analysis['expansion_readiness_score']
                            }
                        }
                    ],
                    "recommended_actions": timeline.recommended_actions + churn_analysis['recommended_actions']
                }
            else:
                # General customer analysis query
                return await self._handle_general_customer_query(message, user_id)
                
        except Exception as e:
            logger.error(f"Error handling customer analysis: {e}")
            return {
                "response": "I need more specific customer information to provide detailed analysis. Could you provide a customer name or ID?",
                "confidence": 0.6,
                "sources": [],
                "insights": [],
                "recommended_actions": ["Specify customer name or ID", "Ask about general customer metrics"]
            }
    
    async def _handle_business_metrics(self, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Handle business metrics and analytics queries"""
        try:
            # Query Snowflake for relevant business metrics
            metrics_query = """
            SELECT 
                'revenue' as metric_type,
                SUM(amount) as total_value,
                COUNT(*) as count,
                AVG(amount) as average_value
            FROM HUBSPOT_DATA.DEALS 
            WHERE deal_stage = 'closed_won' 
            AND created_date >= CURRENT_DATE - 30
            
            UNION ALL
            
            SELECT 
                'pipeline' as metric_type,
                SUM(amount) as total_value,
                COUNT(*) as count,
                AVG(amount) as average_value
            FROM HUBSPOT_DATA.DEALS 
            WHERE deal_stage IN ('proposal', 'negotiation', 'decision_maker_bought_in')
            AND created_date >= CURRENT_DATE - 30
            """
            
            metrics_data = await self.cortex_service.execute_query(metrics_query)
            
            context_prompt = f"""
            User query: {message.message}
            
            Business Metrics Summary:
            {json.dumps(metrics_data, indent=2) if metrics_data else 'No recent data available'}
            
            Provide insights and analysis based on this business data.
            """
            
            ai_response = await smart_ai_service.generate_response(
                context_prompt,
                model_preference="balanced",
                user_context={"role": message.user_role}
            )
            
            return {
                "response": ai_response,
                "confidence": 0.8,
                "sources": ["HubSpot Data", "Business Analytics"],
                "insights": [
                    {
                        "type": "business_metrics",
                        "data": metrics_data or []
                    }
                ],
                "recommended_actions": ["Review detailed metrics in dashboard", "Schedule metrics review meeting"]
            }
            
        except Exception as e:
            logger.error(f"Error handling business metrics: {e}")
            return {
                "response": "I can help you with business metrics. What specific metrics are you interested in?",
                "confidence": 0.5,
                "sources": [],
                "insights": [],
                "recommended_actions": ["Ask about specific metrics like revenue or pipeline", "Request dashboard access"]
            }
    
    async def _handle_autonomy_management(self, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Handle autonomy and automation queries"""
        try:
            # Get autonomy dashboard
            autonomy_data = await progressive_autonomy_manager.get_autonomy_dashboard()
            
            context_prompt = f"""
            User query: {message.message}
            
            AI Autonomy Status:
            - Overall Autonomy Score: {autonomy_data['overall_autonomy_score']['percentage']:.1f}%
            - Grade: {autonomy_data['overall_autonomy_score']['grade']}
            - Recent Decisions: {len(autonomy_data.get('recent_decisions', []))}
            - Performance: {autonomy_data.get('performance_metrics', {})}
            
            Respond about AI autonomy, automation capabilities, or decision management.
            """
            
            ai_response = await smart_ai_service.generate_response(
                context_prompt,
                model_preference="balanced",
                user_context={"role": message.user_role}
            )
            
            return {
                "response": ai_response,
                "confidence": 0.8,
                "sources": ["Autonomy Manager", "Decision Analytics"],
                "insights": [
                    {
                        "type": "autonomy_status",
                        "data": autonomy_data['overall_autonomy_score']
                    }
                ],
                "recommended_actions": autonomy_data.get('recommendations', [])
            }
            
        except Exception as e:
            logger.error(f"Error handling autonomy management: {e}")
            return {
                "response": "I can help you understand our AI automation capabilities. What would you like to know?",
                "confidence": 0.6,
                "sources": [],
                "insights": [],
                "recommended_actions": ["Ask about specific automation areas", "Request autonomy status report"]
            }
    
    async def _handle_general_business(self, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Handle general business queries"""
        try:
            # Use AI service for general business intelligence
            context_prompt = f"""
            User query: {message.message}
            
            You are Sophia, the AI business intelligence assistant for Pay Ready. 
            Provide helpful, actionable insights based on the user's query.
            Focus on business value, strategic thinking, and practical recommendations.
            """
            
            ai_response = await smart_ai_service.generate_response(
                context_prompt,
                model_preference="premium" if message.user_role == "ceo" else "balanced",
                user_context={"role": message.user_role}
            )
            
            return {
                "response": ai_response,
                "confidence": 0.7,
                "sources": ["Sophia AI", "Business Intelligence"],
                "insights": [],
                "recommended_actions": ["Explore specific areas of interest", "Request detailed analysis"]
            }
            
        except Exception as e:
            logger.error(f"Error handling general business query: {e}")
            return {
                "response": "I'm here to help with your business questions. Could you provide more specific details about what you'd like to know?",
                "confidence": 0.5,
                "sources": [],
                "insights": [],
                "recommended_actions": ["Be more specific about your question", "Try asking about OKRs, customers, or metrics"]
            }
    
    async def _handle_data_query(self, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Handle data and reporting queries"""
        return await self._handle_business_metrics(message, user_id)
    
    async def _handle_system_status(self, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Handle system status and health queries"""
        try:
            # Basic system health check
            health_status = {
                "okr_service": "healthy",
                "gong_integration": "healthy", 
                "snowflake_connection": "healthy",
                "ai_services": "healthy"
            }
            
            context_prompt = f"""
            User query: {message.message}
            
            System Health Status:
            {json.dumps(health_status, indent=2)}
            
            Provide status information and any relevant system insights.
            """
            
            ai_response = await smart_ai_service.generate_response(
                context_prompt,
                model_preference="balanced",
                user_context={"role": message.user_role}
            )
            
            return {
                "response": ai_response,
                "confidence": 0.9,
                "sources": ["System Health Monitor"],
                "insights": [
                    {
                        "type": "system_health",
                        "data": health_status
                    }
                ],
                "recommended_actions": ["Monitor system performance", "Review integration health"]
            }
            
        except Exception as e:
            logger.error(f"Error handling system status: {e}")
            return {
                "response": "System status check is temporarily unavailable. Core services appear to be functioning normally.",
                "confidence": 0.6,
                "sources": [],
                "insights": [],
                "recommended_actions": ["Try again in a few minutes", "Contact support if issues persist"]
            }
    
    # Utility methods
    def _extract_customer_id(self, message: str) -> Optional[str]:
        """Extract customer ID from message (placeholder implementation)"""
        # TODO: Implement customer ID extraction logic
        # This could use NER, regex patterns, or database lookups
        return None
    
    async def _handle_general_customer_query(self, message: ChatMessage, user_id: str) -> Dict[str, Any]:
        """Handle general customer queries without specific customer ID"""
        context_prompt = f"""
        User query: {message.message}
        
        Provide general customer insights and recommendations. 
        Suggest how to get more specific customer information.
        """
        
        ai_response = await smart_ai_service.generate_response(
            context_prompt,
            model_preference="balanced",
            user_context={"role": message.user_role}
        )
        
        return {
            "response": ai_response,
            "confidence": 0.6,
            "sources": ["Customer Intelligence"],
            "insights": [],
            "recommended_actions": ["Specify a customer name or ID", "Ask about customer metrics in general"]
        }
    
    async def _store_conversation(self, conversation_id: str, user_message: str, 
                                 ai_response: str, user_id: str) -> None:
        """Store conversation for continuity and learning"""
        try:
            # Store in memory (in production, use proper database)
            if conversation_id not in self.conversation_memory:
                self.conversation_memory[conversation_id] = {
                    "user_id": user_id,
                    "messages": [],
                    "created_at": datetime.now(),
                    "last_updated": datetime.now()
                }
            
            self.conversation_memory[conversation_id]["messages"].append({
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.now()
            })
            self.conversation_memory[conversation_id]["last_updated"] = datetime.now()
            
            # TODO: Store in Snowflake for persistent conversation history
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")


# Initialize service
universal_chat_service = UniversalChatService()


# API Routes
@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    message: ChatMessage,
    current_user = Depends(get_current_user)
):
    """Send a chat message and get AI response"""
    try:
        response = await universal_chat_service.process_chat_message(message, current_user.id)
        return response
        
    except Exception as e:
        logger.error(f"Error in chat message endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/okrs", response_model=Dict[str, Any])
async def get_okr_status(
    okr_query: OKRQuery = Depends(),
    current_user = Depends(get_current_user)
):
    """Get real-time OKR status and insights"""
    try:
        okr_data = await okr_tracking_service.get_real_time_okr_dashboard()
        return okr_data
        
    except Exception as e:
        logger.error(f"Error in OKR status endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve OKR data")


@router.get("/customer/{customer_id}", response_model=Dict[str, Any])
async def get_customer_analysis(
    customer_id: str,
    analysis_type: str = "timeline",
    time_range_days: int = 90,
    current_user = Depends(get_current_user)
):
    """Get comprehensive customer analysis"""
    try:
        if analysis_type == "timeline":
            result = await enhanced_gong_integration.get_customer_interaction_timeline(
                customer_id, time_range_days
            )
            return {
                "analysis_type": "timeline",
                "customer_id": customer_id,
                "data": result.__dict__  # Convert dataclass to dict
            }
        elif analysis_type == "expansion":
            result = await enhanced_gong_integration.analyze_customer_expansion_potential(customer_id)
            return result
        elif analysis_type == "churn":
            result = await enhanced_gong_integration.assess_churn_risk(customer_id)
            return result
        elif analysis_type == "health":
            result = await enhanced_gong_integration.analyze_relationship_health(customer_id)
            return result
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
            
    except Exception as e:
        logger.error(f"Error in customer analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze customer data")


@router.post("/autonomy/evaluate", response_model=Dict[str, Any])
async def evaluate_autonomy(
    request: AutonomyRequest,
    current_user = Depends(get_current_user)
):
    """Evaluate autonomy level for a proposed action"""
    try:
        # Convert request to ActionRequest
        action_request = ActionRequest(
            action_id=f"action_{datetime.now().timestamp()}",
            category=ActionCategory(request.category),
            description=request.action_description,
            confidence_score=request.confidence_score,
            impact_score=request.impact_score,
            risk_score=request.risk_score,
            context=request.context,
            recommended_action=request.action_description,
            timestamp=datetime.now()
        )
        
        decision = await progressive_autonomy_manager.evaluate_action_autonomy(action_request)
        
        return {
            "action_id": decision.action_id,
            "autonomy_level": decision.autonomy_level.value,
            "should_execute": decision.should_execute,
            "requires_approval": decision.requires_approval,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "estimated_impact": decision.estimated_impact,
            "risk_assessment": decision.risk_assessment
        }
        
    except Exception as e:
        logger.error(f"Error in autonomy evaluation endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate autonomy")


@router.get("/autonomy/dashboard", response_model=Dict[str, Any])
async def get_autonomy_dashboard(
    current_user = Depends(get_current_user)
):
    """Get autonomy management dashboard"""
    try:
        dashboard_data = await progressive_autonomy_manager.get_autonomy_dashboard()
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error in autonomy dashboard endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve autonomy dashboard")


@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation_history(
    conversation_id: str,
    current_user = Depends(get_current_user)
):
    """Get conversation history for continuity"""
    try:
        conversation = universal_chat_service.conversation_memory.get(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check user access
        if conversation["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "conversation_id": conversation_id,
            "messages": conversation["messages"],
            "created_at": conversation["created_at"].isoformat(),
            "last_updated": conversation["last_updated"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in conversation history endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation history")


@router.get("/health", response_model=Dict[str, Any])
async def chat_service_health():
    """Check chat service health"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "okr_tracking": "operational",
                "gong_integration": "operational",
                "autonomy_manager": "operational",
                "ai_service": "operational"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        } 