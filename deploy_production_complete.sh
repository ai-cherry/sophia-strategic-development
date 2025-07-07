#!/bin/bash
# SOPHIA AI COMPLETE PRODUCTION DEPLOYMENT
# Domain: sophia-intel.ai
# Frontend: Vercel
# Backend: Lambda Labs 3-node K3s cluster

set -euo pipefail

# Configuration
export DOMAIN="sophia-intel.ai"
export NAMECHEAP_API_KEY="d6913ec33b2c4d328be9cbb4db382eca"
export VERCEL_API_TOKEN="zjlHk1AEREFUS3DmLivZ90GZ"
export LAMBDA_API_KEY="secret_pulumi_87a092f03b5e4896a56542ed6e07d249.bHCTOCe4mkvm9jiT53DWZpnewReAoGic"

echo "🚀 SOPHIA AI PRODUCTION DEPLOYMENT"
echo "=================================="
echo "Domain: $DOMAIN"
echo "Frontend: Vercel"
echo "Backend: Lambda Labs K3s Cluster"
echo ""

# Step 1: Launch Lambda Labs cluster
echo "📦 Step 1: Launching Lambda Labs cluster..."
python3 launch_production_cluster.py

# Wait for cluster config
while [ ! -f "sophia_cluster_config.json" ]; do
    echo "Waiting for cluster config..."
    sleep 5
done

# Get worker IPs
WORKER_IP1=$(jq -r '.workers[0].ip' sophia_cluster_config.json)
WORKER_IP2=$(jq -r '.workers[1].ip' sophia_cluster_config.json)
MASTER_IP="192.222.51.151"

echo "✅ Cluster nodes:"
echo "  Master: $MASTER_IP"
echo "  Worker 1: $WORKER_IP1"
echo "  Worker 2: $WORKER_IP2"

# Step 2: Setup K3s cluster
echo "📦 Step 2: Setting up K3s cluster..."
./setup_k3s_cluster.sh

# Step 3: Deploy Vercel frontend
echo "📦 Step 3: Deploying frontend to Vercel..."
cd frontend
vercel --prod --token=$VERCEL_API_TOKEN --yes
cd ..

# Step 4: Configure DNS
echo "📦 Step 4: Configuring DNS..."
python3 configure_dns.py

# Step 5: Deploy backend services
echo "📦 Step 5: Deploying backend services to K3s..."
./deploy_backend_k3s.sh

echo "✅ Deployment complete!"
echo ""
echo "Access your application at:"
echo "  Frontend: https://sophia-intel.ai"
echo "  API: https://api.sophia-intel.ai"
echo "  Docs: https://api.sophia-intel.ai/docs"
