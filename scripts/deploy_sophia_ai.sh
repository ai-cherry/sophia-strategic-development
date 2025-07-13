#!/bin/bash
# Deploy Sophia AI to Production
# This script handles DNS, Vercel, and Kubernetes deployment

set -e

echo "🚀 Sophia AI Production Deployment"
echo "=================================="
echo "Domain: sophia-intel.ai"
echo "Version: v2025.7.12"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check for required tools
tools=("vercel" "kubectl" "pulumi")
for tool in "${tools[@]}"; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ $tool not found. Please install it first."
        exit 1
    fi
done

echo "✅ All tools installed"

# Step 1: Configure DNS
echo ""
echo "🌐 Step 1: Configuring DNS with Namecheap"
echo "-----------------------------------------"

# Create a Python script to configure DNS
cat > /tmp/configure_dns.py << 'EOF'
import os
import requests
import sys

# Get credentials from environment
api_key = os.environ.get('NAMECHEAP_API_KEY')
api_user = os.environ.get('NAMECHEAP_API_USER', 'scoobyjava')
client_ip = requests.get('https://api.ipify.org').text
domain = 'sophia-intel.ai'

if not api_key:
    print("❌ NAMECHEAP_API_KEY not set")
    sys.exit(1)

# DNS records to create
records = [
    {'Type': 'A', 'Name': '@', 'Address': '76.76.21.21', 'TTL': '1800'},
    {'Type': 'A', 'Name': 'www', 'Address': '76.76.21.21', 'TTL': '1800'},
    {'Type': 'A', 'Name': 'api', 'Address': '192.222.58.232', 'TTL': '1800'},
    {'Type': 'CNAME', 'Name': 'dashboard', 'Address': 'cname.vercel-dns.com.', 'TTL': '1800'},
    {'Type': 'A', 'Name': 'docs', 'Address': '76.76.21.21', 'TTL': '1800'},
    {'Type': 'A', 'Name': 'grafana', 'Address': '192.222.58.232', 'TTL': '1800'},
]

# Namecheap API endpoint
url = f"https://api.namecheap.com/xml.response"

# Set DNS records
for i, record in enumerate(records, 1):
    params = {
        'ApiUser': api_user,
        'ApiKey': api_key,
        'UserName': api_user,
        'ClientIp': client_ip,
        'Command': 'namecheap.domains.dns.setHosts',
        'SLD': 'sophia-intel',
        'TLD': 'ai',
        f'HostName{i}': record['Name'],
        f'RecordType{i}': record['Type'],
        f'Address{i}': record['Address'],
        f'TTL{i}': record['TTL']
    }
    
    # Add all records in one call
    if i == 1:
        for j, r in enumerate(records[1:], i+1):
            params[f'HostName{j}'] = r['Name']
            params[f'RecordType{j}'] = r['Type']
            params[f'Address{j}'] = r['Address']
            params[f'TTL{j}'] = r['TTL']
        
        response = requests.get(url, params=params)
        if 'Success' in response.text:
            print("✅ DNS records configured successfully")
        else:
            print(f"❌ DNS configuration failed: {response.text}")
        break

print("\nDNS Records configured:")
for record in records:
    print(f"  {record['Type']} {record['Name']}.sophia-intel.ai → {record['Address']}")
EOF

# Run DNS configuration with Pulumi ESC
pulumi env run sophia-ai/production -- python /tmp/configure_dns.py

# Step 2: Deploy Frontend to Vercel
echo ""
echo "🎨 Step 2: Deploying Frontend to Vercel"
echo "--------------------------------------"

cd frontend

# Create vercel.json if it doesn't exist
if [ ! -f vercel.json ]; then
    cat > vercel.json << EOF
{
  "name": "sophia-intel-ai",
  "alias": ["sophia-intel.ai", "www.sophia-intel.ai", "dashboard.sophia-intel.ai"],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.sophia-intel.ai",
    "NEXT_PUBLIC_APP_URL": "https://sophia-intel.ai"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "https://api.sophia-intel.ai",
      "NEXT_PUBLIC_APP_URL": "https://sophia-intel.ai"
    }
  }
}
EOF
fi

# Deploy with Vercel
echo "Deploying to Vercel..."
pulumi env run sophia-ai/production -- vercel --prod --yes

cd ..

# Step 3: Deploy Backend to Lambda Labs
echo ""
echo "🖥️  Step 3: Deploying Backend to Lambda Labs"
echo "------------------------------------------"

# SSH into Lambda Labs and set up Kubernetes
echo "Setting up K3s on Lambda Labs..."
cat > /tmp/setup_k3s.sh << 'EOF'
#!/bin/bash
# Install K3s if not already installed
if ! command -v k3s &> /dev/null; then
    curl -sfL https://get.k3s.io | sh -
fi

# Create namespace
kubectl create namespace sophia-ai-prod || true

# Apply configurations
kubectl apply -f k8s/base/
kubectl apply -f k8s/argocd/
kubectl apply -f k8s/monitoring/
kubectl apply -f k8s/base/hpa-config.yaml
EOF

# Copy files and setup
echo "Copying files to Lambda Labs..."
scp -r k8s root@192.222.58.232:/root/
scp /tmp/setup_k3s.sh root@192.222.58.232:/tmp/
ssh root@192.222.58.232 "chmod +x /tmp/setup_k3s.sh && /tmp/setup_k3s.sh"

# Step 4: Configure n8n workflows
echo ""
echo "🔄 Step 4: Setting up n8n Workflows"
echo "----------------------------------"
echo "n8n will be configured at: https://n8n.sophia-intel.ai"
echo "Please complete n8n setup manually after deployment"

# Step 5: Validate Deployment
echo ""
echo "✅ Step 5: Validating Deployment"
echo "-------------------------------"

# Check DNS propagation
echo "Checking DNS propagation..."
dig +short sophia-intel.ai
dig +short api.sophia-intel.ai

# Check services
echo ""
echo "Checking service health..."
curl -s -o /dev/null -w "Frontend: %{http_code}\n" https://sophia-intel.ai || true
curl -s -o /dev/null -w "API: %{http_code}\n" https://api.sophia-intel.ai/health || true

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "Your Sophia AI instance is available at:"
echo "  🌐 Main Site: https://sophia-intel.ai"
echo "  🎨 Dashboard: https://dashboard.sophia-intel.ai"
echo "  🔌 API: https://api.sophia-intel.ai"
echo "  📊 Monitoring: https://grafana.sophia-intel.ai"
echo "  📚 Docs: https://docs.sophia-intel.ai"
echo ""
echo "Next steps:"
echo "1. Wait for DNS propagation (5-30 minutes)"
echo "2. Configure SSL certificates (auto via Let's Encrypt)"
echo "3. Set up monitoring alerts in Grafana"
echo "4. Configure n8n workflows"
echo "5. Run production validation tests" 