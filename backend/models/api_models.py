"""
API Models for Sophia AI Platform - Pydantic v2
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Request Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    mode: str = Field(default="sophia", pattern="^(universal|sophia|executive)$")
    stream: bool = Field(default=True)
    model: str = Field(default="gpt-4")
    session_id: str | None = None


class KnowledgeUploadRequest(BaseModel):
    filename: str
    content_type: str
    size: int = Field(..., gt=0, le=100_000_000)  # 100MB limit


# Response Models
class ChatResponse(BaseModel):
    response: str
    mode: str
    session_id: str
    timestamp: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatStreamChunk(BaseModel):
    content: str
    finished: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    services: dict[str, bool] = Field(default_factory=dict)


class DashboardMetrics(BaseModel):
    revenue: dict[str, Any]
    agents: dict[str, Any]
    success_rate: dict[str, Any]
    api_calls: dict[str, Any]
    timestamp: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    correlation_id: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# MCP Models
class MCPServiceHealth(BaseModel):
    status: str
    service: str
    capabilities: list[str]
    timestamp: str
    version: str
    response_time: str
    uptime: str
