#!/bin/bash
# Prepare deployment package for Lambda Labs
# Creates a tarball with all necessary files for deployment

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Preparing Sophia AI Deployment Package ===${NC}"

# Create deployment directory
DEPLOY_DIR="sophia-deployment-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEPLOY_DIR"

echo "Creating deployment package in: $DEPLOY_DIR"

# Copy essential files
echo -e "${BLUE}Copying deployment files...${NC}"

# Scripts
cp -v scripts/deploy_sophia_stack.sh "$DEPLOY_DIR/"
cp -v scripts/optimize_docker_swarm_resources.py "$DEPLOY_DIR/"
cp -v scripts/monitor_swarm_performance.sh "$DEPLOY_DIR/"

# Docker compose files
if [ -f "docker-compose.cloud.yml.optimized" ]; then
    cp -v docker-compose.cloud.yml.optimized "$DEPLOY_DIR/"
else
    echo -e "${YELLOW}Warning: Optimized config not found. Using backup...${NC}"
    cp -v docker-compose.cloud.yml.backup "$DEPLOY_DIR/docker-compose.cloud.yml"
fi

# Copy production compose if exists
if [ -f "docker-compose.production.yml" ]; then
    cp -v docker-compose.production.yml "$DEPLOY_DIR/"
fi

# Create deployment instructions
cat > "$DEPLOY_DIR/DEPLOYMENT_INSTRUCTIONS.md" << 'EOF'
# Sophia AI Deployment Instructions

## Prerequisites
1. SSH access to Lambda Labs (146.235.200.1)
2. Docker Swarm initialized
3. Required secrets set as environment variables

## Deployment Steps

### 1. Upload deployment package
```bash
# From your local machine
scp sophia-deployment-*.tar.gz ubuntu@146.235.200.1:~/
```

### 2. Connect to Lambda Labs
```bash
ssh ubuntu@146.235.200.1
```

### 3. Extract deployment package
```bash
tar -xzf sophia-deployment-*.tar.gz
cd sophia-deployment-*
```

### 4. Set required environment variables
```bash
# Set these with your actual values
export POSTGRES_PASSWORD="your-postgres-password"
export GRAFANA_PASSWORD="your-grafana-password"
export PULUMI_ACCESS_TOKEN="your-pulumi-token"
export MEM0_API_KEY="your-mem0-key"
export SNOWFLAKE_ACCOUNT="your-snowflake-account"
export SNOWFLAKE_USER="your-snowflake-user"
export SNOWFLAKE_PASSWORD="your-snowflake-password"
export VERCEL_V0DEV_API_KEY="your-vercel-key"
```

### 5. Run the deployment
```bash
# Make scripts executable
chmod +x *.sh

# Deploy the stack
./deploy_sophia_stack.sh
```

### 6. Monitor deployment
```bash
# Check service status
docker service ls

# Monitor performance
./monitor_swarm_performance.sh
```

## Post-Deployment

### Access URLs
- Dashboard: https://api.sophia-ai.lambda.cloud/dashboard
- Chat: https://chat-mcp.sophia-ai.lambda.cloud
- API Docs: https://api.sophia-ai.lambda.cloud/docs
- Grafana: https://sophia-ai.lambda.cloud:3000
- Prometheus: https://sophia-ai.lambda.cloud:9090

### Troubleshooting
- Check logs: `docker service logs <service-name>`
- Scale service: `docker service scale sophia-ai_backend=3`
- Update service: `docker service update --force <service-name>`
EOF

# Create quick deploy script
cat > "$DEPLOY_DIR/quick_deploy.sh" << 'EOF'
#!/bin/bash
# Quick deployment script for Lambda Labs

set -euo pipefail

echo "🚀 Starting Sophia AI deployment..."

# Check if we're on a manager node
if ! docker node ls &>/dev/null; then
    echo "❌ ERROR: Not on a Docker Swarm manager node"
    echo "Initialize swarm with: docker swarm init"
    exit 1
fi

# Check for required environment variables
required_vars=(
    "POSTGRES_PASSWORD"
    "PULUMI_ACCESS_TOKEN"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo "❌ ERROR: $var is not set"
        echo "Set it with: export $var='your-value'"
        exit 1
    fi
done

# Run the main deployment
./deploy_sophia_stack.sh

echo "✅ Deployment initiated! Monitor with:"
echo "   docker stack ps sophia-ai"
echo "   ./monitor_swarm_performance.sh"
EOF

chmod +x "$DEPLOY_DIR/quick_deploy.sh"

# Create tarball
echo -e "${BLUE}Creating deployment package...${NC}"
tar -czf "$DEPLOY_DIR.tar.gz" "$DEPLOY_DIR"

# Display instructions
echo -e "${GREEN}✅ Deployment package created: $DEPLOY_DIR.tar.gz${NC}"
echo ""
echo -e "${BLUE}=== Next Steps ===${NC}"
echo "1. Upload to Lambda Labs:"
echo "   scp $DEPLOY_DIR.tar.gz ubuntu@146.235.200.1:~/"
echo ""
echo "2. SSH to Lambda Labs:"
echo "   ssh ubuntu@146.235.200.1"
echo ""
echo "3. Extract and deploy:"
echo "   tar -xzf $DEPLOY_DIR.tar.gz"
echo "   cd $DEPLOY_DIR"
echo "   ./quick_deploy.sh"
echo ""
echo "See $DEPLOY_DIR/DEPLOYMENT_INSTRUCTIONS.md for detailed instructions" 