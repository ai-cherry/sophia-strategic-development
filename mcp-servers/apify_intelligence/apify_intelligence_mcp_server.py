#!/usr/bin/env python3
"""
Apify Intelligence MCP Server for Sophia AI
Provides competitive intelligence and web scraping capabilities
Leverages Apify CLI and SDK for business intelligence
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApifyIntelligenceMCPServer:
    """Apify Intelligence MCP Server for competitive intelligence and market research"""
    
    def __init__(self, port: int = 9015):
        self.port = port
        self.server = Server("apify-intelligence")
        self.apify_token = get_config_value("apify_api_token")
        self.apify_client = None
        
        # Competitive intelligence configurations
        self.intelligence_configs = {
            "competitor_analysis": {
                "actor_id": "apify/website-content-crawler",
                "description": "Analyze competitor websites for insights",
                "max_pages": 50
            },
            "pricing_intelligence": {
                "actor_id": "apify/web-scraper", 
                "description": "Extract pricing information from competitor sites",
                "max_pages": 20
            },
            "market_research": {
                "actor_id": "apify/google-search-scraper",
                "description": "Research market trends and opportunities",
                "max_results": 100
            },
            "social_listening": {
                "actor_id": "apify/instagram-scraper",
                "description": "Monitor social media for brand mentions",
                "max_posts": 200
            },
            "news_monitoring": {
                "actor_id": "apify/google-news-scraper",
                "description": "Track industry news and trends",
                "max_articles": 50
            }
        }
        
        # Initialize HTTP client for Apify API
        self.http_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.apify_token}"},
            timeout=60.0
        )
        
        self._register_tools()
        
    def _register_tools(self):
        """Register MCP tools for Apify intelligence"""
        
        @self.server.call_tool()
        async def competitive_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
            """Analyze competitor websites for business intelligence"""
            competitor_urls = arguments.get("urls", [])
            analysis_type = arguments.get("analysis_type", "comprehensive")
            
            if not competitor_urls:
                return [TextContent(
                    type="text",
                    text="Error: No competitor URLs provided for analysis"
                )]
            
            logger.info(f"🔍 Starting competitive analysis for {len(competitor_urls)} competitors")
            
            try:
                results = await self._run_competitive_analysis(competitor_urls, analysis_type)
                
                # Format results for business intelligence
                analysis_report = self._format_competitive_analysis(results)
                
                return [TextContent(
                    type="text", 
                    text=f"📊 Competitive Analysis Report:\n\n{analysis_report}"
                )]
                
            except Exception as e:
                logger.error(f"❌ Competitive analysis failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during competitive analysis: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def pricing_intelligence(arguments: Dict[str, Any]) -> List[TextContent]:
            """Extract and analyze competitor pricing strategies"""
            target_companies = arguments.get("companies", [])
            product_categories = arguments.get("categories", [])
            
            logger.info(f"💰 Analyzing pricing for {len(target_companies)} companies")
            
            try:
                pricing_data = await self._extract_pricing_intelligence(target_companies, product_categories)
                
                # Generate pricing insights
                insights = self._analyze_pricing_strategy(pricing_data)
                
                return [TextContent(
                    type="text",
                    text=f"💰 Pricing Intelligence Report:\n\n{insights}"
                )]
                
            except Exception as e:
                logger.error(f"❌ Pricing intelligence failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during pricing analysis: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def market_research(arguments: Dict[str, Any]) -> List[TextContent]:
            """Conduct comprehensive market research using Apify"""
            research_topics = arguments.get("topics", [])
            market_segments = arguments.get("segments", [])
            geographical_focus = arguments.get("geography", "global")
            
            logger.info(f"📈 Conducting market research on {len(research_topics)} topics")
            
            try:
                research_results = await self._conduct_market_research(
                    research_topics, market_segments, geographical_focus
                )
                
                # Generate market insights
                market_insights = self._generate_market_insights(research_results)
                
                return [TextContent(
                    type="text",
                    text=f"📈 Market Research Report:\n\n{market_insights}"
                )]
                
            except Exception as e:
                logger.error(f"❌ Market research failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during market research: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def social_listening(arguments: Dict[str, Any]) -> List[TextContent]:
            """Monitor social media for brand mentions and sentiment"""
            brands = arguments.get("brands", [])
            keywords = arguments.get("keywords", [])
            platforms = arguments.get("platforms", ["instagram", "twitter"])
            
            logger.info(f"👂 Social listening for {len(brands)} brands across {len(platforms)} platforms")
            
            try:
                social_data = await self._conduct_social_listening(brands, keywords, platforms)
                
                # Analyze sentiment and trends
                social_insights = self._analyze_social_sentiment(social_data)
                
                return [TextContent(
                    type="text",
                    text=f"👂 Social Listening Report:\n\n{social_insights}"
                )]
                
            except Exception as e:
                logger.error(f"❌ Social listening failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during social listening: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def news_monitoring(arguments: Dict[str, Any]) -> List[TextContent]:
            """Monitor industry news and trends"""
            industry_keywords = arguments.get("keywords", [])
            companies = arguments.get("companies", [])
            time_range = arguments.get("time_range", "7d")
            
            logger.info(f"📰 Monitoring news for {len(industry_keywords)} keywords")
            
            try:
                news_data = await self._monitor_industry_news(industry_keywords, companies, time_range)
                
                # Generate news insights
                news_insights = self._analyze_news_trends(news_data)
                
                return [TextContent(
                    type="text",
                    text=f"📰 News Monitoring Report:\n\n{news_insights}"
                )]
                
            except Exception as e:
                logger.error(f"❌ News monitoring failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during news monitoring: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def run_custom_scraper(arguments: Dict[str, Any]) -> List[TextContent]:
            """Run custom Apify actor for specific intelligence needs"""
            actor_id = arguments.get("actor_id", "")
            input_data = arguments.get("input", {})
            description = arguments.get("description", "Custom scraping task")
            
            if not actor_id:
                return [TextContent(
                    type="text",
                    text="Error: No actor_id provided for custom scraper"
                )]
            
            logger.info(f"🎯 Running custom scraper: {actor_id}")
            
            try:
                results = await self._run_custom_apify_actor(actor_id, input_data)
                
                formatted_results = self._format_custom_scraper_results(results, description)
                
                return [TextContent(
                    type="text",
                    text=f"🎯 Custom Scraper Results ({description}):\n\n{formatted_results}"
                )]
                
            except Exception as e:
                logger.error(f"❌ Custom scraper failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error running custom scraper: {str(e)}"
                )]

    async def _run_competitive_analysis(self, urls: List[str], analysis_type: str) -> Dict[str, Any]:
        """Run competitive analysis using Apify actors"""
        results = {}
        
        for url in urls:
            logger.info(f"🔍 Analyzing competitor: {url}")
            
            # Use website content crawler
            actor_input = {
                "startUrls": [{"url": url}],
                "maxCrawlPages": self.intelligence_configs["competitor_analysis"]["max_pages"],
                "crawlHttpsUrls": True,
                "crawlSubdomains": False,
                "removeCookieWarnings": True,
                "extractorOptions": {
                    "businessInfo": True,
                    "pricing": True,
                    "products": True,
                    "contact": True
                }
            }
            
            try:
                result = await self._run_apify_actor(
                    self.intelligence_configs["competitor_analysis"]["actor_id"],
                    actor_input
                )
                results[url] = result
                
            except Exception as e:
                logger.error(f"❌ Failed to analyze {url}: {e}")
                results[url] = {"error": str(e)}
        
        return results

    async def _extract_pricing_intelligence(self, companies: List[str], categories: List[str]) -> Dict[str, Any]:
        """Extract pricing intelligence from competitor websites"""
        pricing_data = {}
        
        for company in companies:
            logger.info(f"💰 Extracting pricing data for: {company}")
            
            # Search for company pricing pages
            search_input = {
                "queries": [f"{company} pricing", f"{company} plans", f"{company} cost"],
                "maxPagesPerQuery": 5,
                "includeUnfilteredResults": False,
                "customDataFunction": """
                ($) => {
                    return {
                        prices: $('[data-price], .price, .cost').text(),
                        plans: $('[data-plan], .plan, .tier').text(),
                        features: $('[data-feature], .feature').text()
                    };
                }
                """
            }
            
            try:
                result = await self._run_apify_actor(
                    self.intelligence_configs["pricing_intelligence"]["actor_id"],
                    search_input
                )
                pricing_data[company] = result
                
            except Exception as e:
                logger.error(f"❌ Failed to extract pricing for {company}: {e}")
                pricing_data[company] = {"error": str(e)}
        
        return pricing_data

    async def _conduct_market_research(self, topics: List[str], segments: List[str], geography: str) -> Dict[str, Any]:
        """Conduct comprehensive market research"""
        research_data = {}
        
        for topic in topics:
            logger.info(f"📈 Researching market topic: {topic}")
            
            # Search for market data
            search_queries = [
                f"{topic} market size {geography}",
                f"{topic} market trends 2024",
                f"{topic} industry analysis",
                f"{topic} competitive landscape"
            ]
            
            search_input = {
                "queries": search_queries,
                "maxPagesPerQuery": 20,
                "countryCode": self._get_country_code(geography),
                "includeUnfilteredResults": False
            }
            
            try:
                result = await self._run_apify_actor(
                    self.intelligence_configs["market_research"]["actor_id"],
                    search_input
                )
                research_data[topic] = result
                
            except Exception as e:
                logger.error(f"❌ Failed to research {topic}: {e}")
                research_data[topic] = {"error": str(e)}
        
        return research_data

    async def _conduct_social_listening(self, brands: List[str], keywords: List[str], platforms: List[str]) -> Dict[str, Any]:
        """Conduct social media listening across platforms"""
        social_data = {}
        
        for brand in brands:
            social_data[brand] = {}
            
            for platform in platforms:
                logger.info(f"👂 Listening on {platform} for: {brand}")
                
                if platform == "instagram":
                    search_input = {
                        "hashtags": [f"#{brand}"] + [f"#{kw}" for kw in keywords],
                        "resultsLimit": self.intelligence_configs["social_listening"]["max_posts"]
                    }
                    
                    try:
                        result = await self._run_apify_actor(
                            self.intelligence_configs["social_listening"]["actor_id"],
                            search_input
                        )
                        social_data[brand][platform] = result
                        
                    except Exception as e:
                        logger.error(f"❌ Failed {platform} listening for {brand}: {e}")
                        social_data[brand][platform] = {"error": str(e)}
        
        return social_data

    async def _monitor_industry_news(self, keywords: List[str], companies: List[str], time_range: str) -> Dict[str, Any]:
        """Monitor industry news and trends"""
        news_data = {}
        
        all_queries = keywords + [f"{company} news" for company in companies]
        
        for query in all_queries:
            logger.info(f"📰 Monitoring news for: {query}")
            
            search_input = {
                "queries": [query],
                "maxArticles": self.intelligence_configs["news_monitoring"]["max_articles"],
                "timeRange": time_range,
                "includeUnfilteredResults": False
            }
            
            try:
                result = await self._run_apify_actor(
                    self.intelligence_configs["news_monitoring"]["actor_id"],
                    search_input
                )
                news_data[query] = result
                
            except Exception as e:
                logger.error(f"❌ Failed to monitor news for {query}: {e}")
                news_data[query] = {"error": str(e)}
        
        return news_data

    async def _run_apify_actor(self, actor_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run an Apify actor and return results"""
        try:
            # Start actor run
            response = await self.http_client.post(
                f"https://api.apify.com/v2/acts/{actor_id}/runs",
                json=input_data
            )
            
            if response.status_code != 201:
                raise Exception(f"Failed to start actor: {response.status_code}")
            
            run_info = response.json()["data"]
            run_id = run_info["id"]
            
            # Wait for completion (with timeout)
            max_wait_time = 300  # 5 minutes
            wait_time = 0
            
            while wait_time < max_wait_time:
                status_response = await self.http_client.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}"
                )
                
                if status_response.status_code == 200:
                    run_status = status_response.json()["data"]
                    
                    if run_status["status"] in ["SUCCEEDED", "FAILED", "ABORTED"]:
                        break
                
                await asyncio.sleep(10)
                wait_time += 10
            
            # Get results
            if run_status["status"] == "SUCCEEDED":
                results_response = await self.http_client.get(
                    f"https://api.apify.com/v2/datasets/{run_status['defaultDatasetId']}/items"
                )
                
                if results_response.status_code == 200:
                    return {
                        "status": "success",
                        "data": results_response.json(),
                        "run_id": run_id,
                        "execution_time": run_status.get("runTimeSecs", 0)
                    }
            
            return {
                "status": "failed",
                "error": f"Actor run failed with status: {run_status['status']}",
                "run_id": run_id
            }
            
        except Exception as e:
            logger.error(f"❌ Apify actor execution failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _run_custom_apify_actor(self, actor_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run custom Apify actor with provided configuration"""
        return await self._run_apify_actor(actor_id, input_data)

    def _format_competitive_analysis(self, results: Dict[str, Any]) -> str:
        """Format competitive analysis results for business intelligence"""
        report = []
        
        for url, data in results.items():
            if "error" in data:
                report.append(f"❌ {url}: {data['error']}")
                continue
                
            report.append(f"🏢 **{url}**")
            
            if "data" in data and data["data"]:
                items = data["data"][:3]  # Top 3 results
                
                for item in items:
                    if "businessInfo" in item:
                        report.append(f"  📋 Business: {item['businessInfo']}")
                    if "pricing" in item:
                        report.append(f"  💰 Pricing: {item['pricing']}")
                    if "products" in item:
                        report.append(f"  📦 Products: {item['products']}")
                        
                report.append(f"  ⏱️ Analysis time: {data.get('execution_time', 0)}s")
            
            report.append("")
        
        return "\n".join(report)

    def _analyze_pricing_strategy(self, pricing_data: Dict[str, Any]) -> str:
        """Analyze pricing strategies and generate insights"""
        insights = ["💰 **Pricing Strategy Analysis**", ""]
        
        for company, data in pricing_data.items():
            if "error" in data:
                insights.append(f"❌ {company}: {data['error']}")
                continue
                
            insights.append(f"🏢 **{company}**")
            
            if "data" in data and data["data"]:
                # Extract pricing patterns
                pricing_mentions = []
                for item in data["data"]:
                    if "prices" in item and item["prices"]:
                        pricing_mentions.append(item["prices"])
                
                if pricing_mentions:
                    insights.append(f"  💵 Pricing found: {len(pricing_mentions)} mentions")
                    insights.append(f"  📊 Strategy: {self._analyze_pricing_patterns(pricing_mentions)}")
                else:
                    insights.append("  ⚠️ No clear pricing information found")
            
            insights.append("")
        
        return "\n".join(insights)

    def _generate_market_insights(self, research_data: Dict[str, Any]) -> str:
        """Generate market insights from research data"""
        insights = ["📈 **Market Research Insights**", ""]
        
        for topic, data in research_data.items():
            if "error" in data:
                insights.append(f"❌ {topic}: {data['error']}")
                continue
                
            insights.append(f"🎯 **{topic}**")
            
            if "data" in data and data["data"]:
                results_count = len(data["data"])
                insights.append(f"  📊 Found {results_count} relevant sources")
                
                # Extract key themes
                themes = self._extract_market_themes(data["data"])
                if themes:
                    insights.append(f"  🔍 Key themes: {', '.join(themes[:5])}")
                
                insights.append(f"  ⏱️ Research time: {data.get('execution_time', 0)}s")
            
            insights.append("")
        
        return "\n".join(insights)

    def _analyze_social_sentiment(self, social_data: Dict[str, Any]) -> str:
        """Analyze social media sentiment and engagement"""
        insights = ["👂 **Social Listening Analysis**", ""]
        
        for brand, platforms in social_data.items():
            insights.append(f"🏢 **{brand}**")
            
            for platform, data in platforms.items():
                if "error" in data:
                    insights.append(f"  ❌ {platform}: {data['error']}")
                    continue
                    
                insights.append(f"  📱 **{platform.title()}**")
                
                if "data" in data and data["data"]:
                    posts_count = len(data["data"])
                    insights.append(f"    📊 Posts analyzed: {posts_count}")
                    
                    # Basic sentiment analysis
                    sentiment = self._analyze_sentiment_basic(data["data"])
                    insights.append(f"    😊 Sentiment: {sentiment}")
                    
                    insights.append(f"    ⏱️ Analysis time: {data.get('execution_time', 0)}s")
            
            insights.append("")
        
        return "\n".join(insights)

    def _analyze_news_trends(self, news_data: Dict[str, Any]) -> str:
        """Analyze news trends and topics"""
        insights = ["📰 **News Monitoring Analysis**", ""]
        
        total_articles = 0
        trending_topics = []
        
        for query, data in news_data.items():
            if "error" in data:
                insights.append(f"❌ {query}: {data['error']}")
                continue
                
            insights.append(f"🔍 **{query}**")
            
            if "data" in data and data["data"]:
                articles_count = len(data["data"])
                total_articles += articles_count
                insights.append(f"  📊 Articles found: {articles_count}")
                
                # Extract trending topics
                topics = self._extract_trending_topics(data["data"])
                trending_topics.extend(topics)
                
                insights.append(f"  ⏱️ Monitoring time: {data.get('execution_time', 0)}s")
            
            insights.append("")
        
        # Overall trends
        insights.append(f"📈 **Overall Trends**")
        insights.append(f"  📰 Total articles analyzed: {total_articles}")
        
        if trending_topics:
            unique_topics = list(set(trending_topics))[:10]
            insights.append(f"  🔥 Trending topics: {', '.join(unique_topics)}")
        
        return "\n".join(insights)

    def _format_custom_scraper_results(self, results: Dict[str, Any], description: str) -> str:
        """Format custom scraper results"""
        if "error" in results:
            return f"❌ Error: {results['error']}"
        
        if "data" in results and results["data"]:
            data_count = len(results["data"])
            execution_time = results.get("execution_time", 0)
            
            return f"""✅ **{description}**
📊 Data points extracted: {data_count}
⏱️ Execution time: {execution_time}s
🎯 Status: {results.get('status', 'unknown')}

First few results:
{json.dumps(results["data"][:3], indent=2)}"""
        
        return f"⚠️ No data extracted for: {description}"

    # Helper methods
    def _get_country_code(self, geography: str) -> str:
        """Convert geography to country code"""
        geography_mapping = {
            "global": "US",
            "usa": "US", 
            "europe": "DE",
            "asia": "JP",
            "uk": "GB"
        }
        return geography_mapping.get(geography.lower(), "US")

    def _analyze_pricing_patterns(self, pricing_mentions: List[str]) -> str:
        """Analyze pricing patterns from mentions"""
        # Simple pattern analysis
        if any("$" in mention for mention in pricing_mentions):
            return "Dollar-based pricing detected"
        elif any("€" in mention for mention in pricing_mentions):
            return "Euro-based pricing detected"
        elif any("free" in mention.lower() for mention in pricing_mentions):
            return "Freemium model detected"
        else:
            return "Pricing strategy unclear"

    def _extract_market_themes(self, data: List[Dict]) -> List[str]:
        """Extract key themes from market research data"""
        themes = []
        for item in data[:10]:  # Analyze first 10 items
            if "title" in item:
                # Simple keyword extraction
                title_words = item["title"].lower().split()
                themes.extend([word for word in title_words if len(word) > 4])
        
        # Return most common themes
        from collections import Counter
        return [theme for theme, count in Counter(themes).most_common(5)]

    def _analyze_sentiment_basic(self, posts: List[Dict]) -> str:
        """Basic sentiment analysis of social posts"""
        positive_words = ["great", "awesome", "love", "amazing", "excellent"]
        negative_words = ["bad", "terrible", "hate", "awful", "horrible"]
        
        positive_count = 0
        negative_count = 0
        
        for post in posts:
            text = str(post).lower()
            positive_count += sum(1 for word in positive_words if word in text)
            negative_count += sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "Positive"
        elif negative_count > positive_count:
            return "Negative"
        else:
            return "Neutral"

    def _extract_trending_topics(self, articles: List[Dict]) -> List[str]:
        """Extract trending topics from news articles"""
        topics = []
        for article in articles:
            if "title" in article:
                # Simple topic extraction
                title_words = article["title"].split()
                topics.extend([word for word in title_words if len(word) > 5])
        
        return topics

    async def start_server(self):
        """Start the Apify Intelligence MCP server"""
        logger.info(f"🚀 Starting Apify Intelligence MCP Server on port {self.port}")
        
        # Add health check endpoint
        @self.server.call_tool()
        async def health_check(arguments: Dict[str, Any]) -> List[TextContent]:
            """Health check for Apify Intelligence MCP server"""
            return [TextContent(
                type="text",
                text=f"✅ Apify Intelligence MCP Server is healthy (Port: {self.port})"
            )]
        
        # Register tools as MCP tools
        tools = [
            Tool(
                name="competitive_analysis",
                description="Analyze competitor websites for business intelligence",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "urls": {"type": "array", "items": {"type": "string"}},
                        "analysis_type": {"type": "string", "default": "comprehensive"}
                    },
                    "required": ["urls"]
                }
            ),
            Tool(
                name="pricing_intelligence", 
                description="Extract and analyze competitor pricing strategies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "companies": {"type": "array", "items": {"type": "string"}},
                        "categories": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["companies"]
                }
            ),
            Tool(
                name="market_research",
                description="Conduct comprehensive market research",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topics": {"type": "array", "items": {"type": "string"}},
                        "segments": {"type": "array", "items": {"type": "string"}},
                        "geography": {"type": "string", "default": "global"}
                    },
                    "required": ["topics"]
                }
            ),
            Tool(
                name="social_listening",
                description="Monitor social media for brand mentions and sentiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "brands": {"type": "array", "items": {"type": "string"}},
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "platforms": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["brands"]
                }
            ),
            Tool(
                name="news_monitoring",
                description="Monitor industry news and trends",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "companies": {"type": "array", "items": {"type": "string"}},
                        "time_range": {"type": "string", "default": "7d"}
                    },
                    "required": ["keywords"]
                }
            ),
            Tool(
                name="run_custom_scraper",
                description="Run custom Apify actor for specific intelligence needs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "actor_id": {"type": "string"},
                        "input": {"type": "object"},
                        "description": {"type": "string"}
                    },
                    "required": ["actor_id", "input"]
                }
            ),
            Tool(
                name="health_check",
                description="Check health status of Apify Intelligence MCP server",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
        
        # Set tools on server
        self.server.tools = tools
        
        # Start the server
        await self.server.run(port=self.port)

    async def cleanup(self):
        """Cleanup resources"""
        if self.http_client:
            await self.http_client.aclose()

# Main execution
async def main():
    server = ApifyIntelligenceMCPServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down Apify Intelligence MCP Server")
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 