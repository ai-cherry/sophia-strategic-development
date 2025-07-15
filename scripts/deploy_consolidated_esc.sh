#!/bin/bash
# Deploy Consolidated ESC Configuration
echo "🚀 Deploying Consolidated Pulumi ESC Configuration..."

# Update the ESC environment
pulumi env set scoobyjava-org/default/sophia-ai-production --file infrastructure/esc/CONSOLIDATED_ESC_CONFIG.yaml

# Validate the deployment
pulumi env get scoobyjava-org/default/sophia-ai-production | head -20

echo "✅ Deployment complete!"
