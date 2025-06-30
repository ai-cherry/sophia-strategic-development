#!/usr/bin/env python3
"""
Tier 1 MCP Repository Implementation Script
Implements the highest-priority MCP repositories for immediate business value
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPRepositoryImplementer:
    """Implements Tier 1 MCP repositories for Sophia AI"""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.mcp_servers_dir = self.base_dir / "mcp-servers"
        self.external_dir = self.base_dir / "external"

        # Ensure directories exist
        self.mcp_servers_dir.mkdir(exist_ok=True)
        self.external_dir.mkdir(exist_ok=True)

    async def implement_tier1_repositories(self):
        """Implement all Tier 1 repositories"""
        logger.info("🚀 Starting Tier 1 MCP Repository Implementation")

        repositories = [
            {
                "name": "anthropic-mcp-python-sdk",
                "url": "https://github.com/modelcontextprotocol/python-sdk.git",
                "priority": "CRITICAL",
                "business_value": "Foundation for all MCP servers",
            },
            {
                "name": "anthropic-mcp-inspector",
                "url": "https://github.com/modelcontextprotocol/inspector.git",
                "priority": "HIGH",
                "business_value": "Development acceleration, QA automation",
            },
            {
                "name": "snowflake-mcp-server",
                "url": "https://github.com/isaacwasserman/mcp-snowflake-server.git",
                "priority": "CRITICAL",
                "business_value": "Data warehouse access for executive dashboards",
            },
            {
                "name": "hubspot-mcp-server",
                "url": "https://github.com/peakmojo/mcp-hubspot.git",
                "priority": "CRITICAL",
                "business_value": "Sales coaching, CRM analytics",
            },
            {
                "name": "slack-mcp-server",
                "url": "https://github.com/korotovsky/slack-mcp-server.git",
                "priority": "HIGH",
                "business_value": "Team communication intelligence",
            },
        ]

        results = []
        for repo in repositories:
            try:
                result = await self.clone_and_setup_repository(repo)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Failed to implement {repo['name']}: {e}")
                results.append(
                    {"name": repo["name"], "status": "failed", "error": str(e)}
                )

        # Generate implementation report
        await self.generate_implementation_report(results)

        return results

    async def clone_and_setup_repository(self, repo_info: dict):
        """Clone and set up a single repository"""
        repo_name = repo_info["name"]
        repo_url = repo_info["url"]

        logger.info(f"📦 Implementing {repo_name}...")

        # Determine target directory
        if "anthropic" in repo_name:
            target_dir = self.external_dir / repo_name
        else:
            target_dir = self.mcp_servers_dir / repo_name.replace("-mcp-server", "")

        # Clone repository
        if not target_dir.exists():
            logger.info(f"   Cloning {repo_url}")
            result = subprocess.run(
                ["git", "clone", repo_url, str(target_dir)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
        else:
            logger.info(f"   Repository already exists at {target_dir}")

        # Setup repository based on type
        setup_result = await self.setup_repository(target_dir, repo_info)

        return {
            "name": repo_name,
            "status": "success",
            "path": str(target_dir),
            "setup_result": setup_result,
        }

    async def setup_repository(self, repo_path: Path, repo_info: dict):
        """Set up repository for integration"""
        repo_name = repo_info["name"]

        logger.info(f"   Setting up {repo_name}")

        # Check for setup files
        setup_files = {
            "package.json": "Node.js project",
            "pyproject.toml": "Python project with pyproject",
            "requirements.txt": "Python project with requirements",
            "Dockerfile": "Containerized project",
            "setup.py": "Python setuptools project",
        }

        detected_type = None
        for file, project_type in setup_files.items():
            if (repo_path / file).exists():
                detected_type = project_type
                break

        if not detected_type:
            logger.warning(f"   No standard setup files found in {repo_name}")
            return {"type": "unknown", "status": "needs_manual_setup"}

        # Repository-specific setup
        if repo_name == "anthropic-mcp-python-sdk":
            return await self.setup_anthropic_sdk(repo_path)
        elif repo_name == "anthropic-mcp-inspector":
            return await self.setup_inspector(repo_path)
        elif repo_name == "snowflake-mcp-server":
            return await self.setup_snowflake_mcp(repo_path)
        elif repo_name == "hubspot-mcp-server":
            return await self.setup_hubspot_mcp(repo_path)
        elif repo_name == "slack-mcp-server":
            return await self.setup_slack_mcp(repo_path)

        return {"type": detected_type, "status": "basic_setup_complete"}

    async def setup_anthropic_sdk(self, repo_path: Path):
        """Set up Anthropic MCP Python SDK"""
        logger.info("   Installing Anthropic MCP SDK")

        # Install in development mode
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(repo_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info("   ✅ Anthropic MCP SDK installed successfully")
            return {"type": "python_sdk", "status": "installed", "editable": True}
        else:
            logger.error(f"   ❌ SDK installation failed: {result.stderr}")
            return {
                "type": "python_sdk",
                "status": "install_failed",
                "error": result.stderr,
            }

    async def setup_inspector(self, repo_path: Path):
        """Set up MCP Inspector"""
        logger.info("   Setting up MCP Inspector")

        # Check if it's a Node.js project
        if (repo_path / "package.json").exists():
            # Install dependencies
            result = subprocess.run(
                ["npm", "install"], cwd=repo_path, capture_output=True, text=True
            )

            if result.returncode == 0:
                logger.info("   ✅ MCP Inspector dependencies installed")
                return {"type": "nodejs", "status": "dependencies_installed"}
            else:
                logger.error(f"   ❌ npm install failed: {result.stderr}")
                return {
                    "type": "nodejs",
                    "status": "install_failed",
                    "error": result.stderr,
                }

        return {"type": "unknown", "status": "needs_manual_setup"}

    async def setup_snowflake_mcp(self, repo_path: Path):
        """Set up Snowflake MCP Server"""
        logger.info("   Setting up Snowflake MCP Server")

        # Create configuration file
        config_content = """
# Snowflake MCP Server Configuration
SNOWFLAKE_ACCOUNT=ZNB04675
SNOWFLAKE_USER=SCOOBYJAVA15
SNOWFLAKE_DATABASE=SOPHIA_AI
SNOWFLAKE_WAREHOUSE=SOPHIA_AI_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_SCHEMA=PROCESSED_AI

# Security note: SNOWFLAKE_PASSWORD should be loaded from Pulumi ESC
# This will be handled by our integration layer
"""

        config_file = repo_path / ".env.example"
        config_file.write_text(config_content)

        # Install Python dependencies if requirements.txt exists
        if (repo_path / "requirements.txt").exists():
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(repo_path / "requirements.txt"),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("   ✅ Snowflake MCP dependencies installed")
                return {
                    "type": "python_mcp",
                    "status": "configured",
                    "config_created": True,
                }
            else:
                logger.error(f"   ❌ Dependencies install failed: {result.stderr}")
                return {
                    "type": "python_mcp",
                    "status": "deps_failed",
                    "error": result.stderr,
                }

        return {"type": "python_mcp", "status": "config_created"}

    async def setup_hubspot_mcp(self, repo_path: Path):
        """Set up HubSpot MCP Server"""
        logger.info("   Setting up HubSpot MCP Server")

        # Create configuration
        config_content = """
# HubSpot MCP Server Configuration
HUBSPOT_API_KEY=your_hubspot_api_key_here
HUBSPOT_PORTAL_ID=your_portal_id_here

# Vector storage configuration
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX_NAME=hubspot-cache

# Cache settings
CACHE_TTL_SECONDS=3600
ENABLE_VECTOR_CACHE=true
"""

        config_file = repo_path / ".env.example"
        config_file.write_text(config_content)

        return {"type": "python_mcp", "status": "config_created"}

    async def setup_slack_mcp(self, repo_path: Path):
        """Set up Slack MCP Server"""
        logger.info("   Setting up Slack MCP Server")

        # Check if it's Node.js or Python
        if (repo_path / "package.json").exists():
            # Node.js setup
            result = subprocess.run(
                ["npm", "install"], cwd=repo_path, capture_output=True, text=True
            )

            if result.returncode == 0:
                logger.info("   ✅ Slack MCP dependencies installed")
                return {"type": "nodejs_mcp", "status": "dependencies_installed"}

        # Create basic configuration
        config_content = """
# Slack MCP Server Configuration
# Note: This server requires no admin approval
SLACK_USER_TOKEN=your_user_token_here
SLACK_WORKSPACE_URL=your_workspace.slack.com

# Transport configuration
MCP_TRANSPORT=stdio
MCP_SERVER_EVENTS=true
"""

        config_file = repo_path / ".env.example"
        config_file.write_text(config_content)

        return {"type": "nodejs_mcp", "status": "config_created"}

    async def generate_implementation_report(self, results: list):
        """Generate implementation report"""
        logger.info("📊 Generating implementation report")

        report_content = f"""# 🚀 TIER 1 MCP REPOSITORY IMPLEMENTATION REPORT

**Implementation Date:** {asyncio.get_event_loop().time()}
**Total Repositories:** {len(results)}

## 📊 Implementation Results

"""

        successful = 0
        failed = 0

        for result in results:
            status_emoji = "✅" if result["status"] == "success" else "❌"
            report_content += f"### {status_emoji} {result['name']}\n"
            report_content += f"- **Status:** {result['status']}\n"

            if result["status"] == "success":
                successful += 1
                report_content += f"- **Path:** {result['path']}\n"
                if "setup_result" in result:
                    setup = result["setup_result"]
                    report_content += f"- **Type:** {setup.get('type', 'unknown')}\n"
                    report_content += (
                        f"- **Setup Status:** {setup.get('status', 'unknown')}\n"
                    )
            else:
                failed += 1
                if "error" in result:
                    report_content += f"- **Error:** {result['error']}\n"

            report_content += "\n"

        report_content += f"""## 📈 Summary

- **Successful:** {successful}/{len(results)}
- **Failed:** {failed}/{len(results)}
- **Success Rate:** {(successful/len(results)*100):.1f}%

## 🎯 Next Steps

1. **Configure API Keys:** Add real API keys to .env files for each service
2. **Test Connections:** Verify each MCP server can connect to its respective service
3. **Integration Testing:** Test MCP servers with Anthropic Inspector
4. **Sophia Integration:** Integrate servers into Sophia AI orchestrator

## 🔧 Manual Setup Required

For any repositories marked as "needs_manual_setup", refer to their individual README files for specific setup instructions.
"""

        # Write report
        report_file = self.base_dir / "TIER1_MCP_IMPLEMENTATION_REPORT.md"
        report_file.write_text(report_content)

        logger.info(f"�� Implementation report written to {report_file}")
        logger.info(
            f"🎯 Summary: {successful}/{len(results)} repositories implemented successfully"
        )


async def main():
    """Main implementation function"""
    implementer = MCPRepositoryImplementer()

    try:
        results = await implementer.implement_tier1_repositories()

        successful = sum(1 for r in results if r["status"] == "success")
        total = len(results)

        if successful == total:
            logger.info("🎉 All Tier 1 repositories implemented successfully!")
        else:
            logger.warning(f"⚠️ {total - successful} repositories need manual attention")

        return successful == total

    except Exception as e:
        logger.error(f"❌ Implementation failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
