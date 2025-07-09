#!/bin/bash
# Sophia AI Unified Deployment Script
# Deploys entire platform across 5 Lambda Labs instances
# Based on the Holistic Deployment Plan

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Instance Configuration
declare -A INSTANCES=(
    ["production"]="104.171.202.103:RTX6000:docker-compose-production.yml:Core Platform Services"
    ["ai-core"]="192.222.58.232:GH200:docker-compose-ai-core.yml:AI/ML Compute Engine"
    ["mcp-orchestrator"]="104.171.202.117:A6000:docker-compose-mcp-orchestrator.yml:MCP Services Hub"
    ["data-pipeline"]="104.171.202.134:A100:docker-compose-data-pipeline.yml:Data Processing Center"
    ["development"]="155.248.194.183:A10:docker-compose-development.yml:Development & Monitoring"
)

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

print_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Function to validate SSH access
validate_ssh_access() {
    local ip=$1
    local instance_name=$2
    
    print_info "Validating SSH access to $instance_name ($ip)..."
    
    if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@$ip "echo 'SSH OK'" > /dev/null 2>&1; then
        print_status "✅ SSH access to $instance_name verified"
        return 0
    else
        print_error "❌ SSH access to $instance_name failed"
        return 1
    fi
}

# Function to prepare deployment directory on remote instance
prepare_deployment_dir() {
    local ip=$1
    local instance_name=$2
    
    print_info "Preparing deployment directory on $instance_name..."
    
    ssh -i "$SSH_KEY" ubuntu@$ip "
        sudo mkdir -p /opt/sophia-ai/{deployment,data,logs}
        sudo chown -R ubuntu:ubuntu /opt/sophia-ai
        cd /opt/sophia-ai
        
        # Initialize Docker Swarm if needed
        if ! docker info | grep -q 'Swarm: active'; then
            echo 'Initializing Docker Swarm...'
            docker swarm init
        fi
        
        # Create required networks
        docker network create --driver overlay sophia-network || true
        docker network create --driver overlay sophia-public || true
        docker network create --driver overlay sophia-private || true
        
        # Create required volumes
        docker volume create sophia-postgres-data || true
        docker volume create sophia-redis-data || true
        docker volume create sophia-grafana-data || true
        docker volume create sophia-prometheus-data || true
        
        echo 'Deployment directory prepared successfully'
    "
}

# Function to copy deployment files to remote instance
copy_deployment_files() {
    local ip=$1
    local instance_name=$2
    local compose_file=$3
    
    print_info "Copying deployment files to $instance_name..."
    
    # Copy Docker Compose file
    if [ -f "deployment/$compose_file" ]; then
        scp -i "$SSH_KEY" "deployment/$compose_file" ubuntu@$ip:/opt/sophia-ai/docker-compose.yml
        print_status "✅ Docker Compose file copied to $instance_name"
    else
        print_error "❌ Docker Compose file deployment/$compose_file not found"
        return 1
    fi
    
    # Copy any additional configuration files
    if [ -d "deployment/configs" ]; then
        scp -i "$SSH_KEY" -r deployment/configs ubuntu@$ip:/opt/sophia-ai/
        print_status "✅ Configuration files copied to $instance_name"
    fi
}

# Function to deploy to specific instance
deploy_instance() {
    local instance_name=$1
    local instance_info=${INSTANCES[$instance_name]}
    local ip=$(echo $instance_info | cut -d: -f1)
    local gpu=$(echo $instance_info | cut -d: -f2)
    local compose_file=$(echo $instance_info | cut -d: -f3)
    local description=$(echo $instance_info | cut -d: -f4)
    
    print_info "===================================================="
    print_info "DEPLOYING TO: $instance_name"
    print_info "GPU: $gpu"
    print_info "IP: $ip"
    print_info "Role: $description"
    print_info "===================================================="
    
    # Validate SSH access
    if ! validate_ssh_access "$ip" "$instance_name"; then
        print_error "Cannot deploy to $instance_name - SSH access failed"
        return 1
    fi
    
    # Prepare deployment directory
    prepare_deployment_dir "$ip" "$instance_name"
    
    # Copy deployment files
    copy_deployment_files "$ip" "$instance_name" "$compose_file"
    
    # Deploy the stack
    print_info "Deploying Docker stack to $instance_name..."
    
    ssh -i "$SSH_KEY" ubuntu@$ip "
        cd /opt/sophia-ai
        
        # Set environment variables
        export DOCKER_REGISTRY=$DOCKER_REGISTRY
        export IMAGE_TAG=$IMAGE_TAG
        export ENVIRONMENT=prod
        export INSTANCE_NAME=$instance_name
        export GPU_TYPE=$gpu
        
        # Deploy the stack
        docker stack deploy -c docker-compose.yml sophia-$instance_name --with-registry-auth
        
        # Wait for services to start
        echo 'Waiting for services to start...'
        sleep 30
        
        # Show deployment status
        echo 'Deployment Status:'
        docker stack services sophia-$instance_name
    "
    
    # Validate deployment
    validate_deployment "$ip" "$instance_name"
    
    print_status "✅ Deployment to $instance_name completed successfully"
}

# Function to validate deployment
validate_deployment() {
    local ip=$1
    local instance_name=$2
    
    print_info "Validating deployment on $instance_name..."
    
    ssh -i "$SSH_KEY" ubuntu@$ip "
        cd /opt/sophia-ai
        
        # Check if all services are running
        failed_services=\$(docker stack services sophia-$instance_name --format 'table {{.Name}}\t{{.Replicas}}' | grep '0/' | wc -l)
        
        if [ \$failed_services -gt 0 ]; then
            echo 'WARNING: Some services failed to start'
            docker stack services sophia-$instance_name --format 'table {{.Name}}\t{{.Replicas}}\t{{.Image}}'
        else
            echo 'SUCCESS: All services are running'
        fi
        
        # Show running containers
        echo 'Running containers:'
        docker ps --filter label=com.docker.stack.namespace=sophia-$instance_name --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
    "
}

# Function to deploy to all instances
deploy_all() {
    print_info "===================================================="
    print_info "SOPHIA AI UNIFIED DEPLOYMENT - ALL INSTANCES"
    print_info "===================================================="
    
    local failed_instances=()
    
    for instance in "${!INSTANCES[@]}"; do
        if deploy_instance "$instance"; then
            print_status "✅ $instance deployment successful"
        else
            print_error "❌ $instance deployment failed"
            failed_instances+=("$instance")
        fi
        echo ""
    done
    
    # Summary
    print_info "===================================================="
    print_info "DEPLOYMENT SUMMARY"
    print_info "===================================================="
    
    if [ ${#failed_instances[@]} -eq 0 ]; then
        print_status "🎉 ALL DEPLOYMENTS SUCCESSFUL!"
        print_info "Access URLs:"
        print_info "  • Production Dashboard: http://104.171.202.103:3000"
        print_info "  • Production API: http://104.171.202.103:8000"
        print_info "  • AI Core Services: http://192.222.58.232:9000"
        print_info "  • MCP Services: http://104.171.202.117:8080"
        print_info "  • Data Pipeline: http://104.171.202.134:9090"
        print_info "  • Development: http://155.248.194.183:3000"
    else
        print_error "❌ SOME DEPLOYMENTS FAILED:"
        for instance in "${failed_instances[@]}"; do
            print_error "  • $instance"
        done
        return 1
    fi
}

# Function to show deployment status
show_status() {
    print_info "===================================================="
    print_info "SOPHIA AI DEPLOYMENT STATUS"
    print_info "===================================================="
    
    for instance in "${!INSTANCES[@]}"; do
        local instance_info=${INSTANCES[$instance]}
        local ip=$(echo $instance_info | cut -d: -f1)
        local gpu=$(echo $instance_info | cut -d: -f2)
        local description=$(echo $instance_info | cut -d: -f4)
        
        print_info "Instance: $instance ($gpu - $description)"
        print_info "IP: $ip"
        
        if validate_ssh_access "$ip" "$instance"; then
            ssh -i "$SSH_KEY" ubuntu@$ip "
                if docker stack services sophia-$instance >/dev/null 2>&1; then
                    echo '  Status: DEPLOYED'
                    docker stack services sophia-$instance --format 'table {{.Name}}\t{{.Replicas}}\t{{.Image}}'
                else
                    echo '  Status: NOT DEPLOYED'
                fi
            "
        else
            print_error "  Status: SSH ACCESS FAILED"
        fi
        echo ""
    done
}

# Function to show help
show_help() {
    cat << EOF
Sophia AI Unified Deployment Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  deploy [instance]    Deploy to specific instance or all instances
  status              Show deployment status for all instances
  validate [instance] Validate deployment on instance
  help                Show this help message

Instances:
  production          Deploy to production instance (RTX6000)
  ai-core            Deploy to AI core instance (GH200)
  mcp-orchestrator   Deploy to MCP orchestrator (A6000)
  data-pipeline      Deploy to data pipeline instance (A100)
  development        Deploy to development instance (A10)
  all                Deploy to all instances (default)

Examples:
  $0 deploy all                    # Deploy to all instances
  $0 deploy production             # Deploy to production instance only
  $0 status                        # Show deployment status
  $0 validate ai-core             # Validate AI core deployment

Environment Variables:
  SSH_KEY             SSH key path (default: ~/.ssh/sophia2025.pem)
  DOCKER_REGISTRY     Docker registry (default: scoobyjava15)
  IMAGE_TAG           Image tag (default: latest)
EOF
}

# Main execution
main() {
    local command=${1:-deploy}
    local target=${2:-all}
    
    case "$command" in
        "deploy")
            case "$target" in
                "all")
                    deploy_all
                    ;;
                "production"|"ai-core"|"mcp-orchestrator"|"data-pipeline"|"development")
                    deploy_instance "$target"
                    ;;
                *)
                    print_error "Invalid instance: $target"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
        "status")
            show_status
            ;;
        "validate")
            if [ -z "$target" ] || [ "$target" = "all" ]; then
                print_error "Please specify an instance to validate"
                show_help
                exit 1
            fi
            if [ -n "${INSTANCES[$target]}" ]; then
                local instance_info=${INSTANCES[$target]}
                local ip=$(echo $instance_info | cut -d: -f1)
                validate_deployment "$ip" "$target"
            else
                print_error "Invalid instance: $target"
                show_help
                exit 1
            fi
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Invalid command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"