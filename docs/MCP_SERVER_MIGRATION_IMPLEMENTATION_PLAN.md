# MCP Server Migration & Implementation Plan

**Date:** July 10, 2025  
**Priority:** CRITICAL  
**Timeline:** 1 week

## Executive Summary

This plan outlines the migration of existing MCP servers to the official Anthropic SDK and implementation of missing core servers. The goal is to achieve 100% standardization on the official SDK with all 6 core servers operational.

## Current State

### Existing Servers (Need Migration)
1. **ai_memory** - Currently uses hybrid approach
2. **snowflake_unified** - Currently uses hybrid approach

### Missing Core Servers (Need Implementation)
1. **github** - Source control integration
2. **slack** - Team communication
3. **codacy** - Code quality analysis
4. **asana** - Project management

## Implementation Plan

### Phase 1: Analyze Existing Servers (30 minutes)
1. Review current ai_memory implementation
2. Review current snowflake_unified implementation
3. Document existing functionality to preserve
4. Identify any custom features needing migration

### Phase 2: Migrate Existing Servers (2 hours)

#### 2.1 AI Memory Server Migration
```python
# Key functionality to preserve:
- store_memory(category, content, metadata)
- recall_memory(category, query, limit)
- search_memories(query, filters)
- delete_memory(memory_id)
- get_memory_stats()
```

#### 2.2 Snowflake Unified Server Migration
```python
# Key functionality to preserve:
- execute_query(query, warehouse)
- get_table_info(database, schema, table)
- analyze_data(table, columns)
- export_results(query, format)
- get_warehouse_status()
```

### Phase 3: Implement Missing Servers (4 hours)

#### 3.1 GitHub MCP Server
**Purpose:** Enable AI to interact with GitHub repositories
```python
# Core tools:
- list_repositories()
- get_repository_info(repo)
- list_issues(repo, state)
- create_issue(repo, title, body)
- list_pull_requests(repo, state)
- get_file_content(repo, path)
- search_code(query, repo)
```

#### 3.2 Slack MCP Server
**Purpose:** Enable AI to interact with Slack workspace
```python
# Core tools:
- list_channels()
- send_message(channel, text)
- search_messages(query, channel)
- get_channel_history(channel, limit)
- get_user_info(user_id)
- upload_file(channel, file_path)
```

#### 3.3 Codacy MCP Server
**Purpose:** Enable AI to analyze code quality
```python
# Core tools:
- analyze_code(code, language)
- analyze_file(file_path)
- get_project_metrics(project_id)
- get_security_issues(project_id)
- get_code_patterns(project_id)
- get_coverage_report(project_id)
```

#### 3.4 Asana MCP Server
**Purpose:** Enable AI to manage projects and tasks
```python
# Core tools:
- list_projects(workspace)
- get_project_tasks(project_id)
- create_task(project_id, name, description)
- update_task(task_id, fields)
- get_task_details(task_id)
- add_comment(task_id, text)
- search_tasks(query, project_id)
```

## Technical Architecture

### Base Class Usage
All servers will inherit from `StandardizedMCPServer`:
```python
from mcp_servers.base.unified_standardized_base import StandardizedMCPServer

class CustomMCPServer(StandardizedMCPServer):
    async def get_custom_tools(self) -> List[Tool]:
        # Define tools
        pass
    
    async def handle_custom_tool(self, name: str, arguments: dict):
        # Handle tool calls
        pass
```

### Configuration Pattern
Each server will use consistent configuration:
```python
config = ServerConfig(
    name="server_name",
    version="1.0.0",
    description="Server description"
)
```

### Error Handling Pattern
Consistent error handling across all servers:
```python
try:
    result = await operation()
    return {"status": "success", "data": result}
except SpecificError as e:
    self.logger.error(f"Operation failed: {e}")
    return {"status": "error", "error": str(e)}
```

## Implementation Order

1. **ai_memory** (45 min) - Critical for system memory
2. **snowflake_unified** (45 min) - Critical for data access
3. **github** (60 min) - Important for code management
4. **slack** (60 min) - Important for notifications
5. **codacy** (60 min) - Important for code quality
6. **asana** (60 min) - Important for project tracking

## Testing Strategy

### Unit Tests
Each server will have unit tests for:
- Tool registration
- Tool execution
- Error handling
- Configuration

### Integration Tests
- Test with MCP Inspector
- Test with actual services (where possible)
- Validate response formats
- Check error scenarios

### Deployment Tests
- Verify server starts correctly
- Check health endpoint
- Validate tool listing
- Test basic operations

## Configuration Updates

### Update sophia_mcp_unified.yaml
```yaml
servers:
  - name: ai_memory
    port: 9001
    version: "2.0.0"  # Updated version
    
  - name: snowflake_unified
    port: 9021
    version: "2.0.0"  # Updated version
    
  - name: github
    port: 9003
    version: "1.0.0"  # New
    
  - name: slack
    port: 9005
    version: "1.0.0"  # New
    
  - name: codacy
    port: 9008
    version: "1.0.0"  # New
    
  - name: asana
    port: 9006
    version: "1.0.0"  # New
```

## Success Criteria

1. **All servers use official SDK** (no custom shim)
2. **All servers pass health checks**
3. **All servers respond to tool listing**
4. **All core functionality preserved**
5. **No breaking changes for existing integrations**
6. **Comprehensive logging implemented**
7. **Error handling standardized**

## Rollback Plan

1. Keep backups of original implementations
2. Version control all changes
3. Test in isolation before deployment
4. Gradual rollout (one server at a time)
5. Monitor logs for errors

## Next Steps After Implementation

1. Update deployment scripts
2. Update documentation
3. Create usage examples
4. Train team on new patterns
5. Monitor performance
6. Gather feedback

---

**Ready to begin implementation!** 