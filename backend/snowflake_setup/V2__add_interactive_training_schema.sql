-- V2: Add Interactive AI Training and User Impact Schema
-- This migration adds the necessary columns and tables to support
-- the interactive, weighted training loop for the Sophia AI platform.

-- Step 1: Add Training Impact Score to the Users table
-- This column will store a value from 0.0 to 1.0, representing the weight of a user's
-- training input. It defaults to 0.1 for existing and new users.
ALTER TABLE payready_core_sql.users
ADD COLUMN training_impact_score FLOAT DEFAULT 0.1;

COMMENT ON COLUMN payready_core_sql.users.training_impact_score IS 'A score from 0.0 to 1.0 representing the authoritative weight of this user''s training input. Controlled by the Unified.';


-- Step 2: Create the Authoritative Knowledge table
-- This table stores the explicit corrections and definitions provided by users.
CREATE TABLE IF NOT EXISTS payready_core_sql.authoritative_knowledge (
    knowledge_id VARCHAR(255) PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    source_user_id VARCHAR(255) NOT NULL,
    user_impact_score FLOAT NOT NULL,
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    last_updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    version INT DEFAULT 1,
    metadata OBJECT,
    
    -- Foreign key to the users table
    CONSTRAINT fk_source_user
        FOREIGN KEY (source_user_id)
        REFERENCES payready_core_sql.users(user_id)
);

-- Add an index on the topic for faster lookups
CREATE INDEX IF NOT EXISTS idx_authoritative_knowledge_topic ON payready_core_sql.authoritative_knowledge (topic);

COMMENT ON TABLE payready_core_sql.authoritative_knowledge IS 'Stores explicit definitions and corrections provided by users via the interactive training loop.';
COMMENT ON COLUMN payready_core_sql.authoritative_knowledge.topic IS 'The subject or entity this piece of knowledge pertains to (e.g., "Customer Health Score").';
COMMENT ON COLUMN payready_core_sql.authoritative_knowledge.content IS 'The authoritative text of the definition or correction.';
COMMENT ON COLUMN payready_core_sql.authoritative_knowledge.user_impact_score IS 'The training_impact_score of the user at the time of creation.';

-- Step 3: Add AI Embedding to the Authoritative Knowledge table
-- This allows for semantic search on authoritative knowledge itself.
ALTER TABLE payready_core_sql.authoritative_knowledge
ADD COLUMN embedding VECTOR(FLOAT, 768);

COMMENT ON COLUMN payready_core_sql.authoritative_knowledge.embedding IS 'Vector embedding of the content for semantic search and relevance scoring.';

-- Grant usage to application roles
GRANT USAGE ON TABLE payready_core_sql.authoritative_knowledge TO ROLE sophia_app_role;
GRANT SELECT, INSERT, UPDATE ON TABLE payready_core_sql.authoritative_knowledge TO ROLE sophia_app_role;

