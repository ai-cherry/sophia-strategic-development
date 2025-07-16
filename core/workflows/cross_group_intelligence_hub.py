"""
Cross-Group Intelligence Hub for Sophia AI
Facilitates knowledge sharing and collaboration between agent groups
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from infrastructure.mcp_servers.enhanced_ai_memory_mcp_server import (
    EnhancedAiMemoryMCPServer,
)
from backend.services.sophia_unified_memory_service import SophiaUnifiedMemoryService

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of insights that can be shared"""

    TECHNICAL_PATTERN = "technical_pattern"
    BUSINESS_METRIC = "business_metric"
    CUSTOMER_FEEDBACK = "customer_feedback"
    MARKET_INTELLIGENCE = "market_intelligence"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    RISK_ASSESSMENT = "risk_assessment"
    OPPORTUNITY_IDENTIFICATION = "opportunity_identification"


@dataclass
class CrossGroupInsight:
    """Represents an insight that can be shared across groups"""

    id: str
    source_group: str
    insight_type: InsightType
    content: str
    confidence: float
    relevance_score: float
    metadata: dict[str, Any]
    created_at: datetime
    used_count: int = 0


class SharedInsightStore:
    """In-memory store for cross-group insights"""

    def __init__(self):
        self.insights: dict[str, CrossGroupInsight] = {}
        self.group_index: dict[str, list[str]] = {}
        self.type_index: dict[InsightType, list[str]] = {}

    async def add_insight(self, insight: CrossGroupInsight):
        """Add a new insight to the store"""
        self.insights[insight.id] = insight

        # Update indices
        if insight.source_group not in self.group_index:
            self.group_index[insight.source_group] = []
        self.group_index[insight.source_group].append(insight.id)

        if insight.insight_type not in self.type_index:
            self.type_index[insight.insight_type] = []
        self.type_index[insight.insight_type].append(insight.id)

        logger.info(f"Added insight {insight.id} from {insight.source_group}")

    async def search(
        self,
        query: str,
        exclude_group: str | None = None,
        insight_types: list[InsightType] | None = None,
    ) -> list[CrossGroupInsight]:
        """Search for relevant insights"""
        results = []

        for insight in self.insights.values():
            # Skip if from excluded group
            if exclude_group and insight.source_group == exclude_group:
                continue

            # Filter by type if specified
            if insight_types and insight.insight_type not in insight_types:
                continue

            # Simple relevance check (in production, use embeddings)
            if query.lower() in insight.content.lower():
                results.append(insight)

        # Sort by relevance and recency
        results.sort(key=lambda x: (x.relevance_score, x.created_at), reverse=True)

        return results[:10]  # Limit results


class CollaborationPatternLearner:
    """Learns patterns of successful cross-group collaborations"""

    def __init__(self):
        self.collaboration_history: list[dict[str, Any]] = []
        self.success_patterns: dict[str, float] = {}

    async def record_collaboration(
        self, groups: list[str], query: str, outcome: str, success_score: float
    ):
        """Record a collaboration instance"""
        self.collaboration_history.append(
            {
                "groups": groups,
                "query": query,
                "outcome": outcome,
                "success_score": success_score,
                "timestamp": datetime.now(),
            }
        )

        # Update success patterns
        pattern_key = f"{'-'.join(sorted(groups))}"
        if pattern_key not in self.success_patterns:
            self.success_patterns[pattern_key] = 0.0

        # Running average
        self.success_patterns[pattern_key] = (
            self.success_patterns[pattern_key] * 0.9 + success_score * 0.1
        )

    def get_recommended_groups(self, primary_group: str, query_type: str) -> list[str]:
        """Recommend groups to collaborate with based on patterns"""
        recommendations = []

        for pattern, score in self.success_patterns.items():
            if primary_group in pattern and score > 0.7:
                groups = pattern.split("-")
                for group in groups:
                    if group != primary_group:
                        recommendations.append(group)

        return list(set(recommendations))


class CrossGroupIntelligenceHub:
    """
    Central hub for cross-group intelligence sharing and collaboration
    """

    def __init__(self):
        self.insight_store = SharedInsightStore()
        self.collaboration_learner = CollaborationPatternLearner()
        self.cortex_service = SophiaUnifiedMemoryService()
        self.memory_service = EnhancedAiMemoryMCPServer()

    async def submit_insight(
        self,
        source_group: str,
        insight_type: InsightType,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Submit an insight from a group"""
        import uuid

        # Calculate relevance score using Cortex
        try:
            async with self.cortex_service as cortex:
                relevance_prompt = f"""
                Rate the business value and cross-functional relevance of this insight:
                {content}

                Return a score from 0.0 to 1.0.
                """
                relevance_result = await cortex.complete_text_with_cortex(
                    prompt=relevance_prompt, max_tokens=50
                )
                relevance_score = float(relevance_result.strip())
        except:
            relevance_score = 0.5

        insight = CrossGroupInsight(
            id=str(uuid.uuid4()),
            source_group=source_group,
            insight_type=insight_type,
            content=content,
            confidence=0.8,  # Default confidence
            relevance_score=relevance_score,
            metadata=metadata or {},
            created_at=datetime.now(),
        )

        await self.insight_store.add_insight(insight)

        # Store in memory for persistence
        await self.memory_service.store_kb_article_memory(
            article_id=insight.id,
            title=f"Cross-Group Insight: {insight_type.value}",
            content=content,
            category="cross_group_intelligence",
            author=source_group,
            keywords=[source_group, insight_type.value],
            importance_score=relevance_score,
        )

        return insight.id

    async def request_cross_group_insight(
        self, requesting_group: str, query: str, context: dict[str, Any]
    ) -> CrossGroupInsight | None:
        """Request insights from other groups"""
        # Find relevant insights
        relevant_insights = await self.insight_store.search(
            query=query, exclude_group=requesting_group
        )

        if not relevant_insights:
            return None

        # Synthesize insights
        synthesis = await self._synthesize_insights(relevant_insights, context)

        if not synthesis:
            return None

        # Record collaboration
        contributing_groups = list({i.source_group for i in relevant_insights})
        await self.collaboration_learner.record_collaboration(
            groups=[requesting_group, *contributing_groups],
            query=query,
            outcome=synthesis.content[:100],
            success_score=synthesis.confidence,
        )

        # Update usage counts
        for insight in relevant_insights:
            insight.used_count += 1

        return synthesis

    async def _synthesize_insights(
        self, insights: list[CrossGroupInsight], context: dict[str, Any]
    ) -> CrossGroupInsight | None:
        """Synthesize multiple insights into a unified response"""
        if not insights:
            return None

        # Use Cortex to synthesize
        insights_text = "\n\n".join(
            [
                f"From {i.source_group} ({i.insight_type.value}):\n{i.content}"
                for i in insights[:5]
            ]
        )

        synthesis_prompt = f"""
        Synthesize these cross-functional insights into a unified recommendation:

        {insights_text}

        Context: {context}

        Provide a clear, actionable synthesis that leverages all perspectives.
        """

        try:
            async with self.cortex_service as cortex:
                synthesis_content = await cortex.complete_text_with_cortex(
                    prompt=synthesis_prompt, max_tokens=500
                )
        except:
            synthesis_content = "Combined insights from multiple groups."

        import uuid

        return CrossGroupInsight(
            id=str(uuid.uuid4()),
            source_group="cross_group_synthesis",
            insight_type=InsightType.OPPORTUNITY_IDENTIFICATION,
            content=synthesis_content,
            confidence=sum(i.confidence for i in insights) / len(insights),
            relevance_score=max(i.relevance_score for i in insights),
            metadata={
                "source_insights": [i.id for i in insights],
                "contributing_groups": list({i.source_group for i in insights}),
            },
            created_at=datetime.now(),
        )

    async def get_collaboration_recommendations(self, group: str) -> list[str]:
        """Get recommended groups for collaboration"""
        return self.collaboration_learner.get_recommended_groups(group, "general")

    async def get_hub_statistics(self) -> dict[str, Any]:
        """Get statistics about the intelligence hub"""
        total_insights = len(self.insight_store.insights)
        insights_by_group = {}
        insights_by_type = {}

        for insight in self.insight_store.insights.values():
            # By group
            if insight.source_group not in insights_by_group:
                insights_by_group[insight.source_group] = 0
            insights_by_group[insight.source_group] += 1

            # By type
            if insight.insight_type.value not in insights_by_type:
                insights_by_type[insight.insight_type.value] = 0
            insights_by_type[insight.insight_type.value] += 1

        return {
            "total_insights": total_insights,
            "insights_by_group": insights_by_group,
            "insights_by_type": insights_by_type,
            "collaboration_patterns": self.collaboration_learner.success_patterns,
            "average_relevance_score": (
                sum(i.relevance_score for i in self.insight_store.insights.values())
                / total_insights
                if total_insights > 0
                else 0
            ),
        }
