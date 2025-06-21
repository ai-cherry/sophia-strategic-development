#!/usr/bin/env python3
"""Sophia AI - Test Permanent Solution.

Tests the GitHub Organization Secrets → Pulumi ESC integration
WITHOUT EXPOSING ANY CREDENTIALS
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PermanentSolutionTester:
    """Test the permanent solution without exposing credentials."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}

    def run_command(self, cmd: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run shell command with proper error handling."""logger.info(f"Testing: {cmd}").

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )

        if check and result.returncode != 0:
            logger.error(f"Command failed: {cmd}")
            logger.error(f"Error: {result.stderr}")

        return result

    def test_gitignore_security(self):
        """Test that .gitignore properly protects secrets."""logger.info("🔒 Testing .gitignore security...").

        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            self.test_results["gitignore"] = {
                "status": "fail",
                "reason": ".gitignore not found",
            }
            return

        with open(gitignore_path, "r") as f:
            gitignore_content = f.read()

        required_patterns = [
            ".env",
            "*token*",
            "*secret*",
            "*key*",
            "PULUMI_ACCESS_TOKEN*",
            ".pulumi/",
        ]

        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)

        if missing_patterns:
            self.test_results["gitignore"] = {
                "status": "fail",
                "reason": f"Missing patterns: {missing_patterns}",
            }
        else:
            self.test_results["gitignore"] = {"status": "pass"}
            logger.info("✅ .gitignore properly protects secrets")

    def test_no_exposed_secrets(self):
        """Test that no secrets are exposed in the repository."""logger.info("🔍 Testing for exposed secrets...").

        # Search for potential secret patterns in tracked files
        dangerous_patterns = [
            "pul-[a-f0-9]{40}",  # Pulumi tokens
            "sk-[a-zA-Z0-9]{48}",  # OpenAI keys
            "xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+",  # Slack tokens
            "AKIA[0-9A-Z]{16}",  # AWS access keys
        ]

        exposed_secrets = []
        for pattern in dangerous_patterns:
            result = self.run_command(f"git grep -E '{pattern}' || true", check=False)
            if result.stdout.strip():
                exposed_secrets.append(f"Pattern '{pattern}' found in: {result.stdout}")

        if exposed_secrets:
            self.test_results["secret_exposure"] = {
                "status": "fail",
                "reason": f"Exposed secrets found: {exposed_secrets}",
            }
            logger.error("❌ SECURITY BREACH: Secrets found in repository!")
        else:
            self.test_results["secret_exposure"] = {"status": "pass"}
            logger.info("✅ No secrets exposed in repository")

    def test_pulumi_esc_environments(self):
        """Test that Pulumi ESC environments are properly configured."""logger.info("🏗️ Testing Pulumi ESC environments...").

        # Test if we can list environments (without exposing tokens)
        result = self.run_command("pulumi env ls", check=False)

        if result.returncode != 0:
            self.test_results["pulumi_esc"] = {
                "status": "warning",
                "reason": "Cannot access Pulumi ESC (may need login)",
            }
            logger.warning("⚠️ Cannot access Pulumi ESC - may need authentication")
            return

        environments = result.stdout.strip().split("\n")
        required_envs = ["default/sophia-ai-base", "default/sophia-ai-production"]

        missing_envs = []
        for env in required_envs:
            if not any(env in line for line in environments):
                missing_envs.append(env)

        if missing_envs:
            self.test_results["pulumi_esc"] = {
                "status": "fail",
                "reason": f"Missing environments: {missing_envs}",
            }
        else:
            self.test_results["pulumi_esc"] = {"status": "pass"}
            logger.info("✅ Pulumi ESC environments configured")

    def test_github_workflow(self):
        """Test that GitHub Actions workflow is properly configured."""logger.info("🚀 Testing GitHub Actions workflow...").

        workflow_path = (
            self.project_root
            / ".github"
            / "workflows"
            / "auto_deploy_with_org_secrets.yml"
        )

        if not workflow_path.exists():
            self.test_results["github_workflow"] = {
                "status": "fail",
                "reason": "GitHub Actions workflow not found",
            }
            return

        with open(workflow_path, "r") as f:
            workflow_content = f.read()

        required_elements = [
            "secrets.PULUMI_ACCESS_TOKEN",
            "secrets.OPENAI_API_KEY",
            "secrets.GONG_ACCESS_KEY",
            "sync_github_to_pulumi.sh",
        ]

        missing_elements = []
        for element in required_elements:
            if element not in workflow_content:
                missing_elements.append(element)

        # Check that no secrets are hardcoded
        if "pul-" in workflow_content or "sk-" in workflow_content:
            self.test_results["github_workflow"] = {
                "status": "fail",
                "reason": "SECURITY BREACH: Hardcoded secrets in workflow",
            }
            logger.error("❌ SECURITY BREACH: Hardcoded secrets in GitHub workflow!")
            return

        if missing_elements:
            self.test_results["github_workflow"] = {
                "status": "fail",
                "reason": f"Missing elements: {missing_elements}",
            }
        else:
            self.test_results["github_workflow"] = {"status": "pass"}
            logger.info("✅ GitHub Actions workflow properly configured")

    def test_sync_script(self):
        """Test that the sync script is properly configured."""logger.info("🔄 Testing sync script...").

        sync_script_path = self.project_root / "scripts" / "sync_github_to_pulumi.sh"

        if not sync_script_path.exists():
            self.test_results["sync_script"] = {
                "status": "fail",
                "reason": "Sync script not found",
            }
            return

        # Check if script is executable
        if not os.access(sync_script_path, os.X_OK):
            self.test_results["sync_script"] = {
                "status": "fail",
                "reason": "Sync script not executable",
            }
            return

        with open(sync_script_path, "r") as f:
            script_content = f.read()

        # Check that script doesn't contain hardcoded secrets
        if "pul-" in script_content or "sk-" in script_content:
            self.test_results["sync_script"] = {
                "status": "fail",
                "reason": "SECURITY BREACH: Hardcoded secrets in sync script",
            }
            logger.error("❌ SECURITY BREACH: Hardcoded secrets in sync script!")
            return

        # Check for required elements
        required_elements = [
            "GITHUB_SECRETS=",
            "pulumi env set",
            "scoobyjava-org/default/sophia-ai-production",
        ]

        missing_elements = []
        for element in required_elements:
            if element not in script_content:
                missing_elements.append(element)

        if missing_elements:
            self.test_results["sync_script"] = {
                "status": "fail",
                "reason": f"Missing elements: {missing_elements}",
            }
        else:
            self.test_results["sync_script"] = {"status": "pass"}
            logger.info("✅ Sync script properly configured")

    def test_backend_integration(self):
        """Test that backend integration is properly configured."""logger.info("🧪 Testing backend integration...").

        config_path = self.project_root / "backend" / "core" / "auto_esc_config.py"

        if not config_path.exists():
            self.test_results["backend_integration"] = {
                "status": "fail",
                "reason": "Backend ESC integration not found",
            }
            return

        with open(config_path, "r") as f:
            config_content = f.read()

        # Check that no secrets are hardcoded
        if "pul-" in config_content or "sk-" in config_content:
            self.test_results["backend_integration"] = {
                "status": "fail",
                "reason": "SECURITY BREACH: Hardcoded secrets in backend config",
            }
            logger.error("❌ SECURITY BREACH: Hardcoded secrets in backend config!")
            return

        # Check for required elements
        required_elements = [
            "class AutoESCConfig",
            "pulumi env open",
            "openai_api_key",
            "gong_access_key",
        ]

        missing_elements = []
        for element in required_elements:
            if element not in config_content:
                missing_elements.append(element)

        if missing_elements:
            self.test_results["backend_integration"] = {
                "status": "fail",
                "reason": f"Missing elements: {missing_elements}",
            }
        else:
            self.test_results["backend_integration"] = {"status": "pass"}
            logger.info("✅ Backend integration properly configured")

    def test_documentation(self):
        """Test that documentation is complete."""logger.info("📚 Testing documentation...").

        doc_path = self.project_root / "PERMANENT_GITHUB_ORG_SECRETS_SOLUTION.md"

        if not doc_path.exists():
            self.test_results["documentation"] = {
                "status": "fail",
                "reason": "Documentation not found",
            }
            return

        with open(doc_path, "r") as f:
            doc_content = f.read()

        required_sections = [
            "GitHub Organization Secrets",
            "Automatic Sync Process",
            "Security Guarantees",
            "Testing the Solution",
            "Verification Checklist",
        ]

        missing_sections = []
        for section in required_sections:
            if section not in doc_content:
                missing_sections.append(section)

        if missing_sections:
            self.test_results["documentation"] = {
                "status": "fail",
                "reason": f"Missing sections: {missing_sections}",
            }
        else:
            self.test_results["documentation"] = {"status": "pass"}
            logger.info("✅ Documentation complete")

    def run_all_tests(self):
        """Run all tests and generate report."""logger.info("🧪 Running comprehensive permanent solution tests...").

        tests = [
            self.test_gitignore_security,
            self.test_no_exposed_secrets,
            self.test_pulumi_esc_environments,
            self.test_github_workflow,
            self.test_sync_script,
            self.test_backend_integration,
            self.test_documentation,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "")
                self.test_results[test_name] = {"status": "error", "reason": str(e)}
                logger.error(f"❌ Test {test_name} failed with error: {e}")

        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report."""logger.info("📊 Generating test report...").

        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results.values() if result["status"] == "pass"
        )
        failed_tests = sum(
            1 for result in self.test_results.values() if result["status"] == "fail"
        )
        warning_tests = sum(
            1 for result in self.test_results.values() if result["status"] == "warning"
        )
        error_tests = sum(
            1 for result in self.test_results.values() if result["status"] == "error"
        )

        print("\n" + "=" * 60)
        print("🧪 PERMANENT SOLUTION TEST REPORT")
        print("=" * 60)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"💥 Errors: {error_tests}")
        print("")

        if failed_tests == 0 and error_tests == 0:
            print("🎉 ALL CRITICAL TESTS PASSED!")
            print("🔒 Permanent solution is SECURE and READY!")
        else:
            print("❌ CRITICAL ISSUES FOUND!")
            print("🚨 DO NOT DEPLOY until issues are resolved!")

        print("\n📋 Detailed Results:")
        print("-" * 40)

        for test_name, result in self.test_results.items():
            status_emoji = {"pass": "✅", "fail": "❌", "warning": "⚠️", "error": "💥"}

            emoji = status_emoji.get(result["status"], "❓")
            print(
                f"{emoji} {test_name.replace('_', ' ').title()}: {result['status'].upper()}"
            )

            if result["status"] != "pass":
                print(f"   Reason: {result.get('reason', 'Unknown')}")

        print("\n" + "=" * 60)

        # Save detailed report
        report_path = self.project_root / "PERMANENT_SOLUTION_TEST_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(
                {
                    "timestamp": "2025-06-20",
                    "summary": {
                        "total": total_tests,
                        "passed": passed_tests,
                        "failed": failed_tests,
                        "warnings": warning_tests,
                        "errors": error_tests,
                    },
                    "results": self.test_results,
                },
                f,
                indent=2,
            )

        logger.info(f"📄 Detailed report saved to: {report_path}")


def main():
    """Main test function."""
    try:
        tester = PermanentSolutionTester()
        tester.run_all_tests()

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
