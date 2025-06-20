#!/usr/bin/env python3
"""Sophia AI Repository Setup Script

This script automates the setup of a new Sophia AI repository with all the necessary
secrets and configurations. It:

1. Creates a new directory for the repository
2. Initializes a Git repository
3. Copies the secrets_manager.py script
4. Imports secrets from a master .env file or Pulumi ESC
5. Sets up the necessary configuration files
6. Creates a README.md file with setup instructions

Usage:
    python setup_new_repo.py --name sophia-new-repo [--source-env /path/to/master.env] [--from-pulumi]
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from typing import List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_command(command: List[str], cwd: Optional[str] = None) -> bool:
    """Run a command and return True if successful"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)

        if result.returncode != 0:
            logger.error(f"Command failed: {' '.join(command)}")
            logger.error(f"Error: {result.stderr}")
            return False

        return True
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return False


def create_directory(path: str) -> bool:
    """Create a directory if it doesn't exist"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def copy_file(source: str, destination: str) -> bool:
    """Copy a file from source to destination"""
    try:
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        logger.error(f"Error copying file from {source} to {destination}: {e}")
        return False


def create_readme(repo_path: str, repo_name: str) -> bool:
    """Create a README.md file with setup instructions"""
    try:
        readme_path = os.path.join(repo_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {repo_name}\n\n")
            f.write("## Setup Instructions\n\n")
            f.write("### 1. Clone the repository\n\n")
            f.write("```bash\n")
            f.write("git clone <repository-url>\n")
            f.write(f"cd {repo_name}\n")
            f.write("```\n\n")
            f.write("### 2. Set up environment variables\n\n")
            f.write("```bash\n")
            f.write("# Generate a template .env file\n")
            f.write("./secrets_manager.py generate-template\n\n")
            f.write("# Edit the template file with your secrets\n")
            f.write("cp env.template .env\n")
            f.write("nano .env  # or use your preferred editor\n\n")
            f.write("# Validate your configuration\n")
            f.write("./secrets_manager.py validate\n")
            f.write("```\n\n")
            f.write("### 3. Sync secrets to Pulumi ESC and GitHub\n\n")
            f.write("```bash\n")
            f.write("# Sync all secrets to all destinations\n")
            f.write("./secrets_manager.py sync-all\n")
            f.write("```\n\n")
            f.write("### 4. Run the health check\n\n")
            f.write("```bash\n")
            f.write("# Fix SSL certificate issues\n")
            f.write("python3 fix_ssl_certificates.py\n\n")
            f.write("# Run the health check\n")
            f.write('python3 run_with_ssl_fix.py "check system status"\n')
            f.write("```\n\n")
            f.write("### 5. Start the MCP servers\n\n")
            f.write("```bash\n")
            f.write("# Start the MCP servers\n")
            f.write("python3 start_mcp_servers.py\n")
            f.write("```\n\n")
            f.write("## Additional Commands\n\n")
            f.write("### Secrets Management\n\n")
            f.write("```bash\n")
            f.write("# Detect missing environment variables\n")
            f.write("./secrets_manager.py detect-missing\n\n")
            f.write("# Import from .env file\n")
            f.write("./secrets_manager.py import-from-env --env-file .env\n\n")
            f.write("# Export to .env file\n")
            f.write("./secrets_manager.py export-to-env --env-file .env.new\n\n")
            f.write("# Sync to Pulumi ESC\n")
            f.write("./secrets_manager.py sync-to-pulumi\n\n")
            f.write("# Sync to GitHub\n")
            f.write("./secrets_manager.py sync-to-github\n\n")
            f.write("# Validate configuration\n")
            f.write("./secrets_manager.py validate\n\n")
            f.write("# Generate template\n")
            f.write(
                "./secrets_manager.py generate-template --output-file env.template\n\n"
            )
            f.write("# Sync all\n")
            f.write("./secrets_manager.py sync-all\n")
            f.write("```\n\n")
            f.write("## Troubleshooting\n\n")
            f.write(
                "If you encounter any issues, please refer to the [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) file for detailed troubleshooting steps.\n"
            )

        return True
    except Exception as e:
        logger.error(f"Error creating README.md: {e}")
        return False


def create_gitignore(repo_path: str) -> bool:
    """Create a .gitignore file"""
    try:
        gitignore_path = os.path.join(repo_path, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("# Environment variables\n")
            f.write(".env\n")
            f.write(".env.*\n")
            f.write("!.env.example\n")
            f.write("\n")
            f.write("# Python\n")
            f.write("__pycache__/\n")
            f.write("*.py[cod]\n")
            f.write("*$py.class\n")
            f.write("*.so\n")
            f.write(".Python\n")
            f.write("env/\n")
            f.write("build/\n")
            f.write("develop-eggs/\n")
            f.write("dist/\n")
            f.write("downloads/\n")
            f.write("eggs/\n")
            f.write(".eggs/\n")
            f.write("lib/\n")
            f.write("lib64/\n")
            f.write("parts/\n")
            f.write("sdist/\n")
            f.write("var/\n")
            f.write("*.egg-info/\n")
            f.write(".installed.cfg\n")
            f.write("*.egg\n")
            f.write("\n")
            f.write("# Virtual Environment\n")
            f.write("venv/\n")
            f.write("ENV/\n")
            f.write("env/\n")
            f.write("sophia_venv/\n")
            f.write("\n")
            f.write("# IDE\n")
            f.write(".idea/\n")
            f.write(".vscode/\n")
            f.write("*.swp\n")
            f.write("*.swo\n")
            f.write("\n")
            f.write("# Logs\n")
            f.write("*.log\n")
            f.write("\n")
            f.write("# Temporary files\n")
            f.write("temp_*\n")
            f.write("*.tmp\n")
            f.write("\n")
            f.write("# Docker\n")
            f.write(".docker/\n")
            f.write("docker-compose.override.yml\n")
            f.write("\n")
            f.write("# Pulumi\n")
            f.write("Pulumi.*.yaml\n")
            f.write("!Pulumi.yaml\n")

        return True
    except Exception as e:
        logger.error(f"Error creating .gitignore: {e}")
        return False


def setup_repository(
    repo_name: str, source_env: Optional[str] = None, from_pulumi: bool = False
) -> bool:
    """Set up a new repository with all the necessary files and configurations"""
    # Create the repository directory
    repo_path = os.path.abspath(repo_name)
    if not create_directory(repo_path):
        return False

    logger.info(f"Created repository directory: {repo_path}")

    # Initialize Git repository
    if not run_command(["git", "init"], cwd=repo_path):
        return False

    logger.info("Initialized Git repository")

    # Copy secrets_manager.py
    if not copy_file(
        "secrets_manager.py", os.path.join(repo_path, "secrets_manager.py")
    ):
        return False

    # Make secrets_manager.py executable
    if not run_command(["chmod", "+x", "secrets_manager.py"], cwd=repo_path):
        return False

    logger.info("Copied and made secrets_manager.py executable")

    # Copy fix_ssl_certificates.py if it exists
    if os.path.exists("fix_ssl_certificates.py"):
        if not copy_file(
            "fix_ssl_certificates.py",
            os.path.join(repo_path, "fix_ssl_certificates.py"),
        ):
            return False
        logger.info("Copied fix_ssl_certificates.py")

    # Copy run_with_ssl_fix.py if it exists
    if os.path.exists("run_with_ssl_fix.py"):
        if not copy_file(
            "run_with_ssl_fix.py", os.path.join(repo_path, "run_with_ssl_fix.py")
        ):
            return False
        logger.info("Copied run_with_ssl_fix.py")

    # Copy start_mcp_servers.py if it exists
    if os.path.exists("start_mcp_servers.py"):
        if not copy_file(
            "start_mcp_servers.py", os.path.join(repo_path, "start_mcp_servers.py")
        ):
            return False
        logger.info("Copied start_mcp_servers.py")

    # Copy SETUP_INSTRUCTIONS.md if it exists
    if os.path.exists("SETUP_INSTRUCTIONS.md"):
        if not copy_file(
            "SETUP_INSTRUCTIONS.md", os.path.join(repo_path, "SETUP_INSTRUCTIONS.md")
        ):
            return False
        logger.info("Copied SETUP_INSTRUCTIONS.md")

    # Create README.md
    if not create_readme(repo_path, repo_name):
        return False

    logger.info("Created README.md")

    # Create .gitignore
    if not create_gitignore(repo_path):
        return False

    logger.info("Created .gitignore")

    # Import secrets from source_env if provided
    if source_env:
        if not os.path.exists(source_env):
            logger.error(f"Source .env file not found: {source_env}")
            return False

        # Copy the source .env file to the repository
        if not copy_file(source_env, os.path.join(repo_path, ".env")):
            return False

        logger.info(f"Copied source .env file from {source_env}")

        # Run secrets_manager.py to validate the configuration
        if not run_command(["./secrets_manager.py", "validate"], cwd=repo_path):
            logger.warning("Validation of imported secrets failed")
        else:
            logger.info("Validated imported secrets")

    # Import secrets from Pulumi ESC if requested
    if from_pulumi:
        # Run secrets_manager.py to import from Pulumi ESC
        if not run_command(["./secrets_manager.py", "sync-to-pulumi"], cwd=repo_path):
            logger.warning("Import from Pulumi ESC failed")
        else:
            logger.info("Imported secrets from Pulumi ESC")

    logger.info(f"Repository setup complete: {repo_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Sophia AI Repository Setup Script")
    parser.add_argument(
        "--name", required=True, help="Name of the repository to create"
    )
    parser.add_argument(
        "--source-env", help="Path to source .env file to import secrets from"
    )
    parser.add_argument(
        "--from-pulumi", action="store_true", help="Import secrets from Pulumi ESC"
    )

    args = parser.parse_args()

    if setup_repository(args.name, args.source_env, args.from_pulumi):
        print(f"\n✅ Repository setup complete: {os.path.abspath(args.name)}")
        print("\nNext steps:")
        print(f"1. cd {args.name}")
        print("2. ./secrets_manager.py validate")
        print("3. ./secrets_manager.py sync-all")
    else:
        print("\n❌ Repository setup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
