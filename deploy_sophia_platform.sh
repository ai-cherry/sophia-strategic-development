#!/bin/bash
#
# Master Deployment Script for the Sophia AI Platform on Lambda Labs
#
# This script orchestrates the entire end-to-end deployment process,
# from provisioning the Lambda Labs instance to deploying all application
# services, by running the single, unified Pulumi infrastructure project.
#

set -e

echo "🚀 Starting Full End-to-End Deployment of the Sophia AI Platform..."

# --- Configuration ---
PULUMI_ORG="scoobyjava-org" # Replace with your Pulumi organization
STACK_NAME="sophia-prod-on-lambda"
INFRA_DIR="./infrastructure"

# --- Main Deployment Step ---
echo "\n🔹 Entering infrastructure project directory..."
cd "$INFRA_DIR"

echo "\n🔹 Selecting or creating the main infrastructure stack..."
# Check if the stack already exists, if not, create it.
if ! pulumi stack ls | grep -q "$STACK_NAME"; then
    echo "Creating new Pulumi stack: $STACK_NAME"
    pulumi stack init "$PULUMI_ORG/$STACK_NAME"
else
    echo "Using existing Pulumi stack: $STACK_NAME"
    pulumi stack select "$STACK_NAME"
fi

echo "\n🔹 Running 'pulumi up' to provision the entire platform."
echo "This will provision the Lambda Labs instance, install Kubernetes, and deploy all services. This may take a very long time..."
pulumi up --yes

echo "\n🎉 Deployment Complete!"
echo "--------------------------"
echo "The Sophia AI platform deployment process has finished."
echo "You can access the services via the URLs provided in the Pulumi stack outputs."
echo "To see outputs, run from the '$INFRA_DIR' directory: pulumi stack output"

cd ..
