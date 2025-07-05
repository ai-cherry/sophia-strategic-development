#!/bin/bash
# Setup script for Lambda Labs deployment
# This prepares everything needed without exposing credentials

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Sophia AI Lambda Labs Deployment Setup ===${NC}"
echo ""

# Create SSH key file
setup_ssh_key() {
    echo -e "${BLUE}Setting up SSH key...${NC}"

    SSH_KEY_PATH="${HOME}/.ssh/lambda_labs_sophia"

    if [ -f "$SSH_KEY_PATH" ]; then
        echo -e "${YELLOW}SSH key already exists at $SSH_KEY_PATH${NC}"
    else
        echo "Creating SSH key file..."
        mkdir -p ~/.ssh

        # Prompt for key content
        echo "Please paste the Lambda Labs SSH private key (press Ctrl+D when done):"
        cat > "$SSH_KEY_PATH"

        chmod 600 "$SSH_KEY_PATH"
        echo -e "${GREEN}✓${NC} SSH key saved to $SSH_KEY_PATH"
    fi

    # Add to SSH config
    if ! grep -q "146.235.200.1" ~/.ssh/config 2>/dev/null; then
        echo "" >> ~/.ssh/config
        echo "Host lambda-sophia" >> ~/.ssh/config
        echo "    HostName 146.235.200.1" >> ~/.ssh/config
        echo "    User ubuntu" >> ~/.ssh/config
        echo "    IdentityFile $SSH_KEY_PATH" >> ~/.ssh/config
        echo "    StrictHostKeyChecking no" >> ~/.ssh/config
        echo -e "${GREEN}✓${NC} Added Lambda Labs to SSH config"
    fi
}

# Create environment file
create_env_file() {
    echo -e "${BLUE}Creating environment configuration...${NC}"

    if [ -f ".env.lambda" ]; then
        echo -e "${YELLOW}Environment file already exists${NC}"
        return
    fi

    cat > .env.lambda << 'EOF'
# Lambda Labs Deployment Configuration
# Generated on $(date)

# Lambda Labs
LAMBDA_INSTANCE_IP=146.235.200.1
LAMBDA_SSH_KEY_PATH=~/.ssh/lambda_labs_sophia
DOCKER_REGISTRY=scoobyjava15

# Pulumi
PULUMI_ORG=scoobyjava-org

# Deployment
DEPLOY_ENVIRONMENT=prod
EOF

    echo -e "${GREEN}✓${NC} Created .env.lambda"
    echo -e "${YELLOW}Note: Add your API keys to .env.lambda before deployment${NC}"
}

# Build Docker images
build_images() {
    echo -e "${BLUE}Building Docker images...${NC}"

    # Check if we have uv.lock
    if [ ! -f "uv.lock" ]; then
        echo -e "${YELLOW}Creating uv.lock file...${NC}"
        if command -v uv &> /dev/null; then
            uv sync
        else
            echo -e "${RED}UV not installed. Installing...${NC}"
            pip install uv
            uv sync
        fi
    fi

    # Build images
    echo "Building backend image..."
    docker build -t scoobyjava15/sophia-backend:latest -f Dockerfile .

    echo "Building frontend image..."
    if [ -d "frontend" ]; then
        docker build -t scoobyjava15/sophia-frontend:latest -f frontend/Dockerfile frontend/
    fi

    # Build MCP servers
    for mcp in mcp-servers/*/; do
        if [ -f "$mcp/Dockerfile" ]; then
            name=$(basename "$mcp")
            echo "Building MCP server: $name"
            docker build -t "scoobyjava15/sophia-$name:latest" -f "$mcp/Dockerfile" .
        fi
    done

    echo -e "${GREEN}✓${NC} Docker images built"
}

# Create deployment package
create_package() {
    echo -e "${BLUE}Creating deployment package...${NC}"

    ./scripts/deploy_lambda_labs_complete.sh
}

# Main menu
main() {
    echo ""
    echo "What would you like to do?"
    echo "1) Setup SSH key"
    echo "2) Create environment file"
    echo "3) Build Docker images"
    echo "4) Create deployment package"
    echo "5) Do everything (recommended)"
    echo ""
    read -p "Select option (1-5): " choice

    case $choice in
        1) setup_ssh_key ;;
        2) create_env_file ;;
        3) build_images ;;
        4) create_package ;;
        5)
            setup_ssh_key
            create_env_file
            build_images
            echo ""
            echo -e "${GREEN}=== Setup Complete ===${NC}"
            echo ""
            echo "Next steps:"
            echo "1. Add your API keys to .env.lambda"
            echo "2. Run: source .env.lambda"
            echo "3. Run: ./scripts/deploy_lambda_labs_complete.sh"
            ;;
        *) echo "Invalid option" ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed${NC}"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}Installing jq...${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install jq
        else
            sudo apt-get update && sudo apt-get install -y jq
        fi
    fi

    echo -e "${GREEN}✓${NC} Prerequisites checked"
}

# Run
check_prerequisites
main
