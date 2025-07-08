-- AI Memory V2 Schema for Snowflake
-- This schema stores all memories from the Memory V2 system

USE DATABASE SOPHIA_AI;
USE SCHEMA AI_MEMORY;

-- Main memory records table
CREATE TABLE IF NOT EXISTS MEMORY_RECORDS (
    -- Primary fields
    id VARCHAR(32) PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- chat, event, insight, context, decision

    -- Content and metadata
    content VARIANT NOT NULL,
    metadata VARIANT,

    -- Timestamps
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    deleted_at TIMESTAMP_NTZ, -- For soft deletes
    expires_at TIMESTAMP_NTZ, -- For TTL support

    -- User context
    user_id VARCHAR(100),
    session_id VARCHAR(100),

    -- Source tracking
    source_system VARCHAR(50), -- gong, slack, github, linear, etc.
    source_id VARCHAR(100), -- Original ID from source system

    -- Search and analytics
    search_text VARCHAR(16777216), -- Concatenated searchable text
    tags ARRAY, -- Array of tags for filtering

    -- Indexes for performance
    INDEX idx_type (type),
    INDEX idx_created (created_at),
    INDEX idx_user (user_id),
    INDEX idx_session (session_id),
    INDEX idx_source (source_system),
    INDEX idx_deleted (deleted_at)
);

-- Memory statistics table for analytics
CREATE TABLE IF NOT EXISTS MEMORY_STATS (
    id VARCHAR(32) PRIMARY KEY DEFAULT UUID_STRING(),
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    -- Cache statistics
    cache_hits NUMBER DEFAULT 0,
    cache_misses NUMBER DEFAULT 0,
    cache_writes NUMBER DEFAULT 0,
    hit_rate FLOAT,

    -- Memory type breakdown
    chat_count NUMBER DEFAULT 0,
    event_count NUMBER DEFAULT 0,
    insight_count NUMBER DEFAULT 0,
    context_count NUMBER DEFAULT 0,
    decision_count NUMBER DEFAULT 0,

    -- Performance metrics
    avg_retrieval_time_ms FLOAT,
    avg_store_time_ms FLOAT,
    total_operations NUMBER DEFAULT 0
);

-- Memory embeddings for future semantic search
CREATE TABLE IF NOT EXISTS MEMORY_EMBEDDINGS (
    memory_id VARCHAR(32) PRIMARY KEY,
    embedding VECTOR(FLOAT, 768),
    model_version VARCHAR(50),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (memory_id) REFERENCES MEMORY_RECORDS(id)
);

-- Audit log for compliance
CREATE TABLE IF NOT EXISTS MEMORY_AUDIT_LOG (
    id VARCHAR(32) PRIMARY KEY DEFAULT UUID_STRING(),
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    -- Action details
    action VARCHAR(20) NOT NULL, -- create, read, update, delete
    memory_id VARCHAR(32),
    memory_type VARCHAR(20),

    -- User context
    user_id VARCHAR(100),
    user_role VARCHAR(20),

    -- Request details
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),

    -- Result
    success BOOLEAN DEFAULT TRUE,
    error_message VARCHAR(1000),

    INDEX idx_timestamp (timestamp),
    INDEX idx_memory (memory_id),
    INDEX idx_user (user_id)
);

-- Views for analytics
CREATE OR REPLACE VIEW MEMORY_SUMMARY AS
SELECT
    type,
    COUNT(*) as count,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions,
    MIN(created_at) as first_memory,
    MAX(created_at) as last_memory,
    AVG(DATEDIFF('second', created_at, updated_at)) as avg_update_time_seconds
FROM MEMORY_RECORDS
WHERE deleted_at IS NULL
GROUP BY type;

CREATE OR REPLACE VIEW RECENT_INSIGHTS AS
SELECT
    id,
    content:insight::STRING as insight,
    content:confidence::FLOAT as confidence,
    content:category::STRING as category,
    content:recommendations as recommendations,
    created_at,
    user_id
FROM MEMORY_RECORDS
WHERE type = 'insight'
    AND deleted_at IS NULL
    AND created_at >= DATEADD('day', -7, CURRENT_TIMESTAMP())
ORDER BY created_at DESC;

CREATE OR REPLACE VIEW USER_ACTIVITY AS
SELECT
    user_id,
    COUNT(*) as total_memories,
    COUNT(DISTINCT type) as memory_types_used,
    COUNT(DISTINCT DATE(created_at)) as active_days,
    MIN(created_at) as first_activity,
    MAX(created_at) as last_activity,
    SUM(CASE WHEN type = 'chat' THEN 1 ELSE 0 END) as chat_count,
    SUM(CASE WHEN type = 'insight' THEN 1 ELSE 0 END) as insight_count,
    SUM(CASE WHEN type = 'decision' THEN 1 ELSE 0 END) as decision_count
FROM MEMORY_RECORDS
WHERE deleted_at IS NULL
GROUP BY user_id;

-- Stored procedures for common operations
CREATE OR REPLACE PROCEDURE CLEANUP_EXPIRED_MEMORIES()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Soft delete expired memories
    UPDATE MEMORY_RECORDS
    SET deleted_at = CURRENT_TIMESTAMP()
    WHERE expires_at < CURRENT_TIMESTAMP()
        AND deleted_at IS NULL;

    RETURN 'Cleanup completed: ' || SQLROWCOUNT || ' memories expired';
END;
$$;

CREATE OR REPLACE PROCEDURE GENERATE_MEMORY_STATS()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO MEMORY_STATS (
        chat_count,
        event_count,
        insight_count,
        context_count,
        decision_count,
        total_operations
    )
    SELECT
        SUM(CASE WHEN type = 'chat' THEN 1 ELSE 0 END),
        SUM(CASE WHEN type = 'event' THEN 1 ELSE 0 END),
        SUM(CASE WHEN type = 'insight' THEN 1 ELSE 0 END),
        SUM(CASE WHEN type = 'context' THEN 1 ELSE 0 END),
        SUM(CASE WHEN type = 'decision' THEN 1 ELSE 0 END),
        COUNT(*)
    FROM MEMORY_RECORDS
    WHERE deleted_at IS NULL;

    RETURN 'Stats generated successfully';
END;
$$;

-- Scheduled tasks
CREATE OR REPLACE TASK MEMORY_CLEANUP_TASK
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC' -- Run at 2 AM UTC daily
AS
    CALL CLEANUP_EXPIRED_MEMORIES();

CREATE OR REPLACE TASK MEMORY_STATS_TASK
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 * * * * UTC' -- Run every hour
AS
    CALL GENERATE_MEMORY_STATS();

-- Enable tasks
ALTER TASK MEMORY_CLEANUP_TASK RESUME;
ALTER TASK MEMORY_STATS_TASK RESUME;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA AI_MEMORY TO ROLE SOPHIA_AI_ROLE;
GRANT EXECUTE TASK ON ALL TASKS IN SCHEMA AI_MEMORY TO ROLE SOPHIA_AI_ROLE;
GRANT USAGE ON ALL PROCEDURES IN SCHEMA AI_MEMORY TO ROLE SOPHIA_AI_ROLE;
