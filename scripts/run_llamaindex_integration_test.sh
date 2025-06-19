#!/bin/bash
# Run LlamaIndex Integration Test
# This script syncs LlamaIndex secrets from GitHub to Pulumi ESC and runs the integration test.

set -e

echo "Sophia AI - LlamaIndex Integration Test"
echo "========================================"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if Pulumi ESC is configured
if ! command -v pulumi &> /dev/null; then
    echo "Warning: Pulumi CLI is not installed or not in PATH"
    echo "Secret management may not work correctly"
fi

# Sync LlamaIndex secrets from GitHub to Pulumi ESC
echo "Syncing LlamaIndex secrets from GitHub to Pulumi ESC..."
python infrastructure/esc/llamaindex_secrets.py --sync-secrets

# Update .env file with LlamaIndex secrets
echo "Updating .env file with LlamaIndex secrets..."
python infrastructure/esc/llamaindex_secrets.py --update-env

# Run the LlamaIndex integration test
echo "Running LlamaIndex integration test..."
python scripts/test_llamaindex_integration.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo "LlamaIndex integration test completed successfully!"
    exit 0
else
    echo "LlamaIndex integration test failed!"
    exit 1
fi
