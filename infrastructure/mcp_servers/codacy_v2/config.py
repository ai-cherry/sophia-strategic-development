"""Configuration for codacy_v2 MCP server."""
from pydantic_settings import BaseSettings
from pydantic import Field

class Codacy_V2Settings(BaseSettings):
    """Settings for codacy_v2 MCP server."""

    PORT: int = Field(default=9005, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "CODACY_V2_"

settings = Codacy_V2Settings()
