"""
AI Memory MCP Server Models - Task 4 Implementation
Systematic Refactoring Project

Following research-backed patterns:
- Clean Architecture with Repository pattern
- Domain-driven design with rich models
- Type safety with comprehensive validation
- Business logic encapsulation
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field, validator


class MemoryType(Enum):
    """Types of memory records"""
    CONVERSATION = "conversation"
    CODE_PATTERN = "code_pattern"
    BUSINESS_INSIGHT = "business_insight"
    TECHNICAL_DECISION = "technical_decision"
    PROJECT_CONTEXT = "project_context"
    USER_PREFERENCE = "user_preference"
    SYSTEM_STATE = "system_state"
    ERROR_PATTERN = "error_pattern"
    PERFORMANCE_METRIC = "performance_metric"
    SECURITY_EVENT = "security_event"


class MemoryCategory(Enum):
    """Memory categorization for organization"""
    # Development Categories
    ARCHITECTURE = "architecture"
    DEBUGGING = "debugging"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    
    # Business Categories
    SALES = "sales"
    MARKETING = "marketing"
    CUSTOMER_SUCCESS = "customer_success"
    PRODUCT = "product"
    STRATEGY = "strategy"
    
    # Technical Categories
    INFRASTRUCTURE = "infrastructure"
    DATABASE = "database"
    API = "api"
    FRONTEND = "frontend"
    BACKEND = "backend"
    
    # Operational Categories
    MONITORING = "monitoring"
    ALERTS = "alerts"
    INCIDENTS = "incidents"
    MAINTENANCE = "maintenance"
    
    # AI/ML Categories
    MODELS = "models"
    TRAINING = "training"
    INFERENCE = "inference"
    DATA_PIPELINE = "data_pipeline"


class MemoryPriority(Enum):
    """Priority levels for memory importance"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ARCHIVE = "archive"


class MemoryStatus(Enum):
    """Status of memory records"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"
    PENDING_REVIEW = "pending_review"
    FLAGGED = "flagged"


class SearchScope(Enum):
    """Scope for memory searches"""
    ALL = "all"
    RECENT = "recent"
    CATEGORY = "category"
    TYPE = "type"
    PRIORITY = "priority"
    SEMANTIC = "semantic"
    CONTEXTUAL = "contextual"


@dataclass
class MemoryMetadata:
    """Rich metadata for memory records"""
    source: str = "unknown"
    confidence_score: float = 1.0
    relevance_score: float = 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    related_memory_ids: List[str] = field(default_factory=list)
    context_window: Dict[str, Any] = field(default_factory=dict)
    validation_status: str = "unvalidated"
    business_impact: Optional[str] = None
    technical_complexity: Optional[str] = None
    
    def update_access(self):
        """Update access tracking"""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def add_tag(self, tag: str):
        """Add a tag if not already present"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def link_memory(self, memory_id: str):
        """Link to another memory record"""
        if memory_id not in self.related_memory_ids:
            self.related_memory_ids.append(memory_id)


@dataclass
class MemoryEmbedding:
    """Vector embedding for semantic search"""
    vector: List[float]
    model: str = "text-embedding-ada-002"
    dimensions: int = 1536
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate embedding after initialization"""
        if len(self.vector) != self.dimensions:
            raise ValueError(f"Vector dimensions mismatch: {len(self.vector)} != {self.dimensions}")
    
    @property
    def numpy_vector(self) -> np.ndarray:
        """Get vector as numpy array for calculations"""
        return np.array(self.vector)
    
    def cosine_similarity(self, other: MemoryEmbedding) -> float:
        """Calculate cosine similarity with another embedding"""
        if self.dimensions != other.dimensions:
            raise ValueError("Cannot compare embeddings with different dimensions")
        
        vec_a = self.numpy_vector
        vec_b = other.numpy_vector
        
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


class MemoryRecord(BaseModel):
    """Core memory record with comprehensive validation"""
    
    # Core Fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., min_length=1, max_length=50000)
    summary: Optional[str] = Field(None, max_length=500)
    
    # Classification
    memory_type: MemoryType
    category: MemoryCategory
    priority: MemoryPriority = MemoryPriority.MEDIUM
    status: MemoryStatus = MemoryStatus.ACTIVE
    
    # Temporal
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Context
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Relationships
    parent_id: Optional[str] = None
    thread_id: Optional[str] = None
    
    # Search and AI
    embedding: Optional[MemoryEmbedding] = None
    keywords: List[str] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @validator('content')
    def validate_content(cls, v):
        """Validate content is meaningful"""
        if not v or v.isspace():
            raise ValueError("Content cannot be empty or whitespace only")
        return v.strip()
    
    @validator('expires_at')
    def validate_expiration(cls, v, values):
        """Validate expiration is in the future"""
        if v and v <= datetime.now():
            raise ValueError("Expiration date must be in the future")
        return v
    
    @validator('priority')
    def validate_priority_context(cls, v, values):
        """Validate priority matches context"""
        # Critical memories should have business impact
        if v == MemoryPriority.CRITICAL:
            metadata = values.get('metadata', {})
            if not metadata.get('business_impact'):
                raise ValueError("Critical memories must specify business impact")
        return v
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if memory has expired"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def is_recent(self, days: int = 7) -> bool:
        """Check if memory is recent"""
        cutoff = datetime.now() - timedelta(days=days)
        return self.created_at > cutoff
    
    def add_keyword(self, keyword: str):
        """Add a keyword for search"""
        keyword = keyword.lower().strip()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.update_timestamp()
    
    def set_embedding(self, vector: List[float], model: str = "text-embedding-ada-002"):
        """Set the embedding vector"""
        self.embedding = MemoryEmbedding(
            vector=vector,
            model=model,
            dimensions=len(vector)
        )
        self.update_timestamp()
    
    def calculate_relevance_score(self, query_context: Dict[str, Any]) -> float:
        """Calculate relevance score based on context"""
        score = 0.0
        
        # Base score from priority
        priority_scores = {
            MemoryPriority.CRITICAL: 1.0,
            MemoryPriority.HIGH: 0.8,
            MemoryPriority.MEDIUM: 0.6,
            MemoryPriority.LOW: 0.4,
            MemoryPriority.ARCHIVE: 0.2
        }
        score += priority_scores.get(self.priority, 0.5) * 0.3
        
        # Recency bonus
        if self.is_recent(days=7):
            score += 0.2
        elif self.is_recent(days=30):
            score += 0.1
        
        # Category match
        if query_context.get('category') == self.category:
            score += 0.3
        
        # Type match
        if query_context.get('memory_type') == self.memory_type:
            score += 0.2
        
        # Keyword overlap
        query_keywords = query_context.get('keywords', [])
        if query_keywords:
            overlap = len(set(self.keywords) & set(query_keywords))
            score += (overlap / len(query_keywords)) * 0.2
        
        return min(score, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = self.dict()
        
        # Handle datetime serialization
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        if self.expires_at:
            result['expires_at'] = self.expires_at.isoformat()
        
        # Handle embedding serialization
        if self.embedding:
            result['embedding'] = {
                'vector': self.embedding.vector,
                'model': self.embedding.model,
                'dimensions': self.embedding.dimensions,
                'created_at': self.embedding.created_at.isoformat()
            }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryRecord:
        """Create from dictionary"""
        # Handle datetime deserialization
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if isinstance(data.get('expires_at'), str):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        # Handle embedding deserialization
        if data.get('embedding'):
            embedding_data = data['embedding']
            if isinstance(embedding_data.get('created_at'), str):
                embedding_data['created_at'] = datetime.fromisoformat(embedding_data['created_at'])
            data['embedding'] = MemoryEmbedding(**embedding_data)
        
        return cls(**data)


@dataclass
class SearchQuery:
    """Structured search query for memory retrieval"""
    text: str
    scope: SearchScope = SearchScope.ALL
    category: Optional[MemoryCategory] = None
    memory_type: Optional[MemoryType] = None
    priority: Optional[MemoryPriority] = None
    limit: int = 10
    similarity_threshold: float = 0.7
    include_expired: bool = False
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_filter_dict(self) -> Dict[str, Any]:
        """Convert to filter dictionary for database queries"""
        filters = {}
        
        if self.category:
            filters['category'] = self.category.value
        if self.memory_type:
            filters['memory_type'] = self.memory_type.value
        if self.priority:
            filters['priority'] = self.priority.value
        if not self.include_expired:
            filters['not_expired'] = True
        
        return filters


@dataclass
class SearchResult:
    """Search result with relevance scoring"""
    memory: MemoryRecord
    relevance_score: float
    similarity_score: Optional[float] = None
    match_reasons: List[str] = field(default_factory=list)
    
    def __lt__(self, other):
        """Enable sorting by relevance score"""
        return self.relevance_score < other.relevance_score


@dataclass
class MemoryStats:
    """Statistics about memory collection"""
    total_memories: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    by_type: Dict[str, int] = field(default_factory=dict)
    by_priority: Dict[str, int] = field(default_factory=dict)
    by_status: Dict[str, int] = field(default_factory=dict)
    recent_count: int = 0
    expired_count: int = 0
    avg_relevance_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class MemoryValidationError(Exception):
    """Custom exception for memory validation errors"""
    pass


class MemoryNotFoundError(Exception):
    """Custom exception for memory not found errors"""
    pass


class MemoryStorageError(Exception):
    """Custom exception for memory storage errors"""
    pass


# Factory functions for common memory types
def create_conversation_memory(
    content: str,
    participants: List[str],
    topic: Optional[str] = None,
    **kwargs
) -> MemoryRecord:
    """Create a conversation memory record"""
    context = {
        "participants": participants,
        "topic": topic or "General Discussion"
    }
    context.update(kwargs.get('context', {}))
    
    return MemoryRecord(
        content=content,
        memory_type=MemoryType.CONVERSATION,
        category=MemoryCategory.STRATEGY,  # Default, can be overridden
        context=context,
        **{k: v for k, v in kwargs.items() if k != 'context'}
    )


def create_code_pattern_memory(
    content: str,
    language: str,
    pattern_type: str,
    complexity: str = "medium",
    **kwargs
) -> MemoryRecord:
    """Create a code pattern memory record"""
    context = {
        "language": language,
        "pattern_type": pattern_type,
        "complexity": complexity
    }
    context.update(kwargs.get('context', {}))
    
    return MemoryRecord(
        content=content,
        memory_type=MemoryType.CODE_PATTERN,
        category=MemoryCategory.ARCHITECTURE,
        context=context,
        **{k: v for k, v in kwargs.items() if k != 'context'}
    )


def create_business_insight_memory(
    content: str,
    impact: str,
    stakeholders: List[str],
    metrics: Optional[Dict[str, Any]] = None,
    **kwargs
) -> MemoryRecord:
    """Create a business insight memory record"""
    context = {
        "impact": impact,
        "stakeholders": stakeholders,
        "metrics": metrics or {}
    }
    context.update(kwargs.get('context', {}))
    
    return MemoryRecord(
        content=content,
        memory_type=MemoryType.BUSINESS_INSIGHT,
        category=MemoryCategory.STRATEGY,
        priority=MemoryPriority.HIGH,
        context=context,
        **{k: v for k, v in kwargs.items() if k != 'context'}
    )


def create_technical_decision_memory(
    content: str,
    decision_type: str,
    rationale: str,
    alternatives: List[str],
    **kwargs
) -> MemoryRecord:
    """Create a technical decision memory record"""
    context = {
        "decision_type": decision_type,
        "rationale": rationale,
        "alternatives": alternatives
    }
    context.update(kwargs.get('context', {}))
    
    return MemoryRecord(
        content=content,
        memory_type=MemoryType.TECHNICAL_DECISION,
        category=MemoryCategory.ARCHITECTURE,
        priority=MemoryPriority.HIGH,
        context=context,
        **{k: v for k, v in kwargs.items() if k != 'context'}
    )


# Utility functions
def categorize_content_automatically(content: str) -> MemoryCategory:
    """Automatically categorize content based on keywords"""
    content_lower = content.lower()
    
    # Technical categories
    if any(word in content_lower for word in ['database', 'sql', 'query', 'schema']):
        return MemoryCategory.DATABASE
    elif any(word in content_lower for word in ['api', 'endpoint', 'rest', 'graphql']):
        return MemoryCategory.API
    elif any(word in content_lower for word in ['frontend', 'ui', 'react', 'vue', 'angular']):
        return MemoryCategory.FRONTEND
    elif any(word in content_lower for word in ['backend', 'server', 'microservice']):
        return MemoryCategory.BACKEND
    elif any(word in content_lower for word in ['deploy', 'deployment', 'ci/cd', 'pipeline']):
        return MemoryCategory.DEPLOYMENT
    elif any(word in content_lower for word in ['test', 'testing', 'unit test', 'integration']):
        return MemoryCategory.TESTING
    elif any(word in content_lower for word in ['security', 'auth', 'encryption', 'vulnerability']):
        return MemoryCategory.SECURITY
    elif any(word in content_lower for word in ['performance', 'optimization', 'speed', 'latency']):
        return MemoryCategory.PERFORMANCE
    
    # Business categories
    elif any(word in content_lower for word in ['sales', 'lead', 'prospect', 'deal']):
        return MemoryCategory.SALES
    elif any(word in content_lower for word in ['marketing', 'campaign', 'brand', 'promotion']):
        return MemoryCategory.MARKETING
    elif any(word in content_lower for word in ['customer', 'support', 'satisfaction', 'feedback']):
        return MemoryCategory.CUSTOMER_SUCCESS
    elif any(word in content_lower for word in ['product', 'feature', 'roadmap', 'requirement']):
        return MemoryCategory.PRODUCT
    elif any(word in content_lower for word in ['strategy', 'vision', 'goal', 'objective']):
        return MemoryCategory.STRATEGY
    
    # Default to architecture for technical content
    return MemoryCategory.ARCHITECTURE


def extract_keywords_from_content(content: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from content using simple NLP"""
    import re
    
    # Simple keyword extraction (in production, use proper NLP)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'was', 'were', 'been', 'have', 'has', 'had', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'did', 'does', 'do'
    }
    
    # Filter and count words
    word_counts = {}
    for word in words:
        if word not in stop_words and len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Return top keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]] 