"""
Centralized service configuration classes
Uses auto_esc_config for secure secret management
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
from .auto_esc_config import get_config_value


class AIServiceConfig:
    """Configuration for AI services"""

    def __init__(self):
        self.openai_api_key = get_config_value("openai_api_key")
        self.anthropic_api_key = get_config_value("anthropic_api_key")
        self.portkey_api_key = get_config_value("portkey_api_key")
        self.openrouter_api_key = get_config_value("openrouter_api_key")

    def validate(self) -> bool:
        """Validate that required secrets are available"""
        required = [self.openai_api_key, self.anthropic_api_key]
        return all(secret is not None for secret in required)


class DataServiceConfig:
    """Configuration for data services"""

    def __init__(self):
# REMOVED: ModernStack dependency_value("postgres_host")
# REMOVED: ModernStack dependency_value("modern_stack_user")
# REMOVED: ModernStack dependency_value("postgres_password")
# REMOVED: ModernStack dependency_value("postgres_database")
# REMOVED: ModernStack dependency_value("postgres_database")
# REMOVED: ModernStack dependency_value("modern_stack_role")
        self.pinecone_api_key = get_config_value("pinecone_api_key")

    def get_modern_stack_url(self) -> str:
        """Generate ModernStack connection URL"""
        if not all(
            [self.postgres_host, self.modern_stack_user, self.postgres_password]
        ):
# REMOVED: ModernStack dependencyuration")
        return f"modern_stack://{self.modern_stack_user}:{self.postgres_password}@{self.postgres_host}"

    def validate(self) -> bool:
# REMOVED: ModernStack dependencyuration"""
        required = [
            self.postgres_host,
            self.modern_stack_user,
            self.postgres_password,
        ]
        return all(config is not None for config in required)


class BusinessServiceConfig:
    """Configuration for business intelligence services"""

    def __init__(self):
        self.gong_access_key = get_config_value("gong_access_key")
        self.gong_access_key_secret = get_config_value("gong_access_key_secret")
        self.hubspot_access_token = get_config_value("hubspot_access_token")
        self.linear_api_key = get_config_value("linear_api_key")
        self.notion_api_token = get_config_value("notion_api_token")

    def validate(self) -> bool:
        """Validate business service configuration"""
        return any(
            [self.gong_access_key, self.hubspot_access_token, self.linear_api_key]
        )


class InfrastructureConfig:
    """Configuration for infrastructure services"""

    def __init__(self):
        self.lambda_api_key = get_config_value("lambda_api_key")
        self.lambda_ip_address = get_config_value("lambda_ip_address")
        self.docker_token = get_config_value("docker_token")
        self.slack_bot_token = get_config_value("slack_bot_token")


# Global configuration instances
ai_config = AIServiceConfig()
data_config = DataServiceConfig()
business_config = BusinessServiceConfig()
infrastructure_config = InfrastructureConfig()
