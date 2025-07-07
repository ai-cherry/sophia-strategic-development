"""
AI Memory MCP Server - Core Module
Consolidated and optimized implementation following enterprise patterns
"""

from .config import AIMemoryConfig
from .models import (
    MemoryCategory,
    MemoryEmbedding,
    MemoryMetadata,
    MemoryPriority,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    SearchQuery,
    SearchResult,
    SearchScope,
)
from .handlers import (
    MemoryStorageHandler,
    MemorySearchHandler,
    MemoryValidationHandler,
    MemoryEmbeddingHandler,
)
from .storage import (
    MemoryStorageInterface,
    SnowflakeMemoryStorage,
    RedisMemoryCache,
    VectorMemoryStore,
)
from .exceptions import (
    MemoryError,
    MemoryNotFoundError,
    MemoryStorageError,
    MemoryValidationError,
    MemoryEmbeddingError,
)

__version__ = "2.0.0"
__all__ = [
    # Configuration
    "AIMemoryConfig",
    
    # Models
    "MemoryCategory",
    "MemoryEmbedding", 
    "MemoryMetadata",
    "MemoryPriority",
    "MemoryRecord",
    "MemoryStatus",
    "MemoryType",
    "SearchQuery",
    "SearchResult",
    "SearchScope",
    
    # Handlers
    "MemoryStorageHandler",
    "MemorySearchHandler",
    "MemoryValidationHandler",
    "MemoryEmbeddingHandler",
    
    # Storage
    "MemoryStorageInterface",
    "SnowflakeMemoryStorage",
    "RedisMemoryCache",
    "VectorMemoryStore",
    
    # Exceptions
    "MemoryError",
    "MemoryNotFoundError",
    "MemoryStorageError",
    "MemoryValidationError",
    "MemoryEmbeddingError",
]

