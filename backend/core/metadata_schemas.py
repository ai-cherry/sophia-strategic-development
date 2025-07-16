"""
Standardized Metadata Schemas for Sophia AI
Provides consistent metadata structure across all components
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class DataSource(Enum):
    """Standardized data sources"""
    GONG = "gong"
    HUBSPOT = "hubspot"
    SLACK = "slack"
    LINEAR = "linear"
    NOTION = "notion"
    ASANA = "asana"
    USER_INPUT = "user_input"
    SYSTEM = "system"

class ContentType(Enum):
    """Standardized content types"""
    TEXT = "text"
    DOCUMENT = "document"
    CALL_TRANSCRIPT = "call_transcript"
    EMAIL = "email"
    CHAT_MESSAGE = "chat_message"
    TASK = "task"
    PROJECT = "project"
    CONTACT = "contact"

@dataclass
class StandardMetadata:
    """Standardized metadata schema for all content"""
    # Core identification
    id: str
    source: DataSource
    content_type: ContentType
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    # Content classification
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    # Business context
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Quality metrics
    confidence_score: Optional[float] = None
    relevance_score: Optional[float] = None
    quality_score: Optional[float] = None
    
    # Processing metadata
    embedding_model: Optional[str] = None
    processing_version: str = "1.0"
    sophia_ai_version: str = "2025.07"
    
    # Custom fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "source": self.source.value,
            "content_type": self.content_type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "category": self.category,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "project_id": self.project_id,
            "confidence_score": self.confidence_score,
            "relevance_score": self.relevance_score,
            "quality_score": self.quality_score,
            "embedding_model": self.embedding_model,
            "processing_version": self.processing_version,
            "sophia_ai_version": self.sophia_ai_version,
            "custom_fields": self.custom_fields
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StandardMetadata":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            source=DataSource(data["source"]),
            content_type=ContentType(data["content_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            processed_at=datetime.fromisoformat(data["processed_at"]) if data.get("processed_at") else None,
            title=data.get("title"),
            description=data.get("description"),
            tags=data.get("tags", []),
            category=data.get("category"),
            user_id=data.get("user_id"),
            organization_id=data.get("organization_id"),
            project_id=data.get("project_id"),
            confidence_score=data.get("confidence_score"),
            relevance_score=data.get("relevance_score"),
            quality_score=data.get("quality_score"),
            embedding_model=data.get("embedding_model"),
            processing_version=data.get("processing_version", "1.0"),
            sophia_ai_version=data.get("sophia_ai_version", "2025.07"),
            custom_fields=data.get("custom_fields", {})
        )

def create_standard_metadata(
    content_id: str,
    source: DataSource,
    content_type: ContentType,
    **kwargs
) -> StandardMetadata:
    """Create standardized metadata with defaults"""
    return StandardMetadata(
        id=content_id,
        source=source,
        content_type=content_type,
        **kwargs
    )
