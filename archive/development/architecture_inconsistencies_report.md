# Architecture Inconsistencies Report

This report identifies files and components that are inconsistent with the new Sophia AI architecture, which is based on the MCP federation model, Pulumi IAC toolkit, and Retool UI.

## 1. Direct API Calls Outside MCP Federation

### Issues Found:

- **`gong_api_alternative.py`**: Makes direct API calls to Gong without going through the MCP federation model.
  ```python
  # Direct API call example
  response = requests.get(
      f"{self.base_url}/users",
      headers=self.headers,
      timeout=30
  )
  ```

- **Other direct API call scripts**: Several scripts in the root directory make direct API calls to various services without going through MCP servers.

### Recommended Fix:

These scripts should be refactored to use the MCP client to call the appropriate MCP server. For example, instead of making direct API calls to Gong, they should use:

```python
from backend.mcp.mcp_client import MCPClient

async def gong_api_call():
    mcp_client = MCPClient("http://localhost:8090")
    await mcp_client.connect()

    result = await mcp_client.call_tool(
        "gong",
        "get_users",
        {}
    )

    await mcp_client.close()
    return result
```

## 2. Direct Pulumi Commands

### Issues Found:

- **`deploy_production.sh`**: Runs Pulumi commands directly, which is inconsistent with the new architecture.
  ```bash
  # Direct Pulumi command
  cd infrastructure
  pulumi up --yes
  cd ..
  ```

- **Other deployment scripts**: Several deployment scripts in the root directory run Pulumi commands directly.

### Recommended Fix:

Infrastructure tasks should be executed through the PulumiMCPServer, which runs in the iac-toolkit Docker container. Scripts should be refactored to use the MCP client to call the Pulumi MCP server:

```python
from backend.mcp.mcp_client import MCPClient

async def deploy_infrastructure():
    mcp_client = MCPClient("http://localhost:8090")
    await mcp_client.connect()

    result = await mcp_client.call_tool(
        "pulumi",
        "run_pulumi_up",
        {
            "script_path": "infrastructure/pulumi/retool_setup.py",
            "stack_name": "dev"
        }
    )

    await mcp_client.close()
    return result
```

## 3. Old UI Components

### Issues Found:

- **`sophia_admin_frontend`**: The old UI that should be replaced by Retool dashboards.
- References to the old UI in various scripts and configuration files:
  - `deploy_production.sh`
  - `quick_setup.sh`
  - `vercel.json`
  - etc.

### Recommended Fix:

The old UI should be replaced by Retool dashboards, which can be created using the RetoolMCPServer. The `scripts/build_retool_dashboards.py` script already demonstrates how to build dashboards using the MCP client:

```python
create_app_result = await self.mcp_client.call_tool(
    "retool",
    "create_admin_dashboard",
    dashboard_name=dashboard_name,
    description="Live dashboard to monitor the health and status of all running MCP servers."
)
```

All references to the old UI in scripts and configuration files should be updated to use Retool dashboards instead.

## 4. Vector Store Direct Access

### Issues Found:

While no direct instances were found of code bypassing the ComprehensiveMemoryManager to access vector stores, there are several files that import Pinecone or Weaviate directly. These should be reviewed to ensure they're using the ComprehensiveMemoryManager or HybridRAGManager for all vector store operations.

### Recommended Fix:

All vector store operations should go through the ComprehensiveMemoryManager or HybridRAGManager:

```python
from backend.core.comprehensive_memory_manager import comprehensive_memory_manager

async def store_memory(agent_id, content, metadata):
    request = MemoryRequest(
        operation=MemoryOperationType.STORE,
        agent_id=agent_id,
        content=content,
        metadata=metadata
    )

    response = await comprehensive_memory_manager.process_memory_request(request)
    return response
```

## Next Steps

1. Create a migration plan to refactor these inconsistent components.
2. Prioritize the migration based on the criticality of each component.
3. Update documentation to reflect the new architecture and best practices.
4. Implement automated checks to prevent future inconsistencies.
