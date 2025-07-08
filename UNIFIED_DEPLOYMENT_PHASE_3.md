# PHASE 3: V2 MCP SERVER DEPLOYMENT (6 Hours)

## Overview
Deploy the 9 V2 MCP servers to Lambda Labs, establishing the enhanced AI capabilities for the platform.

## Prerequisites from Phase 2
- [ ] Backend deployed and healthy at api.sophia-intel.ai
- [ ] WebSocket connections working
- [ ] Docker infrastructure ready on Lambda Labs

## 3.1 Implement Priority MCP Servers (2 hours)

### A. GitHub V2 Implementation (Port 9006)
```python
# infrastructure/mcp_servers/github_v2/handlers/main_handler.py
import asyncio
import logging
from typing import Any, Dict, List, Optional
from github import Github
from github.GithubException import GithubException

from ..config import settings
from ..models.data_models import (
    RepoRequest, RepoResponse, IssueRequest, PRRequest,
    CommitRequest, WorkflowRequest, SearchRequest
)

logger = logging.getLogger(__name__)

class GitHubHandler:
    """Enhanced GitHub operations handler for live coding assistance"""

    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN)
        self._cache = {}

    async def get_repository(self, request: RepoRequest) -> RepoResponse:
        """Get repository information with caching"""
        cache_key = f"repo:{request.owner}/{request.repo}"

        if cache_key in self._cache:
            return RepoResponse(**self._cache[cache_key])

        try:
            repo = await asyncio.to_thread(
                self.github.get_repo, f"{request.owner}/{request.repo}"
            )

            response_data = {
                "success": True,
                "data": {
                    "name": repo.name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "topics": repo.get_topics(),
                    "default_branch": repo.default_branch,
                    "open_issues": repo.open_issues_count,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat()
                }
            }

            self._cache[cache_key] = response_data
            return RepoResponse(**response_data)

        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return RepoResponse(
                success=False,
                error=f"GitHub API error: {e.status} - {e.data}"
            )

    async def search_code(self, request: SearchRequest) -> Dict[str, Any]:
        """Search code across repositories"""
        try:
            # Build search query
            query_parts = [request.query]
            if request.language:
                query_parts.append(f"language:{request.language}")
            if request.repo:
                query_parts.append(f"repo:{request.repo}")

            query = " ".join(query_parts)

            # Perform search
            results = await asyncio.to_thread(
                self.github.search_code, query
            )

            # Process results
            items = []
            for item in results[:request.limit]:
                items.append({
                    "repository": item.repository.full_name,
                    "path": item.path,
                    "url": item.html_url,
                    "score": item.score,
                    "sha": item.sha
                })

            return {
                "success": True,
                "total_count": results.totalCount,
                "items": items
            }

        except Exception as e:
            logger.error(f"Code search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_file_content(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """Get file content from repository"""
        try:
            repo_obj = await asyncio.to_thread(
                self.github.get_repo, f"{owner}/{repo}"
            )

            content = await asyncio.to_thread(
                repo_obj.get_contents, path
            )

            if content.type == "file":
                return {
                    "success": True,
                    "content": content.decoded_content.decode('utf-8'),
                    "sha": content.sha,
                    "size": content.size,
                    "encoding": content.encoding
                }
            else:
                return {
                    "success": False,
                    "error": "Path is not a file"
                }

        except Exception as e:
            logger.error(f"Get file content error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
```

### B. Perplexity V2 Implementation (Port 9008)
```python
# infrastructure/mcp_servers/perplexity_v2/handlers/main_handler.py
import asyncio
import logging
from typing import Any, Dict, List, Optional
import httpx
from datetime import datetime, timedelta

from ..config import settings
from ..models.data_models import (
    SearchRequest, SearchResponse, DocumentRequest,
    CodeExampleRequest, APIReferenceRequest
)

logger = logging.getLogger(__name__)

class PerplexityHandler:
    """Real-time documentation and code search handler"""

    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        self._cache = {}
        self._cache_ttl = timedelta(minutes=30)

    async def search_documentation(self, request: SearchRequest) -> SearchResponse:
        """Search technical documentation with caching"""
        cache_key = f"doc:{request.query}:{request.context}"

        # Check cache
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if cached['expires'] > datetime.utcnow():
                return SearchResponse(**cached['data'])

        try:
            # Enhance query for technical documentation
            enhanced_query = f"{request.query} site:docs.python.org OR site:developer.mozilla.org OR site:docs.github.com"

            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "pplx-70b-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a technical documentation expert. Provide accurate, concise information with sources."
                        },
                        {
                            "role": "user",
                            "content": enhanced_query
                        }
                    ],
                    "temperature": 0.1,
                    "return_citations": True
                }
            )

            response.raise_for_status()
            data = response.json()

            # Process response
            result = {
                "success": True,
                "content": data['choices'][0]['message']['content'],
                "citations": data.get('citations', []),
                "sources": self._extract_sources(data),
                "timestamp": datetime.utcnow().isoformat()
            }

            # Cache result
            self._cache[cache_key] = {
                'data': result,
                'expires': datetime.utcnow() + self._cache_ttl
            }

            return SearchResponse(**result)

        except Exception as e:
            logger.error(f"Documentation search error: {e}")
            return SearchResponse(
                success=False,
                error=str(e)
            )

    async def find_code_examples(self, request: CodeExampleRequest) -> Dict[str, Any]:
        """Find relevant code examples"""
        try:
            # Build targeted query
            query = f"{request.topic} code example {request.language}"
            if request.framework:
                query += f" {request.framework}"

            query += " site:github.com OR site:stackoverflow.com"

            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "pplx-70b-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"Find working {request.language} code examples. Include only tested, production-ready code."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            )

            response.raise_for_status()
            data = response.json()

            # Extract code blocks
            content = data['choices'][0]['message']['content']
            code_blocks = self._extract_code_blocks(content)

            return {
                "success": True,
                "examples": code_blocks,
                "explanation": content,
                "sources": self._extract_sources(data)
            }

        except Exception as e:
            logger.error(f"Code example search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown content"""
        import re

        blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            language = match.group(1) or 'plaintext'
            code = match.group(2).strip()
            blocks.append({
                "language": language,
                "code": code
            })

        return blocks

    def _extract_sources(self, response_data: dict) -> List[str]:
        """Extract source URLs from response"""
        sources = []
        if 'citations' in response_data:
            for citation in response_data['citations']:
                if 'url' in citation:
                    sources.append(citation['url'])
        return sources
```

### C. Slack V2 Implementation (Port 9007)
```python
# infrastructure/mcp_servers/slack_v2/handlers/main_handler.py
import asyncio
import logging
from typing import Any, Dict, List, Optional
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta

from ..config import settings
from ..models.data_models import (
    MessageRequest, MessageResponse, ChannelRequest,
    ThreadRequest, FileRequest, UserRequest
)

logger = logging.getLogger(__name__)

class SlackHandler:
    """Enhanced Slack operations for team collaboration"""

    def __init__(self):
        self.client = AsyncWebClient(token=settings.SLACK_BOT_TOKEN)
        self.user_cache = {}
        self.channel_cache = {}

    async def send_message(self, request: MessageRequest) -> MessageResponse:
        """Send message with formatting and attachments"""
        try:
            # Resolve channel name to ID if needed
            channel_id = await self._resolve_channel(request.channel)

            # Build message
            kwargs = {
                "channel": channel_id,
                "text": request.text
            }

            # Add blocks for rich formatting
            if request.blocks:
                kwargs["blocks"] = request.blocks

            # Add thread support
            if request.thread_ts:
                kwargs["thread_ts"] = request.thread_ts

            # Send message
            response = await self.client.chat_postMessage(**kwargs)

            return MessageResponse(
                success=True,
                data={
                    "ts": response["ts"],
                    "channel": response["channel"],
                    "message": response["message"]
                }
            )

        except SlackApiError as e:
            logger.error(f"Slack API error: {e}")
            return MessageResponse(
                success=False,
                error=f"Slack error: {e.response['error']}"
            )

    async def search_messages(self, query: str, channel: Optional[str] = None) -> Dict[str, Any]:
        """Search messages across workspace"""
        try:
            search_query = query
            if channel:
                channel_id = await self._resolve_channel(channel)
                search_query = f"in:{channel_id} {query}"

            response = await self.client.search_messages(
                query=search_query,
                sort="timestamp",
                sort_dir="desc",
                count=20
            )

            # Process results
            messages = []
            for match in response["messages"]["matches"]:
                messages.append({
                    "text": match["text"],
                    "user": await self._get_user_name(match["user"]),
                    "channel": match["channel"]["name"],
                    "timestamp": match["ts"],
                    "permalink": match["permalink"]
                })

            return {
                "success": True,
                "total": response["messages"]["total"],
                "messages": messages
            }

        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_code_snippet(self, title: str, content: str,
                                 language: str = "python",
                                 channel: Optional[str] = None) -> Dict[str, Any]:
        """Share code snippet with syntax highlighting"""
        try:
            # Prepare file upload
            kwargs = {
                "content": content,
                "filename": f"{title}.{self._get_extension(language)}",
                "title": title,
                "filetype": language
            }

            if channel:
                kwargs["channels"] = await self._resolve_channel(channel)

            response = await self.client.files_upload_v2(**kwargs)

            return {
                "success": True,
                "file": {
                    "id": response["file"]["id"],
                    "url": response["file"]["url_private"],
                    "permalink": response["file"]["permalink"]
                }
            }

        except Exception as e:
            logger.error(f"File upload error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _resolve_channel(self, channel: str) -> str:
        """Resolve channel name to ID"""
        if channel.startswith('C'):  # Already an ID
            return channel

        if channel in self.channel_cache:
            return self.channel_cache[channel]

        # Fetch channel list
        response = await self.client.conversations_list(
            types="public_channel,private_channel"
        )

        for ch in response["channels"]:
            self.channel_cache[ch["name"]] = ch["id"]
            if ch["name"] == channel.lstrip('#'):
                return ch["id"]

        raise ValueError(f"Channel {channel} not found")

    async def _get_user_name(self, user_id: str) -> str:
        """Get user display name with caching"""
        if user_id in self.user_cache:
            return self.user_cache[user_id]

        try:
            response = await self.client.users_info(user=user_id)
            name = response["user"]["profile"]["display_name"] or response["user"]["name"]
            self.user_cache[user_id] = name
            return name
        except:
            return user_id

    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "rust": "rs",
            "cpp": "cpp",
            "c": "c"
        }
        return extensions.get(language, "txt")
```

## 3.2 Build and Deploy MCP Servers (2 hours)

### A. Build Script for All V2 Servers
```bash
#!/bin/bash
# scripts/build-v2-mcp-servers.sh

set -e

REGISTRY="scoobyjava15"
SERVERS=(
    "ai_memory_v2:9000"
    "snowflake_v2:9001"
    "linear_v2:9002"
    "notion_v2:9003"
    "asana_v2:9004"
    "codacy_v2:9005"
    "github_v2:9006"
    "slack_v2:9007"
    "perplexity_v2:9008"
)

echo "🏗️ Building V2 MCP Servers"
echo "========================="

for server_port in "${SERVERS[@]}"; do
    IFS=':' read -r server port <<< "$server_port"
    server_name=${server//_/-}

    echo ""
    echo "📦 Building $server (port $port)..."

    # Build image
    docker build \
        -t ${REGISTRY}/sophia-${server_name}:latest \
        -f infrastructure/mcp_servers/${server}/Dockerfile \
        --build-arg PORT=${port} \
        infrastructure/mcp_servers/${server}/

    if [ $? -eq 0 ]; then
        echo "✅ Built $server successfully"
    else
        echo "❌ Failed to build $server"
        exit 1
    fi
done

echo ""
echo "🎉 All V2 MCP servers built successfully!"
```

### B. Deploy to Lambda Labs
```bash
#!/bin/bash
# scripts/deploy-v2-mcp-to-lambda.sh

set -e

LAMBDA_HOST="${LAMBDA_LABS_HOST:-146.235.200.1}"
LAMBDA_USER="${LAMBDA_LABS_USER:-ubuntu}"
REGISTRY="scoobyjava15"

echo "🚀 Deploying V2 MCP Servers to Lambda Labs"
echo "=========================================="

# Create docker-compose on Lambda Labs
ssh ${LAMBDA_USER}@${LAMBDA_HOST} << 'EOF'
    mkdir -p ~/sophia-mcp-v2
    cd ~/sophia-mcp-v2
EOF

# Copy docker-compose file
scp docker-compose.mcp-v2.yml ${LAMBDA_USER}@${LAMBDA_HOST}:~/sophia-mcp-v2/

# Deploy stack
ssh ${LAMBDA_USER}@${LAMBDA_HOST} << 'EOF'
    cd ~/sophia-mcp-v2

    # Pull latest images
    docker-compose pull

    # Deploy with Docker Compose
    docker-compose up -d

    # Wait for services
    echo "⏳ Waiting for services to start..."
    sleep 30

    # Check health
    docker-compose ps

    # Test endpoints
    for port in 9000 9001 9002 9003 9004 9005 9006 9007 9008; do
        echo -n "Testing port $port: "
        if curl -s -f http://localhost:$port/health > /dev/null; then
            echo "✅ Healthy"
        else
            echo "❌ Not responding"
        fi
    done
EOF
```

## 3.3 Configure API Gateway Integration (1 hour)

### A. Update Backend Routes
```python
# backend/api/mcp_integration_routes.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import httpx
import asyncio

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])

# MCP server endpoints
MCP_SERVERS = {
    "ai-memory": "http://localhost:9000",
    "snowflake": "http://localhost:9001",
    "linear": "http://localhost:9002",
    "notion": "http://localhost:9003",
    "asana": "http://localhost:9004",
    "codacy": "http://localhost:9005",
    "github": "http://localhost:9006",
    "slack": "http://localhost:9007",
    "perplexity": "http://localhost:9008"
}

@router.get("/servers")
async def list_mcp_servers():
    """List all available MCP servers and their status"""
    statuses = {}

    async def check_server(name: str, url: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=2)
                statuses[name] = {
                    "url": url,
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
        except:
            statuses[name] = {
                "url": url,
                "status": "offline",
                "response_time": None
            }

    # Check all servers in parallel
    await asyncio.gather(*[
        check_server(name, url) for name, url in MCP_SERVERS.items()
    ])

    return statuses

@router.post("/{server}/{endpoint:path}")
async def proxy_mcp_request(server: str, endpoint: str, body: Dict[str, Any]):
    """Proxy requests to MCP servers"""
    if server not in MCP_SERVERS:
        raise HTTPException(status_code=404, detail=f"MCP server '{server}' not found")

    server_url = MCP_SERVERS[server]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{server_url}/api/v2/{endpoint}",
                json=body,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"MCP server error: {str(e)}")
```

### B. Update Nginx for MCP Routes
```nginx
# Add to /etc/nginx/sites-available/sophia-api.conf

# MCP Server Upstreams
upstream mcp_ai_memory {
    server 127.0.0.1:9000;
}

upstream mcp_snowflake {
    server 127.0.0.1:9001;
}

upstream mcp_github {
    server 127.0.0.1:9006;
}

upstream mcp_slack {
    server 127.0.0.1:9007;
}

upstream mcp_perplexity {
    server 127.0.0.1:9008;
}

# In the main server block, add:

# Direct MCP access (optional)
location ~ ^/mcp/ai-memory/(.*) {
    proxy_pass http://mcp_ai_memory/$1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location ~ ^/mcp/github/(.*) {
    proxy_pass http://mcp_github/$1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Add similar blocks for other priority servers
```

## 3.4 Integration Testing (1 hour)

### A. MCP Integration Test Suite
```python
# tests/test_mcp_integration.py
import pytest
import httpx
import asyncio
from datetime import datetime

API_BASE = "https://api.sophia-intel.ai"

@pytest.mark.asyncio
async def test_mcp_servers_health():
    """Test all MCP servers are healthy"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/api/v1/mcp/servers")
        assert response.status_code == 200

        servers = response.json()
        assert len(servers) == 9

        # Check priority servers
        priority_servers = ["github", "slack", "perplexity", "ai-memory", "snowflake"]
        for server in priority_servers:
            assert server in servers
            assert servers[server]["status"] == "healthy"

@pytest.mark.asyncio
async def test_github_integration():
    """Test GitHub MCP server functionality"""
    async with httpx.AsyncClient() as client:
        # Test repository info
        response = await client.post(
            f"{API_BASE}/api/v1/mcp/github/repository",
            json={
                "owner": "ai-cherry",
                "repo": "sophia-main"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

@pytest.mark.asyncio
async def test_perplexity_integration():
    """Test Perplexity documentation search"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/api/v1/mcp/perplexity/search",
            json={
                "query": "FastAPI WebSocket implementation",
                "context": "python"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "content" in data

@pytest.mark.asyncio
async def test_slack_integration():
    """Test Slack message functionality"""
    async with httpx.AsyncClient() as client:
        # Test channel list
        response = await client.post(
            f"{API_BASE}/api/v1/mcp/slack/channels",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert "channels" in data
```

### B. End-to-End Chat Test with MCP
```python
# tests/test_chat_with_mcp.py
import pytest
import websockets
import json
import asyncio

WS_URL = "wss://api.sophia-intel.ai/ws/test-user"

@pytest.mark.asyncio
async def test_chat_with_github_context():
    """Test chat with GitHub code search"""
    async with websockets.connect(WS_URL) as websocket:
        # Send message requesting code
        await websocket.send(json.dumps({
            "message": "Show me examples of WebSocket implementation in Python",
            "search_context": "code_search",
            "access_level": "employee"
        }))

        # Receive response
        response = await websocket.recv()
        data = json.loads(response)

        assert data["type"] == "response"
        assert "WebSocket" in data["data"]["response"]
        assert len(data["data"]["sources"]) > 0

@pytest.mark.asyncio
async def test_chat_with_documentation():
    """Test chat with Perplexity documentation search"""
    async with websockets.connect(WS_URL) as websocket:
        # Send documentation query
        await websocket.send(json.dumps({
            "message": "How do I implement authentication in FastAPI?",
            "search_context": "documentation",
            "access_level": "employee"
        }))

        # Receive response
        response = await websocket.recv()
        data = json.loads(response)

        assert data["type"] == "response"
        assert "FastAPI" in data["data"]["response"]
        assert "authentication" in data["data"]["response"].lower()
```

## Success Criteria ✅
- [ ] All 9 V2 MCP servers built and deployed
- [ ] Health endpoints returning 200 for all servers
- [ ] Priority servers (GitHub, Slack, Perplexity) fully functional
- [ ] API gateway routing working
- [ ] Integration tests passing
- [ ] Chat system using MCP servers for enhanced responses

## Rollback Plan 🔄
```bash
# SSH to Lambda Labs
ssh ubuntu@146.235.200.1

# Stop specific MCP server
cd ~/sophia-mcp-v2
docker-compose stop <service-name>

# Rollback all MCP servers
docker-compose down
docker-compose up -d --scale github=0 --scale slack=0 --scale perplexity=0

# Remove problematic server
docker-compose rm -f <service-name>
```

## Phase 3 Completion Checklist
- [ ] All MCP servers implemented
- [ ] Docker images built and pushed
- [ ] Servers deployed to Lambda Labs
- [ ] API gateway integration complete
- [ ] Health monitoring active
- [ ] Integration tests passing
- [ ] Ready for Phase 4: End-to-End Validation

## Time Tracking
- Start Time: ___________
- End Time: ___________
- Total Duration: ___________
- Issues Encountered: ___________

## Notes
_Document any deviations from the plan or additional fixes required_
