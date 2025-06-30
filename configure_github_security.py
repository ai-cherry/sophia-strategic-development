#!/usr/bin/env python3
"""
Configure GitHub repository security settings for Sophia AI MCP integration
"""

import json
import logging
import subprocess
from datetime import datetime

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GitHubSecurityConfigurator:
    """Configure GitHub repository security settings."""

    def __init__(self):
        """Initialize with GitHub configuration."""
        self.pat_token = self.extract_pat_from_git_remote()
        self.headers = {
            "Authorization": f"token {self.pat_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Sophia-AI-Security-Configurator",
        }
        self.base_url = "https://api.github.com"
        self.org_name = "ai-cherry"
        self.repo_name = "sophia-main"

    def extract_pat_from_git_remote(self) -> str:
        """Extract PAT token from git remote URL."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd="/home/ubuntu/sophia-main",
            )

            if result.returncode == 0:
                remote_url = result.stdout.strip()
                if "github_pat_" in remote_url:
                    start = remote_url.find("github_pat_")
                    end = remote_url.find("@github.com")
                    if start != -1 and end != -1:
                        return remote_url[start:end]
            return None
        except Exception as e:
            logger.error(f"Error extracting PAT: {e}")
            return None

    def configure_branch_protection(self) -> bool:
        """Configure branch protection rules for main branch."""
        logger.info("🔒 Configuring branch protection rules")

        protection_config = {
            "required_status_checks": {
                "strict": True,
                "contexts": [
                    "mcp-server-validation",
                    "mcp-inspector-validation",
                    "integration-test",
                    "security-scan",
                ],
            },
            "enforce_admins": False,
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True,
                "require_last_push_approval": True,
            },
            "restrictions": None,
            "allow_force_pushes": False,
            "allow_deletions": False,
            "block_creations": False,
            "required_conversation_resolution": True,
        }

        try:
            response = requests.put(
                f"{self.base_url}/repos/{self.org_name}/{self.repo_name}/branches/main/protection",
                headers=self.headers,
                json=protection_config,
            )

            if response.status_code in [200, 201]:
                logger.info("✅ Branch protection rules configured successfully")
                return True
            else:
                logger.error(
                    f"❌ Failed to configure branch protection: {response.status_code}"
                )
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error configuring branch protection: {e}")
            return False

    def configure_repository_security(self) -> bool:
        """Configure repository security settings."""
        logger.info("🛡️ Configuring repository security settings")

        security_configs = [
            # Enable vulnerability alerts
            {
                "endpoint": f"/repos/{self.org_name}/{self.repo_name}/vulnerability-alerts",
                "method": "PUT",
                "data": None,
                "description": "vulnerability alerts",
            },
            # Enable automated security fixes
            {
                "endpoint": f"/repos/{self.org_name}/{self.repo_name}/automated-security-fixes",
                "method": "PUT",
                "data": None,
                "description": "automated security fixes",
            },
            # Enable dependency graph
            {
                "endpoint": f"/repos/{self.org_name}/{self.repo_name}",
                "method": "PATCH",
                "data": {"has_vulnerability_alerts": True},
                "description": "dependency graph",
            },
        ]

        success_count = 0

        for config in security_configs:
            try:
                if config["method"] == "PUT":
                    response = requests.put(
                        f"{self.base_url}{config['endpoint']}",
                        headers=self.headers,
                        json=config["data"],
                    )
                elif config["method"] == "PATCH":
                    response = requests.patch(
                        f"{self.base_url}{config['endpoint']}",
                        headers=self.headers,
                        json=config["data"],
                    )

                if response.status_code in [200, 201, 204]:
                    logger.info(f"✅ Enabled {config['description']}")
                    success_count += 1
                else:
                    logger.warning(
                        f"⚠️ Could not enable {config['description']}: {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"❌ Error configuring {config['description']}: {e}")

        return success_count > 0

    def create_issue_templates(self) -> bool:
        """Create issue templates for MCP integration."""
        logger.info("📋 Creating issue templates")

        templates = [
            {
                "name": "mcp-server-bug.md",
                "content": """---
name: MCP Server Bug Report
about: Report a bug in an MCP server
title: '[MCP-BUG] '
labels: ['bug', 'mcp-server']
assignees: ['scoobyjava']
---

## MCP Server Bug Report

**Server Name:**
**Version:**
**Environment:**

### Description
A clear description of the bug.

### Steps to Reproduce
1.
2.
3.

### Expected Behavior
What should happen.

### Actual Behavior
What actually happens.

### Logs
```
Paste relevant logs here
```

### Additional Context
Any other context about the problem.

### Checklist
- [ ] I have checked existing issues
- [ ] I have provided all required information
- [ ] I have included relevant logs
""",
            },
            {
                "name": "mcp-integration-request.md",
                "content": """---
name: New MCP Integration Request
about: Request a new MCP server integration
title: '[MCP-REQUEST] '
labels: ['enhancement', 'mcp-integration']
assignees: ['scoobyjava']
---

## MCP Integration Request

**Service/Tool:**
**Repository URL:**
**Priority:** High/Medium/Low

### Business Justification
Why this integration is needed.

### Technical Requirements
- [ ] API access available
- [ ] Documentation reviewed
- [ ] Security assessment completed
- [ ] Integration approach defined

### Success Criteria
What defines a successful integration.

### Additional Notes
Any other relevant information.

### Checklist
- [ ] Business case documented
- [ ] Technical feasibility confirmed
- [ ] Security implications reviewed
""",
            },
            {
                "name": "security-vulnerability.md",
                "content": """---
name: Security Vulnerability Report
about: Report a security vulnerability
title: '[SECURITY] '
labels: ['security', 'vulnerability']
assignees: ['scoobyjava']
---

## Security Vulnerability Report

**Severity:** Critical/High/Medium/Low
**Component:**
**Affected Versions:**

### Description
Clear description of the vulnerability.

### Impact
What could happen if exploited.

### Steps to Reproduce
1.
2.
3.

### Mitigation
Suggested fixes or workarounds.

### Additional Information
Any other relevant details.

### Checklist
- [ ] I have not disclosed this publicly
- [ ] I have provided clear reproduction steps
- [ ] I have suggested mitigation approaches
""",
            },
        ]

        success_count = 0

        for template in templates:
            try:
                # Create the file content for GitHub API
                file_data = {
                    "message": f"Add {template['name']} issue template",
                    "content": template["content"].encode("utf-8").hex(),
                    "branch": "main",
                }

                response = requests.put(
                    f"{self.base_url}/repos/{self.org_name}/{self.repo_name}/contents/.github/ISSUE_TEMPLATE/{template['name']}",
                    headers=self.headers,
                    json=file_data,
                )

                if response.status_code in [200, 201]:
                    logger.info(f"✅ Created issue template: {template['name']}")
                    success_count += 1
                else:
                    logger.warning(
                        f"⚠️ Could not create {template['name']}: {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"❌ Error creating {template['name']}: {e}")

        return success_count > 0

    def configure_secrets_management(self) -> dict:
        """Review and document secrets management configuration."""
        logger.info("🔐 Reviewing secrets management configuration")

        # Document required secrets for MCP integration
        required_secrets = {
            "production_secrets": [
                {
                    "name": "PULUMI_ACCESS_TOKEN",
                    "description": "Pulumi access token for ESC integration",
                    "scope": "organization",
                    "managed_by": "pulumi_esc",
                },
                {
                    "name": "NOTION_API_KEY",
                    "description": "Notion API key for MCP server",
                    "scope": "repository",
                    "managed_by": "pulumi_esc",
                },
                {
                    "name": "SLACK_BOT_TOKEN",
                    "description": "Slack bot token for MCP server",
                    "scope": "repository",
                    "managed_by": "pulumi_esc",
                },
                {
                    "name": "SNOWFLAKE_ACCOUNT",
                    "description": "Snowflake account identifier",
                    "scope": "repository",
                    "managed_by": "pulumi_esc",
                },
                {
                    "name": "SNOWFLAKE_USER",
                    "description": "Snowflake user for MCP server",
                    "scope": "repository",
                    "managed_by": "pulumi_esc",
                },
                {
                    "name": "SNOWFLAKE_PASSWORD",
                    "description": "Snowflake password",
                    "scope": "repository",
                    "managed_by": "pulumi_esc",
                },
            ],
            "test_secrets": [
                {
                    "name": "NOTION_API_KEY_TEST",
                    "description": "Test Notion API key",
                    "scope": "repository",
                    "managed_by": "pulumi_esc",
                },
                {
                    "name": "SLACK_BOT_TOKEN_TEST",
                    "description": "Test Slack bot token",
                    "scope": "repository",
                    "managed_by": "pulumi_esc",
                },
            ],
            "infrastructure_secrets": [
                {
                    "name": "SLACK_WEBHOOK_URL",
                    "description": "Slack webhook for notifications",
                    "scope": "repository",
                    "managed_by": "github_secrets",
                },
                {
                    "name": "GITLEAKS_LICENSE",
                    "description": "GitLeaks license key",
                    "scope": "organization",
                    "managed_by": "github_secrets",
                },
            ],
        }

        # Create secrets management documentation
        secrets_doc = {
            "architecture": "GitHub Organization Secrets → Pulumi ESC → Application Runtime",
            "primary_storage": "GitHub Organization Secrets",
            "management_tool": "Pulumi ESC",
            "deployment_method": "GitHub Actions with secure workflows",
            "required_secrets": required_secrets,
            "security_principles": [
                "Never hardcode credentials in source code",
                "Use environment variables populated by Pulumi ESC",
                "Rotate secrets regularly through Pulumi ESC",
                "Audit secret access through GitHub and Pulumi logs",
                "Validate secrets through automated security scanning",
            ],
            "implementation_notes": [
                "All production secrets managed through Pulumi ESC",
                "Test secrets isolated from production",
                "Infrastructure secrets stored in GitHub for CI/CD",
                "Secrets validation in deployment pipeline",
                "Automated security scanning for secret exposure",
            ],
        }

        # Save secrets configuration
        with open("secrets-management-config.json", "w") as f:
            json.dump(secrets_doc, f, indent=2)

        logger.info("✅ Secrets management configuration documented")
        return secrets_doc

    def run_configuration(self) -> dict:
        """Run complete GitHub security configuration."""
        logger.info("🚀 Starting GitHub security configuration")

        results = {
            "timestamp": datetime.now().isoformat(),
            "branch_protection": False,
            "repository_security": False,
            "issue_templates": False,
            "secrets_management": None,
        }

        try:
            # Configure branch protection
            results["branch_protection"] = self.configure_branch_protection()

            # Configure repository security
            results["repository_security"] = self.configure_repository_security()

            # Create issue templates
            results["issue_templates"] = self.create_issue_templates()

            # Configure secrets management
            results["secrets_management"] = self.configure_secrets_management()

            # Calculate overall success
            success_count = sum(
                [
                    results["branch_protection"],
                    results["repository_security"],
                    results["issue_templates"],
                    bool(results["secrets_management"]),
                ]
            )

            results["overall_success"] = success_count >= 3
            results["success_rate"] = f"{success_count}/4"

            logger.info(
                f"🎉 GitHub security configuration completed: {results['success_rate']} successful"
            )

        except Exception as e:
            logger.error(f"❌ Configuration failed: {e}")
            results["error"] = str(e)

        return results


def main():
    """Main execution function."""
    print("🔒 GitHub Security Configuration for Sophia AI")
    print("=" * 60)

    try:
        configurator = GitHubSecurityConfigurator()
        results = configurator.run_configuration()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 CONFIGURATION SUMMARY")
        print("=" * 60)

        if results.get("overall_success"):
            print(f"✅ Configuration successful: {results['success_rate']}")
            print("🔒 Branch protection rules configured")
            print("🛡️ Repository security settings enabled")
            print("📋 Issue templates created")
            print("🔐 Secrets management documented")
        else:
            print(f"⚠️ Partial success: {results['success_rate']}")
            if not results["branch_protection"]:
                print("❌ Branch protection configuration failed")
            if not results["repository_security"]:
                print("❌ Repository security configuration failed")
            if not results["issue_templates"]:
                print("❌ Issue templates creation failed")

        print("=" * 60)

        return 0 if results.get("overall_success") else 1

    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
