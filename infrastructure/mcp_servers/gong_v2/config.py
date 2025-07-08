"""Configuration for gong_v2 MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings


class GongV2Settings(BaseSettings):
    """Settings for gong_v2 MCP server."""

    # Server settings
    PORT: int = Field(default=9009, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Gong API credentials (from Pulumi ESC)
    GONG_API_KEY: str = Field(default="", description="Gong API key")
    GONG_API_SECRET: str = Field(default="", description="Gong API secret")

    # Optional webhook secret
    GONG_WEBHOOK_SECRET: str = Field(default="", description="Gong webhook secret")

    # Cache settings
    CACHE_TTL_MINUTES: int = Field(default=15, description="Cache TTL in minutes")

    # Rate limiting
    RATE_LIMIT_CALLS_PER_MINUTE: int = Field(default=60, description="API rate limit")

    class Config:
        env_prefix = "GONG_V2_"
        # Also check without prefix for Pulumi ESC
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check for Pulumi ESC environment variables without prefix
        if not self.GONG_API_KEY:
            self.GONG_API_KEY = get_config_value("gong_api_key", "")
        if not self.GONG_API_SECRET:
            self.GONG_API_SECRET = get_config_value("gong_api_secret", "")


settings = GongV2Settings()
