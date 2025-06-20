# Sophia AI - High-Level Project Overview

## 🎯 Project Vision
Sophia AI is an enterprise-grade AI orchestrator and business intelligence platform designed for Pay Ready company. It serves as the central "Pay Ready Brain" that orchestrates multiple AI agents, integrates with business systems, and provides real-time insights for executive decision-making.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Executive Dashboard                       │
│                    (Retool/Frontend)                        │
├─────────────────────────────────────────────────────────────┤
│                    API Gateway Layer                         │
│                  (FastAPI + WebSockets)                     │
├─────────────────────────────────────────────────────────────┤
│                  AI Agent Orchestrator                       │
│              (Multi-Agent Architecture)                      │
├─────────────────────────────────────────────────────────────┤
│                    MCP Server Layer                          │
│            (Model Context Protocol Servers)                  │
├─────────────────────────────────────────────────────────────┤
│                 Integration Layer                            │
│        (External APIs & Business Systems)                    │
├─────────────────────────────────────────────────────────────┤
│                  Data & Storage Layer                        │
│      (Snowflake, PostgreSQL, Pinecone, Redis)              │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Core Technology Stack

### **Backend Technologies**
- **Language**: Python 3.11+
- **Framework**: FastAPI (async REST APIs)
- **AI/ML**: OpenAI, Anthropic Claude, LlamaIndex
- **Vector DB**: Pinecone, Weaviate
- **Data Warehouse**: Snowflake
- **Cache**: Redis
- **Database**: PostgreSQL
- **Message Queue**: RabbitMQ/Celery

### **Frontend Technologies**
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI / Ant Design
- **State Management**: Redux Toolkit
- **Real-time**: WebSockets
- **Dashboards**: Retool (low-code platform)

### **Infrastructure & DevOps**
- **IaC**: Pulumi (Infrastructure as Code)
- **Secrets**: Pulumi ESC (Environment Secrets & Configuration)
- **CI/CD**: GitHub Actions
- **Containers**: Docker
- **Orchestration**: Kubernetes (optional)
- **Cloud**: Lambda Labs, Vercel, AWS
- **Monitoring**: Prometheus, Grafana

### **AI & Integration Tools**
- **LLM Gateway**: OpenRouter, Portkey
- **Web Scraping**: Apify
- **Workflow Automation**: n8n, Pipedream
- **Data Pipeline**: Airbyte, Estuary
- **Communication**: Slack SDK
- **CRM**: HubSpot, Intercom APIs
- **Sales Intelligence**: Gong.io

## 🤖 MCP (Model Context Protocol) Structure

### **What is MCP?**
MCP is a protocol that enables AI assistants to interact with external systems through standardized server interfaces. Sophia AI uses MCP servers as bridges between AI agents and various services.

### **MCP Server Architecture**
```
mcp_config.json                    # MCP configuration file
├── Local MCP Servers
│   ├── ai_memory_mcp_server      # Persistent AI memory
│   ├── gong_mcp_server           # Gong.io sales intelligence
│   ├── slack_mcp_server          # Slack communication
│   ├── snowflake_mcp_server      # Data warehouse queries
│   ├── pinecone_mcp_server       # Vector database operations
│   ├── linear_mcp_server         # Project management
│   ├── claude_mcp_server         # Claude AI integration
│   ├── retool_mcp_server         # Dashboard automation
│   ├── docker_mcp_server         # Container management
│   ├── pulumi_mcp_server         # Infrastructure automation
│   └── knowledge_mcp_server      # Knowledge base management
├── Remote MCP Servers
│   ├── github.com/modelcontextprotocol/servers
│   └── Custom enterprise MCP servers
└── MCP Gateway
    └── Unified MCP client for all servers
```

### **MCP Server Categories**

1. **Data & Analytics MCP Servers**
   - `gong_mcp_server`: Sales call analysis and insights
   - `snowflake_mcp_server`: Data warehouse queries and analytics
   - `apollo_mcp_server`: Sales intelligence and prospecting

2. **AI & Knowledge MCP Servers**
   - `ai_memory_mcp_server`: Persistent conversation memory
   - `claude_mcp_server`: Claude AI capabilities
   - `knowledge_mcp_server`: RAG and knowledge base
   - `codebase_awareness_mcp_server`: Code understanding

3. **Integration MCP Servers**
   - `slack_mcp_server`: Team communication
   - `linear_mcp_server`: Project management
   - `hubspot_mcp_server`: CRM operations
   - `intercom_mcp_server`: Customer support

4. **Infrastructure MCP Servers**
   - `pulumi_mcp_server`: Infrastructure as Code
   - `docker_mcp_server`: Container management
   - `lambda_labs_mcp_server`: Compute resources
   - `vercel_mcp_server`: Frontend deployment

## 📁 Project Structure

```
sophia-main/
├── backend/                      # Python backend services
│   ├── agents/                   # AI agent implementations
│   │   ├── core/                # Base agent classes
│   │   └── specialized/         # Domain-specific agents
│   ├── mcp/                     # MCP server implementations
│   ├── integrations/            # External service integrations
│   ├── app/                     # FastAPI application
│   │   └── routes/             # API endpoints
│   ├── knowledge/               # Knowledge base & RAG
│   ├── pipeline/                # Data pipeline architecture
│   └── core/                    # Core utilities
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   └── services/           # API clients
│   └── knowledge-admin/        # Knowledge management UI
├── infrastructure/              # Pulumi IaC
│   ├── components/             # Infrastructure components
│   ├── esc/                    # Secret management
│   └── pulumi/                 # Service configurations
├── scripts/                     # Automation scripts
│   ├── dev/                    # Development utilities
│   └── deploy/                 # Deployment scripts
├── tests/                       # Test suites
│   ├── infrastructure/         # IaC tests
│   ├── integration/            # Integration tests
│   └── api/                    # API tests
├── docs/                        # Documentation
├── database/                    # Database schemas
│   └── init/                   # SQL initialization
└── mcp-config/                  # MCP configurations
```

## 🚀 Key Features & Capabilities

### **1. Executive Intelligence Dashboard**
- Real-time KPI monitoring
- AI-generated insights and alerts
- Revenue and client health tracking
- Team performance analytics

### **2. Multi-Agent AI System**
- **Executive Agent**: Strategic insights and summaries
- **Sales Coach Agent**: Call analysis and coaching
- **Client Health Agent**: Customer success monitoring
- **Research Agent**: Market intelligence gathering
- **HR Agent**: Team analytics and insights
- **Marketing Agent**: Campaign performance

### **3. Intelligent Integrations**
- **Gong.io**: Automatic call transcription and analysis
- **Slack**: Real-time notifications and commands
- **HubSpot**: CRM synchronization
- **Snowflake**: Data warehouse analytics
- **Linear**: Project management automation

### **4. Knowledge Management**
- Vector-based semantic search
- Document ingestion and chunking
- RAG (Retrieval Augmented Generation)
- Persistent AI memory across sessions

### **5. Infrastructure Automation**
- One-command deployment with Pulumi
- Automated secret management
- CI/CD pipelines with GitHub Actions
- Multi-environment support

## 🔧 Development Workflow

### **Local Development**
```bash
# Start backend
python scripts/start_backend_simple.py

# Run MCP servers
python scripts/start_mcp_servers.py

# Launch frontend
cd frontend && npm start

# Run tests
pytest tests/
```

### **Infrastructure Management**
```bash
# Deploy infrastructure
pulumi up

# Manage secrets
python infrastructure/esc/setup_all_secrets_once.py

# Sync configurations
bash scripts/sync_from_github_org_secrets.py
```

### **MCP Server Usage**
```bash
# Test MCP server
python scripts/dev/simple_mcp_check.py

# Use MCP in code
from backend.mcp.mcp_client import MCPClient
client = MCPClient("gong_mcp_server")
result = await client.call_tool("get_recent_calls", {"limit": 10})
```

## 🎯 Business Value

1. **Executive Visibility**: Real-time business intelligence
2. **Sales Optimization**: AI-powered coaching and insights
3. **Operational Efficiency**: Automated workflows and integrations
4. **Data-Driven Decisions**: Unified analytics platform
5. **Scalable Architecture**: Enterprise-ready infrastructure

## 🔐 Security & Compliance

- **Secret Management**: Pulumi ESC for all credentials
- **Authentication**: API key and OAuth2 support
- **Encryption**: TLS for all communications
- **Audit Logging**: Comprehensive activity tracking
- **Access Control**: Role-based permissions

## 📈 Performance & Scalability

- **Async Architecture**: High-performance async Python
- **Caching**: Redis for frequently accessed data
- **Vector Search**: Sub-50ms semantic search
- **Auto-scaling**: Kubernetes-ready architecture
- **Load Balancing**: Built-in support for horizontal scaling

## 🌟 Unique Differentiators

1. **MCP Protocol**: Standardized AI-to-service communication
2. **Multi-Agent Orchestration**: Specialized AI agents for each domain
3. **Pulumi IaC**: Complete infrastructure as code
4. **Unified Platform**: Single source of truth for business intelligence
5. **AI Memory**: Persistent context across all interactions

This architecture provides Pay Ready with a comprehensive, scalable, and intelligent platform that serves as the central nervous system for their business operations.
