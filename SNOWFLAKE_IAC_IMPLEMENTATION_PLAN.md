# Snowflake IaC Implementation Plan

**Date:** January 14, 2025
**Scope:** Snowflake Infrastructure as Code + System Optimization

## 🎯 Overview

This plan implements a comprehensive Snowflake IaC solution using Pulumi while optimizing existing tools for better functionality and holistic awareness.

## 📊 Phase 1: Environment Cleanup (Immediate)

### Virtual Environment Cleanup Strategy

**Current Issue:** 2,439 cache directories consuming significant disk space

**Solution:**
```bash
# 1. Clean all Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# 2. Clean virtual environments (preserve main .venv)
find . -path "./.venv" -prune -o -type d -name "venv" -exec rm -rf {} + 2>/dev/null
find . -path "./.venv" -prune -o -type d -name ".venv" -exec rm -rf {} + 2>/dev/null

# 3. Add to .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "venv/" >> .gitignore
echo ".venv/" >> .gitignore
```

**Best Practice:** Use a single virtual environment at project root

## 📋 Phase 2: Snowflake IaC Setup

### 2.1 Initialize Pulumi Project
```bash
cd infrastructure/snowflake_iac
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pulumi login
pulumi stack init dev
```

### 2.2 Configure Snowflake Credentials
```bash
# Using Pulumi ESC (recommended)
pulumi config set snowflake:account $SNOWFLAKE_ACCOUNT
pulumi config set snowflake:username $SNOWFLAKE_USERNAME
pulumi config set snowflake:password $SNOWFLAKE_PASSWORD --secret
pulumi config set snowflake:role SYSADMIN
pulumi config set snowflake:warehouse COMPUTE_WH
```

### 2.3 Deploy Infrastructure
```bash
pulumi preview  # Review changes
pulumi up       # Deploy
```

## 🔧 Phase 3: MCP Server Enhancements

### 3.1 Enhanced Notion MCP Server

**Location:** `infrastructure/mcp_servers/notion_v2/`

**Key Features:**
- Bidirectional sync with Snowflake
- Change detection via polling
- Automatic schema mapping
- Embedding generation triggers

**Implementation:**
```python
# notion_v2/sync_manager.py
class NotionSnowflakeSync:
    def __init__(self):
        self.notion_client = NotionClient()
        self.snowflake_client = SnowflakeClient()

    async def sync_employees(self):
        """Sync employees from Notion to Snowflake"""
        notion_employees = await self.notion_client.get_database_items(
            database_id=EMPLOYEES_DB_ID
        )

        for employee in notion_employees:
            await self.snowflake_client.upsert_employee(
                employee_id=employee.id,
                data=self.transform_employee_data(employee)
            )
```

### 3.2 Enhanced Snowflake MCP Server

**Location:** `infrastructure/mcp_servers/snowflake_v2/`

**Key Features:**
- Natural language to SQL translation
- Vector similarity search
- Cross-schema contextualization
- Caching layer integration

**Implementation:**
```python
# snowflake_v2/query_engine.py
class SnowflakeQueryEngine:
    async def semantic_search(self, query: str, entity_type: str = None):
        """Perform semantic search using embeddings"""
        query_embedding = await self.generate_embedding(query)

        sql = f"""
        SELECT
            ENTITY_TYPE,
            ENTITY_ID,
            NAME,
            DESCRIPTION,
            VECTOR_COSINE_SIMILARITY(EMBEDDING, {query_embedding}) as SIMILARITY
        FROM SOPHIA_AI.FOUNDATIONAL_KNOWLEDGE.V_ENTITY_SEARCH
        WHERE SIMILARITY > 0.7
        ORDER BY SIMILARITY DESC
        LIMIT 10
        """

        return await self.execute_query(sql)
```

## 🚀 Phase 4: Unified Chat Integration

### 4.1 Intent Recognition Enhancement

**File:** `backend/services/unified_chat_service.py`

```python
FOUNDATIONAL_KNOWLEDGE_INTENTS = {
    "find_expert": ["who knows", "expert on", "specialist in"],
    "product_info": ["product features", "what does", "capabilities of"],
    "customer_info": ["tell me about customer", "customer details"],
    "competitive": ["competitor", "how do we compare", "competitive advantage"],
    "pricing": ["pricing for", "cost of", "how much"],
}

async def classify_foundational_intent(query: str):
    """Classify queries related to foundational knowledge"""
    query_lower = query.lower()

    for intent, patterns in FOUNDATIONAL_KNOWLEDGE_INTENTS.items():
        if any(pattern in query_lower for pattern in patterns):
            return intent

    return None
```

### 4.2 Memory Architecture Updates

**6-Tier Memory Integration:**
- **L0 (Hottest):** Current conversation context
- **L1 (Hot):** Frequently accessed foundational knowledge
- **L2 (Warm):** Recent Gong/HubSpot data
- **L3 (Cool):** Historical patterns
- **L4 (Cold):** Archived conversations
- **L5 (Frozen):** Long-term storage in Snowflake

## 📊 Phase 5: Data Flow Architecture

### 5.1 Ingestion Flow
```
User Input (Chat) → Intent Recognition →
    ├── Query Intent → Snowflake MCP → Response
    └── Ingestion Intent → Notion MCP → Notion → Snowflake
```

### 5.2 Query Flow
```
User Query → Unified Chat Service →
    ├── Memory Cache Check (L0-L1)
    ├── Snowflake Semantic Search
    ├── Cross-Schema Join (if needed)
    └── Response Generation with Citations
```

## 🔒 Phase 6: Security & Performance

### 6.1 Security Measures
- Row-level security in Snowflake
- API key rotation for MCP servers
- Encrypted connections
- Audit logging

### 6.2 Performance Optimization
- Materialized views for common queries
- Result caching in Redis
- Batch embedding generation
- Query optimization hints

## 📈 Phase 7: Monitoring & Maintenance

### 7.1 Snowflake Monitoring
```sql
-- Create monitoring views
CREATE VIEW SOPHIA_AI.MONITORING.V_EMBEDDING_FRESHNESS AS
SELECT
    TABLE_NAME,
    COUNT(*) as TOTAL_ROWS,
    SUM(CASE WHEN EMBEDDING IS NULL THEN 1 ELSE 0 END) as MISSING_EMBEDDINGS,
    MAX(UPDATED_AT) as LAST_UPDATE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'FOUNDATIONAL_KNOWLEDGE'
GROUP BY TABLE_NAME;
```

### 7.2 Pulumi State Management
```bash
# Backup state before major changes
pulumi stack export --file backup-$(date +%Y%m%d).json

# Review drift
pulumi refresh
pulumi preview
```

## 🎯 Implementation Timeline

### Week 1: Foundation
- [ ] Environment cleanup
- [ ] Pulumi project setup
- [ ] Basic Snowflake resources deployment
- [ ] Initial tables and schemas

### Week 2: MCP Enhancement
- [ ] Notion MCP v2 development
- [ ] Snowflake MCP v2 development
- [ ] Bidirectional sync implementation
- [ ] Testing and validation

### Week 3: Integration
- [ ] Unified chat enhancements
- [ ] Memory architecture updates
- [ ] End-to-end testing
- [ ] Performance optimization

### Week 4: Production
- [ ] Production deployment
- [ ] Monitoring setup
- [ ] Documentation
- [ ] Team training

## 🚦 Success Metrics

1. **Query Performance:** < 200ms for semantic search
2. **Sync Latency:** < 5 minutes from Notion to Snowflake
3. **Embedding Coverage:** > 95% of entities have embeddings
4. **Cache Hit Rate:** > 80% for common queries
5. **User Satisfaction:** Natural language queries feel intuitive

## 🔧 Quick Start Commands

```bash
# 1. Clean environment
make clean-cache

# 2. Deploy Snowflake
cd infrastructure/snowflake_iac
pulumi up

# 3. Start MCP servers
docker-compose up -d notion-mcp-v2 snowflake-mcp-v2

# 4. Test integration
python scripts/test_foundational_knowledge.py
```

This implementation provides a robust, scalable foundation for Sophia AI's knowledge management while maintaining simplicity and avoiding over-complication.
