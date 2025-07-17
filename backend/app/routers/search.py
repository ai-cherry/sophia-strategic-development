"""
Search API Router

Connects the frontend search interface to the Unified Search MCP server
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
from datetime import datetime

# Import MCP client utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.auth import get_current_user
from backend.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    """Web search request"""
    query: str = Field(..., description="Search query")
    strategy: str = Field("auto", description="Search strategy: auto, fast, scale, stealth, hybrid")
    sources: Optional[List[str]] = Field(None, description="Specific sources to search")
    max_results: int = Field(20, description="Maximum results to return")
    use_cache: bool = Field(True, description="Whether to use cached results")


class CodeSearchRequest(BaseModel):
    """Code search request"""
    query: str = Field(..., description="Code search query")
    language: Optional[str] = Field(None, description="Programming language filter")
    sources: List[str] = Field(default_factory=lambda: ["github", "stackoverflow"])
    max_results: int = Field(20, description="Maximum results")


class AcademicSearchRequest(BaseModel):
    """Academic search request"""
    query: str = Field(..., description="Academic search query")
    year_from: Optional[int] = Field(None, description="Filter papers from this year")
    sources: List[str] = Field(default_factory=lambda: ["arxiv", "scholar", "pubmed"])
    max_results: int = Field(30, description="Maximum results")


class SearchResult(BaseModel):
    """Individual search result"""
    title: str
    snippet: str
    url: str
    source: str
    score: float
    timestamp: Optional[datetime] = None


class SearchResponse(BaseModel):
    """Search response"""
    success: bool
    results: List[SearchResult]
    response_time: float
    strategy_used: str
    total_results: int
    error: Optional[str] = None


class SearchStats(BaseModel):
    """Search statistics"""
    total_searches: int
    playwright_searches: int
    apify_searches: int
    zenrows_searches: int
    cache_hits: int
    avg_response_time: float


class UnifiedSearchClient:
    """Client for interacting with the Unified Search MCP server"""
    
    def __init__(self):
        self.server_url = "http://localhost:3020"  # Unified Search MCP server
        self._stats_cache = None
        self._stats_cache_time = None
        self._cache_duration = 30  # seconds
    
    async def search_web(self, request: SearchRequest) -> SearchResponse:
        """Execute web search"""
        try:
            # In production, this would call the MCP server
            # For now, return mock data
            logger.info(f"Web search: {request.query} with strategy {request.strategy}")
            
            # Simulate search results
            results = []
            
            if "playwright" in request.query.lower():
                results.append(SearchResult(
                    title="Playwright: Fast, reliable end-to-end testing",
                    snippet="Playwright enables reliable end-to-end testing for modern web apps across all browsers...",
                    url="https://playwright.dev",
                    source="duckduckgo",
                    score=0.95
                ))
                results.append(SearchResult(
                    title="microsoft/playwright - GitHub",
                    snippet="Playwright is a framework for Web Testing and Automation. It allows testing across all modern browsers...",
                    url="https://github.com/microsoft/playwright",
                    source="github",
                    score=0.92
                ))
            
            if "apify" in request.query.lower():
                results.append(SearchResult(
                    title="Apify: Web Scraping and Automation Platform",
                    snippet="Build, deploy and monitor web scrapers at scale. Extract data from any website...",
                    url="https://apify.com",
                    source="duckduckgo",
                    score=0.90
                ))
            
            if "zenrows" in request.query.lower():
                results.append(SearchResult(
                    title="ZenRows: Web Scraping API",
                    snippet="The easiest way to extract data from any website. Handle anti-bot protection...",
                    url="https://zenrows.com",
                    source="duckduckgo",
                    score=0.88
                ))
            
            # Default results if no specific match
            if not results:
                results = [
                    SearchResult(
                        title=f"Result for: {request.query}",
                        snippet=f"This is a sample search result for your query about {request.query}...",
                        url=f"https://example.com/search?q={request.query}",
                        source="duckduckgo",
                        score=0.8 - (i * 0.1)
                    )
                    for i in range(min(5, request.max_results))
                ]
            
            return SearchResponse(
                success=True,
                results=results[:request.max_results],
                response_time=0.342,  # Mock response time
                strategy_used=request.strategy,
                total_results=len(results)
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return SearchResponse(
                success=False,
                results=[],
                response_time=0,
                strategy_used=request.strategy,
                total_results=0,
                error=str(e)
            )
    
    async def search_code(self, request: CodeSearchRequest) -> SearchResponse:
        """Execute code search"""
        try:
            logger.info(f"Code search: {request.query}")
            
            # Mock code search results
            results = [
                SearchResult(
                    title=f"Code example: {request.query}",
                    snippet=f"```python\n# Example implementation of {request.query}\ndef example():\n    pass\n```",
                    url=f"https://github.com/example/{request.query}",
                    source="github",
                    score=0.9
                ),
                SearchResult(
                    title=f"How to implement {request.query} in Python",
                    snippet=f"Here's the best way to implement {request.query} with proper error handling...",
                    url=f"https://stackoverflow.com/questions/123456/{request.query}",
                    source="stackoverflow",
                    score=0.85
                )
            ]
            
            return SearchResponse(
                success=True,
                results=results[:request.max_results],
                response_time=0.287,
                strategy_used="fast",
                total_results=len(results)
            )
            
        except Exception as e:
            logger.error(f"Code search error: {e}")
            return SearchResponse(
                success=False,
                results=[],
                response_time=0,
                strategy_used="fast",
                total_results=0,
                error=str(e)
            )
    
    async def search_academic(self, request: AcademicSearchRequest) -> SearchResponse:
        """Execute academic search"""
        try:
            logger.info(f"Academic search: {request.query}")
            
            # Mock academic search results
            results = [
                SearchResult(
                    title=f"Survey on {request.query}: Recent Advances and Future Directions",
                    snippet=f"This paper provides a comprehensive survey of recent advances in {request.query}...",
                    url=f"https://arxiv.org/abs/2024.12345",
                    source="arxiv",
                    score=0.93
                ),
                SearchResult(
                    title=f"Deep Learning Approaches to {request.query}",
                    snippet=f"We present a novel deep learning architecture for {request.query} that achieves state-of-the-art...",
                    url=f"https://arxiv.org/abs/2024.67890",
                    source="arxiv",
                    score=0.89
                )
            ]
            
            return SearchResponse(
                success=True,
                results=results[:request.max_results],
                response_time=0.523,
                strategy_used="scale",
                total_results=len(results)
            )
            
        except Exception as e:
            logger.error(f"Academic search error: {e}")
            return SearchResponse(
                success=False,
                results=[],
                response_time=0,
                strategy_used="scale",
                total_results=0,
                error=str(e)
            )
    
    async def get_stats(self) -> SearchStats:
        """Get search statistics"""
        try:
            # Check cache
            import time
            current_time = time.time()
            
            if (self._stats_cache and 
                self._stats_cache_time and 
                current_time - self._stats_cache_time < self._cache_duration):
                return self._stats_cache
            
            # Mock statistics
            stats = SearchStats(
                total_searches=142,
                playwright_searches=67,
                apify_searches=43,
                zenrows_searches=32,
                cache_hits=89,
                avg_response_time=0.387
            )
            
            # Update cache
            self._stats_cache = stats
            self._stats_cache_time = current_time
            
            return stats
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            # Return empty stats on error
            return SearchStats(
                total_searches=0,
                playwright_searches=0,
                apify_searches=0,
                zenrows_searches=0,
                cache_hits=0,
                avg_response_time=0
            )


# Initialize search client
search_client = UnifiedSearchClient()


@router.post("/web", response_model=SearchResponse)
async def search_web(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Execute web search with intelligent routing
    
    Strategies:
    - auto: Automatically select best strategy
    - fast: Use Playwright for speed
    - scale: Use Apify for volume
    - stealth: Use ZenRows for protected sites
    - hybrid: Use multiple strategies
    """
    logger.info(f"User {current_user.email} searching: {request.query}")
    
    # Execute search
    response = await search_client.search_web(request)
    
    # Log search in background
    background_tasks.add_task(
        log_search_activity,
        user_id=current_user.id,
        query=request.query,
        strategy=request.strategy,
        results_count=response.total_results
    )
    
    return response


@router.post("/code", response_model=SearchResponse)
async def search_code(
    request: CodeSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Search for code repositories and examples"""
    logger.info(f"User {current_user.email} code search: {request.query}")
    
    return await search_client.search_code(request)


@router.post("/academic", response_model=SearchResponse)
async def search_academic(
    request: AcademicSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Search academic papers and research"""
    logger.info(f"User {current_user.email} academic search: {request.query}")
    
    return await search_client.search_academic(request)


@router.get("/stats", response_model=SearchStats)
async def get_search_stats(
    current_user: User = Depends(get_current_user)
):
    """Get search service statistics"""
    return await search_client.get_stats()


@router.delete("/cache")
async def clear_search_cache(
    query: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Clear search cache
    
    - If query provided, clear only that query's cache
    - Otherwise clear all search cache
    """
    logger.info(f"User {current_user.email} clearing cache for query: {query or 'all'}")
    
    # In production, this would call the MCP server to clear cache
    return {
        "success": True,
        "message": f"Cache cleared for: {query or 'all searches'}"
    }


async def log_search_activity(
    user_id: int,
    query: str,
    strategy: str,
    results_count: int
):
    """Log search activity for analytics"""
    try:
        # In production, this would save to database
        logger.info(f"Search activity: user={user_id}, query={query}, "
                   f"strategy={strategy}, results={results_count}")
    except Exception as e:
        logger.error(f"Failed to log search activity: {e}")
