"""Sophia AI - Secure Configuration Management
🔐 IMPORTANT: This file is now LEGACY - Use backend/core/auto_esc_config.py instead!

The permanent GitHub Organization Secrets → Pulumi ESC solution automatically handles all configuration.
This file is kept for backward compatibility only.

For new code, use:
from backend.core.auto_esc_config import config
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# 🚨 LEGACY WARNING
logger.warning(
    "secure_config.py is LEGACY. Use backend/core/auto_esc_config.py for automatic secret loading from Pulumi ESC."
)


@dataclass
class SecureAPIConfig:
    """LEGACY: Secure API configuration management
    
    🔐 PERMANENT SOLUTION AVAILABLE:
    Use backend/core/auto_esc_config.py for automatic secret loading from Pulumi ESC.
    
    This class is kept for backward compatibility only.
    """

    # AI/ML Services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    replicate_api_key: Optional[str] = None
    together_api_key: Optional[str] = None

    # Gateway Services
    portkey_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    kong_access_token: Optional[str] = None
    arize_api_key: Optional[str] = None

    # Business Intelligence
    hubspot_api_key: Optional[str] = None
    gong_access_key: Optional[str] = None
    gong_client_secret: Optional[str] = None
    salesforce_api_key: Optional[str] = None
    looker_api_key: Optional[str] = None

    # Apartment Industry APIs
    yardi_api_key: Optional[str] = None
    yardi_api_secret: Optional[str] = None
    realpage_api_key: Optional[str] = None
    appfolio_api_key: Optional[str] = None
    entrata_api_key: Optional[str] = None
    costar_api_key: Optional[str] = None

    # Vector Databases
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west-2"
    weaviate_url: Optional[str] = None
    weaviate_api_key: Optional[str] = None

    # Communication
    slack_bot_token: Optional[str] = None
    slack_app_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None

    # Analytics
    google_analytics_key: Optional[str] = None
    mixpanel_api_key: Optional[str] = None
    amplitude_api_key: Optional[str] = None
    segment_write_key: Optional[str] = None

    # Payment Processing
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    plaid_client_id: Optional[str] = None
    plaid_secret: Optional[str] = None

    # Infrastructure
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    gcp_credentials_json: Optional[str] = None
    azure_subscription_id: Optional[str] = None
    lambda_labs_api_key: Optional[str] = None

    # Monitoring
    datadog_api_key: Optional[str] = None
    datadog_app_key: Optional[str] = None
    sentry_dsn: Optional[str] = None
    new_relic_api_key: Optional[str] = None

    # Development Tools
    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    jira_api_token: Optional[str] = None
    linear_api_key: Optional[str] = None
    notion_api_key: Optional[str] = None

    @classmethod
    def from_environment(cls) -> "SecureAPIConfig":
        """LEGACY: Load configuration from environment variables
        
        🔐 PERMANENT SOLUTION AVAILABLE:
        Use backend/core/auto_esc_config.py for automatic secret loading from Pulumi ESC.
        
        This method is kept for backward compatibility only.
        """
        logger.warning(
            "SecureAPIConfig.from_environment() is LEGACY. "
            "Use 'from backend.core.auto_esc_config import config' for automatic ESC integration."
        )
        
        config = cls()

        # Map environment variables to config attributes
        env_mapping = {
            # AI/ML Services
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "HUGGINGFACE_API_KEY": "huggingface_api_key",
            "COHERE_API_KEY": "cohere_api_key",
            "REPLICATE_API_KEY": "replicate_api_key",
            "TOGETHER_API_KEY": "together_api_key",
            # Gateway Services
            "PORTKEY_API_KEY": "portkey_api_key",
            "OPENROUTER_API_KEY": "openrouter_api_key",
            "KONG_ACCESS_TOKEN": "kong_access_token",
            "ARIZE_API_KEY": "arize_api_key",
            # Business Intelligence
            "HUBSPOT_API_KEY": "hubspot_api_key",
            "GONG_ACCESS_KEY": "gong_access_key",
            "GONG_CLIENT_SECRET": "gong_client_secret",
            "SALESFORCE_API_KEY": "salesforce_api_key",
            "LOOKER_API_KEY": "looker_api_key",
            # Apartment Industry
            "YARDI_API_KEY": "yardi_api_key",
            "YARDI_API_SECRET": "yardi_api_secret",
            "REALPAGE_API_KEY": "realpage_api_key",
            "APPFOLIO_API_KEY": "appfolio_api_key",
            "ENTRATA_API_KEY": "entrata_api_key",
            "COSTAR_API_KEY": "costar_api_key",
            # Vector Databases
            "PINECONE_API_KEY": "pinecone_api_key",
            "PINECONE_ENVIRONMENT": "pinecone_environment",
            "WEAVIATE_URL": "weaviate_url",
            "WEAVIATE_API_KEY": "weaviate_api_key",
            # Communication
            "SLACK_BOT_TOKEN": "slack_bot_token",
            "SLACK_APP_TOKEN": "slack_app_token",
            "SLACK_SIGNING_SECRET": "slack_signing_secret",
            "TWILIO_ACCOUNT_SID": "twilio_account_sid",
            "TWILIO_AUTH_TOKEN": "twilio_auth_token",
            # Analytics
            "GOOGLE_ANALYTICS_KEY": "google_analytics_key",
            "MIXPANEL_API_KEY": "mixpanel_api_key",
            "AMPLITUDE_API_KEY": "amplitude_api_key",
            "SEGMENT_WRITE_KEY": "segment_write_key",
            # Payment Processing
            "STRIPE_API_KEY": "stripe_api_key",
            "STRIPE_WEBHOOK_SECRET": "stripe_webhook_secret",
            "PAYPAL_CLIENT_ID": "paypal_client_id",
            "PAYPAL_CLIENT_SECRET": "paypal_client_secret",
            "PLAID_CLIENT_ID": "plaid_client_id",
            "PLAID_SECRET": "plaid_secret",
            # Infrastructure
            "AWS_ACCESS_KEY_ID": "aws_access_key_id",
            "AWS_SECRET_ACCESS_KEY": "aws_secret_access_key",
            "GCP_CREDENTIALS_JSON": "gcp_credentials_json",
            "AZURE_SUBSCRIPTION_ID": "azure_subscription_id",
            "LAMBDA_LABS_API_KEY": "lambda_labs_api_key",
            # Monitoring
            "DATADOG_API_KEY": "datadog_api_key",
            "DATADOG_APP_KEY": "datadog_app_key",
            "SENTRY_DSN": "sentry_dsn",
            "NEW_RELIC_API_KEY": "new_relic_api_key",
            # Development Tools
            "GITHUB_TOKEN": "github_token",
            "GITLAB_TOKEN": "gitlab_token",
            "JIRA_API_TOKEN": "jira_api_token",
            "LINEAR_API_KEY": "linear_api_key",
            "NOTION_API_KEY": "notion_api_key",
        }

        # Load from environment
        for env_var, attr_name in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                setattr(config, attr_name, value)

        return config

    def get_secret(self, key: str) -> Optional[str]:
        """LEGACY: Get a secret value
        
        🔐 PERMANENT SOLUTION AVAILABLE:
        Use backend/core/auto_esc_config.py for automatic secret loading from Pulumi ESC.
        """
        logger.warning(
            f"get_secret('{key}') is LEGACY. "
            "Use 'from backend.core.auto_esc_config import config' for automatic ESC integration."
        )
        return getattr(self, key, None)

    def validate_required_secrets(self) -> Dict[str, Any]:
        """LEGACY: Validate that required secrets are present
        
        🔐 PERMANENT SOLUTION AVAILABLE:
        Use scripts/test_permanent_solution.py for comprehensive validation.
        """
        logger.warning(
            "validate_required_secrets() is LEGACY. "
            "Use 'python scripts/test_permanent_solution.py' for comprehensive validation."
        )
        
        required_secrets = [
            "openai_api_key",
            "anthropic_api_key", 
            "pinecone_api_key",
            "gong_access_key",
            "slack_bot_token"
        ]
        
        missing = []
        for secret in required_secrets:
            if not getattr(self, secret):
                missing.append(secret)
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "total_secrets": len(required_secrets)
        }


# 🚨 LEGACY COMPATIBILITY FUNCTION
def get_secure_config() -> SecureAPIConfig:
    """LEGACY: Get secure configuration
    
    🔐 PERMANENT SOLUTION AVAILABLE:
    Use backend/core/auto_esc_config.py for automatic secret loading from Pulumi ESC.
    
    Example:
    from backend.core.auto_esc_config import config
    openai_key = config.openai_api_key
    """
    logger.warning(
        "get_secure_config() is LEGACY. "
        "Use 'from backend.core.auto_esc_config import config' for automatic ESC integration."
    )
    return SecureAPIConfig.from_environment()
