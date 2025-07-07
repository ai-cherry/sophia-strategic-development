"""Configuration for perplexity_v2 MCP server."""
from pydantic_settings import BaseSettings
from pydantic import Field

class Perplexity_V2Settings(BaseSettings):
    """Settings for perplexity_v2 MCP server."""

    PORT: int = Field(default=9008, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "PERPLEXITY_V2_"

settings = Perplexity_V2Settings()
