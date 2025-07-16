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

@dataclass
class GongCallData:
    """Data model for Gong call records."""

    call_id: str
    title: str
    started_at: datetime
    duration: int  # in seconds
    transcript: str
    participants: list[str] = field(default_factory=list)
    meeting_url: str | None = None
    call_type: str | None = None

    def to_memory_record(self) -> MemoryRecord:
        """Convert to a MemoryRecord for storage in the memory system."""
        return MemoryRecord(
            id=f"gong_call_{self.call_id}",
            content=f"Call: {self.title}\nTranscript: {self.transcript[:500]}...",
            category="gong_call",
            tags=["gong", "call", self.call_type or "unknown_type"],
            deal_id=None,  # Could be enhanced to extract deal info
            call_id=self.call_id,
            source_system="gong",
            additional_metadata={
                "duration": self.duration,
                "participants": self.participants,
                "meeting_url": self.meeting_url,
                "started_at": self.started_at.isoformat(),
            },
        )

@dataclass
class SlackMessageData:
    """Data model for Slack message records."""

    message_id: str
    channel_id: str
    channel_name: str
    user_id: str
    text: str
    timestamp: datetime
    thread_ts: str | None = None
    message_type: str = "message"

    def to_memory_record(self) -> MemoryRecord:
        """Convert to a MemoryRecord for storage in the memory system."""
        return MemoryRecord(
            id=f"slack_message_{self.message_id}",
            content=f"Channel: {self.channel_name}\nMessage: {self.text}",
            category="slack_message",
            tags=["slack", "message", self.channel_name],
            source_system="slack",
            additional_metadata={
                "channel_id": self.channel_id,
                "channel_name": self.channel_name,
                "user_id": self.user_id,
                "thread_ts": self.thread_ts,
                "message_type": self.message_type,
                "timestamp": self.timestamp.isoformat(),
            },
        )

@dataclass
class IntegratedConversationRecord:
    """Data model for integrated conversations across platforms (Gong, Slack, etc.)."""

    conversation_id: str
    source_platform: str
    conversation_time: datetime
    conversation_title: str
    conversation_content: str
    participants: list[str] = field(default_factory=list)
    duration_seconds: int = 0
    platform_metadata: dict[str, Any] = field(default_factory=dict)

    # AI-generated insights (populated via analysis)
    key_insights: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    sentiment_score: float | None = None
    summary: str | None = None

    def to_memory_record(self) -> MemoryRecord:
        """Convert to a MemoryRecord for storage in the memory system."""
        return MemoryRecord(
            id=f"integrated_conv_{self.conversation_id}",
            content=f"Platform: {self.source_platform}\nTitle: {self.conversation_title}\nContent: {self.conversation_content[:500]}...",
            category="integrated_conversation",
            tags=["integrated", self.source_platform, "conversation"],
            source_system=f"integrated_{self.source_platform}",
            importance_score=0.8,  # Integrated conversations are typically important
            additional_metadata={
                "source_platform": self.source_platform,
                "participants": self.participants,
                "duration_seconds": self.duration_seconds,
                "conversation_time": self.conversation_time.isoformat(),
                "key_insights": self.key_insights,
                "action_items": self.action_items,
                "sentiment_score": self.sentiment_score,
                "summary": self.summary,
                "platform_metadata": self.platform_metadata,
            },
        )
