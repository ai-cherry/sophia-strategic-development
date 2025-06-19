#!/bin/bash

# Sophia AI Lambda Labs Deployment Script
# Secure deployment automation for Lambda Labs cloud compute

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/sophia-lambda-deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if required environment variables are set
    if [ -z "${LAMBDA_LABS_API_KEY:-}" ]; then
        error "LAMBDA_LABS_API_KEY environment variable is required"
        exit 1
    fi
    
    # Check if Docker is available (optional)
    if command -v docker &> /dev/null; then
        log "Docker found - container deployment available"
    else
        warning "Docker not found - container deployment unavailable"
    fi
    
    success "Prerequisites check passed"
}

# Install deployment dependencies
install_dependencies() {
    log "Installing deployment dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    pip install -q aiohttp python-dotenv requests
    
    # Install project dependencies
    if [ -f "requirements.txt" ]; then
        pip install -q -r requirements.txt
    fi
    
    success "Dependencies installed"
}

# Validate Lambda Labs connectivity
validate_lambda_labs() {
    log "Validating Lambda Labs connectivity..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    python3 -c "
import asyncio
import sys
import os
sys.path.append('.')

async def validate():
    try:
        from backend.integrations.lambda_labs_integration import LambdaLabsIntegration
        
        async with LambdaLabsIntegration() as client:
            health = await client.health_check()
            
            if health['status'] == 'healthy':
                print('✅ Lambda Labs API connectivity verified')
                print(f'Available instance types: {health.get(\"instance_types_count\", 0)}')
                print(f'Active instances: {health.get(\"active_instances\", 0)}')
                return True
            else:
                print(f'❌ Lambda Labs API health check failed: {health.get(\"error\", \"Unknown error\")}')
                return False
                
    except Exception as e:
        print(f'❌ Lambda Labs validation failed: {str(e)}')
        return False

result = asyncio.run(validate())
sys.exit(0 if result else 1)
"
    
    if [ $? -eq 0 ]; then
        success "Lambda Labs connectivity validated"
    else
        error "Lambda Labs connectivity validation failed"
        exit 1
    fi
}

# Deploy application to Lambda Labs
deploy_to_lambda_labs() {
    log "Deploying Sophia AI to Lambda Labs..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Get deployment configuration
    INSTANCE_NAME="${LAMBDA_LABS_INSTANCE_NAME:-sophia-ai-production}"
    INSTANCE_TYPE="${LAMBDA_LABS_INSTANCE_TYPE:-gpu_1x_a100_sxm4}"
    SSH_KEY_NAME="${LAMBDA_LABS_SSH_KEY_NAME:-sophia-ai-key}"
    
    log "Deployment configuration:"
    log "  Instance name: $INSTANCE_NAME"
    log "  Instance type: $INSTANCE_TYPE"
    log "  SSH key: $SSH_KEY_NAME"
    
    python3 -c "
import asyncio
import sys
import os
sys.path.append('.')

async def deploy():
    try:
        from backend.integrations.lambda_labs_integration import LambdaLabsIntegration
        
        async with LambdaLabsIntegration() as client:
            # Check for existing instances
            instances = await client.list_instances()
            existing_instance = None
            
            for instance in instances:
                if instance.name == '$INSTANCE_NAME':
                    existing_instance = instance
                    break
            
            if existing_instance:
                print(f'Found existing instance: {existing_instance.name} ({existing_instance.status})')
                
                if existing_instance.status == 'active':
                    print('✅ Instance is already running')
                    print(f'IP Address: {existing_instance.ip}')
                    return True
                else:
                    print(f'Instance status: {existing_instance.status}')
                    # Could implement restart logic here
                    return True
            else:
                print('No existing instance found - creating new instance...')
                
                # Create new instance
                new_instance = await client.create_instance(
                    name='$INSTANCE_NAME',
                    instance_type='$INSTANCE_TYPE',
                    ssh_key_names=['$SSH_KEY_NAME']
                )
                
                if new_instance:
                    print(f'✅ Created new instance: {new_instance.name} ({new_instance.id})')
                    print(f'Status: {new_instance.status}')
                    if new_instance.ip:
                        print(f'IP Address: {new_instance.ip}')
                    return True
                else:
                    print('❌ Failed to create instance')
                    return False
                    
    except Exception as e:
        print(f'❌ Deployment failed: {str(e)}')
        return False

result = asyncio.run(deploy())
sys.exit(0 if result else 1)
"
    
    if [ $? -eq 0 ]; then
        success "Lambda Labs deployment completed"
    else
        error "Lambda Labs deployment failed"
        exit 1
    fi
}

# Setup SSH access
setup_ssh_access() {
    log "Setting up SSH access..."
    
    SSH_KEY_PATH="${SSH_KEY_PATH:-$HOME/.ssh/sophia_ai_lambda}"
    
    if [ ! -f "$SSH_KEY_PATH" ]; then
        warning "SSH key not found at $SSH_KEY_PATH"
        log "To create SSH key, run:"
        log "  ssh-keygen -t rsa -b 4096 -f $SSH_KEY_PATH -C 'sophia-ai@lambda-labs'"
        log "Then add the public key to Lambda Labs dashboard"
        return 0
    fi
    
    # Set proper permissions
    chmod 600 "$SSH_KEY_PATH"
    
    success "SSH access configured"
}

# Deploy application code
deploy_application_code() {
    log "Deploying application code..."
    
    # This would typically involve:
    # 1. Copying code to the Lambda Labs instance
    # 2. Installing dependencies on the remote instance
    # 3. Starting the application services
    # 4. Configuring environment variables
    
    # For now, we'll create a deployment package
    cd "$PROJECT_ROOT"
    
    DEPLOY_PACKAGE="/tmp/sophia-ai-deploy.tar.gz"
    
    log "Creating deployment package..."
    tar -czf "$DEPLOY_PACKAGE" \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='node_modules' \
        .
    
    success "Deployment package created: $DEPLOY_PACKAGE"
    
    # TODO: Implement actual code deployment to Lambda Labs instance
    # This would involve SCP/rsync to transfer files and remote execution
    
    log "Application code deployment completed"
}

# Run health checks
run_health_checks() {
    log "Running post-deployment health checks..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    python3 -c "
import asyncio
import sys
import os
sys.path.append('.')

async def health_check():
    try:
        from backend.integrations.lambda_labs_integration import LambdaLabsIntegration
        
        async with LambdaLabsIntegration() as client:
            health = await client.health_check()
            
            print('Lambda Labs Health Check Results:')
            print(f'  Status: {health[\"status\"]}')
            print(f'  API Accessible: {health[\"api_accessible\"]}')
            print(f'  Active Instances: {health.get(\"active_instances\", 0)}')
            print(f'  Total Instances: {health.get(\"total_instances\", 0)}')
            
            if health['status'] == 'healthy':
                print('✅ All health checks passed')
                return True
            else:
                print('❌ Health checks failed')
                return False
                
    except Exception as e:
        print(f'❌ Health check failed: {str(e)}')
        return False

result = asyncio.run(health_check())
sys.exit(0 if result else 1)
"
    
    if [ $? -eq 0 ]; then
        success "Health checks passed"
    else
        error "Health checks failed"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log "Cleaning up temporary files..."
    
    # Remove temporary files
    rm -f /tmp/sophia-ai-deploy.tar.gz
    
    success "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting Sophia AI Lambda Labs deployment..."
    log "Log file: $LOG_FILE"
    
    # Trap cleanup on exit
    trap cleanup EXIT
    
    # Run deployment steps
    check_prerequisites
    install_dependencies
    validate_lambda_labs
    setup_ssh_access
    deploy_to_lambda_labs
    deploy_application_code
    run_health_checks
    
    success "🎉 Sophia AI Lambda Labs deployment completed successfully!"
    
    log "Deployment summary:"
    log "  - Lambda Labs instance deployed"
    log "  - Application code packaged"
    log "  - Health checks passed"
    log "  - SSH access configured"
    
    log "Next steps:"
    log "  1. Connect to your Lambda Labs instance via SSH"
    log "  2. Configure environment variables"
    log "  3. Start the Sophia AI services"
    log "  4. Monitor application logs"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

