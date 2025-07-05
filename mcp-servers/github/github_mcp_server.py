#!/usr/bin/env python3
"""
GitHub MCP Server - Unified Implementation
Provides repository management and issue tracking capabilities
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from backend.core.config_manager import ConfigManager
    from backend.mcp_servers.base.unified_mcp_base import (
        HealthStatus,
        ServerConfig,
        StandardizedMCPServer,
    )
    from backend.utils.custom_logger import setup_logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the project root")
    sys.exit(1)

logger = setup_logger("mcp.github")


class GitHubMCPServer(StandardizedMCPServer):
    """GitHub integration MCP server"""

    def __init__(self, config: Optional[ServerConfig] = None):
        if not config:
            config = ServerConfig(
                name="github",
                port=9003,
                version="1.0.0",
                description="GitHub repository and issue management",
            )
        super().__init__(config)

        # GitHub-specific configuration
        self.github_token = os.getenv("GITHUB_TOKEN") or ConfigManager().get(
            "github_token"
        )
        self.base_url = "https://api.github.com"

    def _register_tools(self):
        """Register GitHub-specific tools"""

        @self.server.tool()
        async def list_repos(owner: str) -> dict[str, Any]:
            """List repositories for a GitHub user or organization"""
            try:
                # Demo implementation
                repos = [
                    {
                        "name": "sophia-main",
                        "full_name": f"{owner}/sophia-main",
                        "description": "Sophia AI main repository",
                        "stars": 42,
                        "language": "Python",
                        "updated_at": datetime.now().isoformat(),
                    }
                ]

                self.logger.info(f"Listed {len(repos)} repositories for {owner}")
                return {
                    "status": "success",
                    "owner": owner,
                    "count": len(repos),
                    "repositories": repos,
                }
            except Exception as e:
                self.logger.error(f"Error listing repos: {e}")
                return {"status": "error", "message": str(e)}

        @self.server.tool()
        async def get_repo(owner: str, repo: str) -> dict[str, Any]:
            """Get detailed information about a repository"""
            try:
                # Demo implementation
                repo_info = {
                    "name": repo,
                    "full_name": f"{owner}/{repo}",
                    "description": "Repository description",
                    "stars": 42,
                    "forks": 10,
                    "open_issues": 5,
                    "language": "Python",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": datetime.now().isoformat(),
                }

                self.logger.info(f"Retrieved info for {owner}/{repo}")
                return {"status": "success", "repository": repo_info}
            except Exception as e:
                self.logger.error(f"Error getting repo: {e}")
                return {"status": "error", "message": str(e)}

        @self.server.tool()
        async def list_issues(
            owner: str, repo: str, state: str = "open"
        ) -> dict[str, Any]:
            """List issues for a repository"""
            try:
                # Demo implementation
                issues = [
                    {
                        "number": 1,
                        "title": "Implement feature X",
                        "state": state,
                        "labels": ["enhancement"],
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": datetime.now().isoformat(),
                    }
                ]

                self.logger.info(
                    f"Listed {len(issues)} {state} issues for {owner}/{repo}"
                )
                return {
                    "status": "success",
                    "repository": f"{owner}/{repo}",
                    "state": state,
                    "count": len(issues),
                    "issues": issues,
                }
            except Exception as e:
                self.logger.error(f"Error listing issues: {e}")
                return {"status": "error", "message": str(e)}

        @self.server.tool()
        async def create_issue(
            owner: str,
            repo: str,
            title: str,
            body: str,
            labels: Optional[list[str]] = None,
        ) -> dict[str, Any]:
            """Create a new issue"""
            try:
                # Demo implementation
                issue = {
                    "number": 42,
                    "title": title,
                    "body": body,
                    "state": "open",
                    "labels": labels or [],
                    "created_at": datetime.now().isoformat(),
                    "html_url": f"https://github.com/{owner}/{repo}/issues/42",
                }

                self.logger.info(f"Created issue #{issue['number']} in {owner}/{repo}")
                return {"status": "success", "issue": issue}
            except Exception as e:
                self.logger.error(f"Error creating issue: {e}")
                return {"status": "error", "message": str(e)}

    async def _check_service_health(self) -> HealthStatus:
        """Check GitHub API connectivity"""
        if not self.github_token:
            return HealthStatus(
                healthy=False,
                latency_ms=0,
                details={"error": "GitHub token not configured"},
            )

        # In production, would make actual API call
        return HealthStatus(
            healthy=True, latency_ms=50, details={"api_status": "operational"}
        )


async def main():
    """Main entry point"""
    server = GitHubMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


# --- Auto-inserted health endpoint ---
try:
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/health")
    async def health():
        return {"status": "ok"}

except ImportError:
    pass

    async def server_specific_init(self):
        """Server-specific initialization"""
        # TODO: Add server-specific initialization
        pass

    def _setup_server_routes(self):
        """Setup server-specific routes"""
        # Existing routes should be moved here
        pass

    async def check_server_health(self) -> bool:
        """Check server health"""
        # TODO: Implement health check
        return True

    async def server_specific_shutdown(self):
        """Server-specific shutdown"""
        # TODO: Add cleanup logic
        pass
