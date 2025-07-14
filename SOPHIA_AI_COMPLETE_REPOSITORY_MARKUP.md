# 🚀 Sophia AI Complete Repository Markup
*Current as of: July 11, 2025 (Post PR #185 Merge)*

## 📋 Executive Summary

**Sophia AI** is an enterprise-grade AI assistant orchestrator platform for Pay Ready company, featuring:
- **2,007+ files** across **422+ directories**
- **53 MCP (Model Context Protocol) servers** for comprehensive integrations
- **11 strategic external repositories** (22k+ combined stars)
- **Microservices architecture** with Kubernetes (K3s) deployment
- **Multi-cloud infrastructure** (Lambda Labs, Vercel, AWS)

## 🏗️ Complete Repository Structure

### 📂 Root Directory Layout

```
sophia-main/
├── 📁 api/                          # Modular API endpoints for serverless deployment
├── 📁 apps/                         # Future monorepo applications (Target: Feb 2025)
├── 📁 archive/                      # Organized historical files (192 archived)
├── 📁 backend/                      # Core Python backend services [PRIMARY]
├── 📁 claude-cli-integration/       # Claude CLI with MCP integration
├── 📁 config/                       # Central configuration management
├── 📁 configs/                      # Additional config files
├── 📁 core/                         # Domain logic and business rules
├── 📁 database/                     # Database schemas and migrations
├── 📁 deployment/                   # Deployment configurations
├── 📁 docker/                       # Docker configurations
├── 📁 docs/                         # Comprehensive documentation (540+ files)
├── 📁 domain/                       # Domain-driven design entities
├── 📁 estuary-config/               # Estuary Flow ETL configurations
├── 📁 external/                     # Strategic external repositories
├── 📁 frontend/                     # React/TypeScript web application
├── 📁 gemini-cli-integration/       # Gemini CLI with MCP integration
├── 📁 gong-webhook-service/         # Gong.io webhook handler
├── 📁 implementation_scripts/       # Implementation automation
├── 📁 infrastructure/               # Pulumi IaC definitions
├── 📁 k3s-manifests/                # K3s Kubernetes manifests
├── 📁 k8s/                          # Kubernetes configurations
├── 📁 kubernetes/                   # Extended K8s resources
├── 📁 libs/                         # Future shared libraries (Target: Feb 2025)
├── 📁 logs/                         # Application logs
├── 📁 mcp-config/                   # MCP server configurations
├── 📁 mcp-servers/                  # 53 MCP server implementations
├── 📁 monitoring/                   # Monitoring stack (Prometheus/Grafana)
├── 📁 n8n-integration/              # N8N workflow automation
├── 📁 npm-mcp-servers/              # NPM-based MCP servers
├── 📁 pulumi/                       # Pulumi project files
├── 📁 scripts/                      # Automation and deployment scripts
├── 📁 security/                     # Security configurations
├── 📁 security_patches/             # Security patch implementations
├── 📁 shared/                       # Shared utilities and components
├── 📁 sophia_admin_api/             # Admin API service
├── 📁 sophia-chrome-extension/      # Chrome browser extension
├── 📁 sophia-quick-deploy/          # Quick deployment utilities
├── 📁 sophia-vscode-extension/      # VS Code extension
├── 📁 static/                       # Static assets
├── 📁 tests/                        # Test suites
├── 📁 ui-ux-agent/                  # UI/UX design automation
├── 📄 .cursorrules                  # Cursor AI development rules
├── 📄 .gitignore                    # Git ignore patterns
├── 📄 CHANGELOG.md                  # Version history
├── 📄 CLEANUP_REPORT_20250711_202643.json  # Cleanup audit trail
├── 📄 CLEANUP_SUCCESS_SUMMARY.md    # Cleanup results
├── 📄 Dockerfile                    # Main Docker configuration
├── 📄 Dockerfile.backend             # Backend-specific Docker
├── 📄 docker-compose.lambda.yml     # Lambda Labs composition
├── 📄 docker-compose.yml            # Docker composition
├── 📄 Makefile                      # Build automation
├── 📄 PR_185_MERGE_COMPLETE.md      # PR merge documentation
├── 📄 README.md                     # Project overview
├── 📄 REPOSITORY_STRUCTURE.md       # Structure documentation
├── 📄 activate_env.sh               # Environment activation
├── 📄 activate_sophia.sh            # Sophia activation script
├── 📄 pyproject.toml                # Python project config (UV)
├── 📄 render.yaml                   # Render deployment config
├── 📄 requirements.txt              # Python dependencies
├── 📄 uv.lock                       # UV dependency lock (516KB)
└── 📄 vercel.json                   # Vercel deployment config
```

## 🔍 Detailed Directory Analysis

### 🧠 Backend Services (`backend/`)

```
backend/
├── 📁 _deprecated/                  # Deprecated but active components
├── 📁 agents/                       # AI agent implementations
│   ├── 📁 core/                     # Base agent framework
│   │   ├── 📄 base_agent.py         # Abstract base agent
│   │   └── 📄 agent_registry.py     # Agent registration
│   └── 📁 specialized/              # Domain-specific agents
│       ├── 📄 call_analysis_agent.py         # Gong call analysis
│       ├── 📄 crm_sync_agent.py             # HubSpot synchronization
│       ├── 📄 notification_agent.py          # Slack notifications
│       ├── 📄 business_intelligence_agent.py # BI insights
│       └── 📄 sales_coach_agent.py          # Sales coaching
├── 📁 api/                          # FastAPI endpoints
│   ├── 📄 main.py                   # API initialization
│   ├── 📄 chat_endpoints.py         # Chat API routes
│   ├── 📄 mcp_endpoints.py          # MCP server routes
│   └── 📄 health_endpoints.py       # Health checks
├── 📁 app/                          # Application entry
│   ├── 📄 fastapi_app.py            # FastAPI application
│   └── 📄 unified_chat_backend.py   # Chat backend
├── 📁 core/                         # Core business logic
│   ├── 📄 auto_esc_config.py        # 🔑 Pulumi ESC integration
│   ├── 📄 date_time_manager.py      # Date/time utilities
│   ├── 📄 config_validator.py       # Configuration validation
│   └── 📄 deployment_validator.py   # Deployment validation
├── 📁 etl/                          # ETL pipelines
│   ├── 📁 airbyte/                  # Airbyte configurations
│   ├── 📁 netsuite/                 # NetSuite integration
│   └── 📁 payready_core/            # Core data ETL
├── 📁 integrations/                 # External integrations
│   ├── 📄 gong_integration.py       # Gong.io API
│   ├── 📄 hubspot_integration.py    # HubSpot CRM
│   └── 📄 slack_integration.py      # Slack API
├── 📁 mcp_servers/                  # MCP server base
├── 📁 middleware/                   # Request middleware
├── 📁 monitoring/                   # Monitoring tools
├── 📁 security/                     # Security components
│   └── 📄 unified_service_auth_manager.py  # Auth management
├── 📁 services/                     # Business services
│   ├── 📄 unified_memory_service.py          # 🧠 Memory management
│   ├── 📄 unified_chat_service.py            # 💬 Chat orchestration
│   ├── 📄 modern_stack_cortex_service.py        # 🏔️ Modern Stack AI
│   ├── 📄 mcp_orchestration_service.py       # MCP coordination
│   ├── 📄 predictive_automation_service.py   # Automation
│   └── 📄 portkey_gateway.py                 # LLM routing
├── 📁 tests/                        # Backend tests
└── 📁 utils/                        # Utilities
    └── 📄 lambda_cost_tracker.py    # Cost monitoring
```

### 🌐 Frontend Application (`frontend/`)

```
frontend/
├── 📁 knowledge-admin/              # Knowledge base admin UI
├── 📁 public/                       # Static assets
├── 📁 src/                          # Source code
│   ├── 📁 components/               # React components
│   │   ├── 📄 UnifiedDashboard.tsx  # 🎯 Main dashboard
│   │   ├── 📄 UnifiedChatDashboard.tsx  # Chat interface
│   │   ├── 📄 ErrorBoundary.tsx     # Error handling
│   │   └── 📁 dashboard/            # Dashboard components
│   │       ├── 📄 KPICards.tsx      # KPI widgets
│   │       └── 📄 RevenueChart.tsx   # Revenue charts
│   ├── 📁 pages/                    # Page components
│   ├── 📁 services/                 # API services
│   │   └── 📄 apiClient.js          # 🔑 Single API client
│   ├── 📁 styles/                   # Styling
│   ├── 📁 utils/                    # Utilities
│   ├── 📄 App.tsx                   # App entry
│   ├── 📄 main.tsx                  # Main entry
│   └── 📄 index.css                 # Global styles
├── 📄 .env.local.template           # Environment template
├── 📄 components.json               # UI components config
├── 📄 index.html                    # HTML entry
├── 📄 package.json                  # Dependencies
├── 📄 package-lock.json             # Lock file
├── 📄 tsconfig.json                 # TypeScript config
├── 📄 vite.config.ts                # Vite configuration
└── 📄 vercel.json                   # Vercel settings
```

### 🔌 MCP Servers (`mcp-servers/`) - 53 Integration Points

```
mcp-servers/
├── 📁 ai_memory/                    # AI memory management
├── 📁 asana/                        # Asana project management
├── 📁 base/                         # Base MCP classes
├── 📁 cline-mcp/                    # Cline v3.18 integration
├── 📁 codacy/                       # Code quality analysis
├── 📁 docker/                       # Docker management
├── 📁 estuary/                      # Estuary Flow ETL
├── 📁 figma/                        # Figma design integration
├── 📁 figma-dev-mode/               # Figma development mode
├── 📁 github/                       # GitHub integration
├── 📁 gong/                         # Gong.io integration
├── 📁 hubspot/                      # HubSpot CRM
├── 📁 huggingface/                  # HuggingFace models
├── 📁 lambda_labs_cli/              # Lambda Labs CLI
├── 📁 linear/                       # Linear project tracking
├── 📁 memory/                       # Memory persistence
├── 📁 n8n/                          # N8N workflows
├── 📁 notion/                       # Notion workspace
├── 📁 openai/                       # OpenAI integration
├── 📁 portkey_admin/                # Portkey administration
├── 📁 pulumi/                       # Pulumi IaC
├── 📁 slack/                        # Slack communication
├── 📁 modern_stack_admin/              # Modern Stack admin
├── 📁 modern_stack_cli_enhanced/       # Enhanced Modern Stack CLI
├── 📁 modern_stack_unified/            # Unified Modern Stack
├── 📁 sophia_business/              # Business intelligence
├── 📁 sophia_data/                  # Data management
├── 📁 sophia_infrastructure/        # Infrastructure
├── 📁 sophia_intelligence/          # AI intelligence
├── 📁 temporal/                     # Temporal workflows
├── 📁 ui_ux_agent/                  # UI/UX automation
├── 📁 vercel/                       # Vercel deployment
└── ... (21 additional servers)      # Various integrations
```

### 🏗️ Infrastructure (`infrastructure/`)

```
infrastructure/
├── 📁 adapters/                     # Infrastructure adapters
├── 📁 agents/                       # Infrastructure agents
├── 📁 components/                   # Reusable components
│   ├── 📁 dns/                      # DNS management
│   ├── 📁 k3s/                      # K3s cluster
│   ├── 📁 lambda-labs/              # Lambda Labs
│   ├── 📁 monitoring/               # Monitoring stack
│   ├── 📁 networking/               # Network config
│   └── 📁 storage/                  # Storage config
├── 📁 core/                         # Core infrastructure
├── 📁 database/                     # Database IaC
├── 📁 dns/                          # DNS configurations
├── 📁 esc/                          # Pulumi ESC configs
│   ├── 📄 setup_pulumi_esc.sh       # ESC setup
│   └── 📄 validate_esc_setup.py     # ESC validation
├── 📁 etl/                          # ETL infrastructure
├── 📁 integrations/                 # Service integrations
├── 📁 kubernetes/                   # K8s resources
│   ├── 📁 base/                     # Base resources
│   ├── 📁 helm/                     # Helm charts
│   ├── 📁 kustomize/                # Kustomization
│   └── 📁 manifests/                # Raw manifests
├── 📁 mcp/                          # MCP infrastructure
├── 📁 monitoring/                   # Monitoring setup
│   ├── 📄 prometheus_config.py      # Prometheus
│   └── 📄 grafana_dashboards.py     # Grafana
├── 📁 n8n/                          # N8N infrastructure
├── 📁 providers/                    # Cloud providers
├── 📁 pulumi/                       # Pulumi projects
├── 📁 security/                     # Security infrastructure
│   ├── 📁 policies/                 # Security policies
│   └── 📁 secrets/                  # Secret management
├── 📁 services/                     # Service definitions
├── 📁 modern_stack_iac/                # Modern Stack IaC
├── 📁 modern_stack_setup/              # Modern Stack setup
│   ├── 📁 schemas/                  # Database schemas
│   └── 📁 procedures/               # Stored procedures
├── 📁 templates/                    # IaC templates
├── 📁 vercel/                       # Vercel deployment
├── 📁 websocket/                    # WebSocket infra
├── 📄 Pulumi.yaml                   # Pulumi project
├── 📄 Pulumi.prod.yaml              # Production stack
├── 📄 index.ts                      # Main IaC entry
└── 📄 package.json                  # Node dependencies
```

### 📜 Scripts (`scripts/`)

```
scripts/
├── 📁 ai/                           # AI-related scripts
├── 📁 analysis/                     # Analysis tools
├── 📁 automation/                   # Automation scripts
├── 📁 ci/                           # CI/CD scripts
│   └── 📄 sync_from_gh_to_pulumi.py # Secret sync
├── 📁 deployment/                   # Deployment scripts
│   ├── 📄 deploy_sophia_k3s_battle_plan.sh  # K3s deployment
│   ├── 📄 deploy_sophia_automated.py        # Automated deploy
│   ├── 📄 deploy_lambda_labs_production.py  # Lambda deploy
│   └── 📄 build_sophia_containers.sh        # Container build
├── 📁 etl/                          # ETL scripts
├── 📁 k3s/                          # K3s management
├── 📁 maintenance/                  # Maintenance tools
├── 📁 migration/                    # Migration scripts
├── 📁 monitoring/                   # Monitoring scripts
├── 📁 security/                     # Security scripts
├── 📁 setup/                        # Setup scripts
├── 📁 modern_stack/                    # Modern Stack scripts
├── 📁 testing/                      # Testing scripts
├── 📁 utilities/                    # Utility scripts
├── 📄 activate_sophia_production.py # Production activation
├── 📄 comprehensive_monitoring.py   # Monitoring setup
├── 📄 fix_sophia_quick_wins.py      # Quick fixes
├── 📄 start_all_mcp_servers.py     # MCP startup
└── ... (150+ additional scripts)    # Various utilities
```

### 📚 Documentation (`docs/`)

```
docs/
├── 📁 01-getting-started/           # Onboarding guides
│   └── 📄 QUICKSTART.md             # Quick start guide
├── 📁 02-development/               # Development guides
│   ├── 📄 DEVELOPMENT_WORKFLOW.md   # Dev workflow
│   └── 📄 CODING_STANDARDS.md       # Coding standards
├── 📁 03-architecture/              # Architecture docs
│   ├── 📄 SYSTEM_ARCHITECTURE.md    # System design
│   ├── 📄 CLEAN_ARCHITECTURE.md     # Clean architecture
│   └── 📄 MCP_ARCHITECTURE.md       # MCP design
├── 📁 04-deployment/                # Deployment guides
│   ├── 📄 LAMBDA_LABS_DEPLOYMENT.md # Lambda deployment
│   ├── 📄 K3S_DEPLOYMENT_GUIDE.md   # K3s deployment
│   ├── 📄 VERCEL_DEPLOYMENT.md      # Vercel deployment
│   └── 📄 SERVERLESS_GUIDE.md       # Serverless guide
├── 📁 05-integrations/              # Integration docs
├── 📁 06-mcp-servers/               # MCP documentation
├── 📁 07-performance/               # Performance guides
├── 📁 08-security/                  # Security docs
│   └── 📄 DEPENDENCY_SECURITY_AUDIT.md  # Security audit
├── 📁 99-reference/                 # Reference materials
│   ├── 📄 PERMANENT_SECRET_MANAGEMENT.md  # Secret management
│   └── 📄 UNIFIED_AI_AGENT_AUTH.md      # Auth system
├── 📁 ai-coding/                    # AI development
├── 📁 ai-context/                   # AI context docs
├── 📁 architecture/                 # Detailed architecture
├── 📁 deployment/                   # Deployment details
│   ├── 📄 BACKEND_DEPLOYMENT_OPTIONS.md
│   ├── 📄 LAMBDA_LABS_DEPLOYMENT_SUCCESS.md
│   └── 📄 VERCEL_DEPLOYMENT_STATUS.md
├── 📁 implementation/               # Implementation guides
├── 📁 monorepo/                     # Monorepo transition
├── 📁 sample_queries/               # Example queries
├── 📁 system_handbook/              # 📚 MASTER DOCUMENTATION
│   ├── 📄 00_SOPHIA_AI_SYSTEM_HANDBOOK.md  # 🎯 Single source of truth
│   ├── 📄 01_PHOENIX_ARCHITECTURE.md       # Phoenix architecture
│   ├── 📄 02_MCP_ECOSYSTEM.md              # MCP ecosystem
│   ├── 📄 03_modern_stack_INTEGRATION.md      # Modern Stack guide
│   ├── 📄 04_AI_MEMORY_SYSTEM.md           # Memory system
│   ├── 📄 05_DEPLOYMENT_INFRASTRUCTURE.md  # Infrastructure
│   ├── 📄 06_SECURITY_FRAMEWORK.md         # Security
│   ├── 📄 07_PERFORMANCE_OPTIMIZATION.md   # Performance
│   ├── 📄 08_MEMORY_AUGMENTED_ARCHITECTURE.md # Memory architecture
│   └── 📄 09_AI_SQL_CORTEX_AGENT_LIFECYCLE.md # AI SQL
└── ... (540+ documentation files)
```

### 🌟 External Strategic Repositories (`external/`)

```
external/
├── 📁 anthropic-mcp-inspector/      # MCP debugging tools
│   └── Official MCP inspection and debugging
├── 📁 anthropic-mcp-python-sdk/     # Official Python SDK
│   └── Core MCP protocol implementation
├── 📁 anthropic-mcp-servers/        # Official MCP servers
│   └── Reference implementations
├── 📁 glips_figma_context/          # Design-to-code (8.7k⭐)
│   └── Figma integration for code generation
├── 📁 microsoft_playwright/         # Browser automation (13.4k⭐)
│   └── Web automation and testing
├── 📁 modern_stack_cortex_official/    # Modern Stack AI
│   └── Official Cortex AI integration
├── 📁 portkey_admin/                # AI gateway
│   └── LLM routing and optimization
├── 📁 openrouter_search/            # Model search
│   └── 200+ AI model discovery
├── 📁 davidamom_modern_stack/          # Modern Stack patterns
├── 📁 dynamike_modern_stack/           # Performance patterns
└── 📁 isaacwasserman_modern_stack/     # Advanced Modern Stack
```

## 🔑 Key Configuration Files

### 🐍 Python Configuration
- `pyproject.toml` - Modern Python project configuration with UV
- `uv.lock` - Locked dependencies (516KB, 231 packages)
- `requirements.txt` - Legacy dependency list
- `.python-version` - Python 3.12 specification

### 🏗️ Infrastructure Configuration
- `infrastructure/Pulumi.yaml` - Pulumi project definition
- `infrastructure/pulumi-esc-config.yaml` - ESC secret management
- `config/cursor_enhanced_mcp_config.json` - MCP server registry
- `config/consolidated_mcp_ports.json` - MCP port assignments

### 🌐 Frontend Configuration
- `frontend/package.json` - Node.js dependencies
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/vite.config.ts` - Vite build settings
- `frontend/vercel.json` - Vercel deployment

### 🐳 Container Configuration
- `Dockerfile` - Main container definition
- `Dockerfile.backend` - Backend-specific container
- `docker-compose.yml` - Local development
- `docker-compose.lambda.yml` - Lambda Labs deployment

### 🔧 Development Tools
- `.cursorrules` - Cursor AI development rules
- `.gitignore` - Git ignore patterns
- `.codacy.yml` - Code quality settings
- `Makefile` - Build automation

## 📊 Repository Statistics

### 📈 Scale Metrics
- **Total Files**: 2,007+ files
- **Total Directories**: 422+ directories
- **Python Files**: 821 source files
- **TypeScript Files**: 150+ files
- **Documentation**: 540+ markdown files
- **Test Files**: 43 files with tests
- **Configuration Files**: 150+ configs

### 💻 Technology Stack
- **Backend**: Python 3.12, FastAPI, UV
- **Frontend**: React 18, TypeScript, Vite
- **Infrastructure**: Pulumi, Kubernetes (K3s)
- **Database**: Modern Stack, PostgreSQL, Redis
- **AI/ML**: OpenAI, Anthropic, Lambda GPU
- **Monitoring**: Prometheus, Grafana
- **CI/CD**: GitHub Actions

### 🌐 Integration Ecosystem
- **MCP Servers**: 53 active integrations
- **External Repos**: 11 strategic repositories
- **API Endpoints**: 56+ REST endpoints
- **WebSocket Channels**: Real-time communication
- **Workflow Automation**: N8N integration

## 🚀 Deployment Architecture

### 🖥️ Infrastructure Targets
1. **Lambda Labs** (Primary)
   - 3 GPU-enabled servers
   - K3s Kubernetes cluster
   - IP: 104.171.202.103, 192.222.58.232, 104.171.202.117

2. **Vercel** (Frontend)
   - React application hosting
   - Domain: sophia-intel.ai
   - Automatic deployments

3. **AWS Lambda** (Serverless)
   - API endpoints
   - Background jobs
   - Event processing

### 🔐 Security & Secrets
- **Pulumi ESC**: Primary secret management
- **GitHub Secrets**: Organization-level secrets
- **Environment Variables**: Fallback only
- **Zero hardcoded secrets**: Enforced by policy

## 🎯 Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install UV
uv sync --all-extras  # Install dependencies

# Environment setup
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
source activate_sophia.sh

# Start backend
cd backend && uv run python -m uvicorn app.fastapi_app:app --reload

# Start frontend
cd frontend && npm install && npm run dev

# Deploy to production (via GitHub Actions)
git push origin main
```

## 📝 Repository Health

### ✅ Strengths
- Clean, organized structure (41% reduction in root clutter)
- Comprehensive documentation (540+ files)
- Enterprise-grade security
- Modern tooling (UV, Ruff, Black)
- Active development (daily commits)

### 🔄 Areas for Enhancement
- Test coverage expansion needed
- Some pre-commit hook compliance
- 3 security vulnerabilities via Dependabot
- External submodule management

## 🎉 Conclusion

The Sophia AI repository represents a **world-class, enterprise-grade AI platform** with:
- ✅ **Professional Organization**: Clean architecture, clear separation
- ✅ **Comprehensive Integration**: 53 MCP servers, 11 external repos
- ✅ **Modern Infrastructure**: K3s, Pulumi, multi-cloud deployment
- ✅ **Enterprise Security**: Zero hardcoded secrets, ESC integration
- ✅ **Active Development**: Continuous improvements and deployment

**Ready for unlimited scaling and production deployment!** 🚀

---
*Generated: July 11, 2025*  
*Version: Post PR #185 Merge*  
*Status: Current and Complete* 