# 🚀 Manual Lambda Labs Deployment Guide

## SSH Key Setup Required

Your SSH public key needs to be added to each Lambda Labs server.

### Step 1: Add SSH Key to Lambda Labs Console
1. Go to Lambda Labs console: https://cloud.lambdalabs.com/
2. Navigate to each instance
3. Add your SSH public key to authorized_keys

### Step 2: Alternative - Use Lambda Labs SSH Key
If you have the Lambda Labs private key, use it:

```bash
# Copy your Lambda Labs private key to ~/.ssh/
cp /path/to/lambda-labs-key ~/.ssh/lambda_labs_key
chmod 600 ~/.ssh/lambda_labs_key

# Update SSH config to use Lambda Labs key
ssh-add ~/.ssh/lambda_labs_key
```

### Step 3: Manual Deployment Commands

Once SSH access is working, run these commands:

```bash
# Deploy primary server
ssh root@192.222.58.232 'bash -s' < scripts/deploy_primary_server.sh

# Deploy MCP orchestrator  
ssh root@104.171.202.117 'bash -s' < scripts/deploy_mcp_server.sh

# Setup SSL certificates
ssh root@192.222.58.232 'bash -s' < scripts/setup_ssl.sh

# Setup monitoring
ssh root@192.222.58.232 'bash -s' < scripts/setup_monitoring.sh
```

### Step 4: Test Deployment

```bash
# Test endpoints
curl -s https://sophia-intel.ai/health
curl -s https://api.sophia-intel.ai/health
curl -s https://app.sophia-intel.ai/health
```

## Alternative: Direct Server Access

If SSH keys are complex, you can also:

1. SSH directly to each server
2. Clone the repository: `git clone https://github.com/ai-cherry/sophia-main.git`
3. Run deployment scripts locally on each server

### Primary Server (192.222.58.232):
```bash
ssh root@192.222.58.232
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
bash scripts/deploy_primary_server.sh
```

### MCP Server (104.171.202.117):
```bash
ssh root@104.171.202.117
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
bash scripts/deploy_mcp_server.sh
```