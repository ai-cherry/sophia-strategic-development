# Lambda Labs Serverless Deployment Guide

## Overview
This guide covers deploying and managing Sophia AI's Lambda Labs serverless-first infrastructure.

## Architecture
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Unified Chat   │────▶│  Hybrid Router   │────▶│   Serverless    │
│    Service      │     │  (80/20 split)   │     │      API        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                            │
                               │                            │
                               ▼                            ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │   GPU Backend    │     │  Cost Monitor   │
                        │  (2 instances)   │     │   & Alerts      │
                        └──────────────────┘     └─────────────────┘
```

## Prerequisites
- Lambda Labs API key (serverless access)
- AWS account for monitoring infrastructure
- Pulumi account for IaC
- Docker for MCP server deployment

## Configuration

### Environment Variables
```bash
# Lambda Labs
export LAMBDA_SERVERLESS_API_KEY="your-api-key"
export LAMBDA_DAILY_BUDGET="50"
export LAMBDA_MONTHLY_BUDGET="1000"

# Monitoring
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."

# Routing
export SERVERLESS_RATIO="0.8"  # 80% to serverless
```

### Pulumi Configuration
```bash
cd infrastructure/pulumi
pulumi config set lambdaApiKey --secret "your-api-key"
pulumi config set slackWebhook --secret "webhook-url"
pulumi config set environment production
```

## Deployment Steps

### 1. Deploy AWS Infrastructure
```bash
cd infrastructure/pulumi
npm install
pulumi up
```

This creates:
- S3 bucket for usage backup
- DynamoDB table for real-time tracking
- Lambda function for cost monitoring
- CloudWatch dashboard

### 2. Deploy MCP Server
```bash
cd mcp-servers/lambda_labs_unified
docker build -t lambda-labs-mcp .
docker push scoobyjava15/lambda-labs-mcp:latest
```

Update `cursor_mcp_config.json`:
```json
{
  "lambda-labs": {
    "command": "docker",
    "args": ["run", "--rm", "-i", "scoobyjava15/lambda-labs-mcp:latest"],
    "env": {
      "LAMBDA_SERVERLESS_API_KEY": "${LAMBDA_SERVERLESS_API_KEY}"
    }
  }
}
```

### 3. Initialize Database
```sql
-- Run in Snowflake
USE ROLE SOPHIA_ADMIN_ROLE;
USE DATABASE SOPHIA_AI;
USE SCHEMA AI_INSIGHTS;

-- Execute Lambda Labs analytics schema
@infrastructure/snowflake_setup/lambda_labs_analytics.sql
```

### 4. Configure Routing
Edit `backend/services/unified_chat_service.py`:
```python
# Add Lambda Labs integration
from backend.services.lambda_labs_chat_integration import LambdaLabsChatIntegration

self.lambda_integration = LambdaLabsChatIntegration()
```

## Usage

### Natural Language Commands
In Sophia AI chat:
- "Use Lambda serverless to analyze this report"
- "Estimate cost for processing 1000 documents"
- "Show Lambda Labs usage for last 7 days"
- "Optimize costs for bulk email generation"

### Programmatic Access
```python
from infrastructure.services.lambda_labs_hybrid_router import LambdaLabsHybridRouter

router = LambdaLabsHybridRouter()
result = await router.generate(
    messages=[{"role": "user", "content": "Hello"}],
    cost_priority="low_cost"
)
```

## Monitoring

### Cost Tracking
- Real-time: DynamoDB table
- Historical: Snowflake AI_INSIGHTS.LAMBDA_LABS_USAGE
- Alerts: Slack notifications at 80% budget

### Performance Metrics
- CloudWatch dashboard: `sophia-ai-lambda-labs-production`
- Grafana dashboard: `Lambda Labs Hybrid Performance`
- Snowflake view: `LAMBDA_LABS_MODEL_PERFORMANCE`

### Budget Enforcement
```sql
-- Check current spend
CALL CHECK_LAMBDA_BUDGET_ALERTS();

-- Find optimization opportunities
SELECT * FROM TABLE(IDENTIFY_COST_OPTIMIZATIONS());
```

## Troubleshooting

### High Latency
1. Check backend distribution
2. Verify GPU instances are healthy
3. Review complexity analyzer accuracy

### Budget Overruns
1. Run cost optimization analysis
2. Adjust serverless ratio
3. Review model selection logic

### API Errors
1. Verify API key is valid
2. Check rate limits
3. Review retry logs

## Best Practices

### Cost Optimization
- Use smallest model that meets quality requirements
- Batch similar requests
- Cache frequent completions
- Schedule non-urgent tasks for off-peak

### Performance
- Pre-warm GPU instances for known peak times
- Use streaming for long responses
- Implement request coalescing

### Reliability
- Monitor both backends continuously
- Test fallback scenarios regularly
- Keep usage data backed up
- Set conservative budget alerts
