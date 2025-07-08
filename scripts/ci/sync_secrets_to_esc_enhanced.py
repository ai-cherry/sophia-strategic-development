#!/usr/bin/env python3
"""
Enhanced sync script that maps actual GitHub secret names to Pulumi ESC
Handles name mismatches between expected and actual secret names
"""

import json
import os
import subprocess
import sys

# GitHub secret name mappings (actual names in your org)
GITHUB_TO_ESC_MAPPINGS = {
    # AI Services
    "OPENAI_API_KEY": "values.sophia.ai.openai_api_key",
    "ANTHROPIC_API_KEY": "values.sophia.ai.anthropic_api_key",
    "GROQ_API_KEY": "values.sophia.ai.groq_api_key",
    "DEEPSEEK_API_KEY": "values.sophia.ai.deepseek_api_key",
    # Infrastructure - Using actual names
    "PULUMI_ACCESS_TOKEN": "values.sophia.infrastructure.pulumi_access_token",
    "DOCKER_TOKEN": "values.sophia.infrastructure.docker_token",  # Not DOCKER_HUB_TOKEN
    "LAMBDA_API_KEY": "values.sophia.infrastructure.lambda_labs.api_key",
    "LAMBDA_SSH_KEY": "values.sophia.infrastructure.lambda_labs.ssh_public_key",
    "LAMBDA_PRIVATE_SSH_KEY": "values.sophia.infrastructure.lambda_labs.ssh_private_key",
    "VERCEL_ACCESS_TOKEN": "values.sophia.infrastructure.vercel_token",
    # Data Services - Using actual names
    "SNOWFLAKE_ACCOUNT": "values.sophia.data.snowflake.account",
    "SNOWFLAKE_USER": "values.sophia.data.snowflake.username",  # Not SNOWFLAKE_USERNAME
    "SNOWFLAKE_PASSWORD": "values.sophia.data.snowflake.password",
    "PINECONE_API_KEY": "values.sophia.data.pinecone_api_key",
    "REDIS_PASSWORD": "values.sophia.data.redis_password",
    # Business Integrations
    "GONG_ACCESS_KEY": "values.sophia.integrations.gong.access_key",
    "GONG_CLIENT_SECRET": "values.sophia.integrations.gong.client_secret",
    "HUBSPOT_ACCESS_TOKEN": "values.sophia.integrations.hubspot_token",
    "SLACK_BOT_TOKEN": "values.sophia.integrations.slack.bot_token",
    "LINEAR_API_KEY": "values.sophia.integrations.linear_api_key",
    "ASANA_API_TOKEN": "values.sophia.integrations.asana_token",
    "GH_API_TOKEN": "values.sophia.integrations.github_token",  # Not GITHUB_TOKEN
    "FIGMA_PAT": "values.sophia.integrations.figma_token",  # Not FIGMA_ACCESS_TOKEN
    # Security
    "JWT_SECRET": "values.sophia.security.jwt_secret",
    "ENCRYPTION_KEY": "values.sophia.security.encryption_key",
    # Additional secrets from your org that might be useful
    "PORTKEY_API_KEY": "values.sophia.ai.portkey_api_key",
    "OPENROUTER_API_KEY": "values.sophia.ai.openrouter_api_key",
    "LANGCHAIN_API_KEY": "values.sophia.ai.langchain_api_key",
    "LANGGRAPH_API_KEY": "values.sophia.ai.langgraph_api_key",
    "TOGETHER_AI_API_KEY": "values.sophia.ai.together_ai_api_key",
    "MISTRAL_API_KEY": "values.sophia.ai.mistral_api_key",
    "PERPLEXITY_API_KEY": "values.sophia.ai.perplexity_api_key",
    "COHERE_API_KEY": "values.sophia.ai.cohere_api_key",
    "ELEVEN_LABS_API_KEY": "values.sophia.ai.eleven_labs_api_key",
    "STABILITY_API_KEY": "values.sophia.ai.stability_api_key",
    "TAVILY_API_KEY": "values.sophia.ai.tavily_api_key",
    "MEM0_API_KEY": "values.sophia.ai.mem0_api_key",
    # Snowflake additional configs
    "SNOWFLAKE_DATABASE": "values.sophia.data.snowflake.database",
    "SNOWFLAKE_WAREHOUSE": "values.sophia.data.snowflake.warehouse",
    "SNOWFLAKE_ROLE": "values.sophia.data.snowflake.role",
    "SNOWFLAKE_SCHEMA": "values.sophia.data.snowflake.schema",
    # Additional integrations
    "NOTION_API_TOKEN": "values.sophia.integrations.notion_token",
    "SLACK_SIGNING_SECRET": "values.sophia.integrations.slack.signing_secret",
    "SLACK_CLIENT_ID": "values.sophia.integrations.slack.client_id",
    "SLACK_CLIENT_SECRET": "values.sophia.integrations.slack.client_secret",
}


def run_pulumi_command(args: list[str]) -> tuple[bool, str, str]:
    """Run a Pulumi command and return success, stdout, stderr"""
    env = os.environ.copy()
    env["PULUMI_SKIP_UPDATE_CHECK"] = "true"

    try:
        result = subprocess.run(
            ["pulumi"] + args, capture_output=True, text=True, env=env, check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def sync_secrets():
    """Sync all secrets from GitHub to Pulumi ESC"""

    # Configuration
    esc_environment = "scoobyjava-org/default/sophia-ai-production"

    print("🔄 Enhanced Secret Sync: GitHub → Pulumi ESC")
    print(f"Target Environment: {esc_environment}")
    print("=" * 60)

    # Track results
    synced = []
    failed = []
    skipped = []
    placeholders = []

    # Process each mapping
    for github_name, esc_path in GITHUB_TO_ESC_MAPPINGS.items():
        # Get secret value from environment
        env_key = f"SECRET_{github_name}"
        secret_value = os.environ.get(env_key, "")

        if not secret_value:
            print(f"⏭️  {github_name} → SKIPPED (not provided)")
            skipped.append(github_name)
            continue

        # Check for placeholders
        placeholder_patterns = ["PLACEHOLDER", "YOUR_", "REPLACE_ME", "DUMMY", "XXX"]
        if any(p in secret_value.upper() for p in placeholder_patterns):
            print(f"⚠️  {github_name} → PLACEHOLDER DETECTED")
            placeholders.append(github_name)
            continue

        # Sync to Pulumi ESC
        args = ["env", "set", esc_environment, esc_path, secret_value, "--secret"]

        success, stdout, stderr = run_pulumi_command(args)

        if success:
            # Mask the value in output
            if len(secret_value) > 8:
                masked_value = secret_value[:4] + "***" + secret_value[-4:]
            else:
                masked_value = "***"
            print(f"✅ {github_name} → {esc_path} ({masked_value})")
            synced.append(github_name)
        else:
            print(f"❌ {github_name} → FAILED: {stderr}")
            failed.append((github_name, stderr))

    # Summary
    print("\n" + "=" * 60)
    print("📊 SYNC SUMMARY")
    print("=" * 60)
    print(f"✅ Synced: {len(synced)} secrets")
    print(f"❌ Failed: {len(failed)} secrets")
    print(f"⚠️  Placeholders: {len(placeholders)} secrets")
    print(f"⏭️  Skipped: {len(skipped)} secrets")
    print(f"📋 Total mappings: {len(GITHUB_TO_ESC_MAPPINGS)}")

    if placeholders:
        print("\n⚠️  Placeholder Secrets:")
        for secret in placeholders:
            print(f"  - {secret}")

    if failed:
        print("\n❌ Failed Secrets:")
        for secret, reason in failed:
            print(f"  - {secret}: {reason}")

    # Generate report
    report = {
        "environment": esc_environment,
        "total_mappings": len(GITHUB_TO_ESC_MAPPINGS),
        "synced": synced,
        "failed": [{"secret": s, "reason": r} for s, r in failed],
        "placeholders": placeholders,
        "skipped": skipped,
        "success_rate": len(synced) / len(GITHUB_TO_ESC_MAPPINGS) * 100
        if GITHUB_TO_ESC_MAPPINGS
        else 0,
    }

    with open("sync_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n📄 Detailed report saved to: sync_report.json")

    # Exit with error if any critical secrets failed
    critical_secrets = ["PULUMI_ACCESS_TOKEN", "DOCKER_TOKEN", "LAMBDA_PRIVATE_SSH_KEY"]
    critical_failed = [s for s, _ in failed if s in critical_secrets]

    if critical_failed:
        print(f"\n❌ CRITICAL SECRETS FAILED: {', '.join(critical_failed)}")
        sys.exit(1)
    elif placeholders:
        print("\n⚠️  WARNING: Some secrets contain placeholder values")
        print("These need to be updated with real values for full functionality")
    else:
        print("\n✅ SYNC SUCCESSFUL: All provided secrets synced to Pulumi ESC")


if __name__ == "__main__":
    # Ensure we're logged into Pulumi
    success, stdout, stderr = run_pulumi_command(["whoami"])
    if not success:
        print("❌ Not logged into Pulumi. Please set PULUMI_ACCESS_TOKEN")
        sys.exit(1)

    print(f"👤 Logged in as: {stdout.strip()}")

    # Run sync
    sync_secrets()
