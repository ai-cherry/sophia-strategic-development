#!/bin/bash
# 🐳 BUILD AND PUSH ALL SOPHIA AI DOCKER IMAGES
# Builds and pushes all necessary images to scoobyjava15 Docker Hub registry

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOCKER_REGISTRY="scoobyjava15"
DOCKER_USERNAME="${DOCKER_USERNAME:-scoobyjava15}"
DOCKER_PASSWORD="${DOCKER_PASSWORD:-}"

echo -e "${BLUE}🐳 BUILDING SOPHIA AI DOCKER IMAGES${NC}"
echo -e "${BLUE}===================================${NC}"
echo "Registry: ${DOCKER_REGISTRY}"
echo "Building images for K3s deployment..."
echo ""

# Function to build and push an image
build_and_push() {
    local image_name="$1"
    local dockerfile_path="$2"
    local context_path="$3"
    
    echo -e "${BLUE}📋 Building ${image_name}...${NC}"
    
    if [ -f "$dockerfile_path" ]; then
        # Build the image
        docker build -t "${DOCKER_REGISTRY}/${image_name}:latest" -f "$dockerfile_path" "$context_path"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Built ${image_name}${NC}"
            
            # Push the image
            echo -e "${YELLOW}🚀 Pushing ${image_name}...${NC}"
            docker push "${DOCKER_REGISTRY}/${image_name}:latest"
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Pushed ${image_name}${NC}"
            else
                echo -e "${RED}❌ Failed to push ${image_name}${NC}"
                return 1
            fi
        else
            echo -e "${RED}❌ Failed to build ${image_name}${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Dockerfile not found: ${dockerfile_path}${NC}"
        echo -e "${BLUE}🔧 Creating basic Dockerfile for ${image_name}...${NC}"
        
        # Create a basic Dockerfile based on the image type
        case "$image_name" in
            "sophia-backend")
                create_backend_dockerfile "$dockerfile_path"
                ;;
            "sophia-frontend")
                create_frontend_dockerfile "$dockerfile_path"
                ;;
            "sophia-mcp-base")
                create_mcp_dockerfile "$dockerfile_path"
                ;;
            *)
                create_generic_dockerfile "$dockerfile_path" "$image_name"
                ;;
        esac
        
        # Retry the build
        build_and_push "$image_name" "$dockerfile_path" "$context_path"
    fi
}

# Function to create backend Dockerfile
create_backend_dockerfile() {
    local dockerfile_path="$1"
    cat > "$dockerfile_path" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY scripts/ ./scripts/
COPY shared/ ./shared/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV ENVIRONMENT=prod

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "backend.app.simple_fastapi"]
EOF
    echo -e "${GREEN}✅ Created backend Dockerfile${NC}"
}

# Function to create frontend Dockerfile
create_frontend_dockerfile() {
    local dockerfile_path="$1"
    cat > "$dockerfile_path" << 'EOF'
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
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Serve the application
CMD ["serve", "-s", "build", "-l", "3000"]
EOF
    echo -e "${GREEN}✅ Created frontend Dockerfile${NC}"
}

# Function to create MCP base Dockerfile
create_mcp_dockerfile() {
    local dockerfile_path="$1"
    cat > "$dockerfile_path" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
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
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9001/health || exit 1

# Default command (will be overridden by specific MCP servers)
CMD ["python", "-m", "mcp_servers.ai_memory.server"]
EOF
    echo -e "${GREEN}✅ Created MCP Dockerfile${NC}"
}

# Function to create generic Dockerfile
create_generic_dockerfile() {
    local dockerfile_path="$1"
    local image_name="$2"
    cat > "$dockerfile_path" << EOF
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
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=prod

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "backend.app.simple_fastapi"]
EOF
    echo -e "${GREEN}✅ Created generic Dockerfile for ${image_name}${NC}"
}

# Step 1: Login to Docker Hub
echo -e "${BLUE}📋 Step 1: Logging into Docker Hub${NC}"

if [ -z "$DOCKER_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  Docker Hub password not provided${NC}"
    echo -e "${BLUE}💡 Please provide Docker Hub credentials:${NC}"
    echo "  export DOCKER_USERNAME=scoobyjava15"
    echo "  export DOCKER_PASSWORD=your_docker_hub_token"
    echo ""
    echo -e "${BLUE}🔧 Attempting interactive login...${NC}"
    docker login --username "$DOCKER_USERNAME"
else
    echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker Hub login successful${NC}"
else
    echo -e "${RED}❌ Docker Hub login failed${NC}"
    echo -e "${YELLOW}💡 Please check your Docker Hub credentials${NC}"
    exit 1
fi

# Step 2: Build and push all images
echo -e "\n${BLUE}📋 Step 2: Building and Pushing Images${NC}"

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}🔧 Creating requirements.txt...${NC}"
    cat > requirements.txt << 'EOF'
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
EOF
    echo -e "${GREEN}✅ Created basic requirements.txt${NC}"
fi

# Images to build
declare -a images=(
    "sophia-backend:backend/Dockerfile:."
    "sophia-frontend:frontend/Dockerfile:."
    "sophia-mcp-base:mcp-servers/Dockerfile:."
    "sophia-ai-backend:backend/Dockerfile:."
    "sophia-ai-mcp-orchestrator:backend/Dockerfile:."
)

# Build and push each image
for image_spec in "${images[@]}"; do
    IFS=':' read -r image_name dockerfile_path context_path <<< "$image_spec"
    build_and_push "$image_name" "$dockerfile_path" "$context_path"
    echo ""
done

echo -e "${GREEN}🎉 All images built and pushed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${BLUE}📊 Images available on Docker Hub:${NC}"
for image_spec in "${images[@]}"; do
    IFS=':' read -r image_name dockerfile_path context_path <<< "$image_spec"
    echo "  ${DOCKER_REGISTRY}/${image_name}:latest"
done

echo -e "\n${BLUE}📋 Next: Deploy to K3s${NC}"
echo "  export KUBECONFIG=~/.kube/k3s-lambda-labs-tunnel"
echo "  kubectl rollout restart deployment -n sophia-ai-prod" 