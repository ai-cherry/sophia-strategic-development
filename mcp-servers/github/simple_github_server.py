#!/usr/bin/env python3
"""Simple GitHub MCP Server for repository integration."""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Basic FastAPI setup
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("FastAPI not available. Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleGitHubManager:
    """Simple GitHub integration without external API calls."""
    
    def __init__(self):
        self.mock_repos = [
            {"name": "sophia-main", "stars": 15, "language": "Python", "status": "active"},
            {"name": "ai-cherry-tools", "stars": 8, "language": "TypeScript", "status": "active"},
            {"name": "mcp-servers", "stars": 12, "language": "Python", "status": "archived"}
        ]
        
        self.mock_issues = [
            {"id": 1, "title": "Deploy MCP servers", "status": "closed", "priority": "high"},
            {"id": 2, "title": "Fix code quality issues", "status": "open", "priority": "medium"},
            {"id": 3, "title": "Add documentation", "status": "open", "priority": "low"}
        ]
        
        self.mock_prs = [
            {"id": 101, "title": "feat: Add AI Memory MCP server", "status": "merged", "author": "sophia-ai"},
            {"id": 102, "title": "fix: Resolve deployment issues", "status": "open", "author": "sophia-ai"}
        ]
    
    async def get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """Get repository information."""
        repo = next((r for r in self.mock_repos if r["name"] == repo_name), None)
        if not repo:
            return {"error": f"Repository {repo_name} not found"}
        
        return {
            "name": repo["name"],
            "stars": repo["stars"],
            "language": repo["language"],
            "status": repo["status"],
            "last_updated": datetime.now().isoformat(),
            "health_score": 85 if repo["status"] == "active" else 60
        }
    
    async def list_repositories(self) -> List[Dict[str, Any]]:
        """List all repositories."""
        return self.mock_repos
    
    async def get_issues(self, status: str = None) -> List[Dict[str, Any]]:
        """Get issues, optionally filtered by status."""
        if status:
            return [issue for issue in self.mock_issues if issue["status"] == status]
        return self.mock_issues
    
    async def create_issue(self, title: str, description: str, priority: str = "medium") -> Dict[str, Any]:
        """Create a new issue."""
        new_issue = {
            "id": len(self.mock_issues) + 1,
            "title": title,
            "description": description,
            "status": "open",
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "author": "sophia-ai"
        }
        
        self.mock_issues.append(new_issue)
        logger.info(f"Created issue: {title}")
        
        return new_issue
    
    async def get_pull_requests(self, status: str = None) -> List[Dict[str, Any]]:
        """Get pull requests."""
        if status:
            return [pr for pr in self.mock_prs if pr["status"] == status]
        return self.mock_prs
    
    async def get_repository_stats(self) -> Dict[str, Any]:
        """Get overall repository statistics."""
        active_repos = len([r for r in self.mock_repos if r["status"] == "active"])
        total_stars = sum(r["stars"] for r in self.mock_repos)
        open_issues = len([i for i in self.mock_issues if i["status"] == "open"])
        
        return {
            "total_repositories": len(self.mock_repos),
            "active_repositories": active_repos,
            "total_stars": total_stars,
            "open_issues": open_issues,
            "open_pull_requests": len([pr for pr in self.mock_prs if pr["status"] == "open"]),
            "languages": list(set(r["language"] for r in self.mock_repos))
        }

# Create FastAPI app
app = FastAPI(title="Simple GitHub MCP Server", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GitHub manager
github_manager = SimpleGitHubManager()

@app.get("/")
async def root():
    return {
        "name": "Simple GitHub MCP Server",
        "version": "1.0.0",
        "status": "running",
        "capabilities": ["repository_info", "issue_management", "pull_request_tracking"]
    }

@app.get("/health")
async def health():
    stats = await github_manager.get_repository_stats()
    return {
        "status": "healthy",
        "service": "github_mcp",
        "timestamp": datetime.now().isoformat(),
        "stats": stats
    }

@app.get("/api/v1/repositories")
async def list_repositories():
    """List all repositories."""
    try:
        repos = await github_manager.list_repositories()
        return {"repositories": repos, "count": len(repos)}
    except Exception as e:
        logger.error(f"Error listing repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/repositories/{repo_name}")
async def get_repository(repo_name: str):
    """Get specific repository information."""
    try:
        repo_info = await github_manager.get_repository_info(repo_name)
        return repo_info
    except Exception as e:
        logger.error(f"Error getting repository {repo_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/issues")
async def get_issues(status: str = None):
    """Get issues, optionally filtered by status."""
    try:
        issues = await github_manager.get_issues(status)
        return {"issues": issues, "count": len(issues)}
    except Exception as e:
        logger.error(f"Error getting issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/issues")
async def create_issue(data: Dict[str, Any]):
    """Create a new issue."""
    try:
        title = data.get("title")
        if not title:
            raise HTTPException(status_code=400, detail="Title is required")
        
        description = data.get("description", "")
        priority = data.get("priority", "medium")
        
        issue = await github_manager.create_issue(title, description, priority)
        return issue
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/pull-requests")
async def get_pull_requests(status: str = None):
    """Get pull requests."""
    try:
        prs = await github_manager.get_pull_requests(status)
        return {"pull_requests": prs, "count": len(prs)}
    except Exception as e:
        logger.error(f"Error getting pull requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats")
async def get_stats():
    """Get repository statistics."""
    try:
        return await github_manager.get_repository_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def main():
    """Run the server."""
    logger.info("Starting Simple GitHub MCP Server on port 9003...")
    
    try:
        # Try to load ESC config if available
        try:
            from backend.core.auto_esc_config import get_config_value
            github_token = get_config_value("github_token")
            if github_token:
                logger.info("✅ GitHub token available")
            else:
                logger.warning("GitHub token not found - using mock data")
        except Exception as e:
            logger.warning(f"Pulumi ESC not available: {e}")
        
        # Start server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=9003,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
