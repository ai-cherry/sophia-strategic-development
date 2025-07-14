"""
Hypothetical RAG Service - Proactive Query Understanding
Phase 2 Implementation with HyDE Evolution and Self-Pruning

Features:
- Hypothetical Document Embeddings (HyDE) evolution
- Proactive "what-if" scenario generation
- Self-pruning memory architecture
- Intelligent cache warming
- Query anticipation and preparation
- Modular memory pruning based on MemOS patterns

Performance Targets:
- 30% recall improvement through hypothetical documents
- 20% storage reduction via intelligent self-pruning
- <50ms hypothetical document generation
- >80% cache hit rate for common queries
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict, deque

from backend.core.auto_esc_config import get_config_value
from backend.utils.logger import get_logger
from backend.services.unified_memory_service import UnifiedMemoryService

logger = get_logger(__name__)

class HypotheticalType(Enum):
    """Types of hypothetical documents"""
    ANSWER_FOCUSED = "answer_focused"  # Direct answer to query
    CONTEXT_RICH = "context_rich"     # Rich contextual information
    SCENARIO_BASED = "scenario_based"  # What-if scenarios
    PROCEDURAL = "procedural"         # How-to information
    COMPARATIVE = "comparative"       # Comparison-based content
    ANALYTICAL = "analytical"         # Deep analysis content

class PruningStrategy(Enum):
    """Memory pruning strategies"""
    AGE_BASED = "age_based"           # Remove old documents
    ACCESS_BASED = "access_based"     # Remove rarely accessed
    CONFIDENCE_BASED = "confidence_based"  # Remove low confidence
    REDUNDANCY_BASED = "redundancy_based"  # Remove similar documents
    SIZE_BASED = "size_based"         # Remove large documents

@dataclass
class HypotheticalDocument:
    """Hypothetical document for proactive RAG"""
    document_id: str
    query: str
    hypothetical_content: str
    document_type: HypotheticalType
    embedding: np.ndarray
    confidence: float
    created_at: datetime
    last_accessed: datetime
    access_count: int
    success_score: float  # How helpful this document has been
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "document_id": self.document_id,
            "query": self.query,
            "hypothetical_content": self.hypothetical_content,
            "document_type": self.document_type.value,
            "embedding": self.embedding.tolist(),
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "success_score": self.success_score,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HypotheticalDocument':
        """Create from dictionary"""
        return cls(
            document_id=data["document_id"],
            query=data["query"],
            hypothetical_content=data["hypothetical_content"],
            document_type=HypotheticalType(data["document_type"]),
            embedding=np.array(data["embedding"], dtype=np.float32),
            confidence=data["confidence"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            access_count=data["access_count"],
            success_score=data["success_score"],
            metadata=data.get("metadata", {})
        )

@dataclass
class PruningMetrics:
    """Metrics for pruning operations"""
    total_documents_before: int
    total_documents_after: int
    documents_pruned: int
    storage_freed_mb: float
    pruning_time_ms: float
    strategies_applied: List[str]
    confidence_threshold: float
    age_threshold_hours: float

class HypotheticalRAGService:
    """
    Proactive RAG with hypothetical document generation and self-pruning
    
    Implements HyDE evolution with intelligent memory management
    """
    
    def __init__(self):
        # Core services
        self.memory_service = UnifiedMemoryService()
        
        # Hypothetical document storage
        self.hypothetical_cache: Dict[str, HypotheticalDocument] = {}
        self.query_patterns: Dict[str, List[str]] = defaultdict(list)
        self.access_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Configuration
        self.max_cache_size = int(get_config_value("hypothetical_max_cache", "10000"))
        self.pruning_threshold = float(get_config_value("hypothetical_pruning_threshold", "0.1"))
        self.max_age_hours = float(get_config_value("hypothetical_max_age_hours", "168"))  # 7 days
        self.min_access_count = int(get_config_value("hypothetical_min_access", "2"))
        self.confidence_decay_rate = float(get_config_value("confidence_decay_rate", "0.95"))
        
        # Pruning configuration
        self.pruning_strategies = [
            PruningStrategy.CONFIDENCE_BASED,
            PruningStrategy.AGE_BASED,
            PruningStrategy.ACCESS_BASED,
            PruningStrategy.REDUNDANCY_BASED
        ]
        
        # Performance tracking
        self.metrics = {
            "hypothetical_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "pruning_operations": 0,
            "storage_freed_mb": 0,
            "avg_generation_time_ms": 0,
            "success_rate": 0.0
        }
        
        # Background tasks
        self.pruning_task = None
        self.warming_task = None
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize the hypothetical RAG service"""
        if self.initialized:
            return
            
        logger.info("Initializing Hypothetical RAG Service...")
        
        # Initialize base memory service
        await self.memory_service.initialize()
        
        # Load existing hypothetical documents
        await self._load_hypothetical_cache()
        
        # Start background tasks
        self.pruning_task = asyncio.create_task(self._background_pruning_loop())
        self.warming_task = asyncio.create_task(self._background_warming_loop())
        
        self.initialized = True
        logger.info(f"✅ Hypothetical RAG Service initialized with {len(self.hypothetical_cache)} documents")
    
    async def generate_hypothetical_answer(
        self, 
        query: str,
        document_type: HypotheticalType = HypotheticalType.ANSWER_FOCUSED,
        force_regenerate: bool = False
    ) -> HypotheticalDocument:
        """
        Generate hypothetical answer for better retrieval
        
        Args:
            query: The query to generate hypothetical answer for
            document_type: Type of hypothetical document to generate
            force_regenerate: Force regeneration even if cached
            
        Returns:
            HypotheticalDocument with generated content
        """
        start_time = time.time()
        
        # Generate cache key
        cache_key = hashlib.md5(f"{query}:{document_type.value}".encode()).hexdigest()
        
        # Check cache first
        if not force_regenerate and cache_key in self.hypothetical_cache:
            cached_doc = self.hypothetical_cache[cache_key]
            cached_doc.last_accessed = datetime.now()
            cached_doc.access_count += 1
            
            # Record access pattern
            self.access_patterns[cache_key].append(datetime.now())
            
            self.metrics["cache_hits"] += 1
            logger.debug(f"Cache hit for hypothetical document: {query}")
            return cached_doc
        
        # Generate new hypothetical document
        self.metrics["cache_misses"] += 1
        
        try:
            # Generate hypothetical content based on type
            hypothetical_content = await self._generate_hypothetical_content(query, document_type)
            
            # Generate embedding
            embedding = await self.memory_service.generate_embedding(hypothetical_content)
            
            # Create hypothetical document
            hyp_doc = HypotheticalDocument(
                document_id=cache_key,
                query=query,
                hypothetical_content=hypothetical_content,
                document_type=document_type,
                embedding=embedding,
                confidence=0.8,  # Initial confidence
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                success_score=0.5,  # Initial success score
                metadata={
                    "generation_time_ms": 0,  # Will be updated below
                    "query_length": len(query),
                    "content_length": len(hypothetical_content)
                }
            )
            
            # Store in cache
            self.hypothetical_cache[cache_key] = hyp_doc
            
            # Record query pattern
            self.query_patterns[document_type.value].append(query)
            
            # Update metrics
            generation_time_ms = (time.time() - start_time) * 1000
            hyp_doc.metadata["generation_time_ms"] = generation_time_ms
            
            self.metrics["hypothetical_generated"] += 1
            current_avg = self.metrics["avg_generation_time_ms"]
            total_generated = self.metrics["hypothetical_generated"]
            self.metrics["avg_generation_time_ms"] = ((current_avg * (total_generated - 1)) + generation_time_ms) / total_generated
            
            logger.info(f"Generated hypothetical document for '{query}' in {generation_time_ms:.1f}ms")
            
            # Check if cache needs pruning
            if len(self.hypothetical_cache) > self.max_cache_size:
                asyncio.create_task(self._emergency_pruning())
            
            return hyp_doc
            
        except Exception as e:
            logger.error(f"Failed to generate hypothetical document for '{query}': {e}")
            raise
    
    async def _generate_hypothetical_content(self, query: str, doc_type: HypotheticalType) -> str:
        """Generate hypothetical content based on query and type"""
        
        # Create type-specific prompts
        prompts = {
            HypotheticalType.ANSWER_FOCUSED: f"""
            Query: {query}
            
            Generate a comprehensive, direct answer to this query as if you were an expert.
            Include specific details, examples, and actionable information.
            Focus on providing exactly what the user is asking for.
            
            Make this answer rich and detailed - it will be used to improve search results.
            """,
            
            HypotheticalType.CONTEXT_RICH: f"""
            Query: {query}
            
            Generate rich contextual information related to this query.
            Include background information, related concepts, prerequisites, and implications.
            Provide the broader context that would help understand this topic fully.
            
            Think like a comprehensive knowledge base entry.
            """,
            
            HypotheticalType.SCENARIO_BASED: f"""
            Query: {query}
            
            Generate realistic scenarios and examples related to this query.
            Include "what-if" situations, use cases, and practical applications.
            Provide concrete examples that illustrate the concepts.
            
            Focus on practical, real-world scenarios.
            """,
            
            HypotheticalType.PROCEDURAL: f"""
            Query: {query}
            
            Generate step-by-step procedural information for this query.
            Include detailed instructions, best practices, and common pitfalls.
            Provide a clear methodology or process.
            
            Structure this as actionable, sequential guidance.
            """,
            
            HypotheticalType.COMPARATIVE: f"""
            Query: {query}
            
            Generate comparative analysis related to this query.
            Include comparisons between different approaches, options, or solutions.
            Highlight pros and cons, trade-offs, and decision criteria.
            
            Focus on helping users make informed choices.
            """,
            
            HypotheticalType.ANALYTICAL: f"""
            Query: {query}
            
            Generate deep analytical content for this query.
            Include detailed analysis, insights, patterns, and implications.
            Provide expert-level understanding and interpretation.
            
            Think like a research report or expert analysis.
            """
        }
        
        prompt = prompts.get(doc_type, prompts[HypotheticalType.ANSWER_FOCUSED])
        
        try:
            # Use the memory service's LLM capabilities
            response = await self.memory_service.portkey.chat.completions.acreate(
                model="openai/gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed for hypothetical content: {e}")
            # Fallback content
            return f"Comprehensive information about: {query}\n\nThis hypothetical document provides detailed insights and analysis related to the query, including relevant context, examples, and actionable information."
    
    async def hypothetical_search(
        self, 
        query: str, 
        limit: int = 10,
        include_types: Optional[List[HypotheticalType]] = None,
        boost_factor: float = 1.2
    ) -> List[Dict[str, Any]]:
        """
        Search using hypothetical document embeddings
        
        Args:
            query: Search query
            limit: Maximum number of results
            include_types: Types of hypothetical documents to include
            boost_factor: Boost factor for hypothetical results
            
        Returns:
            List of search results with hypothetical enhancement
        """
        try:
            # Generate hypothetical documents for different types
            if include_types is None:
                include_types = [HypotheticalType.ANSWER_FOCUSED, HypotheticalType.CONTEXT_RICH]
            
            hypothetical_docs = []
            for doc_type in include_types:
                try:
                    hyp_doc = await self.generate_hypothetical_answer(query, doc_type)
                    hypothetical_docs.append(hyp_doc)
                except Exception as e:
                    logger.warning(f"Failed to generate {doc_type} hypothetical doc: {e}")
            
            # Search using hypothetical embeddings
            all_results = []
            
            for hyp_doc in hypothetical_docs:
                # Use hypothetical embedding for search
                search_results = await self._search_with_hypothetical_embedding(
                    hyp_doc.embedding, query, limit
                )
                
                # Boost scores and add hypothetical context
                for result in search_results:
                    result["score"] *= boost_factor
                    result["hypothetical_enhanced"] = True
                    result["hypothetical_type"] = hyp_doc.document_type.value
                    result["hypothetical_confidence"] = hyp_doc.confidence
                
                all_results.extend(search_results)
            
            # Also include regular search results
            regular_results = await self.memory_service.search_knowledge(query, limit=limit//2)
            for result in regular_results:
                result["hypothetical_enhanced"] = False
                all_results.append(result)
            
            # Deduplicate and rank
            deduplicated_results = self._deduplicate_results(all_results)
            ranked_results = sorted(deduplicated_results, key=lambda x: x.get("score", 0), reverse=True)
            
            # Update success scores for used hypothetical documents
            await self._update_hypothetical_success_scores(hypothetical_docs, ranked_results)
            
            return ranked_results[:limit]
            
        except Exception as e:
            logger.error(f"Hypothetical search failed: {e}")
            # Fallback to regular search
            return await self.memory_service.search_knowledge(query, limit=limit)
    
    async def _search_with_hypothetical_embedding(
        self, 
        embedding: np.ndarray, 
        query: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search using a hypothetical embedding"""
        # This would integrate with the actual search infrastructure
        # For now, simulate search results
        
        # In production, this would:
        # 1. Use the embedding to search Weaviate
        # 2. Search PostgreSQL with pgvector
        # 3. Combine and rank results
        
        # Simulate search results
        return [
            {
                "content": f"Result {i+1} for hypothetical search: {query}",
                "source": "hypothetical_search",
                "score": 0.9 - (i * 0.1),
                "metadata": {"search_type": "hypothetical"}
            }
            for i in range(min(3, limit))
        ]
    
    async def _update_hypothetical_success_scores(
        self, 
        hypothetical_docs: List[HypotheticalDocument], 
        results: List[Dict[str, Any]]
    ):
        """Update success scores based on search result quality"""
        
        # Calculate success metrics
        total_score = sum(result.get("score", 0) for result in results[:5])  # Top 5 results
        avg_score = total_score / min(5, len(results)) if results else 0
        
        # Update success scores for hypothetical documents
        for hyp_doc in hypothetical_docs:
            # Exponential moving average
            hyp_doc.success_score = 0.8 * hyp_doc.success_score + 0.2 * avg_score
            
            # Update confidence based on success
            if hyp_doc.success_score > 0.7:
                hyp_doc.confidence = min(1.0, hyp_doc.confidence * 1.05)
            elif hyp_doc.success_score < 0.3:
                hyp_doc.confidence = max(0.1, hyp_doc.confidence * 0.95)
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""
        seen_content = set()
        deduplicated = []
        
        for result in results:
            content = result.get("content", "")
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                deduplicated.append(result)
        
        return deduplicated
    
    async def _background_pruning_loop(self):
        """Background task for regular memory pruning"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._comprehensive_pruning()
            except Exception as e:
                logger.error(f"Background pruning failed: {e}")
    
    async def _background_warming_loop(self):
        """Background task for cache warming"""
        while True:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                await self._warm_hypothetical_cache()
            except Exception as e:
                logger.error(f"Background warming failed: {e}")
    
    async def _comprehensive_pruning(self) -> PruningMetrics:
        """Comprehensive memory pruning using multiple strategies"""
        start_time = time.time()
        initial_count = len(self.hypothetical_cache)
        initial_size_mb = self._calculate_cache_size_mb()
        
        logger.info(f"Starting comprehensive pruning of {initial_count} hypothetical documents")
        
        pruned_docs = []
        strategies_applied = []
        
        # Apply pruning strategies in order
        for strategy in self.pruning_strategies:
            if strategy == PruningStrategy.CONFIDENCE_BASED:
                pruned = await self._prune_by_confidence()
                pruned_docs.extend(pruned)
                if pruned:
                    strategies_applied.append("confidence_based")
            
            elif strategy == PruningStrategy.AGE_BASED:
                pruned = await self._prune_by_age()
                pruned_docs.extend(pruned)
                if pruned:
                    strategies_applied.append("age_based")
            
            elif strategy == PruningStrategy.ACCESS_BASED:
                pruned = await self._prune_by_access()
                pruned_docs.extend(pruned)
                if pruned:
                    strategies_applied.append("access_based")
            
            elif strategy == PruningStrategy.REDUNDANCY_BASED:
                pruned = await self._prune_by_redundancy()
                pruned_docs.extend(pruned)
                if pruned:
                    strategies_applied.append("redundancy_based")
        
        # Remove pruned documents from cache
        for doc_id in pruned_docs:
            if doc_id in self.hypothetical_cache:
                del self.hypothetical_cache[doc_id]
        
        # Calculate metrics
        final_count = len(self.hypothetical_cache)
        final_size_mb = self._calculate_cache_size_mb()
        pruning_time_ms = (time.time() - start_time) * 1000
        
        metrics = PruningMetrics(
            total_documents_before=initial_count,
            total_documents_after=final_count,
            documents_pruned=len(pruned_docs),
            storage_freed_mb=initial_size_mb - final_size_mb,
            pruning_time_ms=pruning_time_ms,
            strategies_applied=strategies_applied,
            confidence_threshold=self.pruning_threshold,
            age_threshold_hours=self.max_age_hours
        )
        
        # Update global metrics
        self.metrics["pruning_operations"] += 1
        self.metrics["storage_freed_mb"] += metrics.storage_freed_mb
        
        logger.info(f"Pruning completed: {metrics.documents_pruned} documents removed, {metrics.storage_freed_mb:.2f}MB freed")
        
        return metrics
    
    async def _prune_by_confidence(self) -> List[str]:
        """Prune documents with low confidence scores"""
        to_prune = []
        
        for doc_id, doc in self.hypothetical_cache.items():
            if doc.confidence < self.pruning_threshold:
                to_prune.append(doc_id)
        
        return to_prune
    
    async def _prune_by_age(self) -> List[str]:
        """Prune old documents"""
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        to_prune = []
        
        for doc_id, doc in self.hypothetical_cache.items():
            if doc.created_at < cutoff_time:
                to_prune.append(doc_id)
        
        return to_prune
    
    async def _prune_by_access(self) -> List[str]:
        """Prune rarely accessed documents"""
        cutoff_time = datetime.now() - timedelta(hours=72)  # 3 days
        to_prune = []
        
        for doc_id, doc in self.hypothetical_cache.items():
            if (doc.last_accessed < cutoff_time and 
                doc.access_count < self.min_access_count):
                to_prune.append(doc_id)
        
        return to_prune
    
    async def _prune_by_redundancy(self) -> List[str]:
        """Prune redundant/similar documents"""
        to_prune = []
        
        # Group documents by query similarity
        query_groups = defaultdict(list)
        
        for doc_id, doc in self.hypothetical_cache.items():
            # Simple grouping by query words
            query_key = " ".join(sorted(doc.query.lower().split()[:3]))
            query_groups[query_key].append(doc_id)
        
        # Keep only the best document from each group
        for group_docs in query_groups.values():
            if len(group_docs) > 1:
                # Sort by success score and keep the best
                group_docs.sort(key=lambda doc_id: self.hypothetical_cache[doc_id].success_score, reverse=True)
                to_prune.extend(group_docs[1:])  # Remove all except the best
        
        return to_prune
    
    async def _emergency_pruning(self):
        """Emergency pruning when cache is too large"""
        if len(self.hypothetical_cache) <= self.max_cache_size:
            return
        
        logger.warning(f"Emergency pruning triggered: {len(self.hypothetical_cache)} > {self.max_cache_size}")
        
        # Quick pruning - remove oldest 20%
        docs_to_remove = int(len(self.hypothetical_cache) * 0.2)
        
        # Sort by last accessed time
        sorted_docs = sorted(
            self.hypothetical_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        for doc_id, _ in sorted_docs[:docs_to_remove]:
            del self.hypothetical_cache[doc_id]
        
        logger.info(f"Emergency pruning removed {docs_to_remove} documents")
    
    async def _warm_hypothetical_cache(self):
        """Warm cache with anticipated queries"""
        # Analyze query patterns to predict future queries
        common_patterns = self._analyze_query_patterns()
        
        for pattern in common_patterns[:5]:  # Top 5 patterns
            try:
                # Generate hypothetical documents for predicted queries
                predicted_query = self._generate_predicted_query(pattern)
                if predicted_query:
                    await self.generate_hypothetical_answer(
                        predicted_query, 
                        HypotheticalType.ANSWER_FOCUSED
                    )
            except Exception as e:
                logger.warning(f"Cache warming failed for pattern {pattern}: {e}")
    
    def _analyze_query_patterns(self) -> List[str]:
        """Analyze query patterns to identify common themes"""
        # Simple pattern analysis - in production would be more sophisticated
        all_queries = []
        for doc in self.hypothetical_cache.values():
            all_queries.append(doc.query.lower())
        
        # Find common words
        word_counts = defaultdict(int)
        for query in all_queries:
            for word in query.split():
                if len(word) > 3:  # Skip short words
                    word_counts[word] += 1
        
        # Return most common words as patterns
        return [word for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    def _generate_predicted_query(self, pattern: str) -> Optional[str]:
        """Generate a predicted query based on a pattern"""
        # Simple query generation - in production would use more sophisticated methods
        templates = [
            f"How to {pattern}?",
            f"What is {pattern}?",
            f"Best practices for {pattern}",
            f"Examples of {pattern}",
            f"Problems with {pattern}"
        ]
        
        import random
        return random.choice(templates)
    
    def _calculate_cache_size_mb(self) -> float:
        """Calculate approximate cache size in MB"""
        total_size = 0
        
        for doc in self.hypothetical_cache.values():
            # Approximate size calculation
            content_size = len(doc.hypothetical_content.encode('utf-8'))
            embedding_size = doc.embedding.nbytes
            metadata_size = len(json.dumps(doc.metadata).encode('utf-8'))
            
            total_size += content_size + embedding_size + metadata_size
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    async def _load_hypothetical_cache(self):
        """Load existing hypothetical documents from storage"""
        # This would load from persistent storage in production
        # For now, start with empty cache
        logger.info("Starting with empty hypothetical cache")
    
    async def _save_hypothetical_cache(self):
        """Save hypothetical cache to persistent storage"""
        # This would save to persistent storage in production
        pass
    
    def get_pruning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pruning and performance statistics"""
        cache_size_mb = self._calculate_cache_size_mb()
        
        # Calculate hit rate
        total_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        hit_rate = self.metrics["cache_hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "cache_statistics": {
                "total_documents": len(self.hypothetical_cache),
                "cache_size_mb": cache_size_mb,
                "max_cache_size": self.max_cache_size,
                "utilization_percent": (len(self.hypothetical_cache) / self.max_cache_size) * 100
            },
            "performance_metrics": {
                **self.metrics,
                "cache_hit_rate": hit_rate,
                "avg_document_size_kb": (cache_size_mb * 1024) / len(self.hypothetical_cache) if self.hypothetical_cache else 0
            },
            "pruning_configuration": {
                "pruning_threshold": self.pruning_threshold,
                "max_age_hours": self.max_age_hours,
                "min_access_count": self.min_access_count,
                "strategies": [s.value for s in self.pruning_strategies]
            },
            "document_type_distribution": self._get_document_type_distribution(),
            "access_patterns": self._get_access_pattern_summary()
        }
    
    def _get_document_type_distribution(self) -> Dict[str, int]:
        """Get distribution of document types in cache"""
        distribution = defaultdict(int)
        for doc in self.hypothetical_cache.values():
            distribution[doc.document_type.value] += 1
        return dict(distribution)
    
    def _get_access_pattern_summary(self) -> Dict[str, Any]:
        """Get summary of access patterns"""
        if not self.hypothetical_cache:
            return {}
        
        access_counts = [doc.access_count for doc in self.hypothetical_cache.values()]
        success_scores = [doc.success_score for doc in self.hypothetical_cache.values()]
        
        return {
            "avg_access_count": np.mean(access_counts),
            "max_access_count": max(access_counts),
            "avg_success_score": np.mean(success_scores),
            "high_performing_docs": sum(1 for score in success_scores if score > 0.8)
        }


# Singleton instance
_hypothetical_rag_instance = None

async def get_hypothetical_rag_service() -> HypotheticalRAGService:
    """Get the singleton HypotheticalRAGService instance"""
    global _hypothetical_rag_instance
    if _hypothetical_rag_instance is None:
        _hypothetical_rag_instance = HypotheticalRAGService()
        await _hypothetical_rag_instance.initialize()
    return _hypothetical_rag_instance 