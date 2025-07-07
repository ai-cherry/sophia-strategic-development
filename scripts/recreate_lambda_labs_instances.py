#!/usr/bin/env python3
"""
Recreate Lambda Labs GH200 instances with correct SSH key.
"""

import json
import os
import time
from datetime import datetime

import requests

# Configuration
API_KEY = os.getenv(
    "LAMBDA_LABS_API_KEY",
    "secret_pulumi_87a092f03b5e4896a56542ed6e07d249.bHCTOCe4mkvm9jiT53DWZpnewReAoGic",
)
API_URL = "https://cloud.lambdalabs.com/api/v1"
SSH_KEY_NAME = "lynn-sophia-key"  # The new key that matches our local key

# Instance configuration
INSTANCE_CONFIG = {
    "region_name": "us-west-3",
    "instance_type_name": "gpu_1x_h100_sxm5",
    "ssh_key_names": [SSH_KEY_NAME],
    "quantity": 1,
}

# Instances to recreate
INSTANCES_TO_RECREATE = [
    {"name": "lynn-sophia-gh200-master-01", "current_id": None},
    {"name": "lynn-sophia-gh200-worker-01", "current_id": None},
    {"name": "lynn-sophia-gh200-worker-02", "current_id": None},
]


def get_headers():
    return {"Authorization": f"Bearer {API_KEY}"}


def list_instances():
    """List all current instances."""
    response = requests.get(f"{API_URL}/instances", headers=get_headers())
    response.raise_for_status()
    return response.json()["data"]


def terminate_instance(instance_id):
    """Terminate a specific instance."""
    response = requests.post(
        f"{API_URL}/instances/{instance_id}/terminate", headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def create_instance(name):
    """Create a new instance."""
    config = INSTANCE_CONFIG.copy()
    config["name"] = name

    response = requests.post(f"{API_URL}/instances", headers=get_headers(), json=config)
    response.raise_for_status()
    return response.json()


def main():
    print("🚀 Lambda Labs GH200 Instance Recreation")
    print("=" * 50)
    print(f"SSH Key: {SSH_KEY_NAME}")
    print(f"Instance Type: {INSTANCE_CONFIG['instance_type_name']}")
    print(f"Region: {INSTANCE_CONFIG['region_name']}")
    print()

    # Get current instances
    print("📋 Getting current instances...")
    current_instances = list_instances()

    # Map instance names to IDs
    for instance in current_instances:
        for target in INSTANCES_TO_RECREATE:
            if instance["name"] == target["name"]:
                target["current_id"] = instance["id"]
                target["current_ip"] = instance["ip"]

    # Display current state
    print("\n📊 Current GH200 Instances:")
    for target in INSTANCES_TO_RECREATE:
        if target.get("current_id"):
            print(
                f"  - {target['name']}: {target.get('current_ip', 'N/A')} (ID: {target['current_id']})"
            )
        else:
            print(f"  - {target['name']}: NOT FOUND")

    # Confirm action
    print("\n⚠️  WARNING: This will terminate and recreate all GH200 instances!")
    print("   - All data on instances will be lost")
    print("   - New instances will have different IP addresses")
    print("   - Cost remains the same ($3,217/month)")

    confirm = input("\nProceed with recreation? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Operation cancelled")
        return

    # Terminate existing instances
    print("\n🗑️  Terminating existing instances...")
    for target in INSTANCES_TO_RECREATE:
        if target.get("current_id"):
            print(f"  - Terminating {target['name']}...")
            try:
                terminate_instance(target["current_id"])
                print("    ✅ Terminated successfully")
            except Exception as e:
                print(f"    ❌ Error: {e}")

    # Wait for termination to complete
    print("\n⏳ Waiting 30 seconds for termination to complete...")
    time.sleep(30)

    # Create new instances
    print("\n🏗️  Creating new instances with correct SSH key...")
    new_instances = []

    for target in INSTANCES_TO_RECREATE:
        print(f"  - Creating {target['name']}...")
        try:
            result = create_instance(target["name"])
            instance_id = result["data"]["instance_ids"][0]
            new_instances.append({"name": target["name"], "id": instance_id})
            print(f"    ✅ Created successfully (ID: {instance_id})")
        except Exception as e:
            print(f"    ❌ Error: {e}")

    # Wait for instances to be ready
    print("\n⏳ Waiting for instances to become active...")
    time.sleep(60)

    # Get final instance details
    print("\n📊 New GH200 Instances:")
    final_instances = list_instances()

    for instance in final_instances:
        for new in new_instances:
            if instance["id"] == new["id"]:
                print(
                    f"  - {instance['name']}: {instance['ip']} (Status: {instance['status']})"
                )

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "action": "recreated_gh200_instances",
        "ssh_key": SSH_KEY_NAME,
        "instances": new_instances,
    }

    with open("lambda_labs_recreation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Instance recreation complete!")
    print("📄 Report saved to: lambda_labs_recreation_report.json")
    print("\n🔑 SSH Access:")
    print("   ssh -i ~/.ssh/lynn_sophia_h200_key ubuntu@<instance_ip>")
    print("\n✅ Script to delete after use: scripts/recreate_lambda_labs_instances.py")


if __name__ == "__main__":
    main()
