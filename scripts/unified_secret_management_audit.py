#!/usr/bin/env python3
"""
Unified Secret Management Audit and Implementation
This script performs a DEEP audit of all secret management in Sophia AI
and creates a unified strategy for GitHub → Pulumi ESC → Application flow
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set


class UnifiedSecretManagementAuditor:
    def __init__(self):
        self.project_root = Path.cwd()
        self.findings = {
            "secret_files": [],
            "sync_scripts": [],
            "workflows": [],
            "config_files": [],
            "secret_references": [],
            "issues": [],
            "recommendations": [],
        }
        self.secret_patterns = {
            "env_vars": re.compile(r'os\.getenv\(["\']([A-Z_]+)["\']\)'),
            "get_config": re.compile(r'get_config_value\(["\']([a-z_]+)["\']\)'),
            "github_secrets": re.compile(r"\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}"),
            "esc_refs": re.compile(r"esc\s+env\s+(get|open|set)"),
            "pulumi_refs": re.compile(r"pulumi\s+env\s+(get|set)"),
            "docker_secrets": re.compile(r"docker\s+secret\s+create"),
        }

    def find_all_secret_files(self):
        """Find ALL files related to secret management"""
        print("🔍 Finding all secret-related files...")

        # Patterns to search for
        search_patterns = [
            "sync*secret*",
            "*secret*sync*",
            "*esc*",
            "*pulumi*secret*",
            "*github*secret*",
            "auto_esc_config*",
            "*config_manager*",
            "*env*",
            "*credential*",
        ]

        # Search for files
        for pattern in search_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file() and not any(
                    skip in str(file_path)
                    for skip in [".git", "__pycache__", "node_modules", ".venv"]
                ):
                    self.analyze_file(file_path)

        # Search for GitHub workflows
        workflows_dir = self.project_root / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                self.findings["workflows"].append(str(workflow))
                self.analyze_workflow(workflow)

    def analyze_file(self, file_path: Path):
        """Analyze a file for secret management patterns"""
        try:
            content = file_path.read_text()

            # Check if it's a sync script
            if "sync" in file_path.name.lower() and (
                "secret" in content.lower() or "esc" in content.lower()
            ):
                self.findings["sync_scripts"].append(str(file_path))

            # Check if it's a config file
            if "config" in file_path.name.lower() or "esc" in file_path.name.lower():
                self.findings["config_files"].append(str(file_path))

            # Find secret references
            for pattern_name, pattern in self.secret_patterns.items():
                matches = pattern.findall(content)
                if matches:
                    self.findings["secret_references"].append(
                        {
                            "file": str(file_path),
                            "type": pattern_name,
                            "secrets": list(set(matches)),
                        }
                    )

        except Exception:
            pass

    def analyze_workflow(self, workflow_path: Path):
        """Analyze GitHub workflow for secret usage"""
        try:
            content = workflow_path.read_text()

            # Find all GitHub secrets
            secrets = self.secret_patterns["github_secrets"].findall(content)
            if secrets:
                self.findings["secret_references"].append(
                    {
                        "file": str(workflow_path),
                        "type": "github_workflow",
                        "secrets": list(set(secrets)),
                    }
                )

            # Check if it's a sync workflow
            if "sync" in content.lower() and "secret" in content.lower():
                print(f"  Found sync workflow: {workflow_path.name}")

        except Exception:
            pass

    def get_github_org_secrets(self) -> list[str]:
        """Get list of secrets from GitHub organization (simulated)"""
        # These are the ACTUAL secrets that should be in GitHub org
        return [
            "ANTHROPIC_API_KEY",
            "ASANA_ACCESS_TOKEN",
            "CODACY_API_TOKEN",
            "DOCKER_HUB_ACCESS_TOKEN",
            "DOCKER_TOKEN",
            "ESTUARY_API_TOKEN",
            "FIGMA_PAT",
            "FIGMA_PROJECT_ID",
            "GITHUB_APP_ID",
            "GITHUB_APP_PRIVATE_KEY",
            "GITHUB_TOKEN",
            "GONG_ACCESS_KEY",
            "GONG_ACCESS_KEY_SECRET",
            "GRAFANA_PASSWORD",
            "HUBSPOT_API_KEY",
            "LAMBDA_API_KEY",
            "LAMBDA_LABS_API_KEY",
            "LAMBDA_LABS_SSH_KEY",
            "LINEAR_API_KEY",
            "MEM0_API_KEY",
            "NOTION_API_TOKEN",
            "OPENAI_API_KEY",
            "OPENROUTER_API_KEY",
            "PINECONE_API_KEY",
            "PINECONE_ENVIRONMENT",
            "PORTKEY_API_KEY",
            "POSTGRES_PASSWORD",
            "PULUMI_ACCESS_TOKEN",
            "SLACK_APP_TOKEN",
            "SLACK_BOT_TOKEN",
            "SLACK_SIGNING_SECRET",
            "SLACK_WEBHOOK_URL",
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_DATABASE",
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_ROLE",
            "SNOWFLAKE_USERNAME",
            "SNOWFLAKE_WAREHOUSE",
            "VERCEL_ACCESS_TOKEN",  # Standardized name
            "WEAVIATE_API_KEY",
            "WEAVIATE_URL",
        ]

    def check_pulumi_esc_status(self) -> dict[str, Any]:
        """Check current Pulumi ESC status"""
        print("\n🔐 Checking Pulumi ESC status...")

        esc_status = {
            "connected": False,
            "environment": "default/sophia-ai-production",
            "secrets_count": 0,
            "secrets": [],
        }

        try:
            # Check if we can access ESC
            result = subprocess.run(
                ["esc", "env", "get", "default/sophia-ai-production"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                esc_status["connected"] = True
                # Count secrets (simplified)
                lines = result.stdout.strip().split("\n")
                esc_status["secrets_count"] = len([l for l in lines if ":" in l])
                print(f"  ✅ ESC connected with {esc_status['secrets_count']} values")
            else:
                print(f"  ❌ ESC connection failed: {result.stderr}")
                self.findings["issues"].append("Pulumi ESC connection failed")

        except Exception as e:
            print(f"  ❌ ESC check failed: {e}")
            self.findings["issues"].append(f"ESC check error: {e}")

        return esc_status

    def analyze_sync_workflow(self):
        """Analyze the GitHub Actions sync workflow"""
        print("\n📋 Analyzing sync workflow...")

        sync_workflow = self.project_root / ".github" / "workflows" / "sync_secrets.yml"
        if sync_workflow.exists():
            content = sync_workflow.read_text()

            # Extract secrets from workflow
            workflow_secrets = set(
                self.secret_patterns["github_secrets"].findall(content)
            )
            github_secrets = set(self.get_github_org_secrets())

            # Find mismatches
            missing_in_workflow = github_secrets - workflow_secrets
            extra_in_workflow = workflow_secrets - github_secrets

            if missing_in_workflow:
                self.findings["issues"].append(
                    f"Secrets missing from sync workflow: {missing_in_workflow}"
                )
                print(
                    f"  ⚠️  Missing from workflow: {len(missing_in_workflow)} secrets"
                )

            if extra_in_workflow:
                self.findings["issues"].append(
                    f"Extra secrets in workflow: {extra_in_workflow}"
                )
                print(f"  ⚠️  Extra in workflow: {len(extra_in_workflow)} secrets")

            if not missing_in_workflow and not extra_in_workflow:
                print("  ✅ Workflow has all required secrets")
        else:
            self.findings["issues"].append("sync_secrets.yml workflow not found")
            print("  ❌ sync_secrets.yml not found!")

    def create_unified_strategy(self):
        """Create a unified secret management strategy"""
        print("\n🎯 Creating unified secret management strategy...")

        strategy = {
            "overview": "Unified secret management for Sophia AI",
            "flow": "GitHub Organization Secrets → GitHub Actions → Pulumi ESC → Application",
            "components": {
                "github_org": {
                    "description": "Central secret storage in ai-cherry organization",
                    "secrets": self.get_github_org_secrets(),
                },
                "sync_workflow": {
                    "file": ".github/workflows/sync_secrets.yml",
                    "trigger": "manual or on push to main",
                    "script": "scripts/ci/sync_from_gh_to_pulumi.py",
                },
                "pulumi_esc": {
                    "environment": "default/sophia-ai-production",
                    "organization": "scoobyjava-org",
                    "structure": "flat key-value pairs under values.sophia",
                },
                "application": {
                    "config": "backend/core/auto_esc_config.py",
                    "method": "get_config_value(key)",
                    "fallback": "environment variables → defaults",
                },
            },
            "standardization": {
                "naming": {
                    "github": "UPPERCASE_WITH_UNDERSCORES",
                    "pulumi": "lowercase_with_underscores",
                    "application": "lowercase_with_underscores",
                },
                "mappings": {
                    "VERCEL_ACCESS_TOKEN": "vercel_api_token",
                    "GITHUB_TOKEN": "github_token",
                    "LAMBDA_LABS_API_KEY": "lambda_labs_api_key",
                },
            },
        }

        # Save strategy
        strategy_path = self.project_root / "UNIFIED_SECRET_MANAGEMENT_STRATEGY.md"
        self.write_strategy_document(strategy_path, strategy)

        return strategy

    def write_strategy_document(self, path: Path, strategy: dict):
        """Write the unified strategy document"""
        content = f"""# Unified Secret Management Strategy for Sophia AI

Generated: {datetime.now().isoformat()}

## Overview

This document defines the SINGLE, AUTHORITATIVE secret management strategy for Sophia AI.

## Secret Flow

```
GitHub Organization Secrets (ai-cherry)
           ↓
    GitHub Actions Workflow
           ↓
    sync_from_gh_to_pulumi.py
           ↓
    Pulumi ESC Environment
           ↓
    auto_esc_config.py
           ↓
    Application Code
```

## Components

### 1. GitHub Organization Secrets

Location: https://github.com/organizations/ai-cherry/settings/secrets/actions

All secrets are stored at the organization level with these exact names:

```
{chr(10).join(sorted(strategy['components']['github_org']['secrets']))}
```

### 2. Sync Workflow

File: `.github/workflows/sync_secrets.yml`

- Trigger: Manual dispatch or push to main
- Script: `scripts/ci/sync_from_gh_to_pulumi.py`
- All secrets must be explicitly passed as environment variables

### 3. Pulumi ESC

Environment: `scoobyjava-org/default/sophia-ai-production`

Structure:
```yaml
values:
  sophia:
    secret_name: secret_value
```

### 4. Application Access

File: `backend/core/auto_esc_config.py`

Usage:
```python
from backend.core.auto_esc_config import get_config_value

# Get a secret
api_key = get_config_value("openai_api_key")
```

## Key Mappings

Some secrets have different names between GitHub and the application:

| GitHub Secret | Pulumi/App Key |
|--------------|----------------|
| VERCEL_ACCESS_TOKEN | vercel_api_token |
| GITHUB_TOKEN | github_token |
| ASANA_API_TOKEN | asana_access_token |
| NOTION_API_KEY | notion_api_token |

## Testing

1. Run sync workflow: `gh workflow run sync_secrets.yml`
2. Check ESC: `esc env get default/sophia-ai-production`
3. Test in app: `python scripts/test_secret_access.py`

## Troubleshooting

If secrets aren't working:

1. Check GitHub org has the secret
2. Check workflow includes the secret
3. Check sync script maps the secret
4. Check auto_esc_config has the mapping
5. Check no hardcoded values override

## DO NOT

- Create .env files
- Hardcode secrets
- Use os.getenv() directly
- Create duplicate sync scripts
- Use different naming conventions

## Maintenance

Weekly: Verify all secrets are synced
Monthly: Audit for unused secrets
Quarterly: Rotate sensitive credentials
"""

        path.write_text(content)
        print(f"  ✅ Strategy document written to {path}")

    def generate_test_script(self):
        """Generate a test script for secret access"""
        print("\n🧪 Generating test script...")

        test_script = '''#!/usr/bin/env python3
"""Test secret access through the unified pipeline"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import get_config_value

# Test critical secrets
test_secrets = [
    "openai_api_key",
    "anthropic_api_key",
    "snowflake_password",
    "lambda_labs_api_key",
    "vercel_api_token",
    "github_token",
]

print("🧪 Testing Secret Access\\n")

passed = 0
failed = 0

for secret in test_secrets:
    value = get_config_value(secret)
    if value and value != secret and "PLACEHOLDER" not in str(value):
        print(f"✅ {secret}: {'*' * 10}")
        passed += 1
    else:
        print(f"❌ {secret}: NOT FOUND")
        failed += 1

print(f"\\n📊 Results: {passed} passed, {failed} failed")

if failed > 0:
    print("\\n⚠️  Some secrets are missing. Run the sync workflow:")
    print("   gh workflow run sync_secrets.yml")
    sys.exit(1)
else:
    print("\\n✅ All secrets accessible!")
'''

        test_path = self.project_root / "scripts" / "test_secret_access.py"
        test_path.write_text(test_script)
        test_path.chmod(0o755)
        print(f"  ✅ Test script created: {test_path}")

    def generate_report(self):
        """Generate comprehensive audit report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "findings": self.findings,
            "statistics": {
                "sync_scripts": len(self.findings["sync_scripts"]),
                "workflows": len(self.findings["workflows"]),
                "config_files": len(self.findings["config_files"]),
                "issues": len(self.findings["issues"]),
            },
            "recommendations": [
                "Use ONLY the sync_secrets.yml workflow for syncing",
                "Update sync_from_gh_to_pulumi.py with current secrets",
                "Remove all legacy sync scripts",
                "Standardize on VERCEL_ACCESS_TOKEN",
                "Test with test_secret_access.py regularly",
            ],
        }

        # Save report
        report_path = (
            self.project_root
            / f"secret_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {report_path}")

        # Print summary
        print("\n📊 Audit Summary:")
        print(f"  Sync scripts found: {report['statistics']['sync_scripts']}")
        print(f"  Workflows found: {report['statistics']['workflows']}")
        print(f"  Config files found: {report['statistics']['config_files']}")
        print(f"  Issues found: {report['statistics']['issues']}")

        if self.findings["issues"]:
            print("\n⚠️  Issues:")
            for issue in self.findings["issues"]:
                print(f"  - {issue}")


def main():
    print("🚀 Unified Secret Management Audit\n")

    auditor = UnifiedSecretManagementAuditor()

    # Run audit
    auditor.find_all_secret_files()
    esc_status = auditor.check_pulumi_esc_status()
    auditor.analyze_sync_workflow()

    # Create unified strategy
    strategy = auditor.create_unified_strategy()

    # Generate test script
    auditor.generate_test_script()

    # Generate report
    auditor.generate_report()

    print("\n✅ Audit complete! Next steps:")
    print("  1. Review UNIFIED_SECRET_MANAGEMENT_STRATEGY.md")
    print("  2. Update sync_from_gh_to_pulumi.py with missing secrets")
    print("  3. Run: gh workflow run sync_secrets.yml")
    print("  4. Test: python scripts/test_secret_access.py")


if __name__ == "__main__":
    main()
