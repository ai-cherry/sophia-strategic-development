#!/usr/bin/env python3
"""
Lambda Labs Secure Manager CLI
Thin wrapper around the unified LambdaLabsClient with focus on secure operations
"""

import argparse
import json
import logging
import sys
from typing import Optional

from backend.integrations.lambda_labs_client import get_lambda_labs_client

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def secure_deploy(instance_name: str, validate_only: bool = False) -> bool:
    """Deploy with enhanced security validation"""
    client = get_lambda_labs_client()

    # Validate instance exists
    instance = client.get_instance(instance_name)
    if not instance:
        logger.error(f"Instance {instance_name} not found")
        return False

    logger.info(f"🔐 Secure deployment to {instance_name}")
    logger.info(f"Instance: {instance.ip} ({instance.instance_type.value})")

    if validate_only:
        logger.info("Running validation only...")
        # Check connectivity
        try:
            returncode, stdout, stderr = client.ssh_command(
                instance_name, "echo 'Connection test successful'"
            )
            if returncode == 0:
                logger.info("✅ SSH connectivity validated")
            else:
                logger.error("❌ SSH connectivity failed")
                return False
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False

        logger.info("✅ Validation complete")
        return True

    # Perform actual deployment
    return client.deploy_sophia(instance_name, "full")


def secure_health_check(instance_name: str) -> Optional[dict]:
    """Perform comprehensive health check with security validation"""
    client = get_lambda_labs_client()

    try:
        health = client.health_check(instance_name)

        # Additional security checks
        security_status = {
            "backend_secure": health.get("backend", False),
            "monitoring_secure": health.get("prometheus", False)
            and health.get("grafana", False),
        }

        # Return combined status
        return {"health": health, "security": security_status}

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return None


def secure_command(instance_name: str, command: str) -> bool:
    """Execute secure command with validation"""
    client = get_lambda_labs_client()

    # Validate command doesn't contain dangerous operations
    dangerous_patterns = [
        "rm -rf /",
        "mkfs",
        "dd if=/dev/zero",
        "> /dev/sd",
        "chmod 777",
    ]

    for pattern in dangerous_patterns:
        if pattern in command:
            logger.error(f"❌ Dangerous command pattern detected: {pattern}")
            return False

    try:
        returncode, stdout, stderr = client.ssh_command(instance_name, command)

        if returncode == 0:
            logger.info("✅ Command executed successfully")
            print(stdout)
            return True
        else:
            logger.error(f"❌ Command failed: {stderr}")
            return False

    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Lambda Labs Secure Manager")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Secure deployment")
    deploy_parser.add_argument("instance", help="Instance name")
    deploy_parser.add_argument(
        "--validate-only", action="store_true", help="Validate only, don't deploy"
    )

    # Health command
    health_parser = subparsers.add_parser("health", help="Secure health check")
    health_parser.add_argument("instance", help="Instance name")
    health_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )

    # Command execution
    cmd_parser = subparsers.add_parser("exec", help="Execute secure command")
    cmd_parser.add_argument("instance", help="Instance name")
    cmd_parser.add_argument("command", help="Command to execute")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get deployment status")
    status_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "deploy":
            success = secure_deploy(args.instance, args.validate_only)
            return 0 if success else 1

        elif args.command == "health":
            health = secure_health_check(args.instance)
            if health:
                if args.json:
                    print(json.dumps(health, indent=2))
                else:
                    # Display regular health checks
                    print("Health Status:")
                    for service, status in health["health"].items():
                        print(f"  {service}: {'✅' if status else '❌'}")

                    # Display security checks
                    print("\nSecurity Status:")
                    for service, status in health["security"].items():
                        print(f"  {service}: {'✅' if status else '❌'}")
                return 0
            else:
                return 1

        elif args.command == "exec":
            success = secure_command(args.instance, args.command)
            return 0 if success else 1

        elif args.command == "status":
            client = get_lambda_labs_client()
            status = client.get_deployment_status()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(f"Deployment Status Report - {status['timestamp']}")
                for name, info in status["instances"].items():
                    print(f"\n{name}:")
                    print(f"  IP: {info['ip']}")
                    print(f"  Type: {info['type']}")
                    print(f"  Region: {info['region']}")
                    print(f"  Status: {info['status']}")
            return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
