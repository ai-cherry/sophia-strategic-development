"""
Centralized service configuration classes
Uses auto_esc_config for secure secret management
"""

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
        self.snowflake_account = get_config_value("snowflake_account")
        self.snowflake_user = get_config_value("snowflake_user")
        self.snowflake_password = get_config_value("snowflake_password")
        self.snowflake_warehouse = get_config_value("snowflake_warehouse")
        self.snowflake_database = get_config_value("snowflake_database")
        self.snowflake_role = get_config_value("snowflake_role")
        self.pinecone_api_key = get_config_value("pinecone_api_key")

    def get_snowflake_url(self) -> str:
        """Generate Snowflake connection URL"""
        if not all(
            [self.snowflake_account, self.snowflake_user, self.snowflake_password]
        ):
            raise ValueError("Missing required Snowflake configuration")
        return f"snowflake://{self.snowflake_user}:{self.snowflake_password}@{self.snowflake_account}"

    def validate(self) -> bool:
        """Validate Snowflake configuration"""
        required = [
            self.snowflake_account,
            self.snowflake_user,
            self.snowflake_password,
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
