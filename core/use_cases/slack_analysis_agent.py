#!/usr/bin/env python3
"""
Slack Analysis Agent
Advanced AI-driven analysis of Slack conversations for business insights
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from core.agents.base_agent import BaseAgent
from infrastructure.mcp_servers.enhanced_ai_memory_mcp_server import (
    EnhancedAiMemoryMCPServer,
)
from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2

logger = logging.getLogger(__name__)


class SlackInsightType(Enum):
    """Types of Slack insights"""

    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TOPIC_EXTRACTION = "topic_extraction"
    ACTION_ITEMS = "action_items"
    DECISION_TRACKING = "decision_tracking"
    CUSTOMER_FEEDBACK = "customer_feedback"


@dataclass
class SlackConversation:
    """Slack conversation data structure"""

    conversation_id: str
    channel_name: str
    title: str
    participants: list[str]
    message_count: int
    start_time: datetime
    end_time: datetime
    messages: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SlackInsight:
    """Slack conversation insight"""

    insight_type: SlackInsightType
    conversation_id: str
    channel_name: str
    summary: str
    details: dict[str, Any]
    confidence_score: float
    business_impact: str
    recommended_actions: list[str]


@dataclass
class SlackAnalysisResult:
    """Result of Slack analysis"""

    conversation: SlackConversation
    insights: list[SlackInsight]
    overall_sentiment: float
    key_topics: list[str]
    action_items: list[str]
    decisions_made: list[str]
    business_value_score: float
    processing_time: float


class SlackAnalysisAgent(BaseAgent):
    """Slack Analysis Agent for AI-driven conversation insights"""

    def __init__(self):
        super().__init__()
        self.name = "slack_analysis"
        self.description = "AI-driven Slack conversation analysis and insights"

        self.cortex_service: QdrantUnifiedMemoryService | None = None
        self.ai_memory: EnhancedAiMemoryMCPServer | None = None
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize Slack Analysis Agent"""
        if self.initialized:
            return

        try:
            self.cortex_service = UnifiedMemoryServiceV2()
            self.ai_memory = EnhancedAiMemoryMCPServer()

            await self.ai_memory.initialize()

            self.initialized = True
            logger.info("✅ Slack Analysis Agent initialized")

        except Exception as e:
            logger.exception(f"Failed to initialize Slack Analysis Agent: {e}")
            raise

    async def analyze_conversation(
        self,
        conversation: SlackConversation,
        analysis_types: list[SlackInsightType] | None = None,
    ) -> SlackAnalysisResult:
        """Analyze a Slack conversation for insights"""
        if not self.initialized:
            await self.initialize()

        start_time = asyncio.get_event_loop().time()

        try:
            if not analysis_types:
                analysis_types = list(SlackInsightType)

            conversation_text = self._extract_conversation_text(conversation)

            # Perform analysis
            insights = []

            if SlackInsightType.SENTIMENT_ANALYSIS in analysis_types:
                sentiment_insight = await self._analyze_sentiment(
                    conversation, conversation_text
                )
                if sentiment_insight:
                    insights.append(sentiment_insight)

            if SlackInsightType.TOPIC_EXTRACTION in analysis_types:
                topic_insight = await self._extract_topics(
                    conversation, conversation_text
                )
                if topic_insight:
                    insights.append(topic_insight)

            # Calculate metrics
            overall_sentiment = await self._calculate_overall_sentiment(
                conversation_text
            )
            key_topics = await self._extract_key_topics(conversation_text)
            action_items = await self._extract_action_items(conversation_text)
            decisions_made = await self._extract_decisions(conversation_text)
            business_value_score = self._calculate_business_value_score(
                conversation_text, insights
            )

            processing_time = asyncio.get_event_loop().time() - start_time

            result = SlackAnalysisResult(
                conversation=conversation,
                insights=insights,
                overall_sentiment=overall_sentiment,
                key_topics=key_topics,
                action_items=action_items,
                decisions_made=decisions_made,
                business_value_score=business_value_score,
                processing_time=processing_time,
            )

            await self._store_analysis_in_memory(result)

            return result

        except Exception as e:
            logger.exception(f"Error analyzing Slack conversation: {e}")
            raise

    async def _analyze_sentiment(
        self, conversation: SlackConversation, text: str
    ) -> SlackInsight:
        """Analyze sentiment of conversation"""
        try:
            async with self.cortex_service as cortex:
                sentiment_prompt = f"""
                Analyze the sentiment of this Slack conversation:

                Conversation from #{conversation.channel_name}:
                {text[:1000]}

                Provide overall sentiment score (-1 to 1) and tone analysis.
                """

                sentiment_analysis = await 
                    prompt=sentiment_prompt, max_tokens=200
                )

                return SlackInsight(
                    insight_type=SlackInsightType.SENTIMENT_ANALYSIS,
                    conversation_id=conversation.conversation_id,
                    channel_name=conversation.channel_name,
                    summary=f"Sentiment analysis: {sentiment_analysis[:100]}",
                    details={"analysis": sentiment_analysis},
                    confidence_score=0.8,
                    business_impact="Medium - Sentiment affects team morale",
                    recommended_actions=["Monitor team sentiment trends"],
                )

        except Exception as e:
            logger.exception(f"Error analyzing sentiment: {e}")
            return None

    async def _extract_topics(
        self, conversation: SlackConversation, text: str
    ) -> SlackInsight:
        """Extract key topics from conversation"""
        try:
            async with self.cortex_service as cortex:
                topic_prompt = f"""
                Extract key topics from this Slack conversation:

                {text[:1000]}

                List the main topics discussed.
                """

                topic_analysis = await 
                    prompt=topic_prompt, max_tokens=200
                )

                return SlackInsight(
                    insight_type=SlackInsightType.TOPIC_EXTRACTION,
                    conversation_id=conversation.conversation_id,
                    channel_name=conversation.channel_name,
                    summary=f"Key topics: {topic_analysis[:100]}",
                    details={"topics": topic_analysis},
                    confidence_score=0.75,
                    business_impact="Medium - Topics indicate discussion focus",
                    recommended_actions=["Track important topics for follow-up"],
                )

        except Exception as e:
            logger.exception(f"Error extracting topics: {e}")
            return None

    def _extract_conversation_text(self, conversation: SlackConversation) -> str:
        """Extract text content from conversation messages"""
        text_parts = []

        for message in conversation.messages:
            user = message.get("user", "Unknown")
            text = message.get("text", "")
            text_parts.append(f"[{user}]: {text}")

        return "\n".join(text_parts)

    async def _calculate_overall_sentiment(self, text: str) -> float:
        """Calculate overall sentiment score"""
        try:
            async with self.cortex_service as cortex:
                sentiment_result = await cortex.analyze_sentiment_with_cortex(
                    text[:500]
                )
                return sentiment_result.get("sentiment_score", 0.0)
        except (AttributeError, KeyError, ValueError, Exception) as e:
            logger.warning(f"Failed to calculate sentiment: {e}")
            return 0.0

    async def _extract_key_topics(self, text: str) -> list[str]:
        """Extract key topics from text"""
        try:
            async with self.cortex_service as cortex:
                topics_prompt = f"Extract 3 key topics from: {text[:300]}"
                topics_result = await 
                    topics_prompt, max_tokens=50
                )
                return [topic.strip() for topic in topics_result.split(",")[:3]]
        except (AttributeError, ValueError, Exception) as e:
            logger.warning(f"Failed to extract topics: {e}")
            return ["General discussion"]

    async def _extract_action_items(self, text: str) -> list[str]:
        """Extract action items from text"""
        try:
            async with self.cortex_service as cortex:
                actions_prompt = f"Extract action items from: {text[:300]}"
                actions_result = await 
                    actions_prompt, max_tokens=100
                )
                return [
                    action.strip()
                    for action in actions_result.split("\n")
                    if action.strip()
                ][:3]
        except (AttributeError, ValueError, Exception) as e:
            logger.warning(f"Failed to extract action items: {e}")
            return []

    async def _extract_decisions(self, text: str) -> list[str]:
        """Extract decisions from text"""
        try:
            async with self.cortex_service as cortex:
                decisions_prompt = f"Extract decisions made from: {text[:300]}"
                decisions_result = await 
                    decisions_prompt, max_tokens=100
                )
                return [
                    decision.strip()
                    for decision in decisions_result.split("\n")
                    if decision.strip()
                ][:3]
        except (AttributeError, ValueError, Exception) as e:
            logger.warning(f"Failed to extract decisions: {e}")
            return []

    def _calculate_business_value_score(
        self, text: str, insights: list[SlackInsight]
    ) -> float:
        """Calculate business value score for conversation"""
        score = 0.0

        business_keywords = ["customer", "revenue", "deal", "project", "deadline"]
        keyword_count = sum(
            1 for keyword in business_keywords if keyword in text.lower()
        )
        score += min(keyword_count * 0.2, 0.6)

        if insights:
            avg_confidence = sum(
                insight.confidence_score for insight in insights
            ) / len(insights)
            score += avg_confidence * 0.4

        return min(score, 1.0)

    async def _store_analysis_in_memory(self, result: SlackAnalysisResult) -> None:
        """Store analysis result in AI Memory"""
        try:
            if not self.ai_memory:
                return

            memory_content = f"""
            Slack Conversation Analysis
            Channel: #{result.conversation.channel_name}
            Participants: {", ".join(result.conversation.participants)}

            Overall Sentiment: {result.overall_sentiment:.2f}
            Business Value: {result.business_value_score:.2f}
            Topics: {", ".join(result.key_topics)}
            Action Items: {len(result.action_items)}
            """

            await self.ai_memory.store_memory(
                content=memory_content,
                category="slack_analysis",
                tags=["slack", "conversation", "analysis"],
                metadata={
                    "conversation_id": result.conversation.conversation_id,
                    "channel": result.conversation.channel_name,
                    "sentiment": result.overall_sentiment,
                    "business_value": result.business_value_score,
                },
                importance_score=result.business_value_score,
            )

        except Exception as e:
            logger.exception(f"Error storing analysis in AI Memory: {e}")
