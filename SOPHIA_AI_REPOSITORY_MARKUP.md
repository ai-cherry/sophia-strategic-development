# 📁 Sophia AI Complete Repository Markup
**Date:** December 2024  
**Repository:** sophia-main  
**Status:** Production Active

## 📊 Repository Statistics

| Metric | Count |
|--------|-------|
| Total Directories | 541 (excluding .venv, node_modules, .git) |
| Python Files | 7,498 |
| TypeScript/JavaScript Files | ~2,000 |
| MCP Servers | 50+ |
| External Repositories | 11 |
| Docker Containers | 25+ |
| Configuration Files | 200+ |
| Documentation Files | 324 |

## 🏗️ Repository Structure

```
sophia-main/
│
├── 🔧 Core Infrastructure
│   ├── infrastructure/          # Pulumi IaC, Kubernetes, monitoring
│   ├── kubernetes/             # K8s manifests, Helm charts
│   ├── k8s/                    # Additional K8s configurations
│   ├── k3s-manifests/          # K3s specific manifests
│   └── deployment/             # Docker compose files
│
├── 🐍 Backend Systems
│   ├── backend/                # Core backend application
│   │   ├── agents/            # AI agents
│   │   ├── api/              # API routes and endpoints
│   │   ├── app/              # FastAPI application
│   │   ├── core/             # Core utilities and config
│   │   ├── etl/              # ETL pipelines (Airbyte, custom)
│   │   ├── integrations/     # External service integrations
│   │   ├── mcp_servers/      # MCP server implementations
│   │   ├── middleware/       # API middleware
│   │   ├── monitoring/       # Performance monitoring
│   │   ├── security/         # Security implementations
│   │   ├── services/         # Business logic services
│   │   ├── tests/            # Backend tests
│   │   └── utils/            # Utility functions
│   │
│   ├── core/                   # Domain logic (Clean Architecture)
│   │   ├── agents/           # Agent base classes
│   │   ├── application/      # Use cases
│   │   ├── infra/           # Infrastructure interfaces
│   │   ├── ports/           # Port definitions
│   │   ├── services/        # Domain services
│   │   ├── use_cases/       # Business use cases
│   │   └── workflows/       # LangGraph workflows
│   │
│   ├── shared/                 # Shared utilities
│   │   ├── agents/          # Shared agent code
│   │   ├── monitoring/      # Shared monitoring
│   │   ├── prompts/         # AI prompts
│   │   ├── security/        # Shared security
│   │   └── utils/           # Shared utilities
│   │
│   └── domain/                 # Domain models
│       ├── entities/        # Business entities
│       ├── events/          # Domain events
│       ├── models/          # Domain models
│       └── value_objects/   # Value objects
│
├── 🌐 Frontend Systems
│   ├── frontend/              # React frontend application
│   │   ├── src/
│   │   │   ├── components/  # React components
│   │   │   ├── pages/      # Page components
│   │   │   ├── services/   # API services
│   │   │   ├── hooks/      # Custom React hooks
│   │   │   ├── utils/      # Frontend utilities
│   │   │   └── types/      # TypeScript types
│   │   ├── knowledge-admin/ # Knowledge admin UI
│   │   └── scripts/        # Build scripts
│   │
│   ├── ui-ux-agent/          # UI/UX automation agent
│   └── static/               # Static HTML files
│
├── 🤖 MCP Servers (50+ servers)
│   └── mcp-servers/
│       ├── ai_memory/        # AI memory management
│       ├── asana/           # Asana integration
│       ├── claude_desktop/  # Claude desktop integration
│       ├── codacy/          # Code quality
│       ├── figma/           # Design integration
│       ├── github/          # GitHub integration
│       ├── gong/            # Call intelligence
│       ├── hubspot/         # CRM integration
│       ├── lambda_labs/     # GPU management
│       ├── linear/          # Project management
│       ├── notion/          # Documentation
│       ├── portkey_admin/   # LLM gateway
│       ├── slack/           # Team communication
│       ├── ELIMINATED/       # Data warehouse
│       ├── ui_ux_agent/     # UI automation
│       └── [40+ more servers...]
│
├── 🔌 External Integrations
│   ├── external/             # Strategic external repositories
│   │   ├── anthropic-mcp-inspector/
│   │   ├── anthropic-mcp-python-sdk/
│   │   ├── anthropic-mcp-servers/
│   │   └── glips_figma_context/
│   │
│   ├── claude-cli-integration/   # Claude CLI
│   ├── gemini-cli-integration/   # Gemini CLI
│   ├── estuary-config/          # Estuary Flow configs
│   ├── n8n-integration/         # N8N workflows
│   └── npm-mcp-servers/         # NPM-based MCP servers
│
├── 📋 Configuration
│   ├── config/               # Application configurations
│   │   ├── enhanced_chat/   # Chat configurations
│   │   ├── estuary/        # Data pipeline configs
│   │   ├── grafana/        # Monitoring dashboards
│   │   ├── mcp/            # MCP server configs
│   │   ├── mem0/           # Memory configs
│   │   ├── portkey/        # LLM gateway configs
│   │   ├── prometheus/     # Metrics configs
│   │   ├── pulumi/         # Infrastructure configs
│   │   └── services/       # Service configs
│   │
│   ├── configs/              # Additional configs
│   └── security/             # Security configurations
│
├── 🗄️ Database
│   ├── database/             # Database schemas and migrations
│   │   └── init/           # Initial schemas
│   │
│   └── scripts/              # Database scripts
│       └── [Various SQL scripts]
│
├── 🔧 Scripts & Tools
│   ├── scripts/              # Utility scripts (100+)
│   │   ├── automation/     # Automation scripts
│   │   ├── backup/         # Backup utilities
│   │   ├── ci/             # CI/CD scripts
│   │   ├── data_pipeline/  # ETL scripts
│   │   ├── deployment/     # Deployment scripts
│   │   ├── integrations/   # Integration scripts
│   │   ├── knowledge_base/ # Knowledge management
│   │   ├── lambda_labs/    # GPU management
│   │   ├── mcp/           # MCP utilities
│   │   ├── migration/      # Migration scripts
│   │   ├── monitoring/     # Monitoring scripts
│   │   ├── one_time/       # One-time scripts
│   │   ├── pulumi/         # Infrastructure scripts
│   │   ├── security/       # Security scripts
│   │   └── utils/          # General utilities
│   │
│   └── implementation_scripts/  # Setup scripts
│
├── 📚 Documentation
│   ├── docs/                 # Main documentation
│   │   ├── 01-getting-started/
│   │   ├── 02-development/
│   │   ├── 03-architecture/
│   │   ├── 04-deployment/
│   │   ├── 05-integrations/
│   │   ├── 06-mcp-servers/
│   │   ├── 07-performance/
│   │   ├── 08-security/
│   │   ├── 99-reference/
│   │   ├── ai-coding/
│   │   ├── ai-context/
│   │   ├── architecture/
│   │   ├── deployment/
│   │   ├── implementation/
│   │   ├── monorepo/
│   │   ├── pdf/
│   │   ├── sample_queries/
│   │   └── system_handbook/
│   │
│   └── [Root-level documentation files]
│
├── 🧪 Testing
│   ├── tests/               # Test suites
│   │   ├── api/           # API tests
│   │   ├── integration/   # Integration tests
│   │   ├── mcp/          # MCP server tests
│   │   └── unit/         # Unit tests
│   │
│   └── [Test configurations]
│
├── 🐳 Docker & Containers
│   ├── docker/              # Dockerfiles
│   ├── deployment/          # Docker compose files
│   └── [Various Dockerfiles]
│
├── 📊 Monitoring & Observability
│   ├── monitoring/          # Monitoring configurations
│   ├── grafana/            # Grafana dashboards
│   └── prometheus/         # Prometheus configs
│
├── 🔐 Security
│   ├── security/           # Security implementations
│   └── security_patches/   # Security patches
│
├── 🚀 Chrome Extensions
│   ├── sophia-chrome-extension/  # Chrome extension
│   └── sophia-vscode-extension/  # VS Code extension
│
├── 📦 Build & Deploy
│   ├── .github/            # GitHub Actions workflows
│   │   └── workflows/     # CI/CD pipelines
│   │
│   ├── pulumi/             # Pulumi projects
│   └── sophia-quick-deploy/ # Quick deployment scripts
│
└── 📄 Root Files
    ├── .cursorrules        # Cursor AI rules
    ├── pyproject.toml      # Python project config
    ├── uv.lock            # UV dependency lock
    ├── package.json       # Node.js dependencies
    ├── requirements.txt   # Python dependencies
    ├── README.md         # Project documentation
    └── [Various configs and scripts]
```

## 🏢 Key Directories Explained

### `/backend`
Core backend application with FastAPI, containing:
- **38 service modules** for business logic
- **11 core configuration files**
- **12 API route modules**
- **4 integration modules** (Gong, HubSpot, Slack, etc.)

### `/mcp-servers`
50+ Model Context Protocol servers including:
- **AI Memory Server** - Persistent memory management
- **Codacy Server** - Code quality analysis
- **GitHub Server** - Repository management
- **Linear Server** - Project tracking
- **Slack Server** - Team communication
- **Modern Stack Server** - Data warehouse access

### `/infrastructure`
Complete infrastructure as code:
- **47 service modules** in `/services`
- **10 Pulumi TypeScript modules**
- **8 Kubernetes directories** with manifests
- **15 Python ETL/integration modules**

### `/scripts`
Over 100 utility scripts organized by function:
- **Deployment automation**
- **Database migrations**
- **MCP server management**
- **Monitoring and alerts**
- **Security scanning**
- **One-time operations**

### `/external`
Strategic external repositories:
- **Microsoft Playwright** (13.4k stars) - Browser automation
- **GLips Figma Context** (8.7k stars) - Design integration
- **Anthropic MCP SDK** - Official MCP implementation
- **Lambda GPU** - AI/ML integrations

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** - Primary language
- **FastAPI** - Web framework
- **LangChain/LangGraph** - AI orchestration
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **UV** - Dependency management

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Vite** - Build tool
- **Chart.js** - Data visualization

### Infrastructure
- **Lambda Labs** - GPU compute (5 servers)
- **Kubernetes/K3s** - Container orchestration
- **Docker** - Containerization
- **Pulumi** - Infrastructure as Code
- **GitHub Actions** - CI/CD

### Databases
- **PostgreSQL** - Primary database with pgvector
- **Weaviate** - Vector database
- **Redis** - Caching layer
- **Modern Stack** - Data warehouse (legacy)

### AI/ML
- **OpenAI GPT-4** - Language model
- **Claude 3.5** - Language model
- **Lambda GPU** - Embeddings (migrating away)
- **Lambda GPU** - Model inference
- **Portkey** - LLM gateway

## 📈 Code Quality Metrics

### Language Distribution
- **Python**: 75%
- **TypeScript**: 15%
- **SQL**: 5%
- **YAML/JSON**: 3%
- **Other**: 2%

### Test Coverage
- **Unit Tests**: 43 test files
- **Integration Tests**: 15+ test suites
- **API Tests**: Comprehensive coverage
- **MCP Tests**: Server-specific tests

### Documentation
- **324 Markdown files**
- **Comprehensive API docs**
- **System handbook**
- **Architecture diagrams**
- **Deployment guides**

## 🚀 Deployment Architecture

### Production Infrastructure
- **5 Lambda Labs GPU Servers**
  - sophia-production-instance (104.171.202.103)
  - sophia-ai-core (192.222.58.232)
  - sophia-mcp-orchestrator (104.171.202.117)
  - sophia-data-pipeline (104.171.202.134)
  - sophia-development (155.248.194.183)

### Services Deployed
- **PostgreSQL** (Port 5432)
- **Redis** (Port 6379)
- **Weaviate** (Port 8080)
- **FastAPI Backend** (Port 8000)
- **React Frontend** (Port 3000)
- **50+ MCP Servers** (Ports 3000-9999)

### CI/CD Pipeline
- **GitHub Actions** for automation
- **Pulumi** for infrastructure
- **Docker Hub** for images
- **Vercel** for frontend hosting

## 🔒 Security Features

- **Pulumi ESC** for secrets management
- **GitHub Organization Secrets**
- **Row-level security** in PostgreSQL
- **API authentication** with JWT
- **Network isolation** between services
- **SSL/TLS** encryption everywhere

## 📊 Active Development Areas

1. **Memory Architecture Migration**
   - Moving from Modern Stack to Weaviate
   - GPU-accelerated embeddings
   - 3-tier caching strategy

2. **MCP Server Consolidation**
   - Reducing from 50+ to ~30 servers
   - Standardizing implementations
   - Improving performance

3. **Frontend Enhancement**
   - CEO dashboard improvements
   - Real-time data visualization
   - Mobile responsiveness

4. **Infrastructure Optimization**
   - Cost reduction strategies
   - Performance improvements
   - Monitoring enhancements

## 🎯 Repository Best Practices

1. **Code Organization**
   - Clean Architecture principles
   - Domain-driven design
   - Microservices architecture

2. **Development Workflow**
   - Feature branches
   - Pull request reviews
   - Automated testing
   - Continuous deployment

3. **Documentation Standards**
   - README for each module
   - API documentation
   - Architecture decisions
   - Deployment guides

4. **Security Practices**
   - No hardcoded secrets
   - Regular dependency updates
   - Security scanning
   - Access control 