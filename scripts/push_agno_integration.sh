#!/bin/bash
# Push Agno integration to GitHub

set -e

# Print header
echo "====================================="
echo "Pushing Agno Integration to GitHub"
echo "====================================="
echo

# Check if git is installed
if ! command -v git > /dev/null 2>&1; then
  echo "Error: git is not installed"
  exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "Error: Not in a git repository"
  exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Create a new branch for the Agno integration
BRANCH_NAME="feature/agno-integration-$(date +%Y%m%d)"
echo "Creating branch: $BRANCH_NAME"
git checkout -b $BRANCH_NAME

# Add the new files
echo "Adding new files..."
git add \
  backend/integrations/agno_integration.py \
  backend/mcp/agno_bridge.py \
  backend/mcp/agno_mcp_server.py \
  backend/app/routers/agno_router.py \
  frontend/src/components/AgUIRetoolEmbed.jsx \
  infrastructure/esc/agno_secrets.py \
  scripts/test_agno_integration.py \
  scripts/start_fastapi_app.py \
  scripts/run_agno_integration_test.sh \
  scripts/push_agno_integration.sh

# Check if docker-compose.yml and mcp-config/mcp_servers.json were modified
if git diff --cached --quiet docker-compose.yml; then
  echo "docker-compose.yml not modified, adding..."
  git add docker-compose.yml
fi

if git diff --cached --quiet mcp-config/mcp_servers.json; then
  echo "mcp-config/mcp_servers.json not modified, adding..."
  git add mcp-config/mcp_servers.json
fi

# Commit the changes
echo "Committing changes..."
git commit -m "Add Agno integration for Sophia AI

This commit adds the Agno integration for Sophia AI, including:
- Agno integration module
- MCP-to-Agno bridge
- Agno MCP server
- FastAPI router
- React component for Retool
- Secret management
- Testing infrastructure"

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin $BRANCH_NAME

echo
echo "====================================="
echo "✅ Agno integration pushed to GitHub!"
echo "====================================="
echo
echo "Branch: $BRANCH_NAME"
echo
echo "Next steps:"
echo "1. Create a pull request on GitHub"
echo "2. Request a code review"
echo "3. Merge the pull request"
echo

# Return to the original branch
echo "Returning to branch: $CURRENT_BRANCH"
git checkout $CURRENT_BRANCH

exit 0
