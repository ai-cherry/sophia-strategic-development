# Lambda Labs Quick Reference

## 🚀 Key Commands

### Chat Commands
```
# Inference
"Use Lambda serverless to [task]"
"Use cheapest model for [simple task]"
"Use most powerful model for [complex task]"

# Cost Management
"Estimate cost for [task]"
"Show Lambda Labs usage"
"What's my Lambda budget status?"
"Optimize costs for [workload]"

# Examples
"Use Lambda serverless to summarize this document"
"Estimate cost for analyzing 1000 emails"
"Show Lambda Labs usage for last 7 days"
"Optimize costs for daily report generation"
```

### CLI Commands
```bash
# Deploy MCP server
./scripts/deploy_lambda_mcp_server.sh

# Check budget
curl http://localhost:8000/api/v1/lambda-labs/budget/status

# Get usage stats
curl http://localhost:8000/api/v1/lambda-labs/usage/stats?days=7

# Test generation
curl -X POST http://localhost:8000/api/v1/lambda-labs/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!", "cost_priority": "low_cost"}'
```

## 💰 Cost Overview

| Model | Cost/1M tokens | Best For |
|-------|----------------|----------|
| llama3.1-8b | $0.07 | Simple tasks, summaries |
| llama3.1-70b | $0.35 | General purpose (default) |
| llama-4-17b | $0.88 | Complex analysis |

### Monthly Budget Examples
- **$50/month**: ~714M tokens (8B model) or ~142M tokens (70B model)
- **$100/month**: ~1.4B tokens (8B model) or ~285M tokens (70B model)
- **$1000/month**: ~14B tokens (8B model) or ~2.8B tokens (70B model)

## 🔧 Configuration

### Environment Variables
```bash
export LAMBDA_SERVERLESS_API_KEY="your-key"
export LAMBDA_DAILY_BUDGET="50"
export LAMBDA_MONTHLY_BUDGET="1000"
export SERVERLESS_RATIO="0.8"  # 80% serverless
```

### Cost Priorities
- `low_cost`: Always use cheapest model
- `balanced`: Balance cost and performance (default)
- `performance`: Prioritize quality over cost
- `latency_critical`: Use GPU for lowest latency

## 📊 Monitoring

### Key Metrics
```sql
-- Daily cost
SELECT SUM(cost_usd) FROM LAMBDA_LABS_USAGE
WHERE timestamp >= CURRENT_DATE;

-- Model distribution
SELECT model, COUNT(*), SUM(cost_usd)
FROM LAMBDA_LABS_USAGE
GROUP BY model;

-- Optimization opportunities
SELECT * FROM TABLE(IDENTIFY_COST_OPTIMIZATIONS());
```

### Dashboards
- Grafana: `http://localhost:3000/d/lambda-labs`
- Modern Stack: `AI_INSIGHTS.LAMBDA_LABS_*` tables

## 🚨 Troubleshooting

### Common Issues

**Budget Exceeded**
```bash
# Check current usage
curl http://localhost:8000/api/v1/lambda-labs/budget/status

# Adjust budget
export LAMBDA_MONTHLY_BUDGET="2000"
```

**High Latency**
```python
# Force GPU for critical tasks
result = await generate(
    prompt="...",
    force_backend="gpu"
)
```

**Model Errors**
```python
# Use fallback model
try:
    result = await generate(model="llama3.1-70b")
except:
    result = await generate(model="llama3.1-8b")
```

## 🎯 Optimization Tips

1. **Model Selection**
   - Questions/answers → 8B model
   - Summaries → 8B or 70B model
   - Analysis/reasoning → 70B or 17B model

2. **Batch Processing**
   ```python
   # Process multiple items together
   results = await batch_generate(prompts)
   ```

3. **Caching**
   ```python
   # Cache frequent responses
   if prompt in cache:
       return cache[prompt]
   ```

4. **Prompt Engineering**
   - Shorter prompts = lower cost
   - Clear instructions = better results
   - Avoid redundancy

## 📈 Expected Savings

| Current GPU Cost | Serverless Cost | Savings |
|-----------------|-----------------|---------|
| $1,000/month | $70-150/month | 85-93% |
| $5,000/month | $350-750/month | 85-93% |
| $10,000/month | $700-1,500/month | 85-93% |

## 🔗 Resources

- [Full Documentation](./06-mcp-servers/lambda_labs_unified.md)
- [Migration Guide](./04-deployment/lambda_labs_migration_guide.md)
- [API Reference](./API_DOCUMENTATION.md#lambda-labs)
- [Architecture Decision](./03-architecture/ADR-007_lambda_serverless_first.md)
