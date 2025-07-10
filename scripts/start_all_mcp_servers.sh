#!/bin/bash
# Start All MCP Servers
# Generated on July 10, 2025

echo "🚀 Starting Sophia AI MCP Servers..."
echo "=================================="

# Set environment
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"

# Base directory
MCP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../mcp-servers" && pwd)"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to start a server
start_server() {
    local server_name=$1
    local port=$2
    local tier=$3
    
    echo -e "${YELLOW}Starting $server_name on port $port (Tier $tier)...${NC}"
    
    if [ -f "$MCP_DIR/$server_name/server.py" ]; then
        cd "$MCP_DIR/$server_name"
        python server.py > "/tmp/mcp_$server_name.log" 2>&1 &
        local pid=$!
        
        # Wait a moment to see if it starts successfully
        sleep 2
        
        if ps -p $pid > /dev/null; then
            echo -e "${GREEN}✅ $server_name started successfully (PID: $pid)${NC}"
            echo "$pid" > "/tmp/mcp_$server_name.pid"
        else
            echo -e "${RED}❌ $server_name failed to start${NC}"
            return 1
        fi
    elif [ -f "$MCP_DIR/$server_name/server_v2.py" ]; then
        cd "$MCP_DIR/$server_name"
        python server_v2.py > "/tmp/mcp_$server_name.log" 2>&1 &
        local pid=$!
        
        # Wait a moment to see if it starts successfully
        sleep 2
        
        if ps -p $pid > /dev/null; then
            echo -e "${GREEN}✅ $server_name started successfully (PID: $pid)${NC}"
            echo "$pid" > "/tmp/mcp_$server_name.pid"
        else
            echo -e "${RED}❌ $server_name failed to start${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ $server_name not implemented yet${NC}"
        return 1
    fi
}

# Function to check server status
check_status() {
    echo -e "\n${YELLOW}Checking server status...${NC}"
    echo "=========================="
    
    for pidfile in /tmp/mcp_*.pid; do
        if [ -f "$pidfile" ]; then
            server=$(basename "$pidfile" .pid | sed 's/mcp_//')
            pid=$(cat "$pidfile")
            
            if ps -p $pid > /dev/null; then
                echo -e "${GREEN}✅ $server is running (PID: $pid)${NC}"
            else
                echo -e "${RED}❌ $server is not running${NC}"
            fi
        fi
    done
}

# Main execution
echo "Starting Tier 1 (Primary) servers..."
start_server "ai_memory" 9000 1
start_server "snowflake_unified" 9001 1
start_server "gong" 9002 1
start_server "hubspot_unified" 9003 1
start_server "slack" 9004 1

echo -e "\nStarting Tier 2 (Secondary) servers..."
start_server "github" 9005 2
start_server "linear" 9006 2
start_server "asana" 9007 2
start_server "notion" 9008 2
start_server "codacy" 3008 2
start_server "portkey_admin" 9013 2
start_server "postgres" 9009 2

echo -e "\nStarting Tier 3 (Tertiary) servers..."
start_server "figma_context" 9010 3
start_server "lambda_labs_cli" 9011 3
start_server "ui_ux_agent" 9012 3
start_server "openrouter_search" 9014 3

# Check final status
check_status

echo -e "\n${GREEN}MCP Server startup complete!${NC}"
echo "Check logs in /tmp/mcp_*.log for details"
echo ""
echo "To stop all servers, run:"
echo "  ./scripts/stop_all_mcp_servers.sh"
echo ""
echo "To check status, run:"
echo "  ./scripts/check_mcp_status.sh" 