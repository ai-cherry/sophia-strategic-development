#!/bin/bash

# Sophia AI Environment Restoration Script
# Use this when other AI coding tools kick you out of your environment

echo "🔄 Restoring Sophia AI Development Environment..."

# Navigate to sophia-main directory
cd ~/sophia-main
echo "✅ Changed to directory: $(pwd)"

# Activate virtual environment
source .venv/bin/activate
echo "✅ Activated virtual environment: $VIRTUAL_ENV"

# Set required environment variables
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org
# Note: Set PULUMI_ACCESS_TOKEN in your environment or use: export PULUMI_ACCESS_TOKEN=your_token_here
if [ -z "$PULUMI_ACCESS_TOKEN" ]; then
    echo "⚠️  PULUMI_ACCESS_TOKEN not set. Please set it manually:"
    echo "   export PULUMI_ACCESS_TOKEN=your_pulumi_token"
else
    echo "✅ PULUMI_ACCESS_TOKEN is set"
fi

echo "✅ Environment variables set:"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo "   PULUMI_ORG: $PULUMI_ORG"
echo "   PULUMI_ACCESS_TOKEN: ${PULUMI_ACCESS_TOKEN:+[SET]}${PULUMI_ACCESS_TOKEN:-[NOT SET]}"

# Verify Python path
echo "✅ Python path: $(which python)"

# Check git status
echo "📊 Git status:"
git status --short

echo ""
echo "🚀 Sophia AI Development Environment Ready!"
echo "   Directory: $(pwd)"
echo "   Virtual Env: $VIRTUAL_ENV"
echo "   Environment: $ENVIRONMENT"
echo ""
echo "💡 Usage examples:"
echo "   • Run FastAPI: uvicorn backend.app.stabilized_fastapi_app:app --host 0.0.0.0 --port 8001"
echo "   • Test Phase 2: python backend/app/phase2_minimal_app.py"
echo "   • Check health: python -c \"from backend.core.auto_esc_config import get_config_value; print('Config loaded:', bool(get_config_value('openai_api_key')))\""
echo ""
