# Estuary Flow Deployment Guide

## 🚀 Quick Start

### Step 1: Set up Estuary on Lambda Labs
```bash
# Run from your local machine
./scripts/setup-estuary-lambda-labs.sh
```

This will:
- Install flowctl CLI on Lambda Labs
- Copy all Estuary configurations
- Set up environment scripts
- Create Grafana dashboard

### Step 2: Add Secrets to GitHub Organization

Go to https://github.com/organizations/ai-cherry/settings/secrets/actions and add:

- `ESTUARY_API_KEY` - Your Estuary API key
- `ESTUARY_API_SECRET` - Your Estuary API secret
- `ESTUARY_GONG_TOKEN` - Random secure token for Gong webhook
- `ESTUARY_SLACK_TOKEN` - Random secure token for Slack webhook
- `ESTUARY_GITHUB_TOKEN` - Random secure token for GitHub webhook
- `REDIS_PASSWORD` - Redis password (if not already set)
- `GRAFANA_API_KEY` - Grafana API key for dashboard creation

### Step 3: Sync Secrets to Pulumi ESC
```bash
# Trigger GitHub Actions to sync secrets
gh workflow run sync_secrets.yml
```

### Step 4: Deploy Estuary Flows on Lambda Labs
```bash
# SSH to Lambda Labs
ssh ubuntu@146.235.200.1

# Navigate to project
cd ~/sophia-ai

# Load environment (after Pulumi ESC sync)
source setup-estuary-env.sh

# Authenticate with Estuary
flowctl auth login

# Deploy all flows
./deploy-estuary-flow.sh
```

### Step 5: Verify Deployment
```bash
# On Lambda Labs
flowctl flows list --prefix sophia-ai/

# Expected output:
# sophia-ai/gong-calls          collection    active
# sophia-ai/slack-messages      collection    active
# sophia-ai/github-events       collection    active
# sophia-ai/gong-calls-enriched derivation    active
# sophia-ai/redis-hot-cache     materialization active
# sophia-ai/snowflake-analytics materialization active
```

### Step 6: Test Webhook Integration
```bash
# Test Gong webhook (from Lambda Labs)
curl -X POST http://localhost:9009/estuary/webhook \
  -H "Authorization: Bearer ${ESTUARY_GONG_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "type": "call_completed",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "data": {
      "call_id": "test-call-001",
      "duration": 1800,
      "sentiment": 0.75,
      "topics": ["pricing", "features"],
      "transcript": "Test call transcript"
    }
  }'

# Expected: {"status":"processed","event_id":"test-001"}
```

### Step 7: Monitor in Grafana
1. Open http://146.235.200.1:3000
2. Navigate to Dashboards → Estuary Flow - Sophia AI
3. Monitor:
   - Flow lag (should be < 5 seconds)
   - Error rates (should be 0)
   - Throughput metrics

## 📊 Monitoring Commands

### Check Flow Status
```bash
# On Lambda Labs
flowctl flows list --prefix sophia-ai/ --status all
```

### View Flow Logs
```bash
# Follow logs for specific flow
flowctl flows logs --follow sophia-ai/gong-calls

# View recent errors
flowctl flows logs sophia-ai/gong-calls --level error --since 1h
```

### Check Materialization Status
```bash
# Redis cache status
flowctl materializations status sophia-ai/redis-hot-cache

# Snowflake status
flowctl materializations status sophia-ai/snowflake-analytics
```

## 🔧 Troubleshooting

### Flow Not Starting
```bash
# Check for validation errors
flowctl catalog test --source config/estuary/gong_v2_collection.yaml

# Force restart
flowctl flows restart sophia-ai/gong-calls
```

### Webhook Not Working
1. Check MCP server logs:
   ```bash
   docker service logs sophia-mcp-v2_gong-v2
   ```

2. Verify token matches:
   ```bash
   echo $ESTUARY_GONG_TOKEN
   ```

3. Test connectivity:
   ```bash
   curl http://localhost:9009/estuary/status
   ```

### High Lag
1. Check derivation performance:
   ```bash
   flowctl flows stats sophia-ai/gong-calls-enriched
   ```

2. Scale up if needed:
   ```bash
   flowctl flows update sophia-ai/gong-calls-enriched --shards 2
   ```

## 🎯 Success Criteria

✅ All flows show "active" status
✅ Webhooks return 200 OK
✅ Lag < 5 seconds in Grafana
✅ No errors in last hour
✅ Data appearing in Redis/Snowflake

## 📞 Support

- Estuary Docs: https://docs.estuary.dev
- Sophia AI Docs: `docs/05-integrations/ESTUARY_FLOW_GUIDE.md`
- Slack: #data-pipelines

---

**Ready to stream real-time data!** 🌊 