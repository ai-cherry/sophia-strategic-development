#!/bin/bash
# Fixed MCP Servers Deployment Script
set -e

echo "🚀 Deploying Sophia AI MCP Servers (FIXED VERSION)..."

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

# Function to start a server if it exists
start_server() {
    local server_name=$1
    local port=$2
    local server_dir="$server_name"

    if [ -d "$server_dir" ] && [ -f "$server_dir/${server_name}_mcp_server.py" ]; then
        echo "🚀 Starting $server_name on port $port..."
        cd "$server_dir"

        # Set environment variables
        export MCP_SERVER_PORT=$port
        export ENVIRONMENT=prod
        export PULUMI_ORG=scoobyjava-org

        # Start the server in background
        python "${server_name}_mcp_server.py" --port $port > "../${server_name}.log" 2>&1 &
        local pid=$!
        echo "  ✅ Started $server_name (PID: $pid) on port $port"
        echo "$pid" > "../${server_name}.pid"

        cd ..
        sleep 2
    else
        echo "  ⚠️  Server $server_name not found or missing main file"
    fi
}

# Check all required ports first
echo "🔍 Checking port availability..."
check_port 9000 || echo "Warning: ai_memory port 9000 conflict"
check_port 9300 || echo "Warning: codacy port 9300 conflict"
check_port 9100 || echo "Warning: asana port 9100 conflict"

echo ""
echo "📦 Starting MCP servers..."

# Start core AI services first
echo "🧠 Starting core AI services..."
start_server "ai_memory" 9000
start_server "codacy" 9300

# Start integration services
echo "🔌 Starting integration services..."
start_server "asana" 9100

# Wait a moment for servers to initialize
echo "⏳ Waiting for servers to initialize..."
sleep 5

echo ""
echo "✅ MCP servers deployment completed!"
echo "📊 Check status with: python health_check.py"
echo "📋 View logs: tail -f *.log"
echo "🛑 Stop all with: pkill -f 'python.*mcp_server.py'"
echo ""
echo "📝 Server PIDs saved in *.pid files"
echo "📄 Server logs available in *.log files"
