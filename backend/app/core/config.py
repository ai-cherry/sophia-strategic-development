"""
Unified configuration for Sophia AI platform
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Sophia AI Platform"
    app_version: str = "3.0.0"
    debug: bool = False
    environment: str = "production"
    
    # API
    api_v3_prefix: str = "/api/v3"
    api_mcp_prefix: str = "/api/mcp"
    api_admin_prefix: str = "/api/admin"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # MCP Configuration
    mcp_config_path: str = "config/cursor_enhanced_mcp_config.json"
    mcp_health_check_interval: int = 60
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
