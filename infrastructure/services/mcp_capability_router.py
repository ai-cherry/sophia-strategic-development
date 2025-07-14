"""
MCP Capability-Based Router
Implements intelligent routing for MCP servers based on capabilities
Uses Open Agent Platform patterns for dynamic server selection
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Capability(Enum):
    """Standard MCP capabilities"""

    # Data capabilities
    DATABASE_QUERY = "database_query"
    VECTOR_SEARCH = "vector_search"
    DATA_ANALYSIS = "data_analysis"

    # Code capabilities
    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"

    # Communication capabilities
    SLACK_MESSAGING = "slack_messaging"
    EMAIL_SENDING = "email_sending"
    NOTIFICATION = "notification"

    # Project management
    TASK_MANAGEMENT = "task_management"
    PROJECT_TRACKING = "project_tracking"
    ISSUE_TRACKING = "issue_tracking"

    # AI/ML capabilities
    TEXT_GENERATION = "text_generation"
    EMBEDDING_GENERATION = "embedding_generation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"

    # Business intelligence
    REVENUE_ANALYSIS = "revenue_analysis"
    CUSTOMER_INSIGHTS = "customer_insights"
    SALES_COACHING = "sales_coaching"


@dataclass
class ServerCapability:
    """Represents a server's capability with metadata"""

    server_name: str
    capability: Capability
    performance_score: float = 1.0  # 0-1 score
    reliability_score: float = 1.0  # 0-1 score
    cost_per_request: float = 0.0
    average_latency_ms: float = 100.0


@dataclass
class RoutingDecision:
    """Represents a routing decision"""

    primary_server: str
    fallback_servers: list[str]
    capability: Capability
    confidence_score: float
    reason: str


class MCPCapabilityRouter:
    """
    Intelligent capability-based router for MCP servers
    Selects optimal server based on capability, performance, and availability
    """

    def __init__(self):
        self.server_capabilities = self._initialize_capabilities()
        self.server_health = {}  # Updated by health monitor
        self.routing_history = []
        self.performance_metrics = {}

    def _initialize_capabilities(self) -> dict[str, list[ServerCapability]]:
        """Initialize server capability mappings"""
        return {
            "ai_memory": [
                ServerCapability("ai_memory", Capability.VECTOR_SEARCH, 0.95, 0.98),
                ServerCapability(
                    "ai_memory", Capability.EMBEDDING_GENERATION, 0.90, 0.95
                ),
                ServerCapability("ai_memory", Capability.DATA_ANALYSIS, 0.85, 0.95),
            ],
            "codacy": [
                ServerCapability("codacy", Capability.CODE_ANALYSIS, 0.98, 0.99),
                ServerCapability("codacy", Capability.CODE_REVIEW, 0.95, 0.98),
            ],
            "github": [
                ServerCapability("github", Capability.CODE_GENERATION, 0.85, 0.95),
                ServerCapability("github", Capability.ISSUE_TRACKING, 0.95, 0.99),
                ServerCapability("github", Capability.PROJECT_TRACKING, 0.90, 0.98),
            ],
            "linear": [
                ServerCapability("linear", Capability.TASK_MANAGEMENT, 0.95, 0.99),
                ServerCapability("linear", Capability.PROJECT_TRACKING, 0.93, 0.98),
                ServerCapability("linear", Capability.ISSUE_TRACKING, 0.92, 0.98),
            ],
            "qdrant_admin": [
                ServerCapability(
                    "qdrant_admin", Capability.DATABASE_QUERY, 0.98, 0.99
                ),
                ServerCapability(
                    "qdrant_admin", Capability.DATA_ANALYSIS, 0.95, 0.98
                ),
                ServerCapability(
                    "qdrant_admin", Capability.REVENUE_ANALYSIS, 0.93, 0.97
                ),
            ],
            "slack": [
                ServerCapability("slack", Capability.SLACK_MESSAGING, 0.99, 0.98),
                ServerCapability("slack", Capability.NOTIFICATION, 0.95, 0.97),
            ],
            "hubspot": [
                ServerCapability("hubspot", Capability.CUSTOMER_INSIGHTS, 0.92, 0.96),
                ServerCapability("hubspot", Capability.SALES_COACHING, 0.88, 0.95),
                ServerCapability("hubspot", Capability.EMAIL_SENDING, 0.95, 0.98),
            ],
        }

    def update_server_health(self, health_data: dict[str, dict]):
        """Update server health information from health monitor"""
        self.server_health = health_data

    def _calculate_server_score(
        self, capability: ServerCapability, health_status: str | None = None
    ) -> float:
        """Calculate overall score for a server capability"""
        # Base score from capability performance and reliability
        base_score = (
            capability.performance_score * 0.6 + capability.reliability_score * 0.4
        )

        # Adjust for health status
        health_multiplier = 1.0
        if health_status == "degraded":
            health_multiplier = 0.7
        elif health_status == "unhealthy":
            health_multiplier = 0.1
        elif health_status == "unknown":
            health_multiplier = 0.3

        # Adjust for latency (prefer faster servers)
        latency_factor = max(0.5, 1.0 - (capability.average_latency_ms / 1000))

        # Calculate final score
        final_score = base_score * health_multiplier * latency_factor

        return final_score

    async def route_request(
        self,
        capability: Capability,
        context: dict | None = None,
        prefer_servers: list[str] | None = None,
        avoid_servers: list[str] | None = None,
    ) -> RoutingDecision:
        """
        Route a request to the best available server for the capability
        """
        # Find all servers that support this capability
        candidate_servers = []

        for server_name, capabilities in self.server_capabilities.items():
            # Skip if in avoid list
            if avoid_servers and server_name in avoid_servers:
                continue

            for cap in capabilities:
                if cap.capability == capability:
                    # Get health status
                    health_info = self.server_health.get(server_name, {})
                    health_status = health_info.get("status", "unknown")

                    # Calculate score
                    score = self._calculate_server_score(cap, health_status)

                    # Boost score if in preferred list
                    if prefer_servers and server_name in prefer_servers:
                        score *= 1.2

                    candidate_servers.append((server_name, cap, score))

        # Sort by score (highest first)
        candidate_servers.sort(key=lambda x: x[2], reverse=True)

        if not candidate_servers:
            return RoutingDecision(
                primary_server="",
                fallback_servers=[],
                capability=capability,
                confidence_score=0.0,
                reason=f"No servers available for capability {capability.value}",
            )

        # Select primary and fallback servers
        primary = candidate_servers[0]
        fallbacks = [s[0] for s in candidate_servers[1:4]]  # Top 3 fallbacks

        # Calculate confidence based on primary server score
        confidence = min(primary[2], 1.0)

        # Create routing decision
        decision = RoutingDecision(
            primary_server=primary[0],
            fallback_servers=fallbacks,
            capability=capability,
            confidence_score=confidence,
            reason=f"Selected {primary[0]} with score {primary[2]:.2f}",
        )

        # Record decision
        self._record_routing_decision(decision)

        return decision

    def _record_routing_decision(self, decision: RoutingDecision):
        """Record routing decision for analysis"""
        self.routing_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "capability": decision.capability.value,
                "primary_server": decision.primary_server,
                "confidence": decision.confidence_score,
            }
        )

        # Keep only last 1000 decisions
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]

    def get_capability_coverage(self) -> dict[str, list[str]]:
        """Get which servers support each capability"""
        coverage = {}

        for capability in Capability:
            servers = []
            for server_name, caps in self.server_capabilities.items():
                if any(c.capability == capability for c in caps):
                    servers.append(server_name)
            coverage[capability.value] = servers

        return coverage

    def get_server_capabilities(self, server_name: str) -> list[Capability]:
        """Get all capabilities for a specific server"""
        if server_name not in self.server_capabilities:
            return []

        return [cap.capability for cap in self.server_capabilities[server_name]]

    def add_server_capability(
        self,
        server_name: str,
        capability: Capability,
        performance_score: float = 0.8,
        reliability_score: float = 0.8,
    ):
        """Add or update a server capability"""
        if server_name not in self.server_capabilities:
            self.server_capabilities[server_name] = []

        # Check if capability already exists
        for i, cap in enumerate(self.server_capabilities[server_name]):
            if cap.capability == capability:
                # Update existing
                self.server_capabilities[server_name][i] = ServerCapability(
                    server_name, capability, performance_score, reliability_score
                )
                return

        # Add new capability
        self.server_capabilities[server_name].append(
            ServerCapability(
                server_name, capability, performance_score, reliability_score
            )
        )

    def get_routing_stats(self) -> dict[str, Any]:
        """Get routing statistics"""
        if not self.routing_history:
            return {"total_requests": 0}

        # Calculate stats
        total = len(self.routing_history)
        by_capability = {}
        by_server = {}
        avg_confidence = 0

        for decision in self.routing_history:
            # Count by capability
            cap = decision["capability"]
            by_capability[cap] = by_capability.get(cap, 0) + 1

            # Count by server
            server = decision["primary_server"]
            by_server[server] = by_server.get(server, 0) + 1

            # Sum confidence
            avg_confidence += decision["confidence"]

        return {
            "total_requests": total,
            "by_capability": by_capability,
            "by_server": by_server,
            "average_confidence": avg_confidence / total if total > 0 else 0,
            "capability_coverage": self.get_capability_coverage(),
        }


# Singleton instance
capability_router = MCPCapabilityRouter()
