"""
Configuration for Snowflake V2 MCP Server
"""

import os

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    """Configuration settings for Snowflake V2 MCP Server"""

    # Server Configuration
    SERVICE_NAME: str = "snowflake_v2"
    PORT: int = Field(default=9001, env="SNOWFLAKE_V2_PORT")
    HOST: str = Field(default="0.0.0.0", env="SNOWFLAKE_V2_HOST")

    # Snowflake Connection (from Pulumi ESC)
    SNOWFLAKE_ACCOUNT: str = Field(..., env="SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER: str = Field(..., env="SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD: str = Field(..., env="SNOWFLAKE_PASSWORD")
    SNOWFLAKE_ROLE: str = Field(default="ACCOUNTADMIN", env="SNOWFLAKE_ROLE")
    SNOWFLAKE_WAREHOUSE: str = Field(
        default="SOPHIA_AI_COMPUTE_WH", env="SNOWFLAKE_WAREHOUSE"
    )
    SNOWFLAKE_DATABASE: str = Field(
        default="SOPHIA_AI_PRODUCTION", env="SNOWFLAKE_DATABASE"
    )
    SNOWFLAKE_SCHEMA: str = Field(default="PUBLIC", env="SNOWFLAKE_SCHEMA")

    # AI Configuration
    EMBEDDING_MODEL: str = Field(
        default="snowflake-arctic-embed-m-v2.0", env="EMBEDDING_MODEL"
    )
    EMBEDDING_DIMENSION: int = Field(default=768, env="EMBEDDING_DIMENSION")

    # Performance Settings
    QUERY_TIMEOUT: int = Field(default=300, env="QUERY_TIMEOUT")
    MAX_BATCH_SIZE: int = Field(default=1000, env="MAX_BATCH_SIZE")
    CONNECTION_POOL_SIZE: int = Field(default=5, env="CONNECTION_POOL_SIZE")

    # Feature Flags
    ENABLE_CORTEX: bool = Field(default=True, env="ENABLE_CORTEX")
    ENABLE_CACHING: bool = Field(default=True, env="ENABLE_CACHING")
    ENABLE_MONITORING: bool = Field(default=True, env="ENABLE_MONITORING")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables"""
        # Try to load from Pulumi ESC first
        try:
            from backend.core.auto_esc_config import get_config_value

            snowflake_config = {
                "SNOWFLAKE_ACCOUNT": get_config_value("snowflake_account"),
                "SNOWFLAKE_USER": get_config_value("snowflake_user"),
                "SNOWFLAKE_PASSWORD": get_config_value("snowflake_password"),
                "SNOWFLAKE_DATABASE": get_config_value(
                    "snowflake_database", "SOPHIA_AI_PRODUCTION"
                ),
                "SNOWFLAKE_WAREHOUSE": get_config_value(
                    "snowflake_warehouse", "SOPHIA_AI_COMPUTE_WH"
                ),
            }

            # Update environment with ESC values
            for key, value in snowflake_config.items():
                if value:
                    os.environ[key] = value

        except ImportError:
            # Fall back to environment variables
            pass

        return cls()
