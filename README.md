# 🤖 Sophia AI Platform

> **Enterprise AI Orchestrator for Business Intelligence & Automation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV package manager
- Cursor AI IDE (recommended)

### Installation
```bash
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
uv sync
```

### Configuration
```bash
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org
```

### Start Services
```bash
# Start MCP servers
python scripts/run_all_mcp_servers.py

# Start backend API
uvicorn backend.app.fastapi_app:app --reload --port 8000

# Start frontend (separate terminal)
cd frontend && npm run dev
```

## 📚 Documentation

### Core Documentation
- **[🏗️ Architecture](ARCHITECTURE.md)** - System design and components
- **[🛠️ Development](DEVELOPMENT.md)** - Development setup and workflow  
- **[🚀 Deployment](DEPLOYMENT.md)** - Production deployment guide
- **[📡 API Reference](API_REFERENCE.md)** - Complete API documentation

### Specialized Guides
- **[🔌 MCP Integration](MCP_INTEGRATION.md)** - MCP server patterns and usage
- **[🤖 Agent Development](AGENT_DEVELOPMENT.md)** - Creating custom agents
- **[🔧 Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[📝 Changelog](CHANGELOG.md)** - Version history and updates

## ✨ Features

### 🧠 AI Orchestration
- **Multi-Agent System**: Specialized agents for different business functions
- **Natural Language Interface**: Conversational business intelligence
- **LangGraph Workflows**: Complex multi-step AI workflows
- **Real-time Processing**: Sub-200ms response times

### 🔌 Integrations
- **Gong**: Sales call analysis and insights
- **HubSpot**: CRM data and customer intelligence  
- **Slack**: Team communication and notifications
- **Linear**: Project management and tracking
- **Snowflake**: Data warehouse and analytics

### 🏗️ Architecture
- **MCP-Driven**: Model Context Protocol for all integrations
- **Agent-Centric**: Specialized AI agents with <3μs instantiation
- **Security-First**: SOC2 compliant with Pulumi ESC secret management
- **Production-Ready**: 99.9% uptime with comprehensive monitoring

## 🎯 Use Cases

### Executive Dashboard
- Real-time business KPIs
- Revenue analytics and forecasting
- Customer health monitoring
- Competitive intelligence

### Sales Intelligence  
- Call analysis and coaching
- Pipeline health assessment
- Deal risk identification
- Performance optimization

### Operations Automation
- Project health monitoring
- Resource allocation optimization
- Automated reporting
- Predictive analytics

## 🔧 Development

### Agent Development
```python
from backend.agents.core.base_agent import BaseAgent

class YourAgent(BaseAgent):
    async def _execute_task(self, task):
        # Your business logic here
        return result
```

### MCP Server Integration
```python
# Natural language commands through MCP
await mcp_client.call_tool(
    server="gong_intelligence",
    tool="analyze_recent_calls",
    arguments={"days": 7}
)
```

### Health Monitoring
```bash
# Check system health
python scripts/comprehensive_health_check.py

# Monitor performance
python scripts/performance_monitor.py
```

## 🌟 Why Sophia AI?

### For Developers
- **Fast Development**: Pre-built agents and MCP integrations
- **Type Safety**: Full Python type hints and async/await
- **Modern Tooling**: UV, FastAPI, React, Cursor AI integration
- **Comprehensive Docs**: Everything you need to get started

### For Business
- **Immediate Value**: Real-time business intelligence
- **Scalable**: Handles growth from startup to enterprise
- **Secure**: Enterprise-grade security and compliance
- **Cost-Effective**: Intelligent routing and optimization

### For Operations
- **Reliable**: 99.9% uptime with comprehensive monitoring
- **Maintainable**: Clean architecture and documentation
- **Extensible**: Easy to add new integrations and capabilities
- **Observable**: Detailed logging and performance metrics

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Follow patterns in [DEVELOPMENT.md](DEVELOPMENT.md)
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Documentation**: See links above for comprehensive guides
- **Issues**: [GitHub Issues](https://github.com/ai-cherry/sophia-main/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ai-cherry/sophia-main/discussions)

---

**Sophia AI** - Transforming business operations through intelligent AI orchestration. 🚀

# Sophia AI

Sophia AI is the central orchestration platform for Pay Ready, providing unified AI-driven business intelligence, automation, and development assistance.

## Getting Started

See the [Getting Started Guide](docs/01-getting-started/README.md).

## Development

See the [Development Guide](docs/02-development/README.md).

## Deployment

See the [Deployment Guides](docs/04-deployment/README.md).

## System Handbook

See the [System Handbook](docs/system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md).
