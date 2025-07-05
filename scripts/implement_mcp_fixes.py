#!/usr/bin/env python3
"""
MCP Server Comprehensive Fix Implementation
Implements all fixes identified in the remediation plan
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

import aiohttp

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MCPFixImplementation:
    """Implements all MCP server fixes"""

    def __init__(self):
        self.lambda_labs_host = "104.171.202.64"
        self.issues_found = []
        self.fixes_applied = []
        self.test_results = {}

    async def run_all_fixes(self):
        """Run all fix phases"""
        logger.info("🚀 Starting MCP Server Comprehensive Fix Implementation")

        # Phase 1: Critical Infrastructure Fixes
        await self.phase1_critical_fixes()

        # Phase 2: Configuration Consolidation
        await self.phase2_configuration_consolidation()

        # Phase 3: Lambda Labs Integration
        await self.phase3_lambda_labs_integration()

        # Phase 4: Test All Connections
        await self.phase4_test_connections()

        # Generate Report
        self.generate_report()

    async def phase1_critical_fixes(self):
        """Phase 1: Fix critical issues"""
        logger.info("\n📋 Phase 1: Critical Infrastructure Fixes")

        # 1.1 Check import errors
        logger.info("Checking for import errors...")
        import_issues = self.check_import_errors()
        if import_issues:
            self.issues_found.extend(import_issues)
            logger.warning(f"Found {len(import_issues)} import issues")
        else:
            logger.info("✅ No import errors found")

        # 1.2 Fix configuration files
        logger.info("Fixing configuration files...")
        config_fixes = await self.fix_configuration_files()
        self.fixes_applied.extend(config_fixes)

        # 1.3 Verify server files exist
        logger.info("Verifying server files...")
        missing_servers = self.verify_server_files()
        if missing_servers:
            self.issues_found.extend(missing_servers)
            logger.warning(f"Missing {len(missing_servers)} server files")

    def check_import_errors(self) -> list[str]:
        """Check for broken imports in all MCP servers"""
        issues = []
        mcp_dirs = [Path("backend/mcp_servers"), Path("mcp-servers")]

        for mcp_dir in mcp_dirs:
            if not mcp_dir.exists():
                continue

            for py_file in mcp_dir.rglob("*.py"):
                try:
                    with open(py_file) as f:
                        content = f.read()

                    # Check for duplicate imports
                    if (
                        "from backend.mcp_servers.base.standardized_mcp_server from"
                        in content
                    ):
                        issues.append(f"Duplicate import in {py_file}")

                    # Check for broken imports
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if "import" in line and line.count("from") > 1:
                            issues.append(f"Broken import in {py_file}:{i+1}")

                except Exception as e:
                    logger.error(f"Error checking {py_file}: {e}")

        return issues

    async def fix_configuration_files(self) -> list[str]:
        """Fix and consolidate configuration files"""
        fixes = []

        # Load unified config
        unified_config_path = Path("config/unified_mcp_config.json")
        if unified_config_path.exists():
            with open(unified_config_path) as f:
                unified_config = json.load(f)

            # Update cursor config to match
            cursor_config_path = Path("config/cursor_enhanced_mcp_config.json")
            if cursor_config_path.exists():
                with open(cursor_config_path) as f:
                    cursor_config = json.load(f)

                # Merge configurations
                updated_servers = {}
                for server_name, server_config in unified_config.get(
                    "mcpServers", {}
                ).items():
                    updated_servers[server_name] = {
                        "command": server_config.get("command", "python"),
                        "args": server_config.get("args", []),
                        "env": server_config.get("env", {}),
                        "port": server_config.get("port"),
                        "capabilities": server_config.get("capabilities", []),
                    }

                cursor_config["mcpServers"] = updated_servers
                cursor_config["lambda_labs"] = unified_config.get("lambda_labs", {})

                # Save updated cursor config
                with open(cursor_config_path, "w") as f:
                    json.dump(cursor_config, f, indent=2)

                fixes.append("Updated cursor_enhanced_mcp_config.json")

        return fixes

    def verify_server_files(self) -> list[str]:
        """Verify all server files exist"""
        missing = []

        servers = [
            "backend/mcp_servers/ai_memory/ai_memory_mcp_server.py",
            "backend/mcp_servers/snowflake_admin_mcp_server.py",
            "backend/mcp_servers/codacy/codacy_mcp_server.py",
            "mcp-servers/linear/linear_mcp_server.py",
            "mcp-servers/github/github_mcp_server.py",
            "mcp-servers/asana/asana_mcp_server.py",
            "mcp-servers/notion/enhanced_notion_mcp_server.py",
            "mcp-servers/ui_ux_agent/ui_ux_agent_mcp_server.py",
            "mcp-servers/portkey_admin/portkey_admin_mcp_server.py",
            "mcp-servers/lambda_labs_cli/lambda_labs_cli_mcp_server.py",
        ]

        for server_path in servers:
            if not Path(server_path).exists():
                missing.append(f"Missing server file: {server_path}")

        return missing

    async def phase2_configuration_consolidation(self):
        """Phase 2: Consolidate configurations"""
        logger.info("\n📋 Phase 2: Configuration Consolidation")

        # Create consolidated port mapping
        port_mapping = {
            "ai_memory": 9001,
            "snowflake_admin": 9020,
            "codacy": 3008,
            "linear": 9004,
            "github": 9103,
            "asana": 9100,
            "notion": 9005,
            "ui_ux_agent": 9002,
            "portkey_admin": 9013,
            "lambda_labs_cli": 9020,
            "snowflake_cortex": 9030,
        }

        # Update consolidated ports config
        consolidated_ports = {
            "version": "5.0",
            "description": "Consolidated MCP Server Port Configuration",
            "last_updated": "2025-01-03T20:00:00",
            "active_servers": port_mapping,
            "lambda_labs": {"host": self.lambda_labs_host, "docker_swarm": True},
        }

        ports_path = Path("config/consolidated_mcp_ports.json")
        with open(ports_path, "w") as f:
            json.dump(consolidated_ports, f, indent=2)

        self.fixes_applied.append("Created consolidated port configuration")

    async def phase3_lambda_labs_integration(self):
        """Phase 3: Lambda Labs Integration"""
        logger.info("\n📋 Phase 3: Lambda Labs Integration")

        # Create Lambda Labs Docker compose file
        docker_compose = {"version": "3.8", "services": {}}

        servers = [
            "ai_memory",
            "snowflake_admin",
            "codacy",
            "linear",
            "github",
            "asana",
            "notion",
            "ui_ux_agent",
            "portkey_admin",
            "lambda_labs_cli",
        ]

        for server in servers:
            docker_compose["services"][server] = {
                "image": f"sophia-ai/{server}:latest",
                "deploy": {
                    "replicas": 2,
                    "placement": {"constraints": ["node.labels.type == lambda-labs"]},
                },
                "environment": {
                    "LAMBDA_LABS_HOST": self.lambda_labs_host,
                    "ENVIRONMENT": "prod",
                    "PULUMI_ORG": "scoobyjava-org",
                },
                "networks": ["sophia-network"],
            }

        docker_compose["networks"] = {
            "sophia-network": {"driver": "overlay", "attachable": True}
        }

        # Save Docker compose file
        docker_path = Path("docker-compose.lambda.yml")
        with open(docker_path, "w") as f:
            import yaml

            yaml.dump(docker_compose, f, default_flow_style=False)

        self.fixes_applied.append("Created Lambda Labs Docker configuration")

    async def phase4_test_connections(self):
        """Phase 4: Test all connections"""
        logger.info("\n📋 Phase 4: Testing All Connections")

        # Test each server health endpoint
        servers_to_test = [
            ("AI Memory", "http://localhost:9001/health", 9001),
            ("Snowflake Admin", "http://localhost:9020/health", 9020),
            ("Codacy", "http://localhost:3008/health", 3008),
            ("Linear", "http://localhost:9004/health", 9004),
            ("GitHub", "http://localhost:9103/health", 9103),
            ("Asana", "http://localhost:9100/health", 9100),
            ("Notion", "http://localhost:9005/health", 9005),
            ("UI/UX Agent", "http://localhost:9002/health", 9002),
            ("Portkey Admin", "http://localhost:9013/health", 9013),
            ("Lambda Labs CLI", "http://localhost:9020/health", 9020),
        ]

        async with aiohttp.ClientSession() as session:
            for server_name, url, port in servers_to_test:
                try:
                    # First check if port is open
                    result = subprocess.run(
                        ["lsof", "-i", f":{port}"], capture_output=True, text=True
                    )

                    if result.returncode != 0:
                        self.test_results[server_name] = {
                            "status": "not_running",
                            "port": port,
                            "error": "Port not in use",
                        }
                        continue

                    # Test health endpoint
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.test_results[server_name] = {
                                "status": "healthy",
                                "port": port,
                                "response": data,
                            }
                        else:
                            self.test_results[server_name] = {
                                "status": "unhealthy",
                                "port": port,
                                "http_status": response.status,
                            }

                except asyncio.TimeoutError:
                    self.test_results[server_name] = {
                        "status": "timeout",
                        "port": port,
                        "error": "Connection timeout",
                    }
                except Exception as e:
                    self.test_results[server_name] = {
                        "status": "error",
                        "port": port,
                        "error": str(e),
                    }

    def generate_report(self):
        """Generate comprehensive report"""
        logger.info("\n📊 MCP Fix Implementation Report")
        logger.info("=" * 60)

        # Issues Found
        if self.issues_found:
            logger.warning(f"\n🚨 Issues Found: {len(self.issues_found)}")
            for issue in self.issues_found:
                logger.warning(f"  - {issue}")
        else:
            logger.info("\n✅ No critical issues found")

        # Fixes Applied
        logger.info(f"\n🔧 Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            logger.info(f"  ✓ {fix}")

        # Test Results
        logger.info("\n🧪 Server Health Test Results:")
        healthy_count = 0
        for server, result in self.test_results.items():
            status = result["status"]
            port = result["port"]

            if status == "healthy":
                logger.info(f"  ✅ {server} (port {port}): HEALTHY")
                healthy_count += 1
            elif status == "not_running":
                logger.warning(f"  ⚠️  {server} (port {port}): NOT RUNNING")
            elif status == "unhealthy":
                logger.error(
                    f"  ❌ {server} (port {port}): UNHEALTHY (HTTP {result.get('http_status')})"
                )
            else:
                logger.error(
                    f"  ❌ {server} (port {port}): {status.upper()} - {result.get('error', 'Unknown error')}"
                )

        # Summary
        total_servers = len(self.test_results)
        logger.info("\n📈 Summary:")
        logger.info(f"  - Total Servers: {total_servers}")
        logger.info(f"  - Healthy: {healthy_count}")
        logger.info(f"  - Issues: {total_servers - healthy_count}")
        logger.info(
            f"  - Success Rate: {(healthy_count/total_servers*100):.1f}%"
            if total_servers > 0
            else "N/A"
        )

        # Lambda Labs Status
        logger.info("\n🖥️  Lambda Labs Integration:")
        logger.info(f"  - Host: {self.lambda_labs_host}")
        logger.info("  - Docker Config: ✅ Created")
        logger.info("  - Port Mapping: ✅ Consolidated")

        # Next Steps
        logger.info("\n📋 Next Steps:")
        if total_servers - healthy_count > 0:
            logger.info("  1. Start non-running servers")
            logger.info("  2. Fix unhealthy server issues")
            logger.info("  3. Deploy to Lambda Labs")
        else:
            logger.info("  1. Deploy to Lambda Labs")
            logger.info("  2. Configure monitoring")
            logger.info("  3. Set up auto-scaling")


async def main():
    """Main execution"""
    fixer = MCPFixImplementation()
    await fixer.run_all_fixes()


if __name__ == "__main__":
    asyncio.run(main())
