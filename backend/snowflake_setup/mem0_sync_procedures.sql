
-- Mem0 Sync Procedure for Snowflake
CREATE OR REPLACE PROCEDURE SOPHIA_AI_MEMORY.SYNC_WITH_MEM0()
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    -- Get unsynchronized memories
    LET unsync_count INTEGER := (
        SELECT COUNT(*)
        FROM SOPHIA_AI_MEMORY.MEMORY_RECORDS
        WHERE mem0_sync_status = 'pending'
    );

    -- Update sync status for batch processing
    UPDATE SOPHIA_AI_MEMORY.MEMORY_RECORDS
    SET mem0_sync_status = 'processing',
        mem0_last_sync = CURRENT_TIMESTAMP()
    WHERE mem0_sync_status = 'pending'
    AND ROWNUM <= 100;

    RETURN 'Marked ' || unsync_count || ' memories for Mem0 sync processing';
END;
$$;

-- Procedure to mark successful sync
CREATE OR REPLACE PROCEDURE SOPHIA_AI_MEMORY.MARK_MEM0_SYNC_SUCCESS(
    MEMORY_ID VARCHAR,
    MEM0_ID VARCHAR
)
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    UPDATE SOPHIA_AI_MEMORY.MEMORY_RECORDS
    SET mem0_sync_status = 'synced',
        mem0_memory_id = MEM0_ID,
        mem0_last_sync = CURRENT_TIMESTAMP()
    WHERE memory_id = MEMORY_ID;

    RETURN 'Memory ' || MEMORY_ID || ' successfully synced with Mem0 ID: ' || MEM0_ID;
END;
$$;

-- Procedure to mark failed sync
CREATE OR REPLACE PROCEDURE SOPHIA_AI_MEMORY.MARK_MEM0_SYNC_FAILED(
    MEMORY_ID VARCHAR,
    ERROR_MESSAGE VARCHAR
)
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    UPDATE SOPHIA_AI_MEMORY.MEMORY_RECORDS
    SET mem0_sync_status = 'failed',
        mem0_last_sync = CURRENT_TIMESTAMP()
    WHERE memory_id = MEMORY_ID;

    -- Log error (would integrate with logging system)
    INSERT INTO SOPHIA_CORE.SYSTEM_HEALTH (
        health_id,
        component_name,
        component_type,
        status,
        health_score,
        metrics
    ) VALUES (
        'mem0_sync_error_' || MEMORY_ID,
        'mem0_sync',
        'memory_integration',
        'error',
        0.0,
        PARSE_JSON('{"error": "' || ERROR_MESSAGE || '", "memory_id": "' || MEMORY_ID || '"}')
    );

    RETURN 'Memory ' || MEMORY_ID || ' sync failed: ' || ERROR_MESSAGE;
END;
$$;
