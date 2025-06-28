-- =====================================================================
-- STG_TRANSFORMED Schema - Enhanced Data Pipeline
-- =====================================================================
-- 
-- This script creates the STG_TRANSFORMED schema for structured business data
-- with AI Memory integration and Snowflake Cortex capabilities.
-- 
-- Features:
-- - Enhanced Gong call data with AI Memory columns
-- - HubSpot data views and materialized tables
-- - Cortex AI processing integration
-- - Vector embeddings for semantic search
-- 
-- Usage: Execute in SOPHIA_AI_DEV database
-- =====================================================================

-- Set context for DEV environment
USE DATABASE SOPHIA_AI_DEV;
CREATE SCHEMA IF NOT EXISTS STG_TRANSFORMED;
USE SCHEMA STG_TRANSFORMED;

-- =====================================================================
-- 1. ENHANCED GONG TABLES WITH AI MEMORY COLUMNS
-- =====================================================================

-- Enhanced Gong calls table with AI Memory integration
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
    
    -- AI-generated insights (Cortex)
    SENTIMENT_SCORE FLOAT, -- From SNOWFLAKE.CORTEX.SENTIMENT()
    CALL_SUMMARY VARCHAR(16777216), -- From SNOWFLAKE.CORTEX.SUMMARIZE()
    KEY_TOPICS VARIANT, -- JSON array of topics
    RISK_INDICATORS VARIANT, -- JSON array of risk signals
    NEXT_STEPS VARIANT, -- JSON array of action items
    
    -- AI Memory columns for semantic search and storage
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768), -- Cortex embedding for semantic search
    AI_MEMORY_METADATA VARCHAR(16777216), -- JSON metadata for AI Memory
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ, -- Last AI Memory update timestamp
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
    CORTEX_PROCESSED_AT TIMESTAMP_LTZ
);

-- Enhanced call transcripts with AI Memory columns
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
    
    -- AI Memory columns for semantic search
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768), -- Cortex embedding for semantic search
    AI_MEMORY_METADATA VARCHAR(16777216), -- JSON metadata for AI Memory
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ, -- Last AI Memory update timestamp
    
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (CALL_ID) REFERENCES STG_GONG_CALLS(CALL_ID)
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
    
    FOREIGN KEY (CALL_ID) REFERENCES STG_GONG_CALLS(CALL_ID)
);

-- =====================================================================
-- 2. HUBSPOT DATA VIEWS AND MATERIALIZED TABLES
-- =====================================================================

-- HubSpot Deals view (from Secure Data Share)
CREATE OR REPLACE VIEW V_STG_HUBSPOT_DEALS AS
SELECT 
    DEAL_ID,
    DEAL_NAME,
    DEAL_STAGE,
    DEAL_AMOUNT,
    CLOSE_DATE,
    CREATE_DATE,
    PIPELINE_NAME,
    DEAL_OWNER,
    DEAL_OWNER_EMAIL,
    DEAL_SOURCE,
    DEAL_TYPE,
    
    -- Contact and company references
    ASSOCIATED_CONTACT_ID,
    ASSOCIATED_COMPANY_ID,
    
    -- Calculated fields
    DATEDIFF('day', CREATE_DATE, CURRENT_DATE()) AS DAYS_SINCE_CREATED,
    DATEDIFF('day', CURRENT_DATE(), CLOSE_DATE) AS DAYS_TO_CLOSE,
    
    -- Deal health indicators
    CASE 
        WHEN DEAL_STAGE IN ('Closed Won', 'Closed - Won') THEN 'Won'
        WHEN DEAL_STAGE IN ('Closed Lost', 'Closed - Lost') THEN 'Lost'
        WHEN CLOSE_DATE < CURRENT_DATE() THEN 'Overdue'
        WHEN DATEDIFF('day', CURRENT_DATE(), CLOSE_DATE) <= 7 THEN 'Closing Soon'
        ELSE 'In Progress'
    END AS DEAL_STATUS,
    
    CURRENT_TIMESTAMP() AS LAST_REFRESHED
    
FROM HUBSPOT_SECURE_SHARE_DB_NAME.V2_LIVE.DEALS
WHERE DEAL_ID IS NOT NULL;

-- HubSpot Contacts view (from Secure Data Share)
CREATE OR REPLACE VIEW V_STG_HUBSPOT_CONTACTS AS
SELECT 
    CONTACT_ID,
    FIRST_NAME,
    LAST_NAME,
    EMAIL,
    PHONE,
    COMPANY_NAME,
    JOB_TITLE,
    LIFECYCLE_STAGE,
    LEAD_STATUS,
    
    -- Company reference
    ASSOCIATED_COMPANY_ID,
    
    -- Contact activity
    CREATE_DATE,
    LAST_MODIFIED_DATE,
    LAST_ACTIVITY_DATE,
    
    -- Calculated fields
    FIRST_NAME || ' ' || LAST_NAME AS FULL_NAME,
    DATEDIFF('day', CREATE_DATE, CURRENT_DATE()) AS DAYS_SINCE_CREATED,
    DATEDIFF('day', LAST_ACTIVITY_DATE, CURRENT_DATE()) AS DAYS_SINCE_LAST_ACTIVITY,
    
    CURRENT_TIMESTAMP() AS LAST_REFRESHED
    
FROM HUBSPOT_SECURE_SHARE_DB_NAME.V2_LIVE.CONTACTS
WHERE CONTACT_ID IS NOT NULL;

-- HubSpot Companies view (from Secure Data Share)
CREATE OR REPLACE VIEW V_STG_HUBSPOT_COMPANIES AS
SELECT 
    COMPANY_ID,
    COMPANY_NAME,
    DOMAIN,
    INDUSTRY,
    ANNUAL_REVENUE,
    NUMBER_OF_EMPLOYEES,
    COMPANY_TYPE,
    COUNTRY,
    STATE,
    CITY,
    
    -- Company activity
    CREATE_DATE,
    LAST_MODIFIED_DATE,
    LAST_ACTIVITY_DATE,
    
    -- Calculated fields
    CASE 
        WHEN NUMBER_OF_EMPLOYEES >= 1000 THEN 'Enterprise'
        WHEN NUMBER_OF_EMPLOYEES >= 100 THEN 'Mid-Market'
        WHEN NUMBER_OF_EMPLOYEES >= 10 THEN 'Small Business'
        ELSE 'Startup'
    END AS COMPANY_SIZE_CATEGORY,
    
    CASE 
        WHEN ANNUAL_REVENUE >= 100000000 THEN 'Large'
        WHEN ANNUAL_REVENUE >= 10000000 THEN 'Medium'
        WHEN ANNUAL_REVENUE >= 1000000 THEN 'Small'
        ELSE 'Startup'
    END AS REVENUE_CATEGORY,
    
    CURRENT_TIMESTAMP() AS LAST_REFRESHED
    
FROM HUBSPOT_SECURE_SHARE_DB_NAME.V2_LIVE.COMPANIES
WHERE COMPANY_ID IS NOT NULL;

-- =====================================================================
-- 3. MATERIALIZED HUBSPOT TABLES WITH AI MEMORY COLUMNS
-- =====================================================================

-- Materialized HubSpot Deals table with AI Memory integration
CREATE TABLE IF NOT EXISTS STG_HUBSPOT_DEALS (
    DEAL_ID VARCHAR(255) PRIMARY KEY,
    DEAL_NAME VARCHAR(500),
    DEAL_STAGE VARCHAR(100),
    DEAL_AMOUNT NUMBER(15,2),
    CLOSE_DATE DATE,
    CREATE_DATE DATE,
    PIPELINE_NAME VARCHAR(255),
    DEAL_OWNER VARCHAR(255),
    DEAL_OWNER_EMAIL VARCHAR(255),
    DEAL_SOURCE VARCHAR(255),
    DEAL_TYPE VARCHAR(255),
    
    -- Contact and company references
    ASSOCIATED_CONTACT_ID VARCHAR(255),
    ASSOCIATED_COMPANY_ID VARCHAR(255),
    
    -- Business calculated fields
    DAYS_SINCE_CREATED NUMBER,
    DAYS_TO_CLOSE NUMBER,
    DEAL_STATUS VARCHAR(50),
    
    -- AI Memory columns for semantic search and storage
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768), -- Cortex embedding for semantic search
    AI_MEMORY_METADATA VARCHAR(16777216), -- JSON metadata for AI Memory
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ, -- Last AI Memory update timestamp
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    LAST_REFRESHED TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Materialized HubSpot Contacts table
CREATE TABLE IF NOT EXISTS STG_HUBSPOT_CONTACTS (
    CONTACT_ID VARCHAR(255) PRIMARY KEY,
    FIRST_NAME VARCHAR(255),
    LAST_NAME VARCHAR(255),
    EMAIL VARCHAR(255),
    PHONE VARCHAR(50),
    COMPANY_NAME VARCHAR(500),
    JOB_TITLE VARCHAR(255),
    LIFECYCLE_STAGE VARCHAR(100),
    LEAD_STATUS VARCHAR(100),
    
    -- Company reference
    ASSOCIATED_COMPANY_ID VARCHAR(255),
    
    -- Contact activity
    CREATE_DATE DATE,
    LAST_MODIFIED_DATE DATE,
    LAST_ACTIVITY_DATE DATE,
    
    -- Calculated fields
    FULL_NAME VARCHAR(511),
    DAYS_SINCE_CREATED NUMBER,
    DAYS_SINCE_LAST_ACTIVITY NUMBER,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    LAST_REFRESHED TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================================
-- 4. TRANSFORMATION PROCEDURES FOR HUBSPOT DATA
-- =====================================================================

-- Procedure to refresh materialized HubSpot Deals table
CREATE OR REPLACE PROCEDURE REFRESH_HUBSPOT_DEALS()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    -- First insert new deals that don't exist
    INSERT INTO STG_HUBSPOT_DEALS (
        DEAL_ID, DEAL_NAME, DEAL_STAGE, DEAL_AMOUNT, CLOSE_DATE, CREATE_DATE,
        PIPELINE_NAME, DEAL_OWNER, DEAL_OWNER_EMAIL, DEAL_SOURCE, DEAL_TYPE,
        ASSOCIATED_CONTACT_ID, ASSOCIATED_COMPANY_ID,
        DAYS_SINCE_CREATED, DAYS_TO_CLOSE, DEAL_STATUS,
        LAST_REFRESHED
    )
    SELECT 
        source.DEAL_ID, source.DEAL_NAME, source.DEAL_STAGE, source.DEAL_AMOUNT, 
        source.CLOSE_DATE, source.CREATE_DATE,
        source.PIPELINE_NAME, source.DEAL_OWNER, source.DEAL_OWNER_EMAIL, 
        source.DEAL_SOURCE, source.DEAL_TYPE,
        source.ASSOCIATED_CONTACT_ID, source.ASSOCIATED_COMPANY_ID,
        source.DAYS_SINCE_CREATED, source.DAYS_TO_CLOSE, source.DEAL_STATUS,
        source.LAST_REFRESHED
    FROM V_STG_HUBSPOT_DEALS source
    WHERE NOT EXISTS (
        SELECT 1 FROM STG_HUBSPOT_DEALS target
        WHERE target.DEAL_ID = source.DEAL_ID
    );
    
    -- Then update existing deals
    UPDATE STG_HUBSPOT_DEALS target
    SET 
        DEAL_NAME = source.DEAL_NAME,
        DEAL_STAGE = source.DEAL_STAGE,
        DEAL_AMOUNT = source.DEAL_AMOUNT,
        CLOSE_DATE = source.CLOSE_DATE,
        PIPELINE_NAME = source.PIPELINE_NAME,
        DEAL_OWNER = source.DEAL_OWNER,
        DEAL_OWNER_EMAIL = source.DEAL_OWNER_EMAIL,
        DEAL_SOURCE = source.DEAL_SOURCE,
        DEAL_TYPE = source.DEAL_TYPE,
        ASSOCIATED_CONTACT_ID = source.ASSOCIATED_CONTACT_ID,
        ASSOCIATED_COMPANY_ID = source.ASSOCIATED_COMPANY_ID,
        DAYS_SINCE_CREATED = source.DAYS_SINCE_CREATED,
        DAYS_TO_CLOSE = source.DAYS_TO_CLOSE,
        DEAL_STATUS = source.DEAL_STATUS,
        UPDATED_AT = CURRENT_TIMESTAMP,
        LAST_REFRESHED = source.LAST_REFRESHED
    FROM V_STG_HUBSPOT_DEALS source
    WHERE target.DEAL_ID = source.DEAL_ID;
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count
    FROM STG_HUBSPOT_DEALS;
    
    -- Generate result message
    SET result_message = 'Refreshed ' || processed_count || ' HubSpot deals';
    
    -- Output the result
    SELECT result_message;
END;
$$;

-- Procedure to refresh materialized HubSpot Contacts table
CREATE OR REPLACE PROCEDURE REFRESH_HUBSPOT_CONTACTS()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    -- First insert new contacts that don't exist
    INSERT INTO STG_HUBSPOT_CONTACTS (
        CONTACT_ID, FIRST_NAME, LAST_NAME, EMAIL, PHONE, COMPANY_NAME,
        JOB_TITLE, LIFECYCLE_STAGE, LEAD_STATUS, ASSOCIATED_COMPANY_ID,
        CREATE_DATE, LAST_MODIFIED_DATE, LAST_ACTIVITY_DATE,
        FULL_NAME, DAYS_SINCE_CREATED, DAYS_SINCE_LAST_ACTIVITY,
        LAST_REFRESHED
    )
    SELECT 
        source.CONTACT_ID, source.FIRST_NAME, source.LAST_NAME, source.EMAIL, 
        source.PHONE, source.COMPANY_NAME, source.JOB_TITLE, source.LIFECYCLE_STAGE, 
        source.LEAD_STATUS, source.ASSOCIATED_COMPANY_ID,
        source.CREATE_DATE, source.LAST_MODIFIED_DATE, source.LAST_ACTIVITY_DATE,
        source.FULL_NAME, source.DAYS_SINCE_CREATED, source.DAYS_SINCE_LAST_ACTIVITY,
        source.LAST_REFRESHED
    FROM V_STG_HUBSPOT_CONTACTS source
    WHERE NOT EXISTS (
        SELECT 1 FROM STG_HUBSPOT_CONTACTS target
        WHERE target.CONTACT_ID = source.CONTACT_ID
    );
    
    -- Then update existing contacts
    UPDATE STG_HUBSPOT_CONTACTS target
    SET 
        FIRST_NAME = source.FIRST_NAME,
        LAST_NAME = source.LAST_NAME,
        EMAIL = source.EMAIL,
        PHONE = source.PHONE,
        COMPANY_NAME = source.COMPANY_NAME,
        JOB_TITLE = source.JOB_TITLE,
        LIFECYCLE_STAGE = source.LIFECYCLE_STAGE,
        LEAD_STATUS = source.LEAD_STATUS,
        ASSOCIATED_COMPANY_ID = source.ASSOCIATED_COMPANY_ID,
        LAST_MODIFIED_DATE = source.LAST_MODIFIED_DATE,
        LAST_ACTIVITY_DATE = source.LAST_ACTIVITY_DATE,
        FULL_NAME = source.FULL_NAME,
        DAYS_SINCE_CREATED = source.DAYS_SINCE_CREATED,
        DAYS_SINCE_LAST_ACTIVITY = source.DAYS_SINCE_LAST_ACTIVITY,
        UPDATED_AT = CURRENT_TIMESTAMP,
        LAST_REFRESHED = source.LAST_REFRESHED
    FROM V_STG_HUBSPOT_CONTACTS source
    WHERE target.CONTACT_ID = source.CONTACT_ID;
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count
    FROM STG_HUBSPOT_CONTACTS;
    
    -- Generate result message
    SET result_message = 'Refreshed ' || processed_count || ' HubSpot contacts';
    
    -- Output the result
    SELECT result_message;
END;
$$;

-- =====================================================================
-- 5. ENHANCED GONG TRANSFORMATION PROCEDURES
-- =====================================================================

-- Enhanced procedure to transform raw Gong calls with AI Memory support
CREATE OR REPLACE PROCEDURE TRANSFORM_RAW_GONG_CALLS()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    -- First insert new calls that don't exist
    INSERT INTO STG_GONG_CALLS (
        CALL_ID, CALL_TITLE, CALL_DATETIME_UTC, CALL_DURATION_SECONDS,
        CALL_DIRECTION, CALL_SYSTEM, CALL_SCOPE, CALL_MEDIA, CALL_LANGUAGE, CALL_URL,
        PRIMARY_USER_ID, PRIMARY_USER_EMAIL, PRIMARY_USER_NAME,
        HUBSPOT_DEAL_ID, HUBSPOT_CONTACT_ID, HUBSPOT_COMPANY_ID,
        CRM_OPPORTUNITY_ID, CRM_ACCOUNT_ID,
        DEAL_STAGE, DEAL_VALUE, ACCOUNT_NAME, CONTACT_NAME,
        TALK_RATIO, LONGEST_MONOLOGUE_SECONDS, INTERACTIVITY_SCORE, QUESTIONS_ASKED_COUNT,
        UPDATED_AT
    )
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
        
        CURRENT_TIMESTAMP AS UPDATED_AT
    FROM SOPHIA_AI_DEV.RAW_AIRBYTE.GONG_CALLS_RAW src
    WHERE PROCESSED = FALSE
    AND NOT EXISTS (
        SELECT 1 FROM STG_GONG_CALLS tgt
        WHERE tgt.CALL_ID = src.RAW_DATA:id::VARCHAR
    );
    
    -- Then update existing calls
    UPDATE STG_GONG_CALLS tgt
    SET 
        CALL_TITLE = src.CALL_TITLE,
        CALL_DATETIME_UTC = src.CALL_DATETIME_UTC,
        CALL_DURATION_SECONDS = src.CALL_DURATION_SECONDS,
        CALL_DIRECTION = src.CALL_DIRECTION,
        HUBSPOT_DEAL_ID = src.HUBSPOT_DEAL_ID,
        HUBSPOT_CONTACT_ID = src.HUBSPOT_CONTACT_ID,
        DEAL_STAGE = src.DEAL_STAGE,
        DEAL_VALUE = src.DEAL_VALUE,
        TALK_RATIO = src.TALK_RATIO,
        UPDATED_AT = src.UPDATED_AT
    FROM (
        SELECT 
            RAW_DATA:id::VARCHAR AS CALL_ID,
            RAW_DATA:title::VARCHAR AS CALL_TITLE,
            RAW_DATA:started::TIMESTAMP_LTZ AS CALL_DATETIME_UTC,
            RAW_DATA:duration::NUMBER AS CALL_DURATION_SECONDS,
            RAW_DATA:direction::VARCHAR AS CALL_DIRECTION,
            RAW_DATA:customData.hubspotDealId::VARCHAR AS HUBSPOT_DEAL_ID,
            RAW_DATA:customData.hubspotContactId::VARCHAR AS HUBSPOT_CONTACT_ID,
            RAW_DATA:customData.dealStage::VARCHAR AS DEAL_STAGE,
            RAW_DATA:customData.dealValue::NUMBER AS DEAL_VALUE,
            RAW_DATA:analytics.talkRatio::FLOAT AS TALK_RATIO,
            CURRENT_TIMESTAMP AS UPDATED_AT
        FROM SOPHIA_AI_DEV.RAW_AIRBYTE.GONG_CALLS_RAW
        WHERE PROCESSED = FALSE
    ) src
    WHERE tgt.CALL_ID = src.CALL_ID;
    
    -- Mark raw records as processed
    UPDATE SOPHIA_AI_DEV.RAW_AIRBYTE.GONG_CALLS_RAW 
    SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP
    WHERE PROCESSED = FALSE;
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count
    FROM STG_GONG_CALLS;
    
    -- Generate result message
    SET result_message = 'Processed ' || processed_count || ' Gong call records';
    
    -- Output the result
    SELECT result_message;
END;
$$;

-- Enhanced procedure to transform raw Gong transcripts with AI Memory support
CREATE OR REPLACE PROCEDURE TRANSFORM_RAW_GONG_TRANSCRIPTS()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    -- Insert transcript segments from RAW_AIRBYTE.GONG_CALL_TRANSCRIPTS_RAW
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
            WHEN segment.value:speakerEmail LIKE '%@payready.com' THEN 'Internal'
            ELSE 'External'
        END AS SPEAKER_TYPE,
        segment.value:text::VARCHAR AS TRANSCRIPT_TEXT,
        segment.value:startTime::NUMBER AS START_TIME_SECONDS,
        segment.value:endTime::NUMBER AS END_TIME_SECONDS,
        (segment.value:endTime::NUMBER - segment.value:startTime::NUMBER) AS SEGMENT_DURATION_SECONDS,
        ARRAY_SIZE(SPLIT(segment.value:text::VARCHAR, ' ')) AS WORD_COUNT
    FROM SOPHIA_AI_DEV.RAW_AIRBYTE.GONG_CALL_TRANSCRIPTS_RAW,
    LATERAL FLATTEN(input => TRANSCRIPT_DATA:transcript.segments) AS segment
    WHERE PROCESSED = FALSE
    AND TRANSCRIPT_DATA:transcript IS NOT NULL;
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count 
    FROM STG_GONG_CALL_TRANSCRIPTS;
    
    -- Mark raw transcripts as processed
    UPDATE SOPHIA_AI_DEV.RAW_AIRBYTE.GONG_CALL_TRANSCRIPTS_RAW 
    SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP
    WHERE PROCESSED = FALSE;
    
    -- Generate result message
    SET result_message = 'Processed ' || processed_count || ' Gong transcript segments';
    
    -- Output the result
    SELECT result_message;
END;
$$;

-- =====================================================================
-- 6. AUTOMATED TASKS FOR STG_TRANSFORMED PIPELINE
-- =====================================================================

-- Task to refresh HubSpot deals every 30 minutes
CREATE OR REPLACE TASK TASK_REFRESH_HUBSPOT_DEALS
    WAREHOUSE = WH_SOPHIA_AI_PROCESSING
    SCHEDULE = 'USING CRON 0,30 * * * * UTC'
    COMMENT = 'Refresh materialized HubSpot deals table from Secure Data Share'
AS
    CALL REFRESH_HUBSPOT_DEALS();

-- Task to refresh HubSpot contacts every hour
CREATE OR REPLACE TASK TASK_REFRESH_HUBSPOT_CONTACTS
    WAREHOUSE = WH_SOPHIA_AI_PROCESSING
    SCHEDULE = 'USING CRON 0 * * * * UTC'
    COMMENT = 'Refresh materialized HubSpot contacts table from Secure Data Share'
AS
    CALL REFRESH_HUBSPOT_CONTACTS();

-- Task to transform raw Gong calls every 15 minutes
CREATE OR REPLACE TASK TASK_TRANSFORM_GONG_CALLS
    WAREHOUSE = WH_SOPHIA_AI_PROCESSING
    SCHEDULE = 'USING CRON 0,15,30,45 * * * * UTC'
    COMMENT = 'Transform raw Gong calls from Airbyte to structured format'
AS
    CALL TRANSFORM_RAW_GONG_CALLS();

-- Task to transform raw Gong transcripts every 30 minutes
CREATE OR REPLACE TASK TASK_TRANSFORM_GONG_TRANSCRIPTS
    WAREHOUSE = WH_SOPHIA_AI_PROCESSING
    SCHEDULE = 'USING CRON 0,30 * * * * UTC'
    COMMENT = 'Transform raw Gong transcripts from Airbyte to structured format'
AS
    CALL TRANSFORM_RAW_GONG_TRANSCRIPTS();

-- =====================================================================
-- 7. INDEXES AND PERFORMANCE OPTIMIZATION
-- =====================================================================

-- Create indexes for performance
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_CALLS_DATETIME ON STG_GONG_CALLS(CALL_DATETIME_UTC);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_CALLS_HUBSPOT_DEAL ON STG_GONG_CALLS(HUBSPOT_DEAL_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_CALLS_PRIMARY_USER ON STG_GONG_CALLS(PRIMARY_USER_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_CALLS_SENTIMENT ON STG_GONG_CALLS(SENTIMENT_SCORE);
-- 
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_TRANSCRIPTS_CALL_ID ON STG_GONG_CALL_TRANSCRIPTS(CALL_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_GONG_TRANSCRIPTS_SPEAKER ON STG_GONG_CALL_TRANSCRIPTS(SPEAKER_EMAIL);
-- 
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_HUBSPOT_DEALS_STAGE ON STG_HUBSPOT_DEALS(DEAL_STAGE);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_HUBSPOT_DEALS_OWNER ON STG_HUBSPOT_DEALS(DEAL_OWNER_EMAIL);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_HUBSPOT_DEALS_AMOUNT ON STG_HUBSPOT_DEALS(DEAL_AMOUNT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_STG_HUBSPOT_DEALS_CLOSE_DATE ON STG_HUBSPOT_DEALS(CLOSE_DATE);
-- 
-- =====================================================================
-- 8. GRANTS AND PERMISSIONS
-- =====================================================================

-- Grant access to tables and views individually
GRANT USAGE ON SCHEMA STG_TRANSFORMED TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT USAGE ON SCHEMA STG_TRANSFORMED TO ROLE ROLE_SOPHIA_DEVELOPER;

-- Grant access to specific tables for ROLE_SOPHIA_AI_AGENT_SERVICE
GRANT SELECT ON TABLE STG_GONG_CALLS TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON TABLE STG_GONG_CALL_TRANSCRIPTS TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON TABLE STG_GONG_CALL_PARTICIPANTS TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON TABLE STG_HUBSPOT_DEALS TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON TABLE STG_HUBSPOT_CONTACTS TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;

-- Grant access to specific views for ROLE_SOPHIA_AI_AGENT_SERVICE
GRANT SELECT ON VIEW V_STG_HUBSPOT_DEALS TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON VIEW V_STG_HUBSPOT_CONTACTS TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON VIEW V_STG_HUBSPOT_COMPANIES TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;

-- Grant access to specific tables for ROLE_SOPHIA_DEVELOPER
GRANT SELECT ON TABLE STG_GONG_CALLS TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON TABLE STG_GONG_CALL_TRANSCRIPTS TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON TABLE STG_GONG_CALL_PARTICIPANTS TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON TABLE STG_HUBSPOT_DEALS TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON TABLE STG_HUBSPOT_CONTACTS TO ROLE ROLE_SOPHIA_DEVELOPER;

-- Grant access to specific views for ROLE_SOPHIA_DEVELOPER
GRANT SELECT ON VIEW V_STG_HUBSPOT_DEALS TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON VIEW V_STG_HUBSPOT_CONTACTS TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON VIEW V_STG_HUBSPOT_COMPANIES TO ROLE ROLE_SOPHIA_DEVELOPER;

-- =====================================================================
-- DEPLOYMENT NOTES
-- =====================================================================

/*
Deployment Steps:

1. Execute this script in SOPHIA_AI_DEV database
2. Update HubSpot Secure Data Share database name (replace HUBSPOT_SECURE_SHARE_DB_NAME)
3. Enable and start automated tasks:
   - ALTER TASK TASK_REFRESH_HUBSPOT_DEALS RESUME;
   - ALTER TASK TASK_REFRESH_HUBSPOT_CONTACTS RESUME;
   - ALTER TASK TASK_TRANSFORM_GONG_CALLS RESUME;
   - ALTER TASK TASK_TRANSFORM_GONG_TRANSCRIPTS RESUME;

4. Test data transformation:
   - CALL REFRESH_HUBSPOT_DEALS();
   - CALL REFRESH_HUBSPOT_CONTACTS();
   - CALL TRANSFORM_RAW_GONG_CALLS();
   - CALL TRANSFORM_RAW_GONG_TRANSCRIPTS();

5. Verify AI Memory columns exist and are ready for embedding storage
6. Test Snowflake Cortex integration with sample data
*/ 