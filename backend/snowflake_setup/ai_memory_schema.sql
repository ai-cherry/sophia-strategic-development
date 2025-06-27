-- SOPHIA AI ENHANCED MEMORY SCHEMA WITH GONG & SLACK INTEGRATION
-- This schema supports comprehensive memory management with cross-platform data integration

-- =====================================================
-- CORE AI MEMORY INFRASTRUCTURE
-- =====================================================

-- Core memory records table
CREATE TABLE IF NOT EXISTS SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS (
    memory_id VARCHAR(255) PRIMARY KEY,
    conversation_id VARCHAR(255),
    user_id VARCHAR(255),
    agent_id VARCHAR(255),
    content TEXT NOT NULL,
    memory_type VARCHAR(50) DEFAULT 'conversation',
    importance_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    last_accessed TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    access_count INTEGER DEFAULT 0,
    metadata VARIANT,
    tags ARRAY,
    is_active BOOLEAN DEFAULT TRUE
);

-- Memory embeddings for vector search
CREATE TABLE IF NOT EXISTS SOPHIA_AI_CORE.AI_MEMORY.MEMORY_EMBEDDINGS (
    embedding_id VARCHAR(255) PRIMARY KEY,
    memory_id VARCHAR(255) REFERENCES SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS(memory_id),
    embedding_vector ARRAY,
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    vector_dimension INTEGER DEFAULT 1536
);

-- Conversation history tracking
CREATE TABLE IF NOT EXISTS SOPHIA_AI_CORE.AI_MEMORY.CONVERSATION_HISTORY (
    conversation_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    agent_id VARCHAR(255),
    start_time TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    end_time TIMESTAMP_NTZ,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    conversation_summary TEXT,
    effectiveness_score FLOAT,
    metadata VARIANT
);

-- Memory categories for organization
CREATE TABLE IF NOT EXISTS SOPHIA_AI_CORE.AI_MEMORY.MEMORY_CATEGORIES (
    category_id VARCHAR(255) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id VARCHAR(255),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- GONG & SLACK RAW DATA SCHEMAS
-- =====================================================

-- Create schemas for raw data from external sources
CREATE SCHEMA IF NOT EXISTS SOPHIA_GONG_RAW;
CREATE SCHEMA IF NOT EXISTS SOPHIA_SLACK_RAW;

-- Grant appropriate permissions
GRANT USAGE ON SCHEMA SOPHIA_GONG_RAW TO ROLE SOPHIA_AI_DEVELOPER;
GRANT USAGE ON SCHEMA SOPHIA_SLACK_RAW TO ROLE SOPHIA_AI_DEVELOPER;
GRANT CREATE TABLE ON SCHEMA SOPHIA_GONG_RAW TO ROLE SOPHIA_AI_DEVELOPER;
GRANT CREATE TABLE ON SCHEMA SOPHIA_SLACK_RAW TO ROLE SOPHIA_AI_DEVELOPER;

-- Note: Airbyte will create the actual tables in these schemas based on the data streams
-- Examples of tables Airbyte might create:
-- SOPHIA_GONG_RAW.gong_calls
-- SOPHIA_GONG_RAW.gong_transcripts  
-- SOPHIA_GONG_RAW.gong_participants
-- SOPHIA_SLACK_RAW.slack_messages
-- SOPHIA_SLACK_RAW.slack_channels
-- SOPHIA_SLACK_RAW.slack_users

-- =====================================================
-- INTEGRATED CONVERSATION VIEW
-- =====================================================

-- Unified view combining Gong calls and Slack conversations
CREATE OR REPLACE VIEW SOPHIA_AI_CORE.AI_MEMORY.INTEGRATED_CONVERSATIONS AS
SELECT 
    'gong_' || COALESCE(call_id, 'unknown') as conversation_id,
    'gong' as source_platform,
    COALESCE(started_at, CURRENT_TIMESTAMP()) as conversation_time,
    COALESCE(title, 'Untitled Call') as conversation_title,
    COALESCE(transcript, '') as conversation_content,
    COALESCE(participants, []) as participants,
    COALESCE(duration, 0) as duration_seconds,
    OBJECT_CONSTRUCT(
        'call_id', call_id,
        'meeting_url', meeting_url,
        'call_type', call_type
    ) as platform_metadata
FROM SOPHIA_GONG_RAW.gong_calls
WHERE transcript IS NOT NULL AND transcript != ''

UNION ALL

SELECT 
    'slack_' || COALESCE(channel_id, 'unknown') || '_' || COALESCE(ts, 'unknown') as conversation_id,
    'slack' as source_platform,
    COALESCE(TO_TIMESTAMP(ts), CURRENT_TIMESTAMP()) as conversation_time,
    COALESCE(channel_name, 'Unknown Channel') as conversation_title,
    COALESCE(text, '') as conversation_content,
    ARRAY_CONSTRUCT(user_id) as participants,
    0 as duration_seconds,
    OBJECT_CONSTRUCT(
        'channel_id', channel_id,
        'user_id', user_id,
        'message_type', type,
        'thread_ts', thread_ts
    ) as platform_metadata
FROM SOPHIA_SLACK_RAW.slack_messages
WHERE text IS NOT NULL AND text != '';

-- =====================================================
-- MEMORY PROCESSING FUNCTIONS
-- =====================================================

-- Function to calculate memory importance based on various factors
CREATE OR REPLACE FUNCTION SOPHIA_AI_CORE.AI_MEMORY.CALCULATE_MEMORY_IMPORTANCE(
    content_length INTEGER,
    access_count INTEGER,
    recency_days INTEGER,
    source_platform VARCHAR(50)
)
RETURNS FLOAT
LANGUAGE SQL
AS
$$
    CASE 
        WHEN content_length > 1000 THEN 0.8
        WHEN content_length > 500 THEN 0.6
        WHEN content_length > 100 THEN 0.4
        ELSE 0.2
    END +
    CASE 
        WHEN access_count > 10 THEN 0.3
        WHEN access_count > 5 THEN 0.2
        WHEN access_count > 1 THEN 0.1
        ELSE 0.0
    END +
    CASE 
        WHEN recency_days <= 1 THEN 0.3
        WHEN recency_days <= 7 THEN 0.2
        WHEN recency_days <= 30 THEN 0.1
        ELSE 0.0
    END +
    CASE 
        WHEN source_platform = 'gong' THEN 0.2
        WHEN source_platform = 'slack' THEN 0.1
        ELSE 0.0
    END
$$;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_memory_records_conversation_id 
ON SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS(conversation_id);

CREATE INDEX IF NOT EXISTS idx_memory_records_user_id 
ON SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS(user_id);

CREATE INDEX IF NOT EXISTS idx_memory_records_created_at 
ON SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS(created_at);

CREATE INDEX IF NOT EXISTS idx_memory_records_importance 
ON SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS(importance_score);

CREATE INDEX IF NOT EXISTS idx_memory_embeddings_memory_id 
ON SOPHIA_AI_CORE.AI_MEMORY.MEMORY_EMBEDDINGS(memory_id);

-- =====================================================
-- SAMPLE DATA FOR TESTING
-- =====================================================

-- Insert sample memory categories
INSERT INTO SOPHIA_AI_CORE.AI_MEMORY.MEMORY_CATEGORIES 
(category_id, category_name, description) VALUES
('cat_business', 'Business Conversations', 'Conversations related to business operations and strategy'),
('cat_technical', 'Technical Discussions', 'Technical conversations and problem-solving'),
('cat_personal', 'Personal Interactions', 'Personal conversations and relationship building'),
('cat_gong_calls', 'Gong Call Records', 'Memory records from Gong call transcripts'),
('cat_slack_msgs', 'Slack Messages', 'Memory records from Slack conversations');

-- Insert sample conversation history
INSERT INTO SOPHIA_AI_CORE.AI_MEMORY.CONVERSATION_HISTORY 
(conversation_id, user_id, agent_id, message_count, effectiveness_score) VALUES
('conv_sample_001', 'user_001', 'sophia_ai', 15, 0.85),
('conv_sample_002', 'user_002', 'sophia_ai', 8, 0.72);

-- Insert sample memory records
INSERT INTO SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS 
(memory_id, conversation_id, user_id, agent_id, content, memory_type, importance_score, metadata, tags) VALUES
('mem_001', 'conv_sample_001', 'user_001', 'sophia_ai', 
 'User discussed quarterly sales targets and expressed concerns about market competition.',
 'business_insight', 0.8, 
 PARSE_JSON('{"topic": "sales", "sentiment": "concerned", "priority": "high"}'),
 ARRAY_CONSTRUCT('sales', 'quarterly', 'competition')),
('mem_002', 'conv_sample_001', 'user_001', 'sophia_ai',
 'User requested technical analysis of customer churn patterns in the CRM system.',
 'technical_request', 0.7,
 PARSE_JSON('{"topic": "analytics", "system": "crm", "urgency": "medium"}'),
 ARRAY_CONSTRUCT('analytics', 'churn', 'crm'));

COMMIT;

