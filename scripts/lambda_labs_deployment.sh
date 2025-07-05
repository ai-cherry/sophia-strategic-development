#!/bin/bash
# Lambda Labs Deployment Script for Sophia AI

# Configuration
MAIN_INSTANCE="104.171.202.64"  # 8x V100 instance
MCP_INSTANCE="150.230.47.71"    # Orchestra instance
AI_INSTANCE="129.153.123.54"    # A100 instance

SSH_KEY="~/.ssh/sophia-ai-key"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 Deploying Sophia AI to Lambda Labs"

# Function to deploy to an instance
deploy_to_instance() {
    local INSTANCE_IP=$1
    local ROLE=$2

    echo -e "${GREEN}Deploying $ROLE to $INSTANCE_IP${NC}"

    # Initial setup commands
    ssh -i $SSH_KEY ubuntu@$INSTANCE_IP << 'EOF'
        # Update system
        sudo apt-get update

        # Install Docker if not present
        if ! command -v docker &> /dev/null; then
            sudo apt-get install -y docker.io docker-compose
            sudo usermod -aG docker ubuntu
            sudo systemctl enable docker
            sudo systemctl start docker
        fi

        # Install Python and dependencies
        sudo apt-get install -y python3-pip python3-venv git

        # Clone or update repository
        if [ -d "sophia-main" ]; then
            cd sophia-main && git pull
        else
            git clone https://github.com/ai-cherry/sophia-main.git
            cd sophia-main
        fi

        # Set up Python environment
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
EOF

    # Deploy based on role
    case $ROLE in
        "main")
            deploy_main_platform $INSTANCE_IP
            ;;
        "mcp")
            deploy_mcp_servers $INSTANCE_IP
            ;;
        "ai")
            deploy_ai_services $INSTANCE_IP
            ;;
    esac
}

# Deploy main platform
deploy_main_platform() {
    local IP=$1
    echo "📦 Deploying main platform..."

    ssh -i $SSH_KEY ubuntu@$IP << 'EOF'
        cd sophia-main

        # Create production docker-compose
        cat > docker-compose.prod.yml << 'COMPOSE'
version: '3.8'
services:
  sophia-api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
    volumes:
      - ./backend:/app
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sophia
      POSTGRES_USER: sophia
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-sophia123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
COMPOSE

        # Start services
        docker-compose -f docker-compose.prod.yml up -d

        # Check status
        docker-compose -f docker-compose.prod.yml ps
EOF
}

# Deploy MCP servers
deploy_mcp_servers() {
    local IP=$1
    echo "🤖 Deploying MCP servers..."

    ssh -i $SSH_KEY ubuntu@$IP << 'EOF'
        cd sophia-main/mcp-servers

        # Deploy each MCP server
        for server in ai-memory codacy github linear snowflake-admin; do
            echo "Deploying $server..."
            cd $server
            if [ -f "Dockerfile" ]; then
                docker build -t sophia-$server .
                docker run -d --name $server --restart unless-stopped \
                    -p $((9000 + $(ls -1 ../ | grep -n "^$server$" | cut -d: -f1))):8000 \
                    -e ENVIRONMENT=prod \
                    -e PULUMI_ORG=scoobyjava-org \
                    sophia-$server
            fi
            cd ..
        done

        # Check all running containers
        docker ps
EOF
}

# Deploy AI services
deploy_ai_services() {
    local IP=$1
    echo "🧠 Deploying AI services..."

    ssh -i $SSH_KEY ubuntu@$IP << 'EOF'
        cd sophia-main

        # Set up GPU-specific services
        nvidia-smi  # Verify GPU access

        # Deploy AI workloads
        docker run -d --name ai-inference \
            --gpus all \
            --restart unless-stopped \
            -p 8080:8080 \
            -v $(pwd)/models:/models \
            -e ENVIRONMENT=prod \
            sophia-ai/inference:latest
EOF
}

# Main deployment
echo "Starting deployment..."

# Deploy to each instance
deploy_to_instance $MAIN_INSTANCE "main"
deploy_to_instance $MCP_INSTANCE "mcp"
deploy_to_instance $AI_INSTANCE "ai"

echo -e "${GREEN}✅ Deployment complete!${NC}"

# Print access information
echo "
📊 Access Information:
- Main API: http://$MAIN_INSTANCE:8000
- MCP Servers: http://$MCP_INSTANCE:9001-9008
- AI Services: http://$AI_INSTANCE:8080

🔐 SSH Access:
- Main: ssh -i $SSH_KEY ubuntu@$MAIN_INSTANCE
- MCP: ssh -i $SSH_KEY ubuntu@$MCP_INSTANCE
- AI: ssh -i $SSH_KEY ubuntu@$AI_INSTANCE
"
