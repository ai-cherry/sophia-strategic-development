# Lambda Labs Migration Guide

## Overview

This guide helps you migrate Sophia AI from GPU-only infrastructure to the Lambda Labs serverless-first hybrid architecture, achieving 85-93% cost reduction.

## Pre-Migration Checklist

- [ ] Lambda Labs API key obtained
- [ ] Current GPU costs documented
- [ ] Backup of current configuration
- [ ] Test environment available
- [ ] Monitoring dashboards accessible
- [ ] Team notified of migration

## Migration Phases

### Phase 1: Foundation (Week 1)

#### 1.1 Deploy Core Services

```bash
# Clone and checkout latest
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Deploy MCP server
./scripts/deploy_lambda_mcp_server.sh

# Verify deployment
docker ps | grep lambda-labs-mcp
```

#### 1.2 Configure Environment

```bash
# Set environment variables
export LAMBDA_SERVERLESS_API_KEY="your-api-key"
export LAMBDA_DAILY_BUDGET="50"
export LAMBDA_MONTHLY_BUDGET="1000"
export SERVERLESS_RATIO="0.2"  # Start with 20% serverless

# Add to shell profile
echo 'export LAMBDA_SERVERLESS_API_KEY="your-api-key"' >> ~/.bashrc
echo 'export SERVERLESS_RATIO="0.2"' >> ~/.bashrc
```

#### 1.3 Initialize Database

```sql
-- Run in Snowflake
USE ROLE SOPHIA_ADMIN_ROLE;
USE DATABASE SOPHIA_AI;
USE SCHEMA AI_INSIGHTS;

-- Execute Lambda Labs schema
@infrastructure/snowflake_setup/lambda_labs_analytics.sql
```

### Phase 2: Integration (Week 2)

#### 2.1 Update Chat Service

```python
# In your main application
from backend.services.enhanced_unified_chat_service import EnhancedUnifiedChatService

# Replace existing chat service
chat_service = EnhancedUnifiedChatService()
```

#### 2.2 Add API Routes

```python
# In your FastAPI app
from backend.api.lambda_labs_routes import router as lambda_router

app.include_router(lambda_router)
```

#### 2.3 Test Integration

```bash
# Test serverless endpoint
curl -X POST http://localhost:8000/api/v1/lambda-labs/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, Lambda Labs!"}'

# Check usage stats
curl http://localhost:8000/api/v1/lambda-labs/usage/stats
```

### Phase 3: Gradual Rollout (Week 3)

#### 3.1 Increase Serverless Ratio

```bash
# Day 1: 20% serverless
export SERVERLESS_RATIO="0.2"

# Day 3: 40% serverless
export SERVERLESS_RATIO="0.4"

# Day 5: 60% serverless
export SERVERLESS_RATIO="0.6"

# Day 7: 80% serverless (target)
export SERVERLESS_RATIO="0.8"
```

#### 3.2 Monitor Performance

```sql
-- Check model performance
SELECT * FROM LAMBDA_LABS_MODEL_PERFORMANCE;

-- Find optimization opportunities
SELECT * FROM TABLE(IDENTIFY_COST_OPTIMIZATIONS());
```

#### 3.3 Adjust Routing

```python
# Force specific backend for testing
result = await router.generate(
    messages=messages,
    force_backend="serverless"  # or "gpu"
)
```

### Phase 4: Optimization (Week 4)

#### 4.1 Analyze Usage Patterns

```python
# Get detailed usage report
python scripts/analyze_lambda_performance.py

# Review optimization recommendations
python scripts/find_lambda_optimizations.py
```

#### 4.2 Implement Optimizations

1. **Model Selection**
   ```python
   # Simple tasks → Small model
   if task_complexity == "simple":
       model = "llama3.1-8b-instruct"
   ```

2. **Batch Processing**
   ```python
   # Group similar requests
   batch_results = await process_batch(requests)
   ```

3. **Caching**
   ```python
   # Cache frequent completions
   cached_result = cache.get(prompt_hash)
   if not cached_result:
       result = await generate(prompt)
       cache.set(prompt_hash, result)
   ```

#### 4.3 Scale Down GPU Infrastructure

```bash
# Reduce GPU instances from 8 to 2
pulumi config set gpu-instances 2
pulumi up

# Update load balancer
kubectl scale deployment gpu-inference --replicas=2
```

## Rollback Plan

If issues arise, you can quickly rollback:

### Immediate Rollback

```bash
# Force all traffic to GPU
export SERVERLESS_RATIO="0.0"

# Or disable Lambda Labs entirely
export DISABLE_LAMBDA_LABS="true"
```

### Gradual Rollback

```bash
# Reduce serverless traffic
export SERVERLESS_RATIO="0.4"  # From 0.8 to 0.4

# Monitor for 24 hours
# If stable, continue reduction
export SERVERLESS_RATIO="0.2"
```

### Full Rollback

```bash
# Restore previous configuration
git checkout main~1 -- config/
git checkout main~1 -- backend/services/

# Restart services
docker-compose restart
```

## Validation Steps

### 1. Functional Testing

```python
# Test all models
models = [
    "llama3.1-8b-instruct",
    "llama3.1-70b-instruct-fp8",
    "llama-4-maverick-17b-128e-instruct-fp8"
]

for model in models:
    result = await test_model(model)
    assert result["success"]
```

### 2. Performance Testing

```bash
# Run load test
python scripts/lambda_load_test.py \
  --concurrent-users 50 \
  --duration 300 \
  --backend mixed
```

### 3. Cost Validation

```sql
-- Compare costs before/after
WITH cost_comparison AS (
  SELECT
    DATE_TRUNC('day', timestamp) as date,
    SUM(CASE WHEN backend = 'gpu' THEN cost_usd END) as gpu_cost,
    SUM(CASE WHEN backend = 'serverless' THEN cost_usd END) as serverless_cost,
    COUNT(*) as total_requests
  FROM LAMBDA_LABS_USAGE
  GROUP BY 1
)
SELECT
  date,
  gpu_cost,
  serverless_cost,
  (gpu_cost + serverless_cost) as total_cost,
  (1 - (serverless_cost / NULLIF(gpu_cost, 0))) * 100 as savings_percent
FROM cost_comparison
ORDER BY date DESC;
```

## Common Issues

### Issue: High Latency on Serverless

**Symptoms**: Response times > 2 seconds

**Solution**:
1. Check model selection
2. Reduce prompt size
3. Enable streaming
4. Use GPU for latency-critical tasks

### Issue: Budget Alerts

**Symptoms**: Frequent budget warnings

**Solution**:
1. Review usage patterns
2. Optimize model selection
3. Implement caching
4. Adjust budget limits

### Issue: Model Errors

**Symptoms**: "Model not available" errors

**Solution**:
1. Check API key validity
2. Verify model names
3. Implement retry logic
4. Use fallback models

## Success Metrics

Track these metrics to validate migration success:

1. **Cost Reduction**
   - Target: 85-93% reduction
   - Measure: Daily/monthly spend

2. **Performance**
   - P50 latency < 500ms
   - P95 latency < 2s
   - P99 latency < 5s

3. **Reliability**
   - Error rate < 1%
   - Availability > 99.9%

4. **Usage Distribution**
   - Serverless: 80%
   - GPU: 20%

## Post-Migration

### 1. Documentation

Update:
- Architecture diagrams
- API documentation
- Runbooks
- Cost projections

### 2. Training

Provide team training on:
- New chat commands
- Cost optimization
- Model selection
- Monitoring tools

### 3. Continuous Optimization

Schedule:
- Weekly usage reviews
- Monthly cost analysis
- Quarterly model evaluation
- Annual architecture review

## Support

During migration:
- Slack: #lambda-migration
- On-call: lambda-oncall@sophia-ai.com
- Documentation: This guide
- Escalation: CTO/VP Engineering
