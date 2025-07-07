#!/bin/bash
# Sophia AI Health Check Script

echo "🏥 Sophia AI Health Check"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check Frontend
echo -n "Frontend (app.sophia-intel.ai): "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://app.sophia-intel.ai || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK ($HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Failed ($HTTP_CODE)${NC}"
fi

# Check API
echo -n "API (api.sophia-intel.ai): "
if curl -s https://api.sophia-intel.ai/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not responding${NC}"
fi

# Check Essential MCP Servers (if running locally)
echo ""
echo "Essential MCP Servers:"
for port in 9001 9002 9005 9103 9104; do
    echo -n "  Port $port: "
    if curl -s localhost:$port/health 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}✅ Healthy${NC}"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi
done

echo ""
echo "Health check complete!"
