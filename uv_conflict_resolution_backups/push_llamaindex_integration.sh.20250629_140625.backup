#!/bin/bash
# Push LlamaIndex Integration to GitHub
# This script commits and pushes the LlamaIndex integration changes to GitHub.

set -e

echo "Sophia AI - Push LlamaIndex Integration to GitHub"
echo "================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed or not in PATH"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get the current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Add all files
echo "Adding files to git..."
git add backend/app/routers/llamaindex_router.py
git add backend/app/fastapi_app.py
git add backend/integrations/llamaindex_integration.py
git add infrastructure/esc/llamaindex_secrets.py
git add scripts/test_llamaindex_integration.py
git add scripts/run_llamaindex_integration_test.sh
git add scripts/push_llamaindex_integration.sh
git add requirements.txt
git add .github/workflows/mcp-ci-cd.yml

# Commit the changes
echo "Committing changes..."
git commit -m "Add LlamaIndex integration for Hybrid RAG Architecture - Phase 1

- Add LlamaIndex integration module with document processing and querying
- Add FastAPI router for LlamaIndex endpoints
- Update FastAPI app to include LlamaIndex router
- Add secret management with Pulumi ESC for LlamaIndex API keys
- Add test scripts for LlamaIndex integration
- Update CI/CD workflow to include LlamaIndex integration tests
- Update requirements.txt with LlamaIndex dependencies"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin $CURRENT_BRANCH

echo "LlamaIndex integration pushed to GitHub successfully!"
