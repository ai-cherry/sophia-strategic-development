#!/bin/bash

# Phase 1 Docker Optimization Deployment Script
# Implements high availability, enhanced health checks, and removes single points of failure
# Usage: ./scripts/deploy_phase1_optimizations.sh [--dry-run] [--rollback]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LAMBDA_LABS_HOST="${LAMBDA_LABS_HOST:-192.222.51.122}"
LAMBDA_LABS_USER="${LAMBDA_LABS_USER:-ubuntu}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
STACK_NAME="sophia-ai"
COMPOSE_FILE="docker-compose.cloud.optimized.yml"
BACKUP_DIR="/opt/sophia-ai/backups/$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Help function
show_help() {
    cat << EOF
Phase 1 Docker Optimization Deployment Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --dry-run       Show what would be deployed without making changes
    --rollback      Rollback to previous deployment
    --help          Show this help message

EXAMPLES:
    $0                    # Deploy Phase 1 optimizations
    $0 --dry-run         # Preview deployment changes
    $0 --rollback        # Rollback to previous version

DESCRIPTION:
    This script implements Phase 1 Docker optimizations including:
    - High availability (2-3 replicas per service)
    - Enhanced health checks with proper timeouts
    - Removal of manager node constraints
    - Improved resource allocation and limits
    - Enhanced monitoring and logging
    - Automated backup configuration

EOF
}

# Parse command line arguments
DRY_RUN=false
ROLLBACK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --rollback)
            ROLLBACK=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validation functions
validate_environment() {
    log_info "Validating deployment environment..."
    
    # Check if running on Lambda Labs
    if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "echo 'Connection successful'" >/dev/null 2>&1; then
        log_error "Cannot connect to Lambda Labs host: ${LAMBDA_LABS_HOST}"
        exit 1
    fi
    
    # Check Docker Swarm status
    if ! ssh "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "docker info --format '{{.Swarm.LocalNodeState}}'" | grep -q "active"; then
        log_error "Docker Swarm is not active on Lambda Labs host"
        exit 1
    fi
    
    # Check if compose file exists
    if [[ ! -f "${PROJECT_ROOT}/${COMPOSE_FILE}" ]]; then
        log_error "Compose file not found: ${PROJECT_ROOT}/${COMPOSE_FILE}"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

# Backup current deployment
backup_current_deployment() {
    log_info "Creating backup of current deployment..."
    
    ssh "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "
        sudo mkdir -p ${BACKUP_DIR}
        
        # Backup current stack configuration
        docker stack ls --format 'table {{.Name}}\t{{.Services}}' > ${BACKUP_DIR}/stack_list.txt
        docker service ls --format 'table {{.Name}}\t{{.Mode}}\t{{.Replicas}}' > ${BACKUP_DIR}/service_list.txt
        
        # Backup current compose file if it exists
        if [[ -f /opt/sophia-ai/docker-compose.current.yml ]]; then
            cp /opt/sophia-ai/docker-compose.current.yml ${BACKUP_DIR}/
        fi
        
        # Backup data directories
        if [[ -d /opt/sophia-ai/data ]]; then
            sudo tar -czf ${BACKUP_DIR}/data_backup.tar.gz -C /opt/sophia-ai data/
        fi
        
        echo 'Backup completed at: ${BACKUP_DIR}'
    "
    
    log_success "Backup created at: ${BACKUP_DIR}"
}

# Deploy optimized configuration
deploy_optimizations() {
    log_info "Deploying Phase 1 Docker optimizations..."
    
    # Copy optimized compose file to Lambda Labs
    scp "${PROJECT_ROOT}/${COMPOSE_FILE}" "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}:/tmp/"
    
    ssh "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "
        # Create necessary directories
        sudo mkdir -p /opt/sophia-ai/data/{postgres,redis,prometheus,grafana,traefik}
        sudo chown -R 1000:1000 /opt/sophia-ai/data/
        
        # Move compose file to deployment location
        sudo mv /tmp/${COMPOSE_FILE} /opt/sophia-ai/
        sudo cp /opt/sophia-ai/${COMPOSE_FILE} /opt/sophia-ai/docker-compose.current.yml
        
        # Set environment variables
        export DOCKER_REGISTRY=${DOCKER_REGISTRY}
        export IMAGE_TAG=latest
        
        # Deploy the optimized stack
        cd /opt/sophia-ai
        docker stack deploy -c ${COMPOSE_FILE} ${STACK_NAME} --with-registry-auth
    "
    
    log_success "Phase 1 optimizations deployed"
}

# Validate deployment
validate_deployment() {
    log_info "Validating deployment health..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        # Check service status
        local services_ready=$(ssh "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "
            docker service ls --filter name=${STACK_NAME} --format '{{.Name}} {{.Replicas}}' | 
            awk '{
                split(\$2, replicas, \"/\");
                if (replicas[1] == replicas[2] && replicas[1] > 0) ready++;
                total++;
            }
            END { print ready \"/\" total }'
        ")
        
        log_info "Services ready: $services_ready"
        
        # Check if all services are ready
        if echo "$services_ready" | grep -q "^[0-9]\+/[0-9]\+$"; then
            local ready=$(echo "$services_ready" | cut -d'/' -f1)
            local total=$(echo "$services_ready" | cut -d'/' -f2)
            
            if [[ "$ready" == "$total" && "$ready" -gt 0 ]]; then
                log_success "All services are healthy and ready"
                return 0
            fi
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            log_error "Deployment validation failed after $max_attempts attempts"
            return 1
        fi
        
        sleep 30
        ((attempt++))
    done
}

# Rollback function
rollback_deployment() {
    log_info "Rolling back to previous deployment..."
    
    # Find the most recent backup
    local latest_backup=$(ssh "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "
        ls -1t /opt/sophia-ai/backups/ | head -1
    ")
    
    if [[ -z "$latest_backup" ]]; then
        log_error "No backup found for rollback"
        exit 1
    fi
    
    log_info "Rolling back to backup: $latest_backup"
    
    ssh "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "
        # Remove current stack
        docker stack rm ${STACK_NAME}
        
        # Wait for stack removal
        sleep 30
        
        # Restore from backup
        if [[ -f /opt/sophia-ai/backups/${latest_backup}/docker-compose.current.yml ]]; then
            cp /opt/sophia-ai/backups/${latest_backup}/docker-compose.current.yml /opt/sophia-ai/
            
            # Redeploy from backup
            cd /opt/sophia-ai
            docker stack deploy -c docker-compose.current.yml ${STACK_NAME} --with-registry-auth
        else
            echo 'No compose file found in backup, manual intervention required'
            exit 1
        fi
    "
    
    log_success "Rollback completed"
}

# Generate deployment report
generate_report() {
    log_info "Generating deployment report..."
    
    local report_file="${PROJECT_ROOT}/phase1_deployment_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Phase 1 Docker Optimization Deployment Report

**Deployment Date**: $(date)
**Lambda Labs Host**: ${LAMBDA_LABS_HOST}
**Stack Name**: ${STACK_NAME}
**Compose File**: ${COMPOSE_FILE}

## Deployment Summary

### Services Deployed
$(ssh "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "docker service ls --filter name=${STACK_NAME} --format 'table {{.Name}}\t{{.Mode}}\t{{.Replicas}}\t{{.Image}}'")

### High Availability Improvements
- **Sophia Backend**: Increased from 1 to 3 replicas
- **Mem0 Server**: Increased from 1 to 2 replicas  
- **Cortex AI SQL**: Increased from 1 to 2 replicas
- **Redis**: Increased from 1 to 2 replicas
- **PostgreSQL**: Increased from 1 to 2 replicas
- **Traefik**: Increased from 1 to 2 replicas
- **Prometheus**: Increased from 1 to 2 replicas
- **Grafana**: Increased from 1 to 2 replicas

### Health Check Enhancements
- Enhanced health check intervals (15-30s)
- Increased retry counts (3-5 retries)
- Proper timeout configurations (5-10s)
- Comprehensive health endpoints

### Resource Optimization
- Removed manager node constraints
- Optimized CPU and memory limits
- Enhanced restart policies
- Improved update strategies

### Network Security
- Encrypted overlay networks
- Enhanced Traefik configuration
- SSL/TLS termination
- Health check load balancing

## Validation Results
$(ssh "${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}" "docker stack ps ${STACK_NAME} --format 'table {{.Name}}\t{{.CurrentState}}\t{{.DesiredState}}\t{{.Error}}'")

## Next Steps
1. Monitor service health for 24 hours
2. Validate application functionality
3. Proceed with Phase 2 (MCP Optimization) if stable
4. Update monitoring dashboards

## Backup Information
- **Backup Location**: ${BACKUP_DIR}
- **Rollback Command**: \`$0 --rollback\`

EOF

    log_success "Deployment report generated: $report_file"
}

# Main execution
main() {
    log_info "Starting Phase 1 Docker Optimization Deployment"
    log_info "Target: ${LAMBDA_LABS_HOST}"
    log_info "Stack: ${STACK_NAME}"
    log_info "Compose: ${COMPOSE_FILE}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN MODE - No changes will be made"
        log_info "Would deploy optimized configuration with:"
        log_info "- High availability (2-3 replicas per service)"
        log_info "- Enhanced health checks"
        log_info "- Removed single points of failure"
        log_info "- Improved resource allocation"
        exit 0
    fi
    
    if [[ "$ROLLBACK" == "true" ]]; then
        validate_environment
        rollback_deployment
        validate_deployment
        log_success "Rollback completed successfully"
        exit 0
    fi
    
    # Normal deployment flow
    validate_environment
    backup_current_deployment
    deploy_optimizations
    
    log_info "Waiting for services to stabilize..."
    sleep 60
    
    if validate_deployment; then
        generate_report
        log_success "Phase 1 Docker optimization deployment completed successfully!"
        log_info "Services are now running with high availability and enhanced health checks"
        log_info "Monitor the deployment and proceed with Phase 2 when stable"
    else
        log_error "Deployment validation failed"
        log_warning "Consider rolling back with: $0 --rollback"
        exit 1
    fi
}

# Execute main function
main "$@"

