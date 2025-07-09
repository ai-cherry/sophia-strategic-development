"""
Gong Enhanced Chat Integration

Integrates Gong conversation intelligence into the enhanced unified chat
to enable natural language queries about conversations, meetings, and calls.

Date: July 9, 2025
"""

import logging
from datetime import datetime
from typing import Any

from backend.services.enhanced_multi_agent_orchestrator import (
    EnhancedMultiAgentOrchestrator,
)
from backend.services.gong_multi_purpose_intelligence import (
    GongMultiPurposeIntelligence,
)

logger = logging.getLogger(__name__)


class GongEnhancedChatIntegration:
    """
    Integration service that enhances the unified chat with Gong conversation intelligence
    """

    def __init__(self):
        self.gong_intelligence = GongMultiPurposeIntelligence()
        self.current_date = "July 9, 2025"

        # Natural language query patterns for Gong intelligence
        self.gong_query_patterns = {
            "project_risks": [
                "project risks mentioned in calls",
                "risks discussed in meetings",
                "blockers from conversations",
                "what risks were mentioned",
            ],
            "customer_feedback": [
                "customer feedback from calls",
                "what customers are saying",
                "customer satisfaction from conversations",
                "support call insights",
            ],
            "competitive_intelligence": [
                "competitors mentioned in calls",
                "competitive intelligence from conversations",
                "what competitors are discussed",
                "competitive mentions",
            ],
            "team_performance": [
                "team performance from meetings",
                "how is the team performing",
                "team feedback from conversations",
                "meeting effectiveness",
            ],
            "sales_pipeline": [
                "sales insights from calls",
                "deal status from conversations",
                "pipeline updates from meetings",
                "prospect feedback",
            ],
            "technical_decisions": [
                "technical decisions from calls",
                "architecture discussions",
                "technology choices from meetings",
                "development decisions",
            ],
        }

    def is_gong_query(self, query: str) -> bool:
        """Determine if a query should be routed to Gong intelligence"""

        query_lower = query.lower()

        # Check for conversation/call related keywords
        conversation_keywords = [
            "call",
            "calls",
            "conversation",
            "conversations",
            "meeting",
            "meetings",
            "discussion",
            "discussions",
            "feedback",
            "mentioned",
            "discussed",
            "from calls",
            "from conversations",
            "from meetings",
            "in calls",
        ]

        # Check for Gong-specific patterns
        for pattern_list in self.gong_query_patterns.values():
            for pattern in pattern_list:
                if pattern.lower() in query_lower:
                    return True

        # Check for conversation keywords
        return any(keyword in query_lower for keyword in conversation_keywords)

    async def process_gong_query(
        self, query: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Process a query through Gong conversation intelligence"""

        try:
            logger.info(f"Processing Gong query: {query}")

            if context is None:
                context = {}

            # Inject current date context
            context["current_date"] = self.current_date
            context["query_type"] = "gong_intelligence"

            # Route query to appropriate Gong intelligence function
            query_category = self._categorize_gong_query(query)

            if query_category == "natural_language":
                # Use natural language processing for complex queries
                result = await self.gong_intelligence.get_natural_language_insights(
                    query
                )
            elif query_category == "project_management":
                # Get project-specific intelligence
                project_insights = (
                    await self.gong_intelligence.get_project_management_intelligence(14)
                )
                result = self._format_project_insights_response(query, project_insights)
            elif query_category == "multi_purpose":
                # Get multi-purpose insights
                insights = await self.gong_intelligence.extract_multi_purpose_insights(
                    7
                )
                result = self._format_multi_purpose_response(query, insights)
            else:
                # Fallback to natural language processing
                result = await self.gong_intelligence.get_natural_language_insights(
                    query
                )

            # Enhanced response formatting
            enhanced_result = {
                "success": True,
                "query": query,
                "response_type": "gong_intelligence",
                "answer": result.get("answer", result),
                "sources": result.get("sources", 0),
                "confidence": result.get("confidence", 0.8),
                "current_date": self.current_date,
                "category": query_category,
                "supporting_data": result.get("supporting_calls", []),
                "suggested_follow_ups": self._generate_follow_up_questions(
                    query, result
                ),
                "processing_time": datetime.now().isoformat(),
            }

            return enhanced_result

        except Exception as e:
            logger.error(f"Error processing Gong query: {e}")
            return {
                "success": False,
                "query": query,
                "response_type": "gong_intelligence",
                "error": str(e),
                "current_date": self.current_date,
            }

    def _categorize_gong_query(self, query: str) -> str:
        """Categorize the type of Gong query"""

        query_lower = query.lower()

        # Check for specific patterns
        for category, patterns in self.gong_query_patterns.items():
            for pattern in patterns:
                if pattern.lower() in query_lower:
                    if category in ["project_risks", "technical_decisions"]:
                        return "project_management"
                    else:
                        return "multi_purpose"

        # Check for project-specific keywords
        project_keywords = [
            "project",
            "sprint",
            "deadline",
            "feature",
            "development",
            "milestone",
        ]
        if any(keyword in query_lower for keyword in project_keywords):
            return "project_management"

        # Default to natural language processing
        return "natural_language"

    def _format_project_insights_response(
        self, query: str, project_insights
    ) -> dict[str, Any]:
        """Format project intelligence insights into a response"""

        # Determine what aspect of project insights to highlight
        query_lower = query.lower()

        if "risk" in query_lower:
            focus_data = project_insights.risk_indicators
            focus_type = "risks"
        elif "decision" in query_lower or "technical" in query_lower:
            focus_data = project_insights.technical_decisions
            focus_type = "technical decisions"
        elif "timeline" in query_lower or "deadline" in query_lower:
            focus_data = project_insights.timeline_discussions
            focus_type = "timeline discussions"
        else:
            focus_data = project_insights.project_references
            focus_type = "project references"

        # Generate response
        if focus_data:
            answer = f"Based on recent conversations, I found {len(focus_data)} {focus_type}:\n\n"

            for i, item in enumerate(focus_data[:5], 1):  # Top 5 items
                content = item.get("content", "No content available")
                call_date = item.get("call_date", "Unknown date")
                answer += f"{i}. {content} (from call on {call_date})\n\n"

            if len(focus_data) > 5:
                answer += f"... and {len(focus_data) - 5} more {focus_type}"
        else:
            answer = f"No {focus_type} found in recent conversations."

        return {
            "answer": answer,
            "sources": len(focus_data),
            "confidence": 0.85,
            "category": focus_type,
            "supporting_calls": [
                {
                    "call_date": item.get("call_date"),
                    "content": item.get("content", "")[:200] + "...",
                }
                for item in focus_data[:3]
            ],
        }

    def _format_multi_purpose_response(
        self, query: str, insights: dict[str, list]
    ) -> dict[str, Any]:
        """Format multi-purpose insights into a response"""

        # Determine which category is most relevant to the query
        query_lower = query.lower()

        relevant_category = None
        if "customer" in query_lower:
            relevant_category = "customer_success"
        elif "sales" in query_lower or "deal" in query_lower:
            relevant_category = "sales_intelligence"
        elif "team" in query_lower or "performance" in query_lower:
            relevant_category = "team_performance"
        elif "competitor" in query_lower:
            relevant_category = "competitive_intel"

        if relevant_category and relevant_category in insights:
            focus_insights = insights[relevant_category]
        else:
            # Combine all insights
            focus_insights = []
            for category_insights in insights.values():
                focus_insights.extend(category_insights)

        # Generate response
        if focus_insights:
            answer = "Based on recent conversations, here are the key insights:\n\n"

            for i, insight in enumerate(focus_insights[:5], 1):
                insight_content = (
                    insight.insight if hasattr(insight, "insight") else str(insight)
                )
                call_date = (
                    insight.call_date if hasattr(insight, "call_date") else "Recent"
                )
                answer += f"{i}. {insight_content} (from {call_date})\n\n"

            if len(focus_insights) > 5:
                answer += f"... and {len(focus_insights) - 5} more insights"
        else:
            answer = "No relevant insights found in recent conversations."

        return {
            "answer": answer,
            "sources": len(focus_insights),
            "confidence": 0.8,
            "category": relevant_category or "general",
            "supporting_calls": [],
        }

    def _generate_follow_up_questions(
        self, original_query: str, result: dict[str, Any]
    ) -> list[str]:
        """Generate suggested follow-up questions based on the query and result"""

        follow_ups = []
        query_lower = original_query.lower()

        # Context-aware follow-up suggestions
        if "risk" in query_lower:
            follow_ups.extend(
                [
                    "What are the most critical risks mentioned in recent calls?",
                    "How are teams addressing these risks?",
                    "Are there any patterns in the risks being identified?",
                ]
            )
        elif "customer" in query_lower:
            follow_ups.extend(
                [
                    "What are customers saying about our new features?",
                    "Are there any churn risk signals in recent calls?",
                    "What expansion opportunities were mentioned?",
                ]
            )
        elif "team" in query_lower:
            follow_ups.extend(
                [
                    "How effective are our team meetings?",
                    "What coaching opportunities were identified?",
                    "Are there any process improvement suggestions?",
                ]
            )
        elif "competitor" in query_lower:
            follow_ups.extend(
                [
                    "Which competitors are mentioned most frequently?",
                    "How do we compare to alternatives in customer discussions?",
                    "What competitive advantages are customers recognizing?",
                ]
            )
        else:
            # General follow-ups
            follow_ups.extend(
                [
                    "What other insights can you extract from recent conversations?",
                    "Are there any urgent action items from recent calls?",
                    "What trends are emerging in our conversations?",
                ]
            )

        return follow_ups[:3]  # Return top 3 follow-up questions


class EnhancedChatWithGongIntegration:
    """
    Enhanced version of the multi-agent orchestrator that includes Gong intelligence
    """

    def __init__(self):
        self.base_orchestrator = EnhancedMultiAgentOrchestrator()
        self.gong_integration = GongEnhancedChatIntegration()
        self.current_date = "July 9, 2025"

    async def process_query_with_gong_intelligence(
        self, query: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Process query with enhanced Gong intelligence routing"""

        if context is None:
            context = {}

        # Inject current date
        context["current_date"] = self.current_date

        # Check if this is a Gong-specific query
        if self.gong_integration.is_gong_query(query):
            logger.info(f"Routing query to Gong intelligence: {query}")

            # Process through Gong intelligence
            gong_result = await self.gong_integration.process_gong_query(query, context)

            # Enhance with additional context if needed
            if gong_result.get("success") and gong_result.get("sources", 0) > 0:
                return gong_result
            else:
                # Fallback to base orchestrator if Gong doesn't have good results
                logger.info(
                    "Gong intelligence had limited results, falling back to base orchestrator"
                )
                base_result = await self.base_orchestrator.process_query(query, context)

                # Combine results
                return {
                    "success": True,
                    "query": query,
                    "primary_response": base_result.get("response", ""),
                    "gong_insights": gong_result.get("answer", ""),
                    "sources": ["enhanced_orchestrator", "gong_intelligence"],
                    "confidence": max(
                        base_result.get("confidence", 0),
                        gong_result.get("confidence", 0),
                    ),
                    "current_date": self.current_date,
                    "processing_approach": "hybrid_gong_enhanced",
                }
        else:
            # Process through base orchestrator
            logger.info(f"Processing query through base orchestrator: {query}")
            return await self.base_orchestrator.process_query(query, context)

    async def stream_process_with_gong(
        self, query: str, context: dict[str, Any] = None
    ):
        """Stream processing with Gong intelligence integration"""

        # First yield Gong intelligence if applicable
        if self.gong_integration.is_gong_query(query):
            yield {
                "type": "gong_analysis_started",
                "message": "Analyzing conversation intelligence...",
                "timestamp": datetime.now().isoformat(),
            }

            gong_result = await self.gong_integration.process_gong_query(query, context)

            yield {
                "type": "gong_analysis_complete",
                "data": gong_result,
                "timestamp": datetime.now().isoformat(),
            }

        # Then stream through base orchestrator
        async for update in self.base_orchestrator.stream_process(query, context):
            yield update
