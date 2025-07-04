-- Mem0 Integration Schema Enhancements for Sophia AI
-- Adds learning capabilities and RLHF support to existing memory system

USE ROLE SYSADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE SOPHIA_AI_CORE;
USE SCHEMA SOPHIA_AI_MEMORY;

-- Enhance memory records with Mem0 integration
ALTER TABLE MEMORY_RECORDS
ADD COLUMN IF NOT EXISTS mem0_memory_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS learning_score FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS feedback_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_reinforced TIMESTAMP_NTZ;

-- Create index for Mem0 lookups
CREATE INDEX IF NOT EXISTS idx_mem0_memory_id ON MEMORY_RECORDS(mem0_memory_id);

-- Create learning analytics table
CREATE TABLE IF NOT EXISTS MEMORY_LEARNING_ANALYTICS (
    analytics_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    memory_id VARCHAR(255) REFERENCES MEMORY_RECORDS(memory_id),
    learning_type VARCHAR(50) NOT NULL, -- 'rlhf', 'conversational', 'business_intelligence'
    feedback_score FLOAT,
    learning_outcome TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    metadata VARIANT,
    CONSTRAINT chk_learning_type CHECK (learning_type IN ('rlhf', 'conversational', 'business_intelligence'))
);

-- Create RLHF feedback table
CREATE TABLE IF NOT EXISTS RLHF_FEEDBACK (
    feedback_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    memory_id VARCHAR(255) REFERENCES MEMORY_RECORDS(memory_id),
    user_id VARCHAR(100) NOT NULL,
    feedback_type VARCHAR(50) NOT NULL, -- 'positive', 'negative', 'correction'
    feedback_text TEXT,
    feedback_score FLOAT,
    applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    applied_at TIMESTAMP_NTZ,
    CONSTRAINT chk_feedback_type CHECK (feedback_type IN ('positive', 'negative', 'correction'))
);

-- Create memory consolidation tracking
CREATE TABLE IF NOT EXISTS MEMORY_CONSOLIDATION (
    consolidation_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    user_id VARCHAR(100) NOT NULL,
    consolidation_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'manual'
    memories_processed INTEGER DEFAULT 0,
    memories_consolidated INTEGER DEFAULT 0,
    started_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    completed_at TIMESTAMP_NTZ,
    status VARCHAR(50) DEFAULT 'in_progress',
    metadata VARIANT
);

-- Create user learning profiles
CREATE TABLE IF NOT EXISTS USER_LEARNING_PROFILES (
    user_id VARCHAR(100) PRIMARY KEY,
    total_memories INTEGER DEFAULT 0,
    total_feedback_given INTEGER DEFAULT 0,
    positive_feedback_ratio FLOAT DEFAULT 0.0,
    learning_velocity FLOAT DEFAULT 0.0, -- memories per day
    last_active TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    preferences VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create stored procedure for applying RLHF feedback
CREATE OR REPLACE PROCEDURE APPLY_RLHF_FEEDBACK(
    P_FEEDBACK_ID VARCHAR,
    P_APPLY_LEARNING BOOLEAN DEFAULT TRUE
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_memory_id VARCHAR;
    v_feedback_type VARCHAR;
    v_feedback_score FLOAT;
    v_current_score FLOAT;
    v_new_score FLOAT;
BEGIN
    -- Get feedback details
    SELECT memory_id, feedback_type, feedback_score
    INTO v_memory_id, v_feedback_type, v_feedback_score
    FROM RLHF_FEEDBACK
    WHERE feedback_id = :P_FEEDBACK_ID AND applied = FALSE;

    IF (v_memory_id IS NULL) THEN
        RETURN 'Feedback not found or already applied';
    END IF;

    -- Get current learning score
    SELECT learning_score
    INTO v_current_score
    FROM MEMORY_RECORDS
    WHERE memory_id = :v_memory_id;

    -- Calculate new score based on feedback type
    IF (v_feedback_type = 'positive') THEN
        v_new_score := LEAST(v_current_score + (v_feedback_score * 0.1), 1.0);
    ELSEIF (v_feedback_type = 'negative') THEN
        v_new_score := GREATEST(v_current_score - (v_feedback_score * 0.1), 0.0);
    ELSE -- correction
        v_new_score := v_current_score; -- Corrections don't change score directly
    END IF;

    IF (P_APPLY_LEARNING) THEN
        -- Update memory record
        UPDATE MEMORY_RECORDS
        SET learning_score = :v_new_score,
            feedback_count = feedback_count + 1,
            last_reinforced = CURRENT_TIMESTAMP()
        WHERE memory_id = :v_memory_id;

        -- Mark feedback as applied
        UPDATE RLHF_FEEDBACK
        SET applied = TRUE,
            applied_at = CURRENT_TIMESTAMP()
        WHERE feedback_id = :P_FEEDBACK_ID;

        -- Log to analytics
        INSERT INTO MEMORY_LEARNING_ANALYTICS (
            memory_id, learning_type, feedback_score, learning_outcome, metadata
        ) VALUES (
            :v_memory_id,
            'rlhf',
            :v_feedback_score,
            'Feedback applied: ' || :v_feedback_type,
            OBJECT_CONSTRUCT(
                'feedback_id', :P_FEEDBACK_ID,
                'old_score', :v_current_score,
                'new_score', :v_new_score
            )
        );
    END IF;

    RETURN 'Feedback processed successfully';
END;
$$;

-- Create function for memory recall with learning boost
CREATE OR REPLACE FUNCTION RECALL_MEMORIES_WITH_LEARNING(
    P_USER_ID VARCHAR,
    P_QUERY_TEXT VARCHAR,
    P_LIMIT INTEGER DEFAULT 10
)
RETURNS TABLE (
    memory_id VARCHAR,
    content TEXT,
    category VARCHAR,
    base_score FLOAT,
    learning_score FLOAT,
    final_score FLOAT,
    created_at TIMESTAMP_NTZ,
    mem0_memory_id VARCHAR
)
AS
$$
SELECT
    m.memory_id,
    m.content,
    m.category,
    VECTOR_COSINE_SIMILARITY(
        m.embedding,
        SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', P_QUERY_TEXT)
    ) as base_score,
    m.learning_score,
    -- Combine base similarity with learning score
    (VECTOR_COSINE_SIMILARITY(
        m.embedding,
        SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', P_QUERY_TEXT)
    ) * 0.7) + (m.learning_score * 0.3) as final_score,
    m.created_at,
    m.mem0_memory_id
FROM MEMORY_RECORDS m
WHERE m.user_id = P_USER_ID
    AND m.is_active = TRUE
ORDER BY final_score DESC
LIMIT P_LIMIT
$$;

-- Create task for periodic memory consolidation
CREATE OR REPLACE TASK CONSOLIDATE_USER_MEMORIES
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC' -- Daily at 2 AM UTC
AS
BEGIN
    -- This would call a more complex consolidation procedure
    -- For now, just update user profiles
    MERGE INTO USER_LEARNING_PROFILES ulp
    USING (
        SELECT
            user_id,
            COUNT(*) as total_memories,
            SUM(CASE WHEN feedback_count > 0 THEN 1 ELSE 0 END) as memories_with_feedback,
            AVG(learning_score) as avg_learning_score
        FROM MEMORY_RECORDS
        WHERE is_active = TRUE
        GROUP BY user_id
    ) stats
    ON ulp.user_id = stats.user_id
    WHEN MATCHED THEN UPDATE SET
        ulp.total_memories = stats.total_memories,
        ulp.updated_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (
        user_id, total_memories, created_at, updated_at
    ) VALUES (
        stats.user_id, stats.total_memories, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
    );
END;

-- Enable the task
ALTER TASK CONSOLIDATE_USER_MEMORIES RESUME;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA SOPHIA_AI_MEMORY TO ROLE SOPHIA_AI_APP_ROLE;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA SOPHIA_AI_MEMORY TO ROLE SOPHIA_AI_APP_ROLE;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA SOPHIA_AI_MEMORY TO ROLE SOPHIA_AI_APP_ROLE;
