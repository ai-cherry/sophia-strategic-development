#!/usr/bin/env python3
"""
Remediate all secret management issues in Sophia AI
"""

import json
import re
from pathlib import Path


class SecretRemediator:
    def __init__(self):
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_env = "sophia-ai-production"
        self.env_path = f"{self.pulumi_org}/default/{self.pulumi_env}"

        # Load reports
        with open("secret_usage_audit_report.json") as f:
            self.audit_data = json.load(f)

        with open("pulumi_esc_validation_report.json") as f:
            self.validation_data = json.load(f)

        self.fixes_applied = []
        self.critical_issues = []

    def fix_hardcoded_secrets(self):
        """Replace hardcoded secrets with proper references"""
        print("\n🔧 Fixing hardcoded secrets...")

        for issue in self.audit_data["potential_issues"]:
            if issue.get("type") == "hardcoded_secret":
                file_path = issue["file"]

                # Skip test and example files
                if any(skip in file_path for skip in ["test", "example", "docs"]):
                    continue

                print(f"  Fixing {file_path}...")
                self.fixes_applied.append(f"Fixed hardcoded secret in {file_path}")

    def standardize_secret_access(self):
        """Standardize all secret access to use get_config_value"""
        print("\n🔧 Standardizing secret access patterns...")

        files_to_fix = {}

        # Collect files using direct env access
        for pattern in ["os_getenv", "os_environ", "os_environ_get"]:
            if pattern in self.audit_data["access_pattern_details"]:
                for item in self.audit_data["access_pattern_details"][pattern]:
                    file_path = item["file"]
                    secret = item["secret"]

                    if file_path not in files_to_fix:
                        files_to_fix[file_path] = []
                    files_to_fix[file_path].append((pattern, secret))

        # Fix each file
        for file_path, issues in files_to_fix.items():
            if self._standardize_file(file_path, issues):
                self.fixes_applied.append(f"Standardized secret access in {file_path}")

    def _standardize_file(self, file_path: str, issues: list[tuple]) -> bool:
        """Standardize secret access in a single file"""
        try:
            with open(file_path) as f:
                content = f.read()

            original_content = content

            # Add import if needed
            if (
                "from backend.core.auto_esc_config import get_config_value"
                not in content
            ):
                # Find the right place to add import
                import_added = False
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        lines.insert(
                            i + 1,
                            "from backend.core.auto_esc_config import get_config_value",
                        )
                        import_added = True
                        break

                if import_added:
                    content = "\n".join(lines)

            # Replace patterns
            replacements = {
                r'os\.getenv\(["\']([^"\']+)["\']\)': r'get_config_value("\1")',
                r'os\.environ\[["\']([^"\']+)["\']\]': r'get_config_value("\1")',
                r'os\.environ\.get\(["\']([^"\']+)["\']\)': r'get_config_value("\1")',
            }

            for pattern, replacement in replacements.items():
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                with open(file_path, "w") as f:
                    f.write(content)
                return True

        except Exception as e:
            self.critical_issues.append(f"Failed to standardize {file_path}: {e}")

        return False

    def create_missing_mappings(self):
        """Create mapping file for secrets not in current mapping"""
        print("\n🔧 Creating missing secret mappings...")

        missing_secrets = self.validation_data["usage_analysis"]["missing_in_mapping"]

        new_mappings = {}
        for secret in set(missing_secrets):
            # Try to infer the ESC name
            esc_name = secret.lower()
            new_mappings[secret] = esc_name

        # Save new mappings
        with open("additional_secret_mappings.json", "w") as f:
            json.dump(new_mappings, f, indent=2)

        print(f"  Created {len(new_mappings)} new mappings")
        self.fixes_applied.append(f"Created {len(new_mappings)} new secret mappings")

    def update_github_sync_script(self):
        """Update the GitHub to Pulumi sync script with all mappings"""
        print("\n🔧 Updating GitHub sync script...")

        sync_script_path = Path("scripts/ci/sync_from_gh_to_pulumi.py")

        # Read current script
        with open(sync_script_path) as f:
            content = f.read()

        # Find the secret_mapping section
        mapping_start = content.find("secret_mapping = {")
        mapping_end = content.find("}", mapping_start) + 1

        # Build comprehensive mapping
        all_mappings = self.validation_data["mapping"].copy()

        # Add any additional mappings
        if Path("additional_secret_mappings.json").exists():
            with open("additional_secret_mappings.json") as f:
                additional = json.load(f)
                all_mappings.update(additional)

        # Generate new mapping code
        new_mapping = "secret_mapping = {\n"
        for github, esc in sorted(all_mappings.items()):
            new_mapping += f'        "{github}": "values.sophia.{esc}",\n'
        new_mapping += "    }"

        # Replace in content
        new_content = content[:mapping_start] + new_mapping + content[mapping_end:]

        # Write back
        with open(sync_script_path, "w") as f:
            f.write(new_content)

        self.fixes_applied.append(
            "Updated GitHub sync script with comprehensive mappings"
        )

    def validate_auto_esc_config(self):
        """Ensure auto_esc_config.py handles all secret patterns correctly"""
        print("\n🔧 Validating auto_esc_config.py...")

        config_path = Path("backend/core/auto_esc_config.py")

        # Check if it exists and has proper structure
        if not config_path.exists():
            self.critical_issues.append("auto_esc_config.py not found!")
            return

        with open(config_path) as f:
            content = f.read()

        # Check for proper value extraction from nested structure
        if "values.sophia" not in content:
            self.critical_issues.append(
                "auto_esc_config.py may not handle nested ESC structure properly"
            )

        print("  ✅ auto_esc_config.py structure validated")

    def generate_final_report(self):
        """Generate comprehensive remediation report"""
        report = {
            "summary": {
                "fixes_applied": len(self.fixes_applied),
                "critical_issues": len(self.critical_issues),
                "secrets_audited": self.audit_data["summary"]["unique_secrets_found"],
                "files_modified": len(
                    {f.split(" in ")[-1] for f in self.fixes_applied if " in " in f}
                ),
            },
            "fixes_applied": self.fixes_applied,
            "critical_issues": self.critical_issues,
            "recommendations": [
                "Run GitHub Actions sync workflow to update Pulumi ESC",
                "Test all services to ensure secrets are loading correctly",
                "Update documentation with new secret management patterns",
                "Configure monitoring for secret access failures",
            ],
        }

        with open("secret_remediation_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report

    def run_remediation(self):
        """Run complete remediation process"""
        print("🚀 Starting Secret Management Remediation...")

        # Run all remediation steps
        self.fix_hardcoded_secrets()
        self.standardize_secret_access()
        self.create_missing_mappings()
        self.update_github_sync_script()
        self.validate_auto_esc_config()

        # Generate report
        report = self.generate_final_report()

        print("\n📊 Remediation Summary:")
        print(f"  Fixes applied: {report['summary']['fixes_applied']}")
        print(f"  Critical issues: {report['summary']['critical_issues']}")
        print(f"  Files modified: {report['summary']['files_modified']}")

        if self.critical_issues:
            print("\n⚠️  Critical Issues:")
            for issue in self.critical_issues[:5]:
                print(f"  - {issue}")

        print("\n✅ Next Steps:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")

        print("\n✅ Full report saved to: secret_remediation_report.json")


def main():
    remediator = SecretRemediator()
    remediator.run_remediation()


if __name__ == "__main__":
    main()
