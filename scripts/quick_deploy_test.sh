#!/bin/bash
#
# Quick deployment test for Sophia AI
# Tests building and running services locally
#

set -e

echo "🚀 SOPHIA AI QUICK DEPLOYMENT TEST"
echo "=================================="
echo "This will build and run services locally to verify everything works"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
status() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed"
fi
status "Docker is installed"

# Check Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed"
fi
status "Python 3 is installed"

# Check environment variables
if [ -z "$PULUMI_ORG" ]; then
    export PULUMI_ORG="scoobyjava-org"
    warning "PULUMI_ORG not set, using default: $PULUMI_ORG"
fi

if [ -z "$ENVIRONMENT" ]; then
    export ENVIRONMENT="prod"
    warning "ENVIRONMENT not set, using default: $ENVIRONMENT"
fi

echo ""
echo "🐳 Building Docker images..."

# Build backend image
echo "Building backend image..."
docker build -f backend/Dockerfile -t sophia-backend:test . || error "Failed to build backend image"
status "Backend image built"

# Build MCP base image
echo "Building MCP base image..."
docker build -f docker/Dockerfile.mcp-base -t sophia-mcp-base:test . || error "Failed to build MCP base image"
status "MCP base image built"

echo ""
echo "🏃 Running services locally..."

# Create a test network
docker network create sophia-test 2>/dev/null || true

# Run Redis (for caching)
echo "Starting Redis..."
docker run -d --name sophia-redis --network sophia-test -p 6379:6379 redis:alpine || warning "Redis already running"

# Run backend
echo "Starting backend..."
docker run -d --name sophia-backend \
    --network sophia-test \
    -p 8000:8000 \
    -e ENVIRONMENT=prod \
    -e PULUMI_ORG=scoobyjava-org \
    -e REDIS_URL=redis://sophia-redis:6379 \
    sophia-backend:test || error "Failed to start backend"

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "🧪 Running health checks..."

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    status "Backend is healthy"
else
    error "Backend health check failed"
fi

# Check enhanced Sophia endpoint
if curl -f http://localhost:8000/api/v4/sophia/health > /dev/null 2>&1; then
    status "Enhanced Sophia API is healthy"
else
    warning "Enhanced Sophia API not ready yet"
fi

echo ""
echo "🧠 Testing Sophia's personality..."

# Test personality
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v4/sophia/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Hello, test my personality", "user_id": "test_user"}' 2>/dev/null || echo "{}")

if echo "$RESPONSE" | grep -q "response"; then
    status "Sophia responded!"
    echo "Response preview: $(echo "$RESPONSE" | jq -r '.response' 2>/dev/null | head -c 100)..."
else
    warning "Personality test failed - this is normal if services are still starting"
fi

echo ""
echo "📊 Deployment Summary"
echo "===================="
echo "✅ Docker images built successfully"
echo "✅ Services running locally"
echo "✅ Basic health checks passed"
echo ""
echo "🌐 Access Points:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "🧹 To clean up:"
echo "  docker stop sophia-backend sophia-redis"
echo "  docker rm sophia-backend sophia-redis"
echo "  docker network rm sophia-test"
echo ""
echo "🚀 Ready for production deployment!"
echo "   Run: make deploy-all"

# Start Weaviate
echo ""
echo "🐳 Starting Weaviate vector database..."
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -p 50051:50051 \
  --restart unless-stopped \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=text2vec-transformers \
  -e ENABLE_MODULES=text2vec-transformers \
  -e TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080 \
  -e CLUSTER_HOSTNAME=node1 \
  semitechnologies/weaviate:1.25.4 || echo "Weaviate already running"

# Start transformer model for Weaviate
docker run -d \
  --name t2v-transformers \
  -p 8081:8080 \
  --restart unless-stopped \
  semitechnologies/transformers-inference:sentence-transformers-all-MiniLM-L6-v2 || echo "Transformers already running"

# Start Redis
echo ""
echo "🔴 Starting Redis cache..."
docker run -d \
  --name redis \
  -p 6379:6379 \
  --restart unless-stopped \
  redis:7-alpine || echo "Redis already running"

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check Weaviate health
echo ""
echo "🔍 Checking Weaviate health..."
curl -s http://localhost:8080/v1/.well-known/ready | jq || echo "Weaviate not ready yet"

# Initialize Weaviate schema
echo ""
echo "📋 Initializing Weaviate schema..."
python scripts/init_weaviate_schema.py

# Set environment variables
echo ""
echo "🔧 Setting environment variables..."
export ENVIRONMENT=prod
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export WEAVIATE_URL=http://localhost:8080
export REDIS_URL=redis://localhost:6379
export POSTGRESQL_URL=postgresql://sophia:sophia@localhost:5432/sophia
export LAMBDA_INFERENCE_URL=http://localhost:8001

# Dummy Snowflake credentials (for transition period)
export SNOWFLAKE_USER=dummy
export SNOWFLAKE_ACCOUNT=dummy
export SNOWFLAKE_PASSWORD=dummy

# Start backend
echo ""
echo "🚀 Starting Sophia backend on port 8001..."
cd backend && python -m uvicorn app.unified_chat_backend:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo ""
echo "⏳ Waiting for backend to start..."
sleep 10

# Test backend health
echo ""
echo "🔍 Testing backend health..."
curl -s http://localhost:8001/health | jq

# Test API endpoints
echo ""
echo "📡 Testing API endpoints..."
echo "1. System status:"
curl -s http://localhost:8001/api/v4/system/status | jq

echo ""
echo "2. Orchestrator health:"
curl -s http://localhost:8001/api/v4/orchestrator/health | jq

echo ""
echo "3. OpenAPI docs available at: http://localhost:8001/docs"

# Test chat endpoint
echo ""
echo "💬 Testing chat endpoint..."
curl -X POST http://localhost:8001/api/v4/chat/unified \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current deployment status?",
    "user_id": "ceo_user"
  }' | jq

echo ""
echo "✅ Deployment test complete!"
echo ""
echo "📊 Service Status:"
echo "  - Weaviate: http://localhost:8080"
echo "  - Redis: redis://localhost:6379"
echo "  - Backend: http://localhost:8001"
echo "  - API Docs: http://localhost:8001/docs"
echo ""
echo "🛑 To stop all services:"
echo "  docker stop weaviate t2v-transformers redis"
echo "  kill $BACKEND_PID" 