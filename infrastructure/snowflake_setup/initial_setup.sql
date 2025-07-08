-- Snowflake Initial Setup for Sophia AI
-- This script creates the foundational database, schemas, and tables

-- Create main database
CREATE DATABASE IF NOT EXISTS SOPHIA_AI_UNIFIED;
USE DATABASE SOPHIA_AI_UNIFIED;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS PRODUCTION;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;
CREATE SCHEMA IF NOT EXISTS MONITORING;
CREATE SCHEMA IF NOT EXISTS AI_MEMORY;
CREATE SCHEMA IF NOT EXISTS KNOWLEDGE;
CREATE SCHEMA IF NOT EXISTS CONFIG;

-- Set default schema
USE SCHEMA PRODUCTION;

-- Create warehouses with appropriate sizes for new project
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
    WITH WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1
    COMMENT = 'General purpose compute warehouse';

CREATE WAREHOUSE IF NOT EXISTS AI_COMPUTE_WH
    WITH WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 2
    COMMENT = 'Analytics and BI workloads';

CREATE WAREHOUSE IF NOT EXISTS CORTEX_COMPUTE_WH
    WITH WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 2
    COMMENT = 'Cortex AI/ML workloads';

CREATE WAREHOUSE IF NOT EXISTS LOADING_WH
    WITH WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1
    COMMENT = 'ETL and data loading';

-- Create resource monitor for cost control
CREATE RESOURCE MONITOR IF NOT EXISTS SOPHIA_AI_DAILY_LIMIT
    WITH CREDIT_QUOTA = 100
    FREQUENCY = DAILY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS
        ON 80 PERCENT DO NOTIFY
        ON 95 PERCENT DO SUSPEND
        ON 100 PERCENT DO SUSPEND_IMMEDIATE;

-- Assign resource monitor to warehouses
ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = SOPHIA_AI_DAILY_LIMIT;
ALTER WAREHOUSE AI_COMPUTE_WH SET RESOURCE_MONITOR = SOPHIA_AI_DAILY_LIMIT;
ALTER WAREHOUSE CORTEX_COMPUTE_WH SET RESOURCE_MONITOR = SOPHIA_AI_DAILY_LIMIT;
ALTER WAREHOUSE LOADING_WH SET RESOURCE_MONITOR = SOPHIA_AI_DAILY_LIMIT;

-- Create configuration tables
USE SCHEMA CONFIG;

CREATE TABLE IF NOT EXISTS SYSTEM_CONFIG (
    config_key VARCHAR NOT NULL PRIMARY KEY,
    config_value VARIANT,
    description VARCHAR,
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_by VARCHAR DEFAULT CURRENT_USER()
);

-- Insert initial configuration
INSERT INTO SYSTEM_CONFIG (config_key, config_value, description)
SELECT * FROM (
    SELECT 'daily_credit_limit' as config_key, 100 as config_value, 'Daily credit limit for all warehouses' as description
    UNION ALL
    SELECT 'default_ai_model', 'mixtral-8x7b', 'Default Cortex AI model'
    UNION ALL
    SELECT 'default_embedding_model', 'e5-base-v2', 'Default embedding model'
    UNION ALL
    SELECT 'cache_ttl_seconds', 300, 'Default cache TTL in seconds'
    UNION ALL
    SELECT 'max_query_results', 1000, 'Maximum results per query'
) AS new_configs
WHERE NOT EXISTS (
    SELECT 1 FROM SYSTEM_CONFIG WHERE config_key = new_configs.config_key
);

-- Create knowledge base tables
USE SCHEMA KNOWLEDGE;

CREATE TABLE IF NOT EXISTS DOCUMENTS (
    document_id VARCHAR DEFAULT UUID_STRING() PRIMARY KEY,
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR,
    tags ARRAY,
    metadata VARIANT,
    embedding VECTOR(FLOAT, 768),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    created_by VARCHAR DEFAULT CURRENT_USER()
);

CREATE TABLE IF NOT EXISTS ENTITIES (
    entity_id VARCHAR DEFAULT UUID_STRING() PRIMARY KEY,
    entity_type VARCHAR NOT NULL, -- 'customer', 'product', 'employee', etc.
    entity_name VARCHAR NOT NULL,
    attributes VARIANT,
    embedding VECTOR(FLOAT, 768),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create AI Memory tables
USE SCHEMA AI_MEMORY;

CREATE TABLE IF NOT EXISTS MEMORY_RECORDS (
    memory_id VARCHAR DEFAULT UUID_STRING() PRIMARY KEY,
    category VARCHAR NOT NULL,
    content TEXT NOT NULL,
    context VARIANT,
    embedding VECTOR(FLOAT, 768),
    importance_score FLOAT DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS CONVERSATION_HISTORY (
    conversation_id VARCHAR DEFAULT UUID_STRING(),
    message_id VARCHAR DEFAULT UUID_STRING() PRIMARY KEY,
    role VARCHAR NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create analytics tables
USE SCHEMA ANALYTICS;

CREATE TABLE IF NOT EXISTS QUERY_METRICS (
    query_id VARCHAR DEFAULT UUID_STRING() PRIMARY KEY,
    query_text TEXT,
    query_type VARCHAR,
    warehouse_name VARCHAR,
    execution_time_ms INTEGER,
    rows_returned INTEGER,
    credits_used FLOAT,
    user_name VARCHAR,
    session_id VARCHAR,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS AI_USAGE_METRICS (
    usage_id VARCHAR DEFAULT UUID_STRING() PRIMARY KEY,
    function_name VARCHAR NOT NULL,
    model_name VARCHAR,
    input_tokens INTEGER,
    output_tokens INTEGER,
    credits_used FLOAT,
    latency_ms INTEGER,
    user_name VARCHAR,
    session_id VARCHAR,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create monitoring tables (already created by monitoring service, but included for completeness)
USE SCHEMA MONITORING;

-- Query performance tracking
CREATE TABLE IF NOT EXISTS QUERY_PERFORMANCE (
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    query_id VARCHAR,
    function_name VARCHAR,
    warehouse_name VARCHAR,
    execution_time_ms NUMBER,
    credits_used FLOAT,
    rows_returned NUMBER,
    cache_hit BOOLEAN,
    error_message VARCHAR,
    user_name VARCHAR,
    session_id VARCHAR
);

-- Credit usage tracking
CREATE TABLE IF NOT EXISTS CREDIT_USAGE (
    date DATE,
    warehouse_name VARCHAR,
    function_type VARCHAR,
    credits_used FLOAT,
    query_count NUMBER,
    avg_execution_time_ms NUMBER,
    PRIMARY KEY (date, warehouse_name, function_type)
);

-- Create views for easy monitoring
CREATE OR REPLACE VIEW DAILY_CREDIT_SUMMARY AS
SELECT
    CURRENT_DATE() as date,
    SUM(credits_used) as total_credits_used,
    100 - SUM(credits_used) as credits_remaining,
    COUNT(DISTINCT warehouse_name) as active_warehouses,
    COUNT(*) as total_queries
FROM CREDIT_USAGE
WHERE date = CURRENT_DATE();

-- Create stored procedures
CREATE OR REPLACE PROCEDURE CHECK_AND_ALERT_CREDIT_USAGE()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    current_usage FLOAT;
    daily_limit FLOAT;
    usage_percentage FLOAT;
BEGIN
    -- Get current usage
    SELECT SUM(credits_used) INTO current_usage
    FROM MONITORING.CREDIT_USAGE
    WHERE date = CURRENT_DATE();

    -- Get daily limit
    SELECT config_value INTO daily_limit
    FROM CONFIG.SYSTEM_CONFIG
    WHERE config_key = 'daily_credit_limit';

    -- Calculate percentage
    usage_percentage := (current_usage / daily_limit) * 100;

    -- Log alert if needed
    IF usage_percentage > 80 THEN
        INSERT INTO MONITORING.ALERT_HISTORY (severity, title, description, metric_value)
        VALUES (
            CASE
                WHEN usage_percentage > 95 THEN 'critical'
                ELSE 'warning'
            END,
            'High Credit Usage',
            'Daily credit usage at ' || ROUND(usage_percentage, 1) || '%',
            usage_percentage
        );
    END IF;

    RETURN 'Credit usage: ' || ROUND(usage_percentage, 1) || '%';
END;
$$;

-- Grant necessary permissions
GRANT USAGE ON DATABASE SOPHIA_AI_UNIFIED TO ROLE ACCOUNTADMIN;
GRANT USAGE ON ALL SCHEMAS IN DATABASE SOPHIA_AI_UNIFIED TO ROLE ACCOUNTADMIN;
GRANT ALL ON ALL TABLES IN DATABASE SOPHIA_AI_UNIFIED TO ROLE ACCOUNTADMIN;
GRANT ALL ON ALL WAREHOUSES TO ROLE ACCOUNTADMIN;

-- Set default context
USE WAREHOUSE COMPUTE_WH;
USE DATABASE SOPHIA_AI_UNIFIED;
USE SCHEMA PRODUCTION;

-- Final message
SELECT 'Snowflake initial setup completed successfully!' as status;
