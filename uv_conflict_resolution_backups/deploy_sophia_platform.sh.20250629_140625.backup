#!/bin/bash
#
# Master Deployment Script for the Sophia AI Platform on Lambda Labs
#
# This script orchestrates the entire end-to-end deployment process by running
# the single, unified Pulumi infrastructure project against the existing
# 'sophia-ai-production' server.
#

set -e

echo "🚀 Starting Full Deployment of the Sophia AI Platform..."

# --- Configuration ---
PULUMI_ORG="scoobyjava-org" # This should match your Pulumi organization
STACK_NAME="sophia-prod-on-lambda"
INFRA_DIR="./infrastructure"

# --- Main Deployment Step ---
echo "\n🔹 Entering infrastructure project directory..."
cd "$INFRA_DIR"

echo "\n🔹 Installing Python dependencies..."
uv sync

echo "\n🔹 Selecting or creating the main infrastructure stack..."
if ! pulumi stack ls | grep -q "$STACK_NAME"; then
    echo "Creating new Pulumi stack: $STACK_NAME"
    pulumi stack init "$PULUMI_ORG/$STACK_NAME"
else
    echo "Using existing Pulumi stack: $STACK_NAME"
    pulumi stack select "$STACK_NAME"
fi

echo "\n🔹 Running 'pulumi up' to configure the server and deploy all services."
echo "This will install Kubernetes on your existing server and deploy all applications. This may take several minutes..."
pulumi up --yes

echo "\n🎉 Deployment Complete!"
echo "--------------------------"
echo "The Sophia AI platform has been deployed to your Lambda Labs server."
echo "To see outputs (like dashboard URLs), run from the '$INFRA_DIR' directory: pulumi stack output"

cd ..
