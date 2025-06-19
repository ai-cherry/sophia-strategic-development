"""
Hybrid RAG Router with Intelligent Query Classification
Routes queries optimally between vector search, MCP federation, and Agno orchestration
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import re
import statistics

from backend.integrations.enhanced_agno_integration import enhanced_agno_integration
from backend.mcp.enhanced_mcp_federation import mcp_federation
from backend.knowledge.hybrid_rag_manager import hybrid_rag_manager
from backend.integrations.llamaindex_integration import llamaindex_integration

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of queries that can be processed."""
    SEMANTIC_SEARCH = "semantic_search"
    STRUCTURED_QUERY = "structured_query"
    HYBRID_WORKFLOW = "hybrid_workflow"
    AGENT_ORCHESTRATION = "agent_orchestration"
    DOCUMENT_ANALYSIS = "document_analysis"

@dataclass
class RoutingDecision:
    """Decision made by the query router."""
    query_type: QueryType
    primary_engine: str
    secondary_engines: List[str]
    confidence: float
    reasoning: str
    estimated_time_ms: int
    parallel_execution: bool

@dataclass
class ProcessingResult:
    """Result from query processing."""
    success: bool
    data: Any
    engine: str
    execution_time_ms: float
    confidence: float
    metadata: Dict[str, Any]
    error: Optional[str] = None

class MLQueryClassifier:
    """Machine learning-based query classifier."""
    
    def __init__(self):
        """Initialize ML query classifier."""
        self.patterns = {
            QueryType.SEMANTIC_SEARCH: [
                r'\b(find|search|look for|locate|discover)\b.*\b(document|file|content|information)\b',
                r'\b(what|where|when|who|how)\b.*\b(about|regarding|concerning)\b',
                r'\b(similar|related|like|comparable)\b.*\b(to|as)\b',
                r'\b(meaning|definition|explanation|description)\b'
            ],
            QueryType.STRUCTURED_QUERY: [
                r'\b(get|retrieve|fetch|pull)\b.*\b(data|records|entries|items)\b',
                r'\b(list|show|display)\b.*\b(all|recent|latest|current)\b',
                r'\b(count|number|total|sum)\b.*\b(of|in)\b',
                r'\b(filter|where|having|with)\b.*\b(condition|criteria)\b'
            ],
            QueryType.HYBRID_WORKFLOW: [
                r'\b(analyze|process|generate|create)\b.*\b(report|summary|analysis|insights)\b',
                r'\b(combine|merge|integrate)\b.*\b(data|information|sources)\b',
                r'\b(workflow|process|pipeline|automation)\b',
                r'\b(business intelligence|bi|analytics|metrics)\b'
            ],
            QueryType.AGENT_ORCHESTRATION: [
                r'\b(automate|orchestrate|coordinate|manage)\b.*\b(task|process|workflow)\b',
                r'\b(agent|assistant|ai)\b.*\b(help|assist|perform|execute)\b',
                r'\b(multi-step|complex|advanced)\b.*\b(operation|task|process)\b',
                r'\b(collaboration|teamwork|coordination)\b'
            ],
            QueryType.DOCUMENT_ANALYSIS: [
                r'\b(analyze|examine|review|study)\b.*\b(document|file|text|content)\b',
                r'\b(extract|parse|process)\b.*\b(information|data|insights)\b',
                r'\b(summarize|abstract|overview)\b.*\b(of|from)\b',
                r'\b(key points|main ideas|important|highlights)\b'
            ]
        }
        
        self.engine_capabilities = {
            "vector_search": {
                "strengths": ["semantic similarity", "document retrieval", "content search"],
                "speed": "fast",
                "accuracy": "high",
                "best_for": [QueryType.SEMANTIC_SEARCH, QueryType.DOCUMENT_ANALYSIS]
            },
            "mcp_federation": {
                "strengths": ["structured data", "real-time info", "service integration"],
                "speed": "medium",
                "accuracy": "very_high",
                "best_for": [QueryType.STRUCTURED_QUERY, QueryType.HYBRID_WORKFLOW]
            },
            "agno_orchestration": {
                "strengths": ["complex workflows", "multi-step tasks", "agent coordination"],
                "speed": "variable",
                "accuracy": "high",
                "best_for": [QueryType.AGENT_ORCHESTRATION, QueryType.HYBRID_WORKFLOW]
            },
            "llamaindex": {
                "strengths": ["document intelligence", "advanced parsing", "entity extraction"],
                "speed": "medium",
                "accuracy": "very_high",
                "best_for": [QueryType.DOCUMENT_ANALYSIS, QueryType.SEMANTIC_SEARCH]
            }
        }
    
    def classify_query(self, query: str, context: Dict[str, Any] = None) -> RoutingDecision:
        """
        Classify query using ML patterns and context.
        
        Args:
            query: The query string
            context: Additional context for classification
            
        Returns:
            RoutingDecision with optimal routing strategy
        """
        query_lower = query.lower()
        context = context or {}
        
        # Score each query type
        type_scores = {}
        for query_type, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            type_scores[query_type] = score
        
        # Determine primary query type
        if not any(type_scores.values()):
            # Default classification based on context
            primary_type = self._classify_by_context(query, context)
        else:
            primary_type = max(type_scores, key=type_scores.get)
        
        # Determine optimal engines
        primary_engine, secondary_engines = self._select_engines(primary_type, query, context)
        
        # Calculate confidence
        max_score = max(type_scores.values()) if type_scores.values() else 0
        total_patterns = sum(len(patterns) for patterns in self.patterns.values())
        confidence = max_score / total_patterns if total_patterns > 0 else 0.5
        
        # Adjust confidence based on context
        if context.get("user_preferences"):
            confidence += 0.1
        if context.get("historical_performance"):
            confidence += 0.1
        
        confidence = min(1.0, confidence)
        
        # Determine execution strategy
        parallel_execution = len(secondary_engines) > 0 and confidence < 0.8
        estimated_time = self._estimate_execution_time(primary_engine, secondary_engines, parallel_execution)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(primary_type, primary_engine, secondary_engines, confidence)
        
        return RoutingDecision(
            query_type=primary_type,
            primary_engine=primary_engine,
            secondary_engines=secondary_engines,
            confidence=confidence,
            reasoning=reasoning,
            estimated_time_ms=estimated_time,
            parallel_execution=parallel_execution
        )
    
    def _classify_by_context(self, query: str, context: Dict[str, Any]) -> QueryType:
        """Classify query based on context when patterns don't match."""
        # Check for document-related context
        if context.get("document_context") or "document" in query.lower():
            return QueryType.DOCUMENT_ANALYSIS
        
        # Check for business context
        if context.get("business_context") or any(word in query.lower() for word in ["sales", "revenue", "customer", "business"]):
            return QueryType.HYBRID_WORKFLOW
        
        # Check for automation context
        if context.get("automation_context") or any(word in query.lower() for word in ["automate", "workflow", "process"]):
            return QueryType.AGENT_ORCHESTRATION
        
        # Check for data context
        if context.get("data_context") or any(word in query.lower() for word in ["data", "database", "records"]):
            return QueryType.STRUCTURED_QUERY
        
        # Default to semantic search
        return QueryType.SEMANTIC_SEARCH
    
    def _select_engines(self, query_type: QueryType, query: str, context: Dict[str, Any]) -> tuple[str, List[str]]:
        """Select optimal engines for query type."""
        # Primary engine selection
        primary_engines = {
            QueryType.SEMANTIC_SEARCH: "vector_search",
            QueryType.STRUCTURED_QUERY: "mcp_federation",
            QueryType.HYBRID_WORKFLOW: "agno_orchestration",
            QueryType.AGENT_ORCHESTRATION: "agno_orchestration",
            QueryType.DOCUMENT_ANALYSIS: "llamaindex"
        }
        
        primary_engine = primary_engines.get(query_type, "vector_search")
        
        # Secondary engine selection
        secondary_engines = []
        
        if query_type == QueryType.SEMANTIC_SEARCH:
            secondary_engines = ["llamaindex"]
            if any(word in query.lower() for word in ["recent", "latest", "current"]):
                secondary_engines.append("mcp_federation")
        
        elif query_type == QueryType.STRUCTURED_QUERY:
            secondary_engines = ["vector_search"]
            if context.get("requires_analysis"):
                secondary_engines.append("agno_orchestration")
        
        elif query_type == QueryType.HYBRID_WORKFLOW:
            secondary_engines = ["mcp_federation", "vector_search"]
            if context.get("document_processing"):
                secondary_engines.append("llamaindex")
        
        elif query_type == QueryType.AGENT_ORCHESTRATION:
            secondary_engines = ["mcp_federation"]
            if context.get("knowledge_required"):
                secondary_engines.append("vector_search")
        
        elif query_type == QueryType.DOCUMENT_ANALYSIS:
            secondary_engines = ["vector_search"]
            if context.get("structured_data"):
                secondary_engines.append("mcp_federation")
        
        return primary_engine, secondary_engines
    
    def _estimate_execution_time(self, primary_engine: str, secondary_engines: List[str], parallel: bool) -> int:
        """Estimate execution time in milliseconds."""
        base_times = {
            "vector_search": 100,
            "mcp_federation": 500,
            "agno_orchestration": 1000,
            "llamaindex": 300
        }
        
        primary_time = base_times.get(primary_engine, 500)
        
        if not secondary_engines:
            return primary_time
        
        secondary_time = max(base_times.get(engine, 500) for engine in secondary_engines)
        
        if parallel:
            # Parallel execution - max of primary and secondary
            return max(primary_time, secondary_time) + 100  # Add coordination overhead
        else:
            # Sequential execution
            return primary_time + secondary_time
    
    def _generate_reasoning(self, query_type: QueryType, primary_engine: str, secondary_engines: List[str], confidence: float) -> str:
        """Generate human-readable reasoning for the routing decision."""
        reasoning_parts = [
            f"Classified as {query_type.value} with {confidence:.1%} confidence",
            f"Primary engine: {primary_engine}"
        ]
        
        if secondary_engines:
            reasoning_parts.append(f"Secondary engines: {', '.join(secondary_engines)}")
        
        engine_info = self.engine_capabilities.get(primary_engine, {})
        if engine_info.get("strengths"):
            reasoning_parts.append(f"Best for: {', '.join(engine_info['strengths'])}")
        
        return ". ".join(reasoning_parts)

class HybridRAGRouter:
    """
    Intelligent router for hybrid RAG architecture.
    Routes queries optimally between vector search, MCP federation, and Agno orchestration.
    """
    
    def __init__(self):
        """Initialize hybrid RAG router."""
        self.classifier = MLQueryClassifier()
        self.initialized = False
        
        # Performance tracking
        self.metrics = {
            "total_queries": 0,
            "routing_decisions": {},
            "engine_performance": {},
            "avg_routing_time_ms": 0.0,
            "success_rate": 0.0
        }
        
        # Adaptive learning
        self.performance_history = {}
        self.learning_enabled = True
    
    async def initialize(self):
        """Initialize the hybrid RAG router."""
        if self.initialized:
            return
        
        try:
            # Initialize all engines
            await enhanced_agno_integration.initialize()
            await mcp_federation.initialize()
            await hybrid_rag_manager.initialize()
            await llamaindex_integration.initialize()
            
            self.initialized = True
            logger.info("Hybrid RAG Router initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hybrid RAG Router: {e}")
            self.initialized = False
            raise
    
    async def route_query(
        self,
        query: str,
        context: Dict[str, Any] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Route query to optimal processing engines.
        
        Args:
            query: The query string
            context: Additional context for routing
            stream: Whether to stream results
            
        Returns:
            Processed results from optimal engines
        """
        if not self.initialized:
            await self.initialize()
        
        start_time = time.perf_counter()
        context = context or {}
        
        try:
            # Make routing decision
            routing_start = time.perf_counter()
            decision = self.classifier.classify_query(query, context)
            routing_time = (time.perf_counter() - routing_start) * 1000
            
            logger.info(f"Routing decision: {decision.reasoning} (took {routing_time:.2f}ms)")
            
            # Update routing metrics
            self._update_routing_metrics(decision, routing_time)
            
            # Execute query based on routing decision
            if stream:
                return self._stream_hybrid_results(query, context, decision)
            else:
                return await self._execute_hybrid_query(query, context, decision)
                
        except Exception as e:
            logger.error(f"Query routing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "routing_time_ms": (time.perf_counter() - start_time) * 1000
            }
    
    async def _execute_hybrid_query(
        self,
        query: str,
        context: Dict[str, Any],
        decision: RoutingDecision
    ) -> Dict[str, Any]:
        """Execute hybrid query based on routing decision."""
        start_time = time.perf_counter()
        
        # Execute primary engine
        primary_result = await self._execute_engine_query(decision.primary_engine, query, context)
        
        # Execute secondary engines if needed
        secondary_results = []
        if decision.secondary_engines:
            if decision.parallel_execution:
                # Parallel execution
                tasks = [
                    self._execute_engine_query(engine, query, context)
                    for engine in decision.secondary_engines
                ]
                secondary_results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Sequential execution
                for engine in decision.secondary_engines:
                    result = await self._execute_engine_query(engine, query, context)
                    secondary_results.append(result)
        
        # Combine results
        combined_result = self._combine_hybrid_results(
            primary_result, secondary_results, decision
        )
        
        # Add routing metadata
        total_time = (time.perf_counter() - start_time) * 1000
        combined_result["routing_metadata"] = {
            "decision": {
                "query_type": decision.query_type.value,
                "primary_engine": decision.primary_engine,
                "secondary_engines": decision.secondary_engines,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "parallel_execution": decision.parallel_execution
            },
            "performance": {
                "total_execution_time_ms": total_time,
                "estimated_time_ms": decision.estimated_time_ms,
                "performance_ratio": decision.estimated_time_ms / total_time if total_time > 0 else 0
            }
        }
        
        # Update performance metrics
        self._update_performance_metrics(decision, combined_result, total_time)
        
        return combined_result
    
    async def _execute_engine_query(self, engine: str, query: str, context: Dict[str, Any]) -> ProcessingResult:
        """Execute query on a specific engine."""
        start_time = time.perf_counter()
        
        try:
            if engine == "vector_search":
                result = await hybrid_rag_manager.search(query, context)
                confidence = 0.8  # High confidence for vector search
                
            elif engine == "mcp_federation":
                result = await mcp_federation.federated_query(query, context)
                confidence = result.get("performance", {}).get("successful_servers", 0) / max(1, result.get("performance", {}).get("total_servers_queried", 1))
                
            elif engine == "agno_orchestration":
                result = await enhanced_agno_integration.process_ultra_fast_request(query, "general_assistant", False)
                confidence = 0.9  # High confidence for Agno
                
            elif engine == "llamaindex":
                result = await llamaindex_integration.process_query(query, context)
                confidence = 0.85  # High confidence for LlamaIndex
                
            else:
                raise ValueError(f"Unknown engine: {engine}")
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            return ProcessingResult(
                success=True,
                data=result,
                engine=engine,
                execution_time_ms=execution_time,
                confidence=confidence,
                metadata={"query": query, "context": context}
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Engine {engine} query failed: {e}")
            
            return ProcessingResult(
                success=False,
                data=None,
                engine=engine,
                execution_time_ms=execution_time,
                confidence=0.0,
                metadata={"query": query, "context": context},
                error=str(e)
            )
    
    def _combine_hybrid_results(
        self,
        primary_result: ProcessingResult,
        secondary_results: List[ProcessingResult],
        decision: RoutingDecision
    ) -> Dict[str, Any]:
        """Combine results from multiple engines."""
        # Start with primary result
        if not primary_result.success:
            # Primary failed, try to use best secondary result
            successful_secondary = [r for r in secondary_results if isinstance(r, ProcessingResult) and r.success]
            if successful_secondary:
                best_secondary = max(successful_secondary, key=lambda r: r.confidence)
                return {
                    "success": True,
                    "data": best_secondary.data,
                    "primary_engine": best_secondary.engine,
                    "fallback_used": True,
                    "confidence": best_secondary.confidence,
                    "execution_time_ms": best_secondary.execution_time_ms
                }
            else:
                return {
                    "success": False,
                    "error": f"Primary engine {decision.primary_engine} failed: {primary_result.error}",
                    "secondary_errors": [
                        r.error for r in secondary_results 
                        if isinstance(r, ProcessingResult) and not r.success
                    ]
                }
        
        # Primary succeeded, enhance with secondary results
        combined_data = {
            "primary_result": primary_result.data,
            "primary_engine": primary_result.engine,
            "primary_confidence": primary_result.confidence
        }
        
        # Add successful secondary results
        successful_secondary = [r for r in secondary_results if isinstance(r, ProcessingResult) and r.success]
        if successful_secondary:
            combined_data["secondary_results"] = {}
            for result in successful_secondary:
                combined_data["secondary_results"][result.engine] = {
                    "data": result.data,
                    "confidence": result.confidence,
                    "execution_time_ms": result.execution_time_ms
                }
        
        # Calculate overall confidence
        all_confidences = [primary_result.confidence] + [r.confidence for r in successful_secondary]
        overall_confidence = statistics.mean(all_confidences) if all_confidences else primary_result.confidence
        
        return {
            "success": True,
            "data": combined_data,
            "confidence": overall_confidence,
            "engines_used": [primary_result.engine] + [r.engine for r in successful_secondary],
            "execution_summary": {
                "primary_time_ms": primary_result.execution_time_ms,
                "secondary_times_ms": {r.engine: r.execution_time_ms for r in successful_secondary}
            }
        }
    
    async def _stream_hybrid_results(
        self,
        query: str,
        context: Dict[str, Any],
        decision: RoutingDecision
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream hybrid results as they become available."""
        start_time = time.perf_counter()
        
        # Initial routing information
        yield {
            "type": "routing_decision",
            "decision": {
                "query_type": decision.query_type.value,
                "primary_engine": decision.primary_engine,
                "secondary_engines": decision.secondary_engines,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning
            },
            "timestamp": time.time()
        }
        
        # Execute primary engine
        yield {"type": "engine_start", "engine": decision.primary_engine}
        primary_result = await self._execute_engine_query(decision.primary_engine, query, context)
        yield {
            "type": "engine_result",
            "engine": decision.primary_engine,
            "success": primary_result.success,
            "data": primary_result.data,
            "confidence": primary_result.confidence,
            "execution_time_ms": primary_result.execution_time_ms,
            "error": primary_result.error
        }
        
        # Execute secondary engines
        secondary_results = []
        if decision.secondary_engines:
            for engine in decision.secondary_engines:
                yield {"type": "engine_start", "engine": engine}
                result = await self._execute_engine_query(engine, query, context)
                secondary_results.append(result)
                yield {
                    "type": "engine_result",
                    "engine": engine,
                    "success": result.success,
                    "data": result.data,
                    "confidence": result.confidence,
                    "execution_time_ms": result.execution_time_ms,
                    "error": result.error
                }
        
        # Final combined result
        combined_result = self._combine_hybrid_results(primary_result, secondary_results, decision)
        total_time = (time.perf_counter() - start_time) * 1000
        
        yield {
            "type": "hybrid_complete",
            "combined_result": combined_result,
            "total_execution_time_ms": total_time,
            "performance_ratio": decision.estimated_time_ms / total_time if total_time > 0 else 0
        }
    
    def _update_routing_metrics(self, decision: RoutingDecision, routing_time_ms: float):
        """Update routing decision metrics."""
        self.metrics["total_queries"] += 1
        
        # Update routing time
        total_queries = self.metrics["total_queries"]
        current_avg = self.metrics["avg_routing_time_ms"]
        self.metrics["avg_routing_time_ms"] = (
            (current_avg * (total_queries - 1) + routing_time_ms) / total_queries
        )
        
        # Update routing decisions
        query_type = decision.query_type.value
        if query_type not in self.metrics["routing_decisions"]:
            self.metrics["routing_decisions"][query_type] = 0
        self.metrics["routing_decisions"][query_type] += 1
    
    def _update_performance_metrics(self, decision: RoutingDecision, result: Dict[str, Any], execution_time_ms: float):
        """Update performance metrics for adaptive learning."""
        # Update success rate
        success = result.get("success", False)
        total_queries = self.metrics["total_queries"]
        current_success_rate = self.metrics["success_rate"]
        self.metrics["success_rate"] = (
            (current_success_rate * (total_queries - 1) + (1 if success else 0)) / total_queries
        )
        
        # Update engine performance
        primary_engine = decision.primary_engine
        if primary_engine not in self.metrics["engine_performance"]:
            self.metrics["engine_performance"][primary_engine] = {
                "total_queries": 0,
                "successful_queries": 0,
                "avg_execution_time_ms": 0.0
            }
        
        engine_metrics = self.metrics["engine_performance"][primary_engine]
        engine_metrics["total_queries"] += 1
        if success:
            engine_metrics["successful_queries"] += 1
        
        # Update average execution time
        current_avg = engine_metrics["avg_execution_time_ms"]
        total_engine_queries = engine_metrics["total_queries"]
        engine_metrics["avg_execution_time_ms"] = (
            (current_avg * (total_engine_queries - 1) + execution_time_ms) / total_engine_queries
        )
        
        # Store performance history for learning
        if self.learning_enabled:
            query_signature = f"{decision.query_type.value}_{primary_engine}"
            if query_signature not in self.performance_history:
                self.performance_history[query_signature] = []
            
            self.performance_history[query_signature].append({
                "success": success,
                "execution_time_ms": execution_time_ms,
                "confidence": result.get("confidence", 0.0),
                "timestamp": time.time()
            })
            
            # Keep only recent history (last 100 entries)
            if len(self.performance_history[query_signature]) > 100:
                self.performance_history[query_signature] = self.performance_history[query_signature][-100:]
    
    def get_router_stats(self) -> Dict[str, Any]:
        """Get comprehensive router statistics."""
        return {
            "routing_metrics": self.metrics,
            "performance_history_size": {
                signature: len(history) 
                for signature, history in self.performance_history.items()
            },
            "engine_success_rates": {
                engine: metrics["successful_queries"] / metrics["total_queries"]
                if metrics["total_queries"] > 0 else 0.0
                for engine, metrics in self.metrics["engine_performance"].items()
            },
            "adaptive_learning": {
                "enabled": self.learning_enabled,
                "total_patterns": len(self.performance_history)
            }
        }
    
    async def optimize_routing(self):
        """Optimize routing decisions based on performance history."""
        if not self.learning_enabled or not self.performance_history:
            return
        
        logger.info("Optimizing routing decisions based on performance history")
        
        # Analyze performance patterns
        for signature, history in self.performance_history.items():
            if len(history) < 10:  # Need sufficient data
                continue
            
            recent_history = history[-20:]  # Last 20 queries
            success_rate = sum(1 for h in recent_history if h["success"]) / len(recent_history)
            avg_time = statistics.mean(h["execution_time_ms"] for h in recent_history)
            
            # Log insights
            logger.info(f"Pattern {signature}: {success_rate:.1%} success rate, {avg_time:.0f}ms avg time")
            
            # TODO: Implement adaptive routing adjustments based on patterns
    
    async def close(self):
        """Close the hybrid RAG router."""
        self.initialized = False
        logger.info("Hybrid RAG Router closed")

# Global instance
hybrid_rag_router = HybridRAGRouter()

