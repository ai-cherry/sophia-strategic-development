"""
Lambda GPU Service - Models Module
Contains all data models, enums, and type definitions
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


# Custom Exception Classes
class CortexEmbeddingError(Exception):
    """Raised when Lambda GPU embedding generation fails"""

    pass


class InsufficientPermissionsError(Exception):
    """Raised when user lacks required ModernStack permissions"""

    pass


class BusinessTableNotFoundError(Exception):
    """Raised when business table doesn't exist or is not accessible"""

    pass


class InvalidInputError(Exception):
    """Raised when input parameters are invalid"""

    pass


class CortexModel(Enum):
    """Available Lambda GPU models"""

    # Text generation models
    LLAMA2_70B = "llama2-70b-chat"
    MISTRAL_7B = "mistral-7b"
    MISTRAL_LARGE = "mistral-large"
    MIXTRAL_8X7B = "mixtral-8x7b"

    # Embedding models
    E5_BASE_V2 = "e5-base-v2"
    MULTILINGUAL_E5_LARGE = "multilingual-e5-large"

    # Analysis models
    SENTIMENT_ANALYSIS = "sentiment"
    SUMMARIZATION = "summarize"


@dataclass
class CortexQuery:
    """Configuration for Cortex AI queries"""

    model: CortexModel
    input_text: str
    parameters: dict[str, Any] | None = None
    context: str | None = None
    max_tokens: int | None = None


@dataclass
class VectorSearchResult:
    """Result from vector similarity search"""

    content: str
    similarity_score: float
    metadata: dict[str, Any]
    source_table: str
    source_id: str


@dataclass
class CortexOperation:
    """Represents a Cortex AI operation with metadata"""

    operation_type: str
    input_text: str
    model: str
    parameters: dict[str, Any] | None = None
    result: Any | None = None
    processing_time: float | None = None
    error: str | None = None


@dataclass
class ProcessingMode:
    """Configuration for processing modes"""

    batch_size: int = 100
    concurrent_operations: int = 5
    retry_attempts: int = 3
    timeout_seconds: int = 30


@dataclass
class CortexResult:
    """Standard result format for Cortex operations"""

    success: bool
    data: Any | None = None
    error_message: str | None = None
    processing_time: float | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class CortexConfig:
    """Configuration for Cortex service"""

    database: str
    schema: str
    warehouse: str
    default_model: str = "e5-base-v2"
    max_batch_size: int = 1000
    connection_timeout: int = 30


@dataclass
class CortexPerformanceMetrics:
    """Performance metrics for Cortex operations"""

    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_processing_time: float = 0.0
    total_processing_time: float = 0.0
    operations_per_second: float = 0.0
