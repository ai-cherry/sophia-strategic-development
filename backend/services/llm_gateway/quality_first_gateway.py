#!/usr/bin/env python3
"""
Quality-First LLM Gateway Orchestrator
Prioritizes response quality over cost with dashboard-based monitoring
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from backend.core.config_manager import ConfigManager
from backend.services.llm_gateway.openrouter_integration import OpenRouterIntegration
from backend.services.llm_gateway.portkey_integration import PortkeyIntegration
from backend.services.llm_gateway.snowflake_cortex_enhanced import (
    SnowflakeCortexEnhanced,
)
from backend.utils.custom_logger import setup_logger

logger = setup_logger("quality_first_gateway")


@dataclass
class LLMRequest:
    """Request structure for LLM gateway"""

    query: str
    context: Optional[str] = None
    user_role: str = "user"
    business_criticality: str = "normal"
    accuracy_requirements: float = 0.85
    consistency_requirements: float = 0.80
    minimum_quality_threshold: float = 0.75
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class QualityOptimizedResponse:
    """Response with quality metrics"""

    response: str
    quality_score: float
    gateway_used: str
    cost_data: dict[str, float]  # Available but not displayed in chat
    performance_metrics: dict[str, Any]
    business_context_preserved: bool
    metadata: dict[str, Any] = None


@dataclass
class GatewaySelection:
    """Gateway selection result"""

    primary: str
    secondary: str
    quality_settings: dict[str, Any]
    fallback_settings: dict[str, Any]


class QualityFirstLLMGateway:
    """
    Quality and performance-focused LLM gateway with dashboard-based cost controls
    """

    def __init__(self):
        self.config = ConfigManager()

        # Initialize gateway integrations
        self.portkey = PortkeyIntegration()
        self.openrouter = OpenRouterIntegration()
        self.snowflake_cortex = SnowflakeCortexEnhanced()

        # Quality-first routing criteria (cost is secondary)
        self.quality_routing_criteria = {
            "response_accuracy": {"weight": 40, "threshold": 0.85},
            "business_context_preservation": {"weight": 30, "threshold": 0.90},
            "response_consistency": {"weight": 20, "threshold": 0.80},
            "performance_speed": {"weight": 10, "threshold": 3.0},  # seconds
            "cost_efficiency": {"weight": 0, "tracked_separately": True},
        }

        # Gateway capabilities
        self.gateway_capabilities = {
            "portkey": {
                "strengths": ["consistency", "reliability", "caching", "fallback"],
                "best_for": ["general_queries", "multi_turn_conversations"],
                "quality_boost": 0.25,  # 25% quality improvement
            },
            "openrouter": {
                "strengths": ["model_variety", "specialized_tasks", "latest_models"],
                "best_for": ["complex_reasoning", "creative_tasks", "domain_specific"],
                "quality_boost": 0.30,  # 30% for specialized tasks
            },
            "snowflake_cortex": {
                "strengths": ["data_locality", "business_context", "cost_efficiency"],
                "best_for": ["data_queries", "analytics", "business_intelligence"],
                "quality_boost": 0.40,  # 40% for data-related tasks
            },
        }

        # Performance tracking
        self.performance_history = []
        self.quality_history = []

        logger.info("Quality-First LLM Gateway initialized")

    async def process_request(self, request: LLMRequest) -> QualityOptimizedResponse:
        """
        Main entry point for processing LLM requests with quality optimization
        """
        start_time = time.time()

        try:
            # Analyze quality requirements
            quality_analysis = await self._analyze_quality_requirements(request)

            # Select optimal gateway
            gateway_selection = await self._select_quality_optimal_gateway(
                request, quality_analysis
            )

            # Execute with quality monitoring
            response = await self._execute_with_quality_monitoring(
                gateway_selection.primary, request, gateway_selection.quality_settings
            )

            # Validate response quality
            quality_score = await self._validate_response_quality(response, request)

            # Handle quality-based fallback if needed
            if quality_score < request.minimum_quality_threshold:
                logger.warning(
                    f"Quality threshold not met ({quality_score:.2f}), using fallback"
                )
                response = await self._execute_quality_fallback(
                    gateway_selection.secondary,
                    request,
                    response,
                    gateway_selection.fallback_settings,
                )
                quality_score = await self._validate_response_quality(response, request)

            # Calculate performance metrics
            execution_time = time.time() - start_time
            performance_metrics = {
                "execution_time_seconds": execution_time,
                "quality_score": quality_score,
                "tokens_used": len(response.split()),
                "gateway_used": gateway_selection.primary,
            }

            # Log to dashboard (not shown in chat)
            await self._log_to_dashboard(
                request, response, quality_score, performance_metrics
            )

            return QualityOptimizedResponse(
                response=response,
                quality_score=quality_score,
                gateway_used=gateway_selection.primary,
                cost_data=await self._calculate_cost_data(
                    response, gateway_selection.primary
                ),
                performance_metrics=performance_metrics,
                business_context_preserved=True,
                metadata={
                    "quality_analysis": quality_analysis,
                    "gateway_capabilities": self.gateway_capabilities[
                        gateway_selection.primary
                    ],
                },
            )

        except Exception as e:
            logger.error(f"Error in quality-first gateway: {e}")
            return await self._emergency_quality_fallback(request, str(e))

    async def _analyze_quality_requirements(
        self, request: LLMRequest
    ) -> dict[str, Any]:
        """Analyze quality requirements for the request"""
        analysis = {
            "query_complexity": self._assess_query_complexity(request.query),
            "context_importance": self._assess_context_importance(request.context),
            "business_criticality": request.business_criticality,
            "domain_specificity": self._detect_domain_specificity(request.query),
            "required_capabilities": self._determine_required_capabilities(request),
        }

        # Determine quality priority
        if request.business_criticality == "critical" or request.user_role == "CEO":
            analysis["quality_priority"] = "maximum"
        elif request.accuracy_requirements > 0.9:
            analysis["quality_priority"] = "high"
        else:
            analysis["quality_priority"] = "standard"

        return analysis

    async def _select_quality_optimal_gateway(
        self, request: LLMRequest, quality_analysis: dict[str, Any]
    ) -> GatewaySelection:
        """Select optimal gateway based on quality requirements"""

        # Score each gateway for the request
        gateway_scores = {}

        for gateway, capabilities in self.gateway_capabilities.items():
            score = 0

            # Match capabilities to requirements
            for capability in quality_analysis["required_capabilities"]:
                if capability in capabilities["strengths"]:
                    score += 0.25

            # Check if request type matches gateway strengths
            request_type = self._categorize_request(request.query)
            if request_type in capabilities["best_for"]:
                score += 0.5

            # Apply quality boost
            score *= 1 + capabilities["quality_boost"]

            # Special handling for data queries
            if "data" in request.query.lower() or "analytics" in request.query.lower():
                if gateway == "snowflake_cortex":
                    score *= 1.5  # Prefer Cortex for data queries

            gateway_scores[gateway] = score

        # Sort by score
        sorted_gateways = sorted(
            gateway_scores.items(), key=lambda x: x[1], reverse=True
        )
        primary = sorted_gateways[0][0]
        secondary = sorted_gateways[1][0] if len(sorted_gateways) > 1 else primary

        # Determine quality settings
        quality_settings = self._determine_quality_settings(primary, quality_analysis)

        fallback_settings = self._determine_quality_settings(
            secondary, quality_analysis
        )

        logger.info(f"Selected primary gateway: {primary}, secondary: {secondary}")

        return GatewaySelection(
            primary=primary,
            secondary=secondary,
            quality_settings=quality_settings,
            fallback_settings=fallback_settings,
        )

    async def _execute_with_quality_monitoring(
        self, gateway: str, request: LLMRequest, quality_settings: dict[str, Any]
    ) -> str:
        """Execute request with quality monitoring"""

        # Route to appropriate gateway
        if gateway == "portkey":
            response = await self.portkey.execute(
                query=request.query, context=request.context, settings=quality_settings
            )
        elif gateway == "openrouter":
            response = await self.openrouter.execute(
                query=request.query, context=request.context, settings=quality_settings
            )
        elif gateway == "snowflake_cortex":
            response = await self.snowflake_cortex.execute(
                query=request.query, context=request.context, settings=quality_settings
            )
        else:
            raise ValueError(f"Unknown gateway: {gateway}")

        return response

    async def _validate_response_quality(
        self, response: str, request: LLMRequest
    ) -> float:
        """Validate response quality against criteria"""
        quality_scores = {}

        # Check response accuracy (would use more sophisticated methods)
        if response and len(response) > 10:
            quality_scores["accuracy"] = 0.9  # Placeholder
        else:
            quality_scores["accuracy"] = 0.1

        # Check business context preservation
        if request.context and any(
            term in response for term in request.context.split()[:5]
        ):
            quality_scores["context_preservation"] = 0.95
        else:
            quality_scores["context_preservation"] = 0.7

        # Check response consistency
        quality_scores["consistency"] = 0.85  # Placeholder

        # Check performance
        quality_scores["performance"] = 0.9  # Placeholder

        # Calculate weighted score
        total_score = 0
        total_weight = 0

        for criterion, settings in self.quality_routing_criteria.items():
            if criterion in [
                "response_accuracy",
                "business_context_preservation",
                "response_consistency",
                "performance_speed",
            ]:
                weight = settings["weight"]
                score_key = criterion.replace("response_", "").replace("_speed", "")
                score = quality_scores.get(score_key, 0.5)

                total_score += score * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.5

    async def _execute_quality_fallback(
        self,
        gateway: str,
        request: LLMRequest,
        original_response: str,
        fallback_settings: dict[str, Any],
    ) -> str:
        """Execute quality-based fallback"""
        # Enhance request with original response context
        enhanced_request = LLMRequest(
            query=f"Please provide a high-quality response to: {request.query}",
            context=f"{request.context}\n\nPrevious response to improve upon: {original_response}",
            user_role=request.user_role,
            business_criticality="high",  # Elevate criticality for fallback
            accuracy_requirements=0.95,
            consistency_requirements=0.90,
            minimum_quality_threshold=0.85,
        )

        return await self._execute_with_quality_monitoring(
            gateway, enhanced_request, fallback_settings
        )

    async def _emergency_quality_fallback(
        self, request: LLMRequest, error: str
    ) -> QualityOptimizedResponse:
        """Emergency fallback with quality preservation"""
        fallback_response = (
            f"I apologize, but I'm currently experiencing technical difficulties. "
            f"Let me provide you with the best information I can regarding: {request.query[:100]}..."
        )

        return QualityOptimizedResponse(
            response=fallback_response,
            quality_score=0.5,
            gateway_used="emergency_fallback",
            cost_data={"total": 0.0},
            performance_metrics={"error": error},
            business_context_preserved=False,
        )

    async def _log_to_dashboard(
        self,
        request: LLMRequest,
        response: str,
        quality_score: float,
        performance_metrics: dict[str, Any],
    ):
        """Log metrics to dashboard (not shown in chat)"""
        dashboard_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": {
                "query": request.query[:100],
                "user_role": request.user_role,
                "business_criticality": request.business_criticality,
            },
            "response": {"length": len(response), "quality_score": quality_score},
            "performance": performance_metrics,
            "cost": await self._calculate_cost_data(
                response, performance_metrics.get("gateway_used", "unknown")
            ),
        }

        # Would send to monitoring service
        self.performance_history.append(dashboard_entry)
        self.quality_history.append(quality_score)

        # Keep only last 1000 entries
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
        if len(self.quality_history) > 1000:
            self.quality_history = self.quality_history[-1000:]

    async def _calculate_cost_data(
        self, response: str, gateway: str
    ) -> dict[str, float]:
        """Calculate cost data for dashboard tracking"""
        # Approximate token count
        tokens = len(response.split()) * 1.3

        # Gateway-specific pricing (examples)
        pricing = {
            "portkey": 0.002,  # per 1k tokens
            "openrouter": 0.001,
            "snowflake_cortex": 0.0005,
        }

        rate = pricing.get(gateway, 0.001)
        cost = (tokens / 1000) * rate

        return {"tokens": tokens, "rate_per_1k": rate, "total": cost}

    def _assess_query_complexity(self, query: str) -> str:
        """Assess query complexity"""
        word_count = len(query.split())

        if word_count < 10:
            return "simple"
        elif word_count < 50:
            return "moderate"
        else:
            return "complex"

    def _assess_context_importance(self, context: Optional[str]) -> str:
        """Assess importance of context"""
        if not context:
            return "none"
        elif len(context) < 100:
            return "low"
        elif len(context) < 1000:
            return "medium"
        else:
            return "high"

    def _detect_domain_specificity(self, query: str) -> list[str]:
        """Detect domain-specific requirements"""
        domains = []

        # Apartment industry keywords
        apartment_keywords = [
            "apartment",
            "rent",
            "property",
            "tenant",
            "lease",
            "payment",
        ]
        if any(keyword in query.lower() for keyword in apartment_keywords):
            domains.append("apartment_industry")

        # Data/analytics keywords
        data_keywords = ["data", "analytics", "report", "metrics", "kpi", "dashboard"]
        if any(keyword in query.lower() for keyword in data_keywords):
            domains.append("data_analytics")

        # Business keywords
        business_keywords = ["revenue", "customer", "sales", "marketing", "strategy"]
        if any(keyword in query.lower() for keyword in business_keywords):
            domains.append("business_intelligence")

        return domains

    def _determine_required_capabilities(self, request: LLMRequest) -> list[str]:
        """Determine required capabilities for the request"""
        capabilities = []

        # Based on query analysis
        if "analyze" in request.query.lower() or "explain" in request.query.lower():
            capabilities.append("reasoning")

        if "create" in request.query.lower() or "generate" in request.query.lower():
            capabilities.append("creative")

        if any(word in request.query.lower() for word in ["data", "report", "metrics"]):
            capabilities.append("data_analysis")

        # Based on requirements
        if request.accuracy_requirements > 0.9:
            capabilities.append("high_accuracy")

        if request.consistency_requirements > 0.85:
            capabilities.append("consistency")

        return capabilities

    def _categorize_request(self, query: str) -> str:
        """Categorize request type"""
        query_lower = query.lower()

        if any(
            word in query_lower for word in ["analyze", "report", "data", "metrics"]
        ):
            return "data_queries"
        elif any(word in query_lower for word in ["create", "write", "generate"]):
            return "creative_tasks"
        elif any(word in query_lower for word in ["explain", "why", "how", "reason"]):
            return "complex_reasoning"
        else:
            return "general_queries"

    def _determine_quality_settings(
        self, gateway: str, quality_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Determine quality settings for gateway"""
        settings = {
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }

        # Adjust based on quality priority
        if quality_analysis["quality_priority"] == "maximum":
            settings["temperature"] = 0.3  # Lower for consistency
            settings["top_p"] = 0.95  # Higher quality sampling

        # Gateway-specific adjustments
        if gateway == "snowflake_cortex":
            settings["use_cortex_complete"] = True
            settings["enable_caching"] = True
        elif gateway == "portkey":
            settings["enable_semantic_caching"] = True
            settings["cache_similarity_threshold"] = 0.88
        elif gateway == "openrouter":
            settings["model_selection"] = "quality_optimized"

        return settings
