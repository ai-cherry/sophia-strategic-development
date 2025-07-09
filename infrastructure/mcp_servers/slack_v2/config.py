"""Configuration for slack_v2 MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Slack_V2Settings(BaseSettings):
    """Settings for slack_v2 MCP server."""

    PORT: int = Field(default=9007, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "SLACK_V2_"


settings = Slack_V2Settings()
