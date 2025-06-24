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
SHOW TABLES IN SCHEMA STG_TRANSFORMED;
SHOW TABLES IN SCHEMA AI_MEMORY;
SHOW TABLES IN SCHEMA OPS_MONITORING;
SHOW TABLES IN SCHEMA CONFIG;

-- Get table details with column information
DESCRIBE TABLE STG_TRANSFORMED.STG_GONG_CALLS;
DESCRIBE TABLE STG_TRANSFORMED.STG_HUBSPOT_DEALS;
```

### Check Data Availability

```sql
-- Check record counts across key tables
SELECT 
    'STG_GONG_CALLS' as table_name,
    COUNT(*) as record_count,
    MIN(CREATED_AT) as earliest_record,
    MAX(UPDATED_AT) as latest_update
FROM STG_TRANSFORMED.STG_GONG_CALLS

UNION ALL

SELECT 
    'STG_HUBSPOT_DEALS' as table_name,
    COUNT(*) as record_count,
    MIN(CREATED_AT) as earliest_record,
    MAX(LAST_REFRESHED) as latest_update
FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS

UNION ALL

SELECT 
    'STG_GONG_CALL_TRANSCRIPTS' as table_name,
    COUNT(*) as record_count,
    MIN(CREATED_AT) as earliest_record,
    MAX(CREATED_AT) as latest_update
FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS;
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
FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
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
FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
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
FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS hd
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
FROM STG_TRANSFORMED.STG_GONG_CALLS
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
FROM STG_TRANSFORMED.STG_GONG_CALLS
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
FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS t
JOIN STG_TRANSFORMED.STG_GONG_CALLS c ON t.CALL_ID = c.CALL_ID
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
    FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
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
FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS hd
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
FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS t
JOIN STG_TRANSFORMED.STG_GONG_CALLS c ON t.CALL_ID = c.CALL_ID
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
FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
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
FROM STG_TRANSFORMED.STG_GONG_CALLS
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
FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
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
    FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS hd
    LEFT JOIN STG_TRANSFORMED.STG_GONG_CALLS gc ON hd.DEAL_ID = gc.HUBSPOT_DEAL_ID
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
WHERE TABLE_SCHEMA = 'STG_TRANSFORMED'
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
WHERE TABLE_SCHEMA IN ('STG_TRANSFORMED', 'AI_MEMORY')
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
FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
WHERE AI_MEMORY_EMBEDDING IS NULL
AND DEAL_NAME IS NOT NULL

UNION ALL

SELECT 
    'STG_GONG_CALL_TRANSCRIPTS' as table_name,
    COUNT(*) as records_without_embeddings
FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS
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

This guide provides a comprehensive foundation for working with the Sophia AI Snowflake setup. Adapt these queries to your specific use cases and always test in the development environment first. 