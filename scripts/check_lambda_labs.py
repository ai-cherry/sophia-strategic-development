#!/usr/bin/env python3
"""Check Lambda Labs instances status"""

import os
from datetime import datetime

import requests

# Lambda Labs API configuration
API_KEY = os.environ.get("LAMBDA_LABS_API_KEY")
API_URL = "https://cloud.lambdalabs.com/api/v1"


def check_instances():
    """Check Lambda Labs instances"""
    if not API_KEY:
        print("❌ LAMBDA_LABS_API_KEY not set")
        return

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        # Get instances
        response = requests.get(f"{API_URL}/instances", headers=headers)

        if response.status_code == 200:
            instances = response.json().get("data", [])

            print(f"🖥️  Lambda Labs Instances ({len(instances)} total)")
            print("=" * 60)

            for instance in instances:
                print(f"\nInstance: {instance.get('name', 'Unknown')}")
                print(f"  ID: {instance.get('id')}")
                print(f"  Type: {instance.get('instance_type_name')}")
                print(f"  Status: {instance.get('status')}")
                print(f"  IP: {instance.get('ip', 'N/A')}")
                print(f"  Region: {instance.get('region_name')}")
                print(f"  Created: {instance.get('created_at')}")

                # Check if it's a Sophia AI instance
                if "sophia" in instance.get("name", "").lower():
                    print("  ✅ This is a Sophia AI instance")
        else:
            print(f"❌ Failed to get instances: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error checking instances: {e}")


def check_ssh_keys():
    """Check SSH keys"""
    if not API_KEY:
        return

    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(f"{API_URL}/ssh-keys", headers=headers)

        if response.status_code == 200:
            keys = response.json().get("data", [])
            print(f"\n🔑 SSH Keys ({len(keys)} total)")
            print("=" * 60)

            for key in keys:
                print(f"  - {key.get('name')}: {key.get('public_key')[:50]}...")
        else:
            print(f"❌ Failed to get SSH keys: {response.status_code}")

    except Exception as e:
        print(f"❌ Error checking SSH keys: {e}")


if __name__ == "__main__":
    print("🔍 Checking Lambda Labs Status")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    check_instances()
    check_ssh_keys()
