#!/usr/bin/env python3
"""Secure Credential Manager for Sophia AI
Centralized secure access to all API keys and credentials via environment variables
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CredentialConfig:
    """Configuration for a credential with validation"""

    name: str
    env_var: str
    required: bool = True
    description: str = ""
    validation_pattern: Optional[str] = None


class SecureCredentialManager:
    """Centralized secure credential management for Sophia AI
    All credentials loaded from environment variables only
    """

    # Define all required credentials
    CREDENTIALS = {
        # Core Infrastructure
        "PULUMI_ACCESS_TOKEN": CredentialConfig(
            name="Pulumi Access Token",
            env_var="PULUMI_ACCESS_TOKEN",
            description="Pulumi Cloud access token for infrastructure management",
        ),
        "SECRET_KEY": CredentialConfig(
            name="Application Secret Key",
            env_var="SECRET_KEY",
            description="Application secret key for encryption",
        ),
        "JWT_SECRET": CredentialConfig(
            name="JWT Secret",
            env_var="JWT_SECRET",
            description="JWT token signing secret",
        ),
        # Database
        "POSTGRES_PASSWORD": CredentialConfig(
            name="PostgreSQL Password",
            env_var="POSTGRES_PASSWORD",
            description="PostgreSQL database password",
        ),
        # AI Services
        "ANTHROPIC_API_KEY": CredentialConfig(
            name="Anthropic API Key",
            env_var="ANTHROPIC_API_KEY",
            description="Anthropic Claude API key",
        ),
        "OPENAI_API_KEY": CredentialConfig(
            name="OpenAI API Key",
            env_var="OPENAI_API_KEY",
            description="OpenAI API key",
        ),
        # Business Integrations
        "GONG_ACCESS_KEY": CredentialConfig(
            name="Gong Access Key",
            env_var="GONG_ACCESS_KEY",
            description="Gong.io API access key",
        ),
        "GONG_CLIENT_SECRET": CredentialConfig(
            name="Gong Client Secret",
            env_var="GONG_CLIENT_SECRET",
            description="Gong.io API client secret",
        ),
        "HUBSPOT_API_TOKEN": CredentialConfig(
            name="HubSpot API Token",
            env_var="HUBSPOT_API_TOKEN",
            description="HubSpot CRM API token",
        ),
        "SLACK_BOT_TOKEN": CredentialConfig(
            name="Slack Bot Token",
            env_var="SLACK_BOT_TOKEN",
            description="Slack bot token for notifications",
        ),
        # Data Infrastructure
        "SNOWFLAKE_ACCOUNT": CredentialConfig(
            name="Snowflake Account",
            env_var="SNOWFLAKE_ACCOUNT",
            description="Snowflake account identifier",
        ),
        "SNOWFLAKE_USER": CredentialConfig(
            name="Snowflake User",
            env_var="SNOWFLAKE_USER",
            description="Snowflake username",
        ),
        "SNOWFLAKE_PASSWORD": CredentialConfig(
            name="Snowflake Password",
            env_var="SNOWFLAKE_PASSWORD",
            description="Snowflake password",
        ),
        # Vector Databases
        "PINECONE_API_KEY": CredentialConfig(
            name="Pinecone API Key",
            env_var="PINECONE_API_KEY",
            description="Pinecone vector database API key",
        ),
        "WEAVIATE_API_KEY": CredentialConfig(
            name="Weaviate API Key",
            env_var="WEAVIATE_API_KEY",
            description="Weaviate vector database API key",
        ),
        # Cloud Services
        "LAMBDA_LABS_API_KEY": CredentialConfig(
            name="Lambda Labs API Key",
            env_var="LAMBDA_LABS_API_KEY",
            description="Lambda Labs GPU cloud API key",
        ),
        "VERCEL_ACCESS_TOKEN": CredentialConfig(
            name="Vercel Access Token",
            env_var="VERCEL_ACCESS_TOKEN",
            description="Vercel deployment access token",
        ),
        # Development Tools
        "RETOOL_API_TOKEN": CredentialConfig(
            name="Retool API Token",
            env_var="RETOOL_API_TOKEN",
            description="Retool API token for workflow management",
        ),
    }

    def __init__(self):
        """Initialize credential manager"""
        self._credentials_cache = {}
        self._load_credentials()

    def _load_credentials(self):
        """Load all credentials from environment variables"""
        missing_required = []

        for key, config in self.CREDENTIALS.items():
            value = os.getenv(config.env_var)

            if value:
                self._credentials_cache[key] = value
                logger.debug(f"Loaded credential: {config.name}")
            elif config.required:
                missing_required.append(config.name)
                logger.warning(
                    f"Missing required credential: {config.name} ({config.env_var})"
                )
            else:
                logger.info(f"Optional credential not set: {config.name}")

        if missing_required:
            logger.error(f"Missing required credentials: {', '.join(missing_required)}")
            # Don't raise exception - allow graceful degradation

    def get_credential(self, key: str) -> Optional[str]:
        """Get a credential value securely"""
        if key not in self.CREDENTIALS:
            logger.error(f"Unknown credential key: {key}")
            return None

        value = self._credentials_cache.get(key)
        if not value:
            # Try to load from environment again
            config = self.CREDENTIALS[key]
            value = os.getenv(config.env_var)
            if value:
                self._credentials_cache[key] = value

        return value

    def get_gong_credentials(self) -> Dict[str, str]:
        """Get Gong.io API credentials"""
        return {
            "access_key": self.get_credential("GONG_ACCESS_KEY") or "",
            "client_secret": self.get_credential("GONG_CLIENT_SECRET") or "",
            "base_url": "https://us-70092.api.gong.io/v2",
        }

    def get_snowflake_credentials(self) -> Dict[str, str]:
        """Get Snowflake credentials"""
        return {
            "account": self.get_credential("SNOWFLAKE_ACCOUNT") or "",
            "user": self.get_credential("SNOWFLAKE_USER") or "",
            "password": self.get_credential("SNOWFLAKE_PASSWORD") or "",
            "warehouse": "COMPUTE_WH",
            "database": "SOPHIA_AI",
            "schema": "PUBLIC",
        }

    def get_database_url(self) -> str:
        """Get PostgreSQL database URL"""
        password = self.get_credential("POSTGRES_PASSWORD") or "password"
        return f"postgresql://postgres:{password}@localhost:5432/sophia_enhanced"

    def validate_credentials(self) -> Dict[str, bool]:
        """Validate all credentials are available"""
        validation_results = {}

        for key, config in self.CREDENTIALS.items():
            value = self.get_credential(key)
            is_valid = bool(value) if config.required else True
            validation_results[key] = is_valid

            if config.required and not is_valid:
                logger.error(
                    f"Validation failed for required credential: {config.name}"
                )

        return validation_results

    def get_missing_credentials(self) -> List[str]:
        """Get list of missing required credentials"""
        missing = []
        for key, config in self.CREDENTIALS.items():
            if config.required and not self.get_credential(key):
                missing.append(config.name)
        return missing

    def get_credential_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all credentials"""
        status = {}
        for key, config in self.CREDENTIALS.items():
            value = self.get_credential(key)
            status[key] = {
                "name": config.name,
                "description": config.description,
                "required": config.required,
                "available": bool(value),
                "env_var": config.env_var,
            }
        return status


# Global credential manager instance
credential_manager = SecureCredentialManager()


def get_credential(key: str) -> Optional[str]:
    """Convenience function to get a credential"""
    return credential_manager.get_credential(key)


def get_gong_credentials() -> Dict[str, str]:
    """Convenience function to get Gong credentials"""
    return credential_manager.get_gong_credentials()


def get_snowflake_credentials() -> Dict[str, str]:
    """Convenience function to get Snowflake credentials"""
    return credential_manager.get_snowflake_credentials()


def validate_all_credentials() -> bool:
    """Validate all required credentials are available"""
    validation_results = credential_manager.validate_credentials()
    return all(validation_results.values())


if __name__ == "__main__":
    # Test credential loading
    print("Sophia AI Secure Credential Manager")
    print("=" * 50)

    status = credential_manager.get_credential_status()
    for key, info in status.items():
        status_icon = "✅" if info["available"] else "❌"
        required_icon = "🔴" if info["required"] else "🟡"
        print(f"{status_icon} {required_icon} {info['name']}: {info['description']}")

    missing = credential_manager.get_missing_credentials()
    if missing:
        print(f"\n❌ Missing required credentials: {', '.join(missing)}")
    else:
        print("\n✅ All required credentials available!")
