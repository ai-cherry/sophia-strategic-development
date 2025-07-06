# 🏗️ Sophia AI Project Structure (Foundation Tier)

**Purpose**: Core system architecture and file organization  
**Auto-Loading**: Always loaded for complex tasks  
**Last Updated**: July 2025

---

## 🎯 Phoenix Architecture Overview

### **Core Principle**: Snowflake as the Center of the Universe
All data flows through Snowflake Cortex as the single source of truth for structured, unstructured, and vectorized data.

```
┌─────────────────────────────────────────────────────────────┐
│                    SOPHIA AI PHOENIX PLATFORM                │
├─────────────────────────────────────────────────────────────┤
│  Frontend: Unified Dashboard (React + TypeScript)            │
│  Backend: Python FastAPI + LangGraph Orchestration          │
│  Data: Snowflake Cortex (THE UNIVERSE CENTER)               │
│  MCP: 28 Consolidated Servers                               │
│  AI: Multi-Model Routing (Portkey + OpenRouter)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

### **Root Level**
```
sophia-ai/
├── backend/                    # Python FastAPI backend
├── frontend/                   # React TypeScript frontend
├── docs/                      # 3-tier documentation system
├── external/                  # Strategic repository collection (22k+ stars)
├── mcp-servers/               # 28 consolidated MCP servers
├── infrastructure/            # Pulumi IaC + Kubernetes
├── scripts/                   # Automation and deployment scripts
└── tests/                     # Test suites
```

### **Backend Architecture**
```
backend/
├── core/                      # Core services and configuration
│   ├── auto_esc_config.py     # Pulumi ESC integration
│   ├── security_config.py     # Security and secret management
│   └── centralized_config_manager.py
├── services/                  # Business logic services
│   ├── unified_llm_service.py # Multi-model LLM routing
│   ├── ai_memory_service.py   # Snowflake Cortex memory
│   └── business_intelligence_service.py
├── integrations/              # External service integrations
│   ├── portkey_gateway_service.py # Portkey LLM gateway
│   ├── snowflake_service.py   # Snowflake Cortex operations
│   └── mcp_orchestration_service.py
├── agents/                    # AI agent implementations
│   ├── core/                  # Base agent classes
│   └── specialized/           # Domain-specific agents
└── api/                       # FastAPI endpoints
```

### **Frontend Architecture**
```
frontend/
├── src/
│   ├── components/
│   │   ├── dashboard/         # Unified Dashboard (SINGLE SOURCE)
│   │   │   └── UnifiedDashboard.tsx
│   │   ├── chat/              # Unified Chat Interface
│   │   └── shared/            # Reusable components
│   ├── services/
│   │   ├── apiClient.js       # SINGLE API CLIENT
│   │   └── llmService.js      # LLM integration
│   └── pages/                 # Page components
├── public/                    # Static assets
└── package.json
```

### **Documentation System (3-Tier)**
```
docs/
├── ai-context/                # Foundation Tier (Auto-loaded for complex tasks)
│   ├── docs-overview.md       # Auto-loading routing map
│   ├── project-structure.md   # This file
│   ├── sophia-brain.md        # AI decision patterns
│   └── data-architecture.md   # Snowflake Cortex patterns
├── components/                # Component Tier (Service-specific)
│   ├── mcp-servers/           # MCP integration patterns
│   ├── business-intelligence/ # BI patterns
│   └── integrations/          # External service patterns
└── features/                  # Feature Tier (Task-specific)
    ├── unified-chat/          # Chat interface patterns
    ├── project-management/    # PM integration patterns
    └── sales-intelligence/    # Sales analytics patterns
```

---

## 🔄 Data Flow Architecture

### **Multi-Tier Data Strategy**
```
External APIs → PostgreSQL (Staging) → Snowflake (Truth) → Redis (Cache) → Frontend
                                    ↓
                            Pinecone (Vector) → AI Memory → Cortex Functions
```

### **Tier Responsibilities**
- **Tier 1 (Redis)**: Ephemeral data, sessions, real-time cache
- **Tier 2 (Pinecone)**: Vector embeddings, semantic search
- **Tier 3 (PostgreSQL)**: ETL staging, external data ingestion
- **Tier 4 (Snowflake)**: Analytical truth, business intelligence

---

## 🤖 MCP Server Organization

### **28 Consolidated Servers** (reduced from 36+ fragmented)
```
Core Intelligence (7):     ai_memory, sophia_intelligence, snowflake_unified
Business Intelligence (8): hubspot, gong, slack, notion, intercom, salesforce
Infrastructure (8):        lambda_labs, pulumi, portkey, postgres, playwright
Specialized (5):           huggingface, graphiti, ui_ux_agent, overlays
```

### **Port Allocation**
```python
MCP_PORTS = {
    "ai_memory": 9000,
    "codacy": 3008,
    "github": 9003,
    "linear": 9004,
    "asana": 3006,
    "notion": 3007,
    "hubspot": 9006,
    "slack": 9005,
    # ... complete port mapping
}
```

---

## 🔐 Security Architecture

### **Secret Management Pipeline**
```
GitHub Organization Secrets → Pulumi ESC → Backend Auto-Loading
```

### **Authentication Layers**
- **Tier 1**: CLI-based (GitHub, Pulumi, Docker, Vercel)
- **Tier 2**: Enhanced API (Snowflake, Lambda Labs, Estuary)
- **Tier 3**: Secure API Keys (OpenAI, Anthropic, Slack, etc.)

---

## 🚀 Deployment Architecture

### **Infrastructure Stack**
- **Frontend**: Vercel (React deployment)
- **Backend**: Lambda Labs (GPU compute + Docker Swarm)
- **Database**: Snowflake (Single source of truth)
- **Secrets**: Pulumi ESC (Centralized configuration)
- **Monitoring**: Grafana + Prometheus

### **Environment Configuration**
```yaml
ENVIRONMENT: "prod"  # ALWAYS default to production
SNOWFLAKE_ACCOUNT: "ZNB04675.us-east-1.us-east-1"
SNOWFLAKE_DATABASE: "SOPHIA_AI_PRODUCTION"
SNOWFLAKE_WAREHOUSE: "SOPHIA_AI_COMPUTE_WH"
```

---

## 📊 Key Technologies

### **Backend Stack**
- **Framework**: FastAPI (Python 3.11+)
- **AI/ML**: Snowflake Cortex, OpenAI, Anthropic
- **Database**: Snowflake, PostgreSQL, Redis, Pinecone
- **Gateway**: Portkey (LLM routing), OpenRouter (Model selection)
- **Orchestration**: LangGraph, MCP Protocol

### **Frontend Stack**
- **Framework**: React 18 + TypeScript
- **Build**: Vite + Vercel deployment
- **Styling**: Tailwind CSS + Glassmorphism
- **State**: Context API + React Query
- **UI Generation**: V0.dev integration

### **Infrastructure Stack**
- **IaC**: Pulumi (TypeScript)
- **Containers**: Docker + Docker Swarm
- **Compute**: Lambda Labs GPU instances
- **Monitoring**: Grafana, Prometheus, Sentry
- **Secrets**: Pulumi ESC + GitHub Actions

---

## 🎯 Development Priorities

### **Quality Standards (NEVER COMPROMISE)**
1. **QUALITY & CORRECTNESS** - Every line must be correct
2. **STABILITY & RELIABILITY** - Rock-solid for CEO operations
3. **MAINTAINABILITY** - Clear, modifiable code
4. **PERFORMANCE** - Important but secondary to quality
5. **COST & SECURITY** - Consider but don't over-optimize

### **Code Hygiene Rules**
- **Zero Duplication**: Never duplicate code or functionality
- **Clean Dependencies**: All dependencies explicit and documented
- **One-Time Scripts**: DELETE after use (following cleanup rules)
- **Production First**: Always default to production environment

---

## 🔍 Architecture Patterns

### **Service Layer Pattern**
```python
# All services follow this pattern
class BaseService:
    def __init__(self, config: Config):
        self.config = config
        
    async def initialize(self):
        # Lazy initialization
        pass
        
    async def health_check(self):
        # Standard health check
        pass
```

### **MCP Integration Pattern**
```python
# All MCP servers follow this pattern
class BaseMCPServer:
    def __init__(self, port: int):
        self.port = port
        self.tools = []
        
    async def handle_request(self, request):
        # Standard MCP request handling
        pass
```

### **API Client Pattern**
```python
# Standardized API integration
class ExternalServiceClient:
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.client = self._create_client()
        
    async def _make_request(self, method, endpoint, **kwargs):
        # Rate limiting + error handling
        pass
```

This foundation documentation provides the core system knowledge required for all complex architectural tasks and system-wide operations.