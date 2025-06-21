#!/bin/bash

# Sophia AI - Simple Environment Setup
# Sets up basic environment variables for Sophia AI backend

set -e

echo "🚀 Setting up Sophia AI environment variables..."

# Create a simple .env file for local development
cat > .env << 'EOF'
# Pulumi Configuration
PULUMI_ORG=your-pulumi-org
PULUMI_ACCESS_TOKEN=your-pulumi-access-token

# Core Application
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Business Integrations
GONG_ACCESS_KEY=your-gong-access-key
GONG_CLIENT_SECRET=your-gong-client-secret
GONG_URL=https://your-instance.app.gong.io

# Development Tools
RETOOL_API_TOKEN=your-retool-api-token

# Database (default development settings)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sophia_enhanced

# Configuration
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1
EOF

echo "✅ Environment file created: .env"
echo "🔧 Testing backend imports..."

# Test backend imports with environment variables
export $(cat .env | xargs) && python3 -c "
import sys
sys.path.append('.')
try:
    import backend.main
    print('✅ Backend imports successful!')
except Exception as e:
    print(f'❌ Backend import failed: {e}')
"

echo "🎯 Environment setup complete!"

