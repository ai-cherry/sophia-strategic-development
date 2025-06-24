-- =====================================================================
-- AI_MEMORY Schema - Core Memory Management Tables
-- =====================================================================
-- 
-- This script creates the AI_MEMORY schema for storing metadata of memories,
-- conversation history, categories, and tags while leveraging business tables
-- for actual embedding storage.
-- 
-- Features:
-- - Memory metadata tracking
-- - Conversation history management
-- - Category and tag organization
-- - Integration with business table embeddings
-- 
-- Usage: Execute in SOPHIA_AI_DEV database
-- =====================================================================

-- Set context for DEV environment
USE DATABASE SOPHIA_AI_DEV;
CREATE SCHEMA IF NOT EXISTS AI_MEMORY;
USE SCHEMA AI_MEMORY;

-- =====================================================================
-- 1. CORE MEMORY MANAGEMENT TABLES
-- =====================================================================

-- Memory records table for storing metadata of memories
CREATE TABLE IF NOT EXISTS MEMORY_RECORDS (
    MEMORY_ID VARCHAR(255) PRIMARY KEY,
    CONTENT_SUMMARY VARCHAR(4000), -- Summary of the memory content
    CATEGORY VARCHAR(100) NOT NULL, -- Memory category (e.g., 'HUBSPOT_DEAL_ANALYSIS', 'GONG_CALL_INSIGHT')
    SUBCATEGORY VARCHAR(100), -- Optional subcategory for finer classification
    
    -- Business context references
    BUSINESS_TABLE_NAME VARCHAR(100), -- Table where actual embedding is stored (e.g., 'STG_HUBSPOT_DEALS')
    BUSINESS_RECORD_ID VARCHAR(255), -- ID of the business record containing the embedding
    EMBEDDING_COLUMN VARCHAR(100) DEFAULT 'ai_memory_embedding', -- Column containing the embedding
    
    -- Memory metadata
    IMPORTANCE_SCORE FLOAT DEFAULT 0.5, -- Importance score (0.0 to 1.0)
    CONFIDENCE_SCORE FLOAT DEFAULT 0.5, -- Confidence score (0.0 to 1.0)
    ACCESS_COUNT NUMBER DEFAULT 0, -- Number of times this memory has been accessed
    LAST_ACCESSED_AT TIMESTAMP_NTZ, -- Last time this memory was accessed
    
    -- Context and relationships
    RELATED_DEAL_ID VARCHAR(255), -- Associated HubSpot deal ID
    RELATED_CONTACT_ID VARCHAR(255), -- Associated HubSpot contact ID
    RELATED_CALL_ID VARCHAR(255), -- Associated Gong call ID
    RELATED_USER_ID VARCHAR(255), -- Associated user/agent ID
    
    -- Auto-detection flags
    AUTO_DETECTED BOOLEAN DEFAULT FALSE, -- Whether this memory was auto-detected
    DETECTION_METHOD VARCHAR(100), -- Method used for auto-detection
    
    -- Metadata
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255), -- User or system that created this memory
    
    -- Additional context
    CONTEXT_METADATA VARIANT -- JSON metadata for additional context
);

-- Memory categories table for organizing memory types
CREATE TABLE IF NOT EXISTS MEMORY_CATEGORIES (
    CATEGORY_ID VARCHAR(100) PRIMARY KEY,
    CATEGORY_NAME VARCHAR(255) NOT NULL,
    CATEGORY_DESCRIPTION VARCHAR(1000),
    PARENT_CATEGORY_ID VARCHAR(100), -- For hierarchical categories
    
    -- Category configuration
    DEFAULT_IMPORTANCE_SCORE FLOAT DEFAULT 0.5,
    AUTO_DETECTION_ENABLED BOOLEAN DEFAULT TRUE,
    RETENTION_DAYS NUMBER, -- How long to keep memories in this category (NULL = forever)
    
    -- Business table mapping
    PREFERRED_BUSINESS_TABLE VARCHAR(100), -- Preferred table for storing embeddings
    PREFERRED_EMBEDDING_COLUMN VARCHAR(100) DEFAULT 'ai_memory_embedding',
    
    -- Metadata
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (PARENT_CATEGORY_ID) REFERENCES MEMORY_CATEGORIES(CATEGORY_ID)
);

-- Memory tags table for flexible tagging system
CREATE TABLE IF NOT EXISTS MEMORY_TAGS (
    TAG_ID VARCHAR(100) PRIMARY KEY,
    TAG_NAME VARCHAR(255) NOT NULL UNIQUE,
    TAG_DESCRIPTION VARCHAR(1000),
    TAG_COLOR VARCHAR(7), -- Hex color code for UI display
    
    -- Tag statistics
    USAGE_COUNT NUMBER DEFAULT 0, -- How many memories use this tag
    LAST_USED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

-- Memory-tag relationship table (many-to-many)
CREATE TABLE IF NOT EXISTS MEMORY_TAG_RELATIONSHIPS (
    MEMORY_ID VARCHAR(255),
    TAG_ID VARCHAR(100),
    
    -- Relationship metadata
    RELEVANCE_SCORE FLOAT DEFAULT 1.0, -- How relevant this tag is to the memory
    ASSIGNED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    ASSIGNED_BY VARCHAR(255), -- User or system that assigned this tag
    AUTO_ASSIGNED BOOLEAN DEFAULT FALSE, -- Whether this tag was auto-assigned
    
    PRIMARY KEY (MEMORY_ID, TAG_ID),
    FOREIGN KEY (MEMORY_ID) REFERENCES MEMORY_RECORDS(MEMORY_ID) ON DELETE CASCADE,
    FOREIGN KEY (TAG_ID) REFERENCES MEMORY_TAGS(TAG_ID) ON DELETE CASCADE
);

-- =====================================================================
-- 2. CONVERSATION HISTORY MANAGEMENT
-- =====================================================================

-- Conversation history table for tracking AI interactions
CREATE TABLE IF NOT EXISTS CONVERSATION_HISTORY (
    CONVERSATION_ID VARCHAR(255) PRIMARY KEY,
    SESSION_ID VARCHAR(255), -- Group related conversations
    
    -- Conversation content
    USER_MESSAGE VARCHAR(16777216), -- User's input message
    AI_RESPONSE VARCHAR(16777216), -- AI's response
    CONVERSATION_SUMMARY VARCHAR(4000), -- Summary of the conversation
    
    -- Context and metadata
    CONVERSATION_TYPE VARCHAR(100), -- Type of conversation (e.g., 'MEMORY_RECALL', 'DEAL_ANALYSIS')
    AGENT_TYPE VARCHAR(100), -- Which agent handled this conversation
    USER_ID VARCHAR(255), -- User who initiated the conversation
    
    -- Memory integration
    MEMORIES_RECALLED VARIANT, -- JSON array of memory IDs that were recalled
    NEW_MEMORIES_CREATED VARIANT, -- JSON array of new memory IDs created
    MEMORY_EFFECTIVENESS_SCORE FLOAT, -- How effective the recalled memories were
    
    -- Performance metrics
    RESPONSE_TIME_MS NUMBER, -- Response time in milliseconds
    TOKEN_COUNT NUMBER, -- Number of tokens used
    COST_ESTIMATE FLOAT, -- Estimated cost of the conversation
    
    -- Quality metrics
    USER_SATISFACTION_SCORE FLOAT, -- User satisfaction (if available)
    RELEVANCE_SCORE FLOAT, -- Relevance of the response
    
    -- Metadata
    STARTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    COMPLETED_AT TIMESTAMP_NTZ,
    DURATION_SECONDS NUMBER, -- Calculated duration
    
    -- Additional context
    CONTEXT_METADATA VARIANT -- JSON metadata for additional context
);

-- Conversation feedback table for learning and improvement
CREATE TABLE IF NOT EXISTS CONVERSATION_FEEDBACK (
    FEEDBACK_ID VARCHAR(255) PRIMARY KEY,
    CONVERSATION_ID VARCHAR(255) NOT NULL,
    
    -- Feedback details
    FEEDBACK_TYPE VARCHAR(50), -- 'POSITIVE', 'NEGATIVE', 'SUGGESTION'
    FEEDBACK_SCORE NUMBER, -- Numeric score (1-5 or 1-10)
    FEEDBACK_TEXT VARCHAR(4000), -- Detailed feedback
    
    -- Feedback context
    FEEDBACK_CATEGORY VARCHAR(100), -- Category of feedback (e.g., 'ACCURACY', 'RELEVANCE', 'SPEED')
    PROVIDED_BY VARCHAR(255), -- User who provided feedback
    PROVIDED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Follow-up actions
    ACTION_TAKEN VARCHAR(1000), -- What action was taken based on this feedback
    ACTION_TAKEN_BY VARCHAR(255), -- Who took the action
    ACTION_TAKEN_AT TIMESTAMP_NTZ,
    
    FOREIGN KEY (CONVERSATION_ID) REFERENCES CONVERSATION_HISTORY(CONVERSATION_ID)
);

-- =====================================================================
-- 3. MEMORY ANALYTICS AND INSIGHTS
-- =====================================================================

-- Memory usage analytics table
CREATE TABLE IF NOT EXISTS MEMORY_USAGE_ANALYTICS (
    ANALYTICS_ID VARCHAR(255) PRIMARY KEY,
    MEMORY_ID VARCHAR(255) NOT NULL,
    
    -- Usage metrics
    ACCESS_DATE DATE,
    ACCESS_COUNT_DAILY NUMBER DEFAULT 0,
    UNIQUE_USERS_DAILY NUMBER DEFAULT 0,
    
    -- Performance metrics
    AVG_RELEVANCE_SCORE FLOAT, -- Average relevance score for the day
    AVG_RESPONSE_TIME_MS NUMBER, -- Average response time when this memory was used
    
    -- Context metrics
    TOP_QUERY_TYPES VARIANT, -- JSON array of most common query types that accessed this memory
    TOP_USER_ROLES VARIANT, -- JSON array of user roles that accessed this memory most
    
    -- Metadata
    CALCULATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (MEMORY_ID) REFERENCES MEMORY_RECORDS(MEMORY_ID),
    UNIQUE (MEMORY_ID, ACCESS_DATE)
);

-- System performance metrics table
CREATE TABLE IF NOT EXISTS SYSTEM_PERFORMANCE_METRICS (
    METRIC_ID VARCHAR(255) PRIMARY KEY,
    METRIC_DATE DATE,
    
    -- Memory system metrics
    TOTAL_MEMORIES NUMBER,
    TOTAL_ACTIVE_MEMORIES NUMBER,
    TOTAL_CATEGORIES NUMBER,
    TOTAL_TAGS NUMBER,
    
    -- Usage metrics
    DAILY_MEMORY_ACCESSES NUMBER,
    DAILY_NEW_MEMORIES NUMBER,
    DAILY_CONVERSATIONS NUMBER,
    UNIQUE_DAILY_USERS NUMBER,
    
    -- Performance metrics
    AVG_MEMORY_RECALL_TIME_MS NUMBER,
    AVG_EMBEDDING_GENERATION_TIME_MS NUMBER,
    AVG_VECTOR_SEARCH_TIME_MS NUMBER,
    
    -- Quality metrics
    AVG_USER_SATISFACTION_SCORE FLOAT,
    AVG_MEMORY_RELEVANCE_SCORE FLOAT,
    
    -- Business impact metrics
    HUBSPOT_MEMORIES_ACCESSED NUMBER,
    GONG_MEMORIES_ACCESSED NUMBER,
    DEAL_INSIGHTS_GENERATED NUMBER,
    CALL_INSIGHTS_GENERATED NUMBER,
    
    -- Metadata
    CALCULATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    UNIQUE (METRIC_DATE)
);

-- =====================================================================
-- 4. STORED PROCEDURES FOR MEMORY MANAGEMENT
-- =====================================================================

-- Procedure to clean up old memories based on retention policies
CREATE OR REPLACE PROCEDURE CLEANUP_OLD_MEMORIES()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    cleaned_count NUMBER DEFAULT 0;
BEGIN
    
    -- Delete memories that exceed retention period for their category
    DELETE FROM MEMORY_RECORDS mr
    WHERE EXISTS (
        SELECT 1 FROM MEMORY_CATEGORIES mc 
        WHERE mc.CATEGORY_ID = mr.CATEGORY 
        AND mc.RETENTION_DAYS IS NOT NULL
        AND mr.CREATED_AT < DATEADD('day', -mc.RETENTION_DAYS, CURRENT_TIMESTAMP())
    );
    
    GET DIAGNOSTICS cleaned_count = ROW_COUNT;
    
    -- Clean up orphaned tag relationships
    DELETE FROM MEMORY_TAG_RELATIONSHIPS 
    WHERE MEMORY_ID NOT IN (SELECT MEMORY_ID FROM MEMORY_RECORDS);
    
    -- Update tag usage counts
    UPDATE MEMORY_TAGS 
    SET USAGE_COUNT = (
        SELECT COUNT(*) 
        FROM MEMORY_TAG_RELATIONSHIPS mtr 
        WHERE mtr.TAG_ID = MEMORY_TAGS.TAG_ID
    );
    
    RETURN 'Cleaned up ' || cleaned_count || ' old memories';
    
EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error cleaning up memories: ' || SQLERRM;
END;
$$;

-- Procedure to calculate daily analytics
CREATE OR REPLACE PROCEDURE CALCULATE_DAILY_MEMORY_ANALYTICS(analytics_date DATE DEFAULT CURRENT_DATE())
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    processed_memories NUMBER DEFAULT 0;
BEGIN
    
    -- Calculate memory usage analytics for the specified date
    INSERT INTO MEMORY_USAGE_ANALYTICS (
        ANALYTICS_ID,
        MEMORY_ID,
        ACCESS_DATE,
        ACCESS_COUNT_DAILY,
        UNIQUE_USERS_DAILY,
        AVG_RELEVANCE_SCORE,
        AVG_RESPONSE_TIME_MS,
        TOP_QUERY_TYPES,
        TOP_USER_ROLES
    )
    SELECT 
        MEMORY_ID || '_' || analytics_date AS ANALYTICS_ID,
        mr.MEMORY_ID,
        analytics_date AS ACCESS_DATE,
        
        -- Count accesses from conversation history
        COUNT(ch.CONVERSATION_ID) AS ACCESS_COUNT_DAILY,
        COUNT(DISTINCT ch.USER_ID) AS UNIQUE_USERS_DAILY,
        AVG(ch.RELEVANCE_SCORE) AS AVG_RELEVANCE_SCORE,
        AVG(ch.RESPONSE_TIME_MS) AS AVG_RESPONSE_TIME_MS,
        
        -- Aggregate query types and user roles (simplified)
        ARRAY_AGG(DISTINCT ch.CONVERSATION_TYPE) AS TOP_QUERY_TYPES,
        ARRAY_AGG(DISTINCT ch.USER_ID) AS TOP_USER_ROLES
        
    FROM MEMORY_RECORDS mr
    LEFT JOIN CONVERSATION_HISTORY ch ON (
        ARRAY_CONTAINS(mr.MEMORY_ID::VARIANT, ch.MEMORIES_RECALLED) 
        AND DATE(ch.STARTED_AT) = analytics_date
    )
    WHERE NOT EXISTS (
        SELECT 1 FROM MEMORY_USAGE_ANALYTICS mua 
        WHERE mua.MEMORY_ID = mr.MEMORY_ID 
        AND mua.ACCESS_DATE = analytics_date
    )
    GROUP BY mr.MEMORY_ID
    HAVING COUNT(ch.CONVERSATION_ID) > 0; -- Only include memories that were accessed
    
    GET DIAGNOSTICS processed_memories = ROW_COUNT;
    
    -- Calculate system-wide metrics
    INSERT INTO SYSTEM_PERFORMANCE_METRICS (
        METRIC_ID,
        METRIC_DATE,
        TOTAL_MEMORIES,
        TOTAL_ACTIVE_MEMORIES,
        TOTAL_CATEGORIES,
        TOTAL_TAGS,
        DAILY_MEMORY_ACCESSES,
        DAILY_NEW_MEMORIES,
        DAILY_CONVERSATIONS,
        UNIQUE_DAILY_USERS,
        AVG_MEMORY_RECALL_TIME_MS,
        AVG_USER_SATISFACTION_SCORE,
        AVG_MEMORY_RELEVANCE_SCORE,
        HUBSPOT_MEMORIES_ACCESSED,
        GONG_MEMORIES_ACCESSED
    )
    SELECT 
        'SYSTEM_' || analytics_date AS METRIC_ID,
        analytics_date AS METRIC_DATE,
        
        -- Memory counts
        (SELECT COUNT(*) FROM MEMORY_RECORDS) AS TOTAL_MEMORIES,
        (SELECT COUNT(*) FROM MEMORY_RECORDS WHERE LAST_ACCESSED_AT >= analytics_date) AS TOTAL_ACTIVE_MEMORIES,
        (SELECT COUNT(*) FROM MEMORY_CATEGORIES WHERE IS_ACTIVE = TRUE) AS TOTAL_CATEGORIES,
        (SELECT COUNT(*) FROM MEMORY_TAGS WHERE IS_ACTIVE = TRUE) AS TOTAL_TAGS,
        
        -- Daily activity
        (SELECT COUNT(*) FROM CONVERSATION_HISTORY WHERE DATE(STARTED_AT) = analytics_date) AS DAILY_CONVERSATIONS,
        (SELECT COUNT(*) FROM MEMORY_RECORDS WHERE DATE(CREATED_AT) = analytics_date) AS DAILY_NEW_MEMORIES,
        (SELECT COUNT(*) FROM CONVERSATION_HISTORY WHERE DATE(STARTED_AT) = analytics_date) AS DAILY_MEMORY_ACCESSES,
        (SELECT COUNT(DISTINCT USER_ID) FROM CONVERSATION_HISTORY WHERE DATE(STARTED_AT) = analytics_date) AS UNIQUE_DAILY_USERS,
        
        -- Performance metrics
        (SELECT AVG(RESPONSE_TIME_MS) FROM CONVERSATION_HISTORY WHERE DATE(STARTED_AT) = analytics_date) AS AVG_MEMORY_RECALL_TIME_MS,
        (SELECT AVG(USER_SATISFACTION_SCORE) FROM CONVERSATION_HISTORY WHERE DATE(STARTED_AT) = analytics_date) AS AVG_USER_SATISFACTION_SCORE,
        (SELECT AVG(RELEVANCE_SCORE) FROM CONVERSATION_HISTORY WHERE DATE(STARTED_AT) = analytics_date) AS AVG_MEMORY_RELEVANCE_SCORE,
        
        -- Business-specific metrics
        (SELECT COUNT(*) FROM MEMORY_RECORDS mr 
         JOIN CONVERSATION_HISTORY ch ON ARRAY_CONTAINS(mr.MEMORY_ID::VARIANT, ch.MEMORIES_RECALLED)
         WHERE mr.CATEGORY LIKE 'HUBSPOT%' AND DATE(ch.STARTED_AT) = analytics_date) AS HUBSPOT_MEMORIES_ACCESSED,
        (SELECT COUNT(*) FROM MEMORY_RECORDS mr 
         JOIN CONVERSATION_HISTORY ch ON ARRAY_CONTAINS(mr.MEMORY_ID::VARIANT, ch.MEMORIES_RECALLED)
         WHERE mr.CATEGORY LIKE 'GONG%' AND DATE(ch.STARTED_AT) = analytics_date) AS GONG_MEMORIES_ACCESSED
    WHERE NOT EXISTS (
        SELECT 1 FROM SYSTEM_PERFORMANCE_METRICS 
        WHERE METRIC_DATE = analytics_date
    );
    
    RETURN 'Calculated analytics for ' || processed_memories || ' memories on ' || analytics_date;
    
EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error calculating analytics: ' || SQLERRM;
END;
$$;

-- =====================================================================
-- 5. INITIAL DATA SETUP
-- =====================================================================

-- Insert default memory categories
INSERT INTO MEMORY_CATEGORIES (
    CATEGORY_ID, CATEGORY_NAME, CATEGORY_DESCRIPTION, 
    DEFAULT_IMPORTANCE_SCORE, PREFERRED_BUSINESS_TABLE
) VALUES 
    ('HUBSPOT_DEAL_ANALYSIS', 'HubSpot Deal Analysis', 'Analysis and insights about HubSpot deals', 0.8, 'STG_HUBSPOT_DEALS'),
    ('HUBSPOT_CONTACT_INSIGHT', 'HubSpot Contact Insight', 'Insights about HubSpot contacts and relationships', 0.7, 'STG_HUBSPOT_CONTACTS'),
    ('HUBSPOT_SALES_PATTERN', 'HubSpot Sales Pattern', 'Sales patterns and trends from HubSpot data', 0.9, 'STG_HUBSPOT_DEALS'),
    ('GONG_CALL_SUMMARY', 'Gong Call Summary', 'Summaries of Gong call recordings', 0.8, 'STG_GONG_CALLS'),
    ('GONG_CALL_INSIGHT', 'Gong Call Insight', 'Insights and analysis from Gong calls', 0.9, 'STG_GONG_CALLS'),
    ('GONG_COACHING_RECOMMENDATION', 'Gong Coaching Recommendation', 'Coaching recommendations based on call analysis', 1.0, 'STG_GONG_CALLS'),
    ('GONG_SENTIMENT_ANALYSIS', 'Gong Sentiment Analysis', 'Sentiment analysis of call conversations', 0.7, 'STG_GONG_CALL_TRANSCRIPTS'),
    ('GENERAL_BUSINESS_INSIGHT', 'General Business Insight', 'General business insights and observations', 0.6, 'MEMORY_RECORDS'),
    ('DEVELOPMENT_CONTEXT', 'Development Context', 'Development-related context and decisions', 0.5, 'MEMORY_RECORDS'),
    ('SYSTEM_CONFIGURATION', 'System Configuration', 'System configuration and setup information', 0.4, 'MEMORY_RECORDS');

-- Insert default tags
INSERT INTO MEMORY_TAGS (TAG_ID, TAG_NAME, TAG_DESCRIPTION, TAG_COLOR) VALUES 
    ('HIGH_VALUE', 'High Value', 'High-value deals or opportunities', '#FF6B6B'),
    ('RISK', 'Risk', 'Risk indicators or concerns', '#FF4757'),
    ('OPPORTUNITY', 'Opportunity', 'Sales opportunities', '#2ED573'),
    ('COACHING', 'Coaching', 'Coaching and improvement opportunities', '#3742FA'),
    ('SENTIMENT_POSITIVE', 'Positive Sentiment', 'Positive sentiment or feedback', '#2ED573'),
    ('SENTIMENT_NEGATIVE', 'Negative Sentiment', 'Negative sentiment or concerns', '#FF4757'),
    ('COMPETITIVE', 'Competitive', 'Competitive intelligence or mentions', '#FFA502'),
    ('PRICING', 'Pricing', 'Pricing discussions or objections', '#FF6348'),
    ('TIMELINE', 'Timeline', 'Timeline or urgency related', '#A4B0BE'),
    ('DECISION_MAKER', 'Decision Maker', 'Decision maker involvement', '#5F27CD');

-- =====================================================================
-- 6. INDEXES AND PERFORMANCE OPTIMIZATION
-- =====================================================================

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS IX_MEMORY_RECORDS_CATEGORY ON MEMORY_RECORDS(CATEGORY);
CREATE INDEX IF NOT EXISTS IX_MEMORY_RECORDS_BUSINESS_TABLE ON MEMORY_RECORDS(BUSINESS_TABLE_NAME, BUSINESS_RECORD_ID);
CREATE INDEX IF NOT EXISTS IX_MEMORY_RECORDS_CREATED_AT ON MEMORY_RECORDS(CREATED_AT);
CREATE INDEX IF NOT EXISTS IX_MEMORY_RECORDS_IMPORTANCE ON MEMORY_RECORDS(IMPORTANCE_SCORE);
CREATE INDEX IF NOT EXISTS IX_MEMORY_RECORDS_DEAL_ID ON MEMORY_RECORDS(RELATED_DEAL_ID);
CREATE INDEX IF NOT EXISTS IX_MEMORY_RECORDS_CALL_ID ON MEMORY_RECORDS(RELATED_CALL_ID);

CREATE INDEX IF NOT EXISTS IX_CONVERSATION_HISTORY_SESSION ON CONVERSATION_HISTORY(SESSION_ID);
CREATE INDEX IF NOT EXISTS IX_CONVERSATION_HISTORY_USER ON CONVERSATION_HISTORY(USER_ID);
CREATE INDEX IF NOT EXISTS IX_CONVERSATION_HISTORY_STARTED_AT ON CONVERSATION_HISTORY(STARTED_AT);
CREATE INDEX IF NOT EXISTS IX_CONVERSATION_HISTORY_TYPE ON CONVERSATION_HISTORY(CONVERSATION_TYPE);

CREATE INDEX IF NOT EXISTS IX_MEMORY_USAGE_ANALYTICS_DATE ON MEMORY_USAGE_ANALYTICS(ACCESS_DATE);
CREATE INDEX IF NOT EXISTS IX_SYSTEM_PERFORMANCE_METRICS_DATE ON SYSTEM_PERFORMANCE_METRICS(METRIC_DATE);

-- =====================================================================
-- 7. GRANTS AND PERMISSIONS
-- =====================================================================

-- Grant access to ROLE_SOPHIA_AI_AGENT_SERVICE for read/write operations
GRANT USAGE ON SCHEMA AI_MEMORY TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA AI_MEMORY TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA AI_MEMORY TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;

-- Grant access to ROLE_SOPHIA_DEVELOPER for development
GRANT USAGE ON SCHEMA AI_MEMORY TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON ALL TABLES IN SCHEMA AI_MEMORY TO ROLE ROLE_SOPHIA_DEVELOPER;

-- Grant future permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA AI_MEMORY TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA AI_MEMORY TO ROLE ROLE_SOPHIA_DEVELOPER;

-- =====================================================================
-- DEPLOYMENT NOTES
-- =====================================================================

/*
Deployment Steps:

1. Execute this script in SOPHIA_AI_DEV database
2. Verify all tables and procedures are created successfully
3. Test the stored procedures:
   - CALL CALCULATE_DAILY_MEMORY_ANALYTICS(CURRENT_DATE());
   - CALL CLEANUP_OLD_MEMORIES();

4. Verify default categories and tags are inserted
5. Test memory record insertion and retrieval
6. Integrate with AI Memory MCP Server for production use

Usage Examples:

-- Create a new memory record
INSERT INTO MEMORY_RECORDS (
    MEMORY_ID, CONTENT_SUMMARY, CATEGORY, BUSINESS_TABLE_NAME, BUSINESS_RECORD_ID,
    IMPORTANCE_SCORE, RELATED_DEAL_ID, AUTO_DETECTED, CREATED_BY
) VALUES (
    'hubspot_deal_12345_analysis', 'Analysis of high-value enterprise deal', 
    'HUBSPOT_DEAL_ANALYSIS', 'STG_HUBSPOT_DEALS', 'deal_12345',
    0.9, 'deal_12345', FALSE, 'sales_coach_agent'
);

-- Query memories by category
SELECT * FROM MEMORY_RECORDS 
WHERE CATEGORY = 'GONG_CALL_INSIGHT' 
AND IMPORTANCE_SCORE > 0.8
ORDER BY CREATED_AT DESC;

-- Get memory analytics
SELECT * FROM MEMORY_USAGE_ANALYTICS 
WHERE ACCESS_DATE >= DATEADD('day', -7, CURRENT_DATE())
ORDER BY ACCESS_COUNT_DAILY DESC;
*/ 