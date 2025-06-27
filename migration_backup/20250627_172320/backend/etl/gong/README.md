# Gong Data ETL for Snowflake Integration

This directory contains the complete ETL pipeline for ingesting Gong call data into Snowflake and processing it with Snowflake Cortex AI capabilities.

## 📋 Overview

The Gong ETL pipeline provides:

- **Raw Data Ingestion**: Fetch call data and transcripts from Gong API
- **Structured Transformation**: Convert JSON data to relational tables
- **AI Processing**: Leverage Snowflake Cortex for sentiment analysis, summarization, and embeddings
- **HubSpot Integration**: Join Gong data with HubSpot Secure Data Share
- **Agent-Ready Data**: Prepare data for Sales Coach and Call Analysis agents

## 🏗️ Architecture

```
Gong API → Raw Tables (VARIANT) → Structured Tables → Cortex AI → Agent Processing
    ↓                                    ↓
Transcripts API → Raw Transcripts → Transcript Segments → Vector Embeddings
                                           ↓
                              HubSpot Secure Data Share → Enriched Views
```

## 📁 Files Structure

```
backend/etl/gong/
├── README.md                     # This file
├── ingest_gong_data.py          # Python ingestion script
├── snowflake_gong_schema.sql    # DDL and transformation logic
└── config/                      # Configuration files (optional)
    ├── airbyte_gong_config.json # Airbyte connector config
    └── fivetran_gong_config.json # Fivetran connector config
```

## 🚀 Setup Instructions

### Option 1: Python Script Ingestion (Recommended for Custom Control)

#### Prerequisites
```bash
# Install required Python packages
pip install snowflake-connector-python aiohttp structlog pydantic

# Ensure Pulumi ESC secrets are configured:
# - gong_access_key
# - gong_access_key_secret  
# - snowflake_user
# - snowflake_password
# - snowflake_account
# - snowflake_database
# - snowflake_warehouse
```

#### Database Setup
```sql
-- Execute the schema creation script
-- File: snowflake_gong_schema.sql
USE DATABASE SOPHIA_AI;
CREATE SCHEMA IF NOT EXISTS GONG_DATA;
-- (Execute remaining DDL from schema file)
```

#### Run Ingestion
```bash
# Incremental sync (default)
python backend/etl/gong/ingest_gong_data.py

# Full sync from specific date
python backend/etl/gong/ingest_gong_data.py \
    --sync-mode full \
    --from-date 2024-01-01 \
    --to-date 2024-12-31

# Incremental without transcripts (faster)
python backend/etl/gong/ingest_gong_data.py \
    --sync-mode incremental \
    --no-transcripts
```

### Option 2: Airbyte Connector (Recommended for Production Scale)

#### Airbyte Configuration
```json
{
  "source": {
    "sourceDefinitionId": "gong-source",
    "connectionConfiguration": {
      "access_key": "${GONG_ACCESS_KEY}",
      "access_key_secret": "${GONG_ACCESS_KEY_SECRET}",
      "start_date": "2024-01-01T00:00:00Z",
      "call_types": ["inbound", "outbound"],
      "include_transcripts": true
    }
  },
  "destination": {
    "destinationDefinitionId": "snowflake-destination",
    "connectionConfiguration": {
      "host": "${SNOWFLAKE_ACCOUNT}.snowflakecomputing.com",
      "role": "SOPHIA_AI_ROLE",
      "warehouse": "COMPUTE_WH",
      "database": "SOPHIA_AI",
      "schema": "GONG_DATA",
      "username": "${SNOWFLAKE_USER}",
      "password": "${SNOWFLAKE_PASSWORD}",
      "jdbc_url_params": "CLIENT_SESSION_KEEP_ALIVE=true"
    }
  },
  "schedule": {
    "scheduleType": "cron",
    "cronExpression": "0 */4 * * * ?" // Every 4 hours
  }
}
```

#### Expected Raw Data Structure
```sql
-- Airbyte will create these tables automatically:
-- _airbyte_raw_calls (VARIANT column with full JSON)
-- _airbyte_raw_call_transcripts (VARIANT column with transcript JSON)

-- Example raw JSON structure:
{
  "id": "call_12345",
  "title": "Discovery Call - Acme Corp",
  "started": "2024-01-15T14:30:00Z",
  "duration": 1800,
  "direction": "Outbound",
  "primaryUserId": "user_789",
  "customData": {
    "hubspotDealId": "deal_456",
    "hubspotContactId": "contact_123",
    "hubspotCompanyId": "company_789",
    "dealStage": "Qualification",
    "dealValue": 50000
  },
  "participants": [
    {
      "userId": "user_789",
      "emailAddress": "sales@yourcompany.com",
      "name": "John Smith"
    }
  ]
}
```

### Option 3: Fivetran Connector (Enterprise Option)

#### Fivetran Configuration
```json
{
  "connector_type": "gong",
  "config": {
    "access_key": "${GONG_ACCESS_KEY}",
    "access_key_secret": "${GONG_ACCESS_KEY_SECRET}",
    "domain": "your-company.gong.io",
    "start_date": "2024-01-01",
    "sync_frequency": "240", // 4 hours
    "destination": {
      "type": "snowflake",
      "config": {
        "host": "${SNOWFLAKE_ACCOUNT}.snowflakecomputing.com",
        "database": "SOPHIA_AI",
        "schema": "GONG_DATA",
        "warehouse": "COMPUTE_WH"
      }
    }
  }
}
```

## 🔄 Data Pipeline Flow

### 1. Raw Data Ingestion
```sql
-- Raw tables store JSON data as VARIANT
GONG_CALLS_RAW (
    CALL_ID VARCHAR(255),
    RAW_DATA VARIANT,  -- Full Gong API response
    INGESTED_AT TIMESTAMP_LTZ,
    PROCESSED BOOLEAN
)

GONG_CALL_TRANSCRIPTS_RAW (
    CALL_ID VARCHAR(255),
    TRANSCRIPT_DATA VARIANT,  -- Full transcript JSON
    INGESTED_AT TIMESTAMP_LTZ,
    PROCESSED BOOLEAN
)
```

### 2. Structured Transformation
```sql
-- Automated procedures extract structured data
CALL TRANSFORM_RAW_CALLS();        -- Every 15 minutes
CALL TRANSFORM_RAW_TRANSCRIPTS();  -- Every 30 minutes

-- Results in structured tables:
STG_GONG_CALLS (
    CALL_ID, CALL_TITLE, CALL_DATETIME_UTC,
    HUBSPOT_DEAL_ID, SENTIMENT_SCORE, CALL_SUMMARY, ...
)

STG_GONG_CALL_TRANSCRIPTS (
    TRANSCRIPT_ID, CALL_ID, SPEAKER_NAME,
    TRANSCRIPT_TEXT, SEGMENT_SENTIMENT,
    TRANSCRIPT_EMBEDDING VECTOR(FLOAT, 1536), ...
)
```

### 3. Cortex AI Processing
```sql
-- Automated AI processing with Snowflake Cortex
CALL PROCESS_CALLS_WITH_CORTEX();      -- Every hour
CALL PROCESS_TRANSCRIPTS_WITH_CORTEX(); -- Every 2 hours

-- AI enhancements:
-- - SNOWFLAKE.CORTEX.SENTIMENT() for sentiment scores
-- - SNOWFLAKE.CORTEX.SUMMARIZE() for call summaries
-- - SNOWFLAKE.CORTEX.EMBED_TEXT() for vector embeddings
```

### 4. HubSpot Integration
```sql
-- Views join Gong data with HubSpot Secure Data Share
SELECT 
    gc.CALL_ID,
    gc.SENTIMENT_SCORE,
    hd.DEAL_NAME,
    hd.DEAL_STAGE,
    hd.DEAL_AMOUNT
FROM STG_GONG_CALLS gc
JOIN HUBSPOT_SECURE_SHARE.PUBLIC.DEALS hd 
    ON gc.HUBSPOT_DEAL_ID = hd.DEAL_ID;
```

## 🤖 Agent Integration

### Sales Coach Agent Data Access
```python
# Example: Get calls needing coaching attention
async def get_coaching_opportunities():
    query = """
    SELECT 
        CALL_ID,
        PRIMARY_USER_NAME,
        SENTIMENT_SCORE,
        TALK_RATIO,
        CALL_SUMMARY,
        DEAL_STAGE
    FROM VW_ENRICHED_GONG_CALLS
    WHERE (SENTIMENT_SCORE < 0.3 OR TALK_RATIO > 0.8)
    AND CALL_DATETIME_UTC >= DATEADD('day', -7, CURRENT_DATE())
    ORDER BY SENTIMENT_SCORE ASC
    """
    return await snowflake_connector.execute_query(query)
```

### Call Analysis Agent Processing
```python
# Example: Analyze call with Cortex AI
async def analyze_call_with_cortex(call_id: str):
    query = """
    SELECT 
        CALL_ID,
        SNOWFLAKE.CORTEX.SUMMARIZE(
            CALL_TITLE || ': ' || STRING_AGG(TRANSCRIPT_TEXT, ' '),
            500
        ) AS AI_SUMMARY,
        AVG(SEGMENT_SENTIMENT) AS OVERALL_SENTIMENT,
        STRING_AGG(
            CASE WHEN SEGMENT_SENTIMENT < 0.2 
            THEN TRANSCRIPT_TEXT ELSE NULL END, 
            ' | '
        ) AS RISK_SEGMENTS
    FROM STG_GONG_CALLS gc
    JOIN STG_GONG_CALL_TRANSCRIPTS t ON gc.CALL_ID = t.CALL_ID
    WHERE gc.CALL_ID = ?
    GROUP BY gc.CALL_ID, gc.CALL_TITLE
    """
    return await snowflake_connector.execute_query(query, [call_id])
```

### Semantic Search for Similar Calls
```python
# Example: Find similar calls using vector embeddings
async def find_similar_calls(query_text: str, limit: int = 10):
    query = """
    WITH query_embedding AS (
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', ?) AS query_vector
    )
    SELECT 
        t.CALL_ID,
        t.TRANSCRIPT_TEXT,
        t.SEGMENT_SENTIMENT,
        VECTOR_COSINE_SIMILARITY(q.query_vector, t.TRANSCRIPT_EMBEDDING) AS similarity
    FROM STG_GONG_CALL_TRANSCRIPTS t
    CROSS JOIN query_embedding q
    WHERE VECTOR_COSINE_SIMILARITY(q.query_vector, t.TRANSCRIPT_EMBEDDING) > 0.7
    ORDER BY similarity DESC
    LIMIT ?
    """
    return await snowflake_connector.execute_query(query, [query_text, limit])
```

## ⚙️ Configuration Management

### Pulumi ESC Secrets Required
```yaml
# Add to sophia-ai-production stack
gong_access_key: "your_gong_access_key"
gong_access_key_secret: "your_gong_secret_key"
snowflake_user: "SOPHIA_AI_USER"
snowflake_password: "encrypted_password"
snowflake_account: "your_account_identifier"
snowflake_database: "SOPHIA_AI"
snowflake_schema: "GONG_DATA"
snowflake_warehouse: "COMPUTE_WH"
snowflake_role: "SOPHIA_AI_ROLE"
```

### Environment Variables (Alternative)
```bash
# For local development only
export GONG_ACCESS_KEY="your_access_key"
export GONG_ACCESS_KEY_SECRET="your_secret"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_ACCOUNT="your_account"
```

## 📊 Monitoring and Maintenance

### Task Monitoring
```sql
-- Check task execution status
SELECT 
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    RETURN_VALUE,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'TASK_%GONG%'
ORDER BY SCHEDULED_TIME DESC;
```

### Data Quality Checks
```sql
-- Check ingestion completeness
SELECT 
    DATE(INGESTED_AT) AS ingestion_date,
    COUNT(*) AS calls_ingested,
    COUNT(CASE WHEN PROCESSED THEN 1 END) AS calls_processed,
    COUNT(CASE WHEN PROCESSED IS FALSE THEN 1 END) AS calls_pending
FROM GONG_CALLS_RAW
WHERE INGESTED_AT >= DATEADD('day', -7, CURRENT_DATE())
GROUP BY DATE(INGESTED_AT)
ORDER BY ingestion_date DESC;
```

### Performance Optimization
```sql
-- Add indexes for query performance
CREATE INDEX IF NOT EXISTS IX_GONG_CALLS_DATETIME 
    ON STG_GONG_CALLS(CALL_DATETIME_UTC);

CREATE INDEX IF NOT EXISTS IX_GONG_CALLS_HUBSPOT_DEAL 
    ON STG_GONG_CALLS(HUBSPOT_DEAL_ID);

CREATE INDEX IF NOT EXISTS IX_TRANSCRIPT_CALL_ID 
    ON STG_GONG_CALL_TRANSCRIPTS(CALL_ID);
```

## 🔧 Troubleshooting

### Common Issues

#### 1. API Rate Limiting
```python
# Error: Gong API rate limit exceeded
# Solution: Increase rate_limit_delay in GongAPIClient
self.rate_limit_delay = 2.0  # Increase from 1.0 to 2.0 seconds
```

#### 2. Snowflake Connection Issues
```python
# Error: Snowflake authentication failed
# Check: Pulumi ESC secret values
await config.validate_snowflake_credentials()
```

#### 3. Missing Transcripts
```sql
-- Check calls without transcripts
SELECT 
    gc.CALL_ID,
    gc.CALL_TITLE,
    gc.CALL_DATETIME_UTC
FROM STG_GONG_CALLS gc
LEFT JOIN STG_GONG_CALL_TRANSCRIPTS t ON gc.CALL_ID = t.CALL_ID
WHERE t.CALL_ID IS NULL
AND gc.CALL_DATETIME_UTC >= DATEADD('day', -7, CURRENT_DATE());
```

#### 4. Cortex Processing Errors
```sql
-- Check Cortex processing status
SELECT 
    PROCESSED_BY_CORTEX,
    COUNT(*) as call_count
FROM STG_GONG_CALLS
WHERE CALL_DATETIME_UTC >= DATEADD('day', -1, CURRENT_DATE())
GROUP BY PROCESSED_BY_CORTEX;
```

### Recovery Procedures

#### Reprocess Failed Records
```sql
-- Reset processing flags for retry
UPDATE GONG_CALLS_RAW 
SET PROCESSED = FALSE, PROCESSING_ERROR = NULL
WHERE PROCESSING_ERROR IS NOT NULL;

-- Rerun transformation
CALL TRANSFORM_RAW_CALLS();
```

#### Backfill Missing Data
```bash
# Backfill specific date range
python backend/etl/gong/ingest_gong_data.py \
    --sync-mode backfill \
    --from-date 2024-01-01 \
    --to-date 2024-01-31
```

## 🚀 Production Deployment

### Recommended Schedule
```sql
-- Production task schedule
-- Raw data ingestion: Every 4 hours
-- Transformation: Every 15-30 minutes  
-- Cortex processing: Every 1-2 hours
-- HubSpot sync: Every hour (via Secure Data Share)
```

### Scaling Considerations
- **Warehouse Size**: Start with MEDIUM, scale to LARGE for high volume
- **Parallel Processing**: Use multiple warehouses for concurrent processing
- **Data Retention**: Implement archival strategy for old call data
- **Cost Optimization**: Use AUTO_SUSPEND and AUTO_RESUME for warehouses

### Security Best Practices
- Store all secrets in Pulumi ESC
- Use service accounts with minimal required permissions
- Enable Snowflake query logging and monitoring
- Implement data masking for sensitive transcript content
- Regular credential rotation

## 📈 Success Metrics

### Data Pipeline Health
- **Ingestion Rate**: Calls per hour successfully processed
- **Processing Latency**: Time from API fetch to agent-ready data
- **Error Rate**: Percentage of failed ingestion attempts
- **Data Freshness**: Age of most recent processed call

### Business Value
- **Agent Response Time**: Faster insights with Snowflake Cortex
- **Data Quality**: Improved accuracy with structured transformation
- **Cost Efficiency**: Reduced external API dependencies
- **Scalability**: Handle increasing call volume seamlessly

---

## 🔗 Related Documentation

- [Snowflake HubSpot Integration](../../../SNOWFLAKE_HUBSPOT_INTEGRATION_SUMMARY.md)
- [Snowflake Cortex Service](../../utils/snowflake_cortex_service.py)
- [Sales Coach Agent](../../agents/specialized/sales_coach_agent.py)
- [Call Analysis Agent](../../agents/specialized/call_analysis_agent.py)

For questions or issues, check the troubleshooting section above or consult the Sophia AI team. 