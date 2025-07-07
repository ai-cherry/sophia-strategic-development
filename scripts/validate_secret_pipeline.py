#!/usr/bin/env python3
"""
Secret Pipeline Validator
Validates the GitHub Secrets → Pulumi ESC → Runtime pipeline
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional  # Added Any


class SecretPipelineValidator:
    def __init__(self):
        self.required_secrets = self._get_required_secrets()
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_stack = "sophia-prod-on-lambda"

    def _get_required_secrets(self) -> list[str]:
        """Get list of all required secrets"""
        return [
            "PULUMI_ACCESS_TOKEN",
            "DOCKER_PERSONAL_ACCESS_TOKEN",
            "LAMBDA_LABS_SSH_KEY",
            "LAMBDA_LABS_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "PORTKEY_API_KEY",
            "OPENROUTER_API_KEY",
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "SLACK_WEBHOOK",
        ]

    def validate_github_secrets(self) -> dict[str, bool]:
        """Validate GitHub organization secrets"""
        results = {}

        for secret in self.required_secrets:
            # Check if secret exists in GitHub Actions environment
            value = os.getenv(secret)
            results[secret] = value is not None and len(value) > 0

        return results

    def validate_pulumi_esc(self) -> dict[str, Any]:  # Changed any to Any
        """Validate Pulumi ESC configuration"""
        try:
            # Check Pulumi ESC environment
            result = subprocess.run(
                ["pulumi", "env", "open", f"{self.pulumi_org}/sophia-ai-production"],
                capture_output=True,
                text=True,
            )

            return {
                "esc_accessible": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None,
            }
        except Exception as e:
            return {"esc_accessible": False, "error": str(e)}

    def validate_runtime_access(self) -> dict[str, Any]:  # Changed any to Any
        """Validate runtime secret access"""
        # This would be run on the deployed instance
        return {"runtime_validation": "Not implemented - requires deployment context"}

    def generate_report(self) -> dict[str, Any]:  # Changed any to Any
        """Generate comprehensive secret validation report"""
        return {
            "timestamp": subprocess.getoutput("date -u +%Y-%m-%dT%H:%M:%SZ"),
            "github_secrets": self.validate_github_secrets(),
            "pulumi_esc": self.validate_pulumi_esc(),
            "runtime_access": self.validate_runtime_access(),
        }


def main():
    validator = SecretPipelineValidator()
    report = validator.generate_report()

    print(json.dumps(report, indent=2))

    # Check for failures
    github_failures = [k for k, v in report["github_secrets"].items() if not v]
    if github_failures:
        print(f"❌ Missing GitHub secrets: {github_failures}")
        return 1

    if not report["pulumi_esc"]["esc_accessible"]:
        print(f"❌ Pulumi ESC not accessible: {report['pulumi_esc']['error']}")
        return 1

    print("✅ Secret pipeline validation passed")
    return 0


if __name__ == "__main__":
    exit(main())
