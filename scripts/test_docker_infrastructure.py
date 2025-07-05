#!/usr/bin/env python3
"""
Test Docker infrastructure readiness
"""

import json
import subprocess
from pathlib import Path


class DockerInfrastructureTester:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.results = {
            "docker_files": {},
            "compose_files": {},
            "build_tests": {},
            "summary": {},
        }

    def check_docker_installed(self) -> bool:
        """Check if Docker is installed and running"""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

        return False

    def check_docker_compose_installed(self) -> bool:
        """Check if Docker Compose is installed"""
        try:
            # Try new docker compose command first
            result = subprocess.run(
                ["docker", "compose", "version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return True

            # Try old docker-compose command
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

        return False

    def check_critical_files(self) -> dict[str, bool]:
        """Check if critical Docker files exist"""
        critical_files = {
            "docker-compose.cloud.yml": self.root_dir / "docker-compose.cloud.yml",
            "Dockerfile.uv.production": self.root_dir / "Dockerfile.uv.production",
            "docker-compose.mcp.yml": self.root_dir / "docker-compose.mcp.yml",
            "MCP Dockerfile Template": self.root_dir
            / "docker"
            / "Dockerfile.mcp-server",
        }

        results = {}
        for name, path in critical_files.items():
            exists = path.exists()
            results[name] = exists

        self.results["docker_files"] = results
        return results

    def validate_compose_files(self) -> dict[str, tuple[bool, str]]:
        """Validate Docker Compose files"""
        compose_files = [
            "docker-compose.yml",
            "docker-compose.mcp.yml",
            "docker-compose.cloud.yml",
            "docker-compose.production.yml",
        ]

        results = {}

        for compose_file in compose_files:
            filepath = self.root_dir / compose_file
            if not filepath.exists():
                results[compose_file] = (False, "File not found")
                continue

            # Validate syntax
            try:
                result = subprocess.run(
                    ["docker", "compose", "-f", str(filepath), "config"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    results[compose_file] = (True, "Valid")
                else:
                    results[compose_file] = (False, result.stderr)
            except Exception as e:
                results[compose_file] = (False, str(e))

        self.results["compose_files"] = results
        return results

    def check_mcp_dockerfiles(self) -> dict[str, bool]:
        """Check if all MCP servers have Dockerfiles"""
        mcp_servers = {
            "AI Memory": self.root_dir / "mcp-servers" / "ai_memory" / "Dockerfile",
            "Codacy": self.root_dir / "mcp-servers" / "codacy" / "Dockerfile",
            "Linear": self.root_dir / "mcp-servers" / "linear" / "Dockerfile",
            "GitHub": self.root_dir / "mcp-servers" / "github" / "Dockerfile",
            "Asana": self.root_dir / "mcp-servers" / "asana" / "Dockerfile",
            "Notion": self.root_dir / "mcp-servers" / "notion" / "Dockerfile",
            "UI/UX Agent": self.root_dir / "mcp-servers" / "ui_ux_agent" / "Dockerfile",
            "Portkey Admin": self.root_dir
            / "mcp-servers"
            / "portkey_admin"
            / "Dockerfile",
            "Lambda Labs CLI": self.root_dir
            / "mcp-servers"
            / "lambda_labs_cli"
            / "Dockerfile",
            "Snowflake Cortex": self.root_dir
            / "mcp-servers"
            / "snowflake_cortex"
            / "Dockerfile",
        }

        results = {}

        for name, path in mcp_servers.items():
            exists = path.exists()
            results[name] = exists

        return results

    def test_docker_build(self, service: str, compose_file: str) -> tuple[bool, str]:
        """Test building a specific Docker service"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    compose_file,
                    "build",
                    "--no-cache",
                    service,
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                return (True, "Build successful")
            else:
                return (False, result.stderr[-500:])  # Last 500 chars of error
        except subprocess.TimeoutExpired:
            return (False, "Build timeout (>5 minutes)")
        except Exception as e:
            return (False, str(e))

    def generate_summary(self):
        """Generate test summary"""
        # Count successes
        docker_files_ok = sum(
            1 for v in self.results.get("docker_files", {}).values() if v
        )
        docker_files_total = len(self.results.get("docker_files", {}))

        compose_files_ok = sum(
            1 for v in self.results.get("compose_files", {}).values() if v[0]
        )
        compose_files_total = len(self.results.get("compose_files", {}))

        self.results["summary"] = {
            "docker_files": f"{docker_files_ok}/{docker_files_total}",
            "compose_files": f"{compose_files_ok}/{compose_files_total}",
            "overall_readiness": f"{(docker_files_ok + compose_files_ok) / (docker_files_total + compose_files_total) * 100:.1f}%",
        }

    def save_report(self):
        """Save test report"""
        report_path = self.root_dir / "docker_infrastructure_test_report.json"
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)

    def run(self):
        """Run all infrastructure tests"""

        # Check prerequisites
        if not self.check_docker_installed():
            return

        if not self.check_docker_compose_installed():
            return

        # Run tests
        self.check_critical_files()
        self.validate_compose_files()
        self.check_mcp_dockerfiles()

        # Generate summary
        self.generate_summary()

        # Print summary

        # Save report
        self.save_report()

        # Recommendations
        if float(self.results["summary"]["overall_readiness"].rstrip("%")) < 100:
            pass
        else:
            pass


if __name__ == "__main__":
    tester = DockerInfrastructureTester()
    tester.run()
