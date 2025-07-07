-- ===============================================================================
-- STAGING_ZONE SCHEMA - Intelligent Data Staging for Large Files
-- Implements "holding place" architecture for enterprise data ingestion
-- ===============================================================================

USE DATABASE SOPHIA_AI_PROD;

-- Create dedicated schema for staging operations
CREATE SCHEMA IF NOT EXISTS STAGING_ZONE
COMMENT = 'Intelligent staging area for large file processing and AI-assisted data discovery';

USE SCHEMA STAGING_ZONE;

-- ===============================================================================
-- 1. STAGED FILES - Main staging tracking table
-- ===============================================================================

CREATE TABLE IF NOT EXISTS STAGED_FILES (
    STAGE_ID VARCHAR(50) PRIMARY KEY,
    USER_ID VARCHAR(100) NOT NULL,
    FILENAME VARCHAR(500) NOT NULL,
    FILE_TYPE VARCHAR(100) NOT NULL,
    FILE_SIZE_BYTES INTEGER NOT NULL,
    ORIGINAL_PATH VARCHAR(1000),

    -- Staging Status and Progress
    STAGE_STATUS VARCHAR(50) DEFAULT 'uploaded', -- uploaded, analyzing, analyzed, reviewed, approved, rejected, processing, completed, failed
    ANALYSIS_PROGRESS FLOAT DEFAULT 0.0,
    PROCESSING_PROGRESS FLOAT DEFAULT 0.0,

    -- AI Analysis Results
    DETECTED_SCHEMA VARIANT,              -- AI-discovered field structure
    SUGGESTED_MAPPINGS VARIANT,           -- Field mapping suggestions
    DATA_PREVIEW VARIANT,                 -- Sample rows for preview (first 10 rows)
    FIELD_STATISTICS VARIANT,             -- Data quality metrics per field
    SUGGESTED_TARGET_SCHEMA VARCHAR(100), -- Recommended destination (SALESFORCE, GONG_DATA, HUBSPOT_DATA, etc.)
    CONTENT_ANALYSIS VARIANT,             -- Content type analysis and patterns

    -- Chunking Strategy
    RECOMMENDED_CHUNK_STRATEGY VARCHAR(50), -- 'content-aware', 'row-based', 'semantic', 'relationship-preserving'
    CHUNK_PREVIEW VARIANT,                -- Sample chunks with metadata
    TOTAL_ESTIMATED_CHUNKS INTEGER,       -- Estimated number of chunks

    -- User Decisions and Overrides
    USER_APPROVED_MAPPINGS VARIANT,       -- User-confirmed field mappings
    USER_SELECTED_TARGET VARCHAR(100),    -- User-chosen destination schema
    USER_CHUNK_PREFERENCES VARIANT,       -- User chunking preferences and parameters
    USER_PROCESSING_NOTES TEXT,           -- User comments and instructions

    -- Quality and Validation
    DATA_QUALITY_SCORE FLOAT,            -- Overall data quality score (0.0 to 1.0)
    VALIDATION_ERRORS VARIANT,           -- Array of validation issues
    CONFIDENCE_SCORE FLOAT,              -- AI confidence in analysis

    -- Safety and Lifecycle Management
    EXPIRY_DATE TIMESTAMP_NTZ,           -- Auto-cleanup date (default 7 days)
    SAFETY_BACKUP_PATH VARCHAR(1000),    -- Backup location for recovery
    RETENTION_POLICY VARCHAR(50) DEFAULT 'standard', -- standard, extended, permanent

    -- Processing Metadata
    ESTIMATED_PROCESSING_TIME_MINUTES INTEGER,
    ACTUAL_PROCESSING_TIME_MINUTES INTEGER,
    PROCESSING_COST_ESTIMATE FLOAT,

    -- Audit Trail
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    ANALYZED_AT TIMESTAMP_NTZ,
    APPROVED_AT TIMESTAMP_NTZ,
    PROCESSED_AT TIMESTAMP_NTZ,
    CREATED_BY VARCHAR(100),
    LAST_MODIFIED_BY VARCHAR(100)
);

-- ===============================================================================
-- 2. STAGED CHUNKS - Intelligent chunking for large files
-- ===============================================================================

CREATE TABLE IF NOT EXISTS STAGED_CHUNKS (
    CHUNK_ID VARCHAR(50) PRIMARY KEY,
    STAGE_ID VARCHAR(50) NOT NULL,
    CHUNK_SEQUENCE INTEGER NOT NULL,
    CHUNK_TYPE VARCHAR(50), -- 'header', 'data', 'metadata', 'relationship', 'summary'

    -- Chunk Content
    CHUNK_CONTENT VARIANT,               -- Actual chunk data
    CHUNK_TEXT TEXT,                     -- Text representation for search
    CHUNK_METADATA VARIANT,             -- Chunk-specific metadata
    CHUNK_SIZE_BYTES INTEGER,
    CHUNK_SIZE_TOKENS INTEGER,

    -- Relationships and Context
    PARENT_CHUNK_ID VARCHAR(50),         -- For hierarchical chunks
    RELATED_CHUNK_IDS ARRAY,             -- Related chunks for context
    BUSINESS_CONTEXT VARCHAR(200),       -- Business meaning of this chunk

    -- AI Processing
    EMBEDDING VECTOR(FLOAT, 768),        -- Semantic embedding
    SIMILARITY_HASH VARCHAR(100),        -- For deduplication
    PROCESSING_STATUS VARCHAR(50) DEFAULT 'pending',

    -- Quality Metrics
    CONTENT_QUALITY_SCORE FLOAT,
    SEMANTIC_COHERENCE_SCORE FLOAT,
    BUSINESS_RELEVANCE_SCORE FLOAT,

    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED_AT TIMESTAMP_NTZ,

    FOREIGN KEY (STAGE_ID) REFERENCES STAGED_FILES(STAGE_ID)
);

-- ===============================================================================
-- 3. STAGING INTERACTIONS - Chat interface tracking
-- ===============================================================================

CREATE TABLE IF NOT EXISTS STAGING_INTERACTIONS (
    INTERACTION_ID VARCHAR(50) PRIMARY KEY,
    STAGE_ID VARCHAR(50) NOT NULL,
    USER_ID VARCHAR(100) NOT NULL,

    -- Interaction Details
    INTERACTION_TYPE VARCHAR(50), -- 'query', 'command', 'approval', 'modification'
    USER_INPUT TEXT NOT NULL,
    AI_RESPONSE TEXT,
    COMMAND_EXECUTED VARCHAR(100),

    -- Context and Results
    INTERACTION_CONTEXT VARIANT,         -- Relevant context for the interaction
    EXECUTION_RESULT VARIANT,            -- Result of any commands executed
    MODIFICATIONS_MADE VARIANT,          -- Changes made to staging configuration

    -- Timing
    RESPONSE_TIME_MS INTEGER,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (STAGE_ID) REFERENCES STAGED_FILES(STAGE_ID)
);

-- ===============================================================================
-- 4. FIELD MAPPINGS - AI-suggested and user-confirmed mappings
-- ===============================================================================

CREATE TABLE IF NOT EXISTS FIELD_MAPPINGS (
    MAPPING_ID VARCHAR(50) PRIMARY KEY,
    STAGE_ID VARCHAR(50) NOT NULL,

    -- Source Field Information
    SOURCE_FIELD_NAME VARCHAR(200) NOT NULL,
    SOURCE_FIELD_TYPE VARCHAR(100),
    SOURCE_SAMPLE_VALUES ARRAY,
    SOURCE_STATISTICS VARIANT,

    -- Target Field Information
    SUGGESTED_TARGET_FIELD VARCHAR(200),
    SUGGESTED_TARGET_SCHEMA VARCHAR(100),
    SUGGESTED_TARGET_TYPE VARCHAR(100),
    MAPPING_CONFIDENCE FLOAT,

    -- User Decisions
    USER_CONFIRMED_TARGET VARCHAR(200),
    USER_CONFIRMED_SCHEMA VARCHAR(100),
    USER_TRANSFORMATION_RULES VARIANT,
    MAPPING_STATUS VARCHAR(50) DEFAULT 'suggested', -- suggested, confirmed, rejected, modified

    -- AI Analysis
    MAPPING_REASONING TEXT,               -- AI explanation for the mapping
    ALTERNATIVE_SUGGESTIONS ARRAY,        -- Other possible mappings

    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONFIRMED_AT TIMESTAMP_NTZ,
    CONFIRMED_BY VARCHAR(100),

    FOREIGN KEY (STAGE_ID) REFERENCES STAGED_FILES(STAGE_ID)
);

-- ===============================================================================
-- 5. PROCESSING JOBS - Track staging to final processing
-- ===============================================================================

CREATE TABLE IF NOT EXISTS STAGING_PROCESSING_JOBS (
    JOB_ID VARCHAR(50) PRIMARY KEY,
    STAGE_ID VARCHAR(50) NOT NULL,

    -- Job Configuration
    TARGET_SCHEMA VARCHAR(100) NOT NULL,
    TARGET_TABLES ARRAY,
    PROCESSING_TYPE VARCHAR(50), -- 'bulk_insert', 'incremental', 'replace'

    -- Processing Status
    JOB_STATUS VARCHAR(50) DEFAULT 'queued', -- queued, running, completed, failed, cancelled
    PROGRESS_PERCENTAGE FLOAT DEFAULT 0.0,
    CHUNKS_PROCESSED INTEGER DEFAULT 0,
    TOTAL_CHUNKS INTEGER,
    RECORDS_PROCESSED INTEGER DEFAULT 0,
    ERRORS_ENCOUNTERED INTEGER DEFAULT 0,

    -- Performance Metrics
    START_TIME TIMESTAMP_NTZ,
    END_TIME TIMESTAMP_NTZ,
    PROCESSING_DURATION_SECONDS INTEGER,
    COMPUTE_CREDITS_USED FLOAT,

    -- Results
    CREATED_ENTRIES ARRAY,               -- IDs of created knowledge entries
    TARGET_TABLE_UPDATES VARIANT,        -- Summary of table updates
    ERROR_LOG VARIANT,                   -- Detailed error information

    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (STAGE_ID) REFERENCES STAGED_FILES(STAGE_ID)
);

-- ===============================================================================
-- 6. PERFORMANCE VIEWS AND INDEXES
-- ===============================================================================

-- Performance view for staging dashboard
CREATE OR REPLACE VIEW STAGING_PERFORMANCE_SUMMARY AS
SELECT
    DATE(CREATED_AT) as STAGING_DATE,
    COUNT(*) as TOTAL_FILES_STAGED,
    COUNT(CASE WHEN STAGE_STATUS = 'completed' THEN 1 END) as COMPLETED_FILES,
    COUNT(CASE WHEN STAGE_STATUS = 'failed' THEN 1 END) as FAILED_FILES,
    AVG(ACTUAL_PROCESSING_TIME_MINUTES) as AVG_PROCESSING_TIME,
    SUM(FILE_SIZE_BYTES) as TOTAL_BYTES_PROCESSED,
    AVG(DATA_QUALITY_SCORE) as AVG_DATA_QUALITY,
    AVG(CONFIDENCE_SCORE) as AVG_AI_CONFIDENCE
FROM STAGED_FILES
WHERE CREATED_AT >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY DATE(CREATED_AT)
ORDER BY STAGING_DATE DESC;

-- Active staging summary
CREATE OR REPLACE VIEW ACTIVE_STAGING_SUMMARY AS
SELECT
    STAGE_STATUS,
    COUNT(*) as FILE_COUNT,
    AVG(ANALYSIS_PROGRESS) as AVG_ANALYSIS_PROGRESS,
    AVG(PROCESSING_PROGRESS) as AVG_PROCESSING_PROGRESS,
    SUM(FILE_SIZE_BYTES) as TOTAL_SIZE_BYTES
FROM STAGED_FILES
WHERE STAGE_STATUS NOT IN ('completed', 'failed')
GROUP BY STAGE_STATUS;

-- User staging activity
CREATE OR REPLACE VIEW USER_STAGING_ACTIVITY AS
SELECT
    USER_ID,
    COUNT(*) as FILES_STAGED,
    SUM(FILE_SIZE_BYTES) as TOTAL_BYTES,
    AVG(DATA_QUALITY_SCORE) as AVG_QUALITY_SCORE,
    MAX(CREATED_AT) as LAST_STAGING_DATE,
    COUNT(CASE WHEN STAGE_STATUS = 'completed' THEN 1 END) as SUCCESSFUL_PROCESSES
FROM STAGED_FILES
WHERE CREATED_AT >= DATEADD(day, -90, CURRENT_TIMESTAMP())
GROUP BY USER_ID
ORDER BY FILES_STAGED DESC;

-- ===============================================================================
-- 7. AUTOMATED TASKS FOR STAGING MANAGEMENT
-- ===============================================================================

-- Cleanup expired staging files
CREATE OR REPLACE TASK TASK_CLEANUP_EXPIRED_STAGING
    WAREHOUSE = WH_SOPHIA_AI_PROCESSING
    SCHEDULE = 'USING CRON 0 2 * * * UTC'
    COMMENT = 'Clean up expired staging files and associated data'
AS
    CALL CLEANUP_EXPIRED_STAGING_DATA();

-- Update staging metrics
CREATE OR REPLACE TASK TASK_UPDATE_STAGING_METRICS
    WAREHOUSE = WH_SOPHIA_AI_PROCESSING
    SCHEDULE = 'USING CRON 0 */6 * * * UTC'
    COMMENT = 'Update staging performance metrics and analytics'
AS
    CALL UPDATE_STAGING_ANALYTICS();

-- ===============================================================================
-- 8. GRANTS AND PERMISSIONS
-- ===============================================================================

-- Grant access to Sophia AI application role
GRANT USAGE ON SCHEMA STAGING_ZONE TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA STAGING_ZONE TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA STAGING_ZONE TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;

-- Grant read access to developers
GRANT USAGE ON SCHEMA STAGING_ZONE TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT ON ALL TABLES IN SCHEMA STAGING_ZONE TO ROLE ROLE_SOPHIA_DEVELOPER;

-- Grant future permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA STAGING_ZONE TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;

-- ===============================================================================
-- 9. SAMPLE DATA AND TESTING
-- ===============================================================================

-- Insert sample staging configuration
INSERT INTO STAGED_FILES (
    STAGE_ID, USER_ID, FILENAME, FILE_TYPE, FILE_SIZE_BYTES,
    STAGE_STATUS, SUGGESTED_TARGET_SCHEMA, DATA_QUALITY_SCORE, CONFIDENCE_SCORE,
    EXPIRY_DATE
) VALUES (
    'stage_sample_001', 'ceo_user', 'salesforce_export_sample.csv', 'text/csv', 2560000,
    'analyzed', 'SALESFORCE', 0.92, 0.87,
    DATEADD(day, 7, CURRENT_TIMESTAMP())
);

SELECT 'STAGING_ZONE Schema Creation Complete!' as STATUS,
       CURRENT_DATABASE() as DATABASE_NAME,
       CURRENT_SCHEMA() as SCHEMA_NAME,
       CURRENT_TIMESTAMP() as COMPLETION_TIME;
