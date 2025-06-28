# File: backend/agents/enhanced/data_models.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime


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


@dataclass
class MemoryRecord:
    """Canonical model for a single memory record, ensuring consistency across the platform."""

    id: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed_at: Optional[datetime] = None

    # Metadata for intelligence and retrieval
    importance_score: float = 0.5
    confidence_score: float = 1.0
    usage_count: int = 0

    # Contextual links to business entities
    deal_id: Optional[str] = None
    call_id: Optional[str] = None
    contact_id: Optional[str] = None

    # Source and detection information
    source_system: str = "sophia_ai"
    auto_detected: bool = False

    # Additional unstructured metadata
    additional_metadata: Dict[str, Any] = field(default_factory=dict)
