#!/bin/bash

# Find which Lambda Labs servers are accessible

SSH_KEY="$HOME/.ssh/sophia_final_key"

# List of servers
declare -A SERVERS=(
    ["sophia-production-instance"]="104.171.202.103"
    ["sophia-ai-core"]="192.222.58.232"
    ["sophia-mcp-orchestrator"]="104.171.202.117"
    ["sophia-data-pipeline"]="104.171.202.134"
    ["sophia-development"]="155.248.194.183"
)

echo "🔍 Testing Lambda Labs servers..."
echo ""

WORKING_SERVERS=()

for name in "${!SERVERS[@]}"; do
    ip="${SERVERS[$name]}"
    echo -n "Testing $name ($ip)... "
    
    if timeout 5 ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o BatchMode=yes ubuntu@$ip "echo 'OK'" 2>/dev/null | grep -q "OK"; then
        echo "✅ WORKING"
        WORKING_SERVERS+=("$name:$ip")
    else
        echo "❌ Not accessible"
    fi
done

echo ""
echo "Summary:"
echo "--------"

if [ ${#WORKING_SERVERS[@]} -eq 0 ]; then
    echo "❌ No servers are currently accessible via SSH"
    echo ""
    echo "Possible issues:"
    echo "1. Servers might be stopped - check Lambda Labs dashboard"
    echo "2. Network connectivity issues"
    echo "3. SSH key might not match"
    echo ""
    echo "Try checking server status via API:"
    echo "python3 scripts/lambda_labs_manager.py list"
else
    echo "✅ Working servers:"
    for server in "${WORKING_SERVERS[@]}"; do
        echo "   - $server"
    done
    echo ""
    echo "You can deploy to any of these servers."
fi 