#!/bin/bash

# Check deployment status on Sophia AI servers

SERVER_IP="${1:-192.222.58.232}"  # Default to GH200
SSH_KEY="$HOME/.ssh/sophia_correct_key"

echo "🔍 Checking deployment status on $SERVER_IP..."
echo ""

# Function to run SSH commands
ssh_cmd() {
    ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 "ubuntu@${SERVER_IP}" "$@" 2>&1
}

# Check connection
echo "1. Testing connection..."
if ssh_cmd "echo 'Connected'" | grep -q "Connected"; then
    echo "✅ Connection successful"
else
    echo "❌ Cannot connect to server"
    exit 1
fi

# Check system info
echo ""
echo "2. System information:"
ssh_cmd "hostname && uname -m && grep MemTotal /proc/meminfo"

# Check Docker status
echo ""
echo "3. Docker status:"
ssh_cmd "docker --version && docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | head -15"

# Check disk space
echo ""
echo "4. Disk space:"
ssh_cmd "df -h / | tail -1"

# Check Sophia directories
echo ""
echo "5. Sophia directories:"
ssh_cmd "ls -la ~/ | grep sophia"

# Check for running services
echo ""
echo "6. Service health:"
ssh_cmd "curl -s http://localhost:8000/health 2>/dev/null || echo 'Backend not running on port 8000'"
ssh_cmd "curl -s http://localhost:3000 2>/dev/null | head -5 || echo 'Frontend not running on port 3000'"

echo ""
echo "✅ Status check complete" 