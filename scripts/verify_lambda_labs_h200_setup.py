#!/usr/bin/env python3
"""
Lambda Labs H200 Setup Verification Script
Verifies all components are properly configured before Kubernetes deployment
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import requests

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class LambdaLabsH200Verifier:
    """Verifies Lambda Labs GH200 GPU setup for Sophia AI"""

    def __init__(self):
        self.api_key = os.getenv("LAMBDA_LABS_API_KEY")
        self.results = {
            "account": {},
            "instances": {},
            "network": {},
            "storage": {},
            "gpu": {},
            "secrets": {},
            "monitoring": {},
        }
        self.instance_ips = []

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{text.center(60)}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")

    def check_mark(self, status: bool) -> str:
        """Return colored checkmark or X"""
        return f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"

    def verify_api_credentials(self) -> bool:
        """Verify Lambda Labs API credentials"""
        self.print_header("VERIFYING API CREDENTIALS")

        if not self.api_key:
            print(f"{RED}❌ LAMBDA_LABS_API_KEY not set in environment{RESET}")
            return False

        try:
            response = requests.get(
                "https://cloud.lambdalabs.com/api/v1/instance-types",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if response.status_code == 200:
                print(f"{GREEN}✅ API Key valid and authenticated{RESET}")
                self.results["account"]["api_valid"] = True
                return True
            else:
                print(f"{RED}❌ API Key invalid: {response.status_code}{RESET}")
                self.results["account"]["api_valid"] = False
                return False

        except Exception as e:
            print(f"{RED}❌ API connection failed: {e}{RESET}")
            self.results["account"]["api_valid"] = False
            return False

    def verify_h200_availability(self) -> bool:
        """Check if H200 instances are available"""
        self.print_header("CHECKING H200 AVAILABILITY")

        try:
            response = requests.get(
                "https://cloud.lambdalabs.com/api/v1/instance-types",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if response.status_code == 200:
                instance_types = response.json().get("data", [])
                h200_types = [
                    inst
                    for inst in instance_types
                    if "h200" in inst.get("name", "").lower()
                ]

                if h200_types:
                    print(f"{GREEN}✅ H200 instances available:{RESET}")
                    for inst in h200_types:
                        price = inst["instance_type"]["price_cents_per_hour"] / 100
                        print(f"   - {inst['name']}: ${price:.2f}/hour")
                    self.results["instances"]["h200_available"] = True
                    return True
                else:
                    # Check for alternatives
                    print(
                        f"{YELLOW}⚠️  H200 not available, checking alternatives:{RESET}"
                    )
                    gpu_types = [
                        inst
                        for inst in instance_types
                        if inst["instance_type"]["description"].get("gpu_count", 0) > 0
                    ]

                    if gpu_types:
                        print(f"{YELLOW}Alternative GPU instances:{RESET}")
                        for inst in gpu_types[:5]:  # Show top 5
                            gpu_mem = inst["instance_type"]["description"].get(
                                "gpu_memory_gb", 0
                            )
                            price = inst["instance_type"]["price_cents_per_hour"] / 100
                            print(
                                f"   - {inst['name']}: {gpu_mem}GB @ ${price:.2f}/hour"
                            )

                    self.results["instances"]["h200_available"] = False
                    return False

        except Exception as e:
            print(f"{RED}❌ Failed to check instance availability: {e}{RESET}")
            self.results["instances"]["h200_available"] = False
            return False

    def verify_running_instances(self) -> bool:
        """Verify H200 instances are running"""
        self.print_header("VERIFYING RUNNING INSTANCES")

        try:
            response = requests.get(
                "https://cloud.lambdalabs.com/api/v1/instances",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if response.status_code == 200:
                instances = response.json().get("data", [])
                h200_instances = [
                    inst
                    for inst in instances
                    if "h200" in inst.get("instance_type", {}).get("name", "").lower()
                    and inst.get("name", "").startswith("sophia-ai-h200")
                ]

                if len(h200_instances) >= 3:
                    print(
                        f"{GREEN}✅ Found {len(h200_instances)} H200 instances:{RESET}"
                    )

                    for inst in h200_instances:
                        status = inst.get("status", "unknown")
                        ip = inst.get("ip", "N/A")
                        name = inst.get("name", "unknown")

                        status_icon = "🟢" if status == "active" else "🔴"
                        print(f"   {status_icon} {name}: {ip} ({status})")

                        if status == "active" and ip != "N/A":
                            self.instance_ips.append(ip)

                    self.results["instances"]["count"] = len(h200_instances)
                    self.results["instances"]["running"] = True
                    return True
                else:
                    print(
                        f"{RED}❌ Only {len(h200_instances)} instances found (need 3){RESET}"
                    )
                    self.results["instances"]["count"] = len(h200_instances)
                    self.results["instances"]["running"] = False
                    return False

        except Exception as e:
            print(f"{RED}❌ Failed to check running instances: {e}{RESET}")
            return False

    def verify_ssh_access(self) -> bool:
        """Verify SSH access to instances"""
        self.print_header("VERIFYING SSH ACCESS")

        ssh_key_path = Path.home() / ".ssh" / "sophia_h200_key"

        if not ssh_key_path.exists():
            print(f"{RED}❌ SSH key not found at {ssh_key_path}{RESET}")
            self.results["network"]["ssh_key"] = False
            return False

        print(f"{GREEN}✅ SSH key found at {ssh_key_path}{RESET}")

        # Test SSH to each instance
        success_count = 0
        for ip in self.instance_ips[:3]:  # Test first 3
            try:
                result = subprocess.run(
                    [
                        "ssh",
                        "-o",
                        "ConnectTimeout=5",
                        "-o",
                        "StrictHostKeyChecking=no",
                        "-i",
                        str(ssh_key_path),
                        f"ubuntu@{ip}",
                        'echo "SSH OK"',
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0 and "SSH OK" in result.stdout:
                    print(f"   {GREEN}✅ SSH to {ip} successful{RESET}")
                    success_count += 1
                else:
                    print(f"   {RED}❌ SSH to {ip} failed{RESET}")

            except Exception as e:
                print(f"   {RED}❌ SSH to {ip} error: {e}{RESET}")

        self.results["network"]["ssh_access"] = success_count == len(
            self.instance_ips[:3]
        )
        return self.results["network"]["ssh_access"]

    def verify_gpu_configuration(self) -> bool:
        """Verify GPU configuration on instances"""
        self.print_header("VERIFYING GPU CONFIGURATION")

        if not self.instance_ips:
            print(f"{RED}❌ No instance IPs available for GPU check{RESET}")
            return False

        ssh_key_path = Path.home() / ".ssh" / "sophia_h200_key"
        master_ip = self.instance_ips[0]

        try:
            # Check nvidia-smi on master node
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-i",
                    str(ssh_key_path),
                    f"ubuntu@{master_ip}",
                    "nvidia-smi --query-gpu=name,memory.total,driver_version,cuda_version --format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                gpu_info = result.stdout.strip()
                print(f"{GREEN}✅ GPU detected on master node:{RESET}")
                print(f"   {gpu_info}")

                # Parse GPU info
                if "H200" in gpu_info or "H100" in gpu_info:
                    self.results["gpu"]["type"] = "H200/H100"
                    self.results["gpu"]["configured"] = True

                    # Check CUDA version
                    if "12.3" in gpu_info or "12.4" in gpu_info:
                        print(f"   {GREEN}✅ CUDA 12.3+ installed{RESET}")
                        self.results["gpu"]["cuda_correct"] = True
                    else:
                        print(f"   {YELLOW}⚠️  CUDA version may need update{RESET}")
                        self.results["gpu"]["cuda_correct"] = False

                    return True
                else:
                    print(
                        f"   {YELLOW}⚠️  GPU is not H200 but may be compatible{RESET}"
                    )
                    self.results["gpu"]["type"] = "Other"
                    self.results["gpu"]["configured"] = True
                    return True

            else:
                print(f"{RED}❌ Failed to detect GPU: {result.stderr}{RESET}")
                return False

        except Exception as e:
            print(f"{RED}❌ GPU verification failed: {e}{RESET}")
            return False

    def verify_environment_secrets(self) -> bool:
        """Verify all required environment variables are set"""
        self.print_header("VERIFYING ENVIRONMENT SECRETS")

        required_vars = [
            "LAMBDA_LABS_API_KEY",
            "LAMBDA_LABS_SSH_KEY_NAME",
            "LAMBDA_LABS_REGION",
            "LAMBDA_LABS_INSTANCE_TYPE",
            "LAMBDA_LABS_CLUSTER_SIZE",
            "LAMBDA_LABS_MAX_CLUSTER_SIZE",
        ]

        missing = []
        for var in required_vars:
            if os.getenv(var):
                print(f"   {GREEN}✅ {var} is set{RESET}")
            else:
                print(f"   {RED}❌ {var} is missing{RESET}")
                missing.append(var)

        self.results["secrets"]["missing"] = missing
        self.results["secrets"]["complete"] = len(missing) == 0

        return len(missing) == 0

    def generate_summary_report(self):
        """Generate summary report"""
        self.print_header("SETUP VERIFICATION SUMMARY")

        # Overall status
        all_checks = [
            self.results.get("account", {}).get("api_valid", False),
            self.results.get("instances", {}).get("running", False),
            self.results["network"].get("ssh_access", False),
            self.results.get("gpu", {}).get("configured", False),
            self.results.get("secrets", {}).get("complete", False),
        ]

        overall_ready = all(all_checks)

        print(
            f"Overall Status: {'READY FOR KUBERNETES' if overall_ready else 'NOT READY'}"
        )
        print("\nChecklist:")
        print(
            f"  {self.check_mark(self.results.get('account', {}).get('api_valid', False))} API Credentials"
        )
        print(
            f"  {self.check_mark(self.results.get('instances', {}).get('h200_available', False))} H200 Availability"
        )
        print(
            f"  {self.check_mark(self.results.get('instances', {}).get('running', False))} 3+ Instances Running"
        )
        print(
            f"  {self.check_mark(self.results['network'].get('ssh_access', False))} SSH Access"
        )
        print(
            f"  {self.check_mark(self.results.get('gpu', {}).get('configured', False))} GPU Configuration"
        )
        print(
            f"  {self.check_mark(self.results.get('gpu', {}).get('cuda_correct', False))} CUDA 12.3+"
        )
        print(
            f"  {self.check_mark(self.results.get('secrets', {}).get('complete', False))} Environment Secrets"
        )

        # Save results
        results_file = f"lambda_labs_h200_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Detailed results saved to: {results_file}")

        if overall_ready:
            print(f"\n{GREEN}✅ Lambda Labs H200 setup is COMPLETE!{RESET}")
            print("You can now proceed with Kubernetes deployment.")

            if self.instance_ips:
                print("\nInstance IPs for Kubernetes setup:")
                print(f"  Master: {self.instance_ips[0]}")
                for i, ip in enumerate(self.instance_ips[1:3], 1):
                    print(f"  Worker {i}: {ip}")
        else:
            print(f"\n{RED}❌ Setup incomplete. Please address the issues above.{RESET}")

            # Provide specific next steps
            print(f"\n{YELLOW}Next Steps:{RESET}")
            if not self.results.get("account", {}).get("api_valid", False):
                print("  1. Set LAMBDA_LABS_API_KEY environment variable")
            if not self.results.get("instances", {}).get("h200_available", False):
                print("  2. Contact Lambda Labs support for H200 access")
            if not self.results.get("instances", {}).get("running", False):
                print("  3. Launch 3 H200 instances following the setup guide")
            if not self.results["network"].get("ssh_access", False):
                print("  4. Configure SSH key and test access")
            if not self.results.get("secrets", {}).get("complete", False):
                print("  5. Set missing environment variables")


def main():
    """Main verification process"""
    print(f"{BLUE}🚀 Lambda Labs H200 Setup Verification for Sophia AI{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    verifier = LambdaLabsH200Verifier()

    # Run all verifications
    verifier.verify_api_credentials()
    verifier.verify_h200_availability()
    verifier.verify_running_instances()

    if verifier.instance_ips:
        verifier.verify_ssh_access()
        verifier.verify_gpu_configuration()

    verifier.verify_environment_secrets()

    # Generate summary
    verifier.generate_summary_report()


if __name__ == "__main__":
    main()
