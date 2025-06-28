-- Manus AI Final Gong DDL v2.0
-- Consolidated SQL script for complete Gong data pipeline in Snowflake

-- ============================================================================
-- SECTION 1: RAW_AIRBYTE SCHEMA - Landing tables for raw Gong data
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_DEV.RAW_AIRBYTE
COMMENT = 'Raw data landing zone for Airbyte and direct API ingestion';

USE SCHEMA SOPHIA_AI_DEV.RAW_AIRBYTE;

-- RAW_GONG_CALLS_RAW: Raw calls data from Gong API
CREATE TABLE IF NOT EXISTS RAW_GONG_CALLS_RAW (
    _AIRBYTE_AB_ID VARCHAR(64) PRIMARY KEY,
    _AIRBYTE_EMITTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _AIRBYTE_NORMALIZED_AT TIMESTAMP_LTZ,
    _AIRBYTE_RAW_GONG_CALLS_HASHID VARCHAR(64),
    _AIRBYTE_DATA VARIANT NOT NULL,
    
    -- Extraction helper columns
    CALL_ID VARCHAR(255) AS (_AIRBYTE_DATA:id::VARCHAR),
    CALL_STARTED_AT TIMESTAMP_LTZ AS (_AIRBYTE_DATA:started::TIMESTAMP_LTZ),
    CALL_TITLE VARCHAR(500) AS (_AIRBYTE_DATA:title::VARCHAR),
    
    -- Processing tracking
    PROCESSED BOOLEAN DEFAULT FALSE,
    PROCESSED_AT TIMESTAMP_LTZ,
    PROCESSING_ERROR VARCHAR(16777216),
    
    -- Metadata
    INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CORRELATION_ID VARCHAR(255),
    SOURCE_SYSTEM VARCHAR(50) DEFAULT 'GONG_API'
)
COMMENT = 'Raw Gong calls data from API ingestion with VARIANT storage for flexibility';

-- RAW_GONG_CALL_TRANSCRIPTS_RAW: Raw transcript data
CREATE TABLE IF NOT EXISTS RAW_GONG_CALL_TRANSCRIPTS_RAW (
    _AIRBYTE_AB_ID VARCHAR(64) PRIMARY KEY,
    _AIRBYTE_EMITTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _AIRBYTE_NORMALIZED_AT TIMESTAMP_LTZ,
    _AIRBYTE_RAW_GONG_TRANSCRIPTS_HASHID VARCHAR(64),
    _AIRBYTE_DATA VARIANT NOT NULL,
    
    -- Extraction helper columns
    CALL_ID VARCHAR(255) AS (_AIRBYTE_DATA:callId::VARCHAR),
    TRANSCRIPT_ID VARCHAR(255) AS (_AIRBYTE_DATA:id::VARCHAR),
    
    -- Processing tracking
    PROCESSED BOOLEAN DEFAULT FALSE,
    PROCESSED_AT TIMESTAMP_LTZ,
    PROCESSING_ERROR VARCHAR(16777216),
    
    -- Metadata
    INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CORRELATION_ID VARCHAR(255),
    SOURCE_SYSTEM VARCHAR(50) DEFAULT 'GONG_API'
)
COMMENT = 'Raw Gong call transcripts with VARIANT storage for transcript segments';

-- ============================================================================
-- SECTION 2: STG_TRANSFORMED SCHEMA - Structured tables with AI Memory integration
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_DEV.STG_TRANSFORMED
COMMENT = 'Structured data layer with AI Memory integration';

USE SCHEMA SOPHIA_AI_DEV.STG_TRANSFORMED;

-- STG_GONG_CALLS: Structured Gong calls with AI Memory columns
CREATE TABLE IF NOT EXISTS STG_GONG_CALLS (
    CALL_ID VARCHAR(255) PRIMARY KEY,
    CALL_TITLE VARCHAR(500),
    CALL_DATETIME_UTC TIMESTAMP_LTZ,
    CALL_DURATION_SECONDS NUMBER,
    CALL_DIRECTION VARCHAR(50),
    CALL_SYSTEM VARCHAR(100),
    CALL_SCOPE VARCHAR(100),
    CALL_MEDIA VARCHAR(50),
    CALL_LANGUAGE VARCHAR(10),
    CALL_URL VARCHAR(1000),
    
    -- Primary user/owner
    PRIMARY_USER_ID VARCHAR(255),
    PRIMARY_USER_EMAIL VARCHAR(255),
    PRIMARY_USER_NAME VARCHAR(255),
    
    -- CRM Integration fields
    HUBSPOT_DEAL_ID VARCHAR(255),
    HUBSPOT_CONTACT_ID VARCHAR(255),
    HUBSPOT_COMPANY_ID VARCHAR(255),
    CRM_OPPORTUNITY_ID VARCHAR(255),
    CRM_ACCOUNT_ID VARCHAR(255),
    
    -- Business context
    DEAL_STAGE VARCHAR(100),
    DEAL_VALUE NUMBER(15,2),
    ACCOUNT_NAME VARCHAR(500),
    CONTACT_NAME VARCHAR(500),
    
    -- Call quality metrics
    TALK_RATIO FLOAT,
    LONGEST_MONOLOGUE_SECONDS NUMBER,
    INTERACTIVITY_SCORE FLOAT,
    QUESTIONS_ASKED_COUNT NUMBER,
    
    -- AI-generated insights (Snowflake Cortex)
    SENTIMENT_SCORE FLOAT,
    CALL_SUMMARY VARCHAR(16777216),
    KEY_TOPICS VARIANT,
    RISK_INDICATORS VARIANT,
    NEXT_STEPS VARIANT,
    COMPETITIVE_MENTIONS VARIANT,
    
    -- AI Memory columns for semantic search and storage
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARIANT,
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
    CORTEX_PROCESSED_AT TIMESTAMP_LTZ,
    
    -- Data quality
    DATA_QUALITY_SCORE FLOAT DEFAULT 1.0,
    VALIDATION_STATUS VARCHAR(50) DEFAULT 'PENDING'
)
COMMENT = 'Structured Gong calls with comprehensive AI Memory integration and business context';

-- STG_GONG_CALL_TRANSCRIPTS: Structured call transcripts with AI processing
CREATE TABLE IF NOT EXISTS STG_GONG_CALL_TRANSCRIPTS (
    TRANSCRIPT_ID VARCHAR(255) PRIMARY KEY,
    CALL_ID VARCHAR(255) NOT NULL,
    SPEAKER_NAME VARCHAR(255),
    SPEAKER_EMAIL VARCHAR(255),
    SPEAKER_TYPE VARCHAR(50),
    TRANSCRIPT_TEXT VARCHAR(16777216),
    START_TIME_SECONDS NUMBER,
    END_TIME_SECONDS NUMBER,
    SEGMENT_DURATION_SECONDS NUMBER,
    WORD_COUNT NUMBER,
    
    -- AI processing results (Snowflake Cortex)
    SEGMENT_SENTIMENT FLOAT,
    SEGMENT_SUMMARY VARCHAR(4000),
    EXTRACTED_ENTITIES VARIANT,
    KEY_PHRASES VARIANT,
    INTENT_CLASSIFICATION VARCHAR(100),
    
    -- AI Memory columns for semantic search
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARIANT,
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
    CORTEX_PROCESSED_AT TIMESTAMP_LTZ,
    
    FOREIGN KEY (CALL_ID) REFERENCES STG_GONG_CALLS(CALL_ID)
)
COMMENT = 'Structured Gong call transcripts with AI processing and semantic search capabilities';

-- ============================================================================
-- SECTION 3: TRANSFORMATION PROCEDURES
-- ============================================================================

-- Transform raw Gong calls to structured format
CREATE OR REPLACE PROCEDURE TRANSFORM_RAW_GONG_CALLS()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
    execution_id VARCHAR(255) DEFAULT CONCAT('GONG_CALLS_', TO_VARCHAR(CURRENT_TIMESTAMP, 'YYYYMMDD_HHMMSS'));
BEGIN
    
    -- Log transformation start
    INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_JOB_LOGS 
    (JOB_ID, JOB_NAME, JOB_TYPE, STATUS, START_TIME, DETAILS)
    VALUES 
    (execution_id, 'TRANSFORM_RAW_GONG_CALLS', 'TRANSFORMATION', 'RUNNING', CURRENT_TIMESTAMP, 
     'Starting transformation of raw Gong calls to structured format');
    
    -- First insert new records that don't exist
    INSERT INTO SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS (
        CALL_ID, CALL_TITLE, CALL_DATETIME_UTC, CALL_DURATION_SECONDS,
        CALL_DIRECTION, CALL_SYSTEM, CALL_SCOPE, CALL_MEDIA, CALL_LANGUAGE, CALL_URL,
        PRIMARY_USER_ID, PRIMARY_USER_EMAIL, PRIMARY_USER_NAME,
        HUBSPOT_DEAL_ID, HUBSPOT_CONTACT_ID, HUBSPOT_COMPANY_ID,
        DEAL_STAGE, DEAL_VALUE, ACCOUNT_NAME, CONTACT_NAME,
        TALK_RATIO, LONGEST_MONOLOGUE_SECONDS, INTERACTIVITY_SCORE, QUESTIONS_ASKED_COUNT,
        UPDATED_AT, VALIDATION_STATUS, DATA_QUALITY_SCORE
    )
    SELECT 
        _AIRBYTE_DATA:id::VARCHAR AS CALL_ID,
        _AIRBYTE_DATA:title::VARCHAR AS CALL_TITLE,
        _AIRBYTE_DATA:started::TIMESTAMP_LTZ AS CALL_DATETIME_UTC,
        _AIRBYTE_DATA:duration::NUMBER AS CALL_DURATION_SECONDS,
        _AIRBYTE_DATA:direction::VARCHAR AS CALL_DIRECTION,
        _AIRBYTE_DATA:system::VARCHAR AS CALL_SYSTEM,
        _AIRBYTE_DATA:scope::VARCHAR AS CALL_SCOPE,
        _AIRBYTE_DATA:media::VARCHAR AS CALL_MEDIA,
        _AIRBYTE_DATA:language::VARCHAR AS CALL_LANGUAGE,
        _AIRBYTE_DATA:url::VARCHAR AS CALL_URL,
            
        -- Primary user extraction
        COALESCE(_AIRBYTE_DATA:primaryUserId::VARCHAR, _AIRBYTE_DATA:ownerId::VARCHAR) AS PRIMARY_USER_ID,
        COALESCE(_AIRBYTE_DATA:primaryUser.emailAddress::VARCHAR, _AIRBYTE_DATA:owner.emailAddress::VARCHAR) AS PRIMARY_USER_EMAIL,
        CONCAT(
            COALESCE(_AIRBYTE_DATA:primaryUser.firstName::VARCHAR, _AIRBYTE_DATA:owner.firstName::VARCHAR, ''),
            ' ',
            COALESCE(_AIRBYTE_DATA:primaryUser.lastName::VARCHAR, _AIRBYTE_DATA:owner.lastName::VARCHAR, '')
        ) AS PRIMARY_USER_NAME,
            
        -- CRM data extraction
        COALESCE(
            _AIRBYTE_DATA:customData.hubspotDealId::VARCHAR,
            _AIRBYTE_DATA:crmData.dealId::VARCHAR
        ) AS HUBSPOT_DEAL_ID,
            
        COALESCE(
            _AIRBYTE_DATA:customData.hubspotContactId::VARCHAR,
            _AIRBYTE_DATA:crmData.contactId::VARCHAR
        ) AS HUBSPOT_CONTACT_ID,
            
        COALESCE(
            _AIRBYTE_DATA:customData.hubspotCompanyId::VARCHAR,
            _AIRBYTE_DATA:crmData.companyId::VARCHAR
        ) AS HUBSPOT_COMPANY_ID,
            
        -- Business context
        COALESCE(_AIRBYTE_DATA:customData.dealStage::VARCHAR, _AIRBYTE_DATA:crmData.stage::VARCHAR) AS DEAL_STAGE,
        COALESCE(_AIRBYTE_DATA:customData.dealValue::NUMBER, _AIRBYTE_DATA:crmData.value::NUMBER) AS DEAL_VALUE,
        COALESCE(_AIRBYTE_DATA:customData.accountName::VARCHAR, _AIRBYTE_DATA:crmData.accountName::VARCHAR) AS ACCOUNT_NAME,
        COALESCE(_AIRBYTE_DATA:customData.contactName::VARCHAR, _AIRBYTE_DATA:crmData.contactName::VARCHAR) AS CONTACT_NAME,
            
        -- Call metrics
        TRY_CAST(_AIRBYTE_DATA:analytics.talkRatio::VARCHAR AS FLOAT) AS TALK_RATIO,
        TRY_CAST(_AIRBYTE_DATA:analytics.longestMonologue::VARCHAR AS NUMBER) AS LONGEST_MONOLOGUE_SECONDS,
        TRY_CAST(_AIRBYTE_DATA:analytics.interactivity::VARCHAR AS FLOAT) AS INTERACTIVITY_SCORE,
        TRY_CAST(_AIRBYTE_DATA:analytics.questionsAsked::VARCHAR AS NUMBER) AS QUESTIONS_ASKED_COUNT,
            
        CURRENT_TIMESTAMP AS UPDATED_AT,
        'PENDING' AS VALIDATION_STATUS,
        1.0 AS DATA_QUALITY_SCORE
            
    FROM SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALLS_RAW src
    WHERE src.PROCESSED = FALSE
      AND src._AIRBYTE_DATA IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS tgt
          WHERE tgt.CALL_ID = src._AIRBYTE_DATA:id::VARCHAR
      );
    
    -- Count inserted records
    SELECT COUNT(*) INTO processed_count 
    FROM SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS
    WHERE CREATED_AT >= CURRENT_TIMESTAMP - INTERVAL '1 HOUR';
    
    -- Then update existing records
    UPDATE SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS tgt
    SET 
        CALL_TITLE = src.CALL_TITLE,
        CALL_DATETIME_UTC = src.CALL_DATETIME_UTC,
        CALL_DURATION_SECONDS = src.CALL_DURATION_SECONDS,
        HUBSPOT_DEAL_ID = src.HUBSPOT_DEAL_ID,
        DEAL_STAGE = src.DEAL_STAGE,
        DEAL_VALUE = src.DEAL_VALUE,
        TALK_RATIO = src.TALK_RATIO,
        UPDATED_AT = CURRENT_TIMESTAMP
    FROM (
        SELECT 
            _AIRBYTE_DATA:id::VARCHAR AS CALL_ID,
            _AIRBYTE_DATA:title::VARCHAR AS CALL_TITLE,
            _AIRBYTE_DATA:started::TIMESTAMP_LTZ AS CALL_DATETIME_UTC,
            _AIRBYTE_DATA:duration::NUMBER AS CALL_DURATION_SECONDS,
            COALESCE(_AIRBYTE_DATA:customData.hubspotDealId::VARCHAR, _AIRBYTE_DATA:crmData.dealId::VARCHAR) AS HUBSPOT_DEAL_ID,
            COALESCE(_AIRBYTE_DATA:customData.dealStage::VARCHAR, _AIRBYTE_DATA:crmData.stage::VARCHAR) AS DEAL_STAGE,
            COALESCE(_AIRBYTE_DATA:customData.dealValue::NUMBER, _AIRBYTE_DATA:crmData.value::NUMBER) AS DEAL_VALUE,
            TRY_CAST(_AIRBYTE_DATA:analytics.talkRatio::VARCHAR AS FLOAT) AS TALK_RATIO
        FROM SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALLS_RAW
        WHERE PROCESSED = FALSE AND _AIRBYTE_DATA IS NOT NULL
    ) src
    WHERE tgt.CALL_ID = src.CALL_ID;
    
    -- Mark raw records as processed
    UPDATE SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALLS_RAW 
    SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP
    WHERE PROCESSED = FALSE AND _AIRBYTE_DATA IS NOT NULL;
    
    -- Log completion
    INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_JOB_LOGS 
    (JOB_ID, JOB_NAME, JOB_TYPE, STATUS, END_TIME, RECORDS_PROCESSED, DETAILS)
    VALUES 
    (execution_id, 'TRANSFORM_RAW_GONG_CALLS', 'TRANSFORMATION', 'SUCCESS', CURRENT_TIMESTAMP, 
     processed_count, CONCAT('Successfully processed ', processed_count, ' Gong call records'));
    
    -- Generate result message
    SET result_message = CONCAT('Processed ', processed_count, ' Gong call records successfully');
    
    -- Output the result
    SELECT result_message;
    
    -- Handle errors with TRY-CATCH block in calling code
END;
$$;

-- Transform raw Gong transcripts to structured format
CREATE OR REPLACE PROCEDURE TRANSFORM_RAW_GONG_TRANSCRIPTS()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
    execution_id VARCHAR(255) DEFAULT CONCAT('GONG_TRANSCRIPTS_', TO_VARCHAR(CURRENT_TIMESTAMP, 'YYYYMMDD_HHMMSS'));
BEGIN
    
    -- Log transformation start
    INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_JOB_LOGS 
    (JOB_ID, JOB_NAME, JOB_TYPE, STATUS, START_TIME, DETAILS)
    VALUES 
    (execution_id, 'TRANSFORM_RAW_GONG_TRANSCRIPTS', 'TRANSFORMATION', 'RUNNING', CURRENT_TIMESTAMP, 
     'Starting transformation of raw Gong transcripts to structured format');
    
    -- Transform transcript segments
    INSERT INTO SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS (
        TRANSCRIPT_ID, CALL_ID, SPEAKER_NAME, SPEAKER_EMAIL, SPEAKER_TYPE,
        TRANSCRIPT_TEXT, START_TIME_SECONDS, END_TIME_SECONDS, SEGMENT_DURATION_SECONDS,
        WORD_COUNT, CREATED_AT
    )
    SELECT 
        CONCAT(raw.CALL_ID, '_', segment.INDEX) AS TRANSCRIPT_ID,
        raw.CALL_ID,
        segment.VALUE:speaker.name::VARCHAR AS SPEAKER_NAME,
        segment.VALUE:speaker.emailAddress::VARCHAR AS SPEAKER_EMAIL,
        CASE 
            WHEN segment.VALUE:speaker.isInternal::BOOLEAN = TRUE THEN 'Internal'
            ELSE 'External'
        END AS SPEAKER_TYPE,
        segment.VALUE:text::VARCHAR AS TRANSCRIPT_TEXT,
        segment.VALUE:startTime::NUMBER AS START_TIME_SECONDS,
        segment.VALUE:endTime::NUMBER AS END_TIME_SECONDS,
        (segment.VALUE:endTime::NUMBER - segment.VALUE:startTime::NUMBER) AS SEGMENT_DURATION_SECONDS,
        ARRAY_SIZE(SPLIT(segment.VALUE:text::VARCHAR, ' ')) AS WORD_COUNT,
        CURRENT_TIMESTAMP AS CREATED_AT
    FROM SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALL_TRANSCRIPTS_RAW raw,
         LATERAL FLATTEN(input => raw._AIRBYTE_DATA:transcript.segments) segment
    WHERE raw.PROCESSED = FALSE
      AND raw._AIRBYTE_DATA IS NOT NULL
      AND raw._AIRBYTE_DATA:transcript.segments IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS stg
          WHERE stg.TRANSCRIPT_ID = CONCAT(raw.CALL_ID, '_', segment.INDEX)
      );
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count 
    FROM SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS
    WHERE CREATED_AT >= CURRENT_TIMESTAMP - INTERVAL '1 HOUR';
    
    -- Mark raw records as processed
    UPDATE SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALL_TRANSCRIPTS_RAW 
    SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP
    WHERE PROCESSED = FALSE AND _AIRBYTE_DATA IS NOT NULL;
    
    -- Log completion
    INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_JOB_LOGS 
    (JOB_ID, JOB_NAME, JOB_TYPE, STATUS, END_TIME, RECORDS_PROCESSED, DETAILS)
    VALUES 
    (execution_id, 'TRANSFORM_RAW_GONG_TRANSCRIPTS', 'TRANSFORMATION', 'SUCCESS', CURRENT_TIMESTAMP, 
     processed_count, CONCAT('Successfully processed ', processed_count, ' Gong transcript segments'));
    
    -- Generate result message
    SET result_message = CONCAT('Processed ', processed_count, ' Gong transcript segments successfully');
    
    -- Output the result
    SELECT result_message;
    
    -- Handle errors with TRY-CATCH block in calling code
END;
$$;

-- AI enrichment procedure for Gong calls using Snowflake Cortex
CREATE OR REPLACE PROCEDURE ENRICH_GONG_CALLS_WITH_AI()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
    execution_id VARCHAR(255) DEFAULT CONCAT('GONG_AI_ENRICHMENT_', TO_VARCHAR(CURRENT_TIMESTAMP, 'YYYYMMDD_HHMMSS'));
BEGIN
    
    -- Log AI enrichment start
    INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_JOB_LOGS 
    (JOB_ID, JOB_NAME, JOB_TYPE, STATUS, START_TIME, DETAILS)
    VALUES 
    (execution_id, 'ENRICH_GONG_CALLS_WITH_AI', 'AI_ENRICHMENT', 'RUNNING', CURRENT_TIMESTAMP, 
     'Starting AI enrichment of Gong calls using Snowflake Cortex');
    
    -- Update calls with AI-generated insights
    UPDATE SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS
    SET 
        -- Generate call summary using Cortex Complete
        CALL_SUMMARY = SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-70b',
            CONCAT('Summarize this sales call in 2-3 sentences. Call Title: ', CALL_TITLE, 
                   '. Duration: ', CALL_DURATION_SECONDS/60, ' minutes. ',
                   'Talk Ratio: ', TALK_RATIO*100, '%. ',
                   'Focus on key discussion points, outcomes, and next steps.')
        ),
        
        -- Generate sentiment score using Cortex Sentiment
        SENTIMENT_SCORE = SNOWFLAKE.CORTEX.SENTIMENT(
            CONCAT('Sales call: ', CALL_TITLE, '. Duration: ', CALL_DURATION_SECONDS/60, ' minutes.')
        ),
        
        -- Generate embeddings for semantic search
        AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT_768(
            'e5-base-v2',
            CONCAT('Gong sales call: ', CALL_TITLE, 
                   '. Account: ', COALESCE(ACCOUNT_NAME, 'Unknown'),
                   '. Deal Stage: ', COALESCE(DEAL_STAGE, 'Unknown'),
                   '. Duration: ', CALL_DURATION_SECONDS/60, ' minutes.',
                   '. Participants: ', COALESCE(CONTACT_NAME, 'Unknown'))
        ),
        
        -- Update AI Memory metadata
        AI_MEMORY_METADATA = OBJECT_CONSTRUCT(
            'source_type', 'GONG_CALL',
            'call_id', CALL_ID,
            'processed_date', CURRENT_TIMESTAMP::VARCHAR
        ),
        
        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP,
        PROCESSED_BY_CORTEX = TRUE,
        CORTEX_PROCESSED_AT = CURRENT_TIMESTAMP
        
    WHERE PROCESSED_BY_CORTEX = FALSE
      AND CALL_TITLE IS NOT NULL
      AND CALL_DURATION_SECONDS > 60;
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count 
    FROM SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS
    WHERE PROCESSED_BY_CORTEX = TRUE
    AND CORTEX_PROCESSED_AT >= CURRENT_TIMESTAMP - INTERVAL '1 HOUR';
    
    -- Log completion
    INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_JOB_LOGS 
    (JOB_ID, JOB_NAME, JOB_TYPE, STATUS, END_TIME, RECORDS_PROCESSED, DETAILS)
    VALUES 
    (execution_id, 'ENRICH_GONG_CALLS_WITH_AI', 'AI_ENRICHMENT', 'SUCCESS', CURRENT_TIMESTAMP, 
     processed_count, CONCAT('Successfully AI-enriched ', processed_count, ' Gong calls'));
    
    -- Generate result message
    SET result_message = CONCAT('AI-enriched ', processed_count, ' Gong calls successfully');
    
    -- Output the result
    SELECT result_message;
    
    -- Handle errors with TRY-CATCH block in calling code
END;
$$;

-- ============================================================================
-- SECTION 4: AUTOMATED TASKS AND SCHEDULING
-- ============================================================================

-- Task to transform raw Gong calls every 15 minutes
CREATE OR REPLACE TASK TASK_TRANSFORM_GONG_CALLS
WAREHOUSE = WH_SOPHIA_ETL_TRANSFORM
SCHEDULE = 'USING CRON 0,15,30,45 * * * * UTC'
COMMENT = 'Transform raw Gong calls from API ingestion to structured format'
AS
CALL SOPHIA_AI_DEV.STG_TRANSFORMED.TRANSFORM_RAW_GONG_CALLS();

-- Task to transform raw Gong transcripts every 20 minutes
CREATE OR REPLACE TASK TASK_TRANSFORM_GONG_TRANSCRIPTS
WAREHOUSE = WH_SOPHIA_ETL_TRANSFORM
SCHEDULE = 'USING CRON 5,25,45 * * * * UTC'
COMMENT = 'Transform raw Gong transcripts from API ingestion to structured format'
AS
CALL SOPHIA_AI_DEV.STG_TRANSFORMED.TRANSFORM_RAW_GONG_TRANSCRIPTS();

-- Task to AI-enrich Gong calls every 30 minutes
CREATE OR REPLACE TASK TASK_AI_ENRICH_GONG_CALLS
WAREHOUSE = WH_SOPHIA_ETL_TRANSFORM
SCHEDULE = 'USING CRON 10,40 * * * * UTC'
COMMENT = 'AI-enrich Gong calls using Snowflake Cortex'
AS
CALL SOPHIA_AI_DEV.STG_TRANSFORMED.ENRICH_GONG_CALLS_WITH_AI();

-- ============================================================================
-- SECTION 5: INDEXES AND PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Indexes for STG_GONG_CALLS table
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_CALLS_DATETIME ON SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS(CALL_DATETIME_UTC);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_CALLS_HUBSPOT_DEAL ON SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS(HUBSPOT_DEAL_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_CALLS_PRIMARY_USER ON SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS(PRIMARY_USER_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_CALLS_SENTIMENT ON SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS(SENTIMENT_SCORE);
-- 
-- Indexes for STG_GONG_CALL_TRANSCRIPTS table
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_TRANSCRIPTS_CALL_ID ON SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS(CALL_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_TRANSCRIPTS_SPEAKER ON SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS(SPEAKER_EMAIL);
-- 
-- Indexes for RAW_AIRBYTE tables
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_RAW_GONG_CALLS_PROCESSED ON SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALLS_RAW(PROCESSED);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_RAW_GONG_TRANSCRIPTS_PROCESSED ON SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALL_TRANSCRIPTS_RAW(PROCESSED);
-- 
-- ============================================================================
-- SECTION 6: GRANTS AND PERMISSIONS
-- ============================================================================

-- Grant permissions for ETL role
GRANT USAGE ON SCHEMA SOPHIA_AI_DEV.RAW_AIRBYTE TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;
GRANT USAGE ON SCHEMA SOPHIA_AI_DEV.STG_TRANSFORMED TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;
GRANT ALL ON ALL TABLES IN SCHEMA SOPHIA_AI_DEV.RAW_AIRBYTE TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;
GRANT ALL ON ALL TABLES IN SCHEMA SOPHIA_AI_DEV.STG_TRANSFORMED TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA SOPHIA_AI_DEV.STG_TRANSFORMED TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;

-- Grant read permissions for application role
GRANT USAGE ON SCHEMA SOPHIA_AI_DEV.STG_TRANSFORMED TO ROLE ROLE_SOPHIA_APPLICATION;
GRANT SELECT ON ALL TABLES IN SCHEMA SOPHIA_AI_DEV.STG_TRANSFORMED TO ROLE ROLE_SOPHIA_APPLICATION;

-- ============================================================================
-- DEPLOYMENT COMPLETION MESSAGE
-- ============================================================================

SELECT 'Manus AI Final Gong DDL v2.0 deployment completed successfully!' AS DEPLOYMENT_STATUS,
       CURRENT_TIMESTAMP() AS DEPLOYMENT_TIMESTAMP,
       'All schemas, tables, procedures, tasks, and indexes created' AS DETAILS;
