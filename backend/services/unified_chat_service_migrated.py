"""
Enhanced Unified Chat Service with CortexGateway Integration
Migrated from direct Snowflake connections to unified gateway pattern
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

# New import - CortexGateway
from core.infra.cortex_gateway import get_gateway

# Existing imports that still work
from core.services.foundational_knowledge_service import FoundationalKnowledgeService
from infrastructure.services.ai_memory_service import AIMemoryService
from infrastructure.services.web_search_service import WebSearchService

logger = logging.getLogger(__name__)


class QueryIntent(str, Enum):
    """Types of query intents for routing"""

    BUSINESS_INTELLIGENCE = "business_intelligence"
    KNOWLEDGE_SEARCH = "knowledge_search"
    WEB_SEARCH = "web_search"
    MEMORY_RECALL = "memory_recall"
    GENERAL_CHAT = "general_chat"
    SQL_QUERY = "sql_query"


class UnifiedChatRequest(BaseModel):
    """Unified chat request model"""

    message: str = Field(..., description="User message")
    context: Optional[dict[str, Any]] = Field(
        default=None, description="Additional context"
    )
    use_knowledge: bool = Field(default=True, description="Search knowledge base")
    use_memory: bool = Field(default=True, description="Use AI memory")
    use_web: bool = Field(default=False, description="Search web if needed")
    stream: bool = Field(default=False, description="Stream response")


class UnifiedChatResponse(BaseModel):
    """Unified chat response model"""

    response: str
    sources: list[dict[str, Any]] = []
    intent: QueryIntent
    processing_time: float
    metadata: dict[str, Any] = {}


class UnifiedChatService:
    """
    Unified chat service with CortexGateway integration.
    Migrated from direct Snowflake connections to use centralized gateway.
    """

    def __init__(self):
        # Initialize CortexGateway
        self.gateway = get_gateway()

        # Initialize other services
        self.knowledge_service = FoundationalKnowledgeService()
        self.memory_service = AIMemoryService()
        self.web_search_service = WebSearchService()

        # Cache for performance
        self._intent_cache = {}

    async def initialize(self):
        """Initialize all services"""
        await self.gateway.initialize()
        await self.knowledge_service.initialize()
        await self.memory_service.initialize()
        logger.info("✅ UnifiedChatService initialized with CortexGateway")

    async def _classify_intent(self, message: str) -> QueryIntent:
        """Classify user intent using Cortex"""
        # Check cache first
        cache_key = hash(message.lower().strip())
        if cache_key in self._intent_cache:
            return self._intent_cache[cache_key]

        prompt = f"""
        Classify the following user message into one of these categories:
        - business_intelligence: Questions about sales, revenue, customers, metrics
        - knowledge_search: Questions about internal knowledge, documentation
        - web_search: Questions requiring current web information
        - memory_recall: Questions about previous conversations or context
        - sql_query: Direct SQL or database queries
        - general_chat: General conversation

        Message: {message}

        Return only the category name.
        """

        # Use CortexGateway instead of direct connection
        result = await self.gateway.complete(prompt, model="mixtral-8x7b")

        intent = QueryIntent.GENERAL_CHAT
        for intent_type in QueryIntent:
            if intent_type.value in result.lower():
                intent = intent_type
                break

        # Cache result
        self._intent_cache[cache_key] = intent
        return intent

    async def _fetch_business_data(self, query: str) -> list[dict[str, Any]]:
        """Fetch business data using CortexGateway"""
        # First, translate natural language to SQL
        sql_prompt = f"""
        Convert this business question to a SQL query for our data warehouse:
        Question: {query}

        Available tables:
        - SALES.TRANSACTIONS (date, amount, customer_id, product_id)
        - CUSTOMERS.PROFILES (customer_id, name, segment, lifetime_value)
        - PRODUCTS.CATALOG (product_id, name, category, price)

        Return only the SQL query.
        """

        sql_query = await self.gateway.complete(sql_prompt, model="mixtral-8x7b")

        # Execute the generated SQL
        try:
            results = await self.gateway.execute_sql(sql_query)
            return results
        except Exception as e:
            logger.error(f"Error executing business query: {e}")
            return []

    async def _search_knowledge(self, query: str) -> list[dict[str, Any]]:
        """Search knowledge base using embeddings"""
        # Generate embedding for the query
        await self.gateway.embed(query)

        # Search using vector similarity
        search_sql = """
        SELECT
            content,
            title,
            VECTOR_COSINE_SIMILARITY(embedding, %s::VECTOR(FLOAT, 768)) as similarity
        FROM KNOWLEDGE.DOCUMENTS
        WHERE similarity > 0.7
        ORDER BY similarity DESC
        LIMIT 5
        """

        results = await self.gateway.execute_sql(search_sql)
        return results

    async def _generate_response(
        self, message: str, intent: QueryIntent, context_data: list[dict[str, Any]]
    ) -> str:
        """Generate response using Cortex with context"""

        # Build context prompt
        context_str = ""
        if context_data:
            context_str = "\n\nRelevant context:\n"
            for item in context_data[:3]:  # Limit context size
                if isinstance(item, dict):
                    context_str += f"- {json.dumps(item, default=str)}\n"
                else:
                    context_str += f"- {item!s}\n"

        prompt = f"""
        User question: {message}
        Intent: {intent.value}
        {context_str}

        Please provide a helpful, accurate response based on the context provided.
        If the context doesn't contain relevant information, say so.
        """

        # Use CortexGateway for completion
        response = await self.gateway.complete(prompt, model="llama2-70b-chat")
        return response

    async def process_message(self, request: UnifiedChatRequest) -> UnifiedChatResponse:
        """Process a chat message with unified intelligence"""
        start_time = datetime.now()

        try:
            # Classify intent
            intent = await self._classify_intent(request.message)
            logger.info(f"Classified intent: {intent.value}")

            # Gather context based on intent
            context_data = []
            sources = []

            # Parallel data fetching using asyncio.gather
            tasks = []

            if intent == QueryIntent.BUSINESS_INTELLIGENCE:
                tasks.append(self._fetch_business_data(request.message))
                sources.append({"type": "business_data", "name": "Snowflake DW"})

            if request.use_knowledge and intent in [
                QueryIntent.KNOWLEDGE_SEARCH,
                QueryIntent.GENERAL_CHAT,
            ]:
                tasks.append(self._search_knowledge(request.message))
                sources.append({"type": "knowledge", "name": "Knowledge Base"})

            if request.use_memory:
                tasks.append(self.memory_service.recall_relevant(request.message))
                sources.append({"type": "memory", "name": "AI Memory"})

            if request.use_web and intent == QueryIntent.WEB_SEARCH:
                tasks.append(self.web_search_service.search(request.message))
                sources.append({"type": "web", "name": "Web Search"})

            # Execute all tasks in parallel
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if not isinstance(result, Exception):
                        context_data.extend(
                            result if isinstance(result, list) else [result]
                        )

            # Generate response with context
            response = await self._generate_response(
                request.message, intent, context_data
            )

            # Store in memory if significant
            if request.use_memory and len(response) > 100:
                await self.memory_service.store(
                    content=f"Q: {request.message}\nA: {response}",
                    category="chat_history",
                    metadata={"intent": intent.value},
                )

            processing_time = (datetime.now() - start_time).total_seconds()

            return UnifiedChatResponse(
                response=response,
                sources=sources,
                intent=intent,
                processing_time=processing_time,
                metadata={
                    "context_items": len(context_data),
                    "model": "llama2-70b-chat",
                    "gateway": "CortexGateway",
                },
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()

            return UnifiedChatResponse(
                response=f"I apologize, but I encountered an error processing your request: {e!s}",
                sources=[],
                intent=QueryIntent.GENERAL_CHAT,
                processing_time=processing_time,
                metadata={"error": str(e)},
            )

    async def process_message_stream(
        self, request: UnifiedChatRequest
    ) -> AsyncIterator[str]:
        """Process message with streaming response"""
        # For now, just yield the full response
        # TODO: Implement true streaming with CortexGateway
        response = await self.process_message(request)
        yield response.response

    async def health_check(self) -> dict[str, Any]:
        """Check health of all services"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {},
        }

        # Check CortexGateway
        gateway_health = await self.gateway.health_check()
        health["services"]["cortex_gateway"] = gateway_health

        # Check other services
        health["services"]["knowledge"] = "healthy"  # Simplified for now
        health["services"]["memory"] = "healthy"
        health["services"]["web_search"] = "healthy"

        # Overall status
        if any(s.get("status") == "unhealthy" for s in health["services"].values()):
            health["status"] = "degraded"

        return health


# Migration notes:
# 1. Replaced all direct snowflake.connector.connect() calls with gateway methods
# 2. Changed SnowflakeCortexService usage to gateway.complete(), gateway.embed()
# 3. Simplified SQL execution using gateway.execute_sql()
# 4. Added proper error handling and health checks
# 5. Maintained backward compatibility with existing API
