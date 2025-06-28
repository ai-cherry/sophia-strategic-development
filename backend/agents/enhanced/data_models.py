# File: backend/agents/enhanced/data_models.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    parameters: dict[str, Any]
    required_capabilities: list[AgentCapability]
    priority: int = 1
    dependencies: list[str] = field(default_factory=list)


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
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryRecord:
    """Canonical model for a single memory record, ensuring consistency across the platform."""

    id: str
    content: str
    category: str
    tags: list[str] = field(default_factory=list)
    embedding: list[float] | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed_at: datetime | None = None

    # Metadata for intelligence and retrieval
    importance_score: float = 0.5
    confidence_score: float = 1.0
    usage_count: int = 0

    # Contextual links to business entities
    deal_id: str | None = None
    call_id: str | None = None
    contact_id: str | None = None

    # Source and detection information
    source_system: str = "sophia_ai"
    auto_detected: bool = False

    # Additional unstructured metadata
    additional_metadata: dict[str, Any] = field(default_factory=dict)
