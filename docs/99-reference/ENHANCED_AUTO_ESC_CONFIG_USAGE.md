# Enhanced Auto ESC Config Usage Guide

> Documentation for the `EnhancedAutoESCConfig` class in `backend/core/auto_esc_config.py`

## Overview

The `EnhancedAutoESCConfig` class provides a comprehensive solution for generating MCP (Model Context Protocol) server configurations from Pulumi ESC (Environment, Secrets, and Configuration). This class is already fully implemented in the codebase and provides advanced features for managing MCP server configurations.

## Key Features

### 1. **Automatic MCP Configuration Generation**
- Generates `.cursor/mcp.json` from Pulumi ESC secrets
- Supports 12+ MCP servers out of the box
- Handles various authentication patterns

### 2. **Server-Specific Configuration**
- Custom logic for each MCP server type
- Environment variable mapping
- Configuration normalization

### 3. **Validation and Error Handling**
- Validates server configurations
- Provides detailed error messages
- Checks for required authentication

### 4. **Perplexity API Support**
- Model preferences for different use cases
- Configurable temperature and token limits
- Support for online search capabilities

## Quick Start

### Basic Usage

```python
from backend.core.auto_esc_config import EnhancedAutoESCConfig

# Initialize the config manager
config = EnhancedAutoESCConfig()

# Generate and write MCP configuration
success = config.write_mcp_json(".cursor/mcp.json")
```

### Validate Configurations

```python
# Validate all server configurations
validation_results = config.validate_mcp_config()

for server, result in validation_results.items():
    if result['valid']:
        print(f"✅ {server}: Configured")
    else:
        print(f"❌ {server}: Missing configuration")
```

## Supported MCP Servers

The following MCP servers are supported out of the box:

1. **lambda-labs** - Lambda Labs GPU infrastructure
2. **qdrant** - Vector database operations
3. **openrouter** - AI model routing
4. **portkey** - AI gateway services
5. **mem0** - Memory management
6. **n8n** - Workflow automation
7. **hubspot** - CRM integration
8. **gong** - Call analytics
9. **slack** - Team communication
10. **linear** - Project management
11. **github** - Source control
12. **estuary-flow** - Data pipelines

## Configuration Methods

### Get Specific Server Configuration

```python
# Get configuration for a specific server
gong_config = config.get_mcp_config('gong')
print(f"Gong API Key: {gong_config.get('api_key')}")
print(f"Gong Endpoint: {gong_config.get('endpoint')}")
```

### Build Server-Specific MCP Configuration

```python
# Get raw configuration
raw_config = config.get_mcp_config('qdrant')

# Build MCP-compatible configuration
mcp_config = config.build_server_config('qdrant', raw_config)
```

### Get Perplexity Configuration

```python
# Get Perplexity API configuration with model preferences
perplexity = config.get_perplexity_config()
print(f"Coding model: {perplexity['model_preferences']['coding']}")
print(f"Temperature: {perplexity['settings']['temperature']}")
```

## Advanced Usage

### Custom Server List

```python
# Override default server list
config.mcp_servers = ['gong', 'hubspot', 'slack']

# Generate configuration for custom servers only
mcp_json = config.generate_mcp_json()
```

### Programmatic Configuration Access

```python
from backend.core.auto_esc_config import (
    get_gong_config,
    get_redis_config,
    get_qdrant_config,
    get_lambda_labs_config
)

# Use specific configuration getters
gong = get_gong_config()
redis = get_redis_config()
qdrant = get_qdrant_config()
lambda_labs = get_lambda_labs_config()
```

## Configuration Structure

### Generated MCP JSON Format

```json
{
  "mcpServers": {
    "gong": {
      "command": "python",
      "args": ["-m", "mcp_servers.gong"],
      "env": {
        "GONG_API_KEY": "your-api-key",
        "GONG_ACCESS_KEY_SECRET": "your-secret",
        "GONG_ENDPOINT": "https://api.gong.io"
      }
    },
    "lambda-labs": {
      "command": "python",
      "args": ["-m", "mcp_servers.lambda_labs"],
      "env": {
        "LAMBDA_LABS_API_KEY": "your-api-key",
        "LAMBDA_SSH_KEY_PATH": "~/.ssh/sophia_correct_key"
      }
    }
  }
}
```

## Environment Variable Mapping

The class automatically maps configuration to server-specific environment variables:

- `api_key` → `{SERVER_NAME}_API_KEY`
- `endpoint` → `{SERVER_NAME}_ENDPOINT`
- Additional config → `{SERVER_NAME}_{KEY}`

## Error Handling

The class provides robust error handling:

```python
try:
    config = config.get_mcp_config('invalid-server')
except Exception as e:
    print(f"Error: {e}")
```

## Testing

Two test scripts are provided:

1. **`scripts/test_enhanced_esc_mcp_config.py`** - Comprehensive testing
2. **`scripts/utils/use_enhanced_esc_config.py`** - Usage examples

Run tests:

```bash
# Test all functionality
python scripts/test_enhanced_esc_mcp_config.py

# Test specific server
python scripts/test_enhanced_esc_mcp_config.py gong

# See usage examples
python scripts/utils/use_enhanced_esc_config.py
```

## Integration with Cursor AI

The generated `.cursor/mcp.json` file is automatically recognized by Cursor AI, enabling:

- Direct access to configured MCP servers
- Automatic environment variable injection
- Seamless API integration
- Enhanced AI capabilities

## Troubleshooting

### Missing Configuration

If a server shows as not configured:
1. Check Pulumi ESC has the required secrets
2. Verify secret names match expected patterns
3. Ensure Pulumi CLI is authenticated

### Invalid Configuration

If validation fails:
1. Check API key format
2. Verify endpoint URLs
3. Review server-specific requirements

### File Write Errors

If writing MCP JSON fails:
1. Ensure `.cursor/` directory exists
2. Check file permissions
3. Verify disk space

## Best Practices

1. **Regular Validation**: Run validation before deployments
2. **Secure Storage**: Never commit generated MCP JSON files
3. **Environment Isolation**: Use different configurations per environment
4. **Monitoring**: Check configuration status regularly
5. **Updates**: Keep server commands and paths up to date

## Future Enhancements

- Dynamic server discovery
- Configuration hot-reloading
- Web UI for configuration management
- Automated secret rotation support
- Multi-environment management

---

*Last Updated: January 2025*
*Version: 1.0.0*
