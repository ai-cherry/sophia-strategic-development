#!/usr/bin/env python3
"""
Enhanced Sentiment Analyzer for Sophia AI
Implements advanced multi-channel sentiment analysis with nuanced emotion detection
"""

from backend.services.unified_memory_service_primary import UnifiedMemoryService
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class SentimentChannel(str, Enum):
    """Supported sentiment analysis channels"""

    GONG_CALLS = "gong_calls"
    GONG_TRANSCRIPTS = "gong_transcripts"
    SLACK_MESSAGES = "slack_messages"
    LINEAR_COMMENTS = "linear_comments"
    ASANA_TASKS = "asana_tasks"
    HUBSPOT_EMAILS = "hubspot_emails"
    EXTERNAL_WEB = "external_web"


class EmotionCategory(str, Enum):
    """Nuanced emotion categories"""

    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CONCERNED = "concerned"
    SATISFIED = "satisfied"
    OVERWHELMED = "overwhelmed"
    OPTIMISTIC = "optimistic"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    DISAPPOINTED = "disappointed"
    ENGAGED = "engaged"
    NEUTRAL = "neutral"


@dataclass
class SentimentAnalysisResult:
    """Comprehensive sentiment analysis result"""

    text: str
    channel: SentimentChannel
    primary_sentiment: float  # -1.0 to 1.0
    emotion_categories: list[EmotionCategory]
    intensity_score: str  # high, medium, low
    context_indicators: list[str]
    urgency_level: str  # high, medium, low
    confidence_score: float  # 0.0 to 1.0
    business_impact_score: float  # 0.0 to 1.0
    recommendations: list[str]
    timestamp: datetime
    metadata: dict[str, Any]


@dataclass
class CrossChannelCorrelation:
    """Cross-channel sentiment correlation analysis"""

    employee_sentiment: float
    customer_sentiment: float
    correlation_coefficient: float
    lag_analysis: dict[str, float]  # 1day, 3day, 7day correlations
    trend_direction: str  # improving, declining, stable
    risk_level: str  # high, medium, low
    insights: list[str]
    recommended_actions: list[str]


class EnhancedSentimentAnalyzer:
    """
    Advanced sentiment analyzer with multi-channel support and nuanced emotion detection
    """

    def __init__(self):
        self.domain_vocabulary = self._load_domain_vocabulary()
        self.sentiment_adjustments = self._load_sentiment_adjustments()
        self.channel_analyzers = self._initialize_channel_analyzers()

    def _load_domain_vocabulary(self) -> dict[str, list[str]]:
        """Load Pay Ready specific domain vocabulary"""
        return {
            "payment_processing": [
                "payment",
                "transaction",
                "processing",
                "gateway",
                "settlement",
            ],
            "client_satisfaction": [
                "onboarding",
                "integration",
                "support",
                "documentation",
                "training",
            ],
            "technical_issues": [
                "latency",
                "downtime",
                "api",
                "error",
                "bug",
                "timeout",
                "failure",
            ],
            "business_growth": [
                "revenue",
                "expansion",
                "upsell",
                "retention",
                "churn",
                "growth",
            ],
            "team_dynamics": [
                "collaboration",
                "communication",
                "workload",
                "deadline",
                "stress",
            ],
        }

    def _load_sentiment_adjustments(self) -> dict[str, dict[str, float]]:
        """Load domain-specific sentiment adjustments"""
        return {
            "payment_processing": {
                "failed transaction": -0.8,
                "successful integration": 0.7,
                "fast processing": 0.6,
                "delayed payment": -0.6,
                "99.9% uptime": 0.8,
            },
            "technical_performance": {
                "200ms latency": -0.4,  # In fintech, this might be concerning
                "sub-100ms": 0.5,
                "api timeout": -0.7,
                "zero downtime": 0.9,
            },
            "team_dynamics": {
                "work-life balance": 0.4,
                "overtime": -0.3,
                "deadline pressure": -0.5,
                "team celebration": 0.8,
            },
        }

    def _initialize_channel_analyzers(self) -> dict[SentimentChannel, Any]:
        """Initialize channel-specific analyzers"""
        return {
            SentimentChannel.GONG_CALLS: self._create_gong_analyzer(),
            SentimentChannel.SLACK_MESSAGES: self._create_slack_analyzer(),
            SentimentChannel.LINEAR_COMMENTS: self._create_linear_analyzer(),
            SentimentChannel.ASANA_TASKS: self._create_asana_analyzer(),
            SentimentChannel.HUBSPOT_EMAILS: self._create_hubspot_analyzer(),
            SentimentChannel.EXTERNAL_WEB: self._create_web_analyzer(),
        }

    async def analyze_sentiment(
        self,
        text: str,
        channel: SentimentChannel,
        context: dict[str, Any] | None = None,
    ) -> SentimentAnalysisResult:
        """
        Perform comprehensive sentiment analysis
        """
        try:
            # Basic sentiment analysis (placeholder for Lambda GPU integration)
            primary_sentiment = await self._analyze_primary_sentiment(text, channel)

            # Emotion categorization
            emotion_categories = await self._categorize_emotions(text, channel)

            # Intensity scoring
            intensity_score = self._calculate_intensity(primary_sentiment, text)

            # Context analysis
            context_indicators = self._extract_context_indicators(text, channel)

            # Urgency assessment
            urgency_level = self._assess_urgency(text, primary_sentiment, context)

            # Confidence scoring
            confidence_score = self._calculate_confidence(text, primary_sentiment)

            # Business impact assessment
            business_impact_score = self._assess_business_impact(text, channel, context)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                primary_sentiment, emotion_categories, urgency_level, channel
            )

            return SentimentAnalysisResult(
                text=text,
                channel=channel,
                primary_sentiment=primary_sentiment,
                emotion_categories=emotion_categories,
                intensity_score=intensity_score,
                context_indicators=context_indicators,
                urgency_level=urgency_level,
                confidence_score=confidence_score,
                business_impact_score=business_impact_score,
                recommendations=recommendations,
                timestamp=datetime.now(),
                metadata=context or {},
            )

        except Exception as e:
            logger.exception(f"Sentiment analysis failed: {e}")
            # Return neutral result on error
            return self._create_fallback_result(text, channel)

    async def _analyze_primary_sentiment(
        self, text: str, channel: SentimentChannel
    ) -> float:
        """Analyze primary sentiment score"""
        # Placeholder for Lambda GPU integration
        # In real implementation, this would call self.QDRANT_service.await self.lambda_gpu.analyze_sentiment()

        base_sentiment = 0.0

        # Simple keyword-based analysis for demonstration
        positive_keywords = [
            "great",
            "excellent",
            "happy",
            "excited",
            "successful",
            "amazing",
        ]
        negative_keywords = [
            "frustrated",
            "angry",
            "disappointed",
            "failed",
            "problem",
            "issue",
        ]

        text_lower = text.lower()

        for keyword in positive_keywords:
            if keyword in text_lower:
                base_sentiment += 0.2

        for keyword in negative_keywords:
            if keyword in text_lower:
                base_sentiment -= 0.3

        # Apply domain-specific adjustments
        domain_adjustment = self._apply_domain_adjustments(text, channel)

        # Combine base sentiment with domain adjustments
        final_sentiment = max(-1.0, min(1.0, base_sentiment + domain_adjustment))

        return final_sentiment

    def _apply_domain_adjustments(self, text: str, channel: SentimentChannel) -> float:
        """Apply domain-specific sentiment adjustments"""
        adjustment = 0.0
        text_lower = text.lower()

        for phrases in self.sentiment_adjustments.values():
            for phrase, score_adjustment in phrases.items():
                if phrase in text_lower:
                    adjustment += score_adjustment * 0.1  # Scale down the adjustment

        return adjustment

    async def _categorize_emotions(
        self, text: str, channel: SentimentChannel
    ) -> list[EmotionCategory]:
        """Categorize emotions in the text"""
        # Placeholder for Lambda GPU CLASSIFY function
        # In real implementation, this would call await self.lambda_gpu.CLASSIFY()

        emotions = []
        text_lower = text.lower()

        emotion_keywords = {
            EmotionCategory.EXCITED: ["excited", "thrilled", "amazing", "fantastic"],
            EmotionCategory.FRUSTRATED: ["frustrated", "annoyed", "irritated"],
            EmotionCategory.CONCERNED: ["concerned", "worried", "anxious"],
            EmotionCategory.SATISFIED: ["satisfied", "happy", "pleased"],
            EmotionCategory.OVERWHELMED: ["overwhelmed", "stressed", "too much"],
            EmotionCategory.OPTIMISTIC: ["optimistic", "hopeful", "positive"],
            EmotionCategory.CONFIDENT: ["confident", "sure", "certain"],
            EmotionCategory.DISAPPOINTED: ["disappointed", "let down", "failed"],
        }

        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                emotions.append(emotion)

        return emotions if emotions else [EmotionCategory.NEUTRAL]

    def _calculate_intensity(self, sentiment_score: float, text: str) -> str:
        """Calculate sentiment intensity"""
        abs_score = abs(sentiment_score)

        # Check for intensity indicators in text
        intensity_indicators = {
            "high": ["very", "extremely", "really", "absolutely", "completely"],
            "medium": ["quite", "fairly", "somewhat", "pretty"],
            "low": ["slightly", "a bit", "kind of", "sort of"],
        }

        text_lower = text.lower()

        for intensity, indicators in intensity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return intensity

        # Fall back to score-based intensity
        if abs_score > 0.7:
            return "high"
        elif abs_score > 0.3:
            return "medium"
        else:
            return "low"

    def _extract_context_indicators(
        self, text: str, channel: SentimentChannel
    ) -> list[str]:
        """Extract context indicators from text"""
        indicators = []
        text_lower = text.lower()

        # Domain-specific context indicators
        for domain, keywords in self.domain_vocabulary.items():
            if any(keyword in text_lower for keyword in keywords):
                indicators.append(domain)

        # Channel-specific indicators
        if channel == SentimentChannel.SLACK_MESSAGES:
            if any(word in text_lower for word in ["meeting", "standup", "demo"]):
                indicators.append("meeting_context")
        elif channel == SentimentChannel.GONG_CALLS:
            if any(word in text_lower for word in ["customer", "client", "prospect"]):
                indicators.append("customer_interaction")

        return indicators

    def _assess_urgency(
        self, text: str, sentiment_score: float, context: dict[str, Any] | None
    ) -> str:
        """Assess urgency level"""
        text_lower = text.lower()

        # High urgency indicators
        urgent_keywords = ["urgent", "asap", "immediately", "critical", "emergency"]
        if any(keyword in text_lower for keyword in urgent_keywords):
            return "high"

        # Sentiment-based urgency
        if sentiment_score < -0.6:
            return "high"
        elif sentiment_score < -0.3:
            return "medium"

        return "low"

    def _calculate_confidence(self, text: str, sentiment_score: float) -> float:
        """Calculate confidence in sentiment analysis"""
        # Factors affecting confidence
        text_length = len(text.split())

        # Longer texts generally provide more confidence
        length_factor = min(1.0, text_length / 20.0)

        # Clear sentiment signals increase confidence
        sentiment_clarity = abs(sentiment_score)

        # Combine factors
        confidence = length_factor * 0.4 + sentiment_clarity * 0.6

        return max(0.1, min(0.95, confidence))

    def _assess_business_impact(
        self, text: str, channel: SentimentChannel, context: dict[str, Any] | None
    ) -> float:
        """Assess business impact score"""
        impact_score = 0.5  # Base impact

        text_lower = text.lower()

        # High impact keywords
        high_impact_keywords = [
            "revenue",
            "customer",
            "churn",
            "retention",
            "deal",
            "contract",
        ]
        if any(keyword in text_lower for keyword in high_impact_keywords):
            impact_score += 0.3

        # Channel-based impact
        channel_impact = {
            SentimentChannel.GONG_CALLS: 0.8,  # Customer interactions have high impact
            SentimentChannel.HUBSPOT_EMAILS: 0.7,
            SentimentChannel.SLACK_MESSAGES: 0.5,
            SentimentChannel.LINEAR_COMMENTS: 0.4,
            SentimentChannel.ASANA_TASKS: 0.4,
        }

        impact_score *= channel_impact.get(channel, 0.5)

        return max(0.0, min(1.0, impact_score))

    def _generate_recommendations(
        self,
        sentiment_score: float,
        emotions: list[EmotionCategory],
        urgency: str,
        channel: SentimentChannel,
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Sentiment-based recommendations
        if sentiment_score < -0.5:
            recommendations.append(
                "Immediate attention required - consider direct follow-up"
            )
            if urgency == "high":
                recommendations.append(
                    "Escalate to management for immediate intervention"
                )
        elif sentiment_score < -0.2:
            recommendations.append("Monitor for additional stress indicators")
            recommendations.append("Consider proactive check-in within 24 hours")
        elif sentiment_score > 0.5:
            recommendations.append(
                "Positive sentiment detected - opportunity for recognition"
            )

        # Emotion-based recommendations
        if EmotionCategory.OVERWHELMED in emotions:
            recommendations.append(
                "Consider workload redistribution or additional support"
            )
        if EmotionCategory.FRUSTRATED in emotions:
            recommendations.append("Identify and address source of frustration")
        if EmotionCategory.EXCITED in emotions:
            recommendations.append("Leverage positive energy for team motivation")

        # Channel-specific recommendations
        if channel == SentimentChannel.SLACK_MESSAGES and sentiment_score < -0.3:
            recommendations.append(
                "Monitor team channel for collective sentiment trends"
            )
        elif channel == SentimentChannel.GONG_CALLS and sentiment_score < -0.4:
            recommendations.append("Review call for customer satisfaction issues")

        return recommendations if recommendations else ["Continue normal monitoring"]

    def _create_fallback_result(
        self, text: str, channel: SentimentChannel
    ) -> SentimentAnalysisResult:
        """Create fallback result when analysis fails"""
        return SentimentAnalysisResult(
            text=text,
            channel=channel,
            primary_sentiment=0.0,
            emotion_categories=[EmotionCategory.NEUTRAL],
            intensity_score="low",
            context_indicators=["analysis_failed"],
            urgency_level="low",
            confidence_score=0.1,
            business_impact_score=0.0,
            recommendations=["Analysis failed - manual review recommended"],
            timestamp=datetime.now(),
            metadata={"error": "sentiment_analysis_failed"},
        )

    # Channel-specific analyzer creation methods (placeholders)
    def _create_gong_analyzer(self):
        """Create Gong-specific analyzer"""
        return {"type": "gong", "features": ["call_context", "speaker_analysis"]}

    def _create_slack_analyzer(self):
        """Create Slack-specific analyzer"""
        return {"type": "slack", "features": ["channel_context", "team_dynamics"]}

    def _create_linear_analyzer(self):
        """Create Linear-specific analyzer"""
        return {"type": "linear", "features": ["project_context", "task_priority"]}

    def _create_asana_analyzer(self):
        """Create Asana-specific analyzer"""
        return {"type": "asana", "features": ["task_context", "deadline_pressure"]}

    def _create_hubspot_analyzer(self):
        """Create HubSpot-specific analyzer"""
        return {"type": "hubspot", "features": ["customer_context", "deal_stage"]}

    def _create_web_analyzer(self):
        """Create web content analyzer"""
        return {"type": "web", "features": ["public_sentiment", "brand_perception"]}


# Global instance
enhanced_sentiment_analyzer = EnhancedSentimentAnalyzer()
