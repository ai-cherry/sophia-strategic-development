-- =====================================================================
-- PROJECT_MANAGEMENT Schema - Linear & Asana Integration
-- =====================================================================
--
-- This script creates the PROJECT_MANAGEMENT schema for storing project
-- management data from Linear and Asana integrations with AI Memory support.
--
-- Features:
-- - Linear projects, issues, teams, and users
-- - Asana projects, tasks, teams, and users
-- - Cross-platform project health analytics
-- - AI Memory integration for semantic search
-- - Snowflake Cortex AI processing
-- - Historical tracking and trend analysis
--
-- Usage: Execute in SOPHIA_AI_DEV database
-- =====================================================================

-- Set context for DEV environment
USE DATABASE SOPHIA_AI_DEV;
CREATE SCHEMA IF NOT EXISTS PROJECT_MANAGEMENT;
USE SCHEMA PROJECT_MANAGEMENT;

-- =====================================================================
-- 1. LINEAR INTEGRATION TABLES
-- =====================================================================

-- Linear projects table
CREATE TABLE IF NOT EXISTS LINEAR_PROJECTS (
    PROJECT_ID VARCHAR(255) PRIMARY KEY,
    NAME VARCHAR(500) NOT NULL,
    DESCRIPTION VARCHAR(16777216),
    STATE_NAME VARCHAR(100),
    STATE_TYPE VARCHAR(50), -- 'planned', 'started', 'completed', 'canceled'
    PROGRESS FLOAT, -- 0.0 to 1.0
    START_DATE DATE,
    TARGET_DATE DATE,
    COMPLETED_AT TIMESTAMP_LTZ,

    -- Team and ownership
    TEAM_ID VARCHAR(255),
    TEAM_NAME VARCHAR(255),
    LEAD_ID VARCHAR(255),
    LEAD_NAME VARCHAR(255),
    LEAD_EMAIL VARCHAR(255),

    -- Metrics and health
    TOTAL_ISSUES NUMBER DEFAULT 0,
    COMPLETED_ISSUES NUMBER DEFAULT 0,
    COMPLETION_RATE FLOAT DEFAULT 0.0,
    HEALTH_SCORE FLOAT, -- Calculated health score 0-100
    RISK_LEVEL VARCHAR(50), -- 'low', 'medium', 'high', 'critical'

    -- AI processing
    AI_SUMMARY VARCHAR(16777216), -- Cortex-generated summary
    AI_RISK_ASSESSMENT VARCHAR(4000), -- AI-generated risk analysis
    AI_RECOMMENDATIONS VARIANT, -- JSON array of AI recommendations

    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768), -- Cortex embedding
    AI_MEMORY_METADATA VARCHAR(16777216), -- JSON metadata
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,

    -- Audit fields
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    SYNCED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    DATA_SOURCE VARCHAR(50) DEFAULT 'LINEAR'
);

-- Linear issues table
CREATE TABLE IF NOT EXISTS LINEAR_ISSUES (
    ISSUE_ID VARCHAR(255) PRIMARY KEY,
    TITLE VARCHAR(1000) NOT NULL,
    DESCRIPTION VARCHAR(16777216),
    STATE_NAME VARCHAR(100),
    STATE_TYPE VARCHAR(50), -- 'backlog', 'unstarted', 'started', 'completed', 'canceled'
    PRIORITY NUMBER, -- 0=No priority, 1=Urgent, 2=High, 3=Normal, 4=Low
    PRIORITY_LABEL VARCHAR(50),
    ESTIMATE FLOAT, -- Story points or time estimate

    -- Relationships
    PROJECT_ID VARCHAR(255),
    PROJECT_NAME VARCHAR(255),
    TEAM_ID VARCHAR(255),
    TEAM_NAME VARCHAR(255),
    ASSIGNEE_ID VARCHAR(255),
    ASSIGNEE_NAME VARCHAR(255),
    ASSIGNEE_EMAIL VARCHAR(255),
    CREATOR_ID VARCHAR(255),
    CREATOR_NAME VARCHAR(255),

    -- Dates
    CREATED_AT TIMESTAMP_LTZ,
    UPDATED_AT TIMESTAMP_LTZ,
    DUE_DATE DATE,
    COMPLETED_AT TIMESTAMP_LTZ,

    -- Labels and categorization
    LABELS VARIANT, -- JSON array of labels
    ISSUE_TYPE VARCHAR(100), -- 'feature', 'bug', 'improvement', etc.

    -- AI processing
    AI_SENTIMENT FLOAT, -- Sentiment analysis of description
    AI_COMPLEXITY_SCORE FLOAT, -- AI-estimated complexity
    AI_PRIORITY_SUGGESTION NUMBER, -- AI-suggested priority
    AI_TAGS VARIANT, -- JSON array of AI-generated tags

    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,

    -- Audit fields
    SYNCED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    DATA_SOURCE VARCHAR(50) DEFAULT 'LINEAR',

    -- Foreign key constraints
    FOREIGN KEY (PROJECT_ID) REFERENCES LINEAR_PROJECTS(PROJECT_ID)
);

-- Linear teams table
CREATE TABLE IF NOT EXISTS LINEAR_TEAMS (
    TEAM_ID VARCHAR(255) PRIMARY KEY,
    NAME VARCHAR(255) NOT NULL,
    KEY VARCHAR(50), -- Team key/abbreviation
    DESCRIPTION VARCHAR(4000),
    IS_ARCHIVED BOOLEAN DEFAULT FALSE,

    -- Metrics
    MEMBER_COUNT NUMBER DEFAULT 0,
    PROJECT_COUNT NUMBER DEFAULT 0,
    TOTAL_ISSUES NUMBER DEFAULT 0,
    ACTIVE_PROJECTS NUMBER DEFAULT 0,

    -- Performance metrics
    VELOCITY FLOAT, -- Issues completed per sprint/period
    CYCLE_TIME_DAYS FLOAT, -- Average time to complete issues
    THROUGHPUT FLOAT, -- Issues completed per time period

    -- AI insights
    AI_TEAM_HEALTH_SCORE FLOAT, -- 0-100 team health score
    AI_PERFORMANCE_TREND VARCHAR(50), -- 'improving', 'stable', 'declining'
    AI_RECOMMENDATIONS VARIANT, -- JSON array of recommendations

    -- Audit fields
    CREATED_AT TIMESTAMP_LTZ,
    UPDATED_AT TIMESTAMP_LTZ,
    SYNCED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    DATA_SOURCE VARCHAR(50) DEFAULT 'LINEAR'
);

-- Linear users table
CREATE TABLE IF NOT EXISTS LINEAR_USERS (
    USER_ID VARCHAR(255) PRIMARY KEY,
    NAME VARCHAR(255) NOT NULL,
    EMAIL VARCHAR(255),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    IS_GUEST BOOLEAN DEFAULT FALSE,

    -- Workload metrics
    TOTAL_ASSIGNED_ISSUES NUMBER DEFAULT 0,
    ACTIVE_ISSUES NUMBER DEFAULT 0,
    COMPLETED_ISSUES_30D NUMBER DEFAULT 0,
    AVERAGE_COMPLETION_TIME_DAYS FLOAT,

    -- Performance metrics
    VELOCITY FLOAT, -- Personal velocity
    QUALITY_SCORE FLOAT, -- Based on issue resolution quality
    COLLABORATION_SCORE FLOAT, -- Based on team interactions

    -- AI insights
    AI_WORKLOAD_ASSESSMENT VARCHAR(50), -- 'underutilized', 'optimal', 'overloaded'
    AI_SKILL_TAGS VARIANT, -- JSON array of AI-identified skills
    AI_PERFORMANCE_INSIGHTS VARCHAR(4000),

    -- Audit fields
    CREATED_AT TIMESTAMP_LTZ,
    UPDATED_AT TIMESTAMP_LTZ,
    SYNCED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    DATA_SOURCE VARCHAR(50) DEFAULT 'LINEAR'
);

-- =====================================================================
-- 2. ASANA INTEGRATION TABLES (Enhanced)
-- =====================================================================

-- Asana projects table (enhanced version of existing)
CREATE TABLE IF NOT EXISTS ASANA_PROJECTS (
    PROJECT_GID VARCHAR(255) PRIMARY KEY,
    NAME VARCHAR(500) NOT NULL,
    NOTES VARCHAR(16777216),
    COLOR VARCHAR(50),
    COMPLETED BOOLEAN DEFAULT FALSE,
    CURRENT_STATUS VARCHAR(100),
    DUE_DATE DATE,
    START_DATE DATE,

    -- Team and ownership
    TEAM_GID VARCHAR(255),
    TEAM_NAME VARCHAR(255),
    OWNER_GID VARCHAR(255),
    OWNER_NAME VARCHAR(255),
    OWNER_EMAIL VARCHAR(255),

    -- Custom fields and metrics
    BUDGET FLOAT,
    SPENT FLOAT,
    BUDGET_UTILIZATION FLOAT,
    RISK_LEVEL VARCHAR(50),

    -- Calculated metrics
    TOTAL_TASKS NUMBER DEFAULT 0,
    COMPLETED_TASKS NUMBER DEFAULT 0,
    COMPLETION_RATE FLOAT DEFAULT 0.0,
    HEALTH_SCORE FLOAT,

    -- AI processing
    AI_SUMMARY VARCHAR(16777216),
    AI_RISK_ASSESSMENT VARCHAR(4000),
    AI_RECOMMENDATIONS VARIANT,

    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,

    -- Audit fields
    CREATED_AT TIMESTAMP_LTZ,
    MODIFIED_AT TIMESTAMP_LTZ,
    SYNCED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    DATA_SOURCE VARCHAR(50) DEFAULT 'ASANA'
);

-- Asana tasks table (enhanced version)
CREATE TABLE IF NOT EXISTS ASANA_TASKS (
    TASK_GID VARCHAR(255) PRIMARY KEY,
    NAME VARCHAR(1000) NOT NULL,
    NOTES VARCHAR(16777216),
    COMPLETED BOOLEAN DEFAULT FALSE,
    DUE_DATE DATE,
    START_DATE DATE,
    COMPLETED_AT TIMESTAMP_LTZ,

    -- Relationships
    PROJECT_GID VARCHAR(255),
    PROJECT_NAME VARCHAR(255),
    ASSIGNEE_GID VARCHAR(255),
    ASSIGNEE_NAME VARCHAR(255),
    ASSIGNEE_EMAIL VARCHAR(255),

    -- Task properties
    PRIORITY VARCHAR(50),
    TASK_TYPE VARCHAR(100),
    ESTIMATED_HOURS FLOAT,
    ACTUAL_HOURS FLOAT,

    -- AI processing
    AI_SENTIMENT FLOAT,
    AI_COMPLEXITY_SCORE FLOAT,
    AI_PRIORITY_SUGGESTION VARCHAR(50),
    AI_TAGS VARIANT,

    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,

    -- Audit fields
    CREATED_AT TIMESTAMP_LTZ,
    MODIFIED_AT TIMESTAMP_LTZ,
    SYNCED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    DATA_SOURCE VARCHAR(50) DEFAULT 'ASANA',

    -- Foreign key constraints
    FOREIGN KEY (PROJECT_GID) REFERENCES ASANA_PROJECTS(PROJECT_GID)
);

-- =====================================================================
-- 3. CROSS-PLATFORM ANALYTICS TABLES
-- =====================================================================

-- Unified project health metrics
CREATE TABLE IF NOT EXISTS PROJECT_HEALTH_METRICS (
    METRIC_ID VARCHAR(255) PRIMARY KEY,
    PROJECT_ID VARCHAR(255) NOT NULL,
    PROJECT_NAME VARCHAR(500),
    PLATFORM VARCHAR(50) NOT NULL, -- 'LINEAR' or 'ASANA'

    -- Health dimensions
    SCHEDULE_HEALTH FLOAT, -- 0-100 score
    SCOPE_HEALTH FLOAT,
    RESOURCE_HEALTH FLOAT,
    QUALITY_HEALTH FLOAT,
    OVERALL_HEALTH FLOAT,

    -- Risk indicators
    SCHEDULE_RISK VARCHAR(50), -- 'low', 'medium', 'high', 'critical'
    SCOPE_RISK VARCHAR(50),
    RESOURCE_RISK VARCHAR(50),
    QUALITY_RISK VARCHAR(50),

    -- Predictive metrics
    PREDICTED_COMPLETION_DATE DATE,
    COMPLETION_PROBABILITY FLOAT, -- 0-1 probability of on-time completion
    BUDGET_OVERRUN_RISK FLOAT, -- 0-1 probability of budget overrun

    -- AI insights
    AI_HEALTH_SUMMARY VARCHAR(4000),
    AI_RISK_FACTORS VARIANT, -- JSON array of risk factors
    AI_RECOMMENDATIONS VARIANT, -- JSON array of recommendations
    AI_TREND_ANALYSIS VARCHAR(4000),

    -- Metadata
    CALCULATION_DATE DATE,
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Team performance analytics
CREATE TABLE IF NOT EXISTS TEAM_PERFORMANCE_METRICS (
    METRIC_ID VARCHAR(255) PRIMARY KEY,
    TEAM_ID VARCHAR(255) NOT NULL,
    TEAM_NAME VARCHAR(255),
    PLATFORM VARCHAR(50) NOT NULL,

    -- Performance metrics
    VELOCITY FLOAT,
    THROUGHPUT FLOAT,
    CYCLE_TIME_DAYS FLOAT,
    LEAD_TIME_DAYS FLOAT,
    QUALITY_SCORE FLOAT,

    -- Collaboration metrics
    COMMUNICATION_SCORE FLOAT,
    KNOWLEDGE_SHARING_SCORE FLOAT,
    CROSS_FUNCTIONAL_SCORE FLOAT,

    -- Workload metrics
    CAPACITY_UTILIZATION FLOAT, -- 0-1
    WORKLOAD_BALANCE_SCORE FLOAT,
    BURNOUT_RISK_SCORE FLOAT,

    -- AI insights
    AI_PERFORMANCE_TREND VARCHAR(50),
    AI_STRENGTHS VARIANT, -- JSON array
    AI_IMPROVEMENT_AREAS VARIANT, -- JSON array
    AI_RECOMMENDATIONS VARIANT,

    -- Time period
    METRIC_PERIOD VARCHAR(50), -- 'weekly', 'monthly', 'quarterly'
    PERIOD_START_DATE DATE,
    PERIOD_END_DATE DATE,

    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================================
-- 4. INDEXES FOR PERFORMANCE
-- =====================================================================

-- Linear indexes
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_LINEAR_PROJECTS_TEAM ON LINEAR_PROJECTS (TEAM_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_LINEAR_PROJECTS_STATE ON LINEAR_PROJECTS (STATE_TYPE);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_LINEAR_PROJECTS_HEALTH ON LINEAR_PROJECTS (HEALTH_SCORE);
--
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_LINEAR_ISSUES_PROJECT ON LINEAR_ISSUES (PROJECT_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_LINEAR_ISSUES_ASSIGNEE ON LINEAR_ISSUES (ASSIGNEE_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_LINEAR_ISSUES_STATE ON LINEAR_ISSUES (STATE_TYPE);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_LINEAR_ISSUES_PRIORITY ON LINEAR_ISSUES (PRIORITY);
--
-- Asana indexes
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_ASANA_PROJECTS_TEAM ON ASANA_PROJECTS (TEAM_GID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_ASANA_PROJECTS_OWNER ON ASANA_PROJECTS (OWNER_GID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_ASANA_PROJECTS_STATUS ON ASANA_PROJECTS (CURRENT_STATUS);
--
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_ASANA_TASKS_PROJECT ON ASANA_TASKS (PROJECT_GID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_ASANA_TASKS_ASSIGNEE ON ASANA_TASKS (ASSIGNEE_GID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_ASANA_TASKS_COMPLETED ON ASANA_TASKS (COMPLETED);
--
-- Analytics indexes
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_PROJECT_HEALTH_PLATFORM ON PROJECT_HEALTH_METRICS (PLATFORM, PROJECT_ID);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_PROJECT_HEALTH_OVERALL ON PROJECT_HEALTH_METRICS (OVERALL_HEALTH);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_TEAM_PERFORMANCE_PLATFORM ON TEAM_PERFORMANCE_METRICS (PLATFORM, TEAM_ID);
--
-- =====================================================================
-- 5. VIEWS FOR UNIFIED ANALYTICS
-- =====================================================================

-- Unified project view across platforms
CREATE OR REPLACE VIEW UNIFIED_PROJECTS AS
SELECT
    PROJECT_ID,
    NAME,
    'LINEAR' AS PLATFORM,
    STATE_TYPE AS STATUS,
    PROGRESS,
    START_DATE,
    TARGET_DATE AS DUE_DATE,
    COMPLETED_AT,
    TEAM_NAME,
    LEAD_NAME AS OWNER_NAME,
    TOTAL_ISSUES AS TOTAL_ITEMS,
    COMPLETED_ISSUES AS COMPLETED_ITEMS,
    COMPLETION_RATE,
    HEALTH_SCORE,
    RISK_LEVEL,
    CREATED_AT,
    UPDATED_AT
FROM LINEAR_PROJECTS

UNION ALL

SELECT
    PROJECT_GID AS PROJECT_ID,
    NAME,
    'ASANA' AS PLATFORM,
    CURRENT_STATUS AS STATUS,
    COMPLETION_RATE / 100.0 AS PROGRESS,
    START_DATE,
    DUE_DATE,
    CASE WHEN COMPLETED THEN MODIFIED_AT ELSE NULL END AS COMPLETED_AT,
    TEAM_NAME,
    OWNER_NAME,
    TOTAL_TASKS AS TOTAL_ITEMS,
    COMPLETED_TASKS AS COMPLETED_ITEMS,
    COMPLETION_RATE,
    HEALTH_SCORE,
    RISK_LEVEL,
    CREATED_AT,
    MODIFIED_AT AS UPDATED_AT
FROM ASANA_PROJECTS;

-- Unified issues/tasks view
CREATE OR REPLACE VIEW UNIFIED_ISSUES AS
SELECT
    ISSUE_ID AS ITEM_ID,
    TITLE,
    'LINEAR' AS PLATFORM,
    STATE_TYPE AS STATUS,
    PRIORITY,
    PRIORITY_LABEL,
    PROJECT_NAME,
    TEAM_NAME,
    ASSIGNEE_NAME,
    CREATED_AT,
    UPDATED_AT,
    DUE_DATE,
    COMPLETED_AT,
    AI_COMPLEXITY_SCORE,
    AI_SENTIMENT
FROM LINEAR_ISSUES

UNION ALL

SELECT
    TASK_GID AS ITEM_ID,
    NAME AS TITLE,
    'ASANA' AS PLATFORM,
    CASE WHEN COMPLETED THEN 'completed' ELSE 'active' END AS STATUS,
    CASE
        WHEN PRIORITY = 'high' THEN 2
        WHEN PRIORITY = 'normal' THEN 3
        WHEN PRIORITY = 'low' THEN 4
        ELSE 0
    END AS PRIORITY,
    PRIORITY AS PRIORITY_LABEL,
    PROJECT_NAME,
    NULL AS TEAM_NAME, -- Asana doesn't have direct team assignment to tasks
    ASSIGNEE_NAME,
    CREATED_AT,
    MODIFIED_AT AS UPDATED_AT,
    DUE_DATE,
    COMPLETED_AT,
    AI_COMPLEXITY_SCORE,
    AI_SENTIMENT
FROM ASANA_TASKS;

-- =====================================================================
-- 6. STORED PROCEDURES FOR DATA PROCESSING
-- =====================================================================

-- Procedure to calculate project health scores
CREATE OR REPLACE PROCEDURE CALCULATE_PROJECT_HEALTH_SCORES()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Update Linear project health scores
    UPDATE LINEAR_PROJECTS
    SET
        HEALTH_SCORE = CASE
            WHEN STATE_TYPE = 'completed' THEN 100
            WHEN STATE_TYPE = 'canceled' THEN 0
            WHEN PROGRESS >= 0.9 THEN 90 + (PROGRESS - 0.9) * 100
            WHEN PROGRESS >= 0.7 THEN 70 + (PROGRESS - 0.7) * 100
            WHEN PROGRESS >= 0.5 THEN 50 + (PROGRESS - 0.5) * 100
            WHEN PROGRESS >= 0.3 THEN 30 + (PROGRESS - 0.3) * 100
            ELSE PROGRESS * 100
        END,
        RISK_LEVEL = CASE
            WHEN STATE_TYPE IN ('completed', 'canceled') THEN 'none'
            WHEN PROGRESS < 0.3 AND TARGET_DATE <= CURRENT_DATE() + INTERVAL '30 days' THEN 'critical'
            WHEN PROGRESS < 0.5 AND TARGET_DATE <= CURRENT_DATE() + INTERVAL '60 days' THEN 'high'
            WHEN PROGRESS < 0.7 AND TARGET_DATE <= CURRENT_DATE() + INTERVAL '90 days' THEN 'medium'
            ELSE 'low'
        END,
        UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE STATE_TYPE IS NOT NULL;

    -- Update Asana project health scores
    UPDATE ASANA_PROJECTS
    SET
        HEALTH_SCORE = CASE
            WHEN COMPLETED THEN 100
            WHEN COMPLETION_RATE >= 90 THEN 90 + (COMPLETION_RATE - 90)
            WHEN COMPLETION_RATE >= 70 THEN 70 + (COMPLETION_RATE - 70) * 0.5
            WHEN COMPLETION_RATE >= 50 THEN 50 + (COMPLETION_RATE - 50) * 0.5
            ELSE COMPLETION_RATE * 0.5
        END,
        RISK_LEVEL = CASE
            WHEN COMPLETED THEN 'none'
            WHEN COMPLETION_RATE < 30 AND DUE_DATE <= CURRENT_DATE() + INTERVAL '30 days' THEN 'critical'
            WHEN COMPLETION_RATE < 50 AND DUE_DATE <= CURRENT_DATE() + INTERVAL '60 days' THEN 'high'
            WHEN COMPLETION_RATE < 70 AND DUE_DATE <= CURRENT_DATE() + INTERVAL '90 days' THEN 'medium'
            ELSE 'low'
        END
    WHERE COMPLETION_RATE IS NOT NULL;

    RETURN 'Project health scores updated successfully';
END;
$$;

-- Procedure to update team performance metrics
CREATE OR REPLACE PROCEDURE UPDATE_TEAM_PERFORMANCE_METRICS()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Calculate Linear team metrics
    UPDATE LINEAR_TEAMS t
    SET
        VELOCITY = (
            SELECT COUNT(*) / 4.0 -- Assuming 4-week periods
            FROM LINEAR_ISSUES i
            WHERE i.TEAM_ID = t.TEAM_ID
            AND i.COMPLETED_AT >= CURRENT_DATE() - INTERVAL '28 days'
        ),
        CYCLE_TIME_DAYS = (
            SELECT AVG(DATEDIFF('day', i.CREATED_AT, i.COMPLETED_AT))
            FROM LINEAR_ISSUES i
            WHERE i.TEAM_ID = t.TEAM_ID
            AND i.COMPLETED_AT >= CURRENT_DATE() - INTERVAL '90 days'
            AND i.COMPLETED_AT IS NOT NULL
        ),
        AI_TEAM_HEALTH_SCORE = CASE
            WHEN VELOCITY >= 10 AND CYCLE_TIME_DAYS <= 7 THEN 90
            WHEN VELOCITY >= 5 AND CYCLE_TIME_DAYS <= 14 THEN 70
            WHEN VELOCITY >= 2 AND CYCLE_TIME_DAYS <= 21 THEN 50
            ELSE 30
        END,
        SYNCED_AT = CURRENT_TIMESTAMP()
    WHERE TEAM_ID IS NOT NULL;

    RETURN 'Team performance metrics updated successfully';
END;
$$;

-- =====================================================================
-- 7. SAMPLE QUERIES FOR ANALYTICS
-- =====================================================================

-- Example: Cross-platform project health dashboard
/*
SELECT
    PLATFORM,
    COUNT(*) AS TOTAL_PROJECTS,
    AVG(HEALTH_SCORE) AS AVG_HEALTH_SCORE,
    COUNT(CASE WHEN RISK_LEVEL = 'critical' THEN 1 END) AS CRITICAL_PROJECTS,
    COUNT(CASE WHEN RISK_LEVEL = 'high' THEN 1 END) AS HIGH_RISK_PROJECTS,
    COUNT(CASE WHEN STATUS IN ('completed') THEN 1 END) AS COMPLETED_PROJECTS
FROM UNIFIED_PROJECTS
WHERE CREATED_AT >= CURRENT_DATE() - INTERVAL '90 days'
GROUP BY PLATFORM;
*/

-- Example: Team performance comparison
/*
SELECT
    TEAM_NAME,
    PLATFORM,
    VELOCITY,
    CYCLE_TIME_DAYS,
    AI_TEAM_HEALTH_SCORE,
    MEMBER_COUNT
FROM (
    SELECT TEAM_NAME, 'LINEAR' AS PLATFORM, VELOCITY, CYCLE_TIME_DAYS, AI_TEAM_HEALTH_SCORE, MEMBER_COUNT
    FROM LINEAR_TEAMS WHERE IS_ARCHIVED = FALSE
    UNION ALL
    SELECT TEAM_NAME, 'ASANA' AS PLATFORM, NULL AS VELOCITY, NULL AS CYCLE_TIME_DAYS, NULL AS AI_TEAM_HEALTH_SCORE, NULL AS MEMBER_COUNT
    FROM ASANA_PROJECTS WHERE TEAM_NAME IS NOT NULL
)
ORDER BY AI_TEAM_HEALTH_SCORE DESC NULLS LAST;
*/

-- =====================================================================
-- 8. GRANTS AND PERMISSIONS
-- =====================================================================

-- Grant permissions to application roles
GRANT USAGE ON SCHEMA PROJECT_MANAGEMENT TO ROLE SOPHIA_AI_APP_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA PROJECT_MANAGEMENT TO ROLE SOPHIA_AI_APP_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA PROJECT_MANAGEMENT TO ROLE SOPHIA_AI_APP_ROLE;
GRANT USAGE ON ALL PROCEDURES IN SCHEMA PROJECT_MANAGEMENT TO ROLE SOPHIA_AI_APP_ROLE;

-- Grant read-only access to analytics role
GRANT USAGE ON SCHEMA PROJECT_MANAGEMENT TO ROLE SOPHIA_AI_ANALYTICS_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA PROJECT_MANAGEMENT TO ROLE SOPHIA_AI_ANALYTICS_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA PROJECT_MANAGEMENT TO ROLE SOPHIA_AI_ANALYTICS_ROLE;
