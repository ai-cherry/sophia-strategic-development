#!/bin/bash

echo "🚀 Quick Backend Deployment for Sophia AI"
echo "========================================"
echo ""

# Check if we're on the Lambda Labs server
if [[ $(hostname -I | cut -d' ' -f1) != "192.222.58.232" ]]; then
    echo "⚠️  This script should be run on the Lambda Labs server"
    echo "SSH into the server first: ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@192.222.58.232"
    exit 1
fi

# Navigate to project directory
cd ~/sophia-main || exit 1

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/qdrant
mkdir -p data/redis
mkdir -p data/postgres

# Set up environment variables
echo "🔧 Setting up environment..."
cat > .env << EOF
# Environment
ENVIRONMENT=prod
NODE_ENV=production

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=https://app.sophia-intel.ai

# Database URLs
DATABASE_URL=postgresql://sophia:sophia_secure_2024@localhost:5432/sophia_ai
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333

# API Keys (these should be set as environment variables)
OPENAI_API_KEY=\${OPENAI_API_KEY}
ANTHROPIC_API_KEY=\${ANTHROPIC_API_KEY}
GONG_API_KEY=\${GONG_API_KEY}
PINECONE_API_KEY=\${PINECONE_API_KEY}
EOF

# Start Qdrant
echo "🔷 Starting Qdrant..."
docker run -d \
    --name qdrant \
    -p 6333:6333 \
    -p 6334:6334 \
    -v $(pwd)/data/qdrant:/qdrant/storage \
    --restart unless-stopped \
    qdrant/qdrant:latest

# Start Redis
echo "🔴 Starting Redis..."
docker run -d \
    --name redis \
    -p 6379:6379 \
    -v $(pwd)/data/redis:/data \
    redis:7-alpine

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if Python venv exists, create if not
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Initialize Qdrant schema
echo "🔷 Initializing Qdrant schema..."
python scripts/init_qdrant_schema.py

# Apply PostgreSQL schema
echo "🐘 Applying PostgreSQL schema..."
python scripts/apply_pg_schema.py

# Start the backend service
echo "🚀 Starting Sophia AI Backend..."
nohup python -m uvicorn backend.app.simple_fastapi:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    > logs/backend.log 2>&1 &

echo "✅ Backend deployment complete!"
echo ""
echo "📍 Services running at:"
echo "  - API: http://192.222.58.232:8000"
echo "  - API Docs: http://192.222.58.232:8000/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Qdrant: localhost:6333"
echo ""
echo "�� Logs available at: logs/backend.log"
echo ""
echo "🔒 Next step: Configure SSL with:"
echo "  sudo certbot --nginx -d sophia-intel.ai -d api.sophia-intel.ai -d webhooks.sophia-intel.ai"
echo "🌟 Sophia AI Backend Ready!"
echo "📍 Endpoints:"
echo "  - API: localhost:8000"
echo "  - Qdrant: localhost:6333" 