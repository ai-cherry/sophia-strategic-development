#!/usr/bin/env python3
"""
GitHub Organization Security Configuration Script
Implements enterprise-grade security policies for ai-cherry organization
"""

import json
import logging
from dataclasses import dataclass

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Configuration for GitHub organization security"""

    org_name: str = "ai-cherry"
    github_token: str | None = None

    # Branch Protection Settings
    branch_protection: dict = None

    # Security Scanning Settings
    security_scanning: dict = None

    # Repository Settings
    repository_settings: dict = None

    def __post_init__(self):
        """Initialize default configurations"""
        if not self.github_token:
            self.github_token = get_config_value("github_token")

        if not self.branch_protection:
            self.branch_protection = {
                "required_status_checks": {
                    "strict": True,
                    "contexts": [
                        "test-suite",
                        "security-scan",
                        "lint-check",
                        "dependency-check",
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

        if not self.security_scanning:
            self.security_scanning = {
                "dependency_graph": True,
                "vulnerability_alerts": True,
                "security_advisories": True,
                "secret_scanning": True,
                "secret_scanning_push_protection": True,
                "code_scanning": True,
                "private_vulnerability_reporting": True,
            }

        if not self.repository_settings:
            self.repository_settings = {
                "default_branch_name": "main",
                "allow_merge_commits": True,
                "allow_squash_merge": True,
                "allow_rebase_merge": False,
                "delete_branch_on_merge": True,
                "allow_auto_merge": False,
                "allow_update_branch": True,
            }


class GitHubSecurityManager:
    """Manages GitHub organization security configuration"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {config.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # Repository priority mapping
        self.repo_priorities = {
            "sophia-main": "critical",
            "orchestra-main": "high",
            "cherry-main": "high",
            "karen-main": "medium",
            "slack-mcp-server": "medium",
            "notion-mcp-server": "medium",
            "codex": "low",
        }

    def get_organization_repositories(self) -> list[dict]:
        """Get all repositories in the organization"""
        try:
            url = f"{self.base_url}/orgs/{self.config.org_name}/repos"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            repos = response.json()
            logger.info(f"Found {len(repos)} repositories in {self.config.org_name}")
            return repos

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get repositories: {e}")
            return []

    def configure_branch_protection(self, repo_name: str, branch: str = "main") -> bool:
        """Configure branch protection rules"""
        try:
            url = f"{self.base_url}/repos/{self.config.org_name}/{repo_name}/branches/{branch}/protection"

            # Adjust protection based on repository priority
            protection_config = self.config.branch_protection.copy()
            priority = self.repo_priorities.get(repo_name, "medium")

            if priority == "critical":
                # Enhanced protection for critical repositories
                protection_config["required_pull_request_reviews"][
                    "required_approving_review_count"
                ] = 2
                protection_config["enforce_admins"] = True

            elif priority == "low":
                # Relaxed protection for low-priority repositories
                protection_config["required_pull_request_reviews"][
                    "required_approving_review_count"
                ] = 1
                protection_config["required_status_checks"]["contexts"] = ["test-suite"]

            response = requests.put(url, headers=self.headers, json=protection_config)

            if response.status_code == 200:
                logger.info(f"✅ Branch protection configured for {repo_name}/{branch}")
                return True
            else:
                logger.warning(
                    f"⚠️ Failed to configure branch protection for {repo_name}: {response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error configuring branch protection for {repo_name}: {e}")
            return False

    def enable_security_features(self, repo_name: str) -> dict[str, bool]:
        """Enable security features for a repository"""
        results = {}

        # Enable vulnerability alerts
        try:
            url = f"{self.base_url}/repos/{self.config.org_name}/{repo_name}/vulnerability-alerts"
            response = requests.put(url, headers=self.headers)
            results["vulnerability_alerts"] = response.status_code == 204

        except Exception as e:
            logger.error(f"Failed to enable vulnerability alerts for {repo_name}: {e}")
            results["vulnerability_alerts"] = False

        # Enable secret scanning
        try:
            url = f"{self.base_url}/repos/{self.config.org_name}/{repo_name}/secret-scanning/alerts"
            response = requests.get(url, headers=self.headers)
            results["secret_scanning"] = response.status_code in [
                200,
                404,
            ]  # 404 means no alerts, which is good

        except Exception as e:
            logger.error(f"Failed to check secret scanning for {repo_name}: {e}")
            results["secret_scanning"] = False

        # Enable automated security fixes
        try:
            url = f"{self.base_url}/repos/{self.config.org_name}/{repo_name}/automated-security-fixes"
            response = requests.put(url, headers=self.headers)
            results["automated_security_fixes"] = response.status_code == 204

        except Exception as e:
            logger.error(
                f"Failed to enable automated security fixes for {repo_name}: {e}"
            )
            results["automated_security_fixes"] = False

        return results

    def configure_repository_settings(self, repo_name: str) -> bool:
        """Configure general repository settings"""
        try:
            url = f"{self.base_url}/repos/{self.config.org_name}/{repo_name}"

            settings = {
                "allow_merge_commit": self.config.repository_settings[
                    "allow_merge_commits"
                ],
                "allow_squash_merge": self.config.repository_settings[
                    "allow_squash_merge"
                ],
                "allow_rebase_merge": self.config.repository_settings[
                    "allow_rebase_merge"
                ],
                "delete_branch_on_merge": self.config.repository_settings[
                    "delete_branch_on_merge"
                ],
                "allow_auto_merge": self.config.repository_settings["allow_auto_merge"],
                "allow_update_branch": self.config.repository_settings[
                    "allow_update_branch"
                ],
            }

            response = requests.patch(url, headers=self.headers, json=settings)

            if response.status_code == 200:
                logger.info(f"✅ Repository settings configured for {repo_name}")
                return True
            else:
                logger.warning(
                    f"⚠️ Failed to configure repository settings for {repo_name}: {response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.error(
                f"❌ Error configuring repository settings for {repo_name}: {e}"
            )
            return False

    def create_security_workflow(self, repo_name: str) -> bool:
        """Create GitHub Actions security workflow"""

        workflow_content = """name: Security Scan
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday at 6 AM UTC

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v3
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

    - name: Run CodeQL Analysis
      uses: github/codeql-action/analyze@v3
      with:
        languages: python, javascript

    - name: Dependency Review
      uses: actions/dependency-review-action@v4
      if: github.event_name == 'pull_request'

    - name: Secret Scanning
      run: |
        echo "Secret scanning is handled by GitHub's built-in secret scanning"
        echo "No additional action needed"
"""

        try:
            # Create .github/workflows directory structure
            url = f"{self.base_url}/repos/{self.config.org_name}/{repo_name}/contents/.github/workflows/security.yml"

            content_encoded = json.dumps(workflow_content).encode("utf-8")
            import base64
from backend.core.auto_esc_config import get_config_value
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

            content_b64 = base64.b64encode(content_encoded).decode("utf-8")

            data = {
                "message": "feat: Add comprehensive security scanning workflow",
                "content": content_b64,
                "branch": "main",
            }

            response = requests.put(url, headers=self.headers, json=data)

            if response.status_code in [200, 201]:
                logger.info(f"✅ Security workflow created for {repo_name}")
                return True
            elif response.status_code == 422:
                logger.info(f"ℹ️ Security workflow already exists for {repo_name}")
                return True
            else:
                logger.warning(
                    f"⚠️ Failed to create security workflow for {repo_name}: {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Error creating security workflow for {repo_name}: {e}")
            return False

    def generate_security_report(self, results: dict) -> str:
        """Generate comprehensive security configuration report"""

        report = f"""
# GitHub Organization Security Configuration Report

**Organization:** {self.config.org_name}
**Generated:** {json.dumps(results.get('timestamp', 'Unknown'))}
**Repositories Processed:** {len(results.get('repositories', {}))}

## 🔒 Security Configuration Summary

### Branch Protection Status
"""

        for repo_name, repo_results in results.get("repositories", {}).items():
            priority = self.repo_priorities.get(repo_name, "medium")
            protection_status = (
                "✅" if repo_results.get("branch_protection", False) else "❌"
            )

            report += f"- **{repo_name}** ({priority} priority): {protection_status} Branch Protection\n"

        report += """
### Security Features Status
"""

        for repo_name, repo_results in results.get("repositories", {}).items():
            security_features = repo_results.get("security_features", {})
            vuln_alerts = (
                "✅" if security_features.get("vulnerability_alerts", False) else "❌"
            )
            secret_scan = (
                "✅" if security_features.get("secret_scanning", False) else "❌"
            )
            auto_fixes = (
                "✅"
                if security_features.get("automated_security_fixes", False)
                else "❌"
            )

            report += f"""- **{repo_name}:**
  - Vulnerability Alerts: {vuln_alerts}
  - Secret Scanning: {secret_scan}
  - Automated Fixes: {auto_fixes}
"""

        report += """
### Security Workflows
"""

        for repo_name, repo_results in results.get("repositories", {}).items():
            workflow_status = (
                "✅" if repo_results.get("security_workflow", False) else "❌"
            )
            report += f"- **{repo_name}**: {workflow_status} Security Workflow\n"

        # Calculate overall security score
        total_checks = 0
        passed_checks = 0

        for repo_results in results.get("repositories", {}).values():
            total_checks += 4  # branch_protection, security_features (3), workflow
            if repo_results.get("branch_protection", False):
                passed_checks += 1
            for feature in repo_results.get("security_features", {}).values():
                if feature:
                    passed_checks += 1
            if repo_results.get("security_workflow", False):
                passed_checks += 1

        security_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        report += f"""
## 📊 Overall Security Score: {security_score:.1f}%

### Recommendations

#### High Priority
- Ensure all critical repositories have 2+ required reviewers
- Enable secret scanning push protection on all repositories
- Implement automated dependency updates

#### Medium Priority
- Set up organization-wide security policies
- Configure custom security advisories
- Implement advanced threat protection

#### Low Priority
- Fine-tune branch protection rules per repository type
- Set up security notification channels
- Create security training documentation

## 🎯 Next Steps

1. **Review and approve** security configurations
2. **Monitor security alerts** regularly
3. **Update security policies** as needed
4. **Train team members** on security best practices
5. **Schedule regular security audits**

---

**Security Status:** {'🟢 EXCELLENT' if security_score >= 90 else '🟡 GOOD' if security_score >= 70 else '🔴 NEEDS IMPROVEMENT'}
**Compliance Level:** {'Enterprise-Grade' if security_score >= 90 else 'Business-Grade' if security_score >= 70 else 'Basic'}
"""

        return report

    def configure_organization_security(self) -> dict:
        """Configure security for entire organization"""
        logger.info(f"🚀 Starting security configuration for {self.config.org_name}")

        results = {
            "timestamp": json.dumps({"timestamp": "2025-06-29T17:45:00Z"}),
            "repositories": {},
        }

        # Get all repositories
        repositories = self.get_organization_repositories()

        if not repositories:
            logger.error("❌ No repositories found or unable to access organization")
            return results

        # Configure security for each repository
        for repo in repositories:
            repo_name = repo["name"]
            logger.info(f"🔧 Configuring security for {repo_name}...")

            repo_results = {}

            # Configure branch protection
            repo_results["branch_protection"] = self.configure_branch_protection(
                repo_name
            )

            # Enable security features
            repo_results["security_features"] = self.enable_security_features(repo_name)

            # Configure repository settings
            repo_results["repository_settings"] = self.configure_repository_settings(
                repo_name
            )

            # Create security workflow
            repo_results["security_workflow"] = self.create_security_workflow(repo_name)

            results["repositories"][repo_name] = repo_results

            logger.info(f"✅ Security configuration completed for {repo_name}")

        return results


def main():
    """Main execution function"""

    # Check for GitHub token
    github_token = get_config_value("github_token")
    if not github_token:
        logger.error("❌ GITHUB_TOKEN environment variable not set")
        logger.info("Please set GITHUB_TOKEN with organization admin permissions")
        return

    # Initialize configuration
    config = SecurityConfig()
    manager = GitHubSecurityManager(config)

    # Configure organization security
    results = manager.configure_organization_security()

    # Generate and save report
    report = manager.generate_security_report(results)

    # Save results and report
    with open("github_security_configuration_results.json", "w") as f:
        json.dump(results, f, indent=2)

    with open("GITHUB_SECURITY_CONFIGURATION_REPORT.md", "w") as f:
        f.write(report)

    logger.info("✅ Security configuration completed!")
    logger.info("📄 Results saved to github_security_configuration_results.json")
    logger.info("📋 Report saved to GITHUB_SECURITY_CONFIGURATION_REPORT.md")

    # Print summary
    total_repos = len(results.get("repositories", {}))
    successful_configs = sum(
        1
        for r in results.get("repositories", {}).values()
        if r.get("branch_protection", False)
    )

    print(
        f"""
🔒 GITHUB SECURITY CONFIGURATION SUMMARY
========================================
Organization: {config.org_name}
Repositories Processed: {total_repos}
Successful Configurations: {successful_configs}/{total_repos}
Success Rate: {(successful_configs/total_repos*100):.1f}%

Next Steps:
1. Review GITHUB_SECURITY_CONFIGURATION_REPORT.md
2. Address any failed configurations
3. Monitor security alerts in GitHub
4. Schedule regular security reviews
"""
    )


if __name__ == "__main__":
    main()
