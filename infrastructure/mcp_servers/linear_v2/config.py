"""Configuration for linear_v2 MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Linear_V2Settings(BaseSettings):
    """Settings for linear_v2 MCP server."""

    PORT: int = Field(default=9002, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "LINEAR_V2_"


settings = Linear_V2Settings()
