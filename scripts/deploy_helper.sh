#!/bin/bash
# 🚀 Deployment Helper Script

set -euo pipefail

echo "🚀 Sophia AI Deployment Helper"
echo "=============================="

# Check if we're in GitHub Actions
if [[ "${GITHUB_ACTIONS:-false}" == "true" ]]; then
    echo "🔧 Running in GitHub Actions - using automated deployment"
    exec ./scripts/deploy/production-deploy.sh
else
    echo "🧑‍💻 Running locally - validation only"
    
    # Validate environment
    echo "🔍 Validating environment..."
    python3 scripts/validate_deployment.py --environment=development
    
    # Generate metrics report
    echo "📊 Generating metrics report..."
    python3 scripts/report_deployment_metrics.py --environment=development
fi
