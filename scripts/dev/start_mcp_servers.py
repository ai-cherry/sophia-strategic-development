#!/usr/bin/env python3
"""Sophia AI MCP Server Starter.

This script starts the MCP servers defined in the mcp_config.json file.
It checks for the required environment variables, validates the Docker Compose
configuration, and starts the MCP servers using Docker Compose.

Usage:
    python start_mcp_servers.py [--config mcp_config.json] [--compose docker compose.mcp.yml]
"""import argparse

import json
import logging
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_mcp_config(config_path: str) -> Dict[str, Any]:
    """Load the MCP configuration from the specified file."""

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading MCP configuration: {e}")
        return {}


def validate_docker_compose(compose_path: str) -> bool:
    """Validate the Docker Compose configuration."""try:.

        result = subprocess.run(
            ["docker", "compose", "-f", compose_path, "config"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Docker Compose configuration is invalid: {result.stderr}")
            return False

        logger.info("Docker Compose configuration is valid")
        return True
    except Exception as e:
        logger.error(f"Error validating Docker Compose configuration: {e}")
        return False


def check_docker_installed() -> bool:
    """Check if Docker is installed and running."""try:.

        result = subprocess.run(["docker", "info"], capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Docker is not running or not installed: {result.stderr}")
            return False

        logger.info("Docker is installed and running")
        return True
    except Exception as e:
        logger.error(f"Error checking Docker installation: {e}")
        return False


def check_docker_compose_installed() -> bool:
    """Check if Docker Compose is installed."""try:.

        result = subprocess.run(
            ["docker", "compose", "--version"], capture_output=True, text=True
        )

        if result.returncode != 0:
            logger.error(f"Docker Compose is not installed: {result.stderr}")
            return False

        logger.info(f"Docker Compose is installed: {result.stdout.strip()}")
        return True
    except Exception as e:
        logger.error(f"Error checking Docker Compose installation: {e}")
        return False


def check_required_env_vars(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set."""required_vars = set().

    missing_vars = []

    # Extract required environment variables from the MCP configuration
    for server in config.get("servers", []):
        for env_var in server.get("environment", []):
            if env_var.startswith("${") and env_var.endswith("}"):
                var_name = env_var[2:-1]
                required_vars.add(var_name)

    # Check if the required environment variables are set
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        return False, missing_vars

    logger.info("All required environment variables are set")
    return True, []


def fix_docker_compose_file(compose_path: str) -> bool:
    """Fix common issues in the Docker Compose file."""try:.

        with open(compose_path, "r") as f:
            content = f.read()

        # Fix the "volumes.slack Additional property depends_on is not allowed" error
        if "volumes:" in content and "depends_on:" in content:
            # This is a simplistic fix - in a real scenario, you'd want to use a YAML parser
            content = content.replace(
                "  volumes:\n    slack:\n      depends_on:",
                "  volumes:\n    slack:\n  depends_on:",
            )

        with open(compose_path, "w") as f:
            f.write(content)

        logger.info(f"Fixed Docker Compose file: {compose_path}")
        return True
    except Exception as e:
        logger.error(f"Error fixing Docker Compose file: {e}")
        return False


def start_mcp_servers(compose_path: str) -> bool:
    """Start the MCP servers using Docker Compose."""try:.

        # Stop any running containers first
        subprocess.run(
            ["docker", "compose", "-f", compose_path, "down"],
            capture_output=True,
            text=True,
        )

        # Start the containers
        result = subprocess.run(
            ["docker", "compose", "-f", compose_path, "up", "-d"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Failed to start MCP servers: {result.stderr}")
            return False

        logger.info("MCP servers started successfully")
        return True
    except Exception as e:
        logger.error(f"Error starting MCP servers: {e}")
        return False


def check_mcp_servers_health(compose_path: str) -> Tuple[bool, Dict[str, str]]:
    """Check the health of the MCP servers."""
    try:
        # Get the list of running containers
        result = subprocess.run(
            ["docker", "compose", "-f", compose_path, "ps"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Failed to get MCP servers status: {result.stderr}")
            return False, {}

        # Parse the output to get the status of each container
        lines = result.stdout.strip().split("\n")
        if len(lines) <= 2:
            logger.error("No MCP servers are running")
            return False, {}

        # Skip the header lines
        container_statuses = {}
        for line in lines[2:]:
            parts = line.split()
            if len(parts) >= 3:
                container_name = parts[0]
                container_status = " ".join(parts[2:])
                container_statuses[container_name] = container_status

        # Check if all containers are running
        all_running = all("Up" in status for status in container_statuses.values())

        if all_running:
            logger.info("All MCP servers are running")
        else:
            logger.warning("Some MCP servers are not running")

        return all_running, container_statuses
    except Exception as e:
        logger.error(f"Error checking MCP servers health: {e}")
        return False, {}


def main():
    parser = argparse.ArgumentParser(description="Sophia AI MCP Server Starter")
    parser.add_argument(
        "--config",
        default="mcp_config.json",
        help="Path to MCP configuration file (default: mcp_config.json)",
    )
    parser.add_argument(
        "--compose",
        default="docker compose.mcp.yml",
        help="Path to Docker Compose file (default: docker compose.mcp.yml)",
    )

    args = parser.parse_args()

    print("\n===== Sophia AI MCP Server Starter =====\n")

    # Check if Docker is installed and running
    if not check_docker_installed():
        print("\n❌ Docker is not installed or not running")
        print("   Please install Docker and start the Docker daemon")
        sys.exit(1)

    # Check if Docker Compose is installed
    if not check_docker_compose_installed():
        print("\n❌ Docker Compose is not installed")
        print("   Please install Docker Compose")
        sys.exit(1)

    # Load the MCP configuration
    config = load_mcp_config(args.config)
    if not config:
        print(f"\n❌ Failed to load MCP configuration from {args.config}")
        sys.exit(1)

    print(f"\n✅ Loaded MCP configuration from {args.config}")
    print(f"   Found {len(config.get('servers', []))} MCP servers")

    # Check if all required environment variables are set
    env_vars_ok, missing_vars = check_required_env_vars(config)
    if not env_vars_ok:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n   Please set these environment variables in your .env file")
        print("   and run the following command to load them:")
        print("   source .env")
        sys.exit(1)

    print("\n✅ All required environment variables are set")

    # Fix common issues in the Docker Compose file
    if not os.path.exists(args.compose):
        print(f"\n❌ Docker Compose file not found: {args.compose}")
        sys.exit(1)

    fix_docker_compose_file(args.compose)

    # Validate the Docker Compose configuration
    if not validate_docker_compose(args.compose):
        print(f"\n❌ Docker Compose configuration is invalid: {args.compose}")
        print("   Please fix the errors and try again")
        sys.exit(1)

    print(f"\n✅ Docker Compose configuration is valid: {args.compose}")

    # Start the MCP servers
    print("\n🚀 Starting MCP servers...")
    if not start_mcp_servers(args.compose):
        print("\n❌ Failed to start MCP servers")
        sys.exit(1)

    print("\n✅ MCP servers started successfully")

    # Wait for the servers to start
    print("\n⏳ Waiting for MCP servers to start...")
    time.sleep(5)

    # Check the health of the MCP servers
    all_running, container_statuses = check_mcp_servers_health(args.compose)

    print("\n===== MCP Servers Status =====")
    for container, status in container_statuses.items():
        status_icon = "✅" if "Up" in status else "❌"
        print(f"{status_icon} {container}: {status}")

    if all_running:
        print("\n✅ All MCP servers are running")
    else:
        print("\n⚠️ Some MCP servers are not running")

    print("\n===== MCP Server Starter Complete =====")
    print("\nTo check the status of the MCP servers:")
    print(f"   docker compose -f {args.compose} ps")
    print("\nTo view the logs of the MCP servers:")
    print(f"   docker compose -f {args.compose} logs")
    print("\nTo stop the MCP servers:")
    print(f"   docker compose -f {args.compose} down")


if __name__ == "__main__":
    main()
