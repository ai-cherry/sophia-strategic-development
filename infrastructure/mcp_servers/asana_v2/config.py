"""Configuration for asana_v2 MCP server."""
from pydantic import Field
from pydantic_settings import BaseSettings


class Asana_V2Settings(BaseSettings):
    """Settings for asana_v2 MCP server."""

    PORT: int = Field(default=9004, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "ASANA_V2_"

settings = Asana_V2Settings()
