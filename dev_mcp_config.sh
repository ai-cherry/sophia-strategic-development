# Development Configuration for MCP Servers

# Environment variables for development
export ENVIRONMENT=dev
export LOG_LEVEL=DEBUG
export MCP_DEBUG=true

# modern_stack configuration (already set by startup_config.py)
export modern_stack_ACCOUNT=ZNB04675
export modern_stack_USER=SCOOBYJAVA15
export modern_stack_DATABASE=SOPHIA_AI
export modern_stack_WAREHOUSE=SOPHIA_AI_WH
export modern_stack_ROLE=ACCOUNTADMIN
export modern_stack_SCHEMA=PROCESSED_AI

# Development shortcuts
alias test-mcp="python test_mcp_servers.py"
alias start-inspector="./start_mcp_inspector.sh"
alias sophia-dev="source .venv/bin/activate && export ENVIRONMENT=dev"

echo "🔧 Sophia AI MCP development environment configured"
