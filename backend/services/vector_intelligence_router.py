"""
Sophia AI Vector Intelligence Router
====================================
Intelligently routes vector searches to the optimal database based on query characteristics.
"""

import asyncio
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json

from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class VectorIntelligenceRouter:
    """Intelligent routing between existing vector systems"""
    
    def __init__(self):
        """Initialize the vector intelligence router"""
        logger.info("🚀 Initializing Vector Intelligence Router...")
        
        # Initialize existing services
        self._init_vector_services()
        
        logger.info("✅ Vector Intelligence Router initialized")
    
    def _init_vector_services(self):
        """Initialize vector database services"""
        try:
            # Snowflake Cortex (primary system)
            self.snowflake_cortex = SnowflakeCortexService()
            logger.info("✅ Snowflake Cortex initialized")
        except Exception as e:
            logger.warning(f"⚠️ Snowflake Cortex initialization failed: {e}")
            self.snowflake_cortex = None
        
        try:
            # AI Memory service (includes Pinecone)
            self.ai_memory = EnhancedAiMemoryMCPServer()
            logger.info("✅ AI Memory service initialized")
        except Exception as e:
            logger.warning(f"⚠️ AI Memory initialization failed: {e}")
            self.ai_memory = None
        
        # Pinecone client would be initialized here if needed directly
        self.pinecone_client = None  # Placeholder
    
    async def intelligent_search(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route to optimal vector database based on query characteristics
        
        Args:
            query: Search query
            context: Query context including requirements
            
        Returns:
            Combined search results from optimal sources
        """
        logger.info(f"🔍 Intelligent vector search for: {query[:50]}...")
        
        # Analyze query to determine optimal routing
        query_analysis = await self.analyze_query_characteristics(query, context)
        
        # Prepare search tasks based on analysis
        search_tasks = []
        
        # Always include Snowflake Cortex (primary system)
        if self.snowflake_cortex:
            search_tasks.append(
                self.search_snowflake_cortex(query, context, query_analysis)
            )
        
        # Add AI Memory for context and real-time needs
        if self.ai_memory and (query_analysis.get("requires_context") or query_analysis.get("requires_realtime")):
            search_tasks.append(
                self.search_ai_memory(query, context, query_analysis)
            )
        
        # Execute searches in parallel
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        # Intelligently combine results
        combined_results = await self.fuse_search_results(valid_results, query, context)
        
        return combined_results
    
    async def analyze_query_characteristics(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze query to determine optimal routing strategy"""
        analysis = {
            "requires_realtime": False,
            "requires_context": False,
            "requires_complex_filtering": False,
            "query_type": "general",
            "estimated_result_size": "medium",
            "priority": context.get("priority", "balanced")
        }
        
        # Check for real-time requirements
        realtime_keywords = ["latest", "current", "now", "today", "recent", "real-time"]
        if any(keyword in query.lower() for keyword in realtime_keywords):
            analysis["requires_realtime"] = True
        
        # Check for context requirements
        context_keywords = ["related", "similar", "context", "history", "previous"]
        if any(keyword in query.lower() for keyword in context_keywords):
            analysis["requires_context"] = True
        
        # Check for complex filtering needs
        filter_keywords = ["filter", "where", "between", "range", "specific"]
        if any(keyword in query.lower() for keyword in filter_keywords):
            analysis["requires_complex_filtering"] = True
        
        # Determine query type
        if any(word in query.lower() for word in ["revenue", "sales", "deals"]):
            analysis["query_type"] = "business_metrics"
        elif any(word in query.lower() for word in ["customer", "contact", "company"]):
            analysis["query_type"] = "customer_data"
        elif any(word in query.lower() for word in ["call", "meeting", "conversation"]):
            analysis["query_type"] = "communication_data"
        
        logger.info(f"📊 Query analysis: {analysis}")
        
        return analysis
    
    async def search_snowflake_cortex(
        self, 
        query: str, 
        context: Dict[str, Any], 
        query_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Search using Snowflake Cortex"""
        if not self.snowflake_cortex:
            return {"source": "snowflake_cortex", "results": [], "error": "Service unavailable"}
        
        try:
            # Determine the best table based on query type
            table_mapping = {
                "business_metrics": "ENRICHED_HUBSPOT_DEALS",
                "customer_data": "ENRICHED_HUBSPOT_CONTACTS",
                "communication_data": "ENRICHED_GONG_CALLS",
                "general": "UNIFIED_KNOWLEDGE_BASE"
            }
            
            table_name = table_mapping.get(
                query_analysis.get("query_type", "general"),
                "UNIFIED_KNOWLEDGE_BASE"
            )
            
            # Execute vector search
            results = await self.snowflake_cortex.search_business_context(
                query=query,
                table_name=table_name,
                limit=context.get("limit", 10)
            )
            
            return {
                "source": "snowflake_cortex",
                "results": results,
                "table": table_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in Snowflake Cortex search: {e}")
            return {"source": "snowflake_cortex", "results": [], "error": str(e)}
    
    async def search_ai_memory(
        self, 
        query: str, 
        context: Dict[str, Any], 
        query_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Search using AI Memory service (includes Pinecone)"""
        if not self.ai_memory:
            return {"source": "ai_memory", "results": [], "error": "Service unavailable"}
        
        try:
            # Determine category based on query type
            category_mapping = {
                "business_metrics": "business_intelligence",
                "customer_data": "customer_insights",
                "communication_data": "conversation_analysis",
                "general": "general"
            }
            
            category = category_mapping.get(
                query_analysis.get("query_type", "general"),
                "general"
            )
            
            # Search memories
            memories = await self.ai_memory.search_memories(
                query=query,
                category=category,
                limit=context.get("limit", 10)
            )
            
            return {
                "source": "ai_memory",
                "results": memories,
                "category": category,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in AI Memory search: {e}")
            return {"source": "ai_memory", "results": [], "error": str(e)}
    
    async def search_pinecone(
        self, 
        query: str, 
        context: Dict[str, Any], 
        query_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Direct Pinecone search for real-time needs"""
        # Placeholder for direct Pinecone integration
        # Currently handled through AI Memory service
        return {"source": "pinecone", "results": [], "note": "Handled via AI Memory"}
    
    async def fuse_search_results(
        self, 
        results: List[Dict[str, Any]], 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Intelligently combine results from multiple sources"""
        if not results:
            return {
                "combined_results": [],
                "sources": [],
                "total_results": 0,
                "fusion_strategy": "none"
            }
        
        # Collect all results with source tracking
        all_results = []
        sources_used = []
        
        for result_set in results:
            source = result_set.get("source", "unknown")
            sources_used.append(source)
            
            for item in result_set.get("results", []):
                all_results.append({
                    **item,
                    "_source": source,
                    "_relevance": self._calculate_relevance(item, query)
                })
        
        # Sort by relevance
        all_results.sort(key=lambda x: x.get("_relevance", 0), reverse=True)
        
        # Apply fusion strategy
        fusion_strategy = self._determine_fusion_strategy(context, len(all_results))
        
        if fusion_strategy == "interleave":
            # Interleave results from different sources
            fused_results = self._interleave_results(all_results, sources_used)
        elif fusion_strategy == "relevance":
            # Pure relevance-based ordering
            fused_results = all_results
        else:
            # Default: relevance with source diversity
            fused_results = self._diverse_fusion(all_results, sources_used)
        
        # Limit results
        max_results = context.get("limit", 20)
        fused_results = fused_results[:max_results]
        
        return {
            "combined_results": fused_results,
            "sources": sources_used,
            "total_results": len(all_results),
            "fusion_strategy": fusion_strategy,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_relevance(self, item: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for a result item"""
        # Simple relevance calculation
        score = 0.5  # Base score
        
        # Check for query terms in content
        query_terms = query.lower().split()
        content = str(item.get("content", "")).lower()
        
        for term in query_terms:
            if term in content:
                score += 0.1
        
        # Boost for similarity score if present
        if "similarity_score" in item:
            score += item["similarity_score"] * 0.5
        
        # Boost for recent items
        if "created_at" in item:
            # Placeholder for recency boost
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_fusion_strategy(self, context: Dict[str, Any], result_count: int) -> str:
        """Determine the best fusion strategy"""
        if context.get("fusion_strategy"):
            return context["fusion_strategy"]
        
        if result_count < 10:
            return "relevance"
        elif result_count < 50:
            return "diverse"
        else:
            return "interleave"
    
    def _interleave_results(
        self, 
        results: List[Dict[str, Any]], 
        sources: List[str]
    ) -> List[Dict[str, Any]]:
        """Interleave results from different sources"""
        # Group by source
        by_source = {}
        for result in results:
            source = result.get("_source", "unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)
        
        # Interleave
        interleaved = []
        max_len = max(len(items) for items in by_source.values())
        
        for i in range(max_len):
            for source in sources:
                if source in by_source and i < len(by_source[source]):
                    interleaved.append(by_source[source][i])
        
        return interleaved
    
    def _diverse_fusion(
        self, 
        results: List[Dict[str, Any]], 
        sources: List[str]
    ) -> List[Dict[str, Any]]:
        """Fusion with source diversity"""
        # Ensure diversity by limiting consecutive results from same source
        diverse_results = []
        last_source = None
        same_source_count = 0
        max_consecutive = 3
        
        for result in results:
            source = result.get("_source", "unknown")
            
            if source == last_source:
                same_source_count += 1
            else:
                same_source_count = 0
                last_source = source
            
            if same_source_count < max_consecutive:
                diverse_results.append(result)
        
        return diverse_results 
