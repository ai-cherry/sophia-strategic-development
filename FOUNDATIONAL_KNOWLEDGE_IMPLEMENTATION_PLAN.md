# Foundational Knowledge Implementation Plan - Practical Approach

## 🎯 Executive Summary

Based on the comprehensive plan provided, here's a pragmatic approach to implementing foundational knowledge for Sophia AI. We'll focus on building the essential framework and structure while avoiding over-engineering before we have real data.

## 📊 What to Build Now vs Later

### ✅ Build Now (Essential Framework)

1. **Core Schema Structure**
   - Basic tables for Employees, Customers, Products, Competitors
   - Primary keys and essential relationships only
   - Skip complex JSON fields until we see real data patterns
   - No vector embeddings yet (wait for actual content)

2. **Simple Security Model**
   - Basic RBAC with 3 roles: Admin, User, ReadOnly
   - Skip row-level security until we understand data sensitivity
   - Use existing Sophia AI authentication

3. **Basic Integration Points**
   - Placeholder fields for external system IDs (Gong, HubSpot, etc.)
   - Simple API endpoints for CRUD operations
   - Skip complex synchronization until we have real integrations

4. **Minimal Views**
   - One unified search view across all entities
   - Skip specialized views until usage patterns emerge

### ⏸️ Defer Until Real Data

1. **Complex Fields**
   - JSON arrays for skills, certifications, features
   - Vector embeddings (wait for actual content to embed)
   - Detailed metadata fields
   - Performance metrics and scores

2. **Advanced Features**
   - AI-generated summaries
   - Semantic search capabilities
   - Complex relationship modeling
   - Automated data quality checks

3. **Sophisticated Integrations**
   - Real-time synchronization
   - Conflict resolution
   - Data transformation pipelines
   - External system webhooks

## 🏗️ Phase 1: Minimal Viable Schema (Week 1)

### Core Tables Only

```sql
-- Simplified EMPLOYEES table
CREATE TABLE IF NOT EXISTS EMPLOYEES (
    EMPLOYEE_ID VARCHAR(255) PRIMARY KEY,
    EMAIL VARCHAR(255) UNIQUE NOT NULL,
    FIRST_NAME VARCHAR(255) NOT NULL,
    LAST_NAME VARCHAR(255) NOT NULL,
    JOB_TITLE VARCHAR(255),
    DEPARTMENT VARCHAR(255),
    MANAGER_ID VARCHAR(255),
    STATUS VARCHAR(50) DEFAULT 'active',

    -- External IDs (for future integration)
    SLACK_USER_ID VARCHAR(255),
    GONG_USER_ID VARCHAR(255),

    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Simplified CUSTOMERS table
CREATE TABLE IF NOT EXISTS CUSTOMERS (
    CUSTOMER_ID VARCHAR(255) PRIMARY KEY,
    COMPANY_NAME VARCHAR(500) NOT NULL,
    INDUSTRY VARCHAR(255),
    STATUS VARCHAR(50) DEFAULT 'active',
    TIER VARCHAR(50),

    -- Key relationship
    SUCCESS_MANAGER_ID VARCHAR(255),

    -- External IDs
    HUBSPOT_COMPANY_ID VARCHAR(255),
    SALESFORCE_ACCOUNT_ID VARCHAR(255),

    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Simplified PRODUCTS table
CREATE TABLE IF NOT EXISTS PRODUCTS (
    PRODUCT_ID VARCHAR(255) PRIMARY KEY,
    PRODUCT_NAME VARCHAR(500) NOT NULL,
    PRODUCT_CATEGORY VARCHAR(255),
    STATUS VARCHAR(50) DEFAULT 'active',

    -- Key relationship
    PRODUCT_MANAGER_ID VARCHAR(255),

    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Simplified COMPETITORS table
CREATE TABLE IF NOT EXISTS COMPETITORS (
    COMPETITOR_ID VARCHAR(255) PRIMARY KEY,
    COMPANY_NAME VARCHAR(500) NOT NULL,
    INDUSTRY VARCHAR(255),
    THREAT_LEVEL VARCHAR(50),

    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Basic Search View

```sql
CREATE OR REPLACE VIEW VW_KNOWLEDGE_SEARCH AS
SELECT
    'EMPLOYEE' AS TYPE,
    EMPLOYEE_ID AS ID,
    CONCAT(FIRST_NAME, ' ', LAST_NAME) AS NAME,
    EMAIL AS KEY_INFO,
    DEPARTMENT AS CATEGORY
FROM EMPLOYEES
WHERE STATUS = 'active'

UNION ALL

SELECT
    'CUSTOMER' AS TYPE,
    CUSTOMER_ID AS ID,
    COMPANY_NAME AS NAME,
    INDUSTRY AS KEY_INFO,
    TIER AS CATEGORY
FROM CUSTOMERS
WHERE STATUS = 'active'

UNION ALL

SELECT
    'PRODUCT' AS TYPE,
    PRODUCT_ID AS ID,
    PRODUCT_NAME AS NAME,
    PRODUCT_CATEGORY AS KEY_INFO,
    STATUS AS CATEGORY
FROM PRODUCTS

UNION ALL

SELECT
    'COMPETITOR' AS TYPE,
    COMPETITOR_ID AS ID,
    COMPANY_NAME AS NAME,
    INDUSTRY AS KEY_INFO,
    THREAT_LEVEL AS CATEGORY
FROM COMPETITORS;
```

## 🔌 Phase 2: Basic API Integration (Week 2)

### Simple REST Endpoints

```python
# Basic CRUD endpoints for each entity
POST   /api/v2/knowledge/employees
GET    /api/v2/knowledge/employees/{id}
PUT    /api/v2/knowledge/employees/{id}
DELETE /api/v2/knowledge/employees/{id}
GET    /api/v2/knowledge/employees/search?q={query}

# Same pattern for customers, products, competitors
```

### Integration with Memory V2

```python
# Store knowledge operations as memories
async def store_knowledge_memory(
    entity_type: str,
    entity_id: str,
    operation: str,
    user_id: str
):
    await memory_client.store_memory(
        MemoryType.EVENT,
        content={
            "entity_type": entity_type,
            "entity_id": entity_id,
            "operation": operation,
            "user_id": user_id
        }
    )
```

## 📥 Phase 3: Smart Data Ingestion Strategy

### 1. Start with Manual Entry (Week 3)
- Build simple web forms for data entry
- Focus on getting 10-20 records of each type
- Learn data patterns from manual entry
- Identify which fields are actually used

### 2. CSV Import Next (Week 4)
- Build CSV import with validation
- Map CSV columns to database fields
- Handle basic data conflicts
- Generate import reports

### 3. API Integration Last (Week 5+)
- Start with read-only integration
- Pull data on-demand first
- Add sync only after understanding data patterns
- Build incremental sync, not full refresh

## 🎯 First Steps for Real Data Ingestion

### Week 1: Manual Foundation
1. **Create 5-10 employee records manually**
   - Start with leadership team
   - Understand actual job titles and departments
   - See which fields are actually needed

2. **Add 5-10 key customers**
   - Start with top revenue customers
   - Understand industry categories
   - Learn tier definitions

3. **Document patterns observed**
   - Which fields are always empty?
   - What additional fields are needed?
   - What validation rules emerge?

### Week 2: Bulk Import Preparation
1. **Export existing data from source systems**
   - Get employee list from HR system
   - Export customer list from CRM
   - Product catalog from documentation

2. **Create mapping templates**
   - Excel templates with required columns
   - Data validation rules
   - Import instructions

3. **Build import scripts**
   ```python
   # Simple CSV importer
   def import_employees_csv(file_path):
       df = pd.read_csv(file_path)

       # Validate required fields
       required = ['email', 'first_name', 'last_name']
       missing = [col for col in required if col not in df.columns]
       if missing:
           raise ValueError(f"Missing columns: {missing}")

       # Import with basic validation
       for _, row in df.iterrows():
           create_employee(
               email=row['email'],
               first_name=row['first_name'],
               last_name=row['last_name'],
               job_title=row.get('job_title', 'Unknown'),
               department=row.get('department', 'Unknown')
           )
   ```

### Week 3: External System Integration
1. **Start with Gong (most valuable)**
   - Map Gong users to employees
   - Link Gong companies to customers
   - Pull call participants only (not full transcripts)

2. **Then HubSpot**
   - Sync company records
   - Map contacts to employees
   - Update customer tiers

3. **Slack last**
   - Just map user IDs initially
   - Don't import message content yet

## 🚫 What NOT to Do Yet

### Avoid These Temptations:
1. **Don't build complex JSON schemas** - Wait to see real data
2. **Don't implement vector search** - Need actual content first
3. **Don't create 50+ fields per table** - Start with 10-15 max
4. **Don't build real-time sync** - Batch updates are fine initially
5. **Don't implement complex RBAC** - Basic roles are sufficient
6. **Don't optimize for performance** - Get it working first

### Skip These Features:
- AI-generated summaries
- Semantic embeddings
- Complex relationship graphs
- Automated data quality scores
- Real-time change notifications
- Multi-level approval workflows

## 📈 Success Metrics for Phase 1

### Week 1 Goals:
- [ ] Schema deployed to Snowflake
- [ ] Basic API endpoints working
- [ ] 10 manual records in each table
- [ ] Simple search functionality

### Week 2 Goals:
- [ ] CSV import working
- [ ] 100+ employees imported
- [ ] 50+ customers imported
- [ ] Basic data validation

### Week 3 Goals:
- [ ] Gong user mapping complete
- [ ] HubSpot company sync working
- [ ] First insights from real data
- [ ] Schema adjustments identified

## 🎉 Summary

**Start Simple:**
1. Build minimal schema (4 tables, 10 fields each)
2. Create basic CRUD APIs
3. Import data manually first
4. Learn from real data patterns
5. Enhance based on actual usage

**Avoid Complexity:**
- No AI features yet
- No complex integrations
- No advanced security
- No performance optimization
- No real-time anything

**Focus on Value:**
- Get real data in the system
- Make it searchable
- Learn what's actually needed
- Build features users request
- Iterate based on feedback

This approach will have you up and running with real, useful data in 3 weeks instead of spending 3 months building features you might not need!
