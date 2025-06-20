#!/bin/bash

# Sophia AI - Start All Services for Dashboard Deployment
# This script starts all necessary services for the Retool dashboards

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Sophia AI - Starting All Services${NC}"
echo -e "${BLUE}============================================${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check prerequisites
echo -e "\n${BLUE}Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker from https://www.docker.com"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from template...${NC}"
    if [ -f env.template ]; then
        cp env.template .env
        echo -e "${GREEN}✓ Created .env file from template${NC}"
        echo -e "${YELLOW}Please edit .env and add your API keys before continuing${NC}"
        exit 1
    else
        echo -e "${RED}✗ No env.template file found${NC}"
        exit 1
    fi
fi

# Start Backend API
echo -e "\n${BLUE}Starting Backend API...${NC}"
if port_in_use 8000; then
    echo -e "${YELLOW}⚠ Backend already running on port 8000${NC}"
else
    echo "Starting backend in background..."
    cd backend && python main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..

    # Wait for backend to start
    echo -n "Waiting for backend to start"
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo -e "\n${GREEN}✓ Backend started successfully${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done

    if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "\n${RED}✗ Backend failed to start${NC}"
        echo "Check backend.log for errors"
        exit 1
    fi
fi

# Start MCP Servers
echo -e "\n${BLUE}Starting MCP Servers...${NC}"

# Start only the essential MCP servers for dashboards
ESSENTIAL_MCP_SERVERS=(
    "gong-mcp"
    "slack-mcp"
    "snowflake-mcp"
    "pinecone-mcp"
    "linear-mcp"
    "retool-mcp"
    "claude-mcp"
    "ai-memory-mcp"
    "knowledge-mcp"
)

echo "Starting essential MCP servers..."
docker-compose up -d ${ESSENTIAL_MCP_SERVERS[@]} 2>/dev/null

# Check MCP server status
echo -e "\n${BLUE}Checking MCP Server Status...${NC}"
sleep 5  # Give servers time to start

RUNNING_SERVERS=$(docker-compose ps --services --filter "status=running" 2>/dev/null)
for server in "${ESSENTIAL_MCP_SERVERS[@]}"; do
    if echo "$RUNNING_SERVERS" | grep -q "^$server$"; then
        echo -e "${GREEN}✓ $server${NC}"
    else
        echo -e "${RED}✗ $server${NC}"
    fi
done

# Start MCP Gateway
echo -e "\n${BLUE}Starting MCP Gateway...${NC}"
if port_in_use 8090; then
    echo -e "${YELLOW}⚠ MCP Gateway already running on port 8090${NC}"
else
    docker-compose up -d mcp-gateway 2>/dev/null
    sleep 3
    if curl -s http://localhost:8090/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ MCP Gateway started${NC}"
    else
        echo -e "${YELLOW}⚠ MCP Gateway may not be ready yet${NC}"
    fi
fi

# Test integrations
echo -e "\n${BLUE}Testing Integrations...${NC}"

# Test Snowflake
echo -n "Testing Snowflake connection..."
if curl -s -H "X-Admin-Key: sophia_admin_2024" \
     http://localhost:8000/api/integrations/snowflake/test >/dev/null 2>&1; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${RED}✗${NC}"
fi

# Test Gong
echo -n "Testing Gong connection..."
if curl -s -H "X-Admin-Key: sophia_admin_2024" \
     http://localhost:8000/api/integrations/gong/test >/dev/null 2>&1; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${RED}✗${NC}"
fi

# Test Slack
echo -n "Testing Slack connection..."
if curl -s -H "X-Admin-Key: sophia_admin_2024" \
     http://localhost:8000/api/integrations/slack/test >/dev/null 2>&1; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${RED}✗${NC}"
fi

# Summary
echo -e "\n${BLUE}============================================${NC}"
echo -e "${BLUE}Service Status Summary${NC}"
echo -e "${BLUE}============================================${NC}"

echo -e "\n${GREEN}Services Running:${NC}"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo "- MCP Gateway: http://localhost:8090"

echo -e "\n${BLUE}Next Steps:${NC}"
echo "1. Run the deployment script:"
echo "   python scripts/deploy_all_dashboards.py"
echo ""
echo "2. Open Retool and create three apps:"
echo "   - Sophia CEO Dashboard"
echo "   - Sophia Knowledge Admin"
echo "   - Sophia Project Intelligence"
echo ""
echo "3. Follow the deployment guide that will be generated"

echo -e "\n${YELLOW}To stop all services:${NC}"
echo "docker-compose down"
if [ ! -z "$BACKEND_PID" ]; then
    echo "kill $BACKEND_PID  # Stop backend"
fi

echo -e "\n${GREEN}All services started successfully!${NC}"
