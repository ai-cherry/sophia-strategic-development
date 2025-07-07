"""
Unified Chat Models - Phase 2A Implementation
Centralized models for all chat functionality
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


# Enums for better type safety
class ChatMode(str, Enum):
    """Chat operation modes"""

    UNIVERSAL = "universal"
    SOPHIA = "sophia"
    EXECUTIVE = "executive"


class ChatProvider(str, Enum):
    """AI providers"""

    OPENAI = "openai"
    PORTKEY = "portkey"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


class MessageRole(str, Enum):
    """Message roles in conversation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatStatus(str, Enum):
    """Chat processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Core Models
class ChatMessage(BaseModel):
    """Individual chat message"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] | None = None


class ChatContext(BaseModel):
    """Chat context information"""

    user_id: str | None = None
    user_role: str | None = None
    organization: str | None = None
    department: str | None = None
    preferences: dict[str, Any] | None = None
    business_context: dict[str, Any] | None = None


class ChatConfiguration(BaseModel):
    """Chat configuration settings"""

    mode: ChatMode = ChatMode.UNIVERSAL
    provider: ChatProvider = ChatProvider.OPENAI
    model: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=8000)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    frequency_penalty: float | None = Field(default=None, ge=-2.0, le=2.0)
    presence_penalty: float | None = Field(default=None, ge=-2.0, le=2.0)
    stop_sequences: list[str] | None = None


# Request Models
class ChatRequest(BaseModel):
    """Unified chat request"""

    message: str = Field(
        ..., min_length=1, max_length=10000, description="User message content"
    )
    mode: ChatMode = Field(default=ChatMode.UNIVERSAL, description="Chat mode")
    session_id: str | None = Field(
        default=None, description="Session ID for conversation continuity"
    )
    context: ChatContext | None = Field(default=None, description="Chat context")
    configuration: ChatConfiguration | None = Field(
        default=None, description="Chat configuration"
    )
    stream: bool = Field(default=False, description="Enable streaming response")

    @validator("session_id", pre=True, always=True)
    def generate_session_id(self, v):
        return v or str(uuid.uuid4())

    @validator("configuration", pre=True, always=True)
    def set_default_config(self, v, values):
        if v is None:
            mode = values.get("mode", ChatMode.UNIVERSAL)
            return ChatConfiguration(mode=mode)
        return v


class StreamChatRequest(ChatRequest):
    """Streaming chat request"""

    stream: bool = Field(default=True, description="Enable streaming response")


# Response Models
class ChatMetadata(BaseModel):
    """Chat response metadata"""

    response_type: str
    features: list[str] = []
    model_used: str | None = None
    provider_info: dict[str, Any] | None = None
    processing_time_ms: int | None = None
    confidence_score: float | None = None


class ChatUsage(BaseModel):
    """Token and cost usage information"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    cost_currency: str = "USD"


class ChatResponse(BaseModel):
    """Unified chat response"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    response: str = Field(..., description="AI response content")
    session_id: str = Field(..., description="Session ID")
    mode: ChatMode = Field(..., description="Chat mode used")
    provider: ChatProvider = Field(..., description="AI provider used")
    status: ChatStatus = Field(default=ChatStatus.COMPLETED)
    metadata: ChatMetadata | None = None
    suggestions: list[str] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    usage: ChatUsage | None = None


class StreamChatResponse(BaseModel):
    """Streaming chat response chunk"""

    id: str
    session_id: str
    delta: str = Field(..., description="Response chunk")
    finished: bool = Field(default=False, description="Whether this is the final chunk")
    metadata: dict[str, Any] | None = None


class ChatError(BaseModel):
    """Chat error response"""

    error_code: str
    error_message: str
    details: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Session Models
class ChatSession(BaseModel):
    """Chat session information"""

    session_id: str
    mode: ChatMode
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    context: ChatContext | None = None
    configuration: ChatConfiguration | None = None
    is_active: bool = True


class ChatHistory(BaseModel):
    """Chat conversation history"""

    session_id: str
    messages: list[ChatMessage] = []
    created_at: datetime
    updated_at: datetime
    total_messages: int = 0


# Analytics Models
class ChatAnalytics(BaseModel):
    """Chat usage analytics"""

    session_id: str
    mode: ChatMode
    provider: ChatProvider
    total_messages: int
    total_tokens: int
    total_cost: float
    average_response_time_ms: float
    user_satisfaction: float | None = None
    created_at: datetime
    period_start: datetime
    period_end: datetime


class ChatMetrics(BaseModel):
    """Aggregated chat metrics"""

    total_sessions: int
    total_messages: int
    total_tokens: int
    total_cost: float
    average_session_length: float
    mode_distribution: dict[str, int]
    provider_distribution: dict[str, int]
    period_start: datetime
    period_end: datetime


# Batch Processing Models
class BatchChatRequest(BaseModel):
    """Batch chat processing request"""

    requests: list[ChatRequest] = Field(..., max_items=100)
    batch_id: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    priority: int = Field(default=1, ge=1, le=10)


class BatchChatResponse(BaseModel):
    """Batch chat processing response"""

    batch_id: str
    responses: list[ChatResponse | ChatError]
    total_requests: int
    successful_requests: int
    failed_requests: int
    processing_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Configuration Models
class ProviderConfig(BaseModel):
    """AI provider configuration"""

    provider: ChatProvider
    api_key: str | None = None
    base_url: str | None = None
    model_mappings: dict[str, str] = {}
    rate_limits: dict[str, int] | None = None
    timeout_seconds: int = 30
    retry_attempts: int = 3


class ModeConfig(BaseModel):
    """Chat mode configuration"""

    mode: ChatMode
    default_provider: ChatProvider
    allowed_providers: list[ChatProvider]
    default_model: str
    system_prompt: str
    max_context_length: int = 4000
    features: list[str] = []


class UnifiedChatConfig(BaseModel):
    """Complete unified chat configuration"""

    providers: list[ProviderConfig]
    modes: list[ModeConfig]
    default_mode: ChatMode = ChatMode.UNIVERSAL
    session_timeout_minutes: int = 60
    max_sessions_per_user: int = 10
    enable_analytics: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 300


# Export all models
__all__ = [
    # Enums
    "ChatMode",
    "ChatProvider",
    "MessageRole",
    "ChatStatus",
    # Core Models
    "ChatMessage",
    "ChatContext",
    "ChatConfiguration",
    # Request Models
    "ChatRequest",
    "StreamChatRequest",
    "BatchChatRequest",
    # Response Models
    "ChatResponse",
    "StreamChatResponse",
    "ChatError",
    "BatchChatResponse",
    "ChatMetadata",
    "ChatUsage",
    # Session Models
    "ChatSession",
    "ChatHistory",
    # Analytics Models
    "ChatAnalytics",
    "ChatMetrics",
    # Configuration Models
    "ProviderConfig",
    "ModeConfig",
    "UnifiedChatConfig",
]
