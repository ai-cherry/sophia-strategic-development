#!/bin/bash
# Master deployment script for Sophia AI
# This script runs all the necessary steps to deploy Sophia AI to production

echo "🚀 Starting Sophia AI deployment process..."

# Step 1: Push changes to GitHub
echo "📤 Pushing changes to GitHub..."
./push_to_github.sh

# Step 2: Set up production server (if not already set up)
echo "🔧 Setting up production server..."
read -p "Do you want to set up a new production server? (y/n): " setup_server
if [[ $setup_server == "y" ]]; then
  ./setup_production_server.sh
else
  echo "Skipping production server setup."
fi

# Step 3: Deploy to production
echo "🚀 Deploying to production..."
./deploy_to_production.sh

# Step 4: Monitor deployment
echo "🔍 Monitoring deployment..."
./monitor_production.sh

echo "✅ Sophia AI deployment process complete!"
echo "🌐 You can access the system at: https://sophia.payready.ai"
