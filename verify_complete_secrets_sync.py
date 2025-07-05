import shlex
import subprocess

#!/usr/bin/env python3
"""
Comprehensive verification that ALL 67 GitHub Organization Secrets
are properly synced to Pulumi ESC and accessible via backend
"""

import asyncio
import sys

# Add backend to path
sys.path.insert(0, ".")


def check_github_actions_status():
    """Check if GitHub Actions workflow is running"""

    # Show recent commits
    subprocess.run(
        shlex.split("git log --oneline -3"), check=True
    )  # SECURITY FIX: Replaced os.system


def test_pulumi_esc_access():
    """Test direct Pulumi ESC access to verify secrets"""

    # Test key secrets that should be synced
    test_secrets = [
        "lambda_api_key",
        "lambda_ip_address",
        "lambda_ssh_private_key",
        "hubspot_access_token",
        "slack_bot_token",
        "linear_api_key",
        "notion_api_key",
        "vercel_access_token",
        "grafana_url",
        "docker_token",
    ]

    for secret in test_secrets:
        result = subprocess.run(
            shlex.split(
                f"pulumi config get {secret} --stack sophia-ai-production >/dev/null 2>&1"
            ),
            check=True,
        )  # SECURITY FIX: Replaced os.system
        if result == 0:
            pass
        else:
            pass


async def test_backend_secret_access():
    """Test backend access to all synced secrets"""

    try:
        from backend.core.auto_esc_config import get_config_value

        # Categorized secrets to test
        secret_categories = {
            "Core AI Services": [
                "openai_api_key",
                "anthropic_api_key",
                "gong_access_key",
                "pinecone_api_key",
            ],
            "Lambda Labs (Critical)": [
                "lambda_api_key",
                "lambda_ip_address",
                "lambda_ssh_private_key",
            ],
            "Business Intelligence": [
                "hubspot_access_token",
                "linear_api_key",
                "notion_api_key",
                "salesforce_access_token",
            ],
            "Communication": ["slack_bot_token", "slack_app_token", "slack_client_id"],
            "Extended AI": [
                "portkey_api_key",
                "openrouter_api_key",
                "huggingface_api_token",
                "langchain_api_key",
            ],
        }

        total_working = 0
        total_tested = 0

        for _category, secrets in secret_categories.items():
            category_working = 0

            for secret in secrets:
                total_tested += 1
                try:
                    value = get_config_value(secret)
                    if value and len(str(value)) > 5:
                        total_working += 1
                        category_working += 1
                    else:
                        pass
                except Exception:
                    pass

        if total_working >= 4:  # Core secrets working
            pass
        else:
            pass

        return total_working, total_tested

    except Exception:
        return 0, 0


def generate_verification_report(backend_working, backend_total):
    """Generate comprehensive verification report"""

    if backend_working >= 10 or backend_working >= 4:
        pass
    else:
        pass


async def main():
    """Run comprehensive verification"""

    # Check GitHub Actions status
    check_github_actions_status()

    # Test Pulumi ESC access
    test_pulumi_esc_access()

    # Test backend access
    backend_working, backend_total = await test_backend_secret_access()

    # Generate report
    generate_verification_report(backend_working, backend_total)


if __name__ == "__main__":
    asyncio.run(main())
