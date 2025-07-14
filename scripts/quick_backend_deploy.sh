#!/bin/bash

echo "🚀 Quick Backend Deployment for Sophia AI"
echo "========================================"
echo ""

# Check if we're on the Lambda Labs server
if [[ $(hostname -I | cut -d' ' -f1) != "192.222.58.232" ]]; then
    echo "⚠️  This script should be run on the Lambda Labs server"
    echo "SSH into the server first: ssh -i ~/.ssh/lambda_labs_private_key ubuntu@192.222.58.232"
    exit 1
fi

# Navigate to project directory
cd ~/sophia-main || exit 1

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/weaviate

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
DATABASE_URL=postgresql://sophia:sophia2025@localhost:5432/sophia_ai
REDIS_URL=redis://localhost:6379
WEAVIATE_URL=http://localhost:8080

# API Keys (these should be set as environment variables)
OPENAI_API_KEY=\${OPENAI_API_KEY}
ANTHROPIC_API_KEY=\${ANTHROPIC_API_KEY}
GONG_API_KEY=\${GONG_API_KEY}
PINECONE_API_KEY=\${PINECONE_API_KEY}
EOF

# Start PostgreSQL
echo "🐘 Starting PostgreSQL..."
docker run -d \
    --name postgres \
    -e POSTGRES_USER=sophia \
    -e POSTGRES_PASSWORD=sophia2025 \
    -e POSTGRES_DB=sophia_ai \
    -p 5432:5432 \
    -v $(pwd)/data/postgres:/var/lib/postgresql/data \
    postgres:15-alpine

# Start Redis
echo "🔴 Starting Redis..."
docker run -d \
    --name redis \
    -p 6379:6379 \
    -v $(pwd)/data/redis:/data \
    redis:7-alpine

# Start Weaviate
echo "🔷 Starting Weaviate..."
docker run -d \
    --name weaviate \
    -p 8080:8080 \
    -p 50051:50051 \
    -v $(pwd)/data/weaviate:/var/lib/weaviate \
    -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
    -e DEFAULT_VECTORIZER_MODULE=text2vec-transformers \
    -e ENABLE_MODULES=text2vec-transformers \
    -e TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080 \
    semitechnologies/weaviate:1.25.4

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

# Initialize Weaviate schema
echo "🔷 Initializing Weaviate schema..."
python scripts/init_weaviate_schema.py

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
echo "  - Weaviate: localhost:8080"
echo ""
echo "📝 Logs available at: logs/backend.log"
echo ""
echo "🔒 Next step: Configure SSL with:"
echo "  sudo certbot --nginx -d sophia-intel.ai -d api.sophia-intel.ai -d webhooks.sophia-intel.ai" 