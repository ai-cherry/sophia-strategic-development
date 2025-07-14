# 📁 Sophia AI Repository Structure

## 🎯 Repository Overview

**Sophia AI** is an advanced AI assistant orchestrator for Pay Ready company, featuring a comprehensive microservices architecture with 2,007+ files across 422+ directories. This document provides a complete guide to the repository structure after the successful cleanup implementation.

---

## 🏗️ Root Directory Structure

```
sophia-ai/
├── 📁 api/                          # API configurations and endpoints
├── 📁 apps/                         # Future monorepo applications (February 2025)
├── 📁 archive/                      # 🆕 Organized archived files (192 files)
├── 📁 backend/                      # Core Python backend services
├── 📁 claude-cli-integration/       # Claude CLI integration tools
├── 📁 config/                       # Configuration files
├── 📁 docs/                         # Comprehensive documentation (540+ MD files)
├── 📁 domain/                       # Domain-specific logic
├── 📁 estuary-config/               # Estuary Flow ETL configurations
├── 📁 external/                     # Strategic external repositories (22k+ stars)
├── 📁 frontend/                     # React/TypeScript frontend
├── 📁 infrastructure/               # Pulumi IaC and deployment configs
├── 📁 libs/                         # Future shared libraries (February 2025)
├── 📁 mcp-servers/                  # 53 MCP servers for integrations
├── 📁 scripts/                      # Utility and deployment scripts
├── 📁 security/                     # Security configurations
├── 📁 security_patches/             # Security patch implementations
├── 📁 shared/                       # Shared utilities and components
├── 📁 sophia-chrome-extension/      # Browser extension
├── 📁 sophia-quick-deploy/          # Quick deployment utilities
├── 📁 sophia-vscode-extension/      # VS Code extension
├── 📁 static/                       # Static assets
├── 📁 tests/                        # Test suites and test data
├── 📁 ui-ux-agent/                  # UI/UX design agent
├── 📄 pyproject.toml                # Python project configuration
├── 📄 uv.lock                       # UV dependency lock file (516KB)
├── 📄 README.md                     # Main project documentation
├── 📄 CHANGELOG.md                  # Version history and changes
├── 📄 Makefile                      # Build and automation commands
└── 📄 .cursorrules                  # Cursor AI development rules
```

---

## 🔍 Core Directories Deep Dive

### 📁 `backend/` - Core Application (PRIMARY)

```
backend/
├── 📁 _deprecated/                  # Deprecated components (preserved - active imports)
├── 📁 agents/                       # AI agent implementations
│   ├── 📁 core/                     # Base agent classes
│   └── 📁 specialized/              # Domain-specific agents
├── 📁 api/                          # FastAPI REST endpoints
├── 📁 app/                          # Application initialization
├── 📁 core/                         # Core business logic
│   ├── 📄 auto_esc_config.py        # 🔑 Pulumi ESC integration
│   └── 📄 date_time_manager.py      # Date/time utilities
├── 📁 etl/                          # Extract, Transform, Load pipelines
├── 📁 integrations/                 # External service integrations
│   ├── 📁 modern_stack/                # Lambda GPU AI integration
│   ├── 📁 gong/                     # Gong.io call analysis
│   └── 📁 hubspot/                  # HubSpot CRM integration
├── 📁 mcp_servers/                  # MCP server implementations
├── 📁 middleware/                   # Request/response middleware
├── 📁 monitoring/                   # Health checks and metrics
├── 📁 security/                     # Authentication and authorization
├── 📁 services/                     # Business service layer
│   ├── 📄 unified_memory_service.py # 🧠 Memory management
│   └── 📄 unified_chat_service.py   # 💬 Chat orchestration
├── 📁 tests/                        # Backend-specific tests
└── 📁 utils/                        # Utility functions
```

### 📁 `docs/` - Comprehensive Documentation

```
docs/
├── 📁 01-getting-started/           # Quick start guides
├── 📁 02-development/               # Development workflows
├── 📁 03-architecture/              # System architecture
├── 📁 04-deployment/                # Deployment guides
├── 📁 05-integrations/              # Integration documentation
├── 📁 06-mcp-servers/               # MCP server documentation
├── 📁 07-performance/               # Performance guidelines
├── 📁 08-security/                  # Security documentation
├── 📁 99-reference/                 # Reference materials
├── 📁 ai-coding/                    # AI-assisted development
├── 📁 ai-context/                   # AI context management
├── 📁 architecture/                 # Detailed architecture docs
├── 📁 archive/                      # Archived documentation
├── 📁 deployment/                   # Deployment strategies
├── 📁 getting-started/              # Onboarding materials
├── 📁 implementation/               # Implementation guides
├── 📁 monorepo/                     # Monorepo transition docs
├── 📁 pdf/                          # PDF documentation
├── 📁 sample_queries/               # Example queries
└── 📁 system_handbook/              # 📚 **MASTER DOCUMENTATION**
    └── 📄 00_SOPHIA_AI_SYSTEM_HANDBOOK.md  # 🎯 Single source of truth
```

### 📁 `infrastructure/` - Infrastructure as Code

```
infrastructure/
├── 📁 adapters/                     # Infrastructure adapters
├── 📁 agents/                       # Infrastructure agents
├── 📁 components/                   # Reusable IaC components
├── 📁 core/                         # Core infrastructure modules
├── 📁 database/                     # Database configurations
├── 📁 dns/                          # DNS configurations
├── 📁 esc/                          # Pulumi ESC configurations
├── 📁 external/                     # External integrations
├── 📁 integrations/                 # Service integrations
├── 📁 kubernetes/                   # K3s cluster configurations
├── 📁 mcp/                          # MCP infrastructure
├── 📁 mcp-gateway/                  # MCP gateway services
├── 📁 monitoring/                   # Monitoring infrastructure
├── 📁 n8n/                          # N8N workflow automation
├── 📁 providers/                    # Cloud provider configs
├── 📁 pulumi/                       # Pulumi project files
├── 📁 security/                     # Security infrastructure
├── 📁 services/                     # Infrastructure services
├── 📁 modern_stack_iac/                # Modern Stack infrastructure
├── 📁 modern_stack_setup/              # Modern Stack setup scripts
├── 📁 templates/                    # Infrastructure templates
├── 📁 vercel/                       # Vercel deployment configs
└── 📁 websocket/                    # WebSocket infrastructure
```

### 📁 `mcp-servers/` - MCP Integration Ecosystem (53 Servers)

```
mcp-servers/
├── 📁 asana/                        # Asana project management
├── 📁 cline-mcp/                    # Cline v3.18 integration
├── 📁 codacy/                       # Code quality analysis
├── 📁 docker/                       # Docker management
├── 📁 estuary/                      # Estuary Flow ETL
├── 📁 figma-dev-mode/               # Figma design integration
├── 📁 gong/                         # Gong.io call analysis
├── 📁 linear/                       # Linear project management
├── 📁 memory/                       # AI memory management
├── 📁 n8n/                          # N8N workflow automation
├── 📁 openai/                       # OpenAI API integration
├── 📁 slack/                        # Slack communication
├── 📁 modern_stack_unified/            # 🏔️ Lambda GPU AI
├── 📁 temporal/                     # Temporal workflow engine
├── 📁 vercel/                       # Vercel deployment
└── 📁 ... (38 additional servers)   # Comprehensive integration suite
```

### 📁 `external/` - Strategic Repository Collection (22k+ Stars)

```
external/
├── 📁 anthropic-mcp-inspector/      # MCP debugging tools
├── 📁 anthropic-mcp-python-sdk/     # Official MCP SDK
├── 📁 anthropic-mcp-servers/        # Official MCP implementations
├── 📁 glips_figma_context/          # Design-to-code (8.7k stars)
├── 📁 microsoft_playwright/         # Browser automation (13.4k stars)
├── 📁 portkey_admin/                # AI gateway optimization
├── 📁 modern_stack_cortex_official/    # Official Modern Stack AI
└── 📁 ... (4 additional repos)      # Strategic community patterns
```

### 📁 `frontend/` - React Application

```
frontend/
├── 📁 public/                       # Static public assets
├── 📁 src/                          # Source code
│   ├── 📁 components/               # React components
│   │   ├── 📄 UnifiedDashboard.tsx  # 🎯 ONLY frontend (rule)
│   │   └── 📄 UnifiedKPICard.tsx    # KPI widgets
│   ├── 📁 pages/                    # Page components
│   ├── 📁 services/                 # API clients
│   │   └── 📄 apiClient.js          # 🔑 Single API client (rule)
│   ├── 📁 styles/                   # CSS and styling
│   └── 📁 utils/                    # Frontend utilities
├── 📄 package.json                  # Frontend dependencies
├── 📄 tsconfig.json                 # TypeScript configuration
└── 📄 vite.config.ts                # Vite build configuration
```

### 📁 `tests/` - Test Suites

```
tests/
├── 📁 ai_evals/                     # AI evaluation tests
├── 📁 backend/                      # Backend-specific tests
├── 📁 infrastructure/               # Infrastructure tests
├── 📁 mcp_servers/                  # MCP server tests
├── 📄 conftest.py                   # Pytest configuration
└── 📄 test_*.py                     # Individual test files (43 files with tests)
```

---

## 🗃️ Archive Structure (Post-Cleanup)

### 📁 `archive/` - Organized Historical Files

```
archive/
├── 📁 one_time_scripts/             # 19 archived one-time scripts
│   ├── 📄 execute_strategic_plan.py          # Strategic implementation (44KB)
│   ├── 📄 enhanced_coding_workflow_integration.py  # Workflow integration (22KB)
│   ├── 📄 deploy_complete_platform.py        # Platform deployment (16KB)
│   ├── 📄 modern_stack_advanced_features_implementation.py  # Modern Stack integration
│   └── 📄 ... (15 additional scripts)        # Various one-time implementations
├── 📁 scattered_docs/               # 172 organized documentation files
│   ├── 📄 UNIFIED_DEPLOYMENT_*.md            # Deployment documentation
│   ├── 📄 BACKEND_CLEAN_ARCHITECTURE_*.md    # Architecture documentation
│   ├── 📄 LAMBDA_LABS_*.md                   # Lambda Labs documentation
│   ├── 📄 modern_stack_*.md                     # Modern Stack documentation
│   └── 📄 ... (168 additional docs)          # Comprehensive historical docs
├── 📁 placeholders/                 # 2 removed placeholder files
│   ├── 📄 .FUTURE_USE_ONLY (apps)            # Apps placeholder
│   └── 📄 .FUTURE_USE_ONLY (libs)            # Libs placeholder
├── 📁 documentation/                # Additional documentation
├── 📁 one-time-scripts/             # Legacy organization
└── 📁 reports/                      # Cleanup and analysis reports
```

---

## 🔑 Key Configuration Files

### **Primary Configuration**
- `📄 pyproject.toml` - Python project configuration with UV dependency management
- `📄 uv.lock` - UV dependency lock file (516KB) - **NEVER MODIFY MANUALLY**
- `📄 .cursorrules` - Cursor AI development rules and guidelines

### **Infrastructure Configuration**
- `📄 infrastructure/Pulumi.yaml` - Pulumi project configuration
- `📄 infrastructure/pulumi-esc-config.yaml` - ESC secret management
- `📄 config/cursor_enhanced_mcp_config.json` - MCP server configuration

### **Frontend Configuration**
- `📄 frontend/package.json` - Frontend dependencies
- `📄 frontend/tsconfig.json` - TypeScript configuration
- `📄 frontend/vite.config.ts` - Vite build configuration

### **Development Configuration**
- `📄 Makefile` - Build and automation commands
- `📄 .gitignore` - Git ignore patterns
- `📄 .codacy.yml` - Code quality configuration

---

## 🚀 Getting Started Guide

### **1. Environment Setup**
```bash
# Clone repository
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# Install UV (Python dependency manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Set environment variables
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
```

### **2. Backend Development**
```bash
# Start backend services
cd backend
uv run python -m uvicorn app.main:app --reload --port 8000

# Run tests
uv run pytest tests/ -v

# Check code quality
uv run ruff check backend/
uv run black backend/ --check
```

### **3. Frontend Development**
```bash
# Start frontend development server
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

### **4. MCP Server Development**
```bash
# Start all MCP servers
python scripts/start_all_mcp_servers.py

# Start specific MCP server
cd mcp-servers/modern_stack_unified
python server.py
```

### **5. Infrastructure Deployment**
```bash
# Deploy infrastructure (via GitHub Actions only)
git push origin main  # Triggers automated deployment

# Local infrastructure management
cd infrastructure
pulumi preview  # Preview changes
pulumi up       # Apply changes (development only)
```

---

## 📊 Repository Statistics

### **File Distribution**
- **Total Files**: 2,007+ files across 422+ directories
- **Python Files**: 821 source files
- **Test Files**: 43 files with actual test functions
- **Documentation**: 540+ markdown files
- **Configuration Files**: 150+ config files

### **Language Breakdown**
- **Primary**: Python (backend services, scripts, MCP servers)
- **Frontend**: TypeScript/React (frontend application)
- **Infrastructure**: TypeScript (Pulumi IaC)
- **Configuration**: YAML, JSON, TOML

### **Key Metrics**
- **MCP Servers**: 53 integration servers
- **External Repositories**: 11 strategic repos (22k+ combined stars)
- **Archive Files**: 192 files organized and preserved
- **Test Coverage**: Significant enhancement opportunities identified

---

## 🎯 Development Workflows

### **Code Quality Standards**
- **Formatting**: Black (88 character line limit)
- **Import Organization**: isort with Black profile
- **Linting**: Ruff with strict configuration
- **Type Checking**: mypy for all Python code
- **Testing**: pytest with async support

### **Git Workflow**
- **Main Branch**: `main` (protected, requires PR)
- **Feature Branches**: `feature/description`
- **Hotfix Branches**: `hotfix/description`
- **Release Branches**: `release/version`

### **Deployment Pipeline**
1. **Code Review**: All changes require PR approval
2. **Automated Testing**: Full test suite runs on PR
3. **Quality Gates**: Ruff, Black, mypy checks
4. **Security Scanning**: Bandit security analysis
5. **Automated Deployment**: GitHub Actions to Lambda Labs

---

## 🔐 Security & Secrets Management

### **Secret Management Hierarchy**
1. **Pulumi ESC** (primary - automatic via `get_config_value()`)
2. **GitHub Organization Secrets** (automatic sync)
3. **Environment Variables** (fallback only)
4. **Hardcoded Defaults** (non-sensitive fallbacks only)

### **Security Tools**
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Ruff**: Security-focused linting rules
- **GitHub Dependabot**: Automated dependency updates

---

## 📚 Documentation Navigation

### **Primary Documentation**
- `📄 README.md` - Main project overview
- `📁 docs/system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md` - **Master documentation**
- `📁 docs/01-getting-started/` - Quick start guides
- `📁 docs/03-architecture/` - System architecture

### **Development Documentation**
- `📁 docs/02-development/` - Development workflows
- `📁 docs/06-mcp-servers/` - MCP server development
- `📁 docs/ai-coding/` - AI-assisted development

### **Deployment Documentation**
- `📁 docs/04-deployment/` - Deployment strategies
- `📁 infrastructure/docs/` - Infrastructure documentation
- `📁 docs/99-reference/` - Reference materials

---

## 🛠️ Maintenance & Operations

### **Regular Tasks**
- **Dependency Updates**: Weekly via Renovate bot
- **Security Scanning**: Nightly automated scans
- **Code Quality**: Continuous monitoring via Codacy
- **Performance Monitoring**: Real-time metrics via monitoring stack

### **File Lifecycle Management**
- **One-time Scripts**: Delete after successful execution
- **Documentation**: Archive outdated docs to `archive/scattered_docs/`
- **Test Files**: Maintain comprehensive coverage for business logic
- **Configuration**: Version control all configuration changes

### **Cleanup Policies**
- **MANDATORY FILE CLEANUP POLICY**: Automatically enforced
- **Archive Organization**: Structured preservation of historical files
- **Regular Audits**: Monthly repository hygiene reviews

---

## 🎊 Conclusion

The Sophia AI repository maintains a **clean, professional, enterprise-grade structure** following industry best practices:

- ✅ **Organized Architecture**: Clear separation of concerns
- ✅ **Comprehensive Documentation**: 540+ files with master handbook
- ✅ **Robust Testing Framework**: Foundation for enhanced coverage
- ✅ **Advanced Integration**: 53 MCP servers + 11 strategic external repos
- ✅ **Enterprise Security**: Pulumi ESC + comprehensive secret management
- ✅ **Modern Tooling**: UV, Ruff, Black, pytest, GitHub Actions
- ✅ **Historical Preservation**: 192 files archived with complete audit trail

**🚀 Ready for enterprise-scale AI assistant development!**

---

*Document Version: 1.0*  
*Last Updated: July 11, 2025*  
*Status: Current and Complete*