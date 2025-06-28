#!/usr/bin/env python3
"""
Secure Pulumi ESC Setup and Management Script for Sophia AI
This script manages all secrets and configuration in Pulumi ESC safely
"""

import getpass
import json
import logging
import subprocess
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from backend.core.security_config import SecretType, SecurityConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PulumiESCManager:
    """Manages Pulumi ESC environment setup and secret management"""

    def __init__(
        self,
        org: str = "scoobyjava-org",
        environment: str = "default/sophia-ai-production",
    ):
        self.org = org
        self.environment = environment
        self.full_env = f"{org}/{environment}"

    def check_pulumi_cli(self) -> bool:
        """Check if Pulumi CLI is installed and authenticated"""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info(f"✅ Pulumi CLI authenticated as: {result.stdout.strip()}")
                return True
            else:
                logger.error(
                    "❌ Pulumi CLI not authenticated. Run 'pulumi login' first."
                )
                return False
        except FileNotFoundError:
            logger.error(
                "❌ Pulumi CLI not found. Install from https://get.pulumi.com/"
            )
            return False

    def check_esc_cli(self) -> bool:
        """Check if ESC CLI is installed"""
        try:
            result = subprocess.run(["esc", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ ESC CLI available: {result.stdout.strip()}")
                return True
            else:
                logger.error("❌ ESC CLI not available.")
                return False
        except FileNotFoundError:
            logger.error(
                "❌ ESC CLI not found. Install from https://get.pulumi.com/esc/install.sh"
            )
            return False

    def environment_exists(self) -> bool:
        """Check if the ESC environment exists"""
        try:
            result = subprocess.run(
                ["esc", "env", "get", self.full_env], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking environment: {e}")
            return False

    def create_environment(self) -> bool:
        """Create the ESC environment"""
        try:
            # Read the template file
            template_path = (
                Path(__file__).parent.parent.parent
                / "pulumi"
                / "esc"
                / "sophia-ai-production.yaml"
            )

            if not template_path.exists():
                logger.error(f"❌ Template file not found: {template_path}")
                return False

            with open(template_path) as f:
                f.read()

            # Create environment using ESC CLI
            result = subprocess.run(
                ["esc", "env", "init", self.full_env], capture_output=True, text=True
            )

            if result.returncode != 0:
                logger.error(f"❌ Failed to create environment: {result.stderr}")
                return False

            # Set the environment definition
            result = subprocess.run(
                ["esc", "env", "set", self.full_env, "--file", str(template_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.error(
                    f"❌ Failed to set environment definition: {result.stderr}"
                )
                return False

            logger.info(f"✅ Created ESC environment: {self.full_env}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating environment: {e}")
            return False

    def set_secret(self, key: str, value: str, secret: bool = True) -> bool:
        """Set a secret or configuration value in ESC"""
        try:
            cmd = ["esc", "env", "set", self.full_env, key, value]
            if secret:
                cmd.append("--secret")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                secret_type = "secret" if secret else "config"
                logger.info(f"✅ Set {secret_type}: {key}")
                return True
            else:
                logger.error(f"❌ Failed to set {key}: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error setting {key}: {e}")
            return False

    def get_secret(self, key: str) -> str | None:
        """Get a secret value from ESC"""
        try:
            result = subprocess.run(
                ["esc", "env", "get", self.full_env, key, "--show-secrets"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None

        except Exception as e:
            logger.error(f"❌ Error getting {key}: {e}")
            return None

    def validate_secrets(self) -> tuple[list[str], list[str]]:
        """Validate all secrets are properly set"""
        missing_secrets = []
        valid_secrets = []

        for secret_key in SecurityConfig.get_secret_keys():
            value = self.get_secret(secret_key)
            if value and not value.startswith("PLACEHOLDER_"):
                valid_secrets.append(secret_key)
            else:
                missing_secrets.append(secret_key)

        return valid_secrets, missing_secrets

    def interactive_secret_setup(self) -> bool:
        """Interactively set up all secrets"""
        logger.info("🔐 Interactive Secret Setup")
        logger.info("=" * 50)

        # Get current secrets status
        valid_secrets, missing_secrets = self.validate_secrets()

        if not missing_secrets:
            logger.info("✅ All secrets are already configured!")
            return True

        logger.info(f"Found {len(missing_secrets)} secrets that need to be configured:")

        for secret_key in missing_secrets:
            config = SecurityConfig.get_secret_config(secret_key)
            if config is None:
                continue

            print(f"\n📝 Setting up: {secret_key}")
            print(f"   Description: {config.description}")
            print(f"   Required: {'Yes' if config.required else 'No'}")
            print(f"   Type: {config.secret_type.value}")

            if not config.required:
                skip = input("   Skip this optional secret? (y/N): ").lower()
                if skip == "y":
                    continue

            # Get secret value securely
            while True:
                if config.secret_type in [SecretType.API_KEY, SecretType.OAUTH_TOKEN]:
                    value = getpass.getpass(f"   Enter {secret_key}: ")
                else:
                    value = getpass.getpass(f"   Enter {secret_key}: ")

                if value.strip():
                    break
                elif config.required:
                    print("   ❌ This secret is required. Please enter a value.")
                else:
                    break

            if value.strip():
                success = self.set_secret(secret_key, value.strip(), secret=True)
                if not success:
                    logger.error(f"❌ Failed to set {secret_key}")
                    return False

        logger.info("✅ Interactive secret setup completed!")
        return True

    def test_secret_loading(self) -> bool:
        """Test that secrets can be loaded by the application"""
        logger.info("🧪 Testing secret loading...")

        try:
            # Import the auto_esc_config to test loading
            from backend.core.auto_esc_config import get_config_value

            test_results = {}
            required_secrets = SecurityConfig.get_required_secrets()

            for secret_key in required_secrets:
                value = get_config_value(secret_key)
                test_results[secret_key] = value is not None and value != ""

            passed = sum(test_results.values())
            total = len(test_results)

            logger.info(f"📊 Secret loading test results: {passed}/{total} passed")

            for secret_key, result in test_results.items():
                status = "✅" if result else "❌"
                logger.info(f"   {status} {secret_key}")

            return passed == total

        except Exception as e:
            logger.error(f"❌ Error testing secret loading: {e}")
            return False

    def export_environment_template(self) -> bool:
        """Export current environment as a template"""
        try:
            template = SecurityConfig.generate_pulumi_esc_template()

            output_path = (
                Path(__file__).parent.parent.parent
                / "pulumi"
                / "esc"
                / "generated-template.yaml"
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                f.write(template)

            logger.info(f"✅ Exported environment template to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Error exporting template: {e}")
            return False

    def cleanup_placeholder_secrets(self) -> bool:
        """Remove any placeholder secrets that shouldn't be there"""
        logger.info("🧹 Cleaning up placeholder secrets...")

        try:
            # Get current environment data
            result = subprocess.run(
                [
                    "esc",
                    "env",
                    "get",
                    self.full_env,
                    "--show-secrets",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.error(f"❌ Failed to get environment data: {result.stderr}")
                return False

            env_data = json.loads(result.stdout)
            values = env_data.get("values", {})

            placeholders_found = []
            for key, value in values.items():
                if isinstance(value, str) and value.startswith("PLACEHOLDER_"):
                    placeholders_found.append(key)

            if placeholders_found:
                logger.warning(
                    f"⚠️  Found {len(placeholders_found)} placeholder values:"
                )
                for key in placeholders_found:
                    logger.warning(f"   - {key}")

                logger.info(
                    "These should be set to real values using the interactive setup."
                )
            else:
                logger.info("✅ No placeholder values found")

            return True

        except Exception as e:
            logger.error(f"❌ Error checking for placeholders: {e}")
            return False


def main():
    """Main function for ESC setup"""
    logger.info("🚀 Sophia AI Pulumi ESC Security Setup")
    logger.info("=" * 60)

    # Initialize manager
    manager = PulumiESCManager()

    # Check prerequisites
    if not manager.check_pulumi_cli():
        sys.exit(1)

    if not manager.check_esc_cli():
        sys.exit(1)

    # Check if environment exists
    if not manager.environment_exists():
        logger.info("🏗️  Environment doesn't exist. Creating...")
        if not manager.create_environment():
            sys.exit(1)
    else:
        logger.info("✅ Environment exists")

    # Interactive menu
    while True:
        print("\n🔐 Pulumi ESC Management Menu:")
        print("1. Interactive Secret Setup")
        print("2. Test Secret Loading")
        print("3. Validate All Secrets")
        print("4. Export Environment Template")
        print("5. Cleanup Placeholder Secrets")
        print("6. Exit")

        choice = input("\nSelect an option (1-6): ").strip()

        if choice == "1":
            manager.interactive_secret_setup()
        elif choice == "2":
            manager.test_secret_loading()
        elif choice == "3":
            valid, missing = manager.validate_secrets()
            logger.info("📊 Validation Results:")
            logger.info(f"   ✅ Valid secrets: {len(valid)}")
            logger.info(f"   ❌ Missing secrets: {len(missing)}")
            if missing:
                logger.info(f"   Missing: {', '.join(missing)}")
        elif choice == "4":
            manager.export_environment_template()
        elif choice == "5":
            manager.cleanup_placeholder_secrets()
        elif choice == "6":
            logger.info("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()
