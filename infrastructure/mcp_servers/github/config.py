"""Configuration for github MCP server."""
from pydantic_settings import BaseSettings
from pydantic import Field

class GithubSettings(BaseSettings):
    """Settings for github MCP server."""
    
    PORT: int = Field(default=9001, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_prefix = "GITHUB_"

settings = GithubSettings()
