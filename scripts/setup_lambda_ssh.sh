#!/bin/bash
# Setup SSH keys for Lambda Labs instances

echo "🔑 Setting up SSH keys for Lambda Labs..."

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "🔐 Generating SSH key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

# Add Lambda Labs instances to known_hosts
echo "📝 Adding Lambda instances to known_hosts..."

LAMBDA_IPS=(
    "192.222.58.232"  # sophia-ai-core
    "104.171.202.103" # sophia-production-instance
    "104.171.202.117" # sophia-mcp-orchestrator
    "104.171.202.134" # sophia-data-pipeline
    "155.248.194.183" # sophia-development
)

for ip in "${LAMBDA_IPS[@]}"; do
    echo "Adding $ip to known_hosts..."
    ssh-keyscan -H $ip >> ~/.ssh/known_hosts 2>/dev/null
done

echo "✅ SSH setup complete!"
echo "🔑 Your public key is:"
cat ~/.ssh/id_rsa.pub
echo ""
echo "📋 Make sure this key is added to your Lambda Labs instances as 'sophia2025'" 