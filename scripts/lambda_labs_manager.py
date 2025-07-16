#!/usr/bin/env python3
"""
Lambda Labs Instance Manager CLI
Thin wrapper around the unified LambdaLabsClient
"""

import argparse
import json
import logging
import sys

from backend.integrations.lambda_labs_client import get_lambda_labs_client

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Lambda Labs Instance Manager")
    parser.add_argument(
        "command", choices=["list", "deploy", "health", "monitor", "report", "metrics"]
    )
    parser.add_argument("--instance", help="Instance name")
    parser.add_argument(
        "--type",
        default="full",
        choices=["full", "backend-only", "mcp-servers-only", "update-config"],
        help="Deployment type",
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    # Get unified client
    client = get_lambda_labs_client()

    try:
        if args.command == "list":
            instances = client.list_instances()
            if args.json:
                output = [
                    {
                        "name": inst.name,
                        "ip": inst.ip,
                        "type": inst.instance_type.value,
                        "region": inst.region.value,
                        "ssh_login": inst.ssh_login,
                    }
                    for inst in instances
                ]
                print(json.dumps(output, indent=2))
            else:
                for instance in instances:
                    print(
                        f"{instance.name}: {instance.ip} ({instance.instance_type.value}) - {instance.region.value}"
                    )

        elif args.command == "deploy":
            if not args.instance:
                print("Error: --instance required for deploy")
                return 1
            success = client.deploy_sophia(args.instance, args.type)
            if success:
                print("✅ Deployment successful!")
                return 0
            else:
                print("❌ Deployment failed!")
                return 1

        elif args.command == "health":
            if not args.instance:
                print("Error: --instance required for health check")
                return 1
            health = client.health_check(args.instance)
            if args.json:
                print(json.dumps(health, indent=2))
            else:
                for service, status in health.items():
                    print(f"{service}: {'✅' if status else '❌'}")

        elif args.command == "metrics":
            if not args.instance:
                print("Error: --instance required for metrics")
                return 1
            metrics = client.get_instance_metrics(args.instance)
            if args.json:
                print(json.dumps(metrics, indent=2))
            else:
                for key, value in metrics.items():
                    print(f"{key}: {value}")

        elif args.command == "report":
            status = client.get_deployment_status()
            print(json.dumps(status, indent=2))

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
