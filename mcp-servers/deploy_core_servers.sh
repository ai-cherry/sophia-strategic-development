#!/bin/bash
# Deploy Core MCP Servers - Fixed Version
# Uses standalone MCP base to avoid import dependencies

set -e

echo "🚀 DEPLOYING CORE MCP SERVERS (FIXED VERSION)"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Core servers to deploy
declare -A SERVERS=(
    ["hubspot"]="9006"
    ["asana"]="9100" 
    ["linear"]="9101"
    ["github"]="9103"
    ["gong"]="9200"
)

# Function to check if port is available
check_port() {
    local port="$1"
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# Function to test server health
test_server_health() {
    local server_name="$1"
    local port="$2"
    local timeout=10

    print_status "$BLUE" "🧪 Testing $server_name health..."

    for i in $(seq 1 "$timeout"); do
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
            print_status "$GREEN" "✅ $server_name is healthy on port $port"
            return 0
        fi
        sleep 1
    done

    print_status "$RED" "❌ $server_name health check failed"
    return 1
}

# Function to copy standalone base to server directory
setup_server_base() {
    local server_name="$1"
    local server_dir="$server_name"
    
    if [ -d "$server_dir" ]; then
        print_status "$BLUE" "📋 Setting up $server_name base..."
        cp base/standalone_mcp_base_v2.py "$server_dir/"
        print_status "$GREEN" "✅ Base copied to $server_name"
    else
        print_status "$RED" "❌ Server directory $server_dir not found"
        return 1
    fi
}

# Function to start a server
start_server() {
    local server_name="$1"
    local port="$2"
    local server_dir="$server_name"
    
    print_status "$BLUE" "🚀 Starting $server_name on port $port..."
    
    # Check if fixed version exists, otherwise use original
    local server_file=""
    if [ -f "$server_dir/${server_name}_mcp_server_fixed.py" ]; then
        server_file="${server_name}_mcp_server_fixed.py"
    elif [ -f "$server_dir/${server_name}_mcp_server.py" ]; then
        server_file="${server_name}_mcp_server.py"
    else
        print_status "$RED" "❌ No server file found for $server_name"
        return 1
    fi
    
    cd "$server_dir"
    
    # Set environment variables
    export MCP_SERVER_PORT="$port"
    export ENVIRONMENT="prod"
    export PULUMI_ORG="scoobyjava-org"
    
    # Start server in background
    python "$server_file" > "../logs/${server_name}.log" 2>&1 &
    local pid=$!
    echo "$pid" > "../logs/${server_name}.pid"
    
    print_status "$GREEN" "✅ Started $server_name (PID: $pid)"
    cd ..
    
    # Wait for startup
    sleep 3
    
    # Test health
    if test_server_health "$server_name" "$port"; then
        print_status "$GREEN" "✅ $server_name is operational"
        return 0
    else
        print_status "$RED" "❌ $server_name failed to start properly"
        return 1
    fi
}

# Main deployment process
main() {
    print_status "$BLUE" "🔍 Phase 1: Pre-deployment Checks"
    
    # Create logs directory
    mkdir -p logs
    
    # Check port availability
    for server in "${!SERVERS[@]}"; do
        port="${SERVERS[$server]}"
        if check_port "$port"; then
            print_status "$GREEN" "✅ Port $port available for $server"
        else
            print_status "$YELLOW" "⚠️  Port $port in use for $server (will attempt restart)"
        fi
    done
    
    print_status "$BLUE" "🔧 Phase 2: Server Base Setup"
    
    # Setup standalone base for each server
    for server in "${!SERVERS[@]}"; do
        setup_server_base "$server"
    done
    
    print_status "$BLUE" "🚀 Phase 3: Server Deployment"
    
    # Deploy servers
    local success_count=0
    local total_count=${#SERVERS[@]}
    
    for server in "${!SERVERS[@]}"; do
        port="${SERVERS[$server]}"
        if start_server "$server" "$port"; then
            ((success_count++))
        fi
    done
    
    print_status "$BLUE" "📊 Phase 4: Deployment Summary"
    echo ""
    echo "Deployment Results:"
    echo "=================="
    echo "Total Servers: $total_count"
    echo "Successful: $success_count"
    echo "Failed: $((total_count - success_count))"
    echo ""
    
    if [ "$success_count" -eq "$total_count" ]; then
        print_status "$GREEN" "🎉 ALL SERVERS DEPLOYED SUCCESSFULLY!"
        echo ""
        echo "🔍 Test Commands:"
        for server in "${!SERVERS[@]}"; do
            port="${SERVERS[$server]}"
            echo "curl -s http://localhost:$port/health | jq ."
        done
        echo ""
        echo "📊 Health Check: python health_check.py"
        echo "🛑 Stop All: pkill -f 'python.*mcp_server'"
        
        return 0
    else
        print_status "$RED" "❌ Some servers failed to deploy"
        echo ""
        echo "📋 Check logs in logs/ directory for details"
        echo "🔧 Fix issues and re-run deployment"
        
        return 1
    fi
}

# Run main deployment
main

print_status "$BLUE" "🎯 Next Steps:"
echo ""
echo "1. Verify all servers: bash scripts/test_all_servers.sh"
echo "2. Load testing: bash scripts/load_test_servers.sh" 
echo "3. Production deployment: bash scripts/deploy_to_kubernetes.sh" 