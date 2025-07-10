"""
Sophia Unified Orchestrator - The OFFICIAL entry point for all Sophia AI requests

This is the single, authoritative orchestrator that combines:
- UnifiedChatService capabilities
- SophiaAIOrchestrator intelligence
- EnhancedMultiAgentOrchestrator parallel execution
- SophiaAgentOrchestrator workflow patterns

All other orchestrators are DEPRECATED and will be removed in version 6.0.

Date: July 9, 2025
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from backend.core.date_time_manager import date_manager
from backend.services.unified_memory_service import get_unified_memory_service

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents"""

    BUSINESS_INTELLIGENCE = "business_intelligence"
    CODE_ANALYSIS = "code_analysis"
    INFRASTRUCTURE = "infrastructure"
    MEMORY_QUERY = "memory_query"
    GENERAL = "general"


@dataclass
class Intent:
    """Analyzed user intent"""

    type: IntentType
    confidence: float
    capabilities_needed: set[str]
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationMetrics:
    """Metrics for monitoring orchestration performance"""

    request_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    active_users: set[str] = field(default_factory=set)
    mcp_server_usage: dict[str, int] = field(default_factory=dict)

    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count

    def calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        if self.request_count == 0:
            return 100.0

        error_rate = self.error_count / self.request_count
        performance_score = min(100, 100 * (1.0 / max(0.1, self.average_response_time)))

        return round((1 - error_rate) * 50 + performance_score * 0.5, 2)


class SophiaUnifiedOrchestrator:
    """
    The unified orchestrator for all Sophia AI operations.

    This replaces:
    - UnifiedChatService
    - SophiaAIOrchestrator
    - EnhancedMultiAgentOrchestrator
    - SophiaAgentOrchestrator
    """

    def __init__(self):
        # Get the underlying memory service
        from backend.services.memory_service_adapter import MemoryServiceAdapter

        base_memory_service = get_unified_memory_service()
        self.memory_service = MemoryServiceAdapter(base_memory_service)

        self.mcp_orchestrator = None  # Will lazy load with adapter
        self.current_date = date_manager.now()
        self.metrics = OrchestrationMetrics()
        self.initialized = False

        logger.info(
            f"✅ SophiaUnifiedOrchestrator initialized - Date: {self.current_date}"
        )

    async def initialize(self):
        """Initialize all services"""
        if self.initialized:
            return

        try:
            # Try to initialize MCP orchestrator with adapter
            try:
                from backend.services.mcp_orchestration_adapter import (
                    MCPOrchestrationAdapter,
                )
                from infrastructure.services.mcp_orchestration_service import (
                    MCPOrchestrationService,
                )

                base_mcp = MCPOrchestrationService()
                self.mcp_orchestrator = MCPOrchestrationAdapter(base_mcp)
                logger.info("✅ MCP Orchestration Service initialized with adapter")
            except ImportError as e:
                logger.warning(f"MCP Orchestration Service not available: {e}")
                # Create a mock MCP orchestrator for now
                self.mcp_orchestrator = self._create_mock_mcp_orchestrator()

            self.initialized = True
            logger.info("✅ SophiaUnifiedOrchestrator fully initialized")

        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise

    def _create_mock_mcp_orchestrator(self):
        """Create a mock MCP orchestrator for when the real one is not available"""

        class MockMCPOrchestrator:
            async def get_servers_by_capability(self, capabilities):
                # Return mock servers
                return [{"name": "mock_server", "capabilities": capabilities}]

            async def execute_business_task(
                self, task_type, description, capabilities, context
            ):
                return {
                    "response": f"Mock response for {task_type}: {description}",
                    "metadata": {"mock": True},
                }

        return MockMCPOrchestrator()

    async def process_request(
        self,
        query: str,
        user_id: str,
        session_id: str,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Process any request through the unified orchestration pipeline.

        This is the ONLY method external services should call.
        """

        # Ensure initialization
        if not self.initialized:
            await self.initialize()

        start_time = date_manager.now()

        # Update metrics
        self.metrics.request_count += 1
        self.metrics.active_users.add(user_id)

        try:
            # Log the request
            logger.info(f"Processing request from user {user_id}: {query[:50]}...")

            # Step 1: Store in memory for learning
            await self.memory_service.add_conversation(
                user_id=user_id,
                session_id=session_id,
                user_message=query,
                ai_response=None,  # Will update after processing
            )

            # Step 2: Analyze intent
            intent = await self._analyze_intent(query, context)

            # Step 3: Route to appropriate handler
            if intent.type == IntentType.BUSINESS_INTELLIGENCE:
                response = await self._handle_business_intelligence(
                    query, intent, user_id, session_id, context
                )
            elif intent.type == IntentType.CODE_ANALYSIS:
                response = await self._handle_code_analysis(
                    query, intent, user_id, session_id, context
                )
            elif intent.type == IntentType.INFRASTRUCTURE:
                response = await self._handle_infrastructure(
                    query, intent, user_id, session_id, context
                )
            elif intent.type == IntentType.MEMORY_QUERY:
                response = await self._handle_memory_query(
                    query, intent, user_id, session_id, context
                )
            else:
                response = await self._handle_general(
                    query, intent, user_id, session_id, context
                )

            # Step 4: Update memory with response
            await self.memory_service.update_conversation(
                session_id=session_id, ai_response=response.get("response", "")
            )

            # Step 5: Add metadata
            end_time = date_manager.now()
            processing_time = (end_time - start_time).total_seconds()

            self.metrics.total_response_time += processing_time

            response["metadata"] = {
                "processing_time": processing_time,
                "intent": {
                    "type": intent.type.value,
                    "confidence": intent.confidence,
                    "capabilities": list(intent.capabilities_needed),
                },
                "orchestrator": "unified",
                "version": "1.0.0",
                "date": self.current_date.isoformat(),
                "health_score": self.metrics.calculate_health_score(),
            }

            return response

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.metrics.error_count += 1

            return {
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "metadata": {
                    "error": True,
                    "orchestrator": "unified",
                    "version": "1.0.0",
                    "date": self.current_date.isoformat(),
                },
            }

    async def _analyze_intent(
        self, query: str, context: Optional[dict[str, Any]]
    ) -> Intent:
        """Analyze user intent from query"""
        query_lower = query.lower()

        # Business intelligence keywords
        if any(
            word in query_lower
            for word in [
                "revenue",
                "sales",
                "deal",
                "customer",
                "crm",
                "hubspot",
                "gong",
                "call",
                "meeting",
                "performance",
                "metrics",
            ]
        ):
            return Intent(
                type=IntentType.BUSINESS_INTELLIGENCE,
                confidence=0.9,
                capabilities_needed={"CRM", "ANALYTICS", "CALLS"},
            )

        # Code analysis keywords
        elif any(
            word in query_lower
            for word in [
                "code",
                "analyze",
                "review",
                "quality",
                "security",
                "bug",
                "refactor",
                "optimize",
                "lint",
                "test",
            ]
        ):
            return Intent(
                type=IntentType.CODE_ANALYSIS,
                confidence=0.9,
                capabilities_needed={"CODE_ANALYSIS", "SECURITY", "METRICS"},
            )

        # Infrastructure keywords
        elif any(
            word in query_lower
            for word in [
                "deploy",
                "infrastructure",
                "server",
                "docker",
                "kubernetes",
                "lambda",
                "pulumi",
                "terraform",
                "aws",
                "cloud",
            ]
        ):
            return Intent(
                type=IntentType.INFRASTRUCTURE,
                confidence=0.9,
                capabilities_needed={"INFRASTRUCTURE", "DEPLOYMENT", "MONITORING"},
            )

        # Memory query keywords
        elif any(
            word in query_lower
            for word in [
                "remember",
                "recall",
                "what did",
                "previous",
                "history",
                "context",
                "earlier",
                "last time",
            ]
        ):
            return Intent(
                type=IntentType.MEMORY_QUERY,
                confidence=0.9,
                capabilities_needed={"MEMORY", "SEARCH"},
            )

        # Default to general
        else:
            return Intent(
                type=IntentType.GENERAL,
                confidence=0.7,
                capabilities_needed={"MEMORY", "SEARCH", "ANALYTICS"},
            )

    async def _handle_business_intelligence(
        self,
        query: str,
        intent: Intent,
        user_id: str,
        session_id: str,
        context: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Handle business intelligence queries"""

        # Check if MCP orchestrator is available
        if not self.mcp_orchestrator:
            logger.warning("MCP orchestrator not available, using memory fallback")
            return await self._handle_memory_fallback(query, user_id, session_id)

        # Get capable MCP servers
        servers = await self.mcp_orchestrator.get_servers_by_capability(
            list(intent.capabilities_needed)
        )

        # Update metrics
        for server in servers:
            self.metrics.mcp_server_usage[server["name"]] = (
                self.metrics.mcp_server_usage.get(server["name"], 0) + 1
            )

        # Execute parallel queries to relevant servers
        tasks = []
        server_names = [s["name"] for s in servers]

        # Route to specific MCP servers based on capabilities
        if "CALL_ANALYSIS" in intent.capabilities_needed and "gong" in server_names:
            tasks.append(
                self._query_mcp_server(
                    "gong",
                    "search_calls",
                    {"query": query, "limit": 10, "context": context},
                )
            )

        if (
            "CRM_DATA" in intent.capabilities_needed
            and "hubspot_unified" in server_names
        ):
            tasks.append(
                self._query_mcp_server(
                    "hubspot_unified",
                    "search_contacts",
                    {"query": query, "limit": 10, "context": context},
                )
            )

        if "TEAM_INSIGHTS" in intent.capabilities_needed and "slack_v2" in server_names:
            tasks.append(
                self._query_mcp_server(
                    "slack_v2",
                    "search_messages",
                    {"query": query, "limit": 10, "context": context},
                )
            )

        if "PROJECT_DATA" in intent.capabilities_needed:
            if "linear" in server_names:
                tasks.append(
                    self._query_mcp_server(
                        "linear",
                        "search_issues",
                        {"query": query, "limit": 10, "context": context},
                    )
                )
            if "asana" in server_names:
                tasks.append(
                    self._query_mcp_server(
                        "asana",
                        "search_tasks",
                        {"query": query, "limit": 10, "context": context},
                    )
                )

        # If no specific servers matched, search memory for business intelligence
        if not tasks:
            try:
                # Try to search memory for relevant information
                results = self.memory_service.search_knowledge(
                    query=query,
                    limit=5,
                    metadata_filter={"user_id": user_id} if user_id else None,
                )

                if results:
                    return {
                        "response": self._format_memory_results(results),
                        "citations": [{"source": "knowledge_base", "results": results}],
                        "sources": ["knowledge_base"],
                    }
            except Exception as e:
                logger.warning(f"Memory search failed: {e}")

        # Execute all queries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process and synthesize results
        response_parts = []
        citations = []
        successful_sources = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"MCP query failed: {result}")
                continue

            if isinstance(result, dict) and result.get("success"):
                source = result.get("source", "unknown")
                data = result.get("data", {})

                # Extract relevant information based on source
                if source == "gong" and data.get("calls"):
                    response_parts.append(
                        f"**Call Intelligence:**\n{self._format_gong_results(data['calls'])}"
                    )
                    citations.append({"source": "gong", "data": data["calls"][:3]})
                    successful_sources.append("gong")

                elif source == "hubspot_unified" and data.get("contacts"):
                    response_parts.append(
                        f"**CRM Data:**\n{self._format_hubspot_results(data['contacts'])}"
                    )
                    citations.append(
                        {"source": "hubspot", "data": data["contacts"][:3]}
                    )
                    successful_sources.append("hubspot")

                elif source == "slack_v2" and data.get("messages"):
                    response_parts.append(
                        f"**Team Insights:**\n{self._format_slack_results(data['messages'])}"
                    )
                    citations.append({"source": "slack", "data": data["messages"][:3]})
                    successful_sources.append("slack")

                elif source in ["linear", "asana"] and data.get("items"):
                    response_parts.append(
                        f"**Project Data ({source}):**\n{self._format_project_results(data['items'])}"
                    )
                    citations.append({"source": source, "data": data["items"][:3]})
                    successful_sources.append(source)

        # If we have results, synthesize them
        if response_parts:
            synthesized_response = "\n\n".join(response_parts)

            # Add a summary if multiple sources
            if len(response_parts) > 1:
                summary = await self._generate_business_summary(query, response_parts)
                synthesized_response = f"{summary}\n\n{synthesized_response}"
        else:
            synthesized_response = "I couldn't retrieve specific business intelligence data for your query. Please try rephrasing or asking about specific systems (Gong calls, HubSpot contacts, Slack discussions, or project management)."

        return {
            "response": synthesized_response,
            "citations": citations,
            "sources": successful_sources,
        }

    async def _handle_code_analysis(
        self,
        query: str,
        intent: Intent,
        user_id: str,
        session_id: str,
        context: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Handle code analysis queries"""

        # Check if MCP orchestrator is available
        if not self.mcp_orchestrator:
            logger.warning("MCP orchestrator not available for code analysis")
            return await self._handle_memory_fallback(query, user_id, session_id)

        # Get code analysis servers
        servers = await self.mcp_orchestrator.get_servers_by_capability(
            ["CODE_ANALYSIS"]
        )

        # For now, return a placeholder
        return {
            "response": "Code analysis capabilities are being migrated to the unified orchestrator. Please check back soon.",
            "sources": [s["name"] for s in servers],
        }

    async def _handle_infrastructure(
        self,
        query: str,
        intent: Intent,
        user_id: str,
        session_id: str,
        context: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Handle infrastructure queries"""

        return {
            "response": "Infrastructure management should use the SophiaIaCOrchestrator for now. This capability will be integrated soon.",
            "sources": ["infrastructure"],
        }

    async def _handle_memory_query(
        self,
        query: str,
        intent: Intent,
        user_id: str,
        session_id: str,
        context: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Handle memory/recall queries"""

        # Search memory
        memories = await self.memory_service.search_conversations(
            user_id=user_id, query=query, limit=5
        )

        if memories:
            response_parts = ["Based on our previous conversations:"]
            for memory in memories:
                response_parts.append(
                    f"- {memory.get('summary', memory.get('content', ''))}"
                )

            return {
                "response": "\n".join(response_parts),
                "sources": ["unified_memory"],
            }
        else:
            return {
                "response": "I don't have any relevant previous conversations to recall.",
                "sources": ["unified_memory"],
            }

    async def _handle_general(
        self,
        query: str,
        intent: Intent,
        user_id: str,
        session_id: str,
        context: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Handle general queries"""

        # For general queries, search knowledge base and provide helpful response
        knowledge_results = self.memory_service.search_knowledge(query=query, limit=3)

        if knowledge_results:
            response_parts = ["Here's what I found:"]
            for result in knowledge_results:
                response_parts.append(f"- {result.get('content', '')}")

            return {
                "response": "\n".join(response_parts),
                "sources": ["knowledge_base"],
            }
        else:
            return {
                "response": "I can help you with business intelligence, code analysis, infrastructure management, or answer questions based on our previous conversations. What would you like to know?",
                "sources": ["general"],
            }

    async def _query_mcp_server(
        self, server_name: str, query_type: str, query_params: dict[str, Any]
    ) -> dict[str, Any]:
        """Query an MCP server"""
        try:
            # This will be implemented with actual MCP server calls
            return {
                "response": f"Query to {server_name} {query_type} is being processed.",
                "source": server_name,
            }
        except Exception as e:
            logger.error(f"Query to {server_name} {query_type} failed: {e}")
            raise

    def _format_memory_results(self, results: list[dict]) -> str:
        """Format memory search results into readable text"""
        if not results:
            return "No relevant information found in memory."

        formatted = []
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            source = result.get("source", "unknown")
            similarity = result.get("similarity", 0)
            formatted.append(
                f"{i}. {content[:200]}... (Source: {source}, Relevance: {similarity:.2f})"
            )

        return "\n".join(formatted)

    def _format_gong_results(self, calls: list[dict]) -> str:
        """Format Gong call results"""
        if not calls:
            return "No relevant calls found."

        formatted = []
        for call in calls[:5]:  # Top 5 calls
            title = call.get("title", "Untitled Call")
            date = call.get("date", "Unknown date")
            participants = call.get("participants", [])
            summary = call.get("summary", "No summary available")
            formatted.append(
                f"• **{title}** ({date})\n  Participants: {', '.join(participants)}\n  Summary: {summary}"
            )

        return "\n".join(formatted)

    def _format_hubspot_results(self, contacts: list[dict]) -> str:
        """Format HubSpot contact results"""
        if not contacts:
            return "No relevant contacts found."

        formatted = []
        for contact in contacts[:5]:  # Top 5 contacts
            name = contact.get("name", "Unknown")
            company = contact.get("company", "Unknown company")
            deal_stage = contact.get("deal_stage", "No active deal")
            value = contact.get("deal_value", 0)
            formatted.append(
                f"• **{name}** ({company})\n  Deal Stage: {deal_stage}\n  Value: ${value:,}"
            )

        return "\n".join(formatted)

    def _format_slack_results(self, messages: list[dict]) -> str:
        """Format Slack message results"""
        if not messages:
            return "No relevant messages found."

        formatted = []
        for msg in messages[:5]:  # Top 5 messages
            author = msg.get("author", "Unknown")
            channel = msg.get("channel", "Unknown channel")
            text = msg.get("text", "")[:100]
            timestamp = msg.get("timestamp", "Unknown time")
            formatted.append(
                f'• **{author}** in #{channel} ({timestamp})\n  "{text}..."'
            )

        return "\n".join(formatted)

    def _format_project_results(self, items: list[dict]) -> str:
        """Format project management results (Linear/Asana)"""
        if not items:
            return "No relevant project items found."

        formatted = []
        for item in items[:5]:  # Top 5 items
            title = item.get("title", "Untitled")
            status = item.get("status", "Unknown")
            assignee = item.get("assignee", "Unassigned")
            priority = item.get("priority", "Normal")
            formatted.append(
                f"• **{title}**\n  Status: {status} | Assignee: {assignee} | Priority: {priority}"
            )

        return "\n".join(formatted)

    async def _generate_business_summary(
        self, query: str, response_parts: list[str]
    ) -> str:
        """Generate a summary of business intelligence results"""
        # For now, return a simple summary
        # TODO: Use Snowflake Cortex to generate intelligent summary
        num_sources = len(response_parts)
        return f'**Business Intelligence Summary**\nFound relevant information from {num_sources} sources for your query: "{query}". Details below:'

    async def _handle_memory_fallback(
        self, query: str, user_id: str, session_id: str
    ) -> dict[str, Any]:
        """Fallback handler when MCP orchestrator is not available"""
        try:
            # Try to search memory for relevant information
            results = self.memory_service.search_knowledge(
                query=query,
                limit=5,
                metadata_filter={"user_id": user_id} if user_id else None,
            )

            if results:
                response = self._format_memory_results(results)
            else:
                response = "I'm currently operating with limited services. The MCP orchestration system is not available, but I can help with basic queries."

            return {
                "response": response,
                "sources": ["memory"],
                "metadata": {
                    "fallback": True,
                    "processing_time": 0.1,
                    "intent": {"type": "memory_query", "confidence": 0.8},
                },
            }
        except Exception as e:
            logger.error(f"Memory fallback failed: {e}")
            return {
                "response": "I'm experiencing technical difficulties. Please try again later.",
                "error": str(e),
                "metadata": {"fallback": True, "error": True},
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get current orchestrator metrics"""
        return {
            "request_count": self.metrics.request_count,
            "error_count": self.metrics.error_count,
            "average_response_time": self.metrics.average_response_time,
            "active_users": len(self.metrics.active_users),
            "mcp_server_usage": self.metrics.mcp_server_usage,
            "health_score": self.metrics.calculate_health_score(),
        }


# Singleton instance
_orchestrator_instance = None


def get_unified_orchestrator() -> SophiaUnifiedOrchestrator:
    """Get or create the unified orchestrator singleton"""
    global _orchestrator_instance

    if _orchestrator_instance is None:
        try:
            _orchestrator_instance = SophiaUnifiedOrchestrator()
        except Exception as e:
            logger.error(f"Failed to create orchestrator: {e}")
            # Return a basic instance even if some services fail
            _orchestrator_instance = SophiaUnifiedOrchestrator()

    return _orchestrator_instance
