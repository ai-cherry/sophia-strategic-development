#!/usr/bin/env python3
"""Sophia AI - Interactive Setup Wizard
Automated environment setup and configuration
"""

import asyncio
import getpass
import json
import os
import subprocess
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class SetupWizard:
    """Interactive setup wizard for Sophia AI environment"""

    def __init__(self):
        self.config = {}
        self.steps_completed = []

    async def run_setup(self) -> bool:
        """Run the complete setup wizard"""
        print("🚀 Welcome to Sophia AI Setup Wizard!")
        print("=" * 50)
        print("This wizard will help you set up your Sophia AI environment.")
        print("Please follow the prompts to configure all components.\n")

        setup_steps = [
            ("Environment Variables", self.setup_environment_variables),
            ("Pulumi Configuration", self.setup_pulumi),
            ("Docker Services", self.setup_docker),
            ("MCP Servers", self.setup_mcp_servers),
            ("Claude Integration", self.setup_claude),
            ("GitHub Integration", self.setup_github),
            ("Cursor IDE", self.setup_cursor_ide),
            ("Final Validation", self.validate_setup),
        ]

        for step_name, step_func in setup_steps:
            print(f"\n📋 Step: {step_name}")
            print("-" * 30)

            try:
                success = await step_func()
                if success:
                    self.steps_completed.append(step_name)
                    print(f"✅ {step_name} completed successfully!")
                else:
                    print(f"❌ {step_name} failed. Please check the configuration.")
                    if not self.ask_continue():
                        return False
            except KeyboardInterrupt:
                print("\n\n⚠️ Setup interrupted by user.")
                return False
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                if not self.ask_continue():
                    return False

        print(
            f"\n🎉 Setup completed! {len(self.steps_completed)}/{len(setup_steps)} steps successful."
        )
        return len(self.steps_completed) == len(setup_steps)

    def ask_continue(self) -> bool:
        """Ask user if they want to continue after an error"""
        response = input("\nDo you want to continue with the setup? (y/n): ").lower()
        return response in ["y", "yes"]

    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} ({default_str}): ").lower()
        if not response:
            return default
        return response in ["y", "yes"]

    def ask_input(self, prompt: str, default: str = "", required: bool = True) -> str:
        """Ask for user input with optional default"""
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "

        while True:
            response = input(full_prompt).strip()
            if response:
                return response
            elif default:
                return default
            elif not required:
                return ""
            else:
                print("This field is required. Please enter a value.")

    def ask_password(self, prompt: str) -> str:
        """Ask for password input (hidden)"""
        return getpass.getpass(f"{prompt}: ")

    async def setup_environment_variables(self) -> bool:
        """Setup environment variables - LEGACY METHOD
        
        🔐 PERMANENT SOLUTION AVAILABLE:
        Use the permanent GitHub organization secrets solution instead:
        
        1. git clone https://github.com/ai-cherry/sophia-main.git
        2. export PULUMI_ORG=scoobyjava-org  
        3. python scripts/setup_permanent_secrets_solution.py
        4. python scripts/test_permanent_solution.py
        
        This method is kept for backward compatibility only.
        """
        print("🚨 LEGACY SETUP DETECTED")
        print("=" * 50)
        print("🔐 PERMANENT SECRET MANAGEMENT SOLUTION AVAILABLE!")
        print("")
        print("Instead of manual setup, use the permanent solution:")
        print("1. export PULUMI_ORG=scoobyjava-org")
        print("2. python scripts/setup_permanent_secrets_solution.py")
        print("3. python scripts/test_permanent_solution.py")
        print("")
        print("All secrets managed automatically via GitHub organization!")
        print("=" * 50)
        
        if not self.ask_yes_no("Continue with legacy manual setup?", False):
            print("✅ Recommended: Use the permanent solution instead!")
            return False

        print("⚠️  Proceeding with legacy manual environment variable setup...")
        print("Note: This method is deprecated and will be removed in future versions.")

        env_vars = {
            "ANTHROPIC_API_KEY": {
                "description": "Anthropic API key for Claude integration",
                "required": True,
                "secret": True,
            },
            "PULUMI_ACCESS_TOKEN": {
                "description": "Pulumi access token for infrastructure management",
                "required": True,
                "secret": True,
            },
            "LINEAR_API_TOKEN": {
                "description": "Linear API token for project management",
                "required": False,
                "secret": True,
            },
            "GONG_CLIENT_ID": {
                "description": "Gong OAuth client ID",
                "required": False,
                "secret": False,
            },
            "GONG_CLIENT_SECRET": {
                "description": "Gong OAuth client secret",
                "required": False,
                "secret": True,
            },
            "SLACK_BOT_TOKEN": {
                "description": "Slack bot token for integration",
                "required": False,
                "secret": True,
            },
        }

        env_file_path = project_root / ".env"
        env_content = []

        if env_file_path.exists():
            print("Found existing .env file. Updating with new values...")
            with open(env_file_path) as f:
                existing_content = f.read()
        else:
            existing_content = ""

        print("\n🔧 Setting up environment variables...")
        for var_name, var_info in env_vars.items():
            if var_name in existing_content:
                print(f"✓ {var_name} already exists in .env file")
                continue

            if var_info["required"]:
                print(f"\n📋 Required: {var_name}")
            else:
                print(f"\n📋 Optional: {var_name}")

            print(f"   Description: {var_info['description']}")

            if var_info["secret"]:
                value = input(f"   Enter {var_name} (will be hidden): ")
            else:
                value = input(f"   Enter {var_name}: ")

            if value.strip():
                env_content.append(f"{var_name}={value.strip()}")
            elif var_info["required"]:
                print(f"❌ {var_name} is required but not provided")
                return False

        # Write updated .env file
        if env_content:
            with open(env_file_path, "a") as f:
                if existing_content and not existing_content.endswith("\n"):
                    f.write("\n")
                f.write("\n".join(env_content) + "\n")

            print(f"✅ Environment variables written to {env_file_path}")
        else:
            print("✅ No new environment variables to add")

        print("\n🚨 IMPORTANT: Consider migrating to the permanent solution!")
        print("Run: python scripts/setup_permanent_secrets_solution.py")
        
        return True

    async def setup_pulumi(self) -> bool:
        """Setup Pulumi configuration"""
        print("Setting up Pulumi configuration...")

        # Check if Pulumi is installed
        try:
            result = subprocess.run(
                ["pulumi", "version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                print("❌ Pulumi is not installed. Please install Pulumi first.")
                print("Visit: https://www.pulumi.com/docs/get-started/install/")
                return False
        except FileNotFoundError:
            print("❌ Pulumi is not installed. Please install Pulumi first.")
            return False

        # Check authentication
        result = subprocess.run(["pulumi", "whoami"], capture_output=True, text=True)
        if result.returncode != 0:
            print("🔐 Pulumi authentication required...")
            token = self.ask_password("Enter your Pulumi access token")

            # Login with token
            login_result = subprocess.run(
                ["pulumi", "login", "--cloud-url", "https://app.pulumi.com"],
                input=token,
                text=True,
                capture_output=True,
            )

            if login_result.returncode != 0:
                print("❌ Pulumi authentication failed")
                return False

        print("✅ Pulumi authentication successful")

        # Setup stack
        if self.ask_yes_no("Do you want to create/select a Pulumi stack?", True):
            stack_name = self.ask_input("Enter stack name", "production")

            # Try to select existing stack or create new one
            select_result = subprocess.run(
                ["pulumi", "stack", "select", stack_name],
                capture_output=True,
                text=True,
                cwd=project_root / "infrastructure",
            )

            if select_result.returncode != 0:
                print(f"Creating new stack: {stack_name}")
                create_result = subprocess.run(
                    ["pulumi", "stack", "init", stack_name],
                    capture_output=True,
                    text=True,
                    cwd=project_root / "infrastructure",
                )

                if create_result.returncode != 0:
                    print(f"❌ Failed to create stack: {create_result.stderr}")
                    return False

        return True

    async def setup_docker(self) -> bool:
        """Setup Docker services"""
        print("Setting up Docker services...")

        # Check if Docker is installed
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                print("❌ Docker is not installed. Please install Docker first.")
                return False
        except FileNotFoundError:
            print("❌ Docker is not installed. Please install Docker first.")
            return False

        # Check if Docker Compose is available
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                print(
                    "❌ Docker Compose is not installed. Please install Docker Compose first."
                )
                return False
        except FileNotFoundError:
            print(
                "❌ Docker Compose is not installed. Please install Docker Compose first."
            )
            return False

        print("✅ Docker and Docker Compose are available")

        if self.ask_yes_no("Do you want to build and start Docker services?", True):
            print("Building Docker images...")
            build_result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.mcp.yml", "build"],
                cwd=project_root,
            )

            if build_result.returncode != 0:
                print("❌ Docker build failed")
                return False

            print("Starting Docker services...")
            up_result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.mcp.yml", "up", "-d"],
                cwd=project_root,
            )

            if up_result.returncode != 0:
                print("❌ Docker services failed to start")
                return False

            print("✅ Docker services started successfully")

        return True

    async def setup_mcp_servers(self) -> bool:
        """Setup MCP servers configuration"""
        print("Setting up MCP servers...")

        mcp_config_path = project_root / "mcp_config.json"

        if mcp_config_path.exists():
            print("✅ MCP configuration file already exists")
            if not self.ask_yes_no(
                "Do you want to update the MCP configuration?", False
            ):
                return True

        # Default MCP configuration
        mcp_config = {
            "mcpServers": {
                "sophia": {
                    "command": "python",
                    "args": ["backend/mcp/sophia_mcp_server.py"],
                    "env": {"PYTHONPATH": str(project_root)},
                },
                "claude": {
                    "command": "python",
                    "args": ["backend/mcp/claude_mcp_server.py"],
                    "env": {
                        "PYTHONPATH": str(project_root),
                        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
                    },
                },
            }
        }

        # Add optional servers based on available tokens
        if os.getenv("LINEAR_API_TOKEN"):
            mcp_config["mcpServers"]["linear"] = {
                "command": "python",
                "args": ["backend/mcp/linear_mcp_server.py"],
                "env": {
                    "PYTHONPATH": str(project_root),
                    "LINEAR_API_TOKEN": os.getenv("LINEAR_API_TOKEN"),
                },
            }

        if os.getenv("GONG_CLIENT_ID"):
            mcp_config["mcpServers"]["gong"] = {
                "command": "python",
                "args": ["backend/mcp/gong_mcp_server.py"],
                "env": {
                    "PYTHONPATH": str(project_root),
                    "GONG_CLIENT_ID": os.getenv("GONG_CLIENT_ID"),
                    "GONG_CLIENT_SECRET": os.getenv("GONG_CLIENT_SECRET", ""),
                },
            }

        if os.getenv("SLACK_BOT_TOKEN"):
            mcp_config["mcpServers"]["slack"] = {
                "command": "python",
                "args": ["backend/mcp/slack_mcp_server.py"],
                "env": {
                    "PYTHONPATH": str(project_root),
                    "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
                },
            }

        # Save MCP configuration
        with open(mcp_config_path, "w") as f:
            json.dump(mcp_config, f, indent=2)

        print(f"✅ MCP configuration saved to {mcp_config_path}")
        return True

    async def setup_claude(self) -> bool:
        """Setup Claude integration"""
        print("Setting up Claude integration...")

        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ ANTHROPIC_API_KEY not found. Please set it first.")
            return False

        # Test Claude API
        try:
            from backend.integrations.claude_integration import claude_integration

            test_result = await claude_integration.test_connection()

            if test_result.get("success"):
                print("✅ Claude API connection successful")
                return True
            else:
                print(
                    f"❌ Claude API test failed: {test_result.get('error', 'Unknown error')}"
                )
                return False
        except Exception as e:
            print(f"❌ Claude integration test failed: {e}")
            return False

    async def setup_github(self) -> bool:
        """Setup GitHub integration"""
        print("Setting up GitHub integration...")

        # Check if gh CLI is installed
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ GitHub CLI (gh) is not installed. Some features may not work.")
                print("Visit: https://cli.github.com/")
                return True  # Not critical for basic functionality
        except FileNotFoundError:
            print("⚠️ GitHub CLI (gh) is not installed. Some features may not work.")
            return True

        # Check authentication
        auth_result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True
        )
        if auth_result.returncode != 0:
            if self.ask_yes_no(
                "GitHub CLI is not authenticated. Do you want to authenticate now?",
                True,
            ):
                login_result = subprocess.run(["gh", "auth", "login"])
                if login_result.returncode != 0:
                    print("❌ GitHub authentication failed")
                    return False

        print("✅ GitHub integration configured")
        return True

    async def setup_cursor_ide(self) -> bool:
        """Setup Cursor IDE integration"""
        print("Setting up Cursor IDE integration...")

        cursor_rules_path = project_root / ".cursorrules"

        if cursor_rules_path.exists():
            print("✅ Cursor rules file already exists")
            return True

        print("❌ .cursorrules file not found")
        print("This file should have been created during the repository setup.")
        print("Please ensure the .cursorrules file exists in the project root.")

        return False

    async def validate_setup(self) -> bool:
        """Validate the complete setup"""
        print("Validating setup...")

        # Run health check
        try:
            from automated_health_check import HealthCheckRunner

            health_checker = HealthCheckRunner()
            results = await health_checker.run_all_checks()

            if results["overall_status"] == "healthy":
                print("✅ All systems are healthy!")
                return True
            else:
                print(f"⚠️ System health: {results['overall_status']}")
                print(f"Health score: {results['health_percentage']:.1f}%")
                return results["health_percentage"] > 70
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False


async def main():
    """Main entry point"""
    wizard = SetupWizard()

    try:
        success = await wizard.run_setup()

        if success:
            print("\n🎉 Sophia AI setup completed successfully!")
            print("\nNext steps:")
            print("1. Open Cursor IDE in this directory")
            print("2. Press Ctrl+L (or Cmd+L) to open the chat")
            print("3. Try a command like: 'Check the health of all services'")
            print("4. Explore the natural language capabilities!")

            print("\n📚 Documentation:")
            print("- API Documentation: docs/API_DOCUMENTATION.md")
            print("- Troubleshooting Guide: docs/TROUBLESHOOTING_GUIDE.md")
            print("- Natural Language Guide: natural_language_interaction_guide.md")
        else:
            print("\n❌ Setup incomplete. Please review the errors above.")
            print("You can run this wizard again to complete the setup.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
