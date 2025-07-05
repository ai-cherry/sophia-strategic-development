#!/usr/bin/env python3
"""
GitHub Organization Secrets Loader for Sophia AI
Loads secrets from GitHub organization level for local development
Part of the permanent GitHub → Pulumi ESC → Backend secret management solution
"""

import json
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubSecretsLoader:
    """Load secrets from GitHub organization for local development"""

    def __init__(self):
        self.org = "ai-cherry"
        self.repo = "sophia-main"  # Adjust if needed

        # Expected secrets from GitHub organization
        self.required_secrets = {
            "OPENAI_API_KEY": "OpenAI API key for embeddings and LLM operations",
            "PINECONE_API_KEY": "Pinecone API key for vector database",
            "PINECONE_ENVIRONMENT": "Pinecone environment (e.g., us-east1-gcp)",
            "GONG_ACCESS_KEY": "Gong API access key",
            "GONG_CLIENT_SECRET": "Gong API client secret",
            "SLACK_BOT_TOKEN": "Slack bot token for notifications",
            "HUBSPOT_ACCESS_TOKEN": "HubSpot CRM access token",
            "LINEAR_API_KEY": "Linear project management API key",
            "NOTION_API_KEY": "Notion API key for knowledge management",
        }

    def load_from_pulumi_esc_fallback(self) -> dict[str, str]:
        """Load secrets from Pulumi ESC if available"""
        secrets = {}

        try:
            # Try to load from ESC environment
            cmd = [
                "pulumi",
                "env",
                "open",
                "scoobyjava-org/default/sophia-ai-production",
                "--format",
                "json",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                config = json.loads(result.stdout)
                logger.info("✅ Loaded secrets from Pulumi ESC")

                # Map ESC keys to expected environment variables
                esc_mappings = {
                    "OPENAI_API_KEY": "openai_api_key",
                    "PINECONE_API_KEY": "pinecone_api_key",
                    "PINECONE_ENVIRONMENT": "pinecone_environment",
                    "GONG_ACCESS_KEY": "gong_access_key",
                    "GONG_CLIENT_SECRET": "gong_client_secret",
                    "SLACK_BOT_TOKEN": "slack_bot_token",
                    "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
                    "LINEAR_API_KEY": "linear_api_key",
                    "NOTION_API_KEY": "notion_api_key",
                }

                for env_var, esc_key in esc_mappings.items():
                    if esc_key in config:
                        secrets[env_var] = config[esc_key]
                        logger.info(f"✅ Loaded {env_var} from ESC")

            else:
                logger.warning("⚠️  Could not load from Pulumi ESC")

        except Exception as e:
            logger.error(f"❌ Error loading from Pulumi ESC: {e}")

        return secrets

    def load_from_local_env(self) -> dict[str, str]:
        """Load secrets from local environment variables"""
        secrets = {}

        for secret_name in self.required_secrets:
            value = os.getenv(secret_name)
            if value and value != "" and not value.startswith("test-"):
                secrets[secret_name] = value
                logger.info(f"✅ Loaded {secret_name} from environment")

        return secrets

    def create_development_secrets(self) -> dict[str, str]:
        """Create development-appropriate secrets for local testing"""
        dev_secrets = {
            "OPENAI_API_KEY": "sk-development-key-for-local-testing",
            "PINECONE_API_KEY": "",
            "PINECONE_ENVIRONMENT": "us-east1-gcp",
            "GONG_ACCESS_KEY": "",
            "GONG_CLIENT_SECRET": "dev-gong-client-secret",
            "SLACK_BOT_TOKEN": "xoxb-dev-slack-token",
            "HUBSPOT_ACCESS_TOKEN": "dev-hubspot-token",
            "LINEAR_API_KEY": "",
            "NOTION_API_KEY": "",
        }

        logger.info("�� Created development secrets for local testing")
        return dev_secrets

    def create_env_file(self, secrets: dict[str, str]) -> None:
        """Create .env file with loaded secrets"""
        env_file_path = ".env.secrets"

        with open(env_file_path, "w") as f:
            f.write("# Sophia AI Secrets - Auto-generated\n")
            f.write("# DO NOT COMMIT TO VERSION CONTROL\n")
            f.write(f"# Generated at: {os.popen('date').read().strip()}\n")
            f.write(
                "# Part of GitHub Organization → Pulumi ESC → Backend integration\n\n"
            )

            for secret_name, value in secrets.items():
                f.write(f"export {secret_name}={value}\n")

        logger.info(f"✅ Created {env_file_path} with {len(secrets)} secrets")

        # Add to .gitignore if not already there
        gitignore_path = ".gitignore"
        if os.path.exists(gitignore_path):
            with open(gitignore_path) as f:
                content = f.read()

            if ".env.secrets" not in content:
                with open(gitignore_path, "a") as f:
                    f.write("\n# Auto-generated secrets\n.env.secrets\n")
                logger.info("✅ Added .env.secrets to .gitignore")

    def load_all_secrets(self) -> dict[str, str]:
        """Load secrets from all available sources"""
        all_secrets = {}

        logger.info("🔐 Loading Sophia AI secrets from multiple sources...")

        # 1. Try local environment variables first
        env_secrets = self.load_from_local_env()
        all_secrets.update(env_secrets)

        # 2. Try Pulumi ESC
        esc_secrets = self.load_from_pulumi_esc_fallback()
        all_secrets.update(esc_secrets)

        # 3. If no real secrets found, create development ones
        if len(all_secrets) == 0:
            logger.info("🔧 No production secrets found, creating development secrets")
            dev_secrets = self.create_development_secrets()
            all_secrets.update(dev_secrets)

        return all_secrets

    def apply_secrets_to_environment(self, secrets: dict[str, str]) -> None:
        """Apply secrets to current environment"""
        for secret_name, value in secrets.items():
            os.environ[secret_name] = value
            logger.debug(f"Set {secret_name} in environment")

        logger.info(f"✅ Applied {len(secrets)} secrets to environment")

    def print_status_report(self, secrets: dict[str, str]) -> None:
        """Print status report of loaded secrets"""

        for secret_name, _description in self.required_secrets.items():
            if secret_name in secrets:
                value = secrets[secret_name]
                if (
                    value.startswith("dev-")
                    or value.startswith("sk-development")
                    or "github" in value.lower()
                ):
                    pass
                else:
                    pass

            else:
                pass

        # Show integration status


def main():
    """Main entry point"""
    loader = GitHubSecretsLoader()

    # Load secrets from all sources
    secrets = loader.load_all_secrets()

    # Apply to environment
    loader.apply_secrets_to_environment(secrets)

    # Create .env file for convenience
    loader.create_env_file(secrets)

    # Print status report
    loader.print_status_report(secrets)


if __name__ == "__main__":
    main()
