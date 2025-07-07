"""
Memory Integration for Gong V2 MCP Server
Stores call insights, decisions, and important moments as memories
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from shared.clients.memory_client import (
    MemoryClient,
    MemoryType,
    store_event,
    store_insight,
)

logger = logging.getLogger(__name__)


class GongMemoryIntegration:
    """
    Integrates Gong call data with AI Memory V2
    Automatically stores important call moments as memories
    """

    def __init__(self):
        self.memory_client = MemoryClient()
        self.min_sentiment_threshold = 0.7  # For positive insights
        self.max_sentiment_threshold = -0.5  # For negative alerts

    async def process_call_completed(self, call_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a completed call and store relevant memories

        Args:
            call_data: Complete call data from Gong

        Returns:
            Summary of memories created
        """
        memories_created = {"events": 0, "insights": 0, "decisions": 0, "total": 0}

        try:
            # Store call completion event
            await store_event(
                source="gong",
                event_type="call_completed",
                content={
                    "call_id": call_data.get("id"),
                    "customer": call_data.get("customer_name"),
                    "duration": call_data.get("duration"),
                    "participants": call_data.get("participants", []),
                    "topics": call_data.get("topics", []),
                },
                severity="info",
            )
            memories_created["events"] += 1

            # Process sentiment insights
            sentiment = call_data.get("sentiment_score", 0)
            if sentiment > self.min_sentiment_threshold:
                await self._store_positive_insight(call_data)
                memories_created["insights"] += 1
            elif sentiment < self.max_sentiment_threshold:
                await self._store_negative_alert(call_data)
                memories_created["insights"] += 1

            # Process action items as decisions
            action_items = call_data.get("action_items", [])
            for item in action_items:
                await self._store_action_decision(call_data, item)
                memories_created["decisions"] += 1

            # Process key moments
            key_moments = call_data.get("key_moments", [])
            for moment in key_moments:
                if self._is_important_moment(moment):
                    await self._store_key_moment(call_data, moment)
                    memories_created["insights"] += 1

            memories_created["total"] = sum(memories_created.values())
            logger.info(
                f"Created {memories_created['total']} memories for call {call_data.get('id')}"
            )

            return memories_created

        except Exception as e:
            logger.error(f"Failed to process call memories: {e}")
            return memories_created

    async def _store_positive_insight(self, call_data: dict[str, Any]):
        """Store positive customer sentiment as insight"""
        await store_insight(
            category="customer_satisfaction",
            insight=f"Positive call with {call_data.get('customer_name')} - sentiment score {call_data.get('sentiment_score')}",
            confidence=0.9,
            recommendations=[
                f"Follow up with {call_data.get('customer_name')} to maintain momentum",
                "Share success patterns with team",
                "Consider upsell opportunities",
            ],
        )

    async def _store_negative_alert(self, call_data: dict[str, Any]):
        """Store negative sentiment as alert insight"""
        await store_insight(
            category="customer_risk",
            insight=f"Concerning call with {call_data.get('customer_name')} - sentiment score {call_data.get('sentiment_score')}",
            confidence=0.85,
            recommendations=[
                f"Schedule urgent follow-up with {call_data.get('customer_name')}",
                "Review call recording for specific concerns",
                "Consider escalation to management",
            ],
        )

    async def _store_action_decision(
        self, call_data: dict[str, Any], action_item: dict[str, Any]
    ):
        """Store action items as decision memories"""
        async with self.memory_client as client:
            await client.store_memory(
                MemoryType.DECISION,
                content={
                    "call_id": call_data.get("id"),
                    "customer": call_data.get("customer_name"),
                    "decision": action_item.get("description"),
                    "owner": action_item.get("assigned_to"),
                    "due_date": action_item.get("due_date"),
                    "priority": action_item.get("priority", "medium"),
                },
                metadata={
                    "source": "gong",
                    "call_date": call_data.get("date"),
                    "participants": call_data.get("participants", []),
                },
            )

    async def _store_key_moment(
        self, call_data: dict[str, Any], moment: dict[str, Any]
    ):
        """Store important call moments as insights"""
        moment_type = moment.get("type", "general")
        categories = {
            "objection": "sales_objection",
            "competitor": "competitive_intelligence",
            "pricing": "pricing_discussion",
            "feature": "feature_request",
            "complaint": "customer_complaint",
        }

        category = categories.get(moment_type, "call_insight")

        await store_insight(
            category=category,
            insight=f"{moment.get('description')} - {call_data.get('customer_name')}",
            confidence=moment.get("confidence", 0.7),
            recommendations=self._generate_moment_recommendations(moment_type, moment),
        )

    def _is_important_moment(self, moment: dict[str, Any]) -> bool:
        """Determine if a moment is important enough to store"""
        important_types = {
            "objection",
            "competitor",
            "pricing",
            "feature",
            "complaint",
            "decision",
        }
        return (
            moment.get("type") in important_types
            or moment.get("importance", 0) > 0.7
            or moment.get("sentiment_shift", 0) > 0.5
        )

    def _generate_moment_recommendations(
        self, moment_type: str, moment: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations based on moment type"""
        recommendations = {
            "objection": [
                "Prepare response for this objection",
                "Share objection handling with team",
                "Update sales playbook",
            ],
            "competitor": [
                "Update competitive intelligence",
                "Prepare battlecard",
                "Share with product team",
            ],
            "pricing": [
                "Review pricing strategy",
                "Consider custom package",
                "Escalate to sales management",
            ],
            "feature": [
                "Log feature request",
                "Share with product team",
                "Follow up on roadmap timing",
            ],
            "complaint": [
                "Immediate follow-up required",
                "Escalate to customer success",
                "Create action plan",
            ],
        }

        return recommendations.get(moment_type, ["Review and follow up appropriately"])

    async def search_call_memories(
        self,
        customer_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        Search for call-related memories

        Args:
            customer_name: Filter by customer
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of relevant memories
        """
        async with self.memory_client as client:
            # Search for all Gong-related memories
            memories = await client.search_memories(
                query=f"gong {customer_name or ''}".strip(),
                memory_types=[
                    MemoryType.EVENT,
                    MemoryType.INSIGHT,
                    MemoryType.DECISION,
                ],
                start_time=start_date,
                end_time=end_date,
                limit=50,
            )

            # Filter by customer if specified
            if customer_name:
                memories = [
                    m
                    for m in memories
                    if customer_name.lower() in str(m.get("content", {})).lower()
                ]

            return memories

    async def get_customer_insights(self, customer_name: str) -> dict[str, Any]:
        """
        Get all insights for a specific customer

        Args:
            customer_name: The customer to search for

        Returns:
            Categorized insights
        """
        memories = await self.search_call_memories(customer_name=customer_name)

        insights = {
            "total_calls": 0,
            "sentiment_trend": [],
            "key_decisions": [],
            "action_items": [],
            "risks": [],
            "opportunities": [],
        }

        for memory in memories:
            memory_type = memory.get("type")
            content = memory.get("content", {})

            if (
                memory_type == MemoryType.EVENT
                and content.get("event_type") == "call_completed"
            ):
                insights["total_calls"] += 1

            elif memory_type == MemoryType.INSIGHT:
                category = content.get("category")
                if category == "customer_risk":
                    insights["risks"].append(content)
                elif category == "customer_satisfaction":
                    insights["opportunities"].append(content)

            elif memory_type == MemoryType.DECISION:
                insights["key_decisions"].append(content)
                if content.get("priority") == "high":
                    insights["action_items"].append(content)

        return insights


# Singleton instance
gong_memory = GongMemoryIntegration()
