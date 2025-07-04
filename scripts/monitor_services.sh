#!/bin/bash

# Sophia AI Services Monitoring Script
# Monitor existing services and display status

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Sophia AI Services Monitor${NC}"
echo "================================"

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local description=$3
    
    echo -n -e "${YELLOW}Checking $description...${NC} "
    
    if curl -s -f -o /dev/null "$url" 2>/dev/null; then
        echo -e "${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Unreachable${NC}"
        return 1
    fi
}

# Display running containers
echo -e "\n${BLUE}📦 Running Containers${NC}"
echo "===================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(sophia|postgres|redis|grafana|prometheus)" || echo "No Sophia-related containers found"

# Check services
echo -e "\n${BLUE}🌐 Service Health Checks${NC}"
echo "======================"

# Check existing services
check_service "grafana" "http://localhost:3001" "Grafana (Port 3001)"
check_service "prometheus" "http://localhost:9090" "Prometheus (Port 9090)"
check_service "postgres" "localhost:5432" "PostgreSQL (Port 5432)" || true
check_service "redis" "localhost:6379" "Redis (Port 6379)" || true

# Check for Sophia backend on various ports
echo -e "\n${BLUE}🔍 Checking for Sophia Backend${NC}"
echo "============================"
for port in 8000 8001 8002 8003; do
    if check_service "sophia-$port" "http://localhost:$port/health" "Sophia Backend (Port $port)"; then
        echo -e "${GREEN}Found Sophia Backend on port $port!${NC}"
        break
    fi
done

# Display resource usage
echo -e "\n${BLUE}📊 Resource Usage${NC}"
echo "==============="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "(sophia|postgres|redis|grafana|prometheus)" || echo "No stats available"

# Display Grafana access info
echo -e "\n${BLUE}📈 Monitoring Access${NC}"
echo "=================="
echo -e "Grafana:     ${GREEN}http://localhost:3001${NC} (admin/admin)"
echo -e "Prometheus:  ${GREEN}http://localhost:9090${NC}"

# Show recent logs from any Sophia containers
echo -e "\n${BLUE}📜 Recent Logs (if any)${NC}"
echo "===================="
for container in $(docker ps --format "{{.Names}}" | grep sophia); do
    echo -e "\n${YELLOW}Logs from $container:${NC}"
    docker logs "$container" --tail 10 2>&1 | head -20
done

echo -e "\n${GREEN}✅ Monitoring complete${NC}" 