"""Cursor Mode Optimization System for Sophia AI.

Provides optimization hints for Cursor AI interaction modes without changing core routing.
Enhances agent routing with mode-specific recommendations for better user experience.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re

from .agent_categories import AgentCategory, CursorMode, get_agent_category

logger = logging.getLogger(__name__)


@dataclass
class CursorModeHint:
    """Optimization hints for Cursor AI interaction modes"""
    preferred_mode: str      # "chat", "composer", "agent"
    response_style: str      # "conversational", "structured", "streaming"  
    complexity_level: str    # "simple", "moderate", "complex"
    estimated_duration: str  # "short", "medium", "long"
    requires_confirmation: bool = False
    supports_streaming: bool = True
    context_required: bool = False


class TaskComplexity(Enum):
    """Task complexity levels for mode optimization"""
    SIMPLE = "simple"        # < 30 seconds, single operation
    MODERATE = "moderate"    # 30 seconds - 5 minutes, multi-step
    COMPLEX = "complex"      # > 5 minutes, autonomous operation


class ResponseStyle(Enum):
    """Response formatting styles"""
    CONVERSATIONAL = "conversational"  # Natural, chat-like responses
    STRUCTURED = "structured"          # Organized, multi-section responses
    STREAMING = "streaming"             # Real-time progress updates


class CursorModeOptimizer:
    """Provides optimization hints without changing core routing"""
    
    # Command patterns mapped to mode hints
    MODE_HINTS = {
        # Quick queries - Chat Mode (conversational, immediate)
        "show": CursorModeHint("chat", "conversational", "simple", "short"),
        "get": CursorModeHint("chat", "conversational", "simple", "short"),
        "check": CursorModeHint("chat", "conversational", "simple", "short"),
        "status": CursorModeHint("chat", "conversational", "simple", "short"),
        "help": CursorModeHint("chat", "conversational", "simple", "short"),
        "list": CursorModeHint("chat", "conversational", "simple", "short"),
        "what": CursorModeHint("chat", "conversational", "simple", "short"),
        "how": CursorModeHint("chat", "conversational", "simple", "short"),
        "why": CursorModeHint("chat", "conversational", "simple", "short"),
        
        # Multi-step tasks - Composer Mode (structured, planned)  
        "analyze": CursorModeHint("composer", "structured", "moderate", "medium", context_required=True),
        "optimize": CursorModeHint("composer", "structured", "moderate", "medium", context_required=True),
        "integrate": CursorModeHint("composer", "structured", "moderate", "medium", context_required=True),
        "generate": CursorModeHint("composer", "structured", "moderate", "medium", context_required=True),
        "create": CursorModeHint("composer", "structured", "moderate", "medium"),
        "build": CursorModeHint("composer", "structured", "moderate", "medium"),
        "design": CursorModeHint("composer", "structured", "moderate", "medium", context_required=True),
        "implement": CursorModeHint("composer", "structured", "moderate", "medium", context_required=True),
        "sync": CursorModeHint("composer", "structured", "moderate", "medium"),
        "process": CursorModeHint("composer", "structured", "moderate", "medium"),
        
        # Complex operations - Agent Mode (streaming, autonomous)
        "deploy": CursorModeHint("agent", "streaming", "complex", "long", requires_confirmation=True),
        "refactor": CursorModeHint("agent", "streaming", "complex", "long", context_required=True),
        "migrate": CursorModeHint("agent", "streaming", "complex", "long", requires_confirmation=True),
        "automate": CursorModeHint("agent", "streaming", "complex", "long", requires_confirmation=True),
        "setup": CursorModeHint("agent", "streaming", "complex", "long", requires_confirmation=True),
        "configure": CursorModeHint("agent", "streaming", "complex", "medium", requires_confirmation=True),
        "install": CursorModeHint("agent", "streaming", "complex", "medium", requires_confirmation=True),
        "update": CursorModeHint("agent", "streaming", "moderate", "medium"),
    }
    
    # Complex command patterns (regex-based)
    COMPLEX_PATTERNS = {
        r"deploy.*to.*production": CursorModeHint("agent", "streaming", "complex", "long", requires_confirmation=True),
        r"migrate.*database": CursorModeHint("agent", "streaming", "complex", "long", requires_confirmation=True),
        r"refactor.*entire": CursorModeHint("agent", "streaming", "complex", "long", context_required=True),
        r"analyze.*all.*calls": CursorModeHint("composer", "structured", "moderate", "medium", context_required=True),
        r"generate.*report": CursorModeHint("composer", "structured", "moderate", "medium"),
        r"check.*health.*all": CursorModeHint("chat", "conversational", "simple", "short"),
    }
    
    @classmethod
    def get_mode_hint(cls, command: str, agent_name: Optional[str] = None) -> Optional[CursorModeHint]:
        """Get optimization hint without affecting routing"""
        command_lower = command.lower().strip()
        
        # First, check complex patterns
        for pattern, hint in cls.COMPLEX_PATTERNS.items():
            if re.search(pattern, command_lower):
                return hint
        
        # Then check simple keyword matching
        for keyword, hint in cls.MODE_HINTS.items():
            if keyword in command_lower:
                # Enhance hint with agent-specific information
                if agent_name:
                    enhanced_hint = cls._enhance_hint_with_agent_info(hint, agent_name)
                    return enhanced_hint
                return hint
        
        # Fallback: use agent category if available
        if agent_name:
            return cls._get_hint_from_agent_category(agent_name)
            
        return None
    
    @classmethod
    def _enhance_hint_with_agent_info(cls, base_hint: CursorModeHint, agent_name: str) -> CursorModeHint:
        """Enhance base hint with agent-specific characteristics"""
        category = get_agent_category(agent_name)
        
        # Adjust based on agent category
        if category == AgentCategory.INFRASTRUCTURE:
            # Infrastructure operations are typically more complex
            return CursorModeHint(
                preferred_mode="agent",
                response_style="streaming", 
                complexity_level="complex",
                estimated_duration="long",
                requires_confirmation=True,
                context_required=True
            )
        elif category == AgentCategory.BUSINESS_INTELLIGENCE:
            # BI operations benefit from structured responses
            return CursorModeHint(
                preferred_mode="composer",
                response_style="structured",
                complexity_level=base_hint.complexity_level,
                estimated_duration=base_hint.estimated_duration,
                context_required=True
            )
        elif category == AgentCategory.MONITORING:
            # Monitoring is typically quick and conversational
            return CursorModeHint(
                preferred_mode="chat", 
                response_style="conversational",
                complexity_level="simple",
                estimated_duration="short"
            )
        
        return base_hint
    
    @classmethod
    def _get_hint_from_agent_category(cls, agent_name: str) -> CursorModeHint:
        """Generate hint based purely on agent category"""
        category = get_agent_category(agent_name)
        
        category_hints = {
            AgentCategory.CODE_ANALYSIS: CursorModeHint(
                "agent", "streaming", "complex", "long", context_required=True
            ),
            AgentCategory.CODE_GENERATION: CursorModeHint(
                "composer", "structured", "moderate", "medium", context_required=True
            ),
            AgentCategory.INFRASTRUCTURE: CursorModeHint(
                "agent", "streaming", "complex", "long", requires_confirmation=True
            ),
            AgentCategory.BUSINESS_INTELLIGENCE: CursorModeHint(
                "composer", "structured", "moderate", "medium", context_required=True
            ),
            AgentCategory.WORKFLOW_AUTOMATION: CursorModeHint(
                "composer", "structured", "moderate", "medium"
            ),
            AgentCategory.INTEGRATION_MANAGEMENT: CursorModeHint(
                "composer", "structured", "moderate", "short"
            ),
            AgentCategory.RESEARCH_ANALYSIS: CursorModeHint(
                "chat", "conversational", "simple", "short"
            ),
            AgentCategory.DOCUMENTATION: CursorModeHint(
                "chat", "conversational", "simple", "short", context_required=True
            ),
            AgentCategory.MONITORING: CursorModeHint(
                "chat", "conversational", "simple", "short"
            ),
        }
        
        return category_hints.get(category, CursorModeHint(
            "chat", "conversational", "simple", "short"
        ))
    
    @classmethod
    def analyze_command_complexity(cls, command: str) -> TaskComplexity:
        """Analyze command complexity for optimization"""
        command_lower = command.lower()
        
        # Complex indicators
        complex_indicators = [
            "deploy", "migrate", "refactor entire", "setup from scratch",
            "configure all", "automate workflow", "full analysis"
        ]
        
        # Moderate indicators
        moderate_indicators = [
            "analyze", "generate", "optimize", "integrate", "create", "build",
            "process", "sync", "update", "configure"
        ]
        
        if any(indicator in command_lower for indicator in complex_indicators):
            return TaskComplexity.COMPLEX
        elif any(indicator in command_lower for indicator in moderate_indicators):
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE
    
    @classmethod
    def get_response_format_hint(cls, mode_hint: CursorModeHint) -> Dict[str, any]:
        """Get response formatting hints for the chosen mode"""
        format_hints = {
            "chat": {
                "style": "conversational",
                "structure": "free_form",
                "use_markdown": True,
                "include_context": False,
                "max_length": "medium"
            },
            "composer": {
                "style": "structured", 
                "structure": "sectioned",
                "use_markdown": True,
                "include_context": True,
                "max_length": "long",
                "include_code_blocks": True
            },
            "agent": {
                "style": "streaming",
                "structure": "progressive",
                "use_markdown": True,
                "include_context": True,
                "max_length": "unlimited",
                "show_progress": True,
                "include_code_blocks": True
            }
        }
        
        return format_hints.get(mode_hint.preferred_mode, format_hints["chat"])
    
    @classmethod 
    def suggest_cursor_workflow(cls, command: str, agent_name: Optional[str] = None) -> Dict[str, any]:
        """Suggest complete Cursor workflow for command"""
        mode_hint = cls.get_mode_hint(command, agent_name)
        if not mode_hint:
            return {}
            
        complexity = cls.analyze_command_complexity(command)
        format_hint = cls.get_response_format_hint(mode_hint)
        
        workflow = {
            "recommended_mode": mode_hint.preferred_mode,
            "complexity_level": complexity.value,
            "estimated_duration": mode_hint.estimated_duration,
            "requires_confirmation": mode_hint.requires_confirmation,
            "context_required": mode_hint.context_required,
            "response_formatting": format_hint,
            "workflow_steps": cls._generate_workflow_steps(mode_hint, complexity)
        }
        
        return workflow
    
    @classmethod
    def _generate_workflow_steps(cls, mode_hint: CursorModeHint, complexity: TaskComplexity) -> List[str]:
        """Generate suggested workflow steps"""
        if mode_hint.preferred_mode == "chat":
            return [
                "Use Chat Mode for quick, conversational interaction",
                "Ask follow-up questions as needed",
                "Get immediate, concise responses"
            ]
        elif mode_hint.preferred_mode == "composer":
            return [
                "Use Composer Mode for structured, multi-file tasks",
                "Provide clear requirements and context",
                "Review generated plan before execution",
                "Iterate on results as needed"
            ]
        elif mode_hint.preferred_mode == "agent":
            return [
                "Use Agent Mode for autonomous, complex operations",
                "Provide comprehensive context and requirements",
                "Review and confirm planned changes" if mode_hint.requires_confirmation else "Monitor progress",
                "Verify results and run tests",
                "Deploy or finalize changes"
            ]
        
        return []


# Integration helper functions
def get_mode_hint(command: str, agent_name: Optional[str] = None) -> Optional[CursorModeHint]:
    """Get Cursor mode optimization hint for command"""
    return CursorModeOptimizer.get_mode_hint(command, agent_name)


def suggest_cursor_workflow(command: str, agent_name: Optional[str] = None) -> Dict[str, any]:
    """Get complete Cursor workflow suggestion"""
    return CursorModeOptimizer.suggest_cursor_workflow(command, agent_name)


def analyze_command_complexity(command: str) -> TaskComplexity:
    """Analyze command complexity level"""
    return CursorModeOptimizer.analyze_command_complexity(command)


# Global instance for easy access
cursor_mode_optimizer = CursorModeOptimizer() 