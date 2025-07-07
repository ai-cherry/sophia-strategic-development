#!/usr/bin/env python3
"""
Comprehensive MCP Debug - Final Analysis
Analyzes all MCP-related code, files, and scripts for consistency and health
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("comprehensive_mcp_debug.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ComprehensiveMCPDebugger:
    """Complete MCP ecosystem debugger and analyzer"""

    def __init__(self):
        self.root_dir = Path("/Users/lynnmusil/sophia-main")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "servers": {},
            "configurations": {},
            "scripts": {},
            "documentation": {},
            "infrastructure": {},
            "issues": [],
            "recommendations": [],
        }
        self.mcp_servers = [
            {"name": "ai-memory", "port": 9001, "health_path": "/health"},
            {"name": "codacy", "port": 3008, "health_path": "/api/v1/health"},
            {"name": "linear", "port": 9004, "health_path": "/health"},
            {"name": "github", "port": 9003, "health_path": "/health"},
            {"name": "snowflake-admin", "port": 9020, "health_path": "/health"},
            {"name": "lambda-labs-cli", "port": 9040, "health_path": "/health"},
            {"name": "asana", "port": 3001, "health_path": "/health"},
            {"name": "notion", "port": 9005, "health_path": "/health"},
        ]

    async def run_comprehensive_analysis(self):
        """Run complete MCP ecosystem analysis"""
        logger.info("🔍 Starting Comprehensive MCP Debug Analysis")

        try:
            # 1. Analyze MCP server files and configurations
            await self.analyze_mcp_server_files()

            # 2. Check server health and connectivity
            await self.check_server_health()

            # 3. Analyze configuration files
            self.analyze_configurations()

            # 4. Analyze scripts and automation
            self.analyze_scripts()

            # 5. Analyze documentation
            self.analyze_documentation()

            # 6. Analyze infrastructure configuration
            self.analyze_infrastructure()

            # 7. Perform Docker and deployment analysis
            await self.analyze_docker_deployment()

            # 8. Generate summary and recommendations
            self.generate_summary()

            # 9. Save results
            self.save_results()

            logger.info("✅ Comprehensive MCP Debug Analysis Complete")
            return self.results

        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            self.results["error"] = str(e)
            return self.results

    async def analyze_mcp_server_files(self):
        """Analyze all MCP server files for consistency and issues"""
        logger.info("📁 Analyzing MCP server files...")

        mcp_dirs = [
            self.root_dir / "mcp-servers",
            self.root_dir / "backend" / "mcp_servers",
        ]

        server_analysis = {}

        for mcp_dir in mcp_dirs:
            if mcp_dir.exists():
                for server_path in mcp_dir.iterdir():
                    if server_path.is_dir():
                        server_name = server_path.name
                        analysis = await self.analyze_single_server(server_path)
                        server_analysis[f"{mcp_dir.name}/{server_name}"] = analysis

        self.results["servers"] = server_analysis

    async def analyze_single_server(self, server_path: Path) -> dict[str, Any]:
        """Analyze a single MCP server directory"""
        analysis = {
            "path": str(server_path),
            "files": [],
            "python_files": [],
            "config_files": [],
            "docker_files": [],
            "main_script": None,
            "health_check": False,
            "imports": [],
            "exports": [],
            "dependencies": [],
            "issues": [],
            "size_kb": 0,
        }

        try:
            # Get all files
            for file_path in server_path.rglob("*"):
                if file_path.is_file():
                    analysis["files"].append(file_path.name)
                    analysis["size_kb"] += file_path.stat().st_size / 1024

                    # Categorize files
                    if file_path.suffix == ".py":
                        analysis["python_files"].append(file_path.name)
                        await self.analyze_python_file(file_path, analysis)
                    elif file_path.name in [
                        "Dockerfile",
                        "docker-compose.yml",
                        "docker-compose.yaml",
                    ]:
                        analysis["docker_files"].append(file_path.name)
                    elif file_path.suffix in [".json", ".yaml", ".yml", ".toml"]:
                        analysis["config_files"].append(file_path.name)

            # Identify main script
            main_candidates = [
                f
                for f in analysis["python_files"]
                if "server" in f.lower() or "main" in f.lower()
            ]
            if main_candidates:
                analysis["main_script"] = main_candidates[0]

            # Check for health endpoint
            analysis["health_check"] = any(
                "health" in f.lower() for f in analysis["files"]
            )

        except Exception as e:
            analysis["issues"].append(f"Analysis error: {e}")

        return analysis

    async def analyze_python_file(self, file_path: Path, analysis: dict[str, Any]):
        """Analyze a Python file for imports, exports, and patterns"""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Extract imports
            import_lines = [
                line.strip()
                for line in content.split("\n")
                if line.strip().startswith(("import ", "from "))
            ]
            analysis["imports"].extend(import_lines)

            # Check for MCP patterns
            if "@mcp.tool" in content:
                analysis["exports"].append("MCP tools")
            if "FastAPI" in content:
                analysis["exports"].append("FastAPI app")
            if "/health" in content:
                analysis["health_check"] = True

            # Check for common issues
            if "hardcoded" in content.lower() and (
                "password" in content.lower() or "token" in content.lower()
            ):
                analysis["issues"].append("Potential hardcoded credentials")

        except Exception as e:
            analysis["issues"].append(f"Python file analysis error: {e}")

    async def check_server_health(self):
        """Check health of all MCP servers"""
        logger.info("🏥 Checking MCP server health...")

        health_results = {}

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5)
        ) as session:
            for server in self.mcp_servers:
                result = await self.check_single_server_health(session, server)
                health_results[server["name"]] = result

        self.results["health_check"] = health_results

        # Summary statistics
        healthy_count = sum(
            1 for r in health_results.values() if r["status"] == "healthy"
        )
        total_count = len(health_results)

        self.results["summary"]["health_percentage"] = (
            (healthy_count / total_count) * 100 if total_count > 0 else 0
        )
        self.results["summary"]["healthy_servers"] = healthy_count
        self.results["summary"]["total_servers"] = total_count

    async def check_single_server_health(
        self, session: aiohttp.ClientSession, server: dict[str, Any]
    ) -> dict[str, Any]:
        """Check health of a single MCP server"""
        result = {
            "name": server["name"],
            "port": server["port"],
            "status": "unknown",
            "response_time_ms": 0,
            "error": None,
            "response_data": None,
        }

        url = f"http://localhost:{server['port']}{server['health_path']}"

        try:
            start_time = time.time()
            async with session.get(url) as response:
                end_time = time.time()
                result["response_time_ms"] = round((end_time - start_time) * 1000, 2)

                if response.status == 200:
                    result["status"] = "healthy"
                    try:
                        result["response_data"] = await response.json()
                    except:
                        result["response_data"] = await response.text()
                else:
                    result["status"] = "unhealthy"
                    result["error"] = f"HTTP {response.status}"

        except aiohttp.ClientConnectorError:
            result["status"] = "unreachable"
            result["error"] = "Connection refused - server not running"
        except TimeoutError:
            result["status"] = "timeout"
            result["error"] = "Request timeout"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def analyze_configurations(self):
        """Analyze all configuration files"""
        logger.info("⚙️ Analyzing configuration files...")

        config_analysis = {
            "mcp_configs": [],
            "docker_configs": [],
            "cursor_configs": [],
            "port_conflicts": [],
            "consistency_issues": [],
        }

        # Find and analyze configuration files
        config_patterns = [
            "**/mcp*.json",
            "**/cursor*.json",
            "**/docker-compose*.yml",
            "**/config*.json",
            "**/ports*.json",
        ]

        for pattern in config_patterns:
            for config_file in self.root_dir.rglob(pattern):
                if config_file.is_file():
                    analysis = self.analyze_config_file(config_file)

                    if "mcp" in config_file.name.lower():
                        config_analysis["mcp_configs"].append(analysis)
                    elif "docker" in config_file.name.lower():
                        config_analysis["docker_configs"].append(analysis)
                    elif "cursor" in config_file.name.lower():
                        config_analysis["cursor_configs"].append(analysis)

        # Check for port conflicts
        config_analysis["port_conflicts"] = self.find_port_conflicts()

        self.results["configurations"] = config_analysis

    def analyze_config_file(self, config_file: Path) -> dict[str, Any]:
        """Analyze a single configuration file"""
        analysis = {
            "file": str(config_file.relative_to(self.root_dir)),
            "type": "unknown",
            "size_kb": round(config_file.stat().st_size / 1024, 2),
            "servers_configured": 0,
            "ports": [],
            "issues": [],
            "last_modified": datetime.fromtimestamp(
                config_file.stat().st_mtime
            ).isoformat(),
        }

        try:
            if config_file.suffix == ".json":
                with open(config_file) as f:
                    data = json.load(f)
                    analysis["type"] = "json"

                    # Extract server information
                    if isinstance(data, dict):
                        if "mcpServers" in data:
                            servers = data["mcpServers"]
                            analysis["servers_configured"] = len(servers)
                            for server_config in servers.values():
                                if "args" in server_config:
                                    for arg in server_config["args"]:
                                        if arg.startswith("--port") or arg.isdigit():
                                            try:
                                                port = int(
                                                    arg.split("=")[-1]
                                                    if "=" in arg
                                                    else arg
                                                )
                                                if 1000 <= port <= 65535:
                                                    analysis["ports"].append(port)
                                            except:
                                                pass

                        # Check for other port configurations
                        if "servers" in data and isinstance(data["servers"], dict):
                            for server_data in data["servers"].values():
                                if "port" in server_data:
                                    analysis["ports"].append(server_data["port"])

        except json.JSONDecodeError:
            analysis["issues"].append("Invalid JSON format")
        except Exception as e:
            analysis["issues"].append(f"Analysis error: {e}")

        return analysis

    def find_port_conflicts(self) -> list[dict[str, Any]]:
        """Find port conflicts across configurations"""
        port_usage = {}
        conflicts = []

        # Collect ports from server definitions
        for server in self.mcp_servers:
            port = server["port"]
            if port not in port_usage:
                port_usage[port] = []
            port_usage[port].append(f"Server: {server['name']}")

        # Find conflicts
        for port, usages in port_usage.items():
            if len(usages) > 1:
                conflicts.append({"port": port, "conflicting_usages": usages})

        return conflicts

    def analyze_scripts(self):
        """Analyze MCP-related scripts"""
        logger.info("📜 Analyzing scripts...")

        script_analysis = {
            "deployment_scripts": [],
            "debug_scripts": [],
            "management_scripts": [],
            "total_scripts": 0,
            "executable_scripts": 0,
        }

        # Find script files
        script_patterns = ["scripts/*.py", "scripts/*.sh", "*.py", "*.sh"]

        for pattern in script_patterns:
            for script_file in self.root_dir.rglob(pattern):
                if (
                    script_file.is_file()
                    and "mcp"
                    in script_file.read_text(encoding="utf-8", errors="ignore").lower()
                ):
                    analysis = {
                        "file": str(script_file.relative_to(self.root_dir)),
                        "type": script_file.suffix,
                        "executable": os.access(script_file, os.X_OK),
                        "size_kb": round(script_file.stat().st_size / 1024, 2),
                        "functions": [],
                    }

                    if "deploy" in script_file.name.lower():
                        script_analysis["deployment_scripts"].append(analysis)
                    elif "debug" in script_file.name.lower():
                        script_analysis["debug_scripts"].append(analysis)
                    else:
                        script_analysis["management_scripts"].append(analysis)

                    script_analysis["total_scripts"] += 1
                    if analysis["executable"]:
                        script_analysis["executable_scripts"] += 1

        self.results["scripts"] = script_analysis

    def analyze_documentation(self):
        """Analyze MCP-related documentation"""
        logger.info("📚 Analyzing documentation...")

        doc_analysis = {
            "mcp_docs": [],
            "deployment_docs": [],
            "total_docs": 0,
            "outdated_docs": [],
        }

        # Find documentation files
        for doc_file in self.root_dir.rglob("*.md"):
            if doc_file.is_file():
                content = doc_file.read_text(encoding="utf-8", errors="ignore").lower()
                if "mcp" in content:
                    doc_info = {
                        "file": str(doc_file.relative_to(self.root_dir)),
                        "size_kb": round(doc_file.stat().st_size / 1024, 2),
                        "last_modified": datetime.fromtimestamp(
                            doc_file.stat().st_mtime
                        ).isoformat(),
                        "contains_ports": bool(
                            any(
                                str(server["port"]) in content
                                for server in self.mcp_servers
                            )
                        ),
                    }

                    if "deploy" in doc_file.name.lower():
                        doc_analysis["deployment_docs"].append(doc_info)
                    else:
                        doc_analysis["mcp_docs"].append(doc_info)

                    doc_analysis["total_docs"] += 1

                    # Check if potentially outdated (> 7 days old)
                    last_mod = datetime.fromtimestamp(doc_file.stat().st_mtime)
                    days_old = (datetime.now() - last_mod).days
                    if days_old > 7:
                        doc_analysis["outdated_docs"].append(doc_info)

        self.results["documentation"] = doc_analysis

    def analyze_infrastructure(self):
        """Analyze infrastructure configuration"""
        logger.info("🏗️ Analyzing infrastructure...")

        infra_analysis = {
            "kubernetes_configs": [],
            "docker_configs": [],
            "deployment_configs": [],
            "total_configs": 0,
        }

        # Analyze Kubernetes configurations
        k8s_dir = self.root_dir / "kubernetes"
        if k8s_dir.exists():
            for k8s_file in k8s_dir.rglob("*.yaml"):
                if k8s_file.is_file():
                    content = k8s_file.read_text(encoding="utf-8", errors="ignore")
                    if "mcp" in content.lower():
                        infra_analysis["kubernetes_configs"].append(
                            {
                                "file": str(k8s_file.relative_to(self.root_dir)),
                                "size_kb": round(k8s_file.stat().st_size / 1024, 2),
                            }
                        )
                        infra_analysis["total_configs"] += 1

        # Analyze Docker configurations
        for docker_file in self.root_dir.rglob("docker-compose*.yml"):
            if docker_file.is_file():
                content = docker_file.read_text(encoding="utf-8", errors="ignore")
                if "mcp" in content.lower():
                    infra_analysis["docker_configs"].append(
                        {
                            "file": str(docker_file.relative_to(self.root_dir)),
                            "size_kb": round(docker_file.stat().st_size / 1024, 2),
                        }
                    )
                    infra_analysis["total_configs"] += 1

        self.results["infrastructure"] = infra_analysis

    async def analyze_docker_deployment(self):
        """Analyze Docker deployment status"""
        logger.info("🐳 Analyzing Docker deployment...")

        deployment_analysis = {
            "docker_available": False,
            "containers": [],
            "images": [],
            "networks": [],
            "volumes": [],
        }

        try:
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )
            deployment_analysis["docker_available"] = result.returncode == 0

            if deployment_analysis["docker_available"]:
                # Get running containers
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if line and "sophia" in line.lower():
                            parts = line.split("\t")
                            deployment_analysis["containers"].append(
                                {
                                    "name": parts[0] if len(parts) > 0 else "unknown",
                                    "status": parts[1] if len(parts) > 1 else "unknown",
                                    "ports": parts[2] if len(parts) > 2 else "none",
                                }
                            )

                # Get images
                result = subprocess.run(
                    [
                        "docker",
                        "images",
                        "--format",
                        "{{.Repository}}\t{{.Tag}}\t{{.Size}}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if line and "sophia" in line.lower():
                            parts = line.split("\t")
                            deployment_analysis["images"].append(
                                {
                                    "repository": parts[0]
                                    if len(parts) > 0
                                    else "unknown",
                                    "tag": parts[1] if len(parts) > 1 else "unknown",
                                    "size": parts[2] if len(parts) > 2 else "unknown",
                                }
                            )

        except subprocess.TimeoutExpired:
            deployment_analysis["error"] = "Docker command timeout"
        except FileNotFoundError:
            deployment_analysis["error"] = "Docker not installed"
        except Exception as e:
            deployment_analysis["error"] = str(e)

        self.results["deployment"] = deployment_analysis

    def generate_summary(self):
        """Generate comprehensive summary and recommendations"""
        logger.info("📊 Generating summary and recommendations...")

        # Calculate summary statistics
        total_servers_found = len(self.results.get("servers", {}))
        healthy_servers = self.results.get("summary", {}).get("healthy_servers", 0)
        total_configs = sum(
            len(configs)
            for configs in self.results.get("configurations", {}).values()
            if isinstance(configs, list)
        )

        summary = {
            "overall_health": "excellent"
            if healthy_servers / max(len(self.mcp_servers), 1) >= 0.8
            else "good"
            if healthy_servers / max(len(self.mcp_servers), 1) >= 0.6
            else "degraded"
            if healthy_servers / max(len(self.mcp_servers), 1) >= 0.3
            else "poor",
            "servers_analyzed": total_servers_found,
            "configurations_found": total_configs,
            "scripts_found": self.results.get("scripts", {}).get("total_scripts", 0),
            "documentation_files": self.results.get("documentation", {}).get(
                "total_docs", 0
            ),
            "infrastructure_configs": self.results.get("infrastructure", {}).get(
                "total_configs", 0
            ),
        }

        # Generate recommendations
        recommendations = []

        # Health-based recommendations
        if healthy_servers < len(self.mcp_servers):
            unhealthy_count = len(self.mcp_servers) - healthy_servers
            recommendations.append(
                {
                    "priority": "high",
                    "category": "health",
                    "title": f"Fix {unhealthy_count} unhealthy MCP servers",
                    "description": "Some MCP servers are not responding or have issues that need attention.",
                }
            )

        # Port conflict recommendations
        port_conflicts = self.results.get("configurations", {}).get(
            "port_conflicts", []
        )
        if port_conflicts:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "configuration",
                    "title": f"Resolve {len(port_conflicts)} port conflicts",
                    "description": "Multiple services are configured to use the same ports.",
                }
            )

        # Documentation recommendations
        outdated_docs = len(
            self.results.get("documentation", {}).get("outdated_docs", [])
        )
        if outdated_docs > 0:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "documentation",
                    "title": f"Update {outdated_docs} outdated documentation files",
                    "description": "Some documentation files haven't been updated recently and may be outdated.",
                }
            )

        # Infrastructure recommendations
        if not self.results.get("deployment", {}).get("docker_available", False):
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "infrastructure",
                    "title": "Docker not available for deployment testing",
                    "description": "Docker is not available, which limits deployment testing capabilities.",
                }
            )

        self.results["summary"].update(summary)
        self.results["recommendations"] = recommendations

    def save_results(self):
        """Save analysis results to file"""
        output_file = (
            f"comprehensive_mcp_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"💾 Results saved to {output_file}")

        # Also create a summary report
        self.create_summary_report(output_file.replace(".json", "_summary.md"))

    def create_summary_report(self, filename: str):
        """Create a human-readable summary report"""
        with open(filename, "w") as f:
            f.write("# Comprehensive MCP Debug Analysis Report\n\n")
            f.write(f"**Generated:** {self.results['timestamp']}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            summary = self.results.get("summary", {})
            f.write(
                f"- **Overall Health:** {summary.get('overall_health', 'unknown').upper()}\n"
            )
            f.write(
                f"- **Healthy Servers:** {summary.get('healthy_servers', 0)}/{summary.get('total_servers', 0)}\n"
            )
            f.write(f"- **Servers Analyzed:** {summary.get('servers_analyzed', 0)}\n")
            f.write(
                f"- **Configurations Found:** {summary.get('configurations_found', 0)}\n"
            )
            f.write(f"- **Scripts Found:** {summary.get('scripts_found', 0)}\n")
            f.write(
                f"- **Documentation Files:** {summary.get('documentation_files', 0)}\n\n"
            )

            # Recommendations
            f.write("## Priority Recommendations\n\n")
            recommendations = self.results.get("recommendations", [])
            for i, rec in enumerate(recommendations, 1):
                f.write(
                    f"{i}. **{rec.get('title', 'Unknown')}** ({rec.get('priority', 'unknown')} priority)\n"
                )
                f.write(f"   - Category: {rec.get('category', 'unknown')}\n")
                f.write(f"   - {rec.get('description', 'No description')}\n\n")

            # Server Health Details
            f.write("## Server Health Details\n\n")
            health_check = self.results.get("health_check", {})
            for server_name, health in health_check.items():
                status_emoji = {
                    "healthy": "✅",
                    "unhealthy": "❌",
                    "unreachable": "🔌",
                    "timeout": "⏰",
                    "error": "⚠️",
                }.get(health.get("status"), "❓")
                f.write(
                    f"- **{server_name}** (:{health.get('port', 'unknown')}) {status_emoji} {health.get('status', 'unknown')}\n"
                )
                if health.get("response_time_ms"):
                    f.write(f"  - Response time: {health.get('response_time_ms')}ms\n")
                if health.get("error"):
                    f.write(f"  - Error: {health.get('error')}\n")

            f.write("\n---\n\n")
            f.write(
                "*Full detailed results available in the corresponding JSON file.*\n"
            )


async def main():
    """Main execution function"""
    debugger = ComprehensiveMCPDebugger()
    results = await debugger.run_comprehensive_analysis()

    # Print summary
    print("\n" + "=" * 80)
    print("🔍 COMPREHENSIVE MCP DEBUG ANALYSIS COMPLETE")
    print("=" * 80)

    summary = results.get("summary", {})
    print(f"Overall Health: {summary.get('overall_health', 'unknown').upper()}")
    print(
        f"Healthy Servers: {summary.get('healthy_servers', 0)}/{summary.get('total_servers', 0)}"
    )
    print(f"Health Percentage: {summary.get('health_percentage', 0):.1f}%")

    recommendations = results.get("recommendations", [])
    if recommendations:
        print(f"\n⚠️  {len(recommendations)} recommendations generated")
        for rec in recommendations[:3]:  # Show top 3
            print(
                f"  • {rec.get('title', 'Unknown')} ({rec.get('priority', 'unknown')} priority)"
            )

    print("\n📊 Analysis Details:")
    print(f"  • Servers Analyzed: {summary.get('servers_analyzed', 0)}")
    print(f"  • Configurations: {summary.get('configurations_found', 0)}")
    print(f"  • Scripts: {summary.get('scripts_found', 0)}")
    print(f"  • Documentation: {summary.get('documentation_files', 0)}")

    print("\n✅ Complete results saved to JSON and markdown files")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
