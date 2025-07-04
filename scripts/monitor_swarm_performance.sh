#!/bin/bash
# Monitor Docker Swarm performance for Sophia AI
# Addresses bottleneck identification and resource tracking

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOPHIA_STACK_NAME="${SOPHIA_STACK_NAME:-sophia-ai}"
ALERT_CPU_THRESHOLD=80
ALERT_MEMORY_THRESHOLD=70
ALERT_DISK_THRESHOLD=85

echo -e "${BLUE}=== Sophia AI Docker Swarm Performance Monitor ===${NC}"
echo "Timestamp: $(date)"
echo "Stack: $SOPHIA_STACK_NAME"
echo ""

# Function to check if we're on a manager node
check_manager_node() {
    if ! docker node ls &>/dev/null; then
        echo -e "${RED}ERROR: This script must be run on a Docker Swarm manager node${NC}"
        exit 1
    fi
}

# Function to format bytes to human readable
format_bytes() {
    local bytes=$1
    if [ $bytes -lt 1024 ]; then
        echo "${bytes}B"
    elif [ $bytes -lt 1048576 ]; then
        echo "$((bytes / 1024))KB"
    elif [ $bytes -lt 1073741824 ]; then
        echo "$((bytes / 1048576))MB"
    else
        echo "$((bytes / 1073741824))GB"
    fi
}

# Node Resource Usage
monitor_nodes() {
    echo -e "${BLUE}=== Node Resource Usage ===${NC}"
    echo "Format: Hostname | Status | Availability | CPU | Memory | Disk"
    echo "----------------------------------------------------------------"
    
    for node_id in $(docker node ls -q); do
        node_info=$(docker node inspect $node_id --format '{{.Description.Hostname}}|{{.Status.State}}|{{.Spec.Availability}}')
        hostname=$(echo $node_info | cut -d'|' -f1)
        status=$(echo $node_info | cut -d'|' -f2)
        availability=$(echo $node_info | cut -d'|' -f3)
        
        # Get node resources (if available)
        if docker node inspect $node_id --format '{{.Description.Resources}}' &>/dev/null; then
            cpu_nano=$(docker node inspect $node_id --format '{{.Description.Resources.NanoCPUs}}')
            memory=$(docker node inspect $node_id --format '{{.Description.Resources.MemoryBytes}}')
            cpu_cores=$((cpu_nano / 1000000000))
            memory_gb=$((memory / 1073741824))
            
            # Try to get actual usage via node exporter or system stats
            # This requires node-exporter or similar monitoring
            usage_info="CPUs: $cpu_cores | RAM: ${memory_gb}GB"
        else
            usage_info="Resources: N/A"
        fi
        
        # Color code based on status
        if [ "$status" == "ready" ] && [ "$availability" == "active" ]; then
            echo -e "${GREEN}✓ $hostname | $status | $availability | $usage_info${NC}"
        else
            echo -e "${YELLOW}⚠ $hostname | $status | $availability | $usage_info${NC}"
        fi
    done
    echo ""
}

# Service Health and Replicas
monitor_services() {
    echo -e "${BLUE}=== Service Health & Replicas ===${NC}"
    echo "Format: Service | Replicas (Running/Desired) | Image | Ports"
    echo "----------------------------------------------------------------"
    
    for service_id in $(docker service ls --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME -q); do
        service_info=$(docker service inspect $service_id --format '{{.Spec.Name}}|{{.Spec.Mode.Replicated.Replicas}}|{{.Spec.TaskTemplate.ContainerSpec.Image}}')
        service_name=$(echo $service_info | cut -d'|' -f1)
        desired_replicas=$(echo $service_info | cut -d'|' -f2)
        image=$(echo $service_info | cut -d'|' -f3 | cut -d':' -f2)
        
        # Get running replicas
        running_replicas=$(docker service ps $service_id --filter "desired-state=running" -q | wc -l)
        
        # Get ports
        ports=$(docker service inspect $service_id --format '{{range .Endpoint.Ports}}{{.PublishedPort}}:{{.TargetPort}} {{end}}')
        [ -z "$ports" ] && ports="none"
        
        # Color code based on health
        if [ "$running_replicas" -eq "$desired_replicas" ]; then
            echo -e "${GREEN}✓ $service_name | $running_replicas/$desired_replicas | $image | $ports${NC}"
        elif [ "$running_replicas" -eq 0 ]; then
            echo -e "${RED}✗ $service_name | $running_replicas/$desired_replicas | $image | $ports${NC}"
        else
            echo -e "${YELLOW}⚠ $service_name | $running_replicas/$desired_replicas | $image | $ports${NC}"
        fi
        
        # Show failed tasks
        failed_count=$(docker service ps $service_id --filter "desired-state=shutdown" -q | wc -l)
        if [ "$failed_count" -gt 0 ]; then
            echo -e "  ${YELLOW}└─ Failed tasks: $failed_count${NC}"
        fi
    done
    echo ""
}

# Resource Constraints and Placement
monitor_constraints() {
    echo -e "${BLUE}=== Resource Limits & Placement Constraints ===${NC}"
    
    for service_id in $(docker service ls --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME -q); do
        service_name=$(docker service inspect $service_id --format '{{.Spec.Name}}')
        
        # Get resource limits
        cpu_limit=$(docker service inspect $service_id --format '{{.Spec.TaskTemplate.Resources.Limits.NanoCPUs}}' 2>/dev/null || echo "0")
        memory_limit=$(docker service inspect $service_id --format '{{.Spec.TaskTemplate.Resources.Limits.MemoryBytes}}' 2>/dev/null || echo "0")
        
        # Get placement constraints
        constraints=$(docker service inspect $service_id --format '{{range .Spec.TaskTemplate.Placement.Constraints}}{{.}} {{end}}' 2>/dev/null)
        
        if [ "$cpu_limit" != "0" ] || [ "$memory_limit" != "0" ] || [ -n "$constraints" ]; then
            echo "Service: $service_name"
            
            if [ "$cpu_limit" != "0" ]; then
                cpu_cores=$(echo "scale=2; $cpu_limit / 1000000000" | bc)
                echo "  CPU Limit: ${cpu_cores} cores"
            else
                echo -e "  ${YELLOW}CPU Limit: none (RISK: unbounded CPU usage)${NC}"
            fi
            
            if [ "$memory_limit" != "0" ]; then
                memory_mb=$((memory_limit / 1048576))
                echo "  Memory Limit: ${memory_mb}MB"
            else
                echo -e "  ${YELLOW}Memory Limit: none (RISK: unbounded memory usage)${NC}"
            fi
            
            if [ -n "$constraints" ]; then
                echo "  Placement: $constraints"
            fi
            echo ""
        fi
    done
}

# Network Performance
monitor_networks() {
    echo -e "${BLUE}=== Overlay Network Status ===${NC}"
    
    for network_id in $(docker network ls --filter driver=overlay --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME -q); do
        network_info=$(docker network inspect $network_id --format '{{.Name}}|{{.Driver}}|{{.Scope}}|{{.Internal}}|{{.Attachable}}')
        network_name=$(echo $network_info | cut -d'|' -f1)
        driver=$(echo $network_info | cut -d'|' -f2)
        scope=$(echo $network_info | cut -d'|' -f3)
        internal=$(echo $network_info | cut -d'|' -f4)
        attachable=$(echo $network_info | cut -d'|' -f5)
        
        # Count connected services
        service_count=$(docker network inspect $network_id --format '{{len .Containers}}')
        
        echo "Network: $network_name"
        echo "  Type: $driver ($scope)"
        echo "  Internal: $internal | Attachable: $attachable"
        echo "  Connected containers: $service_count"
        echo ""
    done
}

# Volume Performance
monitor_volumes() {
    echo -e "${BLUE}=== Persistent Volumes ===${NC}"
    
    # List volumes used by the stack
    for volume_name in $(docker volume ls --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME --format '{{.Name}}'); do
        volume_info=$(docker volume inspect $volume_name --format '{{.Driver}}|{{.Mountpoint}}')
        driver=$(echo $volume_info | cut -d'|' -f1)
        mountpoint=$(echo $volume_info | cut -d'|' -f2)
        
        echo "Volume: $volume_name"
        echo "  Driver: $driver"
        echo "  Mount: $mountpoint"
        
        # Check disk usage if possible
        if [ -d "$mountpoint" ] && command -v df &>/dev/null; then
            disk_usage=$(df -h "$mountpoint" 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//')
            if [ -n "$disk_usage" ]; then
                echo -n "  Disk Usage: $disk_usage%"
                if [ "$disk_usage" -gt "$ALERT_DISK_THRESHOLD" ]; then
                    echo -e " ${RED}(WARNING: High disk usage!)${NC}"
                else
                    echo ""
                fi
            fi
        fi
        echo ""
    done
}

# Performance Alerts
check_alerts() {
    echo -e "${BLUE}=== Performance Alerts ===${NC}"
    
    alerts=0
    
    # Check for services with no replicas running
    for service_id in $(docker service ls --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME -q); do
        service_name=$(docker service inspect $service_id --format '{{.Spec.Name}}')
        running_replicas=$(docker service ps $service_id --filter "desired-state=running" -q | wc -l)
        
        if [ "$running_replicas" -eq 0 ]; then
            echo -e "${RED}🚨 CRITICAL: Service '$service_name' has no running replicas${NC}"
            alerts=$((alerts + 1))
        fi
    done
    
    # Check for services without resource limits
    for service_id in $(docker service ls --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME -q); do
        service_name=$(docker service inspect $service_id --format '{{.Spec.Name}}')
        cpu_limit=$(docker service inspect $service_id --format '{{.Spec.TaskTemplate.Resources.Limits.NanoCPUs}}' 2>/dev/null || echo "0")
        memory_limit=$(docker service inspect $service_id --format '{{.Spec.TaskTemplate.Resources.Limits.MemoryBytes}}' 2>/dev/null || echo "0")
        
        if [ "$cpu_limit" == "0" ] && [ "$memory_limit" == "0" ]; then
            echo -e "${YELLOW}⚠️  WARNING: Service '$service_name' has no resource limits${NC}"
            alerts=$((alerts + 1))
        fi
    done
    
    # Check for single replica services (potential SPOF)
    for service_id in $(docker service ls --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME -q); do
        service_name=$(docker service inspect $service_id --format '{{.Spec.Name}}')
        replicas=$(docker service inspect $service_id --format '{{.Spec.Mode.Replicated.Replicas}}')
        
        if [ "$replicas" -eq 1 ] && [[ ! "$service_name" =~ (postgres|mysql|db) ]]; then
            echo -e "${YELLOW}⚠️  WARNING: Service '$service_name' is running with only 1 replica (SPOF)${NC}"
            alerts=$((alerts + 1))
        fi
    done
    
    if [ "$alerts" -eq 0 ]; then
        echo -e "${GREEN}✅ No performance alerts detected${NC}"
    else
        echo -e "\n${RED}Total alerts: $alerts${NC}"
    fi
    echo ""
}

# Generate recommendations
generate_recommendations() {
    echo -e "${BLUE}=== Recommendations ===${NC}"
    
    # Check for optimization opportunities
    recommendations=0
    
    # Single replica services
    single_replica_services=$(docker service ls --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME --format '{{.Name}}:{{.Replicas}}' | grep ':1/' | cut -d':' -f1)
    if [ -n "$single_replica_services" ]; then
        echo "📌 Scale these single-replica services for high availability:"
        for service in $single_replica_services; do
            echo "   docker service scale ${SOPHIA_STACK_NAME}_$service=3"
        done
        recommendations=$((recommendations + 1))
        echo ""
    fi
    
    # Services without limits
    services_without_limits=$(docker service ls --filter label=com.docker.stack.namespace=$SOPHIA_STACK_NAME -q | while read service_id; do
        cpu=$(docker service inspect $service_id --format '{{.Spec.TaskTemplate.Resources.Limits.NanoCPUs}}' 2>/dev/null || echo "0")
        if [ "$cpu" == "0" ]; then
            docker service inspect $service_id --format '{{.Spec.Name}}'
        fi
    done)
    
    if [ -n "$services_without_limits" ]; then
        echo "📌 Add resource limits to prevent node saturation:"
        echo "   Run: python scripts/optimize_docker_swarm_resources.py docker-compose.cloud.yml"
        recommendations=$((recommendations + 1))
        echo ""
    fi
    
    if [ "$recommendations" -eq 0 ]; then
        echo -e "${GREEN}✅ No immediate optimizations needed${NC}"
    fi
}

# Main execution
main() {
    check_manager_node
    
    monitor_nodes
    monitor_services
    monitor_constraints
    monitor_networks
    monitor_volumes
    check_alerts
    generate_recommendations
    
    echo -e "${BLUE}=== Monitoring Complete ===${NC}"
    echo "Next run: $(date -d '+5 minutes')"
}

# Run main function
main 