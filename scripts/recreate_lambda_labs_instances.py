#!/usr/bin/env python3
"""
Recreate Lambda Labs GH200 instances with correct SSH key.
"""

import contextlib
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
    # Get current instances
    current_instances = list_instances()

    # Map instance names to IDs
    for instance in current_instances:
        for target in INSTANCES_TO_RECREATE:
            if instance["name"] == target["name"]:
                target["current_id"] = instance["id"]
                target["current_ip"] = instance["ip"]

    # Display current state
    for target in INSTANCES_TO_RECREATE:
        if target.get("current_id"):
            pass
        else:
            pass

    # Confirm action

    confirm = input("\nProceed with recreation? (yes/no): ")
    if confirm.lower() != "yes":
        return

    # Terminate existing instances
    for target in INSTANCES_TO_RECREATE:
        if target.get("current_id"):
            with contextlib.suppress(Exception):
                terminate_instance(target["current_id"])

    # Wait for termination to complete
    time.sleep(30)

    # Create new instances
    new_instances = []

    for target in INSTANCES_TO_RECREATE:
        try:
            result = create_instance(target["name"])
            instance_id = result["data"]["instance_ids"][0]
            new_instances.append({"name": target["name"], "id": instance_id})
        except Exception:
            pass

    # Wait for instances to be ready
    time.sleep(60)

    # Get final instance details
    final_instances = list_instances()

    for instance in final_instances:
        for new in new_instances:
            if instance["id"] == new["id"]:
                pass

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "action": "recreated_gh200_instances",
        "ssh_key": SSH_KEY_NAME,
        "instances": new_instances,
    }

    with open("lambda_labs_recreation_report.json", "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
