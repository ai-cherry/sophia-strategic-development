#!/bin/bash
# 🐳 BUILD DOCKER IMAGES DIRECTLY ON LAMBDA LABS K3S INSTANCE
# Builds images locally on the K3s cluster for immediate deployment

set -euo pipefail

# Configuration
LAMBDA_K3S_IP="192.222.58.232"
SSH_KEY_PATH="$HOME/.ssh/sophia2025_private_key"
SSH_USER="ubuntu"
REMOTE_BUILD_DIR="/tmp/sophia-build"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🐳 BUILDING SOPHIA AI IMAGES ON LAMBDA LABS${NC}"
echo -e "${BLUE}============================================${NC}"
echo "Target: $LAMBDA_K3S_IP"
echo "Strategy: Local K3s containerd images"
echo ""

# Function to run commands on the remote instance
run_remote() {
    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$SSH_USER@$LAMBDA_K3S_IP" "$1"
}

# Function to run commands with sudo
run_remote_sudo() {
    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$SSH_USER@$LAMBDA_K3S_IP" "sudo $1"
}

# Function to copy files to remote
copy_to_remote() {
    scp -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" -r "$1" "$SSH_USER@$LAMBDA_K3S_IP:$2"
}

echo -e "${BLUE}📋 Step 1: Preparing Remote Build Environment${NC}"

# Create remote build directory
run_remote "mkdir -p $REMOTE_BUILD_DIR"

# Copy essential files to remote
echo -e "${YELLOW}🔧 Copying source code...${NC}"
copy_to_remote "backend/" "$REMOTE_BUILD_DIR/"
copy_to_remote "frontend/" "$REMOTE_BUILD_DIR/"
copy_to_remote "mcp-servers/" "$REMOTE_BUILD_DIR/"
copy_to_remote "shared/" "$REMOTE_BUILD_DIR/"

# Create requirements.txt on remote
echo -e "${YELLOW}🔧 Creating requirements.txt...${NC}"
run_remote "cat > $REMOTE_BUILD_DIR/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
aiohttp==3.9.0
redis==5.0.1
psycopg2-binary==2.9.9
openai==1.3.0
anthropic==0.7.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
EOF"

echo -e "${GREEN}✅ Remote build environment ready${NC}"

echo -e "\n${BLUE}📋 Step 2: Building Images with K3s Containerd${NC}"

# Build backend image
echo -e "${YELLOW}🔧 Building sophia-backend...${NC}"
run_remote "cd $REMOTE_BUILD_DIR && cat > Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY shared/ ./shared/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV ENVIRONMENT=prod

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD [\"python\", \"-m\", \"backend.app.simple_fastapi\"]
EOF"

# Build using K3s ctr (containerd)
run_remote_sudo "cd $REMOTE_BUILD_DIR && k3s ctr images build --tag scoobyjava15/sophia-backend:latest -f Dockerfile.backend ."

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Built sophia-backend${NC}"
else
    echo -e "${RED}❌ Failed to build sophia-backend${NC}"
fi

# Build frontend image
echo -e "${YELLOW}🔧 Building sophia-frontend...${NC}"
run_remote "cd $REMOTE_BUILD_DIR && cat > Dockerfile.frontend << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY frontend/ .

# Build the application
RUN npm run build

# Install serve
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Serve the application
CMD [\"serve\", \"-s\", \"build\", \"-l\", \"3000\"]
EOF"

run_remote_sudo "cd $REMOTE_BUILD_DIR && k3s ctr images build --tag scoobyjava15/sophia-frontend:latest -f Dockerfile.frontend ."

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Built sophia-frontend${NC}"
else
    echo -e "${RED}❌ Failed to build sophia-frontend${NC}"
fi

# Build MCP orchestrator image
echo -e "${YELLOW}🔧 Building sophia-ai-mcp-orchestrator...${NC}"
run_remote "cd $REMOTE_BUILD_DIR && cat > Dockerfile.mcp << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY mcp-servers/ ./mcp-servers/
COPY backend/ ./backend/
COPY shared/ ./shared/

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=prod

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:9001/health || exit 1

# Default command
CMD [\"python\", \"-m\", \"mcp_servers.ai_memory.server\"]
EOF"

run_remote_sudo "cd $REMOTE_BUILD_DIR && k3s ctr images build --tag scoobyjava15/sophia-ai-mcp-orchestrator:latest -f Dockerfile.mcp ."

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Built sophia-ai-mcp-orchestrator${NC}"
else
    echo -e "${RED}❌ Failed to build sophia-ai-mcp-orchestrator${NC}"
fi

echo -e "\n${BLUE}📋 Step 3: Verifying Built Images${NC}"
run_remote_sudo "k3s ctr images list | grep scoobyjava15"

echo -e "\n${GREEN}🎉 Images built successfully on Lambda Labs K3s!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "${BLUE}📊 Available images for deployment:${NC}"
echo "  scoobyjava15/sophia-backend:latest"
echo "  scoobyjava15/sophia-frontend:latest" 
echo "  scoobyjava15/sophia-ai-mcp-orchestrator:latest"

echo -e "\n${BLUE}📋 Next: Restart deployments to use new images${NC}"
echo "  export KUBECONFIG=~/.kube/k3s-lambda-labs-tunnel"
echo "  kubectl rollout restart deployment -n sophia-ai-prod"
echo "  kubectl rollout restart deployment -n default"

echo -e "\n${YELLOW}🔧 Cleanup remote build directory...${NC}"
run_remote "rm -rf $REMOTE_BUILD_DIR"
echo -e "${GREEN}✅ Cleanup complete${NC}" 