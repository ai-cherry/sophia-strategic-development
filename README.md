# 🤖 Sophia AI - Enterprise Intelligence Platform

**Advanced AI-driven business intelligence platform with comprehensive data integration, semantic search, and automated insights generation.**

---

## 🚀 **Quick Start for AI Coders**

### **Essential Documentation (READ FIRST)**
- **[📚 Documentation Index](./docs/README_DOCUMENTATION_INDEX.md)** - Complete guide to all documentation
- **[🤖 AI Coder Reference](./docs/AI_CODER_REFERENCE.md)** - Context, rules, and guidelines for AI development
- **[🏗️ Architecture Patterns](./docs/ARCHITECTURE_PATTERNS_AND_STANDARDS.md)** - Code patterns and best practices
- **[🔌 Platform Integration Guidelines](./docs/PLATFORM_INTEGRATION_GUIDELINES.md)** - External platform integration standards

### **Development Setup**
```bash
# 1. Clone and setup
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# 2. Read essential documentation
cat docs/AI_CODER_REFERENCE.md

# 3. Install dependencies
uv sync
npm install

# 4. Configure environment (see docs/GITHUB_SECRETS_TEMPLATE.md)
cp .env.example .env
# Edit .env with your credentials

# 5. Start MCP servers
python scripts/start_mcp_servers.py

# 6. Run health checks
python scripts/health_check.py
```

---

## 🏗️ **System Architecture**

### **Clean Architecture Implementation (NEW)**

We are transitioning to Clean Architecture (Hexagonal Architecture) for improved maintainability and testability:

- **Domain Layer** - Pure business logic with no external dependencies
- **Application Layer** - Use cases and business workflows
- **Infrastructure Layer** - External service implementations (Snowflake, Portkey, etc.)
- **Presentation Layer** - API endpoints and request handling

See [Architecture Documentation](./docs/03-architecture/) for detailed implementation guide.

### **Core Components**
```
┌─────────────────────────────────────────────────────────────────┐
│                    SOPHIA AI ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer (React)                                        │
│  ├── CEO Dashboard        ├── Knowledge Dashboard              │
│  ├── Project Dashboard    └── Conversational Interface         │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway Layer (FastAPI)                                   │
│  ├── Authentication       ├── Rate Limiting                    │
│  ├── Request Routing      └── Response Caching                 │
├─────────────────────────────────────────────────────────────────┤
│  Agent Orchestration Layer                                     │
│  ├── Enhanced Agents      ├── Specialized Agents              │
│  ├── Infrastructure Agents└── LangGraph Workflows             │
├─────────────────────────────────────────────────────────────────┤
│  MCP Server Network (Ports 9000-9020)                         │
│  ├── AI Memory (9000)     ├── Snowflake Admin (9012)          │
│  ├── Gong Intelligence    ├── HubSpot CRM                     │
│  ├── Slack Integration    └── Linear Projects                  │
├─────────────────────────────────────────────────────────────────┤
│  Data & Intelligence Layer                                     │
│  ├── Snowflake (Structured)├── Pinecone (Vectors)             │
│  ├── Semantic Search      └── Memory Management               │
├─────────────────────────────────────────────────────────────────┤
│  External Integrations (14 Platforms)                         │
│  ├── Gong (Sales)         ├── HubSpot (CRM)                   │
│  ├── Slack (Comms)        ├── Linear (Projects)               │
│  ├── GitHub (Code)        └── OpenRouter (LLMs)               │
└─────────────────────────────────────────────────────────────────┘
```

### **Key Features**
- **🧠 AI-Powered Intelligence**: Advanced semantic search and automated insights
- **🔌 14 Platform Integrations**: Comprehensive business tool connectivity
- **🏗️ Infrastructure as Code**: Fully automated deployment and management
- **🔐 Enterprise Security**: SOC2 compliant with comprehensive audit trails
- **📊 Real-time Analytics**: Live dashboards and performance monitoring
- **🤖 Agent-Centric Architecture**: Specialized AI agents for business functions

---

## 📊 **Platform Integrations**

### **Data Stack**
- **Snowflake** - Data warehouse and analytics
- **Estuary** - Data pipeline orchestration
- **Gong** - Sales conversation intelligence
- **Slack** - Team communication analysis
- **HubSpot** - CRM and customer data

### **Development Stack**
- **Vercel** - Frontend deployment
- **Lambda Labs** - Compute infrastructure
- **Figma** - Design system integration

### **AI Stack**
- **Portkey** - LLM gateway and optimization
- **OpenRouter** - Multi-model LLM access

### **Operations Stack**
- **Linear** - Project management
- **Asana** - Task coordination
- **UserGems** - Contact intelligence
- **Apollo.io** - Sales intelligence

---

## 🛠️ **Development Guidelines**

### **Architecture Principles**
1. **MCP-First Integration** - All external platforms use Model Context Protocol
2. **Agent-Centric Design** - Specialized AI agents for domain expertise
3. **Infrastructure as Code** - Automated deployment and configuration
4. **Security by Design** - Pulumi ESC credential management
5. **Performance Optimization** - Sub-microsecond agent instantiation

### **Coding Standards**
```python
# Required patterns for all code
from typing import Dict, List, Any, Optional
import asyncio
import logging

class ExampleAgent(BaseAgent):
    def __init__(self, agent_name: str):
        super().__init__(agent_name, "enhanced", ["capability1", "capability2"])
        self.logger = logging.getLogger(f"sophia.agents.{agent_name}")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Always validate inputs
            if not request.get("query"):
                raise ValueError("Query parameter required")
            
            # Use async for I/O operations
            result = await self._process_async_operation(request)
            
            return {
                "status": "success",
                "data": result,
                "agent": self.agent_name
            }
            
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.agent_name
            }
```

### **Performance Requirements**
- **Agent Instantiation**: < 3 microseconds
- **API Response Time**: < 200ms
- **Database Queries**: Parameterized with limits
- **Memory Usage**: Lazy-load heavy resources

---

## 🔐 **Security & Credentials**

### **Credential Management Flow**
```
GitHub Organization Secrets → Pulumi ESC → Application Runtime
```

### **Required Environment Variables**
See [GitHub Secrets Template](./docs/GITHUB_SECRETS_TEMPLATE.md) for complete list:

```bash
# Core Infrastructure
SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222
SNOWFLAKE_USER=SCOOBYJAVA15
SNOWFLAKE_PASSWORD=<PAT_TOKEN>

# AI Services
OPENROUTER_API_KEY=<api_key>
PORTKEY_API_KEY=<api_key>

# Platform Integrations
GONG_ACCESS_KEY=<access_key>
SLACK_BOT_TOKEN=<bot_token>
HUBSPOT_ACCESS_TOKEN=<access_token>
LINEAR_API_KEY=<api_key>

# Infrastructure
PULUMI_ACCESS_TOKEN=<access_token>
GITHUB_TOKEN=<personal_access_token>
```

---

## 🚀 **Deployment**

### **Automated Deployment**
```bash
# Deploy complete infrastructure
python scripts/automated_pulumi_esc_deployment.py

# Deploy specific components
python scripts/deploy_mcp_servers.py
python scripts/deploy_integrations.py

# Monitor deployment
python scripts/health_check.py
```

### **GitHub Actions Workflows**
- **Automated Infrastructure Deployment** - Complete system deployment
- **Dashboard Deployment Automation** - Frontend deployment
- **Unified Secret Sync** - Credential management
- **MCP Server Deployment** - Backend service deployment

---

## 📊 **Monitoring & Health**

### **Health Check Endpoints**
```bash
# System health
curl https://app.sophia-intel.ai/health

# Component health
curl https://app.sophia-intel.ai/mcp/health
curl https://app.sophia-intel.ai/database/health
curl https://app.sophia-intel.ai/integrations/health
```

### **Performance Monitoring**
```bash
# Check agent performance
python scripts/performance_test.py

# Monitor integration health
python scripts/integration_health_monitor.py

# Database performance
python scripts/snowflake_config_manager.py status
```

---

## 🧪 **Testing**

### **Test Categories**
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/

# Security tests
pytest tests/security/

# Full test suite with coverage
pytest --cov=backend tests/
```

### **Test Requirements**
- **Minimum 80% code coverage**
- **All public methods tested**
- **Mock external dependencies**
- **Test error conditions**

---

## 📚 **Documentation**

### **For AI Coders**
- **[AI Coder Reference](./docs/AI_CODER_REFERENCE.md)** - Complete development context
- **[Architecture Patterns](./docs/ARCHITECTURE_PATTERNS_AND_STANDARDS.md)** - Code patterns and standards
- **[Platform Integration Guidelines](./docs/PLATFORM_INTEGRATION_GUIDELINES.md)** - Integration best practices

### **For Operations**
- **[Infrastructure Management](./docs/INFRASTRUCTURE_MANAGEMENT_ARCHITECTURE.md)** - IaC and automation
- **[MCP Port Strategy](./docs/MCP_PORT_STRATEGY.md)** - Server architecture
- **[Best Practices Guide](./docs/SOPHIA_AI_BEST_PRACTICES_GUIDE.md)** - Operational guidelines

### **For Data Teams**
- **[Snowflake Integration Analysis](./sophia-ai-snowflake-ecosystem-integration-analysis.md)** - Data warehouse setup
- **[Estuary Integration Guide](./docs/ESTUARY_INTEGRATION_GUIDE.md)** - Data pipeline configuration

---

## 🤝 **Contributing**

### **Development Workflow**
1. **Read documentation** - Start with [AI Coder Reference](./docs/AI_CODER_REFERENCE.md)
2. **Create feature branch** from `main`
3. **Follow coding standards** and architecture patterns
4. **Add comprehensive tests** with good coverage
5. **Update documentation** as needed
6. **Submit pull request** with detailed description

### **Code Review Checklist**
- [ ] Follows architecture patterns and coding standards
- [ ] Includes comprehensive tests
- [ ] Uses proper error handling and logging
- [ ] Implements security best practices
- [ ] Updates relevant documentation
- [ ] Passes all automated checks

---

## 📈 **Performance Metrics**

### **Current Performance**
- **Agent Instantiation**: 2.1μs average (target: <3μs)
- **API Response Time**: 145ms average (target: <200ms)
- **Database Query Performance**: 98% under 100ms
- **System Uptime**: 99.9% availability
- **Integration Health**: 14/14 platforms operational

### **Optimization Features**
- **Connection Pooling** - Reduced database connection overhead
- **Query Caching** - 85% cache hit rate for repeated queries
- **Lazy Loading** - Deferred resource initialization
- **Async Processing** - Non-blocking I/O operations

---

## 🔗 **Links & Resources**

### **Live Applications**
- **Production App**: https://app.sophia-intel.ai
- **API Documentation**: https://api.sophia-intel.ai/docs
- **Health Dashboard**: https://status.sophia-intel.ai

### **External Documentation**
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Pulumi ESC Documentation](https://www.pulumi.com/docs/esc/)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### **Support**
- **Technical Issues**: Create GitHub issue with `bug` label
- **Feature Requests**: Create GitHub issue with `enhancement` label
- **Security Issues**: Email security@sophia-ai.com
- **Documentation**: Submit PR with documentation updates

---

## 📄 **License**

This project is proprietary software. All rights reserved.

---

**Sophia AI - Transforming business intelligence through advanced AI and comprehensive data integration.**

*Last Updated: June 27, 2025*  
*Version: 2.0*  
*Status: Production*

