# 🚨 Sophia AI Deployment Recovery Guide

## Current Crisis Status

**Problem:** 95%+ deployment failure rate on Vercel
**Root Cause:** GitHub Actions → Vercel webhook chain broken
**Impact:** Production domain returning 404 NOT_FOUND
**Urgency:** CRITICAL - No working production deployment

## ✅ Fixes Already Implemented

### 1. vercel.json Configuration Fixed
```json
// OLD (BROKEN)
"functions": {
  "app/**/*.js": { ... }
}

// NEW (FIXED)
"functions": {
  "api/**/*.py": { ... }
}
```

### 2. Build Configuration Corrected
- **Build Command:** `cd frontend && npm run build`
- **Output Directory:** `frontend/dist`
- **Root Directory:** `frontend`

### 3. Environment Variables Migrated
- **From:** REACT_APP_* prefixes
- **To:** VITE_* prefixes (15+ variables configured)

## 🚀 IMMEDIATE RECOVERY OPTIONS

### Option 1: Manual Vercel Dashboard Deployment (RECOMMENDED)

1. **Access Vercel Dashboard**
   - Go to https://vercel.com/lynn-musils-projects/sophia-ai-frontend-dev
   - Log in as scoobyjava

2. **Force New Deployment**
   - Click "Deployments" tab
   - Click "..." menu on latest failed deployment
   - Select "Redeploy"
   - Choose "Use latest commit from main branch"

3. **Monitor Progress**
   - Watch for build duration > 2 seconds (indicates progress)
   - Look for "Building" → "Ready" status progression
   - Verify production domain serves traffic

### Option 2: GitHub Actions Workflow (AUTOMATED)

1. **Trigger New Workflow**
   - Go to https://github.com/ai-cherry/sophia-main/actions
   - Select "Fix Vercel Deployment Pipeline"
   - Click "Run workflow"
   - Select main branch and click "Run workflow"

2. **Monitor Execution**
   - Watch for green checkmarks on all jobs
   - Check deployment URL in workflow output

### Option 3: Vercel CLI (TECHNICAL)

```bash
# Install Vercel CLI
npm install -g vercel

# Authenticate (requires browser)
vercel login

# Deploy from project directory
cd /path/to/sophia-main
vercel --prod

# Monitor deployment
vercel ls
```

## 🔍 Verification Steps

### 1. Check Production Domain
```bash
curl -I https://sophia-ai-frontend-dev.vercel.app
# Should return HTTP 200 or valid response (not 404)
```

### 2. Test API Endpoints
```bash
curl https://sophia-ai-frontend-dev.vercel.app/health
curl https://sophia-ai-frontend-dev.vercel.app/api/v2/health
```

### 3. Verify Build Logs
- Check Vercel deployment logs for:
  - ✅ Functions pattern recognition
  - ✅ Frontend build success
  - ✅ API endpoints deployment

## 🛠️ Required Secrets (If Missing)

### GitHub Secrets
```
VERCEL_TOKEN=Y57oxELkt4ufdVnk2CBZ5ayi
VERCEL_ORG_ID=[Get from Vercel dashboard]
VERCEL_PROJECT_ID=prj_AtuvhI284XG3dyOWYEhvepguCjcu
```

### Vercel Environment Variables
```
VITE_SOPHIA_ENV=production
VITE_SOPHIA_API_URL=https://sophia-ai-frontend-dev.vercel.app
VITE_PORTKEY_API_KEY=[From Pulumi ESC]
VITE_N8N_WEBHOOK_URL=[From n8n instance]
[... 15+ additional variables]
```

## 🎯 Success Indicators

### Deployment Success
- ✅ Build duration > 30 seconds (not 2 seconds)
- ✅ Status: "Ready" (not "Error")
- ✅ Production domain serves content
- ✅ API endpoints respond correctly

### Long-term Health
- ✅ GitHub Actions trigger on commits
- ✅ Automatic deployments work
- ✅ Environment variables sync properly
- ✅ Monitoring and alerts active

## 🚨 Emergency Contacts

### If All Options Fail
1. **Check Vercel Status:** https://vercel-status.com
2. **Review GitHub Actions:** Look for workflow failures
3. **Validate Repository:** Ensure latest commits are pushed
4. **Contact Support:** Vercel support with project ID

## 📋 Post-Recovery Checklist

- [ ] Production domain serving traffic
- [ ] API endpoints responding
- [ ] Environment variables configured
- [ ] GitHub Actions triggering properly
- [ ] Monitoring systems active
- [ ] Documentation updated
- [ ] Team notified of resolution

---

**Last Updated:** July 1, 2025
**Status:** CRITICAL - Immediate action required
**Next Review:** After successful deployment

