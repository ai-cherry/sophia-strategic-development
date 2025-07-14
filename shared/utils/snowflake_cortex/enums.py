"""Enums for Lambda GPU service."""

from backend.services.unified_memory_service_primary import UnifiedMemoryService
from enum import Enum


class CortexModel(str, Enum):
    """Available Cortex AI models."""

    # Text generation models
    MIXTRAL_8X7B = "mixtral-8x7b"
    MISTRAL_7B = "mistral-7b"
    MISTRAL_LARGE = "mistral-large"
    LLAMA2_70B = "llama2-70b"
    LLAMA3_8B = "llama3-8b"
    LLAMA3_70B = "llama3-70b"
    GEMMA_7B = "gemma-7b"

    # Embedding models
    E5_BASE_V2 = "e5-base-v2"
    

    # Specialized models
    MIXTRAL_7B_INSTRUCT = "mixtral-7b-instruct"


class TaskType(str, Enum):
    """Task types for routing and optimization."""

    SQL_GENERATION = "sql_generation"
    DATA_ANALYSIS = "data_analysis"
    EMBEDDING = "embedding"
    COMPLETION = "completion"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SEARCH = "search"


class MCPMode(str, Enum):
    """Cortex adapter operation modes."""

    DIRECT = "direct"  # Direct SQL execution
    MCP = "mcp"  # Via MCP server
    AUTO = "auto"  # Auto-detect based on availability


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
