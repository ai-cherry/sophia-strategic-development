#!/bin/bash

# Enhanced Sophia AI Deployment Script
# Deploys main stack, monitoring, and backup services

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
LAMBDA_LABS_HOST="${LAMBDA_LABS_HOST:-146.235.200.1}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're on a manager node
check_swarm_manager() {
    if ! docker info | grep -q "Swarm: active"; then
        log_error "This node is not part of a Docker Swarm"
        log_info "Initialize swarm with: docker swarm init"
        exit 1
    fi

    if ! docker info | grep -q "Is Manager: true"; then
        log_error "This node is not a Swarm manager"
        exit 1
    fi
}

# Create required directories
create_directories() {
    log_info "Creating required directories..."

    directories=(
        "/mnt/data/postgres"
        "/mnt/data/redis"
        "/mnt/backup/postgres"
        "/mnt/backup/redis"
        "/mnt/monitoring/prometheus"
        "/mnt/monitoring/grafana"
        "/mnt/monitoring/loki"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            sudo mkdir -p "$dir"
            log_success "Created $dir"
        fi
    done
}

# Create Docker secrets
create_secrets() {
    log_info "Creating Docker secrets..."

    # Function to create a secret if it doesn't exist
    create_secret() {
        local name=$1
        local value=$2

        if docker secret ls | grep -q "^$name "; then
            log_warning "Secret $name already exists"
        else
            echo "$value" | docker secret create "$name" - >/dev/null
            log_success "Created secret: $name"
        fi
    }

    # Create required secrets (use environment variables or defaults)
    create_secret "postgres_password" "${POSTGRES_PASSWORD:-$(openssl rand -base64 32)}"
    create_secret "grafana_password" "${GRAFANA_PASSWORD:-$(openssl rand -base64 32)}"
    create_secret "pulumi_access_token" "${PULUMI_ACCESS_TOKEN:-dummy-token}"
    create_secret "mem0_api_key" "${MEM0_API_KEY:-dummy-key}"
    create_secret "cortex_api_key" "${CORTEX_API_KEY:-dummy-key}"
    create_secret "snowflake_account" "${SNOWFLAKE_ACCOUNT:-dummy-account}"
    create_secret "snowflake_user" "${SNOWFLAKE_USER:-dummy-user}"
    create_secret "snowflake_password" "${SNOWFLAKE_PASSWORD:-dummy-password}"
}

# Create networks
create_networks() {
    log_info "Creating Docker networks..."

    # Create public network if it doesn't exist
    if ! docker network ls | grep -q "sophia-public"; then
        docker network create \
            --driver overlay \
            --attachable \
            --opt encrypted=true \
            --subnet=10.0.1.0/24 \
            sophia-public
        log_success "Created sophia-public network"
    fi

    # Create private network if it doesn't exist
    if ! docker network ls | grep -q "sophia-private"; then
        docker network create \
            --driver overlay \
            --internal \
            --opt encrypted=true \
            --subnet=10.0.2.0/24 \
            sophia-private
        log_success "Created sophia-private network"
    fi
}

# Deploy main stack
deploy_main_stack() {
    log_info "Deploying main Sophia AI stack..."

    if [ -f "docker-compose.cloud.enhanced.yml" ]; then
        docker stack deploy -c docker-compose.cloud.enhanced.yml sophia-ai
        log_success "Main stack deployed"
    else
        log_error "docker-compose.cloud.enhanced.yml not found"
        exit 1
    fi
}

# Deploy monitoring stack
deploy_monitoring() {
    log_info "Deploying monitoring stack..."

    if [ -f "monitoring-stack.yml" ]; then
        docker stack deploy -c monitoring-stack.yml sophia-monitoring
        log_success "Monitoring stack deployed"
    else
        log_warning "monitoring-stack.yml not found, skipping monitoring deployment"
    fi
}

# Deploy backup services
deploy_backup() {
    log_info "Deploying backup services..."

    if [ -f "backup-stack.yml" ]; then
        docker stack deploy -c backup-stack.yml sophia-backup
        log_success "Backup services deployed"
    else
        log_warning "backup-stack.yml not found, skipping backup deployment"
    fi
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."

    sleep 10

    # Check service status
    services=$(docker service ls --filter label=com.docker.stack.namespace=sophia-ai --format "{{.Name}}")

    for service in $services; do
        replicas=$(docker service ls --filter name=$service --format "{{.Replicas}}")
        log_info "$service: $replicas"
    done
}

# Show access information
show_access_info() {
    log_info "Deployment complete! Access your services at:"
    echo ""
    echo "  Main Application:  https://api.sophia-ai.lambda.cloud"
    echo "  Traefik Dashboard: https://traefik.sophia-ai.lambda.cloud"
    echo "  Grafana:          https://grafana.sophia-ai.lambda.cloud"
    echo "  Prometheus:       https://prometheus.sophia-ai.lambda.cloud"
    echo ""
    echo "  Internal Services:"
    echo "  - PostgreSQL:     postgres:5432"
    echo "  - Redis:          redis:6379"
    echo "  - Mem0 Server:    mem0-server:8080"
    echo "  - Cortex Server:  cortex-aisql-server:8080"
    echo ""
}

# Main execution
main() {
    log_info "Starting enhanced Sophia AI deployment..."

    # Pre-flight checks
    check_swarm_manager

    # Setup
    create_directories
    create_secrets
    create_networks

    # Deploy stacks
    deploy_main_stack
    deploy_monitoring
    deploy_backup

    # Post-deployment
    wait_for_services
    show_access_info

    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"
