"""
Intelligent Query Router for Sophia AI
Uses Lambda GPU for AI-driven intent analysis and optimal routing
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query type classification for routing decisions"""

    OPERATIONAL = "operational"  # Real-time operations -> MCP
    ANALYTICAL = "analytical"  # Analytics/insights -> Cortex
    HYBRID = "hybrid"  # Requires both systems
    SYSTEM = "system"  # System status/health


class UrgencyLevel(Enum):
    """Query urgency for prioritization"""

    CRITICAL = "critical"  # Sub-second response needed
    HIGH = "high"  # <3 seconds
    MEDIUM = "medium"  # <10 seconds
    LOW = "low"  # <30 seconds


@dataclass
class QueryAnalysis:
    """Analysis result for query routing"""

    query_type: QueryType
    urgency: UrgencyLevel
    confidence: float
    target_systems: list[str]
    processing_strategy: str
    estimated_response_time: float
    context_requirements: list[str]
    business_domain: str
    recommended_model: str


class IntelligentQueryRouter:
    """AI-powered query router using Lambda GPU for intent analysis"""

    def __init__(self):
        self.cortex_service = EnhancedSophiaUnifiedMemoryService()

        # Business domain mappings
        self.domain_keywords = {
            "customer_management": [
                "customer",
                "client",
                "account",
                "churn",
                "expansion",
                "relationship",
                "deal",
            ],
            "project_management": [
                "project",
                "task",
                "sprint",
                "milestone",
                "asana",
                "linear",
                "notion",
                "slack",
            ],
            "financial_analysis": [
                "revenue",
                "profit",
                "cost",
                "budget",
                "financial",
                "money",
                "pricing",
            ],
            "operational_metrics": [
                "performance",
                "efficiency",
                "utilization",
                "capacity",
                "resource",
            ],
            "strategic_planning": [
                "strategy",
                "goal",
                "objective",
                "okr",
                "roadmap",
                "vision",
                "growth",
            ],
            "infrastructure": [
                "system",
                "server",
                "database",
                "deployment",
                "infrastructure",
                "pulumi",
            ],
            "development": [
                "code",
                "github",
                "pull request",
                "deployment",
                "bug",
                "feature",
            ],
            "intelligence": [
                "insights",
                "analytics",
                "trends",
                "prediction",
                "forecast",
                "analysis",
            ],
        }

        # System capability mappings
        self.system_capabilities = {
            "mcp_servers": {
                "response_time": 0.5,  # seconds
                "strengths": [
                    "real-time",
                    "operational",
                    "immediate_actions",
                    "live_updates",
                ],
                "use_cases": [
                    "task_creation",
                    "status_updates",
                    "notifications",
                    "real_time_monitoring",
                ],
            },
            "QDRANT_cortex": {
                "response_time": 3.0,  # seconds
                "strengths": [
                    "analytics",
                    "historical_analysis",
                    "predictions",
                    "complex_queries",
                ],
                "use_cases": [
                    "trend_analysis",
                    "forecasting",
                    "semantic_search",
                    "data_insights",
                ],
            },
        }

    async def analyze_and_route(
        self, query: str, user_context: dict[str, Any]
    ) -> QueryAnalysis:
        """
        Analyze query using Cortex AI and determine optimal routing strategy
        """
        try:
            # Use Cortex for intelligent query analysis
            analysis_prompt = f"""
            Analyze this business intelligence query for optimal system routing:

            Query: "{query}"
            User Role: {user_context.get("role", "employee")}
            User Department: {user_context.get("department", "unknown")}

            Analyze and classify:

            1. QUERY TYPE:
               - OPERATIONAL: Needs real-time data/actions (MCP servers)
               - ANALYTICAL: Needs historical analysis/insights (Lambda GPU)
               - HYBRID: Needs both real-time and analytical data
               - SYSTEM: System status/health queries

            2. URGENCY LEVEL:
               - CRITICAL: Immediate response needed (<1s)
               - HIGH: Fast response needed (<3s)
               - MEDIUM: Standard response acceptable (<10s)
               - LOW: Detailed analysis acceptable (<30s)

            3. BUSINESS DOMAIN:
               - customer_management, project_management, financial_analysis
               - operational_metrics, strategic_planning, infrastructure
               - development, intelligence

            4. TARGET SYSTEMS (choose one or more):
               - mcp_servers: For real-time operations and immediate actions
               - QDRANT_cortex: For analytics, trends, and complex analysis
               - both: For queries requiring real-time data + analytics

            5. PROCESSING STRATEGY:
               - sequential: Process systems in order
               - parallel: Process systems simultaneously
               - conditional: Route based on data availability

            Respond in JSON format:
            {{
                "query_type": "OPERATIONAL|ANALYTICAL|HYBRID|SYSTEM",
                "urgency": "CRITICAL|HIGH|MEDIUM|LOW",
                "confidence": 0.0-1.0,
                "target_systems": ["mcp_servers", "QDRANT_cortex"],
                "processing_strategy": "sequential|parallel|conditional",
                "business_domain": "domain_name",
                "reasoning": "Brief explanation of routing decision",
                "context_requirements": ["list", "of", "required", "context"],
                "recommended_model": "premium|balanced|cost_optimized"
            }}
            """

            # Get AI analysis from Cortex
            cortex_response = await self.cortex_service.generate_insights(
                analysis_prompt,
                context_data={"query": query, "user_context": user_context},
            )

            # Parse and validate response
            if isinstance(cortex_response, dict) and "query_type" in cortex_response:
                analysis_data = cortex_response
            else:
                # Fallback to rule-based analysis
                logger.warning("Cortex analysis failed, using rule-based fallback")
                analysis_data = await self._fallback_analysis(query, user_context)

            # Create QueryAnalysis object
            return QueryAnalysis(
                query_type=QueryType(
                    analysis_data.get("query_type", "ANALYTICAL").lower()
                ),
                urgency=UrgencyLevel(analysis_data.get("urgency", "MEDIUM").lower()),
                confidence=float(analysis_data.get("confidence", 0.7)),
                target_systems=analysis_data.get(
                    "target_systems", ["QDRANT_cortex"]
                ),
                processing_strategy=analysis_data.get(
                    "processing_strategy", "sequential"
                ),
                estimated_response_time=self._estimate_response_time(
                    analysis_data.get("target_systems", ["QDRANT_cortex"]),
                    analysis_data.get("processing_strategy", "sequential"),
                ),
                context_requirements=analysis_data.get("context_requirements", []),
                business_domain=analysis_data.get("business_domain", "general"),
                recommended_model=analysis_data.get("recommended_model", "balanced"),
            )

        except Exception as e:
            logger.exception(f"Error in query analysis: {e}")
            # Return safe fallback
            return await self._fallback_analysis(query, user_context)

    async def _fallback_analysis(
        self, query: str, user_context: dict[str, Any]
    ) -> QueryAnalysis:
        """Rule-based fallback when Cortex analysis fails"""
        query_lower = query.lower()

        # Determine query type based on keywords
        operational_keywords = [
            "create",
            "update",
            "delete",
            "send",
            "notify",
            "execute",
            "run",
            "start",
            "stop",
        ]
        analytical_keywords = [
            "analyze",
            "trend",
            "forecast",
            "predict",
            "insights",
            "report",
            "dashboard",
        ]
        system_keywords = ["health", "status", "performance", "connectivity", "system"]

        if any(keyword in query_lower for keyword in system_keywords):
            query_type = QueryType.SYSTEM
            target_systems = ["mcp_servers"]
            urgency = UrgencyLevel.HIGH
        elif any(keyword in query_lower for keyword in operational_keywords):
            query_type = QueryType.OPERATIONAL
            target_systems = ["mcp_servers"]
            urgency = UrgencyLevel.HIGH
        elif any(keyword in query_lower for keyword in analytical_keywords):
            query_type = QueryType.ANALYTICAL
            target_systems = ["QDRANT_cortex"]
            urgency = UrgencyLevel.MEDIUM
        else:
            # Default to hybrid for complex queries
            query_type = QueryType.HYBRID
            target_systems = ["mcp_servers", "QDRANT_cortex"]
            urgency = UrgencyLevel.MEDIUM

        # Determine business domain
        business_domain = "general"
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                business_domain = domain
                break

        return QueryAnalysis(
            query_type=query_type,
            urgency=urgency,
            confidence=0.6,  # Lower confidence for fallback
            target_systems=target_systems,
            processing_strategy="parallel" if len(target_systems) > 1 else "sequential",
            estimated_response_time=self._estimate_response_time(
                target_systems, "parallel"
            ),
            context_requirements=["user_role", "business_context"],
            business_domain=business_domain,
            recommended_model="balanced",
        )

    def _estimate_response_time(
        self, target_systems: list[str], strategy: str
    ) -> float:
        """Estimate response time based on target systems and strategy"""
        if not target_systems:
            return 1.0

        system_times = []
        for system in target_systems:
            if system in self.system_capabilities:
                system_times.append(self.system_capabilities[system]["response_time"])
            else:
                system_times.append(2.0)  # Default estimate

        if strategy == "parallel":
            # Parallel processing - limited by slowest system
            return max(system_times) + 0.5  # Add coordination overhead
        else:
            # Sequential processing - sum of all systems
            return sum(system_times) + 0.2  # Add minimal coordination overhead

    async def get_routing_recommendations(self, business_domain: str) -> dict[str, Any]:
        """Get routing recommendations for a specific business domain"""
        try:
            recommendations = {
                "customer_management": {
                    "preferred_systems": ["mcp_servers", "QDRANT_cortex"],
                    "strategy": "hybrid",
                    "real_time_priority": [
                        "interaction_updates",
                        "deal_changes",
                        "churn_alerts",
                    ],
                    "analytical_priority": [
                        "sentiment_analysis",
                        "expansion_predictions",
                        "relationship_health",
                    ],
                },
                "project_management": {
                    "preferred_systems": ["mcp_servers"],
                    "strategy": "operational_first",
                    "real_time_priority": [
                        "task_updates",
                        "status_changes",
                        "notifications",
                    ],
                    "analytical_priority": [
                        "team_performance",
                        "project_health",
                        "resource_planning",
                    ],
                },
                "financial_analysis": {
                    "preferred_systems": ["QDRANT_cortex"],
                    "strategy": "analytical_first",
                    "real_time_priority": ["deal_alerts", "revenue_milestones"],
                    "analytical_priority": [
                        "revenue_trends",
                        "forecasting",
                        "profitability_analysis",
                    ],
                },
                "infrastructure": {
                    "preferred_systems": ["mcp_servers"],
                    "strategy": "operational_first",
                    "real_time_priority": ["system_health", "deployments", "scaling"],
                    "analytical_priority": [
                        "cost_analysis",
                        "utilization_trends",
                        "capacity_planning",
                    ],
                },
            }

            return recommendations.get(
                business_domain,
                {
                    "preferred_systems": ["QDRANT_cortex"],
                    "strategy": "balanced",
                    "real_time_priority": [],
                    "analytical_priority": ["general_analysis"],
                },
            )

        except Exception as e:
            logger.exception(f"Error getting routing recommendations: {e}")
            return {"preferred_systems": ["QDRANT_cortex"], "strategy": "balanced"}

    async def optimize_routing_performance(self) -> dict[str, Any]:
        """Analyze and optimize routing performance"""
        try:
            # This would analyze historical routing decisions and performance
            optimization_report = {
                "total_queries_analyzed": 0,  # Would be populated from logs
                "average_response_time": 0.0,
                "routing_accuracy": 0.0,
                "performance_improvements": [],
                "recommended_adjustments": [],
            }

            return optimization_report

        except Exception as e:
            logger.exception(f"Error optimizing routing performance: {e}")
            return {"error": "Performance optimization unavailable"}


# Global router instance
intelligent_router = IntelligentQueryRouter()
