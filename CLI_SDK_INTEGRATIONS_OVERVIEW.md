# CLI Workflows, SDKs, and Integrations Overview

## 1. CLI Workflows

### A. Top-level Shell Scripts (Project Root)
- **deploy.sh, deploy_fixed.sh, deploy_final.sh**: Unified deployment orchestration scripts managing full or partial deployments of the Sophia AI platform and its components.
- **ensure_venv.sh**: Sets up and activates the Python virtual environment for development or deployment.
- **install_gemini_cli.sh**: Installs the Gemini CLI tool used for large file processing and AI document handling.
- **push_*.sh**: Scripts to push codebase optimizations, performance improvements, or bypass hooks to remote repositories or environments.

### B. MCP-Servers Folder Shell Scripts
- **run_all_mcp_servers.py / start_all_mcp_servers.py**: Python scripts to start all MCP servers in bulk for local or production environments.
- **deploy_lambda_labs_kubernetes.sh**: Deploys the Sophia AI platform components to Lambda Labs Kubernetes clusters.
- **deploy_*.sh / deploy_*.py**: Service-specific deployment scripts, e.g., deploy_gong_webhook_service.py, deploy_snowflake_schemas.sh, deploy_n8n_enterprise_enhancement.py.

### C. Click-based Python CLI Tools
- **anthropic-mcp-servers/scripts/release.py**: CLI tool for managing MCP server releases, including versioning and deployment.
- **anthropic-mcp-python-sdk/examples/servers/**: Example MCP server CLI implementations demonstrating usage of Click for command-line interfaces.
- **backend/mcp_servers/enhanced_mcp_base.py**: Base CLI framework for enhanced MCP server operations, providing common commands and utilities.
- **mcp-servers/snowflake_cli_enhanced/snowflake_cli_enhanced_mcp_server.py**: Enhanced CLI for Snowflake MCP server with additional commands for database management and monitoring.

## 2. SDKs

### A. External SDK Packages (Located in `external/`)
- **anthropic-mcp-python-sdk**: Official Python SDK for building and interacting with MCP servers and clients.
- **glips_figma_context**: SDK for integrating with Figma design context and APIs.
- **microsoft_playwright**: Playwright testing and automation SDK and CLI.
- **snowflake_cortex_official, davidamom_snowflake, dynamike_snowflake, isaacwasserman_snowflake**: Community MCP server SDKs focused on Snowflake database integrations.
- **openrouter_search, portkey_admin**: Specialized SDKs for routing and administrative tasks.

### B. Internal Client-Library Code
- **backend/integrations/**: Contains API client libraries and wrappers for external services such as Gong, Estuary, Portkey Gateway, and others.
- **backend/api/**: Lightweight HTTP endpoint wrappers and route handlers that act as SDK-like interfaces for internal and external APIs.

## 3. Integrations

### A. Backend Integrations (`backend/integrations/`)
- **estuary_flow_manager.py**: Manages data flows to and from Estuary vector database.
- **enhanced_gong_integration.py & gong_api_client.py**: Integration with Gong.io call analysis platform, including API clients and webhook processors.
- **portkey_gateway_service.py**: Gateway service integration for Portkey administrative APIs.
- **gong_webhook_processor.py & gong_webhook_server.py**: Webhook handling for Gong events.

### B. MCP Server Integrations (`mcp-servers/`)
- **hubspot/**: MCP server and clients for HubSpot CRM integration.
- **slack/**: Slack MCP server and integration scripts.
- **salesforce/**: Salesforce MCP server integration.
- **asana/**: Asana task management MCP server.
- **snowflake/**: Snowflake database MCP servers and enhanced CLI tools.
- **intercom/**: Intercom messaging platform MCP server.
- **apollo/**: Apollo.io MCP server for sales intelligence.
- **ai_memory/**: AI memory MCP server for context and conversation management.

---

This overview captures the main CLI workflows, SDKs, and integrations in the Sophia AI codebase, grouped by their location and purpose. Each category includes representative examples and brief descriptions to provide a clear understanding of the system's components.
