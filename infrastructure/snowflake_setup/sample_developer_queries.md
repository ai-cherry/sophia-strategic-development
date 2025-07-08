# Sophia AI Snowflake Developer Queries Guide

This guide provides sample SQL queries for developers working with the Sophia AI Snowflake setup. These queries demonstrate how to interact with the new schemas, perform vector searches, and leverage Snowflake Cortex AI capabilities.

## Table of Contents
1. [Basic Data Exploration](#basic-data-exploration)
2. [HubSpot Data Queries](#hubspot-data-queries)
3. [Gong Call Analysis](#gong-call-analysis)
4. [Vector Search and AI Memory](#vector-search-and-ai-memory)
5. [Snowflake Cortex AI Functions](#snowflake-cortex-ai-functions)
6. [Configuration Management](#configuration-management)
7. [Monitoring and Operations](#monitoring-and-operations)
8. [Advanced Analytics](#advanced-analytics)

## Prerequisites

Before running these queries, ensure you have:
- Access to the `SOPHIA_AI_DEV` database
- Appropriate role permissions (`ROLE_SOPHIA_DEVELOPER` or `ROLE_SOPHIA_AI_AGENT_SERVICE`)
- Understanding of the schema structure

```sql
-- Set context
USE DATABASE SOPHIA_AI_DEV;
USE WAREHOUSE WH_SOPHIA_AGENT_QUERY;
```

## Basic Data Exploration

### Explore Available Schemas and Tables

```sql
-- List all schemas in the database
SHOW SCHEMAS;

-- List tables in each schema
SHOW TABLES IN SCHEMA STG_ESTUARY;
SHOW TABLES IN SCHEMA AI_MEMORY;
SHOW TABLES IN SCHEMA OPS_MONITORING;
SHOW TABLES IN SCHEMA CONFIG;

-- Get table details with column information
DESCRIBE TABLE STG_ESTUARY.STG_GONG_CALLS;
DESCRIBE TABLE STG_ESTUARY.STG_HUBSPOT_DEALS;
```

### Check Data Availability

```sql
-- Check record counts across key tables
SELECT
    'STG_GONG_CALLS' as table_name,
    COUNT(*) as record_count,
    MIN(CREATED_AT) as earliest_record,
    MAX(UPDATED_AT) as latest_update
FROM STG_ESTUARY.STG_GONG_CALLS

UNION ALL

SELECT
    'STG_HUBSPOT_DEALS' as table_name,
    COUNT(*) as record_count,
    MIN(CREATED_AT) as earliest_record,
    MAX(LAST_REFRESHED) as latest_update
FROM STG_ESTUARY.STG_HUBSPOT_DEALS

UNION ALL

SELECT
    'STG_GONG_CALL_TRANSCRIPTS' as table_name,
    COUNT(*) as record_count,
    MIN(CREATED_AT) as earliest_record,
    MAX(CREATED_AT) as latest_update
FROM STG_ESTUARY.STG_GONG_CALL_TRANSCRIPTS;
```

## HubSpot Data Queries

### Basic Deal Analysis

```sql
-- Get recent deals with key metrics
SELECT
    DEAL_ID,
    DEAL_NAME,
    DEAL_STAGE,
    DEAL_AMOUNT,
    CLOSE_DATE,
    DEAL_OWNER,
    DAYS_TO_CLOSE,
    DEAL_STATUS,
    LAST_REFRESHED
FROM STG_ESTUARY.STG_HUBSPOT_DEALS
WHERE LAST_REFRESHED >= DATEADD('day', -7, CURRENT_DATE())
ORDER BY DEAL_AMOUNT DESC
LIMIT 20;
```

### Deal Pipeline Analysis

```sql
-- Analyze deals by stage and pipeline
SELECT
    PIPELINE_NAME,
    DEAL_STAGE,
    COUNT(*) as deal_count,
    SUM(DEAL_AMOUNT) as total_value,
    AVG(DEAL_AMOUNT) as avg_deal_size,
    AVG(DAYS_TO_CLOSE) as avg_days_to_close
FROM STG_ESTUARY.STG_HUBSPOT_DEALS
WHERE DEAL_STATUS = 'In Progress'
GROUP BY PIPELINE_NAME, DEAL_STAGE
ORDER BY PIPELINE_NAME, total_value DESC;
```

### High-Value Deal Analysis

```sql
-- Identify high-value deals with AI Memory data
SELECT
    hd.DEAL_ID,
    hd.DEAL_NAME,
    hd.DEAL_STAGE,
    hd.DEAL_AMOUNT,
    hd.CLOSE_DATE,
    hd.DEAL_OWNER,
    CASE
        WHEN hd.AI_MEMORY_EMBEDDING IS NOT NULL THEN 'Has AI Insights'
        ELSE 'No AI Insights'
    END as ai_analysis_status,
    hd.AI_MEMORY_UPDATED_AT,
    -- Extract key insights from metadata
    hd.AI_MEMORY_METADATA:importance_score::FLOAT as importance_score
FROM STG_ESTUARY.STG_HUBSPOT_DEALS hd
WHERE hd.DEAL_AMOUNT > 50000
AND hd.DEAL_STATUS IN ('In Progress', 'Closing Soon')
ORDER BY hd.DEAL_AMOUNT DESC;
```

## Gong Call Analysis

### Recent Call Activity

```sql
-- Get recent calls with sentiment analysis
SELECT
    CALL_ID,
    CALL_TITLE,
    CALL_DATETIME_UTC,
    PRIMARY_USER_NAME,
    CALL_DURATION_SECONDS / 60 as duration_minutes,
    SENTIMENT_SCORE,
    CASE
        WHEN SENTIMENT_SCORE > 0.5 THEN 'Very Positive'
        WHEN SENTIMENT_SCORE > 0.2 THEN 'Positive'
        WHEN SENTIMENT_SCORE > -0.2 THEN 'Neutral'
        WHEN SENTIMENT_SCORE > -0.5 THEN 'Negative'
        ELSE 'Very Negative'
    END as sentiment_category,
    TALK_RATIO,
    HUBSPOT_DEAL_ID,
    ACCOUNT_NAME
FROM STG_ESTUARY.STG_GONG_CALLS
WHERE CALL_DATETIME_UTC >= DATEADD('day', -30, CURRENT_DATE())
AND SENTIMENT_SCORE IS NOT NULL
ORDER BY CALL_DATETIME_UTC DESC
LIMIT 50;
```

### Call Performance by Sales Rep

```sql
-- Analyze call performance metrics by sales representative
SELECT
    PRIMARY_USER_NAME as sales_rep,
    COUNT(*) as total_calls,
    AVG(SENTIMENT_SCORE) as avg_sentiment,
    AVG(TALK_RATIO) as avg_talk_ratio,
    AVG(CALL_DURATION_SECONDS / 60) as avg_duration_minutes,
    COUNT(DISTINCT HUBSPOT_DEAL_ID) as unique_deals_discussed,
    -- Performance assessment
    CASE
        WHEN AVG(SENTIMENT_SCORE) > 0.3 AND AVG(TALK_RATIO) BETWEEN 0.3 AND 0.6 THEN 'High Performer'
        WHEN AVG(SENTIMENT_SCORE) > 0.1 AND AVG(TALK_RATIO) BETWEEN 0.2 AND 0.7 THEN 'Good Performer'
        ELSE 'Needs Coaching'
    END as performance_category
FROM STG_ESTUARY.STG_GONG_CALLS
WHERE CALL_DATETIME_UTC >= DATEADD('day', -90, CURRENT_DATE())
AND PRIMARY_USER_NAME IS NOT NULL
GROUP BY PRIMARY_USER_NAME
HAVING COUNT(*) >= 5  -- Only reps with at least 5 calls
ORDER BY avg_sentiment DESC, total_calls DESC;
```

### Call Transcript Analysis

```sql
-- Analyze call transcripts with AI processing status
SELECT
    t.CALL_ID,
    c.CALL_TITLE,
    c.ACCOUNT_NAME,
    COUNT(t.TRANSCRIPT_ID) as transcript_segments,
    AVG(t.SEGMENT_SENTIMENT) as avg_transcript_sentiment,
    SUM(t.WORD_COUNT) as total_words,
    COUNT(CASE WHEN t.AI_MEMORY_EMBEDDING IS NOT NULL THEN 1 END) as segments_with_embeddings,
    -- AI processing status
    CASE
        WHEN COUNT(CASE WHEN t.AI_MEMORY_EMBEDDING IS NOT NULL THEN 1 END) = COUNT(t.TRANSCRIPT_ID)
        THEN 'Fully Processed'
        WHEN COUNT(CASE WHEN t.AI_MEMORY_EMBEDDING IS NOT NULL THEN 1 END) > 0
        THEN 'Partially Processed'
        ELSE 'Not Processed'
    END as ai_processing_status
FROM STG_ESTUARY.STG_GONG_CALL_TRANSCRIPTS t
JOIN STG_ESTUARY.STG_GONG_CALLS c ON t.CALL_ID = c.CALL_ID
WHERE c.CALL_DATETIME_UTC >= DATEADD('day', -7, CURRENT_DATE())
GROUP BY t.CALL_ID, c.CALL_TITLE, c.ACCOUNT_NAME
ORDER BY total_words DESC;
```

## Vector Search and AI Memory

### Semantic Search for Similar Deals

```sql
-- Find deals similar to a specific deal using vector embeddings
WITH target_deal AS (
    SELECT AI_MEMORY_EMBEDDING as target_embedding
    FROM STG_ESTUARY.STG_HUBSPOT_DEALS
    WHERE DEAL_ID = 'your_deal_id_here'
    AND AI_MEMORY_EMBEDDING IS NOT NULL
)
SELECT
    hd.DEAL_ID,
    hd.DEAL_NAME,
    hd.DEAL_STAGE,
    hd.DEAL_AMOUNT,
    hd.COMPANY_NAME,
    VECTOR_COSINE_SIMILARITY(td.target_embedding, hd.AI_MEMORY_EMBEDDING) as similarity_score
FROM STG_ESTUARY.STG_HUBSPOT_DEALS hd
CROSS JOIN target_deal td
WHERE hd.AI_MEMORY_EMBEDDING IS NOT NULL
AND hd.DEAL_ID != 'your_deal_id_here'
AND VECTOR_COSINE_SIMILARITY(td.target_embedding, hd.AI_MEMORY_EMBEDDING) > 0.7
ORDER BY similarity_score DESC
LIMIT 10;
```

### Find Similar Call Transcripts

```sql
-- Search for call transcripts similar to a query using embeddings
WITH query_embedding AS (
    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 'pricing objection budget concerns') as query_vector
)
SELECT
    t.CALL_ID,
    c.CALL_TITLE,
    c.ACCOUNT_NAME,
    t.SPEAKER_NAME,
    t.TRANSCRIPT_TEXT,
    t.SEGMENT_SENTIMENT,
    VECTOR_COSINE_SIMILARITY(q.query_vector, t.AI_MEMORY_EMBEDDING) as similarity_score
FROM STG_ESTUARY.STG_GONG_CALL_TRANSCRIPTS t
JOIN STG_ESTUARY.STG_GONG_CALLS c ON t.CALL_ID = c.CALL_ID
CROSS JOIN query_embedding q
WHERE t.AI_MEMORY_EMBEDDING IS NOT NULL
AND VECTOR_COSINE_SIMILARITY(q.query_vector, t.AI_MEMORY_EMBEDDING) > 0.7
ORDER BY similarity_score DESC
LIMIT 20;
```

### AI Memory Usage Analysis

```sql
-- Analyze AI Memory usage patterns
SELECT
    CATEGORY,
    COUNT(*) as memory_count,
    AVG(IMPORTANCE_SCORE) as avg_importance,
    AVG(ACCESS_COUNT) as avg_access_count,
    MAX(LAST_ACCESSED_AT) as last_accessed,
    COUNT(CASE WHEN AUTO_DETECTED = TRUE THEN 1 END) as auto_detected_count
FROM AI_MEMORY.MEMORY_RECORDS
WHERE CREATED_AT >= DATEADD('day', -30, CURRENT_DATE())
GROUP BY CATEGORY
ORDER BY memory_count DESC;
```

## Snowflake Cortex AI Functions

### Generate Embeddings for New Data

```sql
-- Generate embeddings for deals without them
SELECT
    DEAL_ID,
    DEAL_NAME,
    SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2',
        DEAL_NAME || ' - ' || COALESCE(DEAL_STAGE, '') || ' - ' || COALESCE(PIPELINE_NAME, '')
    ) as generated_embedding
FROM STG_ESTUARY.STG_HUBSPOT_DEALS
WHERE AI_MEMORY_EMBEDDING IS NULL
AND DEAL_NAME IS NOT NULL
LIMIT 10;
```

### Sentiment Analysis on Call Data

```sql
-- Analyze sentiment for calls without sentiment scores
SELECT
    CALL_ID,
    CALL_TITLE,
    ACCOUNT_NAME,
    SNOWFLAKE.CORTEX.SENTIMENT(
        CALL_TITLE || ' ' || COALESCE(ACCOUNT_NAME, '') || ' ' || COALESCE(DEAL_STAGE, '')
    ) as calculated_sentiment,
    SNOWFLAKE.CORTEX.SUMMARIZE(
        'Call with ' || COALESCE(ACCOUNT_NAME, 'Unknown') ||
        ' about ' || COALESCE(CALL_TITLE, 'business discussion') ||
        '. Deal stage: ' || COALESCE(DEAL_STAGE, 'Unknown'),
        100
    ) as call_summary
FROM STG_ESTUARY.STG_GONG_CALLS
WHERE SENTIMENT_SCORE IS NULL
AND CALL_TITLE IS NOT NULL
LIMIT 5;
```

### Text Completion for Analysis

```sql
-- Use Cortex for deal risk analysis
SELECT
    DEAL_ID,
    DEAL_NAME,
    DEAL_STAGE,
    DEAL_AMOUNT,
    DAYS_TO_CLOSE,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama2-70b-chat',
        'Analyze the risk level of this deal: ' ||
        'Deal: ' || DEAL_NAME ||
        ', Stage: ' || DEAL_STAGE ||
        ', Value: $' || DEAL_AMOUNT ||
        ', Days to close: ' || DAYS_TO_CLOSE ||
        '. Provide a brief risk assessment and recommendations.',
        {'max_tokens': 200}
    ) as risk_analysis
FROM STG_ESTUARY.STG_HUBSPOT_DEALS
WHERE DEAL_STATUS = 'In Progress'
AND DEAL_AMOUNT > 25000
LIMIT 3;
```

## Configuration Management

### Query Configuration Settings

```sql
-- Get all configuration settings for the application
SELECT
    SETTING_NAME,
    SETTING_VALUE,
    DATA_TYPE,
    CATEGORY,
    DESCRIPTION,
    ENVIRONMENT,
    APPLICATION_NAME,
    UPDATED_AT
FROM CONFIG.APPLICATION_SETTINGS
WHERE ENVIRONMENT = 'DEV'
AND APPLICATION_NAME = 'SOPHIA_AI'
ORDER BY CATEGORY, SETTING_NAME;
```

### Check Feature Flag Status

```sql
-- Check status of feature flags
SELECT
    FLAG_NAME,
    IS_ENABLED,
    FLAG_TYPE,
    ROLLOUT_PERCENTAGE,
    ENVIRONMENT,
    START_DATE,
    END_DATE,
    USAGE_COUNT
FROM CONFIG.FEATURE_FLAGS
WHERE ENVIRONMENT = 'DEV'
AND APPLICATION_NAME = 'SOPHIA_AI'
ORDER BY FLAG_NAME;
```

### Configuration Usage Examples

```sql
-- Use configuration functions
SELECT CONFIG.GET_CONFIG_VALUE('ai_memory.similarity_threshold', 'DEV', 'SOPHIA_AI') as similarity_threshold;
SELECT CONFIG.EVALUATE_FEATURE_FLAG('enhanced_ai_memory', 'user_123', 'DEV', 'SOPHIA_AI') as flag_enabled;
```

## Monitoring and Operations

### ETL Job Performance

```sql
-- Monitor ETL job performance
SELECT
    JOB_NAME,
    JOB_TYPE,
    STATUS,
    AVG(DURATION_SECONDS) as avg_duration_seconds,
    COUNT(*) as total_runs,
    SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) as successful_runs,
    SUM(CASE WHEN STATUS = 'FAILED' THEN 1 ELSE 0 END) as failed_runs,
    MAX(START_TIME) as last_run_time,
    AVG(ROWS_PROCESSED) as avg_rows_processed
FROM OPS_MONITORING.ETL_JOB_LOGS
WHERE START_TIME >= DATEADD('day', -7, CURRENT_DATE())
GROUP BY JOB_NAME, JOB_TYPE, STATUS
ORDER BY JOB_NAME, STATUS;
```

### Application Error Analysis

```sql
-- Analyze application errors
SELECT
    APPLICATION_NAME,
    SERVICE_NAME,
    ERROR_LEVEL,
    COUNT(*) as error_count,
    COUNT(DISTINCT ERROR_TYPE) as unique_error_types,
    MAX(OCCURRED_AT) as last_occurrence,
    -- Most common error messages
    MODE(ERROR_MESSAGE) as most_common_error
FROM OPS_MONITORING.APP_ERROR_LOGS
WHERE OCCURRED_AT >= DATEADD('day', -7, CURRENT_DATE())
GROUP BY APPLICATION_NAME, SERVICE_NAME, ERROR_LEVEL
ORDER BY error_count DESC;
```

### System Health Overview

```sql
-- System health check summary
SELECT
    APPLICATION_NAME,
    SERVICE_NAME,
    CHECK_TYPE,
    STATUS,
    AVG(RESPONSE_TIME_MS) as avg_response_time,
    MAX(LAST_CHECK_AT) as last_check,
    CONSECUTIVE_FAILURES
FROM OPS_MONITORING.SYSTEM_HEALTH_CHECKS
WHERE IS_ACTIVE = TRUE
GROUP BY APPLICATION_NAME, SERVICE_NAME, CHECK_TYPE, STATUS, CONSECUTIVE_FAILURES
ORDER BY APPLICATION_NAME, SERVICE_NAME;
```

## Advanced Analytics

### Deal and Call Correlation Analysis

```sql
-- Analyze correlation between call activity and deal success
WITH deal_call_summary AS (
    SELECT
        hd.DEAL_ID,
        hd.DEAL_NAME,
        hd.DEAL_STAGE,
        hd.DEAL_AMOUNT,
        hd.DEAL_STATUS,
        COUNT(gc.CALL_ID) as call_count,
        AVG(gc.SENTIMENT_SCORE) as avg_call_sentiment,
        AVG(gc.TALK_RATIO) as avg_talk_ratio,
        SUM(gc.CALL_DURATION_SECONDS) / 3600 as total_call_hours
    FROM STG_ESTUARY.STG_HUBSPOT_DEALS hd
    LEFT JOIN STG_ESTUARY.STG_GONG_CALLS gc ON hd.DEAL_ID = gc.HUBSPOT_DEAL_ID
    WHERE hd.DEAL_STATUS IN ('Won', 'Lost', 'In Progress')
    GROUP BY hd.DEAL_ID, hd.DEAL_NAME, hd.DEAL_STAGE, hd.DEAL_AMOUNT, hd.DEAL_STATUS
)
SELECT
    DEAL_STATUS,
    COUNT(*) as deal_count,
    AVG(call_count) as avg_calls_per_deal,
    AVG(avg_call_sentiment) as avg_sentiment,
    AVG(avg_talk_ratio) as avg_talk_ratio,
    AVG(total_call_hours) as avg_total_call_hours,
    AVG(DEAL_AMOUNT) as avg_deal_value
FROM deal_call_summary
GROUP BY DEAL_STATUS
ORDER BY
    CASE DEAL_STATUS
        WHEN 'Won' THEN 1
        WHEN 'In Progress' THEN 2
        WHEN 'Lost' THEN 3
    END;
```

### AI Memory Effectiveness Analysis

```sql
-- Analyze AI Memory effectiveness and usage patterns
WITH memory_effectiveness AS (
    SELECT
        mr.CATEGORY,
        mr.BUSINESS_TABLE_NAME,
        COUNT(*) as total_memories,
        AVG(mr.IMPORTANCE_SCORE) as avg_importance,
        AVG(mr.ACCESS_COUNT) as avg_access_count,
        -- Calculate recency score
        AVG(DATEDIFF('day', mr.CREATED_AT, CURRENT_DATE())) as avg_age_days,
        COUNT(CASE WHEN mr.LAST_ACCESSED_AT >= DATEADD('day', -30, CURRENT_DATE()) THEN 1 END) as recently_accessed
    FROM AI_MEMORY.MEMORY_RECORDS mr
    GROUP BY mr.CATEGORY, mr.BUSINESS_TABLE_NAME
)
SELECT
    CATEGORY,
    BUSINESS_TABLE_NAME,
    total_memories,
    avg_importance,
    avg_access_count,
    avg_age_days,
    recently_accessed,
    recently_accessed / total_memories as recent_access_rate,
    -- Effectiveness score
    (avg_importance * 0.4 +
     LEAST(avg_access_count / 10, 1) * 0.3 +
     recently_accessed / total_memories * 0.3) as effectiveness_score
FROM memory_effectiveness
ORDER BY effectiveness_score DESC;
```

### Conversation Intelligence Insights

```sql
-- Generate conversation intelligence insights
WITH conversation_analysis AS (
    SELECT
        DATE_TRUNC('week', ch.STARTED_AT) as week_start,
        ch.CONVERSATION_TYPE,
        ch.AGENT_TYPE,
        COUNT(*) as conversation_count,
        AVG(ch.RESPONSE_TIME_MS) as avg_response_time,
        AVG(ch.MEMORY_EFFECTIVENESS_SCORE) as avg_memory_effectiveness,
        AVG(ch.USER_SATISFACTION_SCORE) as avg_user_satisfaction,
        COUNT(DISTINCT ch.USER_ID) as unique_users
    FROM AI_MEMORY.CONVERSATION_HISTORY ch
    WHERE ch.STARTED_AT >= DATEADD('week', -8, CURRENT_DATE())
    GROUP BY DATE_TRUNC('week', ch.STARTED_AT), ch.CONVERSATION_TYPE, ch.AGENT_TYPE
)
SELECT
    week_start,
    conversation_type,
    agent_type,
    conversation_count,
    avg_response_time,
    avg_memory_effectiveness,
    avg_user_satisfaction,
    unique_users,
    -- Trend analysis
    LAG(conversation_count) OVER (
        PARTITION BY conversation_type, agent_type
        ORDER BY week_start
    ) as prev_week_conversations,
    conversation_count - LAG(conversation_count) OVER (
        PARTITION BY conversation_type, agent_type
        ORDER BY week_start
    ) as conversation_growth
FROM conversation_analysis
ORDER BY week_start DESC, conversation_count DESC;
```

## Performance Optimization Tips

### Index Usage Verification

```sql
-- Check if indexes are being used efficiently
SELECT
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    INDEX_TYPE
FROM INFORMATION_SCHEMA.INDEXES
WHERE TABLE_SCHEMA = 'STG_ESTUARY'
ORDER BY TABLE_NAME, INDEX_NAME;
```

### Query Performance Analysis

```sql
-- Analyze query performance for large tables
SELECT
    TABLE_NAME,
    ROW_COUNT,
    BYTES,
    CLUSTERING_KEY,
    AUTOMATIC_CLUSTERING
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('STG_ESTUARY', 'AI_MEMORY')
AND TABLE_TYPE = 'BASE TABLE'
ORDER BY BYTES DESC;
```

## Best Practices for Developers

1. **Always use appropriate roles**: Use `ROLE_SOPHIA_DEVELOPER` for development queries
2. **Leverage vector search**: Use `VECTOR_COSINE_SIMILARITY` for semantic searches
3. **Use configuration functions**: Leverage `CONFIG.GET_CONFIG_VALUE()` for settings
4. **Monitor performance**: Check query execution time and optimize accordingly
5. **Handle nulls**: Always check for NULL values in AI Memory columns
6. **Use appropriate warehouses**: Use `WH_SOPHIA_AGENT_QUERY` for queries, `WH_SOPHIA_AI_PROCESSING` for heavy processing

## Troubleshooting Common Issues

### Missing Embeddings

```sql
-- Find records without embeddings that should have them
SELECT
    'STG_HUBSPOT_DEALS' as table_name,
    COUNT(*) as records_without_embeddings
FROM STG_ESTUARY.STG_HUBSPOT_DEALS
WHERE AI_MEMORY_EMBEDDING IS NULL
AND DEAL_NAME IS NOT NULL

UNION ALL

SELECT
    'STG_GONG_CALL_TRANSCRIPTS' as table_name,
    COUNT(*) as records_without_embeddings
FROM STG_ESTUARY.STG_GONG_CALL_TRANSCRIPTS
WHERE AI_MEMORY_EMBEDDING IS NULL
AND TRANSCRIPT_TEXT IS NOT NULL
AND LENGTH(TRANSCRIPT_TEXT) > 10;
```

### Configuration Issues

```sql
-- Check for missing or invalid configuration
SELECT
    SETTING_NAME,
    SETTING_VALUE,
    DATA_TYPE,
    VALIDATION_RULE
FROM CONFIG.APPLICATION_SETTINGS
WHERE IS_ACTIVE = TRUE
AND (
    SETTING_VALUE IS NULL
    OR (DATA_TYPE = 'NUMBER' AND TRY_TO_NUMBER(SETTING_VALUE) IS NULL)
    OR (DATA_TYPE = 'BOOLEAN' AND SETTING_VALUE NOT IN ('true', 'false'))
);
```

# Enhanced Gong Data Queries with AI Memory Integration

## 🔍 **Semantic Search Queries**

### **Basic Gong Call Search**
```sql
-- Find calls about pricing discussions using vector similarity
WITH query_embedding AS (
    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 'pricing discussion negotiation cost') as embedding
)
SELECT
    gc.CALL_ID,
    gc.CALL_TITLE,
    gc.ACCOUNT_NAME,
    gc.CALL_SUMMARY,
    gc.SENTIMENT_SCORE,
    VECTOR_COSINE_SIMILARITY(gc.AI_MEMORY_EMBEDDING, qe.embedding) as SIMILARITY_SCORE
FROM STG_ESTUARY.STG_GONG_CALLS gc
CROSS JOIN query_embedding qe
WHERE gc.AI_MEMORY_EMBEDDING IS NOT NULL
AND VECTOR_COSINE_SIMILARITY(gc.AI_MEMORY_EMBEDDING, qe.embedding) >= 0.7
ORDER BY SIMILARITY_SCORE DESC
LIMIT 10;
```

### **Advanced Transcript Search with Speaker Analysis**
```sql
-- Search transcript segments for competitive mentions
WITH query_embedding AS (
    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 'competitor salesforce hubspot alternative') as embedding
)
SELECT
    gt.TRANSCRIPT_ID,
    gt.CALL_ID,
    gt.SPEAKER_NAME,
    gt.SPEAKER_TYPE,
    gt.TRANSCRIPT_TEXT,
    gt.SEGMENT_SENTIMENT,
    gc.ACCOUNT_NAME,
    gc.DEAL_STAGE,
    VECTOR_COSINE_SIMILARITY(gt.AI_MEMORY_EMBEDDING, qe.embedding) as SIMILARITY_SCORE
FROM STG_ESTUARY.STG_GONG_CALL_TRANSCRIPTS gt
CROSS JOIN query_embedding qe
JOIN STG_ESTUARY.STG_GONG_CALLS gc ON gt.CALL_ID = gc.CALL_ID
WHERE gt.AI_MEMORY_EMBEDDING IS NOT NULL
AND VECTOR_COSINE_SIMILARITY(gt.AI_MEMORY_EMBEDDING, qe.embedding) >= 0.75
AND gt.SPEAKER_TYPE = 'External'  -- Customer mentions
ORDER BY SIMILARITY_SCORE DESC
LIMIT 15;
```

## 📊 **AI-Enhanced Analytics Queries**

### **Sentiment Analysis with Account Insights**
```sql
-- Comprehensive sentiment analysis by account with AI insights
SELECT
    gc.ACCOUNT_NAME,
    COUNT(*) as total_calls,
    AVG(gc.SENTIMENT_SCORE) as avg_sentiment,
    COUNT(CASE WHEN gc.SENTIMENT_SCORE > 0.3 THEN 1 END) as positive_calls,
    COUNT(CASE WHEN gc.SENTIMENT_SCORE < -0.3 THEN 1 END) as negative_calls,
    AVG(gc.TALK_RATIO) as avg_talk_ratio,

    -- AI-generated insights
    LISTAGG(DISTINCT gc.KEY_TOPICS, ', ') as common_topics,
    LISTAGG(DISTINCT gc.RISK_INDICATORS, ', ') as identified_risks,

    -- Deal context
    gc.DEAL_STAGE,
    MAX(gc.CALL_DATETIME_UTC) as latest_call,

    -- Account health score (custom calculation)
    CASE
        WHEN AVG(gc.SENTIMENT_SCORE) > 0.5 AND COUNT(*) > 3 THEN 'Excellent'
        WHEN AVG(gc.SENTIMENT_SCORE) > 0.2 AND COUNT(*) > 1 THEN 'Good'
        WHEN AVG(gc.SENTIMENT_SCORE) > -0.2 THEN 'Fair'
        ELSE 'At Risk'
    END as account_health

FROM STG_ESTUARY.STG_GONG_CALLS gc
WHERE gc.CALL_DATETIME_UTC >= DATEADD(month, -3, CURRENT_TIMESTAMP())
AND gc.ACCOUNT_NAME IS NOT NULL
GROUP BY gc.ACCOUNT_NAME, gc.DEAL_STAGE
HAVING COUNT(*) >= 2  -- Accounts with multiple interactions
ORDER BY avg_sentiment DESC, total_calls DESC;
```

### **Topic Analysis with AI Memory Cross-Reference**
```sql
-- Analyze discussion topics and cross-reference with AI Memory
WITH topic_analysis AS (
    SELECT
        gc.CALL_ID,
        gc.ACCOUNT_NAME,
        gc.PRIMARY_USER_NAME,
        gc.SENTIMENT_SCORE,
        topic.value::STRING as topic,
        gc.AI_MEMORY_METADATA:embedding_generated_at::TIMESTAMP_NTZ as ai_processed_at
    FROM STG_ESTUARY.STG_GONG_CALLS gc,
    LATERAL FLATTEN(input => gc.KEY_TOPICS) AS topic
    WHERE gc.KEY_TOPICS IS NOT NULL
    AND gc.CALL_DATETIME_UTC >= DATEADD(day, -30, CURRENT_TIMESTAMP())
),
memory_insights AS (
    SELECT
        mr.SOURCE_ID as call_id,
        mr.CATEGORY,
        mr.RELEVANCE_SCORE,
        mr.ACCESS_COUNT,
        mr.METADATA:key_topics as memory_topics
    FROM AI_MEMORY.MEMORY_RECORDS mr
    WHERE mr.SOURCE_TYPE = 'gong'
    AND mr.CATEGORY = 'gong_call_insight'
)
SELECT
    ta.topic,
    COUNT(*) as mention_frequency,
    AVG(ta.sentiment_score) as avg_sentiment_for_topic,
    COUNT(DISTINCT ta.account_name) as unique_accounts,
    COUNT(DISTINCT ta.primary_user_name) as unique_reps,

    -- AI Memory insights
    AVG(mi.relevance_score) as avg_memory_relevance,
    AVG(mi.access_count) as avg_memory_access,

    -- Top accounts discussing this topic
    LISTAGG(DISTINCT
        CASE WHEN ta.sentiment_score > 0.3
        THEN ta.account_name || ' (Positive)'
        ELSE ta.account_name
        END, ', '
    ) WITHIN GROUP (ORDER BY ta.sentiment_score DESC) as top_accounts

FROM topic_analysis ta
LEFT JOIN memory_insights mi ON ta.call_id = mi.call_id
GROUP BY ta.topic
HAVING COUNT(*) >= 3  -- Topics mentioned in multiple calls
ORDER BY mention_frequency DESC, avg_sentiment_for_topic DESC
LIMIT 20;
```

## 🎯 **Deal Risk Assessment Queries**

### **AI-Powered Deal Risk Analysis**
```sql
-- Comprehensive deal risk assessment using AI insights
WITH deal_risk_analysis AS (
    SELECT
        gc.HUBSPOT_DEAL_ID,
        gc.ACCOUNT_NAME,
        gc.DEAL_STAGE,
        gc.DEAL_VALUE,

        -- Call metrics
        COUNT(*) as total_calls,
        AVG(gc.SENTIMENT_SCORE) as avg_sentiment,
        AVG(gc.TALK_RATIO) as avg_talk_ratio,
        MAX(gc.CALL_DATETIME_UTC) as last_call_date,
        DATEDIFF('day', MAX(gc.CALL_DATETIME_UTC), CURRENT_TIMESTAMP()) as days_since_last_call,

        -- Risk indicators from AI analysis
        LISTAGG(DISTINCT ri.value::STRING, '; ') as all_risk_indicators,
        COUNT(DISTINCT ri.value::STRING) as unique_risk_count,

        -- Next steps tracking
        LISTAGG(DISTINCT ns.value::STRING, '; ') as all_next_steps,

        -- AI Memory integration
        MAX(gc.AI_MEMORY_UPDATED_AT) as latest_ai_analysis

    FROM STG_ESTUARY.STG_GONG_CALLS gc
    LEFT JOIN LATERAL FLATTEN(input => gc.RISK_INDICATORS) AS ri ON TRUE
    LEFT JOIN LATERAL FLATTEN(input => gc.NEXT_STEPS) AS ns ON TRUE
    WHERE gc.HUBSPOT_DEAL_ID IS NOT NULL
    AND gc.DEAL_STAGE NOT IN ('Closed Won', 'Closed Lost')
    GROUP BY gc.HUBSPOT_DEAL_ID, gc.ACCOUNT_NAME, gc.DEAL_STAGE, gc.DEAL_VALUE
)
SELECT
    *,
    -- Calculated risk score (0-100, higher = more risk)
    CASE
        WHEN days_since_last_call > 14 THEN 25 ELSE 0 END +
    CASE
        WHEN avg_sentiment < -0.3 THEN 30
        WHEN avg_sentiment < 0 THEN 15
        ELSE 0
    END +
    CASE
        WHEN unique_risk_count > 2 THEN 25
        WHEN unique_risk_count > 0 THEN 10
        ELSE 0
    END +
    CASE
        WHEN avg_talk_ratio > 0.8 THEN 10  -- Rep talking too much
        WHEN avg_talk_ratio < 0.3 THEN 15  -- Customer not engaged
        ELSE 0
    END as calculated_risk_score,

    -- Risk category
    CASE
        WHEN (
            CASE WHEN days_since_last_call > 14 THEN 25 ELSE 0 END +
            CASE WHEN avg_sentiment < -0.3 THEN 30 WHEN avg_sentiment < 0 THEN 15 ELSE 0 END +
            CASE WHEN unique_risk_count > 2 THEN 25 WHEN unique_risk_count > 0 THEN 10 ELSE 0 END +
            CASE WHEN avg_talk_ratio > 0.8 THEN 10 WHEN avg_talk_ratio < 0.3 THEN 15 ELSE 0 END
        ) >= 50 THEN 'High Risk'
        WHEN (
            CASE WHEN days_since_last_call > 14 THEN 25 ELSE 0 END +
            CASE WHEN avg_sentiment < -0.3 THEN 30 WHEN avg_sentiment < 0 THEN 15 ELSE 0 END +
            CASE WHEN unique_risk_count > 2 THEN 25 WHEN unique_risk_count > 0 THEN 10 ELSE 0 END +
            CASE WHEN avg_talk_ratio > 0.8 THEN 10 WHEN avg_talk_ratio < 0.3 THEN 15 ELSE 0 END
        ) >= 25 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_category

FROM deal_risk_analysis
ORDER BY calculated_risk_score DESC, deal_value DESC;
```

## 🏆 **Sales Performance & Coaching Queries**

### **Rep Performance with AI Coaching Insights**
```sql
-- Sales rep performance analysis with AI-generated coaching recommendations
WITH rep_performance AS (
    SELECT
        gc.PRIMARY_USER_NAME as sales_rep,
        gc.PRIMARY_USER_EMAIL,

        -- Call metrics
        COUNT(*) as total_calls,
        AVG(gc.CALL_DURATION_SECONDS) / 60 as avg_call_duration_minutes,
        AVG(gc.SENTIMENT_SCORE) as avg_sentiment,
        AVG(gc.TALK_RATIO) as avg_talk_ratio,
        AVG(gc.INTERACTIVITY_SCORE) as avg_interactivity,
        AVG(gc.QUESTIONS_ASKED_COUNT) as avg_questions_asked,

        -- Deal outcomes
        COUNT(DISTINCT gc.HUBSPOT_DEAL_ID) as unique_deals_touched,
        COUNT(DISTINCT gc.ACCOUNT_NAME) as unique_accounts,
        SUM(CASE WHEN gc.DEAL_STAGE IN ('Closed Won') THEN gc.DEAL_VALUE ELSE 0 END) as won_deal_value,

        -- AI insights
        COUNT(CASE WHEN ARRAY_SIZE(gc.RISK_INDICATORS) > 0 THEN 1 END) as calls_with_risks,
        COUNT(CASE WHEN ARRAY_SIZE(gc.NEXT_STEPS) > 0 THEN 1 END) as calls_with_next_steps,

        -- Time analysis
        MAX(gc.CALL_DATETIME_UTC) as last_call_date,
        MIN(gc.CALL_DATETIME_UTC) as first_call_date

    FROM STG_ESTUARY.STG_GONG_CALLS gc
    WHERE gc.CALL_DATETIME_UTC >= DATEADD(month, -3, CURRENT_TIMESTAMP())
    AND gc.PRIMARY_USER_NAME IS NOT NULL
    GROUP BY gc.PRIMARY_USER_NAME, gc.PRIMARY_USER_EMAIL
),
coaching_insights AS (
    SELECT
        mr.METADATA:primary_user::STRING as sales_rep,
        COUNT(*) as coaching_memories,
        AVG(mr.RELEVANCE_SCORE) as avg_coaching_relevance,
        LISTAGG(DISTINCT mr.METADATA:coaching_area::STRING, ', ') as coaching_areas
    FROM AI_MEMORY.MEMORY_RECORDS mr
    WHERE mr.SOURCE_TYPE = 'gong'
    AND mr.CATEGORY = 'gong_coaching_recommendation'
    GROUP BY mr.METADATA:primary_user::STRING
)
SELECT
    rp.*,

    -- Performance scores (0-100)
    LEAST(100, GREATEST(0,
        (rp.avg_sentiment + 1) * 25 +  -- Sentiment contribution (0-50)
        CASE
            WHEN rp.avg_talk_ratio BETWEEN 0.4 AND 0.6 THEN 25  -- Ideal talk ratio
            WHEN rp.avg_talk_ratio BETWEEN 0.3 AND 0.7 THEN 15
            ELSE 5
        END +
        LEAST(25, rp.avg_questions_asked * 5)  -- Questions asked contribution
    )) as performance_score,

    -- Coaching insights
    COALESCE(ci.coaching_memories, 0) as coaching_recommendations_count,
    ci.coaching_areas,

    -- Performance category
    CASE
        WHEN rp.avg_sentiment > 0.4 AND rp.avg_talk_ratio BETWEEN 0.4 AND 0.6 THEN 'Top Performer'
        WHEN rp.avg_sentiment > 0.2 AND rp.total_calls >= 10 THEN 'Strong Performer'
        WHEN rp.avg_sentiment > -0.1 THEN 'Developing'
        ELSE 'Needs Immediate Coaching'
    END as performance_category,

    -- Specific coaching recommendations
    CASE
        WHEN rp.avg_talk_ratio > 0.7 THEN 'Focus on active listening and asking more questions'
        WHEN rp.avg_talk_ratio < 0.3 THEN 'Increase engagement and value proposition delivery'
        WHEN rp.avg_sentiment < 0 THEN 'Work on relationship building and objection handling'
        WHEN rp.avg_questions_asked < 3 THEN 'Improve discovery questioning techniques'
        ELSE 'Continue current approach with minor optimizations'
    END as primary_coaching_focus

FROM rep_performance rp
LEFT JOIN coaching_insights ci ON rp.sales_rep = ci.sales_rep
WHERE rp.total_calls >= 5  -- Minimum call threshold for meaningful analysis
ORDER BY performance_score DESC, total_calls DESC;
```

## 🔗 **Cross-Platform Integration Queries**

### **AI Memory Cross-Reference Analysis**
```sql
-- Cross-reference Gong insights with HubSpot data and AI Memory
WITH gong_hubspot_unified AS (
    SELECT
        gc.CALL_ID,
        gc.HUBSPOT_DEAL_ID,
        gc.ACCOUNT_NAME,
        gc.CALL_DATETIME_UTC,
        gc.SENTIMENT_SCORE,
        gc.CALL_SUMMARY,
        gc.AI_MEMORY_METADATA,

        -- HubSpot deal data (assuming integration)
        -- hd.DEAL_NAME,
        -- hd.DEAL_STAGE as HUBSPOT_DEAL_STAGE,
        -- hd.DEAL_AMOUNT,
        -- hd.CLOSE_DATE,

        -- AI Memory records
        mr.MEMORY_ID,
        mr.CATEGORY as MEMORY_CATEGORY,
        mr.RELEVANCE_SCORE,
        mr.ACCESS_COUNT,
        mr.LAST_ACCESSED_AT

    FROM STG_ESTUARY.STG_GONG_CALLS gc
    LEFT JOIN AI_MEMORY.MEMORY_RECORDS mr
        ON gc.CALL_ID = mr.SOURCE_ID
        AND mr.SOURCE_TYPE = 'gong'
    WHERE gc.CALL_DATETIME_UTC >= DATEADD(month, -1, CURRENT_TIMESTAMP())
)
SELECT
    ACCOUNT_NAME,
    COUNT(DISTINCT CALL_ID) as total_calls,
    COUNT(DISTINCT MEMORY_ID) as ai_memories_created,
    AVG(SENTIMENT_SCORE) as avg_sentiment,
    AVG(RELEVANCE_SCORE) as avg_memory_relevance,
    SUM(ACCESS_COUNT) as total_memory_accesses,

    -- Memory categories for this account
    LISTAGG(DISTINCT MEMORY_CATEGORY, ', ') as memory_categories,

    -- Latest insights
    MAX(CALL_DATETIME_UTC) as latest_call,
    MAX(LAST_ACCESSED_AT) as latest_memory_access,

    -- Account intelligence score
    CASE
        WHEN COUNT(DISTINCT MEMORY_ID) >= 5 AND AVG(RELEVANCE_SCORE) > 0.8 THEN 'High Intelligence'
        WHEN COUNT(DISTINCT MEMORY_ID) >= 3 AND AVG(RELEVANCE_SCORE) > 0.6 THEN 'Good Intelligence'
        WHEN COUNT(DISTINCT MEMORY_ID) >= 1 THEN 'Basic Intelligence'
        ELSE 'Limited Intelligence'
    END as intelligence_level

FROM gong_hubspot_unified
WHERE ACCOUNT_NAME IS NOT NULL
GROUP BY ACCOUNT_NAME
ORDER BY total_memory_accesses DESC, avg_memory_relevance DESC;
```

## 🚀 **Advanced AI Functions**

### **Cortex-Powered Call Summarization**
```sql
-- Generate AI summaries for recent calls without existing summaries
SELECT
    CALL_ID,
    ACCOUNT_NAME,
    CALL_TITLE,
    CALL_DATETIME_UTC,

    -- Generate summary using Snowflake Cortex
    SNOWFLAKE.CORTEX.SUMMARIZE(
        CONCAT(
            'Call Title: ', COALESCE(CALL_TITLE, 'Unknown'),
            '. Account: ', COALESCE(ACCOUNT_NAME, 'Unknown'),
            '. Duration: ', CALL_DURATION_SECONDS / 60, ' minutes.',
            '. Key Topics: ', COALESCE(KEY_TOPICS::STRING, 'None specified')
        )
    ) as AI_GENERATED_SUMMARY,

    -- Sentiment analysis
    SNOWFLAKE.CORTEX.SENTIMENT(
        COALESCE(CALL_SUMMARY, CALL_TITLE)
    ) as AI_SENTIMENT_ANALYSIS,

    -- Topic extraction
    SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
        COALESCE(CALL_SUMMARY, CALL_TITLE),
        'What were the main topics discussed in this call?'
    ) as AI_EXTRACTED_TOPICS

FROM STG_ESTUARY.STG_GONG_CALLS
WHERE CALL_DATETIME_UTC >= DATEADD(day, -7, CURRENT_TIMESTAMP())
AND (CALL_SUMMARY IS NULL OR LENGTH(CALL_SUMMARY) < 50)
AND CALL_TITLE IS NOT NULL
ORDER BY CALL_DATETIME_UTC DESC
LIMIT 20;
```

### **Embedding Generation and Similarity Search**
```sql
-- Generate embeddings for new calls and find similar historical calls
WITH new_call_embeddings AS (
    SELECT
        CALL_ID,
        ACCOUNT_NAME,
        CALL_SUMMARY,
        SNOWFLAKE.CORTEX.EMBED_TEXT(
            'e5-base-v2',
            CONCAT(COALESCE(CALL_SUMMARY, ''), ' ', COALESCE(CALL_TITLE, ''))
        ) as call_embedding
    FROM STG_ESTUARY.STG_GONG_CALLS
    WHERE CALL_DATETIME_UTC >= DATEADD(day, -1, CURRENT_TIMESTAMP())
    AND AI_MEMORY_EMBEDDING IS NULL
),
historical_calls AS (
    SELECT
        CALL_ID as historical_call_id,
        ACCOUNT_NAME as historical_account,
        CALL_SUMMARY as historical_summary,
        AI_MEMORY_EMBEDDING as historical_embedding
    FROM STG_ESTUARY.STG_GONG_CALLS
    WHERE AI_MEMORY_EMBEDDING IS NOT NULL
    AND CALL_DATETIME_UTC >= DATEADD(month, -6, CURRENT_TIMESTAMP())
)
SELECT
    nce.CALL_ID as new_call_id,
    nce.ACCOUNT_NAME as new_account,
    nce.CALL_SUMMARY as new_summary,

    hc.historical_call_id,
    hc.historical_account,
    hc.historical_summary,

    VECTOR_COSINE_SIMILARITY(nce.call_embedding, hc.historical_embedding) as similarity_score

FROM new_call_embeddings nce
CROSS JOIN historical_calls hc
WHERE VECTOR_COSINE_SIMILARITY(nce.call_embedding, hc.historical_embedding) >= 0.8
ORDER BY nce.CALL_ID, similarity_score DESC;
```

## 📈 **Monitoring & Operations Queries**

### **Data Pipeline Health Check**
```sql
-- Monitor the health of the Gong data pipeline
SELECT
    'RAW_ESTUARY.RAW_GONG_CALLS_RAW' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN PROCESSED = TRUE THEN 1 END) as processed_records,
    COUNT(CASE WHEN PROCESSED = FALSE THEN 1 END) as pending_records,
    COUNT(CASE WHEN PROCESSING_ERROR IS NOT NULL THEN 1 END) as error_records,
    MAX(INGESTED_AT) as latest_ingestion,
    MIN(INGESTED_AT) as earliest_ingestion
FROM RAW_ESTUARY.RAW_GONG_CALLS_RAW

UNION ALL

SELECT
    'STG_ESTUARY.STG_GONG_CALLS' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN AI_MEMORY_EMBEDDING IS NOT NULL THEN 1 END) as records_with_embeddings,
    COUNT(CASE WHEN CALL_SUMMARY IS NOT NULL THEN 1 END) as records_with_summaries,
    COUNT(CASE WHEN PROCESSED_BY_CORTEX = TRUE THEN 1 END) as cortex_processed,
    MAX(UPDATED_AT) as latest_update,
    MIN(CREATED_AT) as earliest_record
FROM STG_ESTUARY.STG_GONG_CALLS

UNION ALL

SELECT
    'AI_MEMORY.MEMORY_RECORDS (Gong)' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN EMBEDDING IS NOT NULL THEN 1 END) as records_with_embeddings,
    COUNT(CASE WHEN IS_ACTIVE = TRUE THEN 1 END) as active_records,
    COUNT(DISTINCT CATEGORY) as unique_categories,
    MAX(UPDATED_AT) as latest_update,
    MIN(CREATED_AT) as earliest_record
FROM AI_MEMORY.MEMORY_RECORDS
WHERE SOURCE_TYPE = 'gong';
```

### **Performance Monitoring**
```sql
-- Monitor query performance and usage patterns
SELECT
    'Gong Calls Semantic Search' as operation_type,
    COUNT(*) as total_operations,
    AVG(DATEDIFF('millisecond', query_start_time, query_end_time)) as avg_duration_ms,
    MAX(DATEDIFF('millisecond', query_start_time, query_end_time)) as max_duration_ms,
    COUNT(CASE WHEN DATEDIFF('millisecond', query_start_time, query_end_time) > 5000 THEN 1 END) as slow_queries
FROM OPS_MONITORING.ETL_JOB_LOGS
WHERE JOB_TYPE = 'gong_semantic_search'
AND LOG_TIMESTAMP >= DATEADD(day, -7, CURRENT_TIMESTAMP())

UNION ALL

SELECT
    'AI Memory Storage' as operation_type,
    COUNT(*) as total_operations,
    AVG(DATEDIFF('millisecond', query_start_time, query_end_time)) as avg_duration_ms,
    MAX(DATEDIFF('millisecond', query_start_time, query_end_time)) as max_duration_ms,
    COUNT(CASE WHEN DATEDIFF('millisecond', query_start_time, query_end_time) > 2000 THEN 1 END) as slow_operations
FROM OPS_MONITORING.ETL_JOB_LOGS
WHERE JOB_TYPE = 'ai_memory_storage'
AND LOG_TIMESTAMP >= DATEADD(day, -7, CURRENT_TIMESTAMP());
```

This guide provides a comprehensive foundation for working with the Sophia AI Snowflake setup. Adapt these queries to your specific use cases and always test in the development environment first.
