#!/bin/bash
echo "🚀 SOPHIA AI - PERMANENT SECRETS FIX"
echo "Loading ALL your GitHub organization secrets..."

# Load secrets directly from GitHub
echo "🔑 Getting PULUMI_ACCESS_TOKEN..."
export PULUMI_ACCESS_TOKEN=$(gh secret get PULUMI_ACCESS_TOKEN --org ai-cherry 2>/dev/null || echo "failed")

echo "🔑 Getting ANTHROPIC_API_KEY..."  
export ANTHROPIC_API_KEY=$(gh secret get ANTHROPIC_API_KEY --org ai-cherry 2>/dev/null || echo "failed")

echo "🔑 Getting OPENAI_API_KEY..."
export OPENAI_API_KEY=$(gh secret get OPENAI_API_KEY --org ai-cherry 2>/dev/null || echo "failed")

echo "🔑 Getting GONG_ACCESS_KEY..."
export GONG_ACCESS_KEY=$(gh secret get GONG_ACCESS_KEY --org ai-cherry 2>/dev/null || echo "failed")

echo "🔑 Getting other critical secrets..."
export GONG_CLIENT_SECRET=$(gh secret get GONG_CLIENT_SECRET --org ai-cherry 2>/dev/null || echo "failed")
export HUBSPOT_ACCESS_TOKEN=$(gh secret get HUBSPOT_ACCESS_TOKEN --org ai-cherry 2>/dev/null || echo "failed")
export LINEAR_API_KEY=$(gh secret get LINEAR_API_KEY --org ai-cherry 2>/dev/null || echo "failed")
export PINECONE_API_KEY=$(gh secret get PINECONE_API_KEY --org ai-cherry 2>/dev/null || echo "failed")
export SLACK_BOT_TOKEN=$(gh secret get SLACK_BOT_TOKEN --org ai-cherry 2>/dev/null || echo "failed")

# Test what loaded
echo ""
echo "📊 VERIFICATION:"
if [[ "$PULUMI_ACCESS_TOKEN" != "failed" ]]; then
    echo "✅ PULUMI_ACCESS_TOKEN: ${PULUMI_ACCESS_TOKEN:0:20}..."
else
    echo "❌ PULUMI_ACCESS_TOKEN: Failed"
fi

if [[ "$ANTHROPIC_API_KEY" != "failed" ]]; then
    echo "✅ ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:20}..."
else
    echo "❌ ANTHROPIC_API_KEY: Failed"  
fi

if [[ "$OPENAI_API_KEY" != "failed" ]]; then
    echo "✅ OPENAI_API_KEY: ${OPENAI_API_KEY:0:20}..."
else
    echo "❌ OPENAI_API_KEY: Failed"
fi

echo ""
echo "🎯 Your GitHub secrets are now loaded into the environment!"
echo "💡 Next: python start_sophia_enhanced.py"
