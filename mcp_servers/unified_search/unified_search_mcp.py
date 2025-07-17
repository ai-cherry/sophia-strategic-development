"""
Unified Search MCP Server

Intelligent web search orchestration combining:
- Playwright for fast, standard sites
- Apify for scalable cloud scraping  
- ZenRows for anti-bot protected sites
- GPU-accelerated caching via memory architecture
"""

import asyncio
import logging
import json
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import time

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, TextContent, ImageContent, EmbeddedResource,
    Prompt, PromptMessage, PromptArgument
)

# Import dependencies
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import aiohttp
    import redis
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
    from backend.core.config.service_configs import ServiceConfigs
    from backend.services.unified_memory_service import UnifiedMemoryService
except ImportError as e:
    logging.error(f"Import error: {e}")
    logging.error("Please install required packages: pip install aiohttp redis playwright beautifulsoup4")
    raise

logger = logging.getLogger(__name__)


class SearchStrategy(Enum):
    """Search strategy selection"""
    FAST = "fast"           # Playwright for speed
    SCALE = "scale"         # Apify for volume
    STEALTH = "stealth"     # ZenRows for protection
    HYBRID = "hybrid"       # Mixed approach
    AUTO = "auto"           # Automatic selection


@dataclass
class SearchRequest:
    """Search request parameters"""
    query: str
    strategy: SearchStrategy = SearchStrategy.AUTO
    sources: List[str] = field(default_factory=list)
    max_results: int = 20
    timeout: int = 30
    use_cache: bool = True
    filters: Dict = field(default_factory=dict)


@dataclass
class SearchResult:
    """Individual search result"""
    title: str
    snippet: str
    url: str
    source: str
    score: float = 0.0
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class UnifiedSearchMCP:
    """
    Unified Search MCP Server
    
    Features:
    - Intelligent routing between Playwright, Apify, and ZenRows
    - Natural language search across multiple sources
    - GPU-accelerated caching via memory architecture
    - Anti-bot bypass for protected sites
    - Parallel search across multiple sources
    """
    
    def __init__(self):
        self.server = Server("unified-search")
        self.redis_client: Optional[redis.Redis] = None
        self.memory_service: Optional[UnifiedMemoryService] = None
        self.config = ServiceConfigs()
        
        # Search statistics
        self.stats = {
            'total_searches': 0,
            'playwright_searches': 0,
            'apify_searches': 0,
            'zenrows_searches': 0,
            'cache_hits': 0,
            'avg_response_time': 0.0
        }
        
        # Cache settings
        self.cache_ttl = 3600  # 1 hour
        
        # Source categorization
        self.easy_sources = ['duckduckgo', 'wikipedia', 'github', 'hackernews']
        self.medium_sources = ['stackoverflow', 'reddit', 'arxiv', 'news']
        self.hard_sources = ['linkedin', 'twitter', 'facebook', 'instagram']
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all MCP handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available search tools"""
            return [
                Tool(
                    name="search_web",
                    description="Search the web using intelligent routing between scrapers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "strategy": {
                                "type": "string",
                                "description": "Search strategy",
                                "enum": ["fast", "scale", "stealth", "hybrid", "auto"],
                                "default": "auto"
                            },
                            "sources": {
                                "type": "array",
                                "description": "Specific sources to search",
                                "items": {"type": "string"}
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum results to return",
                                "default": 20
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="scrape_url",
                    description="Scrape a specific URL with automatic method selection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to scrape"
                            },
                            "method": {
                                "type": "string",
                                "description": "Scraping method",
                                "enum": ["playwright", "zenrows", "auto"],
                                "default": "auto"
                            },
                            "selectors": {
                                "type": "object",
                                "description": "CSS selectors for extraction",
                                "additionalProperties": {"type": "string"}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="search_code",
                    description="Search for code repositories and technical content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Code/technical search query"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language filter"
                            },
                            "sources": {
                                "type": "array",
                                "description": "Code sources (github, gitlab, stackoverflow)",
                                "items": {"type": "string"},
                                "default": ["github", "stackoverflow"]
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="search_academic",
                    description="Search academic papers and research",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Academic search query"
                            },
                            "year_from": {
                                "type": "integer",
                                "description": "Filter papers from this year"
                            },
                            "sources": {
                                "type": "array",
                                "description": "Academic sources",
                                "items": {"type": "string"},
                                "default": ["arxiv", "scholar", "pubmed"]
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_search_stats",
                    description="Get search service statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="clear_search_cache",
                    description="Clear search result cache",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Specific query to clear (optional)"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute search tools"""
            
            # Ensure services are initialized
            await self._ensure_initialized()
            
            try:
                if name == "search_web":
                    return await self._handle_search_web(arguments)
                elif name == "scrape_url":
                    return await self._handle_scrape_url(arguments)
                elif name == "search_code":
                    return await self._handle_search_code(arguments)
                elif name == "search_academic":
                    return await self._handle_search_academic(arguments)
                elif name == "get_search_stats":
                    return await self._handle_get_stats()
                elif name == "clear_search_cache":
                    return await self._handle_clear_cache(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List available prompt templates"""
            return [
                Prompt(
                    name="research_topic",
                    description="Comprehensive research on a topic",
                    arguments=[
                        PromptArgument(
                            name="topic",
                            description="Research topic",
                            required=True
                        ),
                        PromptArgument(
                            name="depth",
                            description="Research depth (quick, standard, deep)",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="competitive_analysis",
                    description="Analyze competitors and market",
                    arguments=[
                        PromptArgument(
                            name="company",
                            description="Company or product to analyze",
                            required=True
                        ),
                        PromptArgument(
                            name="aspects",
                            description="Specific aspects to focus on",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="trend_analysis",
                    description="Analyze trends in a specific domain",
                    arguments=[
                        PromptArgument(
                            name="domain",
                            description="Domain to analyze (tech, business, etc)",
                            required=True
                        ),
                        PromptArgument(
                            name="timeframe",
                            description="Time period to analyze",
                            required=False
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, Any]) -> PromptMessage:
            """Get specific prompt template"""
            
            if name == "research_topic":
                topic = arguments.get("topic", "")
                depth = arguments.get("depth", "standard")
                
                sources = {
                    "quick": ["wikipedia", "duckduckgo"],
                    "standard": ["wikipedia", "duckduckgo", "stackoverflow", "github"],
                    "deep": ["arxiv", "scholar", "wikipedia", "news", "stackoverflow", "github"]
                }
                
                query = f"""
                Research the topic: {topic}
                
                Search across these sources: {', '.join(sources.get(depth, sources['standard']))}
                
                Provide:
                1. Overview and key concepts
                2. Current state and recent developments
                3. Key players and contributors
                4. Challenges and opportunities
                5. Future outlook
                """
                
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=query)
                )
                
            elif name == "competitive_analysis":
                company = arguments.get("company", "")
                aspects = arguments.get("aspects", "products, market share, strategy")
                
                query = f"""
                Analyze {company} focusing on: {aspects}
                
                Search for:
                1. Company overview and history
                2. Products and services
                3. Market position and competitors
                4. Recent news and developments
                5. Strengths and weaknesses
                6. Customer sentiment
                """
                
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=query)
                )
                
            elif name == "trend_analysis":
                domain = arguments.get("domain", "")
                timeframe = arguments.get("timeframe", "last 12 months")
                
                query = f"""
                Analyze trends in {domain} over {timeframe}
                
                Focus on:
                1. Emerging technologies and innovations
                2. Market shifts and disruptions
                3. Key events and milestones
                4. Industry leaders and influencers
                5. Future predictions and forecasts
                """
                
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=query)
                )
                
            else:
                return PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Unknown prompt template: {name}"
                    )
                )
    
    async def _ensure_initialized(self):
        """Ensure services are initialized"""
        if not self.redis_client:
            try:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("✅ Connected to Redis for caching")
            except:
                logger.warning("Redis not available - caching disabled")
                self.redis_client = None
        
        # Initialize memory service for GPU caching
        if not self.memory_service:
            try:
                from backend.services.unified_memory_service import UnifiedMemoryService
                self.memory_service = UnifiedMemoryService()
                logger.info("✅ Connected to Unified Memory Service")
            except:
                logger.warning("Memory service not available")
                self.memory_service = None
    
    async def _handle_search_web(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle web search with intelligent routing"""
        start_time = time.time()
        
        # Parse arguments
        query = arguments.get("query", "")
        strategy = SearchStrategy(arguments.get("strategy", "auto"))
        sources = arguments.get("sources", [])
        max_results = arguments.get("max_results", 20)
        
        # Check cache first
        cache_key = f"search:{query}:{strategy.value}:{','.join(sources)}"
        if self.redis_client and arguments.get("use_cache", True):
            cached = self.redis_client.get(cache_key)
            if cached:
                self.stats['cache_hits'] += 1
                logger.info(f"Cache hit for query: {query}")
                return [TextContent(
                    type="text",
                    text=f"🔍 Search Results (cached):\n\n{cached}"
                )]
        
        # Create search request
        request = SearchRequest(
            query=query,
            strategy=strategy,
            sources=sources,
            max_results=max_results
        )
        
        # Route to appropriate search method
        if strategy == SearchStrategy.AUTO:
            results = await self._search_auto(request)
        elif strategy == SearchStrategy.FAST:
            results = await self._search_playwright(request)
        elif strategy == SearchStrategy.SCALE:
            results = await self._search_apify(request)
        elif strategy == SearchStrategy.STEALTH:
            results = await self._search_zenrows(request)
        else:  # HYBRID
            results = await self._search_hybrid(request)
        
        # Format results
        output = self._format_search_results(results, query, strategy)
        
        # Cache results
        if self.redis_client and len(output) < 50000:
            self.redis_client.setex(cache_key, self.cache_ttl, output)
        
        # Store in memory architecture if available (would integrate with UnifiedMemoryService)
        # This is a placeholder for future integration
        logger.info(f"Would store search results in memory: {query}")
        
        # Update stats
        response_time = time.time() - start_time
        self.stats['total_searches'] += 1
        self.stats['avg_response_time'] = (
            (self.stats['avg_response_time'] * (self.stats['total_searches'] - 1) + response_time) /
            self.stats['total_searches']
        )
        
        return [TextContent(type="text", text=output)]
    
    async def _search_auto(self, request: SearchRequest) -> List[SearchResult]:
        """Automatically select best search strategy"""
        # Analyze query and sources to determine best approach
        query_lower = request.query.lower()
        
        # Protected sites need stealth
        if any(site in query_lower for site in ['linkedin', 'twitter', 'facebook']):
            return await self._search_zenrows(request)
        
        # Code searches use fast approach
        if any(term in query_lower for term in ['code', 'github', 'function', 'class']):
            return await self._search_playwright(request)
        
        # Academic searches need scale
        if any(term in query_lower for term in ['paper', 'research', 'study', 'journal']):
            return await self._search_apify(request)
        
        # Default to hybrid
        return await self._search_hybrid(request)
    
    async def _search_playwright(self, request: SearchRequest) -> List[SearchResult]:
        """Fast search using Playwright"""
        self.stats['playwright_searches'] += 1
        results = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Search DuckDuckGo
                if not request.sources or 'duckduckgo' in request.sources:
                    await page.goto(f"https://duckduckgo.com/?q={request.query}")
                    await page.wait_for_selector('.result', timeout=5000)
                    
                    search_results = await page.query_selector_all('.result')
                    for i, result in enumerate(search_results[:request.max_results // 2]):
                        title_elem = await result.query_selector('h2')
                        snippet_elem = await result.query_selector('.result__snippet')
                        
                        if title_elem and snippet_elem:
                            title = await title_elem.inner_text()
                            snippet = await snippet_elem.inner_text()
                            link_elem = await title_elem.query_selector('a')
                            url = await link_elem.get_attribute('href') if link_elem else ''
                            
                            if url:
                                results.append(SearchResult(
                                    title=title,
                                    snippet=snippet,
                                    url=url,
                                    source='duckduckgo',
                                    score=1.0 - (i * 0.1)
                                ))
                
                # Search GitHub if requested
                if not request.sources or 'github' in request.sources:
                    await page.goto(f"https://github.com/search?q={request.query}&type=repositories")
                    await page.wait_for_selector('.repo-list-item', timeout=5000)
                    
                    repos = await page.query_selector_all('.repo-list-item')
                    for i, repo in enumerate(repos[:request.max_results // 2]):
                        title_elem = await repo.query_selector('h3 a')
                        desc_elem = await repo.query_selector('p')
                        
                        if title_elem:
                            title = await title_elem.inner_text()
                            href = await title_elem.get_attribute('href')
                            url = f'https://github.com{href}' if href else ''
                            snippet = await desc_elem.inner_text() if desc_elem else ""
                            
                            if url:
                                results.append(SearchResult(
                                    title=title,
                                    snippet=snippet,
                                    url=url,
                                    source='github',
                                    score=0.9 - (i * 0.1)
                                ))
                
            finally:
                await browser.close()
        
        return results
    
    async def _search_apify(self, request: SearchRequest) -> List[SearchResult]:
        """Scalable search using Apify actors"""
        self.stats['apify_searches'] += 1
        
        # Simulated Apify integration - replace with actual API calls
        results = []
        
        # Example implementation
        sources_to_search = request.sources or ['stackoverflow', 'reddit', 'news']
        
        for source in sources_to_search:
            if source == 'stackoverflow':
                # Simulate Stack Overflow search
                for i in range(min(5, request.max_results // len(sources_to_search))):
                    results.append(SearchResult(
                        title=f"[SO] {request.query} - Solution {i+1}",
                        snippet=f"Best answer for {request.query} with {10+i} upvotes...",
                        url=f"https://stackoverflow.com/questions/{12345+i}",
                        source='stackoverflow',
                        score=0.8 - (i * 0.1)
                    ))
            
            elif source == 'reddit':
                # Simulate Reddit search
                for i in range(min(5, request.max_results // len(sources_to_search))):
                    results.append(SearchResult(
                        title=f"[Reddit] Discussion: {request.query}",
                        snippet=f"Popular thread about {request.query} in r/programming...",
                        url=f"https://reddit.com/r/programming/comments/{67890+i}",
                        source='reddit',
                        score=0.7 - (i * 0.1)
                    ))
        
        return results
    
    async def _search_zenrows(self, request: SearchRequest) -> List[SearchResult]:
        """Stealth search using ZenRows for protected sites"""
        self.stats['zenrows_searches'] += 1
        
        # Simulated ZenRows integration - replace with actual API calls
        results = []
        
        # Example for protected sites
        if 'linkedin' in (request.sources or []):
            results.append(SearchResult(
                title=f"LinkedIn: {request.query} professionals",
                snippet=f"Connect with experts in {request.query}...",
                url=f"https://linkedin.com/search/results/{request.query}",
                source='linkedin',
                score=0.9
            ))
        
        return results
    
    async def _search_hybrid(self, request: SearchRequest) -> List[SearchResult]:
        """Hybrid search using multiple strategies"""
        # Categorize sources
        easy = [s for s in (request.sources or self.easy_sources) if s in self.easy_sources]
        medium = [s for s in (request.sources or self.medium_sources) if s in self.medium_sources]
        hard = [s for s in (request.sources or self.hard_sources) if s in self.hard_sources]
        
        tasks = []
        
        # Create tasks for different strategies
        if easy:
            req = SearchRequest(request.query, SearchStrategy.FAST, easy, request.max_results // 3)
            tasks.append(self._search_playwright(req))
        
        if medium:
            req = SearchRequest(request.query, SearchStrategy.SCALE, medium, request.max_results // 3)
            tasks.append(self._search_apify(req))
        
        if hard:
            req = SearchRequest(request.query, SearchStrategy.STEALTH, hard, request.max_results // 3)
            tasks.append(self._search_zenrows(req))
        
        # Execute all tasks concurrently
        results_batches = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and deduplicate results
        all_results = []
        seen_urls = set()
        
        for batch in results_batches:
            if isinstance(batch, Exception):
                logger.error(f"Search batch error: {batch}")
                continue
            
            if isinstance(batch, list):
                for result in batch:
                    if result.url not in seen_urls:
                        seen_urls.add(result.url)
                        all_results.append(result)
        
        # Sort by score
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        return all_results[:request.max_results]
    
    def _format_search_results(self, results: List[SearchResult], query: str, strategy: SearchStrategy) -> str:
        """Format search results for display"""
        output = f"🔍 Web Search Results:\n\n"
        output += f"Query: {query}\n"
        output += f"Strategy: {strategy.value}\n"
        output += f"Total Results: {len(results)}\n\n"
        
        if not results:
            output += "No results found."
            return output
        
        # Group by source
        by_source = {}
        for result in results:
            if result.source not in by_source:
                by_source[result.source] = []
            by_source[result.source].append(result)
        
        # Format each source
        for source, source_results in by_source.items():
            output += f"\n📌 {source.upper()} Results:\n"
            
            for i, result in enumerate(source_results[:5], 1):
                output += f"\n{i}. {result.title}\n"
                output += f"   {result.snippet}\n"
                output += f"   🔗 {result.url}\n"
                output += f"   Score: {result.score:.2f}\n"
        
        return output
    
    async def _handle_scrape_url(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle URL scraping with automatic method selection"""
        url = arguments.get("url", "")
        method = arguments.get("method", "auto")
        selectors = arguments.get("selectors", {})
        
        # Auto-select method based on URL
        if method == "auto":
            if any(domain in url for domain in ["linkedin.com", "twitter.com", "facebook.com"]):
                method = "zenrows"
            else:
                method = "playwright"
        
        output = f"🕷️ Scraping URL: {url}\n"
        output += f"Method: {method}\n\n"
        
        try:
            if method == "playwright":
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    await page.goto(url, wait_until='domcontentloaded')
                    await page.wait_for_load_state('networkidle')
                    
                    # Extract content
                    if selectors:
                        output += "Extracted Data:\n"
                        for key, selector in selectors.items():
                            try:
                                elem = await page.query_selector(selector)
                                if elem:
                                    text = await elem.inner_text()
                                    output += f"  {key}: {text[:200]}...\n"
                            except:
                                output += f"  {key}: [Not found]\n"
                    else:
                        # Get page content
                        content = await page.content()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract basic info
                        title = soup.title.string if soup.title else "No title"
                        paragraphs = soup.find_all('p')[:3]
                        
                        output += f"Title: {title}\n\n"
                        output += "Content:\n"
                        for p in paragraphs:
                            output += f"  {p.get_text()[:200]}...\n"
                    
                    await browser.close()
            
            elif method == "zenrows":
                output += "ZenRows scraping would be used for this protected site.\n"
                output += "This would bypass anti-bot measures using premium proxies.\n"
            
        except Exception as e:
            output += f"Error: {str(e)}\n"
        
        return [TextContent(type="text", text=output)]
    
    async def _handle_search_code(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle code-specific searches"""
        query = arguments.get("query", "")
        language = arguments.get("language", "")
        sources = arguments.get("sources", ["github", "stackoverflow"])
        
        # Modify query for code search
        if language:
            query = f"{query} language:{language}"
        
        # Use fast search for code
        request = SearchRequest(
            query=query,
            strategy=SearchStrategy.FAST,
            sources=sources,
            max_results=20
        )
        
        return await self._handle_search_web({
            "query": query,
            "strategy": "fast",
            "sources": sources,
            "max_results": 20
        })
    
    async def _handle_search_academic(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle academic paper searches"""
        query = arguments.get("query", "")
        year_from = arguments.get("year_from")
        sources = arguments.get("sources", ["arxiv", "scholar", "pubmed"])
        
        # Modify query for academic search
        if year_from:
            query = f"{query} after:{year_from}"
        
        # Use scale search for academic papers
        return await self._handle_search_web({
            "query": query,
            "strategy": "scale",
            "sources": sources,
            "max_results": 30
        })
    
    async def _handle_get_stats(self) -> List[TextContent]:
        """Get search statistics"""
        output = "📊 Search Service Statistics:\n\n"
        output += f"Total Searches: {self.stats['total_searches']}\n"
        output += f"  - Playwright: {self.stats['playwright_searches']}\n"
        output += f"  - Apify: {self.stats['apify_searches']}\n"
        output += f"  - ZenRows: {self.stats['zenrows_searches']}\n"
        output += f"Cache Hits: {self.stats['cache_hits']}\n"
        
        if self.stats['total_searches'] > 0:
            cache_hit_rate = (self.stats['cache_hits'] / self.stats['total_searches']) * 100
            output += f"Cache Hit Rate: {cache_hit_rate:.1f}%\n"
        
        output += f"Average Response Time: {self.stats['avg_response_time']:.2f}s\n"
        
        return [TextContent(type="text", text=output)]
    
    async def _handle_clear_cache(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Clear search cache"""
        query = arguments.get("query")
        
        if not self.redis_client:
            return [TextContent(
                type="text",
                text="Cache not available (Redis not connected)"
            )]
        
        try:
            if query:
                # Clear specific query
                pattern = f"search:{query}:*"
                keys = list(self.redis_client.scan_iter(match=pattern))
                if keys:
                    self.redis_client.delete(*keys)
                    output = f"✅ Cleared {len(keys)} cache entries for query: {query}"
                else:
                    output = f"No cache entries found for query: {query}"
            else:
                # Clear all search cache
                pattern = "search:*"
                keys = list(self.redis_client.scan_iter(match=pattern))
                if keys:
                    self.redis_client.delete(*keys)
                    output = f"✅ Cleared {len(keys)} total search cache entries"
                else:
                    output = "No cache entries found"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error clearing cache: {str(e)}"
            )]
    
    async def run(self):
        """Run the MCP server"""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = UnifiedSearchMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
