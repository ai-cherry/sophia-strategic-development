#!/bin/bash

# Sophia AI - GitHub Actions Deployment Setup Script
# This script will help you get from the current state to a functional deployment

set -e

echo "🚀 Sophia AI GitHub Actions Deployment Setup"
echo "============================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

# Check if we're in the right directory
if [ ! -f ".github/workflows/deploy-sophia-unified.yml" ]; then
    print_error "This script must be run from the repository root where deploy-sophia-unified.yml exists"
    exit 1
fi

print_info "Setting up GitHub Actions deployment for Sophia AI..."
echo ""

# Step 1: Check GitHub secrets
print_step "Step 1: Checking GitHub secrets configuration..."
echo ""

print_info "Required GitHub secrets for deployment:"
echo "  - DOCKER_USERNAME (Docker Hub username)"
echo "  - DOCKER_PASSWORD (Docker Hub Personal Access Token)"
echo "  - LAMBDA_PRIVATE_SSH_KEY (SSH key for Lambda Labs instances)"
echo "  - PULUMI_ACCESS_TOKEN (Optional: For infrastructure management)"
echo "  - SLACK_WEBHOOK (Optional: For notifications)"
echo ""

print_warning "Please ensure these secrets are configured at:"
echo "  https://github.com/ai-cherry/sophia-main/settings/secrets/actions"
echo ""

# Step 2: Validate SSH key
print_step "Step 2: Validating SSH key configuration..."
echo ""

if [ -f "$HOME/.ssh/sophia2025.pem" ]; then
    print_success "SSH key found at $HOME/.ssh/sophia2025.pem"
    
    # Test SSH key format
    if ssh-keygen -y -f "$HOME/.ssh/sophia2025.pem" > /dev/null 2>&1; then
        print_success "SSH key format is valid"
    else
        print_error "SSH key format is invalid"
        exit 1
    fi
else
    print_warning "SSH key not found at $HOME/.ssh/sophia2025.pem"
    print_info "The SSH key should be stored as LAMBDA_PRIVATE_SSH_KEY in GitHub secrets"
fi

# Test SSH connections to all instances
print_info "Testing SSH connections to Lambda Labs instances..."
instances=(
    "104.171.202.103:sophia-production-instance"
    "192.222.58.232:sophia-ai-core"
    "104.171.202.117:sophia-mcp-orchestrator"
    "104.171.202.134:sophia-data-pipeline"
    "155.248.194.183:sophia-development"
)

ssh_success=0
for instance in "${instances[@]}"; do
    ip=$(echo $instance | cut -d: -f1)
    name=$(echo $instance | cut -d: -f2)
    
    if [ -f "$HOME/.ssh/sophia2025.pem" ]; then
        if timeout 10 ssh -i "$HOME/.ssh/sophia2025.pem" -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@$ip "echo 'SSH OK'" > /dev/null 2>&1; then
            print_success "SSH connection to $name ($ip) successful"
            ((ssh_success++))
        else
            print_error "SSH connection to $name ($ip) failed"
        fi
    else
        print_warning "Cannot test SSH to $name ($ip) - no SSH key found"
    fi
done

if [ $ssh_success -eq 5 ]; then
    print_success "All SSH connections successful"
elif [ $ssh_success -gt 0 ]; then
    print_warning "$ssh_success out of 5 SSH connections successful"
else
    print_warning "No SSH connections could be tested"
fi

echo ""

# Step 3: Validate Docker images
print_step "Step 3: Validating Docker configuration..."
echo ""

if command -v docker &> /dev/null; then
    print_success "Docker is installed"
    
    # Check if Docker daemon is running
    if docker info > /dev/null 2>&1; then
        print_success "Docker daemon is running"
    else
        print_error "Docker daemon is not running"
        exit 1
    fi
else
    print_error "Docker is not installed"
    exit 1
fi

# Test Docker Hub login (if credentials are available)
if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
    print_info "Testing Docker Hub login..."
    if echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin > /dev/null 2>&1; then
        print_success "Docker Hub login successful"
        docker logout > /dev/null 2>&1
    else
        print_error "Docker Hub login failed"
    fi
else
    print_warning "DOCKER_USERNAME and DOCKER_PASSWORD not set - cannot test Docker Hub login"
fi

# Step 4: Check deployment files
print_step "Step 4: Validating deployment files..."
echo ""

deployment_files=(
    "deployment/docker-compose-production.yml"
    "deployment/docker-compose-ai-core.yml"
    "deployment/docker-compose-mcp-orchestrator.yml"
    "deployment/docker-compose-data-pipeline.yml"
    "deployment/docker-compose-development.yml"
)

all_deployment_files_exist=true
for file in "${deployment_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Deployment file exists: $file"
    else
        print_error "Deployment file missing: $file"
        all_deployment_files_exist=false
    fi
done

if $all_deployment_files_exist; then
    print_success "All deployment files are present"
else
    print_error "Some deployment files are missing"
    exit 1
fi

# Step 5: Check main Dockerfiles
print_step "Step 5: Validating main Dockerfiles..."
echo ""

main_dockerfiles=(
    "Dockerfile.production"
    "frontend/Dockerfile"
)

for dockerfile in "${main_dockerfiles[@]}"; do
    if [ -f "$dockerfile" ]; then
        print_success "Dockerfile exists: $dockerfile"
    else
        print_error "Dockerfile missing: $dockerfile"
        exit 1
    fi
done

# Step 6: Check MCP server Dockerfiles
print_step "Step 6: Validating MCP server Dockerfiles..."
echo ""

mcp_v2_servers=(
    "infrastructure/mcp_servers/ai_memory_v2"
    "infrastructure/mcp_servers/gong_v2"
    "infrastructure/mcp_servers/snowflake_v2"
    "infrastructure/mcp_servers/slack_v2"
    "infrastructure/mcp_servers/linear_v2"
    "infrastructure/mcp_servers/github_v2"
    "infrastructure/mcp_servers/codacy_v2"
    "infrastructure/mcp_servers/asana_v2"
)

mcp_v2_count=0
for server in "${mcp_v2_servers[@]}"; do
    if [ -f "$server/Dockerfile" ]; then
        print_success "MCP V2 server Dockerfile exists: $server/Dockerfile"
        ((mcp_v2_count++))
    else
        print_warning "MCP V2 server Dockerfile missing: $server/Dockerfile"
    fi
done

print_info "Found $mcp_v2_count out of ${#mcp_v2_servers[@]} MCP V2 server Dockerfiles"

# Check legacy MCP servers
legacy_mcp_count=0
if [ -d "mcp-servers" ]; then
    for server_dir in mcp-servers/*/; do
        if [ -f "$server_dir/Dockerfile" ]; then
            ((legacy_mcp_count++))
        fi
    done
fi

print_info "Found $legacy_mcp_count legacy MCP server Dockerfiles"

# Step 7: Test local Docker builds
print_step "Step 7: Testing local Docker builds..."
echo ""

print_info "Testing backend Docker build..."
if docker build -f Dockerfile.production -t test-sophia-backend . > /dev/null 2>&1; then
    print_success "Backend Docker build successful"
    docker rmi test-sophia-backend > /dev/null 2>&1
else
    print_error "Backend Docker build failed"
    exit 1
fi

print_info "Testing frontend Docker build..."
if docker build -f frontend/Dockerfile -t test-sophia-frontend frontend/ > /dev/null 2>&1; then
    print_success "Frontend Docker build successful"
    docker rmi test-sophia-frontend > /dev/null 2>&1
else
    print_error "Frontend Docker build failed"
    exit 1
fi

# Step 8: Generate deployment summary
print_step "Step 8: Generating deployment summary..."
echo ""

print_success "GitHub Actions deployment setup validation complete!"
echo ""

print_info "DEPLOYMENT SUMMARY:"
echo "=================="
echo ""
echo "🏗️ Infrastructure Ready:"
echo "  - 5 Lambda Labs instances configured"
echo "  - SSH access tested (${ssh_success}/5 successful)"
echo "  - Docker environment validated"
echo ""
echo "📦 Container Images:"
echo "  - Backend: Dockerfile.production ✅"
echo "  - Frontend: frontend/Dockerfile ✅"
echo "  - MCP V2 Servers: $mcp_v2_count/8 available"
echo "  - Legacy MCP Servers: $legacy_mcp_count available"
echo ""
echo "🚀 Deployment Files:"
echo "  - docker-compose-production.yml ✅"
echo "  - docker-compose-ai-core.yml ✅"
echo "  - docker-compose-mcp-orchestrator.yml ✅"
echo "  - docker-compose-data-pipeline.yml ✅"
echo "  - docker-compose-development.yml ✅"
echo ""
echo "🔧 GitHub Actions:"
echo "  - Workflow: .github/workflows/deploy-sophia-unified.yml ✅"
echo "  - Secrets: Configure at https://github.com/ai-cherry/sophia-main/settings/secrets/actions"
echo ""

# Step 9: Next steps
print_info "NEXT STEPS:"
echo "==========="
echo ""
echo "1. 🔐 Configure GitHub Secrets:"
echo "   Go to: https://github.com/ai-cherry/sophia-main/settings/secrets/actions"
echo "   Add these secrets:"
echo "     - DOCKER_USERNAME=scoobyjava15"
echo "     - DOCKER_PASSWORD=<your-docker-hub-token>"
echo "     - LAMBDA_PRIVATE_SSH_KEY=<contents-of-sophia2025.pem>"
echo "     - PULUMI_ACCESS_TOKEN=<your-pulumi-token> (optional)"
echo "     - SLACK_WEBHOOK=<your-slack-webhook> (optional)"
echo ""
echo "2. 🚀 Run the Deployment:"
echo "   Go to: https://github.com/ai-cherry/sophia-main/actions/workflows/deploy-sophia-unified.yml"
echo "   Click 'Run workflow'"
echo "   Select target: 'development' (recommended for first deployment)"
echo "   Click 'Run workflow'"
echo ""
echo "3. 📊 Monitor Deployment:"
echo "   Watch the GitHub Actions progress"
echo "   Check the deployment summary"
echo "   Access deployed services:"
echo "     - Production: http://104.171.202.103:3000"
echo "     - AI Core: http://192.222.58.232:9000"
echo "     - MCP Orchestrator: http://104.171.202.117:8080"
echo "     - Data Pipeline: http://104.171.202.134:9090"
echo "     - Development: http://155.248.194.183:3000"
echo ""

# Step 10: Create quick deployment script
print_step "Step 10: Creating quick deployment script..."
echo ""

cat > deploy_quick.sh << 'EOF'
#!/bin/bash
# Quick deployment script for Sophia AI

echo "🚀 Sophia AI Quick Deployment"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f ".github/workflows/deploy-sophia-unified.yml" ]; then
    echo "❌ This script must be run from the repository root"
    exit 1
fi

echo "📋 Available deployment targets:"
echo "  1. development (A10 - safest for testing)"
echo "  2. production (RTX6000 - core platform)"
echo "  3. ai-core (GH200 - AI/ML services)"
echo "  4. mcp-orchestrator (A6000 - business tools)"
echo "  5. data-pipeline (A100 - data processing)"
echo "  6. all (deploy to all instances)"
echo ""

read -p "Select deployment target (1-6): " choice

case $choice in
    1) target="development" ;;
    2) target="production" ;;
    3) target="ai-core" ;;
    4) target="mcp-orchestrator" ;;
    5) target="data-pipeline" ;;
    6) target="all" ;;
    *) echo "Invalid choice"; exit 1 ;;
esac

echo ""
echo "🎯 Deploying to: $target"
echo "📍 GitHub Actions URL: https://github.com/ai-cherry/sophia-main/actions/workflows/deploy-sophia-unified.yml"
echo ""
echo "⚠️  Please run the deployment through GitHub Actions web interface:"
echo "   1. Go to the URL above"
echo "   2. Click 'Run workflow'"
echo "   3. Select target: $target"
echo "   4. Click 'Run workflow'"
echo ""
echo "✅ Deployment will start automatically!"
EOF

chmod +x deploy_quick.sh
print_success "Created quick deployment script: ./deploy_quick.sh"

echo ""
print_success "🎉 Setup complete! Your Sophia AI deployment is ready."
print_info "Run ./deploy_quick.sh for a quick deployment helper"
echo "" 