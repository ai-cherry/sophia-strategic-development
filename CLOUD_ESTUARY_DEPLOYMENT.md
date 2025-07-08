# Cloud-Only Estuary Flow Deployment

## 🌩️ Everything Runs in the Cloud!

No local machine required. All deployment happens via GitHub Actions or directly on Lambda Labs.

## 🚀 Option 1: GitHub Actions (Recommended)

### Trigger Deployment
```bash
# From GitHub web UI:
# Go to Actions → Deploy Estuary Flow → Run workflow

# Or via GitHub CLI (if you have it):
gh workflow run deploy-estuary-flow.yml
```

This will:
- Install flowctl on Lambda Labs
- Pull latest code from GitHub
- Load secrets from Pulumi ESC (already synced from GitHub)
- Deploy Estuary flows
- Test webhooks
- Report status to Slack

## 🖥️ Option 2: Direct SSH Deployment

### One Command Deployment
```bash
ssh ubuntu@146.235.200.1 'bash -s' < scripts/cloud-deploy-estuary.sh
```

Or if you're already SSH'd in:
```bash
ssh ubuntu@146.235.200.1

# Then run:
curl -sSL https://raw.githubusercontent.com/ai-cherry/sophia-main/main/scripts/cloud-deploy-estuary.sh | bash
```

## 🔐 Secrets Already Available

These secrets are **already in GitHub Organization** and sync to Pulumi ESC:

✅ `GONG_API_KEY` → Used as `ESTUARY_GONG_TOKEN`
✅ `GONG_WEBHOOK_SECRET` → Webhook authentication
✅ `SLACK_WEBHOOK` → Used as `ESTUARY_SLACK_TOKEN`
✅ `GITHUB_TOKEN` → Used as `ESTUARY_GITHUB_TOKEN`
✅ `REDIS_PASSWORD` → Redis authentication
✅ `SNOWFLAKE_*` → All Snowflake credentials
✅ `GRAFANA_API_KEY` → Dashboard creation

### Only Missing (Optional):
- `ESTUARY_API_KEY` - Only needed if you have an Estuary account
- `ESTUARY_API_SECRET` - Only needed if you have an Estuary account

Without these, you'll need to run `flowctl auth login` manually on Lambda Labs.

## 📊 Monitor Deployment

### Via GitHub Actions
- Go to Actions tab in GitHub
- Click on "Deploy Estuary Flow" workflow
- Watch real-time logs

### Via SSH
```bash
ssh ubuntu@146.235.200.1

# Check deployment status
cd ~/sophia-main
flowctl flows list --prefix sophia-ai/

# Check MCP server health
for port in {9000..9009}; do
  curl -s http://localhost:$port/health && echo " - Port $port ✓" || echo " - Port $port ✗"
done
```

## 🎯 What Happens Automatically

1. **Secrets Flow**:
   ```
   GitHub Org Secrets → Pulumi ESC → Lambda Labs Environment
   ```

2. **Code Flow**:
   ```
   GitHub Repository → Lambda Labs Clone → Estuary Deployment
   ```

3. **Webhook Tokens**:
   - Uses existing `GONG_WEBHOOK_SECRET` for Gong webhook auth
   - Uses existing `SLACK_WEBHOOK` for Slack webhook auth
   - Uses existing `GITHUB_TOKEN` for GitHub webhook auth

## 🧪 Test Webhooks

After deployment, test from Lambda Labs:
```bash
ssh ubuntu@146.235.200.1

# Load environment
cd ~/sophia-main
eval $(pulumi env open scoobyjava-org/default/sophia-ai-production --format=shell)

# Test Gong webhook
curl -X POST http://localhost:9009/estuary/webhook \
  -H "Authorization: Bearer ${GONG_WEBHOOK_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "type": "call_completed",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "data": {
      "call_id": "test-call-001",
      "duration": 1800,
      "sentiment": 0.75,
      "topics": ["cloud", "deployment"],
      "transcript": "Cloud deployment test"
    }
  }'
```

## 🎉 Success Indicators

✅ GitHub Action shows green checkmark
✅ Slack notification received
✅ `flowctl flows list` shows active flows
✅ Webhooks return 200 OK
✅ Grafana dashboard accessible

## 🔧 Troubleshooting

### If Estuary Auth Needed
```bash
ssh ubuntu@146.235.200.1
cd ~/sophia-main
flowctl auth login
# Follow prompts
./scripts/deploy-estuary-flow.sh
```

### Check Logs
```bash
# GitHub Action logs
gh run view

# Lambda Labs logs
ssh ubuntu@146.235.200.1
docker service logs sophia-mcp-v2_gong-v2 --tail 50
```

---

**Everything runs in the cloud - no local machine needed!** ☁️
