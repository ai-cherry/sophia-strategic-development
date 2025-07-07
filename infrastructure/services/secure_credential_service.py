"""Secure Credential Service for Sophia AI Platform.

Provides secure access to API credentials through Pulumi ESC integration
without exposing secrets in data warehouse or logs.
"""

from __future__ import annotations

import logging

from infrastructure.security.secret_management import SecretManager

logger = logging.getLogger(__name__)


class SecureCredentialService:
    """Secure credential retrieval service integrated with Pulumi ESC."""

    def __init__(self, secret_manager: SecretManager | None = None):
        self.secret_manager = secret_manager or SecretManager()
        self.config = self.secret_manager.config
        self.logger = logger.bind(component="secure_credential_service")

    async def get_api_credentials(self, platform: str) -> dict[str, str]:
        """Retrieve API credentials securely from Pulumi ESC.

        Args:
            platform: Platform name (asana, salesforce, slack, etc.)

        Returns:
            Dictionary containing platform credentials and metadata

        Raises:
            ValueError: If platform is not supported
            RuntimeError: If credentials are not available or invalid
        """
        try:
            # Validate secrets before retrieval
            validation_results = await self.secret_manager.validate_secrets()

            if platform == "asana":
                if not validation_results.get("asana", False):
                    raise RuntimeError("Asana credentials validation failed")

                return {
                    "token": self.config.asana_pat_token,
                    "base_url": "https://app.asana.com/api/1.0",
                    "auth_type": "Bearer",
                    "rate_limit": 150,  # requests per minute
                }

            elif platform == "salesforce":
                if not validation_results.get("salesforce", False):
                    raise RuntimeError("Salesforce credentials validation failed")

                return {
                    "access_token": self.config.salesforce_access_token,
                    "base_url": "https://your-instance.salesforce.com",
                    "auth_type": "Bearer",
                    "rate_limit": 1000,
                }

            elif platform == "slack":
                if not validation_results.get("slack_enhanced", False):
                    raise RuntimeError("Enhanced Slack credentials validation failed")

                return {
                    "client_id": self.config.slack_client_id,
                    "client_secret": self.config.slack_client_secret,
                    "signing_secret": self.config.slack_signing_secret,
                    "app_token": self.config.slack_app_token,
                    "bot_token": self.config.slack_bot_token,
                    "base_url": "https://slack.com/api",
                    "auth_type": "Bearer",
                    "rate_limit": 50,
                }

            elif platform == "hubspot":
                return {
                    "access_token": self.config.hubspot_access_token,
                    "client_secret": self.config.hubspot_client_secret,
                    "base_url": "https://api.hubapi.com",
                    "auth_type": "Bearer",
                    "rate_limit": 100,
                }

            elif platform == "gong":
                return {
                    "access_key": self.config.gong_access_key,
                    "client_secret": self.config.gong_client_secret,
                    "access_key_secret": self.config.gong_access_key_secret,
                    "base_url": "https://api.gong.io/v2",
                    "auth_type": "Basic",
                    "rate_limit": 300,
                }

            elif platform == "linear":
                return {
                    "api_key": self.config.linear_api_key,
                    "base_url": "https://api.linear.app/graphql",
                    "auth_type": "Bearer",
                    "rate_limit": 1000,
                }

            else:
                raise ValueError(f"Unsupported platform: {platform}")

        except Exception as e:
            self.logger.error(f"Failed to retrieve credentials for {platform}: {e}")
            raise

    async def get_platform_endpoints(self, platform: str) -> dict[str, dict[str, str]]:
        """Get platform API endpoints configuration.

        Args:
            platform: Platform name

        Returns:
            Dictionary of endpoint configurations
        """
        endpoints = {
            "asana": {
                "projects": {"url": "/projects", "method": "GET"},
                "tasks": {"url": "/tasks", "method": "GET"},
                "users": {"url": "/users", "method": "GET"},
            },
            "salesforce": {
                "accounts": {
                    "url": "/services/data/v58.0/sobjects/Account",
                    "method": "GET",
                },
                "opportunities": {
                    "url": "/services/data/v58.0/sobjects/Opportunity",
                    "method": "GET",
                },
                "leads": {"url": "/services/data/v58.0/sobjects/Lead", "method": "GET"},
            },
            "slack": {
                "channels": {"url": "/conversations.list", "method": "GET"},
                "messages": {"url": "/conversations.history", "method": "GET"},
                "users": {"url": "/users.list", "method": "GET"},
            },
            "hubspot": {
                "contacts": {"url": "/crm/v3/objects/contacts", "method": "GET"},
                "companies": {"url": "/crm/v3/objects/companies", "method": "GET"},
                "deals": {"url": "/crm/v3/objects/deals", "method": "GET"},
            },
            "gong": {
                "calls": {"url": "/calls", "method": "POST"},
                "transcripts": {"url": "/calls/transcript", "method": "POST"},
                "users": {"url": "/users", "method": "GET"},
            },
            "linear": {
                "issues": {"url": "", "method": "POST"},  # GraphQL endpoint
                "projects": {"url": "", "method": "POST"},
                "teams": {"url": "", "method": "POST"},
            },
        }

        return endpoints.get(platform, {})

    async def health_check(self) -> dict[str, bool]:
        """Perform health check on all managed credentials."""
        return await self.secret_manager.validate_secrets()
