#!/bin/bash
# Integrate MCP repositories as submodules

echo "🔗 Integrating MCP repositories as submodules..."

# Add Anthropic MCP servers
git submodule add https://github.com/modelcontextprotocol/servers.git external/anthropic-mcp-servers

# Add MCP Inspector
git submodule add https://github.com/modelcontextprotocol/inspector.git external/anthropic-mcp-inspector

# Initialize and update submodules
git submodule update --init --recursive

# Commit submodule additions
git add .gitmodules external/
git commit -m "Add MCP repositories as submodules

- Added Anthropic MCP servers for reference implementations
- Added MCP Inspector for testing and debugging
- Configured submodules for automatic updates"

echo "✅ Submodules integrated successfully"
