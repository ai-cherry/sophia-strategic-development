#!/bin/bash
# Check what Sophia AI services are currently running locally

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Sophia AI Local Services Check ===${NC}"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Docker is not running!${NC}"
    echo "Please start Docker Desktop first."
    exit 1
fi

# Check Docker containers
echo -e "${BLUE}Docker Containers:${NC}"
containers=$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | tail -n +2)
if [ -z "$containers" ]; then
    echo "  No containers running"
else
    echo "$containers" | while IFS= read -r line; do
        echo "  $line"
    done
fi
echo ""

# Check specific ports
echo -e "${BLUE}Port Status:${NC}"
check_port() {
    local port=$1
    local service=$2
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Port $port: $service is running"
    else
        echo -e "  ${RED}✗${NC} Port $port: $service is not running"
    fi
}

# Core services
check_port 8000 "Backend API"
check_port 3000 "Frontend"
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"

echo ""

# MCP servers
echo -e "${BLUE}MCP Servers:${NC}"
check_port 9001 "AI Memory MCP"
check_port 9100 "Dashboard MCP"
check_port 9101 "Chat MCP"
check_port 3008 "Codacy MCP"
check_port 9030 "Prompt Optimizer MCP"

echo ""

# Check if running locally or need to deploy to Lambda Labs
echo -e "${BLUE}Next Steps:${NC}"
if docker ps | grep -q sophia; then
    echo -e "${YELLOW}Local services detected.${NC}"
    echo "To deploy to Lambda Labs (Docker Cloud):"
    echo "  1. Stop local services: docker-compose down"
    echo "  2. Run: ./scripts/prepare_deployment_package.sh"
    echo "  3. Upload and deploy to Lambda Labs"
else
    echo -e "${GREEN}No local services running.${NC}"
    echo "Ready to deploy to Lambda Labs:"
    echo "  1. Run: ./scripts/prepare_deployment_package.sh"
    echo "  2. Upload package to Lambda Labs"
    echo "  3. Run deployment script on Lambda Labs"
fi

echo ""
echo -e "${BLUE}Lambda Labs Access:${NC}"
echo "After deployment, access services at:"
echo "  - API: http://104.171.202.64:8000"
echo "  - Frontend: http://104.171.202.64:3000"
echo "  - API Docs: http://104.171.202.64:8000/docs"
