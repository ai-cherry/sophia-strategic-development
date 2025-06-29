# Development Configuration for MCP Servers

# Environment variables for development
export ENVIRONMENT=dev
export LOG_LEVEL=DEBUG
export MCP_DEBUG=true

# Snowflake configuration (already set by startup_config.py)
export SNOWFLAKE_ACCOUNT=ZNB04675
export SNOWFLAKE_USER=SCOOBYJAVA15
export SNOWFLAKE_DATABASE=SOPHIA_AI
export SNOWFLAKE_WAREHOUSE=SOPHIA_AI_WH
export SNOWFLAKE_ROLE=ACCOUNTADMIN
export SNOWFLAKE_SCHEMA=PROCESSED_AI

# Development shortcuts
alias test-mcp="python test_mcp_servers.py"
alias start-inspector="./start_mcp_inspector.sh"
alias sophia-dev="source .venv/bin/activate && export ENVIRONMENT=dev"

echo "🔧 Sophia AI MCP development environment configured"
