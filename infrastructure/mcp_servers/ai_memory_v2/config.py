"""Configuration for ai_memory_v2 MCP server."""

import os

from pydantic import Field
from pydantic_settings import BaseSettings

# Import from shared config
try:
    from core.auto_esc_config import get_config_value
except ImportError:
    # Fallback if running standalone
    def get_config_value(key: str, default: str | None = None) -> str | None:
        return os.getenv(key.upper(), default)


class AiMemoryV2Settings(BaseSettings):
    """Settings for ai_memory_v2 MCP server."""

    # Server settings
    PORT: int = Field(default=9001, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Database settings
    DB_DSN: str = Field(
        default="postgresql+asyncpg://user:pass@localhost:5432/ai_memory",
        description="PostgreSQL connection string with pgvector",
        alias="AI_MEMORY_V2_DB_DSN",
    )
    DB_POOL_MIN: int = Field(default=1, description="Min DB pool size")
    DB_POOL_MAX: int = Field(default=5, description="Max DB pool size")

    # OpenAI settings for embeddings
    OPENAI_API_KEY: str = Field(
        default="", description="OpenAI API key for embeddings", alias="OPENAI_API_KEY"
    )
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002", description="OpenAI embedding model"
    )
    EMBEDDING_DIMENSION: int = Field(default=1536, description="Embedding vector size")

    # Memory settings
    DEFAULT_SEARCH_LIMIT: int = Field(default=10, description="Default search results")
    SIMILARITY_THRESHOLD: float = Field(default=0.7, description="Min similarity score")
    MAX_MEMORY_SIZE: int = Field(default=10000, description="Max characters per memory")

    # Feature flags
    ENABLE_AUTO_CATEGORIZATION: bool = Field(
        default=True, description="Auto-categorize memories"
    )
    ENABLE_DUPLICATE_DETECTION: bool = Field(
        default=True, description="Detect duplicate memories"
    )
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")

    # Redis Configuration
    REDIS_HOST: str = get_config_value("redis_host", "146.235.200.1")
    REDIS_PORT: int = int(get_config_value("redis_port", "6379"))
    REDIS_PASSWORD: str | None = get_config_value("redis_password") or os.getenv(
        "REDIS_PASSWORD"
    )

    # Snowflake Configuration (for future use)
    SNOWFLAKE_ACCOUNT: str | None = get_config_value("snowflake_account")
    SNOWFLAKE_DATABASE: str = "SOPHIA_AI"
    SNOWFLAKE_SCHEMA: str = "AI_MEMORY"

    # Memory Configuration
    DEFAULT_CACHE_TTL: int = 3600  # 1 hour
    MAX_SEARCH_RESULTS: int = 100

    # Feature Flags
    ENABLE_SNOWFLAKE_PERSISTENCE: bool = (
        get_config_value("enable_snowflake_persistence", "true").lower() == "true"
    )
    ENABLE_VECTOR_EMBEDDINGS: bool = (
        get_config_value("enable_vector_embeddings", "false").lower() == "true"
    )

    class Config:
        env_prefix = "AI_MEMORY_V2_"
        case_sensitive = True


settings = AiMemoryV2Settings()
