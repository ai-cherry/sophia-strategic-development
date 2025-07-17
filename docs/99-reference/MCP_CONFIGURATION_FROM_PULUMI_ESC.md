# MCP Configuration from Pulumi ESC

## Overview

The `EnhancedAutoESCConfig` class extends Sophia AI's configuration management to automatically generate MCP (Model Context Protocol) server configurations from secrets stored in Pulumi ESC and GitHub Organization Secrets.

## Key Features

- **Automatic Secret Retrieval**: Pulls API keys and endpoints from Pulumi ESC
- **Normalized Configuration**: Standardizes different naming conventions across services
- **Server-Specific Handling**: Custom configuration for each MCP server type
- **Validation Support**: Verify configurations before deployment
- **JSON Generation**: Creates `.cursor/mcp.json` automatically

## Architecture

```
GitHub Organization Secrets
          ↓
    Pulumi ESC
          ↓
EnhancedAutoESCConfig
          ↓
    .cursor/mcp.json
```

## Usage

### 1. Simple Sync Script (Recommended for automation)

```bash
# Quick sync - just generate and write
python scripts/sync_mcp_config.py
```

This minimal script is perfect for:
- Automated workflows
- CI/CD pipelines
- Quick manual updates
- Cron jobs

### 2. Comprehensive Tool (For validation and troubleshooting)

```bash
# Generate MCP configuration
python scripts/utils/generate_mcp_config.py

# Validate configuration without writing
python scripts/utils/generate_mcp_config.py --validate

# Show generated configuration
python scripts/utils/generate_mcp_config.py --show-config

# Custom output path
python scripts/utils/generate_mcp_config.py --output /path/to/mcp.json
```

### 3. Programmatic Usage

```python
from backend.core.auto_esc_config import EnhancedAutoESCConfig

# Initialize
config = EnhancedAutoESCConfig()

# Generate configuration
mcp_json = config.generate_mcp_json()

# Write to file
config.write_mcp_json(".cursor/mcp.json")

# Validate configurations
validation_results = config.validate_mcp_config()
```

## MCP Server Configurations

### Supported Servers

1. **lambda-labs**: GPU infrastructure management
2. **qdrant**: Vector database operations
3. **openrouter**: AI model routing
4. **portkey**: AI gateway optimization
5. **mem0**: Conversational memory
6. **n8n**: Workflow automation
7. **hubspot**: CRM integration
8. **gong**: Call analysis
9. **slack**: Team communication
10. **linear**: Project management
11. **github**: Code repository
12. **estuary-flow**: Data pipeline

### Secret Naming Convention

Secrets should be stored in Pulumi ESC with these naming patterns:

```yaml
# API Keys
{SERVER_NAME}_API_KEY: "your-api-key"
GONG_ACCESS_KEY: "gong-key"
HUBSPOT_ACCESS_TOKEN: "hubspot-token"

# Endpoints (optional, defaults provided)
{SERVER_NAME}_ENDPOINT: "https://api.example.com"
GONG_BASE_URL: "https://api.gong.io"

# Additional Configuration
{SERVER_NAME}_CONFIG: '{"option": "value"}'
```

## Generated MCP JSON Structure

```json
{
  "mcpServers": {
    "gong": {
      "command": "python",
      "args": ["-m", "mcp_servers.gong"],
      "env": {
        "GONG_API_KEY": "...",
        "GONG_ACCESS_KEY_SECRET": "...",
        "GONG_ENDPOINT": "https://api.gong.io"
      }
    },
    "qdrant": {
      "command": "python",
      "args": ["-m", "mcp_servers.qdrant"],
      "env": {
        "QDRANT_API_KEY": "...",
        "QDRANT_URL": "https://cloud.qdrant.io",
        "QDRANT_CLUSTER_NAME": "sophia-ai-production"
      }
    }
  }
}
```

## Configuration Normalization

The system automatically normalizes different naming conventions:

- `access_token` → `api_key`
- `token` → `api_key`
- `bot_token` → `api_key`
- `url` → `endpoint`
- `base_url` → `endpoint`
- `host` → `endpoint`

## Server-Specific Configurations

### Lambda Labs
```python
{
  "api_key": "LAMBDA_API_KEY",
  "endpoint": "https://cloud.lambda.ai/api/v1/instances",
  "ssh_private_key_path": "~/.ssh/sophia_correct_key"
}
```

### Gong
```python
{
  "access_key": "GONG_ACCESS_KEY",
  "access_key_secret": "GONG_ACCESS_KEY_SECRET",
  "endpoint": "https://api.gong.io"
}
```

### Qdrant
```python
{
  "api_key": "QDRANT_API_KEY",
  "url": "https://cloud.qdrant.io",
  "cluster_name": "sophia-ai-production"
}
```

## Validation

The validation feature checks:

1. **Authentication**: Presence of API key or authentication token
2. **Endpoint**: Valid endpoint URL (where required)
3. **Configuration**: Additional server-specific requirements

```bash
# Run validation
python scripts/utils/generate_mcp_config.py --validate

# Output
📋 MCP Server Configuration Validation Results:

Server          Valid    Has Auth    Has Endpoint    Notes
------------------------------------------------------------
gong            ✅       ✅          ✅              
qdrant          ✅       ✅          ✅              
lambda-labs     ✅       ✅          ✅              
slack           ❌       ❌          ✅              
```

## Integration with Cursor IDE

The generated `.cursor/mcp.json` file is automatically loaded by Cursor IDE to provide MCP server capabilities within the development environment.

### Automatic Regeneration

Add to your development workflow:

```bash
# In .bashrc or .zshrc
alias mcp-refresh='python scripts/sync_mcp_config.py'

# Manual trigger
python scripts/sync_mcp_config.py
```

### GitHub Actions Automation

The `.github/workflows/sync-secrets.yml` workflow automatically syncs MCP configuration:

**Triggers:**
- `repository_dispatch` event with type `secrets-updated`
- Manual workflow dispatch
- Daily at 2 AM UTC (scheduled)

**Features:**
- Automatic Pulumi ESC login
- MCP configuration generation
- Git commit only if changes detected
- Job summaries with server list
- Failure notifications via GitHub issues

**Trigger via API:**
```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/ai-cherry/sophia-main/dispatches \
  -d '{"event_type":"secrets-updated"}'
```

## Troubleshooting

### Missing Secrets

If servers show as invalid during validation:

1. Check Pulumi ESC configuration:
   ```bash
   pulumi env get scoobyjava-org/default/sophia-ai-production
   ```

2. Verify secret names match expected patterns
3. Ensure GitHub Organization Secrets are synced to Pulumi ESC

### Configuration Not Loading

1. Check file permissions on `.cursor/mcp.json`
2. Restart Cursor IDE after generating new configuration
3. Verify JSON syntax is valid

### Server-Specific Issues

- **Lambda Labs**: Ensure SSH key path exists
- **Gong**: Both access key and secret are required
- **Qdrant**: Cluster name must match your Qdrant setup

## Best Practices

1. **Regular Updates**: Regenerate MCP config after secret rotation
2. **Version Control**: Don't commit `.cursor/mcp.json` (contains secrets)
3. **Environment Separation**: Use different Pulumi ESC environments for staging/production
4. **Validation First**: Always validate before deploying new configurations

## Security Considerations

- MCP configurations contain sensitive API keys
- Store `.cursor/mcp.json` in `.gitignore`
- Use Pulumi ESC's secret encryption
- Rotate API keys regularly
- Monitor MCP server access logs

## Future Enhancements

- [ ] Auto-discovery of MCP servers from directory
- [ ] Environment-specific configurations
- [ ] Secret rotation automation
- [ ] Health check integration
- [ ] Configuration hot-reloading

## Related Documentation

- [Pulumi ESC Documentation](../infrastructure/esc/README.md)
- [MCP Server Development Guide](../mcp-servers/README.md)
- [GitHub Organization Secrets](PERMANENT_GITHUB_ORG_SECRETS_SOLUTION.md)
