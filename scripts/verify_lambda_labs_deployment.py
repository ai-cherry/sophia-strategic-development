#!/usr/bin/env python3
"""
Verify Lambda Labs deployment configuration.
Ensures all settings are correct and no exposed credentials exist.
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configuration constants
CORRECT_IP = "192.222.58.232"
CORRECT_SSH_KEY = "sophia2025.pem"
CORRECT_SSH_PATH = "~/.ssh/sophia2025.pem"

# Old values that should NOT exist
FORBIDDEN_IPS = [
    "192.222.58.232",
    "192.222.58.232",
    "104.171.202.103",
    "192.222.58.232",
    "104.171.202.117",
    "104.171.202.134",
    "155.248.194.183",
    "192.222.58.232"
]

FORBIDDEN_KEYS = [
    "sophia2025.pem",
    "sophia2025.pem",
    "sophia-ai-key",
    "lambda_labs_ssh_key"
]

# Patterns for exposed credentials
CREDENTIAL_PATTERNS = {
    'lambda_api_key': re.compile(r'secret_sophia5apikey_[a-zA-Z0-9]+\.[a-zA-Z0-9]+'),
    'lambda_cloud_api_key': re.compile(r'secret_sophiacloudapi_[a-zA-Z0-9]+\.[a-zA-Z0-9]+'),
    'github_pat': re.compile(r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----')
}


class DeploymentVerifier:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []

    def check_pulumi_esc(self) -> bool:
        """Verify Pulumi ESC is configured correctly"""
        print("🔍 Checking Pulumi ESC configuration...")

        try:
            # Check if we can access Pulumi ESC
            from backend.core.auto_esc_config import get_config_value

            # Try to get Lambda Labs configuration
            lambda_ip = get_config_value("lambda_labs_production_ip")
            lambda_api_key = get_config_value("lambda_api_key")
            lambda_cloud_api_key = get_config_value("lambda_cloud_api_key")

            if lambda_ip == CORRECT_IP:
                self.successes.append("✅ Pulumi ESC has correct Lambda Labs IP")
            else:
                self.issues.append(f"❌ Pulumi ESC has wrong IP: {lambda_ip} (should be {CORRECT_IP})")

            if lambda_api_key and len(lambda_api_key) > 20:
                self.successes.append("✅ Lambda API key present in Pulumi ESC")
            else:
                self.issues.append("❌ Lambda API key missing or invalid in Pulumi ESC")

            if lambda_cloud_api_key and len(lambda_cloud_api_key) > 20:
                self.successes.append("✅ Lambda Cloud API key present in Pulumi ESC")
            else:
                self.issues.append("❌ Lambda Cloud API key missing or invalid in Pulumi ESC")

            return True

        except Exception as e:
            self.issues.append(f"❌ Cannot access Pulumi ESC: {e}")
            return False

    def check_ssh_key(self) -> bool:
        """Verify SSH key exists and has correct permissions"""
        print("🔑 Checking SSH key configuration...")

        ssh_key_path = Path(os.path.expanduser(CORRECT_SSH_PATH))

        if ssh_key_path.exists():
            self.successes.append(f"✅ SSH key exists at {CORRECT_SSH_PATH}")

            # Check permissions
            stat_info = ssh_key_path.stat()
            mode = oct(stat_info.st_mode)[-3:]

            if mode == "600":
                self.successes.append("✅ SSH key has correct permissions (600)")
            else:
                self.warnings.append(f"⚠️  SSH key has permissions {mode} (should be 600)")

            # Test SSH connection
            result = subprocess.run(
                ["ssh", "-i", str(ssh_key_path), "-o", "ConnectTimeout=5",
                 "-o", "StrictHostKeyChecking=no", f"ubuntu@{CORRECT_IP}", "echo OK"],
                check=False, capture_output=True
            )

            if result.returncode == 0:
                self.successes.append(f"✅ SSH connection to {CORRECT_IP} successful")
            else:
                self.issues.append(f"❌ SSH connection failed: {result.stderr.decode()}")

            return True
        else:
            self.issues.append(f"❌ SSH key not found at {CORRECT_SSH_PATH}")
            return False

    def scan_for_old_references(self):
        """Scan codebase for old IP addresses and SSH keys"""
        print("🔍 Scanning for outdated references...")

        files_with_issues = []

        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'archive', '.venv']):
                continue

            for file in files:
                if file.endswith(('.py', '.sh', '.yml', '.yaml', '.json', '.md')):
                    filepath = Path(root) / file

                    try:
                        with open(filepath, encoding='utf-8') as f:
                            content = f.read()

                        # Check for old IPs
                        for old_ip in FORBIDDEN_IPS:
                            if old_ip in content:
                                files_with_issues.append((str(filepath), f"Contains old IP: {old_ip}"))

                        # Check for old SSH keys
                        for old_key in FORBIDDEN_KEYS:
                            if old_key in content:
                                files_with_issues.append((str(filepath), f"Contains old SSH key: {old_key}"))

                    except Exception:
                        pass

        if files_with_issues:
            self.issues.append(f"❌ Found {len(files_with_issues)} files with outdated references")
            for filepath, issue in files_with_issues[:10]:  # Show first 10
                self.issues.append(f"   - {filepath}: {issue}")

            if len(files_with_issues) > 10:
                self.issues.append(f"   ... and {len(files_with_issues) - 10} more files")
        else:
            self.successes.append("✅ No outdated IP addresses or SSH keys found")

    def scan_for_exposed_credentials(self):
        """Scan for exposed API keys and credentials"""
        print("🔐 Scanning for exposed credentials...")

        exposed_credentials = []

        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'archive', '.venv']):
                continue

            for file in files:
                if file.endswith(('.py', '.sh', '.yml', '.yaml', '.json')):
                    filepath = Path(root) / file

                    try:
                        with open(filepath, encoding='utf-8') as f:
                            content = f.read()

                        # Check for credential patterns
                        for cred_type, pattern in CREDENTIAL_PATTERNS.items():
                            matches = pattern.findall(content)
                            if matches:
                                exposed_credentials.append((str(filepath), cred_type, len(matches)))

                    except Exception:
                        pass

        if exposed_credentials:
            self.issues.append(f"❌ Found exposed credentials in {len(exposed_credentials)} files")
            for filepath, cred_type, count in exposed_credentials:
                self.issues.append(f"   - {filepath}: {count} {cred_type} exposed")
        else:
            self.successes.append("✅ No exposed credentials found")

    def check_github_actions(self):
        """Check GitHub Actions workflows are configured correctly"""
        print("🔧 Checking GitHub Actions workflows...")

        workflows_dir = Path('.github/workflows')
        if not workflows_dir.exists():
            self.warnings.append("⚠️  No GitHub Actions workflows found")
            return

        workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))

        for workflow_file in workflow_files:
            try:
                with open(workflow_file) as f:
                    content = yaml.safe_load(f)

                if content and isinstance(content, dict):
                    # Check environment variables
                    if 'env' in content:
                        if 'LAMBDA_LABS_IP' in content['env']:
                            if content['env']['LAMBDA_LABS_IP'] == CORRECT_IP:
                                self.successes.append(f"✅ {workflow_file.name} has correct Lambda Labs IP")
                            else:
                                self.issues.append(f"❌ {workflow_file.name} has wrong IP: {content['env']['LAMBDA_LABS_IP']}")

                    # Check for hardcoded credentials
                    yaml_str = str(content)
                    for pattern in CREDENTIAL_PATTERNS.values():
                        if pattern.search(yaml_str):
                            self.issues.append(f"❌ {workflow_file.name} contains exposed credentials")
                            break

            except Exception as e:
                self.warnings.append(f"⚠️  Could not parse {workflow_file.name}: {e}")

    def check_docker_configuration(self):
        """Check Docker configuration files"""
        print("🐳 Checking Docker configuration...")

        # Check docker-compose files
        compose_files = list(Path('.').glob('docker-compose*.yml')) + list(Path('.').glob('docker-compose*.yaml'))

        for compose_file in compose_files:
            try:
                with open(compose_file) as f:
                    content = yaml.safe_load(f)

                if content and 'services' in content:
                    # Check for hardcoded passwords
                    yaml_str = yaml.dump(content)
                    if 'password:' in yaml_str.lower() and '${' not in yaml_str:
                        self.warnings.append(f"⚠️  {compose_file.name} may contain hardcoded passwords")

            except Exception:
                pass

        # Check Dockerfiles
        dockerfiles = list(Path('.').glob('Dockerfile*'))

        for dockerfile in dockerfiles:
            try:
                with open(dockerfile) as f:
                    content = f.read()

                # Check for exposed secrets
                if 'ENV ' in content:
                    for pattern in CREDENTIAL_PATTERNS.values():
                        if pattern.search(content):
                            self.issues.append(f"❌ {dockerfile.name} contains exposed credentials")
                            break

            except Exception:
                pass

    def generate_report(self):
        """Generate verification report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"lambda_labs_verification_report_{timestamp}.md"

        with open(report_file, 'w') as f:
            f.write("# Lambda Labs Deployment Verification Report\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n")
            f.write(f"**Target IP**: {CORRECT_IP}\n")
            f.write(f"**SSH Key**: {CORRECT_SSH_PATH}\n\n")

            # Summary
            f.write("## Summary\n\n")
            f.write(f"- ✅ **Successes**: {len(self.successes)}\n")
            f.write(f"- ⚠️  **Warnings**: {len(self.warnings)}\n")
            f.write(f"- ❌ **Issues**: {len(self.issues)}\n\n")

            # Details
            if self.successes:
                f.write("## ✅ Successes\n\n")
                for success in self.successes:
                    f.write(f"{success}\n")
                f.write("\n")

            if self.warnings:
                f.write("## ⚠️  Warnings\n\n")
                for warning in self.warnings:
                    f.write(f"{warning}\n")
                f.write("\n")

            if self.issues:
                f.write("## ❌ Issues\n\n")
                for issue in self.issues:
                    f.write(f"{issue}\n")
                f.write("\n")

            # Recommendations
            f.write("## Recommendations\n\n")

            if self.issues:
                f.write("1. **Fix Critical Issues**:\n")
                f.write("   ```bash\n")
                f.write("   python scripts/update_lambda_labs_references.py\n")
                f.write("   python scripts/cleanup_lambda_labs_deployment.py\n")
                f.write("   ```\n\n")

            if self.warnings:
                f.write("2. **Address Warnings**:\n")
                f.write("   - Review and update configuration files\n")
                f.write("   - Ensure proper permissions on SSH keys\n\n")

            f.write("3. **Regular Verification**:\n")
            f.write("   ```bash\n")
            f.write("   python scripts/verify_lambda_labs_deployment.py\n")
            f.write("   ```\n\n")

            # Configuration Reference
            f.write("## Correct Configuration\n\n")
            f.write("```yaml\n")
            f.write("# Lambda Labs Production Instance\n")
            f.write(f"ip: {CORRECT_IP}\n")
            f.write("type: GH200\n")
            f.write(f"ssh_key: {CORRECT_SSH_PATH}\n")
            f.write("user: ubuntu\n")
            f.write("\n")
            f.write("# Service Ports\n")
            f.write("backend: 8000\n")
            f.write("mcp_servers: 9000-9100\n")
            f.write("prometheus: 9090\n")
            f.write("grafana: 3000\n")
            f.write("```\n")

        print(f"\n📊 Report saved to: {report_file}")

    def run(self):
        """Run all verification checks"""
        print("🚀 Lambda Labs Deployment Verification")
        print("=" * 50)

        # Run checks
        self.check_pulumi_esc()
        self.check_ssh_key()
        self.scan_for_old_references()
        self.scan_for_exposed_credentials()
        self.check_github_actions()
        self.check_docker_configuration()

        # Generate report
        self.generate_report()

        # Summary
        print("\n📈 Verification Summary:")
        print(f"  ✅ Successes: {len(self.successes)}")
        print(f"  ⚠️  Warnings: {len(self.warnings)}")
        print(f"  ❌ Issues: {len(self.issues)}")

        if self.issues:
            print("\n❌ Critical issues found! Review the report for details.")
            return False
        elif self.warnings:
            print("\n⚠️  Some warnings found. Review the report for recommendations.")
            return True
        else:
            print("\n✅ All checks passed! Deployment configuration is correct.")
            return True


def main():
    verifier = DeploymentVerifier()
    success = verifier.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
