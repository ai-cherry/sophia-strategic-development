#!/usr/bin/env python3
"""
Fix Lambda Labs SSH access issue.

The GH200 instances were created with a different SSH key than what we have locally.
This script documents the issue and provides solutions.
"""

import json
import os
import subprocess
import sys
from datetime import datetime


def main():
    print("🔧 Lambda Labs SSH Access Fix")
    print("=" * 50)

    # Document the issue
    issue_report = {
        "timestamp": datetime.now().isoformat(),
        "issue": "SSH key mismatch",
        "details": {
            "instances_created_with": "lynn-sophia-h200-key",
            "instances_public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILTp3t8xBshdPge6O5DuJQKwCCW4pvpir6zb0Fty7c4P",
            "local_key_name": "lynn_sophia_h200_key",
            "local_public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID5Oz2Q3EZFGl0Zap+eZaCIn55FfVjpt5Y+lE+t8/pxI",
            "new_key_added": "lynn-sophia-key",
            "new_key_matches_local": True,
        },
        "affected_instances": [
            {"name": "lynn-sophia-gh200-master-01", "ip": "192.222.50.155"},
            {"name": "lynn-sophia-gh200-worker-01", "ip": "192.222.51.100"},
            {"name": "lynn-sophia-gh200-worker-02", "ip": "192.222.51.49"},
        ],
    }

    print("\n📋 Issue Summary:")
    print("- Instances were created with SSH key: lynn-sophia-h200-key")
    print("- This key has a different public key than our local key")
    print("- New key 'lynn-sophia-key' was added but instances still use old key")

    print("\n🚀 Solution Options:")
    print("\n1. **Recreate Instances** (Recommended)")
    print("   - Terminate existing GH200 instances")
    print("   - Create new instances with 'lynn-sophia-key'")
    print("   - This ensures clean setup with correct SSH access")

    print("\n2. **Use Lambda Labs Console**")
    print("   - Log into Lambda Labs dashboard")
    print("   - Navigate to each instance")
    print("   - Add 'lynn-sophia-key' to the instances")
    print("   - This might require instance restart")

    print("\n3. **Find Original Private Key**")
    print("   - The private key might be in GitHub secrets")
    print("   - Check LAMBDA_LABS_SSH_PRIVATE_KEY secret")
    print("   - Use that key for SSH access")

    # Save the report
    report_path = "lambda_labs_ssh_fix_report.json"
    with open(report_path, "w") as f:
        json.dump(issue_report, f, indent=2)

    print(f"\n✅ Report saved to: {report_path}")

    # Check if we should proceed with instance recreation
    print("\n⚠️  To recreate instances with correct SSH key:")
    print("   1. Run: python scripts/recreate_lambda_labs_instances.py")
    print("   2. This will terminate and recreate all GH200 instances")
    print("   3. Estimated time: 5-10 minutes")
    print("   4. Cost: Same ($3,217/month)")

    print("\n✅ Script to delete after use: scripts/fix_lambda_labs_ssh_access.py")


if __name__ == "__main__":
    main()
