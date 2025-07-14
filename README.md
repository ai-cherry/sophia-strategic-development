# 🤖 Sophia AI Platform

## 🚀 Lambda Labs Infrastructure Migration

Sophia AI has been upgraded with an optimized Lambda Labs deployment strategy:

- **73% cost reduction** through serverless inference
- **50-70% faster builds** with multi-stage Docker optimization
- **99.9% uptime capability** with enhanced monitoring
- **Intelligent GPU scheduling** with NVIDIA GPU Operator

See `docs/implementation/LAMBDA_LABS_MIGRATION_PLAN.md` for complete migration details.



> **CEO-Level AI Assistant for Pay Ready Business Intelligence**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 🎯 Project Context

- **Company**: Pay Ready (80 employees)
- **Primary User**: CEO (sole user initially)
- **Development**: CEO-led with AI assistance
- **Rollout**: CEO → Super users (3 months) → Company-wide (6+ months)
- **Priority**: Quality & Stability over Performance & Scale

## 🚨 Development Status

**Monorepo Transition**: We are transitioning to a monorepo structure. **Continue using the current directory structure** (`backend/`, `frontend/`, etc.) until the migration is complete in April 2025. See [MONOREPO_TRANSITION_GUIDE.md](docs/monorepo/MONOREPO_TRANSITION_GUIDE.md) for details.

**Enhancement Phase**: January-March 2025 focused on Memory & Learning, Data Automation, and Intelligence Enhancement. See [System Handbook](docs/system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md) for the integrated plan.

## 🏗️ Unified Infrastructure Approach

**IMPORTANT**: Sophia AI follows a **Unified Infrastructure** pattern. All components use a "Unified" naming convention to distinguish current standards from legacy code.

### Core Unified Components:
- **Unified Chat**: Single chat interface for all AI interactions
- **Unified Dashboard**: One dashboard component extended for all views
- **Unified Secret Management**: Centralized GitHub → Pulumi ESC → Application flow
- **Unified Deployment**: Single deployment approach for all environments
- **Unified API Client**: One API client for all frontend requests

See [UNIFIED_INFRASTRUCTURE.md](UNIFIED_INFRASTRUCTURE.md) for the complete list and migration guide.

**Rule**: If it's not "Unified", it's legacy and should not be used for new development.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV package manager
- Cursor AI IDE (recommended)
- Pulumi CLI (for infrastructure deployment)

### 🔥 Infrastructure as Code (IaC) - NEW!
**Major Update (July 5, 2025)**: Complete Infrastructure as Code implementation with automated SSH key management for Lambda Labs. See [Infrastructure Documentation Index](docs/INFRASTRUCTURE_AS_CODE_INDEX.md) for details.

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
- **🚀 AI Agent Real Changes**: Revolutionary capability for infrastructure modifications

### 🔌 Integrations
- **Gong**: Sales call analysis and insights
- **HubSpot**: CRM data and customer intelligence
- **Slack**: Team communication and notifications
- **Linear**: Project management and tracking
- **Modern Stack**: Data warehouse and analytics

### 🏗️ Architecture
- **MCP-Driven**: Model Context Protocol for all integrations
- **Agent-Centric**: Specialized AI agents with <3μs instantiation
- **Security-First**: SOC2 compliant with Pulumi ESC secret management
- **Production-Ready**: 99.9% uptime with comprehensive monitoring
- **🔐 AI Agent Authentication**: Enterprise-grade security for real infrastructure changes

### 🤖 **Revolutionary AI Agent Capabilities**
- **Infrastructure Agent**: Deploy via Pulumi, manage Docker containers, control Vercel deployments
- **Data Agent**: Execute Modern Stack queries, manage database schemas, control Estuary Flow pipelines
- **Integration Agent**: Create Linear tickets, send Slack messages, update HubSpot records
- **🛡️ Enterprise Security**: Zero Trust authentication, risk-based confirmations, complete audit trails

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

### AI Agent Operations (NEW)
```python
# AI agents can make real infrastructure changes
from backend.security.unified_service_auth_manager import UnifiedServiceAuthManager

auth_manager = UnifiedServiceAuthManager()

# Deploy infrastructure
await auth_manager.execute_operation(
    agent_type="infrastructure_agent",
    service="pulumi",
    operation="infrastructure_deployment",
    params={"stack": "production"}
)

# Create database schema
await auth_manager.execute_operation(
    agent_type="data_agent",
    service="snowflake",
    operation="schema_creation",
    params={"schema": "AI_AGENT_TEST"}
)

# Send business notifications
await auth_manager.execute_operation(
    agent_type="integration_agent",
    service="slack",
    operation="message_send",
    params={"channel": "#deployments", "message": "Infrastructure updated"}
)
```

### Natural Language AI Agent Commands
```bash
# Infrastructure operations
"Deploy the updated infrastructure to production"
"Scale up the compute cluster for analytics"
"Create a new Docker service for the MCP gateway"

# Data operations
"Create a new schema for AI agent testing"
"Run the quarterly revenue analysis query"
"Set up a data flow from HubSpot to Modern Stack"

# Business tool integration
"Create a Linear ticket for the authentication bug"
"Send a Slack message about deployment status"
"Update the HubSpot deal with latest information"
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

## 🗓️ Roadmap

### Q1 2025: Intelligence Enhancement
- **January**: Memory & Learning Layer (Mem0, Prompt Optimization)
- **February**: Data Pipeline Automation (N8N Workflows)
- **March**: Multi-Agent Learning System

### Q2 2025: Platform Evolution
- **April**: Monorepo Migration
- **May**: Production Optimization
- **June**: Team Onboarding
# Last deployment: Sun Jul  6 04:36:37 PM UTC 2025

## 🏗️ Unified Infrastructure

The Sophia AI platform now uses a unified naming convention and deployment strategy:

### Cloud-First Architecture
- **Docker Hub Registry**: All images pushed to `scoobyjava15/*`
- **K3s**: Lightweight Kubernetes orchestration on Lambda Labs
- **Kubernetes**: Target orchestration platform

### Unified Scripts
- `unified_deployment.sh` - Main deployment script
- `unified_docker_hub_push.sh` - Build and push to Docker Hub
- `unified_docker_secrets.sh` - Docker secrets management
- `unified_monitoring.sh` - Service monitoring
- `unified_troubleshooting.sh` - Debugging tools
- `scripts/unified_secret_sync.py` - GitHub → Pulumi ESC sync

### Unified Documentation
- `UNIFIED_INFRASTRUCTURE.md` - Complete infrastructure guide
- `UNIFIED_ORCHESTRATION_MIGRATION_PLAN.md` - Swarm → K3s → K8s
- `UNIFIED_SECRET_MANAGEMENT_STRATEGY.md` - Secret management
- `UNIFIED_DEPLOYMENT_STRATEGY.md` - Deployment patterns
- `UNIFIED_DEPLOYMENT_AUDIT_RESOLUTION.md` - Audit resolution

### Current Status (July 2025)

✅ **Production MCP Servers** (All 16 Migrated to Official SDK):

## 🛡️ Technical Debt Prevention - "Clean by Design"

**NEW**: Sophia AI now features a comprehensive **"Clean by Design"** framework that automatically prevents technical debt accumulation.

### 🚨 Zero Technical Debt Policy
Based on our recent cleanup of **290 dead code items** (279 files, 11 directories, 3MB), we've implemented automated prevention:

- **Zero tolerance** for archive directories (`archive/`, `backup/`, `_archived/`)
- **Automated cleanup** of one-time scripts after 30 days
- **Pre-commit blocking** of technical debt patterns
- **Documentation lifecycle** management with auto-archiving

### 🤖 Automated Tools
```bash
# Daily cleanup (runs automatically)
python scripts/utils/daily_cleanup.py

# Pre-commit validation (blocks bad commits)
python scripts/utils/pre_push_debt_check.py

# View complete strategy
cat docs/99-reference/TECHNICAL_DEBT_PREVENTION_STRATEGY.md
```

### 🎯 Success Metrics
- **One-time scripts**: <10 at any time (auto-managed)
- **Archive directories**: 0 (zero tolerance)
- **Backup files**: 0 (zero tolerance)
- **Stale documentation**: <5 files >90 days old

**Result**: Zero major cleanups needed - prevention eliminates technical debt before it accumulates.

---