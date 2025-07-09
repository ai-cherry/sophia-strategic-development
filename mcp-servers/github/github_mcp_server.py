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
from urllib.parse import urlparse

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from backend.core.auto_esc_config import get_config_value

    # Add base directory to path
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "base"))
    from unified_mcp_base import (
        MCPServerConfig,
        ServiceMCPServer,
    )

    from dataclasses import dataclass
    from github import Github

    # Use shared utilities instead of backend
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from shared.utils.custom_logger import setup_logger
except ImportError as e:
    print(f"Failed to import dependencies: {e}")
    sys.exit(1)

logger = setup_logger("mcp.github")


class GitHubMCPServer(ServiceMCPServer):
    """GitHub integration MCP server, refactored to use SimpleMCPServer."""

    def __init__(self):
        config = MCPServerConfig(name="github", port=9003, version="2.0.0")
        super().__init__(config)
        self.github_token: str | None = None
        self.base_url = "https://api.github.com"
        
        # Initialize server tools during construction
        self._setup_tools()

    async def server_specific_init(self) -> None:
        """Initialize GitHub-specific configuration."""
        self.github_token = os.getenv("GITHUB_TOKEN") or get_config_value(
            "github_token"
        )
        if not self.github_token:
            self.logger.warning("GitHub token not configured. Some tools may fail.")

    def _setup_tools(self):
        """Setup GitHub-specific tools and configuration."""
        # Register MCP tools
        self.mcp_tool(
            name="list_repos",
            description="List repositories for a GitHub user or organization",
            parameters={
                "owner": {
                    "type": "string",
                    "description": "GitHub owner name",
                    "required": True,
                }
            },
        )(self.list_repos)

        self.mcp_tool(
            name="get_repo",
            description="Get detailed information about a repository",
            parameters={
                "owner": {
                    "type": "string",
                    "description": "GitHub owner name",
                    "required": True,
                },
                "repo": {
                    "type": "string",
                    "description": "Repository name",
                    "required": True,
                },
            },
        )(self.get_repo)

        self.mcp_tool(
            name="list_issues",
            description="List issues for a repository",
            parameters={
                "owner": {
                    "type": "string",
                    "description": "GitHub owner name",
                    "required": True,
                },
                "repo": {
                    "type": "string",
                    "description": "Repository name",
                    "required": True,
                },
                "state": {
                    "type": "string",
                    "description": "Issue state (open, closed, all)",
                    "required": False,
                    "default": "open",
                },
            },
        )(self.list_issues)

        self.mcp_tool(
            name="create_issue",
            description="Create a new issue",
            parameters={
                "owner": {
                    "type": "string",
                    "description": "GitHub owner name",
                    "required": True,
                },
                "repo": {
                    "type": "string",
                    "description": "Repository name",
                    "required": True,
                },
                "title": {
                    "type": "string",
                    "description": "Issue title",
                    "required": True,
                },
                "body": {
                    "type": "string",
                    "description": "Issue body",
                    "required": True,
                },
                "labels": {
                    "type": "array",
                    "description": "Issue labels",
                    "required": False,
                },
            },
        )(self.create_issue)

    def initialize_server(self):
        """Initialize server-specific components - synchronous method from base class."""
        # Run async initialization in a sync context
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(self.server_specific_init())

    async def execute_mcp_tool(self, tool_name: str, params: dict[str, Any]) -> Any:
        """Execute GitHub MCP tools."""
        if tool_name == "list_repos":
            return await self.list_repos(params["owner"])
        elif tool_name == "get_repo":
            return await self.get_repo(params["owner"], params["repo"])
        elif tool_name == "list_issues":
            return await self.list_issues(
                params["owner"], params["repo"], params.get("state", "open")
            )
        elif tool_name == "create_issue":
            return await self.create_issue(
                params["owner"],
                params["repo"],
                params["title"],
                params["body"],
                params.get("labels"),
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def list_repos(self, owner: str) -> dict[str, Any]:
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
            self.logger.exception(f"Error listing repos: {e}")
            return {"status": "error", "message": str(e)}

    async def get_repo(self, owner: str, repo: str) -> dict[str, Any]:
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
            self.logger.exception(f"Error getting repo: {e}")
            return {"status": "error", "message": str(e)}

    async def list_issues(
        self, owner: str, repo: str, state: str = "open"
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
            self.logger.info(f"Listed {len(issues)} {state} issues for {owner}/{repo}")
            return {
                "status": "success",
                "repository": f"{owner}/{repo}",
                "state": state,
                "count": len(issues),
                "issues": issues,
            }
        except Exception as e:
            self.logger.exception(f"Error listing issues: {e}")
            return {"status": "error", "message": str(e)}

    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
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
            self.logger.exception(f"Error creating issue: {e}")
            return {"status": "error", "message": str(e)}

    async def check_server_health(self) -> bool:
        """Check GitHub API connectivity"""
        if not self.github_token:
            self.logger.warning("GitHub token not configured, health check degraded.")
            return False
        # In production, would make an actual API call to https://api.github.com/zen
        return True

    async def server_specific_cleanup(self) -> None:
        """Server-specific shutdown actions, if any."""
        self.logger.info("GitHub MCP server shutting down.")
        pass


async def main():
    """Main entry point"""
    server = GitHubMCPServer()
    server.run()


if __name__ == "__main__":
    import asyncio

    # Create and run the server directly
    server = GitHubMCPServer()
    server.run()


# --- Auto-inserted health endpoint ---
try:
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/health")
    async def health():
        return {"status": "ok"}

except ImportError:
    pass
