#!/usr/bin/env python3
"""
Pulumi ESC Configuration Update Script
Updates Pulumi ESC environment with new infrastructure credentials
Handles Estuary Flow, Lambda Labs, and Snowflake configuration
"""

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class PulumiESCUpdater:
    """
    Updates Pulumi ESC environment with infrastructure credentials
    Manages secure credential synchronization from GitHub Organization Secrets
    """

    def __init__(
        self, environment: str = "scoobyjava-org/default/sophia-ai-production"
    ):
        self.environment = environment
        self.current_config = {}
        self._load_current_config()

    def _load_current_config(self):
        """Load current Pulumi ESC configuration"""
        try:
            result = subprocess.run(
                ["pulumi", "env", "get", self.environment],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Parse current configuration
                self.current_config = self._parse_esc_output(result.stdout)
                logger.info(
                    f"Loaded current ESC configuration: {len(self.current_config)} items"
                )
            else:
                logger.warning(f"Failed to load ESC config: {result.stderr}")

        except Exception as e:
            logger.error(f"Error loading ESC configuration: {e}")

    def _parse_esc_output(self, output: str) -> dict[str, Any]:
        """Parse Pulumi ESC output into dictionary"""
        config = {}

        for line in output.split("\n"):
            if ":" in line and not line.strip().startswith("#"):
                try:
                    key, value = line.split(":", 1)
                    key = key.strip().strip('"')
                    value = value.strip().strip('"')

                    if value != "[secret]":
                        config[key] = value
                except Exception:
                    continue

        return config

    def update_estuary_flow_config(self, config: dict[str, Any]):
        """
        Update Estuary Flow configuration in Pulumi ESC

        Args:
            config: Estuary Flow configuration dictionary
        """
        logger.info("Updating Estuary Flow configuration...")

        estuary_config = {
            "estuary_flow_access_token": config.get("access_token"),
            "estuary_flow_tenant": config.get("tenant", "sophia-ai"),
            "estuary_flow_api_url": config.get("api_url", "https://api.estuary.dev"),
            "estuary_flow_webhook_url": config.get("webhook_url"),
            "estuary_flow_organization": config.get("organization", "sophia-ai"),
        }

        self._update_esc_values(estuary_config, "estuary_flow")

    def update_lambda_labs_config(self, config: dict[str, Any]):
        """
        Update Lambda Labs configuration in Pulumi ESC

        Args:
            config: Lambda Labs configuration dictionary
        """
        logger.info("Updating Lambda Labs configuration...")

        lambda_config = {
            "lambda_api_key": config.get("api_key"),
            "lambda_ssh_private_key": config.get("ssh_private_key"),
            "lambda_region": config.get("region", "us-west-1"),
            "lambda_instance_type": config.get("instance_type", "gpu_1x_a10"),
            "lambda_ip_address": config.get("ip_address"),
        }

        self._update_esc_values(lambda_config, "lambda_labs")

    def update_postgresql_config(self, config: dict[str, Any]):
        """
        Update PostgreSQL configuration in Pulumi ESC

        Args:
            config: PostgreSQL configuration dictionary
        """
        logger.info("Updating PostgreSQL configuration...")

        postgresql_config = {
            "postgresql_host": config.get("host"),
            "postgresql_port": str(config.get("port", 5432)),
            "postgresql_database": config.get("database", "sophia_staging"),
            "postgresql_user": config.get("username", "sophia_user"),
            "postgresql_password": config.get("password"),
            "postgresql_ssl_mode": config.get("ssl_mode", "require"),
            "postgresql_connection_string": config.get("connection_string"),
        }

        self._update_esc_values(postgresql_config, "postgresql")

    def update_redis_config(self, config: dict[str, Any]):
        """
        Update Redis configuration in Pulumi ESC

        Args:
            config: Redis configuration dictionary
        """
        logger.info("Updating Redis configuration...")

        redis_config = {
            "redis_host": config.get("host"),
            "redis_port": str(config.get("port", 6379)),
            "redis_password": config.get("password"),
            "redis_url": config.get("url"),
            "redis_max_memory": config.get("max_memory", "2gb"),
            "redis_max_memory_policy": config.get("max_memory_policy", "allkeys-lru"),
        }

        self._update_esc_values(redis_config, "redis")

    def update_snowflake_config(self, config: dict[str, Any]):
        """
        Update Snowflake configuration in Pulumi ESC

        Args:
            config: Snowflake configuration dictionary
        """
        logger.info("Updating Snowflake configuration...")

        snowflake_config = {
            "snowflake_account": config.get("account"),
            "snowflake_user": config.get("user", "PROGRAMMATIC_SERVICE_USER"),
            "sophia_ai_token": config.get(
                "token"
            ),  # Secure token for programmatic access
            "snowflake_role": config.get("role", "SYSADMIN"),
            "snowflake_warehouse": config.get("warehouse", "COMPUTE_WH"),
            "snowflake_database": config.get("database", "SOPHIA_AI"),
            "snowflake_schema": config.get("schema", "PUBLIC"),
        }

        self._update_esc_values(snowflake_config, "snowflake")

    def _update_esc_values(self, config: dict[str, Any], section: str):
        """
        Update ESC values for a specific section

        Args:
            config: Configuration dictionary
            section: Configuration section name
        """
        for key, value in config.items():
            if value is not None:
                try:
                    # Use pulumi env set to update individual values
                    cmd = ["pulumi", "env", "set", self.environment, f"{key}={value}"]

                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=30
                    )

                    if result.returncode == 0:
                        logger.info(f"Updated {section}.{key}")
                    else:
                        logger.error(
                            f"Failed to update {section}.{key}: {result.stderr}"
                        )

                except Exception as e:
                    logger.error(f"Error updating {section}.{key}: {e}")

    def create_comprehensive_esc_config(self) -> str:
        """
        Create comprehensive ESC configuration YAML

        Returns:
            YAML configuration string
        """
        config_yaml = """# Sophia AI Comprehensive Pulumi ESC Configuration
# Updated for Estuary Flow, Lambda Labs, and Snowflake integration

imports:
  - github-org-secrets

values:
  # Data Pipeline Infrastructure
  data_infrastructure:
    # Estuary Flow Configuration
    estuary_flow:
      access_token:
        fn::secret: ${github-org-secrets.ESTUARY_FLOW_ACCESS_TOKEN}
      tenant: "sophia-ai"
      api_url: "https://api.estuary.dev"
      webhook_url: "https://sophia-ai-frontend-dev.vercel.app/api/estuary/webhook"
      organization: "sophia-ai"

    # PostgreSQL Staging Database
    postgresql:
      host:
        fn::secret: ${github-org-secrets.POSTGRESQL_HOST}
      port: "5432"
      database: "sophia_staging"
      user: "sophia_user"
      password:
        fn::secret: ${github-org-secrets.POSTGRESQL_PASSWORD}
      ssl_mode: "require"
      connection_string:
        fn::secret: ${github-org-secrets.POSTGRESQL_CONNECTION_STRING}

    # Redis Cache
    redis:
      host:
        fn::secret: ${github-org-secrets.REDIS_HOST}
      port: "6379"
      password:
        fn::secret: ${github-org-secrets.REDIS_PASSWORD}
      url:
        fn::secret: ${github-org-secrets.REDIS_URL}
      max_memory: "2gb"
      max_memory_policy: "allkeys-lru"

  # Compute Infrastructure
  compute_infrastructure:
    # Lambda Labs Configuration
    lambda_labs:
      api_key:
        fn::secret: ${github-org-secrets.LAMBDA_API_KEY}
      ssh_private_key:
        fn::secret: ${github-org-secrets.LAMBDA_SSH_PRIVATE_KEY}
      ip_address:
        fn::secret: ${github-org-secrets.LAMBDA_IP_ADDRESS}
      region: "us-west-1"
      instance_type: "gpu_1x_a10"

  # Data Warehouse
  data_warehouse:
    # Snowflake Configuration
    snowflake:
      account:
        fn::secret: ${github-org-secrets.SNOWFLAKE_ACCOUNT}
      user: "PROGRAMMATIC_SERVICE_USER"
      token:
        fn::secret: ${github-org-secrets.SOPHIA_AI_TOKEN}
      role: "SYSADMIN"
      warehouse: "COMPUTE_WH"
      database: "SOPHIA_AI"
      schema: "PUBLIC"

  # External Integrations
  external_integrations:
    # HubSpot CRM
    hubspot:
      access_token:
        fn::secret: ${github-org-secrets.HUBSPOT_ACCESS_TOKEN}
      api_key:
        fn::secret: ${github-org-secrets.HUBSPOT_API_KEY}
      portal_id:
        fn::secret: ${github-org-secrets.HUBSPOT_PORTAL_ID}

    # Gong Revenue Intelligence
    gong:
      access_key:
        fn::secret: ${github-org-secrets.GONG_ACCESS_KEY}
      client_secret:
        fn::secret: ${github-org-secrets.GONG_CLIENT_SECRET}
      webhook_secret:
        fn::secret: ${github-org-secrets.GONG_WEBHOOK_SECRET}

    # Slack Communication
    slack:
      bot_token:
        fn::secret: ${github-org-secrets.SLACK_BOT_TOKEN}
      app_token:
        fn::secret: ${github-org-secrets.SLACK_APP_TOKEN}
      signing_secret:
        fn::secret: ${github-org-secrets.SLACK_SIGNING_SECRET}
      client_id:
        fn::secret: ${github-org-secrets.SLACK_CLIENT_ID}
      client_secret:
        fn::secret: ${github-org-secrets.SLACK_CLIENT_SECRET}

  # AI Services
  ai_services:
    # OpenAI
    openai:
      api_key:
        fn::secret: ${github-org-secrets.OPENAI_API_KEY}

    # Anthropic
    anthropic:
      api_key:
        fn::secret: ${github-org-secrets.ANTHROPIC_API_KEY}

    # Portkey Gateway
    portkey:
      api_key:
        fn::secret: ${github-org-secrets.PORTKEY_API_KEY}
      config:
        fn::secret: ${github-org-secrets.PORTKEY_CONFIG}

    # Vector Database
    pinecone:
      api_key:
        fn::secret: ${github-org-secrets.PINECONE_API_KEY}
      environment:
        fn::secret: ${github-org-secrets.PINECONE_ENVIRONMENT}

  # Deployment Configuration
  deployment:
    # Vercel
    vercel:
      token:
        fn::secret: ${github-org-secrets.VERCEL_TOKEN}
      project_id:
        fn::secret: ${github-org-secrets.VERCEL_PROJECT_ID}
      org_id:
        fn::secret: ${github-org-secrets.VERCEL_ORG_ID}

    # GitHub
    github:
      token:
        fn::secret: ${github-org-secrets.GITHUB_TOKEN}
      webhook_secret:
        fn::secret: ${github-org-secrets.GITHUB_WEBHOOK_SECRET}

    # Pulumi
    pulumi:
      access_token:
        fn::secret: ${github-org-secrets.PULUMI_ACCESS_TOKEN}

  # Environment Variables Export
  environment_variables:
    # Data Pipeline
    ESTUARY_FLOW_ACCESS_TOKEN: ${data_infrastructure.estuary_flow.access_token}
    ESTUARY_FLOW_TENANT: ${data_infrastructure.estuary_flow.tenant}
    POSTGRESQL_HOST: ${data_infrastructure.postgresql.host}
    POSTGRESQL_PORT: ${data_infrastructure.postgresql.port}
    POSTGRESQL_DATABASE: ${data_infrastructure.postgresql.database}
    POSTGRESQL_USER: ${data_infrastructure.postgresql.user}
    POSTGRESQL_PASSWORD: ${data_infrastructure.postgresql.password}
    REDIS_HOST: ${data_infrastructure.redis.host}
    REDIS_PORT: ${data_infrastructure.redis.port}
    REDIS_URL: ${data_infrastructure.redis.url}

    # Snowflake
    SNOWFLAKE_ACCOUNT: ${data_warehouse.snowflake.account}
    SNOWFLAKE_USER: ${data_warehouse.snowflake.user}
    SOPHIA_AI_TOKEN: ${data_warehouse.snowflake.token}
    SNOWFLAKE_ROLE: ${data_warehouse.snowflake.role}
    SNOWFLAKE_WAREHOUSE: ${data_warehouse.snowflake.warehouse}
    SNOWFLAKE_DATABASE: ${data_warehouse.snowflake.database}
    SNOWFLAKE_SCHEMA: ${data_warehouse.snowflake.schema}

    # External Integrations
    HUBSPOT_ACCESS_TOKEN: ${external_integrations.hubspot.access_token}
    GONG_ACCESS_KEY: ${external_integrations.gong.access_key}
    GONG_CLIENT_SECRET: ${external_integrations.gong.client_secret}
    SLACK_BOT_TOKEN: ${external_integrations.slack.bot_token}

    # AI Services
    OPENAI_API_KEY: ${ai_services.openai.api_key}
    ANTHROPIC_API_KEY: ${ai_services.anthropic.api_key}
    PORTKEY_API_KEY: ${ai_services.portkey.api_key}
    PINECONE_API_KEY: ${ai_services.pinecone.api_key}
"""

        return config_yaml

    def deploy_esc_configuration(self, config_yaml: str):
        """
        Deploy comprehensive ESC configuration

        Args:
            config_yaml: YAML configuration string
        """
        import os
        import tempfile

        # Save configuration to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_file:
            config_file.write(config_yaml)
            config_file_path = config_file.name

        try:
            # Deploy configuration using Pulumi ESC
            cmd = [
                "pulumi",
                "env",
                "init",
                self.environment,
                "--file",
                config_file_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                logger.info("ESC configuration deployed successfully")
            else:
                logger.error(f"Failed to deploy ESC configuration: {result.stderr}")

        finally:
            os.unlink(config_file_path)

    def sync_github_secrets_to_esc(self):
        """
        Sync GitHub Organization Secrets to Pulumi ESC
        This ensures all secrets are available in ESC
        """
        logger.info("Syncing GitHub Organization Secrets to Pulumi ESC...")

        # List of GitHub secrets that should be synced to ESC
        github_secrets = [
            "ESTUARY_FLOW_ACCESS_TOKEN",
            "LAMBDA_API_KEY",
            "LAMBDA_SSH_PRIVATE_KEY",
            "LAMBDA_IP_ADDRESS",
            "POSTGRESQL_HOST",
            "POSTGRESQL_PASSWORD",
            "POSTGRESQL_CONNECTION_STRING",
            "REDIS_HOST",
            "REDIS_PASSWORD",
            "REDIS_URL",
            "SNOWFLAKE_ACCOUNT",
            "SOPHIA_AI_TOKEN",
            "HUBSPOT_ACCESS_TOKEN",
            "GONG_ACCESS_KEY",
            "GONG_CLIENT_SECRET",
            "SLACK_BOT_TOKEN",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "PORTKEY_API_KEY",
            "PINECONE_API_KEY",
        ]

        logger.info(f"Syncing {len(github_secrets)} secrets from GitHub to ESC")

        # Note: In practice, this would use GitHub API to fetch secrets
        # and Pulumi ESC API to update them. For now, we log the requirement.
        for secret in github_secrets:
            logger.info(f"  - {secret}")

        logger.info("GitHub secrets sync configuration ready")


def update_infrastructure_credentials(
    estuary_config: dict[str, Any] = None,
    lambda_config: dict[str, Any] = None,
    postgresql_config: dict[str, Any] = None,
    redis_config: dict[str, Any] = None,
    snowflake_config: dict[str, Any] = None,
):
    """
    Update infrastructure credentials in Pulumi ESC

    Args:
        estuary_config: Estuary Flow configuration
        lambda_config: Lambda Labs configuration
        postgresql_config: PostgreSQL configuration
        redis_config: Redis configuration
        snowflake_config: Snowflake configuration
    """
    updater = PulumiESCUpdater()

    if estuary_config:
        updater.update_estuary_flow_config(estuary_config)

    if lambda_config:
        updater.update_lambda_labs_config(lambda_config)

    if postgresql_config:
        updater.update_postgresql_config(postgresql_config)

    if redis_config:
        updater.update_redis_config(redis_config)

    if snowflake_config:
        updater.update_snowflake_config(snowflake_config)

    logger.info("Infrastructure credentials updated in Pulumi ESC")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    updater = PulumiESCUpdater()

    # Generate comprehensive configuration
    config_yaml = updater.create_comprehensive_esc_config()

    # Save configuration to file
    with open("comprehensive-esc-config.yaml", "w") as f:
        f.write(config_yaml)

    print("📋 Comprehensive Pulumi ESC configuration generated!")
    print("   File: comprehensive-esc-config.yaml")
    print("   Ready for deployment with: pulumi env init")

    # Sync GitHub secrets
    updater.sync_github_secrets_to_esc()

    print("✅ Pulumi ESC update script ready for execution!")
