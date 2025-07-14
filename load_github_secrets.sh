#!/bin/bash
# Sophia AI - Permanent GitHub Secrets Loader
# This loads ALL your actual GitHub organization secrets

echo "🔑 Loading Sophia AI Secrets from GitHub Organization ai-cherry..."

# Load critical secrets from your GitHub organization
export PULUMI_ACCESS_TOKEN="$(gh secret get PULUMI_ACCESS_TOKEN --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export ANTHROPIC_API_KEY="$(gh secret get ANTHROPIC_API_KEY --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export OPENAI_API_KEY="$(gh secret get OPENAI_API_KEY --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export GONG_ACCESS_KEY="$(gh secret get GONG_ACCESS_KEY --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export GONG_CLIENT_SECRET="$(gh secret get GONG_CLIENT_SECRET --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export HUBSPOT_ACCESS_TOKEN="$(gh secret get HUBSPOT_ACCESS_TOKEN --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export LINEAR_API_KEY="$(gh secret get LINEAR_API_KEY --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export LAMBDA_API_KEY="$(gh secret get LAMBDA_API_KEY --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export QDRANT_URL"$(gh secret get QDRANT_URL--org ai-cherry 2>/dev/null || echo 'ZNB04675')"
export QDRANT_SECRET"$(gh secret get QDRANT_SECRET--org ai-cherry 2>/dev/null || echo 'loading_failed')"
export PINECONE_API_KEY="$(gh secret get PINECONE_API_KEY --org ai-cherry 2>/dev/null || echo 'loading_failed')"
export SLACK_BOT_TOKEN="$(gh secret get SLACK_BOT_TOKEN --org ai-cherry 2>/dev/null || echo 'loading_failed')"

# Verify what loaded successfully
echo ""
echo "📊 SECRET LOADING RESULTS:"
secret_count=0

for var in PULUMI_ACCESS_TOKEN ANTHROPIC_API_KEY OPENAI_API_KEY GONG_ACCESS_KEY; do
    if [[ "${!var}" != "loading_failed" && "${!var}" != "" ]]; then
        echo "✅ $var: Successfully loaded"
        ((secret_count++))
    else
        echo "❌ $var: Failed to load from GitHub"
    fi
done

echo ""
echo "🎯 Loaded $secret_count/4 critical secrets from GitHub organization"
echo "💡 Now run: python start_sophia_enhanced.py"
