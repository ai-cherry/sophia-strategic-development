"""Data models for ai_memory_v2 MCP server."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryCategory(str, Enum):
    """Memory category enumeration."""
    GENERAL = "general"
    TECHNICAL = "technical"
    BUSINESS = "business"
    PERSONAL = "personal"
    PROJECT = "project"
    LEARNING = "learning"

class MemoryEntry(BaseModel):
    """Memory entry model."""
    id: int | None = Field(None, description="Memory ID")
    content: str = Field(..., description="Memory content", max_length=10000)
    embedding: list[float] | None = Field(None, description="Embedding vector")
    category: MemoryCategory = Field(default=MemoryCategory.GENERAL, description="Memory category")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: list[str] = Field(default_factory=list, description="Memory tags")
    source: str | None = Field(None, description="Source of memory (e.g., conversation, document)")
    user_id: str | None = Field(None, description="User who created the memory")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results")
    threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")
    categories: list[MemoryCategory] | None = Field(None, description="Filter by categories")
    tags: list[str] | None = Field(None, description="Filter by tags")
    user_id: str | None = Field(None, description="Filter by user")
    date_from: datetime | None = Field(None, description="Filter by date range")
    date_to: datetime | None = Field(None, description="Filter by date range")

class SearchResult(BaseModel):
    """Search result model."""
    memory: MemoryEntry = Field(..., description="Memory entry")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    highlights: list[str] | None = Field(None, description="Highlighted snippets")

class MemoryStats(BaseModel):
    """Memory statistics model."""
    total_memories: int = Field(..., description="Total number of memories")
    memories_by_category: dict[str, int] = Field(..., description="Count by category")
    top_tags: list[dict[str, Any]] = Field(..., description="Most used tags")
    storage_size_mb: float = Field(..., description="Total storage size in MB")
    oldest_memory: datetime | None = Field(None, description="Oldest memory date")
    newest_memory: datetime | None = Field(None, description="Newest memory date")

class BulkMemoryRequest(BaseModel):
    """Bulk memory storage request."""
    memories: list[MemoryEntry] = Field(..., description="List of memories to store")
    skip_duplicates: bool = Field(default=True, description="Skip duplicate memories")

class MemoryUpdateRequest(BaseModel):
    """Memory update request."""
    content: str | None = Field(None, description="Updated content")
    category: MemoryCategory | None = Field(None, description="Updated category")
    metadata: dict[str, Any] | None = Field(None, description="Updated metadata")
    tags: list[str] | None = Field(None, description="Updated tags")
