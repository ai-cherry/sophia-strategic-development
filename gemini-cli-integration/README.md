# Sophia AI - Gemini CLI Integration

## Overview

This integration brings Google's powerful Gemini CLI with MCP (Model Context Protocol) support directly into the Sophia AI ecosystem. It provides seamless access to Gemini 2.5 Pro's 1M token context window while leveraging our existing 4-tier MCP server architecture.

## Features

### 🚀 **Core Capabilities**
- **Free Gemini 2.5 Pro Access** - 60 requests/minute, 1,000 requests/day
- **1M Token Context Window** - Comprehensive codebase analysis
- **MCP Server Integration** - Direct connection to all Sophia AI services
- **Intelligent Routing** - Automatic request routing based on content
- **Health Monitoring** - Continuous server health checks and auto-recovery
- **Security Compliance** - JWT authentication and encryption

### 🏗️ **Architecture Integration**
- **sophia-ai-intelligence** (Port 8091) - AI model routing and optimization
- **sophia-data-intelligence** (Port 8092) - Data warehousing and ETL pipelines
- **sophia-infrastructure** (Port 8093) - Container and infrastructure management
- **sophia-business-intelligence** (Port 8094) - CRM and business analytics
- **sophia-regulatory-compliance** (Port 8095) - Regulatory monitoring and analysis
- **sophia-figma-dev-mode** - Design-to-code automation
- **sophia-ui-ux-agent** - Intelligent design automation

## Quick Start

### 1. Installation

```bash
# Run the automated setup script
./gemini-cli-integration/setup-gemini-cli.sh
```

This script will:
- Install Gemini CLI globally
- Configure MCP server integration
- Create project context files
- Set up helper scripts and environment templates

### 2. Configuration

```bash
# Copy environment template
cp .gemini/env.template .gemini/env

# Edit with your credentials
nano .gemini/env
```

Required environment variables:
```bash
PULUMI_ORG=scoobyjava-org
PULUMI_STACK=sophia-ai-production
FIGMA_PERSONAL_ACCESS_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### 3. Start MCP Servers

```bash
# Start all MCP servers
./gemini-cli-integration/start-mcp-servers.sh

# Or start specific servers
python gemini-cli-integration/gemini_mcp_integration.py --action start --server sophia-ai-intelligence
```

### 4. Test Integration

```bash
# Run integration tests
./gemini-cli-integration/test-integration.sh

# Launch Gemini CLI
gemini
```

## Usage Examples

### Basic Codebase Analysis
```bash
gemini "Analyze the Sophia AI codebase structure and identify key components"
```

### Regulatory Compliance Query
```bash
gemini "What are the current CFPB regulations for AI-based consumer interactions?"
```

### Business Intelligence
```bash
gemini "Generate a summary of our dashboard performance metrics from the last 30 days"
```

### Design System Analysis
```bash
gemini "Review the UI components in the frontend directory and suggest improvements"
```

### Infrastructure Management
```bash
gemini "Check the status of our Snowflake connections and suggest optimizations"
```

## Advanced Features

### Intelligent Routing

The system automatically routes requests to appropriate MCP servers based on content:

- **AI/Model queries** → `sophia-ai-intelligence`
- **Data/Database queries** → `sophia-data-intelligence`
- **Infrastructure queries** → `sophia-infrastructure`
- **Business queries** → `sophia-business-intelligence`
- **Compliance queries** → `sophia-regulatory-compliance`
- **Design queries** → `sophia-figma-dev-mode`

### Health Monitoring

```bash
# Check server status
python gemini-cli-integration/gemini_mcp_integration.py --action status

# Start continuous monitoring
python gemini-cli-integration/gemini_mcp_integration.py --action monitor --interval 30
```

### Workflow Automation

The integration supports automatic triggers for common workflows:

- **Code Analysis** - Triggered on large codebase queries
- **Compliance Monitoring** - Triggered on regulatory keywords
- **Design Analysis** - Triggered on Figma URL detection
- **Business Intelligence** - Triggered on dashboard/metrics queries

## Configuration

### MCP Server Configuration

The main configuration is in `.gemini/settings.json`:

```json
{
  "mcpServers": {
    "sophia-ai-intelligence": {
      "command": "python",
      "args": ["-m", "backend.mcp.unified_mcp_servers", "--server", "ai-intelligence"],
      "capabilities": ["model_routing", "cost_optimization", "semantic_caching"],
      "auto_start": true
    }
  },
  "routing": {
    "strategy": "intelligent",
    "rules": [
      {
        "pattern": "ai.*|model.*|intelligence.*",
        "server": "sophia-ai-intelligence"
      }
    ]
  }
}
```

### Security Configuration

```json
{
  "security": {
    "authentication": {
      "enabled": true,
      "type": "jwt",
      "secretSource": "pulumi-esc"
    },
    "geminiCliSecurity": {
      "enableSandboxing": true,
      "restrictFileAccess": true,
      "allowedDirectories": ["/app", "/tmp/gemini-workspace"]
    }
  }
}
```

## Management Scripts

### Server Management
```bash
# Start all servers
./gemini-cli-integration/start-mcp-servers.sh

# Stop all servers
./gemini-cli-integration/stop-mcp-servers.sh

# Test integration
./gemini-cli-integration/test-integration.sh
```

### Python API
```python
from gemini_mcp_integration import GeminiMCPIntegration

async with GeminiMCPIntegration() as integration:
    # Start all servers
    await integration.start_all_servers()
    
    # Check status
    status = await integration.get_all_server_status()
    
    # Route a request
    server = await integration.route_request("Analyze our data pipeline")
```

## Troubleshooting

### Common Issues

**1. MCP Server Connection Failures**
```bash
# Check if ports are available
netstat -tulpn | grep :809

# Restart specific server
python gemini-cli-integration/gemini_mcp_integration.py --action stop --server sophia-ai-intelligence
python gemini-cli-integration/gemini_mcp_integration.py --action start --server sophia-ai-intelligence
```

**2. Gemini CLI Installation Issues**
```bash
# Verify Node.js version (18+ required)
node --version

# Reinstall Gemini CLI
npm uninstall -g @google/gemini-cli
npm install -g @google/gemini-cli
```

**3. Authentication Errors**
```bash
# Verify environment variables
source .gemini/env
echo $PULUMI_ORG

# Check Pulumi ESC access
pulumi config get --stack sophia-ai-production
```

**4. Performance Issues**
```bash
# Check server health
python gemini-cli-integration/gemini_mcp_integration.py --action status

# Monitor resource usage
htop
```

### Debug Mode

Enable debug logging:
```bash
export GEMINI_CLI_LOG_LEVEL=debug
export PYTHONPATH=/app
python gemini-cli-integration/gemini_mcp_integration.py --action monitor
```

## Performance Optimization

### Caching Configuration
```json
{
  "performance": {
    "caching": {
      "enabled": true,
      "ttl": 300,
      "gemini_context_cache": {
        "enabled": true,
        "ttl": 3600,
        "max_context_size": 500000
      }
    }
  }
}
```

### Connection Pooling
```json
{
  "performance": {
    "connection_pooling": true,
    "request_batching": true,
    "async_operations": true
  }
}
```

## Security Best Practices

### 1. Credential Management
- Store all API keys in Pulumi ESC
- Use environment variables for configuration
- Never commit credentials to version control

### 2. Access Control
- Enable JWT authentication for MCP servers
- Implement rate limiting
- Use sandboxing for file operations

### 3. Network Security
- Restrict MCP server access to localhost
- Use encryption for data in transit
- Monitor for suspicious activity

## Monitoring and Observability

### Prometheus Metrics
- Server health and response times
- Request routing and success rates
- Resource utilization and performance

### Grafana Dashboards
- `gemini-cli-overview` - Overall system health
- `mcp-server-health` - Individual server status
- `performance-metrics` - Performance and latency
- `usage-analytics` - Usage patterns and trends

### Logging
```bash
# View MCP server logs
tail -f /var/log/sophia-ai/mcp-servers.log

# View Gemini CLI logs
tail -f ~/.gemini/logs/gemini-cli.log
```

## Development Workflow

### 1. Code Analysis
```bash
gemini "Review the recent changes in the backend/agents directory"
```

### 2. Testing
```bash
gemini "Generate unit tests for the new regulatory compliance agent"
```

### 3. Documentation
```bash
gemini "Create API documentation for the business intelligence endpoints"
```

### 4. Deployment
```bash
gemini "Check the deployment status and suggest optimizations"
```

## Integration with Existing Tools

### Cursor IDE
- Automatic MCP server detection
- Context-aware code completion
- Integrated terminal support

### GitHub Actions
- Automated testing on MCP configuration changes
- Deployment pipeline integration
- Performance monitoring

### Slack Integration
- Server health notifications
- Query result sharing
- Team collaboration features

## Roadmap

### Phase 1 (Current)
- ✅ Basic MCP server integration
- ✅ Intelligent routing
- ✅ Health monitoring
- ✅ Security implementation

### Phase 2 (Next Month)
- 🔄 Advanced workflow automation
- 🔄 Enhanced performance optimization
- 🔄 Comprehensive monitoring dashboards
- 🔄 Team collaboration features

### Phase 3 (Future)
- 📋 Machine learning-based routing
- 📋 Predictive health monitoring
- 📋 Advanced security features
- 📋 Multi-tenant support

## Support

### Documentation
- Project context: `GEMINI.md`
- API documentation: `/api/docs`
- MCP server specs: `backend/mcp/README.md`

### Team Communication
- Slack: `#sophia-ai-dev`
- Email: `dev-team@sophia-intel.ai`
- Issues: GitHub Issues

### Resources
- [Gemini CLI Documentation](https://github.com/google/gemini-cli)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Sophia AI Architecture Guide](../docs/architecture.md)

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Run tests and linting
5. Submit pull request

### Code Standards
- Python: Black formatting, type hints, docstrings
- JavaScript: ESLint + Prettier
- Documentation: Markdown with proper structure

### Testing
```bash
# Run integration tests
./gemini-cli-integration/test-integration.sh

# Run Python tests
pytest gemini-cli-integration/tests/

# Run performance tests
python gemini-cli-integration/performance_tests.py
```

## License

This integration is part of the Sophia AI platform and follows the same licensing terms as the main project.

---

**Ready to enhance your Sophia AI development workflow with Google Gemini CLI!** 🚀

