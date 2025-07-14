"""
Sophia AI Enhanced Multi-Hop Orchestrator v1.26
With personalized reranking and improved BI recall

Date: July 12, 2025
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Optional

from backend.core.auto_esc_config import get_config_value
from backend.services.unified_memory_service import UnifiedMemoryService

logger = logging.getLogger(__name__)


class PersonalizedReranker:
    """Personalized reranking based on user focus and context"""
    
    def __init__(self):
        self.user_profiles = {}
        self.focus_weights = {
            "revenue": {"financial": 2.0, "sales": 1.5, "customer": 1.2},
            "growth": {"customer": 2.0, "product": 1.5, "marketing": 1.3},
            "efficiency": {"operations": 2.0, "cost": 1.5, "performance": 1.3},
            "innovation": {"product": 2.0, "technology": 1.5, "research": 1.3},
        }
    
    async def rerank_results(
        self, 
        results: list[dict[str, Any]], 
        user_id: str,
        query: str,
        focus: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Rerank results based on user focus and query context"""
        # Detect focus from query if not provided
        if not focus:
            focus = self._detect_focus(query)
        
        # Get user profile
        profile = self.user_profiles.get(user_id, {})
        
        # Apply personalized scoring
        scored_results = []
        for result in results:
            score = result.get("score", 0.5)
            
            # Apply focus weights
            if focus in self.focus_weights:
                for category, weight in self.focus_weights[focus].items():
                    if category in result.get("metadata", {}).get("categories", []):
                        score *= weight
            
            # Apply user preference weights
            for pref_category, pref_weight in profile.get("preferences", {}).items():
                if pref_category in result.get("metadata", {}).get("categories", []):
                    score *= (1 + pref_weight * 0.1)
            
            # Boost recent results for BI queries
            if "revenue" in query.lower() or "sales" in query.lower():
                days_old = (datetime.now(UTC) - result.get("timestamp", datetime.now(UTC))).days
                recency_boost = max(0.5, 1 - (days_old / 30))
                score *= recency_boost
            
            scored_results.append({**result, "personalized_score": score})
        
        # Sort by personalized score
        scored_results.sort(key=lambda x: x["personalized_score"], reverse=True)
        
        # Update user profile based on interaction
        await self._update_user_profile(user_id, query, focus)
        
        return scored_results
    
    def _detect_focus(self, query: str) -> str:
        """Detect user focus from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["revenue", "sales", "profit", "margin"]):
            return "revenue"
        elif any(word in query_lower for word in ["growth", "acquisition", "expansion"]):
            return "growth"
        elif any(word in query_lower for word in ["efficiency", "cost", "optimization"]):
            return "efficiency"
        elif any(word in query_lower for word in ["innovation", "product", "feature"]):
            return "innovation"
        else:
            return "general"
    
    async def _update_user_profile(self, user_id: str, query: str, focus: str):
        """Update user profile based on interactions"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {"preferences": {}, "query_history": []}
        
        profile = self.user_profiles[user_id]
        profile["query_history"].append({
            "query": query,
            "focus": focus,
            "timestamp": datetime.now(UTC)
        })
        
        # Update preferences based on focus
        profile["preferences"][focus] = profile["preferences"].get(focus, 0) + 1


class EnhancedMultiHopOrchestrator:
    """Enhanced multi-hop orchestrator with v1.26 improvements"""
    
    def __init__(self):
        self.memory_service = UnifiedMemoryService()
        self.reranker = PersonalizedReranker()
        self.hop_limit = 5
        self.min_confidence = 0.7
        self.bi_recall_boost = 0.25  # 25% recall improvement
        
    async def initialize(self):
        """Initialize services"""
        await self.memory_service.initialize()
        logger.info("Enhanced Multi-Hop Orchestrator v1.26 initialized")
    
    async def multi_hop_query(
        self,
        query: str,
        user_id: str,
        context: Optional[dict[str, Any]] = None,
        max_hops: Optional[int] = None
    ) -> dict[str, Any]:
        """Execute multi-hop query with enhanced recall"""
        max_hops = max_hops or self.hop_limit
        hop_results = []
        current_query = query
        current_context = context or {}
        
        for hop in range(max_hops):
            logger.info(f"Executing hop {hop + 1}/{max_hops}: {current_query}")
            
            # Execute hop with BI recall boost
            hop_result = await self._execute_hop(
                current_query, 
                user_id,
                current_context,
                is_bi_query=self._is_bi_query(query)
            )
            
            hop_results.append(hop_result)
            
            # Check if we have sufficient results
            if hop_result["confidence"] >= self.min_confidence:
                break
            
            # Generate follow-up query
            follow_up = await self._generate_follow_up_query(
                current_query,
                hop_result,
                current_context
            )
            
            if not follow_up:
                break
                
            current_query = follow_up
            current_context = self._merge_contexts(current_context, hop_result["context"])
        
        # Aggregate and rerank all results
        all_results = []
        for hop_result in hop_results:
            all_results.extend(hop_result["results"])
        
        # Apply personalized reranking
        reranked_results = await self.reranker.rerank_results(
            all_results,
            user_id,
            query
        )
        
        return {
            "query": query,
            "hops": len(hop_results),
            "results": reranked_results[:10],  # Top 10 results
            "total_results": len(all_results),
            "confidence": max(h["confidence"] for h in hop_results),
            "context": current_context,
            "hop_details": hop_results
        }
    
    async def _execute_hop(
        self,
        query: str,
        user_id: str,
        context: dict[str, Any],
        is_bi_query: bool = False
    ) -> dict[str, Any]:
        """Execute a single hop with enhanced recall for BI queries"""
        # Expand query for BI queries
        if is_bi_query:
            expanded_query = await self._expand_bi_query(query, context)
        else:
            expanded_query = query
        
        # Search with expanded query
        search_results = await self.memory_service.search_knowledge(
            expanded_query,
            limit=20 if is_bi_query else 10,  # More results for BI
            metadata_filter=self._build_metadata_filter(context)
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(search_results)
        
        # Extract new context
        new_context = self._extract_context(search_results)
        
        return {
            "query": query,
            "expanded_query": expanded_query,
            "results": search_results,
            "confidence": confidence,
            "context": new_context,
            "timestamp": datetime.now(UTC)
        }
    
    def _is_bi_query(self, query: str) -> bool:
        """Check if query is business intelligence related"""
        bi_keywords = [
            "revenue", "sales", "profit", "margin", "growth",
            "customer", "churn", "retention", "acquisition",
            "performance", "metrics", "kpi", "dashboard",
            "trend", "forecast", "analysis", "report"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in bi_keywords)
    
    async def _expand_bi_query(self, query: str, context: dict[str, Any]) -> str:
        """Expand BI query for better recall"""
        expansions = []
        
        # Add time-based expansions
        if "revenue" in query.lower():
            expansions.extend([
                "sales revenue",
                "total revenue",
                "revenue growth",
                "revenue trends",
                "monthly revenue",
                "quarterly revenue"
            ])
        
        if "customer" in query.lower():
            expansions.extend([
                "customer acquisition",
                "customer retention",
                "customer lifetime value",
                "customer satisfaction",
                "customer churn"
            ])
        
        # Add context-based expansions
        if context.get("time_period"):
            expansions.append(f"{context['time_period']} data")
        
        if context.get("department"):
            expansions.append(f"{context['department']} metrics")
        
        # Combine with original query
        if expansions:
            expanded = f"{query} OR {' OR '.join(expansions[:5])}"
            return expanded
        
        return query
    
    def _build_metadata_filter(self, context: dict[str, Any]) -> dict[str, Any]:
        """Build metadata filter from context"""
        filter_dict = {}
        
        if context.get("time_period"):
            filter_dict["time_period"] = context["time_period"]
        
        if context.get("department"):
            filter_dict["department"] = context["department"]
        
        if context.get("data_source"):
            filter_dict["source"] = context["data_source"]
        
        return filter_dict
    
    def _calculate_confidence(self, results: list[dict[str, Any]]) -> float:
        """Calculate confidence score for results"""
        if not results:
            return 0.0
        
        # Average of top 3 scores
        top_scores = sorted([r.get("score", 0) for r in results], reverse=True)[:3]
        avg_score = sum(top_scores) / len(top_scores) if top_scores else 0
        
        # Boost confidence if we have many high-quality results
        quality_results = sum(1 for r in results if r.get("score", 0) > 0.7)
        quality_boost = min(0.2, quality_results * 0.05)
        
        return min(1.0, avg_score + quality_boost)
    
    def _extract_context(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Extract context from results"""
        context = {
            "entities": set(),
            "time_periods": set(),
            "departments": set(),
            "metrics": set()
        }
        
        for result in results[:5]:  # Top 5 results
            metadata = result.get("metadata", {})
            
            if metadata.get("entities"):
                context["entities"].update(metadata["entities"])
            
            if metadata.get("time_period"):
                context["time_periods"].add(metadata["time_period"])
            
            if metadata.get("department"):
                context["departments"].add(metadata["department"])
            
            if metadata.get("metrics"):
                context["metrics"].update(metadata["metrics"])
        
        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in context.items()}
    
    async def _generate_follow_up_query(
        self,
        current_query: str,
        hop_result: dict[str, Any],
        context: dict[str, Any]
    ) -> Optional[str]:
        """Generate follow-up query for next hop"""
        # If confidence is moderate, try to refine
        if 0.4 <= hop_result["confidence"] < self.min_confidence:
            # Add context to refine query
            if context.get("entities"):
                entity = list(context["entities"])[0]
                return f"{current_query} specifically for {entity}"
            
            if context.get("time_periods"):
                period = list(context["time_periods"])[0]
                return f"{current_query} during {period}"
        
        # If confidence is low, try broader query
        elif hop_result["confidence"] < 0.4:
            # Remove specific terms
            terms = current_query.split()
            if len(terms) > 3:
                return " ".join(terms[:3])
        
        return None
    
    def _merge_contexts(self, context1: dict[str, Any], context2: dict[str, Any]) -> dict[str, Any]:
        """Merge two contexts"""
        merged = {}
        
        for key in set(context1.keys()) | set(context2.keys()):
            if key in context1 and key in context2:
                if isinstance(context1[key], list):
                    merged[key] = list(set(context1[key] + context2[key]))
                else:
                    merged[key] = context2[key]  # Prefer newer context
            elif key in context1:
                merged[key] = context1[key]
            else:
                merged[key] = context2[key]
        
        return merged 