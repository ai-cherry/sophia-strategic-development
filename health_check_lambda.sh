#!/bin/bash
# Sophia AI Health Check Script - Lambda Labs Deployment
# This script checks services deployed on Lambda Labs, not locally

echo "🏥 Sophia AI Health Check (Lambda Labs Deployment)"
echo "================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Lambda Labs server
LAMBDA_HOST="192.222.58.232"

# Check Frontend (Vercel)
echo "📱 Frontend Services:"
echo -n "  app.sophia-intel.ai: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://app.sophia-intel.ai || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK ($HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Failed ($HTTP_CODE)${NC}"
fi

# Check Backend API (Lambda Labs)
echo ""
echo "🖥️  Backend Services (Lambda Labs):"
echo -n "  api.sophia-intel.ai: "
if curl -s https://api.sophia-intel.ai/health 2>/dev/null | grep -q "healthy"; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not responding${NC}"
fi

# Check MCP Servers on Lambda Labs
echo ""
echo "🤖 MCP Servers (Lambda Labs - $LAMBDA_HOST):"
echo -e "${YELLOW}Note: MCP servers should be running on Lambda Labs, not locally${NC}"

# Check if we can SSH to Lambda Labs
if command -v ssh &> /dev/null && ssh -o ConnectTimeout=5 -o BatchMode=yes ubuntu@$LAMBDA_HOST exit 2>/dev/null; then
    echo "Checking MCP servers via SSH..."
    ssh ubuntu@$LAMBDA_HOST << 'EOF'
    for port in 9001 9002 9005 9103 9104; do
        SERVICE_NAME=""
        case $port in
            9001) SERVICE_NAME="AI Memory" ;;
            9002) SERVICE_NAME="qdrant" ;;
            9005) SERVICE_NAME="Unified Intelligence" ;;
            9103) SERVICE_NAME="Slack" ;;
            9104) SERVICE_NAME="GitHub" ;;
        esac

        echo -n "  Port $port ($SERVICE_NAME): "
        if curl -s localhost:$port/health 2>/dev/null | grep -q "healthy"; then
            echo -e "\033[0;32m✅ Healthy\033[0m"
        else
            echo -e "\033[0;31m❌ Not responding\033[0m"
        fi
    done
EOF
else
    echo -e "${YELLOW}⚠️  Cannot SSH to Lambda Labs. To check MCP servers, run:${NC}"
    echo "   ssh ubuntu@$LAMBDA_HOST"
    echo "   Then check ports 9001, 9002, 9005, 9103, 9104"
fi

# Summary
echo ""
echo "📊 Deployment Architecture:"
echo "  • Frontend: Vercel (app.sophia-intel.ai)"
echo "  • Backend API: Lambda Labs (api.sophia-intel.ai)"
echo "  • MCP Servers: Lambda Labs (internal ports 9001-9104)"
echo "  • Database: Lambda Labs (PostgreSQL + Redis)"
echo ""
echo -e "${YELLOW}💡 Tip: MCP servers are not exposed to the internet.${NC}"
echo "   Access them through the backend API proxy endpoints."
echo ""
echo "Health check complete!"
