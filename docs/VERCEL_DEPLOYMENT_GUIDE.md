# 🚀 Sophia AI Frontend Vercel Deployment Guide

## Overview

This guide covers the complete Vercel deployment setup for the Sophia AI frontend, including the new dedicated project configuration and React environment variable integration.

## 🚀 Deployment Architecture

### Environment Mapping
- **Production**: `main` branch → `sophia.payready.com` → `https://api.sophia.payready.com`
- **Staging**: `develop` branch → Vercel preview → `https://api.staging.sophia.payready.com`
- **Development**: PR branches → Vercel preview → `https://api.dev.sophia.payready.com`
- **Local**: `localhost:3000` → configurable backend

### New Vercel Project Configuration
- **Project Name**: `sophia-ai-frontend-prod`
- **GitHub Repository**: `ai-cherry/sophia-main`
- **Source Directory**: `frontend/`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Framework**: Vite (React)

## 🔧 Environment Variables

### React Environment Variables (Vercel Compatible)
The frontend now uses `REACT_APP_` prefixed environment variables for Vercel compatibility while maintaining `VITE_` fallbacks for local development:

```javascript
// Environment variable priority (frontend/src/services/apiClient.js)
const apiUrl = process.env.REACT_APP_API_URL || import.meta.env.VITE_API_URL;
const environment = process.env.REACT_APP_ENVIRONMENT || import.meta.env.VITE_ENVIRONMENT || import.meta.env.MODE || process.env.NODE_ENV;
```

### GitHub Secrets Required
Ensure these secrets are configured in the GitHub organization:

```bash
# Vercel Integration
VERCEL_ACCESS_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_org_id
VERCEL_PROJECT_ID_SOPHIA_PROD=new_project_id  # Set after Pulumi creates project

# API Configuration
SOPHIA_API_KEY=your_api_key
```

### Environment-Specific Configuration

#### Production (main branch)
```bash
REACT_APP_API_URL=https://api.sophia.payready.com
REACT_APP_WS_URL=wss://api.sophia.payready.com/ws
REACT_APP_ENVIRONMENT=production
```

#### Staging (develop branch)
```bash
REACT_APP_API_URL=https://api.staging.sophia.payready.com
REACT_APP_WS_URL=wss://api.staging.sophia.payready.com/ws
REACT_APP_ENVIRONMENT=staging
```

#### Development (PR branches)
```bash
REACT_APP_API_URL=https://api.dev.sophia.payready.com
REACT_APP_WS_URL=wss://api.dev.sophia.payready.com/ws
REACT_APP_ENVIRONMENT=development
```

## 📁 Local Development Setup

### 1. Environment Configuration
Create `frontend/.env.local`:

```bash
# Local Development Configuration
REACT_APP_API_URL=https://api.dev.sophia.payready.com
REACT_APP_WS_URL=wss://api.dev.sophia.payready.com/ws
REACT_APP_ENVIRONMENT=development
REACT_APP_API_KEY=sophia-dashboard-dev-key
REACT_APP_DEBUG=true
```

### 2. Development Commands
```bash
# Install dependencies
cd frontend
npm ci

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔄 GitHub Actions Integration

### Updated Workflow Features
The GitHub Actions workflow (`.github/workflows/deploy-sophia-platform.yml`) now includes:

1. **Environment Detection**: Automatic detection of production/staging/development environments
2. **React Environment Variables**: Proper `REACT_APP_` variable injection
3. **New Vercel Project Targeting**: Uses `VERCEL_PROJECT_ID_SOPHIA_PROD`
4. **Enhanced PR Comments**: Detailed deployment information with testing checklists
5. **Health Checks**: Automatic deployment verification
6. **Frontend-Only Deployments**: Option to deploy only frontend changes

### Workflow Triggers
```yaml
# Automatic triggers
push:
  branches: [main, develop]
  paths: ['frontend/**']

pull_request:
  branches: [main, develop]
  paths: ['frontend/**']

# Manual trigger with options
workflow_dispatch:
  inputs:
    deploy_frontend_only: true
```

### Deployment Flow
1. **Environment Detection**: Determines target environment based on branch
2. **Dependency Installation**: `npm ci` in frontend directory
3. **Frontend Tests**: Linting and unit tests (if enabled)
4. **Environment Variable Injection**: Sets appropriate `REACT_APP_` variables
5. **Build Process**: `npm run build` with environment-specific configuration
6. **Vercel Deployment**: Deploy to new dedicated project
7. **Health Check**: Verify deployment accessibility
8. **PR Comments**: Detailed deployment information and testing checklist

## 🧪 Testing Workflows

### Deployment Testing Checklist
When a PR is created, the GitHub Actions workflow automatically comments with this checklist:

- [ ] Dashboard loads correctly
- [ ] Chat interface connects to backend
- [ ] WebSocket connection established
- [ ] API calls return data
- [ ] Authentication works
- [ ] Mobile responsive design
- [ ] Environment variables loaded correctly
- [ ] Cross-origin requests working

### Manual Testing Commands
```bash
# Test API connectivity
curl https://api.dev.sophia.payready.com/health

# Test WebSocket (browser console)
const ws = new WebSocket('wss://api.dev.sophia.payready.com/ws');
ws.onopen = () => console.log('WebSocket connected');
```

## 🔒 Security Configuration

### Vercel Configuration (`frontend/vercel.json`)
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; connect-src 'self' https://api.sophia.payready.com https://api.staging.sophia.payready.com https://api.dev.sophia.payready.com wss://api.sophia.payready.com wss://api.staging.sophia.payready.com wss://api.dev.sophia.payready.com;"
        }
      ]
    }
  ]
}
```

### CORS Configuration
The frontend is configured to work with the following API endpoints:
- Production: `https://api.sophia.payready.com`
- Staging: `https://api.staging.sophia.payready.com`
- Development: `https://api.dev.sophia.payready.com`

## 🚀 Deployment Commands

### Manual Deployment (if needed)
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to preview
cd frontend
vercel

# Deploy to production
vercel --prod
```

### Environment-Specific Deployments
```bash
# Deploy with specific environment variables
vercel --env REACT_APP_API_URL=https://api.sophia.payready.com --prod
```

## 📊 Monitoring & Analytics

### Deployment Monitoring
- **GitHub Actions**: Monitor deployment status in Actions tab
- **Vercel Dashboard**: View deployment logs and metrics
- **Health Checks**: Automatic verification of deployment accessibility

### Performance Monitoring
- **Vercel Analytics**: Built-in performance monitoring
- **Core Web Vitals**: Automatic tracking of loading performance
- **Error Tracking**: Integration with error monitoring services

## 🔧 Troubleshooting

### Common Issues

#### 1. Environment Variables Not Loading
**Problem**: Frontend can't connect to backend
**Solution**: 
- Verify `REACT_APP_` prefixed variables in GitHub secrets
- Check Vercel project environment variables
- Ensure build process includes environment variables

#### 2. CORS Errors
**Problem**: Cross-origin requests blocked
**Solution**:
- Verify API endpoints in `vercel.json` CSP headers
- Check backend CORS configuration
- Ensure WebSocket URLs use correct protocol (wss://)

#### 3. Build Failures
**Problem**: npm run build fails
**Solution**:
- Check for TypeScript errors
- Verify all dependencies are installed
- Review build logs in GitHub Actions

#### 4. Deployment Timeouts
**Problem**: Vercel deployment times out
**Solution**:
- Check build performance
- Optimize bundle size
- Review Vercel function timeout settings

### Debug Commands
```bash
# Check environment variables
echo $REACT_APP_API_URL

# Test API connectivity
curl -I https://api.sophia.payready.com/health

# Check WebSocket connection
wscat -c wss://api.sophia.payready.com/ws

# Verify build output
npm run build && ls -la dist/
```

## 📚 Additional Resources

### Documentation Links
- [Vercel Documentation](https://vercel.com/docs)
- [React Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)

### Support Contacts
- **Frontend Issues**: Development Team
- **Deployment Issues**: DevOps Team
- **API Issues**: Backend Team

---

## ✅ Deployment Readiness Checklist

Before deploying to production, ensure:

- [ ] All GitHub secrets are configured
- [ ] New Vercel project is created by Pulumi
- [ ] Environment variables are properly set
- [ ] API endpoints are accessible
- [ ] SSL certificates are valid
- [ ] DNS configuration is correct
- [ ] Health checks are passing
- [ ] Performance metrics are acceptable
- [ ] Security headers are configured
- [ ] Error monitoring is enabled

---

**Note**: This deployment setup is designed to work seamlessly with Manus AI's Pulumi infrastructure provisioning. The GitHub Actions workflow will automatically target the new dedicated Vercel project once it's created and the `VERCEL_PROJECT_ID_SOPHIA_PROD` secret is updated.

## 🏗️ Architecture Overview

```
GitHub Repository (ai-cherry/sophia-main)
├── frontend/ (React + Vite application)
├── .github/workflows/deploy-sophia-platform.yml
└── Vercel Project: sophia-ai-frontend-prod
    ├── Production: sophia.payready.com (main branch)
    ├── Staging: staging.sophia.payready.com (develop branch)
    └── Preview: <random>.vercel.app (PR deployments)
```

## 🔧 Environment Configuration

### Environment Variables

The frontend uses the following environment variables:

| Variable | Description | Production | Staging | Development |
|----------|-------------|------------|---------|-------------|
| `VITE_API_URL` | Backend API URL | `https://api.sophia.payready.com` | `https://api.staging.sophia.payready.com` | `https://api.dev.sophia.payready.com` |
| `VITE_WS_URL` | WebSocket URL | `wss://api.sophia.payready.com/ws` | `wss://api.staging.sophia.payready.com/ws` | `wss://api.dev.sophia.payready.com/ws` |
| `VITE_ENVIRONMENT` | Environment identifier | `production` | `staging` | `development` |
| `VITE_API_KEY` | API authentication key | `sophia-prod-key` | `sophia-staging-key` | `sophia-dev-key` |

### Required GitHub Secrets

Ensure these secrets are configured in the GitHub repository:

| Secret | Description | Required |
|--------|-------------|----------|
| `VERCEL_ACCESS_TOKEN` | Vercel deployment token | ✅ |
| `VERCEL_ORG_ID` | Vercel organization ID | ✅ |
| `VERCEL_PROJECT_ID_SOPHIA_PROD` | Sophia AI production project ID | ✅ |

## 🚀 Deployment Workflows

### 1. Production Deployment

**Trigger**: Push to `main` branch with frontend changes

```yaml
# Automatic on main branch push
git push origin main

# Manual deployment
gh workflow run deploy-sophia-platform.yml \
  --field environment=prod \
  --field deploy_frontend_only=true
```

**Result**: Deploys to `https://sophia.payready.com`

### 2. Staging Deployment

**Trigger**: Push to `develop` branch with frontend changes

```yaml
# Automatic on develop branch push
git push origin develop

# Manual deployment
gh workflow run deploy-sophia-platform.yml \
  --field environment=staging \
  --field deploy_frontend_only=true
```

**Result**: Deploys to staging preview URL

### 3. Preview Deployment

**Trigger**: Pull Request to `main` or `develop` with frontend changes

```yaml
# Automatic on PR creation/update
# Creates preview deployment with unique URL
```

**Result**: Deploys to `<unique-id>.vercel.app` with PR comment

## 🛠️ Local Development Setup

### 1. Environment Configuration

Create `.env.local` in the `frontend/` directory:

```bash
# Sophia AI Frontend - Local Development
# Connect to dev backend for testing

# Backend API Configuration
VITE_API_URL=https://api.dev.sophia.payready.com
VITE_WS_URL=wss://api.dev.sophia.payready.com/ws
VITE_ENVIRONMENT=development
VITE_API_KEY=sophia-dashboard-dev-key

# Feature Flags
VITE_ENABLE_CHAT=true
VITE_ENABLE_VOICE_INPUT=false
VITE_ENABLE_FILE_UPLOAD=true
VITE_ENABLE_DEBUG_MODE=true
```

### 2. Development Commands

```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies
npm ci

# Start development server
npm run dev

# Run tests
npm run test

# Build for production
npm run build

# Preview production build
npm run preview
```

### 3. Testing Against Different Backends

#### Local Backend
```bash
# .env.local
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

#### Development Backend
```bash
# .env.local
VITE_API_URL=https://api.dev.sophia.payready.com
VITE_WS_URL=wss://api.dev.sophia.payready.com/ws
```

#### Staging Backend
```bash
# .env.local
VITE_API_URL=https://api.staging.sophia.payready.com
VITE_WS_URL=wss://api.staging.sophia.payready.com/ws
```

## 🧪 Testing Preview Deployments

### 1. Create a Pull Request

```bash
# Create feature branch
git checkout -b feature/new-dashboard-component

# Make changes to frontend
# ... edit files in frontend/ ...

# Commit and push
git add frontend/
git commit -m "Add new dashboard component"
git push origin feature/new-dashboard-component

# Create PR via GitHub UI or CLI
gh pr create --title "Add new dashboard component" --body "Description of changes"
```

### 2. Automatic Preview Deployment

The GitHub Actions workflow will:
1. Detect frontend changes in the PR
2. Build the frontend with staging environment variables
3. Deploy to a unique Vercel preview URL
4. Comment on the PR with deployment details

### 3. Testing the Preview

The PR comment will include:
- 🔗 Preview URL
- 🔧 Environment configuration
- ✅ Health check status
- 📋 Testing checklist

Example testing checklist:
- [ ] Dashboard loads correctly
- [ ] Chat interface works
- [ ] API connectivity verified
- [ ] WebSocket connection stable
- [ ] Authentication flow works
- [ ] All components render properly

## 🔍 Troubleshooting

### Common Issues

#### 1. Environment Variables Not Loading

**Problem**: API calls failing with incorrect URLs

**Solution**: 
- Verify `.env.local` exists and has correct variables
- Check that variables are prefixed with `VITE_`
- Restart development server after env changes

```bash
# Check loaded environment variables
console.log('API URL:', import.meta.env.VITE_API_URL);
console.log('Environment:', import.meta.env.VITE_ENVIRONMENT);
```

#### 2. WebSocket Connection Issues

**Problem**: Real-time features not working

**Solution**:
- Verify WebSocket URL is correct
- Check browser network tab for connection errors
- Ensure backend WebSocket endpoint is accessible

```bash
# Test WebSocket connection manually
wscat -c wss://api.dev.sophia.payready.com/ws
```

#### 3. Build Failures

**Problem**: Build fails during deployment

**Solution**:
- Check build logs in GitHub Actions
- Verify all dependencies are installed
- Test build locally

```bash
# Local build test
npm run build

# Check for TypeScript errors
npm run type-check

# Run linting
npm run lint
```

#### 4. Deployment Not Triggering

**Problem**: No deployment on push/PR

**Solution**:
- Verify changes are in `frontend/` directory
- Check GitHub Actions workflow triggers
- Ensure required secrets are configured

### Debug Commands

```bash
# Check Vercel deployment status
vercel ls --scope=<org-id>

# View deployment logs
vercel logs <deployment-url>

# Test API connectivity
curl -f https://api.dev.sophia.payready.com/health

# Check WebSocket endpoint
curl -I https://api.dev.sophia.payready.com/ws
```

## 📊 Monitoring & Analytics

### Deployment Metrics

Monitor these key metrics:
- **Build Time**: Should be < 3 minutes
- **Bundle Size**: Target < 500KB gzipped
- **First Load**: Target < 2 seconds
- **API Response**: Target < 200ms

### Health Checks

Automatic health checks verify:
- ✅ Frontend loads successfully
- ✅ API connectivity works
- ✅ WebSocket connection establishes
- ✅ Authentication flow functions

### Performance Monitoring

Use browser dev tools to monitor:
- Core Web Vitals
- Network requests
- JavaScript errors
- Console warnings

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env.local` to git
- Use different API keys per environment
- Rotate keys regularly

### Content Security Policy
- Configured in `vercel.json`
- Restricts resource loading
- Prevents XSS attacks

### HTTPS/WSS
- All production traffic uses HTTPS/WSS
- TLS 1.3 encryption
- Secure cookie settings

## 📈 Best Practices

### Development Workflow
1. Always test locally first
2. Create feature branches for changes
3. Use descriptive commit messages
4. Test preview deployments thoroughly
5. Get code review before merging

### Performance Optimization
1. Use code splitting for large components
2. Optimize images and assets
3. Implement lazy loading
4. Monitor bundle size

### Error Handling
1. Implement proper error boundaries
2. Log errors to monitoring service
3. Provide user-friendly error messages
4. Test error scenarios

## 🎯 Next Steps

After successful deployment:

1. **Configure Custom Domains**
   - Set up `sophia.payready.com` for production
   - Configure SSL certificates
   - Set up DNS records

2. **Set Up Monitoring**
   - Configure error tracking (Sentry)
   - Set up performance monitoring
   - Create alerting rules

3. **Optimize Performance**
   - Implement caching strategies
   - Optimize build process
   - Monitor Core Web Vitals

4. **Security Hardening**
   - Regular security audits
   - Dependency updates
   - Access control reviews

---

**This guide ensures your Sophia AI frontend is properly configured for the new Vercel project with production-ready deployment automation and comprehensive testing workflows.** 