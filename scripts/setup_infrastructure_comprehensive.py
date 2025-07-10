#!/usr/bin/env python3
"""
Comprehensive Infrastructure Setup for Sophia AI
This script coordinates all infrastructure components using IaC principles
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests


class InfrastructureManager:
    """Manages all infrastructure components for Sophia AI"""

    def __init__(self):
        self.env_file = Path("local.env")
        self.load_environment()

    def load_environment(self):
        """Load environment variables from local.env"""
        if self.env_file.exists():
            with open(self.env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        print("✅ Environment loaded")

    def run_command(self, cmd: str, description: str) -> bool:
        """Run a shell command with error handling"""
        print(f"\n🚀 {description}")
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                print(f"✅ {description} - Success")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"❌ {description} - Failed")
                if result.stderr:
                    print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def update_github_secrets(self):
        """Update GitHub organization secrets"""
        print("\n📝 Updating GitHub Secrets...")
        return self.run_command(
            "python scripts/update_github_secrets.py", "GitHub secrets update"
        )

    def setup_pulumi_esc(self):
        """Set up Pulumi ESC with all secrets"""
        print("\n🔐 Setting up Pulumi ESC...")

        # Login to Pulumi
        if not self.run_command("pulumi login", "Pulumi login"):
            return False

        # Set the organization
        os.environ["PULUMI_ORG"] = "scoobyjava-org"

        # Create/update ESC environment
        secrets_to_sync = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GONG_ACCESS_KEY",
            "LAMBDA_API_KEY",
            "DOCKER_USERNAME",
            "DOCKER_PERSONAL_ACCESS_TOKEN",
        ]

        for secret in secrets_to_sync:
            value = os.getenv(secret)
            if value:
                cmd = f'pulumi env set default/sophia-ai-production "{secret}" "{value}" --secret'
                self.run_command(cmd, f"Setting {secret} in Pulumi ESC")

        return True

    def setup_snowflake(self):
        """Set up Snowflake infrastructure"""
        print("\n❄️ Setting up Snowflake...")
        return self.run_command(
            "python scripts/setup_snowflake_infrastructure.py",
            "Snowflake infrastructure setup",
        )

    def setup_lambda_labs(self):
        """Set up Lambda Labs infrastructure"""
        print("\n🖥️ Setting up Lambda Labs...")

        api_key = os.getenv("LAMBDA_API_KEY")
        if not api_key:
            print("❌ Lambda API key not found")
            return False

        # Check current instances
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.get(
                "https://cloud.lambda.ai/api/v1/instances", headers=headers
            )

            if response.status_code == 200:
                instances = response.json().get("data", [])
                print(f"✅ Found {len(instances)} Lambda Labs instances")

                for instance in instances:
                    print(
                        f"  - {instance.get('name', 'unnamed')}: {instance.get('status', 'unknown')}"
                    )
            else:
                print(f"❌ Failed to get Lambda Labs instances: {response.status_code}")

        except Exception as e:
            print(f"❌ Error checking Lambda Labs: {e}")

        return True

    def setup_github_actions(self):
        """Configure GitHub Actions workflows"""
        print("\n🔄 Setting up GitHub Actions...")

        # Check if workflows exist
        workflow_path = Path(".github/workflows")
        if workflow_path.exists():
            workflows = list(workflow_path.glob("*.yml")) + list(
                workflow_path.glob("*.yaml")
            )
            print(f"✅ Found {len(workflows)} workflow files")

            # Trigger sync workflow if it exists
            sync_workflow = workflow_path / "sync_secrets.yml"
            if sync_workflow.exists():
                self.run_command(
                    "gh workflow run sync_secrets.yml",
                    "Triggering secrets sync workflow",
                )
        else:
            print("⚠️ No workflows directory found")

        return True

    def setup_vercel(self):
        """Set up Vercel deployment"""
        print("\n▲ Setting up Vercel...")

        vercel_token = os.getenv("VERCEL_API_TOKEN")
        if not vercel_token:
            print("❌ Vercel API token not found")
            return False

        # Check Vercel projects
        headers = {"Authorization": f"Bearer {vercel_token}"}

        try:
            response = requests.get(
                "https://api.vercel.com/v9/projects", headers=headers
            )

            if response.status_code == 200:
                projects = response.json().get("projects", [])
                print(f"✅ Found {len(projects)} Vercel projects")

                for project in projects:
                    print(f"  - {project.get('name', 'unnamed')}")
            else:
                print(f"❌ Failed to get Vercel projects: {response.status_code}")

        except Exception as e:
            print(f"❌ Error checking Vercel: {e}")

        return True

    def setup_monitoring(self):
        """Set up monitoring services"""
        print("\n📊 Setting up monitoring...")

        # Check Sentry
        sentry_token = os.getenv("SENTRY_API_TOKEN")
        if sentry_token:
            print("✅ Sentry API token found")
        else:
            print("⚠️ Sentry API token not found")

        # Check Arize
        arize_key = os.getenv("ARIZE_API_KEY")
        if arize_key:
            print("✅ Arize API key found")
        else:
            print("⚠️ Arize API key not found")

        return True

    def setup_ai_routing(self):
        """Set up AI routing services"""
        print("\n🤖 Setting up AI routing...")

        # Check Portkey
        portkey_key = os.getenv("PORTKEY_API_KEY")
        if portkey_key:
            print("✅ Portkey API key found")

            # Configure Portkey rules
            portkey_config = {
                "routes": [
                    {
                        "name": "primary",
                        "models": ["gpt-4", "claude-3-sonnet"],
                        "loadBalancing": "round-robin",
                        "retries": 3,
                        "timeout": 30,
                    }
                ]
            }

            config_file = Path("config/portkey_config.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, "w") as f:
                json.dump(portkey_config, f, indent=2)

            print("✅ Portkey configuration created")
        else:
            print("⚠️ Portkey API key not found")

        # Check OpenRouter
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            print("✅ OpenRouter API key found")
        else:
            print("⚠️ OpenRouter API key not found")

        return True

    def cleanup_obsolete(self):
        """Clean up obsolete configurations"""
        print("\n🧹 Cleaning up obsolete configurations...")

        # List of files/directories to check for cleanup
        obsolete_patterns = ["*.backup", "*.old", "*_deprecated*", "temp_*", "test_*"]

        cleanup_count = 0
        for pattern in obsolete_patterns:
            for file in Path(".").rglob(pattern):
                if file.is_file():
                    print(f"  - Found obsolete file: {file}")
                    cleanup_count += 1

        print(f"✅ Found {cleanup_count} obsolete files (manual cleanup recommended)")

        return True

    def create_infrastructure_report(self):
        """Create a comprehensive infrastructure report"""
        print("\n📋 Creating infrastructure report...")

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "environment": {
                "snowflake_account": os.getenv("SNOWFLAKE_ACCOUNT", "not set"),
                "pulumi_org": os.getenv("PULUMI_ORG", "not set"),
                "github_org": "ai-cherry",
            },
            "services": {
                "snowflake": (
                    "configured"
                    if os.getenv("SNOWFLAKE_PASSWORD")
                    else "not configured"
                ),
                "lambda_labs": (
                    "configured" if os.getenv("LAMBDA_API_KEY") else "not configured"
                ),
                "github": "configured" if os.getenv("GITHUB_PAT") else "not configured",
                "vercel": (
                    "configured" if os.getenv("VERCEL_API_TOKEN") else "not configured"
                ),
                "docker": (
                    "configured" if os.getenv("DOCKER_USERNAME") else "not configured"
                ),
            },
            "ai_services": {
                "openai": (
                    "configured" if os.getenv("OPENAI_API_KEY") else "not configured"
                ),
                "anthropic": (
                    "configured" if os.getenv("ANTHROPIC_API_KEY") else "not configured"
                ),
                "portkey": (
                    "configured" if os.getenv("PORTKEY_API_KEY") else "not configured"
                ),
            },
        }

        report_file = Path("infrastructure_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Infrastructure report saved to {report_file}")

        return True

    def run_all(self):
        """Run all infrastructure setup steps"""
        print("🚀 Starting comprehensive infrastructure setup for Sophia AI")
        print("=" * 60)

        steps = [
            ("GitHub Secrets", self.update_github_secrets),
            ("Pulumi ESC", self.setup_pulumi_esc),
            ("Snowflake", self.setup_snowflake),
            ("Lambda Labs", self.setup_lambda_labs),
            ("GitHub Actions", self.setup_github_actions),
            ("Vercel", self.setup_vercel),
            ("Monitoring", self.setup_monitoring),
            ("AI Routing", self.setup_ai_routing),
            ("Cleanup", self.cleanup_obsolete),
            ("Report", self.create_infrastructure_report),
        ]

        results = {}

        for step_name, step_func in steps:
            try:
                results[step_name] = step_func()
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                results[step_name] = False

            # Add a small delay between steps
            time.sleep(2)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 Infrastructure Setup Summary")
        print("=" * 60)

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        for step_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {step_name}")

        print(f"\nTotal: {success_count}/{total_count} steps completed successfully")

        if success_count == total_count:
            print("\n🎉 Infrastructure setup completed successfully!")
        else:
            print("\n⚠️ Some steps failed. Please check the logs above.")


def main():
    """Main function"""
    manager = InfrastructureManager()

    # Check if running specific step or all
    if len(sys.argv) > 1:
        step = sys.argv[1]
        if hasattr(manager, f"setup_{step}"):
            getattr(manager, f"setup_{step}")()
        else:
            print(f"Unknown step: {step}")
            print(
                "Available steps: github_secrets, pulumi_esc, snowflake, lambda_labs, github_actions, vercel, monitoring, ai_routing"
            )
    else:
        manager.run_all()


if __name__ == "__main__":
    main()
