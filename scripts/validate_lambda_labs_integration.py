#!/usr/bin/env python3
"""
Validate Lambda Labs + GitHub + Pulumi ESC Integration
This script validates that all components are properly configured for H200 deployment.
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


class IntegrationValidator:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.successes: list[str] = []
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_env_prod = "sophia-ai-production"
        self.pulumi_env_h200 = "sophia-ai-h200-production"

    def validate_github_cli(self) -> bool:
        """Validate GitHub CLI is authenticated"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True
            )
            if result.returncode == 0:
                # Extract logged in user (check both stdout and stderr)
                output = result.stdout + result.stderr
                if (
                    "Logged in to github.com" in output
                    or "✓ Logged in to github.com" in output
                ):
                    self.successes.append("✅ GitHub CLI authenticated")

                    # Check organization access with better error handling
                    try:
                        org_result = subprocess.run(
                            ["gh", "api", "/orgs/ai-cherry"],
                            capture_output=True,
                            text=True,
                        )
                        if org_result.returncode == 0:
                            # Try to parse the result
                            try:
                                import json

                                org_data = json.loads(org_result.stdout)
                                if org_data.get("login") == "ai-cherry":
                                    self.successes.append(
                                        "✅ GitHub organization 'ai-cherry' access confirmed"
                                    )
                                    return True
                                else:
                                    self.warnings.append(
                                        "⚠️  Organization found but name doesn't match"
                                    )
                                    return True  # Still authenticated, just warning
                            except:
                                self.warnings.append(
                                    "⚠️  Could not parse organization data, but GitHub CLI is authenticated"
                                )
                                return True  # Still authenticated
                        else:
                            self.warnings.append(
                                "⚠️  Could not access 'ai-cherry' organization (may need permissions)"
                            )
                            return True  # Still authenticated, just no org access
                    except Exception as e:
                        self.warnings.append(f"⚠️  Organization check failed: {e}")
                        return True  # Still authenticated
                else:
                    self.errors.append("❌ GitHub CLI not authenticated")
                    return False
            else:
                self.errors.append("❌ GitHub CLI not authenticated")
                return False
        except FileNotFoundError:
            self.errors.append(
                "❌ GitHub CLI not installed (install with: brew install gh)"
            )
            return False
        except Exception as e:
            self.errors.append(f"❌ GitHub CLI error: {e}")
            return False

    def validate_github_secrets(self) -> bool:
        """Validate all Lambda Labs secrets exist in GitHub"""
        required_secrets = [
            "LAMBDA_LABS_API_KEY",
            "LAMBDA_LABS_SSH_KEY_NAME",
            "LAMBDA_LABS_SSH_PRIVATE_KEY",
            "LAMBDA_LABS_REGION",
            "LAMBDA_LABS_INSTANCE_TYPE",
            "LAMBDA_LABS_CLUSTER_SIZE",
            "LAMBDA_LABS_MAX_CLUSTER_SIZE",
            "LAMBDA_LABS_SHARED_FS_ID",
            "LAMBDA_LABS_SHARED_FS_MOUNT",
            "LAMBDA_LABS_ASG_NAME",
        ]

        try:
            result = subprocess.run(
                ["gh", "secret", "list", "--org", "ai-cherry"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                secret_list = result.stdout
                missing = []
                found = []

                for secret in required_secrets:
                    if secret in secret_list:
                        found.append(secret)
                    else:
                        missing.append(secret)

                if missing:
                    self.errors.append(
                        f"❌ Missing GitHub secrets: {', '.join(missing)}"
                    )
                    if found:
                        self.successes.append(
                            f"✅ Found {len(found)}/10 Lambda Labs secrets in GitHub"
                        )
                    return False
                else:
                    self.successes.append(
                        "✅ All 10 Lambda Labs secrets present in GitHub"
                    )

                    # Validate specific values
                    self._validate_secret_values()
                    return True
            else:
                self.errors.append(f"❌ Failed to list GitHub secrets: {result.stderr}")
                return False

        except Exception as e:
            self.errors.append(f"❌ GitHub secret validation error: {e}")
            return False

    def _validate_secret_values(self):
        """Validate specific secret values (non-sensitive ones)"""
        # These are safe to validate as they're configuration values, not actual secrets
        expected_values = {
            "LAMBDA_LABS_SSH_KEY_NAME": "lynn-sophia-h200-key",
            "LAMBDA_LABS_REGION": "us-west-1",
            "LAMBDA_LABS_INSTANCE_TYPE": "gpu_1x_h200",
            "LAMBDA_LABS_CLUSTER_SIZE": "3",
            "LAMBDA_LABS_MAX_CLUSTER_SIZE": "16",
            "LAMBDA_LABS_SHARED_FS_ID": "lynn-sophia-shared-fs",
            "LAMBDA_LABS_SHARED_FS_MOUNT": "/mnt/shared",
            "LAMBDA_LABS_ASG_NAME": "lynn-sophia-h200-asg",
        }

        # Note: We can't actually read secret values via CLI for security
        # This is just a placeholder to show expected values
        self.successes.append(
            "✅ Expected secret values documented (cannot verify actual values for security)"
        )

    def validate_pulumi_esc(self) -> bool:
        """Validate Pulumi ESC configuration"""
        try:
            # Check Pulumi login
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True
            )

            if result.returncode != 0:
                self.errors.append("❌ Pulumi not logged in (run: pulumi login)")
                return False

            username = result.stdout.strip()
            self.successes.append(f"✅ Pulumi logged in as: {username}")

            # Check production ESC environment
            prod_result = subprocess.run(
                [
                    "pulumi",
                    "env",
                    "get",
                    f"{self.pulumi_org}/default/{self.pulumi_env_prod}",
                ],
                capture_output=True,
                text=True,
            )

            if prod_result.returncode == 0:
                self.successes.append(
                    f"✅ Production ESC environment exists: {self.pulumi_env_prod}"
                )
            else:
                self.warnings.append(
                    f"⚠️  Production ESC environment not found: {self.pulumi_env_prod}"
                )

            # Check H200 ESC environment (may not exist yet)
            h200_result = subprocess.run(
                [
                    "pulumi",
                    "env",
                    "get",
                    f"{self.pulumi_org}/default/{self.pulumi_env_h200}",
                ],
                capture_output=True,
                text=True,
            )

            if h200_result.returncode == 0:
                self.successes.append(
                    f"✅ H200 ESC environment configured: {self.pulumi_env_h200}"
                )

                # Try to validate Lambda Labs configuration
                try:
                    config = json.loads(h200_result.stdout)
                    if "sophia" in config and "infrastructure" in config["sophia"]:
                        if "lambda_labs" in config["sophia"]["infrastructure"]:
                            self.successes.append(
                                "✅ Lambda Labs configuration present in H200 ESC"
                            )
                            return True
                except:
                    pass

            else:
                self.warnings.append(
                    f"⚠️  H200 ESC environment needs to be created: pulumi env init {self.pulumi_org}/{self.pulumi_env_h200}"
                )

            return prod_result.returncode == 0

        except FileNotFoundError:
            self.errors.append(
                "❌ Pulumi CLI not installed (install from: https://www.pulumi.com/docs/install/)"
            )
            return False
        except Exception as e:
            self.errors.append(f"❌ Pulumi ESC validation error: {e}")
            return False

    def validate_ssh_key(self) -> bool:
        """Validate SSH key configuration"""
        ssh_key_path = Path.home() / ".ssh" / "lynn_sophia_h200_key"
        pub_key_path = ssh_key_path.with_suffix(".pub")

        if ssh_key_path.exists():
            # Check permissions
            permissions = oct(ssh_key_path.stat().st_mode)[-3:]
            if permissions == "600":
                self.successes.append(
                    "✅ SSH private key exists with correct permissions (600)"
                )
            else:
                self.warnings.append(
                    f"⚠️  SSH key permissions should be 600, found {permissions}"
                )
                # Fix permissions
                os.chmod(ssh_key_path, 0o600)
                self.successes.append("✅ Fixed SSH key permissions to 600")

            # Check public key
            if pub_key_path.exists():
                with open(pub_key_path) as f:
                    key_content = f.read()
                    if "ssh-ed25519" in key_content:
                        self.successes.append(
                            "✅ SSH key is ED25519 (modern encryption)"
                        )

                        # Extract fingerprint
                        try:
                            result = subprocess.run(
                                ["ssh-keygen", "-l", "-f", str(pub_key_path)],
                                capture_output=True,
                                text=True,
                            )
                            if result.returncode == 0:
                                fingerprint = result.stdout.strip()
                                self.successes.append(
                                    f"✅ SSH key fingerprint: {fingerprint}"
                                )
                        except:
                            pass
                    else:
                        self.warnings.append("⚠️  SSH key is not ED25519")

                return True
            else:
                self.errors.append(f"❌ SSH public key not found at {pub_key_path}")
                return False
        else:
            self.errors.append(f"❌ SSH key not found at {ssh_key_path}")
            self.warnings.append(
                "💡 Generate with: ssh-keygen -t ed25519 -f ~/.ssh/lynn_sophia_h200_key -C 'lynn-sophia-h200'"
            )
            return False

    def validate_lambda_labs_api(self) -> bool:
        """Validate Lambda Labs API access"""
        api_key = os.getenv("LAMBDA_LABS_API_KEY")

        if not api_key:
            # Try to get from Pulumi ESC
            try:
                # First try production environment
                result = subprocess.run(
                    [
                        "pulumi",
                        "env",
                        "get",
                        f"{self.pulumi_org}/default/{self.pulumi_env_prod}",
                        "lambda_labs_api_key",
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    api_key = result.stdout.strip()
                else:
                    # Try H200 environment
                    result = subprocess.run(
                        [
                            "pulumi",
                            "env",
                            "get",
                            f"{self.pulumi_org}/default/{self.pulumi_env_h200}",
                            "sophia.infrastructure.lambda_labs.api_key",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        api_key = result.stdout.strip()
            except:
                pass

        if api_key:
            # Test API access
            try:
                response = requests.get(
                    "https://cloud.lambdalabs.com/api/v1/instance-types",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10,
                )

                if response.status_code == 200:
                    self.successes.append("✅ Lambda Labs API key valid")

                    # Check for instance types
                    data = response.json()
                    instance_types = data.get("data", {})

                    # Check for H200 availability
                    h200_types = [
                        t
                        for t in instance_types.values()
                        if "h200" in t.get("instance_type", {}).get("name", "").lower()
                    ]

                    if h200_types:
                        self.successes.append(
                            "✅ H200 GPU instances found in Lambda Labs"
                        )
                        # Show availability
                        for h200 in h200_types:
                            regions = h200.get("regions_with_capacity_available", [])
                            if regions:
                                self.successes.append(
                                    f"✅ H200 available in regions: {', '.join(r['name'] for r in regions)}"
                                )
                            else:
                                self.warnings.append(
                                    "⚠️  H200 currently not available in any region"
                                )
                    else:
                        self.warnings.append(
                            "⚠️  H200 GPU instances not found in instance types"
                        )

                    # List current instances
                    self._check_current_instances(api_key)

                    return True
                else:
                    self.errors.append(
                        f"❌ Lambda Labs API key invalid: HTTP {response.status_code}"
                    )
                    return False

            except requests.exceptions.RequestException as e:
                self.errors.append(f"❌ Lambda Labs API connection failed: {e}")
                return False
            except Exception as e:
                self.errors.append(f"❌ Lambda Labs API test failed: {e}")
                return False
        else:
            self.warnings.append("⚠️  Lambda Labs API key not found in environment")
            self.warnings.append(
                "💡 Set with: export LAMBDA_LABS_API_KEY='your-api-key'"
            )
            return False

    def _check_current_instances(self, api_key: str):
        """Check current Lambda Labs instances"""
        try:
            response = requests.get(
                "https://cloud.lambdalabs.com/api/v1/instances",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                instances = data.get("data", [])

                if instances:
                    self.successes.append(
                        f"✅ Found {len(instances)} current Lambda Labs instances:"
                    )
                    for inst in instances:
                        name = inst.get("name", "unnamed")
                        ip = inst.get("ip", "no-ip")
                        gpu_type = inst.get("instance_type", {}).get("name", "unknown")
                        status = inst.get("status", "unknown")
                        self.successes.append(
                            f"   • {name}: {ip} ({gpu_type}) - {status}"
                        )
                else:
                    self.warnings.append("⚠️  No current Lambda Labs instances found")
        except:
            pass  # Non-critical, just informational

    def check_infrastructure_files(self) -> bool:
        """Check for required infrastructure files"""
        required_files = [
            "infrastructure/esc/lambda-labs-h200-config.yaml",
            "scripts/ci/sync_from_gh_to_pulumi.py",
            ".github/workflows/sync_secrets.yml",
            "scripts/verify_lambda_labs_h200_setup.py",
        ]

        all_exist = True
        for file_path in required_files:
            path = Path(file_path)
            if path.exists():
                self.successes.append(f"✅ Infrastructure file exists: {file_path}")
            else:
                self.warnings.append(f"⚠️  Infrastructure file missing: {file_path}")
                all_exist = False

        return all_exist

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 70)
        print("🔍 Lambda Labs + GitHub + Pulumi ESC Integration Validation")
        print("=" * 70)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🏢 Organization: ai-cherry")
        print(f"🔧 Pulumi Org: {self.pulumi_org}")
        print("=" * 70 + "\n")

        total_checks = len(self.successes) + len(self.errors) + len(self.warnings)

        if self.successes:
            print("✅ SUCCESSES:")
            for success in self.successes:
                print(f"   {success}")
            print()

        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
            print()

        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"   {error}")
            print()

        # Overall status
        print("=" * 70)
        if not self.errors:
            print("🎉 OVERALL: Integration validation PASSED!")
            print("   ✅ Ready for H200 GPU deployment")
            print("\n📋 Next Steps:")
            print("   1. Run: gh workflow run sync_secrets.yml")
            print("   2. Run: pulumi env init scoobyjava-org/sophia-ai-h200-production")
            print("   3. Run: pulumi up -s sophia-ai-h200-production")
        else:
            print("❌ OVERALL: Integration validation FAILED")
            print("   Please fix the errors above before proceeding")

        print("\n📊 Summary:")
        print(f"   Total checks: {total_checks}")
        print(f"   Successes: {len(self.successes)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Errors: {len(self.errors)}")
        print("=" * 70)


def main():
    validator = IntegrationValidator()

    print("🚀 Starting Lambda Labs H200 Integration Validation...")
    print("   This will check GitHub CLI, Pulumi ESC, SSH keys, and API access\n")

    # Run all validations
    checks = [
        ("GitHub CLI", validator.validate_github_cli),
        ("GitHub Secrets", validator.validate_github_secrets),
        ("Pulumi ESC", validator.validate_pulumi_esc),
        ("SSH Key", validator.validate_ssh_key),
        ("Lambda Labs API", validator.validate_lambda_labs_api),
        ("Infrastructure Files", validator.check_infrastructure_files),
    ]

    for check_name, check_func in checks:
        print(f"🔄 Checking {check_name}...", end="", flush=True)
        result = check_func()
        print(" Done" if result else " Failed")

    # Generate report
    validator.generate_report()

    # Exit with appropriate code
    sys.exit(0 if not validator.errors else 1)


if __name__ == "__main__":
    main()
