"""
Temporal Q&A Learning Service for Sophia AI
Enables natural language learning of date/time concepts through conversational interactions
Integrates with existing unified chat and knowledge base infrastructure
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from backend.core.date_time_manager import date_manager

logger = logging.getLogger(__name__)

# Try to import Snowflake Cortex service, fallback if not available
try:
    from backend.services.snowflake_cortex_service import SnowflakeCortexService

    CORTEX_AVAILABLE = True
except ImportError:
    CORTEX_AVAILABLE = False
    logger.warning("Snowflake Cortex service not available, using fallback analysis")


class TemporalLearningType(Enum):
    """Types of temporal learning interactions"""

    DATE_CORRECTION = "date_correction"
    TIME_CONTEXT = "time_context"
    TEMPORAL_REFERENCE = "temporal_reference"
    CURRENT_EVENTS = "current_events"
    SEASONAL_CONTEXT = "seasonal_context"
    BUSINESS_TIMELINE = "business_timeline"
    HISTORICAL_CONTEXT = "historical_context"


class LearningConfidence(Enum):
    """Confidence levels for learned temporal information"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


@dataclass
class TemporalLearningInteraction:
    """Represents a single temporal learning interaction"""

    id: str
    user_question: str
    user_correction: str
    system_response: str
    learning_type: TemporalLearningType
    confidence: LearningConfidence
    timestamp: datetime
    context: dict[str, Any] = field(default_factory=dict)
    validated: bool = False
    applied: bool = False


@dataclass
class TemporalKnowledge:
    """Represents learned temporal knowledge"""

    concept: str
    description: str
    examples: list[str]
    confidence: LearningConfidence
    source_interactions: list[str]
    last_updated: datetime
    usage_count: int = 0
    validation_score: float = 0.0


class TemporalQALearningService:
    """
    Natural language Q&A learning service for temporal awareness
    Integrates with existing unified chat and knowledge base infrastructure
    """

    def __init__(self):
        if CORTEX_AVAILABLE:
            try:
                self.cortex_service = SnowflakeCortexService()
            except Exception as e:
                logger.warning(f"Failed to initialize Snowflake Cortex service: {e}")
                self.cortex_service = None
        else:
            self.cortex_service = None

        # Current system temporal baseline
        self.system_date = date_manager.get_current_date_str()
        self.system_timezone = "UTC"

        # Learning storage
        self.learning_interactions: list[TemporalLearningInteraction] = []
        self.temporal_knowledge: dict[str, TemporalKnowledge] = {}

        # Learning patterns
        self.temporal_patterns = {
            "date_formats": [],
            "time_references": [],
            "temporal_references": [],
            "contextual_clues": [],
            "correction_patterns": [],
        }

        logger.info("🕒 Temporal Q&A Learning Service initialized")

    async def process_qa_interaction(
        self, user_message: str, context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Process a natural language Q&A interaction for temporal learning
        Integrates with existing chat infrastructure
        """
        if context is None:
            context = {}

        try:
            # Analyze if this is a temporal learning opportunity
            temporal_analysis = await self._analyze_temporal_content(user_message)

            if not temporal_analysis["is_temporal"]:
                return {"learning_applied": False, "reason": "not_temporal"}

            # Determine learning type and generate response
            learning_type = temporal_analysis["learning_type"]

            # Generate contextual response with learning integration
            response_data = await self._generate_learning_response(
                user_message, learning_type, context
            )

            # Create learning interaction record
            interaction = TemporalLearningInteraction(
                id=f"temporal_qa_{int(date_manager.now().timestamp())}",
                user_question=user_message,
                user_correction="",  # Will be filled if user provides correction
                system_response=response_data["response"],
                learning_type=learning_type,
                confidence=LearningConfidence.MEDIUM,
                timestamp=date_manager.now(),
                context=context,
            )

            # Store interaction
            self.learning_interactions.append(interaction)

            # Apply immediate learning if high confidence
            if temporal_analysis["confidence"] > 0.8:
                await self._apply_immediate_learning(interaction)

            return {
                "learning_applied": True,
                "interaction_id": interaction.id,
                "response": response_data["response"],
                "learning_type": learning_type.value,
                "confidence": temporal_analysis["confidence"],
                "suggestions": response_data.get("suggestions", []),
                "follow_up_questions": await self._generate_followup_questions(
                    learning_type
                ),
            }

        except Exception as e:
            logger.error(f"Error processing temporal Q&A interaction: {e}")
            return {"learning_applied": False, "error": str(e)}

    async def _analyze_temporal_content(self, message: str) -> dict[str, Any]:
        """Analyze message for temporal learning opportunities"""

        # Temporal keywords and patterns
        temporal_keywords = [
            "date",
            "time",
            "today",
            "yesterday",
            "tomorrow",
            "now",
            "current",
            "when",
            "what day",
            "what time",
            "calendar",
            "schedule",
            "deadline",
            "season",
            "month",
            "year",
            "week",
            "holiday",
            "event",
            "timeline",
        ]

        # Check for temporal content
        is_temporal = any(keyword in message.lower() for keyword in temporal_keywords)

        if not is_temporal:
            return {"is_temporal": False, "confidence": 0.0}

        # Use Snowflake Cortex for deeper analysis if available
        if self.cortex_service:
            try:
                analysis_prompt = f"""
                Analyze this message for temporal learning opportunities:
                Message: "{message}"

                Current system date: {self.system_date}

                Determine:
                1. Learning type (date_correction, time_context, temporal_reference, etc.)
                2. Confidence level (0.0 to 1.0)
                3. Key temporal concepts mentioned
                4. Learning opportunity description

                Return JSON format.
                """

                cortex_analysis = await self.cortex_service.complete_text(
                    prompt=analysis_prompt, max_tokens=500
                )

                # Parse Cortex response
                analysis_data = json.loads(cortex_analysis)

                # Determine learning type
                learning_type = self._determine_learning_type(message, analysis_data)

                return {
                    "is_temporal": True,
                    "learning_type": learning_type,
                    "confidence": analysis_data.get("confidence", 0.7),
                    "concepts": analysis_data.get("temporal_concepts", []),
                    "description": analysis_data.get("learning_opportunity", ""),
                }

            except Exception as e:
                logger.warning(f"Cortex analysis failed, using fallback: {e}")

        # Fallback analysis
        learning_type = self._determine_learning_type(message, {})
        return {
            "is_temporal": True,
            "learning_type": learning_type,
            "confidence": 0.6,
            "concepts": [],
            "description": "Basic temporal learning opportunity detected",
        }

    def _determine_learning_type(
        self, message: str, analysis_data: dict
    ) -> TemporalLearningType:
        """Determine the type of temporal learning from the message"""

        message_lower = message.lower()

        # Pattern matching for learning types
        if any(
            word in message_lower for word in ["correct", "wrong", "actually", "fix"]
        ):
            return TemporalLearningType.DATE_CORRECTION
        elif any(
            word in message_lower for word in ["context", "background", "situation"]
        ):
            return TemporalLearningType.TIME_CONTEXT
        elif any(
            word in message_lower for word in ["news", "events", "happening", "current"]
        ):
            return TemporalLearningType.CURRENT_EVENTS
        elif any(word in message_lower for word in ["season", "weather", "holiday"]):
            return TemporalLearningType.SEASONAL_CONTEXT
        elif any(
            word in message_lower
            for word in ["business", "work", "project", "deadline"]
        ):
            return TemporalLearningType.BUSINESS_TIMELINE
        elif any(
            word in message_lower for word in ["history", "past", "before", "ago"]
        ):
            return TemporalLearningType.HISTORICAL_CONTEXT
        else:
            return TemporalLearningType.TEMPORAL_REFERENCE

    async def _generate_learning_response(
        self, message: str, learning_type: TemporalLearningType, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate an educational response that incorporates learning"""

        # Response templates by learning type
        if learning_type == TemporalLearningType.DATE_CORRECTION:
            response = f"""
            Thank you for the correction! I want to learn from this interaction.

            Current system understanding: {self.system_date}
            Your input: "{message}"

            I'm analyzing this correction to improve my temporal awareness.
            Can you help me understand:
            1. What specific date/time information should I update?
            2. How should I apply this in future conversations?
            3. Is this a permanent change or contextual?

            This learning will help me provide more accurate temporal information.
            """
            suggestions = [
                "Provide specific date format you prefer",
                "Explain the context for this correction",
                "Confirm if this applies globally or to specific scenarios",
            ]
        elif learning_type == TemporalLearningType.TIME_CONTEXT:
            response = f"""
            I'm learning about temporal context from your question: "{message}"

            Current temporal framework:
            - System date: {self.system_date}
            - Timezone: {self.system_timezone}
            - Context awareness: Learning mode

            Your question helps me understand how to better contextualize time-related information.

            Would you like me to:
            - Adjust how I reference dates and times?
            - Learn specific temporal patterns you use?
            - Understand your preferred time context format?
            """
            suggestions = [
                "Share your preferred date/time format",
                "Explain what temporal context is most useful",
                "Provide examples of good temporal framing",
            ]
        else:
            response = f"""
            I'm processing your temporal reference: "{message}"

            Based on my current understanding ({self.system_date}), I'm learning how to better handle temporal information.

            This interaction teaches me about:
            - How you refer to dates and times
            - What temporal precision you need
            - How to maintain temporal consistency

            Is my temporal understanding aligned with your expectations?
            """
            suggestions = [
                "Confirm if my date understanding is correct",
                "Share any specific temporal preferences",
                "Let me know if you need different time formats",
            ]

        return {"response": response.strip(), "suggestions": suggestions}

    async def _generate_followup_questions(
        self, learning_type: TemporalLearningType
    ) -> list[str]:
        """Generate contextual follow-up questions for deeper learning"""

        questions_map = {
            TemporalLearningType.DATE_CORRECTION: [
                "What date format do you prefer for different contexts?",
                "Should I always use this correction or only in specific situations?",
                "How can I validate temporal information before presenting it?",
            ],
            TemporalLearningType.TIME_CONTEXT: [
                "What level of temporal precision is most useful for you?",
                "How should I indicate uncertainty about temporal information?",
                "What temporal context clues should I pay attention to?",
            ],
            TemporalLearningType.BUSINESS_TIMELINE: [
                "What are your key business temporal cycles?",
                "How far in advance do you typically plan?",
                "What temporal milestones are most important to track?",
            ],
        }

        return questions_map.get(
            learning_type,
            [
                "What temporal patterns should I learn from this interaction?",
                "How can I improve my temporal awareness?",
                "What temporal context would be most helpful?",
            ],
        )

    async def _apply_immediate_learning(self, interaction: TemporalLearningInteraction):
        """Apply learning immediately for high-confidence interactions"""

        try:
            # Extract temporal concepts and update knowledge base
            temporal_concepts = await self._extract_temporal_concepts(interaction)

            for concept in temporal_concepts:
                await self._update_temporal_knowledge(concept, interaction)

            # Update learning patterns
            await self._update_learning_patterns(interaction)

            # Mark interaction as applied
            interaction.applied = True

            logger.info(f"Applied immediate learning from interaction {interaction.id}")

        except Exception as e:
            logger.error(f"Error applying immediate learning: {e}")

    async def _extract_temporal_concepts(
        self, interaction: TemporalLearningInteraction
    ) -> list[dict[str, Any]]:
        """Extract temporal concepts from an interaction"""

        # Fallback concept extraction
        return [{"concept": "temporal_reference", "confidence": 0.5}]

    async def _update_temporal_knowledge(
        self, concept: dict[str, Any], interaction: TemporalLearningInteraction
    ):
        """Update the temporal knowledge base with new learning"""

        concept_key = concept.get("concept", "unknown")

        if concept_key in self.temporal_knowledge:
            # Update existing knowledge
            knowledge = self.temporal_knowledge[concept_key]
            knowledge.usage_count += 1
            knowledge.last_updated = date_manager.now()
            knowledge.source_interactions.append(interaction.id)

            # Update confidence based on reinforcement
            if knowledge.confidence != LearningConfidence.VERIFIED:
                if knowledge.usage_count >= 3:
                    knowledge.confidence = LearningConfidence.HIGH
                elif knowledge.usage_count >= 2:
                    knowledge.confidence = LearningConfidence.MEDIUM
        else:
            # Create new temporal knowledge
            self.temporal_knowledge[concept_key] = TemporalKnowledge(
                concept=concept_key,
                description=concept.get("description", ""),
                examples=[interaction.user_question],
                confidence=LearningConfidence.LOW,
                source_interactions=[interaction.id],
                last_updated=date_manager.now(),
                usage_count=1,
            )

    async def _update_learning_patterns(self, interaction: TemporalLearningInteraction):
        """Update learning patterns based on the interaction"""

        # Add temporal reference patterns
        self.temporal_patterns["temporal_references"].append(
            {
                "question": interaction.user_question,
                "learning_type": interaction.learning_type.value,
                "confidence": interaction.confidence.value,
                "timestamp": interaction.timestamp.isoformat(),
            }
        )

    async def process_user_correction(
        self,
        interaction_id: str,
        correction: str,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Process a user correction to improve learning"""

        try:
            # Find the original interaction
            interaction = next(
                (i for i in self.learning_interactions if i.id == interaction_id), None
            )

            if not interaction:
                return {"success": False, "error": "Interaction not found"}

            # Update interaction with correction
            interaction.user_correction = correction
            interaction.confidence = LearningConfidence.HIGH
            interaction.validated = True

            # Apply learning immediately for corrections
            await self._apply_immediate_learning(interaction)

            return {
                "success": True,
                "interaction_id": interaction_id,
                "learning_applied": True,
                "updated_knowledge": await self._get_updated_knowledge_summary(),
            }

        except Exception as e:
            logger.error(f"Error processing user correction: {e}")
            return {"success": False, "error": str(e)}

    async def get_learning_dashboard_data(self) -> dict[str, Any]:
        """Get comprehensive learning data for the dashboard"""

        total_interactions = len(self.learning_interactions)
        validated_interactions = len(
            [i for i in self.learning_interactions if i.validated]
        )
        applied_learnings = len([i for i in self.learning_interactions if i.applied])

        # Learning type distribution
        learning_type_counts = {}
        for interaction in self.learning_interactions:
            type_name = interaction.learning_type.value
            learning_type_counts[type_name] = learning_type_counts.get(type_name, 0) + 1

        # Confidence distribution
        confidence_counts = {}
        for interaction in self.learning_interactions:
            conf_name = interaction.confidence.value
            confidence_counts[conf_name] = confidence_counts.get(conf_name, 0) + 1

        # Recent learning activity
        recent_interactions = sorted(
            self.learning_interactions, key=lambda x: x.timestamp, reverse=True
        )[:10]

        return {
            "summary": {
                "total_interactions": total_interactions,
                "validated_interactions": validated_interactions,
                "applied_learnings": applied_learnings,
                "knowledge_concepts": len(self.temporal_knowledge),
                "learning_accuracy": validated_interactions
                / max(total_interactions, 1),
            },
            "distributions": {
                "learning_types": learning_type_counts,
                "confidence_levels": confidence_counts,
            },
            "recent_activity": [
                {
                    "id": i.id,
                    "question": (
                        i.user_question[:100] + "..."
                        if len(i.user_question) > 100
                        else i.user_question
                    ),
                    "learning_type": i.learning_type.value,
                    "confidence": i.confidence.value,
                    "timestamp": i.timestamp.isoformat(),
                    "validated": i.validated,
                    "applied": i.applied,
                }
                for i in recent_interactions
            ],
            "knowledge_base": {
                concept: {
                    "description": knowledge.description,
                    "confidence": knowledge.confidence.value,
                    "usage_count": knowledge.usage_count,
                    "last_updated": knowledge.last_updated.isoformat(),
                }
                for concept, knowledge in self.temporal_knowledge.items()
            },
            "learning_patterns": self.temporal_patterns,
            "system_status": {
                "current_date": self.system_date,
                "timezone": self.system_timezone,
                "learning_mode": "active",
            },
        }

    async def _get_updated_knowledge_summary(self) -> dict[str, Any]:
        """Get a summary of recently updated knowledge"""

        recent_knowledge = {
            concept: knowledge
            for concept, knowledge in self.temporal_knowledge.items()
            if (date_manager.now() - knowledge.last_updated).total_seconds()
            < 300  # Last 5 minutes
        }

        return {
            "updated_concepts": len(recent_knowledge),
            "concepts": list(recent_knowledge.keys()),
            "total_knowledge_base": len(self.temporal_knowledge),
        }

    async def get_learning_suggestions(self) -> list[dict[str, Any]]:
        """Generate suggestions for improving temporal learning"""

        suggestions = []

        # Analyze learning gaps
        learning_type_counts = {}
        for interaction in self.learning_interactions:
            type_name = interaction.learning_type.value
            learning_type_counts[type_name] = learning_type_counts.get(type_name, 0) + 1

        # Suggest underutilized learning types
        all_types = [lt.value for lt in TemporalLearningType]
        for learning_type in all_types:
            if learning_type_counts.get(learning_type, 0) < 2:
                suggestions.append(
                    {
                        "type": "learning_opportunity",
                        "suggestion": f"Consider exploring {learning_type.replace('_', ' ')} learning",
                        "description": f"Limited interactions in {learning_type} category",
                        "priority": "medium",
                    }
                )

        # Suggest validation for unvalidated interactions
        unvalidated_count = len(
            [i for i in self.learning_interactions if not i.validated]
        )
        if unvalidated_count > 5:
            suggestions.append(
                {
                    "type": "validation_needed",
                    "suggestion": "Review and validate recent learning interactions",
                    "description": f"{unvalidated_count} interactions need validation",
                    "priority": "high",
                }
            )

        return suggestions


# Global service instance
_temporal_qa_learning_service = None


def get_temporal_qa_learning_service() -> TemporalQALearningService:
    """Get the global temporal Q&A learning service instance"""
    global _temporal_qa_learning_service
    if _temporal_qa_learning_service is None:
        _temporal_qa_learning_service = TemporalQALearningService()
    return _temporal_qa_learning_service
