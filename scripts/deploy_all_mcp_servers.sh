#!/bin/bash

# Deploy All MCP Servers
echo "🚀 Deploying All MCP Servers..."

# Set project root
PROJECT_ROOT="/Users/lynnmusil/sophia-main"
cd "$PROJECT_ROOT"

# Export Python path
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Kill any existing processes on MCP ports
echo "Cleaning up existing processes..."
for port in 9001 3008 9003 9004 9006 9100 9101 9102 9105; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done

# Start each MCP server
echo "Starting MCP servers..."

# AI Memory (port 9001)
echo "Starting AI Memory on port 9001..."
MCP_SERVER_PORT=9001 python mcp-servers/ai_memory/server.py > logs/ai_memory.log 2>&1 &
echo "  PID: $!"

# Codacy (port 3008)
echo "Starting Codacy on port 3008..."
MCP_SERVER_PORT=3008 python mcp-servers/codacy/server.py > logs/codacy.log 2>&1 &
echo "  PID: $!"

# GitHub (port 9003)
echo "Starting GitHub on port 9003..."
MCP_SERVER_PORT=9003 python mcp-servers/github/server.py > logs/github.log 2>&1 &
echo "  PID: $!"

# Asana (port 9006)
echo "Starting Asana on port 9006..."
MCP_SERVER_PORT=9006 python mcp-servers/asana/server.py > logs/asana.log 2>&1 &
echo "  PID: $!"

# Slack (port 9101)
echo "Starting Slack on port 9101..."
MCP_SERVER_PORT=9101 python mcp-servers/slack/server.py > logs/slack.log 2>&1 &
echo "  PID: $!"

# Sleep to let servers start
echo "Waiting for servers to start..."
sleep 5

# Check status
echo ""
echo "📊 MCP Server Status:"
echo "====================="

for port in 9001 3008 9003 9006 9101; do
    if lsof -ti:$port > /dev/null; then
        echo "✅ Port $port: Running"
    else
        echo "❌ Port $port: Not running"
    fi
done

echo ""
echo "Logs available in:"
echo "  tail -f logs/ai_memory.log"
echo "  tail -f logs/codacy.log"
echo "  tail -f logs/github.log"
echo "  tail -f logs/asana.log"
echo "  tail -f logs/slack.log" 