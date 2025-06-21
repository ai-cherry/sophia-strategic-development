"""Centralized Agent Router for Sophia AI.

Handles all natural language commands and routes to appropriate agents
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..specialized.client_health_agent import ClientHealthAgent
from ..specialized.hr_agent import HRAgent
from ..specialized.marketing_agent import MarketingAgent

# Agent Imports
from ..specialized.sales_coach_agent import SalesCoachAgent
from .base_agent import AgentConfig

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Types of capabilities agents can have."""

    DOCKER = "docker"
    PULUMI = "pulumi"
    CLAUDE = "claude"
    GONG = "gong"
    SLACK = "slack"
    GENERAL = "general"
    SALES_COACHING = "sales_coaching"
    CLIENT_HEALTH = "client_health"
    MARKETING_INTELLIGENCE = "marketing_intelligence"
    HR_ANALYTICS = "hr_analytics"


@dataclass
class AgentRegistration:
    """Registration info for an agent."""name: str.

    capabilities: List[AgentCapability]
    handler: Callable
    description: str
    context_requirements: List[str] = None


class CentralizedAgentRouter:
    """Central router for all agent commands.

            - Maintains agent registry
            - Routes based on intent and context
            - Logs all routing decisions
    """def __init__(self):.

        self.agents: Dict[str, AgentRegistration] = {}
        self.agent_instances: Dict[str, Any] = {}
        self.routing_history: List[Dict[str, Any]] = []
        self.context_manager = None  # Will be set during initialization

        # Initialize and register agents
        self._register_specialized_agents()

    def _register_specialized_agents(self):
        """Initializes and registers all specialized agents."""
        # This would typically be driven by a config file.
        agent_configs = {
            "sales_coach": AgentConfig(
                agent_id="sales_coach_01",
                agent_type="specialized",
                specialization="Sales Coaching",
            ),
            "client_health": AgentConfig(
                agent_id="client_health_01",
                agent_type="specialized",
                specialization="Client Health",
            ),
            "marketing": AgentConfig(
                agent_id="marketing_01",
                agent_type="specialized",
                specialization="Marketing Intelligence",
            ),
            "hr": AgentConfig(
                agent_id="hr_01",
                agent_type="specialized",
                specialization="HR Analytics",
            ),
        }

        loop = asyncio.get_event_loop()

        # Sales Coach
        sales_coach = loop.run_until_complete(SalesCoachAgent.pooled(agent_configs["sales_coach"]))
        self.agent_instances["sales_coach"] = sales_coach
        self.register_agent(
            AgentRegistration(
                name="sales_coach",
                capabilities=[AgentCapability.SALES_COACHING, AgentCapability.GONG],
                handler=sales_coach.process_task,
                description="Analyzes sales calls to provide coaching and performance insights.",
            )
        )

        # Client Health
        client_health = loop.run_until_complete(ClientHealthAgent.pooled(agent_configs["client_health"]))
        self.agent_instances["client_health"] = client_health
        self.register_agent(
            AgentRegistration(
                name="client_health",
                capabilities=[AgentCapability.CLIENT_HEALTH],
                handler=client_health.process_task,
                description="Monitors client health and predicts churn risk.",
            )
        )

        # Marketing
        marketing = MarketingAgent(agent_configs["marketing"])
        self.agent_instances["marketing"] = marketing
        self.register_agent(
            AgentRegistration(
                name="marketing",
                capabilities=[AgentCapability.MARKETING_INTELLIGENCE],
                handler=marketing.process_task,
                description="Synthesizes market intelligence from internal and external sources.",
            )
        )

        # HR
        hr = loop.run_until_complete(HRAgent.pooled(agent_configs["hr"]))
        self.agent_instances["hr"] = hr
        self.register_agent(
            AgentRegistration(
                name="hr",
                capabilities=[AgentCapability.HR_ANALYTICS, AgentCapability.SLACK],
                handler=hr.process_task,
                description="Analyzes team communication patterns for engagement insights.",
            )
        )

    def register_agent(self, registration: AgentRegistration):
        """Register an agent with its capabilities."""self.agents[registration.name] = registration.

        logger.info(
            f"Registered agent: {registration.name} with capabilities: {registration.capabilities}"
        )

    async def route_command(
        self, command: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route a command to the appropriate agent.

                        Returns the result and logs the routing decision
        """start_time = datetime.utcnow().

        try:
            # Analyze command to determine intent and target agent
            intent_analysis = self._analyze_command(command)

            # Select the best agent based on intent and capabilities
            selected_agent = self._select_agent(intent_analysis, context)

            if not selected_agent:
                return {
                    "status": "error",
                    "message": "No suitable agent found for this command",
                    "command": command,
                }

            # Check context requirements
            if selected_agent.context_requirements:
                missing_context = self._check_context_requirements(
                    selected_agent.context_requirements, context
                )
                if missing_context:
                    return {
                        "status": "error",
                        "message": f"Missing required context: {missing_context}",
                        "command": command,
                    }

            # Execute the command
            result = await selected_agent.handler(command, context)

            # Log routing decision
            routing_info = {
                "timestamp": start_time.isoformat(),
                "command": command,
                "selected_agent": selected_agent.name,
                "intent": intent_analysis,
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "status": result.get("status", "unknown"),
            }
            self.routing_history.append(routing_info)
            logger.info(f"Routed command to {selected_agent.name}: {command[:50]}...")

            return {**result, "routing_info": routing_info}

        except Exception as e:
            logger.error(f"Error routing command: {e}")
            return {"status": "error", "message": str(e), "command": command}

    def _analyze_command(self, command: str) -> Dict[str, Any]:
        """Analyze command to determine intent and required capabilities."""command_lower = command.lower().

        # Docker-related keywords
        if any(
            keyword in command_lower for keyword in ["docker", "container", "image"]
        ):
            return {"agent": "docker_agent"}

        # Pulumi/Infrastructure keywords
        elif any(
            keyword in command_lower for keyword in ["pulumi", "iac", "deploy", "stack"]
        ):
            return {"agent": "pulumi_agent"}

        # Claude/AI assistance keywords
        elif any(
            keyword in command_lower
            for keyword in ["claude", "review", "generate", "analyze", "refactor"]
        ):
            return {"agent": "claude_agent"}

        # Specialized Agent keywords
        elif any(
            keyword in command_lower
            for keyword in ["coach", "sales call", "performance review"]
        ):
            return {"agent": "sales_coach", "task_type": "analyze_gong_call"}

        elif any(
            keyword in command_lower
            for keyword in ["client health", "churn risk", "at-risk"]
        ):
            return {"agent": "client_health", "task_type": "calculate_health_score"}

        elif any(
            keyword in command_lower
            for keyword in ["competitor", "market analysis", "marketing insight"]
        ):
            return {"agent": "marketing", "task_type": "generate_competitive_analysis"}

        elif any(
            keyword in command_lower
            for keyword in ["hr", "team engagement", "communication patterns"]
        ):
            return {"agent": "hr", "task_type": "analyze_team_communication"}

        # Gong/CRM keywords
        elif any(
            keyword in command_lower
            for keyword in ["gong", "call", "meeting", "crm", "sales"]
        ):
            return {"agent": "gong_agent"}  # Placeholder for a more generic Gong agent

        # Slack/Communication keywords
        elif any(
            keyword in command_lower
            for keyword in ["slack", "notify", "message", "channel"]
        ):
            return {
                "agent": "slack_agent"
            }  # Placeholder for a more generic Slack agent

        # Knowledge base keywords
        elif any(
            keyword in command_lower
            for keyword in ["knowledge", "search", "ingest", "document", "ask"]
        ):
            return {"agent": "knowledge_agent"}

        # Hugging Face keywords
        elif any(
            keyword in command_lower
            for keyword in ["huggingface", "hf", "model", "dataset", "paper", "space"]
        ):
            return "huggingface_agent"

        # Codebase keywords
        elif any(
            keyword in command_lower
            for keyword in ["codebase", "architecture", "contextualize"]
        ):
            return "codebase_awareness_agent"

        # Admin keywords
        elif any(
            keyword in command_lower
            for keyword in ["admin", "status", "health", "system"]
        ):
            return "admin_agent"
        elif any(keyword in command_lower for keyword in ["hubspot", "crm", "deal"]):
            return "hubspot_agent"
        elif any(
            keyword in command_lower for keyword in ["intercom", "support", "ticket"]
        ):
            return "intercom_agent"
        elif any(keyword in command_lower for keyword in ["iac", "infra", "configure"]):
            return "iac_manager_agent"

        # Default to Brain agent for general and complex queries
        else:
            logger.info(
                "No specific agent found for command, defaulting to Brain agent."
            )
            return {"agent": "brain_agent"}

    def _select_agent(
        self, intent_analysis: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Optional[AgentRegistration]:
        """Select the best agent based on intent analysis."""agent_name = intent_analysis.get("agent").

        if agent_name in self.agents:
            return self.agents[agent_name]

        return None

    def _check_context_requirements(
        self, requirements: List[str], context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Check if all required context fields are present."""if not context:.

            return requirements

        missing = [req for req in requirements if req not in context]
        return missing

    def get_routing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent routing history for debugging and monitoring."""return self.routing_history[-limit:].

    def get_registered_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered agents."""
        return {
            name: {
                "capabilities": [cap.value for cap in agent.capabilities],
                "description": agent.description,
                "context_requirements": agent.context_requirements,
            }
            for name, agent in self.agents.items()
        }


# Global router instance
agent_router = CentralizedAgentRouter()
