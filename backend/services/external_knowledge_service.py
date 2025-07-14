"""
External Knowledge Integration Service
Because your AI shouldn't live in a bubble
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

from backend.services.unified_memory_service_primary import UnifiedMemoryService
from backend.core.auto_esc_config import get_config_value
from backend.core.logging_config import get_logger


class ExternalKnowledgeService:
    """
    Injects fresh external knowledge into the RAG system
    X posts, news, trends - keeping Sophia street smart
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.memory = UnifiedMemoryService()

        # API configs
        self.x_api_key = get_config_value("x_api_key")
        self.news_api_key = get_config_value("news_api_key")

        # Cache for deduplication
        self.seen_content = set()  # Hash of content we've already processed
        self.cache_ttl = timedelta(hours=24)

    async def enrich_query_with_external(
        self, query: str, sources: List[str] = ["x", "news"]
    ) -> Dict[str, Any]:
        """
        Enrich a query with real-time external knowledge
        """
        enrichment_tasks = []

        if "x" in sources and self.x_api_key:
            enrichment_tasks.append(self._fetch_x_intel(query))

        if "news" in sources and self.news_api_key:
            enrichment_tasks.append(self._fetch_news_intel(query))

        # Fetch all sources in parallel
        results = await asyncio.gather(*enrichment_tasks, return_exceptions=True)

        # Process and store relevant content
        stored_items = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"External fetch failed: {result}")
                continue

            if result and "items" in result:
                for item in result["items"]:
                    # Deduplicate
                    content_hash = hashlib.md5(item["content"].encode()).hexdigest()
                    if content_hash in self.seen_content:
                        continue

                    # Store in temporary memory class
                    memory_id = await self._store_external_knowledge(item)
                    if memory_id:
                        stored_items.append(
                            {
                                "id": memory_id,
                                "source": item["source"],
                                "title": item.get("title", ""),
                                "preview": item["content"][:200] + "...",
                            }
                        )
                        self.seen_content.add(content_hash)

        # Now search with enriched context
        enriched_results = await self.memory.search_knowledge(
            query=query, limit=10, metadata_filter={"enriched": True}
        )

        return {
            "query": query,
            "external_sources": sources,
            "items_added": len(stored_items),
            "enriched_results": enriched_results,
            "external_items": stored_items,
        }

    async def _fetch_x_intel(self, query: str) -> Dict[str, Any]:
        """
        Fetch relevant posts from X
        Because real-time sentiment matters
        """
        try:
            # X API v2 semantic search endpoint (hypothetical)
            headers = {"Authorization": f"Bearer {self.x_api_key}"}
            params = {
                "query": query,
                "limit": 10,
                "sort": "relevance",
                "time_range": "24h",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.x.com/v2/semantic/search",
                    headers=headers,
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        items = []
                        for post in data.get("posts", []):
                            # Filter for quality
                            if post.get("engagement", {}).get("likes", 0) > 10:
                                items.append(
                                    {
                                        "source": "x",
                                        "content": post["text"],
                                        "author": post["author"]["username"],
                                        "url": post["url"],
                                        "timestamp": post["created_at"],
                                        "engagement": post["engagement"],
                                        "metadata": {
                                            "likes": post["engagement"]["likes"],
                                            "reposts": post["engagement"]["reposts"],
                                            "replies": post["engagement"]["replies"],
                                        },
                                    }
                                )

                        return {"items": items}
                    else:
                        self.logger.warning(f"X API returned {response.status}")
                        return {"items": []}

        except Exception as e:
            self.logger.error(f"X fetch failed: {e}")
            return {"items": []}

    async def _fetch_news_intel(self, query: str) -> Dict[str, Any]:
        """
        Fetch relevant news articles
        For when you need the bigger picture
        """
        try:
            headers = {"X-Api-Key": self.news_api_key}
            params = {
                "q": query,
                "sortBy": "relevancy",
                "language": "en",
                "from": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://newsapi.org/v2/everything", headers=headers, params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        items = []
                        for article in data.get("articles", [])[:5]:
                            items.append(
                                {
                                    "source": "news",
                                    "content": f"{article['title']}. {article['description']}",
                                    "title": article["title"],
                                    "url": article["url"],
                                    "timestamp": article["publishedAt"],
                                    "metadata": {
                                        "source_name": article["source"]["name"],
                                        "author": article.get("author", "Unknown"),
                                    },
                                }
                            )

                        return {"items": items}
                    else:
                        self.logger.warning(f"News API returned {response.status}")
                        return {"items": []}

        except Exception as e:
            self.logger.error(f"News fetch failed: {e}")
            return {"items": []}

    async def _store_external_knowledge(self, item: Dict[str, Any]) -> Optional[str]:
        """
        Store external knowledge in Weaviate with TTL
        """
        try:
            # Add to memory with external flag and TTL
            memory_id = await self.memory.add_knowledge(
                content=item["content"],
                source=f"external_{item['source']}",
                metadata={
                    **item.get("metadata", {}),
                    "external": True,
                    "enriched": True,
                    "ttl": (datetime.utcnow() + self.cache_ttl).isoformat(),
                    "url": item.get("url", ""),
                    "author": item.get("author", ""),
                    "fetched_at": datetime.utcnow().isoformat(),
                },
            )

            return memory_id

        except Exception as e:
            self.logger.error(f"Failed to store external knowledge: {e}")
            return None

    async def cleanup_expired_external(self):
        """
        Remove expired external knowledge
        Run this periodically to prevent bloat
        """
        try:
            # Query for expired external items
            # This would need Weaviate batch delete implementation
            # For now, log what would be cleaned
            self.logger.info("External knowledge cleanup - would remove expired items")

            # Clear seen content cache
            self.seen_content.clear()

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """
        Get current trending topics for proactive enrichment
        """
        trending = []

        # Get trending from X
        if self.x_api_key:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://api.x.com/v2/trends/place/1",  # Worldwide
                        headers={"Authorization": f"Bearer {self.x_api_key}"},
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            for trend in data.get("trends", [])[:10]:
                                trending.append(
                                    {
                                        "topic": trend["name"],
                                        "source": "x_trending",
                                        "volume": trend.get("tweet_volume", 0),
                                        "url": trend.get("url", ""),
                                    }
                                )
            except Exception as e:
                self.logger.error(f"Failed to get X trends: {e}")

        return trending

    async def auto_enrich_trending(self):
        """
        Automatically enrich knowledge base with trending topics
        Run this as a background task
        """
        trends = await self.get_trending_topics()

        for trend in trends[:5]:  # Top 5 trends
            # Skip if not relevant to business
            if any(
                skip in trend["topic"].lower()
                for skip in ["celebrity", "sports", "entertainment"]
            ):
                continue

            # Enrich with this trending topic
            await self.enrich_query_with_external(
                query=trend["topic"], sources=["x", "news"]
            )

            # Don't overwhelm APIs
            await asyncio.sleep(2)

        self.logger.info(f"Auto-enriched {len(trends)} trending topics")
