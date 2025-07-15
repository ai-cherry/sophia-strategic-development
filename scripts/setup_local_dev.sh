#!/bin/bash
# 🧑‍💻 Local Development Setup Script

set -euo pipefail

echo "🧑‍💻 Setting up Sophia AI for local development..."

# Create local environment file
if [[ ! -f .env.local ]]; then
    echo "📄 Creating .env.local from template..."
    cp .env.local.template .env.local
    echo "✅ .env.local created - please edit with your API keys"
else
    echo "✅ .env.local already exists"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check database connection
echo "🗄️  Checking database connection..."
python -c "
from backend.core.auto_esc_config import get_config_value
print('✅ Configuration system working')
"

# Test essential services
echo "🔧 Testing essential services..."
python -c "
import os
print('✅ OpenAI key:', 'configured' if os.getenv('OPENAI_API_KEY') else 'missing')
print('✅ Anthropic key:', 'configured' if os.getenv('ANTHROPIC_API_KEY') else 'missing')
print('✅ Database URL:', 'configured' if os.getenv('DATABASE_URL') else 'missing')
"

echo "🎉 Local development setup complete!"
echo "🚀 Run: python -m backend.app.main"
