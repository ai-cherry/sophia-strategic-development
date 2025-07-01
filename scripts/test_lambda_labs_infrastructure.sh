#!/bin/bash
# Lambda Labs Infrastructure Testing Protocol
# Comprehensive validation of Lambda Labs GPU infrastructure for Sophia AI MCP servers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "$(printf '=%.0s' {1..70})"
}

# Global test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0

# Test result tracking
track_test() {
    local test_name="$1"
    local status="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    case $status in
        "PASS")
            PASSED_TESTS=$((PASSED_TESTS + 1))
            log_success "$test_name"
            ;;
        "FAIL")
            FAILED_TESTS=$((FAILED_TESTS + 1))
            log_error "$test_name"
            ;;
        "WARN")
            WARNINGS=$((WARNINGS + 1))
            log_warning "$test_name"
            ;;
    esac
}

# Test 1: Lambda CLI availability and authentication
test_lambda_cli_auth() {
    log_header "🔐 Testing Lambda CLI Authentication"
    
    # Check if lambda CLI is installed
    if command -v lambda &> /dev/null; then
        track_test "Lambda CLI installed" "PASS"
    else
        track_test "Lambda CLI not found - install from https://lambdalabs.com/cli" "FAIL"
        return 1
    fi
    
    # Test authentication
    if lambda auth status &> /dev/null; then
        track_test "Lambda CLI authentication successful" "PASS"
        
        # Get account info
        local account_info=$(lambda auth status 2>/dev/null | head -5)
        log_info "Account info: $account_info"
    else
        track_test "Lambda CLI authentication failed - run 'lambda auth login'" "FAIL"
        return 1
    fi
}

# Test 2: GPU resource availability
test_gpu_resources() {
    log_header "🖥️  Testing GPU Resource Availability"
    
    # List all instances
    local instances_output
    if instances_output=$(lambda list --json 2>/dev/null); then
        track_test "Lambda Labs API connectivity" "PASS"
        
        # Parse instance data
        local running_instances=$(echo "$instances_output" | jq -r '.[] | select(.status=="running") | .name' 2>/dev/null | wc -l)
        local total_instances=$(echo "$instances_output" | jq -r '.[].name' 2>/dev/null | wc -l)
        
        log_info "Total instances: $total_instances"
        log_info "Running instances: $running_instances"
        
        if [ "$running_instances" -gt 0 ]; then
            track_test "GPU instances available and running" "PASS"
            
            # Show running instances
            echo "$instances_output" | jq -r '.[] | select(.status=="running") | "Instance: \(.name) | Type: \(.instance_type.name) | Region: \(.region.name)"' 2>/dev/null
        else
            track_test "No running GPU instances found" "WARN"
        fi
    else
        track_test "Failed to connect to Lambda Labs API" "FAIL"
        return 1
    fi
}

# Test 3: Kubernetes integration with Lambda Labs
test_k8s_lambda_integration() {
    log_header "☸️  Testing Kubernetes Integration"
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        track_test "kubectl not found - Kubernetes testing skipped" "WARN"
        return 0
    fi
    
    # Check Kubernetes cluster connectivity
    if kubectl cluster-info &> /dev/null; then
        track_test "Kubernetes cluster connectivity" "PASS"
    else
        track_test "Kubernetes cluster not accessible" "FAIL"
        return 1
    fi
    
    # Check for Lambda Labs nodes
    local lambda_nodes=$(kubectl get nodes -l lambdalabs.com/gpu-type 2>/dev/null | wc -l)
    if [ "$lambda_nodes" -gt 1 ]; then  # > 1 because of header line
        track_test "Lambda Labs nodes found in Kubernetes cluster" "PASS"
        
        # Show Lambda Labs nodes
        kubectl get nodes -l lambdalabs.com/gpu-type -o custom-columns=NAME:.metadata.name,GPU-TYPE:.metadata.labels.'lambdalabs\.com/gpu-type',STATUS:.status.conditions[-1].type 2>/dev/null
    else
        track_test "No Lambda Labs nodes found in Kubernetes cluster" "WARN"
    fi
    
    # Check for GPU resources
    local gpu_capacity=$(kubectl describe nodes 2>/dev/null | grep -c "nvidia.com/gpu" || echo "0")
    if [ "$gpu_capacity" -gt 0 ]; then
        track_test "GPU resources available in cluster (nvidia.com/gpu: $gpu_capacity)" "PASS"
    else
        track_test "No GPU resources found in cluster" "WARN"
    fi
    
    # Check for Lambda Labs storage classes
    local lambda_storage=$(kubectl get storageclass 2>/dev/null | grep -c "lambda-labs" || echo "0")
    if [ "$lambda_storage" -gt 0 ]; then
        track_test "Lambda Labs storage classes configured" "PASS"
    else
        track_test "Lambda Labs storage classes not found" "WARN"
    fi
}

# Test 4: MCP server connectivity
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
    log_header "⚡ Running Performance Benchmarks"
    
    # Network latency to Lambda Labs
    if command -v ping &> /dev/null; then
        local ping_result=$(ping -c 3 cloud.lambdalabs.com 2>/dev/null | tail -1 | awk -F'/' '{print $5}' 2>/dev/null || echo "unknown")
        if [ "$ping_result" != "unknown" ] && [ "$ping_result" != "" ]; then
            track_test "Network latency to Lambda Labs: ${ping_result}ms" "PASS"
            
            # Check if latency is acceptable
            if (( $(echo "$ping_result < 100" | bc -l 2>/dev/null || echo "0") )); then
                log_info "Excellent network latency"
            elif (( $(echo "$ping_result < 200" | bc -l 2>/dev/null || echo "0") )); then
                log_info "Good network latency"
            else
                log_warning "High network latency - may affect performance"
            fi
        else
            track_test "Could not measure network latency to Lambda Labs" "WARN"
        fi
    else
        track_test "Ping command not available - network test skipped" "WARN"
    fi
    
    # MCP server response time benchmark
    if curl -s http://localhost:9020/health > /dev/null 2>&1; then
        local response_time=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:9020/health 2>/dev/null)
        if [ "$response_time" != "" ]; then
            local response_ms=$(echo "$response_time * 1000" | bc -l 2>/dev/null | cut -d. -f1)
            track_test "Lambda Labs MCP server response time: ${response_ms}ms" "PASS"
            
            # Check response time
            if [ "$response_ms" -lt 100 ]; then
                log_info "Excellent MCP server response time"
            elif [ "$response_ms" -lt 500 ]; then
                log_info "Good MCP server response time"
            else
                log_warning "Slow MCP server response time"
            fi
        else
            track_test "Could not measure MCP server response time" "WARN"
        fi
    fi
}

# Test 6: Configuration validation
test_configuration_validation() {
    log_header "⚙️  Testing Configuration Validation"
    
    # Check environment variables
    local required_vars=("ENVIRONMENT" "PULUMI_ORG")
    for var in "${required_vars[@]}"; do
        if [ -n "${!var}" ]; then
            track_test "Environment variable $var is set" "PASS"
            log_info "$var=${!var}"
        else
            track_test "Environment variable $var is not set" "WARN"
        fi
    done
    
    # Check Pulumi ESC configuration
    if command -v pulumi &> /dev/null; then
        if pulumi org get-default &> /dev/null; then
            track_test "Pulumi CLI configured" "PASS"
            local org=$(pulumi org get-default 2>/dev/null)
            log_info "Pulumi organization: $org"
        else
            track_test "Pulumi CLI not configured" "WARN"
        fi
    else
        track_test "Pulumi CLI not installed" "WARN"
    fi
    
    # Check MCP configuration files
    local config_files=(
        "config/consolidated_mcp_ports.json"
        "config/cursor_enhanced_mcp_config.json"
    )
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            track_test "Configuration file $config_file exists" "PASS"
            
            # Validate JSON syntax
            if jq . "$config_file" > /dev/null 2>&1; then
                track_test "Configuration file $config_file has valid JSON" "PASS"
            else
                track_test "Configuration file $config_file has invalid JSON" "FAIL"
            fi
        else
            track_test "Configuration file $config_file not found" "FAIL"
        fi
    done
}

# Test 7: Security validation
test_security_validation() {
    log_header "🛡️  Testing Security Configuration"
    
    # Check for hardcoded secrets (basic scan)
    local secret_patterns=("api_key" "password" "token" "secret")
    local found_secrets=0
    
    for pattern in "${secret_patterns[@]}"; do
        local matches=$(find . -name "*.py" -o -name "*.js" -o -name "*.yaml" -o -name "*.json" 2>/dev/null | \
                       xargs grep -l -i "$pattern" 2>/dev/null | \
                       grep -v ".git" | \
                       grep -v "node_modules" | \
                       grep -v "test" | \
                       wc -l)
        if [ "$matches" -gt 0 ]; then
            found_secrets=$((found_secrets + matches))
        fi
    done
    
    if [ "$found_secrets" -eq 0 ]; then
        track_test "No obvious hardcoded secrets found in source code" "PASS"
    else
        track_test "Potential hardcoded secrets found ($found_secrets files) - manual review needed" "WARN"
    fi
    
    # Check file permissions
    local sensitive_files=(
        ".env"
        ".env.local"
        "config/secrets.json"
    )
    
    for file in "${sensitive_files[@]}"; do
        if [ -f "$file" ]; then
            local perms=$(stat -c "%a" "$file" 2>/dev/null || stat -f "%A" "$file" 2>/dev/null)
            if [ "$perms" = "600" ] || [ "$perms" = "400" ]; then
                track_test "File $file has secure permissions ($perms)" "PASS"
            else
                track_test "File $file has insecure permissions ($perms) - should be 600" "WARN"
            fi
        fi
    done
}

# Generate final report
generate_report() {
    log_header "📊 Lambda Labs Infrastructure Test Report"
    
    local success_rate=0
    if [ "$TOTAL_TESTS" -gt 0 ]; then
        success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    fi
    
    echo -e "\n${BLUE}Summary:${NC}"
    echo "  Total Tests: $TOTAL_TESTS"
    echo "  Passed: $PASSED_TESTS"
    echo "  Failed: $FAILED_TESTS"
    echo "  Warnings: $WARNINGS"
    echo "  Success Rate: $success_rate%"
    
    if [ "$success_rate" -ge 90 ]; then
        log_success "Infrastructure is in excellent condition!"
    elif [ "$success_rate" -ge 75 ]; then
        log_success "Infrastructure is in good condition with minor issues"
    elif [ "$success_rate" -ge 50 ]; then
        log_warning "Infrastructure has moderate issues that should be addressed"
    else
        log_error "Infrastructure has significant issues requiring immediate attention"
    fi
    
    # Save detailed report
    local report_file="lambda_labs_infrastructure_report_$(date +%Y%m%d_%H%M%S).json"
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "summary": {
    "total_tests": $TOTAL_TESTS,
    "passed_tests": $PASSED_TESTS,
    "failed_tests": $FAILED_TESTS,
    "warnings": $WARNINGS,
    "success_rate": $success_rate
  },
  "environment": {
    "environment": "${ENVIRONMENT:-unknown}",
    "pulumi_org": "${PULUMI_ORG:-unknown}",
    "user": "$(whoami)",
    "hostname": "$(hostname)",
    "os": "$(uname -s)",
    "arch": "$(uname -m)"
  },
  "recommendations": [
    $([ "$FAILED_TESTS" -gt 0 ] && echo '"Address failed tests immediately",' || echo "")
    $([ "$WARNINGS" -gt 3 ] && echo '"Review and resolve warning conditions",' || echo "")
    $([ "$success_rate" -lt 90 ] && echo '"Consider infrastructure optimization",' || echo "")
    "Regular monitoring and maintenance"
  ]
}
EOF
    
    log_info "Detailed report saved to: $report_file"
    
    # Exit with appropriate code
    if [ "$FAILED_TESTS" -gt 0 ]; then
        exit 1
    elif [ "$WARNINGS" -gt 5 ]; then
        exit 2
    else
        exit 0
    fi
}

# Main execution
main() {
    log_header "🧪 Lambda Labs Infrastructure Testing Protocol"
    log_info "Starting comprehensive Lambda Labs infrastructure validation..."
    
    # Run all tests
    test_lambda_cli_auth
    test_gpu_resources
    test_k8s_lambda_integration
    test_mcp_lambda_connectivity
    test_performance_benchmarks
    test_configuration_validation
    test_security_validation
    
    # Generate final report
    generate_report
}

# Handle script arguments
case "${1:-}" in
    "--help"|"-h")
        echo "Lambda Labs Infrastructure Testing Protocol"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message"
        echo "  --quiet, -q   Suppress verbose output"
        echo "  --auth-only   Test only authentication"
        echo "  --mcp-only    Test only MCP servers"
        echo ""
        echo "Environment Variables:"
        echo "  ENVIRONMENT   Current environment (prod/staging/dev)"
        echo "  PULUMI_ORG    Pulumi organization for ESC access"
        echo ""
        exit 0
        ;;
    "--quiet"|"-q")
        # Redirect output to reduce verbosity
        exec > >(grep -E "(✅|❌|⚠️|📊)" >&1)
        ;;
    "--auth-only")
        test_lambda_cli_auth
        exit $?
        ;;
    "--mcp-only")
        test_mcp_lambda_connectivity
        exit $?
        ;;
esac

# Run main function
main 