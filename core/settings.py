"""
Enhanced Settings for Sophia AI Platform - 2025 Best Practices
"""

from backend.services.unified_memory_service import UnifiedMemoryService
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Modern settings with Pydantic v2"""

    # Application
    app_name: str = "Sophia AI Platform"
    app_version: str = "3.0.0"
    environment: str = "production"
    debug: bool = False

    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    allowed_origins: list[str] = ["*"]

    # Database
    database_url: str = "sqlite:///./sophia_ai.db"
    redis_url: str = "redis://localhost:6379"

    # AI Services
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    pinecone_api_key: str = ""

    # Qdrant
    
    
    
    

    # Rate Limiting
    rate_limit_per_minute: int = 60

    class Config:
        env_prefix = "SOPHIA_"
        case_sensitive = False
        env_file = ".env"
