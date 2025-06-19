# 🔐 ORGANIZATION SECRET MANAGEMENT - QUICK REFERENCE

## 📍 WHERE TO UPDATE SECRETS (ORGANIZATION LEVEL)

### **Primary Location: GitHub Organization Secrets**
```
URL: https://github.com/organizations/ai-cherry/settings/secrets/actions
Method: Web UI → "New organization secret" / Edit existing
Repository Access: Selected repositories → sophia-main
Auto-sync: Yes (to Pulumi ESC within minutes)
```

## 🔑 ORGANIZATION SECRET SETUP

### **For Each Secret:**
```bash
1. Go to: https://github.com/organizations/ai-cherry/settings/secrets/actions
2. Click "New organization secret"
3. Name: SECRET_NAME
4. Value: your_secret_value
5. Repository access: "Selected repositories"
6. Select: ai-cherry/sophia-main
7. Click "Add secret"
```

## 🧪 VALIDATION COMMANDS

### **Test All Secret Management**
```bash
# Run comprehensive test suite
python automated_health_check.py

# Test environment validation
python backend/core/secure_environment_validator.py
```

### **Test Specific Integrations**
```bash
# Lambda Labs connectivity test
python -c "
import asyncio, sys
sys.path.append('.')
from backend.integrations.lambda_labs_integration import LambdaLabsIntegration
async def test():
    async with LambdaLabsIntegration() as client:
        health = await client.health_check()
        print(f'Lambda Labs Status: {health[\"status\"]}')
asyncio.run(test())
"

# Pulumi ESC connectivity test
python -c "
import asyncio, sys
sys.path.append('.')
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC
async def test():
    esc = EnhancedPulumiESC()
    health = await esc.health_check()
    print(f'Pulumi ESC Status: {health[\"status\"]}')
asyncio.run(test())
"
```

## 🔑 REQUIRED ORGANIZATION SECRETS

### **Core Infrastructure**
```bash
PULUMI_ACCESS_TOKEN=your_pulumi_token
LAMBDA_LABS_API_KEY=your_lambda_labs_key
```

### **AI Services**
```bash
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

### **Business Integrations**
```bash
GONG_API_KEY=your_gong_key
GONG_API_SECRET=your_gong_secret
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_APP_TOKEN=your_slack_app_token
SLACK_SIGNING_SECRET=your_slack_secret
```

### **Deployment & Infrastructure**
```bash
VERCEL_ACCESS_TOKEN=your_vercel_token
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET=your_jwt_secret
SECRET_KEY=your_app_secret
```

## ✅ ORGANIZATION SECRET ADVANTAGES

### **Security Benefits**
- ✅ Centralized management across all ai-cherry repositories
- ✅ Granular access control (choose which repos can access)
- ✅ Organization-level audit logs and monitoring
- ✅ Better compliance with security policies
- ✅ Reduced secret duplication and management overhead

### **Management Benefits**
- ✅ Single source of truth for all organization secrets
- ✅ Easier secret rotation (update once, applies everywhere)
- ✅ Team collaboration with multiple organization admins
- ✅ Scalable for adding new repositories
- ✅ No need to duplicate secrets across repositories

## 🚀 QUICK SETUP CHECKLIST

### **1. Access Organization Secrets**
- [ ] Go to: https://github.com/organizations/ai-cherry/settings/secrets/actions
- [ ] Verify you have organization admin access

### **2. Add Core Secrets**
- [ ] LAMBDA_LABS_API_KEY (with sophia-main repository access)
- [ ] ANTHROPIC_API_KEY (with sophia-main repository access)
- [ ] PULUMI_ACCESS_TOKEN (with sophia-main repository access)

### **3. Configure Repository Access**
- [ ] For each secret: Repository access → "Selected repositories"
- [ ] Select: ai-cherry/sophia-main
- [ ] Verify access is configured correctly

### **4. Test and Validate**
- [ ] Run: `python automated_health_check.py`
- [ ] Verify: All tests pass
- [ ] Check: GitHub Actions can access secrets
- [ ] Confirm: Deployment workflows succeed

## 🔄 ORGANIZATION SECRET UPDATE WORKFLOW

```
1. Update secret in GitHub Organization Secrets UI
2. Ensure repository access includes sophia-main
3. Wait 5 minutes for auto-sync to Pulumi ESC
4. Run: python automated_health_check.py
5. Verify: All tests pass
6. Deploy: Git push triggers secure deployment with org secrets
```

## 🔍 TROUBLESHOOTING

### **If Secrets Not Available in GitHub Actions**
```bash
# Check:
1. Secret exists at organization level
2. Repository access includes "ai-cherry/sophia-main"
3. Secret name matches exactly (case-sensitive)
4. Organization permissions allow repository access
```

### **If Tests Fail**
```bash
# Run diagnostics:
python automated_health_check.py

# Check specific issues:
- Environment validation
- Secret format validation
- API connectivity
- Hardcoded secret detection
```

## 📊 MONITORING

### **Organization Audit Logs**
```
URL: https://github.com/organizations/ai-cherry/settings/audit-log
Monitor: Secret access, modifications, repository access changes
```

### **Health Monitoring**
```bash
# Automated health checks
python automated_health_check.py

# Environment validation
python backend/core/secure_environment_validator.py
```

## 🎯 SUMMARY

**Your organization-level secret management provides:**
- **Enterprise security** with centralized control
- **Simple management** with single update location
- **Better compliance** with organization policies
- **Enhanced monitoring** with audit logs
- **Team collaboration** with shared access
- **Scalable architecture** for multiple repositories

**To update any secret:**
**https://github.com/organizations/ai-cherry/settings/secrets/actions**

**Your organization secrets are now optimally configured!** 🔐✨

