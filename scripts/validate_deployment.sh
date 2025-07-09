#!/bin/bash
# Comprehensive deployment validation script for Sophia AI

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Sophia AI Deployment Validation${NC}"
echo -e "${BLUE}===================================${NC}\n"

# Configuration - Updated with actual Lambda Labs IPs
MAIN_HOST="192.222.58.232"  # lynn-sophia-gh200-master-01
PLATFORM_HOST="192.222.58.232"  # sophia-platform-prod
MCP_HOST="165.1.69.44"  # sophia-mcp-prod
AI_HOST="192.222.58.232"  # sophia-ai-prod

# Try different hosts
API_URL="http://$MAIN_HOST"
FRONTEND_URL="https://app.sophia-intel.ai"
HEALTH_ENDPOINT="/health"
TIMEOUT=10

# Track overall status
OVERALL_STATUS=0

# Function to check endpoint
check_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    echo -ne "${YELLOW}Checking $name...${NC} "

    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$url" || echo "000")

    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✅ OK (HTTP $response)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $response)${NC}"
        OVERALL_STATUS=1
        return 1
    fi
}

# Function to check JSON health endpoint
check_health_endpoint() {
    local name=$1
    local url=$2

    echo -ne "${YELLOW}Checking $name health...${NC} "

    response=$(curl -s --connect-timeout $TIMEOUT "$url" 2>/dev/null)

    if [ $? -eq 0 ] && [ -n "$response" ]; then
        # Try to parse JSON
        if echo "$response" | jq . >/dev/null 2>&1; then
            status=$(echo "$response" | jq -r '.status // .healthy // "unknown"' 2>/dev/null)
            if [ "$status" = "healthy" ] || [ "$status" = "true" ] || [ "$status" = "ok" ]; then
                echo -e "${GREEN}✅ HEALTHY${NC}"
                echo -e "  Response: $(echo "$response" | jq -c .)"
                return 0
            else
                echo -e "${RED}❌ UNHEALTHY (status: $status)${NC}"
                echo -e "  Response: $(echo "$response" | jq -c .)"
                OVERALL_STATUS=1
                return 1
            fi
        else
            echo -e "${YELLOW}⚠️  Non-JSON response${NC}"
            echo -e "  Response: $response"
            return 0
        fi
    else
        echo -e "${RED}❌ UNREACHABLE${NC}"
        OVERALL_STATUS=1
        return 1
    fi
}

# Function to check MCP server
check_mcp_server() {
    local name=$1
    local port=$2
    local host=$3

    echo -ne "${YELLOW}Checking MCP $name on $host:$port...${NC} "

    # Try to connect to the port
    if timeout 5 bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        echo -e "${GREEN}✅ PORT OPEN${NC}"
        # Try health endpoint
        curl -s --connect-timeout 5 "http://$host:$port/health" >/dev/null 2>&1 && echo -e "  ${GREEN}Health endpoint responding${NC}" || echo -e "  ${YELLOW}No health endpoint${NC}"
        return 0
    else
        echo -e "${RED}❌ PORT CLOSED${NC}"
        OVERALL_STATUS=1
        return 1
    fi
}

echo -e "${BLUE}1. Frontend Validation${NC}"
echo -e "${BLUE}----------------------${NC}"
check_endpoint "Frontend Homepage" "$FRONTEND_URL"
check_endpoint "Frontend Assets" "$FRONTEND_URL/favicon.ico"

echo -e "\n${BLUE}2. Lambda Labs Instance Checks${NC}"
echo -e "${BLUE}------------------------------${NC}"
echo -e "${YELLOW}Main Instance ($MAIN_HOST):${NC}"
check_endpoint "Main Host HTTP" "http://$MAIN_HOST"
check_endpoint "Main API" "http://$MAIN_HOST:8000"
check_endpoint "Main Frontend" "http://$MAIN_HOST:3000"

echo -e "\n${YELLOW}Platform Instance ($PLATFORM_HOST):${NC}"
check_endpoint "Platform HTTP" "http://$PLATFORM_HOST"
check_endpoint "Platform API" "http://$PLATFORM_HOST:8000"

echo -e "\n${BLUE}3. MCP Server Validation${NC}"
echo -e "${BLUE}------------------------${NC}"
check_mcp_server "AI Memory" 9000 "$MCP_HOST"
check_mcp_server "Codacy" 3008 "$MCP_HOST"
check_mcp_server "Linear" 9004 "$MCP_HOST"
check_mcp_server "GitHub" 9001 "$MCP_HOST"
check_mcp_server "Slack" 9002 "$MCP_HOST"
check_mcp_server "HubSpot" 9003 "$MCP_HOST"

echo -e "\n${BLUE}4. Infrastructure Services${NC}"
echo -e "${BLUE}--------------------------${NC}"
check_endpoint "Prometheus (Main)" "http://$MAIN_HOST:9090" 401  # May require auth
check_endpoint "Grafana (Main)" "http://$MAIN_HOST:3001"

echo -e "\n${BLUE}5. DNS Resolution${NC}"
echo -e "${BLUE}-----------------${NC}"
for domain in "api.sophia-intel.ai" "app.sophia-intel.ai"; do
    echo -ne "${YELLOW}Resolving $domain...${NC} "
    if host "$domain" >/dev/null 2>&1; then
        ip=$(dig +short "$domain" | head -n1)
        echo -e "${GREEN}✅ OK ($ip)${NC}"
    else
        echo -e "${RED}❌ FAILED${NC}"
        OVERALL_STATUS=1
    fi
done

echo -e "\n${BLUE}6. Lambda Labs Instance Summary${NC}"
echo -e "${BLUE}-------------------------------${NC}"
echo -e "Main Instance (GH200): $MAIN_HOST"
echo -e "Platform Instance: $PLATFORM_HOST"
echo -e "MCP Instance: $MCP_HOST"
echo -e "AI Instance: $AI_HOST"

echo -e "\n${BLUE}================================${NC}"
if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ DEPLOYMENT VALIDATION PASSED${NC}"
    echo -e "${GREEN}All checks completed successfully!${NC}"
else
    echo -e "${RED}❌ DEPLOYMENT VALIDATION FAILED${NC}"
    echo -e "${RED}Some checks failed. Please investigate.${NC}"
    echo -e "\n${YELLOW}Note: Services may still be deploying via GitHub Actions.${NC}"
    echo -e "${YELLOW}Check: https://github.com/ai-cherry/sophia-main/actions${NC}"
fi
echo -e "${BLUE}================================${NC}"

# Return overall status
exit $OVERALL_STATUS
