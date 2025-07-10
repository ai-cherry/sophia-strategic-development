# SOPHIA AI SYSTEM HANDBOOK
## The Definitive Source of Truth

**Version**: Phoenix 1.0
**Last Updated**: July 2025
**Status**: AUTHORITATIVE - This document supersedes all previous architecture documentation

---

## 🎯 DEVELOPMENT PRIORITIES & CONTEXT

### Company Context
- **Company Size**: 80 employees (Pay Ready)
- **Initial User**: CEO (sole user for 3+ months)
- **Development Team**: CEO + AI assistants
- **Rollout Plan**: CEO → 2-3 super users (3 months) → Full company (6+ months)

### Priority Order (NEVER COMPROMISE)
1. **QUALITY & CORRECTNESS** - Every line must be correct and well-structured
2. **STABILITY & RELIABILITY** - Rock-solid system for CEO operations
3. **MAINTAINABILITY** - Clear code that's easy to modify
4. **PERFORMANCE** - Important but secondary to quality
5. **COST & SECURITY** - Consider but don't over-optimize yet

### Quality Standards
- **Zero Duplication**: Never duplicate code or functionality
- **Clear Dependencies**: All dependencies explicit and documented
- **Conflict Prevention**: Check for conflicts before implementing
- **Structure First**: Plan structure to avoid future issues
- **Clean Codebase**: Delete one-time scripts after use

---

## 🔥 THE PHOENIX ARCHITECTURE

### Core Principle: Snowflake as the Center of the Universe

Sophia AI operates on a unified architecture where **Snowflake is the single, undisputed source of truth** for all data—structured, unstructured, and vectorized. This eliminates the fragmentation that previously existed across multiple databases and vector stores.

```
┌─────────────────────────────────────────────────────────────┐
│                    SOPHIA AI PHOENIX PLATFORM                │
├─────────────────────────────────────────────────────────────┤
│  Frontend: Unified Dashboard (React + TypeScript)            │
│  ├─ Unified Chat (Primary Interface)                           │
│  ├─ Project Management Hub (Linear + Asana + Slack)          │
│  ├─ Knowledge AI (File Upload + Learning Status)             │
│  ├─ Sales Intelligence (Revenue Engine)                      │
│  └─ System Health (MCP Server Status)                        │
├─────────────────────────────────────────────────────────────┤
│  Backend: Python FastAPI + LangGraph Orchestration          │
│  ├─ Unified Chat Service (Natural Language Processing)       │
│  ├─ MCP Server Gateway (27 Consolidated Servers)             │
│  ├─ AI Memory System (Snowflake Cortex Native)               │
│  └─ Business Intelligence Engine                             │
├─────────────────────────────────────────────────────────────┤
│  DATA LAYER: SNOWFLAKE CORTEX (THE UNIVERSE CENTER)         │
│  ├─ L3: Core Data Lakehouse (All Business Data)              │
│  ├─ L2: Semantic Memory (Cortex Embeddings + Vector Search)  │
│  ├─ L1: Fast Cache (Materialized Views + Result Caching)     │
│  └─ AI Processing: Native Cortex Functions                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ UNIFIED DATA ARCHITECTURE

### The Snowflake Universe Schema

**ALL DATA FLOWS INTO SNOWFLAKE**. No exceptions. No parallel systems.

```sql
-- AUTHORITATIVE DDL - This is the single source of truth
CREATE SCHEMA IF NOT EXISTS SOPHIA_CORE;
CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_MEMORY;
CREATE SCHEMA IF NOT EXISTS SOPHIA_BUSINESS_INTELLIGENCE;
CREATE SCHEMA IF NOT EXISTS SOPHIA_PROJECT_MANAGEMENT;
CREATE SCHEMA IF NOT EXISTS SOPHIA_KNOWLEDGE_BASE;

-- L3: Core Data Lakehouse
CREATE TABLE SOPHIA_CORE.UNIFIED_DATA_CATALOG (
    data_id VARCHAR(255) PRIMARY KEY,
    source_system VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    metadata VARIANT,
    content_hash VARCHAR(64),
    ai_processed BOOLEAN DEFAULT FALSE
);

-- L2: Semantic Memory (Cortex Native)
CREATE TABLE SOPHIA_AI_MEMORY.MEMORY_RECORDS (
    memory_id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(FLOAT, 768), -- Cortex Native Embeddings
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    importance_score FLOAT DEFAULT 0.5,
    business_context VARIANT,
    tags ARRAY
);

-- L1: Fast Cache Layer
CREATE TABLE SOPHIA_CORE.QUERY_CACHE (
    cache_key VARCHAR(255) PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL,
    result_data VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP_NTZ,
    hit_count INTEGER DEFAULT 0
);
```

### Multi-Tier Data Architecture

While Snowflake remains the **central analytical data warehouse** and ultimate source of truth for business data, Sophia AI employs a pragmatic multi-tier architecture optimized for different data workloads:

#### Tier 1: Ephemeral & Real-time (Redis)
- **Purpose**: Session management, caching, pub/sub events
- **Use Cases**:
  - API response caching (<50ms access)
  - Real-time notifications
  - Rate limiting
  - Session storage
- **Data Retention**: Hours to days
- **Implementation**: Redis Cluster with persistence for critical ephemeral data

#### Tier 2: Vector & AI Memory (Pinecone)
- **Purpose**: Semantic search and AI memory storage
- **Use Cases**:
  - AI conversation embeddings
  - Document similarity search
  - Knowledge base vectors
  - Context retrieval
- **Integration**: Works alongside Snowflake Cortex for hybrid vector search

#### Tier 3: ETL Staging (PostgreSQL)
- **Purpose**: Temporary staging for external data ingestion
- **Use Cases**:
  - HubSpot data staging
  - Gong call data processing
  - Slack message buffering
- **Data Flow**: External API → PostgreSQL → Transformation → Snowflake

#### Tier 4: Analytical Truth (Snowflake)
- **Purpose**: Central data warehouse and analytical processing
- **Use Cases**:
  - Business intelligence
  - Historical analysis
  - Complex queries
  - Cortex AI operations
- **Data Retention**: Permanent business records

**Note**: This multi-tier approach reflects the current implementation reality. While Snowflake remains central for business data, specialized databases handle specific workloads for optimal performance.

---


## 🗄️ ENHANCED SNOWFLAKE ARCHITECTURE

### Complete Database Structure (Enhanced January 2025)

**Database**: SOPHIA_AI_PRODUCTION
**Schemas** (11 total + Enhanced Tables):
- SOPHIA_CORE - Core business data
- SOPHIA_AI_MEMORY - Enhanced 6-tier memory storage
- SOPHIA_BUSINESS_INTELLIGENCE - BI analytics with GPU acceleration
- CORTEX_AI - Enhanced Cortex AI functions with GH200 integration
- AI_MEMORY - Memory architecture with GPU caching
- ANALYTICS - Analytics views with vector search
- CHAT - Chat context storage with GPU embeddings
- MONITORING - System monitoring with GPU metrics
- GONG_INTEGRATION - Gong data with AI analysis
- HUBSPOT_INTEGRATION - HubSpot data with predictive insights
- SLACK_INTEGRATION - Slack data with sentiment analysis

**Enhanced Warehouses**:
- SOPHIA_AI_COMPUTE_WH (LARGE) - General compute with GPU acceleration
- SOPHIA_AI_ANALYTICS_WH (X-LARGE) - Enhanced analytics workloads
- SOPHIA_AI_CORTEX_WH (MEDIUM) - AI operations with GH200 integration
- SOPHIA_AI_GH200_WH (X-LARGE) - Dedicated GH200 GPU processing

**Enhanced Memory Architecture** (6-Tier with GPU Acceleration):
- L0: GPU memory (<10ms) - GH200 HBM3e 96GB
- L1: Session cache (<50ms) - Redis enhanced
- L2: Cortex cache (<100ms) - Snowflake + GPU acceleration
- L3: Persistent memory (<200ms) - Snowflake native
- L4: Knowledge graph (<300ms) - Snowflake vector search
- L5: Workflow memory (<400ms) - Snowflake long-term

**New Enhanced Tables**:
```sql
-- L0 GPU Memory Simulation (for monitoring)
CREATE TABLE SOPHIA_AI_MEMORY.GPU_MEMORY_POOLS (
    pool_name VARCHAR(50) PRIMARY KEY,
    allocated_memory_gb FLOAT,
    used_memory_gb FLOAT,
    pool_type VARCHAR(50),
    last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Enhanced Cortex Cache with GPU metadata
CREATE TABLE SOPHIA_AI_MEMORY.CORTEX_CACHE_ENHANCED (
    cache_key VARCHAR(255) PRIMARY KEY,
    cache_value VARIANT,
    gpu_processed BOOLEAN DEFAULT FALSE,
    processing_time_ms INTEGER,
    gpu_memory_used_mb INTEGER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    ttl INTEGER
);

-- GPU Performance Metrics
CREATE TABLE SOPHIA_AI_MEMORY.GPU_PERFORMANCE_METRICS (
    metric_id VARCHAR(255) PRIMARY KEY,
    gpu_id INTEGER,
    memory_utilization FLOAT,
    compute_utilization FLOAT,
    temperature_celsius FLOAT,
    power_usage_watts FLOAT,
    recorded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

## 🧠 THE SOPHIA AI BRAIN

### Natural Language Processing Pipeline

```python
# Unified Chat Service - The Heart of Sophia
class SophiaUnifiedChatService:
    """
    The central nervous system of Sophia AI.
    All user interactions flow through this service.
    """

    def __init__(self):
        self.snowflake_cortex = SnowflakeCortexService()
        self.ai_memory = SophiaAIMemoryService()
        self.business_intelligence = SophiaBusinessIntelligence()
        self.project_hub = SophiaProjectHub()

    async def process_message(self, message: str, context: dict) -> dict:
        """
        Process natural language input through the Sophia AI brain.

        Flow:
        1. Intent Detection (Cortex Classification)
        2. Context Retrieval (Vector Search)
        3. Business Logic Routing
        4. Response Generation
        5. Memory Storage
        """
        # Intent detection using Snowflake Cortex
        intent = await self.snowflake_cortex.classify_intent(message)

        # Context retrieval from semantic memory
        context_data = await self.ai_memory.retrieve_context(
            message, intent, limit=10
        )

        # Route to appropriate business logic
        response = await self._route_to_service(intent, message, context_data)

        # Store interaction in memory
        await self.ai_memory.store_interaction(
            message, response, intent, context
        )

        return response
```

### MCP Server Consolidation

**28 Consolidated MCP Servers** (reduced from 36+ fragmented servers):

**Core Intelligence** (7 servers):
- `ai_memory` - Snowflake Cortex native memory
- `sophia_intelligence_unified` - Central AI orchestration
- `snowflake_unified` - Single database interface
- `codacy` - Code quality and security
- `github` - Repository management
- `linear` - Engineering project management
- `asana` - Product management

**Business Intelligence** (48+ servers):
- `hubspot_unified` - CRM and sales data
- `gong` - Call analysis and sales intelligence
- `slack_unified` - Communication analytics
- `notion` - Knowledge management
- `intercom` - Customer support
- `salesforce` - Extended CRM
- `apollo` - Sales prospecting
- `bright_data` - Market intelligence

**Infrastructure** (48+ servers):
- `lambda_labs_cli` - GPU compute management
- `pulumi` - Infrastructure as code
- `portkey_admin` - LLM gateway optimization
- `postgres` - Legacy system bridge
- `playwright` - Browser automation
- `figma_context` - Design system integration
- `apify_intelligence` - Web scraping
- `v0dev` (9023) - **NEW**: AI-powered UI generation

**Specialized** (5 servers):
- `huggingface_ai` - Model management
- `graphiti` - Knowledge graphs
- `ui_ux_agent` - Design automation
- `overlays` - System monitoring
- `migration_orchestrator` - Data migration

---

## 🎯 THE UNIFIED DASHBOARD

### Single Source of Truth Frontend

**Location**: `frontend/src/components/dashboard/UnifiedDashboard.tsx`

**CRITICAL RULE**: All new frontend development MUST extend this component. No new dashboards.

```typescript
// Unified Dashboard Structure
const UnifiedDashboard = () => {
  const [activeTab, setActiveTab] = useState('unified_overview');

  return (
    <div className="unified-dashboard">
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'unified_chat' && <UnifiedChatInterface />}
      {activeTab === 'projects-okrs' && <ProjectManagementHub />}
      {activeTab === 'knowledge-ai' && <KnowledgeAIInterface />}
      {activeTab === 'sales-intelligence' && <SalesIntelligenceHub />}
      {activeTab === 'system-health' && <SystemHealthDashboard />}
      {activeTab === 'financials' && <FinancialsOverview />}
      {activeTab === 'employees' && <EmployeeManagement />}
      {activeTab === 'sophia-persona' && <SophiaPersonaManager />}
    </div>
  );
};
```

### Tab Definitions (Actual Implementation)

1. **Unified Overview** - Executive KPIs: Project Health, Budget Usage, Team Utilization, On-Time Delivery
2. **Projects & OKRs** - Cross-platform project health with health scores, progress tracking, and OKR alignment
3. **Knowledge AI** - Data ingestion status, AI learning metrics, manual upload, and data source sync
4. **Sales Intelligence** - Pipeline value, active deals, win rate, and calls analyzed
5. **LLM Metrics** - Cost monitoring, budget tracking, provider usage, cache performance, and Snowflake savings
6. **Lambda Labs Health** - Infrastructure health monitoring for GPU compute resources
7. **Workflow Designer** - Visual workflow creation and management interface
8. **Unified Chat** - Primary AI chat interface with contextual awareness

---

## 🚀 ENHANCED DEPLOYMENT ARCHITECTURE

### Infrastructure Stack (GGH200 GPU Enhanced)

**Primary Deployment**: Vercel (Frontend) + Lambda Labs GH200 Clusters (Backend)
**Database**: Snowflake (Enhanced with GPU acceleration)
**Secrets Management**: Pulumi ESC (Automated pipeline)
**Container Orchestration**: K3s on Lambda Labs
**GPU Architecture**: NVIDIA GH200 (96GB HBM3e, 4.8TB/s bandwidth)
**Memory Architecture**: 6-Tier with GPU acceleration
**Monitoring**: Enhanced Grafana + Prometheus + GPU metrics

### Enhanced Infrastructure Components

**K3s Configuration**:
- **Manifests**: Kustomize-based in `k8s/` directory
- **Namespaces**: sophia-ai-prod, mcp-servers, monitoring
- **Ingress**: Traefik with automatic TLS
- **Secrets**: Pulumi ESC with automatic sync

**6-Tier Memory Architecture**:
- **L0 (GPU Memory)**: 96GB HBM3e per node (<10ms latency)
  - Active Models: 41GB pool
  - Inference Cache: 27GB pool
  - Vector Cache: 20GB pool
  - Buffer: 8GB pool
- **L1 (Session Cache)**: Redis with enhanced performance
- **L2 (Cortex Cache)**: Snowflake + GPU acceleration
- **L3-L5**: Snowflake native with vector search

**Snowflake Integration**:
- **GPU External Functions**: Direct GPU calls from Snowflake SQL
- **Cortex Enhancement**: GPU-accelerated AI operations
- **Cost Optimization**: 40% reduction vs external LLM APIs
- **Performance**: 10x faster inference, 50x faster vector operations

**Enhanced SSH Key Management**:
- **Active Instance**: lynn-sophia-gh200-master-01 (192.222.58.232)
- **Lambda Labs Key**: lynn-sophia-key (ID: b6d556aad0f64c8eb22c9224b3dff66a)
- **Local Private Key**: ~/.ssh/sophia2025.pem
- **SSH Command**: `ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232`
- **Documentation**: See `docs/04-deployment/LAMBDA_LABS_SSH_CONFIGURATION.md`
- All SSH operations automated through Pulumi ESC pipeline

### Environment Configuration

```yaml
# Production Environment (AUTHORITATIVE)
ENVIRONMENT: "prod"
SNOWFLAKE_ACCOUNT: "payready.us-east-1"
SNOWFLAKE_DATABASE: "SOPHIA_AI_PRODUCTION"
SNOWFLAKE_WAREHOUSE: "SOPHIA_COMPUTE_WH"
SNOWFLAKE_ROLE: "SOPHIA_AI_ROLE"

# MCP Server Ports (Consolidated)
MCP_AI_MEMORY_PORT: 9000
MCP_CODACY_PORT: 3008
MCP_GITHUB_PORT: 9003
MCP_LINEAR_PORT: 9004
MCP_ASANA_PORT: 3006
MCP_NOTION_PORT: 3007
MCP_HUBSPOT_PORT: 9006
MCP_SLACK_PORT: 9005
```

---

## 🔐 SECURITY FRAMEWORK

### Secret Management Pipeline

```
GitHub Organization Secrets (ai-cherry)
           ↓
    GitHub Actions (automatic sync)
           ↓
    Pulumi ESC Environments
           ↓
    Sophia AI Backend (automatic loading)
```

**NEVER**:
- Create or manage `.env` files
- Hardcode API keys or tokens
- Share secrets in chat/email
- Manual environment variable setup

**ALWAYS**:
- Use GitHub organization secrets
- Leverage Pulumi ESC for centralized configuration
- Implement automatic backend configuration loading
- Use GitHub Actions for secret synchronization

### AI Agent Authentication System

**DEPRECATED**: The Unified AI Agent Authentication System has been removed from the codebase (July 2025). The related files (`backend/security/unified_service_auth_manager.py`, `scripts/setup_unified_ai_agent_auth.py`) have been deleted as part of the code hygiene enforcement.

For infrastructure operations, use standard authentication methods:
- GitHub CLI: `gh auth login`
- Pulumi CLI: `pulumi login`
- Docker: `docker login`
- Vercel: `vercel login`

All secrets continue to be managed through the GitHub Organization Secrets → Pulumi ESC pipeline.

### Business Value**: AI agents can make real infrastructure changes with enterprise security, natural language interface for technical operations, zero credential exposure, and complete audit compliance.

---

## 📊 BUSINESS INTELLIGENCE FRAMEWORK

### Executive Dashboard KPIs

**Revenue Intelligence**:
- Monthly Recurring Revenue (MRR)
- Customer Acquisition Cost (CAC)
- Customer Lifetime Value (CLV)
- Churn Rate Analysis

**Operational Intelligence**:
- Project Health Scores (Linear + Asana)
- Team Productivity Metrics
- System Performance Indicators
- AI Learning Progress

**Strategic Intelligence**:
- Market Analysis (Bright Data)
- Competitive Positioning
- Growth Forecasting
- Risk Assessment

### Natural Language Query Examples

```sql
-- Unified Dashboard Queries (Natural Language → SQL)
"Show me revenue trends for the last 6 months"
→ SELECT date_trunc('month', created_date) as month,
         sum(amount) as revenue
  FROM hubspot_deals
  WHERE created_date >= dateadd('month', -6, current_date())
  GROUP BY month ORDER BY month;

"What are our top 5 customers by revenue?"
→ SELECT customer_name, sum(deal_amount) as total_revenue
  FROM hubspot_deals
  WHERE deal_stage = 'closed_won'
  GROUP BY customer_name
  ORDER BY total_revenue DESC LIMIT 5;
```

### AI SQL and Cortex Agent Interaction

**Complete Lifecycle Documentation**: See [AI SQL and Cortex Agent Interaction Lifecycle](./09_AI_SQL_CORTEX_AGENT_LIFECYCLE.md)

This comprehensive guide covers the complete journey from natural language input to Snowflake Cortex execution, including:
- **Phase-by-Phase Processing**: Intent detection → Agent selection → SQL generation → Execution
- **Cortex Agent Specifications**: Snowflake Ops, Semantic Memory, and Business Intelligence agents
- **Performance Optimization**: Connection pooling, batch processing, intelligent caching
- **Integration Patterns**: Chat interface integration and error handling strategies
- **Monitoring & Analytics**: Performance metrics and quality assurance frameworks

### Natural Language UI Generation (V0.dev Integration)

```typescript
// UI Component Generation (Natural Language → React Component)
"Create a dashboard with glassmorphism styling"
→ Generates complete React component with modern glass effect

"Build a responsive data table with sorting and filtering"
→ Creates full-featured table component with TypeScript types

"Design a modal dialog with form validation"
→ Produces accessible modal with built-in validation logic

"Generate a chart component for revenue visualization"
→ Delivers interactive chart with real-time data binding
```

---

## 🔄 DEVELOPMENT WORKFLOW

### Phoenix Development Principles

1. **Snowflake First**: All data decisions go through Snowflake
2. **Unified Dashboard**: All UI development extends UnifiedDashboard.tsx
3. **MCP Consolidation**: No new fragmented servers
4. **Real Data Only**: No mock data in production paths
5. **Documentation Authority**: This handbook is the single source of truth

### Development Commands

```bash
# Start the Phoenix Platform
cd sophia-main
source activate_env.sh

# Backend (Unified Test Server)
python -m backend.test_ceo_server

# Frontend (Unified Dashboard)
cd frontend && npm run dev

# MCP Servers (Consolidated)
python scripts/activate_sophia_production.py

# Deployment
vercel --prod  # Frontend
pulumi up     # Infrastructure
```

---

## 🎯 ROADMAP: THE PHOENIX PLAN

### Phase 1: Foundation (Weeks 1-2) ✅ COMPLETE
- [x] Snowflake schema deployment
- [x] Unified dashboard creation
- [x] MCP server consolidation
- [x] Mock data elimination
- [x] System handbook creation

### Phase 1.5: Quality Foundation (Week 1) 🔄 IN PROGRESS
- [x] Dependency analysis - 120 circular dependencies found
- [x] Orphaned scripts audit - 12 scripts identified for deletion
- [ ] Circular dependency resolution - Base interfaces created
- [ ] Service boundary definition
- [ ] Import hierarchy establishment

### Phase 2: Core Intelligence (Weeks 3-4) 🔄 IN PROGRESS
- [ ] Sophia AI brain deployment
- [ ] Cortex embeddings integration
- [ ] Natural language processing
- [ ] Memory system activation

### Phase 3: Project Management Hub (Weeks 5-6)
- [ ] Linear + Asana integration
- [ ] OKR tracking system
- [ ] Team productivity analytics
- [ ] Cross-platform project health

### Phase 4: Knowledge Base (Weeks 7-8)
- [ ] File upload system
- [ ] AI training loop
- [ ] Knowledge categorization
- [ ] Learning progress tracking

### Phase 5: Unified Management (Weeks 9-10)
- [ ] User management system
- [ ] Tab access permissions
- [ ] LLM usage analytics
- [ ] Sophia persona customization

### Phase 6: System Excellence (Weeks 11-12)
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation completion
- [ ] Production deployment

### Phase 7: Monorepo Transformation (Months 4-6)
- [ ] Migrate to monorepo structure (`apps/` and `libs/`)
- [ ] Implement Turborepo for 5x faster builds
- [ ] Consolidate CI/CD workflows
- [ ] Unified dependency management with UV and PNPM
- [ ] Clean up old structure after successful migration

**Note**: During the monorepo transition (current), continue using the existing `backend/` and `frontend/` structure. See `docs/monorepo/MONOREPO_TRANSITION_GUIDE.md` for details.

---

## 🚀 PHASE 7: MONOREPO TRANSFORMATION (JANUARY-APRIL 2025)

**STATUS**: Planning Phase - Infrastructure Ready

The monorepo transformation is a critical evolution that will:
- Reduce build times from 15-20 minutes to <5 minutes
- Consolidate 15+ CI/CD workflows into 5-10 reusable templates
- Enable single-command development setup
- Provide unified dependency management

### Timeline
- **January 2025**: Foundation enhancement (Memory & Learning)
- **February 2025**: Data pipeline automation
- **March 2025**: Intelligence enhancement
- **April 2025**: Actual monorepo migration
- **May 2025**: Production optimization

**CRITICAL**: Continue using old structure (`backend/`, `frontend/`) until April 2025.

---

## 🧠 PHASE 8: INTEGRATED ENHANCEMENT PLAN (JANUARY-MARCH 2025)

**STATUS**: Ready for Implementation

Building on our existing strengths while incorporating advanced capabilities from industry best practices.

### Phase 1: Foundation Enhancement (4 weeks - January)

#### Memory & Learning Layer
- **Mem0 Integration**: Deploy persistent cross-session memory with RLHF
- **Enhanced Snowflake Schema**: Add learning analytics and feedback tables
- **AI Memory Evolution**: Integrate Mem0 with existing AI Memory MCP
- **Learning Dashboard**: Real-time visualization of memory improvements

#### Intelligent Orchestration
- **Prompt Optimizer MCP**: Deploy Tree of Thoughts optimization
- **Advanced LangGraph**: Conditional edges, human checkpoints, parallel execution
- **Unified MCP Gateway**: Single entry point with capability-based routing
- **Performance Metrics**: Track optimization improvements

### Phase 2: Data Pipeline Automation (4 weeks - February)

#### N8N Workflow Implementation
- **Automated Ingestion**: Salesforce, HubSpot, Gong, Intercom → Snowflake
- **AI Enrichment**: Automatic embedding generation and sentiment analysis
- **Real-time Sync**: Webhook handlers for instant updates
- **Executive Alerts**: Proactive notifications for key events

#### Cross-Platform Intelligence
- **Unified Customer View**: 360° visibility across all platforms
- **Deal Intelligence**: Automated progression tracking and risk assessment
- **Team Analytics**: Performance metrics and coaching opportunities
- **Natural Language Queries**: Ask questions across all data sources

### Phase 3: Intelligence Enhancement (4 weeks - March)

#### Multi-Agent Learning System
- **Specialized Agents**: Deploy domain-specific AI agents
- **Learning Loops**: Continuous improvement from user interactions
- **Memory Consolidation**: Periodic optimization of stored knowledge
- **Performance Tracking**: Measure learning effectiveness

#### Conversational Training
- **Natural Language Workflows**: Create workflows through conversation
- **Dynamic Agent Creation**: Generate new agents based on needs
- **Self-Improving Responses**: Learn from feedback and corrections
- **Context Preservation**: Maintain conversation state across sessions

### Technical Architecture Enhancements

```python
# Enhanced Memory Architecture
MEMORY_TIERS = {
    "L1": "Session Cache (Redis) - <50ms",
    "L2": "Snowflake Cortex - <100ms",
    "L3": "Mem0 Persistent - <200ms",
    "L4": "Knowledge Graph - <300ms",
    "L5": "LangGraph Workflow - <400ms"
}

# Intelligent Routing
ROUTING_STRATEGY = {
    "prompt_optimization": "ALWAYS",
    "memory_type": "CONTEXTUAL",
    "agent_selection": "CAPABILITY_BASED",
    "workflow_execution": "CONDITIONAL"
}
```

### Success Metrics

#### Technical Metrics
- API response time < 100ms (p99)
- Memory recall accuracy > 95%
- Workflow automation coverage > 80%
- LLM cost reduction > 40%

#### Business Metrics
- Executive decision time: 70% faster
- Data freshness: < 5 minutes
- Insight generation: 10x increase
- Manual tasks eliminated: 90%

### Integration Principles

1. **Snowflake Remains Central**: All data flows through Snowflake
2. **Quality Over Features**: CEO-focused development
3. **Incremental Enhancement**: Phased approach with continuous value
4. **Existing Pattern Reuse**: Leverage StandardizedMCPServer, config_manager
5. **Pay Ready Scale**: Optimized for 80 employees, CEO primary user

---

## 🏆 SUCCESS METRICS

### Technical Excellence
- **Uptime**: 99.9% system availability
- **Performance**: <200ms API response times
- **Reliability**: Zero data loss, atomic transactions
- **Security**: Enterprise-grade secret management

### Business Impact
- **User Adoption**: 100% executive team usage
- **Decision Speed**: 60% faster executive decisions
- **Data Quality**: 100% single source of truth
- **Development Velocity**: 40% faster feature delivery

### AI Intelligence
- **Context Accuracy**: 95% relevant context retrieval
- **Learning Speed**: Continuous improvement metrics
- **Natural Language**: 90% intent recognition accuracy
- **Memory Efficiency**: <100ms semantic search

---

## 📞 SUPPORT & ESCALATION

### Development Issues
- **Architecture Questions**: Consult this handbook first
- **MCP Server Issues**: Check consolidated server status
- **Data Questions**: Snowflake is the source of truth
- **Frontend Issues**: Extend UnifiedDashboard.tsx only

### Emergency Contacts
- **System Down**: Check Grafana dashboards
- **Data Loss**: Snowflake recovery procedures
- **Security Breach**: Immediate Pulumi ESC rotation
- **Performance Issues**: Lambda Labs scaling procedures

---

## 🔄 DOCUMENT VERSIONING

**Version History**:
- Phoenix 1.0 (January 2025): Initial unified architecture
- Previous versions: DEPRECATED and removed

**Update Process**:
1. All architectural changes must update this handbook
2. Changes require approval from system architect
3. Version control through Git with clear commit messages
4. Quarterly comprehensive reviews

---

**END OF HANDBOOK**

*This document represents the complete, authoritative architecture for Sophia AI. Any conflicts between this handbook and other documentation should be resolved in favor of this document. The Phoenix has risen.*

---

## 🧠 ENHANCED MEMORY ARCHITECTURE (Phoenix 1.1)

### Multi-Tiered Memory Integration

**Status**: Phase 1 Complete - Foundation Ready
**Next Phase**: Enhanced Unified Chat Service with 5-tier memory

The Phoenix Platform has been enhanced with a sophisticated multi-tiered memory system that integrates Mem0's persistent memory capabilities while maintaining Snowflake as the center of the universe.

### Memory Tier Architecture

```
L1: Session Cache (Redis)           - <50ms access time
L2: Snowflake Cortex (Core)         - <100ms semantic search
L3: Mem0 Persistent (New)           - <200ms cross-session learning
L4: Knowledge Graph (Enhanced)      - Entity relationship memory
L5: LangGraph Workflow (Enhanced)   - Behavioral pattern memory
```

### Enhanced MCP Server Portfolio

**Core Intelligence** (48+ servers - Enhanced):
- `ai_memory` (9000) - Enhanced with 5-tier integration
- `mem0_persistent` (9010) - **NEW**: Cross-session learning
- `sophia_intelligence_unified` (8001) - Memory-aware orchestration
- `snowflake_unified` (8080) - Cortex + Mem0 sync
- `codacy` (3008) - Memory-aware code analysis
- `github` (9003) - Repository memory context
- `linear` (9004) - Project memory tracking
- `asana` (3006) - Task memory correlation

### Enhanced Unified Dashboard

**New Tab**: Memory Analytics
- Multi-tier memory system status
- AI learning progress visualization
- Memory system insights and health
- Cross-tier synchronization metrics

### Implementation Status

**✅ Phase 1 Complete (Foundation)**:
- [x] Snowflake schema enhanced with Mem0 integration
- [x] MCP server configuration deployed
- [x] Session cache enhancement configured
- [x] Mem0 sync procedures created
- [x] Documentation completed

**🚀 Ready for Phase 2**: Enhanced Unified Chat Service with multi-tier memory integration

### Deep Dive Documentation

For complete implementation details, see:
- [Phoenix Memory Integration Plan](./04_PHOENIX_MEMORY_INTEGRATION_PLAN.md)
- [Phoenix Memory Integration Summary](./05_PHOENIX_MEMORY_INTEGRATION_SUMMARY.md)

---

**Version**: Phoenix 1.1 (Memory Enhanced)
**Memory Integration**: Multi-tiered architecture with Mem0 persistent learning
**Status**: Foundation complete, ready for Phase 2 implementation

*The Phoenix Platform now combines the power of Snowflake-centric architecture with sophisticated multi-tiered memory capabilities, enabling persistent learning and contextual intelligence while maintaining our core principle: Snowflake as the center of the universe.*

## 🧹 Codebase Cleanup (Updated 2025-07-03)

### Removed Components
- **Backup Files**: 92 backup files removed
- **Obsolete Directories**: 10 directories removed
- **Deprecated Docker Files**: All non-production Dockerfiles consolidated
- **Legacy FastAPI Apps**: Consolidated to single `unified_fastapi_app.py`
- **Environment Files**: Removed in favor of Pulumi ESC secret management

### Dockcloud Integration
- **Docker Files Updated**: 0 references cleaned
- **Compose Files Updated**: 0 configurations cleaned
- **CI/CD Workflows Updated**: 0 workflows cleaned
- **Secret Management**: 100% Pulumi ESC integration, no local .env files

### Current Architecture
- **Single Dockerfile**: Multi-stage production build
- **Unified FastAPI App**: Single backend application
- **Dockcloud Deployment**: Lambda Labs infrastructure only
- **Enterprise Secrets**: GitHub Org Secrets → Pulumi ESC → Containers

---

## 📚 Table of Contents

1. [🏗️ System Architecture](#system-architecture)
2. [🔧 Core Components](#core-components)
3. [🌊 Data Flow](#data-flow)
4. [🔐 Security & Authentication](#security--authentication)
5. [🚀 Deployment & Operations](#deployment--operations)
6. [📈 Performance & Scaling](#performance--scaling)
7. [🔄 Monorepo Transformation](#monorepo-transformation)
8. [🎯 Unified Interface Architecture](#unified-interface-architecture)
9. [🛠️ Development Guidelines](#development-guidelines)
10. [📊 Business Intelligence](#business-intelligence)
11. [🔮 Future Roadmap](#future-roadmap)

---

## 🎯 Unified Interface Architecture

> **CRITICAL**: Sophia AI uses a SINGLE unified dashboard and SINGLE chat interface. There are no separate CEO, Executive, or Admin dashboards.

### Frontend Architecture (✅ Already Unified)

The frontend implements a clean, unified architecture:

```
frontend/src/components/
├── dashboard/
│   └── UnifiedDashboard.tsx    # THE ONLY DASHBOARD (with 5 tabs)
└── shared/
    └── EnhancedUnifiedChat.tsx  # THE ONLY CHAT INTERFACE
```

#### UnifiedDashboard.tsx
- **Location**: `frontend/src/components/dashboard/UnifiedDashboard.tsx`
- **Purpose**: Single dashboard with role-based content adaptation
- **Tabs**:
  1. **Unified Overview** - Executive KPIs and metrics
  2. **Projects & OKRs** - Cross-platform project management
  3. **Knowledge AI** - Data ingestion and AI learning metrics
  4. **Sales Intelligence** - Pipeline and deal analytics
  5. **Unified Chat** - Integrated chat interface (embeds EnhancedUnifiedChat)

#### EnhancedUnifiedChat.tsx
- **Location**: `frontend/src/components/shared/EnhancedUnifiedChat.tsx`
- **Purpose**: Single chat interface with context switching
- **Contexts**:
  - Business Intelligence
  - CEO Deep Research
  - Internal Only
  - Blended Intelligence
- **Features**:
  - WebSocket real-time communication
  - Source attribution
  - Suggested follow-up questions
  - Role-based access control

### Backend Architecture (🔄 Consolidation in Progress)

The backend is being consolidated into a unified architecture:

#### Target State:
```
backend/
├── services/
│   └── unified_chat_service.py      # THE ONLY CHAT SERVICE
├── api/
│   └── unified_routes.py            # THE ONLY API ROUTES
└── models/
    └── chat_models.py               # Shared data models
```

#### Key Principles:
1. **Single Service Entry Point** - All chat logic in UnifiedChatService
2. **Context-Based Routing** - Internal routing based on chat context
3. **Role-Based Access Control** - CEO, Executive, Manager, Employee levels
4. **Unified Data Models** - Consistent request/response models

### Access Control

The unified interfaces adapt content based on user role:

```python
class AccessLevel(Enum):
    CEO = "ceo"         # Full access to all features and data
    EXECUTIVE = "executive"  # Access to strategic features
    MANAGER = "manager"     # Access to team and project data
    EMPLOYEE = "employee"   # Basic access to relevant data
```

### Important Notes

1. **No Multiple Dashboards** - Despite legacy references in documentation, there is only ONE dashboard
2. **No Multiple Chat Services** - Backend consolidation will result in ONE chat service
3. **Role-Based Adaptation** - The same interfaces show different content based on user role
4. **Context Switching** - Chat interface can switch contexts, not interfaces

---

**END OF HANDBOOK**

*This document represents the complete, authoritative architecture for Sophia AI. Any conflicts between this handbook and other documentation should be resolved in favor of this document. The Phoenix has risen.*

---

## 🔄 SNOWFLAKE CORTEX DUAL-MODE ADAPTER

### Architecture Overview

The Snowflake Cortex service now supports dual-mode operation, providing flexibility and enhanced capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│              Snowflake Cortex Dual-Mode Adapter              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐           ┌─────────────────────────┐  │
│  │   Direct Mode   │           │      MCP Mode           │  │
│  │                 │           │                         │  │
│  │ • SQL Execution │           │ • PAT Authentication    │  │
│  │ • Batch Ops     │           │ • Standardized Tools    │  │
│  │ • Legacy Auth   │           │ • Cortex Search/Analyst │  │
│  └────────┬────────┘           └───────────┬─────────────┘  │
│           │                                 │                 │
│           └─────────────┬───────────────────┘                │
│                         ▼                                     │
│              ┌──────────────────────┐                        │
│              │   Unified Interface   │                        │
│              │  • Auto Mode Selection│                        │
│              │  • Intelligent Routing│                        │
│              │  • Result Caching    │                        │
│              └──────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Mode Selection Strategy

1. **AUTO Mode** (Default):
   - Checks for PAT token availability
   - Falls back to direct mode if needed
   - Task-based routing optimization

2. **DIRECT Mode**:
   - Traditional username/password auth
   - Direct SQL execution
   - Optimal for batch operations

3. **MCP Mode**:
   - Programmatic Access Token (PAT) auth
   - Access to Cortex Search & Analyst
   - Standardized tool interfaces

### Implementation Structure

```
shared/utils/snowflake_cortex/
├── __init__.py          # Exports facade
├── service.py           # Main service class
├── core.py             # Direct SQL adapter
├── mcp_client.py       # MCP server client
├── enums.py            # Models and modes
├── pool.py             # Connection pooling
├── cache.py            # Result caching
└── errors.py           # Error handling
```

### Performance Optimizations

- **Connection Pooling**: 8 concurrent connections (configurable)
- **Result Caching**: Redis-based with semantic similarity
- **Intelligent Routing**: Task-specific mode selection
- **Metrics Tracking**: Prometheus integration

---

## 🎯 MCP REGISTRY V2 & TIERING

### Registry Architecture

The enhanced MCP Registry v2 introduces YAML-based configuration with sophisticated tiering and capability mapping:

```yaml
# Tier Definitions
PRIMARY:   Critical servers (must be operational)
SECONDARY: Important servers (should be operational)
TERTIARY:  Optional servers (nice to have)
```

### Server Capabilities

Each MCP server declares its capabilities for intelligent routing:

```yaml
servers:
  - name: snowflake-official
    tier: PRIMARY
    capabilities: [ANALYTICS, EMBEDDING, SEARCH, COMPLETION]

  - name: redis-cache
    tier: PRIMARY
    capabilities: [CACHE, PUBSUB, STATE]

  - name: ai-memory-v2
    tier: PRIMARY
    capabilities: [MEMORY, EMBEDDINGS, SEARCH]
```

### Registry Features

1. **YAML Configuration**: `config/mcp/mcp_servers.yaml`
2. **Health Monitoring**: Automatic health checks every 30s
3. **Capability Routing**: Find servers by capability
4. **Tier-based Failover**: Primary → Secondary → Tertiary
5. **Metrics Integration**: Prometheus metrics for all operations

### Migration Path

```python
# Old Registry (Deprecated)
from infrastructure.mcp_servers.mcp_registry import MCPRegistry
registry = MCPRegistry()

# New Registry v2
from infrastructure.mcp_servers.registry_v2 import get_registry
registry = get_registry()

# Get primary server for capability
server = registry.get_primary_server_for_capability("ANALYTICS")

# Get all healthy servers
healthy = registry.get_healthy_servers()
```

### Server Distribution (January 2025)

- **PRIMARY Tier**: 9 servers (Snowflake, Redis, AI Memory, Gong, HubSpot, Slack, GitHub, Linear, Codacy)
- **SECONDARY Tier**: 9 servers (Pulumi, Portkey, Lambda Labs, PostgreSQL, UI/UX Agent, Estuary)
- **TERTIARY Tier**: 7 servers (OpenRouter, n8n, Notion, Asana, Perplexity, v0dev, Salesforce)

---

## 2. Core Architecture
### 2.1 Phoenix Plan Overview
The Phoenix Plan represents our strategic architecture, rising from the ashes of complexity into a clean, maintainable system.

**Core Principles:**
- Single source of truth for configuration
- Unified deployment pipeline
- Clear separation of concerns
- Production-first mindset

**Key Components:**
- **Orchestration**: K3s on Lambda Labs (lightweight Kubernetes)
- **Frontend**: Vercel (Next.js)
- **Registry**: Docker Hub (scoobyjava15)
- **Secrets**: Pulumi ESC

### 2.3 Infrastructure Layer
**Deployment Target**: Lambda Labs GPU Infrastructure
- **Primary**: 192.222.58.232 (H100 instance)
- **Orchestration**: K3s (Lightweight Kubernetes)
- **Registry**: scoobyjava15 (Docker Hub)
- **Deployment**: GitHub Actions only

**K3s Architecture**:
```
k8s/
├── base/           # Base manifests
├── overlays/       # Environment configs
│   ├── production/
│   └── staging/
└── helm/          # Helm charts
```

### 2.4 Data Architecture
**Storage Layers**:
1. **PostgreSQL**: Primary relational data
2. **Redis**: Session cache, pub/sub
3. **Snowflake**: Analytics, vector operations
4. **K3s PVCs**: Persistent volume claims for stateful services

## 5. Deployment Procedures
### 5.1 Golden Rule
**ALL DEPLOYMENTS VIA GITHUB ACTIONS - NO LOCAL DEPLOYMENTS**

### 5.2 Deployment Pipeline
1. **Code Push**: Developer pushes to main branch
2. **CI Pipeline**: Tests, linting, security scans
3. **Build**: Docker images built and pushed to registry
4. **Deploy**: K3s manifests applied via kubectl
5. **Verify**: Health checks and monitoring

### 5.3 K3s Deployment
- **Primary Method**: GitHub Actions workflow
- **Manifests**: Kustomize-based in `k8s/` directory
- **Secrets**: Pulumi ESC automatic sync
- **Monitoring**: Prometheus + Grafana stack

### 5.5 Emergency Procedures
**K3s Cluster Recovery**:
```bash
# Rollback deployment
kubectl rollout undo deployment/[name] -n [namespace]

# Emergency restart
kubectl delete pods --all -n [namespace]

# Cluster diagnostics
kubectl get events -A --sort-by='.lastTimestamp'
```

## 10. Operational Excellence
### 10.1 Deployment Checklist
- [ ] All changes committed to Git
- [ ] GitHub Actions workflow passing
- [ ] K3s manifests validated
- [ ] Resource limits defined
- [ ] Health checks implemented
- [ ] Monitoring configured

### 10.2 K3s Best Practices
- Use Kustomize for environment management
- Define resource limits on all containers
- Implement proper health checks
- Use rolling updates for zero downtime
- Monitor resource usage continuously
- Regular backups of stateful data

---
