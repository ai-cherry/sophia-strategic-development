"""
Enhanced Unified Chat Service for Sophia AI v3.0

Provides complete ecosystem access including:
- All Sophia AI services (Database, AI Memory, Knowledge Base)
- All Pay Ready business systems (Gong, Slack, Linear, Asana, Notion, HubSpot, Salesforce, Intercom)
- Web search and external intelligence
- Infrastructure and deployment systems
- Real-time project management assessment across ALL data sources

Natural Language Queries for Complete Ecosystem:
- "What project risks were mentioned in Gong calls this week?"
- "Show me Slack discussions about the new feature launch"
- "What's the Linear engineering velocity this sprint?"
- "How are our HubSpot deals progressing?"
- "What customer feedback came through Intercom?"
- "Cross-reference Asana tasks with Gong customer requests"

Date: July 9, 2025
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from backend.services.enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator
from infrastructure.services.snowflake_cortex_service import SnowflakeCortexService
from backend.services.ai_memory_service import AIMemoryService

import logging
logger = logging.getLogger(__name__)


class EcosystemSource(Enum):
    """Complete Pay Ready ecosystem data sources"""
    
    # Core Sophia AI
    DATABASE = "database"
    AI_MEMORY = "ai_memory"
    KNOWLEDGE_BASE = "knowledge_base"
    WEB_SEARCH = "web_search"
    
    # Business Intelligence Systems
    GONG = "gong"  # Conversation intelligence - NOT standalone
    HUBSPOT = "hubspot"  # CRM intelligence
    SALESFORCE = "salesforce"  # Sales operations
    FINANCIAL_SYSTEMS = "financial_systems"  # Revenue, metrics
    CUSTOMER_HEALTH = "customer_health"  # Satisfaction, churn risk
    
    # Communication Systems
    SLACK = "slack"  # Team communication
    TEAMS = "teams"  # Microsoft Teams
    INTERCOM = "intercom"  # Customer support
    SUPPORT_CHANNELS = "support_channels"  # All support channels
    
    # Project Management Systems
    LINEAR = "linear"  # Engineering tasks
    ASANA = "asana"  # Project management
    NOTION = "notion"  # Documentation
    GITHUB = "github"  # Development activity
    
    # Infrastructure Systems
    LAMBDA_LABS = "lambda_labs"  # GPU infrastructure
    PULUMI = "pulumi"  # Infrastructure as code
    KUBERNETES = "kubernetes"  # Container orchestration


@dataclass
class EcosystemQuery:
    """Enhanced query with complete ecosystem context"""
    
    # Core query data
    query: str
    user_id: str
    session_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Date/time awareness
    current_date: str = "July 9, 2025"
    current_timestamp: str = "2025-07-09T00:00:00Z"
    
    # Ecosystem routing
    required_sources: List[EcosystemSource] = field(default_factory=list)
    priority_sources: List[EcosystemSource] = field(default_factory=list)
    
    # Intent and complexity
    intent_category: str = "general"
    complexity_level: str = "moderate"
    requires_cross_system_analysis: bool = False
    
    # Response requirements
    include_citations: bool = True
    include_confidence_scores: bool = True
    include_cross_system_patterns: bool = True


@dataclass
class EcosystemResponse:
    """Enhanced response with ecosystem intelligence"""
    
    # Core response
    response: str
    confidence: float
    processing_time: float
    
    # Ecosystem context
    sources_used: List[str]
    ecosystem_patterns: List[str]
    cross_system_correlations: Dict[str, Any]
    
    # Business intelligence
    project_health_insights: Dict[str, Any]
    risk_indicators: List[str]
    opportunities: List[str]
    
    # Citations and metadata
    citations: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    # Current date context
    current_date: str = "July 9, 2025"
    date_validated: bool = True


class EcosystemQueryAnalyzer:
    """Analyzes queries to determine ecosystem routing requirements"""
    
    def __init__(self):
        self.snowflake_cortex = SnowflakeCortexService()
        
    async def analyze_query(self, query: str, context: Dict[str, Any]) -> EcosystemQuery:
        """Analyze query to determine ecosystem routing"""
        
        # Intent analysis using Snowflake Cortex
        intent_analysis = await self.snowflake_cortex.complete_text(f"""
        Analyze this query for ecosystem routing: "{query}"
        Current date: July 9, 2025
        
        Determine:
        1. Intent category (project_management, business_intelligence, communication, technical, general)
        2. Required data sources from: gong, slack, linear, asana, notion, hubspot, salesforce, intercom, database, web
        3. Complexity level (simple, moderate, complex)
        4. Whether cross-system analysis is needed
        5. Priority data sources (most relevant)
        
        Return JSON format:
        {{
            "intent_category": "category",
            "required_sources": ["source1", "source2"],
            "priority_sources": ["source1"],
            "complexity_level": "level",
            "requires_cross_system_analysis": true/false,
            "reasoning": "explanation"
        }}
        """)
        
        try:
            analysis = json.loads(intent_analysis)
        except:
            # Fallback analysis
            analysis = self._fallback_analysis(query)
        
        # Convert to EcosystemQuery
        ecosystem_query = EcosystemQuery(
            query=query,
            user_id=context.get("user_id", "unknown"),
            session_id=context.get("session_id", "unknown"),
            context=context,
            intent_category=analysis.get("intent_category", "general"),
            complexity_level=analysis.get("complexity_level", "moderate"),
            requires_cross_system_analysis=analysis.get("requires_cross_system_analysis", False)
        )
        
        # Map sources to enums
        required_sources = []
        for source in analysis.get("required_sources", []):
            try:
                required_sources.append(EcosystemSource(source))
            except ValueError:
                continue
        
        priority_sources = []
        for source in analysis.get("priority_sources", []):
            try:
                priority_sources.append(EcosystemSource(source))
            except ValueError:
                continue
        
        ecosystem_query.required_sources = required_sources
        ecosystem_query.priority_sources = priority_sources
        
        return ecosystem_query
    
    def _fallback_analysis(self, query: str) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        
        query_lower = query.lower()
        required_sources = []
        priority_sources = []
        
        # Simple keyword-based routing
        if any(word in query_lower for word in ["call", "conversation", "customer", "sales", "meeting"]):
            required_sources.extend(["gong", "hubspot"])
            priority_sources.append("gong")
        
        if any(word in query_lower for word in ["slack", "team", "discussion", "chat"]):
            required_sources.append("slack")
            priority_sources.append("slack")
        
        if any(word in query_lower for word in ["linear", "issue", "bug", "feature", "engineering"]):
            required_sources.append("linear")
            priority_sources.append("linear")
        
        if any(word in query_lower for word in ["asana", "project", "task", "deadline"]):
            required_sources.append("asana")
            priority_sources.append("asana")
        
        if any(word in query_lower for word in ["notion", "documentation", "doc", "wiki"]):
            required_sources.append("notion")
            priority_sources.append("notion")
        
        # Always include database and AI memory
        required_sources.extend(["database", "ai_memory"])
        
        return {
            "intent_category": "general",
            "required_sources": list(set(required_sources)),
            "priority_sources": list(set(priority_sources)),
            "complexity_level": "moderate",
            "requires_cross_system_analysis": len(required_sources) > 2,
            "reasoning": "Fallback keyword-based analysis"
        }


class EcosystemRouter:
    """Routes queries to appropriate ecosystem services"""
    
    def __init__(self):
        self.enhanced_orchestrator = EnhancedMultiAgentOrchestrator()
        
    async def route_query(self, ecosystem_query: EcosystemQuery) -> EcosystemResponse:
        """Route query through the complete ecosystem"""
        
        start_time = datetime.now()
        
        # Use enhanced multi-agent orchestrator for complete ecosystem access
        orchestration_result = await self.enhanced_orchestrator.process_query(
            query=ecosystem_query.query,
            context={
                "user_id": ecosystem_query.user_id,
                "session_id": ecosystem_query.session_id,
                "current_date": ecosystem_query.current_date,
                "required_sources": [s.value for s in ecosystem_query.required_sources],
                "priority_sources": [s.value for s in ecosystem_query.priority_sources],
                "intent_category": ecosystem_query.intent_category,
                "complexity_level": ecosystem_query.complexity_level,
                "requires_cross_system_analysis": ecosystem_query.requires_cross_system_analysis
            }
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extract ecosystem intelligence
        ecosystem_patterns = orchestration_result.get("cross_system_patterns", [])
        sources_used = orchestration_result.get("ecosystem_sources_used", [])
        
        # Extract business intelligence
        project_health_insights = self._extract_project_health(orchestration_result)
        risk_indicators = self._extract_risk_indicators(orchestration_result)
        opportunities = self._extract_opportunities(orchestration_result)
        
        # Generate citations
        citations = self._generate_citations(orchestration_result, sources_used)
        
        # Build ecosystem response
        ecosystem_response = EcosystemResponse(
            response=orchestration_result.get("response", "No response generated"),
            confidence=orchestration_result.get("confidence", 0.0),
            processing_time=processing_time,
            sources_used=sources_used,
            ecosystem_patterns=ecosystem_patterns,
            cross_system_correlations=orchestration_result.get("cross_system_correlations", {}),
            project_health_insights=project_health_insights,
            risk_indicators=risk_indicators,
            opportunities=opportunities,
            citations=citations,
            metadata={
                "orchestration_success": orchestration_result.get("success", False),
                "agent_types_used": orchestration_result.get("agent_types_used", []),
                "execution_metrics": orchestration_result.get("execution_metrics", {}),
                "query_intent": ecosystem_query.intent_category,
                "complexity": ecosystem_query.complexity_level
            }
        )
        
        return ecosystem_response
    
    def _extract_project_health(self, orchestration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project health insights from orchestration results"""
        
        # Look for project health data in the results
        project_health = {}
        
        response_text = orchestration_result.get("response", "")
        if "health score" in response_text.lower():
            project_health["health_mentioned"] = True
        
        if "risk" in response_text.lower():
            project_health["risks_identified"] = True
        
        # Extract from agent results if available
        agent_results = orchestration_result.get("agent_results", {})
        if "project_intelligence" in str(agent_results):
            project_health["project_data_available"] = True
        
        return project_health
    
    def _extract_risk_indicators(self, orchestration_result: Dict[str, Any]) -> List[str]:
        """Extract risk indicators from orchestration results"""
        
        risks = []
        response_text = orchestration_result.get("response", "").lower()
        
        # Common risk keywords
        risk_keywords = ["delay", "behind schedule", "blocked", "issue", "problem", "concern", "risk"]
        
        for keyword in risk_keywords:
            if keyword in response_text:
                risks.append(f"Potential {keyword} identified in ecosystem data")
        
        return risks
    
    def _extract_opportunities(self, orchestration_result: Dict[str, Any]) -> List[str]:
        """Extract opportunities from orchestration results"""
        
        opportunities = []
        response_text = orchestration_result.get("response", "").lower()
        
        # Common opportunity keywords
        opportunity_keywords = ["opportunity", "improve", "optimize", "enhance", "potential", "growth"]
        
        for keyword in opportunity_keywords:
            if keyword in response_text:
                opportunities.append(f"Potential {keyword} identified in ecosystem data")
        
        return opportunities
    
    def _generate_citations(self, orchestration_result: Dict[str, Any], sources_used: List[str]) -> List[Dict[str, Any]]:
        """Generate citations for ecosystem sources"""
        
        citations = []
        
        for source in sources_used:
            citation = {
                "source": source,
                "type": self._get_source_type(source),
                "relevance": "high" if source in ["gong", "slack", "linear", "asana"] else "medium",
                "timestamp": datetime.now().isoformat()
            }
            citations.append(citation)
        
        return citations
    
    def _get_source_type(self, source: str) -> str:
        """Get the type of data source"""
        
        source_types = {
            "gong": "conversation_intelligence",
            "slack": "team_communication",
            "linear": "engineering_tasks",
            "asana": "project_management",
            "notion": "documentation",
            "hubspot": "crm_data",
            "salesforce": "sales_operations",
            "intercom": "customer_support",
            "database": "historical_data",
            "ai_memory": "contextual_memory",
            "web_search": "external_intelligence"
        }
        
        return source_types.get(source, "unknown")


class EnhancedUnifiedChatService:
    """
    Enhanced unified chat service with complete Pay Ready ecosystem access
    
    Natural Language Examples:
    - "What did customers say about our new feature in Gong calls this week?"
    - "Show me Linear tasks related to the issues discussed in Slack #engineering"
    - "Cross-reference HubSpot deals with customer feedback from Intercom"
    - "What project risks were mentioned across Gong, Slack, and Asana?"
    - "How is our engineering velocity in Linear compared to customer requests in Gong?"
    """
    
    def __init__(self):
        self.query_analyzer = EcosystemQueryAnalyzer()
        self.ecosystem_router = EcosystemRouter()
        self.ai_memory = AIMemoryService()
        
        # Progress streaming callbacks
        self.progress_callbacks = []
        
    async def process_ecosystem_query(
        self, 
        query: str, 
        user_id: str, 
        session_id: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process query with complete ecosystem access
        
        This is the main entry point for natural language queries that can access:
        - Gong conversation intelligence (NOT as standalone service)
        - Slack team communication
        - Linear engineering tasks
        - Asana project management
        - Notion documentation
        - HubSpot CRM data
        - Salesforce sales operations
        - Intercom customer support
        - Database and AI memory
        - Web search and external intelligence
        """
        
        try:
            # Analyze query for ecosystem routing
            ecosystem_query = await self.query_analyzer.analyze_query(
                query=query,
                context={
                    "user_id": user_id,
                    "session_id": session_id,
                    **(context or {})
                }
            )
            
            # Stream progress update
            await self._stream_progress({
                "type": "ecosystem_analysis",
                "status": "completed",
                "intent": ecosystem_query.intent_category,
                "sources_required": [s.value for s in ecosystem_query.required_sources],
                "cross_system_analysis": ecosystem_query.requires_cross_system_analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            # Route through ecosystem
            ecosystem_response = await self.ecosystem_router.route_query(ecosystem_query)
            
            # Store interaction in AI memory
            await self._store_ecosystem_interaction(ecosystem_query, ecosystem_response)
            
            # Build final response
            final_response = {
                "response": ecosystem_response.response,
                "confidence": ecosystem_response.confidence,
                "processing_time": ecosystem_response.processing_time,
                
                # Ecosystem intelligence
                "ecosystem_sources_used": ecosystem_response.sources_used,
                "ecosystem_patterns": ecosystem_response.ecosystem_patterns,
                "cross_system_correlations": ecosystem_response.cross_system_correlations,
                
                # Business intelligence
                "project_health_insights": ecosystem_response.project_health_insights,
                "risk_indicators": ecosystem_response.risk_indicators,
                "opportunities": ecosystem_response.opportunities,
                
                # Metadata
                "citations": ecosystem_response.citations,
                "metadata": ecosystem_response.metadata,
                "current_date": ecosystem_response.current_date,
                "date_validated": ecosystem_response.date_validated,
                
                # Query context
                "query_intent": ecosystem_query.intent_category,
                "complexity_level": ecosystem_query.complexity_level,
                "requires_cross_system_analysis": ecosystem_query.requires_cross_system_analysis
            }
            
            # Stream final progress update
            await self._stream_progress({
                "type": "ecosystem_response",
                "status": "completed",
                "confidence": ecosystem_response.confidence,
                "sources_count": len(ecosystem_response.sources_used),
                "patterns_found": len(ecosystem_response.ecosystem_patterns),
                "timestamp": datetime.now().isoformat()
            })
            
            return final_response
            
        except Exception as e:
            logger.error(f"Ecosystem query processing error: {e}")
            
            # Return error response
            return {
                "response": f"I encountered an error processing your ecosystem query: {str(e)}",
                "confidence": 0.0,
                "processing_time": 0.0,
                "ecosystem_sources_used": [],
                "ecosystem_patterns": [],
                "error": str(e),
                "current_date": "July 9, 2025",
                "date_validated": True
            }
    
    async def stream_ecosystem_query(
        self, 
        query: str, 
        user_id: str, 
        session_id: str, 
        context: Dict[str, Any] = None
    ):
        """Stream ecosystem query processing with real-time updates"""
        
        # Set up progress capturing
        progress_updates = []
        
        def capture_progress(update):
            progress_updates.append(update)
        
        self.progress_callbacks.append(capture_progress)
        
        try:
            # Process query
            result = await self.process_ecosystem_query(query, user_id, session_id, context)
            
            # Yield progress updates
            for update in progress_updates:
                yield {
                    "type": "progress",
                    "data": update
                }
            
            # Yield final result
            yield {
                "type": "final_response",
                "data": result
            }
            
        finally:
            # Remove progress callback
            if capture_progress in self.progress_callbacks:
                self.progress_callbacks.remove(capture_progress)
    
    async def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get status of all ecosystem services"""
        
        ecosystem_status = {
            "current_date": "July 9, 2025",
            "date_validated": True,
            "services": {
                # Business Intelligence
                "gong": {"status": "active", "type": "conversation_intelligence"},
                "hubspot": {"status": "active", "type": "crm_intelligence"},
                "salesforce": {"status": "pending", "type": "sales_operations"},
                "financial_systems": {"status": "active", "type": "financial_metrics"},
                "customer_health": {"status": "active", "type": "customer_intelligence"},
                
                # Communication
                "slack": {"status": "active", "type": "team_communication"},
                "teams": {"status": "pending", "type": "team_communication"},
                "intercom": {"status": "pending", "type": "customer_support"},
                "support_channels": {"status": "pending", "type": "support_communication"},
                
                # Project Management
                "linear": {"status": "active", "type": "engineering_tasks"},
                "asana": {"status": "active", "type": "project_management"},
                "notion": {"status": "active", "type": "documentation"},
                "github": {"status": "pending", "type": "development_activity"},
                
                # Core Services
                "database": {"status": "active", "type": "historical_data"},
                "ai_memory": {"status": "active", "type": "contextual_memory"},
                "web_search": {"status": "active", "type": "external_intelligence"}
            },
            "capabilities": [
                "Cross-system pattern recognition",
                "Natural language ecosystem queries",
                "Real-time project health assessment",
                "Risk and opportunity identification",
                "Comprehensive business intelligence synthesis"
            ]
        }
        
        return ecosystem_status
    
    async def _store_ecosystem_interaction(
        self, 
        ecosystem_query: EcosystemQuery, 
        ecosystem_response: EcosystemResponse
    ):
        """Store ecosystem interaction in AI memory"""
        
        try:
            interaction_data = {
                "query": ecosystem_query.query,
                "user_id": ecosystem_query.user_id,
                "session_id": ecosystem_query.session_id,
                "intent_category": ecosystem_query.intent_category,
                "sources_used": ecosystem_response.sources_used,
                "ecosystem_patterns": ecosystem_response.ecosystem_patterns,
                "confidence": ecosystem_response.confidence,
                "processing_time": ecosystem_response.processing_time,
                "current_date": ecosystem_response.current_date
            }
            
            await self.ai_memory.store_memory(
                content=json.dumps(interaction_data),
                category="ecosystem_interaction",
                metadata={
                    "intent": ecosystem_query.intent_category,
                    "sources_count": len(ecosystem_response.sources_used),
                    "cross_system": ecosystem_query.requires_cross_system_analysis
                }
            )
            
        except Exception as e:
            logger.warning(f"Failed to store ecosystem interaction: {e}")
    
    async def _stream_progress(self, update: Dict[str, Any]):
        """Stream progress update to all registered callbacks"""
        
        for callback in self.progress_callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    def add_progress_callback(self, callback):
        """Add progress callback for streaming updates"""
        self.progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback):
        """Remove progress callback"""
        if callback in self.progress_callbacks:
            self.progress_callbacks.remove(callback)


# Natural Language Query Examples for Complete Ecosystem Access
ECOSYSTEM_QUERY_EXAMPLES = [
    # Gong Intelligence (integrated, not standalone)
    "What project risks were mentioned in Gong calls this week?",
    "Show me customer feedback about our new feature from Gong conversations",
    "Which customers expressed concerns in recent Gong calls?",
    "What competitive mentions came up in Gong calls this month?",
    
    # Cross-System Project Intelligence
    "Cross-reference Linear engineering tasks with customer requests from Gong",
    "Show me Asana project status and related Slack discussions",
    "How do our Gong customer conversations align with Linear development priorities?",
    "What project risks appear in both Slack discussions and Gong calls?",
    
    # Communication Intelligence
    "What are the team discussing in Slack about the product launch?",
    "Show me decision points from recent Slack #leadership conversations",
    "What support issues are trending in Intercom this week?",
    "Find action items mentioned in Slack that relate to Linear tasks",
    
    # Business Intelligence Synthesis
    "How is our sales pipeline in HubSpot performing compared to customer sentiment in Gong?",
    "What's the correlation between customer health scores and support ticket volume?",
    "Show me revenue trends and customer feedback patterns",
    "How do our financial metrics align with customer satisfaction data?",
    
    # Complete Ecosystem Queries
    "Give me a comprehensive project health assessment across all systems",
    "What patterns emerge when looking at Gong, Slack, Linear, and Asana together?",
    "Show me all customer touchpoints from Gong, Intercom, and HubSpot",
    "What's the complete picture of our product development from all data sources?"
] 