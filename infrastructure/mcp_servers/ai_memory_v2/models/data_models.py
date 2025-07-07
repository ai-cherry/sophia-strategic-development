"""Data models for ai_memory_v2 MCP server."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

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
    id: Optional[int] = Field(None, description="Memory ID")
    content: str = Field(..., description="Memory content", max_length=10000)
    embedding: Optional[List[float]] = Field(None, description="Embedding vector")
    category: MemoryCategory = Field(default=MemoryCategory.GENERAL, description="Memory category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Memory tags")
    source: Optional[str] = Field(None, description="Source of memory (e.g., conversation, document)")
    user_id: Optional[str] = Field(None, description="User who created the memory")
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
    categories: Optional[List[MemoryCategory]] = Field(None, description="Filter by categories")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    user_id: Optional[str] = Field(None, description="Filter by user")
    date_from: Optional[datetime] = Field(None, description="Filter by date range")
    date_to: Optional[datetime] = Field(None, description="Filter by date range")

class SearchResult(BaseModel):
    """Search result model."""
    memory: MemoryEntry = Field(..., description="Memory entry")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    highlights: Optional[List[str]] = Field(None, description="Highlighted snippets")

class MemoryStats(BaseModel):
    """Memory statistics model."""
    total_memories: int = Field(..., description="Total number of memories")
    memories_by_category: Dict[str, int] = Field(..., description="Count by category")
    top_tags: List[Dict[str, Any]] = Field(..., description="Most used tags")
    storage_size_mb: float = Field(..., description="Total storage size in MB")
    oldest_memory: Optional[datetime] = Field(None, description="Oldest memory date")
    newest_memory: Optional[datetime] = Field(None, description="Newest memory date")
    
class BulkMemoryRequest(BaseModel):
    """Bulk memory storage request."""
    memories: List[MemoryEntry] = Field(..., description="List of memories to store")
    skip_duplicates: bool = Field(default=True, description="Skip duplicate memories")
    
class MemoryUpdateRequest(BaseModel):
    """Memory update request."""
    content: Optional[str] = Field(None, description="Updated content")
    category: Optional[MemoryCategory] = Field(None, description="Updated category")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
