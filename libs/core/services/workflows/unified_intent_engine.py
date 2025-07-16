from __future__ import annotations

"""
Unified Intent Engine for Sophia AI
Provides centralized intent understanding with learning capabilities
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService
from infrastructure.mcp_servers.enhanced_ai_memory_mcp_server import (
    UnifiedMemoryService,
)
from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService
from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService

logger = logging.getLogger(__name__)


class IntentCategory(Enum):
    """Primary intent categories"""

    BUSINESS_INTELLIGENCE = "business_intelligence"
    DEVELOPMENT = "development"
    INFRASTRUCTURE = "infrastructure"
    SALES_COACHING = "sales_coaching"
    KNOWLEDGE_QUERY = "knowledge_query"
    WORKFLOW_CREATION = "workflow_creation"
    SYSTEM_MANAGEMENT = "system_management"
    CROSS_FUNCTIONAL = "cross_functional"


class AgentCapability(Enum):
    """Agent capabilities required for different tasks"""

    DATA_ANALYSIS = "data_analysis"
    CODE_GENERATION = "code_generation"
    INFRASTRUCTURE_MANAGEMENT = "infrastructure_management"
    SALES_ANALYSIS = "sales_analysis"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    WORKFLOW_DESIGN = "workflow_design"
    MEMORY_MANAGEMENT = "memory_management"
    WEB_RESEARCH = "web_research"


@dataclass
class IntentAnalysis:
    """Result of intent analysis"""

    primary_category: IntentCategory
    confidence: float
    required_capabilities: list[AgentCapability]
    suggested_workflow: str
    context_factors: dict[str, Any]
    entities: dict[str, list[str]]
    complexity_score: float
    cross_group_needed: bool


class UnifiedIntentEngine:
    """
    Central intent understanding with context awareness and learning
    """

    def __init__(self):
        self.cortex_service = SophiaUnifiedMemoryService()
        self.memory_service = SophiaUnifiedMemoryService()
        self.intent_patterns: dict[str, list[dict]] = {}
        self.capability_mapping: dict[IntentCategory, list[AgentCapability]] = {
            IntentCategory.BUSINESS_INTELLIGENCE: [
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.KNOWLEDGE_RETRIEVAL,
                AgentCapability.WEB_RESEARCH,
            ],
            IntentCategory.DEVELOPMENT: [
                AgentCapability.CODE_GENERATION,
                AgentCapability.MEMORY_MANAGEMENT,
                AgentCapability.INFRASTRUCTURE_MANAGEMENT,
            ],
            IntentCategory.SALES_COACHING: [
                AgentCapability.SALES_ANALYSIS,
                AgentCapability.DATA_ANALYSIS,
            ],
            IntentCategory.WORKFLOW_CREATION: [
                AgentCapability.WORKFLOW_DESIGN,
                AgentCapability.MEMORY_MANAGEMENT,
            ],
        }
        self._load_learned_patterns()

    def _load_learned_patterns(self):
        """Load previously learned intent patterns"""
        # In production, this would load from persistent storage
        self.intent_patterns = {
            "business_intelligence": [
                {"keywords": ["revenue", "sales", "kpi", "metrics"], "weight": 0.8},
                {"keywords": ["customer", "churn", "satisfaction"], "weight": 0.7},
            ],
            "development": [
                {"keywords": ["code", "implement", "debug", "fix"], "weight": 0.9},
                {"keywords": ["deploy", "build", "test"], "weight": 0.7},
            ],
            "sales_coaching": [
                {"keywords": ["deal", "call", "gong", "coaching"], "weight": 0.85},
                {"keywords": ["performance", "improvement"], "weight": 0.6},
            ],
        }

    async def analyze_intent(
        self, message: str, context: dict[str, Any]
    ) -> IntentAnalysis:
        """
        Analyze user intent with full context awareness
        """
        logger.info(f"Analyzing intent for message: {message[:100]}...")

        # 1. Recall relevant memories
        memories = await self._recall_relevant_memories(
            context.get("user_id", "unknown"), message
        )

        # 2. Extract entities
        entities = await self._extract_entities(message)

        # 3. Perform deep intent analysis
        analysis_prompt = f"""
        Analyze this request with full context:

        Current Message: {message}
        User Role: {context.get('user_role', 'unknown')}
        Recent Context: {json.dumps(context.get('recent_messages', [])[:3])}
        Historical Patterns: {json.dumps(memories[:3])}
        Detected Entities: {json.dumps(entities)}

        Determine:
        1. Primary intent category (business_intelligence, development, infrastructure, sales_coaching, knowledge_query, workflow_creation, system_management, cross_functional)
        2. Required capabilities (list specific capabilities needed)
        3. Optimal workflow type (single_agent, multi_agent_parallel, multi_agent_sequential, human_in_loop)
        4. Confidence level (0.0 to 1.0)
        5. Complexity score (0.0 to 1.0)
        6. Whether cross-group collaboration is needed (true/false)

        Return as JSON with these exact fields.
        """

        try:
            # Use QdrantUnifiedMemoryService for intent analysis
            QDRANT_service = QdrantSophiaUnifiedMemoryService()
            await QDRANT_service.initialize()
            
            # Use the enhanced router for LLM calls
            intent_result = await QDRANT_service.router_service.complete_chat(
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500
            )
            
            # Parse the analysis
            intent_data = json.loads(intent_result)

            # Map to our enums and create IntentAnalysis
            intent_analysis = IntentAnalysis(
                primary_category=IntentCategory(
                    intent_data.get("primary_intent_category", "knowledge_query")
                ),
                confidence=float(intent_data.get("confidence_level", 0.5)),
                required_capabilities=[
                    AgentCapability(cap)
                    for cap in intent_data.get("required_capabilities", [])
                    if cap in [e.value for e in AgentCapability]
                ],
                suggested_workflow=intent_data.get(
                    "optimal_workflow_type", "single_agent"
                ),
                context_factors={
                    "user_role": context.get("user_role"),
                    "session_id": context.get("session_id"),
                    "recent_topics": self._extract_recent_topics(context),
                },
                entities=entities,
                complexity_score=float(intent_data.get("complexity_score", 0.5)),
                cross_group_needed=intent_data.get("cross_group_needed", False),
            )

        except Exception as e:
            logger.exception(f"Error in intent analysis: {e}")
            # Fallback to pattern matching
            intent_analysis = await self._fallback_intent_analysis(message, entities)

        # 4. Learn from this interaction
        await self._update_intent_patterns(message, intent_analysis)

        return intent_analysis

    async def _recall_relevant_memories(self, user_id: str, query: str) -> list[dict]:
        """Recall relevant memories for context"""
        try:
            # EnhancedAiMemoryMCPServer doesn't have a direct recall_memories method
            # We'll need to use the specific recall methods based on context
            memories = []

            # Recall business intelligence memories
            bi_memories = await self.memory_service.recall_gong_call_insights(
                query=query, limit=2
            )
            memories.extend(bi_memories)

            # Recall foundational knowledge
            foundational = await self.memory_service.recall_foundational_knowledge(
                query=query, limit=2
            )
            memories.extend(foundational)

            # Recall KB articles
            kb_articles = await self.memory_service.recall_kb_articles(
                query=query, limit=1
            )
            memories.extend(kb_articles)

            return memories[:5]  # Limit to 5 total
        except Exception as e:
            logger.exception(f"Error recalling memories: {e}")
            return []

    async def _extract_entities(self, message: str) -> dict[str, list[str]]:
        """Extract entities from the message"""
        entities = {
            "companies": [],
            "people": [],
            "dates": [],
            "metrics": [],
            "technologies": [],
        }

        # Simple pattern matching for demo
        # In production, use Lambda GPU or spaCy
        import re

        # Company names (simple capitalized words for demo)
        companies = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", message)
        entities["companies"] = [c for c in companies if len(c) > 3]

        # Metrics (numbers with context)
        metrics = re.findall(r"\b\d+(?:\.\d+)?%?\b", message)
        entities["metrics"] = metrics

        # Technologies (from known list)
        tech_keywords = [
            "python",
            "react",
            "docker",
            "kubernetes",
            "qdrant",
            "langchain",
        ]
        message_lower = message.lower()
        entities["technologies"] = [
            tech for tech in tech_keywords if tech in message_lower
        ]

        return entities

    def _extract_recent_topics(self, context: dict) -> list[str]:
        """Extract topics from recent messages"""
        recent_messages = context.get("recent_messages", [])
        topics = []

        for msg in recent_messages[-5:]:
            # Simple keyword extraction
            words = msg.lower().split()
            important_words = [w for w in words if len(w) > 4]
            topics.extend(important_words[:3])

        return list(set(topics))

    async def _fallback_intent_analysis(
        self, message: str, entities: dict
    ) -> IntentAnalysis:
        """Fallback intent analysis using pattern matching"""
        message_lower = message.lower()

        # Score each category
        scores = {}
        for category, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                keywords = pattern["keywords"]
                weight = pattern["weight"]
                matches = sum(1 for kw in keywords if kw in message_lower)
                score += (matches / len(keywords)) * weight
            scores[category] = score

        # Get highest scoring category
        best_category = max(scores.items(), key=lambda x: x[1])
        category_enum = IntentCategory(best_category[0])

        # Determine complexity
        complexity = min(1.0, len(message.split()) / 50.0)

        return IntentAnalysis(
            primary_category=category_enum,
            confidence=min(0.9, best_category[1]),
            required_capabilities=self.capability_mapping.get(category_enum, []),
            suggested_workflow=(
                "multi_agent_parallel" if complexity > 0.5 else "single_agent"
            ),
            context_factors={},
            entities=entities,
            complexity_score=complexity,
            cross_group_needed=complexity > 0.7,
        )

    async def _update_intent_patterns(self, message: str, intent: IntentAnalysis):
        """Update learned patterns based on interaction"""
        # In production, this would update persistent storage
        # and potentially retrain models
        category_key = intent.primary_category.value

        if category_key not in self.intent_patterns:
            self.intent_patterns[category_key] = []

        # Extract keywords from successful classification
        words = message.lower().split()
        important_words = [w for w in words if len(w) > 3][:5]

        # Update patterns with decay
        self.intent_patterns[category_key].append(
            {
                "keywords": important_words,
                "weight": intent.confidence * 0.5,  # Decay factor
            }
        )

        # Keep only recent patterns
        if len(self.intent_patterns[category_key]) > 10:
            self.intent_patterns[category_key] = self.intent_patterns[category_key][
                -10:
            ]

        logger.info(f"Updated intent patterns for {category_key}")

    async def get_intent_statistics(self) -> dict[str, Any]:
        """Get statistics about intent patterns"""
        stats = {
            "total_patterns": sum(
                len(patterns) for patterns in self.intent_patterns.values()
            ),
            "categories": list(self.intent_patterns.keys()),
            "average_confidence": 0.0,
            "pattern_distribution": {},
        }

        total_weight = 0
        total_patterns = 0

        for category, patterns in self.intent_patterns.items():
            pattern_count = len(patterns)
            avg_weight = (
                sum(p["weight"] for p in patterns) / pattern_count
                if pattern_count > 0
                else 0
            )

            stats["pattern_distribution"][category] = {
                "count": pattern_count,
                "average_weight": avg_weight,
            }

            total_weight += sum(p["weight"] for p in patterns)
            total_patterns += pattern_count

        stats["average_confidence"] = (
            total_weight / total_patterns if total_patterns > 0 else 0
        )

        return stats
