# 🏗️ SOPHIA AI ARCHITECTURE

## System Overview

Sophia AI is an enterprise-grade AI orchestrator platform designed for business intelligence and automation.

### Core Principles
- **Agent-Centric**: Specialized AI agents for different business functions
- **MCP-Driven**: Model Context Protocol for all integrations
- **Production-First**: Direct production deployment, no staging environments
- **Security-First**: SOC2 compliant with comprehensive audit trails

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOPHIA AI ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer (React + Next.js)                              │
│  ├── Unified Dashboard        ├── Knowledge Dashboard              │
│  ├── Project Dashboard    └── Conversational Interface         │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway Layer (FastAPI)                                   │
│  ├── Authentication       ├── Rate Limiting                    │
│  ├── Request Routing      └── Response Caching                 │
├─────────────────────────────────────────────────────────────────┤
│  Agent Orchestration Layer                                     │
│  ├── Base Agents          ├── Specialized Agents              │
│  ├── LangGraph Workflows  └── Task Management                  │
├─────────────────────────────────────────────────────────────────┤
│  MCP Server Network                                            │
│  ├── AI Memory (9000)     ├── Modern Stack Admin (9012)          │
│  ├── Gong Intelligence    ├── HubSpot CRM                     │
│  ├── Slack Integration    └── Linear Projects                  │
├─────────────────────────────────────────────────────────────────┤
│  Data & Intelligence Layer                                     │
│  ├── Modern Stack (Structured)├── Pinecone (Vectors)             │
│  ├── Semantic Search      └── Memory Management               │
├─────────────────────────────────────────────────────────────────┤
│  External Integrations                                         │
│  ├── Gong (Sales)         ├── HubSpot (CRM)                   │
│  ├── Slack (Comms)        ├── Linear (Projects)               │
│  ├── GitHub (Code)        └── OpenRouter (LLMs)               │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Agent Architecture
All agents inherit from `BaseAgent` class providing:
- Standardized task execution
- Health monitoring
- Performance tracking
- Configuration management

### MCP Integration
Model Context Protocol servers handle all external integrations:
- Standardized interface
- Health monitoring
- Port management
- Tool schemas
- **AI Agent Authentication**: Enterprise-grade security for real infrastructure changes
- **Risk-Based Operations**: CRITICAL/HIGH/MEDIUM/LOW risk classification
- **Complete Audit Trail**: All AI agent operations logged and traceable

### AI Agent Authentication System
Revolutionary three-tier security architecture enabling AI agents to make real infrastructure changes:

#### **Tier 1: CLI-Based Authentication (Highest Security)**
- **GitHub**: Secure token storage with `gh auth login`
- **Pulumi**: Organization access with infrastructure deployment capabilities
- **Docker**: Registry operations with container management
- **Lambda Labs**: Frontend deployment automation

#### **Tier 2: Enhanced API Authentication**
- **Modern Stack**: Role-based database access with query execution
- **Lambda Labs**: GPU instance management with cost optimization
- **Estuary Flow**: Data pipeline operations with real-time flows

#### **Tier 3: Secure API Key Management**
- **OpenAI/Anthropic**: AI model access with cost tracking
- **Slack/Linear/HubSpot**: Business tool integration with audit trails

#### **Agent Permission Matrix**
- **Infrastructure Agent**: Can deploy infrastructure, manage containers (CRITICAL risk)
- **Data Agent**: Can execute database operations, manage schemas (HIGH risk)
- **Integration Agent**: Can create tickets, send messages (MEDIUM risk)

#### **Enterprise Security Features**
- **Zero Trust Authentication**: Every operation explicitly authenticated
- **Risk-Based Confirmation**: CRITICAL operations require user approval
- **Complete Audit Trail**: All actions logged with full traceability
- **Permission Validation**: Agent type permissions enforced

### Data Flow
1. External data → MCP servers → Structured storage
2. User queries → Agent orchestration → Data retrieval
3. AI processing → Response generation → User interface
4. **AI Agent Operations** → Authentication → Risk Assessment → Execution → Audit

For detailed implementation patterns, see [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md) and [MCP_INTEGRATION.md](MCP_INTEGRATION.md).
