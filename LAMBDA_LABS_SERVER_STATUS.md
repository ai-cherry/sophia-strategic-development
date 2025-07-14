# Lambda Labs Server Configuration Update

**Date:** December 2024

## 🖥️ Current Lambda Labs Servers

| Name | IP Address | GPU Type | Region | Purpose |
|------|------------|----------|---------|---------|
| sophia-production-instance | **104.171.202.103** | gpu_1x_rtx6000 | us-south-1 | **Production (Use This!)** |
| sophia-ai-core | 192.222.58.232 | gpu_1x_gh200 | us-east-3 | High-performance GPU |
| sophia-mcp-orchestrator | 104.171.202.117 | gpu_1x_a6000 | us-south-1 | MCP servers |
| sophia-data-pipeline | 104.171.202.134 | gpu_1x_a100 | us-south-1 | Data processing |
| sophia-development | 155.248.194.183 | gpu_1x_a10 | us-west-1 | Development |

## 🚨 Current Issues

1. **DNS Mismatch**: 
   - Domain `sophia-intel.ai` points to → `192.222.58.232` (sophia-ai-core)
   - But SSH is timing out to that server
   - Deployment scripts updated to use → `104.171.202.103` (sophia-production-instance)

2. **Documentation Drift**:
   - You already migrated from Snowflake to Weaviate days/weeks ago
   - But documentation still said "NEVER use Weaviate"
   - Now fixed in System Handbook

## 🔧 What Needs to Happen

### Option 1: Use sophia-production-instance (Recommended)
```bash
# Scripts already updated to use:
SERVER_IP="104.171.202.103"

# Update DNS in Namecheap:
sophia-intel.ai → 104.171.202.103
api.sophia-intel.ai → 104.171.202.103
webhooks.sophia-intel.ai → 104.171.202.103
```

### Option 2: Fix SSH to sophia-ai-core
If you prefer to use the GH200 GPU server (192.222.58.232):
1. Check if SSH is enabled on that server
2. Check security group/firewall rules
3. Verify the server is running

## 📝 Updated Scripts

Both deployment scripts now use the correct server:
- `scripts/deploy_sophia_production_real.sh` → Uses 104.171.202.103
- `scripts/verify_and_fix_deployment.py` → Uses 104.171.202.103

## 🚀 Next Steps

1. **Test SSH Connection**:
   ```bash
   ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.103
   ```

2. **If SSH Works**, run deployment:
   ```bash
   ./scripts/deploy_sophia_production_real.sh
   ```

3. **Update DNS** (if you want domain to match):
   - Log into Namecheap
   - Change A records to point to 104.171.202.103

## 💡 Server Recommendations

- **Production**: Use `sophia-production-instance` (104.171.202.103)
- **MCP Servers**: Could run on `sophia-mcp-orchestrator` (104.171.202.117)
- **Data Processing**: Use `sophia-data-pipeline` (104.171.202.134) for heavy ETL
- **Development**: Use `sophia-development` (155.248.194.183) for testing

The GH200 server (192.222.58.232) has the most powerful GPU but seems to have connectivity issues from your location. 