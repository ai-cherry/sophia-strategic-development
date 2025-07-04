#!/usr/bin/env python3
"""
Simple GitHub MCP Server
Provides repository management functionality
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleGitHubServer:
    def __init__(self):
        self.app = FastAPI(title="Simple GitHub MCP Server", version="1.0.0")
        self.access_token = os.getenv("GITHUB_TOKEN", "")
        self.setup_routes()
        self.setup_middleware()

    def setup_middleware(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Setup API routes"""

        @self.app.get("/")
        async def root():
            return {
                "name": "Simple GitHub MCP Server",
                "version": "1.0.0",
                "status": "running",
                "capabilities": ["get_repository", "get_pull_requests", "get_issues"],
                "has_access_token": bool(self.access_token),
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "has_access_token": bool(self.access_token),
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.post("/api/get_repository")
        async def get_repository(request: dict[str, Any]):
            """Get GitHub repository information"""
            try:
                owner = request.get("owner", "")
                repo = request.get("repo", "")

                if not owner or not repo:
                    raise HTTPException(
                        status_code=400, detail="Owner and repo are required"
                    )

                # Mock repository data for demo
                repository_info = {
                    "name": repo,
                    "full_name": f"{owner}/{repo}",
                    "owner": {"login": owner, "type": "Organization"},
                    "description": "Sophia AI - AI assistant orchestrator for Pay Ready",
                    "private": True,
                    "html_url": f"https://github.com/{owner}/{repo}",
                    "clone_url": f"https://github.com/{owner}/{repo}.git",
                    "ssh_url": f"git@github.com:{owner}/{repo}.git",
                    "stargazers_count": 42,
                    "watchers_count": 15,
                    "forks_count": 5,
                    "open_issues_count": 8,
                    "default_branch": "main",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": datetime.now().isoformat(),
                    "pushed_at": datetime.now().isoformat(),
                    "language": "Python",
                    "languages": {
                        "Python": 75.2,
                        "TypeScript": 18.5,
                        "JavaScript": 4.1,
                        "Shell": 1.8,
                        "Dockerfile": 0.4,
                    },
                    "topics": [
                        "ai",
                        "mcp",
                        "orchestrator",
                        "business-intelligence",
                        "automation",
                    ],
                    "license": {"name": "MIT License", "spdx_id": "MIT"},
                }

                logger.info(f"Retrieved repository info for {owner}/{repo}")

                return {
                    "success": True,
                    "repository": repository_info,
                    "has_access_token": bool(self.access_token),
                }

            except Exception as e:
                logger.error(f"Error getting repository: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/get_pull_requests")
        async def get_pull_requests(request: dict[str, Any]):
            """Get GitHub pull requests"""
            try:
                owner = request.get("owner", "")
                repo = request.get("repo", "")
                state = request.get("state", "open")

                if not owner or not repo:
                    raise HTTPException(
                        status_code=400, detail="Owner and repo are required"
                    )

                # Mock pull request data
                pull_requests = [
                    {
                        "number": 47,
                        "title": "🔒 Complete Security Vulnerability Resolution",
                        "body": "Resolved all 264 GitHub security vulnerabilities including critical and high-severity issues.",
                        "state": "open",
                        "user": {
                            "login": "ai-developer",
                            "avatar_url": "https://github.com/identicons/ai-developer.png",
                        },
                        "created_at": "2025-07-02T18:00:00Z",
                        "updated_at": datetime.now().isoformat(),
                        "head": {"ref": "security-fixes", "sha": "3162c507"},
                        "base": {"ref": "main", "sha": "236172b5"},
                        "mergeable": True,
                        "mergeable_state": "clean",
                        "draft": False,
                        "labels": [
                            {"name": "security", "color": "d73a4a"},
                            {"name": "critical", "color": "b60205"},
                        ],
                        "requested_reviewers": [{"login": "security-team"}],
                        "assignees": [{"login": "ai-developer"}],
                    },
                    {
                        "number": 46,
                        "title": "📖 Comprehensive Coding MCP Servers Documentation",
                        "body": "Added comprehensive documentation and testing framework for all coding-focused MCP servers.",
                        "state": "merged",
                        "user": {
                            "login": "ai-developer",
                            "avatar_url": "https://github.com/identicons/ai-developer.png",
                        },
                        "created_at": "2025-07-02T17:30:00Z",
                        "updated_at": "2025-07-02T17:45:00Z",
                        "merged_at": "2025-07-02T17:45:00Z",
                        "head": {"ref": "mcp-documentation", "sha": "236172b5"},
                        "base": {"ref": "main", "sha": "3efc1b05"},
                        "mergeable": None,
                        "mergeable_state": "clean",
                        "draft": False,
                        "labels": [
                            {"name": "documentation", "color": "0075ca"},
                            {"name": "enhancement", "color": "a2eeef"},
                        ],
                    },
                    {
                        "number": 45,
                        "title": "🚀 Comprehensive Remodel Complete",
                        "body": "Research-validated architecture transformation with 39× performance improvements.",
                        "state": "merged",
                        "user": {
                            "login": "ai-developer",
                            "avatar_url": "https://github.com/identicons/ai-developer.png",
                        },
                        "created_at": "2025-07-02T12:00:00Z",
                        "updated_at": "2025-07-02T15:00:00Z",
                        "merged_at": "2025-07-02T15:00:00Z",
                        "head": {"ref": "comprehensive-remodel", "sha": "7f51015d"},
                        "base": {"ref": "main", "sha": "adaac35d"},
                        "labels": [
                            {"name": "infrastructure", "color": "1d76db"},
                            {"name": "performance", "color": "fbca04"},
                        ],
                    },
                ]

                # Filter by state
                filtered_prs = [pr for pr in pull_requests if pr["state"] == state]

                logger.info(
                    f"Retrieved {len(filtered_prs)} pull requests for {owner}/{repo} (state: {state})"
                )

                return {
                    "success": True,
                    "pull_requests": filtered_prs,
                    "total_count": len(filtered_prs),
                    "state": state,
                }

            except Exception as e:
                logger.error(f"Error getting pull requests: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/get_issues")
        async def get_issues(request: dict[str, Any]):
            """Get GitHub issues"""
            try:
                owner = request.get("owner", "")
                repo = request.get("repo", "")
                state = request.get("state", "open")
                labels = request.get("labels", [])

                if not owner or not repo:
                    raise HTTPException(
                        status_code=400, detail="Owner and repo are required"
                    )

                # Mock issues data
                issues = [
                    {
                        "number": 15,
                        "title": "Enhance MCP server auto-discovery",
                        "body": "Implement automatic discovery and registration of new MCP servers in the ecosystem.",
                        "state": "open",
                        "user": {
                            "login": "product-manager",
                            "avatar_url": "https://github.com/identicons/product-manager.png",
                        },
                        "labels": [
                            {"name": "enhancement", "color": "a2eeef"},
                            {"name": "mcp", "color": "7057ff"},
                        ],
                        "assignees": [{"login": "ai-developer"}],
                        "milestone": {"title": "Q3 2025 Features", "number": 3},
                        "created_at": "2025-07-01T14:00:00Z",
                        "updated_at": datetime.now().isoformat(),
                        "comments": 3,
                    },
                    {
                        "number": 14,
                        "title": "Add real-time collaboration features",
                        "body": "Enable real-time collaboration between multiple developers using the AI Memory system.",
                        "state": "open",
                        "user": {
                            "login": "tech-lead",
                            "avatar_url": "https://github.com/identicons/tech-lead.png",
                        },
                        "labels": [
                            {"name": "feature", "color": "0052cc"},
                            {"name": "collaboration", "color": "5319e7"},
                        ],
                        "assignees": [],
                        "created_at": "2025-06-30T16:30:00Z",
                        "updated_at": "2025-07-02T10:15:00Z",
                        "comments": 7,
                    },
                    {
                        "number": 13,
                        "title": "Improve Codacy integration performance",
                        "body": "Optimize the Codacy MCP server for faster code analysis and reduced memory usage.",
                        "state": "closed",
                        "user": {
                            "login": "performance-engineer",
                            "avatar_url": "https://github.com/identicons/performance-engineer.png",
                        },
                        "labels": [
                            {"name": "performance", "color": "fbca04"},
                            {"name": "codacy", "color": "d4c5f9"},
                        ],
                        "assignees": [{"login": "ai-developer"}],
                        "closed_at": "2025-07-02T16:00:00Z",
                        "created_at": "2025-06-28T09:00:00Z",
                        "updated_at": "2025-07-02T16:00:00Z",
                        "comments": 12,
                    },
                ]

                # Filter by state and labels
                filtered_issues = [issue for issue in issues if issue["state"] == state]
                if labels:
                    filtered_issues = [
                        issue
                        for issue in filtered_issues
                        if any(label["name"] in labels for label in issue["labels"])
                    ]

                logger.info(
                    f"Retrieved {len(filtered_issues)} issues for {owner}/{repo}"
                )

                return {
                    "success": True,
                    "issues": filtered_issues,
                    "total_count": len(filtered_issues),
                    "state": state,
                    "labels": labels,
                }

            except Exception as e:
                logger.error(f"Error getting issues: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/get_commits")
        async def get_commits(request: dict[str, Any]):
            """Get recent commits"""
            try:
                owner = request.get("owner", "")
                repo = request.get("repo", "")
                branch = request.get("branch", "main")
                limit = request.get("limit", 10)

                # Mock commits data
                commits = [
                    {
                        "sha": "236172b5",
                        "commit": {
                            "author": {
                                "name": "AI Developer",
                                "email": "ai@sophia.dev",
                                "date": datetime.now().isoformat(),
                            },
                            "message": "Add comprehensive coding MCP servers documentation and testing framework",
                            "tree": {"sha": "abc123"},
                            "comment_count": 0,
                        },
                        "author": {
                            "login": "ai-developer",
                            "avatar_url": "https://github.com/identicons/ai-developer.png",
                        },
                        "html_url": f"https://github.com/{owner}/{repo}/commit/236172b5",
                    },
                    {
                        "sha": "3162c507",
                        "commit": {
                            "author": {
                                "name": "AI Developer",
                                "email": "ai@sophia.dev",
                                "date": "2025-07-02T18:00:00Z",
                            },
                            "message": "🔒 COMPLETE SECURITY VULNERABILITY RESOLUTION",
                            "tree": {"sha": "def456"},
                            "comment_count": 2,
                        },
                        "author": {
                            "login": "ai-developer",
                            "avatar_url": "https://github.com/identicons/ai-developer.png",
                        },
                        "html_url": f"https://github.com/{owner}/{repo}/commit/3162c507",
                    },
                ]

                result_commits = commits[:limit]

                return {
                    "success": True,
                    "commits": result_commits,
                    "branch": branch,
                    "total_count": len(result_commits),
                }

            except Exception as e:
                logger.error(f"Error getting commits: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def start_server(self, port: int = 9003):
        """Start the GitHub MCP server"""
        logger.info(f"📁 Starting Simple GitHub MCP Server on port {port}")

        config = uvicorn.Config(
            app=self.app, host="0.0.0.0", port=port, log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


def main():
    """Main function to run the server"""
    server = SimpleGitHubServer()

    try:
        asyncio.run(server.start_server(port=9003))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == "__main__":
    main()
