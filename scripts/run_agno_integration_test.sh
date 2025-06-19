#!/bin/bash
# Run the Agno integration test

set -e

# Print header
echo "====================================="
echo "Sophia AI - Agno Integration Test"
echo "====================================="
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not accessible"
  exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose > /dev/null 2>&1; then
  echo "Error: docker-compose is not installed"
  exit 1
fi

# Set environment variables
export AGNO_API_KEY=${AGNO_API_KEY:-"agno_dev_key_for_testing_only"}

# Start required services
echo "Starting required services..."
docker-compose up -d --build mcp-gateway agno-mcp

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run the test
echo "Running Agno integration test..."
python scripts/test_agno_integration.py

# Check the exit code
if [ $? -eq 0 ]; then
  echo
  echo "====================================="
  echo "✅ Agno integration test passed!"
  echo "====================================="
else
  echo
  echo "====================================="
  echo "❌ Agno integration test failed!"
  echo "====================================="
  exit 1
fi

# Ask if user wants to stop the services
read -p "Do you want to stop the services? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Stopping services..."
  docker-compose stop mcp-gateway agno-mcp
  echo "Services stopped"
fi

exit 0
