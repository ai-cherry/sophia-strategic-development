# Cline v3.18 Sophia AI Integration - Implementation Guide

## 🎯 Overview

This guide provides step-by-step instructions for integrating Cline v3.18 features into Sophia AI's MCP server ecosystem, enhancing capabilities with Claude 4 optimization, free Gemini CLI for large contexts, WebFetch, self-knowledge, and improved diff editing.

## 📋 Prerequisites

1. **Environment Setup**
   ```bash
   cd ~/sophia-main
   source .venv/bin/activate
   ```

2. **Required Tools**
   - Python 3.11+
   - Docker & Docker Compose
   - Gemini CLI (optional but recommended)
   - Node.js 18+ (for some MCP servers)

## 🚀 Phase 1: Core Infrastructure (Day 1-3)

### Step 1: Install Gemini CLI

```bash
# Install Gemini CLI for free large context processing
./scripts/install_gemini_cli.sh

# Verify installation
gemini --version
```

### Step 2: Create Enhanced Base MCP Server

```python
# File: backend/mcp/base/enhanced_standardized_mcp_server.py
"""Enhanced Standardized MCP Server with Cline v3.18 Features."""
import os
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging

from backend.mcp.base.standardized_mcp_server import StandardizedMCPServer
from backend.mcp.mixins.cline_v3_18_features import ClineV318FeaturesMixin
from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)

class EnhancedStandardizedMCPServer(StandardizedMCPServer, ClineV318FeaturesMixin):
    """Enhanced base class for all MCP servers with Cline v3.18 features."""
    
    def __init__(self, name: str, port: int, version: str = "1.1.0"):
        """Initialize enhanced MCP server with v3.18 features."""
        super().__init__(name, port, version)
        ClineV318FeaturesMixin.__init__(self)
        self.v318_features = True
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request with v3.18 intelligent routing."""
        # Check if this is a v3.18 feature request
        if request.get('use_v318_features', True):
            return await self.process_with_v318(request)
        
        # Fallback to standard processing
        return await super().handle_request(request)
    
    def get_nl_commands(self) -> List[str]:
        """Return natural language commands with v3.18 features."""
        base_commands = super().get_nl_commands() if hasattr(super(), 'get_nl_commands') else []
        v318_commands = [
            f"Process large file with Gemini for {self.name}",
            f"Fetch web content for {self.name}",
            f"Show {self.name} capabilities",
            f"Apply smart diff to {self.name} files"
        ]
        return base_commands + v318_commands
```

### Step 3: Update Existing Enhanced MCP Servers

```python
# File: mcp-servers/linear/enhanced_linear_mcp_server.py
"""Enhanced Linear MCP Server with Cline v3.18 Features."""
from typing import Dict, List, Any, Optional
import aiohttp
import logging

from backend.mcp.base.enhanced_standardized_mcp_server import EnhancedStandardizedMCPServer
from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)

class EnhancedLinearMCPServer(EnhancedStandardizedMCPServer):
    """Linear MCP Server with v3.18 enhancements."""
    
    def __init__(self):
        super().__init__(
            name="linear",
            port=9003,
            version="1.1.0"
        )
        self.linear_api_key = config.linear_api_key
        self.linear_api_url = "https://api.linear.app/graphql"
        
    async def fetch_linear_data(self, query: str) -> Dict[str, Any]:
        """Fetch Linear data with automatic web caching."""
        # Use WebFetch mixin for caching
        cache_key = f"linear_query_{hash(query)}"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": self.linear_api_key,
                "Content-Type": "application/json"
            }
            
            async with session.post(self.linear_api_url, json={"query": query}, headers=headers) as response:
                return await response.json()
    
    async def process_large_project_data(self, project_id: str) -> Dict[str, Any]:
        """Process large project data using Gemini CLI."""
        # Fetch all project data
        project_data = await self.fetch_project_details(project_id)
        
        # Check if data is large enough for Gemini
        data_str = str(project_data)
        if len(data_str) > self.context_threshold:
            # Use Gemini CLI for processing
            result = await self.process_with_gemini(
                data_str,
                "Analyze this Linear project data and provide insights"
            )
            return {"analysis": result, "model": "gemini_cli"}
        
        # Use standard processing for smaller data
        return {"data": project_data, "model": "standard"}
    
    def _get_nl_commands(self) -> List[str]:
        """Linear-specific natural language commands."""
        return [
            "Create Linear issue for [task]",
            "Fetch Linear project roadmap from web",
            "Process large Linear export with Gemini",
            "Show Linear server capabilities",
            "Update Linear issue with smart diff"
        ]
```

## 📦 Phase 2: MCP Server Enhancements (Day 4-7)

### Enhanced Snowflake Admin Server

```python
# File: mcp-servers/snowflake_admin/enhanced_snowflake_admin_server.py
"""Enhanced Snowflake Admin MCP Server with v3.18 Features."""
from typing import Dict, List, Any, Optional
import snowflake.connector
import logging

from backend.mcp.base.enhanced_standardized_mcp_server import EnhancedStandardizedMCPServer
from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)

class EnhancedSnowflakeAdminMCPServer(EnhancedStandardizedMCPServer):
    """Snowflake Admin with Gemini CLI for large queries."""
    
    def __init__(self):
        super().__init__(
            name="snowflake_admin",
            port=9010,
            version="1.1.0"
        )
        self.snowflake_config = {
            "account": config.snowflake_account,
            "user": config.snowflake_user,
            "password": config.snowflake_password,
            "warehouse": config.snowflake_warehouse,
            "database": config.snowflake_database,
            "schema": config.snowflake_schema
        }
        
    async def execute_large_query(self, query: str) -> Dict[str, Any]:
        """Execute large query with intelligent model routing."""
        # Estimate query size
        estimated_rows = await self._estimate_query_size(query)
        
        if estimated_rows > 100000:
            # Use Gemini CLI for large result sets
            logger.info(f"Routing large query to Gemini CLI: ~{estimated_rows} rows")
            return await self._process_with_gemini_streaming(query)
        else:
            # Use standard execution
            return await self._execute_standard_query(query)
    
    async def analyze_schema_documentation(self, schema_url: str) -> Dict[str, Any]:
        """Fetch and analyze schema documentation from web."""
        # Use WebFetch to get documentation
        doc_content = await self.fetch_web_content(schema_url)
        
        # Analyze with Claude 4 for complex reasoning
        analysis = await self._analyze_with_claude4(doc_content['content'])
        
        return {
            "source": schema_url,
            "analysis": analysis,
            "cached": doc_content.get('cached', False)
        }
    
    def _get_nl_commands(self) -> List[str]:
        """Snowflake-specific natural language commands."""
        return [
            "Execute large Snowflake query with Gemini",
            "Fetch Snowflake documentation from [url]",
            "Analyze table schema with Claude 4",
            "Show Snowflake server capabilities",
            "Optimize query performance"
        ]
```

### Enhanced Slack Integration

```python
# File: mcp-servers/slack/enhanced_slack_mcp_server.py
"""Enhanced Slack MCP Server with v3.18 Features."""
from typing import Dict, List, Any, Optional
from slack_sdk.web.async_client import AsyncWebClient
import logging

from backend.mcp.base.enhanced_standardized_mcp_server import EnhancedStandardizedMCPServer
from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)

class EnhancedSlackMCPServer(EnhancedStandardizedMCPServer):
    """Slack server with Gemini for large history processing."""
    
    def __init__(self):
        super().__init__(
            name="slack",
            port=9011,
            version="1.1.0"
        )
        self.slack_client = AsyncWebClient(token=config.slack_bot_token)
        
    async def analyze_channel_history(self, channel_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze channel history with intelligent routing."""
        # Fetch history
        messages = await self._fetch_channel_history(channel_id, days)
        
        # Check size for routing
        total_text = "\n".join([msg.get('text', '') for msg in messages])
        
        if len(total_text) > self.context_threshold:
            # Use Gemini for large histories
            analysis = await self.process_with_gemini(
                total_text,
                f"Analyze this Slack channel history and provide key insights, decisions, and action items"
            )
            return {
                "channel_id": channel_id,
                "message_count": len(messages),
                "analysis": analysis,
                "model": "gemini_cli"
            }
        else:
            # Use standard analysis
            return await self._standard_analysis(messages)
```

## 🔧 Phase 3: Integration & Testing (Day 8-10)

### Updated MCP Configuration

```json
// File: mcp-config/unified_mcp_servers_v318.json
{
  "servers": {
    "ai_memory": {
      "port": 9000,
      "version": "1.1.0",
      "features": ["auto_discovery", "smart_recall", "v318"],
      "status": "enhanced"
    },
    "codacy": {
      "port": 3008,
      "version": "1.1.0",
      "features": ["real_time_analysis", "security_scan", "v318"],
      "status": "enhanced"
    },
    "linear": {
      "port": 9003,
      "version": "1.1.0",
      "features": ["webfetch", "self_knowledge", "v318"],
      "status": "enhanced"
    },
    "snowflake_admin": {
      "port": 9010,
      "version": "1.1.0",
      "features": ["gemini_cli", "webfetch", "v318"],
      "status": "enhanced"
    },
    "slack": {
      "port": 9011,
      "version": "1.1.0",
      "features": ["gemini_cli", "large_history", "v318"],
      "status": "enhanced"
    }
  },
  "v318_features": {
    "gemini_cli": {
      "enabled": true,
      "context_threshold": 100000,
      "cost": "free"
    },
    "claude_4": {
      "enabled": true,
      "use_for": ["reasoning", "code_generation"]
    },
    "webfetch": {
      "enabled": true,
      "cache_ttl_hours": 24
    },
    "self_knowledge": {
      "enabled": true
    },
    "improved_diff": {
      "enabled": true,
      "success_rate": 0.95
    }
  }
}
```

### Testing Script

```python
# File: scripts/test_v318_integration.py
"""Test Cline v3.18 Integration."""
import asyncio
import aiohttp
import json
from typing import Dict, Any

async def test_mcp_server(server_name: str, port: int) -> Dict[str, Any]:
    """Test a single MCP server's v3.18 features."""
    print(f"\n🧪 Testing {server_name} on port {port}...")
    
    tests = {
        "self_knowledge": await test_self_knowledge(port),
        "webfetch": await test_webfetch(port),
        "gemini_cli": await test_gemini_cli(port),
        "model_routing": await test_model_routing(port)
    }
    
    return {
        "server": server_name,
        "port": port,
        "tests": tests,
        "v318_ready": all(tests.values())
    }

async def test_self_knowledge(port: int) -> bool:
    """Test self-knowledge capability."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://localhost:{port}/capabilities",
                json={}
            ) as response:
                data = await response.json()
                return "features" in data and "natural_language_commands" in data
    except:
        return False

async def test_webfetch(port: int) -> bool:
    """Test WebFetch capability."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://localhost:{port}/webfetch",
                json={"url": "https://example.com"}
            ) as response:
                data = await response.json()
                return "content" in data and "summary" in data
    except:
        return False

async def test_gemini_cli(port: int) -> bool:
    """Test Gemini CLI integration."""
    try:
        async with aiohttp.ClientSession() as session:
            # Create large context
            large_text = "Test content " * 20000  # ~100K chars
            async with session.post(
                f"http://localhost:{port}/process",
                json={
                    "content": large_text,
                    "use_v318_features": True
                }
            ) as response:
                data = await response.json()
                return data.get("model_used") == "gemini_cli"
    except:
        return False

async def test_model_routing(port: int) -> bool:
    """Test intelligent model routing."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://localhost:{port}/route",
                json={
                    "context_size": 150000,
                    "requirements": ["large_context"],
                    "prefer_free": True
                }
            ) as response:
                data = await response.json()
                return data.get("model") == "gemini_cli"
    except:
        return False

async def main():
    """Run all v3.18 integration tests."""
    print("🚀 Cline v3.18 Integration Test Suite")
    print("=====================================")
    
    # Load server configuration
    with open("mcp-config/unified_mcp_servers_v318.json", "r") as f:
        config = json.load(f)
    
    # Test each server
    results = []
    for server_name, server_config in config["servers"].items():
        if server_config.get("status") == "enhanced":
            result = await test_mcp_server(
                server_name,
                server_config["port"]
            )
            results.append(result)
    
    # Summary
    print("\n📊 Test Summary")
    print("===============")
    ready_count = sum(1 for r in results if r["v318_ready"])
    print(f"✅ v3.18 Ready: {ready_count}/{len(results)} servers")
    
    for result in results:
        status = "✅" if result["v318_ready"] else "❌"
        print(f"{status} {result['server']}: {result['tests']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎯 Natural Language Command Examples

### AI Memory Server
- "Store this conversation about v3.18 integration"
- "Recall similar MCP server implementations"
- "Process this 500K token file with Gemini"
- "Show AI Memory server capabilities"

### Codacy Server
- "Analyze this code with Claude 4"
- "Scan for security vulnerabilities"
- "Apply smart diff to fix issues"
- "Show Codacy performance metrics"

### Linear Server
- "Create issue from this web page"
- "Process large project export with Gemini"
- "Fetch Linear API docs and analyze"
- "Show Linear integration capabilities"

### Snowflake Admin
- "Execute this 1M row query with Gemini"
- "Fetch Snowflake best practices from web"
- "Analyze query performance with Claude 4"
- "Show Snowflake server capabilities"

### Slack Server
- "Analyze last 90 days of #general with Gemini"
- "Fetch user profile from web"
- "Process large file upload"
- "Show Slack server metrics"

## 📈 Performance Optimization

### Model Selection Strategy
```python
def select_optimal_model(context_size: int, task_type: str, prefer_free: bool = True) -> str:
    """Select optimal model based on context and task."""
    if context_size > 100_000 and prefer_free:
        return "gemini_cli"  # Free for large contexts
    elif task_type in ["reasoning", "code_generation", "analysis"]:
        return "claude_4"  # Best for complex tasks
    elif context_size < 32_000 and task_type == "simple":
        return "local"  # Fast for simple tasks
    else:
        return "gpt4"  # Good general purpose
```

### Caching Strategy
- WebFetch: 24-hour TTL for web content
- API responses: 1-hour TTL for dynamic data
- Static content: 7-day TTL
- Clear cache on demand

## 🚨 Monitoring & Alerts

### Key Metrics
1. **Model Usage**
   - Track requests by model
   - Monitor costs (especially non-free models)
   - Alert on unusual patterns

2. **Performance**
   - Response times by model
   - Success rates for diff operations
   - Cache hit rates

3. **Errors**
   - Model routing failures
   - Gemini CLI availability
   - WebFetch failures

## 🎉 Success Criteria

- ✅ All MCP servers enhanced with v3.18 features
- ✅ 95%+ diff editing success rate
- ✅ Cost reduction through Gemini CLI usage
- ✅ Improved response times with intelligent routing
- ✅ Self-documenting MCP servers
- ✅ Seamless integration with existing workflows

## 📚 Additional Resources

- [Cline v3.18 Release Notes](https://github.com/cline/cline/releases/tag/v3.18.0)
- [Gemini CLI Documentation](https://ai.google.dev/gemini-api/docs/cli)
- [Claude 4 API Reference](https://docs.anthropic.com/claude/reference)
- [MCP Protocol Specification](https://modelcontextprotocol.io/docs)

## 🤝 Support

For issues or questions:
1. Check MCP server logs: `docker-compose logs [server_name]`
2. Run diagnostics: `python scripts/test_v318_integration.py`
3. Review error patterns in monitoring dashboard
4. Contact the Sophia AI team

---

*Last Updated: December 2024*
*Version: 1.0.0*
