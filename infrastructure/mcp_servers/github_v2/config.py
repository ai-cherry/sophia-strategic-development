"""Configuration for github_v2 MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Github_V2Settings(BaseSettings):
    """Settings for github_v2 MCP server."""

    PORT: int = Field(default=9006, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "GITHUB_V2_"


settings = Github_V2Settings()
