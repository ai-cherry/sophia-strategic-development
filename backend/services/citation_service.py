"""
Citation Service

Extracts, validates, and manages citations from LLM responses to provide
transparency and build trust with users.
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """Represents a citation with source information"""
    id: int
    source: str
    title: str
    excerpt: str
    url: Optional[str] = None
    confidence: Optional[float] = None
    type: str = "document"  # document, web, database, api
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if data.get("metadata") is None:
            data.pop("metadata", None)
        return data


class CitationService:
    """Service for managing citations in AI responses"""
    
    def __init__(self):
        self.citation_cache: Dict[str, Citation] = {}  # Cache by hash
        self.citation_stats = {
            "total_citations": 0,
            "verified_citations": 0,
            "invalid_citations": 0,
            "cache_hits": 0,
        }
    
    async def extract_citations(
        self,
        response: str,
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[str, List[Citation]]:
        """
        Extract citations from LLM response.
        
        Args:
            response: LLM response text
            sources: Optional list of source documents used
            
        Returns:
            Tuple of (formatted_response, citations)
        """
        # Extract citation markers from response
        citation_pattern = r'\[cite:([^\]]+)\]'
        citations_found = re.findall(citation_pattern, response)
        
        if not citations_found and not sources:
            # No citations to process
            return response, []
        
        # Process citations
        citations = []
        citation_map = {}
        
        # If sources provided, create citations from them
        if sources:
            for idx, source in enumerate(sources, 1):
                citation = await self._create_citation_from_source(idx, source)
                citations.append(citation)
                # Map source identifiers to citation IDs
                if "id" in source:
                    citation_map[str(source["id"])] = idx
                if "title" in source:
                    citation_map[source["title"]] = idx
        
        # Process inline citations
        for idx, cite_ref in enumerate(citations_found, len(citations) + 1):
            # Check if this references an existing source
            if cite_ref in citation_map:
                continue
            
            # Create new citation
            citation = await self._extract_inline_citation(idx, cite_ref, response)
            citations.append(citation)
            citation_map[cite_ref] = idx
        
        # Format response with numbered citations
        formatted_response = response
        for cite_ref, citation_id in citation_map.items():
            # Replace [cite:reference] with [1], [2], etc.
            pattern = rf'\[cite:{re.escape(cite_ref)}\]'
            formatted_response = re.sub(pattern, f'[{citation_id}]', formatted_response)
        
        # Update statistics
        self.citation_stats["total_citations"] += len(citations)
        
        return formatted_response, citations
    
    async def _create_citation_from_source(
        self,
        citation_id: int,
        source: Dict[str, Any]
    ) -> Citation:
        """Create citation from source document"""
        # Generate cache key
        cache_key = self._generate_cache_key(source)
        
        # Check cache
        if cache_key in self.citation_cache:
            self.citation_stats["cache_hits"] += 1
            cached = self.citation_cache[cache_key]
            cached.id = citation_id  # Update ID for current response
            return cached
        
        # Extract relevant information
        citation = Citation(
            id=citation_id,
            source=source.get("source", "Unknown Source"),
            title=source.get("title", "Untitled"),
            excerpt=self._truncate_excerpt(source.get("content", "")),
            url=source.get("url"),
            confidence=source.get("score", source.get("confidence")),
            type=self._determine_source_type(source),
            metadata={
                "created_at": source.get("created_at"),
                "author": source.get("author"),
                "page": source.get("page"),
            }
        )
        
        # Validate and cache
        if await self._validate_citation(citation):
            self.citation_cache[cache_key] = citation
            self.citation_stats["verified_citations"] += 1
        else:
            self.citation_stats["invalid_citations"] += 1
        
        return citation
    
    async def _extract_inline_citation(
        self,
        citation_id: int,
        reference: str,
        full_response: str
    ) -> Citation:
        """Extract citation from inline reference"""
        # Try to find context around the citation
        context_pattern = rf'([^.]*\[cite:{re.escape(reference)}\][^.]*\.)'
        context_match = re.search(context_pattern, full_response)
        
        excerpt = ""
        if context_match:
            excerpt = context_match.group(1)
            # Clean up the excerpt
            excerpt = re.sub(r'\[cite:[^\]]+\]', '', excerpt).strip()
        
        # Parse reference for metadata
        parts = reference.split(":")
        source = parts[0] if parts else "Unknown"
        title = parts[1] if len(parts) > 1 else reference
        
        citation = Citation(
            id=citation_id,
            source=source,
            title=title,
            excerpt=self._truncate_excerpt(excerpt),
            type="inline",
            confidence=0.8  # Default confidence for inline citations
        )
        
        return citation
    
    def _truncate_excerpt(self, text: str, max_length: int = 200) -> str:
        """Truncate excerpt to reasonable length"""
        if len(text) <= max_length:
            return text
        
        # Find last complete word before limit
        truncated = text[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.8:  # If we're not losing too much
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def _determine_source_type(self, source: Dict[str, Any]) -> str:
        """Determine the type of source"""
        # Check for explicit type
        if "type" in source:
            return source["type"]
        
        # Infer from other fields
        if "url" in source and source["url"]:
            if "http" in source["url"]:
                return "web"
        
        if "table" in source or "database" in source:
            return "database"
        
        if "api" in source or "endpoint" in source:
            return "api"
        
        return "document"
    
    def _generate_cache_key(self, source: Dict[str, Any]) -> str:
        """Generate cache key for source"""
        # Use stable fields for cache key
        key_parts = [
            source.get("source", ""),
            source.get("title", ""),
            source.get("url", ""),
            str(source.get("page", "")),
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _validate_citation(self, citation: Citation) -> bool:
        """Validate citation has minimum required information"""
        # Must have source and title
        if not citation.source or not citation.title:
            return False
        
        # Must have some content
        if not citation.excerpt:
            return False
        
        # URL validation if present
        if citation.url:
            # Basic URL validation
            if not (citation.url.startswith("http") or citation.url.startswith("/")):
                return False
        
        return True
    
    async def verify_citations(
        self,
        citations: List[Citation],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Citation]:
        """
        Verify citations against available sources.
        
        Args:
            citations: List of citations to verify
            context: Optional context with available sources
            
        Returns:
            List of verified citations
        """
        verified_citations = []
        
        for citation in citations:
            # Skip if already verified
            if citation.confidence and citation.confidence > 0.9:
                verified_citations.append(citation)
                continue
            
            # Verify against context if available
            if context and "sources" in context:
                verification_score = await self._verify_against_sources(
                    citation,
                    context["sources"]
                )
                citation.confidence = verification_score
            
            # Only include citations with reasonable confidence
            if citation.confidence and citation.confidence > 0.5:
                verified_citations.append(citation)
                self.citation_stats["verified_citations"] += 1
            else:
                self.citation_stats["invalid_citations"] += 1
                logger.warning(f"Citation failed verification: {citation.title}")
        
        return verified_citations
    
    async def _verify_against_sources(
        self,
        citation: Citation,
        sources: List[Dict[str, Any]]
    ) -> float:
        """Verify citation against known sources"""
        best_score = 0.0
        
        for source in sources:
            score = 0.0
            
            # Title match
            if source.get("title") == citation.title:
                score += 0.4
            elif source.get("title") and citation.title.lower() in source["title"].lower():
                score += 0.2
            
            # Source match
            if source.get("source") == citation.source:
                score += 0.3
            
            # Content match (excerpt in source content)
            if "content" in source and citation.excerpt:
                if citation.excerpt in source["content"]:
                    score += 0.3
                elif any(word in source["content"] for word in citation.excerpt.split()[:5]):
                    score += 0.1
            
            best_score = max(best_score, score)
        
        return best_score
    
    def format_citations_for_display(self, citations: List[Citation]) -> List[Dict[str, Any]]:
        """Format citations for frontend display"""
        return [citation.to_dict() for citation in citations]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get citation service statistics"""
        total = max(self.citation_stats["total_citations"], 1)
        return {
            **self.citation_stats,
            "verification_rate": self.citation_stats["verified_citations"] / total,
            "invalid_rate": self.citation_stats["invalid_citations"] / total,
            "cache_hit_rate": self.citation_stats["cache_hits"] / total,
            "cache_size": len(self.citation_cache),
        } 