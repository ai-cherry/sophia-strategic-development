-- =====================================================================
-- Enhanced Data Pipeline Schema for Sophia AI
-- =====================================================================
--
-- This schema creates the enhanced data pipeline infrastructure for Sophia AI,
-- integrating with Estuary Flow, Gong data share, HubSpot, and other sources
-- for comprehensive business intelligence and AI-powered insights.
--
-- Database: SOPHIA_AI_DB
-- Purpose: Complete data pipeline integration with real-time processing
-- =====================================================================

USE DATABASE SOPHIA_AI_DB;

-- =====================================================================
-- 1. RAW DATA SCHEMAS (Estuary Flow Ingestion)
-- =====================================================================

-- Raw data from Estuary Flow ingestion
CREATE SCHEMA IF NOT EXISTS RAW_DATA;
USE SCHEMA RAW_DATA;

-- HubSpot raw data tables
CREATE TABLE IF NOT EXISTS HUBSPOT_CONTACTS_RAW (
    _ESTUARY_FLOW_DOCUMENT VARIANT,
    _ESTUARY_INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _ESTUARY_SOURCE_SYSTEM VARCHAR(50) DEFAULT 'hubspot',

    -- Extracted fields for performance
    CONTACT_ID VARCHAR(255),
    EMAIL VARCHAR(255),
    FIRSTNAME VARCHAR(255),
    LASTNAME VARCHAR(255),
    COMPANY VARCHAR(255),
    PHONE VARCHAR(255),
    LIFECYCLESTAGE VARCHAR(100),
    CREATEDATE TIMESTAMP_LTZ,
    LASTMODIFIEDDATE TIMESTAMP_LTZ,
    HUBSPOT_OWNER_ID VARCHAR(255),

    -- Properties as variant for flexibility
    PROPERTIES VARIANT,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS HUBSPOT_DEALS_RAW (
    _ESTUARY_FLOW_DOCUMENT VARIANT,
    _ESTUARY_INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _ESTUARY_SOURCE_SYSTEM VARCHAR(50) DEFAULT 'hubspot',

    -- Extracted fields
    DEAL_ID VARCHAR(255),
    DEALNAME VARCHAR(500),
    AMOUNT NUMBER(15,2),
    DEALSTAGE VARCHAR(255),
    PIPELINE VARCHAR(255),
    CLOSEDATE TIMESTAMP_LTZ,
    CREATEDATE TIMESTAMP_LTZ,
    HUBSPOT_OWNER_ID VARCHAR(255),

    -- Associated records
    ASSOCIATED_COMPANY_IDS VARIANT,
    ASSOCIATED_CONTACT_IDS VARIANT,

    -- Properties as variant
    PROPERTIES VARIANT,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS HUBSPOT_COMPANIES_RAW (
    _ESTUARY_FLOW_DOCUMENT VARIANT,
    _ESTUARY_INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _ESTUARY_SOURCE_SYSTEM VARCHAR(50) DEFAULT 'hubspot',

    -- Extracted fields
    COMPANY_ID VARCHAR(255),
    NAME VARCHAR(500),
    DOMAIN VARCHAR(255),
    INDUSTRY VARCHAR(255),
    CITY VARCHAR(255),
    STATE VARCHAR(255),
    COUNTRY VARCHAR(255),
    CREATEDATE TIMESTAMP_LTZ,

    -- Properties as variant
    PROPERTIES VARIANT,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Gong raw data tables (from API and data share)
CREATE TABLE IF NOT EXISTS GONG_CALLS_RAW (
    _ESTUARY_FLOW_DOCUMENT VARIANT,
    _ESTUARY_INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _ESTUARY_SOURCE_SYSTEM VARCHAR(50) DEFAULT 'gong',

    -- Extracted fields
    CALL_ID VARCHAR(255),
    TITLE VARCHAR(500),
    URL VARCHAR(500),
    PURPOSE VARCHAR(255),
    MEETING_URL VARCHAR(500),
    ACTUAL_START TIMESTAMP_LTZ,
    ACTUAL_END TIMESTAMP_LTZ,
    DURATION INTEGER,
    PRIMARY_USER_ID VARCHAR(255),
    DIRECTION VARCHAR(50),
    SYSTEM VARCHAR(100),
    SCOPE VARCHAR(100),
    MEDIA VARCHAR(100),
    LANGUAGE VARCHAR(50),
    WORKSPACE_ID VARCHAR(255),

    -- Participants and transcript
    PARTICIPANTS VARIANT,
    TRANSCRIPT TEXT,
    CUSTOM_DATA VARIANT,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS GONG_USERS_RAW (
    _ESTUARY_FLOW_DOCUMENT VARIANT,
    _ESTUARY_INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _ESTUARY_SOURCE_SYSTEM VARCHAR(50) DEFAULT 'gong',

    -- Extracted fields
    USER_ID VARCHAR(255),
    EMAIL_ADDRESS VARCHAR(255),
    FIRST_NAME VARCHAR(255),
    LAST_NAME VARCHAR(255),
    ACTIVE BOOLEAN,
    PHONE_NUMBER VARCHAR(50),
    EXTENSION VARCHAR(20),
    CREATED TIMESTAMP_LTZ,

    -- Settings and metadata
    SETTINGS VARIANT,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Slack raw data tables
CREATE TABLE IF NOT EXISTS SLACK_MESSAGES_RAW (
    _ESTUARY_FLOW_DOCUMENT VARIANT,
    _ESTUARY_INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    _ESTUARY_SOURCE_SYSTEM VARCHAR(50) DEFAULT 'slack',

    -- Extracted fields
    MESSAGE_TS VARCHAR(255),
    CHANNEL VARCHAR(255),
    USER_ID VARCHAR(255),
    TEXT TEXT,
    THREAD_TS VARCHAR(255),
    REPLY_COUNT INTEGER,

    -- Rich content
    REACTIONS VARIANT,
    FILES VARIANT,
    EDITED VARIANT,

    -- Metadata
    DELETED_TS VARCHAR(255),
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================================
-- 2. GONG DATA SHARE INTEGRATION
-- =====================================================================

-- Schema for Gong data share (direct access to Gong's Snowflake share)
CREATE SCHEMA IF NOT EXISTS GONG_DATA_SHARE;
USE SCHEMA GONG_DATA_SHARE;

-- Create views to access Gong data share
-- Note: Actual data share access requires authorization from Gong support
-- Account identifier: MYJDJNU-FP71296
-- Data share: PAYREADY_GONG_089AA23F865C4231A097A44517FA10E9.INBOUND

-- Placeholder for Gong data share views (to be created after authorization)
CREATE OR REPLACE VIEW GONG_CALLS_SHARE AS
SELECT
    CALL_ID,
    TITLE,
    URL,
    ACTUAL_START,
    ACTUAL_END,
    DURATION,
    PARTICIPANTS,
    TRANSCRIPT,
    WORKSPACE_ID,
    CREATED_DATE,
    MODIFIED_DATE
FROM PAYREADY_GONG_089AA23F865C4231A097A44517FA10E9.INBOUND.CALLS
WHERE WORKSPACE_ID IN (
    SELECT WORKSPACE_ID
    FROM PAYREADY_GONG_089AA23F865C4231A097A44517FA10E9.INBOUND.WORKSPACES
    WHERE WORKSPACE_NAME = 'Pay Ready'
);

CREATE OR REPLACE VIEW GONG_USERS_SHARE AS
SELECT
    USER_ID,
    EMAIL_ADDRESS,
    FIRST_NAME,
    LAST_NAME,
    ACTIVE,
    WORKSPACE_ID,
    CREATED_DATE,
    MODIFIED_DATE
FROM PAYREADY_GONG_089AA23F865C4231A097A44517FA10E9.INBOUND.USERS
WHERE WORKSPACE_ID IN (
    SELECT WORKSPACE_ID
    FROM PAYREADY_GONG_089AA23F865C4231A097A44517FA10E9.INBOUND.WORKSPACES
    WHERE WORKSPACE_NAME = 'Pay Ready'
);

-- =====================================================================
-- 3. PROCESSED DATA SCHEMAS (Transformed and Enriched)
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS PROCESSED_DATA;
USE SCHEMA PROCESSED_DATA;

-- Unified contact data (combining HubSpot, Gong, Slack)
CREATE TABLE IF NOT EXISTS UNIFIED_CONTACTS (
    UNIFIED_CONTACT_ID VARCHAR(255) PRIMARY KEY,

    -- Source system tracking
    HUBSPOT_CONTACT_ID VARCHAR(255),
    GONG_USER_ID VARCHAR(255),
    SLACK_USER_ID VARCHAR(255),

    -- Unified contact information
    EMAIL_ADDRESS VARCHAR(255) UNIQUE,
    FIRST_NAME VARCHAR(255),
    LAST_NAME VARCHAR(255),
    FULL_NAME VARCHAR(500) GENERATED ALWAYS AS (FIRST_NAME || ' ' || LAST_NAME),
    PHONE_NUMBER VARCHAR(50),

    -- Company and role information
    COMPANY_NAME VARCHAR(500),
    JOB_TITLE VARCHAR(255),
    DEPARTMENT VARCHAR(255),
    SENIORITY_LEVEL VARCHAR(100),

    -- Engagement metrics
    TOTAL_INTERACTIONS INTEGER DEFAULT 0,
    LAST_INTERACTION_DATE TIMESTAMP_LTZ,
    INTERACTION_SCORE FLOAT, -- Calculated engagement score

    -- Communication preferences
    PREFERRED_CHANNEL VARCHAR(100),
    RESPONSE_TIME_AVERAGE INTEGER, -- Average response time in minutes
    COMMUNICATION_FREQUENCY VARCHAR(50),

    -- AI-powered insights
    PERSONALITY_INSIGHTS VARIANT, -- AI-generated personality analysis
    COMMUNICATION_STYLE VARIANT, -- AI-analyzed communication patterns
    TOPICS_OF_INTEREST VARIANT, -- AI-extracted topics from interactions
    SENTIMENT_ANALYSIS VARIANT, -- Overall sentiment analysis

    -- Vector embeddings for semantic search
    CONTACT_EMBEDDING VECTOR(FLOAT, 1536), -- OpenAI embedding
    INTERACTION_EMBEDDING VECTOR(FLOAT, 1536), -- Interaction-based embedding

    -- Data quality and confidence
    DATA_COMPLETENESS_SCORE FLOAT, -- 0-1 score of data completeness
    CONFIDENCE_SCORE FLOAT, -- 0-1 confidence in data accuracy
    LAST_ENRICHMENT_DATE TIMESTAMP_LTZ,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255) DEFAULT 'system',
    UPDATED_BY VARCHAR(255) DEFAULT 'system'
);

-- Unified interaction history (calls, emails, slack messages)
CREATE TABLE IF NOT EXISTS UNIFIED_INTERACTIONS (
    INTERACTION_ID VARCHAR(255) PRIMARY KEY,
    UNIFIED_CONTACT_ID VARCHAR(255),

    -- Source tracking
    SOURCE_SYSTEM VARCHAR(50), -- 'gong', 'hubspot', 'slack'
    SOURCE_ID VARCHAR(255),
    SOURCE_URL VARCHAR(500),

    -- Interaction details
    INTERACTION_TYPE VARCHAR(100), -- 'call', 'email', 'slack_message', 'meeting'
    INTERACTION_DIRECTION VARCHAR(50), -- 'inbound', 'outbound', 'internal'
    INTERACTION_DATE TIMESTAMP_LTZ,
    DURATION_MINUTES INTEGER,

    -- Content and context
    SUBJECT VARCHAR(500),
    CONTENT TEXT,
    SUMMARY TEXT, -- AI-generated summary
    KEY_TOPICS VARIANT, -- AI-extracted key topics
    ACTION_ITEMS VARIANT, -- AI-extracted action items

    -- Participants
    PARTICIPANTS VARIANT, -- Array of participant information
    PRIMARY_PARTICIPANT_ID VARCHAR(255),
    INTERNAL_PARTICIPANTS VARIANT,
    EXTERNAL_PARTICIPANTS VARIANT,

    -- Sentiment and analysis
    SENTIMENT_SCORE FLOAT, -- -1 to 1 sentiment score
    EMOTION_ANALYSIS VARIANT, -- Detailed emotion analysis
    INTENT_CLASSIFICATION VARCHAR(255), -- AI-classified intent
    OUTCOME_CLASSIFICATION VARCHAR(255), -- AI-classified outcome

    -- Business context
    DEAL_STAGE VARCHAR(255),
    OPPORTUNITY_ID VARCHAR(255),
    ACCOUNT_ID VARCHAR(255),
    PRODUCT_MENTIONED VARIANT, -- Products/services mentioned
    COMPETITOR_MENTIONED VARIANT, -- Competitors mentioned

    -- Vector embeddings
    CONTENT_EMBEDDING VECTOR(FLOAT, 1536),
    CONTEXT_EMBEDDING VECTOR(FLOAT, 1536),

    -- Quality and confidence
    TRANSCRIPTION_CONFIDENCE FLOAT, -- For calls
    AI_ANALYSIS_CONFIDENCE FLOAT,
    MANUAL_REVIEW_STATUS VARCHAR(50), -- 'pending', 'reviewed', 'approved'

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (UNIFIED_CONTACT_ID) REFERENCES UNIFIED_CONTACTS(UNIFIED_CONTACT_ID)
);

-- Deal intelligence (enhanced HubSpot deals with AI insights)
CREATE TABLE IF NOT EXISTS DEAL_INTELLIGENCE (
    DEAL_ID VARCHAR(255) PRIMARY KEY,
    HUBSPOT_DEAL_ID VARCHAR(255) UNIQUE,

    -- Basic deal information
    DEAL_NAME VARCHAR(500),
    AMOUNT NUMBER(15,2),
    CURRENCY VARCHAR(10) DEFAULT 'USD',
    DEAL_STAGE VARCHAR(255),
    PIPELINE VARCHAR(255),
    PROBABILITY FLOAT,

    -- Timeline
    CREATE_DATE TIMESTAMP_LTZ,
    CLOSE_DATE TIMESTAMP_LTZ,
    LAST_ACTIVITY_DATE TIMESTAMP_LTZ,
    DAYS_IN_STAGE INTEGER,
    SALES_CYCLE_LENGTH INTEGER,

    -- Account and contacts
    ACCOUNT_ID VARCHAR(255),
    PRIMARY_CONTACT_ID VARCHAR(255),
    DECISION_MAKERS VARIANT, -- Array of decision maker contact IDs
    INFLUENCERS VARIANT, -- Array of influencer contact IDs

    -- Sales team
    OWNER_ID VARCHAR(255),
    SALES_REP_NAME VARCHAR(255),
    SALES_MANAGER VARCHAR(255),

    -- AI-powered insights
    WIN_PROBABILITY_AI FLOAT, -- AI-calculated win probability
    RISK_FACTORS VARIANT, -- AI-identified risk factors
    SUCCESS_FACTORS VARIANT, -- AI-identified success factors
    NEXT_BEST_ACTIONS VARIANT, -- AI-recommended next actions
    COMPETITIVE_THREATS VARIANT, -- AI-identified competitive threats

    -- Interaction analysis
    TOTAL_INTERACTIONS INTEGER DEFAULT 0,
    LAST_MEANINGFUL_INTERACTION TIMESTAMP_LTZ,
    ENGAGEMENT_SCORE FLOAT, -- Overall engagement score
    SENTIMENT_TREND VARIANT, -- Sentiment trend over time

    -- Product fit analysis
    PRODUCT_FIT_SCORE FLOAT, -- AI-calculated product-market fit
    RECOMMENDED_PRODUCTS VARIANT, -- AI-recommended products
    TECHNICAL_REQUIREMENTS VARIANT, -- Identified technical requirements
    BUDGET_INDICATORS VARIANT, -- AI-extracted budget indicators

    -- Forecasting
    FORECAST_CATEGORY VARCHAR(100), -- 'commit', 'best_case', 'pipeline', 'omitted'
    FORECAST_CONFIDENCE FLOAT,
    WEIGHTED_AMOUNT NUMBER(15,2),

    -- Vector embeddings
    DEAL_EMBEDDING VECTOR(FLOAT, 1536),
    INTERACTION_EMBEDDING VECTOR(FLOAT, 1536),

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (PRIMARY_CONTACT_ID) REFERENCES UNIFIED_CONTACTS(UNIFIED_CONTACT_ID)
);

-- =====================================================================
-- 4. ANALYTICS AND INSIGHTS SCHEMAS
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS ANALYTICS;
USE SCHEMA ANALYTICS;

-- Sales performance analytics
CREATE TABLE IF NOT EXISTS SALES_PERFORMANCE_METRICS (
    METRIC_ID VARCHAR(255) PRIMARY KEY,
    METRIC_DATE DATE,
    METRIC_PERIOD VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'quarterly'

    -- Sales rep performance
    SALES_REP_ID VARCHAR(255),
    SALES_REP_NAME VARCHAR(255),
    TEAM VARCHAR(255),
    MANAGER VARCHAR(255),

    -- Activity metrics
    CALLS_MADE INTEGER DEFAULT 0,
    EMAILS_SENT INTEGER DEFAULT 0,
    MEETINGS_HELD INTEGER DEFAULT 0,
    DEMOS_GIVEN INTEGER DEFAULT 0,

    -- Pipeline metrics
    OPPORTUNITIES_CREATED INTEGER DEFAULT 0,
    OPPORTUNITIES_ADVANCED INTEGER DEFAULT 0,
    OPPORTUNITIES_WON INTEGER DEFAULT 0,
    OPPORTUNITIES_LOST INTEGER DEFAULT 0,

    -- Revenue metrics
    PIPELINE_GENERATED NUMBER(15,2) DEFAULT 0,
    REVENUE_CLOSED NUMBER(15,2) DEFAULT 0,
    AVERAGE_DEAL_SIZE NUMBER(15,2),
    WIN_RATE FLOAT,

    -- Efficiency metrics
    SALES_CYCLE_AVERAGE INTEGER, -- Days
    ACTIVITIES_PER_OPPORTUNITY FLOAT,
    CONVERSION_RATE_LEAD_TO_OPP FLOAT,
    CONVERSION_RATE_OPP_TO_CLOSE FLOAT,

    -- AI-powered insights
    PERFORMANCE_SCORE FLOAT, -- AI-calculated performance score
    IMPROVEMENT_AREAS VARIANT, -- AI-identified improvement areas
    SUCCESS_PATTERNS VARIANT, -- AI-identified success patterns
    COACHING_RECOMMENDATIONS VARIANT, -- AI-generated coaching recommendations

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Customer health and engagement analytics
CREATE TABLE IF NOT EXISTS CUSTOMER_HEALTH_METRICS (
    HEALTH_ID VARCHAR(255) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(255),
    METRIC_DATE DATE,

    -- Engagement metrics
    INTERACTION_FREQUENCY FLOAT, -- Interactions per week
    LAST_INTERACTION_DAYS INTEGER, -- Days since last interaction
    RESPONSE_TIME_AVERAGE INTEGER, -- Average response time in hours
    MEETING_ATTENDANCE_RATE FLOAT,

    -- Product usage metrics (if available)
    LOGIN_FREQUENCY FLOAT,
    FEATURE_ADOPTION_SCORE FLOAT,
    SUPPORT_TICKET_COUNT INTEGER,
    SUPPORT_SATISFACTION_SCORE FLOAT,

    -- Relationship strength
    RELATIONSHIP_SCORE FLOAT, -- 0-100 relationship strength score
    DECISION_MAKER_ENGAGEMENT FLOAT,
    CHAMPION_STRENGTH FLOAT,
    STAKEHOLDER_COVERAGE FLOAT,

    -- Risk indicators
    CHURN_RISK_SCORE FLOAT, -- 0-1 churn risk probability
    EXPANSION_OPPORTUNITY_SCORE FLOAT, -- 0-1 expansion probability
    COMPETITIVE_RISK_SCORE FLOAT,

    -- Sentiment analysis
    OVERALL_SENTIMENT FLOAT, -- -1 to 1 sentiment score
    SENTIMENT_TREND VARCHAR(50), -- 'improving', 'stable', 'declining'
    SATISFACTION_INDICATORS VARIANT,

    -- AI insights
    HEALTH_STATUS VARCHAR(50), -- 'healthy', 'at_risk', 'critical'
    RISK_FACTORS VARIANT,
    OPPORTUNITY_FACTORS VARIANT,
    RECOMMENDED_ACTIONS VARIANT,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (CUSTOMER_ID) REFERENCES FOUNDATIONAL_KNOWLEDGE.CUSTOMERS(CUSTOMER_ID)
);

-- =====================================================================
-- 5. REAL-TIME DATA PROCESSING VIEWS
-- =====================================================================

-- Real-time contact enrichment view
CREATE OR REPLACE VIEW REAL_TIME_CONTACT_ENRICHMENT AS
SELECT
    hc.CONTACT_ID as HUBSPOT_CONTACT_ID,
    hc.EMAIL,
    hc.FIRSTNAME,
    hc.LASTNAME,
    hc.COMPANY,
    gu.USER_ID as GONG_USER_ID,
    gu.EMAIL_ADDRESS as GONG_EMAIL,
    sm.USER_ID as SLACK_USER_ID,

    -- Interaction counts
    COUNT(DISTINCT gc.CALL_ID) as GONG_CALL_COUNT,
    COUNT(DISTINCT sm.MESSAGE_TS) as SLACK_MESSAGE_COUNT,

    -- Latest interactions
    MAX(gc.ACTUAL_START) as LAST_GONG_CALL,
    MAX(sm.CREATED_AT) as LAST_SLACK_MESSAGE,

    -- Engagement score calculation
    (COUNT(DISTINCT gc.CALL_ID) * 10 + COUNT(DISTINCT sm.MESSAGE_TS) * 2) as ENGAGEMENT_SCORE

FROM RAW_DATA.HUBSPOT_CONTACTS_RAW hc
LEFT JOIN RAW_DATA.GONG_USERS_RAW gu ON LOWER(hc.EMAIL) = LOWER(gu.EMAIL_ADDRESS)
LEFT JOIN RAW_DATA.GONG_CALLS_RAW gc ON gu.USER_ID = gc.PRIMARY_USER_ID
LEFT JOIN RAW_DATA.SLACK_MESSAGES_RAW sm ON gu.EMAIL_ADDRESS = sm.USER_ID
GROUP BY 1,2,3,4,5,6,7,8;

-- Real-time deal intelligence view
CREATE OR REPLACE VIEW REAL_TIME_DEAL_INTELLIGENCE AS
SELECT
    hd.DEAL_ID,
    hd.DEALNAME,
    hd.AMOUNT,
    hd.DEALSTAGE,
    hd.CLOSEDATE,

    -- Associated interactions
    COUNT(DISTINCT gc.CALL_ID) as RELATED_CALLS,
    MAX(gc.ACTUAL_START) as LAST_CALL_DATE,

    -- Sentiment analysis from calls
    AVG(
        CASE
            WHEN CONTAINS(UPPER(gc.TRANSCRIPT), 'POSITIVE') THEN 1
            WHEN CONTAINS(UPPER(gc.TRANSCRIPT), 'NEGATIVE') THEN -1
            ELSE 0
        END
    ) as SENTIMENT_SCORE,

    -- AI-powered win probability (simplified)
    CASE
        WHEN hd.DEALSTAGE = 'closedwon' THEN 1.0
        WHEN hd.DEALSTAGE = 'closedlost' THEN 0.0
        WHEN COUNT(DISTINCT gc.CALL_ID) > 5 AND hd.AMOUNT > 50000 THEN 0.8
        WHEN COUNT(DISTINCT gc.CALL_ID) > 3 AND hd.AMOUNT > 25000 THEN 0.6
        WHEN COUNT(DISTINCT gc.CALL_ID) > 1 THEN 0.4
        ELSE 0.2
    END as AI_WIN_PROBABILITY

FROM RAW_DATA.HUBSPOT_DEALS_RAW hd
LEFT JOIN RAW_DATA.GONG_CALLS_RAW gc ON hd.DEAL_ID = gc.CUSTOM_DATA:deal_id::STRING
GROUP BY 1,2,3,4,5;

-- =====================================================================
-- 6. DATA QUALITY AND MONITORING
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS DATA_QUALITY;
USE SCHEMA DATA_QUALITY;

-- Data pipeline monitoring
CREATE TABLE IF NOT EXISTS PIPELINE_MONITORING (
    MONITOR_ID VARCHAR(255) PRIMARY KEY,
    PIPELINE_NAME VARCHAR(255),
    SOURCE_SYSTEM VARCHAR(100),
    DESTINATION_SYSTEM VARCHAR(100),

    -- Execution metrics
    EXECUTION_DATE TIMESTAMP_LTZ,
    EXECUTION_STATUS VARCHAR(50), -- 'success', 'failure', 'warning'
    RECORDS_PROCESSED INTEGER,
    RECORDS_FAILED INTEGER,
    PROCESSING_TIME_SECONDS INTEGER,

    -- Data quality metrics
    DATA_COMPLETENESS_SCORE FLOAT,
    DATA_ACCURACY_SCORE FLOAT,
    DUPLICATE_RECORD_COUNT INTEGER,
    SCHEMA_VALIDATION_ERRORS INTEGER,

    -- Error details
    ERROR_MESSAGE TEXT,
    ERROR_DETAILS VARIANT,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Data freshness monitoring
CREATE TABLE IF NOT EXISTS DATA_FRESHNESS_MONITORING (
    FRESHNESS_ID VARCHAR(255) PRIMARY KEY,
    TABLE_NAME VARCHAR(255),
    SCHEMA_NAME VARCHAR(255),

    -- Freshness metrics
    LAST_UPDATE_TIME TIMESTAMP_LTZ,
    EXPECTED_UPDATE_FREQUENCY INTEGER, -- Expected update frequency in minutes
    FRESHNESS_STATUS VARCHAR(50), -- 'fresh', 'stale', 'critical'
    MINUTES_SINCE_UPDATE INTEGER,

    -- Record counts
    TOTAL_RECORDS INTEGER,
    NEW_RECORDS_TODAY INTEGER,
    UPDATED_RECORDS_TODAY INTEGER,

    -- Metadata
    CHECKED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================================
-- 7. STORED PROCEDURES FOR DATA PROCESSING
-- =====================================================================

-- Procedure to refresh unified contacts
CREATE OR REPLACE PROCEDURE REFRESH_UNIFIED_CONTACTS()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Merge HubSpot contacts into unified contacts
    MERGE INTO PROCESSED_DATA.UNIFIED_CONTACTS uc
    USING (
        SELECT
            CONTACT_ID as HUBSPOT_CONTACT_ID,
            EMAIL,
            FIRSTNAME,
            LASTNAME,
            COMPANY,
            PHONE,
            CURRENT_TIMESTAMP() as UPDATED_AT
        FROM RAW_DATA.HUBSPOT_CONTACTS_RAW
        WHERE EMAIL IS NOT NULL
    ) hc
    ON uc.HUBSPOT_CONTACT_ID = hc.HUBSPOT_CONTACT_ID
    WHEN MATCHED THEN
        UPDATE SET
            EMAIL_ADDRESS = hc.EMAIL,
            FIRST_NAME = hc.FIRSTNAME,
            LAST_NAME = hc.LASTNAME,
            COMPANY_NAME = hc.COMPANY,
            PHONE_NUMBER = hc.PHONE,
            UPDATED_AT = hc.UPDATED_AT
    WHEN NOT MATCHED THEN
        INSERT (
            UNIFIED_CONTACT_ID,
            HUBSPOT_CONTACT_ID,
            EMAIL_ADDRESS,
            FIRST_NAME,
            LAST_NAME,
            COMPANY_NAME,
            PHONE_NUMBER,
            CREATED_AT,
            UPDATED_AT
        )
        VALUES (
            UUID_STRING(),
            hc.HUBSPOT_CONTACT_ID,
            hc.EMAIL,
            hc.FIRSTNAME,
            hc.LASTNAME,
            hc.COMPANY,
            hc.PHONE,
            CURRENT_TIMESTAMP(),
            hc.UPDATED_AT
        );

    RETURN 'Unified contacts refreshed successfully';
END;
$$;

-- Procedure to calculate engagement scores
CREATE OR REPLACE PROCEDURE CALCULATE_ENGAGEMENT_SCORES()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Update engagement scores based on interactions
    UPDATE PROCESSED_DATA.UNIFIED_CONTACTS
    SET
        INTERACTION_SCORE = (
            SELECT
                COALESCE(COUNT(DISTINCT ui.INTERACTION_ID) * 10, 0) +
                COALESCE(SUM(CASE WHEN ui.INTERACTION_TYPE = 'call' THEN 20 ELSE 5 END), 0)
            FROM PROCESSED_DATA.UNIFIED_INTERACTIONS ui
            WHERE ui.UNIFIED_CONTACT_ID = UNIFIED_CONTACTS.UNIFIED_CONTACT_ID
            AND ui.INTERACTION_DATE >= DATEADD('day', -30, CURRENT_DATE())
        ),
        LAST_INTERACTION_DATE = (
            SELECT MAX(ui.INTERACTION_DATE)
            FROM PROCESSED_DATA.UNIFIED_INTERACTIONS ui
            WHERE ui.UNIFIED_CONTACT_ID = UNIFIED_CONTACTS.UNIFIED_CONTACT_ID
        ),
        UPDATED_AT = CURRENT_TIMESTAMP();

    RETURN 'Engagement scores calculated successfully';
END;
$$;

-- =====================================================================
-- 8. TASKS FOR AUTOMATED DATA PROCESSING
-- =====================================================================

-- Task to refresh unified contacts every 15 minutes
CREATE OR REPLACE TASK REFRESH_UNIFIED_CONTACTS_TASK
    WAREHOUSE = SOPHIA_AI_WH
    SCHEDULE = 'USING CRON 0,15,30,45 * * * * UTC'
AS
    CALL REFRESH_UNIFIED_CONTACTS();

-- Task to calculate engagement scores every hour
CREATE OR REPLACE TASK CALCULATE_ENGAGEMENT_SCORES_TASK
    WAREHOUSE = SOPHIA_AI_WH
    SCHEDULE = 'USING CRON 0 * * * * UTC'
AS
    CALL CALCULATE_ENGAGEMENT_SCORES();

-- Start the tasks
ALTER TASK REFRESH_UNIFIED_CONTACTS_TASK RESUME;
ALTER TASK CALCULATE_ENGAGEMENT_SCORES_TASK RESUME;

-- =====================================================================
-- 9. GRANTS AND PERMISSIONS
-- =====================================================================

-- Grant permissions to Sophia AI role
GRANT USAGE ON DATABASE SOPHIA_AI_DB TO ROLE SOPHIA_AI_ROLE;
GRANT USAGE ON ALL SCHEMAS IN DATABASE SOPHIA_AI_DB TO ROLE SOPHIA_AI_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN DATABASE SOPHIA_AI_DB TO ROLE SOPHIA_AI_ROLE;
GRANT SELECT ON ALL VIEWS IN DATABASE SOPHIA_AI_DB TO ROLE SOPHIA_AI_ROLE;
GRANT EXECUTE ON ALL PROCEDURES IN DATABASE SOPHIA_AI_DB TO ROLE SOPHIA_AI_ROLE;

-- Grant permissions for future objects
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE SOPHIA_AI_DB TO ROLE SOPHIA_AI_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN DATABASE SOPHIA_AI_DB TO ROLE SOPHIA_AI_ROLE;
GRANT SELECT ON FUTURE VIEWS IN DATABASE SOPHIA_AI_DB TO ROLE SOPHIA_AI_ROLE;

COMMIT;
