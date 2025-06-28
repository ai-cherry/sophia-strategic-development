-- =====================================================================
-- CONFIG Schema - Application Configuration Management
-- =====================================================================
-- 
-- This script creates the CONFIG schema for storing application settings,
-- feature flags, environment-specific configurations, and system parameters.
-- 
-- Features:
-- - Environment-specific application settings
-- - Feature flags and toggles
-- - System configuration parameters
-- - Configuration versioning and history
-- - Dynamic configuration updates
-- 
-- Usage: Execute in SOPHIA_AI_DEV database
-- =====================================================================

-- Set context for DEV environment
-- USE DATABASE SOPHIA_AI_DEV;
CREATE SCHEMA IF NOT EXISTS CONFIG;
-- USE SCHEMA CONFIG;

-- =====================================================================
-- 1. APPLICATION SETTINGS TABLES
-- =====================================================================

-- Application settings table for storing key-value configuration pairs
CREATE TABLE IF NOT EXISTS APPLICATION_SETTINGS (
    SETTING_ID VARCHAR(255) PRIMARY KEY,
    SETTING_NAME VARCHAR(255) NOT NULL,
    SETTING_VALUE VARCHAR(16777216), -- Support large configuration values (JSON, etc.)
    DATA_TYPE VARCHAR(50) NOT NULL, -- 'STRING', 'NUMBER', 'BOOLEAN', 'JSON', 'TEXT'
    DESCRIPTION VARCHAR(1000),
    
    -- Environment and scope
    ENVIRONMENT VARCHAR(50) NOT NULL DEFAULT 'DEV', -- 'DEV', 'STAGING', 'PRODUCTION'
    APPLICATION_NAME VARCHAR(255) NOT NULL, -- 'SOPHIA_AI_BACKEND', 'AI_MEMORY_MCP', etc.
    SERVICE_NAME VARCHAR(255), -- Optional service-specific settings
    COMPONENT_NAME VARCHAR(255), -- Optional component-specific settings
    
    -- Setting metadata
    CATEGORY VARCHAR(100), -- 'DATABASE', 'API', 'SECURITY', 'FEATURE_FLAGS', etc.
    IS_SENSITIVE BOOLEAN DEFAULT FALSE, -- Whether this setting contains sensitive data
    IS_ENCRYPTED BOOLEAN DEFAULT FALSE, -- Whether the value is encrypted
    ENCRYPTION_METHOD VARCHAR(100), -- Encryption method used (if encrypted)
    
    -- Validation and constraints
    VALIDATION_RULE VARCHAR(1000), -- Validation expression or pattern
    MIN_VALUE FLOAT, -- For numeric settings
    MAX_VALUE FLOAT, -- For numeric settings
    ALLOWED_VALUES TEXT, -- JSON array of allowed values
    
    -- Lifecycle management
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    IS_READONLY BOOLEAN DEFAULT FALSE, -- Prevent accidental changes
    REQUIRES_RESTART BOOLEAN DEFAULT FALSE, -- Whether changing this setting requires app restart
    
    -- Change tracking
    VERSION NUMBER DEFAULT 1,
    PREVIOUS_VALUE VARCHAR(16777216), -- Previous value for rollback
    CHANGED_BY VARCHAR(255), -- User or system that made the change
    CHANGED_AT TIMESTAMP,
    CHANGE_REASON VARCHAR(1000), -- Reason for the change
    
    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(255),
    
    -- Constraints
    UNIQUE (SETTING_NAME, ENVIRONMENT, APPLICATION_NAME, SERVICE_NAME, COMPONENT_NAME)
);

-- Configuration history table for tracking changes
CREATE TABLE IF NOT EXISTS CONFIGURATION_HISTORY (
    HISTORY_ID VARCHAR(255) PRIMARY KEY,
    SETTING_ID VARCHAR(255) NOT NULL,
    
    -- Change details
    CHANGE_TYPE VARCHAR(50) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'ROLLBACK'
    OLD_VALUE VARCHAR(16777216),
    NEW_VALUE VARCHAR(16777216),
    OLD_VERSION NUMBER,
    NEW_VERSION NUMBER,
    
    -- Change context
    CHANGED_BY VARCHAR(255) NOT NULL,
    CHANGED_AT TIMESTAMP NOT NULL,
    CHANGE_REASON VARCHAR(1000),
    CHANGE_SOURCE VARCHAR(100), -- 'ADMIN_UI', 'API', 'SCRIPT', 'AUTOMATED'
    
    -- Impact tracking
    AFFECTED_SERVICES TEXT, -- JSON array of services affected by this change
    ROLLBACK_REQUIRED BOOLEAN DEFAULT FALSE,
    ROLLBACK_COMPLETED BOOLEAN DEFAULT FALSE,
    ROLLBACK_COMPLETED_AT TIMESTAMP,
    
    -- Additional metadata
    CHANGE_METADATA TEXT, -- JSON object for additional change context
    
    FOREIGN KEY (SETTING_ID) REFERENCES APPLICATION_SETTINGS(SETTING_ID)
);

-- =====================================================================
-- 2. FEATURE FLAGS AND TOGGLES
-- =====================================================================

-- Feature flags table for controlling feature availability
CREATE TABLE IF NOT EXISTS FEATURE_FLAGS (
    FLAG_ID VARCHAR(255) PRIMARY KEY,
    FLAG_NAME VARCHAR(255) NOT NULL,
    FLAG_DESCRIPTION VARCHAR(1000),
    
    -- Flag configuration
    IS_ENABLED BOOLEAN DEFAULT FALSE,
    FLAG_TYPE VARCHAR(50) DEFAULT 'BOOLEAN', -- 'BOOLEAN', 'PERCENTAGE', 'WHITELIST', 'EXPERIMENT'
    
    -- Environment and scope
    ENVIRONMENT VARCHAR(50) NOT NULL DEFAULT 'DEV',
    APPLICATION_NAME VARCHAR(255) NOT NULL,
    SERVICE_NAME VARCHAR(255),
    
    -- Targeting and rollout
    ROLLOUT_PERCENTAGE FLOAT DEFAULT 0, -- For percentage-based rollouts (0-100)
    TARGET_USERS TEXT, -- JSON array of specific users to target
    TARGET_GROUPS TEXT, -- JSON array of user groups to target
    TARGET_CONDITIONS TEXT, -- JSON object with targeting conditions
    
    -- Experiment configuration (for A/B testing)
    EXPERIMENT_NAME VARCHAR(255),
    EXPERIMENT_VARIANTS TEXT, -- JSON object defining experiment variants
    TRAFFIC_ALLOCATION TEXT, -- JSON object defining traffic split
    
    -- Lifecycle management
    START_DATE TIMESTAMP, -- When this flag becomes active
    END_DATE TIMESTAMP, -- When this flag should be disabled
    IS_PERMANENT BOOLEAN DEFAULT FALSE, -- Whether this is a permanent flag
    CLEANUP_DATE TIMESTAMP, -- When this flag can be safely removed
    
    -- Monitoring and metrics
    USAGE_COUNT NUMBER DEFAULT 0, -- How many times this flag has been evaluated
    LAST_EVALUATED_AT TIMESTAMP,
    PERFORMANCE_IMPACT VARCHAR(1000), -- Notes on performance impact
    
    -- Dependencies
    DEPENDS_ON_FLAGS TEXT, -- JSON array of other flags this depends on
    CONFLICTS_WITH_FLAGS TEXT, -- JSON array of flags that conflict with this one
    
    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(255),
    LAST_MODIFIED_BY VARCHAR(255),
    
    -- Constraints
    UNIQUE (FLAG_NAME, ENVIRONMENT, APPLICATION_NAME, SERVICE_NAME)
);

-- Feature flag evaluation logs
CREATE TABLE IF NOT EXISTS FEATURE_FLAG_EVALUATIONS (
    EVALUATION_ID VARCHAR(255) PRIMARY KEY,
    FLAG_ID VARCHAR(255) NOT NULL,
    
    -- Evaluation context
    USER_ID VARCHAR(255),
    SESSION_ID VARCHAR(255),
    REQUEST_ID VARCHAR(255),
    
    -- Evaluation result
    EVALUATED_AT TIMESTAMP NOT NULL,
    RESULT_VALUE TEXT, -- The actual result (boolean, string, number, object)
    EVALUATION_REASON VARCHAR(255), -- Why this result was returned
    
    -- Context information
    USER_PROPERTIES TEXT, -- JSON object with user properties used in evaluation
    REQUEST_PROPERTIES TEXT, -- JSON object with request properties
    
    -- Performance tracking
    EVALUATION_TIME_MS NUMBER, -- Time taken to evaluate the flag
    CACHE_HIT BOOLEAN DEFAULT FALSE, -- Whether the result came from cache
    
    -- Metadata
    APPLICATION_NAME VARCHAR(255),
    SERVICE_NAME VARCHAR(255),
    ENVIRONMENT VARCHAR(50),
    
    FOREIGN KEY (FLAG_ID) REFERENCES FEATURE_FLAGS(FLAG_ID)
);

-- =====================================================================
-- 3. SYSTEM CONFIGURATION PARAMETERS
-- =====================================================================

-- System parameters table for technical configuration
CREATE TABLE IF NOT EXISTS SYSTEM_PARAMETERS (
    PARAMETER_ID VARCHAR(255) PRIMARY KEY,
    PARAMETER_NAME VARCHAR(255) NOT NULL,
    PARAMETER_VALUE VARCHAR(16777216),
    DATA_TYPE VARCHAR(50) NOT NULL,
    DESCRIPTION VARCHAR(1000),
    
    -- Parameter classification
    CATEGORY VARCHAR(100) NOT NULL, -- 'DATABASE', 'CACHE', 'SECURITY', 'PERFORMANCE', etc.
    SUBCATEGORY VARCHAR(100),
    PRIORITY_LEVEL VARCHAR(50) DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    
    -- Environment scope
    ENVIRONMENT VARCHAR(50) NOT NULL DEFAULT 'DEV',
    APPLIES_TO_ALL_ENVIRONMENTS BOOLEAN DEFAULT FALSE,
    
    -- Validation and constraints
    VALIDATION_PATTERN VARCHAR(1000), -- Regex or validation rule
    MIN_VALUE FLOAT,
    MAX_VALUE FLOAT,
    ALLOWED_VALUES TEXT,
    UNIT_OF_MEASURE VARCHAR(50), -- 'SECONDS', 'MB', 'PERCENT', etc.
    
    -- Impact and dependencies
    REQUIRES_RESTART BOOLEAN DEFAULT FALSE,
    AFFECTS_PERFORMANCE BOOLEAN DEFAULT FALSE,
    AFFECTS_SECURITY BOOLEAN DEFAULT FALSE,
    DEPENDENT_PARAMETERS TEXT, -- JSON array of dependent parameters
    
    -- Monitoring
    CURRENT_USAGE_VALUE FLOAT, -- Current actual usage (for monitoring)
    USAGE_THRESHOLD_WARNING FLOAT, -- Warning threshold
    USAGE_THRESHOLD_CRITICAL FLOAT, -- Critical threshold
    LAST_MONITORED_AT TIMESTAMP,
    
    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(255),
    LAST_MODIFIED_BY VARCHAR(255),
    
    UNIQUE (PARAMETER_NAME, ENVIRONMENT)
);

-- Configuration templates for easy environment setup
CREATE TABLE IF NOT EXISTS CONFIGURATION_TEMPLATES (
    TEMPLATE_ID VARCHAR(255) PRIMARY KEY,
    TEMPLATE_NAME VARCHAR(255) NOT NULL,
    TEMPLATE_DESCRIPTION VARCHAR(1000),
    
    -- Template scope
    TEMPLATE_TYPE VARCHAR(100), -- 'ENVIRONMENT_SETUP', 'SERVICE_CONFIG', 'FEATURE_SET'
    TARGET_ENVIRONMENT VARCHAR(50), -- Environment this template is designed for
    APPLICATION_NAME VARCHAR(255),
    SERVICE_NAME VARCHAR(255),
    
    -- Template content
    CONFIGURATION_JSON TEXT NOT NULL, -- JSON object with all configuration settings
    FEATURE_FLAGS_JSON TEXT, -- JSON object with feature flag settings
    SYSTEM_PARAMETERS_JSON TEXT, -- JSON object with system parameters
    
    -- Template metadata
    VERSION VARCHAR(50) DEFAULT '1.0',
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    IS_DEFAULT BOOLEAN DEFAULT FALSE, -- Whether this is the default template for the scope
    
    -- Usage tracking
    USAGE_COUNT NUMBER DEFAULT 0,
    LAST_USED_AT TIMESTAMP,
    LAST_USED_BY VARCHAR(255),
    
    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(255),
    
    UNIQUE (TEMPLATE_NAME, TARGET_ENVIRONMENT, APPLICATION_NAME)
);

-- =====================================================================
-- 4. CONFIGURATION VALIDATION AND DEPLOYMENT
-- =====================================================================

-- Configuration validation rules
CREATE TABLE IF NOT EXISTS CONFIGURATION_VALIDATION_RULES (
    RULE_ID VARCHAR(255) PRIMARY KEY,
    RULE_NAME VARCHAR(255) NOT NULL,
    RULE_DESCRIPTION VARCHAR(1000),
    
    -- Rule scope
    APPLIES_TO_SETTINGS BOOLEAN DEFAULT TRUE,
    APPLIES_TO_FLAGS BOOLEAN DEFAULT TRUE,
    APPLIES_TO_PARAMETERS BOOLEAN DEFAULT TRUE,
    TARGET_CATEGORY VARCHAR(100), -- Optional category filter
    TARGET_ENVIRONMENT VARCHAR(50), -- Optional environment filter
    
    -- Validation logic
    VALIDATION_TYPE VARCHAR(100), -- 'REGEX', 'RANGE', 'DEPENDENCY', 'CUSTOM_SQL', 'JAVASCRIPT'
    VALIDATION_EXPRESSION VARCHAR(4000), -- The actual validation logic
    ERROR_MESSAGE VARCHAR(1000), -- Message to show when validation fails
    
    -- Rule metadata
    SEVERITY_LEVEL VARCHAR(50) DEFAULT 'ERROR', -- 'WARNING', 'ERROR', 'CRITICAL'
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(255)
);

-- Configuration deployment tracking
CREATE TABLE IF NOT EXISTS CONFIGURATION_DEPLOYMENTS (
    DEPLOYMENT_ID VARCHAR(255) PRIMARY KEY,
    DEPLOYMENT_NAME VARCHAR(255),
    
    -- Deployment details
    SOURCE_ENVIRONMENT VARCHAR(50), -- Environment configuration is copied from
    TARGET_ENVIRONMENT VARCHAR(50) NOT NULL, -- Environment configuration is deployed to
    DEPLOYMENT_TYPE VARCHAR(100), -- 'FULL', 'PARTIAL', 'ROLLBACK', 'TEMPLATE'
    
    -- Deployment content
    SETTINGS_DEPLOYED TEXT, -- JSON array of setting IDs deployed
    FLAGS_DEPLOYED TEXT, -- JSON array of flag IDs deployed
    PARAMETERS_DEPLOYED TEXT, -- JSON array of parameter IDs deployed
    TEMPLATE_USED VARCHAR(255), -- Template ID if deployment used a template
    
    -- Deployment status
    STATUS VARCHAR(50) DEFAULT 'PENDING', -- 'PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED', 'ROLLED_BACK'
    STARTED_AT TIMESTAMP,
    COMPLETED_AT TIMESTAMP,
    DURATION_SECONDS NUMBER,
    
    -- Validation and testing
    VALIDATION_PASSED BOOLEAN,
    VALIDATION_ERRORS TEXT, -- JSON array of validation errors
    SMOKE_TESTS_PASSED BOOLEAN,
    SMOKE_TEST_RESULTS TEXT, -- JSON object with smoke test results
    
    -- Rollback information
    ROLLBACK_DEPLOYMENT_ID VARCHAR(255), -- Reference to rollback deployment if this was rolled back
    CAN_ROLLBACK BOOLEAN DEFAULT TRUE,
    ROLLBACK_DEADLINE TIMESTAMP, -- After this time, rollback may not be safe
    
    -- Impact tracking
    AFFECTED_SERVICES TEXT, -- JSON array of services affected
    DOWNTIME_REQUIRED BOOLEAN DEFAULT FALSE,
    ESTIMATED_IMPACT VARCHAR(1000),
    ACTUAL_IMPACT VARCHAR(1000),
    
    -- Metadata
    INITIATED_BY VARCHAR(255) NOT NULL,
    APPROVED_BY VARCHAR(255), -- For production deployments
    DEPLOYMENT_NOTES VARCHAR(4000),
    
    FOREIGN KEY (ROLLBACK_DEPLOYMENT_ID) REFERENCES CONFIGURATION_DEPLOYMENTS(DEPLOYMENT_ID)
);

-- =====================================================================
-- 5. STORED PROCEDURES FOR CONFIGURATION MANAGEMENT
-- =====================================================================

-- Procedure to get configuration value with fallback
CREATE OR REPLACE FUNCTION GET_CONFIG_VALUE(
    setting_name VARCHAR,
    environment VARCHAR DEFAULT 'DEV',
    application_name VARCHAR DEFAULT 'SOPHIA_AI',
    service_name VARCHAR DEFAULT NULL,
    component_name VARCHAR DEFAULT NULL
)
RETURNS TEXT
LANGUAGE SQL
AS
$$
    SELECT 
        CASE 
            WHEN DATA_TYPE = 'NUMBER' THEN TO_VARIANT(TO_NUMBER(SETTING_VALUE))
            WHEN DATA_TYPE = 'BOOLEAN' THEN TO_VARIANT(TO_BOOLEAN(SETTING_VALUE))
            WHEN DATA_TYPE = 'JSON' THEN PARSE_JSON(SETTING_VALUE)
            WHEN DATA_TYPE = 'TEXT' THEN PARSE_JSON(SETTING_VALUE)
            ELSE TO_VARIANT(SETTING_VALUE)
        END
    FROM APPLICATION_SETTINGS
    WHERE SETTING_NAME = setting_name
    AND ENVIRONMENT = environment
    AND APPLICATION_NAME = application_name
    AND (SERVICE_NAME = service_name OR (service_name IS NULL AND SERVICE_NAME IS NULL))
    AND (COMPONENT_NAME = component_name OR (component_name IS NULL AND COMPONENT_NAME IS NULL))
    AND IS_ACTIVE = TRUE
    ORDER BY 
        CASE WHEN SERVICE_NAME IS NOT NULL THEN 1 ELSE 2 END,
        CASE WHEN COMPONENT_NAME IS NOT NULL THEN 1 ELSE 2 END
    LIMIT 1
$$;

-- Procedure to evaluate feature flag
CREATE OR REPLACE FUNCTION EVALUATE_FEATURE_FLAG(
    flag_name VARCHAR,
    user_id VARCHAR DEFAULT NULL,
    environment VARCHAR DEFAULT 'DEV',
    application_name VARCHAR DEFAULT 'SOPHIA_AI',
    service_name VARCHAR DEFAULT NULL,
    user_properties TEXT DEFAULT NULL
)
RETURNS TEXT
LANGUAGE SQL
AS
$$
    WITH flag_config AS (
        SELECT 
            FLAG_ID, IS_ENABLED, FLAG_TYPE, ROLLOUT_PERCENTAGE,
            TARGET_USERS, TARGET_GROUPS, TARGET_CONDITIONS
        FROM FEATURE_FLAGS
        WHERE FLAG_NAME = flag_name
        AND ENVIRONMENT = environment
        AND APPLICATION_NAME = application_name
        AND (SERVICE_NAME = service_name OR (service_name IS NULL AND SERVICE_NAME IS NULL))
        AND (START_DATE IS NULL OR START_DATE <= CURRENT_TIMESTAMP)
        AND (END_DATE IS NULL OR END_DATE > CURRENT_TIMESTAMP)
        LIMIT 1
    )
    SELECT 
        CASE 
            WHEN NOT IS_ENABLED THEN TO_VARIANT(FALSE)
            WHEN FLAG_TYPE = 'BOOLEAN' THEN TO_VARIANT(IS_ENABLED)
            WHEN FLAG_TYPE = 'PERCENTAGE' THEN 
                TO_VARIANT(
                    CASE 
                        WHEN user_id IS NULL THEN FALSE
                        WHEN (HASH(user_id) % 100) < ROLLOUT_PERCENTAGE THEN TRUE
                        ELSE FALSE
                    END
                )
            WHEN FLAG_TYPE = 'WHITELIST' THEN 
                TO_VARIANT(
                    CASE 
                        WHEN user_id IS NULL THEN FALSE
                        WHEN ARRAY_CONTAINS(user_id::TEXT, TARGET_USERS) THEN TRUE
                        ELSE FALSE
                    END
                )
            ELSE TO_VARIANT(IS_ENABLED)
        END
    FROM flag_config
$$;

-- Procedure to update configuration setting
CREATE OR REPLACE PROCEDURE UPDATE_CONFIG_SETTING(
    setting_name VARCHAR,
    new_value VARCHAR,
    environment VARCHAR DEFAULT 'DEV',
    application_name VARCHAR DEFAULT 'SOPHIA_AI',
    service_name VARCHAR DEFAULT NULL,
    component_name VARCHAR DEFAULT NULL,
    changed_by VARCHAR DEFAULT 'SYSTEM',
    change_reason VARCHAR DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    setting_id VARCHAR;
    old_value VARCHAR;
    old_version NUMBER;
    new_version NUMBER;
BEGIN
    
    -- Get current setting details
    SELECT SETTING_ID, SETTING_VALUE, VERSION
    INTO setting_id, old_value, old_version
    FROM APPLICATION_SETTINGS
    WHERE SETTING_NAME = setting_name
    AND ENVIRONMENT = environment
    AND APPLICATION_NAME = application_name
    AND (SERVICE_NAME = service_name OR (service_name IS NULL AND SERVICE_NAME IS NULL))
    AND (COMPONENT_NAME = component_name OR (component_name IS NULL AND COMPONENT_NAME IS NULL));
    
    IF (setting_id IS NULL) THEN
        RETURN 'Setting not found: ' || setting_name;
    END IF;
    
    -- Calculate new version
--     new_version := old_version + 1;
    
    -- Update the setting
    UPDATE APPLICATION_SETTINGS
    SET 
        SETTING_VALUE = new_value,
        PREVIOUS_VALUE = old_value,
        VERSION = new_version,
        CHANGED_BY = changed_by,
        CHANGED_AT = CURRENT_TIMESTAMP,
        CHANGE_REASON = change_reason,
        UPDATED_AT = CURRENT_TIMESTAMP
    WHERE SETTING_ID = setting_id;
    
    -- Log the change in history
    INSERT INTO CONFIGURATION_HISTORY (
        HISTORY_ID, SETTING_ID, CHANGE_TYPE, OLD_VALUE, NEW_VALUE,
        OLD_VERSION, NEW_VERSION, CHANGED_BY, CHANGED_AT, CHANGE_REASON, CHANGE_SOURCE
    ) VALUES (
        setting_id || '_' || new_version, setting_id, 'UPDATE', old_value, new_value,
        old_version, new_version, changed_by, CURRENT_TIMESTAMP, change_reason, 'PROCEDURE'
    );
    
    RETURN 'Successfully updated setting: ' || setting_name || ' to version ' || new_version;
    
-- EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error updating setting: ' || SQLERRM;
END;
$$;

-- Procedure to deploy configuration template
CREATE OR REPLACE PROCEDURE DEPLOY_CONFIGURATION_TEMPLATE(
    template_id VARCHAR,
    target_environment VARCHAR,
    deployed_by VARCHAR,
    deployment_notes VARCHAR DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    deployment_id VARCHAR;
    template_config TEXT;
    settings_count NUMBER DEFAULT 0;
BEGIN
    
    -- Generate deployment ID
    SET deployment_id = 'DEPLOY_' || template_id || '_' || target_environment || '_' || DATE_PART('epoch', CURRENT_TIMESTAMP);
    
    -- Get template configuration
    SELECT CONFIGURATION_JSON
    INTO template_config
    FROM CONFIGURATION_TEMPLATES
    WHERE TEMPLATE_ID = template_id AND IS_ACTIVE = TRUE;
    
    IF (template_config IS NULL) THEN
        RETURN 'Template not found or inactive: ' || template_id;
    END IF;
    
    -- Create deployment record
    INSERT INTO CONFIGURATION_DEPLOYMENTS (
        DEPLOYMENT_ID, DEPLOYMENT_NAME, TARGET_ENVIRONMENT, DEPLOYMENT_TYPE,
        TEMPLATE_USED, STATUS, STARTED_AT, INITIATED_BY, DEPLOYMENT_NOTES
    ) VALUES (
        deployment_id, 'Template Deployment: ' || template_id, target_environment, 'TEMPLATE',
        template_id, 'IN_PROGRESS', CURRENT_TIMESTAMP, deployed_by, deployment_notes
    );
    
    -- Deploy each setting from the template
    -- Note: This is a simplified version - in practice, you'd iterate through the JSON
    -- and create/update individual settings
    
    -- Update deployment status
    UPDATE CONFIGURATION_DEPLOYMENTS
    SET 
        STATUS = 'SUCCESS',
        COMPLETED_AT = CURRENT_TIMESTAMP,
        DURATION_SECONDS = DATEDIFF('second', STARTED_AT, CURRENT_TIMESTAMP)
    WHERE DEPLOYMENT_ID = deployment_id;
    
    -- Update template usage
    UPDATE CONFIGURATION_TEMPLATES
    SET 
        USAGE_COUNT = USAGE_COUNT + 1,
        LAST_USED_AT = CURRENT_TIMESTAMP,
        LAST_USED_BY = deployed_by
    WHERE TEMPLATE_ID = template_id;
    
    RETURN 'Successfully deployed template ' || template_id || ' to ' || target_environment || ' (Deployment: ' || deployment_id || ')';
    
-- EXCEPTION
    WHEN OTHER THEN
        -- Update deployment status to failed
        UPDATE CONFIGURATION_DEPLOYMENTS
        SET STATUS = 'FAILED', COMPLETED_AT = CURRENT_TIMESTAMP
        WHERE DEPLOYMENT_ID = deployment_id;
        
        RETURN 'Error deploying template: ' || SQLERRM;
END;
$$;

-- =====================================================================
-- 6. INITIAL CONFIGURATION DATA
-- =====================================================================

-- Insert default application settings for Sophia AI
INSERT INTO APPLICATION_SETTINGS (
    SETTING_ID, SETTING_NAME, SETTING_VALUE, DATA_TYPE, DESCRIPTION,
    ENVIRONMENT, APPLICATION_NAME, CATEGORY
) VALUES 
    -- Database settings
    ('DB_CONNECTION_POOL_SIZE_DEV', 'database.connection_pool_size', '10', 'NUMBER', 'Maximum database connection pool size', 'DEV', 'SOPHIA_AI', 'DATABASE'),
    ('DB_QUERY_TIMEOUT_DEV', 'database.query_timeout_seconds', '30', 'NUMBER', 'Database query timeout in seconds', 'DEV', 'SOPHIA_AI', 'DATABASE'),
    ('DB_RETRY_ATTEMPTS_DEV', 'database.retry_attempts', '3', 'NUMBER', 'Number of retry attempts for failed database operations', 'DEV', 'SOPHIA_AI', 'DATABASE'),
    
    -- API settings
    ('API_RATE_LIMIT_DEV', 'api.rate_limit_per_minute', '1000', 'NUMBER', 'API rate limit per minute per user', 'DEV', 'SOPHIA_AI', 'API'),
    ('API_TIMEOUT_DEV', 'api.request_timeout_seconds', '60', 'NUMBER', 'API request timeout in seconds', 'DEV', 'SOPHIA_AI', 'API'),
    ('API_MAX_PAYLOAD_SIZE_DEV', 'api.max_payload_size_mb', '10', 'NUMBER', 'Maximum API payload size in MB', 'DEV', 'SOPHIA_AI', 'API'),
    
    -- AI Memory settings
    ('AI_MEMORY_EMBEDDING_MODEL_DEV', 'ai_memory.embedding_model', 'e5-base-v2', 'STRING', 'Default embedding model for AI Memory', 'DEV', 'SOPHIA_AI', 'AI_MEMORY'),
    ('AI_MEMORY_SIMILARITY_THRESHOLD_DEV', 'ai_memory.similarity_threshold', '0.7', 'NUMBER', 'Default similarity threshold for vector search', 'DEV', 'SOPHIA_AI', 'AI_MEMORY'),
    ('AI_MEMORY_MAX_RESULTS_DEV', 'ai_memory.max_search_results', '10', 'NUMBER', 'Maximum number of results returned by memory search', 'DEV', 'SOPHIA_AI', 'AI_MEMORY'),
    
    -- Snowflake Cortex settings
    ('CORTEX_BATCH_SIZE_DEV', 'cortex.batch_processing_size', '100', 'NUMBER', 'Batch size for Cortex AI processing', 'DEV', 'SOPHIA_AI', 'CORTEX'),
    ('CORTEX_RETRY_ATTEMPTS_DEV', 'cortex.retry_attempts', '3', 'NUMBER', 'Number of retry attempts for Cortex operations', 'DEV', 'SOPHIA_AI', 'CORTEX'),
    
    -- Security settings
    ('SECURITY_JWT_EXPIRY_DEV', 'security.jwt_expiry_hours', '24', 'NUMBER', 'JWT token expiry time in hours', 'DEV', 'SOPHIA_AI', 'SECURITY'),
    ('SECURITY_MAX_LOGIN_ATTEMPTS_DEV', 'security.max_login_attempts', '5', 'NUMBER', 'Maximum login attempts before lockout', 'DEV', 'SOPHIA_AI', 'SECURITY'),
    
    -- Performance settings
    ('PERF_CACHE_TTL_DEV', 'performance.cache_ttl_seconds', '300', 'NUMBER', 'Default cache TTL in seconds', 'DEV', 'SOPHIA_AI', 'PERFORMANCE'),
    ('PERF_ASYNC_BATCH_SIZE_DEV', 'performance.async_batch_size', '50', 'NUMBER', 'Batch size for async operations', 'DEV', 'SOPHIA_AI', 'PERFORMANCE');

-- Insert default feature flags
INSERT INTO FEATURE_FLAGS (
    FLAG_ID, FLAG_NAME, FLAG_DESCRIPTION, IS_ENABLED,
    ENVIRONMENT, APPLICATION_NAME, FLAG_TYPE
) VALUES 
    ('ENHANCED_AI_MEMORY_DEV', 'enhanced_ai_memory', 'Enable enhanced AI Memory features with Snowflake Cortex integration', TRUE, 'DEV', 'SOPHIA_AI', 'BOOLEAN'),
    ('GONG_REAL_TIME_PROCESSING_DEV', 'gong_real_time_processing', 'Enable real-time processing of Gong call data', FALSE, 'DEV', 'SOPHIA_AI', 'BOOLEAN'),
    ('HUBSPOT_ADVANCED_ANALYTICS_DEV', 'hubspot_advanced_analytics', 'Enable advanced analytics for HubSpot data', TRUE, 'DEV', 'SOPHIA_AI', 'BOOLEAN'),
    ('CORTEX_AUTO_EMBEDDINGS_DEV', 'cortex_auto_embeddings', 'Automatically generate embeddings using Snowflake Cortex', TRUE, 'DEV', 'SOPHIA_AI', 'BOOLEAN'),
    ('EXPERIMENTAL_LANGGRAPH_DEV', 'experimental_langgraph', 'Enable experimental LangGraph workflow features', FALSE, 'DEV', 'SOPHIA_AI', 'PERCENTAGE'),
    ('DEBUG_VERBOSE_LOGGING_DEV', 'debug_verbose_logging', 'Enable verbose debug logging', TRUE, 'DEV', 'SOPHIA_AI', 'BOOLEAN'),
    ('PERFORMANCE_MONITORING_DEV', 'performance_monitoring', 'Enable detailed performance monitoring', TRUE, 'DEV', 'SOPHIA_AI', 'BOOLEAN');

-- Set percentage for experimental features
UPDATE FEATURE_FLAGS 
SET ROLLOUT_PERCENTAGE = 25 
WHERE FLAG_NAME = 'experimental_langgraph' AND ENVIRONMENT = 'DEV';

-- =====================================================================
-- 7. INDEXES AND PERFORMANCE OPTIMIZATION
-- =====================================================================

-- Create indexes for performance
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_APPLICATION_SETTINGS_NAME_ENV ON APPLICATION_SETTINGS(SETTING_NAME, ENVIRONMENT, APPLICATION_NAME);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_APPLICATION_SETTINGS_CATEGORY ON APPLICATION_SETTINGS(CATEGORY, ENVIRONMENT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_APPLICATION_SETTINGS_UPDATED_AT ON APPLICATION_SETTINGS(UPDATED_AT);
-- 
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_FEATURE_FLAGS_NAME_ENV ON FEATURE_FLAGS(FLAG_NAME, ENVIRONMENT, APPLICATION_NAME);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_FEATURE_FLAGS_TYPE ON FEATURE_FLAGS(FLAG_TYPE, IS_ENABLED);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_FEATURE_FLAGS_DATES ON FEATURE_FLAGS(START_DATE, END_DATE);
-- 
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_CONFIGURATION_HISTORY_SETTING ON CONFIGURATION_HISTORY(SETTING_ID, CHANGED_AT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_FEATURE_FLAG_EVALUATIONS_FLAG_TIME ON FEATURE_FLAG_EVALUATIONS(FLAG_ID, EVALUATED_AT);
-- 
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_SYSTEM_PARAMETERS_NAME_ENV ON SYSTEM_PARAMETERS(PARAMETER_NAME, ENVIRONMENT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IX_CONFIGURATION_DEPLOYMENTS_ENV_STATUS ON CONFIGURATION_DEPLOYMENTS(TARGET_ENVIRONMENT, STATUS);
-- 
-- =====================================================================
-- 8. GRANTS AND PERMISSIONS
-- =====================================================================

-- Grant access to ROLE_SOPHIA_AI_AGENT_SERVICE for configuration operations
GRANT USAGE ON SCHEMA CONFIG TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT ON ALL TABLES IN SCHEMA CONFIG TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA CONFIG TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA CONFIG TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;

-- Grant access to ROLE_SOPHIA_DEVELOPER for development configuration
GRANT USAGE ON SCHEMA CONFIG TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA CONFIG TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA CONFIG TO ROLE ROLE_SOPHIA_DEVELOPER;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA CONFIG TO ROLE ROLE_SOPHIA_DEVELOPER;

-- Grant future permissions
GRANT SELECT ON FUTURE TABLES IN SCHEMA CONFIG TO ROLE ROLE_SOPHIA_AI_AGENT_SERVICE;
GRANT SELECT, INSERT, UPDATE ON FUTURE TABLES IN SCHEMA CONFIG TO ROLE ROLE_SOPHIA_DEVELOPER;

-- =====================================================================
-- DEPLOYMENT NOTES
-- =====================================================================

/*
Deployment Steps:

1. Execute this script in SOPHIA_AI_DEV database
2. Verify all tables, functions, and procedures are created successfully
3. Test the configuration functions:
   - SELECT GET_CONFIG_VALUE('database.connection_pool_size', 'DEV', 'SOPHIA_AI');
   - SELECT EVALUATE_FEATURE_FLAG('enhanced_ai_memory', 'user_123', 'DEV', 'SOPHIA_AI');

4. Test configuration updates:
   - CALL UPDATE_CONFIG_SETTING('api.rate_limit_per_minute', '2000', 'DEV', 'SOPHIA_AI', NULL, NULL, 'admin', 'Increased for testing');

5. Verify default settings and feature flags are inserted
6. Integrate with your application configuration management system

Usage Examples:

-- Get a configuration value
SELECT GET_CONFIG_VALUE('ai_memory.similarity_threshold', 'DEV', 'SOPHIA_AI');

-- Evaluate a feature flag
SELECT EVALUATE_FEATURE_FLAG('enhanced_ai_memory', 'user_123', 'DEV', 'SOPHIA_AI');

-- Update a configuration setting
CALL UPDATE_CONFIG_SETTING(
    'cortex.batch_processing_size', '200', 'DEV', 'SOPHIA_AI', 
    NULL, NULL, 'admin', 'Increased batch size for better performance'
);

-- Query configuration history
SELECT * FROM CONFIGURATION_HISTORY 
WHERE SETTING_ID LIKE '%BATCH_SIZE%' 
ORDER BY CHANGED_AT DESC;

-- Query feature flag evaluations
SELECT 
    FLAG_NAME, 
    COUNT(*) AS evaluation_count,
    AVG(CASE WHEN RESULT_VALUE::BOOLEAN THEN 1 ELSE 0 END) AS enabled_rate
FROM FEATURE_FLAG_EVALUATIONS ffe
JOIN FEATURE_FLAGS ff ON ffe.FLAG_ID = ff.FLAG_ID
WHERE EVALUATED_AT >= DATEADD('day', -7, CURRENT_TIMESTAMP)
GROUP BY FLAG_NAME
ORDER BY evaluation_count DESC;
*/ 