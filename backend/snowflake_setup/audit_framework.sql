-- =====================================================================
-- Comprehensive Audit Framework
-- =====================================================================

-- Create audit log table
CREATE TABLE IF NOT EXISTS OPS_MONITORING.DATA_ACCESS_AUDIT (
    AUDIT_ID VARCHAR(255) PRIMARY KEY,
    USER_ID VARCHAR(255) NOT NULL,
    ROLE VARCHAR(255),
    SESSION_ID VARCHAR(255),
    
    -- Access details
    SCHEMA_NAME VARCHAR(255),
    TABLE_NAME VARCHAR(255),
    OPERATION_TYPE VARCHAR(50),
    QUERY_TEXT VARCHAR(16777216),
    
    -- Timing
    ACCESS_TIMESTAMP TIMESTAMP_LTZ NOT NULL,
    EXECUTION_TIME_MS NUMBER,
    
    -- Results
    ROWS_ACCESSED NUMBER,
    SUCCESS BOOLEAN,
    ERROR_MESSAGE VARCHAR(4000),
    
    -- Security context
    IP_ADDRESS VARCHAR(45),
    USER_AGENT VARCHAR(1000),
    
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION AUDIT_DATA_ACCESS()
RETURNS STRING
LANGUAGE SQL
AS
$$
    INSERT INTO OPS_MONITORING.DATA_ACCESS_AUDIT (
        AUDIT_ID,
        USER_ID,
        ROLE,
        SCHEMA_NAME,
        TABLE_NAME,
        OPERATION_TYPE,
        ACCESS_TIMESTAMP
    ) VALUES (
        RANDOM()::STRING,
        CURRENT_USER(),
        CURRENT_ROLE(),
        CURRENT_SCHEMA(),
        'UNKNOWN',
        'SELECT',
        CURRENT_TIMESTAMP()
    );
    
    RETURN 'Audit logged';
$$;
