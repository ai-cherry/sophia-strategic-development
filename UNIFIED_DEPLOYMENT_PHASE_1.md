# PHASE 1: FOUNDATION & FRONTEND FIXES (2 Hours)

## Overview
This phase fixes critical configuration issues preventing the frontend from building and connecting to the backend.

## Pre-Flight Checklist
- [ ] Verify GitHub → Pulumi ESC → Backend secret flow
- [ ] Create deployment branch: `fix/deploy-unified-chat`
- [ ] Backup current configurations
- [ ] Document current Vercel project settings

## 1.1 Fix Vercel Build Configuration (30 minutes)

### A. Update Root vercel.json
```json
{
  "version": 2,
  "name": "sophia-ai",
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.sophia-intel.ai/$1"
    },
    {
      "src": "/ws/(.*)",
      "dest": "https://api.sophia-intel.ai/ws/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "https://api.sophia-intel.ai",
    "VITE_WS_URL": "wss://api.sophia-intel.ai/ws",
    "VITE_ENVIRONMENT": "production"
  }
}
```

### B. Update Frontend vercel.json
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### C. Add Build Script to frontend/package.json
```json
{
  "scripts": {
    "build": "vite build",
    "vercel-build": "npm run build"
  }
}
```

## 1.2 Create Production Environment Configuration (15 minutes)

### A. Create frontend/.env.local
```bash
# Production Environment Variables
VITE_API_URL=https://api.sophia-intel.ai
VITE_WS_URL=wss://api.sophia-intel.ai/ws
VITE_ENVIRONMENT=production
VITE_DEBUG=false
VITE_LOG_LEVEL=warn

# Feature Flags
VITE_ENABLE_WEBSOCKET=true
VITE_ENABLE_MCP_SERVERS=true
VITE_ENABLE_AI_MEMORY=true
```

### B. Create frontend/.env.development
```bash
# Development Environment Variables
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENVIRONMENT=development
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
```

### C. Update .gitignore
```
# Environment files
.env.local
.env.*.local
!.env.template
!.env.development.template
```

## 1.3 Clean Domain References (15 minutes)

### A. Search and Replace Script
```bash
#!/bin/bash
# scripts/fix-domain-references.sh

echo "🔍 Finding old domain references..."
grep -r "payready.com" frontend/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.json" | tee old-domains.log

echo "🔧 Replacing with sophia-intel.ai..."
find frontend/ -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.json" \) \
  -exec sed -i.bak 's/payready\.com/sophia-intel.ai/g' {} \;

echo "✅ Domain references updated"
```

### B. Verify API Client Configuration
```typescript
// frontend/src/services/apiClient.ts
const API_BASE = import.meta.env.VITE_API_URL || 'https://api.sophia-intel.ai';
const WS_BASE = import.meta.env.VITE_WS_URL || 'wss://api.sophia-intel.ai/ws';

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## 1.4 CI/CD Pipeline Guards (30 minutes)

### A. Create .github/workflows/frontend-checks.yml
```yaml
name: Frontend Pre-Deploy Checks
on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
      - 'vercel.json'
      - '.github/workflows/frontend-checks.yml'

jobs:
  validate-env:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check Required Environment Variables
        run: |
          required_vars=(
            "VITE_API_URL"
            "VITE_WS_URL"
            "VITE_ENVIRONMENT"
          )

          for var in "${required_vars[@]}"; do
            if ! grep -q "$var" frontend/.env.template; then
              echo "❌ Missing $var in .env.template"
              exit 1
            fi
          done
          echo "✅ All required environment variables documented"

      - name: Validate Build Configuration
        run: |
          if ! grep -q "@vercel/static-build" vercel.json; then
            echo "❌ Incorrect build system in vercel.json"
            exit 1
          fi
          echo "✅ Build configuration valid"

      - name: Test Local Build
        working-directory: frontend
        run: |
          npm ci
          npm run build
          if [ ! -d "dist" ]; then
            echo "❌ Build output directory 'dist' not found"
            exit 1
          fi
          echo "✅ Local build successful"
```

### B. Update Vercel Deployment Workflow
```yaml
# .github/workflows/vercel-deployment.yml
name: Deploy Frontend to Vercel
on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - 'vercel.json'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install Vercel CLI
        run: npm install -g vercel@latest

      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build Project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy to Production
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Post Deployment Tests
        run: |
          sleep 30  # Wait for deployment to propagate
          response=$(curl -s -o /dev/null -w "%{http_code}" https://app.sophia-intel.ai)
          if [ $response -ne 200 ]; then
            echo "❌ Deployment verification failed: HTTP $response"
            exit 1
          fi
          echo "✅ Deployment successful: HTTP $response"
```

## 1.5 Local Validation (30 minutes)

### A. Test Script
```bash
#!/bin/bash
# scripts/test-frontend-build.sh

cd frontend

echo "📦 Installing dependencies..."
npm ci

echo "🔧 Setting up test environment..."
cp .env.template .env.local
sed -i 's|http://localhost:8000|https://api.sophia-intel.ai|g' .env.local

echo "🏗️ Building frontend..."
npm run build

echo "🔍 Validating build output..."
if [ ! -f "dist/index.html" ]; then
  echo "❌ Build failed: index.html not found"
  exit 1
fi

if [ ! -d "dist/assets" ]; then
  echo "❌ Build failed: assets directory not found"
  exit 1
fi

echo "✅ Frontend build successful!"
echo "📊 Build stats:"
du -sh dist/
find dist -name "*.js" -o -name "*.css" | wc -l
```

### B. Preview Deployment
```bash
# Test with Vercel CLI locally
cd frontend
vercel dev --listen 3000

# In another terminal, test the preview
curl http://localhost:3000
curl http://localhost:3000/api/health  # Should proxy to backend
```

## Success Criteria ✅
- [ ] `vercel.json` uses `@vercel/static-build` instead of `@vercel/next`
- [ ] Frontend builds successfully with `npm run build`
- [ ] Environment variables properly configured
- [ ] All domain references updated to sophia-intel.ai
- [ ] CI/CD checks pass
- [ ] Local preview works

## Rollback Plan 🔄
```bash
# Revert vercel.json
git checkout HEAD~1 vercel.json

# Revert environment files
rm frontend/.env.local
git checkout HEAD~1 frontend/.env.template

# Revert domain changes
git checkout HEAD~1 frontend/
```

## Phase 1 Completion Checklist
- [ ] All configuration files updated
- [ ] Environment variables set correctly
- [ ] Domain references cleaned
- [ ] CI/CD pipelines configured
- [ ] Local validation passed
- [ ] Changes committed to feature branch
- [ ] Ready for Phase 2: Backend Deployment

## Time Tracking
- Start Time: ___________
- End Time: ___________
- Total Duration: ___________
- Issues Encountered: ___________

## Notes
_Document any deviations from the plan or additional fixes required_
