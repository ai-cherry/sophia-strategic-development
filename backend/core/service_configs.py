"""
Service Configuration Classes
Centralized configuration for all Sophia AI services
"""

from typing import Dict
from backend.core.auto_esc_config import get_config_value


class AIServiceConfig:
    """Configuration for AI services"""
    
    def __init__(self):
        self.openai_api_key = get_config_value("openai_api_key")
        self.anthropic_api_key = get_config_value("anthropic_api_key")
        self.portkey_api_key = get_config_value("portkey_api_key")
        
    def validate(self) -> bool:
        """Validate AI service configuration"""
        return bool(self.openai_api_key or self.anthropic_api_key)


class DataServiceConfig:
    """Configuration for data services"""
    
    def __init__(self):
        self.postgres_host = get_config_value("postgres_host")
        self.postgres_user = get_config_value("postgres_user")
        self.postgres_password = get_config_value("postgres_password")
        self.postgres_database = get_config_value("postgres_database")
        self.redis_url = get_config_value("redis_url")
        self.QDRANT_client_url = get_config_value("QDRANT_URL")
        self.pinecone_api_key = get_config_value("pinecone_api_key")

    def get_postgres_url(self) -> str:
        """Generate PostgreSQL connection URL"""
        if not all([self.postgres_host, self.postgres_user, self.postgres_password]):
            raise ValueError("Missing required PostgreSQL configuration")
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}/{self.postgres_database}"

    def validate(self) -> bool:
        """Validate data service configuration"""
        required = [
            self.postgres_host,
            self.postgres_user,
            self.postgres_password,
            self.postgres_database
        ]
        return all(required)


class BusinessServiceConfig:
    """Configuration for business integration services"""
    
    def __init__(self):
        self.gong_api_key = get_config_value("gong_api_key")
        self.hubspot_api_key = get_config_value("hubspot_api_key")
        self.slack_webhook_url = get_config_value("slack_webhook_url")
        self.linear_api_key = get_config_value("linear_api_key")
        
    def validate(self) -> bool:
        """Validate business service configuration"""
        return bool(self.gong_api_key or self.hubspot_api_key)


class InfrastructureConfig:
    """Configuration for infrastructure services"""
    
    def __init__(self):
        self.lambda_labs_api_key = get_config_value("lambda_labs_api_key")
        self.docker_hub_username = get_config_value("docker_hub_username")
        self.docker_hub_token = get_config_value("docker_hub_token")
        
    def validate(self) -> bool:
        """Validate infrastructure configuration"""
        return bool(self.lambda_labs_api_key)


class UnifiedServiceConfig:
    """Unified configuration for all services"""
    
    def __init__(self):
        self.ai = AIServiceConfig()
        self.data = DataServiceConfig()
        self.business = BusinessServiceConfig()
        self.infrastructure = InfrastructureConfig()
        
    def validate_all(self) -> Dict[str, bool]:
        """Validate all service configurations"""
        return {
            "ai": self.ai.validate(),
            "data": self.data.validate(),
            "business": self.business.validate(),
            "infrastructure": self.infrastructure.validate()
        }
