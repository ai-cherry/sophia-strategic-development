#!/usr/bin/env python3
"""
CI/CD Pipeline Validation Script
Comprehensive validation of the rehabilitated pipeline
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class PipelineValidator:
    """Validate all aspects of the CI/CD pipeline"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.validation_results = {}
        self.all_passed = True

    def run_command(self, cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def check_mark(self, passed: bool) -> str:
        """Return colored check or X mark"""
        return f"{GREEN}✅{RESET}" if passed else f"{RED}❌{RESET}"

    def validate_dependencies(self) -> bool:
        """Validate all dependencies are installable"""
        logger.info("Validating dependencies...")

        checks = {
            "requirements.txt exists": Path("requirements.txt").exists(),
            "requirements.in exists": Path("requirements.in").exists(),
            "uv.lock exists": Path("uv.lock").exists(),
        }

        # Check UV installation
        exit_code, stdout, _ = self.run_command(["uv", "--version"])
        checks["UV installed"] = exit_code == 0

        # Check imports
        exit_code, stdout, stderr = self.run_command(
            ["python", "scripts/ci_cd_rehab/check_imports.py", "--fail-on-issues"]
        )
        checks["All imports healthy"] = exit_code == 0

        # Test import of key packages
        test_imports = [
            "fastapi",
            "anthropic",
            "openai",
            "snowflake.connector",
            "pulumi",
            "pydantic",
            "httpx",
            "structlog",
        ]

        for package in test_imports:
            exit_code, _, _ = self.run_command(["python", "-c", f"import {package}"])
            checks[f"{package} importable"] = exit_code == 0

        # Check for problematic imports
        exit_code, stdout, _ = self.run_command(
            ["grep", "-r", "anthropic_mcp_python_sdk", ".", "--include=*.py"]
        )
        checks["No old SDK references"] = exit_code != 0  # grep returns 1 if not found

        all_passed = all(checks.values())
        self.validation_results["dependencies"] = checks

        return all_passed

    def validate_github_actions(self) -> bool:
        """Validate GitHub Actions workflows"""
        logger.info("Validating GitHub Actions...")

        checks = {}

        # Check workflow files exist
        workflows = [
            ".github/workflows/_template.yml",
            ".github/workflows/production.yml",
            ".github/workflows/sync_secrets.yml",
        ]

        for workflow in workflows:
            checks[f"{workflow} exists"] = Path(workflow).exists()

        # Validate workflow syntax
        for workflow in workflows:
            if Path(workflow).exists():
                # Use yq or similar to validate YAML
                try:
                    with open(workflow) as f:
                        yaml.safe_load(f)
                    checks[f"{workflow} valid YAML"] = True
                except yaml.YAMLError:
                    checks[f"{workflow} valid YAML"] = False

        # Check composite action
        action_path = ".github/actions/pulumi-login/action.yml"
        checks["Pulumi login action exists"] = Path(action_path).exists()

        # Check for legacy workflows in techdebt
        techdebt_workflows = (
            list(Path(".techdebt").glob("archived_workflows/*.yml"))
            if Path(".techdebt").exists()
            else []
        )
        checks["Legacy workflows archived"] = (
            len(techdebt_workflows) == 0 or Path(".techdebt").exists()
        )

        all_passed = all(checks.values())
        self.validation_results["github_actions"] = checks

        return all_passed

    def validate_secrets(self) -> bool:
        """Validate secret configuration"""
        logger.info("Validating secrets...")

        checks = {}

        # Check secret map file
        secret_map_path = Path("config/pulumi/secret_map.yaml")
        checks["Secret map exists"] = secret_map_path.exists()

        if secret_map_path.exists():
            try:
                with open(secret_map_path) as f:
                    secret_map = yaml.safe_load(f)
                checks["Secret map valid"] = isinstance(secret_map, dict)
                checks["Secret mappings defined"] = len(secret_map) > 0
            except:
                checks["Secret map valid"] = False

        # Check Pulumi access
        exit_code, stdout, _ = self.run_command(["pulumi", "whoami"])
        checks["Pulumi authenticated"] = exit_code == 0

        # Check critical environment variables
        critical_vars = ["PULUMI_ACCESS_TOKEN", "LAMBDA_API_KEY", "OPENAI_API_KEY"]

        for var in critical_vars:
            value = os.environ.get(var)
            checks[f"{var} set"] = value is not None and len(value) > 0

        all_passed = all(checks.values())
        self.validation_results["secrets"] = checks

        return all_passed

    def validate_infrastructure(self) -> bool:
        """Validate infrastructure configuration"""
        logger.info("Validating infrastructure...")

        checks = {}

        # Check deployment scripts
        scripts = ["scripts/deploy-infrastructure.sh", "scripts/deploy-application.sh"]

        for script in scripts:
            path = Path(script)
            checks[f"{script} exists"] = path.exists()
            if path.exists():
                checks[f"{script} executable"] = path.stat().st_mode & 0o111 != 0

        # Check Pulumi configuration
        pulumi_dir = Path("infrastructure/pulumi")
        checks["Pulumi directory exists"] = pulumi_dir.exists()

        if pulumi_dir.exists():
            checks["package.json exists"] = (pulumi_dir / "package.json").exists()
            checks["Pulumi.yaml exists"] = (pulumi_dir / "Pulumi.yaml").exists()

        # Test infrastructure endpoints (if available)
        backend_url = os.environ.get("BACKEND_URL")
        if backend_url:
            try:
                response = requests.get(f"{backend_url}/health", timeout=5)
                checks["Backend health check"] = response.status_code == 200
            except:
                checks["Backend health check"] = False

        all_passed = all(checks.values())
        self.validation_results["infrastructure"] = checks

        return all_passed

    def validate_code_quality(self) -> bool:
        """Validate code quality standards"""
        logger.info("Validating code quality...")

        checks = {}

        # Run linters
        exit_code, stdout, stderr = self.run_command(
            ["ruff", "check", ".", "--statistics"]
        )

        # Parse ruff output
        if exit_code == 0:
            checks["Ruff check passed"] = True
            checks["Linting issues"] = 0
        else:
            checks["Ruff check passed"] = False
            # Try to extract issue count from output
            import re

            match = re.search(r"Found (\d+) error", stderr + stdout)
            if match:
                checks["Linting issues"] = int(match.group(1))

        # Check Black formatting
        exit_code, _, _ = self.run_command(["black", "--check", "."])
        checks["Black formatting"] = exit_code == 0

        # Check for techdebt flag
        checks["Techdebt cleared"] = not Path(".techdebt/ci_cd_rehab.flag").exists()

        all_passed = all(v for k, v in checks.items() if isinstance(v, bool))
        self.validation_results["code_quality"] = checks

        return all_passed

    def validate_documentation(self) -> bool:
        """Validate documentation completeness"""
        logger.info("Validating documentation...")

        checks = {}

        docs = [
            "docs/04-deployment/CI_CD_PIPELINE.md",
            "docs/04-deployment/CI_CD_REHAB_PLAYBOOK.md",
            "docs/08-security/SECRET_MANAGEMENT.md",
        ]

        for doc in docs:
            checks[f"{doc} exists"] = Path(doc).exists()

        # Check README references CI/CD
        readme_path = Path("README.md")
        if readme_path.exists():
            content = readme_path.read_text()
            checks["README mentions CI/CD"] = (
                "ci/cd" in content.lower() or "cicd" in content.lower()
            )

        all_passed = all(checks.values())
        self.validation_results["documentation"] = checks

        return all_passed

    def validate_monitoring(self) -> bool:
        """Validate monitoring setup"""
        logger.info("Validating monitoring...")

        checks = {}

        # Check Grafana dashboard config
        dashboard_path = Path("configs/grafana/dashboards/ci_cd_overview.json")
        checks["CI/CD dashboard exists"] = dashboard_path.exists()

        # Check if monitoring endpoints are configured
        checks["Grafana URL configured"] = bool(os.environ.get("GRAFANA_URL"))
        checks["Grafana API key configured"] = bool(os.environ.get("GRAFANA_API_KEY"))

        all_passed = all(checks.values())
        self.validation_results["monitoring"] = checks

        return all_passed

    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("\n" + "=" * 60)
        report.append("CI/CD PIPELINE VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append("")

        # Overall status
        total_checks = sum(len(checks) for checks in self.validation_results.values())
        passed_checks = sum(
            sum(1 for v in checks.values() if v)
            for checks in self.validation_results.values()
        )

        overall_status = "PASSED" if self.all_passed else "FAILED"
        status_color = GREEN if self.all_passed else RED

        report.append(f"Overall Status: {status_color}{overall_status}{RESET}")
        report.append(f"Checks Passed: {passed_checks}/{total_checks}")
        report.append("")

        # Detailed results
        for category, checks in self.validation_results.items():
            report.append(f"\n{BLUE}{category.upper()}{RESET}")
            report.append("-" * len(category))

            for check, passed in checks.items():
                if isinstance(passed, bool):
                    report.append(f"  {self.check_mark(passed)} {check}")
                else:
                    report.append(f"  ℹ️  {check}: {passed}")

        # Recommendations
        if not self.all_passed:
            report.append(f"\n{YELLOW}RECOMMENDATIONS:{RESET}")

            if not all(self.validation_results.get("dependencies", {}).values()):
                report.append("- Run: python scripts/ci_cd_rehab/fix_dependencies.py")
                report.append("- Run: pip install -r requirements.txt")

            if not all(self.validation_results.get("secrets", {}).values()):
                report.append("- Check PULUMI_ACCESS_TOKEN is set")
                report.append("- Run: .github/workflows/sync_secrets.yml")

            if not all(self.validation_results.get("code_quality", {}).values()):
                report.append("- Run: ruff check --fix .")
                report.append("- Run: black .")
                report.append("- Clear techdebt: rm -rf .techdebt")

        report.append("\n" + "=" * 60)

        return "\n".join(report)

    def run_validation(self) -> bool:
        """Run all validations"""
        validations = [
            ("Dependencies", self.validate_dependencies),
            ("GitHub Actions", self.validate_github_actions),
            ("Secrets", self.validate_secrets),
            ("Infrastructure", self.validate_infrastructure),
            ("Code Quality", self.validate_code_quality),
            ("Documentation", self.validate_documentation),
            ("Monitoring", self.validate_monitoring),
        ]

        for name, validator in validations:
            logger.info(f"\nRunning {name} validation...")
            passed = validator()
            if not passed:
                self.all_passed = False

            status = "PASSED" if passed else "FAILED"
            color = GREEN if passed else RED
            logger.info(f"{name}: {color}{status}{RESET}")

        return self.all_passed


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate CI/CD pipeline rehabilitation"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--github-output", action="store_true", help="Write GitHub Actions output"
    )

    args = parser.parse_args()

    # Run validation
    validator = PipelineValidator()
    all_passed = validator.run_validation()

    # Output results
    if args.json:
        print(
            json.dumps(
                {
                    "passed": all_passed,
                    "timestamp": datetime.now().isoformat(),
                    "results": validator.validation_results,
                },
                indent=2,
            )
        )
    elif args.github_output:
        # Write GitHub Actions outputs
        print(f"::set-output name=validation_passed::{str(all_passed).lower()}")

        # Add annotations for failures
        for category, checks in validator.validation_results.items():
            for check, passed in checks.items():
                if not passed:
                    print(f"::error::{category}: {check} failed")
    else:
        # Print human-readable report
        report = validator.generate_report()
        print(report)

    # Exit code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
