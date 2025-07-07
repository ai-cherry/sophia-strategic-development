#!/bin/bash
# Unified Build Images Script - Build Docker images for Sophia AI

set -e

echo "🏗️ Building Sophia AI Docker Images"
echo "===================================="

# Build main backend image
echo "📦 Building sophia-ai backend image..."
docker build -f Dockerfile.production -t scoobyjava15/sophia-ai:latest .

# For now, we'll use placeholder images for the others
echo "📦 Using placeholder images for other services..."

# Tag redis and postgres with our registry (they'll use official images)
docker pull redis:7-alpine
docker tag redis:7-alpine scoobyjava15/redis:latest

docker pull postgres:16-alpine
docker tag postgres:16-alpine scoobyjava15/postgres:latest

# For services we don't have yet, we'll create minimal placeholders
echo "📦 Creating placeholder for mem0-server..."
cat > Dockerfile.mem0 << 'EOF'
FROM python:3.12-slim
RUN pip install fastapi uvicorn
RUN echo 'from fastapi import FastAPI; app = FastAPI(); app.get("/health")(lambda: {"status": "ok"})' > app.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
docker build -f Dockerfile.mem0 -t scoobyjava15/sophia-ai-mem0:latest .
rm Dockerfile.mem0

echo "📦 Creating placeholder for cortex-aisql-server..."
cat > Dockerfile.cortex << 'EOF'
FROM python:3.12-slim
RUN pip install fastapi uvicorn
RUN echo 'from fastapi import FastAPI; app = FastAPI(); app.get("/health")(lambda: {"status": "ok"})' > app.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
docker build -f Dockerfile.cortex -t scoobyjava15/sophia-ai-cortex:latest .
rm Dockerfile.cortex

echo "✅ Build complete!"
echo ""
echo "📋 Images built:"
echo "  - scoobyjava15/sophia-ai:latest"
echo "  - scoobyjava15/sophia-ai-mem0:latest"
echo "  - scoobyjava15/sophia-ai-cortex:latest"
echo ""
echo "🚀 Now run ./unified_push_images.sh to push to Lambda Labs"
