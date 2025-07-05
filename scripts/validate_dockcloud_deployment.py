#!/usr/bin/env python3
"""
Dockcloud Deployment Validation Script for Sophia AI

This script validates that all Dockcloud configurations are correct after cleanup
and ensures the platform is ready for Lambda Labs deployment.

Validates:
1. Docker build integrity
2. Docker-compose configuration validity
3. Service endpoint definitions
4. Secret management configuration
5. CI/CD workflow integrity
6. MCP server configurations
7. Infrastructure deployment readiness
"""

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("dockcloud_validation.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validation result for a specific check."""

    check_name: str
    passed: bool
    message: str
    details: dict | None = None


@dataclass
class ValidationReport:
    """Comprehensive validation report."""

    timestamp: str
    overall_status: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    results: list[ValidationResult]
    recommendations: list[str]


class DockcloudDeploymentValidator:
    """Validates Dockcloud deployment readiness."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.results: list[ValidationResult] = []

        # Expected files after cleanup
        self.required_files = [
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.override.yml",
            "docker-compose.prod.yml",
            "docker-compose.cloud.yml",
            "docker/Dockerfile.mcp-server",
            "pyproject.toml",
            ".dockerignore",
            "backend/app/unified_fastapi_app.py",
        ]

        # Files that should NOT exist after cleanup
        self.prohibited_files = [
            "backend/env.example",
            "frontend/env.example",
            "deployment_credentials.env.example",
            "Dockerfile.advanced",
            "Dockerfile.optimized",
            "backend/app/working_fastapi_app.py",
            "backend/app/modernized_fastapi_app.py",
            "sophia_standalone_server.py",
            "deploy.sh",
            "package.json",
        ]

        # Expected services in docker-compose.cloud.yml
        self.expected_cloud_services = [
            "sophia-backend",
            "mem0-server",
            "cortex-aisql-server",
            "redis",
            "postgres",
            "traefik",
            "prometheus",
            "grafana",
        ]

    async def validate_deployment(self) -> ValidationReport:
        """Execute comprehensive deployment validation."""
        logger.info("🔍 Starting Dockcloud Deployment Validation")
        logger.info(f"   Project Root: {self.project_root}")

        # Execute all validation checks
        await self._validate_file_structure()
        await self._validate_docker_build()
        await self._validate_compose_files()
        await self._validate_secret_management()
        await self._validate_mcp_configuration()
        await self._validate_ci_workflows()
        await self._validate_infrastructure_config()
        await self._validate_service_endpoints()

        # Generate report
        report = self._generate_report()
        self._save_report(report)

        return report

    async def _validate_file_structure(self) -> None:
        """Validate that required files exist and prohibited files are removed."""
        logger.info("📁 Validating file structure...")

        # Check required files
        missing_files = []
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            self.results.append(
                ValidationResult(
                    check_name="Required Files",
                    passed=False,
                    message=f"Missing {len(missing_files)} required files",
                    details={"missing_files": missing_files},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="Required Files",
                    passed=True,
                    message="All required files present",
                )
            )

        # Check prohibited files are removed
        remaining_files = []
        for file_path in self.prohibited_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                remaining_files.append(file_path)

        if remaining_files:
            self.results.append(
                ValidationResult(
                    check_name="Prohibited Files Removed",
                    passed=False,
                    message=f"Found {len(remaining_files)} files that should be deleted",
                    details={"remaining_files": remaining_files},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="Prohibited Files Removed",
                    passed=True,
                    message="All obsolete files successfully removed",
                )
            )

    async def _validate_docker_build(self) -> None:
        """Validate Docker build integrity."""
        logger.info("🐳 Validating Docker build...")

        try:
            # Test main Dockerfile build
            result = subprocess.run(
                [
                    "docker",
                    "build",
                    "--target",
                    "production",
                    "-t",
                    "sophia-ai:validation",
                    ".",
                    "--quiet",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                self.results.append(
                    ValidationResult(
                        check_name="Main Docker Build",
                        passed=True,
                        message="Docker build successful",
                        details={"image_id": result.stdout.strip()},
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        check_name="Main Docker Build",
                        passed=False,
                        message="Docker build failed",
                        details={"error": result.stderr},
                    )
                )

            # Test MCP server Dockerfile
            result = subprocess.run(
                [
                    "docker",
                    "build",
                    "-f",
                    "docker/Dockerfile.mcp-server",
                    "--build-arg",
                    "MCP_SERVER_PATH=backend/mcp_servers/ai_memory",
                    "--build-arg",
                    "MCP_SERVER_MODULE=enhanced_ai_memory_mcp_server",
                    "--build-arg",
                    "MCP_SERVER_PORT=8080",
                    "-t",
                    "sophia-ai:mcp-validation",
                    ".",
                    "--quiet",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                self.results.append(
                    ValidationResult(
                        check_name="MCP Server Docker Build",
                        passed=True,
                        message="MCP server Docker build successful",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        check_name="MCP Server Docker Build",
                        passed=False,
                        message="MCP server Docker build failed",
                        details={"error": result.stderr},
                    )
                )

        except subprocess.TimeoutExpired:
            self.results.append(
                ValidationResult(
                    check_name="Docker Build Timeout",
                    passed=False,
                    message="Docker build timed out after 5 minutes",
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    check_name="Docker Build Error",
                    passed=False,
                    message=f"Docker build error: {str(e)}",
                )
            )

    async def _validate_compose_files(self) -> None:
        """Validate docker-compose file configurations."""
        logger.info("📋 Validating docker-compose files...")

        compose_files = [
            "docker-compose.yml",
            "docker-compose.override.yml",
            "docker-compose.prod.yml",
            "docker-compose.cloud.yml",
        ]

        for compose_file in compose_files:
            file_path = self.project_root / compose_file
            if not file_path.exists():
                self.results.append(
                    ValidationResult(
                        check_name=f"Compose File: {compose_file}",
                        passed=False,
                        message=f"Missing {compose_file}",
                    )
                )
                continue

            try:
                with open(file_path) as f:
                    compose_config = yaml.safe_load(f)

                # Validate YAML structure
                if "services" not in compose_config:
                    self.results.append(
                        ValidationResult(
                            check_name=f"Compose File: {compose_file}",
                            passed=False,
                            message="Missing 'services' section",
                        )
                    )
                    continue

                # Special validation for cloud deployment file
                if compose_file == "docker-compose.cloud.yml":
                    missing_services = []
                    for service in self.expected_cloud_services:
                        if service not in compose_config["services"]:
                            missing_services.append(service)

                    if missing_services:
                        self.results.append(
                            ValidationResult(
                                check_name=f"Compose File: {compose_file}",
                                passed=False,
                                message=f"Missing services: {missing_services}",
                            )
                        )
                    else:
                        self.results.append(
                            ValidationResult(
                                check_name=f"Compose File: {compose_file}",
                                passed=True,
                                message="All expected services present",
                            )
                        )
                else:
                    self.results.append(
                        ValidationResult(
                            check_name=f"Compose File: {compose_file}",
                            passed=True,
                            message="Valid YAML structure",
                        )
                    )

                # Check for prohibited environment file references
                content = file_path.read_text()
                if ".env.example" in content:
                    self.results.append(
                        ValidationResult(
                            check_name=f"Environment References: {compose_file}",
                            passed=False,
                            message="Contains references to .env.example files",
                        )
                    )
                else:
                    self.results.append(
                        ValidationResult(
                            check_name=f"Environment References: {compose_file}",
                            passed=True,
                            message="No prohibited environment file references",
                        )
                    )

            except yaml.YAMLError as e:
                self.results.append(
                    ValidationResult(
                        check_name=f"Compose File: {compose_file}",
                        passed=False,
                        message=f"Invalid YAML: {str(e)}",
                    )
                )
            except Exception as e:
                self.results.append(
                    ValidationResult(
                        check_name=f"Compose File: {compose_file}",
                        passed=False,
                        message=f"Error reading file: {str(e)}",
                    )
                )

    async def _validate_secret_management(self) -> None:
        """Validate secret management configuration."""
        logger.info("🔐 Validating secret management...")

        # Check that Pulumi ESC config exists
        esc_config_path = self.project_root / "infrastructure/esc/production.yaml"
        if esc_config_path.exists():
            self.results.append(
                ValidationResult(
                    check_name="Pulumi ESC Configuration",
                    passed=True,
                    message="ESC configuration file found",
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="Pulumi ESC Configuration",
                    passed=False,
                    message="Missing ESC configuration file",
                )
            )

        # Check auto_esc_config.py exists
        auto_esc_path = self.project_root / "backend/core/auto_esc_config.py"
        if auto_esc_path.exists():
            self.results.append(
                ValidationResult(
                    check_name="Auto ESC Config",
                    passed=True,
                    message="Auto ESC config module found",
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="Auto ESC Config",
                    passed=False,
                    message="Missing auto ESC config module",
                )
            )

        # Validate no hardcoded secrets in docker files
        secret_patterns = [
            "sk-",  # OpenAI keys
            "pul-",  # Pulumi tokens
            "ghp_",  # GitHub tokens
        ]

        for docker_file in ["Dockerfile", "docker-compose.cloud.yml"]:
            file_path = self.project_root / docker_file
            if file_path.exists():
                content = file_path.read_text()
                found_secrets = []
                for pattern in secret_patterns:
                    if pattern in content:
                        found_secrets.append(pattern)

                if found_secrets:
                    self.results.append(
                        ValidationResult(
                            check_name=f"Secret Leakage: {docker_file}",
                            passed=False,
                            message=f"Found potential secrets: {found_secrets}",
                        )
                    )
                else:
                    self.results.append(
                        ValidationResult(
                            check_name=f"Secret Leakage: {docker_file}",
                            passed=True,
                            message="No hardcoded secrets detected",
                        )
                    )

    async def _validate_mcp_configuration(self) -> None:
        """Validate MCP server configurations."""
        logger.info("🔧 Validating MCP configurations...")

        # Check cursor MCP config
        cursor_config_path = (
            self.project_root / "config/cursor_enhanced_mcp_config.json"
        )
        if cursor_config_path.exists():
            try:
                with open(cursor_config_path) as f:
                    mcp_config = json.load(f)

                if "mcpServers" in mcp_config:
                    server_count = len(mcp_config["mcpServers"])
                    self.results.append(
                        ValidationResult(
                            check_name="MCP Server Configuration",
                            passed=True,
                            message=f"Found {server_count} configured MCP servers",
                        )
                    )
                else:
                    self.results.append(
                        ValidationResult(
                            check_name="MCP Server Configuration",
                            passed=False,
                            message="Missing mcpServers section",
                        )
                    )

            except json.JSONDecodeError as e:
                self.results.append(
                    ValidationResult(
                        check_name="MCP Server Configuration",
                        passed=False,
                        message=f"Invalid JSON: {str(e)}",
                    )
                )
        else:
            self.results.append(
                ValidationResult(
                    check_name="MCP Server Configuration",
                    passed=False,
                    message="Missing MCP configuration file",
                )
            )

        # Check MCP server directories exist
        mcp_servers_path = self.project_root / "mcp-servers"
        if mcp_servers_path.exists():
            server_dirs = [
                d
                for d in mcp_servers_path.iterdir()
                if d.is_dir() and not d.name.startswith("_")
            ]
            self.results.append(
                ValidationResult(
                    check_name="MCP Server Directories",
                    passed=True,
                    message=f"Found {len(server_dirs)} MCP server directories",
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="MCP Server Directories",
                    passed=False,
                    message="Missing mcp-servers directory",
                )
            )

    async def _validate_ci_workflows(self) -> None:
        """Validate CI/CD workflow configurations."""
        logger.info("🔄 Validating CI/CD workflows...")

        workflows_path = self.project_root / ".github/workflows"
        if not workflows_path.exists():
            self.results.append(
                ValidationResult(
                    check_name="GitHub Workflows Directory",
                    passed=False,
                    message="Missing .github/workflows directory",
                )
            )
            return

        workflow_files = list(workflows_path.glob("*.yml"))
        if not workflow_files:
            self.results.append(
                ValidationResult(
                    check_name="GitHub Workflows",
                    passed=False,
                    message="No workflow files found",
                )
            )
            return

        # Check for prohibited references
        for workflow_file in workflow_files:
            try:
                content = workflow_file.read_text()

                # Check for references to deleted files
                prohibited_refs = [
                    "deploy.sh",
                    "scripts/deploy_to_lambda_labs.py",
                    ".env.example",
                ]

                found_refs = []
                for ref in prohibited_refs:
                    if ref in content:
                        found_refs.append(ref)

                if found_refs:
                    self.results.append(
                        ValidationResult(
                            check_name=f"Workflow: {workflow_file.name}",
                            passed=False,
                            message=f"Contains references to deleted files: {found_refs}",
                        )
                    )
                else:
                    self.results.append(
                        ValidationResult(
                            check_name=f"Workflow: {workflow_file.name}",
                            passed=True,
                            message="No prohibited file references",
                        )
                    )

            except Exception as e:
                self.results.append(
                    ValidationResult(
                        check_name=f"Workflow: {workflow_file.name}",
                        passed=False,
                        message=f"Error reading workflow: {str(e)}",
                    )
                )

    async def _validate_infrastructure_config(self) -> None:
        """Validate infrastructure configuration."""
        logger.info("🏗️ Validating infrastructure configuration...")

        # Check Pulumi configuration
        pulumi_yaml_path = self.project_root / "Pulumi.yaml"
        if pulumi_yaml_path.exists():
            self.results.append(
                ValidationResult(
                    check_name="Pulumi Configuration",
                    passed=True,
                    message="Pulumi.yaml found",
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="Pulumi Configuration",
                    passed=False,
                    message="Missing Pulumi.yaml",
                )
            )

        # Check infrastructure directory
        infra_path = self.project_root / "infrastructure"
        if infra_path.exists():
            self.results.append(
                ValidationResult(
                    check_name="Infrastructure Directory",
                    passed=True,
                    message="Infrastructure directory found",
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="Infrastructure Directory",
                    passed=False,
                    message="Missing infrastructure directory",
                )
            )

        # Check deployment script exists
        deploy_script_path = (
            self.project_root / "scripts/deploy_to_lambda_labs_cloud.py"
        )
        if deploy_script_path.exists():
            self.results.append(
                ValidationResult(
                    check_name="Lambda Labs Deployment Script",
                    passed=True,
                    message="Deployment script found",
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    check_name="Lambda Labs Deployment Script",
                    passed=False,
                    message="Missing deployment script",
                )
            )

    async def _validate_service_endpoints(self) -> None:
        """Validate service endpoint definitions."""
        logger.info("🌐 Validating service endpoints...")

        # Check docker-compose.cloud.yml for proper service definitions
        cloud_compose_path = self.project_root / "docker-compose.cloud.yml"
        if not cloud_compose_path.exists():
            self.results.append(
                ValidationResult(
                    check_name="Service Endpoints",
                    passed=False,
                    message="Missing docker-compose.cloud.yml",
                )
            )
            return

        try:
            with open(cloud_compose_path) as f:
                compose_config = yaml.safe_load(f)

            services = compose_config.get("services", {})

            # Check critical service ports
            expected_ports = {
                "sophia-backend": [8000],
                "mem0-server": [8080],
                "cortex-aisql-server": [8080],
                "redis": [6379],
                "postgres": [5432],
                "traefik": [80, 443],
                "prometheus": [9090],
                "grafana": [3000],
            }

            missing_ports = []
            for service_name, expected_service_ports in expected_ports.items():
                if service_name not in services:
                    missing_ports.append(f"{service_name} (missing service)")
                    continue

                service_config = services[service_name]
                if "ports" not in service_config:
                    missing_ports.append(f"{service_name} (no ports)")
                    continue

                # Extract port numbers from service configuration
                service_ports = []
                for port_config in service_config["ports"]:
                    if isinstance(port_config, dict):
                        service_ports.append(
                            port_config.get("published", port_config.get("target"))
                        )
                    elif isinstance(port_config, str) and ":" in port_config:
                        service_ports.append(int(port_config.split(":")[0]))
                    elif isinstance(port_config, int):
                        service_ports.append(port_config)

                for expected_port in expected_service_ports:
                    if expected_port not in service_ports:
                        missing_ports.append(f"{service_name}:{expected_port}")

            if missing_ports:
                self.results.append(
                    ValidationResult(
                        check_name="Service Endpoints",
                        passed=False,
                        message=f"Missing service ports: {missing_ports}",
                    )
                )
            else:
                self.results.append(
                    ValidationResult(
                        check_name="Service Endpoints",
                        passed=True,
                        message="All expected service endpoints configured",
                    )
                )

        except Exception as e:
            self.results.append(
                ValidationResult(
                    check_name="Service Endpoints",
                    passed=False,
                    message=f"Error validating endpoints: {str(e)}",
                )
            )

    def _generate_report(self) -> ValidationReport:
        """Generate comprehensive validation report."""
        passed_checks = sum(1 for result in self.results if result.passed)
        failed_checks = len(self.results) - passed_checks

        overall_status = "PASS" if failed_checks == 0 else "FAIL"

        recommendations = []
        if failed_checks > 0:
            recommendations.append("Fix all failed validation checks before deployment")
            recommendations.append("Run validation again after fixes")

        recommendations.extend(
            [
                "Perform staging deployment test on Lambda Labs",
                "Run comprehensive integration tests",
                "Monitor deployment logs for any issues",
                "Validate all service endpoints after deployment",
            ]
        )

        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            overall_status=overall_status,
            total_checks=len(self.results),
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            results=self.results,
            recommendations=recommendations,
        )

    def _save_report(self, report: ValidationReport) -> None:
        """Save validation report to file."""
        report_path = self.project_root / "DOCKCLOUD_VALIDATION_REPORT.json"

        report_dict = {
            "validation_summary": {
                "timestamp": report.timestamp,
                "overall_status": report.overall_status,
                "total_checks": report.total_checks,
                "passed_checks": report.passed_checks,
                "failed_checks": report.failed_checks,
            },
            "detailed_results": [
                {
                    "check_name": result.check_name,
                    "passed": result.passed,
                    "message": result.message,
                    "details": result.details,
                }
                for result in report.results
            ],
            "recommendations": report.recommendations,
            "dockcloud_readiness": {
                "docker_build_ready": any(
                    r.check_name.startswith("Docker Build") and r.passed
                    for r in report.results
                ),
                "compose_config_ready": any(
                    r.check_name.startswith("Compose File") and r.passed
                    for r in report.results
                ),
                "secret_management_ready": any(
                    r.check_name.startswith("Pulumi ESC") and r.passed
                    for r in report.results
                ),
                "deployment_script_ready": any(
                    r.check_name == "Lambda Labs Deployment Script" and r.passed
                    for r in report.results
                ),
            },
        }

        with open(report_path, "w") as f:
            json.dump(report_dict, f, indent=2)

        logger.info(f"📊 Validation report saved: {report_path}")

        # Log summary
        logger.info("\n📈 VALIDATION SUMMARY")
        logger.info(f"   Overall Status: {report.overall_status}")
        logger.info(f"   Total Checks: {report.total_checks}")
        logger.info(f"   Passed: {report.passed_checks}")
        logger.info(f"   Failed: {report.failed_checks}")

        if report.failed_checks > 0:
            logger.info("\n❌ FAILED CHECKS:")
            for result in report.results:
                if not result.passed:
                    logger.info(f"   - {result.check_name}: {result.message}")


async def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Dockcloud Deployment Validation")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    validator = DockcloudDeploymentValidator(args.project_root)
    report = await validator.validate_deployment()

    if report.overall_status == "PASS":
        logger.info("✅ All validation checks passed - Ready for Dockcloud deployment!")
        return 0
    else:
        logger.error(f"❌ Validation failed - {report.failed_checks} checks failed")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
