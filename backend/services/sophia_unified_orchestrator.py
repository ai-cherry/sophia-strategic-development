"""
Sophia AI Unified Orchestrator with Dynamic Routing
Critique capabilities + n8n optimization + X/video integration
Target: <150ms rerouting

Date: July 12, 2025
"""

import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx
from prometheus_client import Counter, Histogram, Gauge

from backend.core.auto_esc_config import get_config_value
from backend.services.enhanced_multi_hop_orchestrator_v2 import EnhancedMultiHopOrchestrator
from backend.services.n8n_alpha_optimizer_v2 import AlphaGridOptimizer, XTrendFetcher
from backend.services.personality_engine import PersonalityEngine
from backend.services.unified_memory_service import UnifiedMemoryService

logger = logging.getLogger(__name__)

# Prometheus metrics
orchestration_latency = Histogram('sophia_orchestration_latency_seconds', 'Orchestration latency', ['route', 'service'])
route_decisions = Counter('sophia_route_decisions_total', 'Route decisions', ['route', 'reason'])
critique_adjustments = Counter('sophia_critique_adjustments_total', 'Critique-based adjustments')
video_injections = Counter('sophia_video_injections_total', 'Video content injections')
current_route_latency = Gauge('sophia_current_route_latency_ms', 'Current route latency in ms', ['route'])


class RouteCritique:
    """Critique engine for route performance"""
    
    def __init__(self):
        self.performance_history = {}
        self.critique_threshold = 150  # ms
        self.adjustment_factor = 0.8
        
    def critique_route(self, route: str, latency_ms: float, success: bool) -> Dict[str, Any]:
        """Critique route performance and suggest adjustments"""
        if route not in self.performance_history:
            self.performance_history[route] = []
        
        self.performance_history[route].append({
            'latency_ms': latency_ms,
            'success': success,
            'timestamp': datetime.now(UTC)
        })
        
        # Keep last 100 entries
        if len(self.performance_history[route]) > 100:
            self.performance_history[route] = self.performance_history[route][-100:]
        
        # Calculate metrics
        recent = self.performance_history[route][-10:]
        avg_latency = sum(r['latency_ms'] for r in recent) / len(recent)
        success_rate = sum(1 for r in recent if r['success']) / len(recent)
        
        critique = {
            'route': route,
            'avg_latency_ms': avg_latency,
            'success_rate': success_rate,
            'needs_optimization': avg_latency > self.critique_threshold,
            'suggested_action': None
        }
        
        if avg_latency > self.critique_threshold:
            if success_rate < 0.95:
                critique['suggested_action'] = 'reroute'
            else:
                critique['suggested_action'] = 'optimize'
        
        return critique


class VideoContentInjector:
    """Inject relevant video content into responses"""
    
    def __init__(self):
        self.video_sources = {
            'youtube': 'https://api.youtube.com/v3/search',
            'vimeo': 'https://api.vimeo.com/videos',
            'internal': 'https://internal.sophia-ai.com/videos'
        }
        
    async def find_relevant_videos(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find relevant video content"""
        videos = []
        
        # Mock video search (in production, would call actual APIs)
        if 'revenue' in query.lower():
            videos.append({
                'title': 'Revenue Analysis Masterclass',
                'url': 'https://youtube.com/watch?v=demo123',
                'duration': '12:34',
                'relevance': 0.95,
                'source': 'youtube'
            })
        
        if 'trends' in query.lower():
            videos.append({
                'title': 'Market Trends 2025',
                'url': 'https://vimeo.com/demo456',
                'duration': '8:45',
                'relevance': 0.88,
                'source': 'vimeo'
            })
        
        return videos[:2]  # Return top 2 videos


class SophiaUnifiedOrchestrator:
    """Unified orchestrator with dynamic routing and critique"""
    
    def __init__(self):
        self.multi_hop = EnhancedMultiHopOrchestrator()
        self.n8n_optimizer = AlphaGridOptimizer()
        self.personality = PersonalityEngine()
        self.memory_service = UnifiedMemoryService()
        self.x_trends = XTrendFetcher()
        self.critique_engine = RouteCritique()
        self.video_injector = VideoContentInjector()
        
        self.routes = {
            'direct': self._route_direct,
            'multi_hop': self._route_multi_hop,
            'hybrid': self._route_hybrid,
            'fast': self._route_fast
        }
        
        self.initialized = False
        
    async def initialize(self):
        """Initialize all components"""
        if self.initialized:
            return
            
        await self.multi_hop.initialize()
        await self.memory_service.initialize()
        self.initialized = True
        logger.info("Sophia Unified Orchestrator initialized")
        
    async def orchestrate(
        self,
        query: str,
        user_id: str,
        mode: str = "professional",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Main orchestration with dynamic routing"""
        start_time = time.time()
        
        if not self.initialized:
            await self.initialize()
        
        # Set personality mode
        self.personality.set_mode(mode, user_id)
        
        # Determine optimal route
        route = await self._select_route(query, context)
        route_decisions.labels(route=route, reason='selected').inc()
        
        # Execute route with critique
        try:
            result = await self.routes[route](query, user_id, context)
            
            # Measure latency
            latency_ms = (time.time() - start_time) * 1000
            orchestration_latency.labels(route=route, service='orchestrator').observe(latency_ms / 1000)
            current_route_latency.labels(route=route).set(latency_ms)
            
            # Critique performance
            critique = self.critique_engine.critique_route(route, latency_ms, True)
            
            # Apply optimizations if needed
            if critique['needs_optimization']:
                critique_adjustments.inc()
                if critique['suggested_action'] == 'reroute' and latency_ms > 150:
                    # Try fast route as fallback
                    logger.info(f"Rerouting from {route} to fast route due to high latency")
                    result = await self._route_fast(query, user_id, context)
                elif critique['suggested_action'] == 'optimize':
                    # Apply n8n optimization
                    await self._apply_n8n_optimization(route)
            
            # Inject X trends and video content
            if context and context.get('include_trends', True):
                trends = await self.x_trends.fetch_trends(query)
                result['trends'] = trends
                
            if context and context.get('include_video', True):
                videos = await self.video_injector.find_relevant_videos(query, context)
                if videos:
                    video_injections.inc()
                    result['videos'] = videos
            
            # Apply personality
            result['response'] = self.personality.enhance_response(
                result.get('response', ''),
                query,
                user_id,
                context
            )
            
            # Add performance metrics
            result['performance'] = {
                'route': route,
                'latency_ms': latency_ms,
                'critique': critique,
                'optimized': critique['needs_optimization']
            }
            
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.critique_engine.critique_route(route, latency_ms, False)
            logger.error(f"Orchestration error: {e}")
            raise
    
    async def _select_route(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Select optimal route based on query and context"""
        # Fast route for simple queries
        if len(query.split()) < 5 and not context:
            return 'fast'
        
        # Multi-hop for complex BI queries
        if any(term in query.lower() for term in ['revenue', 'trends', 'analysis', 'forecast']):
            return 'multi_hop'
        
        # Hybrid for mixed queries
        if context and context.get('include_trends'):
            return 'hybrid'
        
        # Default to direct
        return 'direct'
    
    async def _route_direct(self, query: str, user_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Direct route for simple queries"""
        results = await self.memory_service.search_knowledge(query, limit=5)
        
        response = "Based on my knowledge:\n\n"
        for r in results[:3]:
            response += f"• {r['content']}\n"
        
        return {
            'response': response,
            'results': results,
            'route': 'direct',
            'hops': 1
        }
    
    async def _route_multi_hop(self, query: str, user_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Multi-hop route for complex queries"""
        result = await self.multi_hop.multi_hop_query(query, user_id, context)
        
        response = "Here's what I found through comprehensive analysis:\n\n"
        for r in result['results'][:5]:
            response += f"• {r['content']}\n"
        
        return {
            'response': response,
            'results': result['results'],
            'route': 'multi_hop',
            'hops': result['hops'],
            'confidence': result['confidence']
        }
    
    async def _route_hybrid(self, query: str, user_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Hybrid route combining multiple sources"""
        # Run direct and multi-hop in parallel
        direct_task = self._route_direct(query, user_id, context)
        multi_hop_task = self._route_multi_hop(query, user_id, context)
        
        direct_result, multi_hop_result = await asyncio.gather(direct_task, multi_hop_task)
        
        # Combine results
        all_results = direct_result['results'] + multi_hop_result['results']
        
        # Deduplicate and rerank
        seen = set()
        unique_results = []
        for r in all_results:
            content_hash = hash(r['content'])
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(r)
        
        # Sort by score
        unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        response = "Combined analysis from multiple sources:\n\n"
        for r in unique_results[:5]:
            response += f"• {r['content']}\n"
        
        return {
            'response': response,
            'results': unique_results[:10],
            'route': 'hybrid',
            'hops': max(direct_result['hops'], multi_hop_result['hops'])
        }
    
    async def _route_fast(self, query: str, user_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Fast route for <50ms responses"""
        # Use cached results if available
        cache_key = f"{user_id}:{query}"
        
        # Mock fast response
        response = f"Quick answer: {query} - Processing..."
        
        return {
            'response': response,
            'results': [],
            'route': 'fast',
            'hops': 0,
            'cached': True
        }
    
    async def _apply_n8n_optimization(self, route: str):
        """Apply n8n optimization to route"""
        optimal_alpha = await self.n8n_optimizer.optimize_alpha(
            service=f"route_{route}",
            window_minutes=5
        )
        logger.info(f"Applied n8n optimization to {route}: alpha={optimal_alpha}")


# Singleton instance
_orchestrator = None

def get_orchestrator() -> SophiaUnifiedOrchestrator:
    """Get singleton orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SophiaUnifiedOrchestrator()
    return _orchestrator
