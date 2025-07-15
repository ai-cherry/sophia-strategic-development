#!/bin/bash

# Sophia AI Deployment Preparation Script
# This script checks for required files and configurations before deployment.

set -e

echo "=== Sophia AI Deployment Preparation ==="
echo "Date: $(date)"
echo ""

# Function to check for file existence
check_file() {
    if [ ! -f "$1" ]; then
        echo "❌ Error: Required file not found at $1"
        exit 1
    else
        echo "✅ Found required file: $1"
    fi
}

echo "1. Checking for required files..."
check_file "docker-compose.platform.yml"
check_file "k8s/production/sophia-deployment.yaml"
check_file "requirements.txt"
check_file ".env"

echo -e "\n2. Checking for required environment variables..."
if [ -z "$DOCKER_HUB_USERNAME" ]; then
    echo "❌ Error: DOCKER_HUB_USERNAME environment variable not set."
    exit 1
else
    echo "✅ DOCKER_HUB_USERNAME is set."
fi

if [ -z "$DOCKER_HUB_TOKEN" ]; then
    echo "❌ Error: DOCKER_HUB_TOKEN environment variable not set."
    exit 1
else
    echo "✅ DOCKER_HUB_TOKEN is set."
fi

echo -e "\n✅ All deployment preparations are complete." 