#!/usr/bin/env python3
"""
Pre-deployment checklist for Lambda Labs H200 GPU Infrastructure
Validates all prerequisites before deploying H200 instances
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class PreDeploymentChecker:
    def __init__(self):
        self.checks = []
        self.warnings = []

    def add_check(self, name: str, passed: bool, details: str = ""):
        """Add a check result"""
        self.checks.append({"name": name, "passed": passed, "details": details})

    def check_github_cli(self):
        """Check GitHub CLI authentication"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True
            )

            if result.returncode == 0:
                # Extract username
                if "Logged in to github.com account" in result.stderr:
                    self.add_check(
                        "GitHub CLI authenticated",
                        True,
                        "✓ Authenticated to github.com",
                    )
                else:
                    self.add_check(
                        "GitHub CLI authenticated", True, result.stderr.strip()
                    )
            else:
                self.add_check("GitHub CLI authenticated", False, "Run: gh auth login")
        except FileNotFoundError:
            self.add_check(
                "GitHub CLI authenticated",
                False,
                "GitHub CLI not installed. Run: brew install gh",
            )
        except Exception as e:
            self.add_check("GitHub CLI authenticated", False, str(e))

    def check_pulumi(self):
        """Check Pulumi authentication"""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True
            )

            if result.returncode == 0:
                username = result.stdout.strip()
                self.add_check(
                    "Pulumi authenticated", True, f"Logged in as: {username}"
                )
            else:
                self.add_check("Pulumi authenticated", False, "Run: pulumi login")
        except FileNotFoundError:
            self.add_check(
                "Pulumi authenticated",
                False,
                "Pulumi CLI not installed. Visit: https://www.pulumi.com/docs/install/",
            )
        except Exception as e:
            self.add_check("Pulumi authenticated", False, str(e))

    def check_ssh_key(self):
        """Check SSH key configuration"""
        ssh_key_path = Path.home() / ".ssh" / "lynn_sophia_h200_key"
        pub_key_path = ssh_key_path.with_suffix(".pub")

        if ssh_key_path.exists():
            # Check permissions
            permissions = oct(ssh_key_path.stat().st_mode)[-3:]
            if permissions == "600":
                details = "SSH key exists with correct permissions (600)"

                # Check if it's ED25519
                if pub_key_path.exists():
                    with open(pub_key_path) as f:
                        key_content = f.read()
                        if "ssh-ed25519" in key_content:
                            details += " - ED25519 key ✓"
                        else:
                            details += " - Warning: Not ED25519"

                self.add_check("SSH key configuration", True, details)
            else:
                self.add_check(
                    "SSH key configuration",
                    False,
                    f"Permissions are {permissions}, should be 600. Run: chmod 600 {ssh_key_path}",
                )
        else:
            self.add_check(
                "SSH key configuration",
                False,
                f"SSH key not found. Run: ssh-keygen -t ed25519 -f {ssh_key_path} -C 'lynn-sophia-h200'",
            )

    def check_lambda_labs_api(self):
        """Check Lambda Labs API key"""
        api_key = os.getenv("LAMBDA_LABS_API_KEY")

        if api_key:
            # Basic validation - check length
            if len(api_key) > 20:
                self.add_check(
                    "Lambda Labs API key",
                    True,
                    f"API key set ({len(api_key)} characters)",
                )
            else:
                self.add_check("Lambda Labs API key", False, "API key seems too short")
        else:
            self.add_check(
                "Lambda Labs API key",
                False,
                "Set with: export LAMBDA_LABS_API_KEY='your-api-key'",
            )

    def check_docker(self):
        """Check Docker availability"""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)

            if result.returncode == 0:
                # Check if logged into Docker Hub
                if "Username:" in result.stdout:
                    self.add_check("Docker", True, "Docker running and logged in")
                else:
                    self.add_check(
                        "Docker", True, "Docker running (not logged in to registry)"
                    )
                    self.warnings.append("Consider: docker login")
            else:
                self.add_check(
                    "Docker", False, "Docker not running. Start Docker Desktop"
                )
        except FileNotFoundError:
            self.add_check("Docker", False, "Docker not installed")
        except Exception as e:
            self.add_check("Docker", False, str(e))

    def check_pulumi_esc_env(self):
        """Check Pulumi ESC environments"""
        try:
            # Check production environment
            result = subprocess.run(
                ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.add_check(
                    "Pulumi ESC (production)", True, "Production environment exists"
                )
            else:
                self.add_check(
                    "Pulumi ESC (production)", False, "Production environment not found"
                )

            # Check H200 environment
            result = subprocess.run(
                [
                    "pulumi",
                    "env",
                    "get",
                    "scoobyjava-org/default/sophia-ai-h200-production",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.add_check("Pulumi ESC (H200)", True, "H200 environment configured")
            else:
                self.add_check(
                    "Pulumi ESC (H200)",
                    False,
                    "Run: pulumi env init scoobyjava-org/sophia-ai-h200-production",
                )

        except Exception as e:
            self.add_check("Pulumi ESC environments", False, str(e))

    def check_github_secrets(self):
        """Check if GitHub secrets are accessible"""
        try:
            result = subprocess.run(
                ["gh", "secret", "list", "--org", "ai-cherry"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                secrets = result.stdout
                h200_secrets = [
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

                found = sum(1 for secret in h200_secrets if secret in secrets)

                if found == len(h200_secrets):
                    self.add_check(
                        "GitHub secrets",
                        True,
                        f"All {len(h200_secrets)} H200 secrets found",
                    )
                else:
                    self.add_check(
                        "GitHub secrets",
                        False,
                        f"Only {found}/{len(h200_secrets)} H200 secrets found",
                    )
            else:
                self.add_check(
                    "GitHub secrets", False, "Could not list organization secrets"
                )

        except Exception as e:
            self.add_check("GitHub secrets", False, str(e))

    def check_infrastructure_files(self):
        """Check required infrastructure files"""
        files_to_check = [
            ("ESC Config", "infrastructure/esc/lambda-labs-h200-config.yaml"),
            ("Sync Script", "scripts/ci/sync_from_gh_to_pulumi.py"),
            ("GitHub Workflow", ".github/workflows/sync_secrets.yml"),
            ("Validation Script", "scripts/validate_lambda_labs_integration.py"),
            ("Verification Script", "scripts/verify_lambda_labs_h200_setup.py"),
        ]

        all_exist = True
        missing = []

        for name, filepath in files_to_check:
            if Path(filepath).exists():
                # Don't add individual success for brevity
                pass
            else:
                all_exist = False
                missing.append(name)

        if all_exist:
            self.add_check("Infrastructure files", True, "All required files present")
        else:
            self.add_check(
                "Infrastructure files", False, f"Missing: {', '.join(missing)}"
            )

    def generate_report(self):
        """Generate and display the checklist report"""
        print("\n" + "=" * 60)
        print("🚀 Lambda Labs H200 Pre-Deployment Checklist")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Directory: {os.getcwd()}")
        print("=" * 60 + "\n")

        # Display checks
        all_passed = True
        for check in self.checks:
            status = "✅" if check["passed"] else "❌"
            print(f"{status} {check['name']}")
            if check["details"]:
                print(f"   └─ {check['details']}")
            if not check["passed"]:
                all_passed = False

        # Display warnings
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")

        # Summary
        print("\n" + "=" * 60)
        passed_count = sum(1 for c in self.checks if c["passed"])
        total_count = len(self.checks)

        print(f"📊 Summary: {passed_count}/{total_count} checks passed")

        if all_passed:
            print("\n✅ All checks passed! Ready for H200 deployment.")
            print("\n🎯 Next steps:")
            print("   1. Run: gh workflow run sync_secrets.yml")
            print(
                "   2. Deploy: cd infrastructure && pulumi up -s sophia-ai-h200-production"
            )
            print("   3. Verify: python scripts/verify_lambda_labs_h200_setup.py")
        else:
            print(
                "\n❌ Some checks failed. Please fix the issues above before deploying."
            )
            print("\n💡 Quick fixes:")
            print("   • GitHub CLI: gh auth login")
            print("   • Pulumi: pulumi login")
            print("   • SSH Key: ssh-keygen -t ed25519 -f ~/.ssh/lynn_sophia_h200_key")
            print("   • API Key: export LAMBDA_LABS_API_KEY='your-key'")

        print("=" * 60 + "\n")

        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "checks": self.checks,
            "warnings": self.warnings,
            "passed": all_passed,
            "summary": f"{passed_count}/{total_count}",
        }

        with open("pre_deployment_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("📄 Report saved to: pre_deployment_report.json")

        return 0 if all_passed else 1


def main():
    """Run all pre-deployment checks"""
    checker = PreDeploymentChecker()

    # Run all checks
    print("🔍 Running pre-deployment checks...")

    checker.check_github_cli()
    checker.check_pulumi()
    checker.check_ssh_key()
    checker.check_lambda_labs_api()
    checker.check_docker()
    checker.check_pulumi_esc_env()
    checker.check_github_secrets()
    checker.check_infrastructure_files()

    # Generate report
    return checker.generate_report()


if __name__ == "__main__":
    sys.exit(main())
