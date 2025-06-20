# Architecture Migration Plan

This plan outlines the steps to migrate the inconsistent components identified in the Architecture Inconsistencies Report to align with the new Sophia AI architecture.

## Phase 1: Direct API Calls Migration

### Priority: High
### Timeline: 1-2 weeks

1. **Create MCP Server Tools for Missing APIs**
   - Review all direct API calls in the codebase
   - Ensure each API has a corresponding tool in the appropriate MCP server
   - Add missing tools to MCP servers as needed

2. **Refactor `gong_api_alternative.py`**
   - Create a new script `gong_mcp_client.py` that uses the MCP client to call the Gong MCP server
   - Implement the same functionality using MCP tools
   - Test the new implementation
   - Replace the old script with the new one

3. **Refactor Other Direct API Call Scripts**
   - Identify all scripts making direct API calls
   - Create new versions that use the MCP client
   - Test the new implementations
   - Replace the old scripts with the new ones

4. **Update Documentation**
   - Update API documentation to reflect the new MCP-based approach
   - Create examples of how to use the MCP client for API calls

## Phase 2: Infrastructure as Code Migration

### Priority: High
### Timeline: 1-2 weeks

1. **Create Pulumi MCP Tools for Missing Operations**
   - Review all direct Pulumi commands in the codebase
   - Ensure each operation has a corresponding tool in the Pulumi MCP server
   - Add missing tools to the Pulumi MCP server as needed

2. **Refactor `deploy_production.sh`**
   - Create a new script `deploy_production_mcp.py` that uses the MCP client to call the Pulumi MCP server
   - Implement the same functionality using MCP tools
   - Test the new implementation
   - Replace the old script with the new one

3. **Refactor Other Deployment Scripts**
   - Identify all scripts running Pulumi commands directly
   - Create new versions that use the MCP client
   - Test the new implementations
   - Replace the old scripts with the new ones

4. **Update Documentation**
   - Update deployment documentation to reflect the new MCP-based approach
   - Create examples of how to use the MCP client for infrastructure operations

## Phase 3: UI Migration

### Priority: Medium
### Timeline: 2-3 weeks

1. **Inventory Current UI Features**
   - Document all features in the current `sophia_admin_frontend`
   - Map each feature to a corresponding Retool dashboard

2. **Create Retool Dashboards**
   - Use the `scripts/build_retool_dashboards.py` script as a template
   - Create scripts to build each required dashboard
   - Test each dashboard for functionality

3. **Update References**
   - Identify all references to the old UI in scripts and configuration files
   - Update these references to use the new Retool dashboards
   - Test the updated scripts and configuration files

4. **Deprecate Old UI**
   - Once all features are migrated, mark the old UI as deprecated
   - Update documentation to point users to the new Retool dashboards
   - Eventually remove the old UI code

## Phase 4: Vector Store Access Migration

### Priority: Medium
### Timeline: 1-2 weeks

1. **Audit Vector Store Access**
   - Review all files that import Pinecone or Weaviate directly
   - Identify any code that bypasses the ComprehensiveMemoryManager

2. **Refactor Direct Vector Store Access**
   - Update code to use the ComprehensiveMemoryManager or HybridRAGManager
   - Test the updated code
   - Document the changes

3. **Update Documentation**
   - Update vector store documentation to emphasize the use of the ComprehensiveMemoryManager
   - Create examples of how to use the ComprehensiveMemoryManager for vector store operations

## Phase 5: Automated Checks

### Priority: Low
### Timeline: 1 week

1. **Create Linting Rules**
   - Create custom linting rules to detect direct API calls, Pulumi commands, and vector store access
   - Integrate these rules into the CI/CD pipeline

2. **Update CI/CD Pipeline**
   - Add checks to the CI/CD pipeline to detect architecture inconsistencies
   - Block PRs that introduce new inconsistencies

3. **Create Architecture Documentation**
   - Document the new architecture and best practices
   - Create a guide for developers on how to follow the new architecture

## Timeline Summary

- **Phase 1 (Direct API Calls)**: Weeks 1-2
- **Phase 2 (Infrastructure as Code)**: Weeks 3-4
- **Phase 3 (UI Migration)**: Weeks 5-7
- **Phase 4 (Vector Store Access)**: Weeks 8-9
- **Phase 5 (Automated Checks)**: Week 10

Total timeline: 10 weeks

## Success Criteria

1. All direct API calls are replaced with MCP client calls
2. All direct Pulumi commands are replaced with MCP client calls
3. All UI features are migrated to Retool dashboards
4. All vector store access goes through the ComprehensiveMemoryManager
5. Automated checks are in place to prevent future inconsistencies
6. Documentation is updated to reflect the new architecture
