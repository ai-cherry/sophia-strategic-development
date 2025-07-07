-- =========================================================================
-- SOPHIA AI PHOENIX PLATFORM - UNIFIED SCHEMA
-- The Single Source of Truth for All Data Architecture
--
-- Version: Phoenix 1.0
-- Created: January 2025
-- Status: AUTHORITATIVE - This DDL supersedes all previous schemas
-- =========================================================================

-- Set the context for deployment
USE ROLE SYSADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE SOPHIA_AI_PRODUCTION;

-- =========================================================================
-- CORE SCHEMAS: The Foundation of the Phoenix Architecture
-- =========================================================================

-- Core platform schema - The universe center
CREATE SCHEMA IF NOT EXISTS SOPHIA_CORE
    COMMENT = 'Core platform data - The center of the Sophia AI universe';

-- AI Memory schema - Cortex native semantic memory
CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_MEMORY
    COMMENT = 'AI Memory system using Snowflake Cortex native embeddings';

-- Business Intelligence schema - Executive insights
CREATE SCHEMA IF NOT EXISTS SOPHIA_BUSINESS_INTELLIGENCE
    COMMENT = 'Business intelligence and executive dashboard data';

-- Project Management schema - Cross-platform project data
CREATE SCHEMA IF NOT EXISTS SOPHIA_PROJECT_MANAGEMENT
    COMMENT = 'Unified project management across Linear, Asana, and Slack';

-- Knowledge Base schema - File uploads and learning data
CREATE SCHEMA IF NOT EXISTS SOPHIA_KNOWLEDGE_BASE
    COMMENT = 'Knowledge base, file uploads, and AI training data';

-- =========================================================================
-- L3: CORE DATA LAKEHOUSE - All Business Data
-- =========================================================================

-- Unified Data Catalog - Master registry of all data
CREATE TABLE IF NOT EXISTS SOPHIA_CORE.UNIFIED_DATA_CATALOG (
    data_id VARCHAR(255) PRIMARY KEY,
    source_system VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    metadata VARIANT,
    content_hash VARCHAR(64),
    ai_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    business_priority VARCHAR(20) DEFAULT 'medium',

    -- Constraints
    CONSTRAINT valid_data_type CHECK (data_type IN (
        'hubspot_deal', 'gong_call', 'linear_issue', 'asana_task',
        'slack_message', 'notion_page', 'uploaded_file', 'ai_memory',
        'business_metric', 'user_interaction'
    )),
    CONSTRAINT valid_priority CHECK (business_priority IN ('critical', 'high', 'medium', 'low'))
) COMMENT = 'Master catalog of all data in the Sophia AI universe';

-- System Health Monitoring
CREATE TABLE IF NOT EXISTS SOPHIA_CORE.SYSTEM_HEALTH (
    health_id VARCHAR(255) PRIMARY KEY,
    component_name VARCHAR(100) NOT NULL,
    component_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    health_score FLOAT NOT NULL,
    last_check TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    metrics VARIANT,
    alerts ARRAY,

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('healthy', 'degraded', 'critical', 'offline')),
    CONSTRAINT valid_health_score CHECK (health_score BETWEEN 0 AND 100)
) COMMENT = 'Real-time system health monitoring for all components';

-- MCP Server Registry
CREATE TABLE IF NOT EXISTS SOPHIA_CORE.MCP_SERVER_REGISTRY (
    server_id VARCHAR(255) PRIMARY KEY,
    server_name VARCHAR(100) NOT NULL,
    server_type VARCHAR(50) NOT NULL,
    port_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'inactive',
    capabilities ARRAY,
    last_heartbeat TIMESTAMP_NTZ,
    configuration VARIANT,

    -- Constraints
    CONSTRAINT valid_server_status CHECK (status IN ('active', 'inactive', 'error', 'maintenance')),
    CONSTRAINT valid_port CHECK (port_number BETWEEN 3000 AND 9999)
) COMMENT = 'Registry of all MCP servers in the consolidated architecture';

-- =========================================================================
-- L2: SEMANTIC MEMORY - Cortex Native Embeddings
-- =========================================================================

-- Memory Records - The AI brain of Sophia
CREATE TABLE IF NOT EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS (
    memory_id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(FLOAT, 768), -- Cortex Native Embeddings
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    importance_score FLOAT DEFAULT 0.5,
    business_context VARIANT,
    tags ARRAY,
    source_data_id VARCHAR(255),
    user_id VARCHAR(100),

    -- Constraints
    CONSTRAINT valid_importance CHECK (importance_score BETWEEN 0 AND 1),
    CONSTRAINT valid_category CHECK (category IN (
        'conversation', 'decision', 'insight', 'task', 'knowledge',
        'project_update', 'business_metric', 'customer_feedback',
        'competitive_intel', 'strategic_plan'
    )),

    -- Foreign key to data catalog
    CONSTRAINT fk_source_data FOREIGN KEY (source_data_id)
        REFERENCES SOPHIA_CORE.UNIFIED_DATA_CATALOG(data_id)
) COMMENT = 'AI Memory system with Cortex native embeddings for semantic search';

-- Memory Interactions - Track how memories are used
CREATE TABLE IF NOT EXISTS SOPHIA_AI_MEMORY.MEMORY_INTERACTIONS (
    interaction_id VARCHAR(255) PRIMARY KEY,
    memory_id VARCHAR(255) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    user_query TEXT,
    relevance_score FLOAT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    context VARIANT,

    -- Constraints
    CONSTRAINT valid_interaction_type CHECK (interaction_type IN (
        'retrieval', 'update', 'deletion', 'synthesis', 'recommendation'
    )),
    CONSTRAINT valid_relevance CHECK (relevance_score BETWEEN 0 AND 1),

    -- Foreign key to memory records
    CONSTRAINT fk_memory FOREIGN KEY (memory_id)
        REFERENCES SOPHIA_AI_MEMORY.MEMORY_RECORDS(memory_id)
) COMMENT = 'Track how AI memories are accessed and used';

-- =========================================================================
-- L1: FAST CACHE LAYER - Performance Optimization
-- =========================================================================

-- Query Cache - Materialized results for fast access
CREATE TABLE IF NOT EXISTS SOPHIA_CORE.QUERY_CACHE (
    cache_key VARCHAR(255) PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL,
    query_text TEXT,
    result_data VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP_NTZ,
    hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    cache_size_bytes INTEGER,

    -- Constraints
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
) COMMENT = 'Query result caching for performance optimization';

-- Session Cache - User session data
CREATE TABLE IF NOT EXISTS SOPHIA_CORE.SESSION_CACHE (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    session_data VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    last_activity TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP_NTZ,

    -- Constraints
    CONSTRAINT valid_session_expiry CHECK (expires_at > created_at)
) COMMENT = 'User session caching for dashboard state management';

-- =========================================================================
-- BUSINESS INTELLIGENCE LAYER
-- =========================================================================

-- Executive KPIs - Unified Dashboard metrics
CREATE TABLE IF NOT EXISTS SOPHIA_BUSINESS_INTELLIGENCE.EXECUTIVE_KPIS (
    kpi_id VARCHAR(255) PRIMARY KEY,
    kpi_name VARCHAR(100) NOT NULL,
    kpi_value FLOAT NOT NULL,
    kpi_unit VARCHAR(50),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    trend_direction VARCHAR(10),
    target_value FLOAT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    metadata VARIANT,

    -- Constraints
    CONSTRAINT valid_trend CHECK (trend_direction IN ('up', 'down', 'stable', 'unknown')),
    CONSTRAINT valid_period CHECK (period_end >= period_start)
) COMMENT = 'Executive KPIs for Unified dashboard';

-- Business Insights - AI-generated insights
CREATE TABLE IF NOT EXISTS SOPHIA_BUSINESS_INTELLIGENCE.BUSINESS_INSIGHTS (
    insight_id VARCHAR(255) PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    impact_level VARCHAR(20) NOT NULL,
    generated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    data_sources ARRAY,
    recommendations ARRAY,

    -- Constraints
    CONSTRAINT valid_confidence CHECK (confidence_score BETWEEN 0 AND 1),
    CONSTRAINT valid_impact CHECK (impact_level IN ('critical', 'high', 'medium', 'low'))
) COMMENT = 'AI-generated business insights from cross-platform data analysis';

-- =========================================================================
-- PROJECT MANAGEMENT LAYER
-- =========================================================================

-- Unified Projects - Cross-platform project tracking
CREATE TABLE IF NOT EXISTS SOPHIA_PROJECT_MANAGEMENT.UNIFIED_PROJECTS (
    project_id VARCHAR(255) PRIMARY KEY,
    project_name VARCHAR(200) NOT NULL,
    source_platform VARCHAR(50) NOT NULL,
    external_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    health_score FLOAT DEFAULT 0.5,
    team_members ARRAY,
    start_date DATE,
    target_date DATE,
    completion_percentage FLOAT DEFAULT 0,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    metadata VARIANT,

    -- Constraints
    CONSTRAINT valid_platform CHECK (source_platform IN ('linear', 'asana', 'slack', 'notion')),
    CONSTRAINT valid_health CHECK (health_score BETWEEN 0 AND 1),
    CONSTRAINT valid_completion CHECK (completion_percentage BETWEEN 0 AND 100)
) COMMENT = 'Unified view of projects across Linear, Asana, and other platforms';

-- Project Health Analytics
CREATE TABLE IF NOT EXISTS SOPHIA_PROJECT_MANAGEMENT.PROJECT_HEALTH_ANALYTICS (
    analysis_id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    analysis_date DATE NOT NULL,
    risk_factors ARRAY,
    success_indicators ARRAY,
    ai_recommendations ARRAY,
    predicted_completion DATE,
    confidence_level FLOAT,

    -- Foreign key to projects
    CONSTRAINT fk_project FOREIGN KEY (project_id)
        REFERENCES SOPHIA_PROJECT_MANAGEMENT.UNIFIED_PROJECTS(project_id)
) COMMENT = 'AI-powered project health analysis and predictions';

-- =========================================================================
-- KNOWLEDGE BASE LAYER
-- =========================================================================

-- Uploaded Files - File management system
CREATE TABLE IF NOT EXISTS SOPHIA_KNOWLEDGE_BASE.UPLOADED_FILES (
    file_id VARCHAR(255) PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    upload_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    uploaded_by VARCHAR(100) NOT NULL,
    processing_status VARCHAR(50) DEFAULT 'pending',
    ai_extracted_content TEXT,
    ai_summary TEXT,
    categories ARRAY,
    metadata VARIANT,

    -- Constraints
    CONSTRAINT valid_processing_status CHECK (processing_status IN (
        'pending', 'processing', 'completed', 'failed', 'archived'
    ))
) COMMENT = 'File upload management with AI processing status';

-- Knowledge Categories - Organizational structure
CREATE TABLE IF NOT EXISTS SOPHIA_KNOWLEDGE_BASE.KNOWLEDGE_CATEGORIES (
    category_id VARCHAR(255) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id VARCHAR(255),
    description TEXT,
    ai_learning_priority INTEGER DEFAULT 5,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    -- Self-referencing foreign key for hierarchy
    CONSTRAINT fk_parent_category FOREIGN KEY (parent_category_id)
        REFERENCES SOPHIA_KNOWLEDGE_BASE.KNOWLEDGE_CATEGORIES(category_id)
) COMMENT = 'Hierarchical knowledge categorization system';

-- =========================================================================
-- AI PROCESSING FUNCTIONS - Cortex Native
-- =========================================================================

-- Create Cortex Search Service for semantic search
CREATE OR REPLACE CORTEX SEARCH SERVICE SOPHIA_SEMANTIC_SEARCH
ON content
ATTRIBUTES metadata, category, tags, business_context
WAREHOUSE = COMPUTE_WH
TARGET_LAG = '1 minute'
AS (
    SELECT
        memory_id,
        content,
        metadata,
        category,
        tags,
        business_context
    FROM SOPHIA_AI_MEMORY.MEMORY_RECORDS
    WHERE embedding IS NOT NULL
);

-- =========================================================================
-- VIEWS: Business Intelligence Layer
-- =========================================================================

-- Executive Dashboard Summary
CREATE OR REPLACE VIEW SOPHIA_BUSINESS_INTELLIGENCE.EXECUTIVE_DASHBOARD_SUMMARY AS
SELECT
    'system_health' as metric_category,
    COUNT(CASE WHEN status = 'healthy' THEN 1 END) as healthy_components,
    COUNT(*) as total_components,
    ROUND((COUNT(CASE WHEN status = 'healthy' THEN 1 END) * 100.0 / COUNT(*)), 2) as health_percentage
FROM SOPHIA_CORE.SYSTEM_HEALTH
UNION ALL
SELECT
    'project_health' as metric_category,
    COUNT(CASE WHEN health_score >= 0.7 THEN 1 END) as healthy_projects,
    COUNT(*) as total_projects,
    ROUND(AVG(health_score) * 100, 2) as avg_health_score
FROM SOPHIA_PROJECT_MANAGEMENT.UNIFIED_PROJECTS
UNION ALL
SELECT
    'ai_memory' as metric_category,
    COUNT(*) as total_memories,
    COUNT(CASE WHEN importance_score >= 0.7 THEN 1 END) as important_memories,
    ROUND(AVG(importance_score) * 100, 2) as avg_importance
FROM SOPHIA_AI_MEMORY.MEMORY_RECORDS;

-- MCP Server Status Overview
CREATE OR REPLACE VIEW SOPHIA_CORE.MCP_SERVER_STATUS AS
SELECT
    server_name,
    server_type,
    port_number,
    status,
    CASE
        WHEN last_heartbeat > DATEADD('minute', -5, CURRENT_TIMESTAMP()) THEN 'online'
        WHEN last_heartbeat > DATEADD('minute', -15, CURRENT_TIMESTAMP()) THEN 'degraded'
        ELSE 'offline'
    END as connectivity_status,
    DATEDIFF('second', last_heartbeat, CURRENT_TIMESTAMP()) as seconds_since_heartbeat
FROM SOPHIA_CORE.MCP_SERVER_REGISTRY
ORDER BY server_type, server_name;

-- =========================================================================
-- STORED PROCEDURES: AI Processing Automation
-- =========================================================================

-- Procedure to process new data through AI pipeline
CREATE OR REPLACE PROCEDURE SOPHIA_CORE.PROCESS_NEW_DATA(DATA_ID VARCHAR)
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    -- Update processing status
    UPDATE SOPHIA_CORE.UNIFIED_DATA_CATALOG
    SET processing_status = 'processing', updated_at = CURRENT_TIMESTAMP()
    WHERE data_id = DATA_ID;

    -- Generate embedding if content exists
    -- This would integrate with Cortex embedding functions

    -- Update completion status
    UPDATE SOPHIA_CORE.UNIFIED_DATA_CATALOG
    SET ai_processed = TRUE, processing_status = 'completed', updated_at = CURRENT_TIMESTAMP()
    WHERE data_id = DATA_ID;

    RETURN 'Data processing completed for ID: ' || DATA_ID;
END;
$$;

-- =========================================================================
-- TASKS: Automated Maintenance
-- =========================================================================

-- Clean up expired cache entries
CREATE OR REPLACE TASK SOPHIA_CORE.CLEANUP_EXPIRED_CACHE
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC'  -- Daily at 2 AM UTC
AS
DELETE FROM SOPHIA_CORE.QUERY_CACHE
WHERE expires_at < CURRENT_TIMESTAMP();

-- Update system health scores
CREATE OR REPLACE TASK SOPHIA_CORE.UPDATE_SYSTEM_HEALTH
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON */5 * * * * UTC'  -- Every 5 minutes
AS
CALL SOPHIA_CORE.CALCULATE_SYSTEM_HEALTH();

-- =========================================================================
-- SECURITY: Role-Based Access Control
-- =========================================================================

-- Create roles for different access levels
CREATE ROLE IF NOT EXISTS SOPHIA_Unified_ROLE;
CREATE ROLE IF NOT EXISTS SOPHIA_EXECUTIVE_ROLE;
CREATE ROLE IF NOT EXISTS SOPHIA_MANAGER_ROLE;
CREATE ROLE IF NOT EXISTS SOPHIA_EMPLOYEE_ROLE;

-- Grant schema permissions
GRANT USAGE ON SCHEMA SOPHIA_CORE TO SOPHIA_Unified_ROLE;
GRANT USAGE ON SCHEMA SOPHIA_AI_MEMORY TO SOPHIA_Unified_ROLE;
GRANT USAGE ON SCHEMA SOPHIA_BUSINESS_INTELLIGENCE TO SOPHIA_Unified_ROLE;
GRANT USAGE ON SCHEMA SOPHIA_PROJECT_MANAGEMENT TO SOPHIA_Unified_ROLE;
GRANT USAGE ON SCHEMA SOPHIA_KNOWLEDGE_BASE TO SOPHIA_Unified_ROLE;

-- Unified has full access
GRANT ALL ON ALL TABLES IN SCHEMA SOPHIA_CORE TO SOPHIA_Unified_ROLE;
GRANT ALL ON ALL TABLES IN SCHEMA SOPHIA_AI_MEMORY TO SOPHIA_Unified_ROLE;
GRANT ALL ON ALL TABLES IN SCHEMA SOPHIA_BUSINESS_INTELLIGENCE TO SOPHIA_Unified_ROLE;
GRANT ALL ON ALL TABLES IN SCHEMA SOPHIA_PROJECT_MANAGEMENT TO SOPHIA_Unified_ROLE;
GRANT ALL ON ALL TABLES IN SCHEMA SOPHIA_KNOWLEDGE_BASE TO SOPHIA_Unified_ROLE;

-- =========================================================================
-- INITIALIZATION DATA
-- =========================================================================

-- Insert MCP server registry entries
INSERT INTO SOPHIA_CORE.MCP_SERVER_REGISTRY
(server_id, server_name, server_type, port_number, status, capabilities) VALUES
('ai-memory-001', 'ai_memory', 'core_intelligence', 9000, 'active', ['memory_storage', 'semantic_search']),
('codacy-001', 'codacy', 'core_intelligence', 3008, 'active', ['code_analysis', 'security_scan']),
('github-001', 'github', 'core_intelligence', 9003, 'active', ['repository_management', 'issue_tracking']),
('linear-001', 'linear', 'core_intelligence', 9004, 'active', ['project_management', 'engineering_tracking']),
('asana-001', 'asana', 'core_intelligence', 3006, 'active', ['product_management', 'task_tracking']),
('notion-001', 'notion', 'business_intelligence', 3007, 'active', ['knowledge_management', 'documentation']),
('hubspot-001', 'hubspot_unified', 'business_intelligence', 9006, 'active', ['crm_data', 'sales_analytics']),
('slack-001', 'slack_unified', 'business_intelligence', 9005, 'active', ['communication_analytics', 'team_insights']);

-- Insert initial knowledge categories
INSERT INTO SOPHIA_KNOWLEDGE_BASE.KNOWLEDGE_CATEGORIES
(category_id, category_name, description, ai_learning_priority) VALUES
('cat-business-001', 'Business Strategy', 'Strategic business documents and plans', 1),
('cat-technical-001', 'Technical Documentation', 'Technical specifications and architecture', 2),
('cat-hr-001', 'Human Resources', 'HR policies, procedures, and team information', 3),
('cat-finance-001', 'Financial Data', 'Financial reports, budgets, and analysis', 1),
('cat-marketing-001', 'Marketing Materials', 'Marketing content, campaigns, and analysis', 4),
('cat-sales-001', 'Sales Resources', 'Sales materials, processes, and customer data', 2);

-- =========================================================================
-- COMPLETION VERIFICATION
-- =========================================================================

-- Verify schema creation
SELECT 'Schema Creation Complete' as status,
       COUNT(*) as total_schemas
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE SCHEMA_NAME LIKE 'SOPHIA_%';

-- Verify table creation
SELECT 'Table Creation Complete' as status,
       COUNT(*) as total_tables
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA LIKE 'SOPHIA_%';

-- =========================================================================
-- END OF UNIFIED PLATFORM SCHEMA
-- =========================================================================

-- Final status message
SELECT
    '🔥 PHOENIX PLATFORM SCHEMA DEPLOYMENT COMPLETE 🔥' as message,
    CURRENT_TIMESTAMP() as deployed_at,
    'Snowflake is now the center of the universe' as architecture_status;
