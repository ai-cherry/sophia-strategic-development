#!/usr/bin/env python3
"""
Infrastructure Validation Script
================================
Validates that all infrastructure components are ready for deployment
"""

import json
import subprocess
from pathlib import Path


class InfrastructureValidator:
    def __init__(self):
        self.results = {
            "ssh_automation": False,
            "typescript_setup": False,
            "secret_sync": False,
            "pulumi_auth": False,
            "lambda_labs": False,
            "services_ready": {},
        }

    def validate_ssh_automation(self) -> bool:
        """Validate SSH key automation is working"""
        print("\n🔐 Validating SSH Key Automation...")

        try:
            # Check if SSH key exists locally
            ssh_key_path = Path.home() / ".ssh" / "pulumi_lambda_key"
            if not ssh_key_path.exists():
                print("  ❌ SSH key not found locally")
                return False
            print("  ✅ SSH key exists locally")

            # Check if SSH key is in Pulumi ESC
            cmd = [
                "pulumi",
                "env",
                "get",
                "scoobyjava-org/default/sophia-ai-production",
                "lambda_labs_ssh_public_key_base64",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("  ❌ SSH key not found in Pulumi ESC")
                return False
            print("  ✅ SSH key stored in Pulumi ESC")

            self.results["ssh_automation"] = True
            return True

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def validate_typescript_setup(self) -> bool:
        """Validate TypeScript infrastructure is ready"""
        print("\n📦 Validating TypeScript Setup...")

        try:
            # Check package.json exists
            package_json = Path("../package.json")
            if not package_json.exists():
                print("  ❌ package.json not found")
                return False
            print("  ✅ package.json exists")

            # Check TypeScript config
            tsconfig = Path("../tsconfig.json")
            if not tsconfig.exists():
                print("  ❌ tsconfig.json not found")
                return False
            print("  ✅ tsconfig.json exists")

            # Check providers directory
            providers_dir = Path("../providers")
            if not providers_dir.exists():
                print("  ❌ providers directory not found")
                return False

            providers = list(providers_dir.glob("*.ts"))
            print(f"  ✅ {len(providers)} provider files found")

            self.results["typescript_setup"] = True
            return True

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def validate_secret_sync(self) -> bool:
        """Validate bi-directional secret sync"""
        print("\n🔄 Validating Secret Synchronization...")

        try:
            # Check if sync script exists
            sync_script = Path("github_sync_bidirectional.py")
            if not sync_script.exists():
                print("  ❌ Sync script not found")
                return False
            print("  ✅ Sync script exists")

            # Check secret mappings
            mappings_file = Path("secret_mappings.json")
            if not mappings_file.exists():
                print("  ❌ Secret mappings not found")
                return False

            with open(mappings_file) as f:
                mappings = json.load(f)

            github_mappings = len(mappings.get("github_to_pulumi", {}))
            services = len(mappings.get("services", {}))

            print(f"  ✅ {github_mappings} GitHub mappings configured")
            print(f"  ✅ {services} services configured")

            self.results["secret_sync"] = True
            return True

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def validate_pulumi_auth(self) -> bool:
        """Validate Pulumi authentication"""
        print("\n🔑 Validating Pulumi Authentication...")

        try:
            cmd = ["pulumi", "whoami"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("  ❌ Pulumi not authenticated")
                return False

            user = result.stdout.strip()
            print(f"  ✅ Authenticated as: {user}")

            # Check access to ESC
            cmd = [
                "pulumi",
                "env",
                "open",
                "scoobyjava-org/default/sophia-ai-production",
                "--format",
                "json",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("  ❌ Cannot access Pulumi ESC")
                return False

            print("  ✅ Pulumi ESC accessible")

            self.results["pulumi_auth"] = True
            return True

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def validate_lambda_labs(self) -> bool:
        """Validate Lambda Labs connectivity"""
        print("\n🖥️  Validating Lambda Labs...")

        try:
            # Test SSH to instances
            instances = [
                ("sophia-platform-prod", "192.9.243.87"),
                ("sophia-mcp-prod", "150.230.43.63"),
            ]

            all_good = True
            for name, ip in instances:
                cmd = [
                    "ssh",
                    "-i",
                    f"{Path.home()}/.ssh/pulumi_lambda_key",
                    "-o",
                    "ConnectTimeout=5",
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{ip}",
                    "echo 'connected'",
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"  ✅ {name} ({ip}) - SSH working")
                else:
                    print(f"  ❌ {name} ({ip}) - SSH failed")
                    all_good = False

            self.results["lambda_labs"] = all_good
            return all_good

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def validate_services(self) -> dict[str, bool]:
        """Validate service-specific requirements"""
        print("\n🚀 Validating Service Readiness...")

        services = {
            "lambda_labs": ["lambda_api_key", "lambda_labs_ssh_public_key_base64"],
            "snowflake": ["snowflake_account", "snowflake_user", "snowflake_password"],
            "estuary": ["estuary_access_token", "estuary_tenant"],
            "github": ["github_token"],
            "portkey": ["portkey_api_key"],
        }

        # Get all ESC values
        cmd = [
            "pulumi",
            "env",
            "open",
            "scoobyjava-org/default/sophia-ai-production",
            "--format",
            "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            esc_data = json.loads(result.stdout)

            for service, required_secrets in services.items():
                print(f"\n  {service}:")
                service_ready = True

                for secret in required_secrets:
                    value = self._get_nested_value(esc_data, secret)
                    if (
                        value
                        and isinstance(value, str)
                        and not value.startswith("PLACEHOLDER_")
                    ):
                        print(f"    ✅ {secret}")
                    else:
                        print(f"    ❌ {secret} (missing or placeholder)")
                        service_ready = False

                self.results["services_ready"][service] = service_ready

        return self.results["services_ready"]

    def _get_nested_value(self, data: dict, path: str):
        """Get value from nested dictionary using dot notation"""
        parts = path.split(".")
        value = data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("📊 INFRASTRUCTURE VALIDATION REPORT")
        print("=" * 60)

        # Core components
        print("\n🔧 Core Components:")
        print(f"  SSH Automation:     {'✅' if self.results['ssh_automation'] else '❌'}")
        print(
            f"  TypeScript Setup:   {'✅' if self.results['typescript_setup'] else '❌'}"
        )
        print(f"  Secret Sync:        {'✅' if self.results['secret_sync'] else '❌'}")
        print(f"  Pulumi Auth:        {'✅' if self.results['pulumi_auth'] else '❌'}")
        print(f"  Lambda Labs:        {'✅' if self.results['lambda_labs'] else '❌'}")

        # Service readiness
        print("\n🚀 Service Readiness:")
        for service, ready in self.results["services_ready"].items():
            print(f"  {service:15} {'✅ Ready' if ready else '❌ Not Ready'}")

        # Overall status
        core_ready = all(
            [
                self.results["ssh_automation"],
                self.results["typescript_setup"],
                self.results["secret_sync"],
                self.results["pulumi_auth"],
            ]
        )

        services_ready = sum(self.results["services_ready"].values())
        total_services = len(self.results["services_ready"])

        print("\n📈 Overall Status:")
        print(f"  Core Infrastructure: {'READY' if core_ready else 'NOT READY'}")
        print(f"  Services Ready: {services_ready}/{total_services}")
        print(f"  Overall Readiness: {(services_ready/total_services)*100:.0f}%")

        if core_ready and services_ready >= 3:
            print("\n✅ Infrastructure is READY for deployment!")
        else:
            print("\n⚠️  Infrastructure needs additional configuration")

    def run(self):
        """Run all validations"""
        print("🚀 Starting Infrastructure Validation...")

        self.validate_ssh_automation()
        self.validate_typescript_setup()
        self.validate_secret_sync()
        self.validate_pulumi_auth()
        self.validate_lambda_labs()
        self.validate_services()

        self.generate_report()


if __name__ == "__main__":
    validator = InfrastructureValidator()
    validator.run()
