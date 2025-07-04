#!/bin/bash

# Sophia AI Deployment and Monitoring Script
# This script deploys the entire stack with monitoring

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Sophia AI Deployment & Monitoring${NC}"
echo "========================================"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to check if ports are available
check_ports() {
    local ports=("8000" "5432" "6379" "9091" "3001" "80" "8080" "9100")
    local all_clear=true
    
    echo -e "${YELLOW}Checking port availability...${NC}"
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${RED}❌ Port $port is already in use${NC}"
            all_clear=false
        fi
    done
    
    if [ "$all_clear" = true ]; then
        echo -e "${GREEN}✅ All ports are available${NC}"
    else
        echo -e "${RED}Please free up the ports before continuing${NC}"
        exit 1
    fi
}

# Function to deploy the stack
deploy_stack() {
    echo -e "${YELLOW}🔧 Deploying Sophia AI stack...${NC}"
    
    # Stop any existing containers
    docker-compose -f docker-compose.monitoring.yml down 2>/dev/null || true
    
    # Start the stack
    docker-compose -f docker-compose.monitoring.yml up -d
    
    echo -e "${GREEN}✅ Stack deployed${NC}"
}

# Function to wait for services to be healthy
wait_for_services() {
    echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
    
    local services=("sophia-backend" "sophia-postgres" "sophia-redis")
    local max_attempts=30
    
    for service in "${services[@]}"; do
        echo -n "Waiting for $service..."
        local attempts=0
        while [ $attempts -lt $max_attempts ]; do
            if docker inspect --format='{{.State.Health.Status}}' $service 2>/dev/null | grep -q "healthy"; then
                echo -e " ${GREEN}✓${NC}"
                break
            fi
            attempts=$((attempts + 1))
            sleep 2
            echo -n "."
        done
        
        if [ $attempts -eq $max_attempts ]; then
            echo -e " ${RED}✗${NC}"
            echo -e "${RED}Service $service failed to become healthy${NC}"
        fi
    done
}

# Function to display service status
display_status() {
    echo -e "\n${BLUE}📊 Service Status${NC}"
    echo "=================="
    
    docker-compose -f docker-compose.monitoring.yml ps
    
    echo -e "\n${BLUE}🌐 Access Points${NC}"
    echo "================"
    echo -e "Sophia API:        ${GREEN}http://localhost:8000${NC}"
    echo -e "Grafana:           ${GREEN}http://localhost:3001${NC} (admin/admin)"
    echo -e "Prometheus:        ${GREEN}http://localhost:9091${NC}"
    echo -e "cAdvisor:          ${GREEN}http://localhost:8080${NC}"
    echo -e "PostgreSQL:        ${GREEN}localhost:5432${NC} (sophia/sophia2024secure)"
    echo -e "Redis:             ${GREEN}localhost:6379${NC}"
}

# Function to show logs
show_logs() {
    echo -e "\n${BLUE}📜 Recent Logs${NC}"
    echo "=============="
    docker-compose -f docker-compose.monitoring.yml logs --tail=20 sophia-backend
}

# Function to create monitoring dashboard
setup_monitoring() {
    echo -e "\n${YELLOW}📈 Setting up monitoring dashboards...${NC}"
    
    # Wait for Grafana to be ready
    sleep 10
    
    # Check if Grafana is accessible
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/health | grep -q "200"; then
        echo -e "${GREEN}✅ Grafana is ready${NC}"
        echo -e "${YELLOW}Please visit http://localhost:3001 and login with admin/admin${NC}"
    else
        echo -e "${YELLOW}⚠️  Grafana is still starting up. Please wait a moment and refresh.${NC}"
    fi
}

# Function to monitor in real-time
monitor_realtime() {
    echo -e "\n${BLUE}📊 Real-time Monitoring${NC}"
    echo "====================="
    echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}\n"
    
    # Show container stats
    docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting deployment process...${NC}\n"
    
    # Run checks
    check_docker
    check_ports
    
    # Deploy
    deploy_stack
    wait_for_services
    
    # Display information
    display_status
    setup_monitoring
    show_logs
    
    echo -e "\n${GREEN}🎉 Deployment complete!${NC}"
    echo -e "${YELLOW}Would you like to monitor in real-time? (y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        monitor_realtime
    fi
}

# Run main function
main 