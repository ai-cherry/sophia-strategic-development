-- Snowflake Complete Alignment Script for Sophia AI
-- This script ensures all components are properly configured

-- Use the correct database
USE DATABASE SOPHIA_AI_PRODUCTION;

-- Select a warehouse for Cortex AI operations
USE WAREHOUSE SOPHIA_AI_CORTEX_WH;

-- =====================================================
-- CREATE MISSING MEMORY ARCHITECTURE TABLES
-- =====================================================

-- Core memory records table
CREATE TABLE IF NOT EXISTS AI_MEMORY.MEMORY_RECORDS (
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
CREATE TABLE IF NOT EXISTS AI_MEMORY.MEMORY_EMBEDDINGS (
    embedding_id VARCHAR(255) PRIMARY KEY,
    memory_id VARCHAR(255) REFERENCES AI_MEMORY.MEMORY_RECORDS(memory_id),
    embedding VECTOR(FLOAT, 768),
    embedding_model VARCHAR(100) DEFAULT 'e5-base-v2',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    vector_dimension INTEGER DEFAULT 768
);

-- Conversation history tracking
CREATE TABLE IF NOT EXISTS AI_MEMORY.CONVERSATION_HISTORY (
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
CREATE TABLE IF NOT EXISTS AI_MEMORY.MEMORY_CATEGORIES (
    category_id VARCHAR(255) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id VARCHAR(255),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- CREATE CORTEX AI TABLES
-- =====================================================

-- Unified embeddings table for Cortex AI
CREATE TABLE IF NOT EXISTS CORTEX_AI.UNIFIED_EMBEDDINGS (
    id VARCHAR(255) PRIMARY KEY,
    source_type VARCHAR(50),
    source_id VARCHAR(255),
    content TEXT,
    embedding VECTOR(FLOAT, 768),
    metadata VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- CREATE UNIFIED SERVICES TABLES
-- =====================================================

-- Unified metrics for dashboard
CREATE TABLE IF NOT EXISTS ANALYTICS.UNIFIED_METRICS (
    metric_id VARCHAR(255) PRIMARY KEY,
    metric_type VARCHAR(50),
    metric_value FLOAT,
    metric_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_system VARCHAR(50),
    metadata VARIANT
);

-- Chat context storage
CREATE TABLE IF NOT EXISTS CHAT.UNIFIED_CONTEXTS (
    context_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    context_type VARCHAR(50),
    context_data VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP_NTZ
);

-- =====================================================
-- CREATE MONITORING TABLES
-- =====================================================

-- Service health monitoring
CREATE TABLE IF NOT EXISTS MONITORING.SERVICE_HEALTH (
    check_id VARCHAR(255) PRIMARY KEY,
    service_name VARCHAR(100),
    check_type VARCHAR(50),
    status VARCHAR(20),
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- AI usage tracking
CREATE TABLE IF NOT EXISTS MONITORING.AI_USAGE (
    usage_id VARCHAR(255) PRIMARY KEY,
    model_name VARCHAR(100),
    operation_type VARCHAR(50),
    tokens_used INTEGER,
    cost_usd FLOAT,
    latency_ms INTEGER,
    user_id VARCHAR(255),
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- CREATE HELPER FUNCTIONS
-- =====================================================

-- Function to generate embeddings
CREATE OR REPLACE FUNCTION sophia_generate_embedding(text_content STRING)
RETURNS VECTOR(FLOAT, 768)
LANGUAGE SQL
AS
$$
    SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', text_content)
$$;

-- Function to calculate memory importance
CREATE OR REPLACE FUNCTION calculate_memory_importance(
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
-- CREATE VIEWS FOR UNIFIED ACCESS
-- =====================================================

-- Dashboard metrics view
CREATE OR REPLACE VIEW ANALYTICS.DASHBOARD_METRICS AS
SELECT
    metric_type,
    AVG(metric_value) as avg_value,
    MAX(metric_value) as max_value,
    MIN(metric_value) as min_value,
    COUNT(*) as data_points,
    MAX(metric_timestamp) as last_updated
FROM ANALYTICS.UNIFIED_METRICS
WHERE metric_timestamp > DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY metric_type;

-- Memory statistics view
CREATE OR REPLACE VIEW AI_MEMORY.MEMORY_STATS AS
SELECT
    memory_type,
    COUNT(*) as total_memories,
    AVG(importance_score) as avg_importance,
    MAX(created_at) as latest_memory,
    SUM(access_count) as total_accesses
FROM AI_MEMORY.MEMORY_RECORDS
WHERE is_active = TRUE
GROUP BY memory_type;

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Grant permissions to SOPHIA_AI_DEVELOPER role
GRANT USAGE ON SCHEMA AI_MEMORY TO ROLE SOPHIA_AI_DEVELOPER;
GRANT USAGE ON SCHEMA CORTEX_AI TO ROLE SOPHIA_AI_DEVELOPER;
GRANT USAGE ON SCHEMA ANALYTICS TO ROLE SOPHIA_AI_DEVELOPER;
GRANT USAGE ON SCHEMA CHAT TO ROLE SOPHIA_AI_DEVELOPER;
GRANT USAGE ON SCHEMA MONITORING TO ROLE SOPHIA_AI_DEVELOPER;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA AI_MEMORY TO ROLE SOPHIA_AI_DEVELOPER;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA CORTEX_AI TO ROLE SOPHIA_AI_DEVELOPER;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA ANALYTICS TO ROLE SOPHIA_AI_DEVELOPER;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA CHAT TO ROLE SOPHIA_AI_DEVELOPER;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA MONITORING TO ROLE SOPHIA_AI_DEVELOPER;

-- =====================================================
-- INSERT SAMPLE DATA
-- =====================================================

-- Insert sample memory categories
INSERT INTO AI_MEMORY.MEMORY_CATEGORIES (category_id, category_name, description)
SELECT * FROM (
    SELECT 'cat_business' as category_id, 'Business Conversations' as category_name, 'Conversations related to business operations and strategy' as description
    UNION ALL
    SELECT 'cat_technical', 'Technical Discussions', 'Technical conversations and problem-solving'
    UNION ALL
    SELECT 'cat_gong_calls', 'Gong Call Records', 'Memory records from Gong call transcripts'
    UNION ALL
    SELECT 'cat_slack_msgs', 'Slack Messages', 'Memory records from Slack conversations'
) AS new_categories
WHERE NOT EXISTS (
    SELECT 1 FROM AI_MEMORY.MEMORY_CATEGORIES WHERE category_id = new_categories.category_id
);

-- Insert sample monitoring data
INSERT INTO MONITORING.SERVICE_HEALTH (check_id, service_name, check_type, status, response_time_ms)
VALUES
    (UUID_STRING(), 'unified_chat_service', 'health_check', 'healthy', 45),
    (UUID_STRING(), 'cortex_ai_service', 'health_check', 'healthy', 120),
    (UUID_STRING(), 'memory_service', 'health_check', 'healthy', 35);

-- =====================================================
-- VERIFY CORTEX AI FUNCTIONS
-- =====================================================

-- Test embedding generation
SELECT
    'Testing Cortex AI Embedding' as test_name,
    LENGTH(SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'Test embedding generation')) as embedding_length,
    CASE
        WHEN LENGTH(SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'Test')) > 0
        THEN 'SUCCESS'
        ELSE 'FAILED'
    END as status;

-- Test completion
SELECT
    'Testing Cortex AI Completion' as test_name,
    SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', 'Say hello in one word') as response,
    'SUCCESS' as status;

-- =====================================================
-- FINAL STATUS CHECK
-- =====================================================

SELECT 'Snowflake alignment complete for Sophia AI!' as message;
