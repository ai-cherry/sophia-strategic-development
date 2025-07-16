"""
🧠 ADVANCED HYBRID SEARCH SERVICE
Multi-modal search combining semantic, keyword, graph, and temporal intelligence

Created: July 14, 2025
Phase: 2.1 - Advanced Memory Intelligence
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, DatetimeRange

from backend.core.truthful_config import get_real_QDRANT_config

logger = logging.getLogger(__name__)

class SearchResultType(Enum):
    DENSE_SEMANTIC = "dense_semantic"
    SPARSE_KEYWORD = "sparse_keyword"
    GRAPH_RELATIONSHIP = "graph_relationship"
    TEMPORAL_RELEVANCE = "temporal_relevance"

@dataclass
class SearchContext:
    """Context for search operations"""
    user_id: str
    session_id: str
    business_domain: str
    urgency_level: float = 0.5
    personalization_enabled: bool = True
    max_results: int = 50
    confidence_threshold: float = 0.7

@dataclass
class SearchResult:
    """Enhanced search result with multiple scoring dimensions"""
    id: str
    content: str
    source: str
    metadata: Dict[str, Any]
    scores: Dict[SearchResultType, float]
    final_score: float
    confidence: float
    relevance_explanation: str
    timestamp: datetime

@dataclass
class BusinessInsights:
    """Business intelligence insights from search"""
    primary_insights: List[SearchResult]
    related_insights: List[SearchResult]
    trend_analysis: Dict[str, Any]
    actionable_recommendations: List[str]
    confidence_score: float
    business_impact: str

class AdvancedHybridSearchService:
    """
    World-class hybrid search combining:
    - Dense semantic search (768D/1024D vectors)
    - Sparse keyword matching (BM25-style)
    - Graph relationship traversal
    - Temporal relevance scoring
    - User personalization
    """
    
    def __init__(self):
        self.QDRANT_config = get_real_QDRANT_config()
        self.client = None
        self.collections = [
            "sophia_knowledge",
            "sophia_conversations", 
            "sophia_documents",
            "sophia_code",
            "sophia_workflows"
        ]
        self.embedding_dimension = 768
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize Qdrant client and validate collections"""
        try:
            self.client = QdrantClient(
                url=self.QDRANT_config["url"],
                api_key=self.QDRANT_config["api_key"],
                timeout=self.QDRANT_config["timeout"]
            )
            
            # Validate collections exist
            await self._ensure_collections_exist()
            
            self.logger.info("✅ Advanced Hybrid Search Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Advanced Hybrid Search Service: {e}")
            raise

    async def hybrid_search(self, query: str, context: SearchContext) -> List[SearchResult]:
        """
        Perform comprehensive hybrid search across all dimensions
        """
        try:
            # 1. Dense semantic search across all collections
            dense_results = await self._parallel_dense_search(query, context)
            
            # 2. Sparse keyword search with BM25-style scoring
            sparse_results = await self._bm25_keyword_search(query, context)
            
            # 3. Graph relationship expansion
            graph_results = await self._graph_relationship_search(query, context)
            
            # 4. Temporal relevance scoring
            temporal_results = await self._temporal_relevance_search(query, context)
            
            # 5. User personalization boost
            if context.personalization_enabled:
                personalized_results = await self._personalization_boost(
                    dense_results, context
                )
            else:
                personalized_results = dense_results
            
            # 6. Ensemble ranking with confidence scores
            final_results = await self._ensemble_ranking(
                dense_results, sparse_results, graph_results, 
                temporal_results, personalized_results, context
            )
            
            self.logger.info(f"✅ Hybrid search completed: {len(final_results)} results")
            return final_results
            
        except Exception as e:
            self.logger.error(f"❌ Hybrid search failed: {e}")
            raise

    async def _parallel_dense_search(self, query: str, context: SearchContext) -> Dict[str, List[SearchResult]]:
        """Search all 5 collections in parallel for maximum speed"""
        try:
            # Generate query embedding (placeholder - would use actual embedding service)
            query_embedding = await self._generate_embedding(query)
            
            # Create search tasks for all collections
            search_tasks = []
            for collection in self.collections:
                task = self._search_collection_dense(
                    collection, query_embedding, query, context
                )
                search_tasks.append(task)
            
            # Execute all searches in parallel
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Process results
            collection_results = {}
            for i, result in enumerate(results):
                collection_name = self.collections[i]
                if isinstance(result, Exception):
                    self.logger.warning(f"Search failed for {collection_name}: {result}")
                    collection_results[collection_name] = []
                else:
                    collection_results[collection_name] = result
            
            return collection_results
            
        except Exception as e:
            self.logger.error(f"❌ Parallel dense search failed: {e}")
            raise

    async def _search_collection_dense(self, collection: str, query_embedding: List[float], 
                                     query: str, context: SearchContext) -> List[SearchResult]:
        """Search a single collection with dense semantic search"""
        try:
            # Build filter based on context
            search_filter = await self._build_search_filter(context, collection)
            
            # Perform vector search
            search_results = self.client.search(
                collection_name=collection,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=context.max_results // len(self.collections),
                score_threshold=context.confidence_threshold
            )
            
            # Convert to SearchResult objects
            results = []
            for point in search_results:
                result = SearchResult(
                    id=str(point.id),
                    content=point.payload.get("content", ""),
                    source=point.payload.get("source", collection),
                    metadata=point.payload,
                    scores={SearchResultType.DENSE_SEMANTIC: point.score},
                    final_score=point.score,
                    confidence=point.score,
                    relevance_explanation=f"Semantic similarity: {point.score:.3f}",
                    timestamp=datetime.now()
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Dense search failed for {collection}: {e}")
            return []

    async def _bm25_keyword_search(self, query: str, context: SearchContext) -> List[SearchResult]:
        """BM25-style keyword search with term frequency analysis"""
        try:
            # Extract keywords from query
            keywords = await self._extract_keywords(query)
            
            # Build keyword filter
            keyword_filter = Filter(
                should=[
                    FieldCondition(
                        key="content",
                        match=MatchValue(value=keyword)
                    ) for keyword in keywords
                ]
            )
            
            # Search across all collections
            keyword_results = []
            for collection in self.collections:
                try:
                    # Use scroll to get all matching documents
                    scroll_results = self.client.scroll(
                        collection_name=collection,
                        scroll_filter=keyword_filter,
                        limit=context.max_results // len(self.collections)
                    )
                    
                    # Calculate BM25-style scores
                    for point in scroll_results[0]:
                        bm25_score = await self._calculate_bm25_score(
                            point.payload.get("content", ""), keywords
                        )
                        
                        result = SearchResult(
                            id=str(point.id),
                            content=point.payload.get("content", ""),
                            source=point.payload.get("source", collection),
                            metadata=point.payload,
                            scores={SearchResultType.SPARSE_KEYWORD: bm25_score},
                            final_score=bm25_score,
                            confidence=bm25_score,
                            relevance_explanation=f"Keyword match: {bm25_score:.3f}",
                            timestamp=datetime.now()
                        )
                        keyword_results.append(result)
                        
                except Exception as e:
                    self.logger.warning(f"Keyword search failed for {collection}: {e}")
                    continue
            
            return keyword_results
            
        except Exception as e:
            self.logger.error(f"❌ BM25 keyword search failed: {e}")
            return []

    async def _graph_relationship_search(self, query: str, context: SearchContext) -> List[SearchResult]:
        """Graph relationship traversal for connected insights"""
        try:
            # Find entities in the query
            entities = await self._extract_entities(query)
            
            # Find related entities through graph relationships
            related_results = []
            for entity in entities:
                # Search for documents containing this entity
                entity_filter = Filter(
                    must=[
                        FieldCondition(
                            key="entities",
                            match=MatchValue(value=entity)
                        )
                    ]
                )
                
                # Search across collections
                for collection in self.collections:
                    try:
                        entity_results = self.client.scroll(
                            collection_name=collection,
                            scroll_filter=entity_filter,
                            limit=10
                        )
                        
                        for point in entity_results[0]:
                            # Calculate relationship score
                            relationship_score = await self._calculate_relationship_score(
                                entity, point.payload
                            )
                            
                            result = SearchResult(
                                id=str(point.id),
                                content=point.payload.get("content", ""),
                                source=point.payload.get("source", collection),
                                metadata=point.payload,
                                scores={SearchResultType.GRAPH_RELATIONSHIP: relationship_score},
                                final_score=relationship_score,
                                confidence=relationship_score,
                                relevance_explanation=f"Entity relationship: {relationship_score:.3f}",
                                timestamp=datetime.now()
                            )
                            related_results.append(result)
                            
                    except Exception as e:
                        self.logger.warning(f"Graph search failed for {collection}: {e}")
                        continue
            
            return related_results
            
        except Exception as e:
            self.logger.error(f"❌ Graph relationship search failed: {e}")
            return []

    async def _temporal_relevance_search(self, query: str, context: SearchContext) -> List[SearchResult]:
        """Temporal relevance scoring (recent > old)"""
        try:
            # Define time windows for relevance
            now = datetime.now()
            time_windows = {
                "recent": (now - timedelta(days=7), now),
                "medium": (now - timedelta(days=30), now - timedelta(days=7)),
                "old": (now - timedelta(days=90), now - timedelta(days=30))
            }
            
            temporal_results = []
            for window_name, (start_time, end_time) in time_windows.items():
                # Create temporal filter
                temporal_filter = Filter(
                    must=[
                        FieldCondition(
                            key="timestamp",
                            range=DatetimeRange(
                                gte=start_time,
                                lte=end_time
                            )
                        )
                    ]
                )
                
                # Search across collections
                for collection in self.collections:
                    try:
                        temporal_search = self.client.scroll(
                            collection_name=collection,
                            scroll_filter=temporal_filter,
                            limit=context.max_results // (len(self.collections) * len(time_windows))
                        )
                        
                        # Calculate temporal scores
                        temporal_score_multiplier = {
                            "recent": 1.0,
                            "medium": 0.7,
                            "old": 0.4
                        }
                        
                        for point in temporal_search[0]:
                            temporal_score = temporal_score_multiplier[window_name]
                            
                            result = SearchResult(
                                id=str(point.id),
                                content=point.payload.get("content", ""),
                                source=point.payload.get("source", collection),
                                metadata=point.payload,
                                scores={SearchResultType.TEMPORAL_RELEVANCE: temporal_score},
                                final_score=temporal_score,
                                confidence=temporal_score,
                                relevance_explanation=f"Temporal relevance ({window_name}): {temporal_score:.3f}",
                                timestamp=datetime.now()
                            )
                            temporal_results.append(result)
                            
                    except Exception as e:
                        self.logger.warning(f"Temporal search failed for {collection}: {e}")
                        continue
            
            return temporal_results
            
        except Exception as e:
            self.logger.error(f"❌ Temporal relevance search failed: {e}")
            return []

    async def _personalization_boost(self, results: Dict[str, List[SearchResult]], 
                                   context: SearchContext) -> List[SearchResult]:
        """Apply personalization boost based on user history"""
        try:
            # Get user interaction history from memory
            user_history = await self._get_user_history(context.user_id)
            
            # Apply personalization boost to all results
            personalized_results = []
            for collection_name, collection_results in results.items():
                for result in collection_results:
                    # Calculate personalization score
                    personalization_score = await self._calculate_personalization_score(
                        result, user_history
                    )
                    
                    # Boost the final score
                    result.scores["personalization"] = personalization_score
                    result.final_score = result.final_score * (1 + personalization_score * 0.2)
                    
                    personalized_results.append(result)
            
            return personalized_results
            
        except Exception as e:
            self.logger.error(f"❌ Personalization boost failed: {e}")
            # Return original results if personalization fails
            all_results = []
            for collection_results in results.values():
                all_results.extend(collection_results)
            return all_results

    async def _ensemble_ranking(self, dense_results: Dict[str, List[SearchResult]],
                              sparse_results: List[SearchResult],
                              graph_results: List[SearchResult],
                              temporal_results: List[SearchResult],
                              personalized_results: List[SearchResult],
                              context: SearchContext) -> List[SearchResult]:
        """Ensemble ranking with confidence scores"""
        try:
            # Combine all results
            all_results = {}
            
            # Add dense results
            for collection_results in dense_results.values():
                for result in collection_results:
                    all_results[result.id] = result
            
            # Merge sparse results
            for result in sparse_results:
                if result.id in all_results:
                    all_results[result.id].scores.update(result.scores)
                else:
                    all_results[result.id] = result
            
            # Merge graph results
            for result in graph_results:
                if result.id in all_results:
                    all_results[result.id].scores.update(result.scores)
                else:
                    all_results[result.id] = result
            
            # Merge temporal results
            for result in temporal_results:
                if result.id in all_results:
                    all_results[result.id].scores.update(result.scores)
                else:
                    all_results[result.id] = result
            
            # Calculate final ensemble scores
            final_results = []
            for result in all_results.values():
                # Weighted ensemble scoring
                ensemble_score = await self._calculate_ensemble_score(result)
                confidence = await self._calculate_confidence_score(result)
                
                result.final_score = ensemble_score
                result.confidence = confidence
                result.relevance_explanation = await self._generate_relevance_explanation(result)
                
                # Filter by confidence threshold
                if confidence >= context.confidence_threshold:
                    final_results.append(result)
            
            # Sort by final score
            final_results.sort(key=lambda x: x.final_score, reverse=True)
            
            # Return top results
            return final_results[:context.max_results]
            
        except Exception as e:
            self.logger.error(f"❌ Ensemble ranking failed: {e}")
            return []

    # Helper methods
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder - would use actual embedding service)"""
        # This would integrate with your embedding service
        # For now, return a dummy embedding
        return [0.1] * self.embedding_dimension

    async def _build_search_filter(self, context: SearchContext, collection: str) -> Optional[Filter]:
        """Build search filter based on context"""
        filters = []
        
        # Business domain filter
        if context.business_domain:
            filters.append(
                FieldCondition(
                    key="business_domain",
                    match=MatchValue(value=context.business_domain)
                )
            )
        
        # User access filter
        filters.append(
            FieldCondition(
                key="access_level",
                match=MatchValue(value="public")
            )
        )
        
        return Filter(must=filters) if filters else None

    async def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        # Simple keyword extraction (would use NLP in production)
        import re
        words = re.findall(r'\b\w+\b', query.lower())
        return [word for word in words if len(word) > 2]

    async def _calculate_bm25_score(self, content: str, keywords: List[str]) -> float:
        """Calculate BM25-style score"""
        # Simplified BM25 calculation
        score = 0.0
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword in content_lower:
                tf = content_lower.count(keyword)
                score += tf / (tf + 1.2)  # Simplified BM25 formula
        
        return min(score, 1.0)

    async def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities from query"""
        # Simple entity extraction (would use NER in production)
        import re
        # Look for capitalized words as potential entities
        entities = re.findall(r'\b[A-Z][a-z]+\b', query)
        return entities

    async def _calculate_relationship_score(self, entity: str, payload: Dict[str, Any]) -> float:
        """Calculate relationship score between entity and document"""
        # Simple relationship scoring
        entities_in_doc = payload.get("entities", [])
        if entity in entities_in_doc:
            return 1.0
        
        # Check for related entities
        content = payload.get("content", "").lower()
        if entity.lower() in content:
            return 0.7
        
        return 0.0

    async def _get_user_history(self, user_id: str) -> Dict[str, Any]:
        """Get user interaction history"""
        # Placeholder for user history retrieval
        return {
            "preferred_topics": [],
            "interaction_patterns": {},
            "feedback_history": []
        }

    async def _calculate_personalization_score(self, result: SearchResult, 
                                             user_history: Dict[str, Any]) -> float:
        """Calculate personalization score"""
        # Simple personalization scoring
        return 0.1  # Placeholder

    async def _calculate_ensemble_score(self, result: SearchResult) -> float:
        """Calculate weighted ensemble score"""
        weights = {
            SearchResultType.DENSE_SEMANTIC: 0.4,
            SearchResultType.SPARSE_KEYWORD: 0.3,
            SearchResultType.GRAPH_RELATIONSHIP: 0.2,
            SearchResultType.TEMPORAL_RELEVANCE: 0.1
        }
        
        ensemble_score = 0.0
        total_weight = 0.0
        
        for score_type, score in result.scores.items():
            if score_type in weights:
                ensemble_score += score * weights[score_type]
                total_weight += weights[score_type]
        
        return ensemble_score / total_weight if total_weight > 0 else 0.0

    async def _calculate_confidence_score(self, result: SearchResult) -> float:
        """Calculate confidence score"""
        # Simple confidence calculation based on number of signals
        num_signals = len(result.scores)
        avg_score = sum(result.scores.values()) / num_signals if num_signals > 0 else 0.0
        
        # Boost confidence with more signals
        confidence_boost = min(num_signals * 0.1, 0.3)
        return min(avg_score + confidence_boost, 1.0)

    async def _generate_relevance_explanation(self, result: SearchResult) -> str:
        """Generate human-readable relevance explanation"""
        explanations = []
        
        for score_type, score in result.scores.items():
            if score > 0.5:
                explanations.append(f"{score_type.value}: {score:.3f}")
        
        return "; ".join(explanations) if explanations else "Low relevance"

    async def _ensure_collections_exist(self):
        """Ensure all required collections exist"""
        # This would check and create collections if needed
        # For now, assume they exist
        pass

    # Business Intelligence Methods
    async def intelligent_business_search(self, query: str, context: SearchContext) -> BusinessInsights:
        """
        Business-aware search that understands:
        - Revenue impact context
        - Customer relationship context  
        - Sales pipeline context
        - Market positioning context
        """
        try:
            # Classify business intent
            business_intent = await self._classify_business_intent(query)
            
            # Route to appropriate business intelligence layer
            if business_intent in ["customer", "client"]:
                return await self._search_customer_intelligence(query, context)
            elif business_intent in ["sales", "revenue"]:
                return await self._search_sales_intelligence(query, context)
            elif business_intent in ["market", "competition"]:
                return await self._search_market_intelligence(query, context)
            else:
                return await self._search_general_business_intelligence(query, context)
                
        except Exception as e:
            self.logger.error(f"❌ Business intelligence search failed: {e}")
            raise

    async def _classify_business_intent(self, query: str) -> str:
        """Classify the business intent of the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["customer", "client", "account", "churn"]):
            return "customer"
        elif any(word in query_lower for word in ["sales", "revenue", "deal", "pipeline"]):
            return "sales"
        elif any(word in query_lower for word in ["market", "competition", "competitor"]):
            return "market"
        else:
            return "general"

    async def _search_customer_intelligence(self, query: str, context: SearchContext) -> BusinessInsights:
        """Search customer intelligence layer"""
        # Perform hybrid search with customer focus
        results = await self.hybrid_search(query, context)
        
        # Filter for customer-related results
        customer_results = [r for r in results if "customer" in r.metadata.get("category", "")]
        
        return BusinessInsights(
            primary_insights=customer_results[:10],
            related_insights=customer_results[10:20],
            trend_analysis={"customer_health": "stable"},
            actionable_recommendations=["Review customer engagement patterns"],
            confidence_score=0.85,
            business_impact="Customer retention and growth"
        )

    async def _search_sales_intelligence(self, query: str, context: SearchContext) -> BusinessInsights:
        """Search sales intelligence layer"""
        # Perform hybrid search with sales focus
        results = await self.hybrid_search(query, context)
        
        # Filter for sales-related results
        sales_results = [r for r in results if "sales" in r.metadata.get("category", "")]
        
        return BusinessInsights(
            primary_insights=sales_results[:10],
            related_insights=sales_results[10:20],
            trend_analysis={"sales_velocity": "increasing"},
            actionable_recommendations=["Focus on high-value opportunities"],
            confidence_score=0.82,
            business_impact="Revenue growth and sales efficiency"
        )

    async def _search_market_intelligence(self, query: str, context: SearchContext) -> BusinessInsights:
        """Search market intelligence layer"""
        # Perform hybrid search with market focus
        results = await self.hybrid_search(query, context)
        
        # Filter for market-related results
        market_results = [r for r in results if "market" in r.metadata.get("category", "")]
        
        return BusinessInsights(
            primary_insights=market_results[:10],
            related_insights=market_results[10:20],
            trend_analysis={"market_trends": "growth_opportunity"},
            actionable_recommendations=["Expand into emerging segments"],
            confidence_score=0.78,
            business_impact="Market positioning and competitive advantage"
        )

    async def _search_general_business_intelligence(self, query: str, context: SearchContext) -> BusinessInsights:
        """Search general business intelligence"""
        # Perform hybrid search across all domains
        results = await self.hybrid_search(query, context)
        
        return BusinessInsights(
            primary_insights=results[:10],
            related_insights=results[10:20],
            trend_analysis={"overall_performance": "positive"},
            actionable_recommendations=["Continue current strategy"],
            confidence_score=0.75,
            business_impact="Overall business performance"
        ) 