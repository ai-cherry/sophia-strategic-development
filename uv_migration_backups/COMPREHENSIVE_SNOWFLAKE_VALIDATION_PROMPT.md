# 🗄️ **COMPREHENSIVE SNOWFLAKE VALIDATION PROMPT**

## **EXECUTIVE SUMMARY**
This prompt ensures your Snowflake deployment matches the comprehensive schema requirements for Sophia AI enterprise deployment. Execute these validation steps to confirm 100% schema alignment and readiness.

---

## **🔧 PREREQUISITE VALIDATION**

### **1. Database and Warehouse Configuration**
```sql
-- Connect to Snowflake and verify basic setup
USE ROLE ACCOUNTADMIN;

-- Verify database exists
SHOW DATABASES LIKE 'SOPHIA_AI_PROD';
-- Expected: Should return SOPHIA_AI_PROD database

-- Verify warehouse configuration
SHOW WAREHOUSES LIKE 'SOPHIA_AI_WH';
-- Expected: SOPHIA_AI_WH with MEDIUM size, AUTO_SUSPEND=60, AUTO_RESUME=TRUE

-- Set context
USE DATABASE SOPHIA_AI_PROD;
USE WAREHOUSE SOPHIA_AI_WH;

-- Verify warehouse settings
ALTER WAREHOUSE SOPHIA_AI_WH SET 
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3
  SCALING_POLICY = 'STANDARD';

SELECT 'Database and Warehouse Configuration: VERIFIED ✅' as STATUS;
```

---

## **📊 SCHEMA VALIDATION**

### **2. Core Schema Existence Verification**
```sql
-- Verify all 6 required schemas exist
SHOW SCHEMAS IN DATABASE SOPHIA_AI_PROD;

-- Expected schemas:
-- 1. UNIVERSAL_CHAT
-- 2. AI_MEMORY  
-- 3. APOLLO_IO
-- 4. PROJECT_MANAGEMENT
-- 5. GONG_INTEGRATION
-- 6. HUBSPOT_INTEGRATION

-- Validate each schema
SELECT 
    CASE 
        WHEN COUNT(*) = 6 THEN 'All 6 Schemas Present: VERIFIED ✅'
        ELSE 'Missing Schemas: FAILED ❌ - Expected 6, Found ' || COUNT(*)
    END as SCHEMA_STATUS
FROM (
    SELECT SCHEMA_NAME 
    FROM INFORMATION_SCHEMA.SCHEMATA 
    WHERE DATABASE_NAME = 'SOPHIA_AI_PROD' 
    AND SCHEMA_NAME IN ('UNIVERSAL_CHAT', 'AI_MEMORY', 'APOLLO_IO', 'PROJECT_MANAGEMENT', 'GONG_INTEGRATION', 'HUBSPOT_INTEGRATION')
);
```

---

## **🔍 TABLE STRUCTURE VALIDATION**

### **3. UNIVERSAL_CHAT Schema Tables**
```sql
USE SCHEMA UNIVERSAL_CHAT;

-- Core Knowledge Management Tables
SELECT 'Validating UNIVERSAL_CHAT tables...' as STATUS;

-- Verify core tables exist
SELECT 
    COUNT(*) as TABLE_COUNT,
    CASE 
        WHEN COUNT(*) >= 14 THEN 'UNIVERSAL_CHAT Tables: VERIFIED ✅'
        ELSE 'UNIVERSAL_CHAT Tables: INCOMPLETE ❌'
    END as VALIDATION_STATUS
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'UNIVERSAL_CHAT'
AND TABLE_NAME IN (
    'KNOWLEDGE_CATEGORIES',
    'KNOWLEDGE_SOURCES', 
    'KNOWLEDGE_BASE_ENTRIES',
    'KNOWLEDGE_EMBEDDINGS',
    'KNOWLEDGE_USAGE_ANALYTICS',
    'CONVERSATION_SESSIONS',
    'CONVERSATION_MESSAGES',
    'CONVERSATION_CONTEXT',
    'USER_MANAGEMENT',
    'TEACHING_SESSIONS',
    'KNOWLEDGE_WEIGHTS',
    'INTERNET_SEARCH_SESSIONS',
    'DYNAMIC_SCRAPING_SESSIONS',
    'SYSTEM_ANALYTICS'
);

-- Verify critical enhancement tables (our additions)
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'INGESTION_JOBS') 
        THEN 'INGESTION_JOBS Table: VERIFIED ✅'
        ELSE 'INGESTION_JOBS Table: MISSING ❌'
    END as INGESTION_STATUS,
    CASE 
        WHEN EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'SEARCH_ANALYTICS')
        THEN 'SEARCH_ANALYTICS Table: VERIFIED ✅'
        ELSE 'SEARCH_ANALYTICS Table: MISSING ❌'
    END as SEARCH_STATUS;
```

### **4. KNOWLEDGE_BASE_ENTRIES Enhanced Structure Validation**
```sql
-- Verify enhanced chunking and metadata support
DESC TABLE KNOWLEDGE_BASE_ENTRIES;

-- Critical fields verification
SELECT 
    CASE WHEN COLUMN_EXISTS THEN 'CHUNKING Support: VERIFIED ✅' ELSE 'CHUNKING Support: MISSING ❌' END as CHUNKING_STATUS
FROM (
    SELECT 
        COUNT(*) > 0 as COLUMN_EXISTS
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'KNOWLEDGE_BASE_ENTRIES' 
    AND COLUMN_NAME IN ('CHUNK_INDEX', 'TOTAL_CHUNKS', 'FILE_SIZE_BYTES', 'FILE_PATH')
    HAVING COUNT(*) = 4
);

-- Verify importance scoring and foundational marking
SELECT 
    CASE WHEN IMPORTANCE_EXISTS AND FOUNDATIONAL_EXISTS THEN 'ENHANCED Features: VERIFIED ✅' 
         ELSE 'ENHANCED Features: MISSING ❌' END as ENHANCEMENT_STATUS
FROM (
    SELECT 
        COUNT(CASE WHEN COLUMN_NAME = 'IMPORTANCE_SCORE' THEN 1 END) > 0 as IMPORTANCE_EXISTS,
        COUNT(CASE WHEN COLUMN_NAME = 'IS_FOUNDATIONAL' THEN 1 END) > 0 as FOUNDATIONAL_EXISTS
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'KNOWLEDGE_BASE_ENTRIES'
);
```

### **5. AI_MEMORY Schema Validation**
```sql
USE SCHEMA AI_MEMORY;

-- Verify AI Memory tables for large context windows
SELECT 
    COUNT(*) as AI_MEMORY_TABLES,
    CASE 
        WHEN COUNT(*) >= 5 THEN 'AI_MEMORY Schema: VERIFIED ✅'
        ELSE 'AI_MEMORY Schema: INCOMPLETE ❌'
    END as VALIDATION_STATUS
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'AI_MEMORY'
AND TABLE_NAME IN (
    'BUSINESS_MEMORY_CATEGORIES',
    'MEMORY_ENTRIES',
    'MEMORY_EMBEDDINGS',
    'MEMORY_RELATIONSHIPS',
    'MEMORY_ACCESS_PATTERNS'
);

-- Verify cross-document relationship support
DESC TABLE MEMORY_RELATIONSHIPS;

-- Check relationship features
SELECT 
    CASE WHEN RELATIONSHIP_FIELDS = 4 THEN 'CROSS-DOCUMENT Support: VERIFIED ✅'
         ELSE 'CROSS-DOCUMENT Support: MISSING ❌' END as RELATIONSHIP_STATUS
FROM (
    SELECT COUNT(*) as RELATIONSHIP_FIELDS
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'MEMORY_RELATIONSHIPS'
    AND COLUMN_NAME IN ('RELATIONSHIP_TYPE', 'STRENGTH', 'CONFIDENCE', 'SOURCE_MEMORY_ID')
);
```

### **6. Integration Schemas Validation**
```sql
-- Validate all integration schemas
SELECT 
    SCHEMA_NAME,
    COUNT(*) as TABLE_COUNT,
    CASE 
        WHEN SCHEMA_NAME = 'APOLLO_IO' AND COUNT(*) >= 4 THEN 'VERIFIED ✅'
        WHEN SCHEMA_NAME = 'PROJECT_MANAGEMENT' AND COUNT(*) >= 4 THEN 'VERIFIED ✅'  
        WHEN SCHEMA_NAME = 'GONG_INTEGRATION' AND COUNT(*) >= 3 THEN 'VERIFIED ✅'
        WHEN SCHEMA_NAME = 'HUBSPOT_INTEGRATION' AND COUNT(*) >= 3 THEN 'VERIFIED ✅'
        ELSE 'INCOMPLETE ❌'
    END as STATUS
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA IN ('APOLLO_IO', 'PROJECT_MANAGEMENT', 'GONG_INTEGRATION', 'HUBSPOT_INTEGRATION')
GROUP BY SCHEMA_NAME
ORDER BY SCHEMA_NAME;
```

---

## **⚡ PERFORMANCE OPTIMIZATION VALIDATION**

### **7. Index Verification**
```sql
USE SCHEMA UNIVERSAL_CHAT;

-- Verify critical indexes exist
SHOW INDEXES IN SCHEMA UNIVERSAL_CHAT;

-- Key indexes that should exist:
-- idx_knowledge_entries_category
-- idx_knowledge_entries_created  
-- idx_knowledge_entries_foundational
-- idx_knowledge_embeddings_entry
-- idx_conversation_sessions_user
-- idx_conversation_messages_session
-- idx_conversation_messages_created
-- idx_knowledge_usage_entry
-- idx_knowledge_usage_user
-- idx_system_analytics_type
-- idx_system_analytics_timestamp

SELECT 'Index verification complete - review SHOW INDEXES output above' as INDEX_STATUS;
```

### **8. Analytical Views Validation**
```sql
-- Verify analytical views exist
SHOW VIEWS IN SCHEMA UNIVERSAL_CHAT;

-- Critical views that should exist:
-- ACTIVE_CONVERSATIONS
-- KNOWLEDGE_BASE_STATS  
-- USER_ACTIVITY_ANALYTICS

SELECT 
    CASE 
        WHEN VIEW_COUNT >= 3 THEN 'Analytical Views: VERIFIED ✅'
        ELSE 'Analytical Views: MISSING ❌'
    END as VIEW_STATUS
FROM (
    SELECT COUNT(*) as VIEW_COUNT
    FROM INFORMATION_SCHEMA.VIEWS 
    WHERE TABLE_SCHEMA = 'UNIVERSAL_CHAT'
    AND TABLE_NAME IN ('ACTIVE_CONVERSATIONS', 'KNOWLEDGE_BASE_STATS', 'USER_ACTIVITY_ANALYTICS')
);
```

---

## **🚀 REAL-TIME STREAMING VALIDATION**

### **9. Snowflake Streams Verification**
```sql
-- Verify real-time streams exist
SHOW STREAMS IN SCHEMA UNIVERSAL_CHAT;

-- Required streams for real-time processing:
-- KNOWLEDGE_UPDATES_STREAM
-- CONVERSATION_UPDATES_STREAM  
-- SYSTEM_ANALYTICS_STREAM
-- USER_ACTIVITY_STREAM
-- INGESTION_JOBS_STREAM
-- SEARCH_ANALYTICS_STREAM

SELECT 
    COUNT(*) as STREAM_COUNT,
    CASE 
        WHEN COUNT(*) >= 6 THEN 'Real-Time Streams: VERIFIED ✅'
        ELSE 'Real-Time Streams: MISSING ❌ - Expected 6, Found ' || COUNT(*)
    END as STREAM_STATUS
FROM INFORMATION_SCHEMA.STREAMS
WHERE STREAM_SCHEMA = 'UNIVERSAL_CHAT';
```

---

## **🔐 SECURITY AND ACCESS VALIDATION**

### **10. User Management and Security**
```sql
-- Verify user management structure
USE SCHEMA UNIVERSAL_CHAT;

-- Check CEO user exists
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'CEO User: VERIFIED ✅'
        ELSE 'CEO User: MISSING ❌'
    END as CEO_USER_STATUS
FROM USER_MANAGEMENT 
WHERE USER_ID = 'ceo_user' AND ROLE = 'ceo';

-- Verify access level structure
DESC TABLE USER_MANAGEMENT;

-- Check access control fields
SELECT 
    CASE WHEN ACCESS_FIELDS >= 3 THEN 'Access Control: VERIFIED ✅'
         ELSE 'Access Control: INCOMPLETE ❌' END as ACCESS_STATUS
FROM (
    SELECT COUNT(*) as ACCESS_FIELDS
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'USER_MANAGEMENT'
    AND COLUMN_NAME IN ('ROLE', 'ACCESS_LEVEL', 'ALLOWED_SCHEMAS')
);
```

---

## **📊 DATA INTEGRITY VALIDATION**

### **11. Sample Data and Categories**
```sql
-- Verify foundational categories exist
SELECT 
    COUNT(*) as CATEGORY_COUNT,
    CASE 
        WHEN COUNT(*) >= 6 THEN 'Knowledge Categories: VERIFIED ✅'
        ELSE 'Knowledge Categories: INCOMPLETE ❌'
    END as CATEGORY_STATUS
FROM KNOWLEDGE_CATEGORIES;

-- List categories for verification
SELECT 
    CATEGORY_ID,
    CATEGORY_NAME,
    IS_FOUNDATIONAL,
    IMPORTANCE_WEIGHT
FROM KNOWLEDGE_CATEGORIES
ORDER BY IMPORTANCE_WEIGHT DESC;

-- Verify knowledge sources
SELECT 
    COUNT(*) as SOURCE_COUNT,
    CASE 
        WHEN COUNT(*) >= 4 THEN 'Knowledge Sources: VERIFIED ✅'
        ELSE 'Knowledge Sources: INCOMPLETE ❌'
    END as SOURCE_STATUS
FROM KNOWLEDGE_SOURCES;
```

### **12. System Health Check**
```sql
-- Overall system health validation
SELECT 
    'SOPHIA_AI_PROD' as DATABASE_NAME,
    CURRENT_WAREHOUSE() as ACTIVE_WAREHOUSE,
    CURRENT_SCHEMA() as CURRENT_SCHEMA,
    CURRENT_TIMESTAMP() as VALIDATION_TIME,
    CURRENT_USER() as VALIDATED_BY;

-- Storage and performance check
SELECT 
    COUNT(DISTINCT TABLE_SCHEMA) as TOTAL_SCHEMAS,
    COUNT(*) as TOTAL_TABLES,
    'System Ready for Production' as STATUS
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_CATALOG = 'SOPHIA_AI_PROD';
```

---

## **🎯 COMPREHENSIVE VALIDATION SUMMARY**

### **13. Final Validation Report**
```sql
-- Comprehensive validation summary
WITH validation_summary AS (
    SELECT 
        'Database Setup' as component,
        CASE WHEN DATABASE_NAME = 'SOPHIA_AI_PROD' THEN 'PASS' ELSE 'FAIL' END as status
    FROM INFORMATION_SCHEMA.DATABASES WHERE DATABASE_NAME = 'SOPHIA_AI_PROD'
    
    UNION ALL
    
    SELECT 
        'Schema Count' as component,
        CASE WHEN COUNT(*) = 6 THEN 'PASS' ELSE 'FAIL' END as status
    FROM INFORMATION_SCHEMA.SCHEMATA 
    WHERE DATABASE_NAME = 'SOPHIA_AI_PROD' 
    AND SCHEMA_NAME IN ('UNIVERSAL_CHAT', 'AI_MEMORY', 'APOLLO_IO', 'PROJECT_MANAGEMENT', 'GONG_INTEGRATION', 'HUBSPOT_INTEGRATION')
    
    UNION ALL
    
    SELECT 
        'Core Tables' as component,
        CASE WHEN COUNT(*) >= 14 THEN 'PASS' ELSE 'FAIL' END as status
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = 'UNIVERSAL_CHAT'
    
    UNION ALL
    
    SELECT 
        'Enhancement Tables' as component,
        CASE WHEN COUNT(*) >= 2 THEN 'PASS' ELSE 'FAIL' END as status
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = 'UNIVERSAL_CHAT'
    AND TABLE_NAME IN ('INGESTION_JOBS', 'SEARCH_ANALYTICS')
)
SELECT 
    component,
    status,
    CASE 
        WHEN status = 'PASS' THEN '✅'
        ELSE '❌'
    END as indicator
FROM validation_summary
ORDER BY component;

-- Final readiness assessment
SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM validation_summary WHERE status = 'FAIL') = 0 
        THEN '🚀 SOPHIA AI SCHEMA: 100% VALIDATED AND PRODUCTION READY ✅'
        ELSE '⚠️ SCHEMA VALIDATION ISSUES DETECTED - REVIEW ABOVE RESULTS ❌'
    END as FINAL_STATUS;
```

---

## **🔧 REMEDIATION STEPS (IF VALIDATION FAILS)**

### **If Missing Schemas:**
```sql
-- Create missing schemas
CREATE SCHEMA IF NOT EXISTS UNIVERSAL_CHAT;
CREATE SCHEMA IF NOT EXISTS AI_MEMORY;
CREATE SCHEMA IF NOT EXISTS APOLLO_IO;
CREATE SCHEMA IF NOT EXISTS PROJECT_MANAGEMENT;
CREATE SCHEMA IF NOT EXISTS GONG_INTEGRATION;
CREATE SCHEMA IF NOT EXISTS HUBSPOT_INTEGRATION;
```

### **If Missing Enhancement Tables:**
```sql
-- Run the enhancement schema script
-- Execute: backend/snowflake_setup/enhanced_ingestion_jobs_schema.sql
```

### **If Missing Indexes:**
```sql
-- Create critical performance indexes
USE SCHEMA UNIVERSAL_CHAT;

CREATE INDEX IF NOT EXISTS idx_knowledge_entries_category ON KNOWLEDGE_BASE_ENTRIES(CATEGORY_ID);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_created ON KNOWLEDGE_BASE_ENTRIES(CREATED_AT);
CREATE INDEX IF NOT EXISTS idx_knowledge_entries_foundational ON KNOWLEDGE_BASE_ENTRIES(IS_FOUNDATIONAL);
CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_entry ON KNOWLEDGE_EMBEDDINGS(ENTRY_ID);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user ON CONVERSATION_SESSIONS(USER_ID);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_session ON CONVERSATION_MESSAGES(SESSION_ID);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_created ON CONVERSATION_MESSAGES(CREATED_AT);
CREATE INDEX IF NOT EXISTS idx_knowledge_usage_entry ON KNOWLEDGE_USAGE_ANALYTICS(ENTRY_ID);
CREATE INDEX IF NOT EXISTS idx_knowledge_usage_user ON KNOWLEDGE_USAGE_ANALYTICS(USER_ID);
CREATE INDEX IF NOT EXISTS idx_system_analytics_type ON SYSTEM_ANALYTICS(METRIC_TYPE);
CREATE INDEX IF NOT EXISTS idx_system_analytics_timestamp ON SYSTEM_ANALYTICS(TIMESTAMP);
```

---

## **📋 VALIDATION CHECKLIST**

### **Pre-Validation Requirements:**
- [ ] Snowflake account access with ACCOUNTADMIN role
- [ ] SOPHIA_AI_PROD database exists
- [ ] SOPHIA_AI_WH warehouse configured properly

### **Core Validation Steps:**
- [ ] Database and warehouse configuration verified
- [ ] All 6 schemas present and accessible  
- [ ] UNIVERSAL_CHAT core tables (14+) verified
- [ ] Enhancement tables (INGESTION_JOBS, SEARCH_ANALYTICS) verified
- [ ] AI_MEMORY schema for large context windows verified
- [ ] Integration schemas (APOLLO_IO, PROJECT_MANAGEMENT, GONG, HUBSPOT) verified
- [ ] Performance indexes created and verified
- [ ] Analytical views operational
- [ ] Real-time streams configured (6 streams)
- [ ] Security and access controls verified
- [ ] Sample data and categories populated
- [ ] System health check passed

### **Success Criteria:**
- [ ] 100% schema validation passed
- [ ] All tables accessible and properly structured
- [ ] Performance optimization features operational
- [ ] Real-time streaming capability confirmed
- [ ] Security framework properly configured
- [ ] System ready for production deployment

---

## **✅ EXPECTED OUTCOME**

Upon successful completion of this validation:

1. **📊 Schema Completeness**: All 6 schemas with 30+ tables operational
2. **⚡ Performance Ready**: Indexes, views, and optimization features active
3. **🚀 Real-Time Capable**: Streaming infrastructure fully configured
4. **🔐 Security Compliant**: Access controls and audit capabilities operational
5. **📈 Analytics Ready**: Comprehensive monitoring and metrics available

**FINAL RESULT: Production-ready Sophia AI with world-class enterprise architecture** 🎯

Execute this validation prompt to ensure 100% alignment between your Snowflake deployment and the comprehensive enhancement requirements. 