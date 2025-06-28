-- =====================================================================
-- Slack Integration Schema for Pay Ready Knowledge Base
-- =====================================================================
-- 
-- This schema creates comprehensive Slack data integration for the knowledge base,
-- capturing team communications, decisions, and institutional knowledge.
--
-- Schema: SLACK_DATA
-- Purpose: Store and process Slack conversations for knowledge extraction
-- =====================================================================

USE DATABASE SOPHIA_AI;
CREATE SCHEMA IF NOT EXISTS SLACK_DATA;
USE SCHEMA SLACK_DATA;

-- =====================================================================
-- 1. RAW SLACK DATA TABLES
-- =====================================================================

-- Raw Slack messages from API/webhook
CREATE TABLE IF NOT EXISTS SLACK_MESSAGES_RAW (
    MESSAGE_ID VARCHAR(255) PRIMARY KEY,
    CHANNEL_ID VARCHAR(255) NOT NULL,
    USER_ID VARCHAR(255),
    TEAM_ID VARCHAR(255),
    
    -- Message content
    MESSAGE_TEXT VARCHAR(16777216),
    MESSAGE_TYPE VARCHAR(50), -- 'message', 'file_share', 'bot_message', etc.
    MESSAGE_SUBTYPE VARCHAR(50),
    
    -- Timing
    TIMESTAMP_SLACK FLOAT, -- Slack's timestamp format
    MESSAGE_DATETIME TIMESTAMP_LTZ GENERATED ALWAYS AS (
        TO_TIMESTAMP(TIMESTAMP_SLACK)
    ),
    
    -- Threading
    THREAD_TS FLOAT, -- Parent message timestamp for threaded messages
    REPLY_COUNT NUMBER DEFAULT 0,
    REPLY_USERS VARIANT, -- JSON array of users who replied
    
    -- Message metadata
    ATTACHMENTS VARIANT, -- JSON array of attachments
    FILES VARIANT, -- JSON array of files
    REACTIONS VARIANT, -- JSON array of reactions
    MENTIONS VARIANT, -- JSON array of mentioned users/channels
    
    -- Raw API response
    RAW_DATA VARIANT NOT NULL,
    
    -- Processing status
    INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED BOOLEAN DEFAULT FALSE,
    PROCESSED_AT TIMESTAMP_LTZ,
    PROCESSING_ERROR VARCHAR(16777216)
);

-- Raw Slack channels data
CREATE TABLE IF NOT EXISTS SLACK_CHANNELS_RAW (
    CHANNEL_ID VARCHAR(255) PRIMARY KEY,
    TEAM_ID VARCHAR(255),
    
    -- Channel information
    CHANNEL_NAME VARCHAR(255),
    CHANNEL_TYPE VARCHAR(50), -- 'public_channel', 'private_channel', 'im', 'mpim'
    IS_CHANNEL BOOLEAN,
    IS_GROUP BOOLEAN,
    IS_IM BOOLEAN,
    IS_PRIVATE BOOLEAN,
    IS_ARCHIVED BOOLEAN,
    
    -- Channel metadata
    TOPIC VARIANT, -- JSON object with topic info
    PURPOSE VARIANT, -- JSON object with purpose info
    MEMBERS VARIANT, -- JSON array of member IDs
    MEMBER_COUNT NUMBER,
    
    -- Timestamps
    CREATED FLOAT,
    CREATED_DATETIME TIMESTAMP_LTZ GENERATED ALWAYS AS (
        TO_TIMESTAMP(CREATED)
    ),
    
    -- Raw API response
    RAW_DATA VARIANT NOT NULL,
    
    -- Processing metadata
    INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    LAST_UPDATED TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Raw Slack users data
CREATE TABLE IF NOT EXISTS SLACK_USERS_RAW (
    USER_ID VARCHAR(255) PRIMARY KEY,
    TEAM_ID VARCHAR(255),
    
    -- User information
    USERNAME VARCHAR(255),
    REAL_NAME VARCHAR(500),
    DISPLAY_NAME VARCHAR(255),
    EMAIL VARCHAR(255),
    
    -- User status
    IS_BOT BOOLEAN DEFAULT FALSE,
    IS_APP_USER BOOLEAN DEFAULT FALSE,
    IS_ADMIN BOOLEAN DEFAULT FALSE,
    IS_OWNER BOOLEAN DEFAULT FALSE,
    IS_DELETED BOOLEAN DEFAULT FALSE,
    
    -- Profile information
    PROFILE VARIANT, -- JSON object with full profile
    TIMEZONE VARCHAR(100),
    
    -- Raw API response
    RAW_DATA VARIANT NOT NULL,
    
    -- Processing metadata
    INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    LAST_UPDATED TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================================
-- 2. STRUCTURED SLACK DATA TABLES
-- =====================================================================

-- Structured conversations (threads)
CREATE TABLE IF NOT EXISTS STG_SLACK_CONVERSATIONS (
    CONVERSATION_ID VARCHAR(255) PRIMARY KEY,
    CHANNEL_ID VARCHAR(255) NOT NULL,
    THREAD_TS FLOAT NOT NULL,
    
    -- Conversation metadata
    CONVERSATION_TITLE VARCHAR(1000), -- Generated or extracted title
    CONVERSATION_TYPE VARCHAR(100), -- 'discussion', 'decision', 'announcement', 'question', etc.
    CONVERSATION_CATEGORY VARCHAR(255), -- 'product', 'sales', 'engineering', 'general', etc.
    
    -- Participants
    PARTICIPANT_COUNT NUMBER,
    PARTICIPANTS VARIANT, -- JSON array of participant user IDs
    INITIATOR_USER_ID VARCHAR(255),
    
    -- Timing
    START_TIME TIMESTAMP_LTZ,
    END_TIME TIMESTAMP_LTZ,
    DURATION_MINUTES NUMBER GENERATED ALWAYS AS (
        DATEDIFF('minute', START_TIME, END_TIME)
    ),
    
    -- Content analysis
    MESSAGE_COUNT NUMBER DEFAULT 0,
    TOTAL_WORD_COUNT NUMBER DEFAULT 0,
    UNIQUE_PARTICIPANTS NUMBER DEFAULT 0,
    
    -- Business context
    MENTIONS_CUSTOMERS VARIANT, -- JSON array of mentioned customer names
    MENTIONS_PRODUCTS VARIANT, -- JSON array of mentioned products
    MENTIONS_COMPETITORS VARIANT, -- JSON array of mentioned competitors
    CONTAINS_DECISIONS BOOLEAN DEFAULT FALSE,
    CONTAINS_ACTION_ITEMS BOOLEAN DEFAULT FALSE,
    
    -- AI-generated insights (Cortex)
    CONVERSATION_SUMMARY VARCHAR(4000), -- SNOWFLAKE.CORTEX.SUMMARIZE()
    SENTIMENT_SCORE FLOAT, -- SNOWFLAKE.CORTEX.SENTIMENT()
    KEY_TOPICS VARIANT, -- JSON array of extracted topics
    ACTION_ITEMS VARIANT, -- JSON array of extracted action items
    DECISIONS_MADE VARIANT, -- JSON array of decisions
    
    -- Knowledge extraction
    KNOWLEDGE_EXTRACTED BOOLEAN DEFAULT FALSE,
    EXTRACTED_INSIGHTS VARIANT, -- JSON array of knowledge insights
    BUSINESS_VALUE_SCORE FLOAT, -- 0.0 to 1.0 - how valuable for knowledge base
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768), -- Cortex embedding for semantic search
    AI_MEMORY_METADATA VARCHAR(16777216), -- JSON metadata for AI Memory
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
    CORTEX_PROCESSED_AT TIMESTAMP_LTZ,
    
    FOREIGN KEY (CHANNEL_ID) REFERENCES SLACK_CHANNELS_RAW(CHANNEL_ID)
);

-- Individual messages within conversations
CREATE TABLE IF NOT EXISTS STG_SLACK_MESSAGES (
    MESSAGE_ID VARCHAR(255) PRIMARY KEY,
    CONVERSATION_ID VARCHAR(255),
    CHANNEL_ID VARCHAR(255) NOT NULL,
    USER_ID VARCHAR(255),
    
    -- Message content
    MESSAGE_TEXT VARCHAR(16777216),
    CLEANED_TEXT VARCHAR(16777216), -- Text with mentions/formatting cleaned
    WORD_COUNT NUMBER,
    
    -- Message classification
    MESSAGE_TYPE VARCHAR(100), -- 'question', 'answer', 'decision', 'action_item', 'information'
    IS_THREAD_STARTER BOOLEAN DEFAULT FALSE,
    IS_REPLY BOOLEAN DEFAULT FALSE,
    
    -- Timing
    MESSAGE_DATETIME TIMESTAMP_LTZ,
    REPLY_TO_MESSAGE_ID VARCHAR(255), -- For threaded replies
    
    -- Engagement
    REACTION_COUNT NUMBER DEFAULT 0,
    REACTIONS VARIANT, -- JSON array of reactions
    REPLY_COUNT NUMBER DEFAULT 0,
    
    -- Content analysis
    MENTIONS_USERS VARIANT, -- JSON array of mentioned user IDs
    MENTIONS_CHANNELS VARIANT, -- JSON array of mentioned channels
    CONTAINS_URLS BOOLEAN DEFAULT FALSE,
    CONTAINS_FILES BOOLEAN DEFAULT FALSE,
    ATTACHED_FILES VARIANT, -- JSON array of file information
    
    -- Business entity extraction
    MENTIONS_CUSTOMERS VARIANT, -- Extracted customer mentions
    MENTIONS_PRODUCTS VARIANT, -- Extracted product mentions
    MENTIONS_COMPETITORS VARIANT, -- Extracted competitor mentions
    CONTAINS_PRICING_INFO BOOLEAN DEFAULT FALSE,
    CONTAINS_TECHNICAL_INFO BOOLEAN DEFAULT FALSE,
    
    -- AI processing
    SENTIMENT_SCORE FLOAT, -- Message-level sentiment
    IMPORTANCE_SCORE FLOAT, -- 0.0 to 1.0 - importance for knowledge base
    EXTRACTED_ENTITIES VARIANT, -- JSON array of named entities
    
    -- Vector embedding for semantic search
    MESSAGE_EMBEDDING VECTOR(FLOAT, 768), -- Cortex embedding
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (CONVERSATION_ID) REFERENCES STG_SLACK_CONVERSATIONS(CONVERSATION_ID),
    FOREIGN KEY (CHANNEL_ID) REFERENCES SLACK_CHANNELS_RAW(CHANNEL_ID),
    FOREIGN KEY (USER_ID) REFERENCES SLACK_USERS_RAW(USER_ID)
);

-- Slack channels with enriched information
CREATE TABLE IF NOT EXISTS STG_SLACK_CHANNELS (
    CHANNEL_ID VARCHAR(255) PRIMARY KEY,
    CHANNEL_NAME VARCHAR(255),
    CHANNEL_TYPE VARCHAR(100),
    
    -- Channel purpose and description
    CHANNEL_PURPOSE VARCHAR(2000),
    CHANNEL_TOPIC VARCHAR(2000),
    BUSINESS_FUNCTION VARCHAR(255), -- 'sales', 'engineering', 'marketing', 'general', etc.
    
    -- Channel activity
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    MEMBER_COUNT NUMBER,
    MESSAGE_COUNT_TOTAL NUMBER DEFAULT 0,
    LAST_MESSAGE_DATE DATE,
    
    -- Channel classification
    IS_CUSTOMER_RELATED BOOLEAN DEFAULT FALSE,
    IS_PRODUCT_RELATED BOOLEAN DEFAULT FALSE,
    IS_INTERNAL_DISCUSSION BOOLEAN DEFAULT TRUE,
    KNOWLEDGE_VALUE_SCORE FLOAT, -- How valuable this channel is for knowledge
    
    -- Members and participation
    ACTIVE_MEMBERS VARIANT, -- JSON array of active member IDs
    TOP_CONTRIBUTORS VARIANT, -- JSON array of most active contributors
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Slack users with enriched information
CREATE TABLE IF NOT EXISTS STG_SLACK_USERS (
    USER_ID VARCHAR(255) PRIMARY KEY,
    USERNAME VARCHAR(255),
    REAL_NAME VARCHAR(500),
    EMAIL VARCHAR(255),
    
    -- Employee mapping
    EMPLOYEE_ID VARCHAR(255), -- Link to FOUNDATIONAL_KNOWLEDGE.EMPLOYEES
    DEPARTMENT VARCHAR(255),
    JOB_TITLE VARCHAR(255),
    
    -- User activity
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    LAST_SEEN_DATE DATE,
    MESSAGE_COUNT_TOTAL NUMBER DEFAULT 0,
    CONVERSATION_COUNT_TOTAL NUMBER DEFAULT 0,
    
    -- Communication patterns
    MOST_ACTIVE_CHANNELS VARIANT, -- JSON array of channel IDs
    COMMUNICATION_STYLE VARCHAR(100), -- 'frequent', 'moderate', 'occasional'
    EXPERTISE_AREAS VARIANT, -- JSON array of inferred expertise areas
    
    -- Knowledge contribution
    KNOWLEDGE_CONTRIBUTIONS NUMBER DEFAULT 0, -- Count of valuable knowledge shared
    KNOWLEDGE_QUALITY_SCORE FLOAT, -- 0.0 to 1.0 - quality of knowledge shared
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (EMPLOYEE_ID) REFERENCES FOUNDATIONAL_KNOWLEDGE.EMPLOYEES(EMPLOYEE_ID)
);

-- =====================================================================
-- 3. KNOWLEDGE EXTRACTION TABLES
-- =====================================================================

-- Extracted knowledge insights from Slack conversations
CREATE TABLE IF NOT EXISTS SLACK_KNOWLEDGE_INSIGHTS (
    INSIGHT_ID VARCHAR(255) PRIMARY KEY,
    CONVERSATION_ID VARCHAR(255),
    MESSAGE_ID VARCHAR(255),
    
    -- Insight classification
    INSIGHT_TYPE VARCHAR(100), -- 'customer_feedback', 'product_insight', 'process_improvement', etc.
    INSIGHT_CATEGORY VARCHAR(255), -- 'sales', 'product', 'engineering', 'customer_success'
    CONFIDENCE_SCORE FLOAT, -- 0.0 to 1.0 - AI confidence in the insight
    
    -- Insight content
    INSIGHT_TITLE VARCHAR(500),
    INSIGHT_DESCRIPTION VARCHAR(4000),
    INSIGHT_SUMMARY VARCHAR(1000),
    
    -- Business context
    RELATED_CUSTOMERS VARIANT, -- JSON array of related customer IDs
    RELATED_PRODUCTS VARIANT, -- JSON array of related product IDs
    RELATED_EMPLOYEES VARIANT, -- JSON array of involved employee IDs
    
    -- Actionability
    IS_ACTIONABLE BOOLEAN DEFAULT FALSE,
    SUGGESTED_ACTIONS VARIANT, -- JSON array of suggested actions
    BUSINESS_IMPACT VARCHAR(50), -- 'high', 'medium', 'low'
    
    -- Validation
    HUMAN_VALIDATED BOOLEAN DEFAULT FALSE,
    VALIDATED_BY_USER_ID VARCHAR(255),
    VALIDATED_AT TIMESTAMP_LTZ,
    VALIDATION_NOTES VARCHAR(2000),
    
    -- Knowledge base integration
    ADDED_TO_KNOWLEDGE_BASE BOOLEAN DEFAULT FALSE,
    KNOWLEDGE_BASE_DOCUMENT_ID VARCHAR(255),
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    EXTRACTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255) DEFAULT 'system',
    
    FOREIGN KEY (CONVERSATION_ID) REFERENCES STG_SLACK_CONVERSATIONS(CONVERSATION_ID),
    FOREIGN KEY (MESSAGE_ID) REFERENCES STG_SLACK_MESSAGES(MESSAGE_ID),
    FOREIGN KEY (VALIDATED_BY_USER_ID) REFERENCES STG_SLACK_USERS(USER_ID)
);

-- =====================================================================
-- 4. DATA TRANSFORMATION PROCEDURES
-- =====================================================================

-- Transform raw Slack messages to structured format
CREATE OR REPLACE PROCEDURE TRANSFORM_RAW_SLACK_MESSAGES()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    
    -- Transform raw messages to structured format
    INSERT INTO STG_SLACK_MESSAGES (
        MESSAGE_ID,
        CHANNEL_ID,
        USER_ID,
        MESSAGE_TEXT,
        CLEANED_TEXT,
        WORD_COUNT,
        MESSAGE_DATETIME,
        IS_THREAD_STARTER,
        IS_REPLY,
        REPLY_TO_MESSAGE_ID,
        REACTION_COUNT,
        REACTIONS,
        MENTIONS_USERS,
        MENTIONS_CHANNELS,
        CONTAINS_URLS,
        CONTAINS_FILES,
        ATTACHED_FILES
    )
    SELECT 
        MESSAGE_ID,
        CHANNEL_ID,
        USER_ID,
        MESSAGE_TEXT,
        -- Clean text by removing Slack formatting
        REGEXP_REPLACE(
            REGEXP_REPLACE(MESSAGE_TEXT, '<@[^>]+>', ''),
            '<#[^>]+>', ''
        ) AS CLEANED_TEXT,
        ARRAY_SIZE(SPLIT(MESSAGE_TEXT, ' ')) AS WORD_COUNT,
        MESSAGE_DATETIME,
        CASE WHEN THREAD_TS IS NULL OR THREAD_TS = TIMESTAMP_SLACK THEN TRUE ELSE FALSE END AS IS_THREAD_STARTER,
        CASE WHEN THREAD_TS IS NOT NULL AND THREAD_TS != TIMESTAMP_SLACK THEN TRUE ELSE FALSE END AS IS_REPLY,
        CASE WHEN THREAD_TS IS NOT NULL AND THREAD_TS != TIMESTAMP_SLACK THEN 
            CONCAT(CHANNEL_ID, '_', THREAD_TS) 
        ELSE NULL END AS REPLY_TO_MESSAGE_ID,
        ARRAY_SIZE(COALESCE(REACTIONS, PARSE_JSON('[]'))) AS REACTION_COUNT,
        REACTIONS,
        RAW_DATA:mentions AS MENTIONS_USERS,
        RAW_DATA:channel_mentions AS MENTIONS_CHANNELS,
        CASE WHEN CONTAINS(MESSAGE_TEXT, 'http') THEN TRUE ELSE FALSE END AS CONTAINS_URLS,
        CASE WHEN FILES IS NOT NULL AND ARRAY_SIZE(FILES) > 0 THEN TRUE ELSE FALSE END AS CONTAINS_FILES,
        FILES AS ATTACHED_FILES
    FROM SLACK_MESSAGES_RAW
    WHERE PROCESSED = FALSE
    AND MESSAGE_TEXT IS NOT NULL
    AND MESSAGE_TEXT != '';
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count 
    FROM STG_SLACK_MESSAGES
    WHERE CREATED_AT >= CURRENT_TIMESTAMP - INTERVAL '1 HOUR';
    
    -- Mark raw messages as processed
    UPDATE SLACK_MESSAGES_RAW 
    SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP
    WHERE PROCESSED = FALSE;
    
    -- Generate result message
    SET result_message = 'Processed ' || processed_count || ' Slack messages';
    
    -- Output the result
    SELECT result_message;
END;
$$;

-- Create conversations from threaded messages
CREATE OR REPLACE PROCEDURE CREATE_SLACK_CONVERSATIONS()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    
    -- Create conversation records from thread starters
    INSERT INTO STG_SLACK_CONVERSATIONS (
        CONVERSATION_ID,
        CHANNEL_ID,
        THREAD_TS,
        CONVERSATION_TITLE,
        PARTICIPANT_COUNT,
        PARTICIPANTS,
        INITIATOR_USER_ID,
        START_TIME,
        END_TIME,
        MESSAGE_COUNT,
        TOTAL_WORD_COUNT,
        UNIQUE_PARTICIPANTS
    )
    SELECT 
        CONCAT(CHANNEL_ID, '_', THREAD_TS) AS CONVERSATION_ID,
        CHANNEL_ID,
        THREAD_TS,
        -- Generate conversation title from first message
        CASE 
            WHEN LENGTH(CLEANED_TEXT) > 100 THEN 
                SUBSTR(CLEANED_TEXT, 1, 97) || '...'
            ELSE CLEANED_TEXT
        END AS CONVERSATION_TITLE,
        COUNT(DISTINCT USER_ID) AS PARTICIPANT_COUNT,
        ARRAY_AGG(DISTINCT USER_ID) AS PARTICIPANTS,
        FIRST_VALUE(USER_ID) OVER (PARTITION BY CHANNEL_ID, THREAD_TS ORDER BY MESSAGE_DATETIME) AS INITIATOR_USER_ID,
        MIN(MESSAGE_DATETIME) AS START_TIME,
        MAX(MESSAGE_DATETIME) AS END_TIME,
        COUNT(*) AS MESSAGE_COUNT,
        SUM(WORD_COUNT) AS TOTAL_WORD_COUNT,
        COUNT(DISTINCT USER_ID) AS UNIQUE_PARTICIPANTS
    FROM STG_SLACK_MESSAGES
    WHERE CONVERSATION_ID IS NULL
    GROUP BY CHANNEL_ID, THREAD_TS, CLEANED_TEXT
    HAVING COUNT(*) >= 2; -- Only create conversations with multiple messages
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count 
    FROM STG_SLACK_CONVERSATIONS
    WHERE CREATED_AT >= CURRENT_TIMESTAMP - INTERVAL '1 HOUR';
    
    -- Update messages with conversation IDs
    UPDATE STG_SLACK_MESSAGES m
    SET CONVERSATION_ID = CONCAT(m.CHANNEL_ID, '_', 
        COALESCE(
            (SELECT THREAD_TS FROM SLACK_MESSAGES_RAW r WHERE r.MESSAGE_ID = m.MESSAGE_ID),
            (SELECT TIMESTAMP_SLACK FROM SLACK_MESSAGES_RAW r WHERE r.MESSAGE_ID = m.MESSAGE_ID)
        )
    )
    WHERE CONVERSATION_ID IS NULL;
    
    -- Generate result message
    SET result_message = 'Created ' || processed_count || ' Slack conversations';
    
    -- Output the result
    SELECT result_message;
END;
$$;

-- Extract knowledge insights from conversations using Cortex AI
CREATE OR REPLACE PROCEDURE EXTRACT_SLACK_KNOWLEDGE_INSIGHTS()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
    conversation_cursor CURSOR FOR 
        SELECT CONVERSATION_ID, CONVERSATION_SUMMARY, KEY_TOPICS, CHANNEL_ID
        FROM STG_SLACK_CONVERSATIONS 
        WHERE KNOWLEDGE_EXTRACTED = FALSE 
        AND BUSINESS_VALUE_SCORE > 0.6;
BEGIN
    
    FOR conversation IN conversation_cursor LOOP
        -- Use Cortex AI to extract insights
        INSERT INTO SLACK_KNOWLEDGE_INSIGHTS (
            INSIGHT_ID,
            CONVERSATION_ID,
            INSIGHT_TYPE,
            INSIGHT_CATEGORY,
            CONFIDENCE_SCORE,
            INSIGHT_TITLE,
            INSIGHT_DESCRIPTION,
            INSIGHT_SUMMARY,
            IS_ACTIONABLE,
            BUSINESS_IMPACT,
            AI_MEMORY_EMBEDDING
        )
        SELECT 
            CONCAT('insight_', conversation.CONVERSATION_ID, '_', ROW_NUMBER() OVER (ORDER BY confidence DESC)) AS INSIGHT_ID,
            conversation.CONVERSATION_ID,
            insight_type,
            insight_category,
            confidence,
            insight_title,
            insight_description,
            insight_summary,
            is_actionable,
            business_impact,
            SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', insight_description) AS AI_MEMORY_EMBEDDING
        FROM (
            SELECT 
                'customer_feedback' AS insight_type,
                'customer_success' AS insight_category,
                0.8 AS confidence,
                'Customer Feedback from Slack' AS insight_title,
                conversation.CONVERSATION_SUMMARY AS insight_description,
                SUBSTR(conversation.CONVERSATION_SUMMARY, 1, 200) AS insight_summary,
                TRUE AS is_actionable,
                'medium' AS business_impact
            WHERE CONTAINS(UPPER(conversation.CONVERSATION_SUMMARY), 'CUSTOMER')
        );
        
        SET processed_count = processed_count + 1;
    END FOR;
    
    -- Mark conversations as processed
    UPDATE STG_SLACK_CONVERSATIONS 
    SET KNOWLEDGE_EXTRACTED = TRUE
    WHERE KNOWLEDGE_EXTRACTED = FALSE 
    AND BUSINESS_VALUE_SCORE > 0.6;
    
    -- Generate result message
    SET result_message = 'Extracted insights from ' || processed_count || ' conversations';
    
    -- Output the result
    SELECT result_message;
END;
$$;

-- =====================================================================
-- 5. CORTEX AI PROCESSING PROCEDURES
-- =====================================================================

-- Process conversations with Snowflake Cortex AI
CREATE OR REPLACE PROCEDURE PROCESS_SLACK_CONVERSATIONS_WITH_CORTEX()
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    
    -- Update conversations with Cortex AI analysis
    UPDATE STG_SLACK_CONVERSATIONS
    SET 
        CONVERSATION_SUMMARY = SNOWFLAKE.CORTEX.SUMMARIZE(
            (SELECT LISTAGG(MESSAGE_TEXT, ' ') 
             FROM STG_SLACK_MESSAGES 
             WHERE CONVERSATION_ID = STG_SLACK_CONVERSATIONS.CONVERSATION_ID)
        ),
        SENTIMENT_SCORE = SNOWFLAKE.CORTEX.SENTIMENT(
            (SELECT LISTAGG(MESSAGE_TEXT, ' ') 
             FROM STG_SLACK_MESSAGES 
             WHERE CONVERSATION_ID = STG_SLACK_CONVERSATIONS.CONVERSATION_ID)
        ),
        AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2',
            CONVERSATION_TITLE || ' ' || 
            (SELECT LISTAGG(MESSAGE_TEXT, ' ') 
             FROM STG_SLACK_MESSAGES 
             WHERE CONVERSATION_ID = STG_SLACK_CONVERSATIONS.CONVERSATION_ID)
        ),
        BUSINESS_VALUE_SCORE = CASE 
            WHEN CONTAINS_DECISIONS OR CONTAINS_ACTION_ITEMS THEN 0.9
            WHEN PARTICIPANT_COUNT > 3 AND MESSAGE_COUNT > 5 THEN 0.7
            WHEN DURATION_MINUTES > 60 THEN 0.6
            ELSE 0.4
        END,
        PROCESSED_BY_CORTEX = TRUE,
        CORTEX_PROCESSED_AT = CURRENT_TIMESTAMP,
        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP
    WHERE PROCESSED_BY_CORTEX = FALSE;
    
    -- Count processed records
    SELECT COUNT(*) INTO processed_count 
    FROM STG_SLACK_CONVERSATIONS
    WHERE PROCESSED_BY_CORTEX = TRUE
    AND CORTEX_PROCESSED_AT >= CURRENT_TIMESTAMP - INTERVAL '1 HOUR';
    
    -- Generate result message
    SET result_message = 'Processed ' || processed_count || ' conversations with Cortex AI';
    
    -- Output the result
    SELECT result_message;
END;
$$;

-- =====================================================================
-- 6. INTEGRATION VIEWS
-- =====================================================================

-- Comprehensive Slack knowledge view for search
CREATE OR REPLACE VIEW VW_SLACK_KNOWLEDGE_SEARCH AS
SELECT 
    'SLACK_CONVERSATION' AS KNOWLEDGE_TYPE,
    CONVERSATION_ID AS RECORD_ID,
    CONVERSATION_TITLE AS TITLE,
    CONVERSATION_SUMMARY AS DESCRIPTION,
    CONCAT('Channel: ', sc.CHANNEL_NAME, ' | Participants: ', PARTICIPANT_COUNT) AS CONTACT_INFO,
    AI_MEMORY_EMBEDDING,
    AI_MEMORY_METADATA,
    UPDATED_AT
FROM STG_SLACK_CONVERSATIONS conv
JOIN STG_SLACK_CHANNELS sc ON conv.CHANNEL_ID = sc.CHANNEL_ID
WHERE BUSINESS_VALUE_SCORE > 0.5

UNION ALL

SELECT 
    'SLACK_INSIGHT' AS KNOWLEDGE_TYPE,
    INSIGHT_ID AS RECORD_ID,
    INSIGHT_TITLE AS TITLE,
    INSIGHT_DESCRIPTION AS DESCRIPTION,
    INSIGHT_CATEGORY AS CONTACT_INFO,
    AI_MEMORY_EMBEDDING,
    AI_MEMORY_METADATA,
    EXTRACTED_AT AS UPDATED_AT
FROM SLACK_KNOWLEDGE_INSIGHTS
WHERE HUMAN_VALIDATED = TRUE OR CONFIDENCE_SCORE > 0.8;

-- Slack activity analytics view
CREATE OR REPLACE VIEW VW_SLACK_ACTIVITY_ANALYTICS AS
SELECT 
    sc.CHANNEL_NAME,
    sc.BUSINESS_FUNCTION,
    COUNT(DISTINCT conv.CONVERSATION_ID) AS CONVERSATION_COUNT,
    COUNT(DISTINCT msg.MESSAGE_ID) AS MESSAGE_COUNT,
    COUNT(DISTINCT msg.USER_ID) AS UNIQUE_PARTICIPANTS,
    AVG(conv.BUSINESS_VALUE_SCORE) AS AVG_BUSINESS_VALUE,
    COUNT(DISTINCT ins.INSIGHT_ID) AS INSIGHTS_EXTRACTED,
    DATE_TRUNC('month', msg.MESSAGE_DATETIME) AS ACTIVITY_MONTH
FROM STG_SLACK_CHANNELS sc
LEFT JOIN STG_SLACK_CONVERSATIONS conv ON sc.CHANNEL_ID = conv.CHANNEL_ID
LEFT JOIN STG_SLACK_MESSAGES msg ON conv.CONVERSATION_ID = msg.CONVERSATION_ID
LEFT JOIN SLACK_KNOWLEDGE_INSIGHTS ins ON conv.CONVERSATION_ID = ins.CONVERSATION_ID
WHERE msg.MESSAGE_DATETIME >= DATEADD('month', -12, CURRENT_DATE())
GROUP BY 
    sc.CHANNEL_NAME,
    sc.BUSINESS_FUNCTION,
    DATE_TRUNC('month', msg.MESSAGE_DATETIME)
ORDER BY ACTIVITY_MONTH DESC, MESSAGE_COUNT DESC;

-- =====================================================================
-- 7. AUTOMATED TASKS
-- =====================================================================

-- Task to transform raw Slack data every 15 minutes
CREATE OR REPLACE TASK TASK_TRANSFORM_SLACK_MESSAGES
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0,15,30,45 * * * * UTC'
    COMMENT = 'Transform raw Slack messages to structured format'
AS
    CALL TRANSFORM_RAW_SLACK_MESSAGES();

-- Task to create conversations every 30 minutes
CREATE OR REPLACE TASK TASK_CREATE_SLACK_CONVERSATIONS
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0,30 * * * * UTC'
    COMMENT = 'Create conversation records from Slack messages'
AS
    CALL CREATE_SLACK_CONVERSATIONS();

-- Task to process conversations with Cortex AI every hour
CREATE OR REPLACE TASK TASK_PROCESS_SLACK_CORTEX
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 * * * * UTC'
    COMMENT = 'Process Slack conversations with Cortex AI'
AS
    CALL PROCESS_SLACK_CONVERSATIONS_WITH_CORTEX();

-- Task to extract knowledge insights every 2 hours
CREATE OR REPLACE TASK TASK_EXTRACT_SLACK_INSIGHTS
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 */2 * * * UTC'
    COMMENT = 'Extract knowledge insights from Slack conversations'
AS
    CALL EXTRACT_SLACK_KNOWLEDGE_INSIGHTS();

-- =====================================================================
-- 8. INDEXES AND PERFORMANCE OPTIMIZATION
-- =====================================================================

-- Create indexes for better query performance
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_SLACK_MESSAGES_CHANNEL_TIME ON STG_SLACK_MESSAGES(CHANNEL_ID, MESSAGE_DATETIME);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_SLACK_MESSAGES_USER ON STG_SLACK_MESSAGES(USER_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_SLACK_CONVERSATIONS_CHANNEL ON STG_SLACK_CONVERSATIONS(CHANNEL_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_SLACK_CONVERSATIONS_VALUE ON STG_SLACK_CONVERSATIONS(BUSINESS_VALUE_SCORE);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_SLACK_INSIGHTS_TYPE ON SLACK_KNOWLEDGE_INSIGHTS(INSIGHT_TYPE);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_SLACK_INSIGHTS_CONFIDENCE ON SLACK_KNOWLEDGE_INSIGHTS(CONFIDENCE_SCORE);
-- 
-- =====================================================================
-- END OF SLACK INTEGRATION SCHEMA
-- ===================================================================== 