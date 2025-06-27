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

# You can add other relevant data models for the enhanced agent framework here. 

# =====================================================
# GONG & SLACK DATA INTEGRATION MODELS
# =====================================================

@dataclass
class GongCallData:
    """Data model for Gong call records integrated into the memory system."""
    call_id: str
    title: str
    started_at: datetime
    duration: int  # in seconds
    transcript: str
    participants: List[str]
    meeting_url: Optional[str] = None
    call_type: Optional[str] = None
    sentiment_score: Optional[float] = None
    key_topics: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    
    # Integration metadata
    processed_at: Optional[datetime] = None
    memory_records_created: List[str] = field(default_factory=list)
    embedding_generated: bool = False
    
    def to_memory_record(self) -> MemoryRecord:
        """Convert Gong call data to a standardized memory record."""
        return MemoryRecord(
            id=f"gong_call_{self.call_id}",
            content=f"Call: {self.title}\nTranscript: {self.transcript[:1000]}...",
            category="gong_call",
            tags=["gong", "call", "transcript"] + self.key_topics,
            created_at=self.started_at,
            importance_score=min(0.8, len(self.transcript) / 5000),  # Higher for longer calls
            call_id=self.call_id,
            source_system="gong",
            auto_detected=True,
            additional_metadata={
                "duration": self.duration,
                "participants": self.participants,
                "meeting_url": self.meeting_url,
                "call_type": self.call_type,
                "sentiment_score": self.sentiment_score,
                "action_items": self.action_items
            }
        )

@dataclass
class SlackMessageData:
    """Data model for Slack message records integrated into the memory system."""
    message_id: str
    channel_id: str
    channel_name: str
    user_id: str
    username: Optional[str] = None
    text: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    thread_ts: Optional[str] = None
    message_type: str = "message"
    reactions: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Integration metadata
    processed_at: Optional[datetime] = None
    memory_record_created: Optional[str] = None
    embedding_generated: bool = False
    
    def to_memory_record(self) -> MemoryRecord:
        """Convert Slack message data to a standardized memory record."""
        importance = 0.3  # Base importance for Slack messages
        
        # Increase importance for longer messages
        if len(self.text) > 200:
            importance += 0.2
        
        # Increase importance for messages with reactions
        if self.reactions:
            importance += 0.1
        
        # Increase importance for messages with attachments
        if self.attachments:
            importance += 0.1
            
        return MemoryRecord(
            id=f"slack_msg_{self.message_id}",
            content=f"Slack #{self.channel_name}: {self.text}",
            category="slack_message",
            tags=["slack", "message", self.channel_name],
            created_at=self.timestamp,
            importance_score=min(importance, 0.8),
            source_system="slack",
            auto_detected=True,
            additional_metadata={
                "channel_id": self.channel_id,
                "channel_name": self.channel_name,
                "user_id": self.user_id,
                "username": self.username,
                "thread_ts": self.thread_ts,
                "message_type": self.message_type,
                "reactions": self.reactions,
                "attachments": self.attachments
            }
        )

@dataclass
class IntegratedConversationRecord:
    """Unified model for conversations from multiple platforms (Gong, Slack, etc.)."""
    conversation_id: str
    source_platform: str  # "gong", "slack", etc.
    conversation_time: datetime
    conversation_title: str
    conversation_content: str
    participants: List[str]
    duration_seconds: int = 0
    platform_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # AI-generated insights
    summary: Optional[str] = None
    key_insights: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    sentiment_score: Optional[float] = None
    importance_score: float = 0.5
    
    # Memory integration
    memory_records: List[str] = field(default_factory=list)
    embedding_vector: Optional[List[float]] = None
    
    def to_memory_record(self) -> MemoryRecord:
        """Convert integrated conversation to a standardized memory record."""
        return MemoryRecord(
            id=f"integrated_conv_{self.conversation_id}",
            content=f"{self.conversation_title}: {self.summary or self.conversation_content[:500]}",
            category=f"{self.source_platform}_conversation",
            tags=[self.source_platform, "conversation"] + [p.lower() for p in self.participants[:3]],
            created_at=self.conversation_time,
            importance_score=self.importance_score,
            source_system=self.source_platform,
            auto_detected=True,
            embedding=self.embedding_vector,
            additional_metadata={
                "platform": self.source_platform,
                "participants": self.participants,
                "duration_seconds": self.duration_seconds,
                "key_insights": self.key_insights,
                "action_items": self.action_items,
                "sentiment_score": self.sentiment_score,
                **self.platform_metadata
            }
        )

@dataclass
class IntegratedKnowledgeContent:
    """Model for knowledge content that spans multiple platforms and sources."""
    content_id: str
    title: str
    content_type: str  # "document", "conversation", "insight", etc.
    source_platforms: List[str]  # ["gong", "slack", "knowledge_base"]
    content_text: str
    
    # Cross-platform references
    related_calls: List[str] = field(default_factory=list)
    related_messages: List[str] = field(default_factory=list)
    related_documents: List[str] = field(default_factory=list)
    
    # AI-enhanced metadata
    topics: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)  # People, companies, products
    sentiment_score: Optional[float] = None
    confidence_score: float = 1.0
    
    # Temporal information
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Memory and search optimization
    embedding_vector: Optional[List[float]] = None
    search_keywords: List[str] = field(default_factory=list)
    importance_score: float = 0.5
    
    def to_memory_record(self) -> MemoryRecord:
        """Convert integrated knowledge content to a standardized memory record."""
        return MemoryRecord(
            id=f"knowledge_{self.content_id}",
            content=f"{self.title}: {self.content_text[:800]}",
            category="integrated_knowledge",
            tags=["knowledge"] + self.topics + self.source_platforms,
            created_at=self.created_at,
            last_accessed_at=self.last_updated,
            importance_score=self.importance_score,
            confidence_score=self.confidence_score,
            source_system="integrated_platform",
            auto_detected=True,
            embedding=self.embedding_vector,
            additional_metadata={
                "content_type": self.content_type,
                "source_platforms": self.source_platforms,
                "related_calls": self.related_calls,
                "related_messages": self.related_messages,
                "related_documents": self.related_documents,
                "topics": self.topics,
                "entities": self.entities,
                "sentiment_score": self.sentiment_score,
                "search_keywords": self.search_keywords
            }
        )

# =====================================================
# AIRBYTE INTEGRATION METADATA
# =====================================================

@dataclass
class AirbyteSourceConfig:
    """Configuration for Airbyte data source connections."""
    source_name: str
    source_type: str  # "gong", "slack", "hubspot", etc.
    connection_id: str
    destination_schema: str
    sync_frequency: str = "daily"
    replication_mode: str = "incremental"
    table_prefix: str = ""
    
    # Authentication and connection details (stored securely)
    auth_method: str = "oauth"  # "oauth", "api_key", "token"
    
    # Data processing preferences
    enable_vectorization: bool = True
    enable_memory_integration: bool = True
    auto_process_insights: bool = True
    
    # Quality and monitoring
    last_sync_at: Optional[datetime] = None
    sync_status: str = "configured"  # "configured", "active", "error", "paused"
    error_count: int = 0
    total_records_synced: int = 0

