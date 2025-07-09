#!/bin/bash
# Docker Swarm Network Troubleshooting Script
# Implements comprehensive network debugging from best practices guide

set -euo pipefail

MASTER_IP="192.222.58.232"
SSH_KEY="$HOME/.ssh/sophia2025"
STACK_NAME="sophia-ai"

echo "🌐 Docker Swarm Network Troubleshooting"
echo "======================================="
echo "Swarm Manager: $MASTER_IP"
echo "Stack: $STACK_NAME"
echo ""

# Function to execute commands on Swarm manager
swarm_exec() {
    ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "$1"
}

# 1. Network Discovery and Status
check_network_discovery() {
    echo "🔍 Network Discovery and Status"
    echo "==============================="

    echo "📋 All Docker Networks:"
    swarm_exec "sudo docker network ls"

    echo ""
    echo "🌐 Overlay Networks Details:"
    swarm_exec "sudo docker network ls --filter driver=overlay --format 'table {{.Name}}\t{{.Driver}}\t{{.Scope}}'"

    echo ""
    echo "🔗 Swarm Overlay Network Inspection:"
    local overlay_networks=$(swarm_exec "sudo docker network ls --filter driver=overlay --format '{{.Name}}' | grep -v ingress")

    for network in $overlay_networks; do
        echo "Network: $network"
        swarm_exec "sudo docker network inspect $network --format '{{json .IPAM}}' | jq -r '.Config[0] // empty'"
        echo ""
    done
}

# 2. Service Network Connectivity Test
test_service_connectivity() {
    echo "🚦 Service Network Connectivity Test"
    echo "===================================="

    echo "📊 Service Network Mapping:"
    swarm_exec "sudo docker service ps $STACK_NAME --format 'table {{.Name}}\t{{.Node}}\t{{.CurrentState}}'"

    echo ""
    echo "🔍 Testing Inter-Service Connectivity:"

    # Get backend container ID
    local backend_container=$(swarm_exec "sudo docker ps --filter 'label=com.docker.swarm.service.name=${STACK_NAME}_sophia-backend' --format '{{.ID}}' | head -1")

    if [ -n "$backend_container" ]; then
        echo "Backend container found: $backend_container"

        # Test connectivity to different services
        echo ""
        echo "🧪 Testing connectivity from backend to:"

        # Test Redis connectivity
        echo "- Redis:"
        swarm_exec "sudo docker exec $backend_container ping -c 2 redis 2>/dev/null && echo '  ✅ Redis reachable' || echo '  ❌ Redis unreachable'"

        # Test PostgreSQL connectivity
        echo "- PostgreSQL:"
        swarm_exec "sudo docker exec $backend_container ping -c 2 postgres 2>/dev/null && echo '  ✅ PostgreSQL reachable' || echo '  ❌ PostgreSQL unreachable'"

        # Test Traefik connectivity
        echo "- Traefik:"
        swarm_exec "sudo docker exec $backend_container ping -c 2 traefik 2>/dev/null && echo '  ✅ Traefik reachable' || echo '  ❌ Traefik unreachable'"

    else
        echo "❌ Backend container not found - cannot test connectivity"
    fi

    echo ""
}

# 3. Port and Firewall Analysis
check_ports_and_firewall() {
    echo "🔥 Port and Firewall Analysis"
    echo "============================="

    echo "🚪 Docker Swarm Required Ports:"
    echo "- 2377/tcp (cluster management)"
    echo "- 7946/tcp+udp (node communication)"
    echo "- 4789/udp (overlay network traffic)"
    echo ""

    echo "📊 Current Port Status:"
    # Check if required ports are listening
    echo "Port 2377 (cluster management):"
    swarm_exec "sudo netstat -tlnp | grep :2377 && echo '  ✅ Listening' || echo '  ❌ Not listening'"

    echo "Port 7946 (node communication):"
    swarm_exec "sudo netstat -tlnp | grep :7946 && echo '  ✅ TCP Listening' || echo '  ❌ TCP Not listening'"
    swarm_exec "sudo netstat -ulnp | grep :7946 && echo '  ✅ UDP Listening' || echo '  ❌ UDP Not listening'"

    echo "Port 4789 (overlay network):"
    swarm_exec "sudo netstat -ulnp | grep :4789 && echo '  ✅ UDP Listening' || echo '  ❌ UDP Not listening'"

    echo ""
    echo "🔥 Firewall Status:"
    swarm_exec "sudo ufw status | head -5"

    echo ""
    echo "🌐 Exposed Application Ports:"
    swarm_exec "sudo netstat -tlnp | grep -E ':(8000|8080|3000|5432|6379)' || echo 'No application ports found listening'"
}

# 4. Overlay Network Deep Inspection
inspect_overlay_networks() {
    echo "🔬 Overlay Network Deep Inspection"
    echo "=================================="

    local overlay_net="${STACK_NAME}_sophia-overlay"

    echo "🔍 Inspecting overlay network: $overlay_net"
    if swarm_exec "sudo docker network ls | grep -q $overlay_net"; then
        echo "✅ Overlay network exists"

        echo ""
        echo "📋 Network Configuration:"
        swarm_exec "sudo docker network inspect $overlay_net --format '{{json .IPAM}}'"

        echo ""
        echo "🔗 Connected Containers:"
        swarm_exec "sudo docker network inspect $overlay_net --format '{{range .Containers}}{{.Name}} - {{.IPv4Address}}{{println}}{{end}}'"

        echo ""
        echo "🏷️ Network Labels:"
        swarm_exec "sudo docker network inspect $overlay_net --format '{{json .Labels}}'"

    else
        echo "❌ Overlay network not found: $overlay_net"
        echo "Creating overlay network..."
        swarm_exec "sudo docker network create --driver=overlay --attachable $overlay_net"
    fi
}

# 5. DNS Resolution Test
test_dns_resolution() {
    echo "🌐 DNS Resolution Test"
    echo "====================="

    local backend_container=$(swarm_exec "sudo docker ps --filter 'label=com.docker.swarm.service.name=${STACK_NAME}_sophia-backend' --format '{{.ID}}' | head -1")

    if [ -n "$backend_container" ]; then
        echo "🧪 Testing DNS resolution from backend container:"

        # Test internal service discovery
        echo ""
        echo "📍 Internal Service Discovery:"
        swarm_exec "sudo docker exec $backend_container nslookup redis 2>/dev/null | grep -A2 'Name:' && echo '  ✅ Redis DNS working' || echo '  ❌ Redis DNS failed'"
        swarm_exec "sudo docker exec $backend_container nslookup postgres 2>/dev/null | grep -A2 'Name:' && echo '  ✅ PostgreSQL DNS working' || echo '  ❌ PostgreSQL DNS failed'"

        echo ""
        echo "🌍 External DNS Resolution:"
        swarm_exec "sudo docker exec $backend_container nslookup google.com 2>/dev/null | grep -A2 'Name:' && echo '  ✅ External DNS working' || echo '  ❌ External DNS failed'"

        echo ""
        echo "🔍 DNS Configuration:"
        swarm_exec "sudo docker exec $backend_container cat /etc/resolv.conf"

    else
        echo "❌ Backend container not found - cannot test DNS"
    fi
}

# 6. Traffic Flow Analysis
analyze_traffic_flow() {
    echo "📊 Traffic Flow Analysis"
    echo "======================="

    echo "🚦 Ingress Network Traffic:"
    swarm_exec "sudo docker network inspect ingress --format '{{json .Containers}}' | jq -r 'to_entries[] | \"Container: \" + .value.Name + \" IP: \" + .value.IPv4Address'"

    echo ""
    echo "📈 Service Port Mappings:"
    swarm_exec "sudo docker service inspect ${STACK_NAME}_sophia-backend --format '{{json .Endpoint.Ports}}' | jq -r '.[] | \"Port \" + (.PublishedPort | tostring) + \" -> \" + (.TargetPort | tostring)'"

    echo ""
    echo "🔍 Load Balancer Status:"
    swarm_exec "sudo docker service ps ${STACK_NAME}_traefik --format 'table {{.Name}}\t{{.Node}}\t{{.CurrentState}}'"
}

# 7. Network Performance Test
test_network_performance() {
    echo "⚡ Network Performance Test"
    echo "=========================="

    local backend_container=$(swarm_exec "sudo docker ps --filter 'label=com.docker.swarm.service.name=${STACK_NAME}_sophia-backend' --format '{{.ID}}' | head -1")

    if [ -n "$backend_container" ]; then
        echo "🏃 Testing network latency between services:"

        # Ping test to measure latency
        echo "Redis latency:"
        swarm_exec "sudo docker exec $backend_container ping -c 5 redis 2>/dev/null | tail -1 && echo '  ✅ Latency test completed' || echo '  ❌ Latency test failed'"

        echo ""
        echo "PostgreSQL latency:"
        swarm_exec "sudo docker exec $backend_container ping -c 5 postgres 2>/dev/null | tail -1 && echo '  ✅ Latency test completed' || echo '  ❌ Latency test failed'"

    else
        echo "❌ Backend container not found - cannot test network performance"
    fi

    echo ""
    echo "🌐 External connectivity test:"
    local api_response_time=$(curl -o /dev/null -s -w "%{time_total}" http://$MASTER_IP:8000/health 2>/dev/null || echo "timeout")
    echo "API response time: ${api_response_time}s"
}

# 8. Common Issues Diagnosis
diagnose_common_issues() {
    echo "🔧 Common Issues Diagnosis"
    echo "========================="

    echo "🔍 Checking for common Docker Swarm network issues:"

    # Check for stale networks
    echo ""
    echo "1. Stale Network Detection:"
    local stale_networks=$(swarm_exec "sudo docker network ls -f dangling=true --format '{{.Name}}'")
    if [ -n "$stale_networks" ]; then
        echo "⚠️ Stale networks detected:"
        echo "$stale_networks"
    else
        echo "✅ No stale networks found"
    fi

    # Check for IP address conflicts
    echo ""
    echo "2. IP Address Conflict Check:"
    swarm_exec "sudo docker network ls --format '{{.Name}}' | xargs -I {} sudo docker network inspect {} --format '{{.Name}}: {{range .IPAM.Config}}{{.Subnet}}{{end}}' | sort"

    # Check for overlay driver issues
    echo ""
    echo "3. Overlay Driver Status:"
    swarm_exec "sudo docker info | grep -A5 'Network:' | grep overlay && echo '✅ Overlay driver loaded' || echo '❌ Overlay driver issues'"

    # Check for encryption issues
    echo ""
    echo "4. Network Encryption Status:"
    local encrypted_networks=$(swarm_exec "sudo docker network ls --format '{{.Name}}' | xargs -I {} sudo docker network inspect {} --format '{{.Name}}: {{.EnableIPv6}} {{.Options.encrypted}}'")
    echo "$encrypted_networks"
}

# 9. Network Repair Suggestions
suggest_network_repairs() {
    echo "🛠️ Network Repair Suggestions"
    echo "============================="

    echo "🔧 Automatic Network Fixes:"
    echo ""

    # Clean up stale networks
    echo "1. Clean up stale networks:"
    echo "   sudo docker network prune -f"

    # Restart networking
    echo ""
    echo "2. Restart Docker networking (if issues persist):"
    echo "   sudo systemctl restart docker"

    # Recreate overlay network
    echo ""
    echo "3. Recreate overlay network (last resort):"
    echo "   sudo docker network rm ${STACK_NAME}_sophia-overlay"
    echo "   sudo docker network create --driver=overlay --attachable ${STACK_NAME}_sophia-overlay"

    # Re-deploy stack
    echo ""
    echo "4. Re-deploy stack with fresh network:"
    echo "   sudo docker stack rm $STACK_NAME"
    echo "   sleep 30"
    echo "   sudo docker stack deploy -c docker-compose.cloud.yml $STACK_NAME"

    echo ""
    echo "⚠️ Run these commands only if network issues are confirmed!"
}

# 10. Generate Network Report
generate_network_report() {
    echo "📊 Network Health Report"
    echo "======================="

    local timestamp=$(date)
    echo "Generated: $timestamp"
    echo ""

    # Count network elements
    local total_networks=$(swarm_exec "sudo docker network ls | wc -l")
    local overlay_networks=$(swarm_exec "sudo docker network ls --filter driver=overlay | wc -l")

    echo "📈 Network Summary:"
    echo "- Total networks: $total_networks"
    echo "- Overlay networks: $overlay_networks"

    # Check service connectivity status
    local backend_container=$(swarm_exec "sudo docker ps --filter 'label=com.docker.swarm.service.name=${STACK_NAME}_sophia-backend' --format '{{.ID}}' | head -1")

    if [ -n "$backend_container" ]; then
        local redis_ping=$(swarm_exec "sudo docker exec $backend_container ping -c 1 redis >/dev/null 2>&1 && echo 'OK' || echo 'FAIL'")
        local postgres_ping=$(swarm_exec "sudo docker exec $backend_container ping -c 1 postgres >/dev/null 2>&1 && echo 'OK' || echo 'FAIL'")

        echo "🌐 Service Connectivity:"
        echo "- Backend → Redis: $redis_ping"
        echo "- Backend → PostgreSQL: $postgres_ping"
    else
        echo "🌐 Service Connectivity: Cannot test (backend not running)"
    fi

    echo ""
    echo "🎯 Recommendations:"
    echo "- Monitor overlay network performance every 15 minutes"
    echo "- Run network cleanup weekly: docker network prune -f"
    echo "- Check firewall rules if connectivity issues persist"
    echo "- Restart Docker service if overlay networks become unstable"
}

# Main execution
main() {
    check_network_discovery
    echo ""
    test_service_connectivity
    echo ""
    check_ports_and_firewall
    echo ""
    inspect_overlay_networks
    echo ""
    test_dns_resolution
    echo ""
    analyze_traffic_flow
    echo ""
    test_network_performance
    echo ""
    diagnose_common_issues
    echo ""
    suggest_network_repairs
    echo ""
    generate_network_report
}

# Execute main function
main
