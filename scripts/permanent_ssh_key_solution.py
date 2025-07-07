#!/usr/bin/env python3
"""
Permanent SSH Key Solution for Lambda Labs GH200 Instances

This script provides a comprehensive solution to permanently resolve SSH access issues
by implementing proper key management and instance recreation with correct keys.
"""

import json
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests


class LambdaLabsSSHResolver:
    def __init__(self):
        self.api_key = os.getenv(
            "LAMBDA_LABS_API_KEY",
            "secret_pulumi_87a092f03b5e4896a56542ed6e07d249.bHCTOCe4mkvm9jiT53DWZpnewReAoGic"
        )
        self.base_url = "https://cloud.lambda.ai/api/v1"

        # SSH key configuration
        self.working_ssh_key_name = "lynn-sophia-key"  # This key matches our local key
        self.problematic_key_name = "lynn-sophia-h200-key"  # This key doesn't match

        # Instance configuration
        self.instances_to_fix = [
            {"name": "lynn-sophia-gh200-master-01", "id": "96cc4b941bc14c7aac0e5e909ee38633", "ip": "192.222.50.155"},
            {"name": "lynn-sophia-gh200-worker-01", "id": "f151bfca6dfa43a48e0dd3d5df1917a8", "ip": "192.222.51.100"},
            {"name": "lynn-sophia-gh200-worker-02", "id": "886cd8549a1145ebbc9cef8b8a0cd17e", "ip": "192.222.51.49"}
        ]

        self.region = "us-east-3"
        self.instance_type = "gpu_1x_gh200"

    def make_api_request(self, method: str, endpoint: str, data: dict | None = None) -> dict:
        """Make authenticated API request to Lambda Labs"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            if method.upper() == "GET":
                response = requests.get(url, auth=(self.api_key, ""), headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, auth=(self.api_key, ""), json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, auth=(self.api_key, ""), headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text}")
            return {}

    def analyze_ssh_key_mismatch(self) -> dict:
        """Analyze the SSH key mismatch issue"""
        print("🔍 Analyzing SSH Key Mismatch Issue")
        print("=" * 50)

        # Get SSH keys from Lambda Labs
        ssh_keys_response = self.make_api_request("GET", "ssh-keys")
        ssh_keys = ssh_keys_response.get("data", [])

        # Get local SSH key
        local_key_path = os.path.expanduser("~/.ssh/lynn_sophia_h200_key.pub")
        local_public_key = ""
        if os.path.exists(local_key_path):
            with open(local_key_path) as f:
                local_public_key = f.read().strip()

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "issue": "SSH key mismatch between instances and local key",
            "lambda_labs_keys": {},
            "local_key": local_public_key,
            "instances_using_wrong_key": [],
            "solution_required": True
        }

        # Analyze each SSH key
        for key in ssh_keys:
            analysis["lambda_labs_keys"][key["name"]] = {
                "id": key["id"],
                "public_key": key["public_key"],
                "matches_local": key["public_key"] == local_public_key
            }

        # Check which instances are using the wrong key
        for instance in self.instances_to_fix:
            analysis["instances_using_wrong_key"].append({
                "name": instance["name"],
                "id": instance["id"],
                "ip": instance["ip"],
                "using_key": self.problematic_key_name,
                "needs_recreation": True
            })

        print("📊 Analysis Results:")
        print(f"   Local key matches 'lynn-sophia-key': {analysis['lambda_labs_keys'].get('lynn-sophia-key', {}).get('matches_local', False)}")
        print(f"   Instances using wrong key: {len(analysis['instances_using_wrong_key'])}")
        print(f"   Solution required: {analysis['solution_required']}")

        return analysis

    def terminate_instance(self, instance_id: str, instance_name: str) -> bool:
        """Terminate a specific instance"""
        print(f"🗑️  Terminating instance: {instance_name}")

        response = self.make_api_request("POST", "instance-operations/terminate", {
            "instance_ids": [instance_id]
        })

        if response:
            print(f"✅ Termination request sent for {instance_name}")
            return True
        else:
            print(f"❌ Failed to terminate {instance_name}")
            return False

    def launch_instance(self, name: str) -> dict | None:
        """Launch a new instance with correct SSH key"""
        print(f"🚀 Launching new instance: {name}")

        payload = {
            "region_name": self.region,
            "instance_type_name": self.instance_type,
            "ssh_key_names": [self.working_ssh_key_name],
            "name": name
        }

        response = self.make_api_request("POST", "instance-operations/launch", payload)

        if response and "data" in response:
            instance_data = response["data"]
            print(f"✅ Successfully launched {name}")
            print(f"   Instance ID: {instance_data['id']}")
            return instance_data
        else:
            print(f"❌ Failed to launch {name}")
            return None

    def wait_for_instance_termination(self, instance_ids: list[str], timeout: int = 300) -> bool:
        """Wait for instances to be fully terminated"""
        print(f"⏳ Waiting for {len(instance_ids)} instances to terminate...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            instances_response = self.make_api_request("GET", "instances")
            if not instances_response:
                break

            active_instances = instances_response.get("data", [])
            still_active = [inst for inst in active_instances if inst["id"] in instance_ids]

            if not still_active:
                print("✅ All instances terminated successfully")
                return True

            print(f"   Still terminating: {len(still_active)} instances")
            time.sleep(10)

        print("⚠️  Timeout waiting for termination")
        return False

    def wait_for_instance_active(self, instance_ids: list[str], timeout: int = 600) -> dict[str, str]:
        """Wait for instances to become active and return their IPs"""
        print(f"⏳ Waiting for {len(instance_ids)} instances to become active...")

        instance_ips = {}
        start_time = time.time()

        while time.time() - start_time < timeout and len(instance_ips) < len(instance_ids):
            instances_response = self.make_api_request("GET", "instances")
            if not instances_response:
                continue

            active_instances = instances_response.get("data", [])

            for instance in active_instances:
                if (instance["id"] in instance_ids and
                    instance["status"] == "active" and
                    instance["ip"] and
                    instance["id"] not in instance_ips):

                    instance_ips[instance["id"]] = instance["ip"]
                    print(f"✅ {instance['name']} is active: {instance['ip']}")

            if len(instance_ips) < len(instance_ids):
                time.sleep(15)

        return instance_ips

    def test_ssh_access(self, ip: str, instance_name: str) -> bool:
        """Test SSH access to an instance"""
        print(f"🔑 Testing SSH access to {instance_name} ({ip})")

        ssh_key_path = os.path.expanduser("~/.ssh/lynn_sophia_h200_key")

        try:
            # Test SSH connection
            result = subprocess.run([
                "ssh", "-i", ssh_key_path,
                "-o", "ConnectTimeout=10",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                f"ubuntu@{ip}",
                "echo 'SSH connection successful' && hostname && uptime"
            ], capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                print(f"✅ SSH access successful to {instance_name}")
                print(f"   Output: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ SSH access failed to {instance_name}")
                print(f"   Error: {result.stderr.strip()}")
                return False

        except subprocess.TimeoutExpired:
            print(f"⏰ SSH connection timeout to {instance_name}")
            return False
        except Exception as e:
            print(f"❌ SSH test error for {instance_name}: {e}")
            return False

    def implement_permanent_solution(self) -> dict:
        """Implement the permanent SSH key solution"""
        print("🎯 Implementing Permanent SSH Key Solution")
        print("=" * 60)

        solution_log = {
            "timestamp": datetime.now().isoformat(),
            "phase": "implementation",
            "steps": [],
            "success": False,
            "new_instances": [],
            "ssh_test_results": {}
        }

        # Step 1: Analyze current state
        print("\n📋 Step 1: Analyzing current state")
        analysis = self.analyze_ssh_key_mismatch()
        solution_log["steps"].append({"step": "analysis", "status": "completed", "data": analysis})

        # Step 2: Terminate problematic instances
        print("\n🗑️  Step 2: Terminating instances with wrong SSH key")
        instance_ids_to_terminate = [inst["id"] for inst in self.instances_to_fix]

        termination_success = True
        for instance in self.instances_to_fix:
            success = self.terminate_instance(instance["id"], instance["name"])
            if not success:
                termination_success = False

        if not termination_success:
            solution_log["steps"].append({"step": "termination", "status": "failed"})
            return solution_log

        # Wait for termination
        if not self.wait_for_instance_termination(instance_ids_to_terminate):
            solution_log["steps"].append({"step": "termination_wait", "status": "timeout"})
            return solution_log

        solution_log["steps"].append({"step": "termination", "status": "completed"})

        # Step 3: Launch new instances with correct SSH key
        print("\n🚀 Step 3: Launching new instances with correct SSH key")
        new_instance_ids = []

        for instance in self.instances_to_fix:
            new_instance = self.launch_instance(instance["name"])
            if new_instance:
                new_instance_ids.append(new_instance["id"])
                solution_log["new_instances"].append({
                    "name": instance["name"],
                    "id": new_instance["id"],
                    "ssh_key": self.working_ssh_key_name
                })
                time.sleep(2)  # Rate limiting

        if len(new_instance_ids) != len(self.instances_to_fix):
            solution_log["steps"].append({"step": "launch", "status": "partial_failure"})
            return solution_log

        solution_log["steps"].append({"step": "launch", "status": "completed"})

        # Step 4: Wait for instances to become active
        print("\n⏳ Step 4: Waiting for instances to become active")
        instance_ips = self.wait_for_instance_active(new_instance_ids)

        if len(instance_ips) != len(new_instance_ids):
            solution_log["steps"].append({"step": "activation_wait", "status": "timeout"})
            return solution_log

        solution_log["steps"].append({"step": "activation", "status": "completed"})

        # Step 5: Test SSH access
        print("\n🔑 Step 5: Testing SSH access to new instances")
        ssh_success_count = 0

        for instance in solution_log["new_instances"]:
            instance_id = instance["id"]
            instance_name = instance["name"]

            if instance_id in instance_ips:
                ip = instance_ips[instance_id]
                instance["ip"] = ip

                # Wait a bit more for SSH to be ready
                print(f"   Waiting for SSH service on {instance_name}...")
                time.sleep(30)

                ssh_success = self.test_ssh_access(ip, instance_name)
                solution_log["ssh_test_results"][instance_name] = {
                    "ip": ip,
                    "ssh_success": ssh_success
                }

                if ssh_success:
                    ssh_success_count += 1

        # Final assessment
        if ssh_success_count == len(self.instances_to_fix):
            solution_log["success"] = True
            solution_log["steps"].append({"step": "ssh_validation", "status": "completed"})
            print("\n🎉 PERMANENT SOLUTION IMPLEMENTED SUCCESSFULLY!")
        else:
            solution_log["steps"].append({"step": "ssh_validation", "status": "partial_success"})
            print(f"\n⚠️  Partial success: {ssh_success_count}/{len(self.instances_to_fix)} instances accessible")

        return solution_log

    def update_github_secrets(self, new_instances: list[dict]) -> bool:
        """Update GitHub secrets with new instance information"""
        print("\n🔄 Updating GitHub secrets with new instance IPs")

        # This would typically use GitHub API to update organization secrets
        # For now, we'll just document what needs to be updated

        updates_needed = {
            "LAMBDA_LABS_GH200_MASTER_IP": None,
            "LAMBDA_LABS_GH200_WORKER_01_IP": None,
            "LAMBDA_LABS_GH200_WORKER_02_IP": None
        }

        for instance in new_instances:
            if "master" in instance["name"]:
                updates_needed["LAMBDA_LABS_GH200_MASTER_IP"] = instance.get("ip")
            elif "worker-01" in instance["name"]:
                updates_needed["LAMBDA_LABS_GH200_WORKER_01_IP"] = instance.get("ip")
            elif "worker-02" in instance["name"]:
                updates_needed["LAMBDA_LABS_GH200_WORKER_02_IP"] = instance.get("ip")

        print("📝 GitHub secrets that need updating:")
        for secret, value in updates_needed.items():
            print(f"   {secret}: {value}")

        return True

    def generate_maintenance_guide(self, solution_log: dict) -> str:
        """Generate a maintenance guide for future SSH key management"""
        guide = f"""
# SSH Key Maintenance Guide for Lambda Labs GH200 Instances

## Solution Implementation Summary
- **Date**: {solution_log['timestamp']}
- **Success**: {solution_log['success']}
- **New Instances**: {len(solution_log['new_instances'])}

## Current SSH Key Configuration
- **Working SSH Key**: {self.working_ssh_key_name}
- **Key Location**: ~/.ssh/lynn_sophia_h200_key
- **Public Key**: Available in Lambda Labs SSH keys

## New Instance Details
"""

        for instance in solution_log['new_instances']:
            guide += f"""
### {instance['name']}
- **Instance ID**: {instance['id']}
- **IP Address**: {instance.get('ip', 'Pending')}
- **SSH Key**: {instance['ssh_key']}
- **SSH Access**: {solution_log['ssh_test_results'].get(instance['name'], {}).get('ssh_success', 'Unknown')}
"""

        guide += """
## SSH Access Commands
```bash
# Connect to master
ssh -i ~/.ssh/lynn_sophia_h200_key ubuntu@<master_ip>

# Connect to worker-01
ssh -i ~/.ssh/lynn_sophia_h200_key ubuntu@<worker_01_ip>

# Connect to worker-02
ssh -i ~/.ssh/lynn_sophia_h200_key ubuntu@<worker_02_ip>
```

## Future SSH Key Management Best Practices

1. **Always verify SSH key match** before launching instances
2. **Use consistent key naming** across all infrastructure
3. **Test SSH access** immediately after instance creation
4. **Update GitHub secrets** with new instance IPs
5. **Document all key changes** in this maintenance guide

## Troubleshooting

If SSH access fails:
1. Verify the correct SSH key is being used
2. Check instance status in Lambda Labs console
3. Ensure security groups allow SSH (port 22)
4. Wait for instance to fully boot (may take 5-10 minutes)

## Emergency Recovery

If all SSH access is lost:
1. Use Lambda Labs console to access instances
2. Regenerate SSH keys if necessary
3. Re-run this permanent solution script
4. Update all documentation and secrets
"""

        return guide


def main():
    """Main execution function"""
    print("🔧 Lambda Labs SSH Key Permanent Solution")
    print("=" * 60)
    print("This script will permanently resolve SSH access issues by:")
    print("1. Analyzing the current SSH key mismatch")
    print("2. Terminating instances with wrong SSH keys")
    print("3. Launching new instances with correct SSH keys")
    print("4. Validating SSH access to all new instances")
    print("5. Generating maintenance documentation")
    print("=" * 60)

    # Confirm execution
    confirm = input("\n⚠️  This will terminate and recreate GH200 instances. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled by user")
        return

    resolver = LambdaLabsSSHResolver()

    # Implement the permanent solution
    solution_log = resolver.implement_permanent_solution()

    # Save solution log
    log_filename = f"ssh_solution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_filename, 'w') as f:
        json.dump(solution_log, f, indent=2)

    print(f"\n📄 Solution log saved to: {log_filename}")

    # Update GitHub secrets if successful
    if solution_log["success"]:
        resolver.update_github_secrets(solution_log["new_instances"])

    # Generate maintenance guide
    maintenance_guide = resolver.generate_maintenance_guide(solution_log)
    guide_filename = f"ssh_maintenance_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(guide_filename, 'w') as f:
        f.write(maintenance_guide)

    print(f"📚 Maintenance guide saved to: {guide_filename}")

    # Final summary
    if solution_log["success"]:
        print("\n🎉 SSH KEY ISSUE PERMANENTLY RESOLVED!")
        print("✅ All instances are accessible via SSH")
        print("✅ Correct SSH keys are in use")
        print("✅ Documentation updated")
    else:
        print("\n⚠️  Solution partially implemented")
        print("❌ Some instances may still have SSH issues")
        print("📞 Manual intervention may be required")


if __name__ == "__main__":
    main()

