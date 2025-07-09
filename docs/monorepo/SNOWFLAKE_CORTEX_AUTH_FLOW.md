# Snowflake Cortex Authentication Flow

## Overview

Sophia AI supports dual authentication modes for Snowflake Cortex integration:
1. **Direct Mode**: Traditional username/password authentication
2. **MCP Mode**: Programmatic Access Token (PAT) authentication via official Snowflake MCP server

## Authentication Modes

### Direct Mode (Legacy)
- Uses traditional Snowflake username/password credentials
- Stored in Pulumi ESC as `snowflake_user` and `snowflake_password`
- Direct SQL execution through `snowflake-connector-python`
- Suitable for batch operations and direct SQL queries

### MCP Mode (Recommended)
- Uses Programmatic Access Token (PAT) for enhanced security
- Token stored in Pulumi ESC as `snowflake_mcp_pat`
- Communicates via official Snowflake MCP server
- Provides standardized tool interfaces for Cortex operations

## Secret Configuration

### GitHub Organization Secrets
```yaml
# Production PAT
SNOWFLAKE_MCP_PAT_PROD: <your-production-pat>

# Staging PAT
SNOWFLAKE_MCP_PAT_STAGING: <your-staging-pat>

# Legacy credentials (still supported)
SNOWFLAKE_USER_PROD: <username>
SNOWFLAKE_PASSWORD_PROD: <password>
```

### Pulumi ESC Mapping
```yaml
values:
  sophia:
    data:
      snowflake:
        # Direct mode credentials
        user: ${SNOWFLAKE_USER_PROD}
        password: ${SNOWFLAKE_PASSWORD_PROD}

        # MCP mode credentials
        mcp_pat: ${SNOWFLAKE_MCP_PAT_PROD}

        # Common configuration
        account: ${SNOWFLAKE_ACCOUNT}
        warehouse: ${SNOWFLAKE_WAREHOUSE}
        database: ${SNOWFLAKE_DATABASE}
        schema: ${SNOWFLAKE_SCHEMA}
```

## Generating PAT Tokens

### Via Snowflake UI
1. Log into Snowflake Console
2. Navigate to Account → Security → Programmatic Access
3. Click "Generate Token"
4. Set appropriate expiration (recommend 90 days)
5. Copy token immediately (shown only once)

### Via SQL
```sql
-- Create PAT for service account
CALL SYSTEM$GENERATE_SCIM_ACCESS_TOKEN('SOPHIA_AI_MCP_SERVICE');

-- List existing tokens
SELECT * FROM TABLE(INFORMATION_SCHEMA.SCIM_ACCESS_TOKENS());
```

## Integration with auto_esc_config

The enhanced `auto_esc_config.py` automatically loads both authentication types:

```python
# Direct mode credentials
snowflake_user = config.get("snowflake_user")
snowflake_password = config.get("snowflake_password")

# MCP mode credentials
snowflake_pat = config.get("snowflake_mcp_pat")
os.environ.setdefault("SNOWFLAKE_MCP_PAT", snowflake_pat or "")
```

## Mode Selection

The Cortex adapter automatically selects the appropriate mode based on:
1. Environment variable `CORTEX_MODE` (if set)
2. Availability of PAT token (prefers MCP if available)
3. Task type (some operations work better in specific modes)

### Environment Override
```bash
# Force direct mode
export CORTEX_MODE=direct

# Force MCP mode
export CORTEX_MODE=mcp
```

### Programmatic Selection
```python
from shared.utils.snowflake_cortex import SnowflakeCortexService, MCPMode

# Explicit mode selection
service = SnowflakeCortexService(mode=MCPMode.MCP)

# Auto-detection (default)
service = SnowflakeCortexService()
```

## Security Best Practices

1. **Rotate PATs Regularly**: Every 90 days minimum
2. **Scope Tokens Appropriately**: Use minimal required permissions
3. **Separate Environments**: Different PATs for prod/staging/dev
4. **Monitor Usage**: Track token usage in Snowflake audit logs
5. **Secure Storage**: Always use Pulumi ESC, never hardcode

## Troubleshooting

### PAT Authentication Failures
```bash
# Check if PAT is loaded
echo $SNOWFLAKE_MCP_PAT | cut -c1-10...

# Test MCP server connection
curl -H "Authorization: Bearer $SNOWFLAKE_MCP_PAT" http://snowflake-mcp:8080/health
```

### Fallback Behavior
If MCP authentication fails, the system automatically falls back to direct mode (if credentials available).

## Migration Path

1. **Phase 1**: Both modes supported (current)
2. **Phase 2**: MCP mode preferred, direct mode deprecated
3. **Phase 3**: MCP mode only (target state)

## Related Documentation
- [MCP Server Configuration](../06-mcp-servers/official_servers.md)
- [Snowflake Cortex Layer Architecture](../03-architecture/SNOWFLAKE_CORTEX_LAYER.md)
- [Secret Rotation Guide](../08-security/SECRET_ROTATION_GUIDE.md)
