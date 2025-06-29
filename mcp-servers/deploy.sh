#!/bin/bash
# MCP Servers Deployment Script
set -e

echo "🚀 Deploying Sophia AI MCP Servers..."

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Check all required ports
echo "🔍 Checking port availability..."
check_port 9000 || echo "Warning: ai_memory port 9000 conflict"
check_port 9001 || echo "Warning: ai_orchestrator port 9001 conflict"
check_port 9002 || echo "Warning: sophia_business_intelligence port 9002 conflict"
check_port 9003 || echo "Warning: sophia_data_intelligence port 9003 conflict"
check_port 9004 || echo "Warning: code_intelligence port 9004 conflict"
check_port 9005 || echo "Warning: sophia_ai_intelligence port 9005 conflict"
check_port 9100 || echo "Warning: asana port 9100 conflict"
check_port 9101 || echo "Warning: linear port 9101 conflict"
check_port 9102 || echo "Warning: notion port 9102 conflict"
check_port 9103 || echo "Warning: slack port 9103 conflict"
check_port 9104 || echo "Warning: github port 9104 conflict"
check_port 9105 || echo "Warning: bright_data port 9105 conflict"
check_port 9106 || echo "Warning: ag_ui port 9106 conflict"
check_port 9200 || echo "Warning: snowflake port 9200 conflict"
check_port 9201 || echo "Warning: snowflake_admin port 9201 conflict"
check_port 9202 || echo "Warning: postgres port 9202 conflict"
check_port 9203 || echo "Warning: pulumi port 9203 conflict"
check_port 9204 || echo "Warning: sophia_infrastructure port 9204 conflict"
check_port 9205 || echo "Warning: docker port 9205 conflict"
check_port 9300 || echo "Warning: codacy port 9300 conflict"

echo "📦 Starting MCP servers..."

# Start core services first
echo "🧠 Starting core AI services..."

if [ -d "mcp-servers/ai_memory" ]; then
    echo "Starting ai_memory on port 9000..."
    cd mcp-servers/ai_memory
    MCP_SERVER_PORT=9000 python -m server &
    cd ../..
    sleep 2
fi

if [ -d "mcp-servers/sophia_ai_intelligence" ]; then
    echo "Starting sophia_ai_intelligence on port 9005..."
    cd mcp-servers/sophia_ai_intelligence
    MCP_SERVER_PORT=9005 python -m server &
    cd ../..
    sleep 2
fi

if [ -d "mcp-servers/codacy" ]; then
    echo "Starting codacy on port 9300..."
    cd mcp-servers/codacy
    MCP_SERVER_PORT=9300 python -m server &
    cd ../..
    sleep 2
fi

echo "✅ All MCP servers deployment initiated!"
echo "📊 Check status with: python mcp-servers/health_check.py"
echo "🛑 Stop all with: pkill -f 'python -m server'"
