# Development Configuration for MCP Servers

# Environment variables for development
export ENVIRONMENT=dev
export LOG_LEVEL=DEBUG
export MCP_DEBUG=true

# Qdrant Configuration (already set by startup_config.py)
export QDRANT_URLZNB04675
export QDRANT_API_KEYSCOOBYJAVA15
export QDRANT_DBSOPHIA_AI
export QDRANT_COLLECTIONSOPHIA_AI_WH
export QDRANT_ROLEACCOUNTADMIN
export QDRANT_SCHEMAPROCESSED_AI

# Development shortcuts
alias test-mcp="python test_mcp_servers.py"
alias start-inspector="./start_mcp_inspector.sh"
alias sophia-dev="source .venv/bin/activate && export ENVIRONMENT=dev"

echo "🔧 Sophia AI MCP development environment configured"
