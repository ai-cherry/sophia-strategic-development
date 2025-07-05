#!/usr/bin/env python3
"""
Standardize MCP Server Configurations
Fixes all configuration inconsistencies and standardizes deployment settings
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("mcp_standardization.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class MCPConfigStandardizer:
    """Standardize all MCP server configurations"""

    def __init__(self):
        self.root_dir = Path("/Users/lynnmusil/sophia-main")
        self.lambda_labs_ips = {
            "platform": "146.235.200.1",
            "mcp": "165.1.69.44",
            "ai": "137.131.6.213",
        }
        self.standard_ports = {
            "ai_memory": 9001,
            "codacy": 3008,
            "github": 9003,
            "linear": 9004,
            "snowflake_admin": 9020,
            "asana": 9006,
            "notion": 9007,
            "lambda_labs_cli": 9040,
            "ui_ux_agent": 9002,
            "portkey_admin": 9013,
            "hubspot": 9021,
        }
        self.issues_found = []
        self.fixes_applied = []

    def standardize_docker_compose(self) -> None:
        """Standardize Docker Compose configurations"""
        logger.info("🔧 Standardizing Docker Compose configurations...")

        compose_file = self.root_dir / "docker-compose.cloud.yml"

        if not compose_file.exists():
            logger.error(f"❌ Docker Compose file not found: {compose_file}")
            return

        try:
            with open(compose_file) as f:
                compose_data = yaml.safe_load(f)

            # Standardize service configurations
            standardized_services = {}

            for service_name, service_config in compose_data.get(
                "services", {}
            ).items():
                if "mcp" in service_name.lower():
                    # Standardize MCP service configuration
                    standardized_config = self._standardize_mcp_service(
                        service_name, service_config
                    )
                    standardized_services[service_name] = standardized_config
                else:
                    standardized_services[service_name] = service_config

            # Update compose data
            compose_data["services"] = standardized_services

            # Write back to file
            with open(compose_file, "w") as f:
                yaml.dump(compose_data, f, default_flow_style=False, indent=2)

            logger.info(f"✅ Standardized Docker Compose configuration: {compose_file}")
            self.fixes_applied.append(f"Standardized Docker Compose: {compose_file}")

        except Exception as e:
            logger.error(f"❌ Error standardizing Docker Compose: {e}")
            self.issues_found.append(f"Docker Compose error: {e}")

    def _standardize_mcp_service(
        self, service_name: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Standardize individual MCP service configuration"""

        # Standard MCP service template
        standard_config = {
            "deploy": {
                "replicas": 1,
                "restart_policy": {
                    "condition": "on-failure",
                    "delay": "5s",
                    "max_attempts": 3,
                },
                "placement": {"constraints": ["node.role == worker"]},
                "resources": {
                    "limits": {"cpus": "0.5", "memory": "512M"},
                    "reservations": {"cpus": "0.1", "memory": "128M"},
                },
            },
            "healthcheck": {
                "test": [
                    "CMD",
                    "curl",
                    "-f",
                    f"http://localhost:{self._get_service_port(service_name)}/health",
                ],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "10s",
            },
            "environment": self._get_standard_environment(),
            "secrets": self._get_standard_secrets(),
            "networks": ["sophia-network"],
        }

        # Merge with existing config, prioritizing standard values
        merged_config = {**config, **standard_config}

        # Ensure proper port configuration
        if "ports" in merged_config:
            port = self._get_service_port(service_name)
            merged_config["ports"] = [f"{port}:{port}"]

        return merged_config

    def _get_service_port(self, service_name: str) -> int:
        """Get standard port for service"""
        for key, port in self.standard_ports.items():
            if key in service_name.lower():
                return port
        return 9000  # Default port

    def _get_standard_environment(self) -> list[str]:
        """Get standard environment variables"""
        return [
            "ENVIRONMENT=prod",
            "PULUMI_ORG=scoobyjava-org",
            "PULUMI_STACK=sophia-ai-production",
            "PYTHONPATH=/app",
            "PYTHONUNBUFFERED=1",
        ]

    def _get_standard_secrets(self) -> list[str]:
        """Get standard secrets"""
        return [
            "openai_api_key",
            "anthropic_api_key",
            "gong_access_token",
            "pinecone_api_key",
            "pulumi_access_token",
        ]

    def standardize_dockerfiles(self) -> None:
        """Standardize all Dockerfiles"""
        logger.info("🔧 Standardizing Dockerfiles...")

        # Find all Dockerfiles
        dockerfiles = []
        for dockerfile_path in self.root_dir.rglob("Dockerfile*"):
            if dockerfile_path.is_file():
                dockerfiles.append(dockerfile_path)

        logger.info(f"Found {len(dockerfiles)} Dockerfiles")

        # Standard Dockerfile template
        standard_dockerfile = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        # Update MCP server Dockerfiles
        for dockerfile in dockerfiles:
            if "mcp" in str(dockerfile).lower():
                try:
                    # Read current content
                    with open(dockerfile) as f:
                        current_content = f.read()

                    # Check if it needs standardization
                    if self._needs_dockerfile_standardization(current_content):
                        # Create standardized version
                        standardized_content = self._create_standardized_dockerfile(
                            dockerfile, current_content
                        )

                        # Write back
                        with open(dockerfile, "w") as f:
                            f.write(standardized_content)

                        logger.info(f"✅ Standardized Dockerfile: {dockerfile}")
                        self.fixes_applied.append(
                            f"Standardized Dockerfile: {dockerfile}"
                        )
                    else:
                        logger.info(f"ℹ️ Dockerfile already standardized: {dockerfile}")

                except Exception as e:
                    logger.error(f"❌ Error standardizing Dockerfile {dockerfile}: {e}")
                    self.issues_found.append(f"Dockerfile error {dockerfile}: {e}")

    def _needs_dockerfile_standardization(self, content: str) -> bool:
        """Check if Dockerfile needs standardization"""
        checks = [
            "FROM python:3.11-slim" in content,
            "WORKDIR /app" in content,
            "HEALTHCHECK" in content,
            "USER appuser" in content,
        ]
        return not all(checks)

    def _create_standardized_dockerfile(
        self, dockerfile_path: Path, current_content: str
    ) -> str:
        """Create standardized Dockerfile content"""

        # Extract service-specific information
        service_name = dockerfile_path.parent.name
        port = self._get_service_port(service_name)

        # Create service-specific Dockerfile
        standardized_content = f"""FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
"""

        return standardized_content

    def standardize_github_workflows(self) -> None:
        """Standardize GitHub Actions workflows"""
        logger.info("🔧 Standardizing GitHub Actions workflows...")

        workflows_dir = self.root_dir / ".github" / "workflows"
        if not workflows_dir.exists():
            logger.warning("⚠️ GitHub workflows directory not found")
            return

        # Find all workflow files
        workflows = list(workflows_dir.glob("*.yml")) + list(
            workflows_dir.glob("*.yaml")
        )

        for workflow_file in workflows:
            try:
                with open(workflow_file) as f:
                    content = f.read()

                # Update Lambda Labs IP addresses
                updated_content = content
                old_ip = "104.171.202.64"

                if old_ip in content:
                    # Replace with correct IP based on context
                    updated_content = updated_content.replace(
                        old_ip, self.lambda_labs_ips["mcp"]
                    )

                    with open(workflow_file, "w") as f:
                        f.write(updated_content)

                    logger.info(f"✅ Updated IP addresses in workflow: {workflow_file}")
                    self.fixes_applied.append(f"Updated workflow IPs: {workflow_file}")

            except Exception as e:
                logger.error(f"❌ Error updating workflow {workflow_file}: {e}")
                self.issues_found.append(f"Workflow error {workflow_file}: {e}")

    def standardize_port_configurations(self) -> None:
        """Standardize port configurations across all configs"""
        logger.info("🔧 Standardizing port configurations...")

        # Update MCP configuration files
        config_files = [
            "config/cursor_enhanced_mcp_config.json",
            "config/consolidated_mcp_ports.json",
            "mcp-config/mcp_servers.json",
        ]

        for config_file in config_files:
            config_path = self.root_dir / config_file
            if not config_path.exists():
                continue

            try:
                with open(config_path) as f:
                    config_data = json.load(f)

                # Update port configurations
                updated = False
                if "mcpServers" in config_data:
                    for server_name, server_config in config_data["mcpServers"].items():
                        if "command" in server_config:
                            # Update port in command
                            for port_name, port_num in self.standard_ports.items():
                                if port_name in server_name.lower():
                                    # Update port in command arguments
                                    if "args" in server_config:
                                        for i, arg in enumerate(server_config["args"]):
                                            if "--port" in arg or "-p" in arg:
                                                if i + 1 < len(server_config["args"]):
                                                    old_port = server_config["args"][
                                                        i + 1
                                                    ]
                                                    if old_port != str(port_num):
                                                        server_config["args"][
                                                            i + 1
                                                        ] = str(port_num)
                                                        updated = True
                                                        logger.info(
                                                            f"Updated port for {server_name}: {old_port} -> {port_num}"
                                                        )

                if updated:
                    with open(config_path, "w") as f:
                        json.dump(config_data, f, indent=2)

                    self.fixes_applied.append(f"Updated ports in: {config_file}")

            except Exception as e:
                logger.error(f"❌ Error updating ports in {config_file}: {e}")
                self.issues_found.append(f"Port config error {config_file}: {e}")

    def generate_deployment_report(self) -> None:
        """Generate deployment standardization report"""
        logger.info("📊 Generating deployment standardization report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "standardization_summary": {
                "total_fixes_applied": len(self.fixes_applied),
                "issues_found": len(self.issues_found),
                "success_rate": f"{((len(self.fixes_applied) / (len(self.fixes_applied) + len(self.issues_found))) * 100):.1f}%"
                if (len(self.fixes_applied) + len(self.issues_found)) > 0
                else "100%",
            },
            "fixes_applied": self.fixes_applied,
            "issues_found": self.issues_found,
            "configuration_standards": {
                "lambda_labs_ips": self.lambda_labs_ips,
                "standard_ports": self.standard_ports,
                "docker_base_image": "python:3.11-slim",
                "environment_variables": self._get_standard_environment(),
                "secrets": self._get_standard_secrets(),
            },
        }

        # Write report
        report_file = self.root_dir / "mcp_standardization_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Report saved to: {report_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("🎯 MCP CONFIGURATION STANDARDIZATION COMPLETE")
        print("=" * 60)
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        print(f"❌ Issues Found: {len(self.issues_found)}")
        print(f"📊 Success Rate: {report['standardization_summary']['success_rate']}")
        print("\n📋 KEY STANDARDIZATIONS:")
        print("• Docker Compose configurations")
        print("• Dockerfile standardization")
        print("• GitHub Actions workflows")
        print("• Port configurations")
        print("• Lambda Labs IP addresses")
        print(f"\n📄 Full report: {report_file}")
        print("=" * 60)

    def run_standardization(self) -> None:
        """Run complete standardization process"""
        logger.info("🚀 Starting MCP configuration standardization...")

        try:
            # Run all standardization steps
            self.standardize_docker_compose()
            self.standardize_dockerfiles()
            self.standardize_github_workflows()
            self.standardize_port_configurations()

            # Generate report
            self.generate_deployment_report()

            logger.info("✅ MCP configuration standardization completed successfully!")

        except Exception as e:
            logger.error(f"❌ Critical error during standardization: {e}")
            raise


def main():
    """Main function"""
    standardizer = MCPConfigStandardizer()
    standardizer.run_standardization()


if __name__ == "__main__":
    main()
