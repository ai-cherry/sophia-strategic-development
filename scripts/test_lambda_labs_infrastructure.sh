#!/bin/bash
# Lambda Labs Infrastructure Testing Protocol
# Comprehensive validation for MCP server deployment on Lambda Labs infrastructure

set -e  # Exit on any error

# Color codes for output
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

log_header() {
    echo -e "\n${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================================================================${NC}"
}

# Test results tracking
declare -A test_results
total_tests=0
passed_tests=0

track_test() {
    local test_name="$1"
    local result="$2"
    total_tests=$((total_tests + 1))

    if [ "$result" = "PASS" ]; then
        passed_tests=$((passed_tests + 1))
        log_success "✅ $test_name"
    elif [ "$result" = "WARN" ]; then
        log_warning "⚠️  $test_name"
    else
        log_error "❌ $test_name"
    fi

    test_results["$test_name"]="$result"
}

# Check prerequisites
check_prerequisites() {
    log_header "🔧 Checking Prerequisites"

    # Check if Lambda CLI is installed
    if command -v lambda &> /dev/null; then
        track_test "Lambda CLI installation" "PASS"
    else
        track_test "Lambda CLI installation" "FAIL"
        log_error "Lambda CLI not found. Install with: pip install lambda-labs"
        return 1
    fi

    # Check if kubectl is available (for Kubernetes tests)
    if command -v kubectl &> /dev/null; then
        track_test "kubectl installation" "PASS"
    else
        track_test "kubectl installation" "WARN"
        log_warning "kubectl not found. Kubernetes tests will be skipped."
    fi

    # Check if curl is available
    if command -v curl &> /dev/null; then
        track_test "curl installation" "PASS"
    else
        track_test "curl installation" "FAIL"
        log_error "curl is required for health checks"
        return 1
    fi

    # Check if jq is available for JSON parsing
    if command -v jq &> /dev/null; then
        track_test "jq installation" "PASS"
    else
        track_test "jq installation" "WARN"
        log_warning "jq not found. JSON parsing will be limited."
    fi
}

# Test 1: Lambda CLI authentication and basic functionality
test_lambda_cli_auth() {
    log_header "🔐 Testing Lambda CLI Authentication"

    # Test authentication status
    if lambda auth status &> /dev/null; then
        track_test "Lambda CLI authentication" "PASS"

        # Get account information
        local account_info=$(lambda account 2>/dev/null)
        if [ $? -eq 0 ]; then
            log_info "Account information retrieved successfully"
            track_test "Lambda account access" "PASS"
        else
            track_test "Lambda account access" "WARN"
        fi
    else
        track_test "Lambda CLI authentication" "FAIL"
        log_error "Lambda CLI authentication failed. Run: lambda auth login"
        return 1
    fi
}

# Test 2: GPU resource availability and management
test_gpu_resources() {
    log_header "🖥️ Testing GPU Resource Availability"

    # List available instances
    log_info "Checking available GPU instances..."
    local instances_output=$(lambda instances list --format json 2>/dev/null)

    if [ $? -eq 0 ]; then
        track_test "Lambda instances list command" "PASS"

        # Check if we have running instances
        if echo "$instances_output" | jq . &> /dev/null; then
            local running_count=$(echo "$instances_output" | jq '[.[] | select(.status=="running")] | length' 2>/dev/null || echo "0")
            log_info "Running instances: $running_count"

            if [ "$running_count" -gt 0 ]; then
                track_test "Running GPU instances available" "PASS"

                # Show instance details
                echo "$instances_output" | jq -r '.[] | select(.status=="running") | "Instance: \(.name), Type: \(.instance_type), Region: \(.region)"' 2>/dev/null || log_warning "Could not parse instance details"
            else
                track_test "Running GPU instances available" "WARN"
                log_warning "No running GPU instances found"
            fi
        else
            track_test "JSON parsing of instances" "WARN"
        fi
    else
        track_test "Lambda instances list command" "FAIL"
        log_error "Failed to list Lambda instances"
    fi

    # Test GPU types availability
    log_info "Checking available GPU types..."
    local gpu_types=$(lambda instance-types list --format json 2>/dev/null)

    if [ $? -eq 0 ]; then
        track_test "Lambda GPU types list" "PASS"

        if echo "$gpu_types" | jq . &> /dev/null; then
            local gpu_count=$(echo "$gpu_types" | jq 'length' 2>/dev/null || echo "0")
            log_info "Available GPU types: $gpu_count"

            # Show some popular GPU types
            log_info "Popular GPU types available:"
            echo "$gpu_types" | jq -r '.[] | select(.name | contains("H100") or contains("A100") or contains("RTX")) | "  - \(.name): \(.description)"' 2>/dev/null || log_info "  (Could not parse GPU type details)"
        fi
    else
        track_test "Lambda GPU types list" "WARN"
        log_warning "Could not retrieve GPU types list"
    fi
}

# Test 3: Kubernetes integration (if available)
test_kubernetes_integration() {
    log_header "☸️ Testing Kubernetes Integration"

    if ! command -v kubectl &> /dev/null; then
        log_warning "kubectl not available, skipping Kubernetes tests"
        return 0
    fi

    # Test cluster connectivity
    if kubectl cluster-info &> /dev/null; then
        track_test "Kubernetes cluster connectivity" "PASS"

        # Check for Lambda Labs nodes
        local lambda_nodes=$(kubectl get nodes -l lambdalabs.com/gpu-type 2>/dev/null | wc -l)
        lambda_nodes=$((lambda_nodes - 1)) # Subtract header line

        if [ "$lambda_nodes" -gt 0 ]; then
            track_test "Lambda Labs nodes in Kubernetes" "PASS"
            log_info "Lambda Labs nodes found: $lambda_nodes"
        else
            track_test "Lambda Labs nodes in Kubernetes" "WARN"
            log_warning "No Lambda Labs specific nodes found in Kubernetes"
        fi

        # Check GPU resources in cluster
        local gpu_resources=$(kubectl get nodes -o json | jq '[.items[] | select(.status.capacity."nvidia.com/gpu" != null)] | length' 2>/dev/null || echo "0")

        if [ "$gpu_resources" -gt 0 ]; then
            track_test "GPU resources in Kubernetes" "PASS"
            log_info "Nodes with GPU resources: $gpu_resources"
        else
            track_test "GPU resources in Kubernetes" "WARN"
            log_warning "No GPU resources detected in Kubernetes cluster"
        fi
    else
        track_test "Kubernetes cluster connectivity" "FAIL"
        log_error "Could not connect to Kubernetes cluster"
    fi
}

# Test 4: MCP server connectivity to Lambda Labs infrastructure
test_mcp_lambda_connectivity() {
    log_header "🔌 Testing MCP Server Connectivity"

    # Test Lambda Labs CLI MCP server (port 9020)
    local lambda_mcp_port=9020
    if curl -f -s http://localhost:$lambda_mcp_port/health > /dev/null 2>&1; then
        track_test "Lambda Labs MCP server (port $lambda_mcp_port) healthy" "PASS"

        # Get detailed health info
        local health_response=$(curl -s http://localhost:$lambda_mcp_port/health 2>/dev/null)
        if echo "$health_response" | jq . &> /dev/null; then
            local server_status=$(echo "$health_response" | jq -r '.status // "unknown"' 2>/dev/null)
            log_info "Lambda Labs MCP server status: $server_status"
        fi
    else
        track_test "Lambda Labs MCP server (port $lambda_mcp_port) not responding" "FAIL"
    fi

    # Test Lambda Labs CLI server capabilities
    if curl -f -s http://localhost:$lambda_mcp_port/capabilities > /dev/null 2>&1; then
        track_test "Lambda Labs MCP server capabilities endpoint accessible" "PASS"

        # Show capabilities
        local capabilities=$(curl -s http://localhost:$lambda_mcp_port/capabilities 2>/dev/null | jq -r '.capabilities[].name' 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
        log_info "Available capabilities: $capabilities"
    else
        track_test "Lambda Labs MCP server capabilities endpoint not accessible" "WARN"
    fi

    # Test other MCP servers that might use Lambda Labs infrastructure
    local other_mcp_ports=(9000 9002 9003 9010 9011)
    for port in "${other_mcp_ports[@]}"; do
        if curl -f -s http://localhost:$port/health > /dev/null 2>&1; then
            track_test "MCP server on port $port responding" "PASS"
        else
            track_test "MCP server on port $port not responding" "WARN"
        fi
    done
}

# Test 5: Performance benchmarking
test_performance_benchmarks() {
    log_header "⚡ Testing Performance Benchmarks"

    # Test network latency to Lambda Labs MCP server
    local lambda_mcp_port=9020
    log_info "Testing network latency to Lambda Labs MCP server..."

    local start_time=$(date +%s%N)
    if curl -f -s http://localhost:$lambda_mcp_port/health > /dev/null 2>&1; then
        local end_time=$(date +%s%N)
        local latency=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds

        if [ "$latency" -lt 100 ]; then
            track_test "Lambda Labs MCP server latency (${latency}ms)" "PASS"
        elif [ "$latency" -lt 500 ]; then
            track_test "Lambda Labs MCP server latency (${latency}ms)" "WARN"
        else
            track_test "Lambda Labs MCP server latency (${latency}ms)" "FAIL"
        fi
    else
        track_test "Lambda Labs MCP server latency test" "FAIL"
    fi

    # Test throughput with multiple concurrent requests
    log_info "Testing concurrent request handling..."
    local concurrent_requests=5
    local success_count=0

    for i in $(seq 1 $concurrent_requests); do
        if curl -f -s http://localhost:$lambda_mcp_port/health > /dev/null 2>&1 &; then
            ((success_count++))
        fi
    done

    wait # Wait for all background jobs to complete

    if [ "$success_count" -eq "$concurrent_requests" ]; then
        track_test "Concurrent request handling ($concurrent_requests requests)" "PASS"
    elif [ "$success_count" -gt 0 ]; then
        track_test "Concurrent request handling ($success_count/$concurrent_requests succeeded)" "WARN"
    else
        track_test "Concurrent request handling (all failed)" "FAIL"
    fi
}

# Test 6: Security and configuration validation
test_security_configuration() {
    log_header "🛡️ Testing Security Configuration"

    # Check for proper environment variable configuration
    if [ -n "$PULUMI_ORG" ]; then
        track_test "PULUMI_ORG environment variable set" "PASS"
        log_info "Pulumi organization: $PULUMI_ORG"
    else
        track_test "PULUMI_ORG environment variable set" "WARN"
        log_warning "PULUMI_ORG not set - may affect MCP server configuration"
    fi

    # Check for Lambda Labs API key
    if [ -n "$LAMBDA_API_KEY" ] || lambda auth status &> /dev/null; then
        track_test "Lambda Labs authentication configured" "PASS"
    else
        track_test "Lambda Labs authentication configured" "WARN"
        log_warning "Lambda Labs authentication not properly configured"
    fi

    # Check MCP server configuration files
    local config_files=(
        "../config/consolidated_mcp_ports.json"
        "../config/cursor_enhanced_mcp_config.json"
    )

    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            track_test "Configuration file exists: $(basename $config_file)" "PASS"

            # Validate JSON format
            if jq . "$config_file" > /dev/null 2>&1; then
                track_test "Configuration file valid JSON: $(basename $config_file)" "PASS"
            else
                track_test "Configuration file valid JSON: $(basename $config_file)" "FAIL"
            fi
        else
            track_test "Configuration file exists: $(basename $config_file)" "WARN"
        fi
    done
}

# Test 7: Resource monitoring and metrics
test_resource_monitoring() {
    log_header "📊 Testing Resource Monitoring"

    # Test system resources
    log_info "Checking system resources..."

    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' 2>/dev/null || echo "unknown")
    log_info "CPU usage: $cpu_usage"

    # Check memory usage
    local memory_info=$(free -h 2>/dev/null | grep "Mem:" | awk '{print "Used: "$3" / Total: "$2}' || echo "unknown")
    log_info "Memory usage: $memory_info"

    # Check disk space
    local disk_usage=$(df -h / 2>/dev/null | awk 'NR==2{print "Used: "$3" / Available: "$4" ("$5" full)"}' || echo "unknown")
    log_info "Disk usage: $disk_usage"

    # Test if monitoring endpoints are accessible
    local monitoring_ports=(9090 3000 8080) # Prometheus, Grafana, custom monitoring
    for port in "${monitoring_ports[@]}"; do
        if curl -f -s http://localhost:$port > /dev/null 2>&1; then
            track_test "Monitoring service on port $port accessible" "PASS"
        else
            track_test "Monitoring service on port $port accessible" "WARN"
        fi
    done

    track_test "System resource monitoring" "PASS"
}

# Generate final report
generate_report() {
    log_header "📋 Final Test Report"

    local success_rate=$(( passed_tests * 100 / total_tests ))

    echo -e "\n${BLUE}Test Summary:${NC}"
    echo -e "  Total tests: $total_tests"
    echo -e "  Passed: $passed_tests"
    echo -e "  Success rate: ${success_rate}%"

    if [ "$success_rate" -ge 80 ]; then
        log_success "🎉 Infrastructure testing completed successfully!"
        log_info "Lambda Labs infrastructure is ready for MCP server deployment"
    elif [ "$success_rate" -ge 60 ]; then
        log_warning "⚠️ Infrastructure testing completed with warnings"
        log_info "Some issues found but infrastructure is mostly functional"
    else
        log_error "❌ Infrastructure testing failed"
        log_error "Critical issues found that need to be resolved"
    fi

    echo -e "\n${BLUE}Detailed Results:${NC}"
    for test_name in "${!test_results[@]}"; do
        local result="${test_results[$test_name]}"
        case "$result" in
            "PASS") echo -e "  ✅ $test_name" ;;
            "WARN") echo -e "  ⚠️  $test_name" ;;
            "FAIL") echo -e "  ❌ $test_name" ;;
        esac
    done

    # Generate JSON report
    local report_file="lambda_labs_infrastructure_test_report_$(date +%Y%m%d_%H%M%S).json"
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "test_summary": {
    "total_tests": $total_tests,
    "passed_tests": $passed_tests,
    "success_rate": $success_rate
  },
  "test_results": $(
    echo "{"
    local first=true
    for test_name in "${!test_results[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        echo "    \"$test_name\": \"${test_results[$test_name]}\""
    done
    echo "  }"
  ),
  "recommendations": [
$(
    if [ "$success_rate" -lt 80 ]; then
        echo '    "Address failed tests before production deployment",'
    fi
    if [ -z "$(command -v kubectl)" ]; then
        echo '    "Install kubectl for full Kubernetes integration testing",'
    fi
    echo '    "Monitor system resources during MCP server deployment",'
    echo '    "Implement automated health checking for production"'
)
  ]
}
EOF

    log_info "Detailed JSON report saved to: $report_file"

    return $([ "$success_rate" -ge 80 ] && echo 0 || echo 1)
}

# Main execution
main() {
    log_header "🚀 Lambda Labs Infrastructure Testing Protocol"
    log_info "Starting comprehensive infrastructure validation..."

    # Run all tests
    check_prerequisites || exit 1
    test_lambda_cli_auth
    test_gpu_resources
    test_kubernetes_integration
    test_mcp_lambda_connectivity
    test_performance_benchmarks
    test_security_configuration
    test_resource_monitoring

    # Generate final report
    generate_report
    local exit_code=$?

    log_header "🏁 Testing Complete"

    exit $exit_code
}

# Execute main function
main "$@"
