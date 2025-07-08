"""Configuration for notion_v2 MCP server."""
from pydantic import Field
from pydantic_settings import BaseSettings


class Notion_V2Settings(BaseSettings):
    """Settings for notion_v2 MCP server."""

    PORT: int = Field(default=9003, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "NOTION_V2_"

settings = Notion_V2Settings()
