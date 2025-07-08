# Lambda Labs Unified MCP Server

## Overview

The Lambda Labs Unified MCP Server provides natural language control over Lambda Labs serverless infrastructure, enabling cost-effective AI inference with automatic optimization.

## Features

- **Serverless Inference**: Access to multiple LLaMA models with pay-per-token pricing
- **Cost Monitoring**: Real-time budget tracking and alerts
- **Intelligent Routing**: Automatic selection between serverless and GPU backends
- **Natural Language Control**: Simple commands for complex infrastructure operations

## Installation

### Docker Deployment

```bash
# Deploy the MCP server
./scripts/deploy_lambda_mcp_server.sh

# Verify deployment
docker ps | grep lambda-labs-mcp
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/mcp-servers/lambda-labs-deployment.yaml

# Check status
kubectl get pods -n sophia-ai -l app=lambda-labs-mcp
```

## Configuration

### Environment Variables

- `LAMBDA_SERVERLESS_API_KEY`: Your Lambda Labs API key (required)
- `LAMBDA_DAILY_BUDGET`: Daily spending limit in USD (default: 50)
- `LAMBDA_MONTHLY_BUDGET`: Monthly spending limit in USD (default: 1000)
- `SLACK_WEBHOOK_URL`: Webhook for budget alerts (optional)

### Cursor Integration

The MCP server is automatically configured in `config/cursor_mcp_config.json`:

```json
{
  "lambda-labs": {
    "command": "docker",
    "args": [
      "run", "--rm", "-i",
      "-v", "${HOME}/.sophia/lambda:/app/data",
      "-e", "LAMBDA_SERVERLESS_API_KEY=${LAMBDA_SERVERLESS_API_KEY}",
      "scoobyjava15/lambda-labs-mcp:latest"
    ]
  }
}
```

## Usage

### Natural Language Commands

In Sophia AI chat, you can use commands like:

#### Inference
```
Use Lambda serverless to summarize this document
Use the cheapest model to generate a simple greeting
Use the most powerful model for complex analysis
```

#### Cost Estimation
```
Estimate cost for processing this 10-page document
How much would it cost to analyze 1000 customer reviews?
What's the cheapest way to generate product descriptions?
```

#### Usage Monitoring
```
Show Lambda Labs usage for the last 7 days
What's my current Lambda Labs budget status?
How much have we spent on Lambda Labs this month?
```

#### Optimization
```
Optimize costs for bulk email generation
What model should I use for simple summaries?
How can I reduce Lambda Labs costs?
```

### Programmatic Access

The MCP server exposes the following tools:

#### `invoke_serverless`
Invoke Lambda Labs serverless inference with intelligent model selection.

**Parameters:**
- `prompt`: The prompt to send to the model
- `model`: Optional specific model to use
- `cost_priority`: One of 'low_cost', 'balanced', 'performance', 'latency_critical'
- `max_tokens`: Maximum tokens to generate

**Example:**
```python
result = await mcp.invoke_tool(
    "invoke_serverless",
    {
        "prompt": "Explain quantum computing",
        "cost_priority": "balanced",
        "max_tokens": 500
    }
)
```

#### `estimate_cost`
Estimate the cost for processing a prompt with a specific model.

**Parameters:**
- `prompt`: The prompt to estimate cost for
- `model`: The model to use for estimation

**Example:**
```python
estimate = await mcp.invoke_tool(
    "estimate_cost",
    {
        "prompt": "Write a 500-word essay",
        "model": "llama3.1-70b-instruct-fp8"
    }
)
```

#### `get_usage_stats`
Get Lambda Labs usage statistics and budget status.

**Parameters:**
- `days`: Number of days to look back (default: 30)

**Example:**
```python
stats = await mcp.invoke_tool(
    "get_usage_stats",
    {"days": 7}
)
```

#### `optimize_costs`
Get cost optimization recommendations for a specific workload.

**Parameters:**
- `workload_description`: Description of the workload to optimize

**Example:**
```python
recommendations = await mcp.invoke_tool(
    "optimize_costs",
    {
        "workload_description": "Daily summarization of 100 news articles"
    }
)
```

## Models

### Available Models

1. **llama3.1-8b-instruct**
   - Cost: $0.07 per million tokens
   - Use for: Simple tasks, summaries, basic Q&A
   - Context: 8,192 tokens

2. **llama3.1-70b-instruct-fp8** (default)
   - Cost: $0.35 per million tokens
   - Use for: General purpose, balanced performance
   - Context: 8,192 tokens

3. **llama-4-maverick-17b-128e-instruct-fp8**
   - Cost: $0.88 per million tokens
   - Use for: Complex analysis, detailed reasoning
   - Context: 8,192 tokens

### Model Selection Strategy

The MCP server automatically selects models based on:
- Query complexity
- Cost priority setting
- User preferences
- Current budget status

## Monitoring

### Metrics

The MCP server tracks:
- Request count by model
- Token usage
- Cost per request
- Response latency
- Error rates
- Budget utilization

### Dashboards

Access monitoring dashboards:
- Grafana: `http://localhost:3000/d/lambda-labs`
- CloudWatch: Via AWS Console

### Alerts

Automatic alerts are sent when:
- Daily budget reaches 80%
- Monthly budget reaches 80%
- Error rate exceeds 5%
- Average latency exceeds 5 seconds

## Best Practices

### Cost Optimization

1. **Use the right model for the task**
   - Simple tasks → 8B model (80% cost savings)
   - Complex tasks → 17B model (better quality)
   - Default tasks → 70B model (balanced)

2. **Batch similar requests**
   - Group similar prompts together
   - Process in bulk for efficiency

3. **Cache frequent responses**
   - Store common completions
   - Reuse for similar queries

4. **Monitor usage patterns**
   - Review weekly usage reports
   - Identify optimization opportunities

### Performance

1. **Streaming responses**
   - Enable streaming for long outputs
   - Better user experience

2. **Async processing**
   - Use async for non-blocking operations
   - Handle multiple requests concurrently

3. **Fallback strategies**
   - Configure GPU fallback for critical tasks
   - Handle serverless unavailability

## Troubleshooting

### Common Issues

#### Budget Exceeded
```
Error: Lambda Labs budget exceeded
```
**Solution**: Review usage, adjust budget limits, or wait for reset

#### Model Unavailable
```
Error: Model llama3.1-70b not available
```
**Solution**: Use alternative model or retry later

#### High Latency
```
Warning: Response time > 5 seconds
```
**Solution**: Check model selection, reduce prompt size, or use GPU backend

### Debug Mode

Enable debug logging:
```bash
docker run --rm -i \
  -e LOG_LEVEL=DEBUG \
  scoobyjava15/lambda-labs-mcp:latest
```

## API Reference

### REST API Endpoints

The Lambda Labs integration exposes these endpoints:

- `POST /api/v1/lambda-labs/generate` - Generate text
- `GET /api/v1/lambda-labs/usage/stats` - Get usage statistics
- `POST /api/v1/lambda-labs/estimate-cost` - Estimate costs
- `GET /api/v1/lambda-labs/budget/status` - Check budget status
- `GET /api/v1/lambda-labs/budget/remaining` - Get remaining budget
- `GET /api/v1/lambda-labs/health` - Health check

See the [API documentation](../API_DOCUMENTATION.md#lambda-labs) for details.

## Migration Guide

### From GPU-Only to Hybrid

1. **Update configuration**
   ```bash
   export SERVERLESS_RATIO=0.8  # 80% serverless
   ```

2. **Test routing**
   ```python
   # Force serverless
   result = await generate(force_backend="serverless")

   # Force GPU
   result = await generate(force_backend="gpu")
   ```

3. **Monitor performance**
   - Compare latency metrics
   - Track cost savings
   - Adjust ratio as needed

### From OpenAI to Lambda Labs

1. **Update API calls**
   ```python
   # Before
   response = openai.chat.completions.create(...)

   # After
   response = await lambda_labs.generate(...)
   ```

2. **Adjust prompts**
   - LLaMA models may need different prompting
   - Test and refine for best results

3. **Update cost calculations**
   - Lambda Labs is typically 85-93% cheaper
   - Adjust budget expectations

## Support

- Documentation: This guide
- Issues: GitHub Issues
- Slack: #lambda-labs channel
- Email: support@sophia-ai.com
