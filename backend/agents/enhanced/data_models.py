# File: backend/agents/enhanced/data_models.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional

class AgentCapability(Enum):
    """Available agent capabilities for the Cortex-enhanced orchestrator."""
    SQL_ANALYSIS = "sql_analysis"
    VECTOR_SEARCH = "vector_search"
    PREDICTIVE_MODELING = "predictive_modeling"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    REPORT_GENERATION = "report_generation"

@dataclass
class AgentTask:
    """
    Defines a single task to be executed by an agent within a workflow.
    It includes all necessary information for the orchestrator to assign
    and manage the task.
    """
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    required_capabilities: List[AgentCapability]
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)

@dataclass
class AgentResult:
    """
    Represents the output of a completed agent task, including the result,
    performance metrics, and any metadata.
    """
    task_id: str
    agent_id: str
    status: str  # e.g., 'completed', 'failed', 'error'
    result: Any
    execution_time: float
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

# You can add other relevant data models for the enhanced agent framework here. 