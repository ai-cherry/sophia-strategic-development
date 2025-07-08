#!/usr/bin/env python3
"""
Deploy Snowflake Infrastructure as Code using Pulumi
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class SnowflakeIaCDeployer:
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.iac_path = self.root_path / "infrastructure" / "snowflake_iac"

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")

        # Check Pulumi CLI
        try:
            result = subprocess.run(
                ["pulumi", "version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✅ Pulumi CLI installed: {result.stdout.strip()}")
            else:
                print(
                    "❌ Pulumi CLI not found. Please install: curl -fsSL https://get.pulumi.com | sh"
                )
                return False
        except FileNotFoundError:
            print(
                "❌ Pulumi CLI not found. Please install: curl -fsSL https://get.pulumi.com | sh"
            )
            return False

        # Check Python
        if sys.version_info < (3, 8):
            print(f"❌ Python 3.8+ required, found {sys.version}")
            return False
        print(f"✅ Python version: {sys.version.split()[0]}")

        # Check if IaC directory exists
        if not self.iac_path.exists():
            print(f"❌ IaC directory not found: {self.iac_path}")
            return False
        print(f"✅ IaC directory found: {self.iac_path}")

        return True

    def setup_virtual_environment(self):
        """Setup Python virtual environment"""
        print("\n🐍 Setting up virtual environment...")

        venv_path = self.iac_path / ".venv"
        if not venv_path.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print("✅ Virtual environment created")
        else:
            print("✅ Virtual environment already exists")

        # Install requirements
        pip_path = venv_path / "bin" / "pip"
        if not pip_path.exists():
            pip_path = venv_path / "Scripts" / "pip.exe"  # Windows

        requirements_path = self.iac_path / "requirements.txt"
        if requirements_path.exists():
            print("📦 Installing dependencies...")
            subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_path)], check=True
            )
            print("✅ Dependencies installed")

    def configure_pulumi(self, stack: str = "dev"):
        """Configure Pulumi stack"""
        print(f"\n⚙️  Configuring Pulumi stack: {stack}")

        os.chdir(self.iac_path)

        # Login to Pulumi (using local backend for simplicity)
        subprocess.run(["pulumi", "login", "--local"], check=True)

        # Select or create stack
        result = subprocess.run(
            ["pulumi", "stack", "ls"], capture_output=True, text=True
        )
        if stack not in result.stdout:
            subprocess.run(["pulumi", "stack", "init", stack], check=True)
            print(f"✅ Created stack: {stack}")
        else:
            subprocess.run(["pulumi", "stack", "select", stack], check=True)
            print(f"✅ Selected stack: {stack}")

    def set_config_values(self):
        """Set Pulumi configuration values"""
        print("\n🔐 Setting configuration values...")

        # Try to get from environment or Pulumi ESC
        from backend.core.auto_esc_config import get_config_value

        configs = {
            "snowflake:account": get_config_value("snowflake_account"),
            "snowflake:username": get_config_value("snowflake_user"),
            "snowflake:role": get_config_value("snowflake_role", "SYSADMIN"),
            "snowflake:warehouse": get_config_value(
                "snowflake_warehouse", "COMPUTE_WH"
            ),
        }

        # Set non-secret configs
        for key, value in configs.items():
            if value:
                subprocess.run(["pulumi", "config", "set", key, value], check=True)
                print(f"✅ Set {key}")

        # Set password as secret
        password = get_config_value("snowflake_password")
        if password:
            subprocess.run(
                ["pulumi", "config", "set", "snowflake:password", password, "--secret"],
                check=True,
            )
            print("✅ Set snowflake:password (secret)")

    def preview_deployment(self) -> bool:
        """Preview the deployment"""
        print("\n👀 Previewing deployment...")

        result = subprocess.run(["pulumi", "preview"], cwd=self.iac_path)

        if result.returncode != 0:
            print("❌ Preview failed")
            return False

        response = input("\n🚀 Proceed with deployment? (y/N): ")
        return response.lower() == "y"

    def deploy(self):
        """Deploy the infrastructure"""
        print("\n🚀 Deploying infrastructure...")

        result = subprocess.run(["pulumi", "up", "--yes"], cwd=self.iac_path)

        if result.returncode == 0:
            print("\n✅ Deployment successful!")

            # Show outputs
            outputs = subprocess.run(
                ["pulumi", "stack", "output", "--json"],
                cwd=self.iac_path,
                capture_output=True,
                text=True,
            )
            if outputs.returncode == 0:
                print("\n📊 Deployment outputs:")
                print(outputs.stdout)
        else:
            print("\n❌ Deployment failed")
            sys.exit(1)

    def run(self, stack: str = "dev", skip_preview: bool = False):
        """Run the deployment process"""
        print("🚀 Snowflake IaC Deployment Tool")
        print("=" * 50)

        if not self.check_prerequisites():
            sys.exit(1)

        try:
            self.setup_virtual_environment()
            self.configure_pulumi(stack)
            self.set_config_values()

            if skip_preview or self.preview_deployment():
                self.deploy()
            else:
                print("\n❌ Deployment cancelled")

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n❌ Deployment interrupted")
            sys.exit(1)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy Snowflake Infrastructure as Code"
    )
    parser.add_argument(
        "--stack", default="dev", help="Pulumi stack name (default: dev)"
    )
    parser.add_argument(
        "--skip-preview", action="store_true", help="Skip preview and deploy directly"
    )

    args = parser.parse_args()

    deployer = SnowflakeIaCDeployer()
    deployer.run(stack=args.stack, skip_preview=args.skip_preview)


if __name__ == "__main__":
    main()
