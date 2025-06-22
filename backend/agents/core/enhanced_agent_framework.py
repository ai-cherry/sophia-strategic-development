"""Enhanced Agent Framework for Sophia AI Platform.

Hybrid framework supporting both traditional and Agno agents.
Provides intelligent agent allocation and seamless integration between architectures.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from agno.agent import Agent as AgnoAgent
from agno.team import Team

from backend.agents.core.agent_framework import agent_framework
from backend.agents.core.agent_router import agent_router
from backend.agents.core.agno_mcp_bridge import agno_mcp_bridge
from backend.agents.core.base_agent import AgentConfig, BaseAgent
from backend.core.config_loader import get_config_loader

logger = logging.getLogger(__name__)


class EnhancedAgentFramework:
    """Enhanced framework supporting both traditional and Agno agents.

    This framework intelligently decides whether to use traditional BaseAgent
    or high-performance Agno agents based on performance requirements,
    while maintaining full backward compatibility.
    """
    def __init__(self):
        self.mcp_orchestrator = agent_framework
        self.agno_bridge = agno_mcp_bridge
        self.agent_router = agent_router
        self.hybrid_agents: Dict[str, Union[BaseAgent, AgnoAgent]] = {}
        self.agent_teams: Dict[str, Team] = {}
        self.performance_metrics: Dict[str, Any] = {}
        self.allocation_strategy = "intelligent"  # intelligent, agno_preferred, traditional_only

    async def initialize(self):
        """Initialize the enhanced framework."""
        logger.info("Initializing Enhanced Agent Framework...")

        # Initialize base components
        await self.mcp_orchestrator.initialize()
        await self.agno_bridge.initialize()

        # Load configuration
        config_loader = await get_config_loader()
        agno_config = config_loader.config_cache.get("agno_integration", {})

        self.allocation_strategy = agno_config.get("bridge_mode", "intelligent")

        logger.info(f"Enhanced Agent Framework initialized with strategy: {self.allocation_strategy}")

    async def create_agent(
        self,
        agent_name: str,
        agent_config: Dict[str, Any],
        force_type: Optional[str] = None
    ) -> Union[BaseAgent, AgnoAgent]:
        """Create agent using optimal framework.

        Args:
            agent_name: Name of the agent
            agent_config: Agent configuration
            force_type: Force specific agent type ('agno', 'traditional', or None)

        Returns:
            Optimally configured agent
        """
        logger.info(f"Creating agent '{agent_name}' with config: {agent_config}")

        # Determine agent type based on strategy
        use_agno = self._should_use_agno(agent_config, force_type)

        if use_agno:
            agent = await self._create_agno_agent(agent_name, agent_config)
        else:
            agent = await self._create_traditional_agent(agent_name, agent_config)

        # Register agent
        self.hybrid_agents[agent_name] = agent

        # Track performance metrics
        self.performance_metrics[agent_name] = {
            "type": "agno" if use_agno else "traditional",
            "created_at": asyncio.get_event_loop().time(),
            "config": agent_config
        }

        logger.info(f"Created {'Agno' if use_agno else 'traditional'} agent: {agent_name}")
        return agent

    async def create_agent_team(
        self,
        team_name: str,
        team_config: Dict[str, Any],
        agents: List[Union[str, Dict[str, Any]]]
    ) -> Team:
        """Create coordinated agent team using Agno Team 2.0.

        Args:
            team_name: Name of the team
            team_config: Team configuration
            agents: List of agent names or agent configurations

        Returns:
            Coordinated agent team
        """
        logger.info(f"Creating agent team '{team_name}' with {len(agents)} members")

        # Create team members
        team_members = []
        for agent_spec in agents:
            if isinstance(agent_spec, str):
                # Use existing agent
                if agent_spec in self.hybrid_agents:
                    agent = self.hybrid_agents[agent_spec]
                    if isinstance(agent, AgnoAgent):
                        team_members.append(agent)
                    else:
                        logger.warning(f"Agent {agent_spec} is not Agno-compatible for teams")
                else:
                    logger.error(f"Agent {agent_spec} not found")
            else:
                # Create new agent for team
                agent_name = agent_spec.get("name", f"{team_name}_member_{len(team_members)}")
                agent_config = agent_spec.get("config", {})
                # Force Agno for team members
                agent = await self.create_agent(agent_name, agent_config, force_type="agno")
                if isinstance(agent, AgnoAgent):
                    team_members.append(agent)

        if not team_members:
            raise ValueError(f"No valid Agno agents available for team {team_name}")

        # Create Agno team
        from agno.models.anthropic import Claude

        team = Team(
            mode=team_config.get("coordination_mode", "coordinate"),
            members=team_members,
            model=Claude(id="claude-sonnet-4-20250514"),
            instructions=team_config.get("instructions", f"Coordinate as team {team_name}"),
            success_criteria=team_config.get("success_criteria", "Complete team task successfully")
        )

        self.agent_teams[team_name] = team

        logger.info(f"Created team '{team_name}' with {len(team_members)} Agno agents")
        return team

    async def route_request(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None,
        prefer_teams: bool = False
    ) -> Dict[str, Any]:
        """Route request to optimal agent or team.

        Args:
            request: Natural language request
            context: Request context
            prefer_teams: Whether to prefer team coordination

        Returns:
            Response from agent or team
        """
        logger.info(f"Routing request: {request[:100]}...")

        # Check if request requires team coordination
        if prefer_teams or self._requires_team_coordination(request, context):
            team_name = self._determine_best_team(request, context)
            if team_name and team_name in self.agent_teams:
                logger.info(f"Routing to team: {team_name}")
                return await self.agent_teams[team_name].run(request)

        # Route to individual agent (existing router handles this)
        return await self.agent_router.route_command(request, context)

    def _should_use_agno(self, agent_config: Dict[str, Any], force_type: Optional[str]) -> bool:
        """Determine whether to use Agno for this agent."""
        if force_type:
            return force_type == "agno"

        if self.allocation_strategy == "traditional_only":
            return False
        elif self.allocation_strategy == "agno_preferred":
            return True
        else:  # intelligent allocation
            # Performance-critical indicators
            performance_critical = agent_config.get('performance_critical', False)
            high_frequency = agent_config.get('high_frequency', False)
            requires_teams = agent_config.get('requires_teams', False)
            low_memory = agent_config.get('low_memory_preferred', False)

            # Complex integration indicators (favor traditional)
            complex_integrations = len(agent_config.get('integrations', [])) > 3
            custom_logic = agent_config.get('has_custom_logic', False)

            # Decision logic
            agno_score = 0
            if performance_critical: agno_score += 3
            if high_frequency: agno_score += 2
            if requires_teams: agno_score += 3
            if low_memory: agno_score += 1
            if complex_integrations: agno_score -= 2
            if custom_logic: agno_score -= 1

            return agno_score > 0

    async def _create_agno_agent(self, agent_name: str, config: Dict[str, Any]) -> AgnoAgent:
        """Create Agno-enhanced agent."""
        mcp_services = config.get('mcp_services', [])

        agent_config = {
            "model": config.get("model", {"type": "claude"}),
            "instructions": config.get("instructions", ""),
            "use_memory": config.get("use_memory", False),
            "use_knowledge": config.get("use_knowledge", False),
            "knowledge": config.get("knowledge", {}),
            "session_state": config.get("session_state", {}),
            "show_tool_calls": config.get("show_tool_calls", True),
            "markdown": config.get("markdown", True),
            "add_state_in_messages": config.get("add_state_in_messages", True)
        }

        return await self.agno_bridge.create_agno_agent_with_mcp_tools(
            agent_name=agent_name,
            agent_config=agent_config,
            mcp_services=mcp_services
        )

    async def _create_traditional_agent(self, agent_name: str, config: Dict[str, Any]) -> BaseAgent:
        """Create traditional BaseAgent."""
        # Convert config to AgentConfig format
        agent_config = AgentConfig(
            agent_id=agent_name,
            agent_type=config.get("agent_type", "specialized"),
            specialization=config.get("specialization", agent_name)
        )

        # This would need to be implemented based on your agent types
        # For now, return a placeholder
        from backend.agents.core.base_agent import BaseAgent

        class GenericAgent(BaseAgent):
            async def get_capabilities(self):
                return []

            async def process_task(self, task):
                return {"status": "completed", "result": "Traditional agent response"}

        return GenericAgent(agent_config)

    def _requires_team_coordination(self, request: str, context: Optional[Dict[str, Any]]) -> bool:
        """Determine if request benefits from team coordination."""
        coordination_keywords = [
            "comprehensive analysis", "cross-platform insights",
            "multi-source data", "complete picture", "integrated view",
            "coordinate", "collaborate", "team analysis"
        ]
        return any(keyword in request.lower() for keyword in coordination_keywords)

    def _determine_best_team(self, request: str, context: Optional[Dict[str, Any]]) -> Optional[str]:
        """Determine the best team for the request."""
        # Simple keyword-based team selection
        if any(keyword in request.lower() for keyword in ["business", "sales", "revenue", "pipeline"]):
            return "business_intelligence"
        elif any(keyword in request.lower() for keyword in ["executive", "strategic", "leadership"]):
            return "executive_knowledge"

        # Return first available team as fallback
        return list(self.agent_teams.keys())[0] if self.agent_teams else None

    async def get_agent(self, agent_name: str) -> Optional[Union[BaseAgent, AgnoAgent]]:
        """Get agent by name."""
        return self.hybrid_agents.get(agent_name)

    async def get_team(self, team_name: str) -> Optional[Team]:
        """Get team by name."""
        return self.agent_teams.get(team_name)

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all agents and teams."""
        return {
            "agents": self.performance_metrics,
            "teams": {name: {"members": len(team.members)} for name, team in self.agent_teams.items()},
            "allocation_strategy": self.allocation_strategy,
            "total_agents": len(self.hybrid_agents),
            "total_teams": len(self.agent_teams)
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the framework."""
        try:
            # Check bridge health
            bridge_health = await self.agno_bridge.health_check()

            # Check agent router health
            router_health = True  # Assume healthy, could add actual check

            return {
                "status": "healthy",
                "bridge_health": bridge_health,
                "router_health": router_health,
                "active_agents": len(self.hybrid_agents),
                "active_teams": len(self.agent_teams)
            }
        except Exception as e:
            logger.error(f"Framework health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global enhanced framework instance
enhanced_agent_framework = EnhancedAgentFramework()


async def initialize_enhanced_framework():
    """Initialize the global enhanced agent framework."""
    await enhanced_agent_framework.initialize()
    logger.info("Enhanced Agent Framework initialized successfully")


# Convenience functions
async def create_hybrid_agent(
    agent_name: str,
    agent_config: Dict[str, Any],
    force_type: Optional[str] = None
) -> Union[BaseAgent, AgnoAgent]:
    """Create hybrid agent using enhanced framework."""
        return await enhanced_agent_framework.create_agent(agent_name, agent_config, force_type)


async def create_agent_team(
    team_name: str,
    team_config: Dict[str, Any],
    agents: List[Union[str, Dict[str, Any]]]
) -> Team:
    """Create agent team using enhanced framework."""
        return await enhanced_agent_framework.create_agent_team(team_name, team_config, agents)


async def route_intelligent_request(
    request: str,
    context: Optional[Dict[str, Any]] = None,
    prefer_teams: bool = False
) -> Dict[str, Any]:
    """Route request intelligently between agents and teams."""
        return await enhanced_agent_framework.route_request(request, context, prefer_teams)
