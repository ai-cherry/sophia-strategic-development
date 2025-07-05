#!/usr/bin/env python3
"""
Validate Pulumi ESC secrets match expected names from codebase
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path.parent))


class PulumiESCValidator:
    def __init__(self):
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_env = "sophia-ai-production"
        self.env_path = f"{self.pulumi_org}/default/{self.pulumi_env}"

        # Load audit results
        with open("secret_usage_audit_report.json") as f:
            self.audit_data = json.load(f)

        # Expected mappings from GitHub to Pulumi ESC
        self.github_to_esc_mapping = {
            # AI Services
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "PERPLEXITY_API_KEY": "perplexity_api_key",
            # Business Intelligence
            "GONG_ACCESS_KEY": "gong_access_key",
            "GONG_INSTANCE_URL": "gong_instance_url",
            "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
            "HUBSPOT_API_KEY": "hubspot_api_key",
            # Communication
            "SLACK_BOT_TOKEN": "slack_bot_token",
            "SLACK_APP_TOKEN": "slack_app_token",
            "SLACK_SIGNING_SECRET": "slack_signing_secret",
            "LINEAR_API_KEY": "linear_api_key",
            # Data Infrastructure
            "SNOWFLAKE_ACCOUNT": "snowflake_account",
            "SNOWFLAKE_USER": "snowflake_user",
            "SNOWFLAKE_PASSWORD": "snowflake_password",
            "SNOWFLAKE_DATABASE": "snowflake_database",
            "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
            "SNOWFLAKE_ROLE": "snowflake_role",
            "PINECONE_API_KEY": "pinecone_api_key",
            "PINECONE_ENVIRONMENT": "pinecone_environment",
            "WEAVIATE_API_KEY": "weaviate_api_key",
            "WEAVIATE_URL": "weaviate_url",
            # Cloud Infrastructure
            "LAMBDA_API_KEY": "lambda_labs_api_key",
            "LAMBDA_LABS_API_KEY": "lambda_labs_api_key",
            "VERCEL_API_TOKEN": "vercel_api_token",
            "VERCEL_PROJECT_ID": "vercel_project_id",
            "PULUMI_ACCESS_TOKEN": "pulumi_access_token",
            # Development Tools
            "GITHUB_TOKEN": "github_token",
            "GH_API_TOKEN": "github_token",
            "CODACY_API_TOKEN": "codacy_api_token",
            "NOTION_API_KEY": "notion_api_token",
            "NOTION_API_TOKEN": "notion_api_token",
            "ASANA_API_TOKEN": "asana_access_token",
            "ASANA_ACCESS_TOKEN": "asana_access_token",
            # Additional Services
            "PORTKEY_API_KEY": "portkey_api_key",
            "OPENROUTER_API_KEY": "openrouter_api_key",
            "ESTUARY_API_KEY": "estuary_api_key",
            "FIGMA_PAT": "figma_pat",
            "FIGMA_PROJECT_ID": "figma_project_id",
            "APIFY_API_TOKEN": "apify_api_token",
            "BRIGHT_DATA_API_KEY": "bright_data_api_key",
            "HUGGINGFACE_API_KEY": "huggingface_api_key",
            "POSTGRES_PASSWORD": "postgres_password",
            "REDIS_PASSWORD": "redis_password",
            "APOLLO_API_KEY": "apollo_api_key",
            "NMHC_API_KEY": "nmhc_api_key",
            "SENTRY_DSN": "sentry_dsn",
            "GRAPHITI_API_KEY": "graphiti_api_key",
            "LANGFUSE_API_KEY": "langfuse_api_key",
            "LANGSMITH_API_KEY": "langsmith_api_key",
            "DEEPSEEK_API_KEY": "deepseek_api_key",
            "GEMINI_API_KEY": "gemini_api_key",
            "CLAUDE_API_KEY": "claude_api_key",
            "RETOOL_API_KEY": "retool_api_key",
            "N8N_API_KEY": "n8n_api_key",
            "SNOWFLAKE_CORTEX_API_KEY": "snowflake_cortex_api_key",
        }

    def get_pulumi_secrets(self) -> dict[str, str]:
        """Get all secrets from Pulumi ESC"""
        try:
            cmd = f"pulumi env open {self.env_path} --format json"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)

            if result.returncode != 0:
                return {}

            env_data = json.loads(result.stdout)

            # Extract secrets from the values.sophia structure
            secrets = {}
            if "values" in env_data and "sophia" in env_data["values"]:
                self._extract_secrets(env_data["values"]["sophia"], secrets)

            return secrets

        except Exception:
            return {}

    def _extract_secrets(self, data: dict, secrets: dict, prefix: str = ""):
        """Recursively extract secrets from nested structure"""
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                self._extract_secrets(value, secrets, f"{full_key}.")
            else:
                secrets[full_key] = value

    def analyze_secret_usage(self) -> dict[str, list[str]]:
        """Analyze which secrets are used in the codebase"""
        usage_analysis = {
            "get_config_value_calls": [],
            "env_var_references": [],
            "missing_in_mapping": [],
            "unused_mappings": [],
        }

        # Analyze get_config_value calls
        if "get_config_value" in self.audit_data["access_pattern_details"]:
            for item in self.audit_data["access_pattern_details"]["get_config_value"]:
                secret_name = item["secret"]
                usage_analysis["get_config_value_calls"].append(secret_name)

        # Analyze environment variable references
        for pattern in ["os_getenv", "os_environ", "os_environ_get", "env_var_ref"]:
            if pattern in self.audit_data["access_pattern_details"]:
                for item in self.audit_data["access_pattern_details"][pattern]:
                    secret_name = item["secret"]
                    usage_analysis["env_var_references"].append(secret_name)

        # Find secrets not in our mapping
        all_used_secrets = set(
            usage_analysis["get_config_value_calls"]
            + usage_analysis["env_var_references"]
        )
        for secret in all_used_secrets:
            if (
                secret not in self.github_to_esc_mapping
                and secret not in self.github_to_esc_mapping.values()
            ):
                usage_analysis["missing_in_mapping"].append(secret)

        return usage_analysis

    def validate_esc_structure(
        self, pulumi_secrets: dict[str, str]
    ) -> dict[str, list[str]]:
        """Validate ESC structure matches expected format"""
        validation_results = {
            "valid_secrets": [],
            "missing_secrets": [],
            "misnamed_secrets": [],
            "extra_secrets": [],
        }

        # Expected secrets based on mapping
        expected_secrets = set(self.github_to_esc_mapping.values())

        # Check each expected secret
        for _github_name, esc_name in self.github_to_esc_mapping.items():
            found = False
            for key in pulumi_secrets:
                if key.endswith(esc_name) or key == esc_name:
                    validation_results["valid_secrets"].append(esc_name)
                    found = True
                    break

            if not found:
                validation_results["missing_secrets"].append(esc_name)

        # Check for extra secrets not in mapping
        for key in pulumi_secrets:
            base_key = key.split(".")[-1]
            if base_key not in expected_secrets:
                validation_results["extra_secrets"].append(key)

        return validation_results

    def generate_fix_script(self, validation_results: dict[str, list[str]]):
        """Generate script to fix missing secrets"""
        fix_script = """#!/bin/bash
# Fix missing secrets in Pulumi ESC

set -e

echo "🔧 Fixing missing secrets in Pulumi ESC..."

"""

        for secret in validation_results["missing_secrets"]:
            github_name = None
            for gh, esc in self.github_to_esc_mapping.items():
                if esc == secret:
                    github_name = gh
                    break

            if github_name:
                fix_script += f"""
# {secret}
if [ -n "${{{github_name}}}" ]; then
    echo "Setting {secret}..."
    pulumi env set {self.env_path} values.sophia.{secret} "${{{github_name}}}"
else
    echo "⚠️  {github_name} not set in environment"
fi
"""

        with open("fix_missing_esc_secrets.sh", "w") as f:
            f.write(fix_script)

        os.chmod("fix_missing_esc_secrets.sh", 0o755)

    def run_validation(self):
        """Run complete validation"""

        # Get current Pulumi secrets
        pulumi_secrets = self.get_pulumi_secrets()
        if not pulumi_secrets:
            return

        # Analyze usage
        usage_analysis = self.analyze_secret_usage()

        # Validate structure
        validation_results = self.validate_esc_structure(pulumi_secrets)

        # Show missing secrets
        if validation_results["missing_secrets"]:
            for _secret in sorted(validation_results["missing_secrets"])[:10]:
                pass
            if len(validation_results["missing_secrets"]) > 10:
                pass

        # Show secrets not in mapping
        if usage_analysis["missing_in_mapping"]:
            for _secret in sorted(set(usage_analysis["missing_in_mapping"]))[:10]:
                pass

        # Generate fix script
        if validation_results["missing_secrets"]:
            self.generate_fix_script(validation_results)

        # Save detailed report
        report = {
            "pulumi_secrets_count": len(pulumi_secrets),
            "usage_analysis": usage_analysis,
            "validation_results": validation_results,
            "mapping": self.github_to_esc_mapping,
        }

        with open("pulumi_esc_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)


def main():
    validator = PulumiESCValidator()
    validator.run_validation()


if __name__ == "__main__":
    main()
