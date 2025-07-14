# 🗄️ Sophia AI Complete Database Schema Documentation
**Date:** December 2024
**Status:** Production Active

## 📊 Overview

Sophia AI uses a multi-database architecture optimized for different workloads:

- **PostgreSQL** - Transactional data and business entities
- **Weaviate** - Vector embeddings and semantic search  
- **Redis** - High-performance caching layer
- **Modern Stack** - Enterprise data warehouse (migration in progress)

## 🐘 PostgreSQL Schemas

### Core Database: `sophia_ai_db`

#### 1. **Companies Table**
```sql
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    founded_date DATE,
    headquarters VARCHAR(255),
    website VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. **Financial Metrics Table**
```sql
CREATE TABLE IF NOT EXISTS financial_metrics (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    metric_date DATE NOT NULL,
    revenue DECIMAL(15,2),
    profit DECIMAL(15,2),
    expenses DECIMAL(15,2),
    growth_rate DECIMAL(5,2),
    market_share DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. **Customer Metrics Table**
```sql
CREATE TABLE IF NOT EXISTS customer_metrics (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    metric_date DATE NOT NULL,
    total_customers INTEGER,
    new_customers INTEGER,
    churned_customers INTEGER,
    retention_rate DECIMAL(5,2),
    acquisition_cost DECIMAL(10,2),
    lifetime_value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. **Strategic Initiatives Table**
```sql
CREATE TABLE IF NOT EXISTS strategic_initiatives (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'planning',
    priority VARCHAR(20) DEFAULT 'medium',
    start_date DATE,
    target_date DATE,
    completion_date DATE,
    progress_percentage INTEGER DEFAULT 0,
    budget DECIMAL(12,2),
    owner VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. **AI Insights Table**
```sql
CREATE TABLE IF NOT EXISTS ai_insights (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    insight_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    confidence_score DECIMAL(3,2),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'new',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    implemented_at TIMESTAMP
);
```

### Staging Schemas (pgvector enabled)

#### **Gong Schema**
```sql
CREATE SCHEMA IF NOT EXISTS gong_raw;

CREATE TABLE IF NOT EXISTS gong_raw.stg_gong_calls (
    call_id TEXT PRIMARY KEY,
    call_title TEXT,
    call_datetime_utc TIMESTAMP WITH TIME ZONE,
    call_duration_seconds NUMERIC,
    primary_user_email TEXT,
    primary_user_name TEXT,
    hubspot_deal_id TEXT,
    deal_stage TEXT,
    deal_value NUMERIC(15,2),
    sentiment_score REAL,
    call_summary TEXT,
    key_topics JSONB,
    risk_indicators JSONB,
    next_steps JSONB,
    embedding VECTOR(768),  -- pgvector for semantic search
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **HubSpot Schema**
```sql
CREATE SCHEMA IF NOT EXISTS hubspot_raw;

CREATE TABLE IF NOT EXISTS hubspot_raw.stg_hubspot_contacts (
    contact_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    company_name TEXT,
    job_title TEXT,
    lifecycle_stage TEXT,
    lead_status TEXT,
    associated_company_id TEXT,
    create_date TIMESTAMP WITH TIME ZONE,
    last_modified_date TIMESTAMP WITH TIME ZONE,
    full_name TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hubspot_raw.stg_hubspot_deals (
    deal_id TEXT PRIMARY KEY,
    deal_name TEXT,
    deal_stage TEXT,
    deal_amount NUMERIC(15,2),
    close_date TIMESTAMP WITH TIME ZONE,
    create_date TIMESTAMP WITH TIME ZONE,
    pipeline_name TEXT,
    deal_owner TEXT,
    associated_contact_id TEXT,
    associated_company_id TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Estuary Flow Tables
```sql
CREATE SCHEMA IF NOT EXISTS estuary_raw;

CREATE TABLE IF NOT EXISTS estuary_raw.hubspot_contacts (
    id VARCHAR PRIMARY KEY,
    email VARCHAR,
    firstname VARCHAR,
    lastname VARCHAR,
    company VARCHAR,
    phone VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    properties JSONB,
    _estuary_flow_document JSONB,
    _estuary_flow_published_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS estuary_raw.gong_calls (
    id VARCHAR PRIMARY KEY,
    title VARCHAR,
    url VARCHAR,
    started TIMESTAMP,
    duration INTEGER,
    participants JSONB,
    transcript TEXT,
    summary TEXT,
    sentiment VARCHAR,
    topics JSONB,
    created_at TIMESTAMP,
    _estuary_flow_document JSONB,
    _estuary_flow_published_at TIMESTAMP DEFAULT NOW()
);
```

## 🔍 Weaviate Vector Database Schemas

### Knowledge Collection
```python
{
    "class": "Knowledge",
    "description": "General knowledge and document storage",
    "vectorIndexType": "hnsw",
    "vectorizer": "text2vec-transformers",
    "properties": [
        {
            "name": "content",
            "dataType": ["text"],
            "description": "The main content/text"
        },
        {
            "name": "title",
            "dataType": ["text"],
            "description": "Title or summary of the content"
        },
        {
            "name": "source",
            "dataType": ["text"],
            "description": "Source of the knowledge"
        },
        {
            "name": "metadata",
            "dataType": ["text"],
            "description": "JSON metadata"
        },
        {
            "name": "category",
            "dataType": ["text"],
            "description": "Category or type of knowledge"
        },
        {
            "name": "timestamp",
            "dataType": ["date"],
            "description": "When this was created"
        },
        {
            "name": "user_id",
            "dataType": ["text"],
            "description": "User who created this"
        }
    ]
}
```

### UserProfile Collection
```python
{
    "class": "UserProfile",
    "description": "User preferences and interaction patterns",
    "vectorIndexType": "hnsw",
    "vectorizer": "text2vec-transformers",
    "properties": [
        {
            "name": "user_id",
            "dataType": ["text"]
        },
        {
            "name": "personality_preferences",
            "dataType": ["text"]
        },
        {
            "name": "interaction_history",
            "dataType": ["text"]
        },
        {
            "name": "communication_style",
            "dataType": ["text"]
        },
        {
            "name": "last_updated",
            "dataType": ["date"]
        }
    ]
}
```

### Conversation Collection
```python
{
    "class": "Conversation",
    "description": "Chat conversations and interactions",
    "vectorIndexType": "hnsw",
    "vectorizer": "text2vec-transformers",
    "properties": [
        {
            "name": "message",
            "dataType": ["text"]
        },
        {
            "name": "role",
            "dataType": ["text"],
            "description": "Role (user/assistant/system)"
        },
        {
            "name": "session_id",
            "dataType": ["text"]
        },
        {
            "name": "user_id",
            "dataType": ["text"]
        },
        {
            "name": "timestamp",
            "dataType": ["date"]
        },
        {
            "name": "context",
            "dataType": ["text"],
            "description": "Additional context (JSON)"
        }
    ]
}
```

### AgentMemory Collection
```python
{
    "class": "AgentMemory",
    "description": "MCP agent memories and learnings",
    "vectorIndexType": "hnsw",
    "vectorizer": "text2vec-transformers",
    "properties": [
        {
            "name": "memory",
            "dataType": ["text"]
        },
        {
            "name": "agent_id",
            "dataType": ["text"]
        },
        {
            "name": "memory_type",
            "dataType": ["text"]
        },
        {
            "name": "source",
            "dataType": ["text"]
        },
        {
            "name": "timestamp",
            "dataType": ["date"]
        },
        {
            "name": "importance",
            "dataType": ["number"]
        }
    ]
}
```

## 🚀 Redis Cache Layers

### Cache Configuration
```yaml
# Three-tier caching strategy

L1_HOT_CACHE:
  ttl: 300       # 5 minutes
  max_size: 1000
  patterns:
    - "llm:response:*"
    - "user:session:*"
    - "dashboard:metrics:*"

L2_WARM_CACHE:  
  ttl: 3600      # 1 hour
  max_size: 10000
  patterns:
    - "vector:*"
    - "search:*"
    - "api:response:*"

L3_COLD_CACHE:
  ttl: 86400     # 24 hours
  max_size: 100000
  patterns:
    - "knowledge:*"
    - "gong:call:*"
    - "slack:msg:*"
```

### Cache Key Patterns
```
# LLM responses
llm:response:{prompt_hash}:{model}:{timestamp}

# Vector embeddings
vector:{content_hash}:{model}:{dimension}

# Search results
search:{query_hash}:{limit}:{filters}

# User sessions
user:session:{user_id}:{session_id}

# API responses
api:response:{endpoint}:{param_hash}

# Dashboard metrics
dashboard:metrics:{metric_type}:{date_range}

# Gong call cache
gong:call:{call_id}:{data_type}

# Slack message cache
slack:msg:{message_id}:{channel}
```

## ❄️ Modern Stack Data Warehouse (Legacy - Migration in Progress)

### Database: SOPHIA_AI_PRODUCTION

#### Core Schemas
```sql
-- Core platform schema
CREATE SCHEMA IF NOT EXISTS SOPHIA_CORE;

-- AI Memory schema
CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_MEMORY;

-- Business Intelligence schema
CREATE SCHEMA IF NOT EXISTS SOPHIA_BUSINESS_INTELLIGENCE;

-- Project Management schema
CREATE SCHEMA IF NOT EXISTS SOPHIA_PROJECT_MANAGEMENT;

-- Knowledge Base schema
CREATE SCHEMA IF NOT EXISTS SOPHIA_KNOWLEDGE_BASE;
```

#### AI Memory Tables
```sql
CREATE TABLE IF NOT EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS (
    memory_id VARCHAR(255) PRIMARY KEY,
    conversation_id VARCHAR(255),
    user_id VARCHAR(255),
    agent_id VARCHAR(255),
    content TEXT NOT NULL,
    memory_type VARCHAR(50) DEFAULT 'conversation',
    importance_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    last_accessed TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    access_count INTEGER DEFAULT 0,
    metadata VARIANT,
    tags ARRAY,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS SOPHIA_AI_MEMORY.MEMORY_EMBEDDINGS (
    embedding_id VARCHAR(255) PRIMARY KEY,
    memory_id VARCHAR(255) REFERENCES MEMORY_RECORDS(memory_id),
    embedding VECTOR(FLOAT, 768),
    embedding_model VARCHAR(100) DEFAULT 'e5-base-v2',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    vector_dimension INTEGER DEFAULT 768
);
```

#### Foundational Knowledge Tables
```sql
CREATE TABLE IF NOT EXISTS FOUNDATIONAL_KNOWLEDGE.EMPLOYEES (
    EMPLOYEE_ID VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    EMAIL VARCHAR(255) UNIQUE NOT NULL,
    FIRST_NAME VARCHAR(255) NOT NULL,
    LAST_NAME VARCHAR(255) NOT NULL,
    JOB_TITLE VARCHAR(255),
    DEPARTMENT VARCHAR(255),
    MANAGER_ID VARCHAR(255),
    STATUS VARCHAR(50) DEFAULT 'active',
    SLACK_USER_ID VARCHAR(255),
    GONG_USER_ID VARCHAR(255),
    HUBSPOT_OWNER_ID VARCHAR(255),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(255) DEFAULT CURRENT_USER,
    FOREIGN KEY (MANAGER_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);

CREATE TABLE IF NOT EXISTS FOUNDATIONAL_KNOWLEDGE.CUSTOMERS (
    CUSTOMER_ID VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    COMPANY_NAME VARCHAR(500) NOT NULL,
    INDUSTRY VARCHAR(255),
    STATUS VARCHAR(50) DEFAULT 'active',
    TIER VARCHAR(50),
    SUCCESS_MANAGER_ID VARCHAR(255),
    HUBSPOT_COMPANY_ID VARCHAR(255),
    SALESFORCE_ACCOUNT_ID VARCHAR(255),
    GONG_COMPANY_ID VARCHAR(255),
    ANNUAL_REVENUE DECIMAL(15,2),
    EMPLOYEE_COUNT INTEGER,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(255) DEFAULT CURRENT_USER,
    FOREIGN KEY (SUCCESS_MANAGER_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);
```

## 🔄 Data Flow Architecture

### 1. **Real-time Ingestion Pipeline**
```
External Sources → Estuary Flow → PostgreSQL (Staging) → Enrichment → Weaviate/Redis
                                          ↓
                                    Modern Stack (Legacy)
```

### 2. **Query Flow**
```
User Query → Redis (L1) → Weaviate (L2) → PostgreSQL (L3) → Modern Stack (Legacy)
               ↓              ↓                ↓
           <10ms         <50ms           <100ms
```

### 3. **Cache Hierarchy**
```
Hot Data (Redis) → Warm Data (Weaviate) → Cold Data (PostgreSQL) → Archive (Modern Stack)
  5 min TTL          1 hour TTL              24 hour TTL             Permanent
```

## 📊 Performance Characteristics

| Database | Primary Use | Latency | Capacity |
|----------|------------|---------|----------|
| Redis | Hot cache, sessions | <10ms | 100GB |
| Weaviate | Vector search | <50ms | 500GB |
| PostgreSQL | Transactional, hybrid | <100ms | 2TB |
| Modern Stack | Analytics, archive | <500ms | Unlimited |

## 🛡️ Security & Access Control

### PostgreSQL
- Row-level security policies
- Role-based access control
- SSL/TLS encryption in transit
- Encrypted at rest

### Weaviate
- API key authentication
- Collection-level permissions
- TLS encryption

### Redis
- Password authentication
- Network isolation
- No persistence for sensitive data

### Modern Stack
- Multi-factor authentication
- Role hierarchy (ACCOUNTADMIN → SYSADMIN → USERADMIN)
- Network policies
- End-to-end encryption

## 🔧 Migration Status

### Current State (December 2024)
- ✅ PostgreSQL: Fully operational
- ✅ Weaviate: Fully operational (primary vector store)
- ✅ Redis: Fully operational (3-tier cache)
- ⚠️ Modern Stack: Legacy, migration in progress

### Migration Plan
1. **Phase 1**: Move hot data to Redis (Complete)
2. **Phase 2**: Move vector search to Weaviate (Complete)
3. **Phase 3**: Move transactional data to PostgreSQL (In Progress)
4. **Phase 4**: Keep Modern Stack for historical analytics only

## 📈 Monitoring & Maintenance

### Key Metrics
- Query latency by database
- Cache hit ratios
- Storage utilization
- Connection pool health
- Vector search accuracy

### Maintenance Tasks
- Weekly vacuum on PostgreSQL
- Redis memory optimization
- Weaviate index rebuilds
- compute cluster auto-suspend

## 🚀 Future Enhancements

1. **Graph Database Integration**
   - Neo4j for relationship mapping
   - Entity resolution graphs

2. **Time-series Optimization**
   - TimescaleDB for metrics
   - InfluxDB for monitoring data

3. **Advanced Caching**
   - Semantic cache with embeddings
   - Predictive cache warming

4. **Multi-region Deployment**
   - Read replicas
   - Geo-distributed caching 