"""
AI Memory MCP Server - Core Module
Consolidated and optimized implementation following enterprise patterns
"""

from .config import AIMemoryConfig
from .exceptions import (
    MemoryEmbeddingError,
    MemoryError,
    MemoryNotFoundError,
    MemoryStorageError,
    MemoryValidationError,
)
from .handlers import (
    MemoryEmbeddingHandler,
    MemorySearchHandler,
    MemoryStorageHandler,
    MemoryValidationHandler,
)
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
from .storage import (
    MemoryStorageInterface,
    RedisMemoryCache,
    SnowflakeMemoryStorage,
    VectorMemoryStore,
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
