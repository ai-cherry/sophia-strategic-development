#!/bin/bash
# Production Environment Configuration for Sophia AI MCP Services

echo "🚀 Configuring Sophia AI MCP Services for Production"

# Set environment variables
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org
export LOG_LEVEL=INFO

# Snowflake configuration (using override)
export SNOWFLAKE_ACCOUNT=ZNB04675
export SNOWFLAKE_USER=SCOOBYJAVA15
export SNOWFLAKE_DATABASE=SOPHIA_AI
export SNOWFLAKE_WAREHOUSE=SOPHIA_AI_WH
export SNOWFLAKE_ROLE=ACCOUNTADMIN
export SNOWFLAKE_SCHEMA=PROCESSED_AI

# MCP Services configuration
export MCP_HEALTH_CHECK_INTERVAL=60
export MCP_AUTO_RESTART=true
export MCP_LOG_LEVEL=INFO

echo "✅ Production environment configured"
echo "🔧 Snowflake Account: $SNOWFLAKE_ACCOUNT"
echo "📊 Environment: $ENVIRONMENT"
echo "🏢 Pulumi Org: $PULUMI_ORG"

# Start services
echo "🚀 Starting MCP services..."
python start_mcp_services.py
