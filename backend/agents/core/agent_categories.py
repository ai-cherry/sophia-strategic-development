"""Clean Agent Categorization System for Sophia AI.

Provides simple categorization without disrupting existing routing architecture.
Maps agents to Cursor AI interaction modes for optimization.
"""

from enum import Enum
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AgentCategory(Enum):
    """Clean agent categorization aligned with Cursor AI modes"""
        # Development Agents (Cursor Agent Mode)
    CODE_ANALYSIS = "code_analysis"          # Deep code exploration
    CODE_GENERATION = "code_generation"      # Multi-file generation
    INFRASTRUCTURE = "infrastructure"        # Large-scale deployments
    
    # Interactive Agents (Cursor Composer Mode) 
    BUSINESS_INTELLIGENCE = "business_intelligence"  # Data analysis
    WORKFLOW_AUTOMATION = "workflow_automation"      # Process optimization
    INTEGRATION_MANAGEMENT = "integration_management" # API coordination
    
    # Advisory Agents (Cursor Chat Mode)
    RESEARCH_ANALYSIS = "research_analysis"   # Quick research
    DOCUMENTATION = "documentation"          # Help and guidance
    MONITORING = "monitoring"                # Status and metrics


class CursorMode(Enum):
    """Cursor AI interaction modes"""
        CHAT = "chat"           # Quick queries and conversational assistance
    COMPOSER = "composer"   # Multi-file tasks and structured operations
    AGENT = "agent"         # Complex autonomous operations


class AgentCategoryManager:
    """Manages agent categorization without disrupting existing routing"""
        # Map existing agents to categories
    CATEGORY_MAPPING = {
        # Business Intelligence Agents
        "gong_agent": AgentCategory.BUSINESS_INTELLIGENCE,
        "sales_coach": AgentCategory.BUSINESS_INTELLIGENCE, 
        "client_health": AgentCategory.BUSINESS_INTELLIGENCE,
        "call_analysis_agent": AgentCategory.BUSINESS_INTELLIGENCE,
        "crm_sync_agent": AgentCategory.BUSINESS_INTELLIGENCE,
        "insight_extraction_agent": AgentCategory.BUSINESS_INTELLIGENCE,
        
        # Infrastructure Agents
        "pulumi_agent": AgentCategory.INFRASTRUCTURE,
        "docker_agent": AgentCategory.INFRASTRUCTURE,
        "iac_manager_agent": AgentCategory.INFRASTRUCTURE,
        
        # Code Development Agents
        "claude_agent": AgentCategory.CODE_GENERATION,
        
        # Research and Analysis
        "marketing": AgentCategory.RESEARCH_ANALYSIS,
        "research_intelligence_agent": AgentCategory.RESEARCH_ANALYSIS,
        "enrichment_agent": AgentCategory.RESEARCH_ANALYSIS,
        
        # Workflow and Automation
        "hr": AgentCategory.WORKFLOW_AUTOMATION,
        "workflow_automation_agent": AgentCategory.WORKFLOW_AUTOMATION,
        
        # Monitoring and Support
        "admin_agent": AgentCategory.MONITORING,
        "metrics_agent": AgentCategory.MONITORING,
        "project_intelligence_agent": AgentCategory.MONITORING,
        "executive_agent": AgentCategory.MONITORING,
        
        # Integration Management
        "hubspot_agent": AgentCategory.INTEGRATION_MANAGEMENT,
        "intercom_agent": AgentCategory.INTEGRATION_MANAGEMENT,
    }
    
    # Map categories to optimal Cursor modes
    CURSOR_MODE_MAPPING = {
        AgentCategory.CODE_ANALYSIS: CursorMode.AGENT,
        AgentCategory.CODE_GENERATION: CursorMode.COMPOSER,
        AgentCategory.INFRASTRUCTURE: CursorMode.AGENT,
        AgentCategory.BUSINESS_INTELLIGENCE: CursorMode.COMPOSER,
        AgentCategory.WORKFLOW_AUTOMATION: CursorMode.COMPOSER,
        AgentCategory.INTEGRATION_MANAGEMENT: CursorMode.COMPOSER,
        AgentCategory.RESEARCH_ANALYSIS: CursorMode.CHAT,
        AgentCategory.DOCUMENTATION: CursorMode.CHAT,
        AgentCategory.MONITORING: CursorMode.CHAT,
    }
    
    @classmethod
    def get_category(cls, agent_name: str) -> AgentCategory:
        """Get category for agent without changing routing logic"""
        return cls.CATEGORY_MAPPING.get(agent_name, AgentCategory.RESEARCH_ANALYSIS)
    
    @classmethod
    def get_agents_by_category(cls, category: AgentCategory) -> List[str]:
        """Get agents in a category for optimization"""
        return [agent for agent, cat in cls.CATEGORY_MAPPING.items() if cat == category]
    
    @classmethod
    def get_optimal_cursor_mode(cls, agent_name: str) -> CursorMode:
        """Get optimal Cursor mode for agent"""
        category = cls.get_category(agent_name)
        return cls.CURSOR_MODE_MAPPING.get(category, CursorMode.CHAT)
    
    @classmethod
    def get_category_description(cls, category: AgentCategory) -> str:
        """Get human-readable description of category"""
        descriptions = {
            AgentCategory.CODE_ANALYSIS: "Deep code exploration and analysis",
            AgentCategory.CODE_GENERATION: "Multi-file code generation and refactoring",
            AgentCategory.INFRASTRUCTURE: "Large-scale deployments and infrastructure management",
            AgentCategory.BUSINESS_INTELLIGENCE: "Data analysis and business insights",
            AgentCategory.WORKFLOW_AUTOMATION: "Process optimization and automation",
            AgentCategory.INTEGRATION_MANAGEMENT: "API coordination and service integration",
            AgentCategory.RESEARCH_ANALYSIS: "Quick research and competitive analysis",
            AgentCategory.DOCUMENTATION: "Help, guidance, and documentation generation",
            AgentCategory.MONITORING: "Status monitoring and performance metrics",
        }
        return descriptions.get(category, "General purpose agent")
    
    @classmethod
    def get_performance_characteristics(cls, category: AgentCategory) -> Dict[str, any]:
        """Get performance characteristics for category optimization"""
        characteristics = {
            AgentCategory.CODE_ANALYSIS: {
                "expected_duration": "long",
                "resource_intensive": True,
                "requires_context": True,
                "parallelizable": False
            },
            AgentCategory.CODE_GENERATION: {
                "expected_duration": "medium", 
                "resource_intensive": True,
                "requires_context": True,
                "parallelizable": True
            },
            AgentCategory.INFRASTRUCTURE: {
                "expected_duration": "long",
                "resource_intensive": False,
                "requires_context": True,
                "parallelizable": False
            },
            AgentCategory.BUSINESS_INTELLIGENCE: {
                "expected_duration": "medium",
                "resource_intensive": True,
                "requires_context": True,
                "parallelizable": True
            },
            AgentCategory.WORKFLOW_AUTOMATION: {
                "expected_duration": "medium",
                "resource_intensive": False,
                "requires_context": True,
                "parallelizable": True
            },
            AgentCategory.INTEGRATION_MANAGEMENT: {
                "expected_duration": "short",
                "resource_intensive": False,
                "requires_context": False,
                "parallelizable": True
            },
            AgentCategory.RESEARCH_ANALYSIS: {
                "expected_duration": "short",
                "resource_intensive": False,
                "requires_context": False,
                "parallelizable": True
            },
            AgentCategory.DOCUMENTATION: {
                "expected_duration": "short",
                "resource_intensive": False,
                "requires_context": True,
                "parallelizable": True
            },
            AgentCategory.MONITORING: {
                "expected_duration": "short",
                "resource_intensive": False,
                "requires_context": False,
                "parallelizable": True
            }
        }
        return characteristics.get(category, {
            "expected_duration": "medium",
            "resource_intensive": False,
            "requires_context": False,
            "parallelizable": True
        })
    
    @classmethod
    def suggest_agent_for_task(cls, task_description: str) -> Optional[str]:
        """Suggest best agent based on task description and category matching"""
        task_lower = task_description.lower()
        
        # Infrastructure keywords
        if any(keyword in task_lower for keyword in ["deploy", "infrastructure", "pulumi", "docker", "container"]):
            infra_agents = cls.get_agents_by_category(AgentCategory.INFRASTRUCTURE)
            return infra_agents[0] if infra_agents else None
            
        # Business intelligence keywords  
        elif any(keyword in task_lower for keyword in ["gong", "sales", "analyze call", "business", "crm"]):
            bi_agents = cls.get_agents_by_category(AgentCategory.BUSINESS_INTELLIGENCE)
            return bi_agents[0] if bi_agents else None
            
        # Code-related keywords
        elif any(keyword in task_lower for keyword in ["code", "refactor", "generate", "programming"]):
            code_agents = cls.get_agents_by_category(AgentCategory.CODE_GENERATION)
            return code_agents[0] if code_agents else None
            
        # Research keywords
        elif any(keyword in task_lower for keyword in ["research", "market", "competitor", "analyze"]):
            research_agents = cls.get_agents_by_category(AgentCategory.RESEARCH_ANALYSIS)
            return research_agents[0] if research_agents else None
            
        # Monitoring keywords
        elif any(keyword in task_lower for keyword in ["status", "health", "metrics", "monitoring"]):
            monitoring_agents = cls.get_agents_by_category(AgentCategory.MONITORING)
            return monitoring_agents[0] if monitoring_agents else None
            
        return None
    
    @classmethod
    def get_category_stats(cls) -> Dict[str, any]:
        """Get statistics about agent distribution across categories"""
        category_counts = {}
        for category in AgentCategory:
            agents = cls.get_agents_by_category(category)
            category_counts[category.value] = {
                "count": len(agents),
                "agents": agents,
                "optimal_cursor_mode": cls.CURSOR_MODE_MAPPING.get(category, CursorMode.CHAT).value
            }
        
        return {
            "total_agents": len(cls.CATEGORY_MAPPING),
            "total_categories": len(AgentCategory),
            "category_distribution": category_counts,
            "unmapped_agents": len([a for a in cls.CATEGORY_MAPPING.values() 
                                  if a == AgentCategory.RESEARCH_ANALYSIS])
        }


# Convenience functions for integration with existing systems
def get_agent_category(agent_name: str) -> AgentCategory:
    """Get category for an agent"""
        return AgentCategoryManager.get_category(agent_name)


def get_optimal_cursor_mode(agent_name: str) -> CursorMode:
    """Get optimal Cursor mode for an agent"""
        return AgentCategoryManager.get_optimal_cursor_mode(agent_name)


def suggest_agent_for_task(task_description: str) -> Optional[str]:
    """Suggest best agent for a task"""
        return AgentCategoryManager.suggest_agent_for_task(task_description)


# Global instance for easy access
agent_category_manager = AgentCategoryManager() 