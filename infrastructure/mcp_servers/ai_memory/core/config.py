"""
AI Memory Configuration Management
Centralized configuration with validation and environment support
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, validator


class AIMemoryConfig(BaseSettings):
    """Centralized configuration for AI Memory MCP server"""

    # Server Configuration
    server_name: str = Field(default="ai_memory", env="AI_MEMORY_SERVER_NAME")
    server_port: int = Field(
        default=9001, env="AI_MEMORY_SERVER_PORT", ge=1024, le=65535
    )
    debug_mode: bool = Field(default=False, env="AI_MEMORY_DEBUG")
    log_level: str = Field(default="INFO", env="AI_MEMORY_LOG_LEVEL")

    # Storage Configuration
    snowflake_account: str = Field(..., env="SNOWFLAKE_ACCOUNT")
    snowflake_user: str = Field(..., env="SNOWFLAKE_USER")
    snowflake_password: str = Field(..., env="SNOWFLAKE_PASSWORD")
    snowflake_database: str = Field(default="SOPHIA_AI", env="SNOWFLAKE_DATABASE")
    snowflake_schema: str = Field(default="AI_MEMORY", env="SNOWFLAKE_SCHEMA")
    snowflake_warehouse: str = Field(default="COMPUTE_WH", env="SNOWFLAKE_WAREHOUSE")

    # Redis Configuration
    redis_url: str = Field(..., env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB", ge=0, le=15)
    redis_max_connections: int = Field(
        default=20, env="REDIS_MAX_CONNECTIONS", ge=1, le=100
    )

    # Vector Store Configuration
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: str = Field(
        default="us-west1-gcp", env="PINECONE_ENVIRONMENT"
    )
    pinecone_index_name: str = Field(
        default="sophia-ai-memory", env="PINECONE_INDEX_NAME"
    )

    weaviate_url: Optional[str] = Field(default=None, env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")

    # AI/ML Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    embedding_model: str = Field(
        default="text-embedding-3-small", env="EMBEDDING_MODEL"
    )
    embedding_dimensions: int = Field(
        default=1536, env="EMBEDDING_DIMENSIONS", ge=512, le=3072
    )

    # Performance Configuration
    embedding_cache_ttl: int = Field(
        default=3600, env="EMBEDDING_CACHE_TTL", ge=60, le=86400
    )
    max_concurrent_operations: int = Field(
        default=10, env="MAX_CONCURRENT_OPS", ge=1, le=100
    )
    vector_similarity_threshold: float = Field(
        default=0.7, env="SIMILARITY_THRESHOLD", ge=0.0, le=1.0
    )
    memory_cleanup_interval: int = Field(
        default=3600, env="CLEANUP_INTERVAL", ge=300, le=86400
    )

    # Search Configuration
    default_search_limit: int = Field(
        default=10, env="DEFAULT_SEARCH_LIMIT", ge=1, le=100
    )
    max_search_limit: int = Field(default=100, env="MAX_SEARCH_LIMIT", ge=1, le=1000)
    search_timeout: int = Field(default=30, env="SEARCH_TIMEOUT", ge=1, le=300)

    # Feature Flags
    enable_advanced_caching: bool = Field(default=True, env="ENABLE_ADVANCED_CACHING")
    enable_metrics_collection: bool = Field(default=True, env="ENABLE_METRICS")
    enable_auto_cleanup: bool = Field(default=True, env="ENABLE_AUTO_CLEANUP")
    enable_embedding_optimization: bool = Field(
        default=True, env="ENABLE_EMBEDDING_OPT"
    )
    enable_async_processing: bool = Field(default=True, env="ENABLE_ASYNC_PROCESSING")

    # Security Configuration
    api_key_required: bool = Field(default=True, env="API_KEY_REQUIRED")
    allowed_origins: list[str] = Field(default_factory=list, env="ALLOWED_ORIGINS")
    rate_limit_requests: int = Field(default=1000, env="RATE_LIMIT_REQUESTS", ge=1)
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW", ge=60)

    # Monitoring Configuration
    enable_health_checks: bool = Field(default=True, env="ENABLE_HEALTH_CHECKS")
    health_check_interval: int = Field(
        default=60, env="HEALTH_CHECK_INTERVAL", ge=10, le=300
    )
    metrics_export_interval: int = Field(
        default=60, env="METRICS_EXPORT_INTERVAL", ge=10, le=300
    )

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @validator("embedding_model")
    def validate_embedding_model(cls, v: str) -> str:
        """Validate embedding model"""
        valid_models = {
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002",
        }
        if v not in valid_models:
            raise ValueError(f"Embedding model must be one of: {valid_models}")
        return v

    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v) -> list[str]:
        """Parse allowed origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v or []

    @property
    def snowflake_connection_params(self) -> dict[str, Any]:
        """Get Snowflake connection parameters"""
        return {
            "account": self.snowflake_account,
            "user": self.snowflake_user,
            "password": self.snowflake_password,
            "database": self.snowflake_database,
            "schema": self.snowflake_schema,
            "warehouse": self.snowflake_warehouse,
        }

    @property
    def redis_connection_params(self) -> dict[str, Any]:
        """Get Redis connection parameters"""
        params = {
            "url": self.redis_url,
            "db": self.redis_db,
            "max_connections": self.redis_max_connections,
        }
        if self.redis_password:
            params["password"] = self.redis_password
        return params

    @property
    def pinecone_connection_params(self) -> dict[str, Any]:
        """Get Pinecone connection parameters"""
        return {
            "api_key": self.pinecone_api_key,
            "environment": self.pinecone_environment,
            "index_name": self.pinecone_index_name,
        }

    def get_cache_config(self) -> dict[str, Any]:
        """Get caching configuration"""
        return {
            "embedding_ttl": self.embedding_cache_ttl,
            "enable_advanced": self.enable_advanced_caching,
            "cleanup_interval": self.memory_cleanup_interval,
        }

    def get_performance_config(self) -> dict[str, Any]:
        """Get performance configuration"""
        return {
            "max_concurrent": self.max_concurrent_operations,
            "similarity_threshold": self.vector_similarity_threshold,
            "search_timeout": self.search_timeout,
            "enable_async": self.enable_async_processing,
        }

    def get_security_config(self) -> dict[str, Any]:
        """Get security configuration"""
        return {
            "api_key_required": self.api_key_required,
            "allowed_origins": self.allowed_origins,
            "rate_limit": {
                "requests": self.rate_limit_requests,
                "window": self.rate_limit_window,
            },
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True
        extra = "forbid"


# Global configuration instance
config = AIMemoryConfig()


def get_config() -> AIMemoryConfig:
    """Get the global configuration instance"""
    return config


def reload_config() -> AIMemoryConfig:
    """Reload configuration from environment"""
    global config
    config = AIMemoryConfig()
    return config
