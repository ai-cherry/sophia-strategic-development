"""
Centralized Agent Router for Sophia AI
Handles all natural language commands and routes to appropriate agents
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Types of capabilities agents can have"""
    DOCKER = "docker"
    PULUMI = "pulumi"
    CLAUDE = "claude"
    GONG = "gong"
    SLACK = "slack"
    GENERAL = "general"

@dataclass
class AgentRegistration:
    """Registration info for an agent"""
    name: str
    capabilities: List[AgentCapability]
    handler: Callable
    description: str
    context_requirements: List[str] = None

class CentralizedAgentRouter:
    """
    Central router for all agent commands
    - Maintains agent registry
    - Routes based on intent and context
    - Logs all routing decisions
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentRegistration] = {}
        self.routing_history: List[Dict[str, Any]] = []
        self.context_manager = None  # Will be set during initialization
        
    def register_agent(self, registration: AgentRegistration):
        """Register an agent with its capabilities"""
        self.agents[registration.name] = registration
        logger.info(f"Registered agent: {registration.name} with capabilities: {registration.capabilities}")
        
    async def route_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route a command to the appropriate agent
        Returns the result and logs the routing decision
        """
        start_time = datetime.utcnow()
        
        try:
            # Analyze command to determine intent and target agent
            intent_analysis = self._analyze_command(command)
            
            # Select the best agent based on intent and capabilities
            selected_agent = self._select_agent(intent_analysis, context)
            
            if not selected_agent:
                return {
                    "status": "error",
                    "message": "No suitable agent found for this command",
                    "command": command
                }
            
            # Check context requirements
            if selected_agent.context_requirements:
                missing_context = self._check_context_requirements(
                    selected_agent.context_requirements, 
                    context
                )
                if missing_context:
                    return {
                        "status": "error",
                        "message": f"Missing required context: {missing_context}",
                        "command": command
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
                "status": result.get("status", "unknown")
            }
            self.routing_history.append(routing_info)
            logger.info(f"Routed command to {selected_agent.name}: {command[:50]}...")
            
            return {
                **result,
                "routing_info": routing_info
            }
            
        except Exception as e:
            logger.error(f"Error routing command: {e}")
            return {
                "status": "error",
                "message": str(e),
                "command": command
            }
    
    def _analyze_command(self, command: str) -> Dict[str, Any]:
        """Analyze command to determine intent and required capabilities"""
        command_lower = command.lower()
        
        # Docker-related keywords
        if any(keyword in command_lower for keyword in ["docker", "container", "image"]):
            return "docker_agent"
        
        # Pulumi/Infrastructure keywords
        elif any(keyword in command_lower for keyword in ["pulumi", "iac", "deploy", "stack"]):
            return "pulumi_agent"
        
        # Claude/AI assistance keywords
        elif any(keyword in command_lower for keyword in ["claude", "review", "generate", "analyze", "refactor"]):
            return "claude_agent"
        
        # Gong/CRM keywords
        elif any(keyword in command_lower for keyword in ["gong", "call", "meeting", "crm", "sales"]):
            return {"primary_capability": AgentCapability.GONG, "confidence": 0.9}
        
        # Slack/Communication keywords
        elif any(keyword in command_lower for keyword in ["slack", "notify", "message", "channel"]):
            return {"primary_capability": AgentCapability.SLACK, "confidence": 0.9}
        
        # Knowledge base keywords
        elif any(keyword in command_lower for keyword in ["knowledge", "search", "ingest", "document", "ask"]):
            return "knowledge_agent"
        
        # Hugging Face keywords
        elif any(keyword in command_lower for keyword in ["huggingface", "hf", "model", "dataset", "paper", "space"]):
            return "huggingface_agent"
        
        # Codebase keywords
        elif any(keyword in command_lower for keyword in ["codebase", "architecture", "contextualize"]):
            return "codebase_awareness_agent"
        
        # Default to Brain agent for general and complex queries
        else:
            logger.info(f"No specific agent found for command, defaulting to Brain agent.")
            return "brain_agent"
    
    def _select_agent(self, intent_analysis: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Optional[AgentRegistration]:
        """Select the best agent based on intent analysis"""
        required_capability = intent_analysis.get("primary_capability")
        
        # Find agents with the required capability
        suitable_agents = [
            agent for agent in self.agents.values()
            if required_capability in agent.capabilities
        ]
        
        # If multiple agents match, prefer the one with higher specificity
        if suitable_agents:
            # For now, return the first match. In future, could use confidence scores
            return suitable_agents[0]
        
        # Fallback to general agent if available
        general_agents = [
            agent for agent in self.agents.values()
            if AgentCapability.GENERAL in agent.capabilities
        ]
        
        return general_agents[0] if general_agents else None
    
    def _check_context_requirements(self, requirements: List[str], context: Optional[Dict[str, Any]]) -> List[str]:
        """Check if all required context fields are present"""
        if not context:
            return requirements
        
        missing = [req for req in requirements if req not in context]
        return missing
    
    def get_routing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent routing history for debugging and monitoring"""
        return self.routing_history[-limit:]
    
    def get_registered_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered agents"""
        return {
            name: {
                "capabilities": [cap.value for cap in agent.capabilities],
                "description": agent.description,
                "context_requirements": agent.context_requirements
            }
            for name, agent in self.agents.items()
        }

# Global router instance
agent_router = CentralizedAgentRouter() 