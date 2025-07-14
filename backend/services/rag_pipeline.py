"""
Retrieval-Augmented Generation (RAG) Pipeline for Sophia AI

Implements a production-ready RAG system with query enhancement,
result reranking, context building, and response validation.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from backend.services.hybrid_search_engine import HybridSearchEngine, SearchResult
from backend.services.unified_memory_service_v2 import get_unified_memory_service
from backend.services.query_optimizer import QueryOptimizer, QueryType
from backend.services.document_chunking_service import DocumentChunk
from backend.services.redis_helper import RedisHelper
from backend.services.portkey_gateway import PortkeyGateway
from shared.utils.monitoring import log_execution_time

logger = logging.getLogger(__name__)


class GenerationModel(Enum):
    """Available LLM models for generation"""

    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    CLAUDE_3 = "claude-3-opus"
    LLAMA3 = "llama-3-70b"


@dataclass
class RAGQuery:
    """Represents a RAG query with metadata"""

    query_id: str
    original_query: str
    enhanced_query: str
    query_type: QueryType
    user_context: Dict[str, Any] = field(default_factory=dict)
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RAGContext:
    """Retrieved context for generation"""

    chunks: List[DocumentChunk]
    relevance_scores: List[float]
    total_tokens: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGResponse:
    """Generated response with metadata"""

    response_id: str
    query_id: str
    response_text: str
    source_chunks: List[str]  # chunk_ids
    confidence_score: float
    generation_model: str
    total_tokens_used: int
    latency_ms: float
    validation_results: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class QueryEnhancer:
    """Enhances user queries for better retrieval"""

    def __init__(self):
        self.memory_service = get_unified_memory_service()

    async def enhance_query(
        self, query: str, user_context: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """
        Enhance query with synonyms, expansions, and context

        Returns:
            Tuple of (enhanced_query, additional_search_terms)
        """
        # Extract key concepts
        key_concepts = self._extract_key_concepts(query)

        # Generate synonyms and related terms
        synonyms = await self._generate_synonyms(key_concepts)

        # Add contextual terms based on user history
        contextual_terms = await self._get_contextual_terms(query, user_context)

        # Expand abbreviations and acronyms
        expanded_query = self._expand_abbreviations(query)

        # Combine enhancements
        enhanced_terms = list(set(synonyms + contextual_terms))
        enhanced_query = f"{expanded_query} {' '.join(enhanced_terms)}"

        return enhanced_query.strip(), enhanced_terms

    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key concepts from query"""
        # Simple implementation - in production use NLP
        # Remove stop words and extract important terms
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "is",
            "are",
            "was",
            "were",
        }
        words = query.lower().split()
        concepts = [w for w in words if w not in stop_words and len(w) > 2]
        return concepts

    async def _generate_synonyms(self, concepts: List[str]) -> List[str]:
        """Generate synonyms for key concepts"""
        synonyms = []

        # Domain-specific synonyms for business context
        synonym_map = {
            "revenue": ["income", "earnings", "sales"],
            "customer": ["client", "user", "account"],
            "deal": ["opportunity", "contract", "agreement"],
            "employee": ["staff", "team member", "personnel"],
            "project": ["initiative", "task", "assignment"],
            "meeting": ["call", "discussion", "conference"],
            "report": ["analysis", "summary", "document"],
            "metric": ["kpi", "measure", "indicator"],
        }

        for concept in concepts:
            if concept in synonym_map:
                synonyms.extend(synonym_map[concept])

        return synonyms

    async def _get_contextual_terms(
        self, query: str, user_context: Dict[str, Any]
    ) -> List[str]:
        """Get contextual terms based on user history"""
        contextual_terms = []

        # Check recent queries for related terms
        recent_queries = user_context.get("recent_queries", [])
        for recent in recent_queries[-5:]:  # Last 5 queries
            # Extract terms that might be related
            terms = self._extract_key_concepts(recent)
            for term in terms:
                if term not in query.lower():
                    contextual_terms.append(term)

        # Add user role/department specific terms
        user_role = user_context.get("role", "").lower()
        if "sales" in user_role:
            contextual_terms.extend(["revenue", "deals", "pipeline"])
        elif "marketing" in user_role:
            contextual_terms.extend(["campaign", "leads", "conversion"])
        elif "engineering" in user_role:
            contextual_terms.extend(["code", "deployment", "performance"])

        return list(set(contextual_terms))

    def _expand_abbreviations(self, query: str) -> str:
        """Expand common abbreviations and acronyms"""
        abbreviations = {
            "kpi": "key performance indicator",
            "roi": "return on investment",
            "crm": "customer relationship management",
            "api": "application programming interface",
            "ui": "user interface",
            "ux": "user experience",
            "hr": "human resources",
            "qa": "quality assurance",
            "ml": "machine learning",
            "ai": "artificial intelligence",
        }

        expanded = query
        for abbr, full in abbreviations.items():
            # Case-insensitive replacement
            import re

            pattern = r"\b" + abbr + r"\b"
            expanded = re.sub(
                pattern, f"{abbr} ({full})", expanded, flags=re.IGNORECASE
            )

        return expanded


class ResultReranker:
    """Reranks search results for optimal relevance"""

    def __init__(self):
        self.memory_service = get_unified_memory_service()
        self.portkey = PortkeyGateway()

    async def rerank_results(
        self, query: str, results: List[SearchResult], top_k: int = 5
    ) -> List[SearchResult]:
        """
        Rerank search results using advanced scoring

        Args:
            query: The user query
            results: Initial search results
            top_k: Number of top results to return

        Returns:
            Reranked results
        """
        if not results:
            return []

        # Calculate multiple relevance signals
        reranked = []

        for result in results:
            # Cross-encoder scoring (query-document relevance)
            cross_score = await self._calculate_cross_encoder_score(
                query, result.content
            )

            # Recency boost
            recency_score = self._calculate_recency_score(result.metadata)

            # Authority score (based on source)
            authority_score = self._calculate_authority_score(result.metadata)

            # Diversity penalty (to avoid redundant results)
            diversity_penalty = self._calculate_diversity_penalty(result, reranked)

            # Combined reranking score
            final_score = (
                0.5 * cross_score
                + 0.2 * result.relevance_score
                + 0.1 * recency_score  # Original score
                + 0.1 * authority_score
                + 0.1 * (1 - diversity_penalty)
            )

            result.relevance_score = final_score
            reranked.append(result)

        # Sort by final score
        reranked.sort(key=lambda x: x.relevance_score, reverse=True)

        return reranked[:top_k]

    async def _calculate_cross_encoder_score(self, query: str, document: str) -> float:
        """Calculate cross-encoder relevance score"""
        # In production, use a fine-tuned cross-encoder model
        # For now, use LLM-based scoring

        prompt = f"""Rate the relevance of this document to the query on a scale of 0-1.
Query: {query}
Document: {document[:500]}...

Return only a number between 0 and 1."""

        try:
            response = await self.portkey.complete(
                prompt=prompt, model=GenerationModel.GPT4_TURBO.value, temperature=0
            )
            score = float(response.strip())
            return max(0, min(1, score))
        except ValueError:
            # Fallback to simple keyword matching
            query_terms = set(query.lower().split())
            doc_terms = set(document.lower().split())
            if query_terms:
                return len(query_terms & doc_terms) / len(query_terms)
            return 0.5

    def _calculate_recency_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate recency score based on document age"""
        created_at = metadata.get("created_at")
        if not created_at:
            return 0.5

        # Parse datetime
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        # Calculate age in days
        age_days = (datetime.now() - created_at).days

        # Exponential decay with 30-day half-life
        import math

        return math.exp(-age_days / 30)

    def _calculate_authority_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate authority score based on source"""
        source = metadata.get("source", "").lower()

        # Authority weights for different sources
        authority_weights = {
            "official_docs": 1.0,
            "qdrant": 0.9,
            "gong": 0.8,
            "hubspot": 0.8,
            "slack": 0.6,
            "user_upload": 0.5,
            "web_scrape": 0.4,
        }

        for key, weight in authority_weights.items():
            if key in source:
                return weight

        return 0.5  # Default authority

    def _calculate_diversity_penalty(
        self, result: SearchResult, existing: List[SearchResult]
    ) -> float:
        """Calculate diversity penalty to avoid redundant results"""
        if not existing:
            return 0.0

        # Simple content similarity check
        max_similarity = 0.0

        for existing_result in existing:
            # Calculate Jaccard similarity
            words1 = set(result.content.lower().split())
            words2 = set(existing_result.content.lower().split())

            if words1 | words2:
                similarity = len(words1 & words2) / len(words1 | words2)
                max_similarity = max(max_similarity, similarity)

        # High similarity = high penalty
        return max_similarity


class ContextBuilder:
    """Builds coherent context from retrieved chunks"""

    def __init__(self):
        self.max_context_tokens = 4000  # Leave room for query and response

    async def build_context(
        self, chunks: List[DocumentChunk], scores: List[float], query: str
    ) -> RAGContext:
        """
        Build coherent context from chunks

        Args:
            chunks: Retrieved document chunks
            scores: Relevance scores for each chunk
            query: The user query

        Returns:
            RAGContext with organized chunks
        """
        # Sort chunks by relevance
        chunk_score_pairs = list(zip(chunks, scores))
        chunk_score_pairs.sort(key=lambda x: x[1], reverse=True)

        # Build context within token limit
        selected_chunks = []
        selected_scores = []
        total_tokens = 0

        for chunk, score in chunk_score_pairs:
            # Estimate tokens (rough: 1 token ≈ 4 characters)
            chunk_tokens = len(chunk.content) // 4

            if total_tokens + chunk_tokens <= self.max_context_tokens:
                selected_chunks.append(chunk)
                selected_scores.append(score)
                total_tokens += chunk_tokens
            else:
                # Try to fit partial chunk
                remaining_tokens = self.max_context_tokens - total_tokens
                if remaining_tokens > 100:  # Minimum useful chunk size
                    # Truncate chunk
                    truncated_content = chunk.content[: remaining_tokens * 4]
                    chunk.content = truncated_content + "..."
                    selected_chunks.append(chunk)
                    selected_scores.append(score)
                    total_tokens = self.max_context_tokens
                break

        # Reorder chunks for coherence (by document order, not score)
        selected_chunks.sort(key=lambda x: (x.document_id, x.sequence))

        # Build metadata
        metadata = {
            "total_chunks_retrieved": len(chunks),
            "chunks_used": len(selected_chunks),
            "avg_relevance_score": (
                sum(selected_scores) / len(selected_scores) if selected_scores else 0
            ),
            "sources": list(set(c.document_id for c in selected_chunks)),
        }

        return RAGContext(
            chunks=selected_chunks,
            relevance_scores=selected_scores,
            total_tokens=total_tokens,
            metadata=metadata,
        )


class ResponseValidator:
    """Validates generated responses for quality and accuracy"""

    def __init__(self):
        self.portkey = PortkeyGateway()

    async def validate_response(
        self, response: str, context: RAGContext, query: str
    ) -> Dict[str, Any]:
        """
        Validate response quality and accuracy

        Returns:
            Validation results with scores and issues
        """
        validation_results = {}

        # Check factual accuracy against context
        factual_score = await self._check_factual_accuracy(response, context)
        validation_results["factual_accuracy"] = factual_score

        # Check response completeness
        completeness_score = await self._check_completeness(response, query)
        validation_results["completeness"] = completeness_score

        # Check for hallucinations
        hallucination_check = await self._check_hallucinations(response, context)
        validation_results["hallucination_free"] = hallucination_check["score"]
        validation_results["potential_hallucinations"] = hallucination_check["issues"]

        # Check response coherence
        coherence_score = self._check_coherence(response)
        validation_results["coherence"] = coherence_score

        # Calculate overall quality score
        validation_results["overall_score"] = (
            0.4 * factual_score
            + 0.3 * hallucination_check["score"]
            + 0.2 * completeness_score
            + 0.1 * coherence_score
        )

        # Determine if response is acceptable
        validation_results["is_acceptable"] = validation_results["overall_score"] >= 0.8

        return validation_results

    async def _check_factual_accuracy(
        self, response: str, context: RAGContext
    ) -> float:
        """Check if response facts align with context"""
        # Extract facts from response
        response_facts = self._extract_facts(response)

        # Check each fact against context
        accurate_facts = 0
        total_facts = len(response_facts)

        if total_facts == 0:
            return 1.0  # No specific facts to verify

        context_text = "\n".join(chunk.content for chunk in context.chunks)

        for fact in response_facts:
            # Simple check: is the fact mentioned in context?
            if self._fact_in_context(fact, context_text):
                accurate_facts += 1

        return accurate_facts / total_facts

    async def _check_completeness(self, response: str, query: str) -> float:
        """Check if response addresses all aspects of the query"""
        # Extract question components
        query_aspects = self._extract_query_aspects(query)

        if not query_aspects:
            return 1.0

        addressed_aspects = 0
        for aspect in query_aspects:
            if aspect.lower() in response.lower():
                addressed_aspects += 1

        return addressed_aspects / len(query_aspects)

    async def _check_hallucinations(
        self, response: str, context: RAGContext
    ) -> Dict[str, Any]:
        """Check for potential hallucinations"""
        context_text = "\n".join(chunk.content for chunk in context.chunks)

        # Use LLM to check for unsupported claims
        prompt = f"""Given the following context and response, identify any claims in the response that are NOT supported by the context.

Context:
{context_text[:2000]}...

Response:
{response}

List any unsupported claims. If all claims are supported, respond with "None"."""

        try:
            result = await self.portkey.complete(
                prompt=prompt, model=GenerationModel.GPT4_TURBO.value, temperature=0
            )

            if result.strip().lower() == "none":
                return {"score": 1.0, "issues": []}
            else:
                issues = [
                    issue.strip() for issue in result.split("\n") if issue.strip()
                ]
                score = max(0, 1 - (len(issues) * 0.2))  # Deduct 0.2 per issue
                return {"score": score, "issues": issues}
        except Exception:
            # Fallback check
            return {"score": 0.8, "issues": ["Could not verify hallucinations"]}

    def _check_coherence(self, response: str) -> float:
        """Check response coherence and structure"""
        sentences = response.split(". ")

        if len(sentences) < 2:
            return 1.0

        # Check for logical flow indicators
        flow_indicators = [
            "therefore",
            "however",
            "additionally",
            "furthermore",
            "in conclusion",
            "for example",
            "specifically",
        ]

        flow_count = sum(
            1 for indicator in flow_indicators if indicator in response.lower()
        )

        # Check for repetition
        unique_sentences = len(set(sentences))
        repetition_ratio = unique_sentences / len(sentences)

        # Combined coherence score
        flow_score = min(1.0, flow_count / (len(sentences) - 1))

        return (repetition_ratio + flow_score) / 2

    def _extract_facts(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        facts = []

        # Simple pattern matching for factual statements
        fact_patterns = [
            r"is \d+",  # Numeric facts
            r"are \d+",
            r"was \d+",
            r"were \d+",
            r"has \d+",
            r"have \d+",
            r"increased by \d+",
            r"decreased by \d+",
            r"(\d+)%",  # Percentage facts
        ]

        import re

        for pattern in fact_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            facts.extend(matches)

        return facts

    def _fact_in_context(self, fact: str, context: str) -> bool:
        """Check if a fact appears in context"""
        # Simple substring check - in production use semantic similarity
        return fact.lower() in context.lower()

    def _extract_query_aspects(self, query: str) -> List[str]:
        """Extract different aspects from a query"""
        # Question words indicate different aspects
        question_words = ["what", "why", "how", "when", "where", "who"]

        aspects = []
        for word in question_words:
            if word in query.lower():
                # Extract the phrase after the question word
                import re

                pattern = f"{word}\\s+([^,.?]+)"
                matches = re.findall(pattern, query, re.IGNORECASE)
                aspects.extend(matches)

        return aspects


class RAGPipeline:
    """Main RAG pipeline orchestrating all components"""

    def __init__(self, generation_model: GenerationModel = GenerationModel.GPT4_TURBO):
        self.search_engine = HybridSearchEngine()
        self.query_optimizer = QueryOptimizer()
        self.query_enhancer = QueryEnhancer()
        self.reranker = ResultReranker()
        self.context_builder = ContextBuilder()
        self.response_validator = ResponseValidator()
        self.portkey = PortkeyGateway()
        self.redis_helper = RedisHelper()
        self.generation_model = generation_model
        self.cache_ttl = 3600  # 1 hour cache

    @log_execution_time
    async def process_query(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
    ) -> RAGResponse:
        """
        Process a query through the complete RAG pipeline

        Args:
            query: User query
            user_context: User context and history
            metadata_filters: Filters for search

        Returns:
            RAGResponse with generated answer
        """
        import time

        start_time = time.time()

        # Generate query ID
        import uuid

        query_id = str(uuid.uuid4())

        # Check cache
        cache_key = f"rag:{query}:{json.dumps(metadata_filters or {})}"
        cached_response = await self.redis_helper.get_json(cache_key)
        if cached_response:
            return RAGResponse(**cached_response)

        # Enhance query
        enhanced_query, additional_terms = await self.query_enhancer.enhance_query(
            query, user_context or {}
        )

        # Analyze query type
        query_analysis = await self.query_optimizer.analyze_query(enhanced_query)

        # Create RAG query object
        RAGQuery(
            query_id=query_id,
            original_query=query,
            enhanced_query=enhanced_query,
            query_type=query_analysis["type"],
            user_context=user_context or {},
            metadata_filters=metadata_filters or {},
        )

        # Search with enhanced query
        search_results = await self.search_engine.search(
            query=enhanced_query,
            filters=metadata_filters,
            limit=20,  # Get more for reranking
        )

        # Rerank results
        reranked_results = await self.reranker.rerank_results(
            query=query, results=search_results, top_k=5
        )

        # Extract chunks from results
        chunks = []
        scores = []
        for result in reranked_results:
            # Create chunk from search result
            chunk = DocumentChunk(
                chunk_id=result.metadata.get("chunk_id", str(uuid.uuid4())),
                document_id=result.metadata.get("document_id", "unknown"),
                content=result.content,
                sequence=result.metadata.get("sequence", 0),
                strategy=result.metadata.get("strategy", "unknown"),
                metadata=result.metadata,
            )
            chunks.append(chunk)
            scores.append(result.relevance_score)

        # Build context
        context = await self.context_builder.build_context(chunks, scores, query)

        # Generate response
        response_text = await self._generate_response(query, context)

        # Validate response
        validation_results = await self.response_validator.validate_response(
            response_text, context, query
        )

        # Calculate metrics
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # Count tokens (rough estimate)
        prompt_tokens = len(query) // 4 + context.total_tokens
        response_tokens = len(response_text) // 4
        total_tokens = prompt_tokens + response_tokens

        # Create response object
        rag_response = RAGResponse(
            response_id=str(uuid.uuid4()),
            query_id=query_id,
            response_text=response_text,
            source_chunks=[c.chunk_id for c in context.chunks],
            confidence_score=validation_results["overall_score"],
            generation_model=self.generation_model.value,
            total_tokens_used=total_tokens,
            latency_ms=latency_ms,
            validation_results=validation_results,
        )

        # Cache successful responses
        if validation_results["is_acceptable"]:
            await self.redis_helper.set_json(
                cache_key,
                {
                    "response_id": rag_response.response_id,
                    "query_id": rag_response.query_id,
                    "response_text": rag_response.response_text,
                    "source_chunks": rag_response.source_chunks,
                    "confidence_score": rag_response.confidence_score,
                    "generation_model": rag_response.generation_model,
                    "total_tokens_used": rag_response.total_tokens_used,
                    "latency_ms": rag_response.latency_ms,
                    "validation_results": rag_response.validation_results,
                    "timestamp": rag_response.timestamp.isoformat(),
                },
                self.cache_ttl,
            )

        return rag_response

    async def _generate_response(self, query: str, context: RAGContext) -> str:
        """Generate response using LLM with context"""
        # Build prompt
        context_text = "\n\n".join(
            [
                f"[Source: {chunk.metadata.get('source', 'Unknown')}]\n{chunk.content}"
                for chunk in context.chunks
            ]
        )

        prompt = f"""Answer the following question based on the provided context. Be specific and cite sources where appropriate.

Context:
{context_text}

Question: {query}

Answer:"""

        # Generate response
        response = await self.portkey.complete(
            prompt=prompt,
            model=self.generation_model.value,
            temperature=0.7,
            max_tokens=1000,
        )

        return response.strip()
