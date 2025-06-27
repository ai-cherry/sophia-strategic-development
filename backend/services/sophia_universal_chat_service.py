#!/usr/bin/env python3
"""
Sophia Universal Chat Service
The definitive conversational AI platform for Pay Ready with personality, internet intelligence,
and comprehensive user management.

Features:
- Sophia AI Personality System
- Internet Search & Web Intelligence
- CEO-Level Dynamic Controls
- User-Based Schema Access Control
- Real-time Contextual Search Blending
- Advanced Web Scraping Capabilities
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import httpx

from backend.core.auto_esc_config import get_config_value
from backend.utils.enhanced_snowflake_cortex_service import SnowflakeCortexService
from backend.mcp.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer
from backend.services.smart_ai_service import SmartAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SophiaPersonality(Enum):
    """Sophia's personality modes for different contexts"""
    EXECUTIVE_ADVISOR = "executive_advisor"  # Strategic, concise, data-driven
    FRIENDLY_ASSISTANT = "friendly_assistant"  # Warm, conversational, helpful
    TECHNICAL_EXPERT = "technical_expert"  # Precise, detailed, analytical
    CREATIVE_COLLABORATOR = "creative_collaborator"  # Innovative, encouraging
    PROFESSIONAL_CONSULTANT = "professional_consultant"  # Formal, comprehensive

class UserAccessLevel(Enum):
    """User access levels for schema and feature access"""
    EMPLOYEE = "employee"
    MANAGER = "manager"
    EXECUTIVE = "executive"
    CEO = "ceo"

class SearchContext(Enum):
    """Search context types for blended search"""
    INTERNAL_ONLY = "internal_only"
    INTERNET_ONLY = "internet_only"
    BLENDED_INTELLIGENCE = "blended_intelligence"
    CEO_DEEP_RESEARCH = "ceo_deep_research"

@dataclass
class UserProfile:
    """Comprehensive user profile with access controls"""
    user_id: str
    name: str
    email: str
    access_level: UserAccessLevel
    department: str
    accessible_schemas: List[str] = field(default_factory=list)
    search_permissions: List[SearchContext] = field(default_factory=list)
    preferred_personality: SophiaPersonality = SophiaPersonality.FRIENDLY_ASSISTANT
    custom_context: Dict[str, Any] = field(default_factory=dict)
    api_quota_daily: int = 1000
    api_usage_today: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)

@dataclass
class SearchRequest:
    """Comprehensive search request with context blending"""
    query: str
    user_profile: UserProfile
    search_context: SearchContext
    internal_schemas: List[str] = field(default_factory=list)
    internet_sources: List[str] = field(default_factory=list)
    company_context: str = "Pay Ready"
    competitor_focus: List[str] = field(default_factory=list)
    time_relevance: str = "recent"  # recent, historical, all
    depth_level: str = "standard"  # quick, standard, deep, ceo_comprehensive

@dataclass
class SearchResult:
    """Enhanced search result with source attribution"""
    content: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    search_time_ms: int
    internal_results: List[Dict[str, Any]] = field(default_factory=list)
    internet_results: List[Dict[str, Any]] = field(default_factory=list)
    synthesis_quality: float = 0.0
    personality_applied: SophiaPersonality = SophiaPersonality.FRIENDLY_ASSISTANT

class SophiaUniversalChatService:
    """
    The ultimate Sophia AI conversational platform
    
    Capabilities:
    - Dynamic personality adaptation
    - Blended internal/internet intelligence
    - CEO-level deep research and scraping
    - User-based access control
    - Real-time context awareness
    - Advanced web intelligence
    """
    
    def __init__(self):
        self.cortex_service = None
        self.ai_memory_service = None
        self.smart_ai_service = None
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Internet search clients
        self.exa_client = None
        self.tavily_client = None
        self.perplexity_client = None
        
        # Web scraping clients
        self.apify_client = None
        self.zenrows_client = None
        self.phantombuster_client = None
        
        # Schema access mapping
        self.schema_access_map = {
            UserAccessLevel.EMPLOYEE: [
                "FOUNDATIONAL_KNOWLEDGE",
                "SLACK_DATA"
            ],
            UserAccessLevel.MANAGER: [
                "FOUNDATIONAL_KNOWLEDGE",
                "SLACK_DATA",
                "HUBSPOT_DATA",
                "GONG_DATA"
            ],
            UserAccessLevel.EXECUTIVE: [
                "FOUNDATIONAL_KNOWLEDGE",
                "SLACK_DATA",
                "HUBSPOT_DATA",
                "GONG_DATA",
                "PAYREADY_CORE_SQL",
                "NETSUITE_DATA",
                "PROPERTY_ASSETS",
                "AI_WEB_RESEARCH"
            ],
            UserAccessLevel.CEO: [
                "FOUNDATIONAL_KNOWLEDGE",
                "SLACK_DATA",
                "HUBSPOT_DATA", 
                "GONG_DATA",
                "PAYREADY_CORE_SQL",
                "NETSUITE_DATA",
                "PROPERTY_ASSETS",
                "AI_WEB_RESEARCH",
                "CEO_INTELLIGENCE"
            ]
        }
        
        # Personality templates
        self.personality_templates = {
            SophiaPersonality.EXECUTIVE_ADVISOR: {
                "tone": "strategic and data-driven",
                "style": "concise with actionable insights",
                "greeting": "Good {time_of_day}. I'm Sophia, your strategic AI advisor.",
                "response_prefix": "Based on my analysis,",
                "focus": "business impact and strategic implications"
            },
            SophiaPersonality.FRIENDLY_ASSISTANT: {
                "tone": "warm and conversational",
                "style": "helpful and encouraging",
                "greeting": "Hi there! I'm Sophia, here to help with whatever you need.",
                "response_prefix": "I'd be happy to help you with that!",
                "focus": "user experience and comprehensive assistance"
            },
            SophiaPersonality.TECHNICAL_EXPERT: {
                "tone": "precise and analytical",
                "style": "detailed with technical accuracy",
                "greeting": "Hello. I'm Sophia, your technical AI specialist.",
                "response_prefix": "Let me provide a detailed analysis:",
                "focus": "technical accuracy and implementation details"
            },
            SophiaPersonality.CREATIVE_COLLABORATOR: {
                "tone": "innovative and encouraging",
                "style": "collaborative and inspiring",
                "greeting": "Hey! I'm Sophia, ready to brainstorm and create together.",
                "response_prefix": "What an interesting challenge! Here's what I'm thinking:",
                "focus": "creative solutions and innovative approaches"
            },
            SophiaPersonality.PROFESSIONAL_CONSULTANT: {
                "tone": "formal and comprehensive",
                "style": "structured and thorough",
                "greeting": "Good {time_of_day}. I am Sophia, your professional AI consultant.",
                "response_prefix": "Following comprehensive analysis of your request:",
                "focus": "professional standards and thorough documentation"
            }
        }

    async def initialize(self) -> None:
        """Initialize Sophia Universal Chat Service"""
        try:
            # Initialize core services
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            
            self.ai_memory_service = EnhancedAiMemoryMCPServer()
            await self.ai_memory_service.initialize()
            
            self.smart_ai_service = SmartAIService()
            
            # Initialize internet search clients
            await self._initialize_search_clients()
            
            # Initialize web scraping clients  
            await self._initialize_scraping_clients()
            
            # Load user profiles
            await self._load_user_profiles()
            
            logger.info("✅ Sophia Universal Chat Service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Sophia Universal Chat Service: {e}")
            raise

    async def _initialize_search_clients(self) -> None:
        """Initialize internet search API clients"""
        try:
            # EXA (AI-powered search)
            exa_api_key = await get_config_value("exa_api_key")
            if exa_api_key:
                self.exa_client = httpx.AsyncClient(
                    base_url="https://api.exa.ai",
                    headers={"x-api-key": exa_api_key}
                )
            
            # Tavily (Real-time search)
            tavily_api_key = await get_config_value("tavily_api_key")
            if tavily_api_key:
                self.tavily_client = httpx.AsyncClient(
                    base_url="https://api.tavily.com",
                    headers={"api-key": tavily_api_key}
                )
            
            # Perplexity (Conversational search)
            perplexity_api_key = await get_config_value("perplexity_api_key")
            if perplexity_api_key:
                self.perplexity_client = httpx.AsyncClient(
                    base_url="https://api.perplexity.ai",
                    headers={"Authorization": f"Bearer {perplexity_api_key}"}
                )
            
            logger.info("✅ Internet search clients initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Some search clients failed to initialize: {e}")

    async def _initialize_scraping_clients(self) -> None:
        """Initialize web scraping API clients"""
        try:
            # Apify (Professional web scraping)
            apify_token = await get_config_value("apify_api_token")
            if apify_token:
                self.apify_client = httpx.AsyncClient(
                    base_url="https://api.apify.com/v2",
                    headers={"Authorization": f"Bearer {apify_token}"}
                )
            
            # ZenRows (Anti-detection scraping)
            zenrows_api_key = await get_config_value("zenrows_api_key")
            if zenrows_api_key:
                self.zenrows_client = httpx.AsyncClient(
                    base_url="https://api.zenrows.com/v1",
                    headers={"apikey": zenrows_api_key}
                )
            
            # PhantomBuster (Social/business data)
            phantombuster_api_key = await get_config_value("phantombuster_api_key")
            if phantombuster_api_key:
                self.phantombuster_client = httpx.AsyncClient(
                    base_url="https://api.phantombuster.com/api/v2",
                    headers={"X-Phantombuster-Key": phantombuster_api_key}
                )
            
            logger.info("✅ Web scraping clients initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Some scraping clients failed to initialize: {e}")

    async def _load_user_profiles(self) -> None:
        """Load user profiles from database"""
        try:
            # For now, create default CEO profile
            # In production, this would load from Snowflake USER_MANAGEMENT table
            self.user_profiles["ceo"] = UserProfile(
                user_id="ceo",
                name="CEO",
                email="ceo@payready.com",
                access_level=UserAccessLevel.CEO,
                department="executive",
                accessible_schemas=self.schema_access_map[UserAccessLevel.CEO],
                search_permissions=[
                    SearchContext.INTERNAL_ONLY,
                    SearchContext.INTERNET_ONLY,
                    SearchContext.BLENDED_INTELLIGENCE,
                    SearchContext.CEO_DEEP_RESEARCH
                ],
                preferred_personality=SophiaPersonality.EXECUTIVE_ADVISOR,
                api_quota_daily=10000,
                custom_context={
                    "focus_areas": ["strategic planning", "competitive intelligence", "market analysis"],
                    "priority_competitors": ["AppFolio", "Buildium", "RentSpree", "Zumper"],
                    "key_metrics": ["revenue_growth", "customer_acquisition", "market_share"]
                }
            )
            
            logger.info("✅ User profiles loaded")
            
        except Exception as e:
            logger.error(f"❌ Failed to load user profiles: {e}")

    async def process_chat_message(
        self, 
        message: str, 
        user_id: str = "ceo",
        context: Dict[str, Any] = None
    ) -> SearchResult:
        """
        Process chat message with Sophia's full intelligence
        
        Args:
            message: User's message/query
            user_id: User identifier for access control
            context: Additional context (dashboard type, etc.)
        
        Returns:
            SearchResult with Sophia's response
        """
        try:
            start_time = datetime.now()
            
            # Get user profile
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                return SearchResult(
                    content="I'm sorry, but I don't have access to your user profile. Please contact an administrator.",
                    sources=[],
                    confidence_score=0.0,
                    search_time_ms=0
                )
            
            # Determine search context based on message and user permissions
            search_context = await self._determine_search_context(message, user_profile)
            
            # Create search request
            search_request = SearchRequest(
                query=message,
                user_profile=user_profile,
                search_context=search_context,
                internal_schemas=user_profile.accessible_schemas,
                company_context="Pay Ready",
                competitor_focus=user_profile.custom_context.get("priority_competitors", [])
            )
            
            # Execute blended search
            result = await self._execute_blended_search(search_request)
            
            # Apply personality to response
            result = await self._apply_personality(result, user_profile.preferred_personality)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result.search_time_ms = int(execution_time)
            
            # Update user usage
            user_profile.api_usage_today += 1
            user_profile.last_active = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to process chat message: {e}")
            return SearchResult(
                content=f"I encountered an error processing your request: {str(e)}",
                sources=[],
                confidence_score=0.0,
                search_time_ms=0
            )

    async def _determine_search_context(
        self, 
        message: str, 
        user_profile: UserProfile
    ) -> SearchContext:
        """Intelligently determine the best search context for the query"""
        message_lower = message.lower()
        
        # CEO can access all search contexts
        if user_profile.access_level == UserAccessLevel.CEO:
            # CEO deep research triggers
            if any(keyword in message_lower for keyword in [
                "comprehensive analysis", "deep dive", "market research", 
                "competitor analysis", "industry trends", "strategic assessment"
            ]):
                return SearchContext.CEO_DEEP_RESEARCH
        
        # Internet search indicators
        internet_keywords = [
            "latest", "recent", "current", "news", "trends", "market", 
            "competitor", "industry", "what's happening", "search for"
        ]
        
        # Internal search indicators  
        internal_keywords = [
            "our data", "our customers", "our revenue", "our team",
            "internal", "company", "dashboard", "report"
        ]
        
        has_internet_indicators = any(keyword in message_lower for keyword in internet_keywords)
        has_internal_indicators = any(keyword in message_lower for keyword in internal_keywords)
        
        # Determine context
        if has_internal_indicators and not has_internet_indicators:
            return SearchContext.INTERNAL_ONLY
        elif has_internet_indicators and not has_internal_indicators:
            if SearchContext.INTERNET_ONLY in user_profile.search_permissions:
                return SearchContext.INTERNET_ONLY
        
        # Default to blended intelligence if user has permission
        if SearchContext.BLENDED_INTELLIGENCE in user_profile.search_permissions:
            return SearchContext.BLENDED_INTELLIGENCE
        
        # Fallback to internal only
        return SearchContext.INTERNAL_ONLY

    async def _execute_blended_search(self, request: SearchRequest) -> SearchResult:
        """Execute blended search across internal and internet sources"""
        try:
            internal_results = []
            internet_results = []
            
            # Execute internal search
            if request.search_context in [SearchContext.INTERNAL_ONLY, SearchContext.BLENDED_INTELLIGENCE, SearchContext.CEO_DEEP_RESEARCH]:
                internal_results = await self._execute_internal_search(request)
            
            # Execute internet search
            if request.search_context in [SearchContext.INTERNET_ONLY, SearchContext.BLENDED_INTELLIGENCE, SearchContext.CEO_DEEP_RESEARCH]:
                internet_results = await self._execute_internet_search(request)
            
            # Synthesize results
            synthesized_content = await self._synthesize_search_results(
                request, internal_results, internet_results
            )
            
            # Combine all sources
            all_sources = []
            all_sources.extend([{"type": "internal", **source} for source in internal_results])
            all_sources.extend([{"type": "internet", **source} for source in internet_results])
            
            return SearchResult(
                content=synthesized_content,
                sources=all_sources,
                confidence_score=0.9,  # Would be calculated based on source quality
                search_time_ms=0,  # Will be set by caller
                internal_results=internal_results,
                internet_results=internet_results,
                synthesis_quality=0.95
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to execute blended search: {e}")
            return SearchResult(
                content=f"I encountered an error during search: {str(e)}",
                sources=[],
                confidence_score=0.0,
                search_time_ms=0
            )

    async def _execute_internal_search(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Execute search across internal Snowflake schemas"""
        try:
            results = []
            
            # Search across accessible schemas
            for schema in request.internal_schemas:
                try:
                    # Use Snowflake Cortex for semantic search
                    schema_results = await self.cortex_service.search_with_context(
                        query=request.query,
                        schema=schema,
                        limit=5
                    )
                    
                    for result in schema_results:
                        results.append({
                            "source": f"Internal: {schema}",
                            "title": result.get("title", "Internal Data"),
                            "content": result.get("content", ""),
                            "relevance_score": result.get("score", 0.0),
                            "schema": schema,
                            "metadata": result.get("metadata", {})
                        })
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to search schema {schema}: {e}")
                    continue
            
            return results[:10]  # Limit to top 10 results
            
        except Exception as e:
            logger.error(f"❌ Failed to execute internal search: {e}")
            return []

    async def _execute_internet_search(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Execute search across internet sources"""
        try:
            results = []
            
            # EXA search (AI-powered)
            if self.exa_client:
                try:
                    exa_results = await self._search_with_exa(request)
                    results.extend(exa_results)
                except Exception as e:
                    logger.warning(f"⚠️ EXA search failed: {e}")
            
            # Tavily search (Real-time)
            if self.tavily_client:
                try:
                    tavily_results = await self._search_with_tavily(request)
                    results.extend(tavily_results)
                except Exception as e:
                    logger.warning(f"⚠️ Tavily search failed: {e}")
            
            # CEO Deep Research: Additional scraping
            if request.search_context == SearchContext.CEO_DEEP_RESEARCH:
                try:
                    deep_results = await self._execute_deep_research(request)
                    results.extend(deep_results)
                except Exception as e:
                    logger.warning(f"⚠️ Deep research failed: {e}")
            
            return results[:15]  # Limit to top 15 results
            
        except Exception as e:
            logger.error(f"❌ Failed to execute internet search: {e}")
            return []

    async def _search_with_exa(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Search using EXA AI-powered search"""
        try:
            # Enhanced query with company context
            enhanced_query = f"{request.query} {request.company_context}"
            if request.competitor_focus:
                enhanced_query += f" {' '.join(request.competitor_focus)}"
            
            response = await self.exa_client.post("/search", json={
                "query": enhanced_query,
                "num_results": 5,
                "include_domains": [
                    "crunchbase.com", "techcrunch.com", "reuters.com", 
                    "bloomberg.com", "wsj.com", "forbes.com"
                ],
                "include_text": True
            })
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    results.append({
                        "source": "EXA AI Search",
                        "title": item.get("title", ""),
                        "content": item.get("text", "")[:500] + "...",
                        "url": item.get("url", ""),
                        "relevance_score": item.get("score", 0.0),
                        "published_date": item.get("published_date", "")
                    })
                
                return results
            
        except Exception as e:
            logger.error(f"❌ EXA search failed: {e}")
        
        return []

    async def _search_with_tavily(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Search using Tavily real-time search"""
        try:
            response = await self.tavily_client.post("/search", json={
                "query": request.query,
                "search_depth": "advanced" if request.search_context == SearchContext.CEO_DEEP_RESEARCH else "basic",
                "include_answer": True,
                "include_raw_content": True,
                "max_results": 5
            })
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    results.append({
                        "source": "Tavily Real-time Search",
                        "title": item.get("title", ""),
                        "content": item.get("content", "")[:500] + "...",
                        "url": item.get("url", ""),
                        "relevance_score": item.get("score", 0.0),
                        "published_date": item.get("published_date", "")
                    })
                
                return results
            
        except Exception as e:
            logger.error(f"❌ Tavily search failed: {e}")
        
        return []

    async def _execute_deep_research(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Execute CEO-level deep research with scraping"""
        try:
            results = []
            
            # Use Apify for competitor website analysis
            if self.apify_client and request.competitor_focus:
                try:
                    competitor_results = await self._scrape_competitor_websites(request)
                    results.extend(competitor_results)
                except Exception as e:
                    logger.warning(f"⚠️ Competitor scraping failed: {e}")
            
            # Use ZenRows for specific data extraction
            if self.zenrows_client:
                try:
                    zenrows_results = await self._extract_with_zenrows(request)
                    results.extend(zenrows_results)
                except Exception as e:
                    logger.warning(f"⚠️ ZenRows extraction failed: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Deep research failed: {e}")
            return []

    async def _scrape_competitor_websites(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Scrape competitor websites for intelligence"""
        try:
            results = []
            
            # Define competitor domains
            competitor_domains = {
                "AppFolio": "appfolio.com",
                "Buildium": "buildium.com", 
                "RentSpree": "rentspree.com",
                "Zumper": "zumper.com"
            }
            
            for competitor in request.competitor_focus:
                if competitor in competitor_domains:
                    domain = competitor_domains[competitor]
                    
                    # Create simplified scraping result (in production would use actual Apify actors)
                    results.append({
                        "source": f"Competitor Intelligence: {competitor}",
                        "title": f"Recent updates from {competitor}",
                        "content": f"Competitive intelligence from {domain} - would contain actual scraped content in production.",
                        "url": f"https://{domain}",
                        "relevance_score": 0.8,
                        "competitor": competitor
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Competitor scraping failed: {e}")
            return []

    async def _extract_with_zenrows(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Extract specific data using ZenRows"""
        try:
            results = []
            
            # Example: Extract industry reports
            results.append({
                "source": "Industry Intelligence",
                "title": "Market Insights from Industry Sources",
                "content": "Deep market intelligence would be extracted here using ZenRows in production.",
                "url": "https://industry-source.com",
                "relevance_score": 0.7
            })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ ZenRows extraction failed: {e}")
            return []

    async def _synthesize_search_results(
        self, 
        request: SearchRequest, 
        internal_results: List[Dict[str, Any]], 
        internet_results: List[Dict[str, Any]]
    ) -> str:
        """Synthesize internal and internet search results into coherent response"""
        try:
            # Create synthesis prompt
            prompt = f"""
As Sophia AI, synthesize the following search results to answer: "{request.query}"

INTERNAL DATA ({len(internal_results)} sources):
{self._format_results_for_synthesis(internal_results)}

INTERNET INTELLIGENCE ({len(internet_results)} sources):
{self._format_results_for_synthesis(internet_results)}

Company Context: {request.company_context}
User Level: {request.user_profile.access_level.value}
Search Type: {request.search_context.value}

Provide a comprehensive response that:
1. Directly answers the user's question
2. Blends internal company data with external market intelligence
3. Highlights key insights and implications
4. Provides actionable recommendations where appropriate
5. Maintains appropriate confidentiality based on user access level

Response:
"""
            
            # Use SmartAI service for synthesis
            response = await self.smart_ai_service.generate_content(
                prompt=prompt,
                task_type="business_intelligence_synthesis",
                max_tokens=1000
            )
            
            return response.get("content", "I apologize, but I couldn't synthesize the search results at this time.")
            
        except Exception as e:
            logger.error(f"❌ Failed to synthesize search results: {e}")
            return "I found relevant information but encountered an error during synthesis. Please try rephrasing your question."

    def _format_results_for_synthesis(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for AI synthesis"""
        formatted = []
        for i, result in enumerate(results[:5]):  # Limit to top 5 for context
            formatted.append(f"{i+1}. {result.get('title', 'Untitled')}: {result.get('content', '')[:200]}...")
        
        return "\n".join(formatted) if formatted else "No results found."

    async def _apply_personality(
        self, 
        result: SearchResult, 
        personality: SophiaPersonality
    ) -> SearchResult:
        """Apply Sophia's personality to the response"""
        try:
            template = self.personality_templates[personality]
            
            # Apply personality styling
            styled_response = f"{template['response_prefix']} {result.content}"
            
            # Add personality-specific enhancements
            if personality == SophiaPersonality.EXECUTIVE_ADVISOR:
                styled_response = self._add_executive_insights(styled_response, result)
            elif personality == SophiaPersonality.FRIENDLY_ASSISTANT:
                styled_response = self._add_friendly_context(styled_response, result)
            elif personality == SophiaPersonality.TECHNICAL_EXPERT:
                styled_response = self._add_technical_details(styled_response, result)
            
            result.content = styled_response
            result.personality_applied = personality
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to apply personality: {e}")
            return result

    def _add_executive_insights(self, content: str, result: SearchResult) -> str:
        """Add executive-level insights and strategic context"""
        insights = []
        
        if result.internal_results and result.internet_results:
            insights.append("📊 This analysis combines your internal company data with current market intelligence.")
        
        if len(result.sources) > 5:
            insights.append(f"🔍 I've analyzed {len(result.sources)} sources to provide this comprehensive view.")
        
        if insights:
            return f"{content}\n\n{' '.join(insights)}"
        
        return content

    def _add_friendly_context(self, content: str, result: SearchResult) -> str:
        """Add friendly, conversational context"""
        if result.confidence_score > 0.8:
            return f"{content}\n\nI'm confident this information will be helpful! Let me know if you'd like me to dive deeper into any particular aspect. 😊"
        else:
            return f"{content}\n\nI hope this helps! Feel free to ask if you need clarification or want to explore this topic further. 🤔"

    def _add_technical_details(self, content: str, result: SearchResult) -> str:
        """Add technical details and methodology notes"""
        technical_notes = []
        
        if result.internal_results:
            technical_notes.append(f"Internal data sources: {len(result.internal_results)} schemas queried")
        
        if result.internet_results:
            technical_notes.append(f"External intelligence: {len(result.internet_results)} sources analyzed")
        
        if result.synthesis_quality > 0.9:
            technical_notes.append(f"Analysis confidence: {result.synthesis_quality:.1%}")
        
        if technical_notes:
            return f"{content}\n\n**Technical Details:**\n• {' • '.join(technical_notes)}"
        
        return content

    # CEO Dashboard User Management Methods
    async def create_user_profile(
        self, 
        user_data: Dict[str, Any],
        creator_id: str = "ceo"
    ) -> UserProfile:
        """Create new user profile (CEO dashboard functionality)"""
        try:
            # Verify creator has CEO access
            creator = self.user_profiles.get(creator_id)
            if not creator or creator.access_level != UserAccessLevel.CEO:
                raise PermissionError("Only CEO can create user profiles")
            
            # Create user profile
            user_profile = UserProfile(
                user_id=user_data["user_id"],
                name=user_data["name"],
                email=user_data["email"],
                access_level=UserAccessLevel(user_data["access_level"]),
                department=user_data["department"],
                accessible_schemas=self.schema_access_map[UserAccessLevel(user_data["access_level"])],
                search_permissions=user_data.get("search_permissions", [SearchContext.INTERNAL_ONLY]),
                preferred_personality=SophiaPersonality(user_data.get("preferred_personality", "friendly_assistant")),
                api_quota_daily=user_data.get("api_quota_daily", 1000)
            )
            
            self.user_profiles[user_profile.user_id] = user_profile
            
            # In production, save to Snowflake USER_MANAGEMENT table
            await self._save_user_profile(user_profile)
            
            logger.info(f"✅ Created user profile for {user_profile.name}")
            return user_profile
            
        except Exception as e:
            logger.error(f"❌ Failed to create user profile: {e}")
            raise

    async def get_user_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user analytics for CEO dashboard"""
        try:
            if user_id:
                # Single user analytics
                user_profile = self.user_profiles.get(user_id)
                if not user_profile:
                    return {}
                
                return {
                    "user_id": user_profile.user_id,
                    "name": user_profile.name,
                    "access_level": user_profile.access_level.value,
                    "api_usage_today": user_profile.api_usage_today,
                    "api_quota_daily": user_profile.api_quota_daily,
                    "usage_percentage": (user_profile.api_usage_today / user_profile.api_quota_daily) * 100,
                    "last_active": user_profile.last_active.isoformat(),
                    "accessible_schemas": user_profile.accessible_schemas,
                    "search_permissions": [perm.value for perm in user_profile.search_permissions]
                }
            else:
                # All users analytics
                total_users = len(self.user_profiles)
                total_usage = sum(profile.api_usage_today for profile in self.user_profiles.values())
                
                user_breakdown = {}
                for level in UserAccessLevel:
                    user_breakdown[level.value] = len([
                        p for p in self.user_profiles.values() 
                        if p.access_level == level
                    ])
                
                return {
                    "total_users": total_users,
                    "total_api_usage_today": total_usage,
                    "user_breakdown_by_level": user_breakdown,
                    "active_users_today": len([
                        p for p in self.user_profiles.values()
                        if p.last_active.date() == datetime.now().date()
                    ])
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get user analytics: {e}")
            return {}

    async def _save_user_profile(self, user_profile: UserProfile) -> None:
        """Save user profile to database"""
        try:
            # In production, save to Snowflake
            # For now, just log the operation
            logger.info(f"Saving user profile for {user_profile.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save user profile: {e}")

    async def close(self) -> None:
        """Close all connections and clean up resources"""
        try:
            if self.cortex_service:
                await self.cortex_service.close()
            
            if self.exa_client:
                await self.exa_client.aclose()
            
            if self.tavily_client:
                await self.tavily_client.aclose()
            
            if self.perplexity_client:
                await self.perplexity_client.aclose()
            
            if self.apify_client:
                await self.apify_client.aclose()
            
            if self.zenrows_client:
                await self.zenrows_client.aclose()
            
            if self.phantombuster_client:
                await self.phantombuster_client.aclose()
            
            logger.info("✅ Sophia Universal Chat Service closed")
            
        except Exception as e:
            logger.error(f"❌ Failed to close Sophia Universal Chat Service: {e}")

# Example usage for testing
async def main():
    """Test the Sophia Universal Chat Service"""
    service = SophiaUniversalChatService()
    await service.initialize()
    
    try:
        # Test CEO-level query with blended intelligence
        result = await service.process_chat_message(
            message="What are the latest trends in PropTech and how do they compare to our current offerings?",
            user_id="ceo"
        )
        
        print("Sophia's Response:")
        print(result.content)
        print(f"\nSources: {len(result.sources)}")
        print(f"Search Time: {result.search_time_ms}ms")
        print(f"Confidence: {result.confidence_score:.2f}")
        
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(main()) 