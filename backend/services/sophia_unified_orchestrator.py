"""
Sophia Unified Orchestrator - The OFFICIAL entry point for all Sophia AI requests

This is the single, authoritative orchestrator that combines:
- UnifiedChatService capabilities
- SophiaAIOrchestrator intelligence
- EnhancedMultiAgentOrchestrator parallel execution
- SophiaAgentOrchestrator workflow patterns

All other orchestrators are DEPRECATED and will be removed in version 6.0.

Date: July 9, 2025
"""

from typing import Any, Dict, List, Optional, Set
import asyncio
import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from backend.core.date_time_manager import date_manager
from backend.services.unified_memory_service import get_unified_memory_service
from infrastructure.services.mcp_orchestration_service import MCPOrchestrationService

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents"""
    BUSINESS_INTELLIGENCE = "business_intelligence"
    CODE_ANALYSIS = "code_analysis"
    INFRASTRUCTURE = "infrastructure"
    MEMORY_QUERY = "memory_query"
    GENERAL = "general"


@dataclass
class Intent:
    """Analyzed user intent"""
    type: IntentType
    confidence: float
    capabilities_needed: Set[str]
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationMetrics:
    """Metrics for monitoring orchestration performance"""
    request_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    active_users: Set[str] = field(default_factory=set)
    mcp_server_usage: Dict[str, int] = field(default_factory=dict)
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    def calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        if self.request_count == 0:
            return 100.0
        
        error_rate = self.error_count / self.request_count
        performance_score = min(100, 100 * (1.0 / max(0.1, self.average_response_time)))
        
        return round((1 - error_rate) * 50 + performance_score * 0.5, 2)


class SophiaUnifiedOrchestrator:
    """
    The unified orchestrator for all Sophia AI operations.
    
    This replaces:
    - UnifiedChatService
    - SophiaAIOrchestrator  
    - EnhancedMultiAgentOrchestrator
    - SophiaAgentOrchestrator
    """
    
    def __init__(self):
        self.memory_service = get_unified_memory_service()
        self.mcp_orchestrator = None  # Will lazy load
        self.current_date = date_manager.now()
        self.metrics = OrchestrationMetrics()
        self.initialized = False
        
        logger.info(f"✅ SophiaUnifiedOrchestrator initialized - Date: {self.current_date}")
        
    async def initialize(self):
        """Initialize all services"""
        if self.initialized:
            return
            
        try:
            # Initialize MCP orchestrator
            self.mcp_orchestrator = MCPOrchestrationService()
            await self.mcp_orchestrator.initialize()
            
            self.initialized = True
            logger.info("✅ All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
        
    async def process_request(
        self,
        query: str,
        user_id: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process any request through the unified orchestration pipeline.
        
        This is the ONLY method external services should call.
        """
        
        # Ensure initialization
        if not self.initialized:
            await self.initialize()
        
        start_time = date_manager.now()
        
        # Update metrics
        self.metrics.request_count += 1
        self.metrics.active_users.add(user_id)
        
        try:
            # Log the request
            logger.info(f"Processing request from user {user_id}: {query[:50]}...")
            
            # Step 1: Store in memory for learning
            await self.memory_service.add_conversation(
                user_id=user_id,
                session_id=session_id,
                user_message=query,
                ai_response=None  # Will update after processing
            )
            
            # Step 2: Analyze intent
            intent = await self._analyze_intent(query, context)
            
            # Step 3: Route to appropriate handler
            if intent.type == IntentType.BUSINESS_INTELLIGENCE:
                response = await self._handle_business_intelligence(query, intent, user_id, session_id, context)
            elif intent.type == IntentType.CODE_ANALYSIS:
                response = await self._handle_code_analysis(query, intent, user_id, session_id, context)
            elif intent.type == IntentType.INFRASTRUCTURE:
                response = await self._handle_infrastructure(query, intent, user_id, session_id, context)
            elif intent.type == IntentType.MEMORY_QUERY:
                response = await self._handle_memory_query(query, intent, user_id, session_id, context)
            else:
                response = await self._handle_general(query, intent, user_id, session_id, context)
            
            # Step 4: Update memory with response
            await self.memory_service.update_conversation(
                session_id=session_id,
                ai_response=response.get("response", "")
            )
            
            # Step 5: Add metadata
            end_time = date_manager.now()
            processing_time = (end_time - start_time).total_seconds()
            
            self.metrics.total_response_time += processing_time
            
            response["metadata"] = {
                "processing_time": processing_time,
                "intent": {
                    "type": intent.type.value,
                    "confidence": intent.confidence,
                    "capabilities": list(intent.capabilities_needed)
                },
                "orchestrator": "unified",
                "version": "1.0.0",
                "date": self.current_date.isoformat(),
                "health_score": self.metrics.calculate_health_score()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.metrics.error_count += 1
            
            return {
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "metadata": {
                    "error": True,
                    "orchestrator": "unified",
                    "version": "1.0.0",
                    "date": self.current_date.isoformat()
                }
            }
    
    async def _analyze_intent(self, query: str, context: Optional[Dict[str, Any]]) -> Intent:
        """Analyze user intent from query"""
        query_lower = query.lower()
        
        # Business intelligence keywords
        if any(word in query_lower for word in [
            "revenue", "sales", "deal", "customer", "crm", "hubspot", 
            "gong", "call", "meeting", "performance", "metrics"
        ]):
            return Intent(
                type=IntentType.BUSINESS_INTELLIGENCE,
                confidence=0.9,
                capabilities_needed={"CRM", "ANALYTICS", "CALLS"}
            )
        
        # Code analysis keywords
        elif any(word in query_lower for word in [
            "code", "analyze", "review", "quality", "security", "bug",
            "refactor", "optimize", "lint", "test"
        ]):
            return Intent(
                type=IntentType.CODE_ANALYSIS,
                confidence=0.9,
                capabilities_needed={"CODE_ANALYSIS", "SECURITY", "METRICS"}
            )
        
        # Infrastructure keywords
        elif any(word in query_lower for word in [
            "deploy", "infrastructure", "server", "docker", "kubernetes",
            "lambda", "pulumi", "terraform", "aws", "cloud"
        ]):
            return Intent(
                type=IntentType.INFRASTRUCTURE,
                confidence=0.9,
                capabilities_needed={"INFRASTRUCTURE", "DEPLOYMENT", "MONITORING"}
            )
        
        # Memory query keywords
        elif any(word in query_lower for word in [
            "remember", "recall", "what did", "previous", "history",
            "context", "earlier", "last time"
        ]):
            return Intent(
                type=IntentType.MEMORY_QUERY,
                confidence=0.9,
                capabilities_needed={"MEMORY", "SEARCH"}
            )
        
        # Default to general
        else:
            return Intent(
                type=IntentType.GENERAL,
                confidence=0.7,
                capabilities_needed={"MEMORY", "SEARCH", "ANALYTICS"}
            )
    
    async def _handle_business_intelligence(
        self, query: str, intent: Intent, user_id: str, session_id: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle business intelligence queries"""
        
        # Get capable MCP servers
        servers = await self.mcp_orchestrator.get_servers_by_capability(list(intent.capabilities_needed))
        
        # Update metrics
        for server in servers:
            self.metrics.mcp_server_usage[server["name"]] = self.metrics.mcp_server_usage.get(server["name"], 0) + 1
        
        # Execute parallel queries to relevant servers
        tasks = []
        if "gong" in [s["name"] for s in servers]:
            tasks.append(self._query_gong(query, context))
        if "hubspot_unified" in [s["name"] for s in servers]:
            tasks.append(self._query_hubspot(query, context))
        if "slack_v2" in [s["name"] for s in servers]:
            tasks.append(self._query_slack(query, context))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Synthesize response
        response_parts = []
        citations = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Server query failed: {result}")
                continue
            
            if isinstance(result, dict):
                if result.get("response"):
                    response_parts.append(result["response"])
                if result.get("citations"):
                    citations.extend(result["citations"])
        
        return {
            "response": "\n\n".join(response_parts) if response_parts else "I couldn't retrieve business intelligence data at this time.",
            "citations": citations,
            "sources": [s["name"] for s in servers]
        }
    
    async def _handle_code_analysis(
        self, query: str, intent: Intent, user_id: str, session_id: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle code analysis queries"""
        
        # Get code analysis servers
        servers = await self.mcp_orchestrator.get_servers_by_capability(["CODE_ANALYSIS"])
        
        # For now, return a placeholder
        return {
            "response": "Code analysis capabilities are being migrated to the unified orchestrator. Please check back soon.",
            "sources": [s["name"] for s in servers]
        }
    
    async def _handle_infrastructure(
        self, query: str, intent: Intent, user_id: str, session_id: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle infrastructure queries"""
        
        return {
            "response": "Infrastructure management should use the SophiaIaCOrchestrator for now. This capability will be integrated soon.",
            "sources": ["infrastructure"]
        }
    
    async def _handle_memory_query(
        self, query: str, intent: Intent, user_id: str, session_id: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle memory/recall queries"""
        
        # Search memory
        memories = await self.memory_service.search_conversations(
            user_id=user_id,
            query=query,
            limit=5
        )
        
        if memories:
            response_parts = ["Based on our previous conversations:"]
            for memory in memories:
                response_parts.append(f"- {memory.get('summary', memory.get('content', ''))}")
            
            return {
                "response": "\n".join(response_parts),
                "sources": ["unified_memory"]
            }
        else:
            return {
                "response": "I don't have any relevant previous conversations to recall.",
                "sources": ["unified_memory"]
            }
    
    async def _handle_general(
        self, query: str, intent: Intent, user_id: str, session_id: str, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle general queries"""
        
        # For general queries, search knowledge base and provide helpful response
        knowledge_results = self.memory_service.search_knowledge(
            query=query,
            limit=3
        )
        
        if knowledge_results:
            response_parts = ["Here's what I found:"]
            for result in knowledge_results:
                response_parts.append(f"- {result.get('content', '')}")
            
            return {
                "response": "\n".join(response_parts),
                "sources": ["knowledge_base"]
            }
        else:
            return {
                "response": "I can help you with business intelligence, code analysis, infrastructure management, or answer questions based on our previous conversations. What would you like to know?",
                "sources": ["general"]
            }
    
    async def _query_gong(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Query Gong MCP server"""
        try:
            # This will be implemented with actual MCP server calls
            return {
                "response": "Gong integration is being configured.",
                "source": "gong"
            }
        except Exception as e:
            logger.error(f"Gong query failed: {e}")
            raise
    
    async def _query_hubspot(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Query HubSpot MCP server"""
        try:
            # This will be implemented with actual MCP server calls
            return {
                "response": "HubSpot integration is being configured.",
                "source": "hubspot"
            }
        except Exception as e:
            logger.error(f"HubSpot query failed: {e}")
            raise
    
    async def _query_slack(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Query Slack MCP server"""
        try:
            # This will be implemented with actual MCP server calls
            return {
                "response": "Slack integration is being configured.",
                "source": "slack"
            }
        except Exception as e:
            logger.error(f"Slack query failed: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current orchestrator metrics"""
        return {
            "request_count": self.metrics.request_count,
            "error_count": self.metrics.error_count,
            "average_response_time": self.metrics.average_response_time,
            "active_users": len(self.metrics.active_users),
            "mcp_server_usage": self.metrics.mcp_server_usage,
            "health_score": self.metrics.calculate_health_score()
        }


# Global instance management
_orchestrator_instance: Optional[SophiaUnifiedOrchestrator] = None


def get_unified_orchestrator() -> SophiaUnifiedOrchestrator:
    """Get or create the unified orchestrator instance"""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = SophiaUnifiedOrchestrator()
    
    return _orchestrator_instance 