#!/bin/bash
# Sophia AI Focused Deployment Script
# Simple, practical deployment without unnecessary complexity

set -e

echo "🚀 Sophia AI Focused Deployment"
echo "=============================="
echo "Starting simple deployment process..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1 successful${NC}"
    else
        echo -e "${RED}❌ $1 failed${NC}"
        exit 1
    fi
}

# Phase 1: Frontend Configuration
echo -e "\n${YELLOW}Phase 1: Frontend Configuration${NC}"
echo "--------------------------------"

if [ -d "frontend" ]; then
    cd frontend

    # Create production environment file
    cat > .env.production << 'EOF'
VITE_API_URL=https://api.sophia-intel.ai
VITE_WS_URL=wss://api.sophia-intel.ai
VITE_ENVIRONMENT=production
EOF

    check_status "Frontend environment configuration"

    # Go back to root
    cd ..
else
    echo -e "${RED}❌ Frontend directory not found${NC}"
    exit 1
fi

# Create simple Vercel configuration
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "buildCommand": "cd frontend && npm install && npm run build",
        "outputDirectory": "frontend/dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.sophia-intel.ai/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/dist/$1"
    }
  ]
}
EOF

check_status "Vercel configuration"

# Phase 2: Backend API Check
echo -e "\n${YELLOW}Phase 2: Backend API Preparation${NC}"
echo "---------------------------------"

# Create simple health check endpoint if main.py doesn't exist
if [ ! -f "backend/main.py" ]; then
    cat > backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Sophia AI API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.sophia-intel.ai",
        "https://sophia-intel.ai",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Sophia AI API", "status": "operational"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "sophia-ai-api",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/api/v1/dashboard/main")
async def dashboard_main():
    return {
        "metrics": {
            "total_users": 1,
            "active_sessions": 1,
            "api_calls_today": 100,
            "system_health": "operational"
        },
        "status": "success"
    }

# Import additional routes if they exist
try:
    from backend.api import unified_chat_routes
    app.include_router(unified_chat_routes.router, prefix="/api/v1")
except ImportError:
    pass
EOF

    check_status "Backend main.py creation"
fi

# Phase 3: Essential MCP Servers
echo -e "\n${YELLOW}Phase 3: Essential MCP Server Configuration${NC}"
echo "-------------------------------------------"

# Create docker-compose for essential MCP servers only
cat > docker-compose.mcp-essential.yml << 'EOF'
version: '3.8'

services:
  ai-memory:
    build:
      context: ./mcp-servers/ai-memory
      dockerfile: Dockerfile
    container_name: sophia-mcp-ai-memory
    ports:
      - "9001:9001"
    environment:
      - PORT=9001
      - ENVIRONMENT=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  snowflake:
    build:
      context: ./mcp-servers/snowflake_unified
      dockerfile: Dockerfile
    container_name: sophia-mcp-snowflake
    ports:
      - "9002:9002"
    environment:
      - PORT=9002
      - ENVIRONMENT=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  unified-intelligence:
    build:
      context: ./mcp-servers/sophia_intelligence_unified
      dockerfile: Dockerfile
    container_name: sophia-mcp-intelligence
    ports:
      - "9005:9005"
    environment:
      - PORT=9005
      - ENVIRONMENT=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9005/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  slack:
    build:
      context: ./mcp-servers/slack_unified
      dockerfile: Dockerfile
    container_name: sophia-mcp-slack
    ports:
      - "9103:9103"
    environment:
      - PORT=9103
      - ENVIRONMENT=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9103/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  github:
    build:
      context: ./mcp-servers/github
      dockerfile: Dockerfile
    container_name: sophia-mcp-github
    ports:
      - "9104:9104"
    environment:
      - PORT=9104
      - ENVIRONMENT=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9104/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  default:
    name: sophia-mcp-network
EOF

check_status "Docker Compose configuration for MCP servers"

# Phase 4: Create Health Check Script
echo -e "\n${YELLOW}Phase 4: Creating Health Check Script${NC}"
echo "-------------------------------------"

cat > health_check.sh << 'EOF'
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
EOF

chmod +x health_check.sh
check_status "Health check script creation"

# Summary
echo -e "\n${GREEN}🎉 Deployment Preparation Complete!${NC}"
echo "===================================="
echo ""
echo "Next Steps:"
echo "1. Deploy frontend: cd frontend && vercel --prod"
echo "2. Deploy backend to Lambda Labs (see instructions below)"
echo "3. Deploy essential MCP servers: docker-compose -f docker-compose.mcp-essential.yml up -d"
echo "4. Run health check: ./health_check.sh"
echo ""
echo "Backend Deployment to Lambda Labs:"
echo "ssh ubuntu@146.235.200.1 'cd /opt/sophia-ai && git pull && docker-compose restart backend'"
echo ""
echo "Remember: Start simple, get it working, then improve!"
