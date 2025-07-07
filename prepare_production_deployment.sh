#!/bin/bash
# Prepare Sophia AI for Production Deployment
# This script prepares the codebase for deployment to Vercel (frontend) and Lambda Labs (backend)

set -euo pipefail

echo "🚀 SOPHIA AI PRODUCTION PREPARATION"
echo "=================================="
echo "Domain: sophia-intel.ai"
echo "Frontend: Vercel"
echo "Backend: Lambda Labs K3s"
echo ""

# Step 1: Check prerequisites
echo "📋 Checking prerequisites..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Check if we have the required environment variables
if [ -z "${VERCEL_API_TOKEN:-}" ]; then
    export VERCEL_API_TOKEN="zjlHk1AEREFUS3DmLivZ90GZ"
fi

if [ -z "${NAMECHEAP_API_KEY:-}" ]; then
    export NAMECHEAP_API_KEY="d6913ec33b2c4d328be9cbb4db382eca"
fi

# Step 2: Prepare frontend for Vercel
echo "🎨 Preparing frontend for Vercel..."

cd frontend

# Create/update vercel.json
cat > vercel.json << 'JSON'
{
  "name": "sophia-ai-frontend",
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "env": {
    "VITE_API_URL": "https://api.sophia-intel.ai",
    "VITE_APP_URL": "https://app.sophia-intel.ai",
    "VITE_ENVIRONMENT": "production"
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.sophia-intel.ai/$1"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
JSON

# Create .vercelignore
cat > .vercelignore << 'IGNORE'
node_modules
.env.local
.env.development
*.log
.DS_Store
IGNORE

# Update environment variables for production
cat > .env.production << 'ENV'
VITE_API_URL=https://api.sophia-intel.ai
VITE_APP_URL=https://app.sophia-intel.ai
VITE_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
ENV

cd ..

# Step 3: Build Docker images for backend
echo "🐳 Building backend Docker images..."

# Create optimized production Dockerfile
cat > Dockerfile.production << 'DOCKERFILE'
# Multi-stage build for production
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV for fast dependency management
RUN curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /build

# Copy dependency files
COPY pyproject.toml uv.lock* ./
COPY backend/ ./backend/

# Install dependencies with UV
RUN uv sync --no-dev

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy from builder
COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/backend /app/backend

# Copy the FastAPI app
COPY backend/fastapi_main.py /app/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV ENVIRONMENT="prod"
ENV PULUMI_ORG="scoobyjava-org"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "fastapi_main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
DOCKERFILE

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.production -t scoobyjava15/sophia-backend:latest .

# Step 4: Create deployment manifests
echo "📄 Creating Kubernetes manifests..."

mkdir -p k8s-manifests

# Create production namespace
cat > k8s-manifests/00-namespace.yaml << 'YAML'
apiVersion: v1
kind: Namespace
metadata:
  name: sophia-ai
  labels:
    app: sophia-ai
    environment: production
YAML

# Create production configmap
cat > k8s-manifests/01-configmap.yaml << 'YAML'
apiVersion: v1
kind: ConfigMap
metadata:
  name: sophia-config
  namespace: sophia-ai
data:
  ENVIRONMENT: "prod"
  PULUMI_ORG: "scoobyjava-org"
  API_URL: "https://api.sophia-intel.ai"
  FRONTEND_URL: "https://app.sophia-intel.ai"
YAML

# Create ingress with SSL
cat > k8s-manifests/02-ingress.yaml << 'YAML'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sophia-ingress
  namespace: sophia-ai
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.sophia-intel.ai
    - mcp.sophia-intel.ai
    - monitor.sophia-intel.ai
    secretName: sophia-tls
  rules:
  - host: api.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-backend
            port:
              number: 8000
YAML

echo "✅ Production preparation complete!"
echo ""
echo "Next steps:"
echo "1. Push Docker image: docker push scoobyjava15/sophia-backend:latest"
echo "2. Deploy frontend: cd frontend && vercel --prod"
echo "3. Run: ./deploy_production_complete.sh"
