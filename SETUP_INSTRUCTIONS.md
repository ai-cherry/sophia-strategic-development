# Sophia AI - Setup Instructions

## 🎯 **PERMANENT SOLUTION: Zero Manual Secret Management**

**IMPORTANT**: Sophia AI now uses a **PERMANENT GitHub Organization Secrets → Pulumi ESC** solution. You no longer need to manually manage `.env` files or configure secrets locally.

**📋 Prerequisites**: Ensure you have access to the [ai-cherry GitHub organization](https://github.com/ai-cherry) where all secrets are managed centrally.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Access to [ai-cherry GitHub organization](https://github.com/ai-cherry)
- Pulumi CLI installed

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# Set up Pulumi organization
export PULUMI_ORG=scoobyjava-org

# Run the permanent solution setup (one-time)
python scripts/setup_permanent_secrets_solution.py
```

### 3. Verify Setup

```bash
# Test the permanent solution
python scripts/test_permanent_solution.py

# Start the backend (automatically loads secrets from ESC)
python backend/main.py

# Start the frontend
cd frontend && npm run dev
```

## 🔐 **SECRET MANAGEMENT - PERMANENT SOLUTION**

### **How It Works**

```
GitHub Organization Secrets (ai-cherry)
           ↓
    GitHub Actions (automatic sync)
           ↓
    Pulumi ESC Environments
           ↓
    Sophia AI Backend (automatic loading)
```

### **Required GitHub Organization Secrets**

All secrets are managed in the [ai-cherry GitHub organization](https://github.com/ai-cherry/settings/secrets/actions):

#### **Infrastructure Secrets**
- `PULUMI_ACCESS_TOKEN` - Pulumi Cloud access token
- `PULUMI_ORG` - Set to `scoobyjava-org`

#### **AI Service Secrets**
- `OPENAI_API_KEY` - OpenAI API key (starts with `sk-`)
- `ANTHROPIC_API_KEY` - Anthropic Claude API key

#### **Business Integration Secrets**
- `GONG_ACCESS_KEY` - Gong API access key
- `GONG_CLIENT_SECRET` - Gong API client secret
- `GONG_URL` - Your Gong instance URL
- `HUBSPOT_API_TOKEN` - HubSpot API token
- `SLACK_BOT_TOKEN` - Slack bot token (starts with `xoxb-`)

#### **Data Infrastructure Secrets**
- `SNOWFLAKE_ACCOUNT` - Snowflake account identifier
- `SNOWFLAKE_USER` - Snowflake username
- `SNOWFLAKE_PASSWORD` - Snowflake password
- `PINECONE_API_KEY` - Pinecone vector database API key

#### **Cloud Service Secrets**
- `LAMBDA_LABS_API_KEY` - Lambda Labs GPU compute API key
- `VERCEL_ACCESS_TOKEN` - Vercel deployment token

### **✅ What You DON'T Need to Do Anymore**
- ❌ Create or manage `.env` files
- ❌ Manually configure environment variables
- ❌ Share API keys via chat/email
- ❌ Update local configurations
- ❌ Worry about exposed credentials

### **✅ What Happens Automatically**
- ✅ Secrets sync from GitHub org to Pulumi ESC
- ✅ Backend automatically loads from ESC
- ✅ GitHub Actions use organization secrets
- ✅ All deployments use centralized secrets
- ✅ Secret rotation via GitHub org updates

## 🧪 **Testing the Setup**

### **Comprehensive Testing**
```bash
# Run all security and functionality tests
python scripts/test_permanent_solution.py
```

### **Backend Testing**
```bash
# Test backend with automatic secret loading
export PULUMI_ORG=scoobyjava-org
python backend/main.py

# Check health endpoint
curl http://localhost:8000/health
```

### **Frontend Testing**
```bash
# Start frontend (no secrets needed)
cd frontend
npm install
npm run dev

# Access at http://localhost:5173
```

## 🏗️ **MCP Server Management**

### **Starting MCP Servers**
```bash
# MCP servers automatically use ESC secrets
docker-compose -f docker-compose.mcp.yml up -d
```

### **Checking MCP Server Status**
```bash
# Check all MCP servers
docker-compose -f docker-compose.mcp.yml ps

# Test specific server
curl http://localhost:8000/health
```

## 🔧 **Development Workflow**

### **For New Developers**
1. **Clone repository**: No secret setup required
2. **Set PULUMI_ORG**: `export PULUMI_ORG=scoobyjava-org`
3. **Start backend**: Automatically loads all secrets
4. **Start developing**: All integrations work immediately

### **For Operations**
1. **Update secrets**: Change values in GitHub organization secrets
2. **Automatic sync**: GitHub Actions syncs to Pulumi ESC
3. **Restart services**: Backend picks up new secrets automatically

### **For Secret Rotation**
1. **Update in GitHub org**: Change secret value in organization settings
2. **Automatic deployment**: Next deployment uses new secrets
3. **Zero downtime**: Seamless secret updates

## 📋 **Troubleshooting**

### **"Secret not found" errors**
- **Cause**: Secret not set in GitHub organization
- **Fix**: Add secret at [GitHub organization secrets](https://github.com/ai-cherry/settings/secrets/actions)

### **"Pulumi ESC access denied"**
- **Cause**: Invalid `PULUMI_ACCESS_TOKEN`
- **Fix**: Update token in GitHub organization secrets

### **"Backend can't find secrets"**
- **Cause**: ESC sync failed
- **Fix**: Check GitHub Actions workflow logs, re-run sync

### **Local development issues**
```bash
# Verify Pulumi access
export PULUMI_ORG=scoobyjava-org
pulumi whoami

# Test ESC access
pulumi env ls

# Check environment
pulumi env open scoobyjava-org/default/sophia-ai-production
```

## 📚 **Documentation References**

- **Permanent Solution Guide**: `PERMANENT_GITHUB_ORG_SECRETS_SOLUTION.md`
- **Setup Success Report**: `PERMANENT_SOLUTION_SUCCESS_REPORT.md`
- **Pulumi Cloud Setup**: `PULUMI_CLOUD_SETUP_GUIDE.md`
- **Security Testing**: `scripts/test_permanent_solution.py`

## 🎉 **Success Indicators**

When everything is working correctly:
- ✅ Backend starts without credential errors
- ✅ All API integrations work
- ✅ MCP servers connect successfully
- ✅ GitHub Actions workflows pass
- ✅ No manual secret management needed

---

## 🔒 **SECURITY GUARANTEE**

The permanent solution ensures:
- **Zero exposed credentials** in the repository
- **Centralized secret management** via GitHub organization
- **Automatic secret synchronization** across all environments
- **Comprehensive audit trail** for all secret access
- **Enterprise-grade security** with encrypted storage

**🎯 RESULT: PERMANENT SOLUTION - NO MORE MANUAL SECRET MANAGEMENT EVER!**
