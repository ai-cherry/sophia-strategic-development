-- =====================================================================
-- Snowflake Gong Data Schema and Transformation Pipeline
-- =====================================================================
--
-- This script creates the complete data pipeline for Gong call data in Snowflake:
-- 1. Raw data tables (VARIANT columns for JSON storage)
-- 2. Structured staging tables (STG_*)
-- 3. Transformation tasks for processing raw data
-- 4. Integration with HubSpot Secure Data Share
-- 5. Snowflake Cortex AI processing examples
--
-- Usage:
--   Execute sections in order, or use Snowflake Tasks for automated processing
-- =====================================================================

-- Set context
USE DATABASE SOPHIA_AI;
CREATE SCHEMA IF NOT EXISTS GONG_DATA;
USE SCHEMA GONG_DATA;

-- =====================================================================
-- 1. RAW DATA TABLES (Landing Zone)
-- =====================================================================

-- Raw calls data from Gong API (JSON/VARIANT storage)
CREATE TABLE IF NOT EXISTS GONG_CALLS_RAW (
    CALL_ID VARCHAR(255) PRIMARY KEY,
    RAW_DATA VARIANT NOT NULL,
    INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CORRELATION_ID VARCHAR(255),
    PROCESSED BOOLEAN DEFAULT FALSE,
    PROCESSED_AT TIMESTAMP_LTZ,
    PROCESSING_ERROR VARCHAR(16777216)
);

-- Raw transcript data from Gong API
CREATE TABLE IF NOT EXISTS GONG_CALL_TRANSCRIPTS_RAW (
    CALL_ID VARCHAR(255) PRIMARY KEY,
    TRANSCRIPT_DATA VARIANT NOT NULL,
    INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CORRELATION_ID VARCHAR(255),
    PROCESSED BOOLEAN DEFAULT FALSE,
    PROCESSED_AT TIMESTAMP_LTZ,
    PROCESSING_ERROR VARCHAR(16777216)
);

-- Ingestion state tracking
CREATE TABLE IF NOT EXISTS GONG_INGESTION_STATE (
    ID NUMBER IDENTITY PRIMARY KEY,
    LAST_SYNC_TIMESTAMP TIMESTAMP_LTZ,
    LAST_CALL_ID VARCHAR(255),
    TOTAL_CALLS_PROCESSED NUMBER,
    SYNC_MODE VARCHAR(50),
    CORRELATION_ID VARCHAR(255),
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================================
-- 2. STRUCTURED STAGING TABLES (Transformed Data)
-- =====================================================================

-- Structured calls table with key business fields
CREATE TABLE IF NOT EXISTS STG_GONG_CALLS (
    CALL_ID VARCHAR(255) PRIMARY KEY,
    CALL_TITLE VARCHAR(500),
    CALL_DATETIME_UTC TIMESTAMP_LTZ,
    CALL_DURATION_SECONDS NUMBER,
    CALL_DIRECTION VARCHAR(50), -- 'Inbound', 'Outbound'
    CALL_SYSTEM VARCHAR(100),
    CALL_SCOPE VARCHAR(100),
    CALL_MEDIA VARCHAR(50), -- 'Video', 'Audio'
    CALL_LANGUAGE VARCHAR(10),
    CALL_URL VARCHAR(1000),

    -- Primary user/owner
    PRIMARY_USER_ID VARCHAR(255),
    PRIMARY_USER_EMAIL VARCHAR(255),
    PRIMARY_USER_NAME VARCHAR(255),

    -- CRM Integration fields
    HUBSPOT_DEAL_ID VARCHAR(255), -- Key for joining with HubSpot data
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

    -- AI-generated insights (to be populated by Cortex)
    SENTIMENT_SCORE FLOAT, -- From SNOWFLAKE.CORTEX.SENTIMENT()
    CALL_SUMMARY VARCHAR(16777216), -- From SNOWFLAKE.CORTEX.SUMMARIZE()
    KEY_TOPICS VARIANT, -- JSON array of topics
    RISK_INDICATORS VARIANT, -- JSON array of risk signals
    NEXT_STEPS VARIANT, -- JSON array of action items

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
    CORTEX_PROCESSED_AT TIMESTAMP_LTZ,

    -- Indexes for performance
    INDEX IX_CALL_DATETIME (CALL_DATETIME_UTC),
    INDEX IX_HUBSPOT_DEAL (HUBSPOT_DEAL_ID),
    INDEX IX_PRIMARY_USER (PRIMARY_USER_ID)
);

-- Call participants table
CREATE TABLE IF NOT EXISTS STG_GONG_CALL_PARTICIPANTS (
    PARTICIPANT_ID VARCHAR(255) PRIMARY KEY,
    CALL_ID VARCHAR(255) NOT NULL,
    USER_ID VARCHAR(255),
    EMAIL_ADDRESS VARCHAR(255),
    FULL_NAME VARCHAR(255),
    PARTICIPANT_TYPE VARCHAR(50), -- 'Internal', 'External', 'Customer'
    ROLE VARCHAR(100),
    COMPANY_NAME VARCHAR(500),
    TALK_TIME_SECONDS NUMBER,
    TALK_RATIO FLOAT,

    -- CRM linking
    HUBSPOT_CONTACT_ID VARCHAR(255),
    CRM_CONTACT_ID VARCHAR(255),

    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (CALL_ID) REFERENCES STG_GONG_CALLS(CALL_ID),
    INDEX IX_CALL_PARTICIPANT (CALL_ID, PARTICIPANT_TYPE)
);

-- Call transcripts with speaker attribution
CREATE TABLE IF NOT EXISTS STG_GONG_CALL_TRANSCRIPTS (
    TRANSCRIPT_ID VARCHAR(255) PRIMARY KEY,
    CALL_ID VARCHAR(255) NOT NULL,
    SPEAKER_NAME VARCHAR(255),
    SPEAKER_EMAIL VARCHAR(255),
    SPEAKER_TYPE VARCHAR(50), -- 'Internal', 'External'
    TRANSCRIPT_TEXT VARCHAR(16777216),
    START_TIME_SECONDS NUMBER,
    END_TIME_SECONDS NUMBER,
    SEGMENT_DURATION_SECONDS NUMBER,
    WORD_COUNT NUMBER,

    -- AI processing results (Cortex)
    SEGMENT_SENTIMENT FLOAT, -- SNOWFLAKE.CORTEX.SENTIMENT()
    SEGMENT_SUMMARY VARCHAR(4000), -- SNOWFLAKE.CORTEX.SUMMARIZE()
    EXTRACTED_ENTITIES VARIANT, -- JSON array of entities
    KEY_PHRASES VARIANT, -- JSON array of key phrases

    -- Vector embedding for semantic search
    TRANSCRIPT_EMBEDDING VECTOR(FLOAT, 1536), -- Cortex embedding

    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (CALL_ID) REFERENCES STG_GONG_CALLS(CALL_ID),
    INDEX IX_CALL_TRANSCRIPT (CALL_ID),
    INDEX IX_SPEAKER (SPEAKER_EMAIL)
);

-- Call topics and themes
CREATE TABLE IF NOT EXISTS STG_GONG_CALL_TOPICS (
    TOPIC_ID VARCHAR(255) PRIMARY KEY,
    CALL_ID VARCHAR(255) NOT NULL,
    TOPIC_NAME VARCHAR(255),
    TOPIC_CATEGORY VARCHAR(100), -- 'Product', 'Pricing', 'Competition', 'Timeline'
    CONFIDENCE_SCORE FLOAT,
    MENTION_COUNT NUMBER,
    TOTAL_DURATION_SECONDS NUMBER,

    -- Topic context
    FIRST_MENTIONED_AT_SECONDS NUMBER,
    LAST_MENTIONED_AT_SECONDS NUMBER,
    MENTIONED_BY_SPEAKER VARCHAR(255),

    -- Business impact
    IMPACT_SCORE FLOAT, -- AI-generated impact assessment
    SENTIMENT_CONTEXT VARCHAR(50), -- 'Positive', 'Negative', 'Neutral'

    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (CALL_ID) REFERENCES STG_GONG_CALLS(CALL_ID),
    INDEX IX_CALL_TOPIC (CALL_ID, TOPIC_CATEGORY)
);

-- =====================================================================
-- 3. DATA TRANSFORMATION LOGIC (Raw to Structured)
-- =====================================================================

-- Transform raw calls to structured format
CREATE OR REPLACE PROCEDURE TRANSFORM_RAW_CALLS()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    error_count NUMBER DEFAULT 0;
BEGIN

    -- Insert/Update structured calls from raw data
    MERGE INTO STG_GONG_CALLS AS target
    USING (
        SELECT
            RAW_DATA:id::VARCHAR AS CALL_ID,
            RAW_DATA:title::VARCHAR AS CALL_TITLE,
            RAW_DATA:started::TIMESTAMP_LTZ AS CALL_DATETIME_UTC,
            RAW_DATA:duration::NUMBER AS CALL_DURATION_SECONDS,
            RAW_DATA:direction::VARCHAR AS CALL_DIRECTION,
            RAW_DATA:system::VARCHAR AS CALL_SYSTEM,
            RAW_DATA:scope::VARCHAR AS CALL_SCOPE,
            RAW_DATA:media::VARCHAR AS CALL_MEDIA,
            RAW_DATA:language::VARCHAR AS CALL_LANGUAGE,
            RAW_DATA:url::VARCHAR AS CALL_URL,

            -- Primary user extraction
            RAW_DATA:primaryUserId::VARCHAR AS PRIMARY_USER_ID,
            RAW_DATA:primaryUser.emailAddress::VARCHAR AS PRIMARY_USER_EMAIL,
            RAW_DATA:primaryUser.firstName::VARCHAR || ' ' || RAW_DATA:primaryUser.lastName::VARCHAR AS PRIMARY_USER_NAME,

            -- CRM data extraction (nested JSON)
            RAW_DATA:customData.hubspotDealId::VARCHAR AS HUBSPOT_DEAL_ID,
            RAW_DATA:customData.hubspotContactId::VARCHAR AS HUBSPOT_CONTACT_ID,
            RAW_DATA:customData.hubspotCompanyId::VARCHAR AS HUBSPOT_COMPANY_ID,
            RAW_DATA:customData.opportunityId::VARCHAR AS CRM_OPPORTUNITY_ID,
            RAW_DATA:customData.accountId::VARCHAR AS CRM_ACCOUNT_ID,

            -- Business context
            RAW_DATA:customData.dealStage::VARCHAR AS DEAL_STAGE,
            RAW_DATA:customData.dealValue::NUMBER AS DEAL_VALUE,
            RAW_DATA:customData.accountName::VARCHAR AS ACCOUNT_NAME,
            RAW_DATA:customData.contactName::VARCHAR AS CONTACT_NAME,

            -- Call metrics (if available)
            RAW_DATA:analytics.talkRatio::FLOAT AS TALK_RATIO,
            RAW_DATA:analytics.longestMonologue::NUMBER AS LONGEST_MONOLOGUE_SECONDS,
            RAW_DATA:analytics.interactivity::FLOAT AS INTERACTIVITY_SCORE,
            RAW_DATA:analytics.questionsAsked::NUMBER AS QUESTIONS_ASKED_COUNT,

            CURRENT_TIMESTAMP() AS UPDATED_AT

        FROM GONG_CALLS_RAW
        WHERE PROCESSED = FALSE
    ) AS source
    ON target.CALL_ID = source.CALL_ID
    WHEN MATCHED THEN UPDATE SET
        CALL_TITLE = source.CALL_TITLE,
        CALL_DATETIME_UTC = source.CALL_DATETIME_UTC,
        CALL_DURATION_SECONDS = source.CALL_DURATION_SECONDS,
        CALL_DIRECTION = source.CALL_DIRECTION,
        HUBSPOT_DEAL_ID = source.HUBSPOT_DEAL_ID,
        HUBSPOT_CONTACT_ID = source.HUBSPOT_CONTACT_ID,
        DEAL_STAGE = source.DEAL_STAGE,
        DEAL_VALUE = source.DEAL_VALUE,
        TALK_RATIO = source.TALK_RATIO,
        UPDATED_AT = source.UPDATED_AT
    WHEN NOT MATCHED THEN INSERT (
        CALL_ID, CALL_TITLE, CALL_DATETIME_UTC, CALL_DURATION_SECONDS,
        CALL_DIRECTION, CALL_SYSTEM, CALL_SCOPE, CALL_MEDIA, CALL_LANGUAGE, CALL_URL,
        PRIMARY_USER_ID, PRIMARY_USER_EMAIL, PRIMARY_USER_NAME,
        HUBSPOT_DEAL_ID, HUBSPOT_CONTACT_ID, HUBSPOT_COMPANY_ID,
        CRM_OPPORTUNITY_ID, CRM_ACCOUNT_ID,
        DEAL_STAGE, DEAL_VALUE, ACCOUNT_NAME, CONTACT_NAME,
        TALK_RATIO, LONGEST_MONOLOGUE_SECONDS, INTERACTIVITY_SCORE, QUESTIONS_ASKED_COUNT,
        UPDATED_AT
    ) VALUES (
        source.CALL_ID, source.CALL_TITLE, source.CALL_DATETIME_UTC, source.CALL_DURATION_SECONDS,
        source.CALL_DIRECTION, source.CALL_SYSTEM, source.CALL_SCOPE, source.CALL_MEDIA, source.CALL_LANGUAGE, source.CALL_URL,
        source.PRIMARY_USER_ID, source.PRIMARY_USER_EMAIL, source.PRIMARY_USER_NAME,
        source.HUBSPOT_DEAL_ID, source.HUBSPOT_CONTACT_ID, source.HUBSPOT_COMPANY_ID,
        source.CRM_OPPORTUNITY_ID, source.CRM_ACCOUNT_ID,
        source.DEAL_STAGE, source.DEAL_VALUE, source.ACCOUNT_NAME, source.CONTACT_NAME,
        source.TALK_RATIO, source.LONGEST_MONOLOGUE_SECONDS, source.INTERACTIVITY_SCORE, source.QUESTIONS_ASKED_COUNT,
        source.UPDATED_AT
    );

    GET DIAGNOSTICS processed_count = ROW_COUNT;

    -- Mark raw records as processed
    UPDATE GONG_CALLS_RAW
    SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP()
    WHERE PROCESSED = FALSE;

    RETURN 'Processed ' || processed_count || ' call records';

EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error processing calls: ' || SQLERRM;
END;
$$;

-- Transform raw transcripts to structured format
CREATE OR REPLACE PROCEDURE TRANSFORM_RAW_TRANSCRIPTS()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
BEGIN

    -- Insert transcript segments from raw data
    INSERT INTO STG_GONG_CALL_TRANSCRIPTS (
        TRANSCRIPT_ID,
        CALL_ID,
        SPEAKER_NAME,
        SPEAKER_EMAIL,
        SPEAKER_TYPE,
        TRANSCRIPT_TEXT,
        START_TIME_SECONDS,
        END_TIME_SECONDS,
        SEGMENT_DURATION_SECONDS,
        WORD_COUNT
    )
    SELECT
        CALL_ID || '_' || segment.index AS TRANSCRIPT_ID,
        CALL_ID,
        segment.value:speakerName::VARCHAR AS SPEAKER_NAME,
        segment.value:speakerEmail::VARCHAR AS SPEAKER_EMAIL,
        CASE
            WHEN segment.value:speakerEmail LIKE '%@yourdomain.com' THEN 'Internal'
            ELSE 'External'
        END AS SPEAKER_TYPE,
        segment.value:text::VARCHAR AS TRANSCRIPT_TEXT,
        segment.value:startTime::NUMBER AS START_TIME_SECONDS,
        segment.value:endTime::NUMBER AS END_TIME_SECONDS,
        (segment.value:endTime::NUMBER - segment.value:startTime::NUMBER) AS SEGMENT_DURATION_SECONDS,
        ARRAY_SIZE(SPLIT(segment.value:text::VARCHAR, ' ')) AS WORD_COUNT
    FROM GONG_CALL_TRANSCRIPTS_RAW,
    LATERAL FLATTEN(input => TRANSCRIPT_DATA:transcript.segments) AS segment
    WHERE PROCESSED = FALSE
    AND TRANSCRIPT_DATA:transcript IS NOT NULL;

    GET DIAGNOSTICS processed_count = ROW_COUNT;

    -- Mark raw transcripts as processed
    UPDATE GONG_CALL_TRANSCRIPTS_RAW
    SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP()
    WHERE PROCESSED = FALSE;

    RETURN 'Processed ' || processed_count || ' transcript segments';

EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error processing transcripts: ' || SQLERRM;
END;
$$;

-- =====================================================================
-- 4. SNOWFLAKE CORTEX AI PROCESSING PROCEDURES
-- =====================================================================

-- Generate AI insights using Snowflake Cortex for calls
CREATE OR REPLACE PROCEDURE PROCESS_CALLS_WITH_CORTEX()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
BEGIN

    -- Update calls with Cortex AI analysis
    UPDATE STG_GONG_CALLS
    SET
        -- Sentiment analysis on call title and any available text
        SENTIMENT_SCORE = SNOWFLAKE.CORTEX.SENTIMENT(
            COALESCE(CALL_TITLE, '') || ' ' || COALESCE(ACCOUNT_NAME, '') || ' ' || COALESCE(DEAL_STAGE, '')
        ),

        -- Summary generation (if we have enough text context)
        CALL_SUMMARY = CASE
            WHEN LENGTH(CALL_TITLE || COALESCE(ACCOUNT_NAME, '') || COALESCE(DEAL_STAGE, '')) > 50 THEN
                SNOWFLAKE.CORTEX.SUMMARIZE(
                    'Call: ' || CALL_TITLE ||
                    CASE WHEN ACCOUNT_NAME IS NOT NULL THEN '. Account: ' || ACCOUNT_NAME ELSE '' END ||
                    CASE WHEN DEAL_STAGE IS NOT NULL THEN '. Stage: ' || DEAL_STAGE ELSE '' END ||
                    CASE WHEN DEAL_VALUE IS NOT NULL THEN '. Value: $' || DEAL_VALUE ELSE '' END,
                    200
                )
            ELSE NULL
        END,

        PROCESSED_BY_CORTEX = TRUE,
        CORTEX_PROCESSED_AT = CURRENT_TIMESTAMP(),
        UPDATED_AT = CURRENT_TIMESTAMP()

    WHERE PROCESSED_BY_CORTEX = FALSE
    AND CALL_TITLE IS NOT NULL;

    GET DIAGNOSTICS processed_count = ROW_COUNT;

    RETURN 'Processed ' || processed_count || ' calls with Cortex AI';

EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error processing calls with Cortex: ' || SQLERRM;
END;
$$;

-- Process transcripts with Cortex AI (sentiment, summarization, embeddings)
CREATE OR REPLACE PROCEDURE PROCESS_TRANSCRIPTS_WITH_CORTEX()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
BEGIN

    -- Update transcript segments with Cortex analysis
    UPDATE STG_GONG_CALL_TRANSCRIPTS
    SET
        -- Sentiment analysis on transcript text
        SEGMENT_SENTIMENT = SNOWFLAKE.CORTEX.SENTIMENT(TRANSCRIPT_TEXT),

        -- Summarization for longer segments
        SEGMENT_SUMMARY = CASE
            WHEN WORD_COUNT > 20 THEN
                SNOWFLAKE.CORTEX.SUMMARIZE(TRANSCRIPT_TEXT, 100)
            ELSE NULL
        END,

        -- Generate embeddings for semantic search
        TRANSCRIPT_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', TRANSCRIPT_TEXT),

        PROCESSED_BY_CORTEX = TRUE

    WHERE PROCESSED_BY_CORTEX = FALSE
    AND TRANSCRIPT_TEXT IS NOT NULL
    AND LENGTH(TRANSCRIPT_TEXT) > 10;

    GET DIAGNOSTICS processed_count = ROW_COUNT;

    RETURN 'Processed ' || processed_count || ' transcript segments with Cortex AI';

EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error processing transcripts with Cortex: ' || SQLERRM;
END;
$$;

-- =====================================================================
-- 5. HUBSPOT INTEGRATION VIEWS (Data Joining Examples)
-- =====================================================================

-- Enriched calls view joining Gong calls with HubSpot data
CREATE OR REPLACE VIEW VW_ENRICHED_GONG_CALLS AS
SELECT
    -- Gong call data
    gc.CALL_ID,
    gc.CALL_TITLE,
    gc.CALL_DATETIME_UTC,
    gc.CALL_DURATION_SECONDS,
    gc.CALL_DIRECTION,
    gc.PRIMARY_USER_NAME,
    gc.SENTIMENT_SCORE,
    gc.CALL_SUMMARY,
    gc.TALK_RATIO,

    -- HubSpot deal data (from Secure Data Share)
    hd.DEAL_NAME,
    hd.DEAL_STAGE,
    hd.DEAL_AMOUNT,
    hd.CLOSE_DATE,
    hd.PIPELINE_NAME,
    hd.DEAL_OWNER,

    -- HubSpot contact data
    hc.FIRST_NAME,
    hc.LAST_NAME,
    hc.EMAIL,
    hc.COMPANY_NAME,
    hc.JOB_TITLE,
    hc.LIFECYCLE_STAGE,

    -- HubSpot company data
    hco.COMPANY_NAME AS HUBSPOT_COMPANY_NAME,
    hco.INDUSTRY,
    hco.ANNUAL_REVENUE,
    hco.NUMBER_OF_EMPLOYEES,

    -- Calculated fields
    DATEDIFF('day', gc.CALL_DATETIME_UTC, hd.CLOSE_DATE) AS DAYS_TO_CLOSE,

    CASE
        WHEN gc.SENTIMENT_SCORE > 0.7 THEN 'Very Positive'
        WHEN gc.SENTIMENT_SCORE > 0.3 THEN 'Positive'
        WHEN gc.SENTIMENT_SCORE > -0.3 THEN 'Neutral'
        WHEN gc.SENTIMENT_SCORE > -0.7 THEN 'Negative'
        ELSE 'Very Negative'
    END AS SENTIMENT_CATEGORY,

    CASE
        WHEN hd.DEAL_STAGE IN ('Closed Won', 'Closed - Won') THEN 'Won'
        WHEN hd.DEAL_STAGE IN ('Closed Lost', 'Closed - Lost') THEN 'Lost'
        ELSE 'In Progress'
    END AS DEAL_OUTCOME

FROM STG_GONG_CALLS gc

-- Join with HubSpot Secure Data Share tables
LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.DEALS hd
    ON gc.HUBSPOT_DEAL_ID = hd.DEAL_ID

LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.CONTACTS hc
    ON gc.HUBSPOT_CONTACT_ID = hc.CONTACT_ID

LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.COMPANIES hco
    ON gc.HUBSPOT_COMPANY_ID = hco.COMPANY_ID

WHERE gc.CALL_DATETIME_UTC >= DATEADD('month', -6, CURRENT_DATE()); -- Last 6 months

-- Sales performance view combining Gong and HubSpot data
CREATE OR REPLACE VIEW VW_SALES_PERFORMANCE_ANALYSIS AS
SELECT
    gc.PRIMARY_USER_NAME AS SALES_REP,
    DATE_TRUNC('month', gc.CALL_DATETIME_UTC) AS CALL_MONTH,

    -- Call metrics
    COUNT(*) AS TOTAL_CALLS,
    AVG(gc.CALL_DURATION_SECONDS) AS AVG_CALL_DURATION,
    AVG(gc.TALK_RATIO) AS AVG_TALK_RATIO,
    AVG(gc.SENTIMENT_SCORE) AS AVG_SENTIMENT,

    -- Deal metrics
    COUNT(DISTINCT gc.HUBSPOT_DEAL_ID) AS UNIQUE_DEALS_DISCUSSED,
    SUM(CASE WHEN hd.DEAL_STAGE IN ('Closed Won', 'Closed - Won') THEN 1 ELSE 0 END) AS DEALS_WON,
    SUM(CASE WHEN hd.DEAL_STAGE IN ('Closed Won', 'Closed - Won') THEN hd.DEAL_AMOUNT ELSE 0 END) AS REVENUE_WON,

    -- Performance indicators
    CASE
        WHEN AVG(gc.SENTIMENT_SCORE) > 0.5 AND AVG(gc.TALK_RATIO) BETWEEN 0.3 AND 0.7 THEN 'High Performer'
        WHEN AVG(gc.SENTIMENT_SCORE) > 0.2 AND AVG(gc.TALK_RATIO) BETWEEN 0.2 AND 0.8 THEN 'Good Performer'
        ELSE 'Needs Coaching'
    END AS PERFORMANCE_CATEGORY

FROM STG_GONG_CALLS gc
LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.DEALS hd
    ON gc.HUBSPOT_DEAL_ID = hd.DEAL_ID

WHERE gc.CALL_DATETIME_UTC >= DATEADD('month', -12, CURRENT_DATE())

GROUP BY
    gc.PRIMARY_USER_NAME,
    DATE_TRUNC('month', gc.CALL_DATETIME_UTC)

ORDER BY
    CALL_MONTH DESC,
    TOTAL_CALLS DESC;

-- =====================================================================
-- 6. AUTOMATED TASKS FOR DATA PIPELINE
-- =====================================================================

-- Task to transform raw calls data every 15 minutes
CREATE OR REPLACE TASK TASK_TRANSFORM_GONG_CALLS
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0,15,30,45 * * * * UTC'
    COMMENT = 'Transform raw Gong calls data to structured format'
AS
    CALL TRANSFORM_RAW_CALLS();

-- Task to transform raw transcripts every 30 minutes
CREATE OR REPLACE TASK TASK_TRANSFORM_GONG_TRANSCRIPTS
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0,30 * * * * UTC'
    COMMENT = 'Transform raw Gong transcript data to structured format'
AS
    CALL TRANSFORM_RAW_TRANSCRIPTS();

-- Task to process calls with Cortex AI every hour
CREATE OR REPLACE TASK TASK_PROCESS_CALLS_CORTEX
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 * * * * UTC'
    COMMENT = 'Process Gong calls with Snowflake Cortex AI'
AS
    CALL PROCESS_CALLS_WITH_CORTEX();

-- Task to process transcripts with Cortex AI every 2 hours
CREATE OR REPLACE TASK TASK_PROCESS_TRANSCRIPTS_CORTEX
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 */2 * * * UTC'
    COMMENT = 'Process Gong transcripts with Snowflake Cortex AI'
AS
    CALL PROCESS_TRANSCRIPTS_WITH_CORTEX();

-- =====================================================================
-- 7. EXAMPLE QUERIES FOR SALES COACH AND CALL ANALYSIS AGENTS
-- =====================================================================

-- Example: Get recent calls with sentiment analysis for coaching
/*
SELECT
    CALL_ID,
    CALL_TITLE,
    PRIMARY_USER_NAME,
    CALL_DATETIME_UTC,
    SENTIMENT_SCORE,
    SENTIMENT_CATEGORY,
    TALK_RATIO,
    DEAL_STAGE,
    DEAL_AMOUNT
FROM VW_ENRICHED_GONG_CALLS
WHERE CALL_DATETIME_UTC >= DATEADD('day', -7, CURRENT_DATE())
AND (SENTIMENT_SCORE < 0.3 OR TALK_RATIO > 0.8)
ORDER BY CALL_DATETIME_UTC DESC;
*/

-- Example: Semantic search for similar call topics using vector embeddings
/*
WITH query_embedding AS (
    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 'pricing objection budget concerns') AS query_vector
)
SELECT
    t.CALL_ID,
    t.SPEAKER_NAME,
    t.TRANSCRIPT_TEXT,
    t.SEGMENT_SENTIMENT,
    VECTOR_COSINE_SIMILARITY(q.query_vector, t.TRANSCRIPT_EMBEDDING) AS similarity_score
FROM STG_GONG_CALL_TRANSCRIPTS t
CROSS JOIN query_embedding q
WHERE VECTOR_COSINE_SIMILARITY(q.query_vector, t.TRANSCRIPT_EMBEDDING) > 0.7
ORDER BY similarity_score DESC
LIMIT 10;
*/

-- Example: Call analysis with HubSpot context for agent processing
/*
SELECT
    gc.CALL_ID,
    gc.CALL_SUMMARY,
    gc.SENTIMENT_SCORE,
    hd.DEAL_NAME,
    hd.DEAL_STAGE,
    hd.DEAL_AMOUNT,
    hc.COMPANY_NAME,

    -- Aggregate transcript insights
    COUNT(t.TRANSCRIPT_ID) AS TRANSCRIPT_SEGMENTS,
    AVG(t.SEGMENT_SENTIMENT) AS AVG_TRANSCRIPT_SENTIMENT,
    STRING_AGG(
        CASE WHEN t.SEGMENT_SENTIMENT < 0.2 THEN t.TRANSCRIPT_TEXT ELSE NULL END,
        ' | '
    ) AS NEGATIVE_SEGMENTS

FROM STG_GONG_CALLS gc
LEFT JOIN STG_GONG_CALL_TRANSCRIPTS t ON gc.CALL_ID = t.CALL_ID
LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.DEALS hd ON gc.HUBSPOT_DEAL_ID = hd.DEAL_ID
LEFT JOIN HUBSPOT_SECURE_SHARE.PUBLIC.CONTACTS hc ON gc.HUBSPOT_CONTACT_ID = hc.CONTACT_ID

WHERE gc.CALL_DATETIME_UTC >= DATEADD('day', -1, CURRENT_DATE())

GROUP BY
    gc.CALL_ID, gc.CALL_SUMMARY, gc.SENTIMENT_SCORE,
    hd.DEAL_NAME, hd.DEAL_STAGE, hd.DEAL_AMOUNT, hc.COMPANY_NAME

ORDER BY gc.CALL_DATETIME_UTC DESC;
*/

-- =====================================================================
-- 8. TASK MANAGEMENT (Enable/Start Tasks)
-- =====================================================================

-- Enable and start the transformation tasks
-- Note: Execute these manually or via automation after initial setup

/*
-- Start the data transformation pipeline
ALTER TASK TASK_TRANSFORM_GONG_CALLS RESUME;
ALTER TASK TASK_TRANSFORM_GONG_TRANSCRIPTS RESUME;
ALTER TASK TASK_PROCESS_CALLS_CORTEX RESUME;
ALTER TASK TASK_PROCESS_TRANSCRIPTS_CORTEX RESUME;

-- Check task status
SHOW TASKS LIKE 'TASK_%GONG%';

-- Monitor task execution history
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    QUERY_START_TIME,
    COMPLETED_TIME,
    RETURN_VALUE,
    ERROR_CODE,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'TASK_%GONG%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 20;
*/
