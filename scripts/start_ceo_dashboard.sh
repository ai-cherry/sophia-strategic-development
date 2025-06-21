#!/bin/bash

# Sophia AI CEO Dashboard Quick Start Script
# This script ensures everything is ready for your CEO dashboard

echo "🚀 Sophia AI CEO Dashboard Quick Start"
echo "====================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ Please run this script from the sophia-main directory${NC}"
    exit 1
fi

# Set environment variables
export SOPHIA_ADMIN_KEY=${SOPHIA_ADMIN_KEY:-"sophia_admin_2024"}
export BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}

echo -e "${BLUE}📋 Configuration:${NC}"
echo "   Backend URL: $BACKEND_URL"
echo "   Admin Key: $SOPHIA_ADMIN_KEY"
echo ""

# Function to check if backend is running
check_backend() {
    curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health
}

# Check if backend is already running
echo -e "${BLUE}🔍 Checking backend status...${NC}"
if [ "$(check_backend)" == "200" ]; then
    echo -e "${GREEN}✅ Backend is already running!${NC}"
else
    echo -e "${YELLOW}⚠️  Backend is not running. Starting it now...${NC}"

    # Start backend in background with proper Python path
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    cd backend
    python3 main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..

    # Wait for backend to start
    echo -n "   Waiting for backend to start"
    for i in {1..30}; do
        if [ "$(check_backend)" == "200" ]; then
            echo -e "\n${GREEN}✅ Backend started successfully!${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done

    if [ "$(check_backend)" != "200" ]; then
        echo -e "\n${RED}❌ Backend failed to start. Check backend.log for errors.${NC}"
        exit 1
    fi
fi

# Run the deployment validation
echo -e "\n${BLUE}🧪 Running deployment validation...${NC}"
cd scripts
python3 deploy_ceo_dashboard.py
cd ..

# Check if validation passed
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ CEO Dashboard is ready!${NC}"
    echo ""
    echo -e "${BLUE}📊 Next Steps:${NC}"
    echo "1. Open Retool (https://retool.com)"
    echo "2. Create a new app called 'Sophia CEO Dashboard'"
    echo "3. Add REST API resource:"
    echo "   - Name: SophiaAPI"
    echo "   - Base URL: $BACKEND_URL"
    echo "   - Headers: X-Admin-Key = $SOPHIA_ADMIN_KEY"
    echo "4. Import configuration from: retool_ceo_dashboard_config.json"
    echo ""
    echo -e "${BLUE}🔧 Quick Test Commands:${NC}"
    echo "# Test dashboard summary:"
    echo "curl -H \"X-Admin-Key: $SOPHIA_ADMIN_KEY\" $BACKEND_URL/api/retool/executive/dashboard-summary"
    echo ""
    echo "# Test strategic chat:"
    echo "curl -X POST -H \"X-Admin-Key: $SOPHIA_ADMIN_KEY\" -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"message\": \"What is our client health status?\", \"mode\": \"internal\"}' \\"
    echo "     $BACKEND_URL/api/retool/executive/strategic-chat"
    echo ""
    echo -e "${GREEN}🎉 Your executive command center is ready for use!${NC}"
else
    echo -e "\n${RED}❌ Validation failed. Please check the errors above.${NC}"
    exit 1
fi

# Keep backend running message
if [ ! -z "$BACKEND_PID" ]; then
    echo ""
    echo -e "${YELLOW}📌 Note: Backend is running in background (PID: $BACKEND_PID)${NC}"
    echo "   To stop it: kill $BACKEND_PID"
    echo "   To view logs: tail -f backend.log"
fi
