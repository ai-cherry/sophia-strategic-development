"""
Unified Chat Service - Simplified HTTP-based MCP Integration
Provides dynamic, contextualized access to MCP servers via HTTP
Enhanced with temporal learning capabilities
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import aiohttp

# Try to import temporal learning service
try:
    from backend.services.temporal_qa_learning_service import (
        get_temporal_qa_learning_service,
    )

    TEMPORAL_LEARNING_AVAILABLE = True
except ImportError:
    TEMPORAL_LEARNING_AVAILABLE = False

logger = logging.getLogger(__name__)

# Log temporal learning availability after logger is defined
if not TEMPORAL_LEARNING_AVAILABLE:
    logger.warning("Temporal learning service not available")

# MCP Server Configuration
MCP_SERVERS = {
    "asana": {
        "url": "http://localhost:9100",
        "description": "Task and project management",
    },
    "notion": {
        "url": "http://localhost:9102",
        "description": "Knowledge base and documentation",
    },
    "slack": {
        "url": "http://localhost:9103",
        "description": "Team communication and updates",
    },
    "snowflake": {
        "url": "http://localhost:9104",
        "description": "Data analytics and reporting",
    },
    "hubspot": {
        "url": "http://localhost:9105",
        "description": "CRM and sales insights",
    },
    "gong": {
        "url": "http://localhost:9106",
        "description": "Call analysis and insights",
    },
}


@dataclass
class QueryContext:
    """Context for query processing"""

    intent: str
    sources_needed: list[str]
    confidence: float
    temporal_context: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.temporal_context is None:
            self.temporal_context = {}


class MCPHttpClient:
    """HTTP client for communicating with MCP servers"""

    def __init__(self, server_name: str, server_config: dict[str, str]):
        self.name = server_name
        self.url = server_config["url"]
        self.description = server_config["description"]
        self.session = None
        self.healthy = False
        self.response_time = 0.0

    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        await self.health_check()

    async def cleanup(self):
        """Cleanup HTTP session."""
        if self.session:
            await self.session.close()

    async def health_check(self) -> bool:
        """Check if MCP server is healthy."""
        try:
            start_time = datetime.now()

            if not self.session:
                return False

            async with self.session.get(f"{self.url}/health") as response:
                self.response_time = (datetime.now() - start_time).total_seconds()
                self.healthy = response.status == 200
                return self.healthy

        except Exception as e:
            logger.warning(f"Health check failed for {self.name}: {e}")
            self.healthy = False
            return False

    async def query(
        self, endpoint: str, method: str = "GET", data: Optional[dict] = None
    ) -> dict[str, Any]:
        """Execute query against MCP server."""
        try:
            if not self.session or not self.healthy:
                return {"error": f"Server {self.name} not available"}

            start_time = datetime.now()
            url = f"{self.url}{endpoint}"

            if method.upper() == "GET":
                async with self.session.get(url, params=data) as response:
                    result = await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
            else:
                return {"error": f"Unsupported method: {method}"}

            response_time = (datetime.now() - start_time).total_seconds()

            # Add metadata
            result["_metadata"] = {
                "server": self.name,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
            }

            return result

        except Exception as e:
            logger.error(f"Query failed for {self.name}: {e}")
            return {"error": str(e), "server": self.name}


class UnifiedChatService:
    """Unified chat service with temporal learning integration"""

    def __init__(self):
        self.servers = {}
        self.session = None
        self.temporal_learning_service = None

        # Initialize temporal learning if available
        if TEMPORAL_LEARNING_AVAILABLE:
            try:
                self.temporal_learning_service = get_temporal_qa_learning_service()
            except Exception as e:
                logger.warning(f"Failed to initialize temporal learning: {e}")
                self.temporal_learning_service = None

    async def initialize(self):
        """Initialize all MCP clients."""
        logger.info("Initializing MCP server clients...")

        for server_name, config in MCP_SERVERS.items():
            client = MCPHttpClient(server_name, config)
            await client.initialize()
            self.servers[server_name] = client

            if client.healthy:
                logger.info(
                    f"✅ {server_name} server connected ({client.response_time:.3f}s)"
                )
            else:
                logger.warning(f"❌ {server_name} server unavailable")

    async def cleanup(self):
        """Cleanup all MCP clients."""
        for client in self.servers.values():
            await client.cleanup()

    async def process_query(
        self, query: str, user_id: str, session_id: str, context: str = "chat"
    ) -> dict[str, Any]:
        """Process user query with temporal learning integration"""
        start_time = datetime.now()

        # Initialize response
        response = {
            "response": "",
            "citations": [],
            "metadata": {
                "query": query,
                "user_id": user_id,
                "session_id": session_id,
                "context": context,
                "timestamp": start_time.isoformat(),
                "processing_time": 0.0,
                "temporal_learning_applied": False,
                "sources_used": [],
                "confidence": 0.0,
            },
        }

        try:
            # Process temporal learning first if available
            temporal_result = None
            if self.temporal_learning_service:
                try:
                    temporal_result = (
                        await self.temporal_learning_service.process_qa_interaction(
                            user_message=query,
                            context={
                                "user_id": user_id,
                                "session_id": session_id,
                                "chat_context": context,
                                "timestamp": start_time.isoformat(),
                            },
                        )
                    )

                    if temporal_result.get("learning_applied", False):
                        response["metadata"]["temporal_learning_applied"] = True
                        response["metadata"][
                            "temporal_interaction_id"
                        ] = temporal_result.get("interaction_id")
                        response["metadata"][
                            "temporal_confidence"
                        ] = temporal_result.get("confidence", 0.0)

                        # If temporal learning provided a complete response, use it
                        if temporal_result.get("response"):
                            response["response"] = temporal_result["response"]
                            response["metadata"]["temporal_response_used"] = True

                            # Add temporal citations if available
                            if temporal_result.get("citations"):
                                response["citations"].extend(
                                    temporal_result["citations"]
                                )

                            # Calculate processing time and return early if complete
                            end_time = datetime.now()
                            response["metadata"]["processing_time"] = (
                                end_time - start_time
                            ).total_seconds()
                            return response

                except Exception as e:
                    logger.warning(f"Temporal learning processing failed: {e}")
                    # Continue with regular processing

            # Regular query processing
            query_context = await self._analyze_query_context(query, user_id)

            # Add temporal context if available
            if temporal_result:
                query_context.temporal_context = temporal_result.get("context", {})

            # Process with MCP servers
            results = await self._process_with_sources(
                query, query_context, user_id, session_id
            )

            # Generate unified response
            unified_response = await self._generate_unified_response(
                query, results, query_context
            )

            # Remove the store_interaction call since it doesn't exist in the service
            # Just log the interaction for now
            if self.temporal_learning_service and unified_response:
                logger.info(f"Temporal learning interaction logged for user {user_id}")

            # Update response
            response["response"] = unified_response
            response["metadata"]["sources_used"] = query_context.sources_needed
            response["metadata"]["confidence"] = query_context.confidence

            # Add citations from results
            for result in results:
                if result.get("citations"):
                    response["citations"].extend(result["citations"])

            # Calculate processing time
            end_time = datetime.now()
            response["metadata"]["processing_time"] = (
                end_time - start_time
            ).total_seconds()

            return response

        except Exception as e:
            logger.error(f"Query processing error: {e}")
            response[
                "response"
            ] = f"I encountered an error processing your query: {e!s}"
            response["metadata"]["error"] = str(e)

            # Calculate processing time even for errors
            end_time = datetime.now()
            response["metadata"]["processing_time"] = (
                end_time - start_time
            ).total_seconds()

            return response

    async def process_temporal_correction(
        self, interaction_id: str, correction: str, user_id: str, session_id: str
    ) -> dict[str, Any]:
        """Process user correction for temporal learning"""
        if not self.temporal_learning_service:
            return {"error": "Temporal learning not available"}

        try:
            result = await self.temporal_learning_service.process_user_correction(
                interaction_id=interaction_id,
                correction=correction,
                context={
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            return result

        except Exception as e:
            logger.error(f"Temporal correction processing error: {e}")
            return {"error": str(e)}

    async def get_temporal_learning_insights(self, user_id: str) -> dict[str, Any]:
        """Get temporal learning insights for the user"""
        if not self.temporal_learning_service:
            return {"error": "Temporal learning not available"}

        try:
            insights = (
                await self.temporal_learning_service.get_learning_dashboard_data()
            )
            return insights

        except Exception as e:
            logger.error(f"Failed to get temporal learning insights: {e}")
            return {"error": str(e)}

    async def _analyze_query_context(self, query: str, user_id: str) -> QueryContext:
        """Simple query analysis to determine intent and needed sources"""
        query_lower = query.lower()

        # Determine intent based on keywords
        if any(
            word in query_lower
            for word in ["task", "project", "deadline", "milestone", "asana"]
        ):
            intent = "project_management"
            sources_needed = ["asana"]
        elif any(
            word in query_lower
            for word in ["team", "slack", "communication", "message"]
        ):
            intent = "team_insights"
            sources_needed = ["slack"]
        elif any(
            word in query_lower
            for word in ["sale", "deal", "revenue", "hubspot", "crm"]
        ):
            intent = "sales_analysis"
            sources_needed = ["hubspot", "gong"]
        elif any(
            word in query_lower
            for word in ["code", "github", "repository", "commit", "linear"]
        ):
            intent = "engineering_insights"
            sources_needed = ["github", "linear"]
        elif any(
            word in query_lower
            for word in [
                "document",
                "note",
                "knowledge",
                "notion",
                "page",
                "documentation",
                "strategic",
                "planning",
            ]
        ):
            intent = "knowledge_management"
            sources_needed = ["notion"]
        else:
            intent = "general_inquiry"
            sources_needed = ["asana", "notion"]  # Default to available servers

        return QueryContext(
            intent=intent, sources_needed=sources_needed, confidence=0.8
        )

    async def _fetch_multi_source_data(self, context: QueryContext) -> dict[str, Any]:
        """Fetch data from multiple MCP servers in parallel"""
        source_data = {}

        # Create parallel tasks for each needed source
        tasks = {}

        for source in context.sources_needed:
            if source == "asana" and source in self.servers:
                tasks["asana_tasks"] = self.servers["asana"].query("/tasks")
                tasks["asana_projects"] = self.servers["asana"].query("/projects")

            elif source == "notion" and source in self.servers:
                tasks["notion_pages"] = self.servers["notion"].query("/pages/search")
                tasks["notion_insights"] = self.servers["notion"].query(
                    "/knowledge/insights"
                )

            elif source == "slack" and source in self.servers:
                tasks["slack_insights"] = self.servers["slack"].query("/insights")

        # Execute all tasks in parallel
        if tasks:
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)

            # Combine results
            for i, (task_name, _) in enumerate(tasks.items()):
                if i < len(results) and not isinstance(results[i], Exception):
                    source_data[task_name] = results[i]

        return source_data

    async def _synthesize_response(
        self, context: QueryContext, source_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Synthesize response from source data"""

        # Build response based on intent and available data
        insights = []
        recommendations = []
        data_sources = []

        if context.intent == "project_management" and "asana_tasks" in source_data:
            tasks_data = source_data["asana_tasks"]
            if "tasks" in tasks_data and tasks_data["tasks"]:
                total_tasks = len(tasks_data["tasks"])
                completed_tasks = len(
                    [t for t in tasks_data["tasks"] if t.get("completed")]
                )

                insights.append(
                    f"You have {total_tasks} total tasks with {completed_tasks} completed"
                )

                # Check for overdue tasks
                overdue_tasks = [
                    t
                    for t in tasks_data["tasks"]
                    if t.get("due_on")
                    and t["due_on"] < datetime.now().strftime("%Y-%m-%d")
                ]
                if overdue_tasks:
                    insights.append(f"⚠️ {len(overdue_tasks)} tasks are overdue")
                    recommendations.append(
                        "Focus on overdue tasks to maintain project momentum"
                    )

                data_sources.append("Asana Tasks")

        elif context.intent == "knowledge_management" and "notion_pages" in source_data:
            pages_data = source_data["notion_pages"]
            if "pages" in pages_data:
                insights.append(
                    f"Found {len(pages_data['pages'])} relevant knowledge base pages"
                )
                data_sources.append("Notion Knowledge Base")

                if "notion_insights" in source_data:
                    knowledge_data = source_data["notion_insights"]
                    if "knowledge_metrics" in knowledge_data:
                        metrics = knowledge_data["knowledge_metrics"]
                        insights.append(
                            f"Knowledge base contains {metrics.get('total_pages', 0)} pages"
                        )

        # Default response if no specific data
        if not insights:
            insights.append(
                "I understand your question but specific data may not be available at the moment."
            )
            recommendations.append(
                "Please check system status or try rephrasing your question."
            )

        response_text = f"Based on your {context.intent} query, here's what I found:"
        if insights:
            response_text += "\n\n" + "\n".join(f"• {insight}" for insight in insights)

        return {
            "response": response_text,
            "insights": insights,
            "recommendations": recommendations,
            "data_sources": data_sources,
            "intent": context.intent,
            "confidence": context.confidence,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "sources_queried": list(source_data.keys()),
            },
        }

    async def _process_with_sources(
        self, query: str, context: QueryContext, user_id: str, session_id: str
    ) -> list[dict[str, Any]]:
        """Process query with multiple sources"""
        results = []

        # Fetch data from all relevant sources
        source_data = await self._fetch_multi_source_data(context)

        # Process each source individually
        for source in context.sources_needed:
            if source in self.servers:
                result = await self.servers[source].query(
                    f"/{source}", data={"query": query}
                )
                if result.get("response"):
                    result["_metadata"]["source"] = source
                    results.append(result)

        return results

    async def _generate_unified_response(
        self, query: str, results: list[dict[str, Any]], context: QueryContext
    ) -> str:
        """Generate a unified response from multiple results"""
        response_parts = []

        for result in results:
            response_parts.append(result["response"])

        unified_response = "\n\n".join(response_parts)

        return unified_response
