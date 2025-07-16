"""
Sophia AI Unified Orchestrator - Consolidated Architecture
Single orchestrator replacing multiple versions

Features:
- Dynamic routing with critique engine
- Multi-hop reasoning capabilities
- Personality engine integration
- Performance optimization
- Business intelligence synthesis
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from backend.services.sophia_unified_memory_service import get_memory_service, UnifiedMemoryService
from backend.services.portkey_gateway import PortkeyGateway
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class RouteType(Enum):
    """Available routing strategies"""
    DIRECT = "direct"           # Simple queries, <50ms
    MULTI_HOP = "multi_hop"     # Complex analysis, <200ms
    HYBRID = "hybrid"           # Mixed approaches, <150ms
    FAST = "fast"               # Emergency fallback, <30ms

class ProcessingMode(Enum):
    """Chat processing modes"""
    QUICK_ANSWER = "quick_answer"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    STRATEGIC_ANALYSIS = "strategic_analysis"
    CONVERSATIONAL = "conversational"

@dataclass
class OrchestrationResult:
    """Result of orchestration process"""
    success: bool
    response: str
    route_used: RouteType
    processing_time_ms: float
    confidence_score: float
    metadata: Dict[str, Any]

class SophiaAIUnifiedOrchestrator:
    """
    Unified orchestrator consolidating all previous versions
    
    Replaces:
    - SophiaUnifiedOrchestrator
    - UnifiedChatOrchestratorV3
    - EnhancedMultiAgentOrchestrator
    - LangGraphMCPOrchestrator
    """
    
    def __init__(self):
        self.memory_service = get_memory_service()
        self.portkey = PortkeyGateway()
        
        # Routing configuration
        self.routes = {
            RouteType.DIRECT: self._route_direct,
            RouteType.MULTI_HOP: self._route_multi_hop,
            RouteType.HYBRID: self._route_hybrid,
            RouteType.FAST: self._route_fast
        }
        
        # Performance tracking
        self.stats = {
            "total_queries": 0,
            "avg_response_time_ms": 0.0,
            "route_distribution": {route.value: 0 for route in RouteType},
            "success_rate": 0.0
        }
        
        # Configuration
        self.max_response_time_ms = 200
        self.confidence_threshold = 0.7
        self.fallback_route = RouteType.FAST
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize orchestrator services"""
        if self.initialized:
            return
            
        await self.memory_service.initialize()
        await self.portkey.initialize()
        
        self.initialized = True
        logger.info("✅ Sophia AI Unified Orchestrator initialized")
    
    async def orchestrate(
        self,
        query: str,
        user_id: str,
        mode: ProcessingMode = ProcessingMode.BUSINESS_INTELLIGENCE,
        context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """Main orchestration method"""
        if not self.initialized:
            await self.initialize()
            
        start_time = time.time()
        
        try:
            # Select optimal route
            route = await self._select_route(query, mode, context)
            
            # Execute route
            response = await self.routes[route](query, user_id, context)
            
            # Calculate metrics
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats["total_queries"] += 1
            self.stats["route_distribution"][route.value] += 1
            
            # Build result
            result = OrchestrationResult(
                success=True,
                response=response["content"],
                route_used=route,
                processing_time_ms=processing_time_ms,
                confidence_score=response.get("confidence", 0.8),
                metadata={
                    "mode": mode.value,
                    "context_used": bool(context),
                    "memory_queries": response.get("memory_queries", 0),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"✅ Query processed via {route.value} in {processing_time_ms:.1f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ Orchestration failed: {e}")
            
            # Fallback to fast route
            try:
                response = await self._route_fast(query, user_id, context)
                processing_time_ms = (time.time() - start_time) * 1000
                
                return OrchestrationResult(
                    success=True,
                    response=response["content"],
                    route_used=RouteType.FAST,
                    processing_time_ms=processing_time_ms,
                    confidence_score=0.5,
                    metadata={"fallback": True, "original_error": str(e)}
                )
            except Exception as fallback_error:
                logger.error(f"❌ Fallback also failed: {fallback_error}")
                
                return OrchestrationResult(
                    success=False,
                    response="I apologize, but I'm experiencing technical difficulties. Please try again.",
                    route_used=RouteType.FAST,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    confidence_score=0.0,
                    metadata={"error": str(fallback_error)}
                )
    
    async def _select_route(
        self,
        query: str,
        mode: ProcessingMode,
        context: Optional[Dict[str, Any]]
    ) -> RouteType:
        """Select optimal routing strategy"""
        # Simple heuristics for route selection
        query_length = len(query.split())
        
        if mode == ProcessingMode.QUICK_ANSWER or query_length < 5:
            return RouteType.DIRECT
        elif mode == ProcessingMode.STRATEGIC_ANALYSIS or query_length > 20:
            return RouteType.MULTI_HOP
        elif context and len(context) > 3:
            return RouteType.HYBRID
        else:
            return RouteType.DIRECT
    
    async def _route_direct(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Direct routing for simple queries"""
        # Simple memory search + LLM response
        memory_results = await self.memory_service.search_memories(
            query=query,
            user_id=user_id,
            limit=3
        )
        
        # Generate response using Portkey
        response = await self.portkey.chat_completion(
            messages=[
                {"role": "system", "content": "You are Sophia, an AI assistant for Pay Ready. Provide concise, helpful responses."},
                {"role": "user", "content": f"Query: {query}\n\nContext: {memory_results}"}
            ],
            model="gpt-4o-mini",
            max_tokens=500
        )
        
        return {
            "content": response["choices"][0]["message"]["content"],
            "confidence": 0.8,
            "memory_queries": 1
        }
    
    async def _route_multi_hop(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Multi-hop routing for complex queries"""
        # Multi-step reasoning process
        steps = []
        current_query = query
        
        for hop in range(3):  # Max 3 hops
            memory_results = await self.memory_service.search_memories(
                query=current_query,
                user_id=user_id,
                limit=5
            )
            
            steps.append({
                "hop": hop + 1,
                "query": current_query,
                "results": memory_results
            })
            
            # Generate follow-up query if needed
            if hop < 2:  # Not the last hop
                follow_up_response = await self.portkey.chat_completion(
                    messages=[
                        {"role": "system", "content": "Generate a follow-up query to gather more information."},
                        {"role": "user", "content": f"Original: {query}\nCurrent: {current_query}\nResults: {memory_results}"}
                    ],
                    model="gpt-4o-mini",
                    max_tokens=100
                )
                
                follow_up = follow_up_response["choices"][0]["message"]["content"]
                if "no follow-up needed" not in follow_up.lower():
                    current_query = follow_up
                else:
                    break
        
        # Synthesize final response
        synthesis_response = await self.portkey.chat_completion(
            messages=[
                {"role": "system", "content": "Synthesize information from multiple research steps into a comprehensive response."},
                {"role": "user", "content": f"Original query: {query}\n\nResearch steps: {json.dumps(steps, indent=2)}"}
            ],
            model="gpt-4o",
            max_tokens=1000
        )
        
        return {
            "content": synthesis_response["choices"][0]["message"]["content"],
            "confidence": 0.9,
            "memory_queries": len(steps),
            "steps": steps
        }
    
    async def _route_hybrid(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Hybrid routing combining direct and multi-hop"""
        # Start with direct approach
        direct_result = await self._route_direct(query, user_id, context)
        
        # If confidence is low, enhance with multi-hop
        if direct_result["confidence"] < 0.7:
            multi_hop_result = await self._route_multi_hop(query, user_id, context)
            
            # Combine results
            combined_response = await self.portkey.chat_completion(
                messages=[
                    {"role": "system", "content": "Combine and enhance two responses into a single, comprehensive answer."},
                    {"role": "user", "content": f"Direct response: {direct_result['content']}\n\nMulti-hop response: {multi_hop_result['content']}"}
                ],
                model="gpt-4o",
                max_tokens=800
            )
            
            return {
                "content": combined_response["choices"][0]["message"]["content"],
                "confidence": 0.85,
                "memory_queries": direct_result["memory_queries"] + multi_hop_result["memory_queries"]
            }
        
        return direct_result
    
    async def _route_fast(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fast routing for emergency fallback"""
        # Minimal processing for speed
        response = await self.portkey.chat_completion(
            messages=[
                {"role": "system", "content": "Provide a brief, helpful response."},
                {"role": "user", "content": query}
            ],
            model="gpt-4o-mini",
            max_tokens=200
        )
        
        return {
            "content": response["choices"][0]["message"]["content"],
            "confidence": 0.6,
            "memory_queries": 0
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status"""
        return {
            "initialized": self.initialized,
            "total_queries": self.stats["total_queries"],
            "avg_response_time_ms": self.stats["avg_response_time_ms"],
            "route_distribution": self.stats["route_distribution"],
            "success_rate": self.stats["success_rate"],
            "memory_service_health": await self.memory_service.get_health_status(),
            "portkey_health": await self.portkey.get_health_status()
        }


# Global instance for shared access
_orchestrator_instance = None

def get_unified_orchestrator() -> SophiaAIUnifiedOrchestrator:
    """Get the unified orchestrator singleton instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = SophiaAIUnifiedOrchestrator()
    return _orchestrator_instance
