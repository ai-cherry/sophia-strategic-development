# SOPHIA AI SYSTEM HANDBOOK
## The Definitive Source of Truth

**Version**: Phoenix 1.0  
**Last Updated**: January 2025  
**Status**: AUTHORITATIVE - This document supersedes all previous architecture documentation

---

## 🔥 THE PHOENIX ARCHITECTURE

### Core Principle: Snowflake as the Center of the Universe

Sophia AI operates on a unified architecture where **Snowflake is the single, undisputed source of truth** for all data—structured, unstructured, and vectorized. This eliminates the fragmentation that previously existed across multiple databases and vector stores.

```
┌─────────────────────────────────────────────────────────────┐
│                    SOPHIA AI PHOENIX PLATFORM                │
├─────────────────────────────────────────────────────────────┤
│  Frontend: Unified Dashboard (React + TypeScript)            │
│  ├─ CEO Universal Chat (Primary Interface)                   │
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

### Tiered Memory System

1. **L3 - Deep Storage**: All raw business data in Snowflake tables
2. **L2 - Semantic Memory**: Cortex embeddings with vector search
3. **L1 - Fast Cache**: Materialized views and result caching

**No Redis. No Pinecone. No Weaviate. No PostgreSQL for business data.**

---

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

**27 Consolidated MCP Servers** (reduced from 36+ fragmented servers):

**Core Intelligence** (7 servers):
- `ai_memory` - Snowflake Cortex native memory
- `sophia_intelligence_unified` - Central AI orchestration
- `snowflake_unified` - Single database interface
- `codacy` - Code quality and security
- `github` - Repository management
- `linear` - Engineering project management
- `asana` - Product management

**Business Intelligence** (8 servers):
- `hubspot_unified` - CRM and sales data
- `gong` - Call analysis and sales intelligence
- `slack_unified` - Communication analytics
- `notion` - Knowledge management
- `intercom` - Customer support
- `salesforce` - Extended CRM
- `apollo` - Sales prospecting
- `bright_data` - Market intelligence

**Infrastructure** (7 servers):
- `lambda_labs_cli` - GPU compute management
- `pulumi` - Infrastructure as code
- `portkey_admin` - LLM gateway optimization
- `postgres` - Legacy system bridge
- `playwright` - Browser automation
- `figma_context` - Design system integration
- `apify_intelligence` - Web scraping

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
  const [activeTab, setActiveTab] = useState('universal-chat');
  
  return (
    <div className="unified-dashboard">
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      
      {activeTab === 'universal-chat' && <UniversalChatInterface />}
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

### Tab Definitions

1. **Universal Chat** - Primary interface, contextualized AI chat
2. **Projects & OKRs** - Cross-platform project health (Linear + Asana + Slack)
3. **Knowledge AI** - File upload, learning status, AI training metrics
4. **Sales Intelligence** - Revenue engine, deal analysis, forecasting
5. **System Health** - MCP server status, API health, performance metrics
6. **Financials** - NetSuite integration, revenue analytics
7. **Employees** - HR systems (Lattice, Trinet), team management
8. **Sophia Persona** - AI personality customization, skills management

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Infrastructure Stack

**Primary Deployment**: Vercel (Frontend) + Lambda Labs (Backend)
**Database**: Snowflake (Single source of truth)
**Secrets Management**: Pulumi ESC
**Container Orchestration**: Kubernetes (Lambda Labs)
**Monitoring**: Grafana + Prometheus

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
-- CEO Dashboard Queries (Natural Language → SQL)
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

# Backend (CEO Test Server)
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

### Phase 5: CEO Management (Weeks 9-10)
- [ ] User management system
- [ ] Tab access permissions
- [ ] LLM usage analytics
- [ ] Sophia persona customization

### Phase 6: System Excellence (Weeks 11-12)
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation completion
- [ ] Production deployment

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
