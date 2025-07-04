
        -- Enhanced Memory Records with Mem0 Integration
        ALTER TABLE IF EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS
        ADD COLUMN IF NOT EXISTS mem0_memory_id VARCHAR(255);

        ALTER TABLE IF EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS
        ADD COLUMN IF NOT EXISTS mem0_sync_status VARCHAR(50) DEFAULT 'pending';

        ALTER TABLE IF EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS
        ADD COLUMN IF NOT EXISTS mem0_last_sync TIMESTAMP_NTZ;

        ALTER TABLE IF EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS
        ADD COLUMN IF NOT EXISTS cross_session_relevance FLOAT DEFAULT 0.0;

        -- Create Mem0 sync status index
        CREATE INDEX IF NOT EXISTS idx_mem0_sync_status
        ON SOPHIA_AI_MEMORY.MEMORY_RECORDS(mem0_sync_status);

        -- Create Mem0 memory ID index
        CREATE INDEX IF NOT EXISTS idx_mem0_memory_id
        ON SOPHIA_AI_MEMORY.MEMORY_RECORDS(mem0_memory_id);

