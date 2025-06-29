# External MCP Repositories

This directory contains external MCP repositories integrated as submodules for the Sophia AI platform.

## Submodules

### Core MCP Framework
- `anthropic-mcp-servers/` - Official Anthropic MCP server implementations and community examples
- `anthropic-mcp-python-sdk/` - Official Python SDK for MCP protocol implementation
- `anthropic-mcp-inspector/` - Visual testing and debugging tool for MCP servers

### Enterprise Integrations
- `notion-mcp-server/` - Official Notion MCP server (production-ready)
- `slack-mcp-server/` - Advanced Slack integration with SSE support

## Usage

### Initialize Submodules (First Time)
```bash
git submodule update --init --recursive
```

### Update All Submodules
```bash
git submodule update --remote --recursive
```

### Update Specific Submodule
```bash
git submodule update --remote external/anthropic-mcp-servers
```

## Integration Guidelines

1. **Reference Only**: Use these repositories as reference implementations
2. **No Direct Modifications**: Do not modify submodule content directly
3. **Custom Adaptations**: Create Sophia-specific adaptations in `mcp-integrations/`
4. **Version Pinning**: Pin to specific commits for production stability

## Maintenance

- Submodules are automatically updated weekly via GitHub Actions
- Manual updates should be tested thoroughly before merging
- Always run integration tests after submodule updates

