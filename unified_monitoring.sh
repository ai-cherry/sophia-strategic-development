#!/bin/bash
# Docker Swarm Production Monitoring Script
# Implements comprehensive health checks and troubleshooting from best practices

set -euo pipefail

MASTER_IP="192.222.58.232"
SSH_KEY="$HOME/.ssh/sophia2025"
STACK_NAME="sophia-ai"

echo "🔍 Sophia AI Docker Swarm Production Monitor"
echo "==========================================="
echo "Swarm Manager: $MASTER_IP"
echo "Stack: $STACK_NAME"
echo ""

# Function to execute commands on Swarm manager
swarm_exec() {
    ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "$1"
}

# 1. Check Swarm cluster health
check_swarm_health() {
    echo "🏥 Checking Swarm Cluster Health..."
    echo "================================="

    echo "📊 Node Status:"
    swarm_exec "sudo docker node ls"

    echo ""
    echo "🔧 Manager Quorum Status:"
    local managers_ready=$(swarm_exec "sudo docker node ls --filter role=manager --format '{{.Status}}' | grep -c Ready")
    local total_managers=$(swarm_exec "sudo docker node ls --filter role=manager --format '{{.Hostname}}' | wc -l")

    echo "Ready Managers: $managers_ready/$total_managers"
    if [ "$managers_ready" -lt 2 ]; then
        echo "⚠️  WARNING: Manager quorum at risk (need at least 2 ready managers)"
    else
        echo "✅ Manager quorum healthy"
    fi

    echo ""
}

# 2. Check service health
check_service_health() {
    echo "🚀 Checking Service Health..."
    echo "============================="

    echo "📋 Service Overview:"
    swarm_exec "sudo docker service ls"

    echo ""
    echo "🔍 Failed Services:"
    local failed_services=$(swarm_exec "sudo docker service ls --format 'table {{.Name}}\t{{.Replicas}}' | grep '0/'")

    if [ -n "$failed_services" ]; then
        echo "❌ Failed services detected:"
        echo "$failed_services"

        echo ""
        echo "🔧 Detailed failure analysis:"
        swarm_exec "sudo docker service ls --format '{{.Name}}' | xargs -I {} sudo docker service ps {} --no-trunc | grep -E '(Failed|Rejected|Shutdown)'"
    else
        echo "✅ All services running normally"
    fi

    echo ""
}

# 3. Check stack health
check_stack_health() {
    echo "📦 Checking Stack Health..."
    echo "=========================="

    echo "🏗️ Stack Services:"
    swarm_exec "sudo docker stack ps $STACK_NAME --no-trunc"

    echo ""
    echo "📊 Resource Usage:"
    swarm_exec "sudo docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'"

    echo ""
}

# 4. Check network connectivity
check_network_health() {
    echo "🌐 Checking Network Health..."
    echo "============================="

    echo "🔗 Overlay Networks:"
    swarm_exec "sudo docker network ls --filter driver=overlay"

    echo ""
    echo "🚦 Network Connectivity Test:"
    # Test connectivity between services
    local test_result=$(swarm_exec "sudo docker exec \$(sudo docker ps --filter 'label=com.docker.swarm.service.name=${STACK_NAME}_sophia-backend' --format '{{.ID}}' | head -1) ping -c 1 redis 2>/dev/null && echo 'SUCCESS' || echo 'FAILED'")

    if [ "$test_result" = "SUCCESS" ]; then
        echo "✅ Inter-service connectivity working"
    else
        echo "❌ Inter-service connectivity issues detected"
        echo "🔧 Network troubleshooting:"
        swarm_exec "sudo docker network inspect ${STACK_NAME}_sophia-overlay --format '{{json .IPAM}}'"
    fi

    echo ""
}

# 5. Check container logs for errors
check_error_logs() {
    echo "📝 Checking Recent Error Logs..."
    echo "==============================="

    echo "🚨 Recent errors from backend service:"
    swarm_exec "sudo docker service logs --tail 20 ${STACK_NAME}_sophia-backend 2>/dev/null | grep -i error || echo 'No recent errors found'"

    echo ""
    echo "🚨 Recent errors from database:"
    swarm_exec "sudo docker service logs --tail 20 ${STACK_NAME}_postgres 2>/dev/null | grep -i error || echo 'No recent errors found'"

    echo ""
}

# 6. Check resource constraints
check_resource_constraints() {
    echo "💾 Checking Resource Constraints..."
    echo "=================================="

    echo "🖥️ System Resources:"
    swarm_exec "free -h && echo '' && df -h | head -5"

    echo ""
    echo "⚠️ Services over 80% memory usage:"
    swarm_exec "sudo docker stats --no-stream --format 'table {{.Container}}\t{{.MemPerc}}' | awk 'NR>1 && \$2+0 > 80'"

    echo ""
}

# 7. Check secret availability
check_secrets() {
    echo "🔐 Checking Docker Secrets..."
    echo "============================="

    echo "🗝️ Available secrets:"
    swarm_exec "sudo docker secret ls"

    echo ""
    echo "🔍 Services with secret mount issues:"
    swarm_exec "sudo docker service ps ${STACK_NAME}_sophia-backend --format 'table {{.Name}}\t{{.CurrentState}}\t{{.Error}}' | grep -v 'Running\\|Complete' || echo 'No secret mount issues detected'"

    echo ""
}

# 8. Performance health check
check_performance() {
    echo "⚡ Performance Health Check..."
    echo "============================"

    echo "🌐 Testing API responsiveness:"
    local api_response=$(curl -s -o /dev/null -w "%{http_code} %{time_total}s" http://$MASTER_IP:8000/health 2>/dev/null || echo "000 timeout")

    if [[ "$api_response" == "200"* ]]; then
        echo "✅ API health endpoint: $api_response"
    else
        echo "❌ API health endpoint failed: $api_response"
    fi

    echo ""
    echo "📊 Load balancer status:"
    swarm_exec "sudo docker service ps ${STACK_NAME}_traefik --format 'table {{.Name}}\t{{.CurrentState}}'"

    echo ""
}

# 9. Auto-healing check
check_auto_healing() {
    echo "🔄 Auto-Healing Status..."
    echo "========================"

    echo "🔧 Recent service restarts:"
    swarm_exec "sudo docker service ps ${STACK_NAME}_sophia-backend --format 'table {{.Name}}\t{{.CurrentState}}\t{{.Error}}' | head -10"

    echo ""
    echo "⏰ Service update history:"
    swarm_exec "sudo docker service inspect ${STACK_NAME}_sophia-backend --format '{{json .UpdateStatus}}' | jq -r '.State // \"No recent updates\"'"

    echo ""
}

# 10. Generate health summary
generate_health_summary() {
    echo "📊 Health Summary Report"
    echo "======================="

    local timestamp=$(date)
    echo "Generated: $timestamp"
    echo ""

    # Count healthy vs unhealthy services
    local total_services=$(swarm_exec "sudo docker service ls --format '{{.Name}}' | wc -l")
    local healthy_services=$(swarm_exec "sudo docker service ls --format '{{.Replicas}}' | grep -v '0/' | wc -l")

    echo "📈 Service Health: $healthy_services/$total_services services healthy"

    # Check overall system health
    local memory_usage=$(swarm_exec "free | awk 'NR==2{printf \"%.0f\", \$3/\$2 * 100}'")
    echo "💾 Memory Usage: ${memory_usage}%"

    local disk_usage=$(swarm_exec "df / | awk 'NR==2{print \$5}' | sed 's/%//'")
    echo "💿 Disk Usage: ${disk_usage}%"

    # Generate recommendations
    echo ""
    echo "🎯 Recommendations:"

    if [ "$healthy_services" -lt "$total_services" ]; then
        echo "- ⚠️ Some services are unhealthy - check service logs"
    fi

    if [ "$memory_usage" -gt 80 ]; then
        echo "- ⚠️ High memory usage detected - consider scaling down or adding nodes"
    fi

    if [ "$disk_usage" -gt 80 ]; then
        echo "- ⚠️ High disk usage - clean up old containers and images"
    fi

    echo "- ✅ Run this monitor every 15 minutes for proactive monitoring"
    echo ""
}

# Main execution
main() {
    check_swarm_health
    check_service_health
    check_stack_health
    check_network_health
    check_error_logs
    check_resource_constraints
    check_secrets
    check_performance
    check_auto_healing
    generate_health_summary
}

# Execute main function
main
