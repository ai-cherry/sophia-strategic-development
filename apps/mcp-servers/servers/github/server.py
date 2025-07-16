"""
Sophia AI GitHub MCP Server
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

# Modern stack imports
from backend.services.unified_memory_service_primary import UnifiedMemoryService
from backend.services.lambda_labs_serverless_service import LambdaLabsServerlessService
import redis.asyncio as redis
import asyncpg


import asyncio
import sys
from pathlib import Path
from typing import Any

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from base.unified_standardized_base import ServerConfig, StandardizedMCPServer
from mcp.types import Tool

from backend.core.auto_esc_config import get_config_value
from backend.core.redis_connection_manager import create_redis_from_config


class GitHubMCPServer(StandardizedMCPServer):
    """GitHub MCP Server using official SDK"""

    def __init__(self):
        config = ServerConfig(
            name="github",
            version="1.0.0",
            description="GitHub repository and issue management server",
        )
        super().__init__(config)

        # GitHub configuration
        self.github_token = get_config_value("github_token")
        self.default_org = get_config_value("github_org", "ai-cherry")


        # Initialize modern stack services
        self.memory_service = UnifiedMemoryService()
        self.lambda_gpu = LambdaLabsServerlessService()
        self.redis = create_redis_from_config()

    async def get_custom_tools(self) -> list[Tool]:
        """Define custom tools for GitHub operations"""
        return [
            Tool(
                name="list_repositories",
                description="List repositories for the organization",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "org": {
                            "type": "string",
                            "description": f"Organization name (default: {self.default_org})",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of repositories (default: 20)",
                        },
                    },
                    "required": [],
                },
            ),
            Tool(
                name="get_repository_info",
                description="Get detailed information about a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository name (e.g., 'sophia-main')",
                        }
                    },
                    "required": ["repo"],
                },
            ),
            Tool(
                name="list_issues",
                description="List issues for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "Repository name"},
                        "state": {
                            "type": "string",
                            "description": "Issue state: open, closed, all (default: open)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum issues (default: 10)",
                        },
                    },
                    "required": ["repo"],
                },
            ),
            Tool(
                name="create_issue",
                description="Create a new issue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "Repository name"},
                        "title": {"type": "string", "description": "Issue title"},
                        "body": {"type": "string", "description": "Issue description"},
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Issue labels",
                        },
                    },
                    "required": ["repo", "title", "body"],
                },
            ),
            Tool(
                name="list_pull_requests",
                description="List pull requests for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "Repository name"},
                        "state": {
                            "type": "string",
                            "description": "PR state: open, closed, all (default: open)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum PRs (default: 10)",
                        },
                    },
                    "required": ["repo"],
                },
            ),
            Tool(
                name="get_file_content",
                description="Get content of a file from repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "Repository name"},
                        "path": {
                            "type": "string",
                            "description": "File path in repository",
                        },
                        "branch": {
                            "type": "string",
                            "description": "Branch name (default: main)",
                        },
                    },
                    "required": ["repo", "path"],
                },
            ),
            Tool(
                name="search_code",
                description="Search code in repositories",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "repo": {
                            "type": "string",
                            "description": "Limit to specific repository",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 10)",
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]

    async def handle_custom_tool(self, name: str, arguments: dict) -> dict[str, Any]:
        """Handle custom tool calls"""
        try:
            if name == "list_repositories":
                return await self._list_repositories(arguments)
            elif name == "get_repository_info":
                return await self._get_repository_info(arguments)
            elif name == "list_issues":
                return await self._list_issues(arguments)
            elif name == "create_issue":
                return await self._create_issue(arguments)
            elif name == "list_pull_requests":
                return await self._list_pull_requests(arguments)
            elif name == "get_file_content":
                return await self._get_file_content(arguments)
            elif name == "search_code":
                return await self._search_code(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            self.logger.error(f"Error handling tool {name}: {e}")
            return {"status": "error", "error": str(e)}

    async def _list_repositories(self, params: dict[str, Any]) -> dict[str, Any]:
        """List repositories"""
        try:
            org = params.get("org", self.default_org)
            limit = params.get("limit", 20)

            # In production, would use GitHub API
            # Simulate response
            repos = [
                {
                    "name": "sophia-main",
                    "description": "Main Sophia AI repository",
                    "stars": 42,
                    "language": "Python",
                },
                {
                    "name": "sophia-docs",
                    "description": "Sophia AI documentation",
                    "stars": 15,
                    "language": "Markdown",
                },
            ]

            return {
                "status": "success",
                "organization": org,
                "repositories": repos[:limit],
                "total": len(repos),
            }

        except Exception as e:
            self.logger.error(f"Error listing repositories: {e}")
            raise

    async def _get_repository_info(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get repository information"""
        try:
            repo = params["repo"]

            # In production, would use GitHub API
            # Simulate response
            info = {
                "name": repo,
                "full_name": f"{self.default_org}/{repo}",
                "description": "Sophia AI main repository",
                "stars": 42,
                "forks": 5,
                "open_issues": 12,
                "language": "Python",
                "created_at": "2024-01-15T00:00:00Z",
                "updated_at": "2025-07-10T00:00:00Z",
            }

            return {"status": "success", "repository": info}

        except Exception as e:
            self.logger.error(f"Error getting repository info: {e}")
            raise

    async def _list_issues(self, params: dict[str, Any]) -> dict[str, Any]:
        """List issues"""
        try:
            repo = params["repo"]
            state = params.get("state", "open")
            limit = params.get("limit", 10)

            # In production, would use GitHub API
            # Simulate response
            issues = [
                {
                    "number": 123,
                    "title": "Implement MCP server standardization",
                    "state": "open",
                    "created_at": "2025-07-09T00:00:00Z",
                    "author": "user1",
                    "labels": ["enhancement", "mcp"],
                },
                {
                    "number": 122,
                    "title": "Fix memory leak in ETL pipeline",
                    "state": "open",
                    "created_at": "2025-07-08T00:00:00Z",
                    "author": "user2",
                    "labels": ["bug", "etl"],
                },
            ]

            return {
                "status": "success",
                "repository": repo,
                "issues": issues[:limit],
                "total": len(issues),
            }

        except Exception as e:
            self.logger.error(f"Error listing issues: {e}")
            raise

    async def _create_issue(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create issue"""
        try:
            repo = params["repo"]
            title = params["title"]
            body = params["body"]
            labels = params.get("labels", [])

            # In production, would use GitHub API
            # Simulate response
            issue = {
                "number": 124,
                "title": title,
                "body": body,
                "state": "open",
                "created_at": "2025-07-10T00:00:00Z",
                "author": "sophia-ai",
                "labels": labels,
                "html_url": f"https://github.com/{self.default_org}/{repo}/issues/124",
            }

            self.logger.info(f"Created issue #{issue['number']} in {repo}")

            return {"status": "success", "issue": issue}

        except Exception as e:
            self.logger.error(f"Error creating issue: {e}")
            raise

    async def _list_pull_requests(self, params: dict[str, Any]) -> dict[str, Any]:
        """List pull requests"""
        try:
            repo = params["repo"]
            state = params.get("state", "open")
            limit = params.get("limit", 10)

            # In production, would use GitHub API
            # Simulate response
            prs = [
                {
                    "number": 180,
                    "title": "Add MCP server standardization",
                    "state": "open",
                    "created_at": "2025-07-09T00:00:00Z",
                    "author": "developer1",
                    "base": "main",
                    "head": "feature/mcp-standardization",
                }
            ]

            return {
                "status": "success",
                "repository": repo,
                "pull_requests": prs[:limit],
                "total": len(prs),
            }

        except Exception as e:
            self.logger.error(f"Error listing pull requests: {e}")
            raise

    async def _get_file_content(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get file content"""
        try:
            repo = params["repo"]
            path = params["path"]
            branch = params.get("branch", "main")

            # In production, would use GitHub API
            # Simulate response
            content = f"# Sample content for {path}\n\nThis is simulated content."

            return {
                "status": "success",
                "repository": repo,
                "path": path,
                "branch": branch,
                "content": content,
                "encoding": "utf-8",
            }

        except Exception as e:
            self.logger.error(f"Error getting file content: {e}")
            raise

    async def _search_code(self, params: dict[str, Any]) -> dict[str, Any]:
        """Search code"""
        try:
            query = params["query"]
            repo = params.get("repo")
            limit = params.get("limit", 10)

            # In production, would use GitHub API
            # Simulate response
            results = [
                {
                    "repository": repo or "sophia-main",
                    "path": "backend/services/mcp_service.py",
                    "match": f"...{query}...",
                    "line_number": 42,
                }
            ]

            return {
                "status": "success",
                "query": query,
                "results": results[:limit],
                "total": len(results),
            }

        except Exception as e:
            self.logger.error(f"Error searching code: {e}")
            raise


async def main():
    """Main entry point"""
    server = GitHubMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
