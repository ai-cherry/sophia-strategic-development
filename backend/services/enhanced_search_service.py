"""
Enhanced Search Service - Multi-Tier LLM Orchestration with Advanced Search
Provides three tiers of search capability:
- Tier 1: <2s (Fast, basic search)
- Tier 2: <30s (Deep search with context)
- Tier 3: <5min (Deep deep search with analysis)
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import aiohttp
from playwright.async_api import Browser, Page, async_playwright

from backend.core.auto_esc_config import get_config_value
from backend.services.ai_memory_service import AIMemoryService
from backend.services.QDRANT_memory_service import QdrantUnifiedMemoryService
from infrastructure.services.unified_ai_orchestrator import (
    AIRequest,
    UnifiedAIOrchestrator,
)

logger = logging.getLogger(__name__)


class SearchTier(Enum):
    """Search tier enumeration"""

    TIER_1 = "tier_1"  # <2s - Fast search
    TIER_2 = "tier_2"  # <30s - Deep search
    TIER_3 = "tier_3"  # <5min - Deep deep search


class SearchProvider(Enum):
    """Search provider enumeration"""

    BRAVE = "brave"
    SEARXNG = "searxng"
    PERPLEXITY = "perplexity"
    BROWSER = "browser"
    INTERNAL = "internal"


@dataclass
class SearchRequest:
    """Search request configuration"""

    query: str
    tier: SearchTier
    providers: list[SearchProvider] = field(default_factory=list)
    max_results: int = 10
    include_context: bool = True
    user_id: str = "anonymous"
    session_id: str = "default"
    time_range: tuple[datetime, datetime] | None = None
    search_domains: list[str] = field(default_factory=list)
    exclude_domains: list[str] = field(default_factory=list)
    language: str = "en"
    safe_search: bool = True


@dataclass
class SearchResult:
    """Search result from a single provider"""

    provider: SearchProvider
    results: list[dict[str, Any]]
    metadata: dict[str, Any]
    processing_time: float
    confidence: float
    citations: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class CacheEntry:
    """Cache entry for semantic caching"""

    query: str
    results: list[SearchResult]
    timestamp: datetime
    tier: SearchTier
    ttl: int
    metadata: dict[str, Any]


class SemanticCache:
    """4-layer semantic caching system"""

    def __init__(self, cortex_service: QdrantUnifiedMemoryService):
        self.cortex = cortex_service
        self.l1_cache: dict[str, CacheEntry] = {}  # Memory cache
        self.l2_cache: dict[str, CacheEntry] = {}  # Session cache
        self.l3_cache: dict[str, CacheEntry] = {}  # User cache
        self.l4_cache: dict[str, CacheEntry] = {}  # Global cache

        # Cache TTL configurations (in seconds)
        self.cache_ttl = {
            SearchTier.TIER_1: 300,  # 5 minutes
            SearchTier.TIER_2: 1800,  # 30 minutes
            SearchTier.TIER_3: 7200,  # 2 hours
        }

    async def get_cached_result(
        self, query: str, tier: SearchTier, user_id: str, session_id: str
    ) -> list[SearchResult] | None:
        """Get cached result using semantic similarity"""

        # Check each cache layer in order
        cache_layers = [
            (self.l1_cache, "L1_MEMORY"),
            (self.l2_cache, f"L2_SESSION_{session_id}"),
            (self.l3_cache, f"L3_USER_{user_id}"),
            (self.l4_cache, "L4_GLOBAL"),
        ]

        for cache, cache_name in cache_layers:
            result = await self._check_cache_layer(cache, query, tier, cache_name)
            if result:
                logger.info(f"Cache hit: {cache_name} for query: {query[:50]}...")
                return result

        return None

    async def _check_cache_layer(
        self,
        cache: dict[str, CacheEntry],
        query: str,
        tier: SearchTier,
        cache_name: str,
    ) -> list[SearchResult] | None:
        """Check a specific cache layer"""

        # Direct hit check
        if query in cache:
            entry = cache[query]
            if not self._is_expired(entry):
                return entry.results

        # Semantic similarity check
        for cached_query, entry in cache.items():
            if self._is_expired(entry):
                continue

            similarity = await self._calculate_semantic_similarity(query, cached_query)
            if similarity > 0.85:  # High similarity threshold
                logger.info(f"Semantic cache hit: {similarity:.2f} similarity")
                return entry.results

        return None

    async def _calculate_semantic_similarity(self, query1: str, query2: str) -> float:
        """Calculate semantic similarity between queries"""
        try:
            # Use Lambda GPU for semantic similarity
            similarity = await self.cortex.calculate_similarity(query1, query2)
            return similarity
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() - entry.timestamp > timedelta(seconds=entry.ttl)

    async def cache_result(
        self,
        query: str,
        results: list[SearchResult],
        tier: SearchTier,
        user_id: str,
        session_id: str,
        metadata: dict[str, Any] = None,
    ) -> None:
        """Cache search results across all layers"""

        entry = CacheEntry(
            query=query,
            results=results,
            timestamp=datetime.utcnow(),
            tier=tier,
            ttl=self.cache_ttl[tier],
            metadata=metadata or {},
        )

        # Store in all cache layers
        self.l1_cache[query] = entry
        self.l2_cache[f"{session_id}_{query}"] = entry
        self.l3_cache[f"{user_id}_{query}"] = entry
        self.l4_cache[query] = entry

        # Clean up expired entries
        await self._cleanup_expired_entries()

    async def _cleanup_expired_entries(self) -> None:
        """Clean up expired cache entries"""
        for cache in [self.l1_cache, self.l2_cache, self.l3_cache, self.l4_cache]:
            expired_keys = [
                key for key, entry in cache.items() if self._is_expired(entry)
            ]
            for key in expired_keys:
                del cache[key]


class BrowserAutomationService:
    """Browser automation service using Playwright"""

    def __init__(self):
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.playwright = None

    async def initialize(self) -> None:
        """Initialize browser automation"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--window-size=1920,1080",
                ],
            )
            self.page = await self.browser.new_page()

            # Set user agent
            await self.page.set_user_agent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )

            logger.info("Browser automation initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser automation: {e}")
            raise

    async def search_with_browser(
        self, query: str, max_results: int = 10, domains: list[str] = None
    ) -> list[dict[str, Any]]:
        """Perform search using browser automation"""

        if not self.page:
            await self.initialize()

        try:
            # Navigate to search engine
            await self.page.goto("https://www.google.com", wait_until="networkidle")

            # Accept cookies if needed
            try:
                await self.page.click('button[id="L2AGLb"]', timeout=3000)
            except:
                pass  # Cookie button might not be present

            # Enter search query
            await self.page.fill('input[name="q"]', query)
            await self.page.press('input[name="q"]', "Enter")

            # Wait for results
            await self.page.wait_for_selector('div[id="search"]', timeout=10000)

            # Extract search results
            results = []
            search_results = await self.page.query_selector_all("div.g")

            for i, result in enumerate(search_results[:max_results]):
                try:
                    # Extract title
                    title_element = await result.query_selector("h3")
                    title = (
                        await title_element.inner_text()
                        if title_element
                        else "No title"
                    )

                    # Extract URL
                    link_element = await result.query_selector("a")
                    url = (
                        await link_element.get_attribute("href") if link_element else ""
                    )

                    # Extract snippet
                    snippet_element = await result.query_selector("span[data-ved]")
                    snippet = (
                        await snippet_element.inner_text() if snippet_element else ""
                    )

                    # Filter by domains if specified
                    if domains and not any(domain in url for domain in domains):
                        continue

                    results.append(
                        {
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "rank": i + 1,
                            "source": "browser_search",
                        }
                    )

                except Exception as e:
                    logger.warning(f"Error extracting result {i}: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Browser search failed: {e}")
            return []

    async def extract_page_content(self, url: str) -> dict[str, Any]:
        """Extract content from a specific page"""

        if not self.page:
            await self.initialize()

        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)

            # Extract page content
            content = await self.page.evaluate(
                """
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style');
                    scripts.forEach(el => el.remove());

                    // Get main content
                    const main = document.querySelector('main') || document.body;

                    return {
                        title: document.title,
                        text: main.innerText.trim(),
                        headings: Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.innerText.trim()),
                        links: Array.from(document.querySelectorAll('a')).slice(0, 20).map(a => ({
                            text: a.innerText.trim(),
                            href: a.href
                        }))
                    };
                }
            """
            )

            return {
                "url": url,
                "title": content.get("title", ""),
                "text": content.get("text", "")[:5000],  # Limit text length
                "headings": content.get("headings", []),
                "links": content.get("links", []),
                "extracted_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {e}")
            return {"url": url, "error": str(e)}

    async def cleanup(self) -> None:
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error cleaning up browser: {e}")


class EnhancedSearchService:
    """Enhanced search service with multi-tier LLM orchestration"""

    def __init__(self):
        self.cortex = UnifiedMemoryService()
        self.ai_memory = AIMemoryService()
        self.ai_orchestrator = UnifiedAIOrchestrator()
        self.semantic_cache = SemanticCache(self.cortex)
        self.browser_service = BrowserAutomationService()

        # API keys
        self.brave_api_key = get_config_value("brave_search_api_key")
        self.perplexity_api_key = get_config_value("perplexity_api_key")
        self.searxng_endpoint = get_config_value(
            "searxng_endpoint", "https://search.sapti.me"
        )

    async def search(
        self, request: SearchRequest
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Main search method with real-time streaming"""

        start_time = datetime.utcnow()

        # Yield initial status
        yield {
            "type": "status",
            "message": f"Starting {request.tier.value} search...",
            "timestamp": start_time.isoformat(),
        }

        # Check cache first
        cached_results = await self.semantic_cache.get_cached_result(
            request.query, request.tier, request.user_id, request.session_id
        )

        if cached_results:
            yield {
                "type": "cache_hit",
                "message": "Found cached results",
                "timestamp": datetime.utcnow().isoformat(),
            }

            for result in cached_results:
                yield {
                    "type": "result",
                    "provider": result.provider.value,
                    "data": result.results,
                    "metadata": result.metadata,
                    "cached": True,
                }
            return

        # Determine search providers based on tier
        providers = await self._determine_providers(request)

        # Execute searches in parallel
        search_tasks = []
        for provider in providers:
            task = self._execute_provider_search(provider, request)
            search_tasks.append(task)

        # Process results as they come in
        completed_results = []
        for task in asyncio.as_completed(search_tasks):
            try:
                result = await task
                completed_results.append(result)

                # Yield result immediately
                yield {
                    "type": "result",
                    "provider": result.provider.value,
                    "data": result.results,
                    "metadata": result.metadata,
                    "processing_time": result.processing_time,
                    "confidence": result.confidence,
                    "cached": False,
                }

            except Exception as e:
                logger.error(f"Search provider failed: {e}")
                yield {
                    "type": "error",
                    "message": f"Provider error: {e!s}",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        # Cache results
        await self.semantic_cache.cache_result(
            request.query,
            completed_results,
            request.tier,
            request.user_id,
            request.session_id,
        )

        # Final synthesis for Tier 2 and 3
        if request.tier in [SearchTier.TIER_2, SearchTier.TIER_3]:
            yield {
                "type": "status",
                "message": "Synthesizing results...",
                "timestamp": datetime.utcnow().isoformat(),
            }

            synthesis = await self._synthesize_results(completed_results, request)
            yield {
                "type": "synthesis",
                "data": synthesis,
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _determine_providers(
        self, request: SearchRequest
    ) -> list[SearchProvider]:
        """Determine which providers to use based on search tier"""

        if request.providers:
            return request.providers

        # Default provider selection by tier
        if request.tier == SearchTier.TIER_1:
            return [SearchProvider.BRAVE, SearchProvider.INTERNAL]
        elif request.tier == SearchTier.TIER_2:
            return [
                SearchProvider.BRAVE,
                SearchProvider.SEARXNG,
                SearchProvider.INTERNAL,
            ]
        else:  # TIER_3
            return [
                SearchProvider.BRAVE,
                SearchProvider.SEARXNG,
                SearchProvider.PERPLEXITY,
                SearchProvider.BROWSER,
                SearchProvider.INTERNAL,
            ]

    async def _execute_provider_search(
        self, provider: SearchProvider, request: SearchRequest
    ) -> SearchResult:
        """Execute search for a specific provider"""

        start_time = datetime.utcnow()

        try:
            if provider == SearchProvider.BRAVE:
                results = await self._search_brave(request)
            elif provider == SearchProvider.SEARXNG:
                results = await self._search_searxng(request)
            elif provider == SearchProvider.PERPLEXITY:
                results = await self._search_perplexity(request)
            elif provider == SearchProvider.BROWSER:
                results = await self._search_browser(request)
            elif provider == SearchProvider.INTERNAL:
                results = await self._search_internal(request)
            else:
                results = []

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            return SearchResult(
                provider=provider,
                results=results,
                metadata={"query": request.query, "tier": request.tier.value},
                processing_time=processing_time,
                confidence=self._calculate_confidence(results, provider),
            )

        except Exception as e:
            logger.error(f"Provider {provider.value} search failed: {e}")
            return SearchResult(
                provider=provider,
                results=[],
                metadata={"error": str(e)},
                processing_time=0.0,
                confidence=0.0,
            )

    async def _search_brave(self, request: SearchRequest) -> list[dict[str, Any]]:
        """Search using Brave Search API"""

        if not self.brave_api_key:
            logger.warning("Brave Search API key not configured")
            return []

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-Subscription-Token": self.brave_api_key,
                    "Accept": "application/json",
                }

                params = {
                    "q": request.query,
                    "count": min(request.max_results, 20),
                    "safesearch": "strict" if request.safe_search else "off",
                    "country": "US",
                    "lang": request.language,
                }

                async with session.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params,
                    timeout=10,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_brave_results(data)
                    else:
                        logger.error(f"Brave Search API error: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Brave Search failed: {e}")
            return []

    async def _search_searxng(self, request: SearchRequest) -> list[dict[str, Any]]:
        """Search using SearXNG"""

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": request.query,
                    "format": "json",
                    "safesearch": "2" if request.safe_search else "0",
                    "lang": request.language,
                }

                async with session.get(
                    f"{self.searxng_endpoint}/search", params=params, timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_searxng_results(data, request.max_results)
                    else:
                        logger.error(f"SearXNG API error: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"SearXNG search failed: {e}")
            return []

    async def _search_perplexity(self, request: SearchRequest) -> list[dict[str, Any]]:
        """Search using Perplexity AI"""

        if not self.perplexity_api_key:
            logger.warning("Perplexity API key not configured")
            return []

        try:
            ai_request = AIRequest(
                messages=[
                    {
                        "role": "user",
                        "content": f"Search and analyze: {request.query}. Provide comprehensive results with sources.",
                    }
                ],
                model="llama-3.1-sonar-small-128k-online",
                provider="perplexity",
                max_tokens=1000,
            )

            response = await self.ai_orchestrator.process_request(ai_request)

            if response.success:
                return [
                    {
                        "title": "Perplexity Analysis",
                        "content": response.content,
                        "url": "https://perplexity.ai",
                        "source": "perplexity",
                        "metadata": response.metadata,
                    }
                ]
            else:
                logger.error(f"Perplexity search failed: {response.error}")
                return []

        except Exception as e:
            logger.error(f"Perplexity search failed: {e}")
            return []

    async def _search_browser(self, request: SearchRequest) -> list[dict[str, Any]]:
        """Search using browser automation"""

        try:
            results = await self.browser_service.search_with_browser(
                request.query, request.max_results, request.search_domains
            )

            # For Tier 3, extract content from top results
            if request.tier == SearchTier.TIER_3 and results:
                enhanced_results = []
                for result in results[:5]:  # Limit to top 5 for content extraction
                    content = await self.browser_service.extract_page_content(
                        result["url"]
                    )
                    result["content"] = content
                    enhanced_results.append(result)
                return enhanced_results

            return results

        except Exception as e:
            logger.error(f"Browser search failed: {e}")
            return []

    async def _search_internal(self, request: SearchRequest) -> list[dict[str, Any]]:
        """Search internal knowledge base and databases"""

        try:
            # Search AI Memory
            memory_results = await self.ai_memory.search_memories(
                query=request.query,
                max_results=request.max_results,
                time_range=request.time_range,
            )

            # Search Qdrant knowledge base
            cortex_results = await self.cortex.search_knowledge_base(
                query=request.query, max_results=request.max_results
            )

            # Combine results
            results = []
            for result in memory_results:
                results.append(
                    {
                        "title": result.get("title", "AI Memory"),
                        "content": result.get("content", ""),
                        "url": f"ai-memory://{result.get('id')}",
                        "source": "ai_memory",
                        "timestamp": result.get("timestamp"),
                        "confidence": result.get("confidence", 0.0),
                    }
                )

            for result in cortex_results:
                results.append(
                    {
                        "title": result.get("title", "Knowledge Base"),
                        "content": result.get("content", ""),
                        "url": f"qdrant://{result.get('id')}",
                        "source": "qdrant",
                        "timestamp": result.get("timestamp"),
                        "confidence": result.get("confidence", 0.0),
                    }
                )

            return results[: request.max_results]

        except Exception as e:
            logger.error(f"Internal search failed: {e}")
            return []

    def _parse_brave_results(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse Brave Search API results"""

        results = []
        web_results = data.get("web", {}).get("results", [])

        for result in web_results:
            results.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("description", ""),
                    "source": "brave",
                    "published": result.get("published", ""),
                    "thumbnail": result.get("thumbnail", {}).get("src", ""),
                }
            )

        return results

    def _parse_searxng_results(
        self, data: dict[str, Any], max_results: int
    ) -> list[dict[str, Any]]:
        """Parse SearXNG results"""

        results = []
        search_results = data.get("results", [])

        for result in search_results[:max_results]:
            results.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("content", ""),
                    "source": "searxng",
                    "engine": result.get("engine", ""),
                    "score": result.get("score", 0.0),
                }
            )

        return results

    def _calculate_confidence(
        self, results: list[dict[str, Any]], provider: SearchProvider
    ) -> float:
        """Calculate confidence score for results"""

        if not results:
            return 0.0

        # Base confidence by provider
        base_confidence = {
            SearchProvider.BRAVE: 0.85,
            SearchProvider.SEARXNG: 0.75,
            SearchProvider.PERPLEXITY: 0.90,
            SearchProvider.BROWSER: 0.80,
            SearchProvider.INTERNAL: 0.95,
        }

        confidence = base_confidence.get(provider, 0.5)

        # Adjust based on result count
        result_count_factor = min(len(results) / 10, 1.0)
        confidence *= 0.5 + 0.5 * result_count_factor

        return confidence

    async def _synthesize_results(
        self, results: list[SearchResult], request: SearchRequest
    ) -> dict[str, Any]:
        """Synthesize search results using AI"""

        # Combine all results
        all_results = []
        for result in results:
            all_results.extend(result.results)

        if not all_results:
            return {"synthesis": "No results found.", "confidence": 0.0}

        # Create synthesis prompt
        synthesis_prompt = f"""
        Analyze and synthesize the following search results for the query: "{request.query}"

        Results from multiple sources:
        {json.dumps(all_results[:20], indent=2)}

        Provide a comprehensive synthesis that:
        1. Answers the user's query directly
        2. Identifies key themes and insights
        3. Highlights any contradictions or uncertainties
        4. Provides actionable recommendations
        5. Cites relevant sources

        Search tier: {request.tier.value}
        """

        try:
            ai_request = AIRequest(
                messages=[{"role": "user", "content": synthesis_prompt}],
                model="claude-3-sonnet-20241022",
                provider="anthropic",
                max_tokens=2000,
            )

            response = await self.ai_orchestrator.process_request(ai_request)

            if response.success:
                return {
                    "synthesis": response.content,
                    "confidence": 0.85,
                    "sources_used": len(all_results),
                    "providers": [r.provider.value for r in results],
                }
            else:
                return {
                    "synthesis": "Failed to synthesize results.",
                    "confidence": 0.0,
                    "error": response.error,
                }

        except Exception as e:
            logger.error(f"Result synthesis failed: {e}")
            return {
                "synthesis": "Failed to synthesize results.",
                "confidence": 0.0,
                "error": str(e),
            }

    async def cleanup(self) -> None:
        """Clean up resources"""
        await self.browser_service.cleanup()
