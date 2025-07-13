"""
Unified Chat Orchestrator v3 - Phase 3
Integrates all Phase 2 enhancements into cohesive chat experience
Multi-hop reasoning + personality + trends + n8n optimization
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.services.enhanced_multi_hop_orchestrator import enhanced_orchestrator
from backend.services.n8n_alpha_optimizer import n8n_optimizer
from backend.services.x_trends_injector import x_trends_injector
from backend.services.personality_engine import personality_engine
from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
from backend.services.portkey_gateway import PortkeyGateway
from backend.core.auto_esc_config import get_config_value
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ChatMode(Enum):
    QUICK_ANSWER = "quick_answer"        # Direct response, minimal processing
    BUSINESS_INTELLIGENCE = "bi"         # Full BI analysis with trends
    STRATEGIC_ANALYSIS = "strategic"     # Deep multi-hop reasoning
    CONVERSATIONAL = "conversational"   # Personality-focused interaction


class ProcessingStage(Enum):
    INTENT_ANALYSIS = "intent_analysis"
    TREND_INJECTION = "trend_injection"
    MULTI_HOP_REASONING = "multi_hop_reasoning"
    PERSONALITY_SYNTHESIS = "personality_synthesis"
    OPTIMIZATION = "optimization"
    RESPONSE_GENERATION = "response_generation"


@dataclass
class ChatContext:
    """Enhanced chat context with all Phase 2 integrations"""
    user_id: str
    session_id: str
    query: str
    chat_mode: ChatMode
    
    # Phase 2 integrations
    trends_context: Optional[Dict[str, Any]] = None
    personality_profile: Optional[Dict[str, Any]] = None
    multi_hop_results: Optional[Dict[str, Any]] = None
    optimization_config: Optional[Dict[str, Any]] = None
    
    # Processing metadata
    processing_stages: List[str] = None
    performance_metrics: Dict[str, float] = None
    confidence_scores: Dict[str, float] = None
    
    def __post_init__(self):
        if self.processing_stages is None:
            self.processing_stages = []
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.confidence_scores is None:
            self.confidence_scores = {}


@dataclass
class UnifiedChatResponse:
    """Comprehensive chat response with all enhancement data"""
    content: str
    chat_mode: ChatMode
    user_id: str
    session_id: str
    
    # Phase 2 enhancement data
    personality_mode: str
    sass_level: float
    trends_injected: int
    multi_hop_steps: int
    optimization_applied: bool
    
    # Performance and confidence
    total_processing_time_ms: float
    stage_timings: Dict[str, float]
    confidence_score: float
    sources: List[str]
    
    # Metadata
    timestamp: datetime
    processing_stages: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "chat_mode": self.chat_mode.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "personality_mode": self.personality_mode,
            "sass_level": self.sass_level,
            "trends_injected": self.trends_injected,
            "multi_hop_steps": self.multi_hop_steps,
            "optimization_applied": self.optimization_applied,
            "total_processing_time_ms": self.total_processing_time_ms,
            "stage_timings": self.stage_timings,
            "confidence_score": self.confidence_score,
            "sources": self.sources,
            "timestamp": self.timestamp.isoformat(),
            "processing_stages": self.processing_stages
        }


class UnifiedChatOrchestratorV3:
    """
    Unified chat orchestrator integrating all Phase 2 enhancements
    Provides seamless, intelligent, and optimized chat experience
    """
    
    def __init__(self):
        # Core services
        self.memory_service = UnifiedMemoryServiceV2()
        self.portkey = PortkeyGateway()
        
        # Phase 2 service integrations
        self.multi_hop_orchestrator = enhanced_orchestrator
        self.n8n_optimizer = n8n_optimizer
        self.trends_injector = x_trends_injector
        self.personality_engine = personality_engine
        
        # Chat session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Performance tracking
        self.stats = {
            "total_chats": 0,
            "avg_processing_time_ms": 0.0,
            "avg_confidence_score": 0.0,
            "mode_distribution": {mode.value: 0 for mode in ChatMode},
            "stage_performance": {stage.value: 0.0 for stage in ProcessingStage}
        }
        
        # Configuration
        self.default_chat_mode = ChatMode.BUSINESS_INTELLIGENCE
        self.max_trends_injection = 3
        self.confidence_threshold = 0.7
        
    async def process_chat(self, 
                          query: str, 
                          user_id: str = "default_user",
                          session_id: Optional[str] = None,
                          chat_mode: Optional[ChatMode] = None) -> UnifiedChatResponse:
        """Main chat processing pipeline with all Phase 2 integrations"""
        
        start_time = time.time()
        
        # Initialize session
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        # Determine chat mode
        if not chat_mode:
            chat_mode = await self._determine_chat_mode(query, user_id)
        
        # Create chat context
        context = ChatContext(
            user_id=user_id,
            session_id=session_id,
            query=query,
            chat_mode=chat_mode
        )
        
        # Initialize session if new
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "message_count": 0,
                "context_history": []
            }
        
        try:
            # Execute processing pipeline
            response = await self._execute_processing_pipeline(context)
            
            # Update session
            self._update_session(session_id, context, response)
            
            # Update statistics
            self._update_stats(response)
            
            logger.info(f"Chat processed: {chat_mode.value} mode, {response.total_processing_time_ms:.1f}ms, confidence: {response.confidence_score:.3f}")
            
            return response
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            
            # Return fallback response
            return await self._generate_fallback_response(context, str(e), time.time() - start_time)
    
    async def _determine_chat_mode(self, query: str, user_id: str) -> ChatMode:
        """Intelligently determine appropriate chat mode"""
        
        query_lower = query.lower()
        
        # Quick answer patterns
        quick_patterns = ["what is", "define", "explain briefly", "quick question"]
        if any(pattern in query_lower for pattern in quick_patterns):
            return ChatMode.QUICK_ANSWER
        
        # Strategic analysis patterns
        strategic_patterns = ["strategy", "roadmap", "long-term", "vision", "planning", "forecast"]
        if any(pattern in query_lower for pattern in strategic_patterns):
            return ChatMode.STRATEGIC_ANALYSIS
        
        # Conversational patterns
        conversational_patterns = ["how are you", "hello", "hi", "thanks", "thank you"]
        if any(pattern in query_lower for pattern in conversational_patterns):
            return ChatMode.CONVERSATIONAL
        
        # Default to business intelligence for most queries
        return ChatMode.BUSINESS_INTELLIGENCE
    
    async def _execute_processing_pipeline(self, context: ChatContext) -> UnifiedChatResponse:
        """Execute the full processing pipeline with all Phase 2 integrations"""
        
        stage_timings = {}
        
        # Stage 1: Intent Analysis
        stage_start = time.time()
        await self._stage_intent_analysis(context)
        stage_timings[ProcessingStage.INTENT_ANALYSIS.value] = (time.time() - stage_start) * 1000
        
        # Stage 2: Trend Injection (if applicable)
        if context.chat_mode in [ChatMode.BUSINESS_INTELLIGENCE, ChatMode.STRATEGIC_ANALYSIS]:
            stage_start = time.time()
            await self._stage_trend_injection(context)
            stage_timings[ProcessingStage.TREND_INJECTION.value] = (time.time() - stage_start) * 1000
        
        # Stage 3: Multi-hop Reasoning (for complex queries)
        if context.chat_mode in [ChatMode.STRATEGIC_ANALYSIS, ChatMode.BUSINESS_INTELLIGENCE]:
            stage_start = time.time()
            await self._stage_multi_hop_reasoning(context)
            stage_timings[ProcessingStage.MULTI_HOP_REASONING.value] = (time.time() - stage_start) * 1000
        
        # Stage 4: Personality Synthesis
        stage_start = time.time()
        await self._stage_personality_synthesis(context)
        stage_timings[ProcessingStage.PERSONALITY_SYNTHESIS.value] = (time.time() - stage_start) * 1000
        
        # Stage 5: Optimization
        stage_start = time.time()
        await self._stage_optimization(context)
        stage_timings[ProcessingStage.OPTIMIZATION.value] = (time.time() - stage_start) * 1000
        
        # Stage 6: Response Generation
        stage_start = time.time()
        response = await self._stage_response_generation(context, stage_timings)
        stage_timings[ProcessingStage.RESPONSE_GENERATION.value] = (time.time() - stage_start) * 1000
        
        return response
    
    async def _stage_intent_analysis(self, context: ChatContext) -> None:
        """Stage 1: Analyze intent and prepare context"""
        
        context.processing_stages.append(ProcessingStage.INTENT_ANALYSIS.value)
        
        # Basic intent analysis
        intent_prompt = f"""Analyze this query for business intelligence context:
        
        Query: {context.query}
        Mode: {context.chat_mode.value}
        
        Determine:
        1. Primary intent (question, request, analysis, conversation)
        2. Business domain (finance, sales, operations, strategy, general)
        3. Complexity level (simple, moderate, complex)
        4. Expected response type (data, insight, recommendation, conversation)
        
        Return JSON: {{"intent": "...", "domain": "...", "complexity": "...", "response_type": "..."}}
        """
        
        try:
            response = await self.portkey.completions.create(
                model="claude-3-5-sonnet-20240620",
                messages=[{"role": "user", "content": intent_prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            intent_data = json.loads(response.choices[0].message.content)
            context.confidence_scores["intent_analysis"] = 0.9
            
            # Store intent data for later stages
            if not hasattr(context, 'intent_data'):
                context.intent_data = intent_data
            
        except Exception as e:
            logger.warning(f"Intent analysis failed: {e}")
            context.confidence_scores["intent_analysis"] = 0.5
            context.intent_data = {"intent": "question", "domain": "general", "complexity": "moderate"}
    
    async def _stage_trend_injection(self, context: ChatContext) -> None:
        """Stage 2: Inject relevant trends if applicable"""
        
        context.processing_stages.append(ProcessingStage.TREND_INJECTION.value)
        
        try:
            # Get trend context
            trend_context = await self.trends_injector.enhance_query_with_trends(
                context.query, 
                max_trends=self.max_trends_injection
            )
            
            context.trends_context = trend_context.to_dict()
            context.confidence_scores["trend_injection"] = trend_context.relevance_score
            
            logger.info(f"Injected {len(trend_context.trending_topics)} trends (relevance: {trend_context.relevance_score:.3f})")
            
        except Exception as e:
            logger.warning(f"Trend injection failed: {e}")
            context.confidence_scores["trend_injection"] = 0.0
            context.trends_context = {"trending_topics": [], "relevance_score": 0.0}
    
    async def _stage_multi_hop_reasoning(self, context: ChatContext) -> None:
        """Stage 3: Apply multi-hop reasoning for complex queries"""
        
        context.processing_stages.append(ProcessingStage.MULTI_HOP_REASONING.value)
        
        try:
            # Determine if multi-hop reasoning is needed
            complexity = getattr(context, 'intent_data', {}).get('complexity', 'moderate')
            
            if complexity in ['complex'] or context.chat_mode == ChatMode.STRATEGIC_ANALYSIS:
                # Execute multi-hop orchestration
                multi_hop_result = await self.multi_hop_orchestrator.orchestrate_enhanced(
                    context.query,
                    context.user_id
                )
                
                context.multi_hop_results = multi_hop_result
                context.confidence_scores["multi_hop_reasoning"] = multi_hop_result.get("confidence", 0.7)
                
                logger.info(f"Multi-hop reasoning: {multi_hop_result.get('reasoning_steps', 0)} steps, "
                           f"recall boost: {multi_hop_result.get('recall_boost', 1.0):.2f}")
            else:
                context.confidence_scores["multi_hop_reasoning"] = 0.8  # High confidence for simpler queries
                
        except Exception as e:
            logger.warning(f"Multi-hop reasoning failed: {e}")
            context.confidence_scores["multi_hop_reasoning"] = 0.6
            context.multi_hop_results = None
    
    async def _stage_personality_synthesis(self, context: ChatContext) -> None:
        """Stage 4: Apply personality-aware synthesis"""
        
        context.processing_stages.append(ProcessingStage.PERSONALITY_SYNTHESIS.value)
        
        try:
            # Prepare data context for personality engine
            data_context = {
                "query": context.query,
                "chat_mode": context.chat_mode.value,
                "trends": context.trends_context,
                "multi_hop": context.multi_hop_results,
                "intent": getattr(context, 'intent_data', {})
            }
            
            # Generate personality response
            personality_response = await self.personality_engine.generate_personalized_response(
                context.query,
                data_context,
                context.user_id
            )
            
            context.personality_profile = personality_response.to_dict()
            context.confidence_scores["personality_synthesis"] = personality_response.confidence
            
            logger.info(f"Personality synthesis: {personality_response.personality_mode.value} mode, "
                       f"sass: {personality_response.sass_level:.2f}")
            
        except Exception as e:
            logger.warning(f"Personality synthesis failed: {e}")
            context.confidence_scores["personality_synthesis"] = 0.6
            context.personality_profile = {
                "personality_mode": "professional",
                "sass_level": 0.6,
                "content": "Professional response mode"
            }
    
    async def _stage_optimization(self, context: ChatContext) -> None:
        """Stage 5: Apply n8n optimization configurations"""
        
        context.processing_stages.append(ProcessingStage.OPTIMIZATION.value)
        
        try:
            # Register performance metrics for optimization
            processing_time = sum(context.performance_metrics.values()) if context.performance_metrics else 150
            
            # Get optimization config
            endpoint = f"chat/{context.chat_mode.value}"
            await self.n8n_optimizer.register_api_call(
                endpoint=endpoint,
                response_time_ms=processing_time,
                success=True,
                query_type="hybrid"
            )
            
            # Get optimized alpha for future requests
            optimal_alpha = await self.n8n_optimizer.get_optimal_alpha(endpoint)
            
            context.optimization_config = {
                "endpoint": endpoint,
                "optimal_alpha": optimal_alpha,
                "processing_time_ms": processing_time
            }
            
            context.confidence_scores["optimization"] = 0.9
            
        except Exception as e:
            logger.warning(f"Optimization failed: {e}")
            context.confidence_scores["optimization"] = 0.7
            context.optimization_config = {"optimal_alpha": 0.5}
    
    async def _stage_response_generation(self, context: ChatContext, stage_timings: Dict[str, float]) -> UnifiedChatResponse:
        """Stage 6: Generate final unified response"""
        
        context.processing_stages.append(ProcessingStage.RESPONSE_GENERATION.value)
        
        # Extract response content
        if context.personality_profile:
            content = context.personality_profile.get("content", "I can help you with that.")
            personality_mode = context.personality_profile.get("personality_mode", "professional")
            sass_level = context.personality_profile.get("sass_level", 0.6)
        else:
            content = "I can help you with that."
            personality_mode = "professional"
            sass_level = 0.6
        
        # Count enhancements applied
        trends_injected = len(context.trends_context.get("trending_topics", [])) if context.trends_context else 0
        multi_hop_steps = context.multi_hop_results.get("reasoning_steps", 0) if context.multi_hop_results else 0
        optimization_applied = bool(context.optimization_config)
        
        # Calculate overall confidence
        confidence_scores = list(context.confidence_scores.values())
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.7
        
        # Collect sources
        sources = []
        if context.multi_hop_results:
            sources.extend(context.multi_hop_results.get("sources", []))
        if context.trends_context:
            sources.append("x_trends")
        
        # Calculate total processing time
        total_time = sum(stage_timings.values())
        
        return UnifiedChatResponse(
            content=content,
            chat_mode=context.chat_mode,
            user_id=context.user_id,
            session_id=context.session_id,
            personality_mode=personality_mode,
            sass_level=sass_level,
            trends_injected=trends_injected,
            multi_hop_steps=multi_hop_steps,
            optimization_applied=optimization_applied,
            total_processing_time_ms=total_time,
            stage_timings=stage_timings,
            confidence_score=overall_confidence,
            sources=list(set(sources)),  # Deduplicate
            timestamp=datetime.utcnow(),
            processing_stages=context.processing_stages
        )
    
    async def _generate_fallback_response(self, context: ChatContext, error: str, processing_time: float) -> UnifiedChatResponse:
        """Generate fallback response when processing fails"""
        
        return UnifiedChatResponse(
            content="I apologize, but I encountered an issue processing your request. Please try again.",
            chat_mode=context.chat_mode,
            user_id=context.user_id,
            session_id=context.session_id,
            personality_mode="professional",
            sass_level=0.4,
            trends_injected=0,
            multi_hop_steps=0,
            optimization_applied=False,
            total_processing_time_ms=processing_time * 1000,
            stage_timings={"error": processing_time * 1000},
            confidence_score=0.3,
            sources=["fallback"],
            timestamp=datetime.utcnow(),
            processing_stages=["error_fallback"]
        )
    
    def _update_session(self, session_id: str, context: ChatContext, response: UnifiedChatResponse) -> None:
        """Update session with context and response"""
        
        session = self.active_sessions[session_id]
        session["message_count"] += 1
        session["last_activity"] = datetime.utcnow()
        
        # Store conversation history
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        
        self.session_history[session_id].append({
            "query": context.query,
            "response": response.content,
            "chat_mode": context.chat_mode.value,
            "confidence": response.confidence_score,
            "timestamp": response.timestamp.isoformat()
        })
        
        # Keep only last 20 messages per session
        if len(self.session_history[session_id]) > 20:
            self.session_history[session_id] = self.session_history[session_id][-20:]
    
    def _update_stats(self, response: UnifiedChatResponse) -> None:
        """Update performance statistics"""
        
        self.stats["total_chats"] += 1
        
        # Update averages
        total_chats = self.stats["total_chats"]
        self.stats["avg_processing_time_ms"] = (
            (self.stats["avg_processing_time_ms"] * (total_chats - 1) + response.total_processing_time_ms) / total_chats
        )
        self.stats["avg_confidence_score"] = (
            (self.stats["avg_confidence_score"] * (total_chats - 1) + response.confidence_score) / total_chats
        )
        
        # Update mode distribution
        self.stats["mode_distribution"][response.chat_mode.value] += 1
        
        # Update stage performance
        for stage, timing in response.stage_timings.items():
            if stage in self.stats["stage_performance"]:
                current_avg = self.stats["stage_performance"][stage]
                self.stats["stage_performance"][stage] = (current_avg + timing) / 2
    
    async def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session context and history"""
        
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        history = self.session_history.get(session_id, [])
        
        return {
            "session_info": session,
            "message_history": history[-10:],  # Last 10 messages
            "total_messages": len(history)
        }
    
    async def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator statistics"""
        
        return {
            "performance_stats": self.stats,
            "active_sessions": len(self.active_sessions),
            "total_session_history": sum(len(history) for history in self.session_history.values()),
            "service_integration_status": {
                "multi_hop_orchestrator": bool(self.multi_hop_orchestrator),
                "n8n_optimizer": bool(self.n8n_optimizer),
                "trends_injector": bool(self.trends_injector),
                "personality_engine": bool(self.personality_engine)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def process_streaming_chat(self, 
                                   query: str, 
                                   user_id: str = "default_user",
                                   session_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Process chat with streaming updates for real-time feedback"""
        
        if not session_id:
            session_id = f"stream_{int(time.time())}"
        
        # Yield initial status
        yield {
            "type": "status",
            "stage": "initializing",
            "message": "Starting chat processing...",
            "session_id": session_id
        }
        
        # Determine chat mode
        chat_mode = await self._determine_chat_mode(query, user_id)
        yield {
            "type": "status",
            "stage": "mode_determined",
            "chat_mode": chat_mode.value,
            "message": f"Processing in {chat_mode.value} mode"
        }
        
        # Process with streaming updates
        context = ChatContext(
            user_id=user_id,
            session_id=session_id,
            query=query,
            chat_mode=chat_mode
        )
        
        # Stream each processing stage
        stages = [
            ("intent_analysis", "Analyzing intent..."),
            ("trend_injection", "Injecting relevant trends..."),
            ("multi_hop_reasoning", "Applying multi-hop reasoning..."),
            ("personality_synthesis", "Synthesizing personality..."),
            ("optimization", "Optimizing performance..."),
            ("response_generation", "Generating response...")
        ]
        
        for stage_name, stage_message in stages:
            yield {
                "type": "status",
                "stage": stage_name,
                "message": stage_message
            }
            
            # Small delay to simulate processing
            await asyncio.sleep(0.1)
        
        # Process normally and yield final result
        response = await self.process_chat(query, user_id, session_id, chat_mode)
        
        yield {
            "type": "response",
            "data": response.to_dict()
        }


# Global instance for service injection
unified_chat_orchestrator_v3 = UnifiedChatOrchestratorV3() 