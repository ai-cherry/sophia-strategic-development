#!/bin/bash
# Sophia AI Deployment Preparation Script

echo "🚀 Preparing Sophia AI deployment..."

# 1. Create deployment package
echo "📦 Creating deployment package..."
mkdir -p sophia-deploy-package/{backend,frontend,configs,scripts}

# 2. Copy essential files
cp -r backend/* sophia-deploy-package/backend/
cp docker-compose.platform.yml sophia-deploy-package/docker-compose.yml
cp -r scripts/deploy_*.py sophia-deploy-package/scripts/

# 3. Create minimal FastAPI app if main one has issues
cat > sophia-deploy-package/backend/minimal_app.py << 'PYEOF'
from fastapi import FastAPI
import os

app = FastAPI(title="Sophia AI", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": os.getenv("ENVIRONMENT", "prod")}

@app.get("/")
async def root():
    return {"message": "Sophia AI Platform", "version": "1.0.0"}
PYEOF

echo "✅ Deployment package ready"
