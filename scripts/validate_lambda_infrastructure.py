#!/usr/bin/env python3
"""
Lambda Labs Infrastructure Validation Script

Validates the complete Lambda Labs infrastructure including:
- API connectivity
- Instance status and health
- SSH connectivity
- Secret management pipeline
- Cost monitoring

Usage:
    python scripts/validate_lambda_infrastructure.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List

import requests

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from backend.core.auto_esc_config import get_lambda_labs_config
except ImportError:
    print("⚠️  Warning: Could not import Lambda Labs config")
    get_lambda_labs_config = None


class LambdaLabsValidator:
    """Comprehensive validation for Lambda Labs infrastructure"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "UNKNOWN",
            "api_access": False,
            "instances": {},
            "ssh_connectivity": {},
            "secret_management": False,
            "total_cost": 0.0,
            "recommendations": [],
        }

        # Expected instances with current configuration
        self.expected_instances = {
            "sophia-ai-core": {
                "ip": "192.222.58.232",
                "instance_type": "gpu_1x_gh200",
                "cost_per_hour": 1.49,
                "purpose": "Core AI Services & Snowflake Cortex",
                "critical": True,
            },
            "sophia-production-instance": {
                "ip": "104.171.202.103",
                "instance_type": "gpu_1x_rtx6000",
                "cost_per_hour": 0.50,
                "purpose": "Monitoring & Operations",
                "critical": True,
            },
            "sophia-mcp-orchestrator": {
                "ip": "104.171.202.117",
                "instance_type": "gpu_1x_a6000",
                "cost_per_hour": 0.80,
                "purpose": "MCP Server Orchestration & Business Intelligence",
                "critical": False,
            },
            "sophia-data-pipeline": {
                "ip": "104.171.202.134",
                "instance_type": "gpu_1x_a100",
                "cost_per_hour": 1.29,
                "purpose": "Data Processing & ETL Operations",
                "critical": False,
            },
            "sophia-development": {
                "ip": "155.248.194.183",
                "instance_type": "gpu_1x_a10",
                "cost_per_hour": 0.75,
                "purpose": "Development & Testing Environment",
                "critical": False,
            },
        }

    def validate_api_access(self) -> bool:
        """Test Lambda Labs API connectivity"""
        print("🔑 Testing Lambda Labs API access...")

        try:
            if not get_lambda_labs_config:
                print("   ❌ Lambda Labs config not available")
                return False

            config = get_lambda_labs_config()
            if not config.get("api_key"):
                print("   ❌ No API key found")
                return False

            headers = {"Authorization": f'Bearer {config["api_key"]}'}
            response = requests.get(
                "https://cloud.lambda.ai/api/v1/instances", headers=headers, timeout=10
            )

            if response.status_code == 200:
                print("   ✅ API access successful")
                self.results["api_access"] = True
                return True
            else:
                print(f"   ❌ API request failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ API test failed: {str(e)}")
            return False

    def validate_instances(self) -> bool:
        """Validate all Lambda Labs instances"""
        print("🖥️  Validating Lambda Labs instances...")

        try:
            if not get_lambda_labs_config:
                return False

            config = get_lambda_labs_config()
            headers = {"Authorization": f'Bearer {config["api_key"]}'}

            response = requests.get(
                "https://cloud.lambda.ai/api/v1/instances", headers=headers, timeout=10
            )

            if response.status_code != 200:
                print(f"   ❌ Failed to get instances: {response.status_code}")
                return False

            data = response.json()
            instances = data.get("data", [])

            active_instances = {}
            total_cost = 0
            critical_instances_active = 0

            for instance in instances:
                name = instance.get("name", "Unknown")
                status = instance.get("status", "Unknown")
                ip = instance.get("ip", "N/A")
                instance_type = instance.get("instance_type", {}).get("name", "Unknown")

                if name in self.expected_instances:
                    expected = self.expected_instances[name]
                    active_instances[name] = {
                        "status": status,
                        "ip": ip,
                        "instance_type": instance_type,
                        "expected_ip": expected["ip"],
                        "ip_matches": ip == expected["ip"],
                        "purpose": expected["purpose"],
                        "critical": expected["critical"],
                    }

                    if status == "active":
                        total_cost += expected["cost_per_hour"]
                        if expected["critical"]:
                            critical_instances_active += 1

            self.results["instances"] = active_instances
            self.results["total_cost"] = total_cost

            # Check results
            instances_found = len(active_instances)
            instances_active = sum(
                1 for inst in active_instances.values() if inst["status"] == "active"
            )
            ips_correct = sum(
                1 for inst in active_instances.values() if inst["ip_matches"]
            )

            print(f"   📊 Found: {instances_found}/5 instances")
            print(f"   🟢 Active: {instances_active}/5 instances")
            print(f"   🎯 Correct IPs: {ips_correct}/5 instances")
            print(f"   🔥 Critical instances active: {critical_instances_active}/2")
            print(f"   💰 Total cost: ${total_cost:.2f}/hour")

            # Success criteria
            success = (
                instances_found == 5
                and instances_active >= 4
                and ips_correct >= 4
                and critical_instances_active == 2
            )

            if success:
                print("   ✅ Instance validation successful")
            else:
                print("   ⚠️  Instance validation has issues")

            return success

        except Exception as e:
            print(f"   ❌ Instance validation failed: {str(e)}")
            return False

    def validate_ssh_connectivity(self) -> bool:
        """Test SSH connectivity to instances"""
        print("🔐 Testing SSH connectivity...")

        ssh_key_path = os.path.expanduser("~/.ssh/sophia_lambda_key")

        if not os.path.exists(ssh_key_path):
            print(f"   ❌ SSH key not found: {ssh_key_path}")
            return False

        successful_connections = 0
        critical_connections = 0

        for name, config in self.expected_instances.items():
            ip = config["ip"]
            is_critical = config["critical"]

            try:
                cmd = [
                    "ssh",
                    "-i",
                    ssh_key_path,
                    "-o",
                    "ConnectTimeout=10",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-o",
                    "LogLevel=ERROR",
                    f"ubuntu@{ip}",
                    'echo "SSH test successful"',
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

                if result.returncode == 0:
                    print(f"   ✅ {name} ({ip}) - SSH OK")
                    successful_connections += 1
                    self.results["ssh_connectivity"][name] = True
                    if is_critical:
                        critical_connections += 1
                else:
                    print(f"   ❌ {name} ({ip}) - SSH FAILED")
                    self.results["ssh_connectivity"][name] = False

            except Exception as e:
                print(f"   ❌ {name} ({ip}) - SSH ERROR: {str(e)}")
                self.results["ssh_connectivity"][name] = False

        success_rate = successful_connections / len(self.expected_instances)
        critical_success = critical_connections >= 1  # At least one critical instance

        print(
            f"   📊 SSH Success Rate: {successful_connections}/5 ({success_rate*100:.1f}%)"
        )
        print(f"   🔥 Critical SSH Access: {critical_connections}/2")

        return success_rate >= 0.6 and critical_success

    def validate_secret_management(self) -> bool:
        """Test secret management pipeline"""
        print("🔐 Testing secret management pipeline...")

        tests_passed = 0
        total_tests = 3

        # Test 1: Pulumi CLI access
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                print("   ✅ Pulumi CLI authenticated")
                tests_passed += 1
            else:
                print("   ❌ Pulumi CLI authentication failed")

        except Exception as e:
            print(f"   ❌ Pulumi test failed: {str(e)}")

        # Test 2: Backend config loading
        try:
            if get_lambda_labs_config:
                config = get_lambda_labs_config()
                if config.get("api_key") and len(config["api_key"]) > 20:
                    print("   ✅ Backend config loading working")
                    tests_passed += 1
                else:
                    print("   ❌ Backend config incomplete")
            else:
                print("   ⚠️  Backend config import not available")

        except Exception as e:
            print(f"   ❌ Backend config test failed: {str(e)}")

        # Test 3: ESC environment access
        try:
            result = subprocess.run(
                [
                    "pulumi",
                    "config",
                    "get",
                    "LAMBDA_API_KEY",
                    "--stack",
                    "sophia-ai-production",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                print("   ✅ Pulumi ESC secret access working")
                tests_passed += 1
            else:
                print("   ❌ Pulumi ESC secret access failed")

        except Exception as e:
            print(f"   ❌ ESC test failed: {str(e)}")

        success = tests_passed >= 2
        self.results["secret_management"] = success

        print(f"   📊 Secret Management Score: {tests_passed}/{total_tests}")

        return success

    def generate_recommendations(self) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        if not self.results["api_access"]:
            recommendations.append(
                "🔑 Fix Lambda Labs API access - check API key in secrets"
            )

        # Check for failed instances
        failed_instances = [
            name
            for name, data in self.results["instances"].items()
            if data.get("status") != "active"
        ]

        if failed_instances:
            recommendations.append(
                f"🖥️  Restart failed instances: {', '.join(failed_instances)}"
            )

        # Check SSH failures
        ssh_failures = [
            name
            for name, success in self.results["ssh_connectivity"].items()
            if not success
        ]

        if ssh_failures:
            recommendations.append(
                f"🔐 Fix SSH connectivity to: {', '.join(ssh_failures)}"
            )

        if not self.results["secret_management"]:
            recommendations.append(
                "☁️  Fix secret management pipeline - check Pulumi ESC access"
            )

        # Cost optimization
        if self.results["total_cost"] > 5.0:
            recommendations.append(
                "💰 Consider stopping non-critical instances to reduce costs"
            )

        # General recommendations
        recommendations.extend(
            [
                "🔄 Run validation weekly to ensure infrastructure health",
                f"💰 Monitor costs - current: ${self.results['total_cost']:.2f}/hour",
                "🔐 Rotate secrets quarterly for security",
                "📋 Keep documentation updated with infrastructure changes",
            ]
        )

        return recommendations

    def print_summary(self):
        """Print validation summary"""
        print(f"\n{'='*70}")
        print("🎯 LAMBDA LABS INFRASTRUCTURE VALIDATION SUMMARY")
        print(f"{'='*70}")

        # Determine overall status
        api_ok = self.results["api_access"]
        instances_ok = (
            len(
                [
                    i
                    for i in self.results["instances"].values()
                    if i.get("status") == "active"
                ]
            )
            >= 4
        )
        ssh_ok = len([s for s in self.results["ssh_connectivity"].values() if s]) >= 3
        secrets_ok = self.results["secret_management"]

        if api_ok and instances_ok and ssh_ok and secrets_ok:
            self.results["overall_status"] = "EXCELLENT"
            status_emoji = "🎉"
        elif api_ok and instances_ok and (ssh_ok or secrets_ok):
            self.results["overall_status"] = "GOOD"
            status_emoji = "✅"
        elif api_ok and (instances_ok or ssh_ok):
            self.results["overall_status"] = "FAIR"
            status_emoji = "⚠️"
        else:
            self.results["overall_status"] = "POOR"
            status_emoji = "❌"

        print(f"{status_emoji} Overall Status: {self.results['overall_status']}")
        print(
            f"💰 Total Cost: ${self.results['total_cost']:.2f}/hour (${self.results['total_cost']*24:.2f}/day)"
        )
        print(f"🔑 API Access: {'✅' if api_ok else '❌'}")
        print(f"🖥️  Instances: {'✅' if instances_ok else '❌'}")
        print(f"🔐 SSH Access: {'✅' if ssh_ok else '❌'}")
        print(f"☁️  Secrets: {'✅' if secrets_ok else '❌'}")

        # Recommendations
        recommendations = self.generate_recommendations()
        self.results["recommendations"] = recommendations

        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                print(f"   {i}. {rec}")

    def save_results(self):
        """Save validation results"""
        timestamp = int(datetime.now().timestamp())
        results_file = f"lambda_infrastructure_validation_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {results_file}")

    def run_validation(self) -> bool:
        """Run complete infrastructure validation"""
        print("🚀 LAMBDA LABS INFRASTRUCTURE VALIDATION")
        print("🔍 Validating complete infrastructure...\n")

        tests = [
            ("API Access", self.validate_api_access),
            ("Instance Status", self.validate_instances),
            ("SSH Connectivity", self.validate_ssh_connectivity),
            ("Secret Management", self.validate_secret_management),
        ]

        passed_tests = 0

        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"   ❌ {test_name} failed with error: {str(e)}\n")

        # Print summary
        self.print_summary()
        self.save_results()

        # Return success if most tests passed
        return passed_tests >= 3


def main():
    """Main execution function"""
    validator = LambdaLabsValidator()

    try:
        is_healthy = validator.run_validation()

        if is_healthy:
            print("\n🎉 Infrastructure validation PASSED!")
            print("✅ Lambda Labs infrastructure is operational")
            return 0
        else:
            print("\n⚠️  Infrastructure validation has issues")
            print("❌ Address recommendations before proceeding")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Validation failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
