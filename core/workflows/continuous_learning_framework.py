"""
Continuous Learning Framework for Sophia AI
Enables learning and improvement from every interaction
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from core.workflows.unified_intent_engine import IntentAnalysis, IntentCategory
from infrastructure.mcp_servers.enhanced_ai_memory_mcp_server import (
    EnhancedAiMemoryMCPServer,
)

logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    """Types of user feedback"""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"

@dataclass
class Feedback:
    """User feedback on an interaction"""

    type: FeedbackType
    content: str
    rating: float | None = None
    timestamp: datetime | None = None

@dataclass
class WorkflowResult:
    """Result of a workflow execution"""

    workflow_id: str
    success: bool
    duration: float
    output: Any
    errors: list[str] | None = None
    metrics: dict[str, float] | None = None

class PatternLearner:
    """Learns patterns from interactions"""

    def __init__(self):
        self.intent_patterns: dict[IntentCategory, list[dict]] = {}
        self.success_patterns: dict[str, dict[str, float]] = {}
        self.failure_patterns: dict[str, list[dict]] = {}

    async def update_patterns(
        self,
        intent_type: IntentCategory,
        success: bool,
        execution_time: float,
        workflow_details: dict | None = None,
    ):
        """Update learned patterns based on interaction outcome"""
        pattern_key = intent_type.value

        if pattern_key not in self.success_patterns:
            self.success_patterns[pattern_key] = {
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "total_interactions": 0,
            }

        stats = self.success_patterns[pattern_key]
        total = stats["total_interactions"]

        # Update running averages
        stats["success_rate"] = (
            stats["success_rate"] * total + (1.0 if success else 0.0)
        ) / (total + 1)
        stats["avg_execution_time"] = (
            stats["avg_execution_time"] * total + execution_time
        ) / (total + 1)
        stats["total_interactions"] = total + 1

        # Track failure patterns
        if not success and workflow_details:
            if pattern_key not in self.failure_patterns:
                self.failure_patterns[pattern_key] = []
            self.failure_patterns[pattern_key].append(
                {
                    "timestamp": datetime.now(),
                    "details": workflow_details,
                    "execution_time": execution_time,
                }
            )

        logger.info(
            f"Updated patterns for {pattern_key}: success_rate={stats['success_rate']:.2f}"
        )

    def get_performance_insights(self, intent_type: IntentCategory) -> dict[str, Any]:
        """Get performance insights for a specific intent type"""
        pattern_key = intent_type.value

        if pattern_key not in self.success_patterns:
            return {"status": "no_data"}

        stats = self.success_patterns[pattern_key]
        failures = self.failure_patterns.get(pattern_key, [])

        return {
            "success_rate": stats["success_rate"],
            "avg_execution_time": stats["avg_execution_time"],
            "total_interactions": stats["total_interactions"],
            "recent_failures": failures[-5:] if failures else [],
            "improvement_suggestions": self._generate_improvement_suggestions(
                stats, failures
            ),
        }

    def _generate_improvement_suggestions(
        self, stats: dict, failures: list
    ) -> list[str]:
        """Generate suggestions for improvement based on patterns"""
        suggestions = []

        if stats["success_rate"] < 0.7:
            suggestions.append(
                "Consider refining intent classification for this category"
            )

        if stats["avg_execution_time"] > 5.0:
            suggestions.append("Optimize workflow execution for better performance")

        if len(failures) > 5:
            # Analyze common failure reasons
            suggestions.append("Review recent failures for common patterns")

        return suggestions

class PerformanceAnalyzer:
    """Analyzes performance trends and identifies areas for improvement"""

    def __init__(self):
        self.performance_history: list[dict[str, Any]] = []
        self.trend_window = 100  # Number of interactions to consider for trends

    async def record_performance(
        self,
        intent: IntentAnalysis,
        workflow_result: WorkflowResult,
        user_feedback: Feedback | None = None,
    ):
        """Record performance metrics"""
        self.performance_history.append(
            {
                "timestamp": datetime.now(),
                "intent_category": intent.primary_category.value,
                "intent_confidence": intent.confidence,
                "workflow_success": workflow_result.success,
                "execution_time": workflow_result.duration,
                "user_feedback": user_feedback.type.value if user_feedback else None,
                "complexity_score": intent.complexity_score,
                "cross_group_used": intent.cross_group_needed,
            }
        )

        # Keep only recent history
        if len(self.performance_history) > self.trend_window * 2:
            self.performance_history = self.performance_history[-self.trend_window :]

    async def analyze_trends(self) -> dict[str, Any]:
        """Analyze performance trends"""
        if len(self.performance_history) < 10:
            return {"status": "insufficient_data"}

        recent = self.performance_history[-self.trend_window :]

        # Calculate metrics
        success_rate = sum(1 for p in recent if p["workflow_success"]) / len(recent)
        avg_execution_time = sum(p["execution_time"] for p in recent) / len(recent)
        avg_confidence = sum(p["intent_confidence"] for p in recent) / len(recent)

        # Feedback analysis
        feedback_counts = {}
        for p in recent:
            if p["user_feedback"]:
                feedback_counts[p["user_feedback"]] = (
                    feedback_counts.get(p["user_feedback"], 0) + 1
                )

        # Complexity analysis
        complex_queries = [p for p in recent if p["complexity_score"] > 0.7]
        complex_success_rate = (
            sum(1 for p in complex_queries if p["workflow_success"])
            / len(complex_queries)
            if complex_queries
            else 0
        )

        trends = {
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time,
            "avg_intent_confidence": avg_confidence,
            "feedback_distribution": feedback_counts,
            "complex_query_success_rate": complex_success_rate,
            "cross_group_usage": sum(1 for p in recent if p["cross_group_used"])
            / len(recent),
            "improvement_needed": self._check_improvement_needed(
                success_rate, avg_execution_time, feedback_counts
            ),
        }

        return trends

    def _check_improvement_needed(
        self, success_rate: float, avg_execution_time: float, feedback_counts: dict
    ) -> bool:
        """Check if improvement is needed based on trends"""
        negative_feedback = feedback_counts.get("negative", 0)
        total_feedback = sum(feedback_counts.values())

        return (
            success_rate < 0.8
            or avg_execution_time > 3.0
            or (total_feedback > 0 and negative_feedback / total_feedback > 0.2)
        )

    async def indicates_improvement_needed(self) -> bool:
        """Quick check if improvement is needed"""
        trends = await self.analyze_trends()
        return trends.get("improvement_needed", False)

class ContinuousLearningFramework:
    """
    Main framework for continuous learning and improvement
    """

    def __init__(self):
        from infrastructure.services.mem0_integration_service import get_mem0_service

        self.mem0_service = get_mem0_service()
        self.memory_service = EnhancedAiMemoryMCPServer()
        self.pattern_learner = PatternLearner()
        self.performance_analyzer = PerformanceAnalyzer()
        self.strategy_adjustments: list[dict[str, Any]] = []

    async def _ensure_mem0_initialized(self):
        """Ensure Mem0 service is initialized (now handled in __init__)"""
        pass

    async def learn_from_interaction(
        self,
        request: str,
        intent: IntentAnalysis,
        workflow_execution: WorkflowResult,
        user_feedback: Feedback | None = None,
    ):
        """Learn from a complete interaction"""
        # self._ensure_mem0_initialized() is no longer needed

        # 1. Store interaction in Mem0
        memory_id = await self._store_interaction_memory(
            request, intent, workflow_execution, user_feedback
        )

        # 2. Update learned patterns
        await self.pattern_learner.update_patterns(
            intent_type=intent.primary_category,
            success=workflow_execution.success,
            execution_time=workflow_execution.duration,
            workflow_details={
                "workflow_id": workflow_execution.workflow_id,
                "errors": workflow_execution.errors,
            },
        )

        # 3. Record performance
        await self.performance_analyzer.record_performance(
            intent, workflow_execution, user_feedback
        )

        # 4. Analyze and adjust if needed
        trends = await self.performance_analyzer.analyze_trends()
        if trends.get("improvement_needed", False):
            await self._adjust_strategies(trends)

        logger.info(
            f"Learned from interaction: memory_id={memory_id}, success={workflow_execution.success}"
        )

    async def _store_interaction_memory(
        self,
        request: str,
        intent: IntentAnalysis,
        workflow_execution: WorkflowResult,
        user_feedback: Feedback | None,
    ) -> str:
        """Store interaction details in Mem0"""
        interaction_data = {
            "request": request,
            "intent": {
                "category": intent.primary_category.value,
                "confidence": intent.confidence,
                "complexity": intent.complexity_score,
                "capabilities_needed": [
                    cap.value for cap in intent.required_capabilities
                ],
            },
            "workflow": {
                "id": workflow_execution.workflow_id,
                "success": workflow_execution.success,
                "duration": workflow_execution.duration,
                "output_summary": str(workflow_execution.output)[:500],
            },
            "feedback": (
                {
                    "type": user_feedback.type.value,
                    "content": user_feedback.content,
                    "rating": user_feedback.rating,
                }
                if user_feedback
                else None
            ),
            "timestamp": datetime.now().isoformat(),
        }

        # Store in Mem0 as conversation
        conversation = [
            {"role": "user", "content": request},
            {"role": "assistant", "content": json.dumps(interaction_data)},
        ]
        memory_id = await self.mem0_service.store_conversation_memory(
            user_id="system", conversation=conversation, metadata=interaction_data
        )

        # Also store key insights in AI Memory for quick recall
        if workflow_execution.success and intent.confidence > 0.8:
            await self.memory_service.store_kb_article_memory(
                article_id=memory_id,
                title=f"Successful Pattern: {intent.primary_category.value}",
                content=json.dumps(interaction_data, indent=2),
                category="learning_patterns",
                author="continuous_learning",
                keywords=[intent.primary_category.value, "success_pattern"],
                importance_score=intent.confidence,
            )

        return memory_id

    async def _adjust_strategies(self, trends: dict[str, Any]):
        """Adjust orchestration strategies based on trends"""
        adjustments = []

        # Low success rate - adjust intent classification thresholds
        if trends["success_rate"] < 0.7:
            adjustments.append(
                {
                    "type": "intent_threshold",
                    "action": "increase_confidence_requirement",
                    "reason": "low_success_rate",
                    "value": 0.8,
                }
            )

        # Slow execution - optimize workflow routing
        if trends["avg_execution_time"] > 4.0:
            adjustments.append(
                {
                    "type": "workflow_optimization",
                    "action": "prefer_parallel_execution",
                    "reason": "slow_execution",
                    "value": True,
                }
            )

        # Low confidence - enhance intent analysis
        if trends["avg_intent_confidence"] < 0.6:
            adjustments.append(
                {
                    "type": "intent_enhancement",
                    "action": "use_deeper_context",
                    "reason": "low_confidence",
                    "value": True,
                }
            )

        self.strategy_adjustments.extend(adjustments)

        # Apply adjustments (in production, this would update the orchestrator config)
        for adjustment in adjustments:
            logger.info(f"Strategy adjustment: {adjustment}")

    async def get_learning_insights(self) -> dict[str, Any]:
        """Get insights from the learning system"""
        # self._ensure_mem0_initialized() is no longer needed

        # Get performance trends
        trends = await self.performance_analyzer.analyze_trends()

        # Get pattern insights for each intent category
        pattern_insights = {}
        for category in IntentCategory:
            pattern_insights[
                category.value
            ] = self.pattern_learner.get_performance_insights(category)

        # Get recent successful patterns from memory
        recent_successes = await self.memory_service.recall_kb_articles(
            query="success_pattern", category="learning_patterns", limit=5
        )

        return {
            "performance_trends": trends,
            "pattern_insights": pattern_insights,
            "recent_successes": recent_successes,
            "active_adjustments": self.strategy_adjustments[-10:],
            "total_interactions": len(self.performance_analyzer.performance_history),
            "learning_status": "active",
        }

    async def get_recommendations(self, intent_category: IntentCategory) -> list[str]:
        """Get recommendations for a specific intent category"""
        insights = self.pattern_learner.get_performance_insights(intent_category)
        recommendations = insights.get("improvement_suggestions", [])

        # Add recommendations based on recent trends
        trends = await self.performance_analyzer.analyze_trends()
        if trends.get("status") != "insufficient_data":
            if trends["success_rate"] < 0.8:
                recommendations.append(
                    f"Focus on improving {intent_category.value} workflows"
                )

            if (
                trends["cross_group_usage"] < 0.3
                and intent_category == IntentCategory.CROSS_FUNCTIONAL
            ):
                recommendations.append(
                    "Increase cross-group collaboration for complex queries"
                )

        return recommendations
