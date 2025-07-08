#!/usr/bin/env python3
"""
Migration Safety Validator
Comprehensive validation to ensure safe MCP V2+ migration
"""

import ast
import json
import logging
import socket
import subprocess
import sys
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validation result"""

    category: str
    check: str
    passed: bool
    message: str
    severity: str  # "critical", "warning", "info"
    details: Optional[dict] = None


class MigrationValidator:
    """Validates migration safety"""

    def __init__(self):
        self.root = Path.cwd()
        self.results: list[ValidationResult] = []
        self.critical_issues = 0
        self.warnings = 0

    def validate_all(self) -> bool:
        """Run all validation checks"""
        logger.info("Starting migration safety validation...")

        # Run validation categories
        self._validate_git_state()
        self._validate_dependencies()
        self._validate_imports()
        self._validate_ports()
        self._validate_secrets()
        self._validate_tests()
        self._validate_docker()
        self._validate_ci_cd()

        # Generate report
        self._generate_report()

        return self.critical_issues == 0

    def _add_result(
        self,
        category: str,
        check: str,
        passed: bool,
        message: str,
        severity: str = "warning",
        details: Optional[dict] = None,
    ):
        """Add validation result"""
        result = ValidationResult(category, check, passed, message, severity, details)
        self.results.append(result)

        if not passed:
            if severity == "critical":
                self.critical_issues += 1
            else:
                self.warnings += 1

    def _validate_git_state(self):
        """Validate git repository state"""
        logger.info("Validating git state...")

        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.stdout.strip():
            self._add_result(
                "git",
                "clean_working_dir",
                False,
                "Working directory has uncommitted changes",
                "critical",
                {"files": result.stdout.strip().split("\n")},
            )
        else:
            self._add_result(
                "git", "clean_working_dir", True, "Working directory is clean"
            )

        # Check current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
        )

        current_branch = result.stdout.strip()
        if current_branch == "main":
            self._add_result(
                "git",
                "feature_branch",
                False,
                "On main branch, should use feature branch",
                "warning",
            )
        else:
            self._add_result(
                "git", "feature_branch", True, f"On feature branch: {current_branch}"
            )

    def _validate_dependencies(self):
        """Validate Python dependencies"""
        logger.info("Validating dependencies...")

        # Check UV installation
        result = subprocess.run(["which", "uv"], capture_output=True, check=False)
        if result.returncode != 0:
            self._add_result(
                "dependencies",
                "uv_installed",
                False,
                "UV package manager not installed",
                "critical",
            )
            return
        else:
            self._add_result(
                "dependencies", "uv_installed", True, "UV package manager installed"
            )

        # Check dependency sync
        result = subprocess.run(
            ["uv", "sync", "--dry-run"], capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            self._add_result(
                "dependencies",
                "deps_synced",
                False,
                "Dependencies not synced",
                "critical",
                {"error": result.stderr},
            )
        else:
            self._add_result(
                "dependencies", "deps_synced", True, "Dependencies are synced"
            )

        # Check for version conflicts
        self._check_version_conflicts()

    def _check_version_conflicts(self):
        """Check for package version conflicts"""
        try:
            result = subprocess.run(
                ["uv", "pip", "freeze"], capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                packages = {}
                for line in result.stdout.strip().split("\n"):
                    if "==" in line:
                        name, version = line.split("==")
                        packages[name.lower()] = version

                # Check critical packages
                critical_packages = {
                    "fastapi": ("0.111.0", "0.112.0"),
                    "pydantic": ("2.6.0", "3.0.0"),
                    "sqlalchemy": ("2.0.0", None),
                }

                for pkg, (min_ver, max_ver) in critical_packages.items():
                    if pkg in packages:
                        current = packages[pkg]
                        if self._version_compare(current, min_ver) < 0:
                            self._add_result(
                                "dependencies",
                                f"{pkg}_version",
                                False,
                                f"{pkg} version {current} is below minimum {min_ver}",
                                "critical",
                            )
                        elif max_ver and self._version_compare(current, max_ver) >= 0:
                            self._add_result(
                                "dependencies",
                                f"{pkg}_version",
                                False,
                                f"{pkg} version {current} is at or above maximum {max_ver}",
                                "warning",
                            )
                        else:
                            self._add_result(
                                "dependencies",
                                f"{pkg}_version",
                                True,
                                f"{pkg} version {current} is compatible",
                            )

        except Exception as e:
            self._add_result(
                "dependencies",
                "version_check",
                False,
                f"Failed to check versions: {e}",
                "warning",
            )

    def _version_compare(self, v1: str, v2: str) -> int:
        """Compare version strings"""
        from packaging import version

        return (
            -1
            if version.parse(v1) < version.parse(v2)
            else (1 if version.parse(v1) > version.parse(v2) else 0)
        )

    def _validate_imports(self):
        """Validate import conflicts"""
        logger.info("Validating imports...")

        v1_imports = set()
        v2_imports = set()
        cross_imports = []

        # Scan Python files
        for py_file in self.root.rglob("*.py"):
            if any(skip in str(py_file) for skip in [".venv", "__pycache__", "test"]):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._check_import(
                                py_file,
                                alias.name,
                                v1_imports,
                                v2_imports,
                                cross_imports,
                            )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._check_import(
                                py_file,
                                node.module,
                                v1_imports,
                                v2_imports,
                                cross_imports,
                            )

            except Exception as e:
                logger.debug(f"Error parsing {py_file}: {e}")

        if cross_imports:
            self._add_result(
                "imports",
                "no_cross_imports",
                False,
                f"Found {len(cross_imports)} cross-version imports",
                "critical",
                {"imports": cross_imports[:10]},  # First 10
            )
        else:
            self._add_result(
                "imports", "no_cross_imports", True, "No cross-version imports found"
            )

    def _check_import(
        self,
        file_path: Path,
        import_str: str,
        v1_imports: set,
        v2_imports: set,
        cross_imports: list,
    ):
        """Check individual import"""
        is_v1_file = "mcp-servers" in str(file_path)
        is_v2_file = "infrastructure/mcp_servers" in str(file_path)

        if is_v1_file and (
            "infrastructure.mcp_servers" in import_str
            or (import_str.startswith("infrastructure") and "mcp" in import_str)
        ):
            cross_imports.append(
                {"file": str(file_path), "import": import_str, "type": "v1_imports_v2"}
            )
        elif is_v2_file and "mcp-servers" in import_str:
            cross_imports.append(
                {"file": str(file_path), "import": import_str, "type": "v2_imports_v1"}
            )

    def _validate_ports(self):
        """Validate port allocations"""
        logger.info("Validating ports...")

        # Load current port allocations
        ports_file = self.root / "config" / "consolidated_mcp_ports.json"
        if not ports_file.exists():
            self._add_result(
                "ports",
                "config_exists",
                False,
                "Port configuration file not found",
                "critical",
            )
            return

        with open(ports_file) as f:
            data = json.load(f)

        # Extract all ports from the complex structure
        all_ports = {}

        # Get ports from active_servers
        if "active_servers" in data and isinstance(data["active_servers"], dict):
            for server, port in data["active_servers"].items():
                if isinstance(port, int):
                    all_ports[server] = port

        # Get ports from mcp_servers nested structure
        if "mcp_servers" in data and isinstance(data["mcp_servers"], dict):
            for category, servers in data["mcp_servers"].items():
                if isinstance(servers, dict):
                    for server, config in servers.items():
                        if isinstance(config, dict) and "port" in config:
                            all_ports[f"{category}.{server}"] = config["port"]

        # Check for duplicates
        port_to_server = {}
        duplicates = []

        for server, port in all_ports.items():
            if port in port_to_server:
                duplicates.append((port, port_to_server[port], server))
            else:
                port_to_server[port] = server

        if duplicates:
            self._add_result(
                "ports",
                "no_duplicates",
                False,
                f"Found {len(duplicates)} duplicate port assignments",
                "critical",
                {"duplicates": duplicates},
            )
        else:
            self._add_result(
                "ports",
                "no_duplicates",
                True,
                f"No duplicate port assignments (checked {len(all_ports)} servers)",
            )

        # Check if ports are available
        unavailable = []
        for server, port in list(all_ports.items())[
            :10
        ]:  # Check first 10 to avoid too many checks
            if not self._is_port_available(port):
                unavailable.append((server, port))

        if unavailable:
            self._add_result(
                "ports",
                "ports_available",
                False,
                f"{len(unavailable)} ports are already in use",
                "warning",
                {"unavailable": unavailable},
            )
        else:
            self._add_result(
                "ports", "ports_available", True, "Sampled ports are available"
            )

    def _is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            return sock.connect_ex(("localhost", port)) != 0

    def _validate_secrets(self):
        """Validate secret management"""
        logger.info("Validating secrets...")

        # Check for .env files
        env_files = list(self.root.rglob(".env*"))
        env_files = [
            f
            for f in env_files
            if not any(skip in str(f) for skip in [".venv", "node_modules", ".git"])
        ]

        if env_files:
            self._add_result(
                "secrets",
                "no_env_files",
                False,
                f"Found {len(env_files)} .env files (should use Pulumi ESC)",
                "warning",
                {"files": [str(f) for f in env_files[:10]]},
            )
        else:
            self._add_result(
                "secrets",
                "no_env_files",
                True,
                "No .env files found (good - using Pulumi ESC)",
            )

        # Check for hardcoded secrets
        self._check_hardcoded_secrets()

    def _check_hardcoded_secrets(self):
        """Check for hardcoded secrets in code"""
        import re

        secret_patterns = [
            (r'api[_-]?key\s*=\s*["\'][\w\-]{20,}["\']', "API key"),
            (r'password\s*=\s*["\'][^"\']+["\']', "Password"),
            (r'token\s*=\s*["\'][\w\-]{20,}["\']', "Token"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Secret"),
        ]

        found_secrets = []

        for py_file in self.root.rglob("*.py"):
            if any(skip in str(py_file) for skip in [".venv", "__pycache__", "test"]):
                continue

            try:
                content = py_file.read_text()
                for pattern, secret_type in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        found_secrets.append(
                            {"file": str(py_file), "type": secret_type}
                        )
                        break
            except:
                pass

        if found_secrets:
            self._add_result(
                "secrets",
                "no_hardcoded",
                False,
                f"Found {len(found_secrets)} potential hardcoded secrets",
                "critical",
                {"secrets": found_secrets[:10]},
            )
        else:
            self._add_result(
                "secrets", "no_hardcoded", True, "No hardcoded secrets found"
            )

    def _validate_tests(self):
        """Validate test coverage"""
        logger.info("Validating tests...")

        # Run tests
        result = subprocess.run(
            ["uv", "run", "pytest", "-q", "--tb=short"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            self._add_result(
                "tests",
                "all_passing",
                False,
                "Some tests are failing",
                "critical",
                {"output": result.stdout[-1000:]},  # Last 1000 chars
            )
        else:
            self._add_result("tests", "all_passing", True, "All tests are passing")

    def _validate_docker(self):
        """Validate Docker configuration"""
        logger.info("Validating Docker...")

        # Check Docker daemon
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            self._add_result(
                "docker",
                "daemon_running",
                False,
                "Docker daemon not running",
                "warning",
            )
        else:
            self._add_result(
                "docker", "daemon_running", True, "Docker daemon is running"
            )

        # Check for Dockerfile conflicts
        dockerfiles = list(self.root.rglob("Dockerfile*"))
        v1_dockerfiles = [f for f in dockerfiles if "mcp-servers" in str(f)]
        v2_dockerfiles = [
            f for f in dockerfiles if "infrastructure/mcp_servers" in str(f)
        ]

        self._add_result(
            "docker",
            "dockerfile_count",
            True,
            f"Found {len(v1_dockerfiles)} V1 and {len(v2_dockerfiles)} V2 Dockerfiles",
            "info",
        )

    def _validate_ci_cd(self):
        """Validate CI/CD configuration"""
        logger.info("Validating CI/CD...")

        workflows_dir = self.root / ".github" / "workflows"
        if not workflows_dir.exists():
            self._add_result(
                "ci_cd",
                "workflows_exist",
                False,
                "No GitHub workflows found",
                "warning",
            )
            return

        workflow_files = list(workflows_dir.glob("*.yml")) + list(
            workflows_dir.glob("*.yaml")
        )

        # Check for MCP-related workflows
        mcp_workflows = [f for f in workflow_files if "mcp" in f.name.lower()]

        if not mcp_workflows:
            self._add_result(
                "ci_cd",
                "mcp_workflows",
                False,
                "No MCP-specific workflows found",
                "warning",
            )
        else:
            self._add_result(
                "ci_cd",
                "mcp_workflows",
                True,
                f"Found {len(mcp_workflows)} MCP workflows",
            )

    def _generate_report(self):
        """Generate validation report"""
        # Print summary
        print("\n" + "=" * 60)
        print("MIGRATION SAFETY VALIDATION REPORT")
        print("=" * 60 + "\n")

        # Group by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)

        # Print by category
        for category, results in categories.items():
            print(f"\n{category.upper()}")
            print("-" * len(category))

            for result in results:
                icon = (
                    "✅"
                    if result.passed
                    else ("❌" if result.severity == "critical" else "⚠️")
                )
                print(f"{icon} {result.check}: {result.message}")

                if result.details and not result.passed:
                    for key, value in result.details.items():
                        if isinstance(value, list) and len(value) > 3:
                            print(f"   {key}: {value[:3]} ... ({len(value)} total)")
                        else:
                            print(f"   {key}: {value}")

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total checks: {len(self.results)}")
        print(f"Passed: {len([r for r in self.results if r.passed])}")
        print(f"Critical issues: {self.critical_issues}")
        print(f"Warnings: {self.warnings}")

        if self.critical_issues > 0:
            print("\n❌ MIGRATION BLOCKED: Fix critical issues before proceeding")
        else:
            print("\n✅ MIGRATION SAFE: No critical issues found")

        # Save detailed report
        report_path = self.root / "reports" / "migration_safety_report.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(
                {
                    "results": [
                        {
                            "category": r.category,
                            "check": r.check,
                            "passed": r.passed,
                            "message": r.message,
                            "severity": r.severity,
                            "details": r.details,
                        }
                        for r in self.results
                    ],
                    "summary": {
                        "total_checks": len(self.results),
                        "passed": len([r for r in self.results if r.passed]),
                        "critical_issues": self.critical_issues,
                        "warnings": self.warnings,
                        "safe_to_proceed": self.critical_issues == 0,
                    },
                },
                f,
                indent=2,
            )

        print(f"\nDetailed report saved to: {report_path}")


def main():
    """Main entry point"""
    validator = MigrationValidator()
    safe = validator.validate_all()

    sys.exit(0 if safe else 1)


if __name__ == "__main__":
    main()
