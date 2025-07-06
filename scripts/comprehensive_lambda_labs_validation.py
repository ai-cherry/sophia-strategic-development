#!/usr/bin/env python3
"""
Comprehensive Lambda Labs Infrastructure Validation
Validates GitHub CLI, Lambda Labs API, Pulumi ESC, SSH keys, and all configurations
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime

import requests


class ComprehensiveLambdaLabsValidator:
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "github_cli": {},
            "lambda_labs": {},
            "pulumi": {},
            "ssh_keys": {},
            "secrets": {},
            "infrastructure": {},
            "recommendations": [],
        }

    def print_section(self, title):
        """Print a section header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")

    def validate_github_cli(self):
        """Validate GitHub CLI authentication and access"""
        self.print_section("GITHUB CLI VALIDATION")

        try:
            # Check auth status
            result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ GitHub CLI authenticated")
                self.validation_results["github_cli"]["authenticated"] = True

                # Check organization access
                org_result = subprocess.run(
                    ["gh", "api", "/orgs/ai-cherry"], capture_output=True, text=True
                )
                if org_result.returncode == 0:
                    org_data = json.loads(org_result.stdout)
                    print(f"✅ Access to organization: {org_data['login']}")
                    self.validation_results["github_cli"]["organization"] = org_data[
                        "login"
                    ]

                    # Check repository access
                    repo_result = subprocess.run(
                        ["gh", "api", "/repos/ai-cherry/sophia-main"],
                        capture_output=True,
                        text=True,
                    )
                    if repo_result.returncode == 0:
                        print("✅ Access to sophia-main repository")
                        self.validation_results["github_cli"]["repo_access"] = True

                        # Check secrets access
                        secrets_result = subprocess.run(
                            [
                                "gh",
                                "api",
                                "/repos/ai-cherry/sophia-main/actions/secrets",
                            ],
                            capture_output=True,
                            text=True,
                        )
                        if secrets_result.returncode == 0:
                            secrets_data = json.loads(secrets_result.stdout)
                            secret_count = secrets_data.get("total_count", 0)
                            print(f"✅ Access to {secret_count} repository secrets")
                            self.validation_results["github_cli"][
                                "secrets_count"
                            ] = secret_count
                        else:
                            print("❌ No access to repository secrets")
                            self.validation_results["github_cli"]["secrets_count"] = 0
                else:
                    print("❌ No access to ai-cherry organization")
                    self.validation_results["github_cli"]["organization"] = None
            else:
                print("❌ GitHub CLI not authenticated")
                self.validation_results["github_cli"]["authenticated"] = False

        except Exception as e:
            print(f"❌ GitHub CLI validation failed: {e}")
            self.validation_results["github_cli"]["error"] = str(e)

    def validate_lambda_labs(self):
        """Validate Lambda Labs API access and infrastructure"""
        self.print_section("LAMBDA LABS VALIDATION")

        api_key = os.environ.get("LAMBDA_LABS_API_KEY")
        if not api_key:
            print("❌ LAMBDA_LABS_API_KEY not set")
            self.validation_results["lambda_labs"]["api_key_set"] = False
            return

        print("✅ LAMBDA_LABS_API_KEY is set")
        self.validation_results["lambda_labs"]["api_key_set"] = True

        try:
            # Test API access
            headers = {"Authorization": f"Bearer {api_key}"}

            # Get instances
            instances_url = "https://cloud.lambdalabs.com/api/v1/instances"
            response = requests.get(instances_url, headers=headers)

            if response.status_code == 200:
                instances = response.json()["data"]
                print("✅ Lambda Labs API access verified")
                print(f"✅ Found {len(instances)} instances")

                self.validation_results["lambda_labs"]["api_access"] = True
                self.validation_results["lambda_labs"]["instances"] = []

                # Categorize instances
                a10_instances = []
                gh200_instances = []

                for instance in instances:
                    instance_info = {
                        "id": instance["id"],
                        "name": instance["name"],
                        "instance_type": instance["instance_type"]["name"],
                        "ip_address": instance["ip"],
                        "status": instance["status"],
                    }

                    if "a10" in instance["instance_type"]["name"].lower():
                        a10_instances.append(instance_info)
                    elif "gh200" in instance["instance_type"]["name"].lower():
                        gh200_instances.append(instance_info)

                    self.validation_results["lambda_labs"]["instances"].append(
                        instance_info
                    )

                print("\n📊 Instance Summary:")
                print(f"  - A10 instances: {len(a10_instances)}")
                for inst in a10_instances:
                    print(
                        f"    • {inst['name']} ({inst['ip_address']}) - {inst['status']}"
                    )

                print(f"  - GH200 instances: {len(gh200_instances)}")
                for inst in gh200_instances:
                    print(
                        f"    • {inst['name']} ({inst['ip_address']}) - {inst['status']}"
                    )

                # Check SSH keys
                ssh_keys_url = "https://cloud.lambdalabs.com/api/v1/ssh-keys"
                ssh_response = requests.get(ssh_keys_url, headers=headers)

                if ssh_response.status_code == 200:
                    ssh_keys = ssh_response.json()["data"]
                    print(f"\n✅ Found {len(ssh_keys)} SSH keys in Lambda Labs")

                    self.validation_results["lambda_labs"]["ssh_keys"] = []
                    for key in ssh_keys:
                        key_info = {"id": key["id"], "name": key["name"]}
                        self.validation_results["lambda_labs"]["ssh_keys"].append(
                            key_info
                        )
                        print(f"  • {key['name']}")

                        # Check if this is the expected H200 key
                        if key["name"] == "lynn-sophia-h200-key":
                            print("    ✅ Found expected H200 SSH key")
                            self.validation_results["lambda_labs"][
                                "h200_key_found"
                            ] = True

            else:
                print(f"❌ Lambda Labs API access failed: {response.status_code}")
                self.validation_results["lambda_labs"]["api_access"] = False
                self.validation_results["lambda_labs"]["error"] = response.text

        except Exception as e:
            print(f"❌ Lambda Labs validation failed: {e}")
            self.validation_results["lambda_labs"]["error"] = str(e)

    def validate_pulumi(self):
        """Validate Pulumi access and ESC configuration"""
        self.print_section("PULUMI VALIDATION")

        token = os.environ.get("PULUMI_ACCESS_TOKEN")
        if not token:
            print("❌ PULUMI_ACCESS_TOKEN not set")
            self.validation_results["pulumi"]["token_set"] = False
            return

        print("✅ PULUMI_ACCESS_TOKEN is set")
        self.validation_results["pulumi"]["token_set"] = True

        try:
            # Check Pulumi login
            login_result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True
            )
            if login_result.returncode == 0:
                username = login_result.stdout.strip()
                print(f"✅ Pulumi logged in as: {username}")
                self.validation_results["pulumi"]["logged_in"] = True
                self.validation_results["pulumi"]["username"] = username

                # List ESC environments
                esc_result = subprocess.run(
                    ["pulumi", "env", "ls", "--org", "scoobyjava-org"],
                    capture_output=True,
                    text=True,
                )
                if esc_result.returncode == 0:
                    environments = esc_result.stdout.strip().split("\n")
                    print(f"\n✅ Found {len(environments)} ESC environments:")

                    self.validation_results["pulumi"]["environments"] = []
                    for env in environments:
                        if env.strip():
                            print(f"  • {env.strip()}")
                            self.validation_results["pulumi"]["environments"].append(
                                env.strip()
                            )

                    # Check specific H200 environment
                    h200_env = "scoobyjava-org/sophia-ai-h200-production"
                    if any(h200_env in env for env in environments):
                        print("\n✅ Found H200 production environment")

                        # Get environment details
                        env_get_result = subprocess.run(
                            ["pulumi", "env", "get", h200_env],
                            capture_output=True,
                            text=True,
                        )
                        if env_get_result.returncode == 0:
                            print("✅ Can access H200 environment configuration")
                            self.validation_results["pulumi"]["h200_env_access"] = True

                            # Check for Lambda Labs secrets
                            if "lambda_labs" in env_get_result.stdout:
                                print("✅ Lambda Labs configuration found in ESC")
                                self.validation_results["pulumi"][
                                    "lambda_labs_config"
                                ] = True
                    else:
                        print("\n❌ H200 production environment not found")
                        self.validation_results["pulumi"]["h200_env_access"] = False

            else:
                print("❌ Pulumi not logged in")
                self.validation_results["pulumi"]["logged_in"] = False

        except Exception as e:
            print(f"❌ Pulumi validation failed: {e}")
            self.validation_results["pulumi"]["error"] = str(e)

    def validate_ssh_configuration(self):
        """Validate SSH keys and configuration"""
        self.print_section("SSH CONFIGURATION VALIDATION")

        ssh_dir = os.path.expanduser("~/.ssh")
        expected_keys = [
            "lynn-sophia-h200-key",
            "lynn_sophia_h200_key",
            "id_ed25519",
            "id_rsa",
        ]

        self.validation_results["ssh_keys"]["found_keys"] = []

        for key_name in expected_keys:
            key_path = os.path.join(ssh_dir, key_name)
            if os.path.exists(key_path):
                # Check permissions
                stat_info = os.stat(key_path)
                permissions = oct(stat_info.st_mode)[-3:]

                if permissions == "600":
                    print(f"✅ Found SSH key: {key_name} (permissions: {permissions})")
                    status = "valid"
                else:
                    print(
                        f"⚠️ Found SSH key: {key_name} (permissions: {permissions} - should be 600)"
                    )
                    status = "wrong_permissions"

                self.validation_results["ssh_keys"]["found_keys"].append(
                    {
                        "name": key_name,
                        "path": key_path,
                        "permissions": permissions,
                        "status": status,
                    }
                )

    def check_github_secrets_sync(self):
        """Check if GitHub secrets are properly synced"""
        self.print_section("GITHUB SECRETS SYNC VALIDATION")

        try:
            # Check repository secrets
            result = subprocess.run(
                ["gh", "api", "/repos/ai-cherry/sophia-main/actions/secrets"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                secrets_data = json.loads(result.stdout)
                secrets = secrets_data.get("secrets", [])

                # Expected Lambda Labs secrets
                expected_secrets = [
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

                found_secrets = [s["name"] for s in secrets]

                print(f"✅ Found {len(secrets)} total secrets in repository")

                self.validation_results["secrets"]["github_total"] = len(secrets)
                self.validation_results["secrets"]["lambda_labs_secrets"] = {}

                for secret_name in expected_secrets:
                    if secret_name in found_secrets:
                        print(f"  ✅ {secret_name}")
                        self.validation_results["secrets"]["lambda_labs_secrets"][
                            secret_name
                        ] = True
                    else:
                        print(f"  ❌ {secret_name} - MISSING")
                        self.validation_results["secrets"]["lambda_labs_secrets"][
                            secret_name
                        ] = False

            else:
                print("❌ Failed to access GitHub secrets")
                self.validation_results["secrets"]["error"] = result.stderr

        except Exception as e:
            print(f"❌ GitHub secrets validation failed: {e}")
            self.validation_results["secrets"]["error"] = str(e)

    def check_infrastructure_files(self):
        """Check if all required infrastructure files exist"""
        self.print_section("INFRASTRUCTURE FILES VALIDATION")

        required_files = {
            "Pulumi ESC Config": "infrastructure/esc/lambda-labs-gh200-config.yaml",
            "Lambda Labs Provisioner": "infrastructure/enhanced_lambda_labs_provisioner.py",
            "Memory Architecture": "backend/core/enhanced_memory_architecture.py",
            "H200 Dockerfile": "Dockerfile.gh200",
            "H200 Requirements": "requirements-gh200.txt",
            "Pulumi Stack": "infrastructure/pulumi/enhanced-gh200-stack.ts",
            "Sync Script": "scripts/ci/sync_from_gh_to_pulumi.py",
            "GitHub Workflow": ".github/workflows/sync_secrets.yml",
        }

        self.validation_results["infrastructure"]["files"] = {}

        for file_desc, file_path in required_files.items():
            if os.path.exists(file_path):
                print(f"✅ {file_desc}: {file_path}")
                self.validation_results["infrastructure"]["files"][file_path] = True
            else:
                print(f"❌ {file_desc}: {file_path} - NOT FOUND")
                self.validation_results["infrastructure"]["files"][file_path] = False

    def generate_recommendations(self):
        """Generate recommendations based on validation results"""
        self.print_section("RECOMMENDATIONS")

        recommendations = []

        # Check GitHub CLI
        if not self.validation_results["github_cli"].get("authenticated"):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "issue": "GitHub CLI not authenticated",
                    "action": "Run: gh auth login",
                }
            )

        # Check Lambda Labs
        if not self.validation_results["lambda_labs"].get("api_access"):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "issue": "Lambda Labs API access failed",
                    "action": "Verify LAMBDA_LABS_API_KEY is correct",
                }
            )

        if not self.validation_results["lambda_labs"].get("h200_key_found"):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "issue": "H200 SSH key not found in Lambda Labs",
                    "action": "Create lynn-sophia-h200-key in Lambda Labs",
                }
            )

        # Check Pulumi
        if not self.validation_results["pulumi"].get("h200_env_access"):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "issue": "Cannot access H200 Pulumi environment",
                    "action": "Create scoobyjava-org/sophia-ai-h200-production environment",
                }
            )

        # Check SSH keys
        if not any(
            k["name"] in ["lynn-sophia-h200-key", "lynn_sophia_h200_key"]
            for k in self.validation_results["ssh_keys"].get("found_keys", [])
        ):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "issue": "H200 SSH key not found locally",
                    "action": "Generate SSH key: ssh-keygen -t ed25519 -f ~/.ssh/lynn_sophia_h200_key",
                }
            )

        # Check GitHub secrets
        missing_secrets = [
            k
            for k, v in self.validation_results["secrets"]
            .get("lambda_labs_secrets", {})
            .items()
            if not v
        ]
        if missing_secrets:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "issue": f"Missing GitHub secrets: {', '.join(missing_secrets)}",
                    "action": "Add missing secrets to GitHub repository settings",
                }
            )

        # Check infrastructure files
        missing_files = [
            k
            for k, v in self.validation_results["infrastructure"]
            .get("files", {})
            .items()
            if not v
        ]
        if missing_files:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "issue": "Missing infrastructure files",
                    "action": f"Create missing files: {', '.join(missing_files)}",
                }
            )

        # Note about GPU model mismatch
        recommendations.append(
            {
                "priority": "MEDIUM",
                "issue": "H200 references need updating to GH200",
                "action": "Run: python scripts/update_h200_to_gh200.py",
            }
        )

        self.validation_results["recommendations"] = recommendations

        if recommendations:
            for rec in recommendations:
                priority_emoji = "🔴" if rec["priority"] == "HIGH" else "🟡"
                print(f"\n{priority_emoji} [{rec['priority']}] {rec['issue']}")
                print(f"   Action: {rec['action']}")
        else:
            print("\n✅ No critical issues found!")

    def save_results(self):
        """Save validation results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lambda_labs_validation_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        print(f"\n💾 Results saved to: {filename}")

    def run_validation(self):
        """Run complete validation"""
        print("🚀 Starting Comprehensive Lambda Labs Validation")
        print(f"Timestamp: {self.validation_results['timestamp']}")

        self.validate_github_cli()
        self.validate_lambda_labs()
        self.validate_pulumi()
        self.validate_ssh_configuration()
        self.check_github_secrets_sync()
        self.check_infrastructure_files()
        self.generate_recommendations()
        self.save_results()

        print("\n" + "=" * 60)
        print("✅ Validation Complete!")
        print("=" * 60)


if __name__ == "__main__":
    validator = ComprehensiveLambdaLabsValidator()
    validator.run_validation()
