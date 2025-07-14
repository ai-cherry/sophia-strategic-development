#!/bin/bash
# Build and push all Sophia AI containers
# "Building containers like we're preparing for the apocalypse"

set -e

# Configuration
DOCKER_REGISTRY="scoobyjava15"
VERSION="${VERSION:-latest}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐳 SOPHIA AI CONTAINER BUILD FACTORY${NC}"
echo -e "${BLUE}=====================================\033[0m"

# Function to build and push image
build_and_push() {
    local name=$1
    local context=$2
    local dockerfile=$3
    
    echo -e "\n${YELLOW}Building $name...${NC}"
    
    docker build -f "$dockerfile" -t "$DOCKER_REGISTRY/$name:$VERSION" "$context"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Built $name${NC}"
        
        echo -e "${YELLOW}Pushing $name...${NC}"
        docker push "$DOCKER_REGISTRY/$name:$VERSION"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Pushed $name${NC}"
        else
            echo -e "${RED}❌ Failed to push $name${NC}"
        fi
    else
        echo -e "${RED}❌ Failed to build $name${NC}"
    fi
}

# Login to Docker Hub
echo -e "${YELLOW}Logging into Docker Hub...${NC}"
echo "$DOCKER_HUB_TOKEN" | docker login -u "$DOCKER_REGISTRY" --password-stdin || {
    echo -e "${RED}❌ Docker login failed. Set DOCKER_HUB_TOKEN environment variable${NC}"
    exit 1
}

# Build Backend
echo -e "\n${BLUE}Building Backend...${NC}"
cat > backend/Dockerfile << 'EOF'
FROM python:3.12-slim

# Install build dependencies for modern_stack-connector
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libssl-dev \
    rustc \
    cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["uvicorn", "app.unified_chat_backend:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

build_and_push "sophia-backend" "backend" "backend/Dockerfile"

# Build MCP Base Image
echo -e "\n${BLUE}Building MCP Base Image...${NC}"
cat > mcp-servers/Dockerfile.base << 'EOF'
FROM python:3.12-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install base dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    modern_stack-connector-python \
    redis \
    pydantic \
    httpx \
    prometheus-client

# Copy base classes
COPY base/ ./base/
EOF

build_and_push "mcp-base" "mcp-servers" "mcp-servers/Dockerfile.base"

# Build each MCP server
MCP_SERVERS=(
    "ai_memory:9001"
    "codacy:3008"
    "github:9003"
    "linear:9004"
    "asana:9006"
    "notion:9102"
    "slack:9101"
)

for server_config in "${MCP_SERVERS[@]}"; do
    IFS=':' read -r server port <<< "$server_config"
    
    echo -e "\n${BLUE}Building MCP $server...${NC}"
    
    # Create server-specific Dockerfile
    cat > "mcp-servers/$server/Dockerfile" << EOF
FROM $DOCKER_REGISTRY/mcp-base:$VERSION

WORKDIR /app

# Copy server-specific code
COPY . .

# Expose port
EXPOSE $port

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
  CMD curl -f http://localhost:$port/health || exit 1

# Run the server
CMD ["python", "-m", "uvicorn", "${server}_mcp_server:app", "--host", "0.0.0.0", "--port", "$port"]
EOF

    # Check if server directory exists
    if [ -d "mcp-servers/$server" ]; then
        build_and_push "mcp-$server" "mcp-servers/$server" "mcp-servers/$server/Dockerfile"
    else
        echo -e "${YELLOW}⚠️  Directory mcp-servers/$server not found - creating stub${NC}"
        mkdir -p "mcp-servers/$server"
        
        # Create a stub server file
        cat > "mcp-servers/$server/${server}_mcp_server.py" << EOF
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="MCP $server Server")

@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy", "service": "mcp-$server"})

@app.get("/")
async def root():
    return {"message": "MCP $server Server - Stub Implementation"}
EOF
        
        build_and_push "mcp-$server" "mcp-servers/$server" "mcp-servers/$server/Dockerfile"
    fi
done

# Build Redis (using official image with custom config)
echo -e "\n${BLUE}Creating Redis configuration...${NC}"
cat > redis.conf << 'EOF'
# Redis configuration for Sophia AI
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
EOF

# Summary
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}🎉 CONTAINER BUILD COMPLETE!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "\n${YELLOW}Images built and pushed:${NC}"
echo -e "- $DOCKER_REGISTRY/sophia-backend:$VERSION"
echo -e "- $DOCKER_REGISTRY/mcp-base:$VERSION"
for server_config in "${MCP_SERVERS[@]}"; do
    IFS=':' read -r server port <<< "$server_config"
    echo -e "- $DOCKER_REGISTRY/mcp-$server:$VERSION"
done

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Deploy to K3s: kubectl apply -f k8s-deployment/"
echo -e "2. Check rollout: kubectl rollout status -n sophia-ai deployment/sophia-backend"
echo -e "3. View logs: kubectl logs -n sophia-ai -l app=sophia-backend"

echo -e "\n${BLUE}Remember: ${NC}"
echo -e "${RED}\"Containers are like children - they'll embarrass you in production\"${NC}" 