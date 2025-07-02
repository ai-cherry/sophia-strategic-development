#!/usr/bin/env python3
"""
Complete Estuary Flow migration and comprehensive secret management fix
"""

import json
import logging
import os
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CompleteEstuaryMigrationAndSecrets:
    def __init__(self):
        self.replacements = {
            # Basic replacements
            "estuary": "estuary",
            "estuary": "Estuary",
            "estuary": "ESTUARY",
            # Specific replacements
            "ESTUARY_ACCESS_TOKEN": "ESTUARY_ACCESS_TOKEN",
            "ESTUARY_CLIENT_ID": "ESTUARY_CLIENT_ID",
            "ESTUARY_CLIENT_SECRET": "ESTUARY_CLIENT_SECRET",
            "ESTUARY_API_URL": "ESTUARY_API_URL",
            "ESTUARY_WORKSPACE_ID": "ESTUARY_WORKSPACE_ID",
            "ESTUARY_REFRESH_TOKEN": "ESTUARY_REFRESH_TOKEN",
            # API URLs
            "api.estuary.com": "api.estuary.dev",
            "cloud.estuary.com": "dashboard.estuary.dev",
            "estuary.com": "estuary.dev",
            # Technical terms
            "estuary sync": "estuary flow",
            "estuary connection": "estuary materialization",
            "estuary source": "estuary capture",
            "estuary destination": "estuary materialization",
            "estuary workspace": "estuary tenant",
            "estuary-cli": "flowctl",
            # Class/Function names
            "EstuaryManager": "EstuaryManager",
            "EstuaryClient": "EstuaryClient",
            "EstuaryConfig": "EstuaryConfig",
            "EstuaryIntegration": "EstuaryIntegration",
            "EstuaryService": "EstuaryService",
            # File/Path names
            "estuary_": "estuary_",
            "estuary-": "estuary-",
            "_estuary": "_estuary",
            "-estuary": "-estuary",
        }

        self.files_modified = []
        self.errors = []

    def replace_in_file(self, file_path: Path) -> bool:
        """Replace estuary references in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply replacements
            for old, new in self.replacements.items():
                # Use word boundaries for whole word replacements
                if old.isalnum():
                    pattern = rf"\b{re.escape(old)}\b"
                else:
                    pattern = re.escape(old)

                content = re.sub(
                    pattern, new, content, flags=re.IGNORECASE if old.islower() else 0
                )

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.files_modified.append(str(file_path))
                return True

        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {e}")

        return False

    def rename_files_and_dirs(self, root_path: Path):
        """Rename files and directories containing 'estuary'"""
        # First, collect all items to rename (to avoid issues during iteration)
        items_to_rename = []

        for path in root_path.rglob("*"):
            if "estuary" in path.name.lower():
                items_to_rename.append(path)

        # Sort by path length (deepest first) to avoid parent/child conflicts
        items_to_rename.sort(key=lambda x: len(str(x)), reverse=True)

        for old_path in items_to_rename:
            new_name = old_path.name
            for old, new in self.replacements.items():
                new_name = new_name.replace(old, new)

            new_path = old_path.parent / new_name

            try:
                old_path.rename(new_path)
                logger.info(f"Renamed: {old_path} -> {new_path}")
            except Exception as e:
                self.errors.append(f"Failed to rename {old_path}: {e}")

    def update_github_sync_script(self):
        """Update the GitHub to Pulumi sync script with Estuary secrets"""
        sync_script_path = Path("scripts/ci/sync_from_gh_to_pulumi.py")

        try:
            with open(sync_script_path) as f:
                content = f.read()

            # Replace estuary mappings with Estuary
            content = re.sub(
                r'"ESTUARY_ACCESS_TOKEN":\s*"estuary_access_token"',
                '"ESTUARY_ACCESS_TOKEN": "estuary_access_token"',
                content,
            )

            # Add new Estuary mappings if not present
            if '"ESTUARY_CLIENT_ID"' not in content:
                # Find the secret_mapping section
                mapping_start = content.find("secret_mapping = {")
                if mapping_start != -1:
                    # Find the end of AI Services section
                    ai_services_end = content.find(
                        "# Business Intelligence", mapping_start
                    )
                    if ai_services_end != -1:
                        # Add Estuary secrets
                        estuary_mappings = """
        # Data Pipeline Services
        "ESTUARY_ACCESS_TOKEN": "estuary_access_token",
        "ESTUARY_CLIENT_ID": "estuary_client_id",
        "ESTUARY_CLIENT_SECRET": "estuary_client_secret",
        "ESTUARY_API_URL": "estuary_api_url",
        "ESTUARY_REFRESH_TOKEN": "estuary_refresh_token",

"""
                        content = (
                            content[:ai_services_end]
                            + estuary_mappings
                            + content[ai_services_end:]
                        )

            with open(sync_script_path, "w") as f:
                f.write(content)

            logger.info("✅ Updated GitHub sync script with Estuary mappings")

        except Exception as e:
            self.errors.append(f"Failed to update sync script: {e}")

    def update_pulumi_esc_config(self):
        """Update Pulumi ESC configuration files"""
        esc_files = [
            "infrastructure/esc/sophia-ai-production.yaml",
            "infrastructure/pulumi-esc-comprehensive-update.py",
        ]

        for file_path in esc_files:
            if Path(file_path).exists():
                self.replace_in_file(Path(file_path))

    def create_comprehensive_secret_mapping(self):
        """Create a comprehensive secret mapping including all secrets from GitHub org"""
        comprehensive_mapping = {
            # AI Services
            "OPENAI_API_KEY": "values.sophia.ai.openai.api_key",
            "ANTHROPIC_API_KEY": "values.sophia.ai.anthropic.api_key",
            "PERPLEXITY_API_KEY": "values.sophia.ai.perplexity.api_key",
            "CLAUDE_API_KEY": "values.sophia.ai.claude.api_key",
            "GEMINI_API_KEY": "values.sophia.ai.gemini.api_key",
            "DEEPSEEK_API_KEY": "values.sophia.ai.deepseek.api_key",
            # Data Pipeline (Estuary)
            "ESTUARY_ACCESS_TOKEN": "values.sophia.data.estuary.access_token",
            "ESTUARY_CLIENT_ID": "values.sophia.data.estuary.client_id",
            "ESTUARY_CLIENT_SECRET": "values.sophia.data.estuary.client_secret",
            "ESTUARY_API_URL": "values.sophia.data.estuary.api_url",
            "ESTUARY_REFRESH_TOKEN": "values.sophia.data.estuary.refresh_token",
            # Business Intelligence
            "GONG_ACCESS_KEY": "values.sophia.business.gong.access_key",
            "GONG_INSTANCE_URL": "values.sophia.business.gong.instance_url",
            "HUBSPOT_ACCESS_TOKEN": "values.sophia.business.hubspot.access_token",
            "HUBSPOT_API_KEY": "values.sophia.business.hubspot.api_key",
            "APOLLO_API_KEY": "values.sophia.business.apollo.api_key",
            # Communication
            "SLACK_BOT_TOKEN": "values.sophia.communication.slack.bot_token",
            "SLACK_APP_TOKEN": "values.sophia.communication.slack.app_token",
            "SLACK_SIGNING_SECRET": "values.sophia.communication.slack.signing_secret",
            "LINEAR_API_KEY": "values.sophia.communication.linear.api_key",
            # Data Infrastructure
            "SNOWFLAKE_ACCOUNT": "values.sophia.infrastructure.snowflake.account",
            "SNOWFLAKE_USER": "values.sophia.infrastructure.snowflake.user",
            "SNOWFLAKE_PASSWORD": "values.sophia.infrastructure.snowflake.password",
            "SNOWFLAKE_DATABASE": "values.sophia.infrastructure.snowflake.database",
            "SNOWFLAKE_WAREHOUSE": "values.sophia.infrastructure.snowflake.warehouse",
            "SNOWFLAKE_ROLE": "values.sophia.infrastructure.snowflake.role",
            "PINECONE_API_KEY": "values.sophia.data.pinecone.api_key",
            "PINECONE_ENVIRONMENT": "values.sophia.data.pinecone.environment",
            "WEAVIATE_API_KEY": "values.sophia.data.weaviate.api_key",
            "WEAVIATE_URL": "values.sophia.data.weaviate.url",
            "POSTGRES_PASSWORD": "values.sophia.infrastructure.postgres.password",
            "REDIS_PASSWORD": "values.sophia.infrastructure.redis.password",
            # Cloud Infrastructure
            "LAMBDA_API_KEY": "values.sophia.infrastructure.lambda_labs.api_key",
            "LAMBDA_LABS_API_KEY": "values.sophia.infrastructure.lambda_labs.api_key",
            "VERCEL_API_TOKEN": "values.sophia.infrastructure.vercel.api_token",
            "VERCEL_PROJECT_ID": "values.sophia.infrastructure.vercel.project_id",
            "PULUMI_ACCESS_TOKEN": "values.sophia.infrastructure.pulumi.access_token",
            # Development Tools
            "GITHUB_TOKEN": "values.sophia.development.github.token",
            "GH_API_TOKEN": "values.sophia.development.github.token",
            "CODACY_API_TOKEN": "values.sophia.development.codacy.api_token",
            "NOTION_API_KEY": "values.sophia.development.notion.api_token",
            "NOTION_API_TOKEN": "values.sophia.development.notion.api_token",
            "ASANA_API_TOKEN": "values.sophia.development.asana.access_token",
            "ASANA_ACCESS_TOKEN": "values.sophia.development.asana.access_token",
            # Additional Services
            "PORTKEY_API_KEY": "values.sophia.ai.portkey.api_key",
            "OPENROUTER_API_KEY": "values.sophia.ai.openrouter.api_key",
            "FIGMA_PAT": "values.sophia.development.figma.pat",
            "FIGMA_PROJECT_ID": "values.sophia.development.figma.project_id",
            "APIFY_API_TOKEN": "values.sophia.integrations.apify.api_token",
            "BRIGHT_DATA_API_KEY": "values.sophia.integrations.bright_data.api_key",
            "HUGGINGFACE_API_KEY": "values.sophia.ai.huggingface.api_key",
            "SENTRY_DSN": "values.sophia.monitoring.sentry.dsn",
            "GRAPHITI_API_KEY": "values.sophia.integrations.graphiti.api_key",
            "LANGFUSE_API_KEY": "values.sophia.monitoring.langfuse.api_key",
            "LANGSMITH_API_KEY": "values.sophia.monitoring.langsmith.api_key",
            "N8N_API_KEY": "values.sophia.integrations.n8n.api_key",
            "SNOWFLAKE_CORTEX_API_KEY": "values.sophia.ai.snowflake_cortex.api_key",
            # Agent Communication
            "AGENT_COMMUNICATION_SECRET": "values.sophia.security.agent_communication_secret",
            "AGENT_ORCHESTRATOR_AUTH_TOKEN": "values.sophia.security.agent_orchestrator_auth_token",
        }

        # Save the comprehensive mapping
        with open("comprehensive_secret_mapping.json", "w") as f:
            json.dump(comprehensive_mapping, f, indent=2)

        logger.info(
            f"✅ Created comprehensive secret mapping with {len(comprehensive_mapping)} secrets"
        )

        return comprehensive_mapping

    def generate_pulumi_esc_commands(self, mapping: dict[str, str]):
        """Generate Pulumi ESC commands to set all secrets"""
        commands = []
        env_path = "scoobyjava-org/default/sophia-ai-production"

        for _github_secret, esc_path in mapping.items():
            cmd = f'pulumi env set {env_path} {esc_path} "${{github_secret}}"'
            commands.append(cmd)

        # Save commands to script
        script_content = """#!/bin/bash
# Set all secrets in Pulumi ESC from GitHub secrets
# Run this after exporting all GitHub secrets as environment variables

set -e

echo "🔧 Setting all secrets in Pulumi ESC..."

"""

        for cmd in commands:
            script_content += f"{cmd}\n"

        script_content += """
echo "✅ All secrets set in Pulumi ESC!"
"""

        with open("set_all_pulumi_secrets.sh", "w") as f:
            f.write(script_content)

        os.chmod("set_all_pulumi_secrets.sh", 0o755)
        logger.info(
            "✅ Generated Pulumi ESC commands script: set_all_pulumi_secrets.sh"
        )

    def run_migration(self):
        """Execute complete migration"""
        logger.info("🚀 Starting complete Estuary migration and secret fix...")

        # Phase 1: Replace estuary with Estuary
        logger.info("\n📝 Phase 1: Replacing estuary with Estuary...")

        # Process all Python files
        for py_file in Path(".").rglob("*.py"):
            if ".git" not in str(py_file) and "node_modules" not in str(py_file):
                self.replace_in_file(py_file)

        # Process configuration files
        for config_pattern in ["*.yml", "*.yaml", "*.json", "*.md"]:
            for config_file in Path(".").rglob(config_pattern):
                if ".git" not in str(config_file) and "node_modules" not in str(
                    config_file
                ):
                    self.replace_in_file(config_file)

        # Rename files and directories
        self.rename_files_and_dirs(Path("."))

        # Phase 2: Update secret management
        logger.info("\n🔐 Phase 2: Updating secret management...")

        # Update GitHub sync script
        self.update_github_sync_script()

        # Update Pulumi ESC configs
        self.update_pulumi_esc_config()

        # Create comprehensive secret mapping
        mapping = self.create_comprehensive_secret_mapping()

        # Generate Pulumi commands
        self.generate_pulumi_esc_commands(mapping)

        # Generate report
        report = {
            "files_modified": len(self.files_modified),
            "errors": len(self.errors),
            "secret_mappings": len(mapping),
            "modified_files": self.files_modified[:20],  # First 20 files
            "error_details": self.errors,
        }

        with open("estuary_migration_complete_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("\n📊 Migration Summary:")
        logger.info(f"  Files modified: {report['files_modified']}")
        logger.info(f"  Errors: {report['errors']}")
        logger.info(f"  Secret mappings: {report['secret_mappings']}")

        if self.errors:
            logger.warning("\n⚠️  Errors encountered:")
            for error in self.errors[:5]:
                logger.warning(f"  - {error}")

        logger.info("\n✅ Migration complete! Next steps:")
        logger.info("  1. Review modified files")
        logger.info("  2. Add all secrets to GitHub Organization")
        logger.info("  3. Run GitHub Actions sync workflow")
        logger.info("  4. Execute set_all_pulumi_secrets.sh")
        logger.info("  5. Test all services")


def main():
    migrator = CompleteEstuaryMigrationAndSecrets()
    migrator.run_migration()


if __name__ == "__main__":
    main()
