#!/usr/bin/env python3
"""Sophia AI Dependency Fixer

This script fixes common dependency issues in the Sophia AI system, including:
1. Pydantic and MCP version compatibility
2. Missing dependencies
3. Version conflicts

Usage:
    python fix_dependencies.py [--requirements requirements.txt]
"""

import logging
import os
import re
import subprocess
import sys
from typing import Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define compatible versions
COMPATIBLE_VERSIONS = {
    "pydantic": "1.10.8",  # Version compatible with MCP
    "mcp": "0.1.0",  # Version compatible with Pydantic
    "certifi": "2023.7.22",  # Version with proper SSL certificates
    "urllib3": "1.26.16",  # Version compatible with requests
    "requests": "2.31.0",  # Latest stable version
    "aiohttp": "3.8.5",  # Latest stable version
    "asyncio": "3.4.3",  # Latest stable version
    "fastapi": "0.100.0",  # Version compatible with Pydantic
    "sqlalchemy": "2.0.19",  # Latest stable version
    "redis": "4.6.0",  # Latest stable version
    "pinecone-client": "2.2.2",  # Latest stable version
    "weaviate-client": "3.24.1",  # Latest stable version
}


def check_installed_packages() -> Dict[str, str]:
    """Check installed packages and their versions"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Failed to list installed packages: {result.stderr}")
            return {}

        import json

        packages = json.loads(result.stdout)

        installed_packages = {}
        for package in packages:
            installed_packages[package["name"].lower()] = package["version"]

        return installed_packages
    except Exception as e:
        logger.error(f"Error checking installed packages: {e}")
        return {}


def parse_requirements(requirements_path: str) -> Dict[str, str]:
    """Parse requirements.txt file"""
    try:
        if not os.path.exists(requirements_path):
            logger.error(f"Requirements file not found: {requirements_path}")
            return {}

        requirements = {}
        with open(requirements_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Handle comments at the end of the line
                if "#" in line:
                    line = line.split("#")[0].strip()

                # Handle options like --no-binary
                if line.startswith("-"):
                    continue

                # Handle requirements with version specifiers
                match = re.match(r"^([a-zA-Z0-9_\-\.]+)([<>=!~]+)(.*)$", line)
                if match:
                    package = match.group(1).lower()
                    operator = match.group(2)
                    version = match.group(3)
                    requirements[package] = f"{operator}{version}"
                else:
                    # Handle requirements without version specifiers
                    requirements[line.lower()] = ""

        return requirements
    except Exception as e:
        logger.error(f"Error parsing requirements file: {e}")
        return {}


def update_requirements(
    requirements_path: str, updated_requirements: Dict[str, str]
) -> bool:
    """Update requirements.txt file with fixed versions"""
    try:
        if not os.path.exists(requirements_path):
            logger.error(f"Requirements file not found: {requirements_path}")
            return False

        # Read the original file to preserve comments and formatting
        with open(requirements_path, "r") as f:
            lines = f.readlines()

        # Update the requirements
        updated_lines = []
        for line in lines:
            original_line = line
            line = line.strip()
            if not line or line.startswith("#"):
                updated_lines.append(original_line)
                continue

            # Handle comments at the end of the line
            comment = ""
            if "#" in line:
                parts = line.split("#", 1)
                line = parts[0].strip()
                comment = f" #{parts[1]}" if len(parts) > 1 else ""

            # Handle options like --no-binary
            if line.startswith("-"):
                updated_lines.append(original_line)
                continue

            # Handle requirements with version specifiers
            match = re.match(r"^([a-zA-Z0-9_\-\.]+)([<>=!~]+)(.*)$", line)
            if match:
                package = match.group(1).lower()
                if package in updated_requirements:
                    updated_lines.append(
                        f"{package}{updated_requirements[package]}{comment}\n"
                    )
                else:
                    updated_lines.append(original_line)
            else:
                # Handle requirements without version specifiers
                package = line.lower()
                if package in updated_requirements:
                    if updated_requirements[package]:
                        updated_lines.append(
                            f"{package}{updated_requirements[package]}{comment}\n"
                        )
                    else:
                        updated_lines.append(original_line)
                else:
                    updated_lines.append(original_line)

        # Write the updated file
        with open(requirements_path, "w") as f:
            f.writelines(updated_lines)

        logger.info(f"Updated requirements file: {requirements_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating requirements file: {e}")
        return False


def install_fixed_dependencies() -> bool:
    """Install fixed dependencies"""
    try:
        # Install compatible versions of key packages
        for package, version in COMPATIBLE_VERSIONS.items():
            logger.info(f"Installing {package}=={version}")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", f"{package}=={version}"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.error(f"Failed to install {package}=={version}: {result.stderr}")
                return False

        logger.info("Installed fixed dependencies")
        return True
    except Exception as e:
        logger.error(f"Error installing fixed dependencies: {e}")
        return False


def check_for_pydantic_mcp_conflict() -> bool:
    """Check for Pydantic and MCP version conflict"""
    installed_packages = check_installed_packages()

    if "pydantic" not in installed_packages:
        logger.warning("Pydantic is not installed")
        return False

    if "mcp" not in installed_packages:
        logger.warning("MCP is not installed")
        return False

    pydantic_version = installed_packages["pydantic"]
    mcp_version = installed_packages["mcp"]

    logger.info(f"Installed Pydantic version: {pydantic_version}")
    logger.info(f"Installed MCP version: {mcp_version}")

    # Check if the installed versions are compatible
    if pydantic_version.startswith("2.") and not mcp_version.startswith("0.2."):
        logger.warning("Pydantic 2.x is not compatible with MCP 0.1.x")
        return True

    return False


def fix_pydantic_mcp_conflict() -> bool:
    """Fix Pydantic and MCP version conflict"""
    try:
        # Downgrade Pydantic to a compatible version
        logger.info(
            f"Downgrading Pydantic to version {COMPATIBLE_VERSIONS['pydantic']}"
        )
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"pydantic=={COMPATIBLE_VERSIONS['pydantic']}",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Failed to downgrade Pydantic: {result.stderr}")
            return False

        # Install compatible MCP version
        logger.info(f"Installing MCP version {COMPATIBLE_VERSIONS['mcp']}")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"mcp=={COMPATIBLE_VERSIONS['mcp']}",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Failed to install MCP: {result.stderr}")
            return False

        logger.info("Fixed Pydantic and MCP version conflict")
        return True
    except Exception as e:
        logger.error(f"Error fixing Pydantic and MCP version conflict: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sophia AI Dependency Fixer")
    parser.add_argument(
        "--requirements",
        default="requirements.txt",
        help="Path to requirements.txt file (default: requirements.txt)",
    )

    args = parser.parse_args()

    print("\n===== Sophia AI Dependency Fixer =====\n")

    # Check installed packages
    installed_packages = check_installed_packages()
    print(f"Found {len(installed_packages)} installed packages")

    # Parse requirements.txt
    requirements = parse_requirements(args.requirements)
    print(f"Found {len(requirements)} requirements in {args.requirements}")

    # Check for Pydantic and MCP version conflict
    if check_for_pydantic_mcp_conflict():
        print("\n⚠️ Detected Pydantic and MCP version conflict")
        print("   This can cause the 'eval_type_backport' import error")

        # Fix Pydantic and MCP version conflict
        if fix_pydantic_mcp_conflict():
            print("\n✅ Fixed Pydantic and MCP version conflict")
        else:
            print("\n❌ Failed to fix Pydantic and MCP version conflict")

    # Update requirements.txt with compatible versions
    updated_requirements = {}
    for package, version in COMPATIBLE_VERSIONS.items():
        if package.lower() in requirements:
            updated_requirements[package.lower()] = f"=={version}"

    if updated_requirements:
        if update_requirements(args.requirements, updated_requirements):
            print(
                f"\n✅ Updated {len(updated_requirements)} requirements in {args.requirements}"
            )
        else:
            print(f"\n❌ Failed to update requirements in {args.requirements}")

    # Install fixed dependencies
    if install_fixed_dependencies():
        print("\n✅ Installed fixed dependencies")
    else:
        print("\n❌ Failed to install fixed dependencies")

    print("\n===== Dependency Fixer Complete =====")
    print("\nTo verify the fix, run:")
    print(
        "   python -c \"import pydantic; print(f'Pydantic version: {pydantic.__version__}')\""
    )
    print("   python -c \"import mcp; print(f'MCP version: {mcp.__version__}')\"")
    print("\nTo run the unified command interface with the fixed dependencies:")
    print('   python unified_command_interface.py "check system status"')


if __name__ == "__main__":
    main()
