"""
Unified Chat Service - The Brain of Sophia AI
Provides dynamic, contextualized access to the entire ecosystem
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from backend.core.context_analyzer import ContextAnalyzer
from backend.core.llm_router import LLMRouter
from backend.services.ai_memory_service import AIMemoryService
from backend.services.asana_service import AsanaService
from backend.services.gong_service import GongService
from backend.services.hubspot_service import HubSpotService
from backend.services.knowledge_service import KnowledgeService

# Add Lambda Labs imports
from backend.services.lambda_labs_service import LambdaLabsService
from backend.services.linear_service import LinearService
from backend.services.mcp_orchestration_service import MCPOrchestrationService
from backend.services.notion_service import NotionService
from backend.services.slack_service import SlackService
from backend.services.snowflake_cortex_service import SnowflakeCortexService
from backend.services.web_search_service import WebSearchService
from infrastructure.services.llm_router import TaskComplexity

# NEW: Unified AI Orchestrator
from infrastructure.services.unified_ai_orchestrator import (
    AIProvider,
    AIRequest,
    UnifiedAIOrchestrator,
)

logger = logging.getLogger(__name__)


@dataclass
class QueryContext:
    """Represents the context of a user query"""

    intent: str
    entities: list[dict[str, Any]]
    time_range: Optional[tuple[datetime, datetime]]
    sources_needed: list[str]
    confidence: float
    user_role: str
    session_history: list[dict[str, Any]]
    requires_orchestration: bool = False
    orchestration_type: Optional[str] = None


@dataclass
class OrchestrationState:
    """State for LangGraph orchestration"""

    query: str
    context: QueryContext
    source_data: dict[str, Any]
    memory_context: dict[str, Any]
    web_context: Optional[dict[str, Any]]
    synthesis_result: Optional[str] = None
    citations: list[dict[str, Any]] = None
    confidence: float = 0.0


class UnifiedChatService:
    """
    The core intelligence service that provides dynamic, contextualized access
    to the entire Sophia AI ecosystem including:
    - All databases (Snowflake, AI Memory)
    - All integrations (Gong, Slack, Linear, Asana, Notion, HubSpot)
    - Web search and external data
    - Real-time system status
    - Multi-agent orchestration via LangGraph
    """

    def __init__(self):
        # Core AI services
        self.cortex = SnowflakeCortexService()
        self.ai_memory = AIMemoryService()
        self.llm_router = LLMRouter()
        self.context_analyzer = ContextAnalyzer()
        self.mcp_orchestrator = MCPOrchestrationService()

        # Lambda Labs integration
        self.lambda_labs = LambdaLabsService()

        # NEW: Unified AI Orchestrator
        self.ai_orchestrator = UnifiedAIOrchestrator()

        # Data source services
        self.knowledge = KnowledgeService()
        self.gong = GongService()
        self.slack = SlackService()
        self.linear = LinearService()
        self.asana = AsanaService()
        self.notion = NotionService()
        self.hubspot = HubSpotService()
        self.web_search = WebSearchService()

        # Service mapping for dynamic routing
        self.service_map = {
            "knowledge": self.knowledge,
            "sales_calls": self.gong,
            "team_communication": self.slack,
            "engineering_tasks": self.linear,
            "product_tasks": self.asana,
            "documentation": self.notion,
            "crm": self.hubspot,
            "web": self.web_search,
            "database": self.cortex,
            "memory": self.ai_memory,
            "lambda_labs": self.lambda_labs,  # Add Lambda Labs to service map
        }

        # Routing configuration
        self.routing_config = {
            "serverless_first": True,
            "gpu_fallback": True,
            "cost_optimization": True,
        }

        # Initialize LangGraph workflow
        self.workflow = self._build_orchestration_workflow()

    def _build_orchestration_workflow(self) -> CompiledStateGraph:
        """Build LangGraph workflow for complex orchestration"""
        workflow = StateGraph(OrchestrationState)

        # Add nodes
        workflow.add_node("analyze_context", self._analyze_context_node)
        workflow.add_node("fetch_data", self._fetch_data_node)
        workflow.add_node("get_memory", self._get_memory_node)
        workflow.add_node("search_web", self._search_web_node)
        workflow.add_node("synthesize", self._synthesize_node)
        workflow.add_node("validate_quality", self._validate_quality_node)

        # Add edges
        workflow.set_entry_point("analyze_context")
        workflow.add_edge("analyze_context", "fetch_data")
        workflow.add_edge("fetch_data", "get_memory")
        workflow.add_edge("get_memory", "search_web")
        workflow.add_edge("search_web", "synthesize")
        workflow.add_edge("synthesize", "validate_quality")
        workflow.add_edge("validate_quality", END)

        return workflow.compile()

    async def process_unified_query(
        self, query: str, user_id: str, session_id: str, context: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Process a query with full ecosystem access

        This is the magic - it understands the query, determines what data sources
        are needed, fetches from multiple sources in parallel, and synthesizes
        a comprehensive response with citations.
        """

        # 1. Analyze query context and intent
        query_context = await self._analyze_query_context(
            query, user_id, session_id, context
        )

        # 2. Check if this requires multi-agent orchestration
        if query_context.requires_orchestration:
            return await self._process_with_orchestration(
                query, query_context, user_id, session_id
            )

        # 3. Standard processing for simpler queries
        return await self._process_standard_query(
            query, query_context, user_id, session_id
        )

    async def _process_with_orchestration(
        self, query: str, query_context: QueryContext, user_id: str, session_id: str
    ) -> dict[str, Any]:
        """Process complex queries using LangGraph orchestration"""

        # Initialize state
        initial_state = OrchestrationState(
            query=query,
            context=query_context,
            source_data={},
            memory_context={},
            web_context=None,
        )

        # Run the workflow
        final_state = await self.workflow.ainvoke(initial_state)

        # Store interaction
        await self._store_interaction(
            query=query,
            response={
                "response": final_state.synthesis_result,
                "citations": final_state.citations,
                "confidence": final_state.confidence,
            },
            context=query_context,
            user_id=user_id,
            session_id=session_id,
        )

        return {
            "response": final_state.synthesis_result,
            "citations": final_state.citations,
            "confidence": final_state.confidence,
            "intent": query_context.intent,
            "data_sources_used": list(final_state.source_data.keys()),
            "orchestration_type": query_context.orchestration_type,
            "metadata": {
                "processing_time": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "session_id": session_id,
            },
        }

    async def _process_standard_query(
        self, query: str, query_context: QueryContext, user_id: str, session_id: str
    ) -> dict[str, Any]:
        """Process standard queries without orchestration"""

        # 2. Fetch relevant data from all needed sources in parallel
        source_data = await self._fetch_multi_source_data(query_context)

        # 3. Search for relevant past conversations and insights
        memory_context = await self._get_memory_context(query, query_context)

        # 4. If needed, search the web for additional context
        web_context = None
        if self._needs_web_search(query_context):
            web_context = await self._search_web(query, query_context)

        # 5. Synthesize response using the most appropriate AI model
        response = await self._synthesize_response(
            query_context=query_context,
            source_data=source_data,
            user_id=user_id,
        )

        # 6. Store this interaction for future learning
        await self._store_interaction(
            query=query,
            response=response,
            context=query_context,
            user_id=user_id,
            session_id=session_id,
        )

        return response

    # LangGraph node implementations
    async def _analyze_context_node(
        self, state: OrchestrationState
    ) -> OrchestrationState:
        """Analyze context in orchestration"""
        # Context is already analyzed, just pass through
        return state

    async def _fetch_data_node(self, state: OrchestrationState) -> OrchestrationState:
        """Fetch data from multiple sources"""
        state.source_data = await self._fetch_multi_source_data(state.context)
        return state

    async def _get_memory_node(self, state: OrchestrationState) -> OrchestrationState:
        """Get memory context"""
        state.memory_context = await self._get_memory_context(
            state.query, state.context
        )
        return state

    async def _search_web_node(self, state: OrchestrationState) -> OrchestrationState:
        """Search web if needed"""
        if self._needs_web_search(state.context):
            state.web_context = await self._search_web(state.query, state.context)
        return state

    async def _synthesize_node(self, state: OrchestrationState) -> OrchestrationState:
        """Synthesize final response"""
        response = await self._synthesize_response(
            query_context=state.context,
            source_data=state.source_data,
            user_id="orchestration",
        )

        state.synthesis_result = response["response"]
        state.citations = response["citations"]
        state.confidence = response["confidence"]

        return state

    async def _validate_quality_node(
        self, state: OrchestrationState
    ) -> OrchestrationState:
        """Validate response quality"""
        # Could add additional quality checks here
        return state

    async def _analyze_query_context(
        self, query: str, user_id: str, session_id: str, context: Optional[str] = None
    ) -> QueryContext:
        """
        Use AI to understand the query intent and determine what sources are needed
        """
        # Get session history for context
        session_history = await self.ai_memory.get_session_history(session_id)

        # Use Snowflake Cortex for fast intent classification
        analysis = await self.cortex.analyze_query_intent(
            query=query, session_history=session_history, user_context=context
        )

        # Determine which data sources are needed
        sources_needed = self._determine_data_sources(
            analysis["intent"], analysis["entities"]
        )

        # Check if this requires orchestration
        requires_orchestration = self._requires_orchestration(analysis)
        orchestration_type = (
            self._get_orchestration_type(analysis) if requires_orchestration else None
        )

        return QueryContext(
            intent=analysis["intent"],
            entities=analysis["entities"],
            time_range=self._extract_time_range(analysis),
            sources_needed=sources_needed,
            confidence=analysis["confidence"],
            user_role=await self._get_user_role(user_id),
            session_history=session_history,
            requires_orchestration=requires_orchestration,
            orchestration_type=orchestration_type,
        )

    def _requires_orchestration(self, analysis: dict) -> bool:
        """Determine if query requires multi-agent orchestration"""
        orchestration_indicators = [
            "complex_analysis",
            "multi_source_synthesis",
            "strategic_planning",
            "cross_functional_insights",
            "predictive_modeling",
        ]

        intent = analysis.get("intent", "").lower()
        return any(indicator in intent for indicator in orchestration_indicators)

    def _get_orchestration_type(self, analysis: dict) -> str:
        """Get the type of orchestration needed"""
        intent = analysis.get("intent", "").lower()

        if "strategic" in intent or "planning" in intent:
            return "business_intelligence"
        elif "development" in intent or "code" in intent:
            return "development"
        elif "infrastructure" in intent or "deployment" in intent:
            return "infrastructure"
        else:
            return "general"

    async def _fetch_multi_source_data(self, context: QueryContext) -> dict[str, Any]:
        """
        Fetch data from multiple sources in parallel based on query context
        """
        tasks = {}

        # Create parallel tasks for each needed source
        for source in context.sources_needed:
            if source == "sales_calls" and context.entities:
                tasks["gong_data"] = self.gong.search_calls(
                    entities=context.entities, time_range=context.time_range
                )

            elif source == "team_communication":
                tasks["slack_data"] = self.slack.search_conversations(
                    query_entities=context.entities, time_range=context.time_range
                )

            elif source == "engineering_tasks":
                tasks["linear_data"] = self.linear.get_relevant_issues(
                    entities=context.entities, include_completed=True
                )

            elif source == "product_tasks":
                tasks["asana_data"] = self.asana.get_relevant_tasks(
                    entities=context.entities, time_range=context.time_range
                )

            elif source == "documentation":
                tasks["notion_data"] = self.notion.search_pages(
                    entities=context.entities
                )

            elif source == "crm":
                tasks["hubspot_data"] = self.hubspot.get_relevant_data(
                    entities=context.entities,
                    data_types=["contacts", "deals", "companies"],
                )

            elif source == "knowledge":
                tasks["knowledge_data"] = self.knowledge.semantic_search(
                    query=context.intent, entities=context.entities
                )

            elif source == "database":
                tasks["database_data"] = self.cortex.execute_business_query(
                    intent=context.intent,
                    entities=context.entities,
                    time_range=context.time_range,
                )

        # Execute all tasks in parallel
        if tasks:
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            return dict(zip(tasks.keys(), results, strict=False))

        return {}

    async def _get_memory_context(
        self, query: str, context: QueryContext
    ) -> dict[str, Any]:
        """
        Retrieve relevant past conversations and insights from AI Memory
        """
        # Search for similar past queries
        similar_queries = await self.ai_memory.find_similar_queries(
            query=query, limit=5, user_role=context.user_role
        )

        # Get relevant insights based on entities
        entity_insights = []
        for entity in context.entities:
            insights = await self.ai_memory.get_entity_insights(
                entity_type=entity["type"], entity_value=entity["value"]
            )
            entity_insights.extend(insights)

        # Get time-based patterns if time range is specified
        time_patterns = None
        if context.time_range:
            time_patterns = await self.ai_memory.get_time_patterns(
                time_range=context.time_range, intent=context.intent
            )

        return {
            "similar_queries": similar_queries,
            "entity_insights": entity_insights,
            "time_patterns": time_patterns,
        }

    def _needs_web_search(self, context: QueryContext) -> bool:
        """
        Determine if web search is needed based on query context
        """
        web_indicators = [
            "competitor",
            "market",
            "industry",
            "trend",
            "news",
            "latest",
            "current",
            "today",
            "external",
            "benchmark",
        ]

        # Check if any web indicators are in the intent or entities
        intent_lower = context.intent.lower()
        for indicator in web_indicators:
            if indicator in intent_lower:
                return True

        for entity in context.entities:
            if entity.get("type") in ["competitor", "industry", "market"]:
                return True

        return False

    async def _search_web(self, query: str, context: QueryContext) -> dict[str, Any]:
        """
        Search the web for additional context
        """
        # Construct optimized search query based on entities
        search_query = self._construct_web_search_query(query, context)

        # Perform web search
        web_results = await self.web_search.search(query=search_query, num_results=5)

        # Extract and summarize relevant information
        summaries = []
        for result in web_results:
            summary = await self.cortex.summarize_web_content(
                content=result["content"], context=query
            )
            summaries.append(
                {
                    "source": result["url"],
                    "title": result["title"],
                    "summary": summary,
                    "relevance_score": result.get("relevance_score", 0.5),
                }
            )

        return {
            "search_query": search_query,
            "results": summaries,
            "search_timestamp": datetime.utcnow().isoformat(),
        }

    async def _synthesize_response(
        self,
        query_context: QueryContext,
        source_data: dict[str, Any],
        user_id: str,
    ) -> dict[str, Any]:
        """
        Synthesize response from multiple data sources using unified AI
        """
        # Build synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(query_context, source_data)

        # NEW: Use unified AI orchestrator for intelligent routing
        ai_request = AIRequest(
            prompt=synthesis_prompt,
            provider=AIProvider.AUTO,  # Let orchestrator decide
            use_case="reasoning"
            if query_context.intent == "complex_analysis"
            else "general",
            complexity=TaskComplexity.COMPLEX
            if len(source_data) > 3
            else TaskComplexity.MODERATE,
            cost_priority="balanced",
            context={
                "intent": query_context.intent,
                "sources": list(source_data.keys()),
                "user_id": user_id,
            },
        )

        # Get AI response
        ai_response = await self.ai_orchestrator.process_request(ai_request)

        if not ai_response.success:
            # Fallback to Lambda Labs directly
            logger.warning(
                f"Orchestrator failed, using Lambda Labs fallback: {ai_response.error}"
            )
            llm_response = await self.lambda_labs.simple_inference(
                synthesis_prompt, complexity="balanced"
            )
            model_info = {"name": "lambda_labs_fallback", "provider": "lambda_labs"}
        else:
            llm_response = ai_response.response
            model_info = {
                "name": ai_response.model,
                "provider": ai_response.provider,
                "duration": ai_response.duration,
                "cost": ai_response.cost_estimate,
            }

        # Extract citations
        citations = self._extract_citations(source_data)

        # Calculate confidence
        confidence = self._calculate_confidence(
            query_context, source_data, llm_response
        )

        return {
            "response": llm_response,
            "citations": citations,
            "confidence": confidence,
            "intent": query_context.intent,
            "data_sources_used": list(source_data.keys()),
            "model_used": model_info["name"],
            "ai_provider": model_info.get("provider", "unknown"),
            "metadata": {
                "processing_time": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "session_id": (
                    query_context.session_history[0].get("session_id")
                    if query_context.session_history
                    else None
                ),
                "ai_metrics": {
                    "duration": model_info.get("duration", 0),
                    "cost_estimate": model_info.get("cost", 0),
                },
            },
        }

    def _determine_data_sources(self, intent: str, entities: list[dict]) -> list[str]:
        """
        Intelligently determine which data sources to query
        """
        sources = set()

        # Intent-based source selection
        intent_source_map = {
            "sales_analysis": ["sales_calls", "crm", "database"],
            "project_status": [
                "engineering_tasks",
                "product_tasks",
                "team_communication",
            ],
            "team_performance": [
                "engineering_tasks",
                "product_tasks",
                "team_communication",
                "database",
            ],
            "customer_insights": [
                "sales_calls",
                "crm",
                "team_communication",
                "knowledge",
            ],
            "competitive_analysis": ["web", "sales_calls", "knowledge"],
            "financial_metrics": ["database", "crm"],
            "product_roadmap": ["product_tasks", "documentation", "engineering_tasks"],
            "technical_question": ["documentation", "knowledge", "engineering_tasks"],
            "general_search": ["knowledge", "memory"],
        }

        # Add sources based on intent
        if intent in intent_source_map:
            sources.update(intent_source_map[intent])
        else:
            # Default to knowledge and memory for unknown intents
            sources.update(["knowledge", "memory"])

        # Entity-based source selection
        for entity in entities:
            entity_type = entity.get("type", "").lower()

            if entity_type in ["customer", "contact", "company"]:
                sources.update(["crm", "sales_calls"])
            elif entity_type in ["project", "task", "issue"]:
                sources.update(["engineering_tasks", "product_tasks"])
            elif entity_type in ["employee", "team", "person"]:
                sources.update(
                    ["team_communication", "engineering_tasks", "product_tasks"]
                )
            elif entity_type in ["competitor", "market", "industry"]:
                sources.add("web")
            elif entity_type in ["metric", "kpi", "number"]:
                sources.add("database")

        return list(sources)

    def _extract_time_range(
        self, analysis: dict
    ) -> Optional[tuple[datetime, datetime]]:
        """
        Extract time range from query analysis
        """
        # Implementation would parse time-related entities
        # For now, return None
        return None

    async def _get_user_role(self, user_id: str) -> str:
        """
        Get user role for permission-based filtering
        """
        # In production, this would query the user service
        # For now, return a default
        return "executive"

    def _construct_web_search_query(self, query: str, context: QueryContext) -> str:
        """
        Construct an optimized web search query
        """
        # Start with the base query
        search_parts = [query]

        # Add relevant entity names
        for entity in context.entities[:3]:  # Limit to top 3 entities
            if entity.get("value"):
                search_parts.append(f'"{entity["value"]}"')

        # Add industry context if available
        if any(e.get("type") == "industry" for e in context.entities):
            search_parts.append("industry analysis")

        return " ".join(search_parts)

    def _get_synthesis_prompt(self, context: QueryContext) -> str:
        """
        Get the appropriate synthesis prompt based on context
        """
        base_prompt = """You are Sophia AI, an executive intelligence assistant with access to the entire company ecosystem.

Your role is to provide comprehensive, actionable insights by synthesizing information from multiple sources.

Guidelines:
1. Be concise but thorough
2. Prioritize actionable insights
3. Cite sources when making claims
4. Highlight any risks or concerns
5. Provide specific recommendations when appropriate
6. Use business language appropriate for executives

User Role: {user_role}
Query Intent: {intent}

Synthesize the provided data into a clear, insightful response."""

        return base_prompt.format(user_role=context.user_role, intent=context.intent)

    def _assess_complexity(self, context: dict) -> str:
        """
        Assess query complexity for model selection
        """
        # Count data sources
        source_count = len([v for v in context.get("source_data", {}).values() if v])

        # Check for multi-entity queries
        entity_count = len(context.get("entities", []))

        # Check for time-series analysis
        has_time_analysis = bool(
            context.get("memory_insights", {}).get("time_patterns")
        )

        # Determine complexity
        if source_count > 3 or entity_count > 5 or has_time_analysis:
            return "high"
        elif source_count > 1 or entity_count > 2:
            return "medium"
        else:
            return "low"

    def _extract_citations(
        self,
        source_data: dict[str, Any],
        memory_context: dict[str, Any],
        web_context: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Extract and format citations from all data sources
        """
        citations = []

        # Extract from source data
        for source_name, data in source_data.items():
            if data and not isinstance(data, Exception):
                if isinstance(data, list):
                    for item in data[:3]:  # Limit citations per source
                        citations.append(
                            {
                                "source": source_name,
                                "title": self._get_citation_title(item, source_name),
                                "confidence": 0.9,
                            }
                        )
                elif isinstance(data, dict) and "results" in data:
                    for result in data["results"][:3]:
                        citations.append(
                            {
                                "source": source_name,
                                "title": self._get_citation_title(result, source_name),
                                "confidence": 0.9,
                            }
                        )

        # Add memory citations
        if memory_context.get("similar_queries"):
            citations.append(
                {
                    "source": "ai_memory",
                    "title": f"Similar insights from {len(memory_context['similar_queries'])} past queries",
                    "confidence": 0.8,
                }
            )

        # Add web citations
        if web_context and web_context.get("results"):
            for result in web_context["results"][:2]:
                citations.append(
                    {
                        "source": "web",
                        "title": result["title"],
                        "url": result.get("source"),
                        "confidence": result.get("relevance_score", 0.7),
                    }
                )

        return citations

    def _get_citation_title(self, item: Any, source: str) -> str:
        """
        Extract appropriate title from different source types
        """
        if isinstance(item, dict):
            # Try common title fields
            for field in ["title", "name", "subject", "summary", "id"]:
                if field in item:
                    return str(item[field])

        # Default titles by source
        default_titles = {
            "gong_data": "Sales call transcript",
            "slack_data": "Team conversation",
            "linear_data": "Engineering task",
            "asana_data": "Product task",
            "notion_data": "Documentation page",
            "hubspot_data": "CRM record",
            "knowledge_data": "Knowledge base entry",
            "database_data": "Database query result",
        }

        return default_titles.get(source, "Data source")

    def _calculate_response_confidence(
        self,
        source_data: dict[str, Any],
        memory_context: dict[str, Any],
        web_context: Optional[dict[str, Any]],
        query_context: QueryContext,
    ) -> float:
        """
        Calculate confidence score for the response
        """
        confidence_factors = []

        # Factor 1: Data source availability (40%)
        sources_requested = len(query_context.sources_needed)
        sources_fulfilled = len(
            [v for v in source_data.values() if v and not isinstance(v, Exception)]
        )
        if sources_requested > 0:
            confidence_factors.append(0.4 * (sources_fulfilled / sources_requested))
        else:
            confidence_factors.append(0.4)

        # Factor 2: Query understanding confidence (30%)
        confidence_factors.append(0.3 * query_context.confidence)

        # Factor 3: Historical context availability (20%)
        has_similar_queries = bool(memory_context.get("similar_queries"))
        has_entity_insights = bool(memory_context.get("entity_insights"))
        memory_score = (0.5 if has_similar_queries else 0) + (
            0.5 if has_entity_insights else 0
        )
        confidence_factors.append(0.2 * memory_score)

        # Factor 4: Data recency (10%)
        # In production, would check timestamps of data
        confidence_factors.append(0.1 * 0.9)  # Assume 90% recency for now

        return sum(confidence_factors)

    async def _store_interaction(
        self,
        query: str,
        response: dict[str, Any],
        context: QueryContext,
        user_id: str,
        session_id: str,
    ) -> None:
        """
        Store the interaction for future learning and context
        """
        interaction = {
            "query": query,
            "response": response["response"],
            "intent": context.intent,
            "entities": context.entities,
            "sources_used": response.get("data_sources_used", []),
            "confidence": response.get("confidence", 0),
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in AI Memory for future retrieval
        await self.ai_memory.store_interaction(interaction)

        # Update entity insights if high confidence
        if response.get("confidence", 0) > 0.8:
            for entity in context.entities:
                await self.ai_memory.update_entity_insight(
                    entity_type=entity["type"],
                    entity_value=entity["value"],
                    insight=response["response"],
                    confidence=response["confidence"],
                )

    async def process_message_with_lambda(
        self, message: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Process message using Lambda Labs serverless inference with intelligent routing"""

        try:
            # Classify message for optimal routing
            classification = await self._classify_message(message, context)

            # Route based on classification
            if classification["requires_gpu"]:
                return await self._route_to_gpu_instance(message, context)
            else:
                return await self._route_to_serverless(message, context, classification)

        except Exception as e:
            return {
                "response": f"Lambda Labs inference failed: {e!s}",
                "success": False,
                "provider": "lambda_labs",
                "fallback_available": True,
            }

    async def _classify_message(
        self, message: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Classify message for optimal routing and model selection"""

        message_lower = message.lower()

        # GPU-required indicators
        gpu_indicators = [
            "train model",
            "fine-tune",
            "large dataset",
            "batch processing",
            "custom model",
            "specialized training",
            "research experiment",
        ]

        requires_gpu = any(indicator in message_lower for indicator in gpu_indicators)

        # Complexity analysis
        complexity_indicators = {
            "simple": ["quick", "brief", "short", "list", "summarize"],
            "complex": [
                "analyze",
                "detailed",
                "comprehensive",
                "research",
                "reasoning",
            ],
        }

        complexity = "balanced"  # default
        for level, indicators in complexity_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                complexity = level
                break

        return {
            "requires_gpu": requires_gpu,
            "complexity": complexity,
            "estimated_tokens": len(message) * 1.5,  # rough estimation
            "priority": "normal",
        }

    async def _route_to_serverless(
        self, message: str, context: dict, classification: dict
    ) -> dict[str, Any]:
        """Route to Lambda Labs serverless with optimization"""

        # Prepare enhanced context
        messages = []
        if context:
            system_context = f"Context: {json.dumps(context, indent=2)}"
            messages.append({"role": "system", "content": system_context})

        messages.append({"role": "user", "content": message})

        # Select optimal model based on classification
        model = self.lambda_labs.select_optimal_model(
            message, classification["complexity"]
        )

        # Execute inference
        result = await self.lambda_labs.chat_completion(
            messages=messages,
            model=model,
            max_tokens=min(500, int(classification["estimated_tokens"] * 2)),
        )

        return {
            "response": result["choices"][0]["message"]["content"],
            "model_used": model,
            "usage": result.get("usage", {}),
            "provider": "lambda_labs_serverless",
            "classification": classification,
            "success": True,
        }

    async def _route_to_gpu_instance(
        self, message: str, context: dict
    ) -> dict[str, Any]:
        """Route to GPU instance for specialized workloads"""

        # This would integrate with existing GPU instance management
        # For now, return a placeholder indicating GPU routing
        return {
            "response": "GPU instance routing not yet implemented. Using serverless fallback.",
            "provider": "lambda_labs_gpu",
            "success": False,
            "fallback_to_serverless": True,
        }

    async def natural_language_control(
        self, command: str, user_id: str
    ) -> dict[str, Any]:
        """
        Process natural language infrastructure control commands
        """
        # Use orchestrator for optimization commands
        if any(
            kw in command.lower()
            for kw in ["optimize", "reduce cost", "improve performance"]
        ):
            optimization_result = (
                await self.ai_orchestrator.natural_language_optimization(command)
            )

            return {
                "type": "infrastructure_optimization",
                "command": command,
                "result": optimization_result,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Regular query processing
        return await self.process_query(command, user_id)
