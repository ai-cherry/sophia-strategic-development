# Gong Pipeline Integration Guide

## Overview
The Gong Pipeline Integration provides comprehensive access to Gong call data through Sophia AI's enhanced data processing and AI capabilities.

## Architecture
```
Gong API → Airbyte → RAW_AIRBYTE → STG_TRANSFORMED → AI_MEMORY → Sophia AI Services
```

## Key Tables

### STG_TRANSFORMED.STG_GONG_CALLS
- CALL_ID: Unique call identifier
- SENTIMENT_SCORE: AI-generated sentiment (-1 to 1)
- CALL_SUMMARY: AI-generated call summary
- KEY_TOPICS: Extracted topics and themes
- RISK_INDICATORS: Identified risk factors
- AI_MEMORY_EMBEDDING: Vector embedding for semantic search

### STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS
- TRANSCRIPT_ID: Unique transcript segment identifier
- CALL_ID: Reference to parent call
- TRANSCRIPT_TEXT: Conversation text
- SEGMENT_SENTIMENT: Segment-level sentiment
- EXTRACTED_ENTITIES: Named entities in segment

## Usage Examples

### Natural Language Queries
- "Show me calls with negative sentiment from last week"
- "What are customers saying about pricing?"
- "Find coaching opportunities for the sales team"

### Direct SQL Access
```sql
SELECT CALL_ID, SENTIMENT_SCORE, CALL_SUMMARY
FROM SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS
WHERE SENTIMENT_SCORE < -0.2
ORDER BY CALL_DATETIME_UTC DESC;
```

## Configuration

### Required Secrets (Pulumi ESC)
- `gong_access_key`: Gong API access key
- `gong_client_secret`: Gong API client secret
- `airbyte_server_url`: Airbyte server URL
- `snowflake_*`: Snowflake connection parameters

## Deployment

### Phase 1: Infrastructure
```bash
python backend/scripts/deploy_gong_snowflake_setup.py --env dev
```

### Phase 2: Airbyte Setup
```bash
python backend/scripts/airbyte_gong_setup.py --setup-complete-pipeline
```

### Phase 3: Testing
```bash
python backend/scripts/enhanced_airbyte_integration_test_suite.py --environment dev
```

## Business Value

- **360° Call Intelligence**: Comprehensive analysis of customer conversations
- **Predictive Risk Assessment**: Early identification of at-risk deals
- **Automated Coaching**: AI-powered sales coaching recommendations
- **Semantic Search**: Natural language queries across all call content

## Monitoring

- Pipeline health and status monitoring
- Data quality validation
- Performance metrics tracking
- Automated alerting for issues 