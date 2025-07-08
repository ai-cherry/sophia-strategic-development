#!/usr/bin/env python3
"""
Canonical Secret Mapping: GitHub Organization Secrets → Pulumi ESC
This is the SINGLE SOURCE OF TRUTH for all secret mappings
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SecretCategory(Enum):
    """Secret categories for organization"""

    AI_SERVICES = "ai_services"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"
    INTEGRATIONS = "integrations"
    SECURITY = "security"
    MONITORING = "monitoring"


@dataclass
class SecretMapping:
    """Defines how a secret maps from GitHub to Pulumi ESC"""

    github_name: str
    esc_path: str
    category: SecretCategory
    description: str
    required: bool = True
    sensitive: bool = True
    validation_regex: Optional[str] = None


# THE CANONICAL MAPPING - SINGLE SOURCE OF TRUTH
SECRET_MAPPINGS = [
    # AI Services
    SecretMapping(
        github_name="OPENAI_API_KEY",
        esc_path="values.sophia.ai.openai_api_key",
        category=SecretCategory.AI_SERVICES,
        description="OpenAI API key for GPT models",
        validation_regex=r"^sk-[a-zA-Z0-9]{48}$",
    ),
    SecretMapping(
        github_name="ANTHROPIC_API_KEY",
        esc_path="values.sophia.ai.anthropic_api_key",
        category=SecretCategory.AI_SERVICES,
        description="Anthropic API key for Claude models",
        validation_regex=r"^sk-ant-[a-zA-Z0-9-]{95}$",
    ),
    SecretMapping(
        github_name="GROQ_API_KEY",
        esc_path="values.sophia.ai.groq_api_key",
        category=SecretCategory.AI_SERVICES,
        description="Groq API key for fast inference",
    ),
    SecretMapping(
        github_name="DEEPSEEK_API_KEY",
        esc_path="values.sophia.ai.deepseek_api_key",
        category=SecretCategory.AI_SERVICES,
        description="DeepSeek API key for coding models",
    ),
    # Infrastructure
    SecretMapping(
        github_name="PULUMI_ACCESS_TOKEN",
        esc_path="values.sophia.infrastructure.pulumi_access_token",
        category=SecretCategory.INFRASTRUCTURE,
        description="Pulumi access token for IaC operations",
        validation_regex=r"^pul-[a-f0-9]{40}$",
    ),
    SecretMapping(
        github_name="DOCKER_HUB_TOKEN",
        esc_path="values.sophia.infrastructure.docker_token",
        category=SecretCategory.INFRASTRUCTURE,
        description="Docker Hub access token for image registry",
    ),
    SecretMapping(
        github_name="LAMBDA_LABS_API_KEY",
        esc_path="values.sophia.infrastructure.lambda_labs.api_key",
        category=SecretCategory.INFRASTRUCTURE,
        description="Lambda Labs API key for GPU instances",
    ),
    SecretMapping(
        github_name="LAMBDA_LABS_SSH_KEY",
        esc_path="values.sophia.infrastructure.lambda_labs.ssh_private_key",
        category=SecretCategory.INFRASTRUCTURE,
        description="SSH private key for Lambda Labs access",
        validation_regex=r"^-----BEGIN (?:RSA )?PRIVATE KEY-----",
    ),
    SecretMapping(
        github_name="VERCEL_ACCESS_TOKEN",
        esc_path="values.sophia.infrastructure.vercel_token",
        category=SecretCategory.INFRASTRUCTURE,
        description="Vercel access token for frontend deployment",
    ),
    # Data Services
    SecretMapping(
        github_name="SNOWFLAKE_ACCOUNT",
        esc_path="values.sophia.data.snowflake.account",
        category=SecretCategory.DATA,
        description="Snowflake account identifier",
        sensitive=False,
    ),
    SecretMapping(
        github_name="SNOWFLAKE_USERNAME",
        esc_path="values.sophia.data.snowflake.username",
        category=SecretCategory.DATA,
        description="Snowflake username",
        sensitive=False,
    ),
    SecretMapping(
        github_name="SNOWFLAKE_PASSWORD",
        esc_path="values.sophia.data.snowflake.password",
        category=SecretCategory.DATA,
        description="Snowflake password",
    ),
    SecretMapping(
        github_name="PINECONE_API_KEY",
        esc_path="values.sophia.data.pinecone_api_key",
        category=SecretCategory.DATA,
        description="Pinecone vector database API key",
    ),
    SecretMapping(
        github_name="POSTGRES_PASSWORD",
        esc_path="values.sophia.data.postgres_password",
        category=SecretCategory.DATA,
        description="PostgreSQL database password",
    ),
    SecretMapping(
        github_name="REDIS_PASSWORD",
        esc_path="values.sophia.data.redis_password",
        category=SecretCategory.DATA,
        description="Redis cache password",
    ),
    # Business Integrations
    SecretMapping(
        github_name="GONG_ACCESS_KEY",
        esc_path="values.sophia.integrations.gong.access_key",
        category=SecretCategory.INTEGRATIONS,
        description="Gong.io API access key",
    ),
    SecretMapping(
        github_name="GONG_CLIENT_SECRET",
        esc_path="values.sophia.integrations.gong.client_secret",
        category=SecretCategory.INTEGRATIONS,
        description="Gong.io client secret",
    ),
    SecretMapping(
        github_name="HUBSPOT_ACCESS_TOKEN",
        esc_path="values.sophia.integrations.hubspot_token",
        category=SecretCategory.INTEGRATIONS,
        description="HubSpot API access token",
    ),
    SecretMapping(
        github_name="SLACK_BOT_TOKEN",
        esc_path="values.sophia.integrations.slack.bot_token",
        category=SecretCategory.INTEGRATIONS,
        description="Slack bot user OAuth token",
        validation_regex=r"^xoxb-[0-9A-Za-z-]+",
    ),
    SecretMapping(
        github_name="LINEAR_API_KEY",
        esc_path="values.sophia.integrations.linear_api_key",
        category=SecretCategory.INTEGRATIONS,
        description="Linear project management API key",
    ),
    SecretMapping(
        github_name="ASANA_ACCESS_TOKEN",
        esc_path="values.sophia.integrations.asana_token",
        category=SecretCategory.INTEGRATIONS,
        description="Asana API access token",
    ),
    SecretMapping(
        github_name="GITHUB_TOKEN",
        esc_path="values.sophia.integrations.github_token",
        category=SecretCategory.INTEGRATIONS,
        description="GitHub personal access token",
        validation_regex=r"^gh[ps]_[a-zA-Z0-9]{36,}$",
    ),
    SecretMapping(
        github_name="FIGMA_ACCESS_TOKEN",
        esc_path="values.sophia.integrations.figma_token",
        category=SecretCategory.INTEGRATIONS,
        description="Figma API access token",
    ),
    # Security
    SecretMapping(
        github_name="JWT_SECRET",
        esc_path="values.sophia.security.jwt_secret",
        category=SecretCategory.SECURITY,
        description="JWT signing secret",
    ),
    SecretMapping(
        github_name="ENCRYPTION_KEY",
        esc_path="values.sophia.security.encryption_key",
        category=SecretCategory.SECURITY,
        description="Data encryption key",
    ),
    # Monitoring
    SecretMapping(
        github_name="SENTRY_DSN",
        esc_path="values.sophia.monitoring.sentry_dsn",
        category=SecretCategory.MONITORING,
        description="Sentry error tracking DSN",
        required=False,
    ),
    SecretMapping(
        github_name="DATADOG_API_KEY",
        esc_path="values.sophia.monitoring.datadog_api_key",
        category=SecretCategory.MONITORING,
        description="Datadog monitoring API key",
        required=False,
    ),
]


def get_all_mappings() -> list[SecretMapping]:
    """Get all secret mappings"""
    return SECRET_MAPPINGS


def get_required_mappings() -> list[SecretMapping]:
    """Get only required secret mappings"""
    return [m for m in SECRET_MAPPINGS if m.required]


def get_mappings_by_category(category: SecretCategory) -> list[SecretMapping]:
    """Get mappings for a specific category"""
    return [m for m in SECRET_MAPPINGS if m.category == category]


def get_github_to_esc_map() -> dict[str, str]:
    """Get simple dict mapping GitHub names to ESC paths"""
    return {m.github_name: m.esc_path for m in SECRET_MAPPINGS}


def get_esc_to_github_map() -> dict[str, str]:
    """Get reverse mapping from ESC paths to GitHub names"""
    return {m.esc_path: m.github_name for m in SECRET_MAPPINGS}


def validate_secret_value(mapping: SecretMapping, value: str) -> bool:
    """Validate a secret value against its regex pattern"""
    if not mapping.validation_regex:
        return True
    import re

    return bool(re.match(mapping.validation_regex, value))


def get_missing_secrets(github_secrets: dict[str, str]) -> list[SecretMapping]:
    """Identify which required secrets are missing from GitHub"""
    missing = []
    for mapping in get_required_mappings():
        if mapping.github_name not in github_secrets:
            missing.append(mapping)
    return missing


def generate_github_cli_commands() -> list[str]:
    """Generate GitHub CLI commands to set all secrets"""
    commands = []
    commands.append("# Set all GitHub Organization Secrets")
    commands.append("# Replace <VALUE> with actual secret values\n")

    for category in SecretCategory:
        mappings = get_mappings_by_category(category)
        if mappings:
            commands.append(f"\n# {category.value.replace('_', ' ').title()}")
            for m in mappings:
                cmd = f"gh secret set {m.github_name} --org ai-cherry --body '<VALUE>'"
                if m.description:
                    cmd = f"# {m.description}\n{cmd}"
                commands.append(cmd)

    return commands


def generate_pulumi_esc_commands() -> list[str]:
    """Generate Pulumi ESC commands to set all secrets"""
    commands = []
    commands.append("# Set all Pulumi ESC secrets")
    commands.append("# Replace <VALUE> with actual secret values\n")

    for mapping in SECRET_MAPPINGS:
        cmd = f"pulumi env set scoobyjava-org/default/sophia-ai-production {mapping.esc_path} '<VALUE>' --secret"
        if mapping.description:
            cmd = f"# {mapping.description}\n{cmd}"
        commands.append(cmd)

    return commands


if __name__ == "__main__":
    # Print summary
    print("🔐 Sophia AI Secret Mapping Summary")
    print("=" * 50)
    print(f"Total Mappings: {len(SECRET_MAPPINGS)}")
    print(f"Required: {len(get_required_mappings())}")
    print(f"Optional: {len(SECRET_MAPPINGS) - len(get_required_mappings())}")
    print("\nBy Category:")
    for category in SecretCategory:
        count = len(get_mappings_by_category(category))
        print(f"  {category.value}: {count}")

    # Generate command files
    with open("set_github_secrets.sh", "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("\n".join(generate_github_cli_commands()))

    with open("set_pulumi_secrets.sh", "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("\n".join(generate_pulumi_esc_commands()))

    print("\n✅ Generated: set_github_secrets.sh")
    print("✅ Generated: set_pulumi_secrets.sh")
