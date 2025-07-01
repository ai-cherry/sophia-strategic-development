# 🚀 Sophia AI Deployment Recovery Guide

## 🚨 Emergency Deployment Recovery

This guide provides step-by-step instructions for recovering from deployment failures and manually deploying Sophia AI when automated workflows fail.

## 📋 Quick Diagnosis Checklist

### ✅ **Step 1: Identify the Problem**

**Common Deployment Failure Symptoms:**
- ❌ 95%+ deployment failure rate in Vercel
- ❌ "The pattern 'app/**/*.js' defined in functions doesn't match any Serverless Functions"
- ❌ Build fails in 2 seconds
- ❌ GitHub Actions not triggering deployments
- ❌ Old commits being deployed instead of latest

**Root Cause Analysis:**
1. **Check vercel.json configuration** - Most common issue
2. **Verify GitHub Actions secrets** - VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
3. **Confirm webhook integration** - GitHub → Vercel connection
4. **Validate file structure** - API files in correct locations

### ✅ **Step 2: Verify Current State**

```bash
# Check current repository status
git status
git log --oneline -5

# Verify vercel.json configuration
grep -A 10 '"functions"' vercel.json

# Check API files exist
ls -la api/
ls -la api/n8n/
ls -la api/mcp/
```

**Expected vercel.json functions section:**
```json
"functions": {
  "api/index.py": {
    "maxDuration": 30,
    "memory": 1024,
    "runtime": "python3.11"
  },
  "api/n8n/webhook.py": {
    "maxDuration": 60,
    "memory": 512,
    "runtime": "python3.11"
  },
  "api/mcp/index.py": {
    "maxDuration": 45,
    "memory": 768,
    "runtime": "python3.11"
  }
}
```

## 🛠️ **Manual Deployment Methods**

### **Method 1: GitHub Actions Force Deployment**

1. **Navigate to GitHub Actions:**
   ```
   https://github.com/ai-cherry/sophia-main/actions
   ```

2. **Run Force Deployment Workflow:**
   - Click "Force Vercel Deployment" workflow
   - Click "Run workflow"
   - Select "production" environment
   - Enable "Force complete rebuild"
   - Click "Run workflow"

3. **Monitor Progress:**
   - Watch the workflow execution
   - Check for validation errors
   - Verify deployment URL in output

### **Method 2: Vercel CLI Deployment**

**Prerequisites:**
```bash
# Install Vercel CLI
npm install -g vercel@latest

# Set environment variables
export VERCEL_TOKEN="your_vercel_token"
export VERCEL_ORG_ID="your_org_id"
export VERCEL_PROJECT_ID="your_project_id"
```

**Deployment Steps:**
```bash
# Navigate to project directory
cd /path/to/sophia-project

# Pull Vercel environment
vercel pull --yes --environment=production --token=$VERCEL_TOKEN

# Build project
vercel build --prod --token=$VERCEL_TOKEN

# Deploy
vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN
```

### **Method 3: Python API Script**

```bash
# Set environment variables
export VERCEL_TOKEN="your_vercel_token"
export VERCEL_ORG_ID="your_org_id"  
export VERCEL_PROJECT_ID="your_project_id"

# Run deployment script
cd sophia-project
python3 scripts/force-vercel-deployment.py
```

## 🔧 **Configuration Fixes**

### **Fix 1: Correct vercel.json Functions Pattern**

**Problem:** `"app/**/*.js"` pattern doesn't match Python API files

**Solution:**
```bash
# Edit vercel.json to use individual function definitions
# Replace any "app/**/*.js" patterns with specific Python files:
"functions": {
  "api/index.py": { ... },
  "api/n8n/webhook.py": { ... },
  "api/mcp/index.py": { ... }
}
```

### **Fix 2: Update Build Configuration**

**Problem:** Incorrect build settings in Vercel dashboard

**Required Settings:**
- **Build Command:** `cd frontend && npm run build`
- **Output Directory:** `frontend/dist`
- **Root Directory:** `frontend`
- **Framework Preset:** Parcel (or None)

### **Fix 3: Environment Variables**

**Required Variables in Vercel:**
```
VITE_SOPHIA_ENV=production
VITE_SOPHIA_API_URL=https://your-domain.vercel.app
VITE_N8N_WEBHOOK_URL=https://your-domain.vercel.app/api/n8n/webhook
VITE_MCP_SERVER_URL=https://your-domain.vercel.app/api/mcp
```

## 📊 **Monitoring and Validation**

### **Health Check Endpoints**

After deployment, test these endpoints:

```bash
# Frontend
curl -f https://your-domain.vercel.app/

# API Health
curl -f https://your-domain.vercel.app/api/health

# n8n Webhook
curl -f https://your-domain.vercel.app/api/n8n/health

# MCP Server  
curl -f https://your-domain.vercel.app/api/mcp/health
```

### **Deployment Validation Script**

```bash
#!/bin/bash
DOMAIN="your-domain.vercel.app"

echo "🔍 Validating deployment at $DOMAIN"

# Test frontend
if curl -f -s "https://$DOMAIN/" > /dev/null; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAILED"
fi

# Test API endpoints
for endpoint in "api/health" "api/n8n/health" "api/mcp/health"; do
    if curl -f -s "https://$DOMAIN/$endpoint" > /dev/null; then
        echo "✅ $endpoint: OK"
    else
        echo "⚠️  $endpoint: Not available"
    fi
done
```

## 🚨 **Emergency Procedures**

### **When All Deployments Fail**

1. **Check Vercel Status:**
   ```
   https://vercel-status.com/
   ```

2. **Verify GitHub Integration:**
   - Go to Vercel dashboard
   - Check Git repository connection
   - Reconnect if necessary

3. **Reset Vercel Project:**
   - Delete current Vercel project
   - Recreate with correct settings
   - Reconnect to GitHub repository

4. **Rollback Strategy:**
   ```bash
   # Find last working commit
   git log --oneline
   
   # Create rollback branch
   git checkout -b rollback-emergency
   git reset --hard <last_working_commit>
   git push origin rollback-emergency
   
   # Deploy rollback branch
   vercel --prod --token=$VERCEL_TOKEN
   ```

### **Contact and Escalation**

**When to Escalate:**
- Multiple deployment methods fail
- Vercel platform issues
- GitHub Actions completely broken
- Security concerns with credentials

**Escalation Steps:**
1. Document all attempted solutions
2. Gather error logs and screenshots
3. Check Vercel and GitHub status pages
4. Contact platform support if needed

## 📈 **Prevention and Monitoring**

### **Automated Monitoring Setup**

```bash
# Create monitoring script
cat > monitor-deployment.sh << 'EOF'
#!/bin/bash
DOMAIN="your-domain.vercel.app"
WEBHOOK_URL="your_slack_webhook_url"

# Check deployment health
if ! curl -f -s "https://$DOMAIN/" > /dev/null; then
    # Send alert
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🚨 Sophia AI deployment is down!"}' \
        $WEBHOOK_URL
fi
EOF

# Make executable
chmod +x monitor-deployment.sh

# Add to crontab (check every 5 minutes)
echo "*/5 * * * * /path/to/monitor-deployment.sh" | crontab -
```

### **Deployment Success Metrics**

**Key Metrics to Track:**
- Deployment success rate (target: >95%)
- Build time (target: <5 minutes)
- Time to recovery (target: <15 minutes)
- API response time (target: <200ms)

**Monitoring Tools:**
- Vercel Analytics
- GitHub Actions insights
- Custom health check scripts
- Uptime monitoring services

## 🔄 **Regular Maintenance**

### **Weekly Checks**
- [ ] Verify all deployments are successful
- [ ] Check environment variables are up to date
- [ ] Review build logs for warnings
- [ ] Test all API endpoints

### **Monthly Reviews**
- [ ] Update dependencies in requirements.txt and package.json
- [ ] Review and optimize vercel.json configuration
- [ ] Audit GitHub Actions workflows
- [ ] Update documentation

### **Quarterly Audits**
- [ ] Security scan of all credentials
- [ ] Performance optimization review
- [ ] Disaster recovery testing
- [ ] Documentation updates

---

## 📞 **Quick Reference**

**Emergency Commands:**
```bash
# Force new deployment
vercel --prod --force

# Check deployment status
vercel ls

# View deployment logs
vercel logs <deployment-url>

# Rollback to previous deployment
vercel rollback <deployment-url>
```

**Important URLs:**
- Vercel Dashboard: https://vercel.com/dashboard
- GitHub Actions: https://github.com/ai-cherry/sophia-main/actions
- Repository: https://github.com/ai-cherry/sophia-main

**Key Files:**
- `vercel.json` - Deployment configuration
- `.github/workflows/` - CI/CD workflows
- `scripts/force-vercel-deployment.py` - Manual deployment script

---

*This guide should be updated whenever deployment procedures change or new issues are discovered.*

