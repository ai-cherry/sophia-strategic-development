#!/bin/bash
# Step-by-step deployment for Sophia AI

echo "🚀 Sophia AI Deployment - Step by Step"
echo "====================================="

# Step 1: Configure DNS
echo ""
echo "📍 Step 1: Configuring DNS for sophia-intel.ai"
echo "---------------------------------------------"

# Create DNS configuration script
cat > /tmp/configure_dns.py << 'EOF'
import requests

# Namecheap credentials
api_key = "d6913ec33b2c4d328be9cbb4db382eca"
api_user = "scoobyjava"
client_ip = requests.get('https://api.ipify.org').text

# DNS records
records = [
    {'Type': 'A', 'Name': '@', 'Address': '76.76.21.21'},
    {'Type': 'A', 'Name': 'www', 'Address': '76.76.21.21'},
    {'Type': 'A', 'Name': 'api', 'Address': '192.222.58.232'},
    {'Type': 'CNAME', 'Name': 'dashboard', 'Address': '192.222.58.232.'},
    {'Type': 'A', 'Name': 'docs', 'Address': '76.76.21.21'},
    {'Type': 'A', 'Name': 'grafana', 'Address': '192.222.58.232'},
]

# Namecheap API
url = "https://api.namecheap.com/xml.response"

# Build parameters
params = {
    'ApiUser': api_user,
    'ApiKey': api_key,
    'UserName': api_user,
    'ClientIp': client_ip,
    'Command': 'namecheap.domains.dns.setHosts',
    'SLD': 'sophia-intel',
    'TLD': 'ai'
}

# Add all records
for i, record in enumerate(records, 1):
    params[f'HostName{i}'] = record['Name']
    params[f'RecordType{i}'] = record['Type']
    params[f'Address{i}'] = record['Address']
    params[f'TTL{i}'] = '1800'

# Make API call
response = requests.post(url, data=params)
if '<ApiResponse Status="OK"' in response.text:
    print("✅ DNS records configured successfully!")
    for r in records:
        print(f"   {r['Type']} {r['Name']}.sophia-intel.ai → {r['Address']}")
else:
    print(f"❌ DNS configuration failed")
    print(response.text)
EOF

python /tmp/configure_dns.py

# Step 2: Deploy Frontend
echo ""
echo "🎨 Step 2: Deploying Frontend (Lambda Labs)
echo "--------------------------------------"

cd frontend

# Create nginx.conf
cat > nginx.conf << EOF
{
  "name": "sophia-intel-ai",
  "alias": ["sophia-intel.ai", "www.sophia-intel.ai"],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.sophia-intel.ai",
    "NEXT_PUBLIC_APP_URL": "https://sophia-intel.ai"
  }
}
EOF

# Deploy to Lambda Labs
echo "Deploy to Lambda Labs
# Lambda Labs Deploy to Lambda Labs

cd ..

echo ""
echo "✅ Deployment Steps Complete!"
echo ""
echo "Your sites will be available at:"
echo "  🌐 https://sophia-intel.ai"
echo "  🌐 https://www.sophia-intel.ai"
echo "  🔌 https://api.sophia-intel.ai (requires backend setup)"
echo ""
echo "DNS propagation may take 5-30 minutes." 