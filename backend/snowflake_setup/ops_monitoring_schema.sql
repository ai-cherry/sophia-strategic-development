-- =====================================================================
-- OPS_MONITORING Schema - Operational Monitoring and Logging
-- =====================================================================
-- 
-- This script creates the OPS_MONITORING schema for tracking ETL jobs,
-- application errors, system performance, and operational metrics.
-- 
-- Features:
-- - ETL job execution tracking
-- - Application error logging
-- - System performance monitoring
-- - Data quality metrics
-- - Alert management
-- 
-- Usage: Execute in SOPHIA_AI_DEV database
-- =====================================================================

-- Set context for DEV environment
USE DATABASE SOPHIA_AI_DEV;
CREATE SCHEMA IF NOT EXISTS OPS_MONITORING;
USE SCHEMA OPS_MONITORING;

-- =====================================================================
-- 1. ETL JOB MONITORING TABLES
-- =====================================================================

-- ETL job execution logs
CREATE TABLE IF NOT EXISTS ETL_JOB_LOGS (
    JOB_LOG_ID VARCHAR(255) PRIMARY KEY,
    JOB_NAME VARCHAR(255) NOT NULL,
    JOB_TYPE VARCHAR(100), -- 'GONG_INGESTION', 'HUBSPOT_REFRESH', 'CORTEX_PROCESSING', etc.
    JOB_CATEGORY VARCHAR(100), -- 'INGESTION', 'TRANSFORMATION', 'AI_PROCESSING'
    
    -- Execution details
    START_TIME TIMESTAMP_LTZ NOT NULL,
    END_TIME TIMESTAMP_LTZ,
    DURATION_SECONDS NUMBER,
    STATUS VARCHAR(50) NOT NULL, -- 'RUNNING', 'SUCCESS', 'FAILED', 'CANCELLED'
    
    -- Data processing metrics
    ROWS_PROCESSED NUMBER DEFAULT 0,
    ROWS_INSERTED NUMBER DEFAULT 0,
    ROWS_UPDATED NUMBER DEFAULT 0,
    ROWS_DELETED NUMBER DEFAULT 0,
    ROWS_FAILED NUMBER DEFAULT 0,
    
    -- Resource utilization
    WAREHOUSE_NAME VARCHAR(255),
    CREDITS_USED FLOAT,
    BYTES_SCANNED NUMBER,
    BYTES_WRITTEN NUMBER,
    
    -- Error handling
    ERROR_MESSAGE VARCHAR(16777216),
    ERROR_CODE VARCHAR(100),
    STACK_TRACE VARCHAR(16777216),
    RETRY_COUNT NUMBER DEFAULT 0,
    MAX_RETRIES NUMBER DEFAULT 3,
    
    -- Context and metadata
    CORRELATION_ID VARCHAR(255), -- For tracking related operations
    TRIGGERED_BY VARCHAR(255), -- User, system, or schedule that triggered the job
    JOB_PARAMETERS VARIANT, -- JSON parameters passed to the job
    
    -- Data quality metrics
    DATA_QUALITY_SCORE FLOAT, -- Overall data quality score (0.0 to 1.0)
    VALIDATION_ERRORS VARIANT, -- JSON array of validation errors
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ETL job schedules and configuration
CREATE TABLE IF NOT EXISTS ETL_JOB_SCHEDULES (
    SCHEDULE_ID VARCHAR(255) PRIMARY KEY,
    JOB_NAME VARCHAR(255) NOT NULL,
    JOB_TYPE VARCHAR(100),
    
    -- Schedule configuration
    SCHEDULE_EXPRESSION VARCHAR(255), -- Cron expression
    TIMEZONE VARCHAR(50) DEFAULT 'UTC',
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    -- Execution settings
    MAX_CONCURRENT_RUNS NUMBER DEFAULT 1,
    TIMEOUT_MINUTES NUMBER DEFAULT 60,
    RETRY_POLICY VARCHAR(50) DEFAULT 'EXPONENTIAL_BACKOFF',
    
    -- Dependencies
    DEPENDS_ON_JOBS VARIANT, -- JSON array of job names this job depends on
    
    -- Notification settings
    NOTIFY_ON_SUCCESS BOOLEAN DEFAULT FALSE,
    NOTIFY_ON_FAILURE BOOLEAN DEFAULT TRUE,
    NOTIFICATION_CHANNELS VARIANT, -- JSON array of notification channels
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    LAST_EXECUTED_AT TIMESTAMP_LTZ,
    NEXT_EXECUTION_AT TIMESTAMP_LTZ
);

-- Data pipeline dependencies
CREATE TABLE IF NOT EXISTS PIPELINE_DEPENDENCIES (
    DEPENDENCY_ID VARCHAR(255) PRIMARY KEY,
    SOURCE_JOB VARCHAR(255) NOT NULL,
    TARGET_JOB VARCHAR(255) NOT NULL,
    DEPENDENCY_TYPE VARCHAR(50), -- 'HARD', 'SOFT', 'CONDITIONAL'
    
    -- Dependency rules
    CONDITION_EXPRESSION VARCHAR(1000), -- Optional condition for dependency
    WAIT_TIMEOUT_MINUTES NUMBER DEFAULT 30,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    UNIQUE (SOURCE_JOB, TARGET_JOB)
);

-- =====================================================================
-- 2. APPLICATION ERROR LOGGING
-- =====================================================================

-- Application error logs
CREATE TABLE IF NOT EXISTS APP_ERROR_LOGS (
    ERROR_LOG_ID VARCHAR(255) PRIMARY KEY,
    APPLICATION_NAME VARCHAR(255) NOT NULL, -- 'SOPHIA_AI_BACKEND', 'AI_MEMORY_MCP', etc.
    SERVICE_NAME VARCHAR(255), -- Specific service or component
    
    -- Error details
    ERROR_LEVEL VARCHAR(50) NOT NULL, -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    ERROR_MESSAGE VARCHAR(16777216) NOT NULL,
    ERROR_CODE VARCHAR(100),
    ERROR_TYPE VARCHAR(255), -- Exception type or error category
    
    -- Context information
    USER_ID VARCHAR(255), -- User associated with the error (if applicable)
    SESSION_ID VARCHAR(255), -- Session ID
    REQUEST_ID VARCHAR(255), -- Request ID for tracing
    CORRELATION_ID VARCHAR(255), -- Correlation ID for distributed tracing
    
    -- Technical details
    STACK_TRACE VARCHAR(16777216),
    FILE_NAME VARCHAR(500),
    LINE_NUMBER NUMBER,
    FUNCTION_NAME VARCHAR(255),
    
    -- Request context
    HTTP_METHOD VARCHAR(10),
    REQUEST_URL VARCHAR(2000),
    REQUEST_HEADERS VARIANT, -- JSON object
    REQUEST_BODY VARCHAR(16777216),
    RESPONSE_STATUS_CODE NUMBER,
    
    -- Environment information
    ENVIRONMENT VARCHAR(50), -- 'DEV', 'STAGING', 'PRODUCTION'
    HOST_NAME VARCHAR(255),
    PROCESS_ID VARCHAR(50),
    THREAD_ID VARCHAR(50),
    
    -- Additional context
    CUSTOM_METADATA VARIANT, -- JSON object for additional context
    TAGS VARIANT, -- JSON array of tags for categorization
    
    -- Resolution tracking
    IS_RESOLVED BOOLEAN DEFAULT FALSE,
    RESOLVED_BY VARCHAR(255),
    RESOLVED_AT TIMESTAMP_LTZ,
    RESOLUTION_NOTES VARCHAR(4000),
    
    -- Metadata
    OCCURRED_AT TIMESTAMP_LTZ NOT NULL,
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Error patterns and analysis
CREATE TABLE IF NOT EXISTS ERROR_PATTERNS (
    PATTERN_ID VARCHAR(255) PRIMARY KEY,
    PATTERN_NAME VARCHAR(255) NOT NULL,
    PATTERN_DESCRIPTION VARCHAR(1000),
    
    -- Pattern matching criteria
    ERROR_MESSAGE_PATTERN VARCHAR(1000), -- Regex pattern for error messages
    ERROR_TYPE_PATTERN VARCHAR(255),
    APPLICATION_NAME_PATTERN VARCHAR(255),
    SERVICE_NAME_PATTERN VARCHAR(255),
    
    -- Pattern statistics
    OCCURRENCE_COUNT NUMBER DEFAULT 0,
    FIRST_SEEN_AT TIMESTAMP_LTZ,
    LAST_SEEN_AT TIMESTAMP_LTZ,
    
    -- Impact assessment
    SEVERITY_LEVEL VARCHAR(50), -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    BUSINESS_IMPACT VARCHAR(1000),
    AFFECTED_USERS_COUNT NUMBER,
    
    -- Resolution information
    KNOWN_SOLUTION VARCHAR(4000),
    RESOLUTION_STEPS VARIANT, -- JSON array of resolution steps
    PREVENTION_MEASURES VARCHAR(4000),
    
    -- Alerting configuration
    ALERT_THRESHOLD NUMBER DEFAULT 5, -- Alert after N occurrences
    ALERT_WINDOW_MINUTES NUMBER DEFAULT 60, -- Within this time window
    IS_ALERTING_ENABLED BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255)
);

-- =====================================================================
-- 3. SYSTEM PERFORMANCE MONITORING
-- =====================================================================

-- System performance metrics
CREATE TABLE IF NOT EXISTS SYSTEM_PERFORMANCE_METRICS (
    METRIC_ID VARCHAR(255) PRIMARY KEY,
    METRIC_TIMESTAMP TIMESTAMP_LTZ NOT NULL,
    APPLICATION_NAME VARCHAR(255) NOT NULL,
    SERVICE_NAME VARCHAR(255),
    
    -- Performance metrics
    CPU_USAGE_PERCENT FLOAT,
    MEMORY_USAGE_PERCENT FLOAT,
    MEMORY_USAGE_MB NUMBER,
    DISK_USAGE_PERCENT FLOAT,
    DISK_IO_READ_MB NUMBER,
    DISK_IO_WRITE_MB NUMBER,
    
    -- Network metrics
    NETWORK_IN_MB NUMBER,
    NETWORK_OUT_MB NUMBER,
    ACTIVE_CONNECTIONS NUMBER,
    
    -- Application-specific metrics
    REQUEST_COUNT NUMBER,
    REQUEST_RATE_PER_SECOND FLOAT,
    AVG_RESPONSE_TIME_MS NUMBER,
    ERROR_RATE_PERCENT FLOAT,
    THROUGHPUT_OPERATIONS_PER_SECOND FLOAT,
    
    -- Database metrics
    DB_CONNECTION_COUNT NUMBER,
    DB_QUERY_COUNT NUMBER,
    DB_AVG_QUERY_TIME_MS NUMBER,
    DB_SLOW_QUERY_COUNT NUMBER,
    
    -- Cache metrics
    CACHE_HIT_RATE_PERCENT FLOAT,
    CACHE_SIZE_MB NUMBER,
    CACHE_EVICTION_COUNT NUMBER,
    
    -- Custom metrics
    CUSTOM_METRICS VARIANT, -- JSON object for application-specific metrics
    
    -- Metadata
    COLLECTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    COLLECTION_METHOD VARCHAR(100) -- 'AGENT', 'API', 'MANUAL'
);

-- System health checks
CREATE TABLE IF NOT EXISTS SYSTEM_HEALTH_CHECKS (
    HEALTH_CHECK_ID VARCHAR(255) PRIMARY KEY,
    CHECK_NAME VARCHAR(255) NOT NULL,
    CHECK_TYPE VARCHAR(100), -- 'ENDPOINT', 'DATABASE', 'SERVICE', 'CUSTOM'
    APPLICATION_NAME VARCHAR(255) NOT NULL,
    SERVICE_NAME VARCHAR(255),
    
    -- Check configuration
    CHECK_URL VARCHAR(2000), -- For endpoint checks
    CHECK_QUERY VARCHAR(4000), -- For database checks
    CHECK_SCRIPT VARCHAR(16777216), -- For custom checks
    EXPECTED_RESPONSE VARCHAR(4000),
    TIMEOUT_SECONDS NUMBER DEFAULT 30,
    
    -- Check results
    STATUS VARCHAR(50) NOT NULL, -- 'HEALTHY', 'DEGRADED', 'UNHEALTHY', 'UNKNOWN'
    RESPONSE_TIME_MS NUMBER,
    RESPONSE_DATA VARCHAR(16777216),
    ERROR_MESSAGE VARCHAR(4000),
    
    -- Check scheduling
    CHECK_INTERVAL_MINUTES NUMBER DEFAULT 5,
    LAST_CHECK_AT TIMESTAMP_LTZ,
    NEXT_CHECK_AT TIMESTAMP_LTZ,
    
    -- Alerting
    CONSECUTIVE_FAILURES NUMBER DEFAULT 0,
    ALERT_THRESHOLD NUMBER DEFAULT 3,
    LAST_ALERT_SENT_AT TIMESTAMP_LTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

-- =====================================================================
-- 4. DATA QUALITY MONITORING
-- =====================================================================

-- Data quality checks
CREATE TABLE IF NOT EXISTS DATA_QUALITY_CHECKS (
    CHECK_ID VARCHAR(255) PRIMARY KEY,
    CHECK_NAME VARCHAR(255) NOT NULL,
    CHECK_DESCRIPTION VARCHAR(1000),
    
    -- Check configuration
    TARGET_TABLE VARCHAR(255) NOT NULL,
    TARGET_COLUMN VARCHAR(255),
    CHECK_TYPE VARCHAR(100), -- 'NULL_CHECK', 'RANGE_CHECK', 'FORMAT_CHECK', 'UNIQUENESS_CHECK', etc.
    CHECK_RULE VARCHAR(4000), -- SQL expression or rule definition
    
    -- Thresholds
    WARNING_THRESHOLD FLOAT, -- Threshold for warnings (e.g., 0.05 for 5% null values)
    CRITICAL_THRESHOLD FLOAT, -- Threshold for critical alerts
    
    -- Check results
    LAST_CHECK_AT TIMESTAMP_LTZ,
    LAST_CHECK_STATUS VARCHAR(50), -- 'PASSED', 'WARNING', 'FAILED'
    LAST_CHECK_VALUE FLOAT, -- Actual measured value
    LAST_CHECK_DETAILS VARCHAR(4000),
    
    -- Check scheduling
    CHECK_FREQUENCY VARCHAR(50), -- 'HOURLY', 'DAILY', 'WEEKLY', 'ON_DEMAND'
    NEXT_CHECK_AT TIMESTAMP_LTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

-- Data quality results
CREATE TABLE IF NOT EXISTS DATA_QUALITY_RESULTS (
    RESULT_ID VARCHAR(255) PRIMARY KEY,
    CHECK_ID VARCHAR(255) NOT NULL,
    
    -- Check execution details
    EXECUTED_AT TIMESTAMP_LTZ NOT NULL,
    EXECUTION_DURATION_MS NUMBER,
    
    -- Results
    STATUS VARCHAR(50) NOT NULL, -- 'PASSED', 'WARNING', 'FAILED'
    MEASURED_VALUE FLOAT,
    EXPECTED_VALUE FLOAT,
    DEVIATION_PERCENT FLOAT,
    
    -- Details
    RECORDS_CHECKED NUMBER,
    RECORDS_FAILED NUMBER,
    FAILURE_RATE_PERCENT FLOAT,
    DETAILS VARCHAR(16777216), -- Detailed results or error information
    SAMPLE_FAILURES VARIANT, -- JSON array of sample failed records
    
    -- Impact assessment
    BUSINESS_IMPACT VARCHAR(1000),
    RECOMMENDED_ACTION VARCHAR(1000),
    
    -- Resolution tracking
    IS_ACKNOWLEDGED BOOLEAN DEFAULT FALSE,
    ACKNOWLEDGED_BY VARCHAR(255),
    ACKNOWLEDGED_AT TIMESTAMP_LTZ,
    ACKNOWLEDGMENT_NOTES VARCHAR(4000),
    
    FOREIGN KEY (CHECK_ID) REFERENCES DATA_QUALITY_CHECKS(CHECK_ID)
);

-- =====================================================================
-- 5. ALERT MANAGEMENT
-- =====================================================================

-- Alert definitions
CREATE TABLE IF NOT EXISTS ALERT_DEFINITIONS (
    ALERT_ID VARCHAR(255) PRIMARY KEY,
    ALERT_NAME VARCHAR(255) NOT NULL,
    ALERT_DESCRIPTION VARCHAR(1000),
    ALERT_TYPE VARCHAR(100), -- 'ETL_FAILURE', 'DATA_QUALITY', 'SYSTEM_HEALTH', 'ERROR_PATTERN'
    
    -- Alert conditions
    CONDITION_EXPRESSION VARCHAR(4000), -- SQL expression or rule
    SEVERITY_LEVEL VARCHAR(50), -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    
    -- Notification settings
    NOTIFICATION_CHANNELS VARIANT, -- JSON array of channels (email, slack, etc.)
    NOTIFICATION_TEMPLATE VARCHAR(4000),
    ESCALATION_RULES VARIANT, -- JSON object defining escalation rules
    
    -- Throttling and suppression
    THROTTLE_MINUTES NUMBER DEFAULT 60, -- Minimum time between alerts
    MAX_ALERTS_PER_HOUR NUMBER DEFAULT 10,
    SUPPRESSION_RULES VARIANT, -- JSON object for suppression conditions
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

-- Alert instances
CREATE TABLE IF NOT EXISTS ALERT_INSTANCES (
    INSTANCE_ID VARCHAR(255) PRIMARY KEY,
    ALERT_ID VARCHAR(255) NOT NULL,
    
    -- Alert details
    TRIGGERED_AT TIMESTAMP_LTZ NOT NULL,
    SEVERITY_LEVEL VARCHAR(50),
    ALERT_MESSAGE VARCHAR(4000),
    ALERT_DETAILS VARIANT, -- JSON object with detailed information
    
    -- Context
    SOURCE_TABLE VARCHAR(255),
    SOURCE_RECORD_ID VARCHAR(255),
    CORRELATION_ID VARCHAR(255),
    AFFECTED_USERS VARIANT, -- JSON array of affected users
    
    -- Status tracking
    STATUS VARCHAR(50) DEFAULT 'OPEN', -- 'OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'SUPPRESSED'
    ACKNOWLEDGED_BY VARCHAR(255),
    ACKNOWLEDGED_AT TIMESTAMP_LTZ,
    RESOLVED_BY VARCHAR(255),
    RESOLVED_AT TIMESTAMP_LTZ,
    RESOLUTION_NOTES VARCHAR(4000),
    
    -- Notification tracking
    NOTIFICATIONS_SENT VARIANT, -- JSON array of sent notifications
    LAST_NOTIFICATION_SENT_AT TIMESTAMP_LTZ,
    
    FOREIGN KEY (ALERT_ID) REFERENCES ALERT_DEFINITIONS(ALERT_ID)
);

-- =====================================================================
-- 6. STORED PROCEDURES FOR MONITORING OPERATIONS
-- =====================================================================

-- Procedure to log ETL job execution
CREATE OR REPLACE PROCEDURE LOG_ETL_JOB(
    job_name VARCHAR,
    job_type VARCHAR,
    status VARCHAR,
    start_time TIMESTAMP_LTZ,
    end_time TIMESTAMP_LTZ DEFAULT NULL,
    rows_processed NUMBER DEFAULT 0,
    error_message VARCHAR DEFAULT NULL,
    correlation_id VARCHAR DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    job_log_id VARCHAR;
    duration_seconds NUMBER;
BEGIN
    
    -- Generate unique job log ID
    SET job_log_id = job_name || '_' || DATE_PART('epoch', start_time);
    
    -- Calculate duration if end_time is provided
    IF (end_time IS NOT NULL) THEN
        SET duration_seconds = DATEDIFF('second', start_time, end_time);
    ELSE
        SET duration_seconds = NULL;
    END IF;
    
    -- Insert or update job log
    MERGE INTO ETL_JOB_LOGS AS target
    USING (
        SELECT 
            job_log_id AS JOB_LOG_ID,
            job_name AS JOB_NAME,
            job_type AS JOB_TYPE,
            start_time AS START_TIME,
            end_time AS END_TIME,
            duration_seconds AS DURATION_SECONDS,
            status AS STATUS,
            rows_processed AS ROWS_PROCESSED,
            error_message AS ERROR_MESSAGE,
            correlation_id AS CORRELATION_ID
    ) AS source
    ON target.JOB_LOG_ID = source.JOB_LOG_ID
    WHEN MATCHED THEN UPDATE SET
        END_TIME = source.END_TIME,
        DURATION_SECONDS = source.DURATION_SECONDS,
        STATUS = source.STATUS,
        ROWS_PROCESSED = source.ROWS_PROCESSED,
        ERROR_MESSAGE = source.ERROR_MESSAGE,
        UPDATED_AT = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (
        JOB_LOG_ID, JOB_NAME, JOB_TYPE, START_TIME, END_TIME,
        DURATION_SECONDS, STATUS, ROWS_PROCESSED, ERROR_MESSAGE, CORRELATION_ID
    ) VALUES (
        source.JOB_LOG_ID, source.JOB_NAME, source.JOB_TYPE, source.START_TIME, source.END_TIME,
        source.DURATION_SECONDS, source.STATUS, source.ROWS_PROCESSED, source.ERROR_MESSAGE, source.CORRELATION_ID
    );
    
    RETURN 'Logged ETL job: ' || job_log_id;
    
EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error logging ETL job: ' || SQLERRM;
END;
$$;

-- Procedure to log application errors
CREATE OR REPLACE PROCEDURE LOG_APPLICATION_ERROR(
    application_name VARCHAR,
    service_name VARCHAR,
    error_level VARCHAR,
    error_message VARCHAR,
    error_type VARCHAR DEFAULT NULL,
    user_id VARCHAR DEFAULT NULL,
    correlation_id VARCHAR DEFAULT NULL,
    custom_metadata VARIANT DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    error_log_id VARCHAR;
BEGIN
    
    -- Generate unique error log ID
    SET error_log_id = application_name || '_' || DATE_PART('epoch', CURRENT_TIMESTAMP()) || '_' || UNIFORM(1, 999999, RANDOM());
    
    -- Insert error log
    INSERT INTO APP_ERROR_LOGS (
        ERROR_LOG_ID, APPLICATION_NAME, SERVICE_NAME, ERROR_LEVEL,
        ERROR_MESSAGE, ERROR_TYPE, USER_ID, CORRELATION_ID,
        CUSTOM_METADATA, OCCURRED_AT
    ) VALUES (
        error_log_id, application_name, service_name, error_level,
        error_message, error_type, user_id, correlation_id,
        custom_metadata, CURRENT_TIMESTAMP()
    );
    
    -- Check for error patterns and update counts
    UPDATE ERROR_PATTERNS 
    SET 
        OCCURRENCE_COUNT = OCCURRENCE_COUNT + 1,
        LAST_SEEN_AT = CURRENT_TIMESTAMP()
    WHERE 
        (ERROR_MESSAGE_PATTERN IS NULL OR REGEXP_LIKE(error_message, ERROR_MESSAGE_PATTERN))
        AND (ERROR_TYPE_PATTERN IS NULL OR error_type LIKE ERROR_TYPE_PATTERN)
        AND (APPLICATION_NAME_PATTERN IS NULL OR application_name LIKE APPLICATION_NAME_PATTERN)
        AND (SERVICE_NAME_PATTERN IS NULL OR service_name LIKE SERVICE_NAME_PATTERN);
    
    RETURN 'Logged application error: ' || error_log_id;
    
EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error logging application error: ' || SQLERRM;
END;
$$;

-- Procedure to check and trigger alerts
CREATE OR REPLACE PROCEDURE CHECK_AND_TRIGGER_ALERTS()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    alerts_triggered NUMBER DEFAULT 0;
BEGIN
    
    -- Check for ETL job failures
    INSERT INTO ALERT_INSTANCES (
        INSTANCE_ID, ALERT_ID, TRIGGERED_AT, SEVERITY_LEVEL,
        ALERT_MESSAGE, ALERT_DETAILS, CORRELATION_ID
    )
    SELECT 
        'ETL_FAILURE_' || ejl.JOB_LOG_ID AS INSTANCE_ID,
        'ETL_JOB_FAILURE' AS ALERT_ID,
        ejl.END_TIME AS TRIGGERED_AT,
        'HIGH' AS SEVERITY_LEVEL,
        'ETL Job Failed: ' || ejl.JOB_NAME AS ALERT_MESSAGE,
        OBJECT_CONSTRUCT(
            'job_name', ejl.JOB_NAME,
            'job_type', ejl.JOB_TYPE,
            'error_message', ejl.ERROR_MESSAGE,
            'duration_seconds', ejl.DURATION_SECONDS
        ) AS ALERT_DETAILS,
        ejl.CORRELATION_ID
    FROM ETL_JOB_LOGS ejl
    WHERE ejl.STATUS = 'FAILED'
    AND ejl.END_TIME >= DATEADD('hour', -1, CURRENT_TIMESTAMP()) -- Last hour
    AND NOT EXISTS (
        SELECT 1 FROM ALERT_INSTANCES ai 
        WHERE ai.CORRELATION_ID = ejl.CORRELATION_ID
        AND ai.ALERT_ID = 'ETL_JOB_FAILURE'
    );
    
    GET DIAGNOSTICS alerts_triggered = ROW_COUNT;
    
    -- Check for high error rates
    INSERT INTO ALERT_INSTANCES (
        INSTANCE_ID, ALERT_ID, TRIGGERED_AT, SEVERITY_LEVEL,
        ALERT_MESSAGE, ALERT_DETAILS
    )
    SELECT 
        'HIGH_ERROR_RATE_' || application_name || '_' || DATE_PART('epoch', CURRENT_TIMESTAMP()) AS INSTANCE_ID,
        'HIGH_ERROR_RATE' AS ALERT_ID,
        CURRENT_TIMESTAMP() AS TRIGGERED_AT,
        CASE WHEN error_count > 100 THEN 'CRITICAL' WHEN error_count > 50 THEN 'HIGH' ELSE 'MEDIUM' END AS SEVERITY_LEVEL,
        'High error rate detected: ' || error_count || ' errors in last hour' AS ALERT_MESSAGE,
        OBJECT_CONSTRUCT(
            'application_name', application_name,
            'error_count', error_count,
            'time_window', 'last_hour'
        ) AS ALERT_DETAILS
    FROM (
        SELECT 
            APPLICATION_NAME,
            COUNT(*) AS error_count
        FROM APP_ERROR_LOGS
        WHERE ERROR_LEVEL IN ('ERROR', 'CRITICAL')
        AND OCCURRED_AT >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
        GROUP BY APPLICATION_NAME
        HAVING COUNT(*) > 20 -- Threshold for high error rate
    ) error_summary
    WHERE NOT EXISTS (
        SELECT 1 FROM ALERT_INSTANCES ai 
        WHERE ai.ALERT_ID = 'HIGH_ERROR_RATE'
        AND ai.TRIGGERED_AT >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
        AND ai.ALERT_DETAILS:application_name = error_summary.application_name
    );
    
    RETURN 'Triggered ' || alerts_triggered || ' new alerts';
    
EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error checking alerts: ' || SQLERRM;
END;
$$;

-- =====================================================================
-- 7. INDEXES AND PERFORMANCE OPTIMIZATION
-- =====================================================================

-- Create indexes for performance
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_ETL_JOB_LOGS_NAME_TIME ON ETL_JOB_LOGS(JOB_NAME, START_TIME);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_ETL_JOB_LOGS_STATUS ON ETL_JOB_LOGS(STATUS);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_ETL_JOB_LOGS_CORRELATION ON ETL_JOB_LOGS(CORRELATION_ID);
-- 
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_APP_ERROR_LOGS_APP_TIME ON APP_ERROR_LOGS(APPLICATION_NAME, OCCURRED_AT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_APP_ERROR_LOGS_LEVEL ON APP_ERROR_LOGS(ERROR_LEVEL);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_APP_ERROR_LOGS_CORRELATION ON APP_ERROR_LOGS(CORRELATION_ID);
-- 
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_SYSTEM_PERFORMANCE_APP_TIME ON SYSTEM_PERFORMANCE_METRICS(APPLICATION_NAME, METRIC_TIMESTAMP);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_SYSTEM_HEALTH_CHECKS_APP ON SYSTEM_HEALTH_CHECKS(APPLICATION_NAME, STATUS);
-- 
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_DATA_QUALITY_RESULTS_CHECK_TIME ON DATA_QUALITY_RESULTS(CHECK_ID, EXECUTED_AT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_ALERT_INSTANCES_TRIGGERED_AT ON ALERT_INSTANCES(TRIGGERED_AT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_ALERT_INSTANCES_STATUS ON ALERT_INSTANCES(STATUS);
-- 
-- =====================================================================
-- 8. GRANTS AND PERMISSIONS
-- =====================================================================

-- Grant access to ROLE_SOPHIA_AI_AGENT_SERVICE for monitoring operations
GRANT USAGE ON SCHEMA OPS_MONITORING TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA OPS_MONITORING TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA OPS_MONITORING TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;

-- Grant access to ROLE_SOPHIA_DEVELOPER for development monitoring
GRANT USAGE ON SCHEMA OPS_MONITORING TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON ALL TABLES IN SCHEMA OPS_MONITORING TO ROLE ROLE_SOPHIA_DEVELOPER;

-- Grant future permissions
GRANT SELECT, INSERT, UPDATE ON FUTURE TABLES IN SCHEMA OPS_MONITORING TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA OPS_MONITORING TO ROLE ROLE_SOPHIA_DEVELOPER;

-- =====================================================================
-- DEPLOYMENT NOTES
-- =====================================================================

/*
Deployment Steps:

1. Execute this script in SOPHIA_AI_DEV database
2. Verify all tables and procedures are created successfully
3. Test the stored procedures:
   - CALL LOG_ETL_JOB('test_job', 'TEST', 'SUCCESS', CURRENT_TIMESTAMP());
   - CALL LOG_APPLICATION_ERROR('SOPHIA_AI', 'TEST_SERVICE', 'INFO', 'Test error message');
   - CALL CHECK_AND_TRIGGER_ALERTS();

4. Set up monitoring dashboards to query these tables
5. Configure alert definitions for your specific use cases
6. Integrate with your application logging frameworks

Usage Examples:

-- Log an ETL job execution
CALL LOG_ETL_JOB(
    'GONG_CALLS_TRANSFORMATION', 'TRANSFORMATION', 'SUCCESS',
    '2024-01-15 10:00:00'::TIMESTAMP_LTZ, '2024-01-15 10:05:00'::TIMESTAMP_LTZ,
    1500, NULL, 'correlation_123'
);

-- Log an application error
CALL LOG_APPLICATION_ERROR(
    'SOPHIA_AI_BACKEND', 'AI_MEMORY_SERVICE', 'ERROR',
    'Failed to store embedding in business table', 'CortexEmbeddingError',
    'user_123', 'correlation_456', PARSE_JSON('{"deal_id": "deal_789"}')
);

-- Query recent ETL job performance
SELECT 
    JOB_NAME,
    AVG(DURATION_SECONDS) AS avg_duration,
    COUNT(*) AS total_runs,
    SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) AS successful_runs
FROM ETL_JOB_LOGS
WHERE START_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY JOB_NAME
ORDER BY avg_duration DESC;

-- Query error patterns
SELECT 
    APPLICATION_NAME,
    ERROR_TYPE,
    COUNT(*) AS error_count,
    MAX(OCCURRED_AT) AS last_occurrence
FROM APP_ERROR_LOGS
WHERE OCCURRED_AT >= DATEADD('day', -1, CURRENT_TIMESTAMP())
GROUP BY APPLICATION_NAME, ERROR_TYPE
ORDER BY error_count DESC;
*/ 