"""
AI Memory Models - Type-Safe Data Structures
Comprehensive Pydantic models with validation and serialization
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import numpy as np
from pydantic import BaseModel, Field, root_validator, validator


class MemoryType(str, Enum):
    """Types of memory records"""

    CONVERSATION = "conversation"
    BUSINESS_INSIGHT = "business_insight"
    TECHNICAL_KNOWLEDGE = "technical_knowledge"
    PERSONAL_PREFERENCE = "personal_preference"
    WORKFLOW_PATTERN = "workflow_pattern"
    DECISION_CONTEXT = "decision_context"
    LEARNING_OUTCOME = "learning_outcome"
    RELATIONSHIP_MAPPING = "relationship_mapping"
    STRATEGIC_PLANNING = "strategic_planning"
    OPERATIONAL_DATA = "operational_data"


class MemoryCategory(str, Enum):
    """Categories for organizing memories"""

    WORK = "work"
    PERSONAL = "personal"
    LEARNING = "learning"
    STRATEGY = "strategy"
    OPERATIONS = "operations"
    RELATIONSHIPS = "relationships"
    INSIGHTS = "insights"
    DECISIONS = "decisions"
    PATTERNS = "patterns"
    CONTEXT = "context"


class MemoryPriority(str, Enum):
    """Priority levels for memory records"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ARCHIVE = "archive"


class MemoryStatus(str, Enum):
    """Status of memory records"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PROCESSING = "processing"
    ERROR = "error"


class SearchScope(str, Enum):
    """Scope for memory searches"""

    ALL = "all"
    RECENT = "recent"
    ARCHIVED = "archived"
    BY_TYPE = "by_type"
    BY_CATEGORY = "by_category"
    BY_PRIORITY = "by_priority"
    SEMANTIC = "semantic"
    EXACT = "exact"


class MemoryMetadata(BaseModel):
    """Metadata for memory records"""

    source: str | None = Field(None, description="Source of the memory")
    author: str | None = Field(None, description="Author or creator")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    confidence_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in memory accuracy"
    )
    relevance_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Relevance score"
    )
    access_count: int = Field(default=0, ge=0, description="Number of times accessed")
    last_accessed: datetime | None = Field(None, description="Last access timestamp")
    related_memories: list[str] = Field(
        default_factory=list, description="Related memory IDs"
    )
    external_references: dict[str, str] = Field(
        default_factory=dict, description="External system references"
    )
    custom_attributes: dict[str, Any] = Field(
        default_factory=dict, description="Custom metadata attributes"
    )

    @validator("tags")
    def validate_tags(self, v: list[str]) -> list[str]:
        """Validate and normalize tags"""
        return [tag.lower().strip() for tag in v if tag.strip()]

    @validator("related_memories")
    def validate_related_memories(self, v: list[str]) -> list[str]:
        """Validate related memory IDs"""
        validated = []
        for memory_id in v:
            try:
                UUID(memory_id)  # Validate UUID format
                validated.append(memory_id)
            except ValueError:
                continue  # Skip invalid UUIDs
        return validated

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class MemoryEmbedding(BaseModel):
    """Vector embedding for memory content"""

    vector: list[float] = Field(..., description="Embedding vector")
    model: str = Field(..., description="Model used for embedding")
    dimensions: int = Field(..., gt=0, description="Vector dimensions")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    content_hash: str = Field(..., description="Hash of the content that was embedded")

    @validator("vector")
    def validate_vector(self, v: list[float]) -> list[float]:
        """Validate embedding vector"""
        if not v:
            raise ValueError("Embedding vector cannot be empty")

        # Check for valid float values
        for i, val in enumerate(v):
            if not isinstance(val, int | float) or np.isnan(val) or np.isinf(val):
                raise ValueError(f"Invalid value at index {i}: {val}")

        return v

    @root_validator
    def validate_dimensions_match(self, values: dict[str, Any]) -> dict[str, Any]:
        """Validate that vector length matches dimensions"""
        vector = values.get("vector", [])
        dimensions = values.get("dimensions", 0)

        if len(vector) != dimensions:
            raise ValueError(
                f"Vector length {len(vector)} does not match dimensions {dimensions}"
            )

        return values

    @property
    def numpy_vector(self) -> np.ndarray:
        """Get vector as numpy array"""
        return np.array(self.vector, dtype=np.float32)

    def cosine_similarity(self, other: MemoryEmbedding) -> float:
        """Calculate cosine similarity with another embedding"""
        if self.dimensions != other.dimensions:
            raise ValueError("Cannot compare embeddings with different dimensions")

        vec_a = self.numpy_vector
        vec_b = other.numpy_vector

        # Normalize vectors
        norm_a = vec_a / np.linalg.norm(vec_a)
        norm_b = vec_b / np.linalg.norm(vec_b)

        # Calculate cosine similarity
        similarity = np.dot(norm_a, norm_b)

        return float(similarity)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class MemoryRecord(BaseModel):
    """Complete memory record with all associated data"""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique memory ID"
    )
    content: str = Field(
        ..., min_length=1, max_length=50000, description="Memory content"
    )
    summary: str | None = Field(None, max_length=500, description="Brief summary")
    memory_type: MemoryType = Field(..., description="Type of memory")
    category: MemoryCategory = Field(..., description="Memory category")
    priority: MemoryPriority = Field(
        default=MemoryPriority.MEDIUM, description="Priority level"
    )
    status: MemoryStatus = Field(
        default=MemoryStatus.ACTIVE, description="Memory status"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = Field(None, description="Expiration timestamp")

    # Associated data
    embedding: MemoryEmbedding | None = Field(None, description="Vector embedding")
    metadata: MemoryMetadata = Field(
        default_factory=MemoryMetadata, description="Additional metadata"
    )

    # Context and relationships
    context: dict[str, Any] = Field(
        default_factory=dict, description="Contextual information"
    )
    parent_memory_id: str | None = Field(
        None, description="Parent memory ID for hierarchical memories"
    )
    child_memory_ids: list[str] = Field(
        default_factory=list, description="Child memory IDs"
    )

    @validator("id")
    def validate_id(self, v: str) -> str:
        """Validate memory ID format"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError("Memory ID must be a valid UUID")

    @validator("content")
    def validate_content(self, v: str) -> str:
        """Validate and normalize content"""
        content = v.strip()
        if not content:
            raise ValueError("Memory content cannot be empty")
        return content

    @validator("summary")
    def validate_summary(self, v: str | None) -> str | None:
        """Validate and normalize summary"""
        if v is None:
            return None
        summary = v.strip()
        return summary if summary else None

    @validator("expires_at")
    def validate_expires_at(
        self, v: datetime | None, values: dict[str, Any]
    ) -> datetime | None:
        """Validate expiration timestamp"""
        if v is None:
            return None

        created_at = values.get("created_at")
        if created_at and v <= created_at:
            raise ValueError("Expiration time must be after creation time")

        return v

    @validator("parent_memory_id")
    def validate_parent_memory_id(self, v: str | None) -> str | None:
        """Validate parent memory ID"""
        if v is None:
            return None
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError("Parent memory ID must be a valid UUID")

    @validator("child_memory_ids")
    def validate_child_memory_ids(self, v: list[str]) -> list[str]:
        """Validate child memory IDs"""
        validated = []
        for memory_id in v:
            try:
                UUID(memory_id)
                validated.append(memory_id)
            except ValueError:
                continue  # Skip invalid UUIDs
        return validated

    @root_validator
    def validate_no_self_reference(self, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure memory doesn't reference itself"""
        memory_id = values.get("id")
        parent_id = values.get("parent_memory_id")
        child_ids = values.get("child_memory_ids", [])

        if parent_id == memory_id:
            raise ValueError("Memory cannot be its own parent")

        if memory_id in child_ids:
            raise ValueError("Memory cannot be its own child")

        return values

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now(UTC)

    def is_expired(self) -> bool:
        """Check if memory has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def add_child_memory(self, child_id: str) -> None:
        """Add a child memory ID"""
        try:
            UUID(child_id)
            if child_id not in self.child_memory_ids and child_id != self.id:
                self.child_memory_ids.append(child_id)
                self.update_timestamp()
        except ValueError:
            raise ValueError("Child memory ID must be a valid UUID")

    def remove_child_memory(self, child_id: str) -> bool:
        """Remove a child memory ID"""
        if child_id in self.child_memory_ids:
            self.child_memory_ids.remove(child_id)
            self.update_timestamp()
            return True
        return False

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class SearchQuery(BaseModel):
    """Search query for memory retrieval"""

    query: str = Field(
        ..., min_length=1, max_length=1000, description="Search query text"
    )
    scope: SearchScope = Field(default=SearchScope.ALL, description="Search scope")
    memory_types: list[MemoryType] = Field(
        default_factory=list, description="Filter by memory types"
    )
    categories: list[MemoryCategory] = Field(
        default_factory=list, description="Filter by categories"
    )
    priorities: list[MemoryPriority] = Field(
        default_factory=list, description="Filter by priorities"
    )
    tags: list[str] = Field(default_factory=list, description="Filter by tags")

    # Search parameters
    limit: int = Field(
        default=10, ge=1, le=100, description="Maximum results to return"
    )
    offset: int = Field(default=0, ge=0, description="Results offset for pagination")
    similarity_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum similarity score"
    )

    # Time filters
    created_after: datetime | None = Field(
        None, description="Filter by creation time"
    )
    created_before: datetime | None = Field(
        None, description="Filter by creation time"
    )
    updated_after: datetime | None = Field(None, description="Filter by update time")
    updated_before: datetime | None = Field(
        None, description="Filter by update time"
    )

    # Advanced filters
    include_expired: bool = Field(default=False, description="Include expired memories")
    include_archived: bool = Field(
        default=False, description="Include archived memories"
    )
    author_filter: str | None = Field(None, description="Filter by author")
    source_filter: str | None = Field(None, description="Filter by source")

    @validator("query")
    def validate_query(self, v: str) -> str:
        """Validate and normalize query"""
        query = v.strip()
        if not query:
            raise ValueError("Search query cannot be empty")
        return query

    @validator("tags")
    def validate_tags(self, v: list[str]) -> list[str]:
        """Validate and normalize tags"""
        return [tag.lower().strip() for tag in v if tag.strip()]

    @root_validator
    def validate_time_ranges(self, values: dict[str, Any]) -> dict[str, Any]:
        """Validate time range filters"""
        created_after = values.get("created_after")
        created_before = values.get("created_before")
        updated_after = values.get("updated_after")
        updated_before = values.get("updated_before")

        if created_after and created_before and created_after >= created_before:
            raise ValueError("created_after must be before created_before")

        if updated_after and updated_before and updated_after >= updated_before:
            raise ValueError("updated_after must be before updated_before")

        return values

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class SearchResult(BaseModel):
    """Search result with relevance scoring"""

    memory: MemoryRecord = Field(..., description="The memory record")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    similarity_score: float | None = Field(
        None, ge=0.0, le=1.0, description="Semantic similarity score"
    )
    match_type: str = Field(
        ..., description="Type of match (exact, semantic, metadata)"
    )
    match_details: dict[str, Any] = Field(
        default_factory=dict, description="Details about the match"
    )

    @validator("match_type")
    def validate_match_type(self, v: str) -> str:
        """Validate match type"""
        valid_types = {
            "exact",
            "semantic",
            "metadata",
            "tag",
            "category",
            "type",
            "hybrid",
        }
        if v not in valid_types:
            raise ValueError(f"Match type must be one of: {valid_types}")
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class MemoryOperationResult(BaseModel):
    """Result of memory operations"""

    success: bool = Field(..., description="Whether operation succeeded")
    operation: str = Field(..., description="Operation that was performed")
    memory_id: str | None = Field(None, description="ID of affected memory")
    message: str | None = Field(None, description="Result message")
    data: dict[str, Any] | None = Field(None, description="Additional result data")
    error_details: dict[str, Any] | None = Field(
        None, description="Error details if failed"
    )
    execution_time: float | None = Field(
        None, ge=0.0, description="Execution time in seconds"
    )

    @classmethod
    def success_result(
        cls,
        operation: str,
        memory_id: str | None = None,
        message: str | None = None,
        data: dict[str, Any] | None = None,
        execution_time: float | None = None,
    ) -> MemoryOperationResult:
        """Create a success result"""
        return cls(
            success=True,
            operation=operation,
            memory_id=memory_id,
            message=message,
            data=data,
            execution_time=execution_time,
        )

    @classmethod
    def error_result(
        cls,
        operation: str,
        message: str,
        memory_id: str | None = None,
        error_details: dict[str, Any] | None = None,
        execution_time: float | None = None,
    ) -> MemoryOperationResult:
        """Create an error result"""
        return cls(
            success=False,
            operation=operation,
            memory_id=memory_id,
            message=message,
            error_details=error_details,
            execution_time=execution_time,
        )


class MemoryBatch(BaseModel):
    """Batch of memory records for bulk operations"""

    memories: list[MemoryRecord] = Field(..., description="List of memory records")
    batch_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Batch identifier"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @validator("memories")
    def validate_memories(self, v: list[MemoryRecord]) -> list[MemoryRecord]:
        """Validate memory records in batch"""
        if not v:
            raise ValueError("Batch cannot be empty")

        if len(v) > 1000:
            raise ValueError("Batch size cannot exceed 1000 memories")

        # Check for duplicate IDs
        memory_ids = [memory.id for memory in v]
        if len(memory_ids) != len(set(memory_ids)):
            raise ValueError("Batch contains duplicate memory IDs")

        return v

    @property
    def size(self) -> int:
        """Get batch size"""
        return len(self.memories)

    def get_memory_by_id(self, memory_id: str) -> MemoryRecord | None:
        """Get memory by ID from batch"""
        for memory in self.memories:
            if memory.id == memory_id:
                return memory
        return None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
