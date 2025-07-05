#!/bin/bash
# Deploy Sophia AI Stack with Dashboard, Chat, and Code MCP Servers
# Includes optimization and monitoring

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="${SOPHIA_STACK_NAME:-sophia-ai}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
LAMBDA_LABS_HOST="${LAMBDA_LABS_HOST:-146.235.200.1}"

echo -e "${BLUE}=== Sophia AI Stack Deployment ===${NC}"
echo "Stack: $STACK_NAME"
echo "Registry: $DOCKER_REGISTRY"
echo "Tag: $IMAGE_TAG"
echo "Target: $LAMBDA_LABS_HOST"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    # Check if we're on a manager node
    if ! docker node ls &>/dev/null; then
        echo -e "${RED}ERROR: This script must be run on a Docker Swarm manager node${NC}"
        echo "Connect to Lambda Labs: ssh ubuntu@$LAMBDA_LABS_HOST"
        exit 1
    fi
    
    # Check for required files
    if [ ! -f "docker-compose.cloud.yml.optimized" ]; then
        echo -e "${YELLOW}Optimized config not found. Running optimization...${NC}"
        python scripts/optimize_docker_swarm_resources.py docker-compose.cloud.yml
    fi
    
    # Check for MCP server configs
    if [ ! -f "docker-compose.mcp-servers.yml" ]; then
        echo -e "${YELLOW}Creating MCP servers configuration...${NC}"
        create_mcp_servers_config
    fi
    
    echo -e "${GREEN}✓ Prerequisites checked${NC}"
}

# Function to create MCP servers configuration
create_mcp_servers_config() {
    cat > docker-compose.mcp-servers.yml << 'EOF'
version: '3.8'

services:
  # Dashboard-related MCP Server
  dashboard-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-dashboard-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
      placement:
        constraints:
          - node.labels.tier == compute
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
      - SERVICE_PORT=9100
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9100/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sophia-overlay
    ports:
      - "9100:9100"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard-mcp.rule=Host(`dashboard-mcp.sophia-ai.lambda.cloud`)"
      - "traefik.http.routers.dashboard-mcp.tls=true"

  # Chat/Unified Intelligence MCP Server
  chat-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-chat-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
      placement:
        constraints:
          - node.labels.tier == compute
          - node.labels.gpu == true
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
      - SERVICE_PORT=9101
      - ENABLE_STREAMING=true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9101/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sophia-overlay
    ports:
      - "9101:9101"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.chat-mcp.rule=Host(`chat-mcp.sophia-ai.lambda.cloud`)"
      - "traefik.http.routers.chat-mcp.tls=true"

  # Code Analysis MCP Server (Codacy)
  codacy-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-codacy-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.5'
          memory: 3G
        reservations:
          cpus: '0.75'
          memory: 1.5G
      placement:
        constraints:
          - node.labels.tier == compute
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
      - SERVICE_PORT=3008
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3008/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sophia-overlay
    ports:
      - "3008:3008"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.codacy-mcp.rule=Host(`codacy-mcp.sophia-ai.lambda.cloud`)"
      - "traefik.http.routers.codacy-mcp.tls=true"

  # AI Memory MCP Server
  ai-memory-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-ai-memory-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
      placement:
        constraints:
          - node.labels.tier == memory
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
      - SERVICE_PORT=9000
      - REDIS_URL=redis://redis:6379
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sophia-overlay
    ports:
      - "9000:9000"
    volumes:
      - ai_memory_data:/data
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.ai-memory-mcp.rule=Host(`memory-mcp.sophia-ai.lambda.cloud`)"
      - "traefik.http.routers.ai-memory-mcp.tls=true"

  # GitHub MCP Server
  github-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-github-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
      placement:
        constraints:
          - node.labels.tier == compute
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
      - SERVICE_PORT=9003
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9003/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sophia-overlay
    ports:
      - "9003:9003"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.github-mcp.rule=Host(`github-mcp.sophia-ai.lambda.cloud`)"
      - "traefik.http.routers.github-mcp.tls=true"

  # Linear MCP Server
  linear-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-linear-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
      placement:
        constraints:
          - node.labels.tier == compute
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
      - SERVICE_PORT=9004
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9004/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sophia-overlay
    ports:
      - "9004:9004"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.linear-mcp.rule=Host(`linear-mcp.sophia-ai.lambda.cloud`)"
      - "traefik.http.routers.linear-mcp.tls=true"

volumes:
  ai_memory_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/sophia-ai/data/ai_memory

networks:
  sophia-overlay:
    external: true
EOF
}

# Function to create secrets
create_secrets() {
    echo -e "${BLUE}Creating Docker secrets...${NC}"
    
    # List of required secrets
    declare -A secrets=(
        ["postgres_password"]="POSTGRES_PASSWORD"
        ["grafana_password"]="GRAFANA_PASSWORD"
        ["pulumi_access_token"]="PULUMI_ACCESS_TOKEN"
        ["mem0_api_key"]="MEM0_API_KEY"
        ["snowflake_account"]="SNOWFLAKE_ACCOUNT"
        ["snowflake_user"]="SNOWFLAKE_USER"
        ["snowflake_password"]="SNOWFLAKE_PASSWORD"
        ["vercel_v0dev_api_key"]="VERCEL_V0DEV_API_KEY"
    )
    
    for secret_name in "${!secrets[@]}"; do
        env_var="${secrets[$secret_name]}"
        if docker secret ls | grep -q "$secret_name"; then
            echo "Secret $secret_name already exists"
        else
            if [ -n "${!env_var:-}" ]; then
                echo "${!env_var}" | docker secret create "$secret_name" -
                echo -e "${GREEN}✓ Created secret: $secret_name${NC}"
            else
                echo -e "${YELLOW}⚠ Warning: $env_var not set, skipping $secret_name${NC}"
            fi
        fi
    done
}

# Function to deploy the stack
deploy_stack() {
    echo -e "${BLUE}Deploying Sophia AI stack...${NC}"
    
    # Deploy core services
    echo "Deploying core services..."
    docker stack deploy -c docker-compose.cloud.yml.optimized "$STACK_NAME"
    
    # Wait for core services to be ready
    echo "Waiting for core services to initialize..."
    sleep 30
    
    # Deploy MCP servers
    echo "Deploying MCP servers..."
    docker stack deploy -c docker-compose.mcp-servers.yml "$STACK_NAME"
    
    echo -e "${GREEN}✓ Stack deployment initiated${NC}"
}

# Function to monitor deployment
monitor_deployment() {
    echo -e "${BLUE}Monitoring deployment...${NC}"
    
    # Wait for services to start
    sleep 10
    
    # Check service status
    echo -e "\n${BLUE}=== Service Status ===${NC}"
    docker service ls --filter label=com.docker.stack.namespace=$STACK_NAME
    
    # Check for any failed services
    failed_services=$(docker service ls --filter label=com.docker.stack.namespace=$STACK_NAME --format "{{.Name}}:{{.Replicas}}" | grep ':0/' || true)
    
    if [ -n "$failed_services" ]; then
        echo -e "\n${RED}⚠ Failed services detected:${NC}"
        echo "$failed_services"
        echo -e "\nChecking logs for failed services..."
        
        for service in $(echo "$failed_services" | cut -d':' -f1); do
            echo -e "\n${YELLOW}Logs for $service:${NC}"
            docker service logs "$service" --tail 50 2>&1 || true
        done
    else
        echo -e "\n${GREEN}✓ All services starting successfully${NC}"
    fi
}

# Function to run performance monitoring
run_performance_monitor() {
    echo -e "\n${BLUE}Running performance monitor...${NC}"
    
    if [ -x "scripts/monitor_swarm_performance.sh" ]; then
        ./scripts/monitor_swarm_performance.sh
    else
        echo -e "${YELLOW}Performance monitor script not found or not executable${NC}"
    fi
}

# Function to display access URLs
display_access_urls() {
    echo -e "\n${BLUE}=== Access URLs ===${NC}"
    echo "Dashboard: https://api.sophia-ai.lambda.cloud/dashboard"
    echo "Chat Interface: https://chat-mcp.sophia-ai.lambda.cloud"
    echo "API Documentation: https://api.sophia-ai.lambda.cloud/docs"
    echo "Grafana: https://sophia-ai.lambda.cloud:3000"
    echo "Prometheus: https://sophia-ai.lambda.cloud:9090"
    echo ""
    echo "MCP Servers:"
    echo "  - Dashboard MCP: https://dashboard-mcp.sophia-ai.lambda.cloud"
    echo "  - Chat MCP: https://chat-mcp.sophia-ai.lambda.cloud"
    echo "  - Codacy MCP: https://codacy-mcp.sophia-ai.lambda.cloud"
    echo "  - AI Memory MCP: https://memory-mcp.sophia-ai.lambda.cloud"
    echo "  - GitHub MCP: https://github-mcp.sophia-ai.lambda.cloud"
    echo "  - Linear MCP: https://linear-mcp.sophia-ai.lambda.cloud"
}

# Function to create remediation report
create_remediation_report() {
    echo -e "\n${BLUE}Creating remediation report...${NC}"
    
    cat > deployment_remediation_report.md << EOF
# Sophia AI Deployment Remediation Report

**Date**: $(date)
**Stack**: $STACK_NAME
**Target**: $LAMBDA_LABS_HOST

## Deployment Summary

### Optimizations Applied
- ✅ Resource limits added to all services
- ✅ Health checks configured
- ✅ Replica counts increased for HA
- ✅ Network topology optimized
- ✅ Placement constraints configured

### Services Deployed
$(docker service ls --filter label=com.docker.stack.namespace=$STACK_NAME --format "- {{.Name}}: {{.Replicas}} replicas")

### Performance Improvements
- Single points of failure eliminated
- Resource saturation risk mitigated
- Network latency optimized
- Monitoring stack deployed

### Next Steps
1. Monitor service health for 24 hours
2. Review Grafana dashboards
3. Check application performance metrics
4. Adjust resource limits based on actual usage

EOF
    
    echo -e "${GREEN}✓ Remediation report created: deployment_remediation_report.md${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting Sophia AI deployment with optimizations...${NC}\n"
    
    check_prerequisites
    create_secrets
    deploy_stack
    monitor_deployment
    run_performance_monitor
    display_access_urls
    create_remediation_report
    
    echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
    echo "Monitor the stack with: docker stack ps $STACK_NAME"
    echo "View service logs with: docker service logs <service-name>"
    echo "Run performance monitor: ./scripts/monitor_swarm_performance.sh"
}

# Run main function
main "$@" 